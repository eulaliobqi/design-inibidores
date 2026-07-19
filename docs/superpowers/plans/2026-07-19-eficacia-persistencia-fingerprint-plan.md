# Eficácia Ampla + Persistência Competitiva + S2'/S3' + Fingerprint — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar as 4 frentes aprovadas na spec (`docs/superpowers/specs/2026-07-19-priorizacao-eficacia-persistencia-fingerprint-design.md`): métrica real de persistência competitiva, análise de subsítios S2'/S3', assinatura digital de interação, e expansão taxonômica para 3 novas espécies — todas reusando trajetórias/scripts já validados no pipeline `design-inibidores`.

**Architecture:** Dois scripts novos e independentes (`scripts/deep_test_persistence.py`, `scripts/deep_test_s2s3_subsites.py`) seguindo o padrão já estabelecido pelos `deep_test_*.py` existentes — rodam no servidor, leem trajetórias `.xtc`/`.tpr` já preservadas, escrevem JSON de resumo, resume-safe por candidato. A Frente 4 não gera script novo (síntese manual dos 2 JSONs em tabela no artigo). A Frente 1 estende 3 scripts já existentes (`search_uniprot_trypsins.py`, `fetch_lepidoptera_af.py`/`map_lepidoptera_sites.py`, `dock_cross_species.py`) com as 3 novas espécies, sem lógica nova.

**Tech Stack:** Python 3.10, MDAnalysis (leitura de `.tpr`/`.xtc`), PLIP 3.0.0 (contatos multi-frame), GROMACS `gmx_mpi` (`trjconv` para extração de frames), AutoDock Vina (docking Frente 1), UniProt REST API.

## Global Constraints

- Nunca fabricar dado — candidato sem trajetória real preservada (`SARESIKKAYKTFLERYKKL`, sem `md.tpr`/`md.xtc`) deve ser reportado como "sem dado real disponível", nunca inferido.
- Todo script novo roda no servidor (`eulalio@200.235.143.10`) dentro de `screen`, resume-safe (não reprocessa o que já tem resultado real salvo).
- Workflow git: editar local (Windows) → commit → push GitHub → `git pull` no servidor → executar → puxar resultado de volta para atualizar artigo/memória.
- Ambiente Python: `conda run -n protein_design_env` (mesmo ambiente de todos os `deep_test_*.py` existentes).
- `gmx_mpi` precisa do prefixo `/home/eulalio/miniforge3/envs/md-gromacs/bin/mpirun -np 1` **apenas para `mdrun`** — todos os outros subcomandos (`trjconv`, `rms`, etc.) chamam o binário `gmx_mpi` diretamente, sem `mpirun` (confirmado nesta sessão: `mpirun` quebra `trjconv`/`make_ndx` com "Unknown command-line option").
- Ao final de cada Frente concluída: atualizar `artigo_resultados.md` (nova subseção) e `project_design_inibidores.md` (memória) com o dado real, e commitar.

## Verificação técnica já feita nesta sessão (base para o código abaixo)

Confirmado por inspeção direta de `outputs/md/SRTRR/minim.gro` no servidor (candidato `SRTRR`, receptor ACR157):

- **Receptor = 231 resíduos** (resid 1–231 no `.gro`, idêntico à numeração original do PDB — resid 91=ASP catalítico, resid 187=ASP do bolso S1, resid 203=SER catalítico, todos batendo com `outputs/structure/binding_site.json`).
- **Peptídeo REINICIA a numeração em 1** logo após o resíduo 231 do receptor (ex.: SRTRR aparece como resíduos 1–5 = SER/ARG/THR/ARG/ARG, colidindo numericamente com os resíduos 1–5 do próprio receptor). `pdb2gmx` reinicia a numeração por cadeia por padrão — **não usar `resid` para separar receptor de peptídeo, usar posição sequencial (`resindex` 0-based do MDAnalysis)**.
- **Átomos da carboxila do Asp**: `OD1`/`OD2` (nomenclatura AMBER99SB-ILDN padrão, confirmado nos átomos reais do resíduo 187).
- **P1 não é sempre o resíduo C-terminal**: 5/13 candidatos do TOP-13 não terminam em Arg/Lys (`RLREELKKAEEWLEKRRKEE`, `SEEEVLAANEAYAAAHTAYN`, `MGSLTAYLEAYAAENAAALA`, `MGYLTAYHQALAAQNAALLA`, `SARESIKKAYKTFLERYKKL`) — a Frente 2 **descobre empiricamente** qual resíduo do peptídeo fica mais perto do Asp-S1 em vez de assumir C-terminal.
- **Frames nativos salvos**: `nstxout-compressed = 2500` passos × 2 fs = 1 frame a cada 5 ps → 2000 frames por réplica de 10 ns (`md.xtc`).

---

## Frente 2 — Persistência Competitiva Real

### Task 1: Função pura de ocupância + RMSD local (testável sem trajetória real)

**Files:**
- Create: `scripts/persistence_utils.py`
- Test: `tests/test_persistence_utils.py`

**Interfaces:**
- Produces: `occupancy_fraction(distances: list[float], cutoff: float = 4.0) -> float`, `find_anchor_residue(distances_per_residue: dict[int, list[float]]) -> int` — usados pela Task 2.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_persistence_utils.py
from scripts.persistence_utils import occupancy_fraction, find_anchor_residue

def test_occupancy_fraction_all_within_cutoff():
    distances = [2.0, 3.5, 1.0, 3.9]
    assert occupancy_fraction(distances, cutoff=4.0) == 1.0

def test_occupancy_fraction_half_within_cutoff():
    distances = [2.0, 5.0, 2.0, 5.0]
    assert occupancy_fraction(distances, cutoff=4.0) == 0.5

def test_occupancy_fraction_empty_returns_none():
    assert occupancy_fraction([], cutoff=4.0) is None

def test_find_anchor_residue_picks_lowest_mean_distance():
    distances_per_residue = {
        0: [10.0, 10.0, 10.0],
        1: [2.0, 2.5, 2.0],   # menor média -> âncora real
        2: [8.0, 9.0, 8.0],
    }
    assert find_anchor_residue(distances_per_residue) == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `conda run -n protein_design_env python -m pytest tests/test_persistence_utils.py -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'scripts.persistence_utils'`

- [ ] **Step 3: Write minimal implementation**

```python
# scripts/persistence_utils.py
"""Funções puras de análise de persistência competitiva (Frente 2).

Sem dependência de MDAnalysis/GROMACS aqui — mantidas testáveis com dado
sintético. A orquestração real (leitura de trajetória) fica em
deep_test_persistence.py.
"""


def occupancy_fraction(distances: list, cutoff: float = 4.0) -> float | None:
    """Fração de frames com distância <cutoff (padrão salt-bridge/H-bond, 4 A).
    Retorna None se a lista estiver vazia (sem dado, não fabricar 0.0)."""
    if not distances:
        return None
    n_within = sum(1 for d in distances if d < cutoff)
    return n_within / len(distances)


def find_anchor_residue(distances_per_residue: dict) -> int:
    """Descobre empiricamente qual resíduo do peptídeo fica mais perto do
    Asp-S1 em média — não assume C-terminal (5/13 candidatos do TOP-13 não
    terminam em Arg/Lys, ver plano)."""
    means = {res_idx: sum(d) / len(d) for res_idx, d in distances_per_residue.items() if d}
    return min(means, key=means.get)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `conda run -n protein_design_env python -m pytest tests/test_persistence_utils.py -v`
Expected: PASS (4 testes)

- [ ] **Step 5: Commit**

```bash
git add scripts/persistence_utils.py tests/test_persistence_utils.py
git commit -m "feat(persistence): funções puras de ocupância e âncora empírica (Frente 2)"
```

### Task 2: Script de orquestração — cálculo real via MDAnalysis

**Files:**
- Create: `scripts/deep_test_persistence.py`

**Interfaces:**
- Consumes: `occupancy_fraction`, `find_anchor_residue` de `scripts/persistence_utils.py` (Task 1).
- Produces: `outputs/persistence_deep/persistence_summary.json` — schema:
  ```json
  {"SRTRR": {"rep1": {"anchor_residue_seq_idx": 4, "anchor_residue_aa": "R",
                        "occupancy_fraction": 0.94, "n_frames": 2000,
                        "local_rmsd_pocket_nm": 0.18},
             "rep2": {...}, "rep3": {...}}}
  ```

- [ ] **Step 1: Write the script**

```python
# scripts/deep_test_persistence.py
"""deep_test_persistence.py — Frente 2: persistência competitiva real (não só RMSD global).

Para cada candidato x réplica (rep1/rep2/rep3), mede quadro-a-quadro a distância entre
cada resíduo do peptídeo e a carboxila do Asp do bolso S1 (OD1/OD2), descobre
empiricamente qual resíduo é a âncora real (menor distância média — não assume
C-terminal, ver docs/superpowers/plans/2026-07-19-eficacia-persistencia-fingerprint-plan.md),
e reporta % de frames com distância <4 A (ocupância) + RMSD local do peptídeo após
superposição só nos Calpha do receptor (separa "balançou na caixa" de "saiu da fenda").

Reusa trajetórias .xtc/.tpr JA EXISTENTES (rep1 em outputs/md/{seq}/ ou
outputs/md/forced_NN/, rep2/rep3 em outputs/md_replicates/{seq}/rep{2,3}/) — nenhuma
simulação nova.

Uso: conda run -n protein_design_env python -m scripts.deep_test_persistence
"""
import json
from pathlib import Path

import MDAnalysis as mda
import numpy as np

from scripts.persistence_utils import occupancy_fraction, find_anchor_residue

CANDIDATES = [
    "SRTRR", "HRPRRPR", "RLREELKKAEEWLEKRRKEE", "SEEEVLAANEAYAAAHTAYN",
    "SALASIAAHQATFLAYLESK", "MGSLTAYLEAYAAENAAALA", "MGYLTAYHQALAAQNAALLA",
    "SARESIKKAYKTFLERYKKL", "VRYRR", "VRTRR", "VRRPR", "HRPRRSR", "HRPRRPK",
]

# rep1: mesmo mapeamento de outputs/md/forced_NN/ usado em deep_test_plip.py e
# deep_test_md_replicates.py (candidatos do batch antigo Fase 4/5) — reconstruído por
# sequência real, não adivinhado.
REP1_DIR_OVERRIDE = {"RLREELKKAEEWLEKRRKEE": "forced_05"}
S1_ASP_RESID = 187  # outputs/structure/binding_site.json, receptor ACR157 (individual_sites[0])
S1_ASP_ATOMS = "name OD1 OD2"
OCCUPANCY_CUTOFF_A = 4.0

MD_DIR = Path("outputs/md")
REPLICATES_DIR = Path("outputs/md_replicates")
OUT_DIR = Path("outputs/persistence_deep")


def _rep1_paths(seq: str) -> tuple[Path, Path] | None:
    run_dir = MD_DIR / REP1_DIR_OVERRIDE.get(seq, seq)
    tpr, xtc = run_dir / "md.tpr", run_dir / "md.xtc"
    if tpr.exists() and xtc.exists():
        return tpr, xtc
    return None


def _rep_paths(seq: str, rep: str) -> tuple[Path, Path] | None:
    if rep == "rep1":
        return _rep1_paths(seq)
    run_dir = REPLICATES_DIR / seq / rep
    tpr, xtc = run_dir / "md.tpr", run_dir / "md.xtc"
    if tpr.exists() and xtc.exists():
        return tpr, xtc
    return None


def analyze_replicate(seq: str, tpr: Path, xtc: Path) -> dict:
    u = mda.Universe(str(tpr), str(xtc))
    protein = u.select_atoms("protein")
    n_receptor = len(protein.residues) - len(seq)
    if n_receptor <= 0:
        return {"error": f"contagem de residuos de proteina ({len(protein.residues)}) "
                          f"menor ou igual ao comprimento do peptideo ({len(seq)})"}

    receptor_residues = protein.residues[:n_receptor]
    peptide_residues = protein.residues[n_receptor:n_receptor + len(seq)]
    if len(peptide_residues) != len(seq):
        return {"error": f"esperava {len(seq)} residuos de peptideo, achou "
                          f"{len(peptide_residues)} (posicao sequencial nao bateu)"}

    s1_asp = receptor_residues[receptor_residues.resids == S1_ASP_RESID]
    if len(s1_asp) == 0:
        return {"error": f"resid {S1_ASP_RESID} (Asp S1) nao encontrado no receptor"}
    s1_asp_atoms = s1_asp.atoms.select_atoms(S1_ASP_ATOMS)
    if len(s1_asp_atoms) == 0:
        return {"error": f"atomos {S1_ASP_ATOMS} nao encontrados no resid {S1_ASP_RESID}"}

    receptor_ca = receptor_residues.atoms.select_atoms("name CA")
    peptide_ca_ref = peptide_residues.atoms.select_atoms("name CA").positions.copy()

    distances_per_residue = {i: [] for i in range(len(seq))}
    local_rmsd_frames = []
    ref_receptor_ca = receptor_ca.positions.copy()

    from MDAnalysis.analysis import align, rms as mda_rms

    for ts in u.trajectory:
        for i, res in enumerate(peptide_residues):
            heavy = res.atoms.select_atoms("not name H*")
            if len(heavy) == 0 or len(s1_asp_atoms) == 0:
                continue
            d = np.min(mda.lib.distances.distance_array(heavy.positions, s1_asp_atoms.positions))
            distances_per_residue[i].append(float(d))
        # RMSD local: superpõe só nos Calpha do receptor, mede RMSD do peptídeo
        rot, _ = align.rotation_matrix(receptor_ca.positions - receptor_ca.positions.mean(axis=0),
                                        ref_receptor_ca - ref_receptor_ca.mean(axis=0))
        moved = (peptide_residues.atoms.select_atoms("name CA").positions
                 - receptor_ca.positions.mean(axis=0)) @ rot.T
        ref = peptide_ca_ref - ref_receptor_ca.mean(axis=0)
        local_rmsd_frames.append(float(np.sqrt(np.mean(np.sum((moved - ref) ** 2, axis=1)))) / 10.0)

    anchor_idx = find_anchor_residue(distances_per_residue)
    return {
        "anchor_residue_seq_idx": anchor_idx,
        "anchor_residue_aa": seq[anchor_idx],
        "occupancy_fraction": occupancy_fraction(distances_per_residue[anchor_idx], OCCUPANCY_CUTOFF_A),
        "n_frames": len(distances_per_residue[anchor_idx]),
        "local_rmsd_pocket_nm": round(float(np.mean(local_rmsd_frames)), 4) if local_rmsd_frames else None,
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = OUT_DIR / "persistence_summary.json"
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}

    for seq in CANDIDATES:
        seq_results = summary.setdefault(seq, {})
        for rep in ("rep1", "rep2", "rep3"):
            if rep in seq_results and "error" not in seq_results[rep]:
                print(f"[{seq}] {rep} ja processado, pulando")
                continue
            paths = _rep_paths(seq, rep)
            if paths is None:
                seq_results[rep] = {"error": "sem trajetoria real (.tpr/.xtc) preservada"}
                print(f"[{seq}] {rep}: sem trajetoria real, pulando")
                summary_path.write_text(json.dumps(summary, indent=2))
                continue
            tpr, xtc = paths
            try:
                result = analyze_replicate(seq, tpr, xtc)
            except Exception as e:
                result = {"error": str(e)}
            seq_results[rep] = result
            print(f"[{seq}] {rep}: {result}")
            summary_path.write_text(json.dumps(summary, indent=2))

    print(f"\nSalvo: {summary_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
git add scripts/deep_test_persistence.py
git commit -m "feat(persistence): script real de ocupancia P1-AspS1 + RMSD local (Frente 2)"
```

### Task 3: Validar contra SRTRR antes de rodar o TOP-13 completo

**Files:**
- None novos — execução de validação no servidor.

- [ ] **Step 1: Push e pull no servidor**

```bash
git push origin main
```
```bash
ssh eulalio@200.235.143.10 "cd ~/design-inibidores && git pull"
```

- [ ] **Step 2: Rodar só SRTRR (editar `CANDIDATES` temporariamente ou usar `python -c`)**

Run (no servidor, dentro de `screen -S persistence_validate`):
```bash
conda run -n protein_design_env python -c "
from scripts.deep_test_persistence import analyze_replicate, _rep_paths
tpr, xtc = _rep_paths('SRTRR', 'rep1')
print(analyze_replicate('SRTRR', tpr, xtc))
"
```

Expected: `anchor_residue_aa` deve ser `R` ou `A`/`R`/`R` (SRTRR = S-R-T-R-R, índices 1/3/4 são Arg) — **não pode ser `S` ou `T`** (não-básicos); `occupancy_fraction` deve ser alto (>0.5), consistente com SRTRR já confirmado como o candidato mais estável e reprodutível (Tabela 9n, DP=0,025nm). Se o resíduo âncora vier errado (S ou T) ou a ocupância vier muito baixa (<0.1) para um candidato já sabido estável, **parar e investigar antes de rodar os 13** — sinal de bug na seleção de átomos.

- [ ] **Step 3: Se validação passar, commit de confirmação**

```bash
git commit --allow-empty -m "test(persistence): valida SRTRR (âncora=Arg, ocupância alta) antes do TOP-13 completo"
```

### Task 4: Rodar Frente 2 completa no servidor e atualizar artigo + memória

**Files:**
- Modify: `artigo_resultados.md` (nova subseção 3.11g)
- Modify: `../../../projects/C--Users-eulal--claude-design-inibidores/memory/project_design_inibidores.md`

- [ ] **Step 1: Rodar no servidor (screen, sobrevive a queda de conexão)**

```bash
ssh eulalio@200.235.143.10 "cd ~/design-inibidores && screen -dmS persistence_full bash -c 'source ~/miniforge3/etc/profile.d/conda.sh && conda activate protein_design_env && python -m scripts.deep_test_persistence > outputs/persistence_run.log 2>&1; echo DONE >> outputs/persistence_run.log'"
```

- [ ] **Step 2: Monitorar até `DONE`** (mesmo padrão de monitor incremental por offset usado para o `deep_test_md_replicates.py` nesta sessão — poll via `wc -l`/`tail -n +N` no `outputs/persistence_run.log`, não `tail -n 5` fixo).

- [ ] **Step 3: Puxar `persistence_summary.json` e escrever Tabela nova em `artigo_resultados.md`** (Seção 3.11g, mesmo estilo das Tabelas 9k-9n): colunas Sequência | Resíduo âncora real | Ocupância (%) | RMSD local do bolso (nm) | Interpretação.

- [ ] **Step 4: Atualizar `project_design_inibidores.md`** com o achado real (quais candidatos têm ocupância alta vs. baixa, se algum candidato "estável" por RMSD global na verdade tem ocupância baixa — i.e., balança mas sai do sítio).

- [ ] **Step 5: Commit + push + pull servidor**

```bash
git add artigo_resultados.md "../../../projects/C--Users-eulal--claude-design-inibidores/memory/project_design_inibidores.md"
git commit -m "docs(artigo): Seção 3.11g — persistência competitiva real (ocupância P1-AspS1)"
git push origin main
```
```bash
ssh eulalio@200.235.143.10 "cd ~/design-inibidores && git pull"
```

---

## Frente 3 — Subsítios S2'/S3' Canônicos

### Task 5: Definir resíduos S2'/S3' operacionalmente (heurística geométrica+sequencial)

**Files:**
- Create: `scripts/s2s3_utils.py`
- Test: `tests/test_s2s3_utils.py`

**Interfaces:**
- Produces: `define_s2s3_residues(binding_site: dict) -> list[int]` — usada pela Task 6.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_s2s3_utils.py
from scripts.s2s3_utils import define_s2s3_residues

def test_define_s2s3_residues_acr157_real_data():
    # Dado real de outputs/structure/binding_site.json, individual_sites[0] (ACR157)
    binding_site = {
        "triad_resseqs": {"HIS": 46, "ASP": 91, "SER": 203},
        "s1_asp_resseq": 187,
        "hotspot_resseqs": [44, 45, 46, 47, 83, 88, 91, 92, 188, 189, 201, 202, 203, 204, 218],
    }
    # Ser+1..Ser+15 = 204..218, excluindo vizinhança do S1 Asp (187 +-2 = 185-189)
    # e do proprio catalitico (201-203) -> sobra 204 e 218 no hotspot real
    assert define_s2s3_residues(binding_site) == [204, 218]

def test_define_s2s3_residues_excludes_s1_neighborhood():
    binding_site = {
        "triad_resseqs": {"HIS": 10, "ASP": 15, "SER": 20},
        "s1_asp_resseq": 25,  # dentro de Ser+1..Ser+15 (21-35) -> 25 +-2 (23-27) excluido
        "hotspot_resseqs": [21, 25, 26, 35, 40],
    }
    # 21: sobrevive (fora da zona 23-27). 25/26: excluidos (dentro da zona).
    # 35: sobrevive (ultimo residuo da janela Ser+15, fora da zona). 40: fora da janela.
    assert define_s2s3_residues(binding_site) == [21, 35]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `conda run -n protein_design_env python -m pytest tests/test_s2s3_utils.py -v`
Expected: FAIL com `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

```python
# scripts/s2s3_utils.py
"""Definição operacional dos subsítios S2'/S3' canônicos (Frente 3).

Sem estrutura cristalográfica com substrato ligado nos receptores deste projeto
(modelos AlphaFold/estruturais), não há posição canônica pronta. Heurística
geométrica+sequencial (aprovada pelo usuário, ver spec 2026-07-19): dos resíduos
já no hotspot 8 A de cada receptor, os que ficam na vizinhança sequencial da Ser
catalítica (Ser+1 a Ser+15) e fora da vizinhança imediata do Asp do bolso S1
(+-2 resíduos) são candidatos a revestir S2'/S3'. Ressalva explícita: é
aproximação, não validação estrutural externa — mesmo tratamento dado ao
mapeamento fraco do sítio S'2 no projeto irmão analise-alosterica.
"""

S2S3_WINDOW = 15
S1_EXCLUSION_RADIUS = 2


def define_s2s3_residues(binding_site: dict) -> list:
    ser = binding_site["triad_resseqs"]["SER"]
    s1_asp = binding_site["s1_asp_resseq"]
    hotspot = binding_site["hotspot_resseqs"]
    s1_zone = set(range(s1_asp - S1_EXCLUSION_RADIUS, s1_asp + S1_EXCLUSION_RADIUS + 1))
    candidates = [
        r for r in hotspot
        if ser < r <= ser + S2S3_WINDOW and r not in s1_zone
    ]
    return sorted(candidates)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `conda run -n protein_design_env python -m pytest tests/test_s2s3_utils.py -v`
Expected: PASS (2 testes)

- [ ] **Step 5: Commit**

```bash
git add scripts/s2s3_utils.py tests/test_s2s3_utils.py
git commit -m "feat(s2s3): heurística geométrica+sequencial p/ subsítios S2'/S3' (Frente 3)"
```

### Task 6: Script multi-frame PLIP para contatos S2'/S3'

**Files:**
- Create: `scripts/deep_test_s2s3_subsites.py`

**Interfaces:**
- Consumes: `define_s2s3_residues` de `scripts/s2s3_utils.py` (Task 5); reusa `extract_last_frame`/`protonate` de `scripts/deep_test_plip.py` generalizados para múltiplos timepoints.
- Produces: `outputs/s2s3_deep/s2s3_summary.json` — schema:
  ```json
  {"SRTRR": {"rep1": {"frames_analisados": [1000, 3000, 5000, 7000, 9000],
                        "contato_s2s3_fracao": 0.4, "residuos_alvo": [204, 218]}}}
  ```

- [ ] **Step 1: Write the script**

```python
# scripts/deep_test_s2s3_subsites.py
"""deep_test_s2s3_subsites.py — Frente 3: contatos reais com subsítios S2'/S3' canônicos.

Extrai múltiplos frames (1, 3, 5, 7, 9 ns) das trajetórias JÁ EXISTENTES do TOP-13
(rep1/rep2/rep3), roda PLIP em cada um (mesmo padrão validado em deep_test_plip.py:
trjconv -pbc mol -center + obabel -h + plip --peptides B), e conta em quantos desses
frames o peptídeo faz contato real (qualquer bloco PLIP: H-bond, hidrofóbico,
salt-bridge) com os resíduos S2'/S3' definidos por scripts/s2s3_utils.py.

Uso: conda run -n protein_design_env python -m scripts.deep_test_s2s3_subsites
"""
import json
import re
import subprocess
from pathlib import Path

from scripts.s2s3_utils import define_s2s3_residues

GMX = "/home/eulalio/miniforge3/envs/md-gromacs/bin/gmx_mpi"
FRAME_TIMES_PS = [1000, 3000, 5000, 7000, 9000]  # 1,3,5,7,9 ns dentro dos 10 ns de produção

CANDIDATES = [
    "SRTRR", "HRPRRPR", "RLREELKKAEEWLEKRRKEE", "SEEEVLAANEAYAAAHTAYN",
    "SALASIAAHQATFLAYLESK", "MGSLTAYLEAYAAENAAALA", "MGYLTAYHQALAAQNAALLA",
    "SARESIKKAYKTFLERYKKL", "VRYRR", "VRTRR", "VRRPR", "HRPRRSR", "HRPRRPK",
]
REP1_DIR_OVERRIDE = {"RLREELKKAEEWLEKRRKEE": "forced_05"}

BINDING_SITE = json.loads(Path("outputs/structure/binding_site.json").read_text())
S1_TARGET = BINDING_SITE["individual_sites"][0]  # ACR157, receptor primário usado no MD
S2S3_RESIDUES = define_s2s3_residues(S1_TARGET)

MD_DIR = Path("outputs/md")
REPLICATES_DIR = Path("outputs/md_replicates")
OUT_DIR = Path("outputs/s2s3_deep")


def _rep_dir(seq: str, rep: str) -> Path | None:
    if rep == "rep1":
        d = MD_DIR / REP1_DIR_OVERRIDE.get(seq, seq)
    else:
        d = REPLICATES_DIR / seq / rep
    if (d / "md.tpr").exists() and (d / "md.xtc").exists():
        return d
    return None


def extract_frame(run_dir: Path, time_ps: int, out_dir: Path) -> Path | None:
    frame_pdb = out_dir / f"frame_{time_ps}.pdb"
    if frame_pdb.exists() and frame_pdb.stat().st_size > 1000:
        return frame_pdb
    cmd = (f"printf '1\\n0\\n' | {GMX} trjconv -s {run_dir / 'md.tpr'} -f {run_dir / 'md.xtc'} "
           f"-o {frame_pdb} -pbc mol -center -dump {time_ps}")
    proc = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=180)
    if not frame_pdb.exists() or frame_pdb.stat().st_size < 1000:
        print(f"  trjconv falhou em {time_ps}ps: {proc.stderr[-300:]}")
        return None
    return frame_pdb


def protonate(frame_pdb: Path) -> Path | None:
    prot_pdb = frame_pdb.with_name(frame_pdb.stem + "_protonated.pdb")
    if prot_pdb.exists() and prot_pdb.stat().st_size > 1000:
        return prot_pdb
    proc = subprocess.run(["obabel", str(frame_pdb), "-O", str(prot_pdb), "-h"],
                           capture_output=True, text=True, timeout=60)
    if not prot_pdb.exists() or prot_pdb.stat().st_size < 1000:
        print(f"  obabel falhou: {proc.stderr[-300:]}")
        return None
    return prot_pdb


def check_s2s3_contact(prot_pdb: Path) -> bool | None:
    out_dir = prot_pdb.parent
    proc = subprocess.run(["plip", "-f", str(prot_pdb), "--peptides", "B", "-o", str(out_dir), "-t"],
                           capture_output=True, text=True, timeout=180)
    reports = list(out_dir.glob(f"{prot_pdb.stem}*_report.txt"))
    if not reports:
        print(f"  PLIP falhou: rc={proc.returncode} {proc.stderr[-300:]}")
        return None
    text = reports[0].read_text(errors="ignore")
    # Contato real com qualquer resíduo S2'/S3': procurar o número do resíduo
    # (coluna RESNR do PLIP) nas linhas de tabela de interação.
    for resnum in S2S3_RESIDUES:
        if re.search(rf"\b{resnum}\b", text):
            return True
    return False


def analyze_replicate(seq: str, rep: str, run_dir: Path) -> dict:
    out_dir = OUT_DIR / seq / rep
    out_dir.mkdir(parents=True, exist_ok=True)
    contacts = []
    for t in FRAME_TIMES_PS:
        frame = extract_frame(run_dir, t, out_dir)
        if frame is None:
            continue
        prot = protonate(frame)
        if prot is None:
            continue
        c = check_s2s3_contact(prot)
        if c is not None:
            contacts.append(c)
    if not contacts:
        return {"error": "nenhum frame processado com sucesso"}
    return {
        "frames_analisados": FRAME_TIMES_PS[:len(contacts)],
        "contato_s2s3_fracao": sum(contacts) / len(contacts),
        "residuos_alvo": S2S3_RESIDUES,
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Residuos S2'/S3' (heuristica real, receptor ACR157): {S2S3_RESIDUES}")
    summary_path = OUT_DIR / "s2s3_summary.json"
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}

    for seq in CANDIDATES:
        seq_results = summary.setdefault(seq, {})
        for rep in ("rep1", "rep2", "rep3"):
            if rep in seq_results and "error" not in seq_results[rep]:
                print(f"[{seq}] {rep} ja processado, pulando")
                continue
            run_dir = _rep_dir(seq, rep)
            if run_dir is None:
                seq_results[rep] = {"error": "sem trajetoria real (.tpr/.xtc) preservada"}
                summary_path.write_text(json.dumps(summary, indent=2))
                continue
            print(f"[{seq}] {rep}...")
            seq_results[rep] = analyze_replicate(seq, rep, run_dir)
            summary_path.write_text(json.dumps(summary, indent=2))
            print(f"[{seq}] {rep}: {seq_results[rep]}")

    print(f"\nSalvo: {summary_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
git add scripts/deep_test_s2s3_subsites.py
git commit -m "feat(s2s3): PLIP multi-frame real p/ contatos S2'/S3' (Frente 3)"
```

### Task 7: Rodar Frente 3 no servidor e atualizar artigo + memória

**Files:**
- Modify: `artigo_resultados.md` (nova subseção 3.11h)
- Modify: `project_design_inibidores.md`

- [ ] **Step 1: Push, pull, rodar em screen** (mesmo padrão da Task 4)

```bash
git push origin main
```
```bash
ssh eulalio@200.235.143.10 "cd ~/design-inibidores && git pull && screen -dmS s2s3_full bash -c 'source ~/miniforge3/etc/profile.d/conda.sh && conda activate protein_design_env && python -m scripts.deep_test_s2s3_subsites > outputs/s2s3_run.log 2>&1; echo DONE >> outputs/s2s3_run.log'"
```

- [ ] **Step 2: Monitorar até `DONE`** (mesmo padrão de monitor incremental por offset).

- [ ] **Step 3: Escrever Tabela nova em `artigo_resultados.md`** (Seção 3.11h): Sequência | Fração de frames com contato S2'/S3' | Resíduos-alvo reais | Interpretação — com a ressalva explícita da heurística (não é validação estrutural externa).

- [ ] **Step 4: Atualizar `project_design_inibidores.md`**.

- [ ] **Step 5: Commit + push + pull servidor**

```bash
git add artigo_resultados.md "../../../projects/C--Users-eulal--claude-design-inibidores/memory/project_design_inibidores.md"
git commit -m "docs(artigo): Seção 3.11h — contatos reais S2'/S3' (heurística geométrica)"
git push origin main
```
```bash
ssh eulalio@200.235.143.10 "cd ~/design-inibidores && git pull"
```

---

## Frente 4 — Assinatura Digital de Interação

### Task 8: Síntese em tabela (sem script novo, conforme spec)

**Files:**
- Modify: `artigo_resultados.md` (nova subseção 3.11i)

- [ ] **Step 1: Ler os 3 JSONs reais já gerados** — `outputs/persistence_deep/persistence_summary.json` (Task 4), `outputs/s2s3_deep/s2s3_summary.json` (Task 7), e a Tabela 9m já existente (contato com tríade catalítica, `outputs/plip_deep/plip_deep_summary.json`).

- [ ] **Step 2: Montar tabela única** para os 4 candidatos reprodutivelmente estáveis (SRTRR, VRYRR, VRRPR, HRPRRPR) + `SEEEVLAANEAYAAAHTAYN` (caso não-canônico): colunas Sequência | Contato tríade (His/Asp/Ser) | Ocupância P1-AspS1 (%) | RMSD local do bolso | Contato S2'/S3' (%) — nenhuma célula inferida, só o que os 3 JSONs mostrarem.

- [ ] **Step 3: Escrever parágrafo de interpretação** apontando quais contatos são comuns aos 4 estáveis vs. ausentes nos marginais/alta-variância — sem extrapolar além do que os números mostrarem.

- [ ] **Step 4: Commit + push + pull servidor**

```bash
git add artigo_resultados.md
git commit -m "docs(artigo): Seção 3.11i — assinatura digital de interação (síntese Frentes 2+3)"
git push origin main
```
```bash
ssh eulalio@200.235.143.10 "cd ~/design-inibidores && git pull"
```

---

## Frente 1 — Expansão Taxonômica (3 novas espécies)

### Task 9: Buscar accessions UniProt reais para as 3 espécies

**Files:**
- Modify: `scripts/search_uniprot_trypsins.py` (adicionar 3 espécies à lista `SPECIES`)

- [ ] **Step 1: Editar a lista `SPECIES`**

```python
# scripts/search_uniprot_trypsins.py — adicionar ao final da lista SPECIES existente:
SPECIES = [
    "Bombyx mori",
    "Manduca sexta",
    "Plutella xylostella",
    "Spodoptera litura",
    "Spodoptera frugiperda",
    "Ostrinia nubilalis",
    "Diatraea saccharalis",
    "Heliothis virescens",
    "Chrysodeixis includens",
]
```

- [ ] **Step 2: Rodar no servidor e registrar accessions reais escolhidos**

```bash
ssh eulalio@200.235.143.10 "cd ~/design-inibidores && git pull && conda run -n protein_design_env python scripts/search_uniprot_trypsins.py 2>&1 | tail -60"
```

Ler a saída (formato já validado: `ACC | nome | len=N | tipo | AlphaFoldDB=True/False`) e escolher, para cada uma das 3 espécies, a entrada com padrão de tripsina digestiva (~250-270aa) e prioridade para `AlphaFoldDB=True` — mesmo critério já usado nas 6 espécies anteriores. Anotar os 3 accessions escolhidos no commit da Task 10 (não fabricar/adivinhar accession sem rodar a busca real).

- [ ] **Step 3: Commit**

```bash
git add scripts/search_uniprot_trypsins.py
git commit -m "feat(R3): adiciona D. saccharalis/H. virescens/C. includens à busca UniProt"
```

### Task 10: Baixar estruturas e mapear tríade catalítica

**Files:**
- Modify: `scripts/fetch_lepidoptera_af.py` (adicionar as 3 espécies com os accessions reais escolhidos na Task 9)
- Modify: `scripts/map_lepidoptera_sites.py` (idem)

- [ ] **Step 1: Editar `SPECIES` em `fetch_lepidoptera_af.py`** com os 3 accessions reais confirmados na Task 9 (formato idêntico às 6 entradas existentes: `"Tag": ("ACCESSION", "Nome científico", "descrição")`).

- [ ] **Step 2: Rodar no servidor**

```bash
ssh eulalio@200.235.143.10 "cd ~/design-inibidores && git pull && conda run -n protein_design_env python scripts/fetch_lepidoptera_af.py"
```

Se alguma espécie não tiver entrada no AlphaFold DB (já ocorreu 2x com *H. armigera*), aplicar o mesmo fallback ESMFold já usado (`api.esmatlas.com/foldSequence/v1/pdb/`, ver `project_design_inibidores.md` seção "Expansão R3" para o padrão exato de chamada) — criar `scripts/fetch_esmfold_fallback.py` reusando a mesma lógica só se necessário (não escrever esse script preventivamente se as 3 espécies tiverem AlphaFold DB real).

- [ ] **Step 3: Editar `STRUCTS` em `map_lepidoptera_sites.py`** com as 3 novas entradas, mesmo formato das 6 existentes.

- [ ] **Step 4: Rodar no servidor**

```bash
ssh eulalio@200.235.143.10 "cd ~/design-inibidores && conda run -n protein_design_env python scripts/map_lepidoptera_sites.py"
```

Verificar na saída que a tríade catalítica real foi encontrada para as 3 (`triade=... S1_Asp=... centro=...`) — se alguma falhar (`FALHOU_TRIADE`), reportar como tal na memória, não inventar tríade.

- [ ] **Step 5: Commit**

```bash
git add scripts/fetch_lepidoptera_af.py scripts/map_lepidoptera_sites.py
git commit -m "feat(R3): baixa estruturas + mapeia tríade catalítica real das 3 novas espécies"
```

### Task 11: Docking real do TOP-13 contra as 3 novas espécies

**Files:**
- Modify: `scripts/dock_cross_species.py`

- [ ] **Step 1: Atualizar `SPECIES` e `CANDIDATES`**

```python
# scripts/dock_cross_species.py — adicionar ao dict SPECIES (usando as tags/accessions
# reais confirmados nas Tasks 9-10):
    "Dsaccharalis": ("data-nontargets/Dsaccharalis-<ACC>-AlphaFold.pdb", "outputs/structure_dsaccharalis/binding_site.json"),
    "Hvirescens": ("data-nontargets/Hvirescens-<ACC>-AlphaFold.pdb", "outputs/structure_hvirescens/binding_site.json"),
    "Cincludens": ("data-nontargets/Cincludens-<ACC>-AlphaFold.pdb", "outputs/structure_cincludens/binding_site.json"),

# CANDIDATES -> TOP-13 completo (Tabela 9n), substituindo a lista atual de 16:
CANDIDATES = [
    "SRTRR", "HRPRRPR", "RLREELKKAEEWLEKRRKEE", "SEEEVLAANEAYAAAHTAYN",
    "SALASIAAHQATFLAYLESK", "MGSLTAYLEAYAAENAAALA", "MGYLTAYHQALAAQNAALLA",
    "SARESIKKAYKTFLERYKKL", "VRYRR", "VRTRR", "VRRPR", "HRPRRSR", "HRPRRPK",
]
```

(`<ACC>` deve ser substituído pelo accession UniProt real confirmado na Task 9 — o script é resume-safe por espécie, então as 8 espécies já dockadas anteriormente não serão reprocessadas, mesmo com a mudança de `CANDIDATES` de 16 para 13: adicionar um guard explícito para não quebrar o resume-safe das espécies antigas — ver Step 2.)

- [ ] **Step 2: Verificar compatibilidade do resume-safe com a mudança de `CANDIDATES`**

O código já filtra `missing = [s for s in CANDIDATES if results.get(s) is None]` — como o TOP-13 é subconjunto do antigo `CANDIDATES` de 16 (exceto `RLRAIWLEAEKLLEERRKKK`, `RVKDQWLEAEKLLEERRKKK`, `KPKFKVR`, que saem da lista), rodar de novo nas 8 espécies antigas não vai gerar chamadas Vina novas para esses 13 (já têm `results[seq]` real salvo) nem vai apagar os 3 resultados removidos do dict (ficam órfãos no `results.json` de cada espécie antiga, inofensivo). Confirmar isso rodando primeiro numa espécie já concluída antes de ir para as 3 novas:

```bash
ssh eulalio@200.235.143.10 "cd ~/design-inibidores && git pull && conda run -n protein_design_env python -c \"
import json
r = json.loads(open('outputs/cross_species_docking/Msexta/results.json').read())
print('já tem os 13 do TOP-13?', all(seq in r for seq in ['SRTRR','HRPRRPR','RLREELKKAEEWLEKRRKEE','SEEEVLAANEAYAAAHTAYN','SALASIAAHQATFLAYLESK','MGSLTAYLEAYAAENAAALA','MGYLTAYHQALAAQNAALLA','SARESIKKAYKTFLERYKKL','VRYRR','VRTRR','VRRPR','HRPRRSR','HRPRRPK']))
\""
```

Expected: `True` — se `False`, algum dos 13 nunca foi dockado nas 8 espécies antigas, e vai gerar Vina novo nessa espécie também (não é erro, só custo extra esperado).

- [ ] **Step 3: Rodar em screen no servidor (docking novo só para as 3 espécies novas, ~39 dockings)**

```bash
ssh eulalio@200.235.143.10 "cd ~/design-inibidores && screen -dmS crossspecies_r3b bash -c 'source ~/miniforge3/etc/profile.d/conda.sh && conda activate protein_design_env && python scripts/dock_cross_species.py > outputs/crossspecies_r3b_run.log 2>&1; echo DONE >> outputs/crossspecies_r3b_run.log'"
```

- [ ] **Step 4: Monitorar até `DONE`**, puxar `outputs/cross_species_docking/all_cross_species_results.json`.

- [ ] **Step 5: Commit**

```bash
git add scripts/dock_cross_species.py
git commit -m "feat(R3): docking real TOP-13 x 3 novas espécies (D. saccharalis/H. virescens/C. includens)"
```

### Task 12: Consolidar matriz 13×11 e atualizar artigo + memória

**Files:**
- Modify: `artigo_resultados.md` (nova subseção, matriz consolidada)
- Modify: `project_design_inibidores.md`

- [ ] **Step 1: Ler os resultados reais das 3 novas espécies** (`all_cross_species_results.json`) e montar a matriz 13×11 completa (8 espécies antigas + 3 novas), mesmo formato da matriz 13×8 já existente na memória do projeto.

- [ ] **Step 2: Escrever nova subseção no artigo** com a matriz completa + interpretação (mesmo padrão da Seção "Cross-species CONCLUÍDO" já escrita para as 8 espécies — nenhuma espécie deve ser tratada como "imune" sem dado real que sustente isso).

- [ ] **Step 3: Atualizar `project_design_inibidores.md`** com o R3 agora fechado (9 espécies-alvo do requisito original, mais as 2 extras já testadas antes = 11 total).

- [ ] **Step 4: Commit + push + pull servidor**

```bash
git add artigo_resultados.md "../../../projects/C--Users-eulal--claude-design-inibidores/memory/project_design_inibidores.md"
git commit -m "docs(artigo): matriz cross-species 13x11 — R3 completo (trio pendente fechado)"
git push origin main
```
```bash
ssh eulalio@200.235.143.10 "cd ~/design-inibidores && git pull"
```

---

## Self-Review (spec coverage)

- **Frente 1** (eficácia ampla/taxonomia): Tasks 9-12. ✓
- **Frente 2** (persistência competitiva): Tasks 1-4. ✓
- **Frente 3** (S2'/S3'): Tasks 5-7. ✓
- **Frente 4** (fingerprint): Task 8. ✓
- **Ordem de execução aprovada** (2+3 → 4 → 1): plano segue essa ordem nas seções acima. ✓
- **Nunca fabricar dado**: cada task de execução real trata explicitamente o caso "sem trajetória/estrutura real" como erro reportado, não valor inferido. ✓
- **Atualização de artigo/memória por frente**: presente em Tasks 4, 7, 8, 12. ✓
- **Checkpoints revisáveis em screen**: Tasks 4, 7, 11 usam `screen -dmS` + log com `DONE`, resume-safe. ✓

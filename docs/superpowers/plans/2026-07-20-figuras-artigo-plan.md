# Figuras do Artigo — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Gerar as 4 figuras aprovadas na spec (`docs/superpowers/specs/2026-07-20-figuras-word-apresentacao-design.md`) a partir de dado real puxado do servidor, em `outputs/figuras_artigo/`, prontas para uso no artigo Word e na apresentação (entregáveis futuros).

**Architecture:** Scripts Python locais (rodam no Windows, não no servidor — matplotlib não precisa de GROMACS/GPU) que buscam JSON real via SSH (`subprocess` + `ssh eulalio@200.235.143.10 "cat <path>"`, mesmo padrão já usado no resto do projeto), computam estatísticas/classificações a partir do dado bruto (nunca hardcodam número final), e renderizam PNG estático via matplotlib. Um módulo compartilhado (`scripts/figuras_utils.py`) centraliza a paleta e o helper de busca remota.

**Tech Stack:** Python 3.13 local (Windows), matplotlib 3.10, numpy — todos já confirmados instalados nesta sessão.

## Global Constraints

- Nunca fabricar dado — todo número vem de um JSON real buscado do servidor nesta execução, nunca copiado do Markdown já publicado nem hardcodado como valor final.
- Paleta e princípios exatamente como documentados na spec: paleta categórica em ordem fixa (azul `#2a78d6`, verde `#008300`, magenta `#e87ba4`, amarelo `#eda100`, aqua `#1baf7a`, laranja `#eb6834`, violeta `#4a3aa7`, vermelho `#e34948`); status reservado (bom `#0ca30c`, atenção `#fab219`, crítico `#d03b3b`); sequencial azul 100→700; sem eixo duplo em nenhuma figura; grades recessivas (`#e1e0d9`); tipografia sans-serif do sistema.
- Saída: `outputs/figuras_artigo/fig{1..4}_*.png`, 300 dpi, fundo branco.
- Cada figura precisa ser lida (Read da imagem) e conferida visualmente antes de a task ser considerada concluída; os valores usados devem ser logados no console e conferidos manualmente contra as Tabelas 9n/9o/9r/9q já publicadas em `artigo_resultados.md`.
- Comando SSH real (confirmado nesta sessão): `ssh -o ConnectTimeout=15 eulalio@200.235.143.10 "cat <caminho>"` — servidor requer VPN da UFV ativa.

## Verificação técnica já feita nesta sessão (base para o código abaixo)

Fontes de dado real confirmadas por inspeção direta no servidor:

- **Fig 1 (réplicas MD)**: rep1 histórica em `outputs/md/md_results.json` (dict chaveado por sequência completa, campo `rmsd_avg_nm`) — confirmado presente para os 13 candidatos do TOP-13. rep2/rep3 em `outputs/md_replicates/replicates_summary.json` (`{seq: {"replicates": {"rep2": {...}, "rep3": {...}}}}`, mesmo campo `rmsd_avg_nm`).
- **Fig 2 (ocupância S1)**: `outputs/persistence_deep/persistence_summary.json` (`{seq: {"rep1"/"rep2"/"rep3": {"occupancy_fraction_4A"/"5A"/"6A": float, ...} ou {"error": str}}}`) — todos os 13 candidatos têm n=3 completo (gap fechado nesta sessão).
- **Fig 3 (cross-species)**: `outputs/cross_species_docking/all_cross_species_results.json` (`{especie: {seq: vina_float_ou_null}}`), 11 espécies × 13 candidatos, 143/143 valores reais confirmados.
- **Fig 4 (fingerprint)**: tríade catalítica via `outputs/plip_deep/plip_deep_summary.json` (`{seq: {"contacts_his_any"/"contacts_asp_any"/"contacts_ser_any": bool}}`) para `SRTRR`/`VRYRR`/`VRRPR`/`HRPRRPR` — confirmado `True` nos 3 campos para os 4. `SEEEVLAANEAYAAAHTAYN` é exceção documentada: seu contato de tríade (`True`/`True`/`True`) vem da Seção 3.10b do artigo (PLIP histórico, mecanismo via π-cátion Tyr12), sem JSON separado preservado no servidor — hardcoded no script com comentário explícito citando a fonte (não é fabricação: é um resultado real já publicado, só sem arquivo JSON de apoio). Ocupância 6Å e RMSD local vêm de `persistence_summary.json` (mesmo de Fig 2). Contato S2'/S3' vem de `outputs/s2s3_deep/s2s3_summary.json` (`{seq: {"rep1"/"rep2"/"rep3": {"contato_s2s3_fracao": float} ou {"error": str}}}`).
- **Classificação de estabilidade (Fig 1)**: regra já documentada em `artigo_resultados.md` — ESTÁVEL REPRODUTÍVEL = RMSD médio n=3 < 0,30 nm **e** DP < 0,05 nm; marginal reprodutível = DP < 0,10 nm (independente da média); ALTA VARIÂNCIA = DP ≥ 0,15 nm. Implementar como função pura a partir do mean/DP real computado, nunca hardcodar a classificação por candidato.
- **TOP-13** (ordem usada em todos os scripts): `SRTRR, HRPRRPR, RLREELKKAEEWLEKRRKEE, SEEEVLAANEAYAAAHTAYN, SALASIAAHQATFLAYLESK, MGSLTAYLEAYAAENAAALA, MGYLTAYHQALAAQNAALLA, SARESIKKAYKTFLERYKKL, VRYRR, VRTRR, VRRPR, HRPRRSR, HRPRRPK`.
- **11 espécies cross-species** (ordem): `Agemmatalis, Harmigera, Msexta, Bmori, Pxylostella, Slitura, Sfrugiperda, Onubilalis, Dsaccharalis, Hvirescens, Cincludens` (chaves reais em `all_cross_species_results.json`).

---

## Task 1: Módulo compartilhado — paleta + busca remota

**Files:**
- Create: `scripts/figuras_utils.py`
- Test: `tests/test_figuras_utils.py`

**Interfaces:**
- Produces: `fetch_remote_json(remote_path: str) -> dict`, `classify_stability(mean_nm: float, std_nm: float) -> str`, module-level constants `CATEGORICAL`, `STATUS`, `SEQUENTIAL_BLUE_3`, `SEQUENTIAL_BLUE_FULL`, `GRID_COLOR`, `TOP13` (list), `SPECIES_ORDER` (list) — usados por todas as Tasks 2-5.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_figuras_utils.py
from scripts.figuras_utils import classify_stability

def test_classify_estavel_reprodutivel():
    assert classify_stability(mean_nm=0.214, std_nm=0.025) == "ESTAVEL_REPRODUTIVEL"

def test_classify_marginal_por_dp_baixo_mas_media_alta():
    # SEEEVLAANEAYAAAHTAYN real: media 0.729, DP 0.041 -> falha o teto de media (<0.30)
    assert classify_stability(mean_nm=0.729, std_nm=0.041) == "MARGINAL_REPRODUTIVEL"

def test_classify_alta_variancia():
    # RLREELKKAEEWLEKRRKEE real: media 0.810, DP 0.606
    assert classify_stability(mean_nm=0.810, std_nm=0.606) == "ALTA_VARIANCIA"

def test_classify_marginal_dp_medio():
    # HRPRRPK real: media 0.421, DP 0.092 -> DP<0.10 mas nao <0.05, e media>0.30
    assert classify_stability(mean_nm=0.421, std_nm=0.092) == "MARGINAL_REPRODUTIVEL"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_figuras_utils.py -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'scripts.figuras_utils'`

- [ ] **Step 3: Write minimal implementation**

```python
# scripts/figuras_utils.py
"""Módulo compartilhado para as figuras do artigo (2026-07-20).

Paleta e princípios da skill dataviz deste ambiente (references/palette.md),
modo claro (destino é documento estático — Word/apresentação, não web).
"""
import json
import subprocess

SSH_HOST = "eulalio@200.235.143.10"

# Paleta categórica — ordem fixa, nunca ciclada.
CATEGORICAL = {
    "azul": "#2a78d6", "verde": "#008300", "magenta": "#e87ba4",
    "amarelo": "#eda100", "aqua": "#1baf7a", "laranja": "#eb6834",
    "violeta": "#4a3aa7", "vermelho": "#e34948",
}

# Status — reservado, nunca reusado como série categórica.
STATUS = {"bom": "#0ca30c", "atencao": "#fab219", "serio": "#ec835a", "critico": "#d03b3b"}

# Sequencial azul, 3 passos usados na Fig 2 (4/5/6 A, claro->escuro).
SEQUENTIAL_BLUE_3 = ["#86b6ef", "#3987e5", "#1c5cab"]  # steps 250/400/550

# Rampa sequencial completa (100->700) para o heatmap da Fig 3.
SEQUENTIAL_BLUE_FULL = [
    "#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7",
    "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b",
]

GRID_COLOR = "#e1e0d9"
AXIS_COLOR = "#c3c2b7"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
TEXT_MUTED = "#898781"

TOP13 = [
    "SRTRR", "HRPRRPR", "RLREELKKAEEWLEKRRKEE", "SEEEVLAANEAYAAAHTAYN",
    "SALASIAAHQATFLAYLESK", "MGSLTAYLEAYAAENAAALA", "MGYLTAYHQALAAQNAALLA",
    "SARESIKKAYKTFLERYKKL", "VRYRR", "VRTRR", "VRRPR", "HRPRRSR", "HRPRRPK",
]

SPECIES_ORDER = [
    "Agemmatalis", "Harmigera", "Msexta", "Bmori", "Pxylostella", "Slitura",
    "Sfrugiperda", "Onubilalis", "Dsaccharalis", "Hvirescens", "Cincludens",
]
SPECIES_LABELS = {
    "Agemmatalis": "A. gemmatalis", "Harmigera": "H. armigera", "Msexta": "M. sexta",
    "Bmori": "B. mori", "Pxylostella": "P. xylostella", "Slitura": "S. litura",
    "Sfrugiperda": "S. frugiperda", "Onubilalis": "O. nubilalis",
    "Dsaccharalis": "D. saccharalis", "Hvirescens": "H. virescens",
    "Cincludens": "C. includens",
}


def fetch_remote_json(remote_path: str) -> dict:
    """Busca um JSON real do servidor via SSH. Levanta RuntimeError explícito
    se a conexão ou o parse falhar — nunca retorna dado parcial/inferido."""
    result = subprocess.run(
        ["ssh", "-o", "ConnectTimeout=15", SSH_HOST, f"cat {remote_path}"],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"SSH falhou buscando {remote_path}: {result.stderr[-500:]}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"JSON invalido em {remote_path}: {e}\nstdout[:300]={result.stdout[:300]}")


def classify_stability(mean_nm: float, std_nm: float) -> str:
    """Mesma regra ja documentada em artigo_resultados.md (Secao 3.11f):
    ESTAVEL_REPRODUTIVEL = media<0.30nm E DP<0.05nm; MARGINAL_REPRODUTIVEL = DP<0.10nm
    (independente da media); ALTA_VARIANCIA = DP>=0.15nm."""
    if std_nm >= 0.15:
        return "ALTA_VARIANCIA"
    if std_nm < 0.05 and mean_nm < 0.30:
        return "ESTAVEL_REPRODUTIVEL"
    if std_nm < 0.10:
        return "MARGINAL_REPRODUTIVEL"
    return "ALTA_VARIANCIA"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_figuras_utils.py -v`
Expected: PASS (4 testes)

- [ ] **Step 5: Commit**

```bash
git add scripts/figuras_utils.py tests/test_figuras_utils.py
git commit -m "feat(figuras): paleta compartilhada + busca remota + classificacao de estabilidade"
```

---

## Task 2: Figura 1 — Réplicas MD n=3

**Files:**
- Create: `scripts/gerar_fig1_replicas_md.py`

**Interfaces:**
- Consumes: `fetch_remote_json`, `classify_stability`, `STATUS`, `TOP13`, `GRID_COLOR`, `TEXT_PRIMARY`, `TEXT_SECONDARY` de `scripts/figuras_utils.py` (Task 1).
- Produces: `outputs/figuras_artigo/fig1_replicas_md.png`.

- [ ] **Step 1: Write the script**

```python
# scripts/gerar_fig1_replicas_md.py
"""Figura 1 — RMSD real medio +/- DP (n=3) por candidato, réplicas MD.

Dado real: rep1 historica (outputs/md/md_results.json) + rep2/rep3
(outputs/md_replicates/replicates_summary.json). Classificacao computada pela
mesma regra ja publicada (nao hardcodada por candidato).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from scripts.figuras_utils import (
    GRID_COLOR, STATUS, TEXT_PRIMARY, TEXT_SECONDARY, TOP13, classify_stability,
    fetch_remote_json,
)

OUT_DIR = Path("outputs/figuras_artigo")
STATUS_LABEL = {
    "ESTAVEL_REPRODUTIVEL": "Estável reprodutível",
    "MARGINAL_REPRODUTIVEL": "Marginal reprodutível",
    "ALTA_VARIANCIA": "Alta variância",
}
STATUS_COLOR = {
    "ESTAVEL_REPRODUTIVEL": STATUS["bom"],
    "MARGINAL_REPRODUTIVEL": STATUS["atencao"],
    "ALTA_VARIANCIA": STATUS["critico"],
}
REFUTED = {"RLREELKKAEEWLEKRRKEE", "VRTRR"}  # recorde de estabilidade ja refutado (Tabela 9n)


def main():
    md_results = fetch_remote_json("~/design-inibidores/outputs/md/md_results.json")
    replicates = fetch_remote_json("~/design-inibidores/outputs/md_replicates/replicates_summary.json")

    rows = []
    for seq in TOP13:
        rep1 = md_results[seq]["rmsd_avg_nm"]
        rep2 = replicates[seq]["replicates"]["rep2"]["rmsd_avg_nm"]
        rep3 = replicates[seq]["replicates"]["rep3"]["rmsd_avg_nm"]
        vals = np.array([rep1, rep2, rep3])
        mean, std = float(vals.mean()), float(vals.std(ddof=1))
        status = classify_stability(mean, std)
        rows.append((seq, mean, std, status))
        print(f"{seq}: n=3 mean={mean:.4f} std={std:.4f} status={status}")

    rows.sort(key=lambda r: r[1])  # RMSD medio ascendente

    fig, ax = plt.subplots(figsize=(9, 6.5))
    y = np.arange(len(rows))
    means = [r[1] for r in rows]
    stds = [r[2] for r in rows]
    colors = [STATUS_COLOR[r[3]] for r in rows]
    labels = [r[0] if len(r[0]) <= 10 else r[0][:10] + "…" for r in rows]

    ax.barh(y, means, xerr=stds, color=colors, edgecolor="none", height=0.6,
            error_kw={"ecolor": TEXT_SECONDARY, "elinewidth": 1.2, "capsize": 3})

    for i, (seq, mean, std, status) in enumerate(rows):
        if seq in REFUTED:
            ax.annotate("recorde refutado (n=3)", xy=(mean + std + 0.02, i),
                        va="center", fontsize=8, color=TEXT_SECONDARY, style="italic")

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9, color=TEXT_PRIMARY)
    ax.set_xlabel("RMSD médio ± DP (nm), n=3 réplicas reais", color=TEXT_PRIMARY)
    ax.set_title("Estabilidade real por réplicas — TOP-13 (n=3)", color=TEXT_PRIMARY, fontsize=12)
    ax.grid(axis="x", color=GRID_COLOR, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(GRID_COLOR)

    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in STATUS_COLOR.values()]
    ax.legend(handles, STATUS_LABEL.values(), loc="lower right", frameon=False, fontsize=8)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "fig1_replicas_md.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, facecolor="white")
    print(f"\nSalvo: {out_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Rodar e conferir**

Run: `python -m scripts.gerar_fig1_replicas_md`
Expected: 13 linhas de log `SEQ: n=3 mean=... std=... status=...`, arquivo `outputs/figuras_artigo/fig1_replicas_md.png` criado.

Conferir manualmente 2 linhas do log contra a Tabela 9n de `artigo_resultados.md`: `SRTRR` deve dar mean≈0,214 std≈0,025 status=ESTAVEL_REPRODUTIVEL; `RLREELKKAEEWLEKRRKEE` deve dar mean≈0,810 std≈0,606 status=ALTA_VARIANCIA.

- [ ] **Step 3: Ler a imagem gerada**

Usar a ferramenta de leitura de imagem sobre `outputs/figuras_artigo/fig1_replicas_md.png` — checar: rótulos não cortados/sobrepostos, barra de erro visível, anotação "recorde refutado" aparece em RLREELKKAEEWLEKRRKEE e VRTRR, legenda de status legível.

- [ ] **Step 4: Commit**

```bash
git add scripts/gerar_fig1_replicas_md.py
git commit -m "feat(figuras): Fig 1 — réplicas MD n=3, RMSD real por candidato"
```

---

## Task 3: Figura 2 — Ocupância do bolso S1

**Files:**
- Create: `scripts/gerar_fig2_ocupancia_s1.py`

**Interfaces:**
- Consumes: `fetch_remote_json`, `SEQUENTIAL_BLUE_3`, `TOP13`, `GRID_COLOR`, `TEXT_PRIMARY`, `TEXT_SECONDARY` de `scripts/figuras_utils.py`.
- Produces: `outputs/figuras_artigo/fig2_ocupancia_s1.png`.

- [ ] **Step 1: Write the script**

```python
# scripts/gerar_fig2_ocupancia_s1.py
"""Figura 2 — Ocupancia real do bolso S1 (4/5/6 A), media n=3, por candidato.

Dado real: outputs/persistence_deep/persistence_summary.json. Reps com
{"error": ...} sao excluidos da media (nunca tratados como 0).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from scripts.figuras_utils import (
    GRID_COLOR, SEQUENTIAL_BLUE_3, TEXT_PRIMARY, TEXT_SECONDARY, TOP13, fetch_remote_json,
)

OUT_DIR = Path("outputs/figuras_artigo")
CUTOFFS = ["4A", "5A", "6A"]
CUTOFF_LABELS = ["4 Å", "5 Å", "6 Å"]


def main():
    data = fetch_remote_json("~/design-inibidores/outputs/persistence_deep/persistence_summary.json")

    rows = []
    for seq in TOP13:
        per_cutoff = {c: [] for c in CUTOFFS}
        for rep in ("rep1", "rep2", "rep3"):
            entry = data[seq].get(rep)
            if entry is None or "error" in entry:
                continue
            for c in CUTOFFS:
                per_cutoff[c].append(entry[f"occupancy_fraction_{c}"])
        means = {c: float(np.mean(v)) * 100 if v else None for c, v in per_cutoff.items()}
        rows.append((seq, means))
        print(f"{seq}: n={len(per_cutoff['4A'])} "
              f"4A={means['4A']:.1f}% 5A={means['5A']:.1f}% 6A={means['6A']:.1f}%")

    rows.sort(key=lambda r: r[1]["6A"], reverse=True)

    fig, ax = plt.subplots(figsize=(10, 6.5))
    x = np.arange(len(rows))
    width = 0.25
    for i, (cutoff, color, label) in enumerate(zip(CUTOFFS, SEQUENTIAL_BLUE_3, CUTOFF_LABELS)):
        vals = [r[1][cutoff] for r in rows]
        ax.bar(x + (i - 1) * width, vals, width=width, color=color, label=label, zorder=3)

    labels = [r[0] if len(r[0]) <= 10 else r[0][:10] + "…" for r in rows]
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8, color=TEXT_PRIMARY)
    ax.set_ylabel("Fração de frames com distância < corte (%)", color=TEXT_PRIMARY)
    ax.set_title("Ocupância real do bolso S1 — TOP-13 (n=3, 4/5/6 Å)", color=TEXT_PRIMARY, fontsize=12)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    vrrpr_idx = [r[0] for r in rows].index("VRRPR")
    ax.annotate("sai do bolso\n(cai entre réplicas)", xy=(vrrpr_idx, rows[vrrpr_idx][1]["6A"]),
                xytext=(vrrpr_idx, rows[vrrpr_idx][1]["6A"] + 15),
                ha="center", fontsize=8, color=TEXT_SECONDARY, style="italic",
                arrowprops={"arrowstyle": "->", "color": TEXT_SECONDARY, "lw": 1})

    ax.legend(frameon=False, fontsize=9, loc="upper right")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "fig2_ocupancia_s1.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, facecolor="white")
    print(f"\nSalvo: {out_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Rodar e conferir**

Run: `python -m scripts.gerar_fig2_ocupancia_s1`
Expected: 13 linhas de log, arquivo criado. Conferir `VRYRR` no log contra Tabela 9o (deve dar 4A≈99,5% 5A≈99,9% 6A≈100,0%) e `VRRPR` (6A≈33,5%).

- [ ] **Step 3: Ler a imagem gerada**

Checar: 3 barras por candidato visíveis e distintas, rótulos do eixo x legíveis (rotacionados, sem corte), anotação do VRRPR aparece na posição certa, legenda com as 3 cores do corte.

- [ ] **Step 4: Commit**

```bash
git add scripts/gerar_fig2_ocupancia_s1.py
git commit -m "feat(figuras): Fig 2 — ocupância real do bolso S1 (4/5/6 Å)"
```

---

## Task 4: Figura 3 — Matriz cross-species

**Files:**
- Create: `scripts/gerar_fig3_cross_species.py`

**Interfaces:**
- Consumes: `fetch_remote_json`, `SEQUENTIAL_BLUE_FULL`, `TOP13`, `SPECIES_ORDER`, `SPECIES_LABELS`, `TEXT_PRIMARY` de `scripts/figuras_utils.py`.
- Produces: `outputs/figuras_artigo/fig3_cross_species.png`.

- [ ] **Step 1: Write the script**

```python
# scripts/gerar_fig3_cross_species.py
"""Figura 3 — Heatmap real Vina (kcal/mol), TOP-13 x 11 especies.

Dado real: outputs/cross_species_docking/all_cross_species_results.json.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

from scripts.figuras_utils import (
    SEQUENTIAL_BLUE_FULL, SPECIES_LABELS, SPECIES_ORDER, TEXT_PRIMARY, TOP13, fetch_remote_json,
)

OUT_DIR = Path("outputs/figuras_artigo")


def main():
    data = fetch_remote_json(
        "~/design-inibidores/outputs/cross_species_docking/all_cross_species_results.json"
    )

    matrix = np.zeros((len(TOP13), len(SPECIES_ORDER)))
    for i, seq in enumerate(TOP13):
        for j, sp in enumerate(SPECIES_ORDER):
            val = data[sp][seq]
            if val is None:
                raise RuntimeError(f"Vina ausente real para {seq} x {sp} — sem inferir, investigar")
            matrix[i, j] = val

    means = matrix.mean(axis=1)
    order = np.argsort(means)  # mais negativo (melhor afinidade media) primeiro
    matrix = matrix[order]
    seqs_sorted = [TOP13[i] for i in order]
    print("Ordem por Vina medio (mais negativo primeiro):")
    for seq, m in zip(seqs_sorted, means[order]):
        print(f"  {seq}: media={m:.2f}")

    # Escala sequencial: mais negativo (melhor) = mais escuro. Inverte o sinal para o cmap.
    cmap = LinearSegmentedColormap.from_list("seq_blue", SEQUENTIAL_BLUE_FULL[::-1])

    fig, ax = plt.subplots(figsize=(11, 7.5))
    im = ax.imshow(matrix, cmap=cmap, aspect="auto")

    ax.set_xticks(range(len(SPECIES_ORDER)))
    ax.set_xticklabels([SPECIES_LABELS[s] for s in SPECIES_ORDER], rotation=45, ha="right",
                        fontsize=8, color=TEXT_PRIMARY, style="italic")
    ax.set_yticks(range(len(seqs_sorted)))
    ax.set_yticklabels([s if len(s) <= 12 else s[:12] + "…" for s in seqs_sorted],
                        fontsize=8, color=TEXT_PRIMARY)
    ax.set_title("Docking real (Vina, kcal/mol) — TOP-13 × 11 espécies Lepidoptera-praga",
                  color=TEXT_PRIMARY, fontsize=12)

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, f"{matrix[i, j]:.1f}", ha="center", va="center", fontsize=6,
                     color="white" if matrix[i, j] < np.median(matrix) else TEXT_PRIMARY)

    cbar = fig.colorbar(im, ax=ax, shrink=0.7)
    cbar.set_label("Vina (kcal/mol) — mais negativo = maior afinidade", fontsize=9, color=TEXT_PRIMARY)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "fig3_cross_species.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, facecolor="white")
    print(f"\nSalvo: {out_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Rodar e conferir**

Run: `python -m scripts.gerar_fig3_cross_species`
Expected: log da ordenação por média + arquivo criado. Conferir `SARESIKKAYKTFLERYKKL` no log contra Tabela 9r (média real ≈ −13,35).

- [ ] **Step 3: Ler a imagem gerada**

Checar: 143 células todas preenchidas com número legível, rótulos de espécie em itálico sem corte, barra de cor com rótulo claro.

- [ ] **Step 4: Commit**

```bash
git add scripts/gerar_fig3_cross_species.py
git commit -m "feat(figuras): Fig 3 — heatmap real cross-species 13×11"
```

---

## Task 5: Figura 4 — Fingerprint (5 candidatos-chave)

**Files:**
- Create: `scripts/gerar_fig4_fingerprint.py`

**Interfaces:**
- Consumes: `fetch_remote_json`, `STATUS`, `TEXT_PRIMARY`, `TEXT_SECONDARY`, `TEXT_MUTED` de `scripts/figuras_utils.py`.
- Produces: `outputs/figuras_artigo/fig4_fingerprint.png`.

- [ ] **Step 1: Write the script**

```python
# scripts/gerar_fig4_fingerprint.py
"""Figura 4 — Assinatura digital de interacao, 5 candidatos-chave.

Dado real: plip_deep_summary.json (triade, exceto SEEEVLAANEAYAAAHTAYN, ver
nota abaixo), persistence_summary.json (ocupancia 6A + RMSD local),
s2s3_summary.json (contato S2'/S3', sinal ja documentado como ruidoso).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from scripts.figuras_utils import STATUS, TEXT_MUTED, TEXT_PRIMARY, TEXT_SECONDARY, fetch_remote_json

OUT_DIR = Path("outputs/figuras_artigo")
CANDIDATES = ["SRTRR", "VRYRR", "VRRPR", "HRPRRPR", "SEEEVLAANEAYAAAHTAYN"]

# SEEEVLAANEAYAAAHTAYN: contato de triade real ja publicado (Secao 3.10b do artigo,
# mecanismo pi-cation via Tyr12), mas sem plip_deep_summary.json preservado no
# servidor (rodou em analise historica separada). Nao e valor fabricado: e o
# resultado real ja verificado e citado em artigo_resultados.md Tabela 9m.
SEEEVLAANE_TRIAD_HISTORICO = {"contacts_his_any": True, "contacts_asp_any": True, "contacts_ser_any": True}


def main():
    plip = fetch_remote_json("~/design-inibidores/outputs/plip_deep/plip_deep_summary.json")
    persistence = fetch_remote_json("~/design-inibidores/outputs/persistence_deep/persistence_summary.json")
    s2s3 = fetch_remote_json("~/design-inibidores/outputs/s2s3_deep/s2s3_summary.json")

    rows = []
    for seq in CANDIDATES:
        triad = plip[seq] if seq in plip else SEEEVLAANE_TRIAD_HISTORICO
        occ6 = [persistence[seq][r]["occupancy_fraction_6A"] for r in ("rep1", "rep2", "rep3")
                if "error" not in persistence[seq].get(r, {"error": 1})]
        rmsd_local = [persistence[seq][r]["local_rmsd_pocket_nm"] for r in ("rep1", "rep2", "rep3")
                      if "error" not in persistence[seq].get(r, {"error": 1})]
        s2s3_vals = [s2s3[seq][r]["contato_s2s3_fracao"] for r in ("rep1", "rep2", "rep3")
                     if "error" not in s2s3[seq].get(r, {"error": 1})]
        row = {
            "seq": seq,
            "triad": all([triad["contacts_his_any"], triad["contacts_asp_any"], triad["contacts_ser_any"]]),
            "occ6_pct": float(np.mean(occ6)) * 100,
            "rmsd_local": float(np.mean(rmsd_local)),
            "s2s3_pct": float(np.mean(s2s3_vals)) * 100,
        }
        rows.append(row)
        print(f"{seq}: triade={row['triad']} occ6={row['occ6_pct']:.1f}% "
              f"rmsd_local={row['rmsd_local']:.3f} s2s3={row['s2s3_pct']:.1f}%")

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.axis("off")

    n = len(rows)
    col_x = [0.20, 0.42, 0.62, 0.82]
    col_titles = ["Tríade His/Asp/Ser", "Ocupância S1 6Å", "RMSD local bolso (nm)",
                  "Contato S2'/S3' (heurística, sinal ruidoso)"]
    row_y = np.linspace(0.80, 0.10, n)

    for cx, title in zip(col_x, col_titles):
        ax.text(cx, 0.94, title, ha="center", va="center", fontsize=9,
                color=TEXT_PRIMARY, weight="bold", wrap=True)

    max_rmsd = max(r["rmsd_local"] for r in rows)
    for ry, row in zip(row_y, rows):
        ax.text(0.02, ry, row["seq"], ha="left", va="center", fontsize=9, color=TEXT_PRIMARY)

        mark = "✓" if row["triad"] else "✗"
        color = STATUS["bom"] if row["triad"] else STATUS["critico"]
        ax.text(col_x[0], ry, mark, ha="center", va="center", fontsize=13, color=color, weight="bold")

        bar_w = 0.14 * (row["occ6_pct"] / 100)
        ax.add_patch(plt.Rectangle((col_x[1] - 0.07, ry - 0.02), bar_w, 0.04, color=STATUS["bom"]))
        ax.text(col_x[1], ry + 0.045, f"{row['occ6_pct']:.0f}%", ha="center", fontsize=7, color=TEXT_SECONDARY)

        bar_w = 0.14 * (row["rmsd_local"] / max_rmsd)
        ax.add_patch(plt.Rectangle((col_x[2] - 0.07, ry - 0.02), bar_w, 0.04, color=STATUS["atencao"]))
        ax.text(col_x[2], ry + 0.045, f"{row['rmsd_local']:.2f}", ha="center", fontsize=7, color=TEXT_SECONDARY)

        bar_w = 0.14 * (row["s2s3_pct"] / 100)
        ax.add_patch(plt.Rectangle((col_x[3] - 0.07, ry - 0.02), bar_w, 0.04,
                                    color=TEXT_MUTED, alpha=0.5, hatch="//"))
        ax.text(col_x[3], ry + 0.045, f"{row['s2s3_pct']:.0f}%", ha="center", fontsize=7, color=TEXT_MUTED)

    ax.set_title("Assinatura digital de interação — 5 candidatos-chave",
                  color=TEXT_PRIMARY, fontsize=12, pad=10)
    ax.text(0.5, 0.02, "Coluna S2'/S3' com hachura = sinal de baixa confiabilidade "
                        "(heurística não validada, 5 frames/réplica)",
            ha="center", fontsize=7, color=TEXT_MUTED, style="italic")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "fig4_fingerprint.png"
    fig.savefig(out_path, dpi=300, facecolor="white")
    print(f"\nSalvo: {out_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Rodar e conferir**

Run: `python -m scripts.gerar_fig4_fingerprint`
Expected: 5 linhas de log. Conferir `VRRPR` contra Tabela 9q (triade=True, occ6≈33,5%, rmsd_local≈0,416, s2s3≈13,3%).

- [ ] **Step 3: Ler a imagem gerada**

Checar: 5 linhas × 4 colunas legíveis, marca ✓ visível e verde para os 5 (todos têm tríade completa), barras proporcionais aos valores reais, coluna S2'/S3' visualmente diferenciada (hachura) das outras 3, nota de rodapé sobre confiabilidade legível.

- [ ] **Step 4: Commit**

```bash
git add scripts/gerar_fig4_fingerprint.py
git commit -m "feat(figuras): Fig 4 — fingerprint dos 5 candidatos-chave"
```

---

## Self-Review (spec coverage)

- **Fig 1 (réplicas MD)**: Task 2. ✓
- **Fig 2 (ocupância S1)**: Task 3. ✓
- **Fig 3 (cross-species)**: Task 4. ✓
- **Fig 4 (fingerprint)**: Task 5. ✓
- **Paleta/princípios da spec usados verbatim**: Task 1 centraliza os hex exatos, consumidos por Tasks 2-5. ✓
- **Dado sempre real, buscado do servidor nesta execução**: todas as Tasks 2-5 chamam `fetch_remote_json` no início, nenhum valor final hardcodado (exceção documentada: tríade histórica de `SEEEVLAANEAYAAAHTAYN`, justificada inline no código). ✓
- **Verificação visual + conferência de números**: Step 2/3 de cada task de figura. ✓
- **Sem eixo duplo em nenhuma figura**: nenhum `twinx()`/`twiny()` usado em nenhum script. ✓

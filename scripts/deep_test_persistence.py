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
import os
import subprocess
from pathlib import Path

import MDAnalysis as mda
import numpy as np
from MDAnalysis.analysis import align

from scripts.persistence_utils import occupancy_fraction, find_anchor_residue

GMX = "/home/eulalio/miniforge3/envs/md-gromacs/bin/gmx_mpi"

CANDIDATES = [
    "SRTRR", "HRPRRPR", "RLREELKKAEEWLEKRRKEE", "SEEEVLAANEAYAAAHTAYN",
    "SALASIAAHQATFLAYLESK", "MGSLTAYLEAYAAENAAALA", "MGYLTAYHQALAAQNAALLA",
    "SARESIKKAYKTFLERYKKL", "VRYRR", "VRTRR", "VRRPR", "HRPRRSR", "HRPRRPK",
]

# rep1: mesmo mapeamento de outputs/md/forced_NN/ usado em deep_test_plip.py e
# deep_test_md_replicates.py (candidatos do batch antigo Fase 4/5) — reconstruído por
# sequência real, não adivinhado.
REP1_DIR_OVERRIDE = {
    "RLREELKKAEEWLEKRRKEE": "forced_05",
    "SEEEVLAANEAYAAAHTAYN": "forced_00",
    "MGYLTAYHQALAAQNAALLA": "forced_01",
    "MGSLTAYLEAYAAENAAALA": "forced_03",
    "SALASIAAHQATFLAYLESK": "forced_04",
}  # mapeamento verificado 2026-07-20 por sequência real em complex_clean.pdb (não adivinhado) —
# faltavam 4 entradas: essas 4 tinham rep1 real preservado em forced_NN/, mas o dict incompleto
# fazia o script procurar em outputs/md/{seq}/ (inexistente) e reportar "sem trajetoria real"
# por engano. SARESIKKAYKTFLERYKKL segue genuinamente sem complex_clean preservado (confirmado
# em md_agent.py: fonte pre-MD, sem geometria equilibrada real de rep1).
S1_ASP_RESID = 187  # outputs/structure/binding_site.json, receptor ACR157 (individual_sites[0])
S1_ASP_ATOMS = "name OD1 OD2"
OCCUPANCY_CUTOFFS_A = [4.0, 5.0, 6.0]
EXPECTED_RECEPTOR_RESIDUES = 231  # receptor ACR157, confirmado em outputs/structure/binding_site.json
# e docs/superpowers/plans/2026-07-19-eficacia-persistencia-fingerprint-plan.md
# (resid 1-231 no .gro, idem numeracao original do PDB)

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


def _ensure_pbc_corrected(tpr: Path, xtc: Path) -> Path | dict:
    """Gera (ou reusa) a trajetoria completa corrigida de PBC (-pbc mol -center) ao lado
    da trajetoria bruta, para nao computar distancia/RMSD sobre moleculas quebradas pela
    imagem periodica da caixa (mesmo problema resolvido em deep_test_plip.py, mas aqui
    para a trajetoria inteira, nao so o ultimo frame — occupancy/RMSD precisam de todos
    os frames). Nome distinto (md_pbc_full.xtc) para nao colidir com md_pbc.xtc
    pre-existente de outro fluxo em alguns diretorios rep1.
    Retorna o Path da trajetoria corrigida, ou um dict {"error": ...} se trjconv falhar.
    """
    corrected_xtc = xtc.parent / "md_pbc_full.xtc"
    if corrected_xtc.exists() and corrected_xtc.stat().st_size > 1000:
        return corrected_xtc
    # mesmo padrao de deep_test_plip.py: pipe de shell real (subprocess.run(input=...) nao
    # funciona de forma confiavel com gmx_mpi em screen detached); sem -dump para pegar a
    # trajetoria inteira, nao so um frame.
    cmd = f"printf '1\\n0\\n' | {GMX} trjconv -s {tpr} -f {xtc} -o {corrected_xtc} -pbc mol -center"
    proc = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=1800)
    if not corrected_xtc.exists() or corrected_xtc.stat().st_size < 1000:
        return {"error": f"trjconv -pbc mol -center falhou ou gerou arquivo vazio/pequeno "
                          f"para {xtc}: {proc.stderr[-400:]}"}
    return corrected_xtc


def analyze_replicate(seq: str, tpr: Path, xtc: Path) -> dict:
    corrected = _ensure_pbc_corrected(tpr, xtc)
    if isinstance(corrected, dict):
        return corrected
    corrected_xtc = corrected

    u = mda.Universe(str(tpr), str(corrected_xtc))
    protein = u.select_atoms("protein")
    n_receptor = len(protein.residues) - len(seq)
    if n_receptor <= 0:
        return {"error": f"contagem de residuos de proteina ({len(protein.residues)}) "
                          f"menor ou igual ao comprimento do peptideo ({len(seq)})"}
    if n_receptor != EXPECTED_RECEPTOR_RESIDUES:
        return {"error": f"n_receptor calculado ({n_receptor}) diferente do esperado para "
                          f"o receptor ACR157 ({EXPECTED_RECEPTOR_RESIDUES}) — contagem de "
                          f"residuos da trajetoria nao bate com o padrao do projeto"}

    receptor_residues = protein.residues[:n_receptor]
    peptide_residues = protein.residues[n_receptor:n_receptor + len(seq)]

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
    result = {
        "anchor_residue_seq_idx": anchor_idx,
        "anchor_residue_aa": seq[anchor_idx],
        "n_frames": len(distances_per_residue[anchor_idx]),
        "local_rmsd_pocket_nm": round(float(np.mean(local_rmsd_frames)), 4) if local_rmsd_frames else None,
    }
    for cutoff in OCCUPANCY_CUTOFFS_A:
        result[f"occupancy_fraction_{int(cutoff)}A"] = occupancy_fraction(
            distances_per_residue[anchor_idx], cutoff)
    return result


def _write_summary_atomic(summary: dict, summary_path: Path) -> None:
    """Grava summary_path atomicamente (tmp + os.replace) para nao corromper
    o progresso acumulado se o processo for interrompido no meio da escrita
    (mesma classe de incidente real do checkpoint.json, commit ce5d209)."""
    tmp_path = summary_path.with_name(summary_path.name + ".tmp")
    tmp_path.write_text(json.dumps(summary, indent=2))
    os.replace(tmp_path, summary_path)


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
                _write_summary_atomic(summary, summary_path)
                continue
            tpr, xtc = paths
            try:
                result = analyze_replicate(seq, tpr, xtc)
            except Exception as e:
                result = {"error": str(e)}
            seq_results[rep] = result
            print(f"[{seq}] {rep}: {result}")
            _write_summary_atomic(summary, summary_path)

    print(f"\nSalvo: {summary_path}")


if __name__ == "__main__":
    main()

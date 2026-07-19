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

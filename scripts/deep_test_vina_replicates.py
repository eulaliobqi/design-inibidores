"""deep_test_vina_replicates.py — Réplicas reais de docking Vina para o TOP-13 (Tabela 9j).

O Vina (build f458505-mod usada neste pipeline) não fixa seed por padrão — cada chamada já usa
uma amostragem estocástica distinta internamente. Rodar N réplicas reais dá média±desvio-padrão
em vez de um único valor pontual, quantificando a variância real já observada empiricamente
(ex.: cross-species docking, Seção 3.11c, mesma sequência/receptor variou ~0,1-0,5 kcal/mol entre
corridas independentes).

Reusa receptor real já preparado (outputs/docking/receptor.pdbqt, ACR157) e a mesma função de
construção de ligante all-atom validada em ~990+ docagens reais (utils.build_peptide_pdbqt).

Uso: conda run -n protein_design_env python scripts/deep_test_vina_replicates.py
"""
import json
import re
import subprocess
from pathlib import Path

from utils import build_peptide_pdbqt

CANDIDATES = [
    "SRTRR", "HRPRRPR", "RLREELKKAEEWLEKRRKEE", "SEEEVLAANEAYAAAHTAYN",
    "SALASIAAHQATFLAYLESK", "MGSLTAYLEAYAAENAAALA", "MGYLTAYHQALAAQNAALLA",
    "SARESIKKAYKTFLERYKKL", "VRYRR", "VRTRR", "VRRPR", "HRPRRSR", "HRPRRPK",
]

N_REPLICATES = 5
CENTER = [3.87, 1.536, -0.592]  # outputs/structure/binding_site.json, consensso real ACR157
RECEPTOR_PDBQT = Path("outputs/docking/receptor.pdbqt")
WORKDIR = Path("outputs/vina_replicates")


def adaptive_grid(length: int) -> list:
    needed = int(length * 3.6) + 8
    s = max(40.0, float(needed))
    return [s, s, s]


def run_vina(lig_pdbqt: Path, out_dir: Path, size: list, rep: int) -> float | None:
    out_pdbqt = out_dir / f"docked_rep{rep}.pdbqt"
    cmd = [
        "vina", "--receptor", str(RECEPTOR_PDBQT), "--ligand", str(lig_pdbqt),
        "--out", str(out_pdbqt),
        "--center_x", str(CENTER[0]), "--center_y", str(CENTER[1]), "--center_z", str(CENTER[2]),
        "--size_x", str(size[0]), "--size_y", str(size[1]), "--size_z", str(size[2]),
        "--exhaustiveness", "16", "--num_modes", "9",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    for line in (proc.stdout + proc.stderr).splitlines():
        m = re.search(r"^\s*1\s+([-\d.]+)", line)
        if m:
            return float(m.group(1))
    return None


def main():
    if not RECEPTOR_PDBQT.exists():
        raise RuntimeError(f"Receptor real ausente: {RECEPTOR_PDBQT}")
    WORKDIR.mkdir(parents=True, exist_ok=True)

    all_results = {}
    for seq in CANDIDATES:
        sp_dir = WORKDIR / seq
        sp_dir.mkdir(exist_ok=True)
        existing = sp_dir / "replicates.json"
        reps = json.loads(existing.read_text()) if existing.exists() else []

        lig_pdbqt = build_peptide_pdbqt(seq, CENTER, sp_dir, logger=None)
        if lig_pdbqt is None:
            print(f"[{seq}] falhou construção do ligante")
            continue

        size = adaptive_grid(len(seq))
        while len(reps) < N_REPLICATES:
            rep_idx = len(reps) + 1
            aff = run_vina(lig_pdbqt, sp_dir, size, rep_idx)
            reps.append(aff)
            print(f"[{seq}] réplica {rep_idx}/{N_REPLICATES}: Vina real = {aff}")
            existing.write_text(json.dumps(reps, indent=2))

        valid = [r for r in reps if r is not None]
        mean = sum(valid) / len(valid) if valid else None
        std = (sum((x - mean) ** 2 for x in valid) / len(valid)) ** 0.5 if valid and mean is not None else None
        all_results[seq] = {"replicates": reps, "mean": mean, "std": std, "n": len(valid)}
        print(f"[{seq}] média real = {mean}, desvio-padrão real = {std} (n={len(valid)})")

    (WORKDIR / "vina_replicates_summary.json").write_text(json.dumps(all_results, indent=2))
    print(f"\nSalvo: {WORKDIR / 'vina_replicates_summary.json'}")


if __name__ == "__main__":
    main()

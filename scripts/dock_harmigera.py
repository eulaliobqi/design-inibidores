"""dock_harmigera.py — Docking real do TOP-10 contra H. armigera (B6CME8, ESMFold).

Diferente de SpecificityAgent (não-alvo: afinidade BAIXA é boa), aqui H. armigera é OUTRA
PRAGA-ALVO (R3): afinidade ALTA (comparável ao alvo primário A. gemmatalis/ACR157) é o resultado
desejado — indicaria eficácia de amplo espectro entre espécies de Lepidoptera-praga.

Uso: conda run -n protein_design_env python scripts/dock_harmigera.py
"""
import json
import subprocess
from pathlib import Path

from utils import build_peptide_pdbqt

RECEPTOR_PDB = "data-nontargets/Harmigera-B6CME8-ESMFold.pdb"
CENTER = [5.153, -5.067, -2.266]  # StructureAgent._analyze_single, real, 2026-07-18
WORKDIR = Path("outputs/harmigera_docking")

TOP10 = [
    "SRTRR", "HRPRRPR", "RLREELKKAEEWLEKRRKEE", "SEEEVLAANEAYAAAHTAYN",
    "SALASIAAHQATFLAYLESK", "MGSLTAYLEAYAAENAAALA", "RLRAIWLEAEKLLEERRKKK",
    "MGYLTAYHQALAAQNAALLA", "RVKDQWLEAEKLLEERRKKK", "SARESIKKAYKTFLERYKKL",
]


def prepare_receptor() -> Path:
    WORKDIR.mkdir(parents=True, exist_ok=True)
    pdbqt = WORKDIR / "receptor.pdbqt"
    if pdbqt.exists() and pdbqt.stat().st_size > 5000:
        return pdbqt
    proc = subprocess.run(
        ["obabel", RECEPTOR_PDB, "-O", str(pdbqt), "-h", "-xr"],
        capture_output=True, text=True, timeout=120,
    )
    if proc.returncode != 0 or not pdbqt.exists():
        raise RuntimeError(f"obabel receptor falhou: {proc.stderr[-300:]}")
    return pdbqt


def adaptive_grid(length: int) -> list:
    needed = int(length * 3.6) + 8
    s = max(40.0, float(needed))
    return [s, s, s]


def run_vina(rec_pdbqt: Path, lig_pdbqt: Path, out_dir: Path, size: list) -> float | None:
    out_pdbqt = out_dir / "docked.pdbqt"
    cmd = [
        "vina", "--receptor", str(rec_pdbqt), "--ligand", str(lig_pdbqt),
        "--out", str(out_pdbqt),
        "--center_x", str(CENTER[0]), "--center_y", str(CENTER[1]), "--center_z", str(CENTER[2]),
        "--size_x", str(size[0]), "--size_y", str(size[1]), "--size_z", str(size[2]),
        "--exhaustiveness", "8", "--num_modes", "9",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    import re
    for line in (proc.stdout + proc.stderr).splitlines():
        m = re.search(r"^\s*1\s+([-\d.]+)", line)
        if m:
            return float(m.group(1))
    return None


def main():
    rec_pdbqt = prepare_receptor()
    print(f"Receptor real preparado: {rec_pdbqt} ({rec_pdbqt.stat().st_size} bytes)")

    results = {}
    for seq in TOP10:
        out_dir = WORKDIR / seq[:15]
        out_dir.mkdir(exist_ok=True)
        lig_pdbqt = build_peptide_pdbqt(seq, CENTER, out_dir, logger=None)
        if lig_pdbqt is None:
            results[seq] = None
            print(f"{seq}: falhou construção do ligante")
            continue
        aff = run_vina(rec_pdbqt, lig_pdbqt, out_dir, adaptive_grid(len(seq)))
        results[seq] = aff
        print(f"{seq} (len={len(seq)}): Vina real vs H. armigera = {aff}")

    (WORKDIR / "harmigera_docking_results.json").write_text(json.dumps(results, indent=2))
    print(f"\nSalvo: {WORKDIR / 'harmigera_docking_results.json'}")


if __name__ == "__main__":
    main()

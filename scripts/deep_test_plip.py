"""deep_test_plip.py — Análise mecanística PLIP real para o TOP-13 (Tabela 9j).

Extrai o último frame da produção MD (10 ns) via `gmx trjconv`, protona com OpenBabel e roda
PLIP 3.0.0 --peptides sobre o complexo real. Reusa a mesma lógica do padrão já usado para os 5
candidatos analisados anteriormente (Seção 3.10b/9c do artigo) — cadeia do peptídeo = P.

Uso: conda run -n protein_design_env python scripts/deep_test_plip.py
(gmx precisa estar disponível — usa o md-gromacs env via subprocess com caminho absoluto)
"""
import json
import re
import subprocess
from pathlib import Path

GMX = "/home/eulalio/miniforge3/envs/md-gromacs/bin/gmx_mpi"

CANDIDATES = [
    "SRTRR", "HRPRRPR", "RLREELKKAEEWLEKRRKEE", "VRRPR", "SARESIKKAYKTFLERYKKL",
    "VRYRR", "VRTRR", "HRPRRSR", "HRPRRPK",
]

MD_DIR = Path("outputs/md")
OUT_DIR = Path("outputs/plip_deep")


def extract_last_frame(seq: str) -> Path | None:
    run_dir = MD_DIR / seq
    tpr = run_dir / "md.tpr"
    xtc = run_dir / "md.xtc"
    if not tpr.exists() or not xtc.exists():
        print(f"[{seq}] sem md.tpr/md.xtc real, pulando")
        return None
    out_dir = OUT_DIR / seq
    out_dir.mkdir(parents=True, exist_ok=True)
    frame_pdb = out_dir / "last_frame.pdb"
    if frame_pdb.exists() and frame_pdb.stat().st_size > 1000:
        return frame_pdb
    proc = subprocess.run(
        [GMX, "trjconv", "-s", str(tpr), "-f", str(xtc), "-o", str(frame_pdb),
         "-pbc", "mol", "-center", "-dump", "999999"],
        input="1\n0\n", capture_output=True, text=True, timeout=180,
    )
    if not frame_pdb.exists() or frame_pdb.stat().st_size < 1000:
        print(f"[{seq}] trjconv falhou: {proc.stderr[-400:]}")
        return None
    return frame_pdb


def protonate(seq: str, frame_pdb: Path) -> Path | None:
    out_dir = frame_pdb.parent
    prot_pdb = out_dir / "last_frame_protonated.pdb"
    if prot_pdb.exists() and prot_pdb.stat().st_size > 1000:
        return prot_pdb
    proc = subprocess.run(
        ["obabel", str(frame_pdb), "-O", str(prot_pdb), "-h"],
        capture_output=True, text=True, timeout=60,
    )
    if not prot_pdb.exists() or prot_pdb.stat().st_size < 1000:
        print(f"[{seq}] obabel protonação falhou: {proc.stderr[-300:]}")
        return None
    return prot_pdb


def run_plip(seq: str, prot_pdb: Path) -> dict:
    out_dir = prot_pdb.parent
    proc = subprocess.run(
        ["plip", "-f", str(prot_pdb), "--peptides", "P", "-o", str(out_dir), "-t"],
        capture_output=True, text=True, timeout=180, cwd=str(out_dir),
    )
    report = out_dir / "report.txt"
    if not report.exists():
        print(f"[{seq}] PLIP falhou: rc={proc.returncode} {proc.stderr[-300:]}")
        return {"seq": seq, "status": "falhou", "stderr": proc.stderr[-500:]}

    text = report.read_text(errors="ignore")
    contacts_his = bool(re.search(r"\bHIS\b", text))
    contacts_asp = bool(re.search(r"\bASP\b", text))
    contacts_ser = bool(re.search(r"\bSER\b", text))
    n_hydrophobic = len(re.findall(r"Hydrophobic Interactions", text))
    n_hbond = text.count("Hydrogen Bonds")
    n_pication = text.count("pi-Cation") + text.count("π-Cation") + text.count("Pi-Cation")
    n_saltbridge = text.count("Salt Bridges")
    return {
        "seq": seq, "status": "real",
        "contacts_his_any": contacts_his, "contacts_asp_any": contacts_asp,
        "contacts_ser_any": contacts_ser,
        "n_hydrophobic_blocks": n_hydrophobic, "n_hbond_blocks": n_hbond,
        "n_pication_blocks": n_pication, "n_saltbridge_blocks": n_saltbridge,
        "report_path": str(report),
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = {}
    for seq in CANDIDATES:
        frame = extract_last_frame(seq)
        if frame is None:
            results[seq] = {"seq": seq, "status": "sem_trajetoria"}
            continue
        prot = protonate(seq, frame)
        if prot is None:
            results[seq] = {"seq": seq, "status": "falhou_protonacao"}
            continue
        r = run_plip(seq, prot)
        results[seq] = r
        print(f"[{seq}] {r.get('status')}: His={r.get('contacts_his_any')} Asp={r.get('contacts_asp_any')} Ser={r.get('contacts_ser_any')} hbonds_blocos={r.get('n_hbond_blocks')}")

    (OUT_DIR / "plip_deep_summary.json").write_text(json.dumps(results, indent=2))
    print(f"\nSalvo: {OUT_DIR / 'plip_deep_summary.json'}")


if __name__ == "__main__":
    main()

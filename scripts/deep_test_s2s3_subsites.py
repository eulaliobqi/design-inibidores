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
import os
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
    # especificamente na coluna RESNR das tabelas de interação do PLIP, não em
    # qualquer número solto no relatório. Formato real (PLIP v3.0.0, tabela
    # "| RESNR | RESTYPE | RESCHAIN | ... |"), ex.:
    #   | 204   | PHE     | A        | 4         | ARG         | B  ...
    # A 1a coluna (RESNR, do receptor/cadeia A) é sempre seguida da 2a coluna
    # RESTYPE com o código de 3 letras maiúsculas do resíduo (ex. PHE, GLY).
    # Isso evita falso-positivo em índices de átomo (DONORIDX/ACCEPTORIDX),
    # distâncias/ângulos, coordenadas ou RESNR_LIG (resíduo do peptídeo, 1-5),
    # que também são números soltos no mesmo relatório.
    for resnum in S2S3_RESIDUES:
        if re.search(rf"^\s*\|\s*{resnum}\s*\|\s*[A-Z]{{3}}\s*\|", text, re.MULTILINE):
            return True
    return False


def analyze_replicate(seq: str, rep: str, run_dir: Path) -> dict:
    out_dir = OUT_DIR / seq / rep
    out_dir.mkdir(parents=True, exist_ok=True)
    frames_ok = []  # timepoints (ps) que realmente produziram um resultado PLIP
    contacts = []   # bool de contato S2'/S3', pareado 1:1 com frames_ok
    for t in FRAME_TIMES_PS:
        frame = extract_frame(run_dir, t, out_dir)
        if frame is None:
            continue
        prot = protonate(frame)
        if prot is None:
            continue
        c = check_s2s3_contact(prot)
        if c is None:
            continue
        frames_ok.append(t)
        contacts.append(c)
    if not contacts:
        return {"error": "nenhum frame processado com sucesso"}
    return {
        "frames_analisados": frames_ok,
        "contato_s2s3_fracao": sum(contacts) / len(contacts),
        "residuos_alvo": S2S3_RESIDUES,
    }


def _write_summary_atomic(summary: dict, summary_path: Path) -> None:
    """Grava summary_path atomicamente (tmp + os.replace) para nao corromper
    o progresso acumulado se o processo for interrompido no meio da escrita
    (mesma classe de incidente real do checkpoint.json, commit ce5d209)."""
    tmp_path = summary_path.with_name(summary_path.name + ".tmp")
    tmp_path.write_text(json.dumps(summary, indent=2))
    os.replace(tmp_path, summary_path)


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
                _write_summary_atomic(summary, summary_path)
                continue
            print(f"[{seq}] {rep}...")
            seq_results[rep] = analyze_replicate(seq, rep, run_dir)
            _write_summary_atomic(summary, summary_path)
            print(f"[{seq}] {rep}: {seq_results[rep]}")

    print(f"\nSalvo: {summary_path}")


if __name__ == "__main__":
    main()

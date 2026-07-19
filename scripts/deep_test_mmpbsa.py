"""deep_test_mmpbsa.py — Energia livre de ligação real (MM-GBSA) para o TOP-13 (Tabela 9j).

Substitui/complementa o score estático do Vina por ΔG_binding real via gmx_MMPBSA (GB, sander),
usando as trajetórias MD já existentes (10 ns, 2001 frames), amostrando o último terço já
equilibrado (frames 1000-2000, a cada 20 = 51 frames reais por candidato).

Bug real corrigido nesta sessão (ValueError: could not convert string to float: '*************' em
BOND): a trajetória crua (md.xtc) não tinha PBC removido antes de passar pelo gmx_MMPBSA — causa
documentada do erro (grupos google gmx_MMPBSA). Fix: pré-processar com
`gmx trjconv -pbc mol -center` antes de rodar o MMPBSA. Confirmado funcionando (SRTRR: 0 erros,
0 avisos, ΔG_TOTAL real = -44,49 kcal/mol).

Ambiente: mmgbsa-env (gmx_MMPBSA v1.5.0.3) com PATH estendido para incluir gmx_mpi (md-gromacs).

Uso: bash (não conda run — precisa das duas ativações/PATH manual, ver launch no screen)
"""
import json
import re
import subprocess
from pathlib import Path

GMX = "/home/eulalio/miniforge3/envs/md-gromacs/bin/gmx_mpi"

CANDIDATES = [
    "SRTRR", "HRPRRPR", "RLREELKKAEEWLEKRRKEE", "SEEEVLAANEAYAAAHTAYN",
    "SALASIAAHQATFLAYLESK", "MGSLTAYLEAYAAENAAALA", "MGYLTAYHQALAAQNAALLA",
    "SARESIKKAYKTFLERYKKL", "VRYRR", "VRTRR", "VRRPR", "HRPRRSR", "HRPRRPK",
]

MD_DIR = Path("outputs/md")
MMPBSA_IN = "&general\nstartframe=1000, endframe=2000, interval=20,\n/\n&gb\nigb=5, saltcon=0.150,\n/\n"


def run(cmd, cwd, timeout, input_text=None):
    # subprocess.run(input=...) não é confiável com gmx_mpi em screen detached
    # (MPI_ABORT / "Cannot read from input") — usar pipe de shell real (testado e
    # confirmado funcionando, 2026-07-18).
    if input_text:
        printf_arg = input_text.replace("\n", "\\n")
        shell_cmd = f"printf '{printf_arg}' | " + " ".join(str(c) for c in cmd)
        return subprocess.run(["bash", "-c", shell_cmd], cwd=str(cwd),
                               capture_output=True, text=True, timeout=timeout)
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)


def process_candidate(seq: str, max_attempts: int = 3) -> dict:
    run_dir = MD_DIR / seq
    tpr, xtc = run_dir / "md.tpr", run_dir / "md.xtc"
    if not tpr.exists() or not xtc.exists():
        return {"seq": seq, "status": "sem_trajetoria_real"}

    final_dat = run_dir / "FINAL_RESULTS_MMPBSA.dat"
    if final_dat.exists():
        return parse_result(seq, final_dat)

    # Bug real corrigido: cwd=run_dir + paths JÁ relativos-à-raiz duplicava o caminho
    # (outputs/md/SEQ/outputs/md/SEQ/md.tpr, inexistente) — causava MPI_ABORT genérico
    # do gmx_mpi ao não achar o arquivo de input. Usar só nomes de arquivo com cwd=run_dir.
    pbc_xtc = run_dir / "md_pbc.xtc"
    if not pbc_xtc.exists() or pbc_xtc.stat().st_size < 1000:
        p = run([GMX, "trjconv", "-s", "md.tpr", "-f", "md.xtc", "-o", "md_pbc.xtc",
                 "-pbc", "mol", "-center"], run_dir, 300, input_text="1\n0\n")
        if not pbc_xtc.exists():
            return {"seq": seq, "status": "falhou_trjconv", "stderr": p.stderr[-500:]}

    ndx = run_dir / "index_mmpbsa.ndx"
    if not ndx.exists():
        run([GMX, "make_ndx", "-f", "md.tpr", "-o", "index_mmpbsa.ndx"], run_dir, 120, input_text="splitch 1\nq\n")
        if not ndx.exists():
            return {"seq": seq, "status": "falhou_make_ndx"}

    (run_dir / "mmpbsa.in").write_text(MMPBSA_IN)

    for attempt in range(1, max_attempts + 1):
        for f in run_dir.glob("_GMXMMPBSA_*"):
            f.unlink()
        cmd = [
            "gmx_MMPBSA", "-O", "-i", "mmpbsa.in", "-cs", "md.tpr",
            "-ci", "index_mmpbsa.ndx", "-cg", "17", "18", "-ct", "md_pbc.xtc",
            "-cp", "topol.top", "-nogui", "-o", "FINAL_RESULTS_MMPBSA.dat",
        ]
        env_cmd = (
            "source ~/miniforge3/etc/profile.d/conda.sh && conda activate mmgbsa-env && "
            f"export PATH=$PATH:/home/eulalio/miniforge3/envs/md-gromacs/bin && "
            f"cd {run_dir} && " + " ".join(cmd)
        )
        proc = subprocess.run(["bash", "-c", env_cmd], capture_output=True, text=True, timeout=600)
        if final_dat.exists():
            print(f"[{seq}] MMPBSA real OK na tentativa {attempt}")
            return parse_result(seq, final_dat)
        print(f"[{seq}] tentativa {attempt}/{max_attempts} falhou: {(proc.stdout + proc.stderr)[-400:]}")

    return {"seq": seq, "status": f"falhou_apos_{max_attempts}_tentativas — pulado conforme instrução"}


def parse_result(seq: str, final_dat: Path) -> dict:
    text = final_dat.read_text(errors="ignore")
    m = re.search(r"ΔTOTAL\s+(-?[\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", text)
    if not m:
        return {"seq": seq, "status": "parse_falhou", "raw_path": str(final_dat)}
    return {
        "seq": seq, "status": "real",
        "delta_g_total_kcal": float(m.group(1)),
        "sd_prop": float(m.group(2)), "sd": float(m.group(3)),
        "sem_prop": float(m.group(4)), "sem": float(m.group(5)),
        "raw_path": str(final_dat),
    }


def main():
    results = {}
    for seq in CANDIDATES:
        r = process_candidate(seq)
        results[seq] = r
        print(f"[{seq}] {r}")
        Path("outputs/mmpbsa_summary.json").write_text(json.dumps(results, indent=2))

    print("\nSalvo: outputs/mmpbsa_summary.json")


if __name__ == "__main__":
    main()

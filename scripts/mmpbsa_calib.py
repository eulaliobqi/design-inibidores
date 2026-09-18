"""B0.5 - MM-PBSA (gmx_MMPBSA, GB) real para os 22 sistemas da campanha de calibracao MD curta.

Reaproveita o pipeline validado em scripts/deep_test_mmpbsa.py (fixes conhecidos:
trjconv -pbc mol -center antes do MMPBSA; env mmgbsa-env + PATH com gmx_mpi de
md-gromacs; pipe de shell em vez de subprocess input= p/ funcionar em screen;
cwd=run_dir com paths so-nome p/ nao duplicar caminho).

Achado real desta sessao: 'splitch 1' (usado no script antigo) NAO produz 2 grupos
por cadeia aqui -- produz ate 10 fragmentos (Protein_chain1..10), porque o splitch
do gmx detecta quebras de conectividade (gaps de loop) dentro de uma mesma cadeia
PDB e trata cada fragmento contiguo como "chain" separada, mesmo com so 2 moleculas
reais no topol.top (Protein_chain_A, Protein_chain_B). Fix: em vez de splitch, criar
os 2 grupos por INTERVALO DE ATOMOS direto (N_A = ultimo atomo em topol_Protein_chain_A.itp,
N_B = idem chain_B) -- testado em bovine__SKTI: 3160/2667 atomos, bate exato com o
[molecules] do topol.top. Os 2 grupos custom ficam sempre nas 2 ULTIMAS posicoes do
.ndx apos o comando, entao o indice e' len(grupos)-2 e len(grupos)-1 (nao precisa
adivinhar nome).

Uso: rodar em screen no servidor (regra nao-negociavel: screen -S antes de job longo).
"""
import json
import re
import subprocess
from pathlib import Path


def chain_letters(topol_top: Path):
    """Ordem real das cadeias proteicas no [molecules] (A = receptor sempre 1a;
    achado real: bovine__ApTI e sfrug__ApTI tem 3 cadeias A/B/C -- ApTI e' um
    inibidor bifuncional de 2 dominios/cadeias -- entao o "ligante" MM-PBSA
    precisa somar TODAS as cadeias apos a A, nao so a B, senao o indice
    complexo fica com menos atomos que a topologia completa (erro real visto:
    "complex index has fewer atoms than the topology")."""
    text = topol_top.read_text(errors="ignore")
    m = re.search(r"\[\s*molecules\s*\](.*?)(?:\[|\Z)", text, re.S)
    letters = []
    for line in m.group(1).splitlines():
        line = line.split(";")[0].strip()
        mm = re.match(r"Protein_chain_(\w+)\s+\d+", line)
        if mm:
            letters.append(mm.group(1))
    return letters


def last_atom_number(itp_path: Path) -> int:
    text = itp_path.read_text(errors="ignore")
    m = re.search(r"\[\s*atoms\s*\](.*?)(?:\[|\Z)", text, re.S)
    body = m.group(1)
    last = 0
    for line in body.splitlines():
        line = line.split(";")[0].strip()
        if not line:
            continue
        tok = line.split()[0]
        if tok.isdigit():
            last = int(tok)
    return last

GMX = "/home/eulalio/miniforge3/envs/md-gromacs/bin/gmx_mpi"
BASE = Path.home() / "design-inibidores" / "data-calibration-b05" / "md_calib"
RESULTS_FILE = BASE / "mmpbsa_calib_results.json"
# Erro real corrigido nesta sessao: startframe=1000/endframe=2000 (herdado de
# scripts/deep_test_mmpbsa.py) presume trajetorias de 10ns/2001 frames (dt=5ps).
# Esta campanha e' de 2ns/401 frames -- startframe=1000 > total_frames(401) =>
# TrajError real do gmx_MMPBSA ("start frame (1000) > total frames (401)").
# Fix: ultimo terco de 401 frames (~1335-2000ps) = frames 268-400, interval=3
# (~45 frames, mesma logica de "amostrar so o trecho ja equilibrado").
MMPBSA_IN = "&general\nstartframe=268, endframe=400, interval=3,\n/\n&gb\nigb=5, saltcon=0.150,\n/\n"


def run(cmd, cwd, timeout, input_text=None):
    if input_text:
        printf_arg = input_text.replace("\n", "\\n")
        shell_cmd = f"printf '{printf_arg}' | " + " ".join(str(c) for c in cmd)
        return subprocess.run(["bash", "-c", shell_cmd], cwd=str(cwd),
                               capture_output=True, text=True, timeout=timeout)
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)


def find_chain_groups(ndx_path: Path):
    """Os 2 grupos custom por intervalo de atomos sao sempre os 2 ultimos do .ndx."""
    text = ndx_path.read_text(errors="ignore")
    names = re.findall(r"\[\s*([^\]]+?)\s*\]", text)
    if len(names) < 2:
        return None, None
    return len(names) - 2, len(names) - 1


def process_tag(tag: str, max_attempts: int = 3) -> dict:
    run_dir = BASE / tag
    tpr, xtc = run_dir / "md.tpr", run_dir / "md.xtc"
    if not tpr.exists() or not xtc.exists():
        return {"status": "sem_trajetoria"}

    final_dat = run_dir / "FINAL_RESULTS_MMPBSA.dat"
    if final_dat.exists():
        return parse_result(final_dat)

    pbc_xtc = run_dir / "md_pbc.xtc"
    if not pbc_xtc.exists() or pbc_xtc.stat().st_size < 1000:
        p = run([GMX, "trjconv", "-s", "md.tpr", "-f", "md.xtc", "-o", "md_pbc.xtc",
                 "-pbc", "mol", "-center"], run_dir, 300, input_text="1\n0\n")
        if not pbc_xtc.exists():
            return {"status": "falhou_trjconv", "stderr": p.stderr[-500:]}

    letters = chain_letters(run_dir / "topol.top")
    if len(letters) < 2:
        return {"status": "falhou_contagem_cadeias", "detail": f"letters={letters}"}
    n_a = last_atom_number(run_dir / f"topol_Protein_chain_{letters[0]}.itp")
    n_lig = sum(last_atom_number(run_dir / f"topol_Protein_chain_{c}.itp") for c in letters[1:])
    if not n_a or not n_lig:
        return {"status": "falhou_contagem_atomos", "detail": f"n_a={n_a} n_lig={n_lig} letters={letters}"}

    ndx = run_dir / "index_mmpbsa.ndx"
    if not ndx.exists():
        run([GMX, "make_ndx", "-f", "md.tpr", "-o", "index_mmpbsa.ndx"], run_dir, 120,
            input_text=f"a 1-{n_a}\na {n_a + 1}-{n_a + n_lig}\nq\n")
        if not ndx.exists():
            return {"status": "falhou_make_ndx"}

    idx_a, idx_b = find_chain_groups(ndx)
    if idx_a is None or idx_b is None:
        return {"status": "falhou_grupos_ndx", "detail": f"idx_a={idx_a} idx_b={idx_b}"}

    (run_dir / "mmpbsa.in").write_text(MMPBSA_IN)

    for attempt in range(1, max_attempts + 1):
        for f in run_dir.glob("_GMXMMPBSA_*"):
            f.unlink()
        cmd = [
            "gmx_MMPBSA", "-O", "-i", "mmpbsa.in", "-cs", "md.tpr",
            "-ci", "index_mmpbsa.ndx", "-cg", str(idx_a), str(idx_b), "-ct", "md_pbc.xtc",
            "-cp", "topol.top", "-nogui", "-o", "FINAL_RESULTS_MMPBSA.dat",
        ]
        env_cmd = (
            "source ~/miniforge3/etc/profile.d/conda.sh && conda activate mmgbsa-env && "
            "export PATH=$PATH:/home/eulalio/miniforge3/envs/md-gromacs/bin && "
            f"cd {run_dir} && " + " ".join(cmd)
        )
        proc = subprocess.run(["bash", "-c", env_cmd], capture_output=True, text=True, timeout=900)
        if final_dat.exists():
            print(f"[{tag}] MMPBSA real OK na tentativa {attempt}")
            return parse_result(final_dat)
        print(f"[{tag}] tentativa {attempt}/{max_attempts} falhou: {(proc.stdout + proc.stderr)[-400:]}")

    return {"status": f"falhou_apos_{max_attempts}_tentativas"}


def parse_result(final_dat: Path) -> dict:
    text = final_dat.read_text(errors="ignore")
    m = re.search(r"ΔTOTAL\s+(-?[\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", text)
    if not m:
        return {"status": "parse_falhou", "raw_path": str(final_dat)}
    return {
        "status": "real",
        "delta_g_total_kcal": float(m.group(1)),
        "sd_prop": float(m.group(2)), "sd": float(m.group(3)),
        "sem_prop": float(m.group(4)), "sem": float(m.group(5)),
        "raw_path": str(final_dat),
    }


def main():
    tags = sorted(p.name for p in BASE.iterdir() if p.is_dir())
    results = {}
    if RESULTS_FILE.exists():
        results = json.loads(RESULTS_FILE.read_text())

    print(f"{len(tags)} sistemas para MM-PBSA")
    for tag in tags:
        if tag in results and results[tag].get("status") == "real":
            print(f"SKIP (ja feito): {tag}")
            continue
        print(f"=== {tag} ===")
        r = process_tag(tag)
        results[tag] = r
        RESULTS_FILE.write_text(json.dumps(results, indent=2, default=str))
        print(f"  -> {r.get('status')}")

    print("MMPBSA_CALIB_ALL_DONE")


if __name__ == "__main__":
    main()

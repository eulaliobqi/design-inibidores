"""
mmgbsa_md82.py -- MM-GBSA (gmx_MMPBSA, GB igb=5, 0,15 M) e PRODIGY no conjunto de quadros das MDs de pH 8,2 (CHARMM36).

Cada MD de 10 ns (pH 8,2; ver run_md_ph_campaign.py) tem md_pbc_sub.xtc (501 quadros, 20 ps) com o complexo inteiro
inteiro e centrado (`trjconv -pbc mol -center`, ver Secao 2.9). Aqui:
  * MM-GBSA de trajetoria unica sobre a 2a metade (quadros 251-501, a cada 2 = 126 quadros), sem entropia;
    receptor = cadeia A da topologia, peptideo = cadeia B (os grupos sao definidos por intervalo de atomos, nao por
    `splitch`, como em mmpbsa_calib.py). A incerteza e' o erro-padrao por blocos de 5 (os quadros sao
    autocorrelacionados), nao o da media dos quadros.
  * PRODIGY em 30 quadros igualmente espacados da mesma metade (receptor A, peptideo B, atomos pesados).
O MM-GBSA e o PRODIGY NAO separaram inibidores de iscas na calibracao (MM-GBSA 4/10 e rho = -0,93 com o tamanho da
interface; PRODIGY 2/10), de modo que os valores servem para ordenar candidatos do mesmo receptor e do mesmo protocolo e
sao dados tambem por residuo; nao sao afinidades.

Uso (servidor, env protein_design_env ativo): python -m scripts.mmgbsa_md82 --front L [--keys K ...] [--tag md82]
"""
import argparse
import json
import re
import statistics as st
import subprocess
import tempfile
from pathlib import Path

from scripts.analyze_md_top_candidates import pbc_traj
from scripts.mmpbsa_calib import GMX, last_atom_number, run
from scripts.prodigy_scores import _frame_to_complex, prodigy

ROOT = Path(__file__).parent.parent
FILES = ["md.tpr", "md_pbc_sub.xtc", "topol_Protein_chain_A.itp", "topol_Protein_chain_B.itp"]


def stage(src: Path, dst: Path):
    dst.mkdir(parents=True, exist_ok=True)
    for f in FILES + [p.name for p in src.glob("*.ff")] + [p.name for p in src.glob("posre_*.itp")]:
        s, d = src / f, dst / f
        if s.exists() and not d.exists():
            d.symlink_to(s.resolve())


def mmpbsa_in(start, end, interval):
    return f"&general\nstartframe={start}, endframe={end}, interval={interval}, verbose=1,\n/\n&gb\nigb=5, saltcon=0.150,\n/\n"


def block_sem(vals, nblocks=5):
    n = len(vals) // nblocks
    if n < 2:
        return None
    means = [sum(vals[i * n:(i + 1) * n]) / n for i in range(nblocks)]
    return st.stdev(means) / nblocks ** 0.5


def parse_dat(p: Path) -> dict:
    t = p.read_text(errors="ignore")
    out = {}
    body = t.split("Delta (Complex - Receptor - Ligand):")[-1]
    for lab, key in (("VDWAALS", "vdw"), ("EEL", "eel"), ("EGB", "egb"), ("ESURF", "esurf"), ("GGAS", "ggas"),
                     ("GSOLV", "gsolv"), ("TOTAL", "total")):
        mm = re.search(rf"Δ?{lab}\s+(-?[\d.]+)\s+([\d.]+)\s+([\d.]+)", body)
        if mm:
            out[key] = float(mm.group(1))
            out[key + "_sd"] = float(mm.group(2))
    return out


def prodigy_frames(run_dir: Path, nframes: int = 30):
    """PRODIGY em `nframes` quadros igualmente espacados da 2a metade (5-10 ns) de md_pbc_sub.xtc."""
    vals = []
    for i in range(nframes):
        t = 5000 + i * (5000 / max(1, nframes - 1))
        with tempfile.TemporaryDirectory() as td:
            fr = Path(td) / "f.pdb"
            run([GMX, "trjconv", "-s", "md.tpr", "-f", "md_pbc_sub.xtc", "-dump", str(t), "-o", str(fr)], run_dir, 120, input_text="1\n")
            if not fr.exists():
                continue
            sp = Path(td) / "s.pdb"
            sp.write_text(_frame_to_complex(fr.read_text()))
            vals.append(prodigy(sp)["dG_kcal"])
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    return {"dG_kcal_mean": sum(vals) / len(vals), "sd": st.pstdev(vals), "n_frames": len(vals)}


def process(front: str, key: str, tag: str, nframes_prodigy: int = 30) -> dict:
    src = ROOT / f"outputs/{tag}_{front}" / key
    run_dir = ROOT / f"outputs/mmgbsa_{tag}" / f"{front}__{key}"
    if not (src / "md_pbc_sub.xtc").exists():
        # o arquivo e' criado na analise (analyze_md_top_candidates), que a fila de energia roda no fim; aqui ele e'
        # gerado sob demanda para que o MM-GBSA nao dependa da ordem das etapas
        if not (src / "md.xtc").exists():
            return {"status": "sem_trajetoria"}
        try:
            pbc_traj(src)
        except RuntimeError:
            return {"status": "sem_trajetoria"}
    stage(src, run_dir)
    # gmx_MMPBSA tira so a agua da topologia; os ions ficariam nela e o indice (so proteina) teria menos atomos que a
    # topologia. Topologia so com as duas cadeias de proteina (as cargas dos ions nao entram no GB implicito).
    top = (src / "topol.top").read_text()
    head, _, tail = top.partition("[ molecules ]")
    keep = [l for l in tail.splitlines() if l.strip().startswith("Protein_chain_") or l.strip().startswith(";")]
    (run_dir / "topol_mmpbsa.top").write_text(head + "[ molecules ]\n" + "\n".join(keep) + "\n")
    res_file = run_dir / "result.json"
    if res_file.exists():
        cached = json.loads(res_file.read_text())
        if cached.get("dG_gb_kcal") is not None:
            return cached
    n_a = last_atom_number(run_dir / "topol_Protein_chain_A.itp")
    n_b = last_atom_number(run_dir / "topol_Protein_chain_B.itp")
    ndx = run_dir / "index_mmpbsa.ndx"
    if not ndx.exists():
        run([GMX, "make_ndx", "-f", "md.tpr", "-o", "index_mmpbsa.ndx"], run_dir, 120,
            input_text=f"a 1-{n_a}\na {n_a + 1}-{n_a + n_b}\nq\n")
    names = re.findall(r"\[\s*([^\]]+?)\s*\]", ndx.read_text())
    ia, ib = len(names) - 2, len(names) - 1
    (run_dir / "mmpbsa.in").write_text(mmpbsa_in(251, 501, 2))
    final = run_dir / "FINAL_RESULTS_MMPBSA.dat"
    log = ""
    for attempt in range(1, 4):
        if final.exists():
            break
        for f in run_dir.glob("_GMXMMPBSA_*"):
            f.unlink()
        cmd = (f"gmx_MMPBSA -O -i mmpbsa.in -cs md.tpr -ci index_mmpbsa.ndx -cg {ia} {ib} -ct md_pbc_sub.xtc "
               f"-cp topol_mmpbsa.top -nogui -o FINAL_RESULTS_MMPBSA.dat -eo FRAME_ENERGIES.csv")
        env_cmd = ("source ~/miniforge3/etc/profile.d/conda.sh && conda activate mmgbsa-env && "
                   "export PATH=$PATH:/home/eulalio/miniforge3/envs/md-gromacs/bin && "
                   f"cd {run_dir} && mpirun -np 4 {cmd} || {cmd}")
        proc = subprocess.run(["bash", "-c", env_cmd], capture_output=True, text=True, timeout=3600)
        log = (proc.stdout + proc.stderr)[-600:]
        if final.exists():
            break
    if not final.exists():
        return {"status": "falhou_mmgbsa", "log": log}
    d = parse_dat(final)
    frames = []
    csvp = run_dir / "FRAME_ENERGIES.csv"
    if csvp.exists():
        # coluna do DeltaG total por quadro: a ultima coluna da secao "Delta Energy Terms"
        rows = [l.strip().split(",") for l in csvp.read_text().splitlines() if l.strip()]
        hdr = [i for i, r in enumerate(rows) if r and r[0].lower().startswith("frame")]
        if hdr:
            h = rows[hdr[-1]]
            if "TOTAL" in h:
                j = h.index("TOTAL")
                for r in rows[hdr[-1] + 1:]:
                    try:
                        frames.append(float(r[j]))
                    except (ValueError, IndexError):
                        break
    out = {"status": "real", "front": front, "key": key, "n_frames": len(frames) or None,
           "dG_gb_kcal": d.get("total"), "components": d, "sem_blocks": block_sem(frames) if frames else None}
    # PRODIGY nos quadros da mesma metade
    pr = prodigy_frames(run_dir, nframes_prodigy)
    if pr:
        out["PRODIGY_md"] = pr
    res_file.write_text(json.dumps(out, indent=1))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--front", choices=["L", "M"], required=True)
    ap.add_argument("--tag", default="md82", help="prefixo do diretorio de MD: outputs/<tag>_<front>")
    ap.add_argument("--keys", nargs="+")
    ap.add_argument("--backfill-prodigy", action="store_true",
                    help="so completa PRODIGY_md das entradas ja calculadas que o nao tem (nao refaz o MM-GBSA)")
    a = ap.parse_args()
    base = ROOT / f"outputs/{a.tag}_{a.front}"
    summ = json.loads((base / "summary.json").read_text()) if (base / "summary.json").exists() else {}
    keys = a.keys or [k for k, v in summ.items() if v.get("status") == "done"]
    outp = ROOT / f"outputs/mmgbsa_{a.tag}_{a.front}.json"
    allr = json.loads(outp.read_text()) if outp.exists() else {}
    if a.backfill_prodigy:
        for k, v in allr.items():
            rd = ROOT / f"outputs/mmgbsa_{a.tag}" / f"{a.front}__{k}"
            if v.get("status") != "real" or "PRODIGY_md" in v or not (rd / "md_pbc_sub.xtc").exists():
                continue
            pr = prodigy_frames(rd)
            print("==", k, "PRODIGY", pr and round(pr["dG_kcal_mean"], 2), flush=True)
            if pr:
                v["PRODIGY_md"] = pr
                (rd / "result.json").write_text(json.dumps(v, indent=1))
                # a fila de energia grava o mesmo JSON: reler antes de gravar para nao perder entradas novas
                cur = json.loads(outp.read_text())
                cur.setdefault(k, v)["PRODIGY_md"] = pr
                outp.write_text(json.dumps(cur, indent=1))
        print("PRODIGY_BACKFILL_DONE")
        return
    for k in keys:
        if allr.get(k, {}).get("status") == "real" and allr[k].get("dG_gb_kcal") is not None:
            continue
        print("==", k, flush=True)
        allr[k] = process(a.front, k, a.tag)
        print("  ->", allr[k].get("status"), allr[k].get("dG_gb_kcal"), flush=True)
        outp.write_text(json.dumps(allr, indent=1))
    print("MMGBSA_DONE")


if __name__ == "__main__":
    main()

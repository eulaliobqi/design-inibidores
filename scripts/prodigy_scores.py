"""
prodigy_scores.py -- PRODIGY (Vangone e Bonvin 2015, eLife 4:e07454, doi 10.7554/eLife.07454) como filtro de energia
sobre (i) as poses iniciais do Boltz-2 dos 48 candidatos finais (protonadas em pH 8,2) e (ii) a calibracao
(inibidores naturais x iscas embaralhadas, mesmo receptor), para saber antes de usar se o escore separa os pares.

PRODIGY NAO e' uma funcao do estado de protonacao: o escore e' linear nas contagens de contatos intermoleculares por
classe de residuo (carregado/polar/apolar) e na fracao de residuos apolares e carregados fora da interface. As
protonacoes de pH 8,2 (PDB2PQR 3.6.2 + PROPKA) entram aqui para manter a mesma entrada das etapas seguintes (MD e MM-GBSA
em pH 8,2) e para registrar os estados nao-padrao; mudar o estado His/Asp/Glu nao muda o escore. O modelo foi treinado
em 81 complexos proteina-proteina; para peptideos de 5-12 residuos a interface e' pequena e o valor absoluto deve ser
lido como ordenacao, nao como afinidade.

Uso (no servidor, env protein_design_env ativo; PRODIGY roda no env `prodigy`):
  python -m scripts.prodigy_scores poses --out outputs/prodigy_poses.json
  python -m scripts.prodigy_scores calib --out outputs/prodigy_calib.json
  python -m scripts.prodigy_scores frames --workdir outputs/md82_L/KEY --out F.json   (conjunto de quadros de uma MD)
"""
import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
PRODIGY = Path.home() / ".local/share/mamba/envs/prodigy/bin/prodigy"
STD = {"HID": "HIS", "HIE": "HIS", "HIP": "HIS", "HSD": "HIS", "HSE": "HIS", "HSP": "HIS", "ASH": "ASP", "GLH": "GLU",
       "LYN": "LYS", "LSN": "LYS", "CYX": "CYS", "CYM": "CYS", "GLUP": "GLU", "ASPP": "ASP"}
NONSTD = ("HID", "HIE", "HIP", "ASH", "GLH", "LYN", "CYM")


def prep(pdb_in: Path, out_dir: Path, ph: float = 8.2) -> dict:
    """PDB2PQR/PROPKA no pH dado; devolve o PDB so de atomos pesados com nomes padrao e o relatorio de estados."""
    out_dir.mkdir(parents=True, exist_ok=True)
    pdb, pqr = out_dir / "prot.pdb", out_dir / "prot.pqr"
    r = subprocess.run(["pdb2pqr30", "--titration-state-method", "propka", "--with-ph", str(ph), "--keep-chain",
                        "--nodebump", "--ff", "AMBER", "--pdb-output", str(pdb), str(pdb_in), str(pqr)],
                       capture_output=True, text=True)
    if not pqr.exists():
        raise RuntimeError("pdb2pqr falhou: " + r.stderr[-400:])
    states = {}
    seen = set()
    for l in pqr.read_text().splitlines():
        if l.startswith("ATOM"):
            key = (l[21], l[22:26].strip(), l[17:21].strip())
            if key in seen:
                continue
            seen.add(key)
            if key[2] in NONSTD:
                states[f"{key[0]}:{key[2]}{key[1]}"] = key[2]
    heavy = out_dir / "heavy.pdb"
    lines = []
    for l in pdb.read_text().splitlines():
        if not l.startswith("ATOM"):
            continue
        el = (l[76:78].strip() or l[12:16].strip()[0]).upper()
        if el.startswith("H"):
            continue
        rn = l[17:21].strip()
        lines.append(l[:17] + f"{STD.get(rn, rn):>3} " + l[21:] if len(l) > 21 else l)
    heavy.write_text("\n".join(lines) + "\nEND\n")
    return {"pdb": str(heavy), "nonstandard_states": states}


def prodigy(pdb: Path, sel=("A", "B"), temp: float = 25.0) -> dict:
    r = subprocess.run([str(PRODIGY), str(pdb), "--selection", sel[0], sel[1], "--temperature", str(temp)],
                       capture_output=True, text=True)
    t = r.stdout

    def g(pat, cast=float):
        m = re.search(pat, t)
        return cast(m.group(1)) if m else None
    return {"dG_kcal": g(r"affinity \(kcal\.mol-1\):\s+(-?[\d.]+)"),
            "Kd_M": g(r"dissociation constant \(M\) at [\d.]+.C:\s+([\d.eE+-]+)"),
            "ic_total": g(r"intermolecular contacts: (\d+)", int),
            "ic_charged_charged": g(r"charged-charged contacts: ([\d.]+)"),
            "ic_charged_polar": g(r"charged-polar contacts: ([\d.]+)"),
            "ic_charged_apolar": g(r"charged-apolar contacts: ([\d.]+)"),
            "ic_polar_polar": g(r"polar-polar contacts: ([\d.]+)"),
            "ic_apolar_polar": g(r"apolar-polar contacts: ([\d.]+)"),
            "ic_apolar_apolar": g(r"apolar-apolar contacts: ([\d.]+)"),
            "nis_apolar_pct": g(r"apolar NIS residues: ([\d.]+)"),
            "nis_charged_pct": g(r"charged NIS residues: ([\d.]+)")}


def cmd_poses(a):
    res = {}
    for F in ("L", "M"):
        for d in sorted((ROOT / f"outputs/md10_{F}").iterdir()):
            src = d / "complex_clean.pdb"
            if not src.exists():
                continue
            key = f"{F}:{d.name}"
            with tempfile.TemporaryDirectory() as td:
                p = prep(src, Path(td), a.ph)
                res[key] = {"front": F, "key": d.name, **prodigy(Path(p["pdb"])), "nonstandard_states": p["nonstandard_states"]}
            print(key, res[key]["dG_kcal"], flush=True)
    Path(a.out).write_text(json.dumps(res, indent=1))


def _is_h(l: str) -> bool:
    el = l[76:78].strip()
    if el:
        return el.upper() == "H"
    n = l[12:16].strip()
    return n[:1] == "H" or (n[:1].isdigit() and n[1:2] == "H")


def _frame_to_complex(pdb_text: str) -> str:
    """Quadro da trajetoria -> complexo de atomos pesados: receptor = cadeia A; todas as outras cadeias da proteina
    (ligante; a ApTI tem 3) viram a cadeia B; agua e ions saem; nomes de residuo padronizados."""
    out = []
    for l in pdb_text.splitlines():
        if not l.startswith("ATOM") or _is_h(l):
            continue
        rn = l[17:21].strip()
        if rn in ("SOL", "WAT", "HOH", "K", "CL", "NA"):
            continue
        ch = "A" if l[21] == "A" else "B"
        rn = STD.get(rn, rn)
        nm = l[12:16].strip()
        nm = {"OC1": "O", "OC2": "OXT", "O1": "O", "O2": "OXT"}.get(nm, nm)
        if rn == "ILE" and nm == "CD":      # AMBER do GROMACS chama o CD1 da Ile de CD; o freesasa exige CD1
            nm = "CD1"
        out.append(l[:12] + (" " + nm).ljust(4)[:4] + " " + f"{rn:>3} " + ch + l[22:])
    return "\n".join(out) + "\nEND\n"


def cmd_calib(a):
    from scripts.mmpbsa_calib import BASE, GMX, run
    res = {}
    for d in sorted(p for p in BASE.iterdir() if p.is_dir()):
        if not ((d / "md.tpr").exists() and (d / "md_pbc.xtc").exists()):
            continue
        vals = []
        for t in a.times:
            with tempfile.TemporaryDirectory() as td:
                fr = Path(td) / "f.pdb"
                run([GMX, "trjconv", "-s", "md.tpr", "-f", "md_pbc.xtc", "-dump", str(t), "-o", str(fr)], d, 120, input_text="1\n")
                if not fr.exists():
                    continue
                sp = Path(td) / "s.pdb"
                sp.write_text(_frame_to_complex(fr.read_text()))
                vals.append(prodigy(sp))
        if vals:
            dg = [v["dG_kcal"] for v in vals if v["dG_kcal"] is not None]
            res[d.name] = {"dG_kcal_mean": sum(dg) / len(dg), "dG_kcal_each": dg, "n_frames": len(dg),
                           "ic_total_mean": sum(v["ic_total"] for v in vals) / len(vals)}
            print(d.name, res[d.name]["dG_kcal_mean"], flush=True)
    Path(a.out).write_text(json.dumps(res, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("poses"); p.add_argument("--out", required=True); p.add_argument("--ph", type=float, default=8.2)
    p.set_defaults(fn=cmd_poses)
    c = sub.add_parser("calib"); c.add_argument("--out", required=True)
    c.add_argument("--times", type=float, nargs="+", default=[1400, 1600, 1800, 2000]); c.set_defaults(fn=cmd_calib)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()

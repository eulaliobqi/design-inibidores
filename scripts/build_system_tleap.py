"""
build_system_tleap.py -- monta o sistema receptor+peptideo solvatado para o GROMACS via
AmberTools/tleap (+ parmed), com suporte a peptideo MACROCICLICO cabeca-cauda (ligacao C(n)-N(1)
explicita na topologia) e LINEAR, no MESMO campo de forca (AMBER ff99SB-ILDN + TIP3P) nas duas frentes.

Por que tleap: o pdb2gmx nao fecha aneis peptidicos. A validacao da falha de julho (dissulfeto
forcado sobre geometria ingenua) nao se aplica: a geometria de partida e' a predicao Boltz-2
CICLICA, em que o anel ja esta fechado.

Protonacao: PROPKA 3 via PDB2PQR no pH informado (padrao 10,0 = intestino medio de Lepidoptera,
9,5-11) define HID/HIE/HIP, LYN, ASH, GLH e CYX da cadeia lateral. Extremidades do peptideo LINEAR:
o campo AMBER so oferece NH3+ / COO- (nao ha N-terminal neutro); no pH 10 o pKa do grupo
alfa-amino (~8) indicaria forma majoritariamente neutra -- limitacao declarada. No macrociclo nao
ha extremidades.

Uso (env mmgbsa-env, onde estao tleap e parmed):
  python scripts/build_system_tleap.py --complex boltz.pdb --out DIR --ph 10.0 [--cyclic] \
      --pdb2pqr ~/miniforge3/envs/protein_design_env/bin/pdb2pqr30
Saidas em DIR: solv_ions.gro, topol.top, build_report.json (+ posre_*.itp ja incluidos no topol.top).
"""
import argparse
import json
import math
import re
import subprocess
from pathlib import Path

import parmed as pmd

SALT_M = 0.15
BUFFER_A = 12.0
RENAME_STD = {"HID": "HIS", "HIE": "HIS", "HIP": "HIS", "CYX": "CYS", "CYM": "CYS",
              "LYN": "LYS", "ASH": "ASP", "GLH": "GLU"}


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def protonate(complex_pdb: Path, out: Path, ph: float, pdb2pqr: str) -> Path:
    prot = out / "protonated.pdb"
    p = run([pdb2pqr, "--ff", "AMBER", "--ffout", "AMBER", "--titration-state-method", "propka",
             "--with-ph", str(ph), "--keep-chain", "--pdb-output", str(prot),
             str(complex_pdb), str(out / "protonated.pqr")], cwd=str(out))
    if p.returncode != 0 or not prot.exists():
        raise RuntimeError(f"pdb2pqr falhou: {p.stderr[-400:]}")
    return prot


def xyz(line):
    return float(line[30:38]), float(line[38:46]), float(line[46:54])


def split_chains(prot: Path):
    atoms = [l for l in prot.read_text().splitlines() if l.startswith("ATOM")]
    chains = {}
    for l in atoms:
        chains.setdefault(l[21], []).append(l)
    return chains


def heavy_renumbered(lines, start):
    """Remove H e OXT, renumera residuos a partir de `start`; devolve (linhas, nomes_de_residuo)."""
    out, names, prev, n = [], [], None, start - 1
    for l in lines:
        an = l[12:16].strip()
        if an.startswith("H") or an == "OXT" or (an[0].isdigit() and "H" in an[:2]):
            continue
        key = l[22:27]
        if key != prev:
            n += 1
            prev = key
            names.append(l[17:20].strip())
        out.append(l[:21] + " " + f"{n:4d}" + " " + l[27:])
    return out, names


def build(complex_pdb: Path, out: Path, ph: float, cyclic: bool, pdb2pqr: str,
          rec_chain="A", pep_chain="B") -> dict:
    out.mkdir(parents=True, exist_ok=True)
    prot = protonate(complex_pdb, out, ph, pdb2pqr)
    chains = split_chains(prot)
    rec, rec_names = heavy_renumbered(chains[rec_chain], 1)
    n_rec = len(rec_names)
    pep, pep_names = heavy_renumbered(chains[pep_chain], n_rec + 1)
    n_pep = len(pep_names)

    # dissulfetos (CYX) do receptor
    sg = [l for l in rec if l[17:20] == "CYX" and l[12:16].strip() == "SG"]
    ss = []
    for i in range(len(sg)):
        for j in range(i + 1, len(sg)):
            if math.dist(xyz(sg[i]), xyz(sg[j])) < 2.4:
                ss.append((int(sg[i][22:26]), int(sg[j][22:26])))

    (out / "heavy.pdb").write_text("\n".join(rec + ["TER"] + pep + ["END"]) + "\n")

    def term(names, cyc):
        if cyc:
            return list(names)                       # todos internos; anel fechado por `bond`
        return ["N" + names[0]] + list(names[1:-1]) + ["C" + names[-1]]
    seq = term(rec_names, False) + term(pep_names, cyclic)

    def leap(extra, save):
        s = ("source oldff/leaprc.ff99SB\nloadamberparams frcmod.ff99SBildn\nsource leaprc.water.tip3p\n"
             f"mol = loadPdbUsingSeq heavy.pdb {{ {' '.join(seq)} }}\n")
        for a, b in ss:
            s += f"bond mol.{a}.SG mol.{b}.SG\n"
        if cyclic:
            s += f"bond mol.{n_rec + 1}.N mol.{n_rec + n_pep}.C\n"
        s += f"check mol\n{extra}{save}quit\n"
        return s

    # passo 1: solvata para contar a agua e dimensionar o sal
    (out / "leap1.in").write_text(leap(f"solvateOct mol TIP3PBOX {BUFFER_A}\n", "saveamberparm mol tmp.prmtop tmp.inpcrd\n"))
    p1 = run(["tleap", "-f", "leap1.in"], cwd=str(out))
    (out / "leap1.log").write_text(p1.stdout + p1.stderr)
    if not (out / "tmp.prmtop").exists() or (out / "tmp.prmtop").stat().st_size == 0:
        raise RuntimeError("tleap (passo 1) falhou; ver leap1.log")
    m = re.search(r"Added (\d+) residues", p1.stdout)
    n_wat = int(m.group(1)) if m else 0
    n_salt = max(1, round(SALT_M * n_wat / 55.5))
    # passo 2: neutraliza e adiciona sal
    (out / "leap2.in").write_text(leap(
        f"solvateOct mol TIP3PBOX {BUFFER_A}\naddIons2 mol Na+ 0\naddIons2 mol Cl- 0\n"
        f"addIonsRand mol Na+ {n_salt} Cl- {n_salt}\n",
        "saveamberparm mol sys.prmtop sys.inpcrd\n"))
    p2 = run(["tleap", "-f", "leap2.in"], cwd=str(out))
    (out / "leap2.log").write_text(p2.stdout + p2.stderr)
    if not (out / "sys.prmtop").exists() or (out / "sys.prmtop").stat().st_size == 0:
        raise RuntimeError("tleap (passo 2) falhou; ver leap2.log")

    parm = pmd.load_file(str(out / "sys.prmtop"), str(out / "sys.inpcrd"))
    for r in parm.residues:
        base = re.sub(r"^[NC](?=[A-Z]{3}$)", "", r.name) if len(r.name) == 4 else r.name
        r.name = RENAME_STD.get(base, base)
    solute_idx = [a.idx for a in parm.atoms if a.residue.name not in ("WAT", "HOH", "Na+", "Cl-", "NA", "CL")]
    # posre (heavy atoms do soluto), um arquivo por moleculetype de soluto
    parm.save(str(out / "topol.top"), format="gromacs", overwrite=True)
    parm.save(str(out / "solv_ions.gro"), format="gro", overwrite=True)
    report = {"ph": ph, "cyclic": cyclic, "n_receptor_res": n_rec, "n_peptide_res": n_pep,
              "peptide": "".join(_one(n) for n in pep_names), "disulfides": ss, "n_water": n_wat,
              "n_salt_pairs": n_salt, "total_charge_solute": None,
              "n_atoms_total": len(parm.atoms)}
    (out / "build_report.json").write_text(json.dumps(report, indent=2))
    _add_posre(out, parm)
    return report


_THREE = {"ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E",
          "GLY": "G", "HIS": "H", "HID": "H", "HIE": "H", "HIP": "H", "ILE": "I", "LEU": "L",
          "LYS": "K", "LYN": "K", "MET": "M", "PHE": "F", "PRO": "P", "SER": "S", "THR": "T",
          "TRP": "W", "TYR": "Y", "VAL": "V", "CYX": "C", "ASH": "D", "GLH": "E"}


def _one(n):
    return _THREE.get(n, "X")


def _add_posre(out: Path, parm) -> None:
    """Restricao posicional (1000 kJ/mol/nm2) nos atomos pesados do soluto, via #ifdef POSRES
    dentro de cada [ moleculetype ] de soluto, como o pdb2gmx faria."""
    top = (out / "topol.top").read_text().splitlines()
    starts = [i for i, l in enumerate(top) if l.strip().startswith("[ moleculetype ]")]
    sys_i = next(i for i, l in enumerate(top) if l.strip().startswith("[ system ]"))
    bounds = starts + [sys_i]
    new, cursor = [], 0
    for k, s in enumerate(starts):
        e = bounds[k + 1]
        block = top[s:e]
        # nome e numero de atomos do moleculetype
        names = [l for l in block[1:] if l.strip() and not l.startswith(";")]
        mol_name = names[0].split()[0]
        atoms_i = next(i for i, l in enumerate(block) if l.strip().startswith("[ atoms ]"))
        heavy = []
        for l in block[atoms_i + 1:]:
            if l.strip().startswith("["):
                break
            if not l.strip() or l.strip().startswith(";"):
                continue
            f = l.split()
            if f[3] in ("WAT", "HOH", "SOL") or f[3] in ("Na+", "Cl-", "NA", "CL"):
                heavy = None
                break
            if not f[4].startswith("H"):
                heavy.append(int(f[0]))
        new.extend(top[cursor:e])
        if heavy:
            pr = out / f"posre_{mol_name}.itp"
            pr.write_text("[ position_restraints ]\n; atom  type      fx      fy      fz\n" +
                          "".join(f"{i:6d}     1  1000  1000  1000\n" for i in heavy))
            new.extend(["", "; Include Position restraint file", "#ifdef POSRES",
                        f'#include "{pr.name}"', "#endif", ""])
        cursor = e
    new.extend(top[cursor:])
    (out / "topol.top").write_text("\n".join(new) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--complex", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ph", type=float, default=10.0)
    ap.add_argument("--cyclic", action="store_true")
    ap.add_argument("--pdb2pqr", default="pdb2pqr30")
    a = ap.parse_args()
    rep = build(Path(a.complex).resolve(), Path(a.out).resolve(), a.ph, a.cyclic, a.pdb2pqr)
    print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()

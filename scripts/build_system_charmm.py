"""
build_system_charmm.py -- monta o sistema receptor+peptideo solvatado para o GROMACS com CHARMM36
(port charmm2gmx de fev/2026, o mesmo .ff usado pelo grupo em ~/gromacs/Milena-MD) + TIP3P (CHARMM),
para o peptideo LINEAR e para o MACROCICLO cabeca-cauda (ligacao C(n)-N(1)).

Substitui scripts/build_system_tleap.py (AMBER ff99SB-ILDN) nas analises de MD.

Fluxo (mesmo do grupo: PREPARE_PH -> TOPOLOGY -> BOX_SOLVATE_IONS):
  1. PDB2PQR/PROPKA no pH informado (nomenclatura AMBER) -> remove H -> renomeia para CHARMM
     (HID/HIE->HSD/HSE, HIP->HSP, CYX->CYS2, LYN->LSN, ASH->ASPP, GLH->GLUP);
  2. pdb2gmx -ter -chainsep ter -merge no (uma [moleculetype] por cadeia; receptor = A, peptideo = B);
  3. MACROCICLO: o GROMACS >= 2024 fecha o anel sozinho quando a distancia C-N da predicao e' de ligacao
     (verificado: sem menu de terminal, ligacao C(n)-N(1) + angulos, diedros, pares, impropers e CMAP em
     todos os residuos, com os parametros do proprio CHARMM36). `verify_ring` confere o anel no itp e
     aborta se estiver aberto -- nunca segue com um linear sem terminais;
  4. editconf -> solvate -> genion (KCl 0,10 M por padrao, hemolinfa/intestino de inseto, igual ao grupo).
Extremidades do peptideo LINEAR (decisao de 01/10/2026, modelo biologico): C-terminal COO- (pKa 3,3) e N-terminal
NEUTRO (NH2 / GLY-NH2) quando pH - 7,7 >= 2 (pKa medio do N-terminal em proteinas dobradas 7,7 +- 0,5; Grimsley,
Scholtz e Pace 2009, Protein Sci 18:247, doi 10.1002/pro.19) -- no pH 10 do intestino medio, <1% protonado. O 1o
residuo Pro nao tem patch neutro no campo (so PRO-NH2+): fica carregado e e' registrado em build_report.json.
So o peptideo (cadeia B); o N-terminal do receptor continua NH3+. (As 8 MDs lineares anteriores usaram NH3+.)
No macrociclo nao ha extremidades.

Saidas em OUT: solv_ions.gro, topol.top (+ itp/posre por cadeia, link simbolico do .ff), build_report.json.
Uso: python -m scripts.build_system_charmm --complex boltz.pdb --out DIR --ph 10.0 [--cyclic] \
         --gmx ~/miniforge3/envs/md-gromacs/bin/gmx_mpi --pdb2pqr pdb2pqr30 --ff-dir <...>.ff
"""
import argparse
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

DEFAULT_FF_DIR = "~/gromacs/Milena-MD/ff/charmm36-feb2026_cgenff-5.0.ff"

# PDB2PQR (--ffout AMBER) -> residuos do .rtp do CHARMM36 no GROMACS (mesmo mapa do grupo,
# bin/pdb2pqr_process.py, + LYN->LSN para Lys neutra em pH alto). CYM existe no rtp e fica como esta.
RENAME_CHARMM = {
    "HISD": "HSD", "HID": "HSD", "HISE": "HSE", "HIE": "HSE", "HISH": "HSP", "HIP": "HSP",
    "ASPH": "ASPP", "ASH": "ASPP", "GLUH": "GLUP", "GLH": "GLUP", "CYX": "CYS2", "LYN": "LSN",
}
_THREE = {"ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E",
          "GLY": "G", "HSD": "H", "HSE": "H", "HSP": "H", "HIS": "H", "ILE": "I", "LEU": "L",
          "LYS": "K", "LSN": "K", "MET": "M", "PHE": "F", "PRO": "P", "SER": "S", "THR": "T",
          "TRP": "W", "TYR": "Y", "VAL": "V", "CYS2": "C", "CYM": "C", "ASPP": "D", "GLUP": "E"}


def sh(cmd, cwd, stdin=None, timeout=900):
    return subprocess.run(cmd, cwd=str(cwd), input=stdin, capture_output=True, text=True, timeout=timeout)


def protonate(complex_pdb: Path, out: Path, ph: float, pdb2pqr: str) -> Path:
    prot = out / "protonated.pdb"
    p = sh([pdb2pqr, "--ff", "AMBER", "--ffout", "AMBER", "--titration-state-method", "propka",
            "--with-ph", str(ph), "--keep-chain", "--nodebump", "--pdb-output", str(prot),
            str(complex_pdb), str(out / "protonated.pqr")], out, timeout=300)
    if p.returncode != 0 or not prot.exists():
        raise RuntimeError(f"pdb2pqr falhou: {p.stderr[-400:]}")
    return prot


def heavy_charmm_pdb(prot: Path, out: Path, cyclic: bool, rec_chain="A", pep_chain="B"):
    """PDB so com atomos pesados (o pdb2gmx -ignh recoloca H), nomes CHARMM, TER entre cadeias.
    No macrociclo remove OXT (nao existe terminal). Devolve (n_res_receptor, sequencia_do_peptideo)."""
    chains = {}
    for l in prot.read_text().splitlines():
        if l.startswith("ATOM"):
            chains.setdefault(l[21], []).append(l)
    if rec_chain not in chains or pep_chain not in chains:
        raise RuntimeError(f"cadeias {rec_chain}/{pep_chain} ausentes; ha {sorted(chains)}")
    out_lines, info = [], {}
    for ch in (rec_chain, pep_chain):
        seen, names = None, []
        for l in chains[ch]:
            an = l[12:16].strip()
            if an.startswith("H") or (an[0].isdigit() and "H" in an[:2]):
                continue
            if an == "OXT" and cyclic and ch == pep_chain:
                continue
            rn = l[17:21].strip()
            rn = RENAME_CHARMM.get(rn, rn)
            if l[22:27] != seen:
                seen = l[22:27]
                names.append(rn)
            out_lines.append(l[:17] + f"{rn:<4s}" + l[21:])
        info[ch] = names
        out_lines.append("TER")
    (out / "heavy.pdb").write_text("\n".join(out_lines) + "\nEND\n")
    return len(info[rec_chain]), "".join(_THREE.get(n, "X") for n in info[pep_chain])


def _pick(items, wanted, kind):
    """items = [(indice, nome)]; devolve o indice do 1o nome que casa com `wanted` (sufixo/igual)."""
    for pref in wanted:
        for i, n in items:
            if n == pref:
                return i
    for pref in wanted:
        for i, n in items:
            if n.endswith(pref):
                return i
    raise RuntimeError(f"terminal {wanted} ausente do menu {kind}: {items}")


def pdb2gmx(gmx, out: Path, ff_name: str, water: str, cyclic: bool, log_name="pdb2gmx.log", nterm_neutral: bool = False):
    """pdb2gmx -ter conduzido de forma interativa: le cada menu de terminal e escolhe PELO NOME
    (NH3+ / COO- nas pontas do receptor e do peptideo linear; PRO-NH2+ se o 1o residuo e' Pro). No
    macrociclo fechado o pdb2gmx nao pergunta os terminais do peptideo (so' os 2 menus do receptor).
    O indice 0 NAO serve: o 1o item do menu e' um patch especifico do residuo (ex.: `MET1`, formil-Met)
    que quebra o pdb2gmx (`atom C1 not found in building block 1MET`)."""
    import select
    import time
    cmd = [gmx, "pdb2gmx", "-f", "heavy.pdb", "-o", "complexo.gro", "-p", "topol.top", "-i", "posre.itp",
           "-ff", ff_name, "-water", water, "-ignh", "-ter", "-chainsep", "ter", "-merge", "no"]
    # pty: com pipe o gmx_mpi segura os menus no buffer e o pdb2gmx espera para sempre
    import pty
    master, slave = pty.openpty()
    proc = subprocess.Popen(cmd, cwd=str(out), stdin=slave, stdout=slave, stderr=slave, close_fds=True)
    os.close(slave)
    buf, answered, chosen, t0 = b"", 0, [], time.time()
    pat = re.compile(r"Select (start|end) terminus type for (\S+)\n((?:\s*\d+: .*\n)+)")
    while True:
        if time.time() - t0 > 900:
            proc.kill()
            raise RuntimeError("pdb2gmx excedeu 15 min")
        r, _, _ = select.select([master], [], [], 3.0)
        if r:
            try:
                chunk = os.read(master, 65536)
            except OSError:          # EIO: o processo fechou o pty (terminou)
                break
            if not chunk:
                break
            buf += chunk
            continue
        if proc.poll() is not None:
            break
        menus = pat.findall(buf.decode(errors="replace").replace("\r", ""))
        if len(menus) > answered:                      # prompt novo esperando resposta
            kind, res, block = menus[answered]
            items = [(int(m.group(1)), m.group(2).strip()) for m in re.finditer(r"^\s*(\d+): (.*)$", block, re.M)]
            chain = answered // 2
            if kind == "start":
                # Pro precisa do patch proprio (PRO-NH2+); o NH3+ generico quebra o grompp (sem ligacoes N-CD)
                if res.startswith("PRO"):
                    want = ["PRO-NH2+"]                     # sem patch neutro para Pro no campo
                elif nterm_neutral and chain == 1:          # peptideo (cadeia B), N-terminal neutro
                    want = ["GLY-NH2"] if res.startswith("GLY") else ["NH2"]
                else:
                    want = ["NH3+"]
                idx = _pick(items, want, f"{kind} {res}")
            else:
                idx = _pick(items, ["COO-"], f"{kind} {res}")
            chosen.append({"chain": "AB"[chain] if chain < 2 else chain, "terminus": kind, "residue": res,
                           "choice": dict(items)[idx]})
            os.write(master, f"{idx}\n".encode())
            answered += 1
    proc.wait()
    os.close(master)
    text = buf.decode(errors="replace").replace("\r", "")
    (out / log_name).write_text(text)
    if proc.returncode != 0 or not (out / "complexo.gro").exists():
        raise RuntimeError(f"pdb2gmx rc={proc.returncode}: {text[-700:]}")
    # o pdb2gmx pode nao perguntar os terminais de uma cadeia curta (observado no macrociclo GDGDG): a
    # validacao do resultado e' feita no itp (ver check_termini), nao pelo numero de menus
    return chosen


# ----------------------------------------------------------------------------------------- ciclizacao
def cn_distance(prot: Path, pep_chain="B") -> float:
    """Distancia (A) entre o C do ultimo residuo e o N do primeiro residuo do peptideo."""
    import math
    first = last = None
    rows = [l for l in prot.read_text().splitlines() if l.startswith("ATOM") and l[21] == pep_chain]
    keys = []
    for l in rows:
        if l[22:27] not in keys:
            keys.append(l[22:27])
    n = c = None
    for l in rows:
        if l[22:27] == keys[0] and l[12:16].strip() == "N":
            n = (float(l[30:38]), float(l[38:46]), float(l[46:54]))
        if l[22:27] == keys[-1] and l[12:16].strip() == "C":
            c = (float(l[30:38]), float(l[38:46]), float(l[46:54]))
    if n is None or c is None:
        raise RuntimeError("N do 1o residuo ou C do ultimo residuo ausentes no peptideo")
    return math.dist(n, c)


def verify_ring(itp: Path) -> dict:
    """O pdb2gmx (GROMACS >= 2024) fecha sozinho o peptideo ciclico quando a distancia C-N da predicao e'
    de ligacao: sem menu de terminal, com a ligacao C(n)-N(1) e os angulos, diedros, pares, impropers e CMAP
    do anel gerados com os mesmos parametros do CHARMM36 das ligacoes internas. Aqui so' CONFERE que o anel
    esta fechado e completo -- nunca segue com anel aberto (viraria um peptideo linear sem terminais)."""
    lines = itp.read_text().splitlines()
    sec = _sections(lines)
    by_res, resname = {}, {}
    for _, f in _data(lines, *sec["atoms"]):
        by_res.setdefault(int(f[2]), {})[f[4]] = int(f[0])
        resname[int(f[2])] = f[3]
    first, last = min(by_res), max(by_res)
    bad = [n for n in by_res[first] if n.startswith(("HT", "HN1", "HN2"))] +           [n for n in by_res[last] if n in ("OT1", "OT2", "OXT", "HT1")]
    if bad:
        raise RuntimeError(f"peptideo ciclico com atomos de terminal ({bad}): anel nao foi fechado")
    C, N1 = by_res[last]["C"], by_res[first]["N"]
    bonds = {frozenset((int(f[0]), int(f[1]))) for _, f in _data(lines, *sec["bonds"])}
    if frozenset((C, N1)) not in bonds:
        raise RuntimeError("ligacao C(n)-N(1) ausente: o pdb2gmx nao fechou o anel")
    n_cmap = len(_data(lines, *sec["cmap"])) if "cmap" in sec else 0
    if n_cmap != len(by_res):
        raise RuntimeError(f"anel com {n_cmap} CMAP (esperava {len(by_res)})")
    return {"closed_by": "pdb2gmx", "bond": [C, N1], "n_cmap": n_cmap, "first_res": resname[first],
            "last_res": resname[last]}


def _sections(lines):
    """indice {nome_da_secao: [i_inicio_dados, i_fim]} dentro de um itp (1a ocorrencia)."""
    idx, cur = {}, None
    for i, l in enumerate(lines):
        m = re.match(r"\s*\[\s*([A-Za-z_]+)\s*\]", l)
        if m:
            if cur:
                idx[cur][1] = i
            cur = m.group(1)
            idx.setdefault(cur, [i + 1, len(lines)])
    if cur:
        idx[cur][1] = len(lines)
    return idx


def _data(lines, a, b):
    return [(i, l.split(";")[0].split()) for i, l in enumerate(lines[a:b], start=a)
            if l.split(";")[0].strip() and not l.strip().startswith("#")]


def peptide_itp(out: Path) -> Path:
    """itp da cadeia B: a 2a [moleculetype] incluida no topol.top (receptor = A, peptideo = B)."""
    inc = re.findall(r'#include\s+"(topol_[^"]+\.itp)"', (out / "topol.top").read_text())
    if len(inc) < 2:
        raise RuntimeError(f"esperava 2 itps de cadeia (-merge no), achei {inc}")
    return out / inc[1]


NTERM_PKA = 7.7   # Grimsley, Scholtz e Pace 2009 (doi 10.1002/pro.19): N-terminal 7,7 +- 0,5 em proteinas dobradas


# --------------------------------------------------------------------------------------------- build
def build(complex_pdb, out, ph=10.0, cyclic=False, gmx="gmx_mpi", pdb2pqr="pdb2pqr30", ff_dir=DEFAULT_FF_DIR,
          water="tip3p", cation="K", salt_m=0.10, box_type="dodecahedron", box_d=1.2, nterm="charged") -> dict:
    complex_pdb, out = Path(complex_pdb).resolve(), Path(out).resolve()
    ff_dir = Path(os.path.expanduser(str(ff_dir))).resolve()
    if not (ff_dir / "forcefield.itp").exists():
        raise FileNotFoundError(f"campo de forca CHARMM36 nao encontrado em {ff_dir}")
    out.mkdir(parents=True, exist_ok=True)
    ff_name = ff_dir.name[:-3] if ff_dir.name.endswith(".ff") else ff_dir.name
    link = out / ff_dir.name
    if link.is_symlink() or link.exists():
        link.unlink()
    os.symlink(ff_dir, link)

    prot = protonate(complex_pdb, out, ph, pdb2pqr)
    n_rec, pep = heavy_charmm_pdb(prot, out, cyclic)
    cn = cn_distance(prot) if cyclic else None
    if cyclic and cn > 2.0:
        raise RuntimeError(f"macrociclo com distancia C(n)-N(1) = {cn:.2f} A (> 2,0): a predicao nao esta "
                           f"fechada e o pdb2gmx nao formaria a ligacao")
    # N-terminal do peptideo linear. Default "charged" DE PROPOSITO: o conjunto de MDs em curso foi montado
    # com NH3+ e um default "auto" mudaria o protocolo no meio do conjunto assim que um processo novo
    # reimportasse este modulo. Quem quer o estado dependente do pH pede "auto" explicitamente (md.nterm).
    nterm_neutral = (not cyclic) and (nterm == "neutral" or (nterm == "auto" and ph - NTERM_PKA >= 2.0))
    answers = pdb2gmx(gmx, out, ff_name, water, cyclic, nterm_neutral=nterm_neutral)
    ring = verify_ring(peptide_itp(out)) if cyclic else None
    if ring:
        ring["cn_distance_A"] = round(cn, 3)

    def run(step, cmd, stdin=None):
        p = sh(cmd, out, stdin=stdin, timeout=900)
        if p.returncode != 0:
            (out / f"{step}_stderr.log").write_text(p.stderr)
            raise RuntimeError(f"{step} rc={p.returncode}: {p.stderr[-600:]}")
        return p
    run("editconf", [gmx, "editconf", "-f", "complexo.gro", "-o", "box.gro", "-c", "-d", str(box_d), "-bt", box_type])
    run("solvate", [gmx, "solvate", "-cp", "box.gro", "-cs", "spc216.gro", "-p", "topol.top", "-o", "solv.gro"])
    (out / "ions.mdp").write_text("integrator = steep\nnsteps = 0\ncutoff-scheme = Verlet\n")
    run("grompp_ions", [gmx, "grompp", "-f", "ions.mdp", "-c", "solv.gro", "-p", "topol.top", "-o", "ions.tpr",
                        "-maxwarn", "2"])
    run("genion", [gmx, "genion", "-s", "ions.tpr", "-o", "solv_ions.gro", "-p", "topol.top",
                   "-pname", cation, "-nname", "CL", "-neutral", "-conc", str(salt_m)], stdin="SOL\n")
    report = {"forcefield": ff_name, "water": water, "ph": ph, "cyclic": cyclic, "n_receptor_res": n_rec,
              "peptide": pep, "n_peptide_res": len(pep), "terminals": answers, "ring": ring,
              "nterm_neutral": nterm_neutral, "nterm_pka_ref": NTERM_PKA,
              "cation": cation, "salt_M": salt_m, "box": f"{box_type} d={box_d} nm"}
    (out / "build_report.json").write_text(json.dumps(report, indent=2))
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--complex", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ph", type=float, default=10.0)
    ap.add_argument("--cyclic", action="store_true")
    ap.add_argument("--gmx", default="gmx_mpi")
    ap.add_argument("--pdb2pqr", default="pdb2pqr30")
    ap.add_argument("--ff-dir", default=DEFAULT_FF_DIR)
    ap.add_argument("--cation", default="K")
    ap.add_argument("--salt", type=float, default=0.10)
    a = ap.parse_args()
    print(json.dumps(build(a.complex, a.out, a.ph, a.cyclic, a.gmx, a.pdb2pqr, a.ff_dir,
                           cation=a.cation, salt_m=a.salt), indent=2))


if __name__ == "__main__":
    main()

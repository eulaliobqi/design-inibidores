"""
scissile_geometry.py -- geometria de ataque da Ser195 sobre cada carbonila do peptideo nas MDs ja existentes.

Para cada candidato (sequencia) e cada trajetoria (md10, md82 e as segundas sementes md10b/md82b), na segunda
metade da corrida e para cada ligacao peptidica i->i+1 (no macrociclo a ultima fecha com a primeira; no linear
a carbonila C-terminal e' excluida), mede:
  d_OG_C   distancia Ser195 OG -- C da carbonila
  ang      angulo OG...C=O (ataque nucleofilico ideal ~ 107 graus, Burgi-Dunitz)
  d_oxy    menor distancia O da carbonila -- N de Gly193 / Ser195 (buraco do oxianion)
  NAC      fracao de quadros com d_OG_C < 3,5 A, 90 <= ang <= 125 e d_oxy < 3,5 A (conformacao quase de ataque)
Descritivo: 10 ns nao medem catalise. Usa md.tpr + md_pbc_sub.xtc (gerado por analyze_md_top_candidates).
Uso (servidor, a partir de ~/design-inibidores): python -m scripts.scissile_geometry SEQ [SEQ ...] > saida.json
"""
import json
import sys
from pathlib import Path

import MDAnalysis as mda
import numpy as np
from MDAnalysis.lib.distances import distance_array, minimize_vectors

from scripts.analyze_md_top_candidates import _STD_RES, receptor_residues, resnum, std_resname

ROOT = Path(__file__).parent.parent
RUNS = [("md10", "pH 10.0 run1"), ("md10b", "pH 10.0 run2"), ("md82", "pH 8.2 run1"), ("md82b", "pH 8.2 run2")]


def find(seq):
    for tag, lab in RUNS:
        for F in "LM":
            p = ROOT / f"outputs/{tag}_{F}/analysis_summary.json"
            if not p.exists():
                continue
            for k, v in json.loads(p.read_text()).items():
                if v.get("sequence") == seq and "error" not in v:
                    yield tag, lab, F, k, bool(v.get("cyclic"))


def run(tag, F, key, seq, cyclic):
    d = ROOT / f"outputs/{tag}_{F}/{key}"
    res_map = receptor_residues(key.split("__")[0])
    u = mda.Universe(str(d / "md.tpr"), str(d / "md_pbc_sub.xtc"))
    prot = u.select_atoms("protein or resname " + " ".join(sorted(_STD_RES)))
    n_rec = len(prot.residues) - len(seq)
    rec, pep = prot.residues[:n_rec], prot.residues[n_rec:]
    sn = resnum(res_map["SER195"])
    ser = rec[rec.resids == sn]
    g193 = rec[rec.resids == sn - 2]
    assert len(ser) == 1 and std_resname(ser[0].resname) == "SER", "Ser195"
    og = ser.atoms.select_atoms("name OG")
    oxy = ser.atoms.select_atoms("name N") + g193.atoms.select_atoms("name N")
    g193_name = g193[0].resname if len(g193) else None
    n_b = len(seq) if cyclic else len(seq) - 1
    C = [pep[i].atoms.select_atoms("name C")[0] for i in range(n_b)]
    O = [pep[i].atoms.select_atoms("name O")[0] for i in range(n_b)]
    nf = len(u.trajectory)
    dOG, ANG, DOX = np.zeros((nf, n_b)), np.zeros((nf, n_b)), np.zeros((nf, n_b))
    for t, ts in enumerate(u.trajectory):
        box = ts.dimensions
        o = og.positions[0]
        for i in range(n_b):
            v1 = minimize_vectors((o - C[i].position)[None, :], box)[0]
            v2 = minimize_vectors((O[i].position - C[i].position)[None, :], box)[0]
            dOG[t, i] = np.linalg.norm(v1)
            ANG[t, i] = np.degrees(np.arccos(np.clip(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)), -1, 1)))
            DOX[t, i] = distance_array(O[i].position[None, :], oxy.positions, box=box).min()
    h2 = np.arange(nf) >= nf // 2
    nac = (dOG < 3.5) & (ANG >= 90) & (ANG <= 125) & (DOX < 3.5)
    out = []
    for i in range(n_b):
        nxt = seq[(i + 1) % len(seq)]
        out.append({"bond": f"{seq[i]}{i+1}-{nxt}{(i+1)%len(seq)+1}", "d_OG_C_median_A": round(float(np.median(dOG[h2, i])), 2),
                    "d_OG_C_min_A": round(float(dOG[h2, i].min()), 2), "frac_d_lt_4A": round(float((dOG[h2, i] < 4.0).mean()), 3),
                    "NAC_frac": round(float(nac[h2, i].mean()), 3), "NAC_frac_all": round(float(nac[:, i].mean()), 3)})
    return {"gly193_name": g193_name, "bonds": out}


if __name__ == "__main__":
    res = {}
    for seq in sys.argv[1:]:
        res[seq] = []
        for tag, lab, F, key, cyc in find(seq):
            try:
                res[seq].append({"run": lab, "dir": f"{tag}_{F}/{key}", **run(tag, F, key, seq, cyc)})
            except Exception as e:  # noqa: BLE001
                res[seq].append({"run": lab, "dir": f"{tag}_{F}/{key}", "error": f"{type(e).__name__}: {e}"})
    print(json.dumps(res, indent=1))

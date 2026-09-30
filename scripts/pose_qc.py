"""
pose_qc.py -- E4 do plano v3. QC de pose (limiares PRE-REGISTRADOS, herdados do projeto do grupo
`GOREs-boltz/qc_thresholds.yaml`) e matriz cruzada 8x8.

QC de pose (por PDB de complexo Boltz-2, cadeia A = receptor, B = peptideo):
  - pares de atomos pesados peptideo-receptor < 2.2 A                    (maximo 0)
  - ligacoes peptidicas: |omega| >= 150 graus (trans); Pro cis aceita
  - quiralidade L em todos os CA do peptideo (Gly excluida)
  - distancia His57 NE2 - Ser195 OG <= 3.8 A (triade mantida; Asp102 nao verificado: nao esta no
    mapa de subsitios do painel)
  - contato peptideo-Asp189 registrado (informativo)
  - macrociclo: distancia C(n)-N(1) <= 1.5 A e omega do fechamento >= 150 graus

Uso:
  python scripts/pose_qc.py qc --candidates data-b23-scoring/results/top_candidates_L.json --front L --out outputs/pose_qc_L.json
  python scripts/pose_qc.py matrix-prepare --candidates <top.json> --front L
  python scripts/pose_qc.py matrix-collect --front L
"""
import argparse
import json
import math
from pathlib import Path

import numpy as np
from Bio.PDB import PDBParser

from analyze_md_top_candidates import receptor_residues, resnum
from score_boltz2_b23 import get_receptor_sequence

ROOT = Path(__file__).parent.parent
RES = ROOT / "data-b23-scoring" / "results"
TH = {"clash_A": 2.2, "omega_min_deg": 150.0, "his_ser_max_A": 3.8, "ring_cn_max_A": 1.5}
SP8 = ["Sfrugiperda", "Slitura", "Onubilalis", "Dsaccharalis", "Cincludens", "Hvirescens",
       "Pxylostella", "Agemmatalis"]


def dihedral(p0, p1, p2, p3):
    b0, b1, b2 = p0 - p1, p2 - p1, p3 - p2
    b1 = b1 / np.linalg.norm(b1)
    v, w = b0 - np.dot(b0, b1) * b1, b2 - np.dot(b2, b1) * b1
    return math.degrees(math.atan2(np.dot(np.cross(b1, v), w), np.dot(v, w)))


def qc_pose(pdb: Path, species: str, cyclic: bool) -> dict:
    st = PDBParser(QUIET=True).get_structure("x", str(pdb))[0]
    rec, pep = list(st["A"]), list(st["B"])
    rmap = receptor_residues(species)
    rec_by = {r.id[1]: r for r in rec}
    heavy_r = np.array([a.coord for r in rec for a in r if a.element != "H"])
    heavy_p = np.array([a.coord for r in pep for a in r if a.element != "H"])
    dmat = np.linalg.norm(heavy_p[:, None, :] - heavy_r[None, :, :], axis=2)
    n_clash = int((dmat < TH["clash_A"]).sum())
    omegas, cis_pro = [], 0
    for i in range(len(pep) - 1):
        a, b = pep[i], pep[i + 1]
        om = dihedral(a["CA"].coord, a["C"].coord, b["N"].coord, b["CA"].coord)
        omegas.append(om)
        if abs(om) < TH["omega_min_deg"] and b.get_resname() == "PRO":
            cis_pro += 1
    ring = {}
    if cyclic:
        a, b = pep[-1], pep[0]
        om = dihedral(a["CA"].coord, a["C"].coord, b["N"].coord, b["CA"].coord)
        d = float(np.linalg.norm(a["C"].coord - b["N"].coord))
        ring = {"ring_CN_A": round(d, 3), "ring_omega_deg": round(om, 1),
                "ring_ok": bool(d <= TH["ring_cn_max_A"] and abs(om) >= TH["omega_min_deg"])}
    n_nonL = 0
    for r in pep:
        if r.get_resname() == "GLY":
            continue
        n, ca, c, cb = (r[k].coord for k in ("N", "CA", "C", "CB"))
        if np.dot(np.cross(n - ca, c - ca), cb - ca) > 0:   # convencao: L => produto misto < 0
            n_nonL += 1
    his = rec_by[resnum(rmap["HIS57"])]["NE2"].coord
    ser = rec_by[resnum(rmap["SER195"])]["OG"].coord
    asp = rec_by[resnum(rmap["ASP189"])]
    d_hs = float(np.linalg.norm(his - ser))
    d_asp = float(np.linalg.norm(heavy_p[:, None, :] - np.array([a.coord for a in asp])[None, :, :],
                                 axis=2).min())
    nonstd = sum(1 for o in omegas if abs(o) < TH["omega_min_deg"]) - cis_pro
    out = {"min_dist_pep_rec_A": round(float(dmat.min()), 2), "n_severe_clash_pairs": n_clash,
           "omega_nonTrans_nonPro": int(nonstd), "n_nonL_CA": int(n_nonL),
           "his57_ser195_A": round(d_hs, 2), "triad_ok": bool(d_hs <= TH["his_ser_max_A"]),
           "pep_asp189_min_A": round(d_asp, 2), **ring}
    out["qc_pass"] = bool(n_clash == 0 and nonstd == 0 and n_nonL == 0 and out["triad_ok"]
                          and (not cyclic or ring["ring_ok"]))
    return out


def cmd_qc(a):
    cands = json.loads(Path(a.candidates).read_text())["candidates"]
    res = {}
    for key, c in cands.items():
        sp = c.get("species", key.split("__")[0])
        try:
            res[key] = {"sequence": c["sequence"], **qc_pose(ROOT / c["pdb"], sp, a.front == "M")}
        except Exception as e:  # noqa: BLE001 - reporta por candidato
            res[key] = {"sequence": c["sequence"], "error": f"{type(e).__name__}: {e}", "qc_pass": False}
    Path(a.out).write_text(json.dumps(res, indent=2))
    print(f"QC {a.front}: {sum(1 for v in res.values() if v.get('qc_pass'))}/{len(res)} aprovados")


def cmd_matrix_prepare(a):
    cands = json.loads(Path(a.candidates).read_text())["candidates"]
    man = {}
    d = RES / f"boltz_yaml_matrix_{a.front}"
    cyc = "      cyclic: true\n" if a.front == "M" else ""
    for key, c in cands.items():
        if c.get("rank", 1) != 1:
            continue
        origin = c.get("species", key)
        for tsp in SP8:
            rseq = get_receptor_sequence(tsp)
            msa = (ROOT / "data-b23-scoring/msa_cache" / f"receptor_{tsp}.csv").resolve()
            stem = f"{tsp}__from_{origin}"
            (d / tsp).mkdir(parents=True, exist_ok=True)
            (d / tsp / f"{stem}.yaml").write_text(
                f"version: 1\nsequences:\n  - protein:\n      id: A\n      sequence: {rseq}\n"
                f"      msa: {msa}\n  - protein:\n      id: B\n      sequence: {c['sequence']}\n"
                f"{cyc}      msa: empty\n")
            man[stem] = {"receptor": tsp, "peptide_of": origin, "sequence": c["sequence"]}
    (RES / f"manifest_matrix_{a.front}.json").write_text(json.dumps(man, indent=2))
    print("matriz", a.front, len(man), "predicoes")


def cmd_matrix_collect(a):
    man = json.loads((RES / f"manifest_matrix_{a.front}.json").read_text())
    out = {}
    for stem, m in man.items():
        f = (ROOT / f"outputs/b23_boltz2_matrix_{a.front}_{m['receptor']}/boltz_results_{m['receptor']}"
             f"/predictions/{stem}/confidence_{stem}_model_0.json")
        if f.exists():
            out[stem] = {**m, "confidence_score": json.loads(f.read_text())["confidence_score"]}
    (RES / f"matrix_{a.front}.json").write_text(json.dumps(out, indent=2))
    print("matriz", a.front, len(out), "/", len(man))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("qc")
    p.add_argument("--candidates", required=True)
    p.add_argument("--front", choices=["L", "M"], required=True)
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_qc)
    p = sub.add_parser("matrix-prepare")
    p.add_argument("--candidates", required=True)
    p.add_argument("--front", choices=["L", "M"], required=True)
    p.set_defaults(func=cmd_matrix_prepare)
    p = sub.add_parser("matrix-collect")
    p.add_argument("--front", choices=["L", "M"], required=True)
    p.set_defaults(func=cmd_matrix_collect)
    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()

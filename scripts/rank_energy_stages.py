"""
rank_energy_stages.py -- classificacao dos peptideos finais pela pontuacao em cada etapa e por um escore agregado.

Etapas (cada uma da a cada candidato um posto, 1 = melhor, dentro do conjunto avaliado; empates recebem o posto medio):
  E2   confianca media do Boltz-2 (5 amostras x 3 sementes)                     maior e' melhor
  E3   diferenca pareada frente aos controles embaralhados (Boltz-2)           maior e' melhor   (sem dado: etapa omitida)
  MD10 RMSD local do peptideo na janela final da MD de 10 ns (pH 10)           menor e' melhor
  PRODIGY-pose   dG do PRODIGY na pose inicial (pH 8,2) e dG por residuo         menor e' melhor (media dos dois postos)
  PRODIGY-MD     dG do PRODIGY no conjunto de quadros da MD de pH 8,2           menor e' melhor (media dos dois postos)
  MMGBSA         dG de MM-GBSA (GB, igb=5, 0,15 M) da MD de pH 8,2; e por residuo menor e' melhor (media dos dois)
Portoes (nao entram no posto): criterio duro de nao clivagem (todos), controle de qualidade de pose, e, nos macrociclos,
o criterio estrito do anel.
A ocupancia de S1 NAO entra: acompanha a pose inicial (Secao 3.9).

O escore agregado e' a media dos postos das etapas disponiveis; o dG por residuo corrige o tamanho do peptideo, porque o
PRODIGY e o MM-GBSA crescem com a interface (calibracao: MM-GBSA acompanha o tamanho da interface, rho = -0,93).

Uso: python -m scripts.rank_energy_stages --stages pre        (selecao dos finalistas para a MD de pH 8,2)
     python -m scripts.rank_energy_stages --stages all        (ranking final, com PRODIGY-MD e MM-GBSA)
"""
import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data-e2-results"


def ranks(vals, higher_better):
    """Posto 1..n com empate pelo posto medio; None fica sem posto."""
    idx = [(i, v) for i, v in enumerate(vals) if v is not None]
    idx.sort(key=lambda t: -t[1] if higher_better else t[1])
    out = [None] * len(vals)
    i = 0
    while i < len(idx):
        j = i
        while j + 1 < len(idx) and idx[j + 1][1] == idx[i][1]:
            j += 1
        for k in range(i, j + 1):
            out[idx[k][0]] = (i + j) / 2 + 1
        i = j + 1
    return out


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def load_rows():
    rows = list(csv.DictReader(open(ROOT / "manuscript/figures/ranking_final.csv", encoding="utf-8")))
    md = {F: json.loads((DATA / f"md10_{F}_analysis.json").read_text()) for F in "LM"}
    pp = json.loads((DATA / "prodigy_poses.json").read_text())
    dl = {}
    for F in "LM":
        for sp, lst in json.loads((DATA / f"delta_paired_{F}.json").read_text()).items():
            for e in lst:
                dl[(F, sp, e["sequence"])] = e["delta"]
    out = []
    for r in rows:
        F, k = r["front"], r["key"]
        m = md[F].get(k, {})
        p = pp.get(f"{F}:{k}", {})
        n = len(r["sequence"])
        out.append({
            "front": F, "key": k, "sequence": r["sequence"], "species": r["species"], "tier": r["tier"], "n_res": n,
            "qc_pose": r["qc_pose"] == "True", "ring_strict": {"True": True, "False": False}.get(r["ring_strict"]),
            "E2": fnum(r["confidence_E2"]), "E3": dl.get((F, r["species"], r["sequence"]), fnum(r["delta_E3"])),
            "MD10_rmsd": m.get("peptide_rmsd_local_nm_final20pct"),
            "PRODIGY_pose": p.get("dG_kcal"),
            "PRODIGY_pose_res": (p["dG_kcal"] / n) if p.get("dG_kcal") is not None else None,
        })
    return out


def attach(rows, path, field, prefix):
    p = Path(path)
    if not p.exists():
        return
    d = json.loads(p.read_text())
    for r in rows:
        v = d.get(f'{r["front"]}:{r["key"]}', {}).get(field)
        r[prefix] = v
        r[prefix + "_res"] = (v / r["n_res"]) if v is not None else None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stages", choices=["pre", "all"], default="pre")
    ap.add_argument("--pool", choices=["all", "gated", "finalists"], default="gated",
                    help="gated: so quem passa o QC de pose, tem delta>0 (ou sem dado) e, nos macrociclos, anel estrito; "
                         "finalists: os candidatos da MD de pH 8,2 (data-e2-results/finalists_ph82.json)")
    ap.add_argument("--out", default="outputs/ranking_energy")
    a = ap.parse_args()
    rows = load_rows()
    if a.stages == "all":
        mm = {}
        for F in "LM":
            pth = ROOT / f"outputs/mmgbsa_md82_{F}.json"
            if pth.exists():
                for k, v in json.loads(pth.read_text()).items():
                    if v.get("status") == "real":
                        mm[f"{F}:{k}"] = {"dG_gb_kcal": v.get("dG_gb_kcal"), "sem": v.get("sem_blocks"),
                                          "dG_kcal_mean": (v.get("PRODIGY_md") or {}).get("dG_kcal_mean")}
        for r in rows:
            m = mm.get(f'{r["front"]}:{r["key"]}', {})
            for src, dst in (("dG_gb_kcal", "MMGBSA"), ("dG_kcal_mean", "PRODIGY_md")):
                v = m.get(src)
                r[dst] = v
                r[dst + "_res"] = (v / r["n_res"]) if v is not None else None
            r["MMGBSA_sem"] = m.get("sem")
    pool = rows
    if a.pool == "finalists":
        fin = json.loads((DATA / "finalists_ph82.json").read_text())
        keep = {(F, x["key"]) for F in fin for x in fin[F]}
        pool = [r for r in rows if (r["front"], r["key"]) in keep]
        if a.stages == "all":
            pool = [r for r in pool if r.get("MMGBSA") is not None]
    if a.pool == "gated":
        pool = [r for r in rows if r["qc_pose"] and (r["E3"] is None or r["E3"] > 0)
                and (r["front"] == "L" or r["ring_strict"])]
    stage_defs = [("E2", ["E2"], True), ("E3", ["E3"], True), ("MD10", ["MD10_rmsd"], False),
                  ("PRODIGY_pose", ["PRODIGY_pose", "PRODIGY_pose_res"], False)]
    if a.stages == "all":
        stage_defs += [("PRODIGY_md", ["PRODIGY_md", "PRODIGY_md_res"], False), ("MMGBSA", ["MMGBSA", "MMGBSA_res"], False)]
    for F in ("L", "M", "ALL"):
        sub = [r for r in pool if F == "ALL" or r["front"] == F]
        for name, cols, hb in stage_defs:
            rk = [ranks([r.get(c) for r in sub], hb) for c in cols]
            for i, r in enumerate(sub):
                vals = [x[i] for x in rk if x[i] is not None]
                r[f"rank_{name}_{F}"] = sum(vals) / len(vals) if vals else None
        for r in sub:
            rs = [r[f"rank_{n}_{F}"] for n, _, _ in stage_defs if r.get(f"rank_{n}_{F}") is not None]
            r[f"agg_{F}"] = sum(rs) / len(rs) if rs else None
            r[f"nstages_{F}"] = len(rs)
        order = sorted(sub, key=lambda r: (r[f"agg_{F}"] is None, r[f"agg_{F}"]))
        for pos, r in enumerate(order, 1):
            r[f"pos_{F}"] = pos
    out = ROOT / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    keys = sorted({k for r in pool for k in r})
    with open(str(out) + f"_{a.stages}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in sorted(pool, key=lambda r: (r["front"], r.get("pos_" + r["front"], 99))):
            w.writerow(r)
    json.dump(pool, open(str(out) + f"_{a.stages}.json", "w"), indent=1)
    print(f"pool={len(pool)} de {len(rows)}")
    for F in "LM":
        print("== frente", F)
        for r in sorted([r for r in pool if r["front"] == F], key=lambda r: r[f"pos_{F}"])[:12]:
            print(f'{r[f"pos_{F}"]:2d} {r["sequence"]:14s} {r["species"]:13s} agg={r[f"agg_{F}"]:.1f} E2={r["E2"]} d3={r["E3"]} '
                  f'rmsd={r["MD10_rmsd"]} prodigy={r["PRODIGY_pose"]}')


if __name__ == "__main__":
    main()

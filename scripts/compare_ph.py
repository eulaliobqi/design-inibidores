"""
compare_ph.py -- comparacao pareada pH 8,2 x pH 10,0 dos mesmos 48 candidatos finais (mesma pose inicial do Boltz-2, mesmo
protocolo CHARMM36 de 10 ns; so o pH muda e, com ele, o estado de protonacao atribuido pelo PROPKA e o numero de contraions).
O N-terminal do peptideo linear e' NH3+ nos dois pH (md.nterm: "charged" no pH 10 original; "auto" mantem NH3+ em pH 8,2).

Le (no servidor ou, em copia, em data-e2-results/):
  outputs/md10_{L,M}/analysis_summary.json   e   outputs/md82_{L,M}/analysis_summary.json     (analyze_md_top_candidates)
  outputs/mmgbsa_md10_{L,M}.json             e   outputs/mmgbsa_md82_{L,M}.json                (mmgbsa_md82.py)
  outputs/md10b_*/ e md82b_*/ (opcional)  replicas com outra semente: piso de ruido entre execucoes do mesmo pH
Escreve outputs/compare_ph.{json,csv,md}.

Leitura: com uma execucao por candidato e pH, uma diferenca so e' atribuivel ao pH se passar do que duas execucoes do mesmo
pH diferem entre si (piso de ruido, quando as replicas existirem). Nada aqui e' inferencia sobre afinidade.
"""
import csv
import json
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
METRICS = [
    ("d_anchor_asp_fim_A", "distancia final ancora-Asp189 (A)"),
    ("occ_5A_h2", "ocupancia de S1 a 5 A, 2a metade"),
    ("peptide_rmsd_local_nm_final20pct", "RMSD local final do peptideo (nm)"),
    ("contact_any_frac_4.5A", "fracao de quadros com contato com o receptor"),
    ("ser195_contact_frac_4.5A", "fracao com contato com a Ser catalitica"),
    ("his57_contact_frac_4.5A", "fracao com contato com a His catalitica"),
]


def load(tag, F):
    for base in (ROOT / "outputs", ROOT / "data-e2-results"):
        for name in (f"{tag}_{F}/analysis_summary.json", f"{tag}_{F}_analysis.json"):
            p = base / name
            if p.exists():
                return json.loads(p.read_text())
    return {}


def load_mm(tag, F):
    for base in (ROOT / "outputs", ROOT / "data-e2-results"):
        p = base / f"mmgbsa_{tag}_{F}.json"
        if p.exists():
            return {k: v for k, v in json.loads(p.read_text()).items() if v.get("status") == "real"}
    return {}


def wilcoxon(d):
    from scipy.stats import wilcoxon as w
    d = [x for x in d if x != 0]
    if len(d) < 6:
        return None
    return float(w(d).pvalue)


def prot_diff(F, key):
    """Residuos cujo estado de protonacao (nome do residuo no protonated.pdb) difere entre os dois pH."""
    out = {}
    for tag in ("md10", "md82"):
        p = ROOT / "outputs" / f"{tag}_{F}" / key / "protonated.pdb"
        if not p.exists():
            return None
        res = {}
        for l in p.read_text().splitlines():
            if l.startswith("ATOM"):
                res[(l[21], l[22:26].strip())] = l[17:21].strip()
        out[tag] = res
    diff = {f"{c}:{out['md10'][(c, n)]}{n}->{out['md82'].get((c, n))}": 1 for (c, n) in out["md10"]
            if out["md82"].get((c, n)) != out["md10"][(c, n)]}
    return sorted(diff)


def main():
    rows = []
    for F in "LM":
        a10, a82 = load("md10", F), load("md82", F)
        m10, m82 = load_mm("md10", F), load_mm("md82", F)
        for key, x in a10.items():
            y = a82.get(key)
            if not y or "occ_5A_h2" not in x or "occ_5A_h2" not in y:
                continue
            r = {"front": F, "key": key, "sequence": x["sequence"]}
            for m, _ in METRICS:
                r[m + "_pH10"], r[m + "_pH82"] = x.get(m), y.get(m)
            r["anchor_aa_pH10"], r["anchor_aa_pH82"] = x.get("anchor_aa"), y.get("anchor_aa")
            r["d_ini_pH10"], r["d_ini_pH82"] = x.get("d_anchor_asp_ini_A"), y.get("d_anchor_asp_ini_A")
            if F == "M":
                r["ring_ok_pH10"], r["ring_ok_pH82"] = x.get("ring_intact"), y.get("ring_intact")
            for tag, mm, suf in (("md10", m10, "pH10"), ("md82", m82, "pH82")):
                v = mm.get(key)
                if v:
                    r["mmgbsa_" + suf] = v.get("dG_gb_kcal")
                    r["mmgbsa_sem_" + suf] = v.get("sem_blocks")
                    r["prodigy_md_" + suf] = (v.get("PRODIGY_md") or {}).get("dG_kcal_mean")
            r["prot_diff"] = prot_diff(F, key)
            rows.append(r)
    out = {"n_pairs": len(rows), "metrics": {}, "agreement": {}}
    from scipy.stats import spearmanr
    for m, label in METRICS + [("mmgbsa", "MM-GBSA dG (kcal/mol)"), ("prodigy_md", "PRODIGY dG nos quadros (kcal/mol)")]:
        pairs = [(r.get(m + "_pH10"), r.get(m + "_pH82")) for r in rows]
        pairs = [(a, b) for a, b in pairs if a is not None and b is not None]
        if len(pairs) < 3:
            continue
        d = [b - a for a, b in pairs]
        rho = spearmanr([a for a, _ in pairs], [b for _, b in pairs])
        out["metrics"][m] = {"label": label, "n": len(pairs), "median_diff_82_minus_10": st.median(d),
                             "mean_diff": st.mean(d), "sd_diff": st.pstdev(d), "wilcoxon_p": wilcoxon(d),
                             "spearman_rho_between_pH": float(rho.statistic), "spearman_p": float(rho.pvalue)}
    # concordancia categorica
    occ = [(r["occ_5A_h2_pH10"] >= .7, r["occ_5A_h2_pH82"] >= .7) for r in rows]
    if occ:
        out["agreement"]["occupancy_ge_0.70"] = {"both": sum(a and b for a, b in occ), "only_pH10": sum(a and not b for a, b in occ),
                                                 "only_pH82": sum(b and not a for a, b in occ), "neither": sum(not a and not b for a, b in occ)}
        out["agreement"]["same_anchor_residue"] = sum(r["anchor_aa_pH10"] == r["anchor_aa_pH82"] for r in rows)
    nd = [len(r["prot_diff"]) for r in rows if r.get("prot_diff") is not None]
    if nd:
        out["protonation_states_differing_per_system"] = {"median": st.median(nd), "min": min(nd), "max": max(nd)}
    # piso de ruido: replicas do mesmo pH com outra semente (md10b_*, md82b_*)
    noise = {}
    for suf, tag, tagb in (("pH10", "md10", "md10b"), ("pH82", "md82", "md82b")):
        diffs = {m: [] for m, _ in METRICS}
        for F in "LM":
            a, b = load(tag, F), load(tagb, F)
            for key, y in b.items():
                x = a.get(key)
                if x and "occ_5A_h2" in x and "occ_5A_h2" in y:
                    for m, _ in METRICS:
                        if x.get(m) is not None and y.get(m) is not None:
                            diffs[m].append(abs(y[m] - x[m]))
        if any(diffs.values()):
            noise[suf] = {m: {"n": len(v), "median_abs_diff": st.median(v)} for m, v in diffs.items() if v}
    if noise:
        out["noise_floor_same_pH_other_seed"] = noise
        out["between_pH_median_abs_diff"] = {m: st.median([abs(r[m + "_pH82"] - r[m + "_pH10"]) for r in rows
                                                            if r.get(m + "_pH82") is not None and r.get(m + "_pH10") is not None])
                                             for m, _ in METRICS if any(r.get(m + "_pH10") is not None for r in rows)}
    (ROOT / "outputs").mkdir(exist_ok=True)
    (ROOT / "outputs/compare_ph.json").write_text(json.dumps({"summary": out, "rows": rows}, indent=1, default=str))
    keys = sorted({k for r in rows for k in r if k != "prot_diff"})
    with open(ROOT / "outputs/compare_ph.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys + ["prot_diff"])
        w.writeheader()
        for r in rows:
            w.writerow({**r, "prot_diff": ";".join(r["prot_diff"]) if r.get("prot_diff") else ""})
    md = [f"# pH 8,2 x pH 10,0 ({out['n_pairs']} candidatos pareados)\n", "| metrica | n | mediana(8,2 - 10) | media | dp | Wilcoxon p | rho Spearman entre pH |", "|---|---|---|---|---|---|---|"]
    for m, v in out["metrics"].items():
        md.append(f"| {v['label']} | {v['n']} | {v['median_diff_82_minus_10']:.3f} | {v['mean_diff']:.3f} | {v['sd_diff']:.3f} | "
                  f"{'' if v['wilcoxon_p'] is None else format(v['wilcoxon_p'], '.3g')} | {v['spearman_rho_between_pH']:.2f} |")
    md.append("\n" + json.dumps({k: out[k] for k in out if k not in ("metrics",)}, indent=1, default=str))
    (ROOT / "outputs/compare_ph.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    sys.exit(main())

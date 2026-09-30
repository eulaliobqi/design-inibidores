"""
analyze_filter_composition.py -- o que o filtro de clivagem circular seleciona?

Compara, por classe (RESISTENTE / MARGINAL / SUSCEPTIVEL), os candidatos da campanha B2.3
(8 especies): comprimento, presenca de K/R (sitio basico de P1 de tripsina), se o P1 geometrico
cai num K/R (ancora canonica possivel) e composicao de aminoacidos. Le o json de
run_cleavage_b23.py (regra circular). Sem nenhum dado novo alem das sequencias ja geradas.

Uso (servidor): python -m scripts.analyze_filter_composition --cleavage outputs/b23_cleavage_circular.json \
        --out data-b23-scoring/results/filter_composition.json
"""
import argparse
import collections
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
AA = "ACDEFGHIKLMNPQRSTVWY"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cleavage", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    d = json.loads((ROOT / args.cleavage).read_text())
    rows = collections.defaultdict(list)
    for sp, e in d["by_species"].items():
        for r in e["results"]:
            rows[r["verdict"]].append((sp, r))
    out = {"rule": d.get("rule")}
    for cls, lst in rows.items():
        n = len(lst)
        lens = [r["length"] for _, r in lst]
        anyKR = sum(any(a in "KR" for a in r["sequence"]) for _, r in lst)
        p1 = [(r["geometric_p1_1based"], r["sequence"]) for _, r in lst if r.get("geometric_p1_1based")]
        p1_is_KR = sum(1 for k, s in p1 if s[k - 1] in "KR")
        comp = collections.Counter("".join(r["sequence"] for _, r in lst))
        tot = sum(comp.values())
        out[cls] = {
            "n": n, "length_mean": round(sum(lens) / n, 2),
            "length_le_10_frac": round(sum(x <= 10 for x in lens) / n, 3),
            "length_hist": dict(sorted(collections.Counter(lens).items())),
            "any_KR_frac": round(anyKR / n, 3),
            "geometric_P1_is_KR_frac": round(p1_is_KR / max(1, len(p1)), 3),
            "aa_composition_pct": {a: round(100 * comp[a] / tot, 1) for a in AA},
            "by_species": dict(collections.Counter(sp for sp, _ in lst)),
        }
        print(cls, json.dumps({k: v for k, v in out[cls].items() if k not in ("aa_composition_pct", "length_hist", "by_species")}))
    (ROOT / args.out).write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

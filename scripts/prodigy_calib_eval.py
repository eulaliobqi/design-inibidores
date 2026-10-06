"""Avalia o PRODIGY na calibracao: em quantos dos 10 pares (5 inibidores x 2 receptores) o inibidor real tem dG mais
negativo que a isca embaralhada. Le outputs/prodigy_calib.json (scripts.prodigy_scores calib)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
c = json.loads((ROOT / "outputs/prodigy_calib.json").read_text())
n = tot = 0
rows = []
for r in ("bovine", "sfrug"):
    for i in ("BBI", "BPTI", "EcTI", "SFTI1", "SKTI"):
        a, b = c.get(f"{r}__{i}"), c.get(f"{r}__{i}_decoy")
        if a and b:
            ok = a["dG_kcal_mean"] < b["dG_kcal_mean"]
            n += ok
            tot += 1
            rows.append((r, i, a["dG_kcal_mean"], b["dG_kcal_mean"], a["ic_total_mean"], b["ic_total_mean"], ok))
            print(f'{r:7s} {i:6s} real {a["dG_kcal_mean"]:7.2f} isca {b["dG_kcal_mean"]:7.2f}  IC {a["ic_total_mean"]:5.0f} / {b["ic_total_mean"]:5.0f}  {"ok" if ok else "isca melhor"}')
print(f"pares em que o inibidor real pontua melhor: {n}/{tot}")
(ROOT / "outputs/prodigy_calib_pairs.json").write_text(json.dumps({"n_ok": n, "n_pairs": tot, "rows": rows}, indent=1))

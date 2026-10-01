"""
compare_ph_conditions.py -- compara as MDs de triagem (10 ns) em duas faixas de pH e com os dois estados do N-terminal do linear.

Condicoes (cada uma = top-3 por especie, 1 replica, CHARMM36; analise = analyze_md_top_candidates.py):
  L10c  linear, pH 10,0, N-terminal CARREGADO (NH3+)  [MD original, outputs/md10_L]
  L10n  linear, pH 10,0, N-terminal NEUTRO (pKa 7,7)   [outputs/mdph_L_ph10]
  L82   linear, pH  8,2, N-terminal NH3+ (76% protonado) [outputs/mdph_L_ph8.2]
  M10   macrociclo, pH 10,0                             [MD original, outputs/md10_M]
  M82   macrociclo, pH  8,2                             [outputs/mdph_M_ph8.2]
Comparacoes pareadas por candidato (mesma sequencia e mesma estrutura inicial): L10n x L10c (efeito do N-terminal a pH 10),
L82 x L10n (efeito do pH no linear) e M82 x M10 (efeito do pH no macrociclo). Descritivo: 1 replica de 10 ns por candidato;
a diferenca de ocupancia de um candidato entre condicoes inclui o ruido da trajetoria (nao ha inferencia por candidato).

Uso: python scripts/compare_ph_conditions.py --root outputs --out outputs/ph_comparison [--lang en|pt]
Saidas: ph_comparison.json e Figure12_pH_comparison.{png,pdf,tif} (en) ou fig12_comparacao_ph.* (pt).
"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

COND = {
    "L10c": ("L", "md10_L"), "L10n": ("L", "mdph_L_ph10"), "L82": ("L", "mdph_L_ph8.2"),
    "M10": ("M", "md10_M"), "M82": ("M", "mdph_M_ph8.2"),
}
PAIRS = [("L10n", "L10c"), ("L82", "L10n"), ("M82", "M10")]   # (y, x)
COL = {"L10c": "#9fb7cc", "L10n": "#457b9d", "L82": "#1d3557", "M10": "#7bc8bd", "M82": "#2a9d8f"}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default="outputs")
    ap.add_argument("--out", default="outputs/ph_comparison")
    ap.add_argument("--lang", default="en", choices=["en", "pt"])
    a = ap.parse_args()
    EN = a.lang == "en"
    T = (lambda en, pt: en if EN else pt)
    LAB = {
        "L10c": T("linear, pH 10, N-term NH3+", "linear, pH 10, N-term NH3+"),
        "L10n": T("linear, pH 10, N-term neutral", "linear, pH 10, N-term neutro"),
        "L82": T("linear, pH 8.2, N-term NH3+", "linear, pH 8,2, N-term NH3+"),
        "M10": T("macrocycle, pH 10", "macrociclo, pH 10"), "M82": T("macrocycle, pH 8.2", "macrociclo, pH 8,2"),
    }
    root, out = Path(a.root), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    data = {}
    for c, (_, d) in COND.items():
        p = root / d / "analysis_summary.json"
        if p.exists():
            data[c] = {k: v for k, v in json.load(open(p)).items() if "error" not in v and "occ_5A_h2" in v}
    res = {"conditions": {}, "pairs": {}}
    for c, d in data.items():
        v = list(d.values())
        res["conditions"][c] = {"label": LAB[c], "n": len(v), "n_pass": sum(x["passes_screen"] for x in v),
                                "mean_occ5_h2": round(float(np.mean([x["occ_5A_h2"] for x in v])), 3) if v else None}
    from scipy.stats import spearmanr, wilcoxon
    paired = {}
    for y, x in PAIRS:
        if y in data and x in data:
            keys = sorted(set(data[y]) & set(data[x]))
            if not keys:
                continue
            ox = np.array([data[x][k]["occ_5A_h2"] for k in keys]); oy = np.array([data[y][k]["occ_5A_h2"] for k in keys])
            r = {"n_paired": len(keys), "mean_delta_occ": round(float((oy - ox).mean()), 3),
                 "n_gain_pass": int(sum((not data[x][k]["passes_screen"]) and data[y][k]["passes_screen"] for k in keys)),
                 "n_lose_pass": int(sum(data[x][k]["passes_screen"] and (not data[y][k]["passes_screen"]) for k in keys)),
                 "n_changed_occ_gt_0.3": int((np.abs(oy - ox) > 0.3).sum())}
            if len(keys) >= 4 and np.ptp(ox) > 0 and np.ptp(oy) > 0:
                r["spearman"] = round(float(spearmanr(ox, oy)[0]), 2)
            if len(keys) >= 6 and np.any(oy != ox):
                r["wilcoxon_p_descriptive"] = round(float(wilcoxon(oy, ox).pvalue), 3)
            res["pairs"][f"{y}_vs_{x}"] = r
            paired[(y, x)] = (keys, ox, oy)
    (out / "ph_comparison.json").write_text(json.dumps(res, indent=2, ensure_ascii=False))

    # ---- figura
    plt.rcParams.update({"font.size": 9, "savefig.dpi": 300, "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(2, 3, figsize=(13, 7.4))
    # A: linear, linhas pareadas entre as tres condicoes
    for panel, conds, ttl in ((ax[0, 0], ["L10c", "L10n", "L82"], T("Linear front", "Frente linear")),
                              (ax[0, 1], ["M10", "M82"], T("Macrocycle front", "Frente macrocíclica"))):
        have = [c for c in conds if c in data]
        if len(have) >= 1:
            keys = sorted(set.intersection(*[set(data[c]) for c in have]))
            for k in keys:
                panel.plot(range(len(have)), [data[c][k]["occ_5A_h2"] for c in have], "-o", ms=3, lw=.7, alpha=.55, color="gray")
            for i, c in enumerate(have):
                panel.scatter([i] * len(keys), [data[c][k]["occ_5A_h2"] for k in keys], s=16, color=COL[c], zorder=3)
            panel.set_xticks(range(len(have))); panel.set_xticklabels([LAB[c].replace(", ", "\n") for c in have], fontsize=7.5)
            ttl = f"{ttl} (n = {len(keys)})"
        panel.axhline(.7, ls="--", c="gray", lw=.8)
        panel.set_ylim(-.03, 1.05); panel.set_ylabel(T("S1 occupancy ≤5 Å, second half", "ocupância de S1 ≤5 Å, 2ª metade")); panel.set_title(ttl, fontsize=10)
    # C: n que passa a triagem por condicao
    cs = [c for c in COND if c in data]
    ax[0, 2].bar(range(len(cs)), [res["conditions"][c]["n_pass"] for c in cs], color=[COL[c] for c in cs])
    for i, c in enumerate(cs):
        ax[0, 2].text(i, res["conditions"][c]["n_pass"] + .05, f"{res['conditions'][c]['n_pass']}/{res['conditions'][c]['n']}", ha="center", fontsize=8)
    ax[0, 2].set_xticks(range(len(cs))); ax[0, 2].set_xticklabels([LAB[c].replace(", ", "\n") for c in cs], fontsize=6.5)
    ax[0, 2].set_ylabel(T("candidates passing the screen", "candidatos que passam na triagem")); ax[0, 2].set_title(T("Pre-registered screen", "Triagem pré-registrada"), fontsize=10)
    # D-F: dispersoes pareadas
    for panel, (y, x) in zip(ax[1], PAIRS):
        panel.plot([0, 1], [0, 1], ls=":", c="gray", lw=1)
        if (y, x) in paired:
            keys, ox, oy = paired[(y, x)]
            panel.scatter(ox, oy, s=22, color=COL[y], alpha=.85)
            r = res["pairs"][f"{y}_vs_{x}"]
            panel.text(.03, .97, f"n = {r['n_paired']}\n" + T("mean Δ = ", "Δ médio = ") + f"{r['mean_delta_occ']:+.2f}\n" +
                       T("gain/lose pass: ", "ganha/perde triagem: ") + f"{r['n_gain_pass']}/{r['n_lose_pass']}", va="top", fontsize=8)
        panel.axhline(.7, ls="--", c="gray", lw=.6); panel.axvline(.7, ls="--", c="gray", lw=.6)
        panel.set_xlim(-.03, 1.03); panel.set_ylim(-.03, 1.03)
        panel.set_xlabel(LAB[x] + T(" (occupancy)", " (ocupância)")); panel.set_ylabel(LAB[y] + T(" (occupancy)", " (ocupância)"))
        panel.set_title({"L10n": T("N-terminal charge at pH 10", "Carga do N-terminal em pH 10"), "L82": T("pH effect, linear", "Efeito do pH, linear"),
                         "M82": T("pH effect, macrocycle", "Efeito do pH, macrociclo")}[y], fontsize=10)
    for a_, L in zip(list(ax[0]) + list(ax[1]), "ABCDEF"):
        a_.text(-.12, 1.06, L, transform=a_.transAxes, fontsize=12, fontweight="bold")
    fig.suptitle(T("10-ns screening MDs in two pH ranges (one replicate per candidate; descriptive)", "MDs de triagem de 10 ns em duas faixas de pH (uma réplica por candidato; descritivo)"), fontsize=10)
    fig.tight_layout()
    name = "Figure12_pH_comparison" if EN else "fig12_comparacao_ph"
    fig.savefig(out / f"{name}.png"); fig.savefig(out / f"{name}.pdf")
    from PIL import Image
    Image.open(out / f"{name}.png").convert("RGB").save(out / f"{name}.tif", compression="tiff_lzw", dpi=(300, 300))
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

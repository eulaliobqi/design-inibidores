"""Figuras que dependem das MDs de pH 8,2 e das energias nas trajetorias (padrao da revista: frontiers_style.py):
  Figure7_pH_comparison        pH 8,2 x pH 10,0 pareado (48 pares)
  FigureS10_energy_trajectories MM-GBSA e PRODIGY nas trajetorias de pH 10 (48) contra tamanho, posicao e entre si
Uso (de manuscript/): python figures/make_figures_ph.py figures/final
Le data-e2-results/{mmgbsa_md10_{L,M}.json, md10_{L,M}_analysis.json} e, para pH 8,2,
data-e2-results/{mmgbsa_md82_{L,M}, md82_{L,M}_analysis}_parcial_2026-10-07.json.
Quando as 48 MDs de pH 8,2 terminarem, apontar --final para os arquivos completos e retirar a legenda 'partial'."""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr, wilcoxon

from frontiers_style import apply_style, mm_figsize, save_journal

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data-e2-results"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else Path(__file__).resolve().parent
OUT = OUT if OUT.is_absolute() else Path.cwd() / OUT
OUT.mkdir(parents=True, exist_ok=True)
apply_style()
BLUE, TEAL, ORANGE, RED, GREY = "#0072B2", "#2a9d8f", "#E69F00", "#D55E00", "#7f7f7f"
FOCUS = {"NGGRPDAP": RED, "GQNDS": ORANGE, "GGHSE": "#CC79A7", "GGKPGEP": "#009E73"}


def _p(v):
    return "P < 0.001" if v < 0.001 else f"P = {v:.3f}"


def load(prefix, suffix=""):
    out = {}
    for F in "LM":
        out[F] = json.load(open(DATA / f"{prefix}_{F}{suffix}.json"))
    return out


def letter(ax, L, dx=-0.2, dy=1.04):
    ax.text(dx, dy, L, transform=ax.transAxes, fontweight="bold", va="bottom", ha="left")


def pick82(final_name, partial_name):
    """Arquivos finais de pH 8,2 se ja existirem em data-e2-results; senao os parciais de 06/10."""
    if (DATA / f"{final_name}_L.json").exists():
        return {F: json.load(open(DATA / f"{final_name}_{F}.json")) for F in "LM"}
    return {F: json.load(open(DATA / f"{partial_name}_{F}_parcial_2026-10-07.json")) for F in "LM"}


def rows():
    """Uma linha por MD de pH 8,2 concluida, com as metricas dos dois pH."""
    m10, an10 = load("mmgbsa_md10"), load("md10", "_analysis")
    m82 = pick82("mmgbsa_md82", "mmgbsa_md82")
    an82 = pick82("md82_analysis", "md82_analysis") if (DATA / "md82_analysis_L.json").exists() else         ({F: json.load(open(DATA / f"md82_{F}_analysis.json")) for F in "LM"} if (DATA / "md82_L_analysis.json").exists() else
         {F: json.load(open(DATA / f"md82_{F}_analysis_parcial_2026-10-07.json")) for F in "LM"})
    R = []
    for F in "LM":
        for k, v in an82[F].items():
            if "error" in v or m82[F].get(k, {}).get("status") != "real":
                continue
            r = {"F": F, "k": k, "seq": v["sequence"]}
            for tag, a, m in (("8", v, m82[F][k]), ("10", an10[F][k], m10[F][k])):
                r["fim" + tag] = a["d_anchor_asp_fim_A"]
                r["occ" + tag] = a["occ_5A_h2"]
                r["dG" + tag] = m["dG_gb_kcal"]
                r["pr" + tag] = (m.get("PRODIGY_md") or {}).get("dG_kcal_mean")
            R.append(r)
    return R


def paired(ax, R, key, ylabel, hline=None):
    for r in R:
        c = FOCUS.get(r["seq"], GREY if r["F"] == "L" else TEAL)
        lw = 1.8 if r["seq"] in FOCUS else 0.9
        ax.plot([0, 1], [r[key + "10"], r[key + "8"]], color=c, lw=lw, alpha=1 if r["seq"] in FOCUS else .6, marker="o", ms=3.5)
    for s, c in FOCUS.items():
        for r in R:
            if r["seq"] == s and (s != "GQNDS" or r["F"] == "L"):
                dy = {"GQNDS": 6, "GGHSE": -6}.get(s, 0) if key == "occ" else ({"NGGRPDAP": 7, "GGKPGEP": -7}.get(s, 0) if key == "fim" else 0)
                if key == "occ" and s == "GGKPGEP":
                    dy = -10
                ax.annotate(s, (1, r[key + "8"]), xytext=(5, dy), textcoords="offset points", color=c, va="center", fontsize=8)
                break
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["pH 10.0", "pH 8.2"])
    ax.set_xlim(-.25, 1.75)
    if key == "occ":
        ax.set_ylim(-0.1, 1.08)
    ax.set_ylabel(ylabel)
    if hline is not None:
        ax.axhline(hline, color="k", lw=.8, ls=":")
    a = np.array([r[key + "8"] for r in R]); b = np.array([r[key + "10"] for r in R])
    p = wilcoxon(a, b).pvalue
    ax.set_title(f"Wilcoxon P = {p:.2f}", fontsize=8)


def agree(ax, R, key, xlabel, ylabel):
    a = np.array([r[key + "10"] for r in R], float); b = np.array([r[key + "8"] for r in R], float)
    for r, x, y in zip(R, a, b):
        ax.scatter(x, y, s=34, color=FOCUS.get(r["seq"], BLUE if r["F"] == "L" else TEAL), zorder=3,
                   edgecolors="k" if r["seq"] in FOCUS else "none", linewidths=.8)
    lo, hi = min(a.min(), b.min()), max(a.max(), b.max())
    ax.plot([lo, hi], [lo, hi], color=GREY, lw=1, ls=":")
    rho = spearmanr(a, b)
    ax.set_title(f"ρ = {rho.statistic:.2f} ({_p(rho.pvalue)})", fontsize=8, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)


def fig8():
    R = rows()
    n = len(R)
    fig, ax = plt.subplots(2, 3, figsize=mm_figsize("double", 125), layout="constrained")
    paired(ax[0, 0], R, "fim", "final anchor–Asp189 distance (Å)", hline=4.0)
    letter(ax[0, 0], "A")
    paired(ax[0, 1], R, "occ", "S1 occupancy, 2nd half (5 Å)", hline=0.7)
    letter(ax[0, 1], "B")
    agree(ax[0, 2], R, "fim", "pH 10.0 final distance (Å)", "pH 8.2 final distance (Å)")
    letter(ax[0, 2], "C")
    agree(ax[1, 0], R, "dG", "MM-GBSA ΔG, pH 10.0 (kcal/mol)", "MM-GBSA ΔG, pH 8.2 (kcal/mol)")
    letter(ax[1, 0], "D")
    agree(ax[1, 1], R, "pr", "PRODIGY ΔG, pH 10.0 (kcal/mol)", "PRODIGY ΔG, pH 8.2 (kcal/mol)")
    letter(ax[1, 1], "E")
    ax[1, 2].axis("off")
    from matplotlib.lines import Line2D
    key = [Line2D([0], [0], marker="o", ls="", color=BLUE, label="linear"),
           Line2D([0], [0], marker="o", ls="", color=TEAL, label="macrocycle")] + \
          [Line2D([0], [0], marker="o", ls="", color=c, mec="k", label=s) for s, c in FOCUS.items()]
    ax[1, 2].legend(handles=key, loc="upper left", frameon=False, title=f"n = {n} paired candidates\n(one run per pH)")
    return save_journal(fig, OUT / "Figure7_pH_comparison"), n


def figS10():
    m10, an10 = load("mmgbsa_md10"), load("md10", "_analysis")
    X = []
    for F in "LM":
        for k, v in m10[F].items():
            if v["dG_gb_kcal"] is None or "PRODIGY_md" not in v:
                continue
            a = an10[F][k]
            X.append((F, a["sequence"], len(a["sequence"]), v["dG_gb_kcal"], v["PRODIGY_md"]["dG_kcal_mean"], a["d_anchor_asp_fim_A"], a["occ_5A_h2"]))
    F_, seq, L, dg, pr, df, oc = zip(*X)
    L, dg, pr, df, oc = map(np.array, (L, dg, pr, df, oc))
    col = [BLUE if f == "L" else TEAL for f in F_]
    fig, ax = plt.subplots(1, 3, figsize=mm_figsize("double", 65), layout="constrained")
    for a_, x, y, xl, yl, L_ in ((ax[0], L, dg, "peptide length (residues)", "MM-GBSA ΔG (kcal/mol)", "A"),
                                 (ax[1], df, dg, "final anchor–Asp189 distance (Å)", "MM-GBSA ΔG (kcal/mol)", "B"),
                                 (ax[2], dg, pr, "MM-GBSA ΔG (kcal/mol)", "PRODIGY ΔG, frames (kcal/mol)", "C")):
        a_.scatter(x, y, s=24, c=col, alpha=.85)
        r = spearmanr(x, y)
        a_.set_title(f"ρ = {r.statistic:.2f} ({_p(r.pvalue)})", fontsize=8, fontweight="bold")
        a_.set_xlabel(xl)
        a_.set_ylabel(yl)
        letter(a_, L_)
    for s, c in FOCUS.items():
        for i, q in enumerate(seq):
            if q == s:
                ax[0].annotate(s, (L[i], dg[i]), xytext=(5, -2), textcoords="offset points", color=c, fontsize=8)
                break
    ax[0].scatter([], [], c=BLUE, label="linear")
    ax[0].scatter([], [], c=TEAL, label="macrocycle")
    ax[0].legend(frameon=False, loc="lower right")
    return save_journal(fig, OUT / "FigureS10_energy_trajectories"), len(X)


if __name__ == "__main__":
    print("fig8", fig8())
    print("figS10", figS10())

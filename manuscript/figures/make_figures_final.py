"""Figuras novas do manuscrito (numeracao final), no padrao da revista (180 mm, 300 dpi, texto >= 8 pt; frontiers_style.py):
  Figure2_calibration     calibracao da escada de escores, agora com o PRODIGY
  Figure6_energy_ranking  PRODIGY nas 48 poses e classificacao por etapa
  Figure8_candidate_poses paineis estruturais (PyMOL) dos quatro candidatos da lista curta
Uso (de manuscript/): python figures/make_figures_final.py figures
Le: data-calibration-b05/*, data-e2-results/prodigy_*.json, figures/_src/*.png, outputs/ranking_energy_pre.json (gerado por
scripts/rank_energy_stages.py) ou, quando existir, outputs/ranking_energy_final_all.json (todas as etapas)."""
import csv
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr

from frontiers_style import apply_style, mm_figsize, save_journal

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
OUT = OUT if OUT.is_absolute() else Path.cwd() / OUT
OUT.mkdir(parents=True, exist_ok=True)
apply_style()
BLUE, ORANGE, GREEN, RED, GREY, TEAL = "#0072B2", "#E69F00", "#009E73", "#D55E00", "#7f7f7f", "#2a9d8f"
INH = ["SFTI1", "BBI", "BPTI", "EcTI", "SKTI"]
LAB = {"SFTI1": "SFTI-1", "BBI": "BBI", "BPTI": "BPTI", "EcTI": "EcTI", "SKTI": "SKTI"}
pairs = [(r, k) for r in ("bovine", "sfrug") for k in INH]
ylab = [f"{'Bt' if r == 'bovine' else 'Sf'} {LAB[k]}" for r, k in pairs]


def letter(ax, L, dx=-0.18, dy=1.04):
    ax.text(dx, dy, L, transform=ax.transAxes, fontweight="bold", va="bottom", ha="left")


def dumbbell(ax, real, decoy, xlabel, higher_better, show_y=True):
    y = np.arange(len(pairs))[::-1]
    for yi, a, c in zip(y, real, decoy):
        good = (a > c) if higher_better else (a < c)
        ax.plot([a, c], [yi, yi], color=GREY if good else RED, lw=1.5, zorder=1)
    ax.scatter(real, y, s=26, color=BLUE, zorder=3, label="real inhibitor")
    ax.scatter(decoy, y, s=26, facecolors="white", edgecolors=ORANGE, linewidths=1.6, zorder=3, label="shuffled decoy")
    n_ok = sum(((a > c) if higher_better else (a < c)) for a, c in zip(real, decoy))
    ax.set_yticks(y)
    ax.set_yticklabels(ylab if show_y else [])
    ax.set_xlabel(xlabel)
    ax.text(0.98, 0.02, f"{n_ok}/10", transform=ax.transAxes, ha="right", va="bottom", fontweight="bold")


def fig1():
    """Study design. Neutral boxes on purpose: the colours used to encode the execution status of
    each queue (done/running/pending), which is project bookkeeping and not a result. Fronts L and M
    keep the blue/teal of the other figures."""
    from matplotlib.patches import FancyBboxPatch
    fig, ax = plt.subplots(figsize=mm_figsize("double", 118))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 72)
    ax.axis("off")
    PLAIN, L_FILL, M_FILL = "#eef1f4", "#dbe9f5", "#d8ede9"
    EDGE = "#495057"

    def box(x, y, w, h, text, fc=PLAIN, ec=EDGE):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.8",
                                    fc=fc, ec=ec, lw=1.2))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8)

    def arr(x1, y1, x2, y2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=EDGE, lw=1.2, shrinkA=0, shrinkB=0))

    def elbow(pts):
        xs_, ys_ = zip(*pts[:-1])
        ax.plot(xs_, ys_, color=EDGE, lw=1.2, solid_joinstyle="miter")
        arr(*pts[-2], *pts[-1])

    w, h = 22, 13
    xs = [1, 26, 51, 76]
    box(xs[0], 57, w, h, "8 pest trypsins\nsubsites S4-S3'\n(2PTC, 1SFI)")
    box(xs[1], 57, w, h, "scoring ladder\ncalibrated\n6 inhibitors\n+ shuffled decoys")
    box(xs[2], 57, w, h, "RFdiffusion +\nProteinMPNN\n880 backbones\n22,066 sequences")
    box(xs[3] - 1, 57, w + 2, h, "hard criterion\nno P1 of midgut\ntrypsin, chymotrypsin\nor elastase")
    for i in range(3):
        arr(xs[i] + w, 63.5, xs[i + 1] - (1 if i == 2 else 0), 63.5)

    box(14, 40, 30, 11, "front L (linear)\n527 sequences", fc=L_FILL)
    box(56, 40, 30, 11, "front M (macrocycle)\n543 sequences", fc=M_FILL)
    elbow([(87, 57), (87, 54), (29, 54), (29, 51.4)])
    elbow([(87, 57), (87, 54), (71, 54), (71, 51.4)])

    box(10, 24, 80, 11, "Boltz-2 E1-E4: co-folding, re-scoring (5 x 3), paired controls, pose QC\n"
                        "48 candidates (24 linear, 24 macrocyclic; 3 per species and front)")
    arr(29, 40, 29, 35.4)
    arr(71, 40, 71, 35.4)

    box(1, 5, 29, 13, "10-ns MD, 48 complexes\npH 10.0 and pH 8.2\n+ 16 repeated runs")
    box(35.5, 5, 29, 13, "trajectory analysis\nS1 occupancy, RMSD,\nMM-GBSA, PRODIGY")
    box(70, 5, 29, 13, "ranking by stage\nshortlisted peptides")
    elbow([(50, 24), (50, 21), (15.5, 21), (15.5, 18.4)])
    arr(30, 11.5, 35.5, 11.5)
    arr(64.5, 11.5, 70, 11.5)
    ax.text(50, 0.8, "No enzymatic assay and no counter-selection against non-target proteases "
                     "was performed.", ha="center", fontsize=8, style="italic")
    return save_journal(fig, OUT / "Figure1_pipeline")


def fig2():
    boltz = json.load(open(ROOT / "data-calibration-b05/boltz_calibration_summary.json"))
    md = json.load(open(ROOT / "data-calibration-b05/md_metrics_pbc_corrected.json"))["systems"]
    gb = json.load(open(ROOT / "data-calibration-b05/mmpbsa_calib_results.json"))
    pr = json.load(open(ROOT / "data-e2-results/prodigy_calib.json"))
    fig, ax = plt.subplots(2, 3, figsize=mm_figsize("double", 130), layout="constrained")
    dumbbell(ax[0, 0], [boltz[f"{r}__{k}"]["confidence"] for r, k in pairs], [boltz[f"{r}__{k}_decoy"]["confidence"] for r, k in pairs], "Boltz-2 confidence", True)
    dumbbell(ax[0, 1], [md[f"{r}__{k}"]["ligand_rmsd_nm_last_third"] for r, k in pairs], [md[f"{r}__{k}_decoy"]["ligand_rmsd_nm_last_third"] for r, k in pairs], "ligand RMSD (nm)", False, False)
    dumbbell(ax[0, 2], [gb[f"{r}__{k}"]["delta_g_total_kcal"] for r, k in pairs], [gb[f"{r}__{k}_decoy"]["delta_g_total_kcal"] for r, k in pairs], "MM-GBSA ΔG (kcal/mol)", False, False)
    dumbbell(ax[1, 0], [pr[f"{r}__{k}"]["dG_kcal_mean"] for r, k in pairs], [pr[f"{r}__{k}_decoy"]["dG_kcal_mean"] for r, k in pairs], "PRODIGY ΔG (kcal/mol)", False)
    tags = [t for t in md if t in gb]
    x = np.array([md[t]["receptor_residues_in_contact_mean"] for t in tags])
    yv = np.array([gb[t]["delta_g_total_kcal"] for t in tags])
    isd = np.array(["decoy" in t for t in tags])
    isb = np.array([t.startswith("bovine") for t in tags])
    for dec, fc, ec in [(False, BLUE, BLUE), (True, "white", ORANGE)]:
        for b, mk in [(True, "o"), (False, "s")]:
            s = (isd == dec) & (isb == b)
            ax[1, 1].scatter(x[s], yv[s], s=26, marker=mk, facecolors=fc, edgecolors=ec, linewidths=1.4)
    ax[1, 1].set_xlabel("receptor residues within 4.5 Å")
    ax[1, 1].set_ylabel("MM-GBSA ΔG (kcal/mol)")
    ax[1, 1].text(0.04, 0.06, f"ρ = {spearmanr(x, yv).statistic:.2f}", transform=ax[1, 1].transAxes, fontweight="bold")
    t2 = [t for t in pr if t in md]
    xp = np.array([pr[t]["ic_total_mean"] for t in t2])
    yp = np.array([pr[t]["dG_kcal_mean"] for t in t2])
    isd2 = np.array(["decoy" in t for t in t2])
    isb2 = np.array([t.startswith("bovine") for t in t2])
    for dec, fc, ec in [(False, BLUE, BLUE), (True, "white", ORANGE)]:
        for b, mk in [(True, "o"), (False, "s")]:
            s = (isd2 == dec) & (isb2 == b)
            ax[1, 2].scatter(xp[s], yp[s], s=26, marker=mk, facecolors=fc, edgecolors=ec, linewidths=1.4)
    ax[1, 2].set_xlabel("PRODIGY contacts")
    ax[1, 2].set_ylabel("PRODIGY ΔG (kcal/mol)")
    ax[1, 2].text(0.96, 0.94, f"ρ = {spearmanr(xp, yp).statistic:.2f}", transform=ax[1, 2].transAxes, fontweight="bold", ha="right", va="top")
    for a, L in zip(ax.flat, "ABCDEF"):
        letter(a, L)
    h, l = ax[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="outside upper center", ncol=2, frameon=False)
    return save_journal(fig, OUT / "Figure2_calibration")


def fig5():
    items = [("NGGRPDAP", "L", "NGGRPDAP, linear, A. gemmatalis"), ("GQNDS", "L", "GQNDS, linear, O. nubilalis"),
             ("GGHSE", "M", "GGHSE, cyclic, S. frugiperda"), ("GGKPGEP", "M", "GGKPGEP, cyclic, A. gemmatalis")]
    from PIL import Image
    fig, ax = plt.subplots(2, 2, figsize=mm_figsize("double", 130), layout="constrained")
    for a, (lab, F, ttl), L in zip(ax.flat, items, "ABCD"):
        p = Path(__file__).resolve().parent / "_src" / f"{lab}_{F}.png"
        img = Image.open(p)
        w, h = img.size
        a.imshow(img.crop((int(w * .12), int(h * .08), int(w * .92), int(h * .95))))
        a.axis("off")
        a.set_title(ttl, loc="left", fontsize=9)
        a.text(-0.02, 1.0, L, transform=a.transAxes, fontweight="bold", va="bottom", ha="right")
    from matplotlib.lines import Line2D
    key = [Line2D([0], [0], color="#ff00ff", lw=4, label="anchor residue (closest to Asp189)"),
           Line2D([0], [0], color="#00ffff", lw=4, label="peptide"),
           Line2D([0], [0], color="#ff9933", lw=4, label="Asp189 (S1)"),
           Line2D([0], [0], color="#7a9a5a", lw=4, label="His57, Ser195"),
           Line2D([0], [0], color="#e6e600", lw=2, ls=":", label="anchor–Asp189 distance")]
    fig.legend(handles=key, loc="outside lower center", ncol=3, frameon=False)
    return save_journal(fig, OUT / "Figure8_candidate_poses")


def fig7():
    src = ROOT / "outputs/ranking_energy_final_all.json"
    allstages = src.exists()
    rows = json.load(open(src if allstages else ROOT / "outputs/ranking_energy_pre.json"))
    pp = json.load(open(ROOT / "data-e2-results/prodigy_poses.json"))
    rk = {(r["front"], r["key"]): r for r in csv.DictReader(open(ROOT / "manuscript/figures/ranking_final.csv", encoding="utf-8"))}
    fig = plt.figure(figsize=mm_figsize("double", 150), layout="constrained")
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.25])
    a = fig.add_subplot(gs[0, 0])
    for F, c in (("L", BLUE), ("M", TEAL)):
        ks = [k for k in pp if pp[k]["front"] == F]
        a.scatter([len(rk[(F, pp[k]["key"])]["sequence"]) for k in ks], [pp[k]["dG_kcal"] for k in ks], s=30, color=c, alpha=.8,
                  label="linear" if F == "L" else "macrocycle")
    short = {("L", "NGGRPDAP"): "NGGRPDAP", ("L", "GQNDS"): "GQNDS", ("M", "GGHSE"): "GGHSE", ("M", "GGKPGEP"): "GGKPGEP"}
    for k, v in pp.items():
        seq = rk[(v["front"], v["key"])]["sequence"]
        if (v["front"], seq) in short:
            a.annotate(seq, (len(seq), v["dG_kcal"]), xytext=(6, 5), textcoords="offset points")
    n = [len(rk[(v["front"], v["key"])]["sequence"]) for v in pp.values()]
    g = [v["dG_kcal"] for v in pp.values()]
    a.text(0.97, 0.96, f"ρ = {spearmanr(n, g).statistic:.2f}", transform=a.transAxes, ha="right", va="top", fontweight="bold")
    a.set_xlabel("peptide length (residues)")
    a.set_ylabel("PRODIGY ΔG, initial pose (kcal/mol)")
    a.legend(frameon=False, loc="lower left")
    letter(a, "A", -0.22, 1.02)
    b = fig.add_subplot(gs[0, 1])
    stages = ["E2", "E3", "MD", "PRODIGY_pose"] + (["PRODIGY_md", "MMGBSA"] if allstages else [])
    names = {"E2": "Boltz-2\nE2", "E3": "paired\nΔ (E3)", "MD": "MD\nRMSD", "PRODIGY_pose": "PRODIGY\npose", "PRODIGY_md": "PRODIGY\nMD", "MMGBSA": "MM-GBSA"}
    sel = []
    for F in "LM":
        sub = sorted([r for r in rows if r["front"] == F], key=lambda r: r["pos_" + F])[:10]
        sel += sub
    mat = np.array([[r.get(f"rank_{s}_{r['front']}") if r.get(f"rank_{s}_{r['front']}") is not None else np.nan for s in stages] +
                    [r[f"agg_{r['front']}"]] for r in sel])
    # The two fronts are ranked in pools of different size (L and M), so a raw rank of 10 means
    # "worst" in one block and "middling" in the other. Colour therefore encodes the rank relative
    # to the pool of its own front; the printed number stays the raw rank.
    npool = {F: sum(1 for r in rows if r["front"] == F and r.get(f"pos_{F}") is not None) for F in "LM"}
    rel = np.array([[(v - 1) / (npool[r["front"]] - 1) if not np.isnan(v) else np.nan for v in row]
                    for r, row in zip(sel, mat)])
    im = b.imshow(rel, cmap="viridis_r", aspect="auto", vmin=0, vmax=1)
    b.set_xticks(range(len(stages) + 1))
    b.set_xticklabels([names[s] for s in stages] + ["aggregate"], fontsize=8)
    b.xaxis.tick_top()
    b.set_yticks(range(len(sel)))
    b.set_yticklabels([f"{r['sequence']} ({'L' if r['front'] == 'L' else 'M'})" for r in sel], fontsize=8)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            if not np.isnan(mat[i, j]):
                b.text(j, i, f"{mat[i, j]:.0f}" if j < mat.shape[1] - 1 else f"{mat[i, j]:.1f}", ha="center", va="center",
                       color="white" if rel[i, j] > 0.45 else "black", fontsize=8)
    b.axhline(len(sel) / 2 - .5, color="white", lw=3)
    cb = fig.colorbar(im, ax=b, shrink=.7, pad=.02)
    cb.set_label(f"rank relative to its front\n(0 = best; L n = {npool['L']}, M n = {npool['M']})")
    for sp in b.spines.values():
        sp.set_visible(False)
    letter(b, "B", -0.30, 1.14)
    return save_journal(fig, OUT / "Figure6_energy_ranking"), allstages


if __name__ == "__main__":
    print("fig1", fig1())
    print("fig2", fig2())
    print("fig5", fig5())
    print("fig7", fig7())

"""Figuras do manuscrito, geradas SO a partir de arquivos de dados versionados.
Fig 2: calibracao (Boltz-2, RMSD do ligante, MM-GBSA, MM-GBSA x contato).
Fig 3: o que o filtro de clivagem circular seleciona.
Largura 180 mm (2 colunas), 300 dpi, paleta Okabe-Ito, fonte >= 6.5 pt."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
BLUE, ORANGE, GREEN, RED, GREY = "#0072B2", "#E69F00", "#009E73", "#D55E00", "#7f7f7f"
plt.rcParams.update({"font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8, "xtick.labelsize": 8,
                     "ytick.labelsize": 8, "legend.fontsize": 8, "axes.spines.top": False,
                     "axes.spines.right": False, "font.family": "DejaVu Sans", "pdf.fonttype": 42})
MM = 1 / 25.4

boltz = json.load(open(ROOT / "data-calibration-b05/boltz_calibration_summary.json"))
md = json.load(open(ROOT / "data-calibration-b05/md_metrics_pbc_corrected.json"))["systems"]
gb = json.load(open(ROOT / "data-calibration-b05/mmpbsa_calib_results.json"))
INH = ["SFTI1", "BBI", "BPTI", "EcTI", "SKTI"]
LAB = {"SFTI1": "SFTI-1", "BBI": "BBI", "BPTI": "BPTI", "EcTI": "EcTI", "SKTI": "SKTI"}
pairs = [(rec, k) for rec in ("bovine", "sfrug") for k in INH]
ylab = [f"{'Bt' if r == 'bovine' else 'Sf'} {LAB[k]}" for r, k in pairs]


def dumbbell(ax, real, decoy, xlabel, higher_better, title):
    y = np.arange(len(pairs))[::-1]
    for yi, a, c in zip(y, real, decoy):
        good = (a > c) if higher_better else (a < c)
        ax.plot([a, c], [yi, yi], color=GREY if good else RED, lw=1, zorder=1)
    ax.scatter(real, y, s=16, color=BLUE, zorder=3, label="real inhibitor")
    ax.scatter(decoy, y, s=16, facecolors="white", edgecolors=ORANGE, linewidths=1.2, zorder=3, label="shuffled decoy")
    n_ok = sum(((a > c) if higher_better else (a < c)) for a, c in zip(real, decoy))
    ax.set_yticks(y); ax.set_yticklabels(ylab); ax.set_xlabel(xlabel)
    ax.set_title(f"{title}  ({n_ok}/10 pairs real better)", loc="left", fontweight="bold", fontsize=6.8)


fig = plt.figure(figsize=(180 * MM, 118 * MM))
gs = fig.add_gridspec(2, 3, hspace=0.55, wspace=0.75, left=0.075, right=0.985, top=0.93, bottom=0.10)
axA, axB, axC, axD = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[0, 2]), fig.add_subplot(gs[1, 0:2])
axE = fig.add_subplot(gs[1, 2]); axE.axis("off")
dumbbell(axA, [boltz[f"{r}__{k}"]["confidence"] for r, k in pairs], [boltz[f"{r}__{k}_decoy"]["confidence"] for r, k in pairs],
         "Boltz-2 confidence", True, "A")
dumbbell(axB, [md[f"{r}__{k}"]["ligand_rmsd_nm_last_third"] for r, k in pairs], [md[f"{r}__{k}_decoy"]["ligand_rmsd_nm_last_third"] for r, k in pairs],
         "Ligand RMSD (nm)", False, "B")
axB.set_yticklabels([]); axB.set_xticks([0.25, 0.75, 1.25])
dumbbell(axC, [gb[f"{r}__{k}"]["delta_g_total_kcal"] for r, k in pairs], [gb[f"{r}__{k}_decoy"]["delta_g_total_kcal"] for r, k in pairs],
         "MM-GBSA ΔG (kcal/mol)", False, "C")
axC.set_yticklabels([])
axA.legend(loc="lower left", frameon=False, bbox_to_anchor=(0.0, 1.06), ncol=2, handletextpad=0.2, columnspacing=1.0)
# D: MM-GBSA x contato (22 sistemas)
tags = [t for t in md if t in gb]
x = np.array([md[t]["receptor_residues_in_contact_mean"] for t in tags]); yv = np.array([gb[t]["delta_g_total_kcal"] for t in tags])
isdecoy = np.array(["decoy" in t for t in tags]); isb = np.array([t.startswith("bovine") for t in tags])
for dec, fc, ec in [(False, BLUE, BLUE), (True, "white", ORANGE)]:
    for b, mk in [(True, "o"), (False, "s")]:
        sel = (isdecoy == dec) & (isb == b)
        axD.scatter(x[sel], yv[sel], s=20, marker=mk, facecolors=fc, edgecolors=ec, linewidths=1.1)
rho = spearmanr(x, yv)
axD.set_xlabel("Receptor residues within 4.5 Å of the ligand (mean)"); axD.set_ylabel("MM-GBSA ΔG (kcal/mol)")
axD.set_title("D", loc="left", fontweight="bold")
axD.text(0.02, 0.06, f"Spearman ρ = {rho.statistic:.2f}, n = {len(tags)} (post hoc)", transform=axD.transAxes, fontsize=6.5)
axE.text(0, 0.95, "Symbols (D)", fontweight="bold", va="top")
for i, (mk, fc, ec, t) in enumerate([("o", BLUE, BLUE, "real, bovine trypsin"), ("s", BLUE, BLUE, "real, S. frugiperda"),
                                     ("o", "white", ORANGE, "decoy, bovine trypsin"), ("s", "white", ORANGE, "decoy, S. frugiperda")]):
    axE.scatter([0.03], [0.78 - 0.14 * i], s=20, marker=mk, facecolors=fc, edgecolors=ec, linewidths=1.1, transform=axE.transAxes)
    axE.text(0.10, 0.78 - 0.14 * i, t, va="center", transform=axE.transAxes)
fig.savefig(OUT / "Figure3_calibration.png", dpi=300); fig.savefig(OUT / "Figure3_calibration.pdf")
plt.close(fig)

# ---------------- Figura 3
fc = json.load(open(ROOT / "data-b23-scoring/results/filter_composition.json"))
cls = ["RESISTENTE", "MARGINAL", "SUSCEPTIVEL"]; col = {"RESISTENTE": GREEN, "MARGINAL": ORANGE, "SUSCEPTIVEL": RED}
name = {"RESISTENTE": "Resistant-like", "MARGINAL": "Marginal", "SUSCEPTIVEL": "Susceptible"}
lens = [5, 6, 7, 8, 10, 12, 14, 16, 18, 19, 20]
fig, axs = plt.subplots(1, 3, figsize=(180 * MM, 58 * MM), gridspec_kw={"wspace": 0.42, "left": 0.06, "right": 0.99, "bottom": 0.2, "top": 0.86})
ax = axs[0]; w = 0.27
for i, c in enumerate(cls):
    h = fc[c]["length_hist"]; tot = fc[c]["n"]
    ax.bar(np.arange(len(lens)) + (i - 1) * w, [100 * h.get(str(L), 0) / tot for L in lens], w, color=col[c], label=f"{name[c]} (n = {tot:,})")
ax.set_xticks(range(len(lens))); ax.set_xticklabels(lens); ax.set_xlabel("Peptide length (residues)"); ax.set_ylabel("Sequences in class (%)")
ax.set_title("A", loc="left", fontweight="bold"); ax.set_ylim(0, 33); ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.02), fontsize=8)
ax = axs[1]
vals = [[100 * fc[c]["any_KR_frac"] for c in cls], [100 * fc[c]["geometric_P1_is_KR_frac"] for c in cls]]
xx = np.arange(3)
ax.bar(xx - 0.19, vals[0], 0.36, color=BLUE, label="contains K or R"); ax.bar(xx + 0.19, vals[1], 0.36, color=GREY, label="geometric P1 proxy is K/R")
for xi, v in zip(xx - 0.19, vals[0]): ax.text(xi, v + 1.5, f"{v:.1f}", ha="center", fontsize=8)
for xi, v in zip(xx + 0.19, vals[1]): ax.text(xi, v + 1.5, f"{v:.1f}", ha="center", fontsize=8)
ax.set_xticks(xx); ax.set_xticklabels([name[c] for c in cls]); ax.set_ylabel("Sequences in class (%)"); ax.set_ylim(0, 118)
ax.set_title("B", loc="left", fontweight="bold"); ax.legend(frameon=False, loc="upper left", fontsize=8)
ax = axs[2]
aa = "GTPSDANLEVIKRFYHMQWC"; aa = "".join(sorted("ACDEFGHIKLMNPQRSTVW Y".replace(" ", ""), key=lambda a: -fc["RESISTENTE"]["aa_composition_pct"][a]))
xx = np.arange(len(aa))
ax.bar(xx - 0.2, [fc["RESISTENTE"]["aa_composition_pct"][a] for a in aa], 0.4, color=GREEN, label="Resistant-like")
ax.bar(xx + 0.2, [fc["SUSCEPTIVEL"]["aa_composition_pct"][a] for a in aa], 0.4, color=RED, label="Susceptible")
ax.set_xticks(xx); ax.set_xticklabels(list(aa)); ax.set_xlabel("Amino acid"); ax.set_ylabel("Composition (%)")
ax.set_title("C", loc="left", fontweight="bold"); ax.legend(frameon=False, loc="upper right")
fig.savefig(OUT / "Figure4_motif_screen.png", dpi=300); fig.savefig(OUT / "Figure4_motif_screen.pdf")
print("figuras 2 e 3 geradas")

# ---------------- Figura 1: fluxograma (contagens vindas dos arquivos de auditoria)
from matplotlib.patches import FancyBboxPatch
audit = json.load(open(ROOT / "data-b23-scoring/results/campaign_audit.json"))
n_bb = sum(v["backbones"] for v in audit.values()); n_seq = sum(v["sequences_unique"] for v in audit.values())
n_res = fc["RESISTENTE"]["n"]
fig, ax = plt.subplots(figsize=(180 * MM, 96 * MM)); ax.axis("off"); ax.set_xlim(0, 100); ax.set_ylim(0, 54)
def box(x, y, w, h, text, color, fs=5.7):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.25,rounding_size=1.2", fc=color, ec="#333333", lw=0.7))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, linespacing=1.25)
def arrow(x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", lw=0.8, color="#333333"))
LB, LO, LG = "#DCEBF7", "#FBE7C2", "#D5EFE4"
ax.text(1, 52.5, "Targets and calibration", fontsize=7.2, fontweight="bold")
box(1, 40, 30, 10, "Receptor panel\n8 pest targets + M. sexta + B. mori\n(AlphaFold models; Asp189-eq. checked)", LB)
box(1, 26, 30, 10, "Subsite mapping\n2PTC / 1SFI → 10 receptors\nFoldseek TM-align: 20/20 pairs accepted", LB)
box(1, 9, 30, 13, "Scoring calibration\n6 natural inhibitors + 5 shuffled decoys\n× 2 receptors (22 systems)\nBoltz-2 · ligand RMSD · MM-GBSA", LO)
arrow(16, 40, 16, 36.4); arrow(16, 26, 16, 22.4)
ax.text(38, 52.5, "Generation and triage", fontsize=7.2, fontweight="bold")
box(38, 40, 27, 10, f"RFdiffusion, cyclic\n11 lengths (5–20 aa) × 10 × 8 targets\n{n_bb} backbones", LG)
box(38, 26, 27, 10, f"ProteinMPNN\n{n_seq:,} unique sequences", LG)
box(38, 12, 27, 11, f"Cleavage-motif screen\n(circular, 7 rules)\n{n_res:,} resistant-like (8.3%)", LG)
arrow(51.5, 40, 51.5, 36.4); arrow(51.5, 26, 51.5, 23.4)
box(72, 40, 27, 10, "Boltz-2 co-folding\n(cyclic peptide + receptor MSA)\nconfidence = 0.8 pLDDT + 0.2 ipTM", LG)
box(72, 26, 27, 10, "Top-1 per target\n(highest confidence among\nresistant-like)", LG)
box(72, 9, 27, 14, "MD 50 ns, 1 replicate\n(linear topology, pH 10)\nS1 occupancy · catalytic contacts\n· peptide RMSD", LG)
arrow(65, 17.5, 72, 45); arrow(85.5, 40, 85.5, 36.4); arrow(85.5, 26, 85.5, 23.4)
ax.text(1, 3.2, "Not evaluated here: selectivity against non-target proteases; enzymatic activity; macrocycle closure in the MD topology.", fontsize=6.3, color="#555555")
fig.savefig(OUT / "Figure1_pipeline.png", dpi=300, bbox_inches="tight"); fig.savefig(OUT / "Figure1_pipeline.pdf", bbox_inches="tight")
print("figura 1 gerada")

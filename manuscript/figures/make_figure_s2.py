"""Figura S2 (gerador antigo: Figure4_motif_screen): propriedades das 22.066 sequencias por classe do filtro por escore de motivo.
Redesenhada em 08/10/2026 nas medidas da revista (frontiers_style.py: 180 mm, 8 pt no tamanho final, 300 dpi):
  A  distribuicao de comprimento por classe (linhas com marcadores: as classes se comparam melhor que em barras agrupadas de 11 categorias)
  B  % de sequencias com K/R e com K/R no P1 geometrico, por classe
  C  composicao de aminoacidos (grafico de pontos ordenado pela classe resistente-like)
Uso (de manuscript/): python figures/make_figure_s2.py
Le data-b23-scoring/results/filter_composition.json; grava figures/Figure4_motif_screen.{png,pdf,tif}."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from frontiers_style import apply_style, mm_figsize, save_journal

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
apply_style()
GREEN, ORANGE, RED, BLUE, GREY = "#009E73", "#E69F00", "#D55E00", "#0072B2", "#7f7f7f"
fc = json.load(open(ROOT / "data-b23-scoring/results/filter_composition.json"))
cls = ["RESISTENTE", "MARGINAL", "SUSCEPTIVEL"]
col = {"RESISTENTE": GREEN, "MARGINAL": ORANGE, "SUSCEPTIVEL": RED}
name = {"RESISTENTE": "Resistant-like", "MARGINAL": "Marginal", "SUSCEPTIVEL": "Susceptible"}
lens = [5, 6, 7, 8, 10, 12, 14, 16, 18, 19, 20]

fig, ax = plt.subplots(1, 3, figsize=mm_figsize("double", 70), layout="constrained",
                       gridspec_kw={"width_ratios": [1.1, 1.3, 1.25]})
a = ax[0]
for c in cls:
    h, n = fc[c]["length_hist"], fc[c]["n"]
    a.plot(range(len(lens)), [100 * h.get(str(L), 0) / n for L in lens], marker="o", ms=4, lw=1.4, color=col[c],
           label=f"{name[c]} (n = {n:,})")
a.set_xticks(range(len(lens)))
a.set_xticklabels(lens, rotation=90)
a.set_xlabel("peptide length (residues)")
a.set_ylabel("sequences in class (%)")
a.set_ylim(0, 40)
a.legend(frameon=False, loc="upper right", handlelength=1.2, borderaxespad=0)

b = ax[1]
xx = np.arange(3)
v1 = [100 * fc[c]["any_KR_frac"] for c in cls]
v2 = [100 * fc[c]["geometric_P1_is_KR_frac"] for c in cls]
b.bar(xx - 0.2, v1, 0.4, color=BLUE, label="contains K or R")
b.bar(xx + 0.2, v2, 0.4, color=GREY, label="geometric P1 is K/R")
for x_, v in list(zip(xx - 0.2, v1)) + list(zip(xx + 0.2, v2)):
    b.text(x_, v + 1.5, f"{v:.1f}", ha="center", fontsize=8)
b.set_xticks(xx)
b.set_xticklabels(["Resistant-\nlike", "Marginal", "Suscep-\ntible"])
b.set_ylabel("sequences in class (%)")
b.set_ylim(0, 125)
b.legend(frameon=False, loc="upper left", handlelength=1.2, borderaxespad=0)

c_ = ax[2]
aa = sorted("ACDEFGHIKLMNPQRSTVWY", key=lambda x: -fc["RESISTENTE"]["aa_composition_pct"][x])
for c in ("RESISTENTE", "SUSCEPTIVEL"):
    c_.plot(range(len(aa)), [fc[c]["aa_composition_pct"][x] for x in aa], marker="o", ms=4, lw=0, color=col[c], label=name[c])
c_.set_xticks(range(len(aa)))
c_.set_xticklabels(aa)
c_.tick_params(axis="x", pad=1)
c_.set_xlabel("amino acid")
c_.set_ylabel("composition (%)")
c_.legend(frameon=False, loc="upper right", handlelength=1.2, borderaxespad=0)

for x_, L_ in zip(ax, "ABC"):
    x_.text(-0.02, 1.03, L_, transform=x_.transAxes, fontweight="bold", va="bottom", ha="right")
print(save_journal(fig, OUT / "Figure4_motif_screen"))

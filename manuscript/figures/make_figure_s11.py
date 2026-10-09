"""Figura S11 -- geometria de ataque da Ser195 sobre a ligacao cindivel: sitio protegido por Pro x sitio exposto.

Pergunta que responde: os peptideos recomendados tem Lys/Arg interno; a tripsina os cliva?
Controle interno ja simulado no mesmo protocolo: PGRGDANP e' o embaralhado de NGGRPDAP (mesma composicao,
mesmo receptor de A. gemmatalis, 10 ns, CHARMM36, pH 10,0) e poe o Arg na S1 na MESMA profundidade
(2,73 A contra 2,78 A; ocupancia 1,00 nos dois), mas sem a prolina: Arg3-Gly4 em vez de Arg4-Pro5.

(A) distribuicao da distancia Ser195 OG -- C da carbonila da ligacao cindivel, por execucao
(B) fracao de quadros em conformacao quase de ataque (NAC)

Uso (de manuscript/): python figures/make_figure_s11.py [DIR_SAIDA]
Le data-e2-results/scissile_geometry_controls.json (gerado por scripts/scissile_geometry.py no servidor).
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from frontiers_style import apply_style, mm_figsize, save_journal

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
OUT = OUT if OUT.is_absolute() else Path.cwd() / OUT
OUT.mkdir(parents=True, exist_ok=True)
apply_style()
EXPOSTO, PROT_L, PROT_M = "#D55E00", "#0072B2", "#2a9d8f"
NAC_D = 3.5

d = json.load(open(ROOT / "data-e2-results/scissile_geometry_controls.json", encoding="utf-8"))
SHORT = {"pH 10.0 run1": "pH 10,0 (1)", "pH 10.0 run2": "pH 10,0 (2)",
         "pH 8.2 run1": "pH 8,2 (1)", "pH 8.2 run2": "pH 8,2 (2)",
         "pH 10.0 shuffled control": "pH 10,0"}
EN = {"pH 10.0 run1": "pH 10.0 (1)", "pH 10.0 run2": "pH 10.0 (2)",
      "pH 8.2 run1": "pH 8.2 (1)", "pH 8.2 run2": "pH 8.2 (2)",
      "pH 10.0 shuffled control": "pH 10.0"}

rows = []
for pep, runs in d.items():
    for r in runs:
        for bond, series in r.get("d_OG_C_h2_by_frame", {}).items():
            nac = next(b["NAC_frac"] for b in r["bonds"] if b["bond"] == bond)
            protegido = bond.split("-")[1][0] == "P"
            rows.append({"pep": pep, "bond": bond, "run": EN[r["run"]], "d": np.array(series),
                         "nac": nac, "prot": protegido,
                         "cyc": pep in ("GGKPGEP", "GGEKPPG")})
# exposto primeiro, depois protegidos lineares, depois ciclicos
rows.sort(key=lambda x: (x["prot"], x["cyc"], x["pep"], x["run"]))
cor = [EXPOSTO if not r["prot"] else (PROT_M if r["cyc"] else PROT_L) for r in rows]
lab = [f"{r['pep']}\n{r['bond']}  {r['run']}" for r in rows]

fig, ax = plt.subplots(1, 2, figsize=mm_figsize("double", 92), layout="constrained",
                       gridspec_kw={"width_ratios": [1.75, 1]})

a = ax[0]
pos = np.arange(len(rows))
vp = a.violinplot([r["d"] for r in rows], positions=pos, vert=False, widths=.82,
                  showextrema=False, showmedians=True)
for body, c in zip(vp["bodies"], cor):
    body.set_facecolor(c); body.set_alpha(.75); body.set_edgecolor("none")
vp["cmedians"].set_color("black"); vp["cmedians"].set_linewidth(1.2)
for i, r in enumerate(rows):
    a.plot(r["d"].min(), i, marker="|", color="black", ms=7, mew=1.2)
a.axvline(NAC_D, ls="--", color="0.35", lw=1)
a.text(NAC_D - 0.08, len(rows) - 0.4, "3.5 Å\n(attack)", ha="right", va="top", fontsize=8, color="0.35")
a.set_yticks(pos)
a.set_yticklabels(lab, fontsize=8)
a.set_xlabel("Ser195 Oγ — carbonyl C distance of the scissile bond (Å)")
a.set_xlim(2.4, None)
a.text(-0.01, 1.02, "A", transform=a.transAxes, fontweight="bold", va="bottom", ha="right")

b = ax[1]
b.barh(pos, [100 * r["nac"] for r in rows], color=cor, height=.72)
for i, r in enumerate(rows):
    v = 100 * r["nac"]
    b.text(v + 0.18, i, f"{v:.1f}%" if v else "0", va="center", fontsize=8)
b.set_yticks(pos); b.set_yticklabels([])
b.set_xlabel("frames in near-attack\nconformation (%)")
b.set_xlim(0, 11)
b.text(-0.01, 1.02, "B", transform=b.transAxes, fontweight="bold", va="bottom", ha="right")

from matplotlib.patches import Patch
fig.legend(handles=[Patch(fc=EXPOSTO, label="exposed K/R–Gly (shuffled control)"),
                    Patch(fc=PROT_L, label="protected R–Pro (linear)"),
                    Patch(fc=PROT_M, label="protected K–Pro (macrocycle)")],
           loc="outside lower center", ncol=3, frameon=False, fontsize=8, handlelength=1.3, columnspacing=1.4)
print(save_journal(fig, OUT / "FigureS11_scissile_protection"))

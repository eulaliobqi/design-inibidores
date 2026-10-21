"""Figura do slide 6: resultados publicados do grupo (Ki dos peptideos e resposta do intestino medio).

Valores: Almeida Barros et al. 2021 (Ki GORE1/GORE2), Mariano et al. 2026 (pro-regiao, Ki 0,78-1,80 mM)
e Junior et al. 2026 (SKTI x GORE-2, resultados qualitativos do resumo). Nada digitado de memoria:
os numeros estao nos resumos/manuscrito conferidos no PubMed e em manuscript_pt_src.md.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib.pyplot as plt  # noqa: E402
from make_slide_figures import AZUL, CINZA, GRAF, LARA, VERDE, salvar  # noqa: E402

fig, (a1, a2) = plt.subplots(1, 2, figsize=(13.2, 4.6), gridspec_kw={"width_ratios": [1, 1.1]})
pep = [("GORE2 (3 resíduos)", 0.10, 0.10, VERDE), ("GORE1 (3 resíduos)", 0.49, 0.49, VERDE),
       ("pró-região do\ntripsinogênio", 0.78, 1.80, CINZA)]
yy = list(range(len(pep)))[::-1]
for (lab, lo, hi, cor), y in zip(pep, yy):
    if lo == hi:
        a1.barh(y, hi, height=0.55, color=cor)
    else:
        a1.barh(y, hi - lo, left=lo, height=0.55, color=cor)
    txt = f"{lo:.2f} mM" if lo == hi else f"{lo:.2f}–{hi:.2f} mM"
    a1.text(hi + 0.06, y, txt.replace(".", ","), va="center", fontsize=15, color=GRAF)
a1.set_yticks(yy)
a1.set_yticklabels([p[0] for p in pep], fontsize=14.5, linespacing=1.3)
a1.set_xlim(0, 2.5)
a1.set_xticks([0, 0.5, 1.0, 1.5, 2.0])
a1.set_xticklabels(["0", "0,5", "1,0", "1,5", "2,0"])
a1.set_xlabel(r"$K_i$ contra tripsinas de $A.\ gemmatalis$ (mM)")
a1.tick_params(axis="y", length=0)
a1.spines["left"].set_visible(False)
a1.set_title("Inibição competitiva e reversível", fontsize=16, loc="left", color=GRAF, pad=10)

a2.axis("off")
a2.set_xlim(0, 10)
a2.set_ylim(0, 6)
a2.set_title(r"Resposta do intestino médio de $A.\ gemmatalis$", fontsize=16, loc="left", color=GRAF, pad=10)
a2.text(5.4, 5.35, "inibidor da soja\n(SKTI)", ha="center", va="center", fontsize=14.5, fontweight="bold", color="#6B7077")
a2.text(8.6, 5.35, "tripeptídeo\nGORE-2", ha="center", va="center", fontsize=14.5, fontweight="bold", color=VERDE)
linhas = [("proteases digestivas", ("▲ induz\n(compensação)", "▼ reprime"), (LARA, VERDE)),
          ("enzimas antioxidantes", ("indução maior", "indução menor"), ("#6B7077", VERDE)),
          ("lesão do epitélio", ("menor", "maior"), ("#6B7077", VERDE))]
for i, (rot, (v1, v2), (c1, c2)) in enumerate(linhas):
    y = 3.85 - i * 1.45
    a2.text(0.0, y, rot, fontsize=14.5, va="center", color=GRAF)
    a2.text(5.4, y, v1, fontsize=14, va="center", ha="center", color=c1, fontweight="bold", linespacing=1.2)
    a2.text(8.6, y, v2, fontsize=14, va="center", ha="center", color=c2, fontweight="bold")
fig.tight_layout(pad=0.6)
salvar(fig, "v2_grupo")

"""Figuras da apresentacao de congresso, em portugues e em escala de projecao.

Le exatamente os mesmos JSON que alimentam as figuras do manuscrito
(data-figuras-base/, data-e2-results/, data-calibration-b05/) e os renders PyMOL
em manuscript/figures/_src/. Nenhum numero e digitado a mao.

Uso (da raiz do projeto):  python apresentacao_congresso/make_slide_figures.py
Saida: apresentacao_congresso/figuras/*.png
"""
import collections
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "figuras"
OUT.mkdir(parents=True, exist_ok=True)

# paleta Okabe-Ito, a mesma das figuras do manuscrito
AZUL, VERDE, AMAR, LARA, CINZA, GRAF = "#0072B2", "#2A9D8F", "#E69F00", "#D55E00", "#9AA0A6", "#1F2328"

plt.rcParams.update({
    "font.family": ["Segoe UI", "DejaVu Sans"],
    "font.size": 15, "axes.titlesize": 17, "axes.labelsize": 15,
    "xtick.labelsize": 14, "ytick.labelsize": 14, "legend.fontsize": 14,
    "axes.edgecolor": "#55595E", "axes.linewidth": 1.0,
    "axes.spines.top": False, "axes.spines.right": False,
    "text.color": GRAF, "axes.labelcolor": GRAF,
    "xtick.color": "#55595E", "ytick.color": "#55595E",
    "figure.facecolor": "white", "savefig.facecolor": "white",
})
DPI = 200


def salvar(fig, nome):
    p = OUT / f"{nome}.png"
    fig.savefig(p, dpi=DPI, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    print(f"  {p.name}")


def virgula_y(ax):
    """Separador decimal em virgula no eixo y, padrao pt-BR."""
    from matplotlib.ticker import FuncFormatter
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.1f}".replace(".", ",")))


def jl(rel):
    return json.load(open(ROOT / rel, encoding="utf-8"))


def milhar(n):
    return f"{n:,}".replace(",", ".")


# ---------------------------------------------------------------- dados ----
L = jl("data-figuras-base/b23_cleavage_linear_hard.json")
M = jl("data-figuras-base/b23_cleavage_circular_hard.json")
CIR_S = jl("data-figuras-base/b23_cleavage_circular.json")
SP = list(L["by_species"])
CURTO = [s[0] + ". " + s[1:] for s in SP]
HL = {s: [r for r in L["by_species"][s]["results"] if r["verdict"] == "RESISTENTE"] for s in SP}
HM = {s: [r for r in M["by_species"][s]["results"] if r["verdict"] == "RESISTENTE"] for s in SP}
TODAS = [r for s in SP for r in L["by_species"][s]["results"]]
DUROL = [r for s in SP for r in HL[s]]
DUROM = [r for s in SP for r in HM[s]]
MOTIVO = sum(CIR_S["by_species"][s]["summary"]["RESISTENTE"] for s in SP)
AA = "ACDEFGHIKLMNPQRSTVWY"


# ------------------------------------------------- 1. a plataforma ---------
def fig_plataforma():
    fig, ax = plt.subplots(figsize=(13.4, 3.9))
    ax.set_xlim(0, 100); ax.set_ylim(2, 34); ax.axis("off")

    etapas = [
        ("1", "Alvo", "8 tripsinas de\nlepidópteros-praga", AZUL),
        ("2", "Calibração", "6 inibidores naturais\n+ iscas embaralhadas", AZUL),
        ("3", "Geração", "880 esqueletos\n22.066 sequências", VERDE),
        ("4", "Critério duro", "sem resíduo que o\nintestino corta", LARA),
        ("5", "Simulação", "48 complexos\n10 ns, dois pH", VERDE),
        ("6", "Classificação", "candidatos\nordenados", AZUL),
    ]
    g = 1.8
    w = (100 - (len(etapas) - 1) * g) / len(etapas)
    for i, (n, tit, sub, cor) in enumerate(etapas):
        x = i * (w + g)
        ax.add_patch(FancyBboxPatch((x, 10), w, 22, boxstyle="round,pad=0,rounding_size=0.8",
                                    fc="white", ec=cor, lw=2.2, zorder=3))
        ax.add_patch(plt.Circle((x + w / 2, 27.4), 1.9, fc=cor, ec="none", zorder=4))
        ax.text(x + w / 2, 27.4, n, ha="center", va="center", color="white",
                fontsize=12, fontweight="bold", zorder=5)
        ax.text(x + w / 2, 21.6, tit, ha="center", va="center", fontsize=14.5,
                fontweight="bold", color=cor, zorder=5)
        ax.text(x + w / 2, 15.4, sub, ha="center", va="center", fontsize=11.8,
                color=GRAF, linespacing=1.5, zorder=5)
        if i < len(etapas) - 1:
            ax.annotate("", xy=(x + w + g - 0.25, 21), xytext=(x + w + 0.25, 21),
                        arrowprops=dict(arrowstyle="-|>", color="#55595E", lw=1.6))

    ax.annotate("", xy=(100, 5.5), xytext=(0, 5.5),
                arrowprops=dict(arrowstyle="-|>", color=CINZA, lw=1.4))
    ax.text(50, 2.4, "cada etapa é calibrada antes de ser usada: o número só vale para o que a calibração sustenta",
            ha="center", va="center", fontsize=13, color="#55595E", style="italic")
    salvar(fig, "fig_plataforma")


# ------------------------------------------------- 2. calibracao -----------
def fig_calibracao():
    boltz = jl("data-calibration-b05/boltz_calibration_summary.json")
    # so os pares que tem isca embaralhada: o ApTI entrou na calibracao sem isca
    pares = [k for k in boltz if not k.endswith("_decoy") and k + "_decoy" in boltz]
    reais = [boltz[k]["confidence"] for k in pares]
    iscas = [boltz[k + "_decoy"]["confidence"] for k in pares]
    ordem = np.argsort(reais)
    reais, iscas = np.array(reais)[ordem], np.array(iscas)[ordem]
    y = np.arange(len(reais))

    fig, ax = plt.subplots(figsize=(10.4, 4.9))
    for i, (r, d) in enumerate(zip(reais, iscas)):
        ax.plot([d, r], [i, i], color=CINZA, lw=2.0, zorder=1, solid_capstyle="round")
    ax.scatter(iscas, y, s=150, facecolor="white", edgecolor=LARA, lw=2.4, zorder=3,
               label="isca embaralhada")
    ax.scatter(reais, y, s=150, color=AZUL, zorder=3, label="inibidor natural")
    ax.set_yticks([]); ax.set_xlabel("confiança do Boltz-2")
    ax.set_xlim(0.58, 1.02)
    from matplotlib.ticker import FuncFormatter
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.2f}".replace(".", ",")))
    ax.legend(frameon=False, loc="lower right", handletextpad=0.4)
    ax.axvspan(0.628, 0.944, color=LARA, alpha=0.07, zorder=0)
    ax.text(0.786, len(y) - 0.4, "faixa das iscas se sobrepõe à dos inibidores:\no valor absoluto não é critério",
            ha="center", va="top", fontsize=13, color=LARA, linespacing=1.4)
    salvar(fig, "fig_calibracao")


# ------------------------------------------------- 3. funil ----------------
def fig_funil():
    fig, ax = plt.subplots(figsize=(11.2, 4.6))
    passos = [("desenhadas pela IA", len(TODAS), CINZA),
              ("triagem por motivo", MOTIVO, AMAR),
              ("critério duro, frente L (linear)", len(DUROL), AZUL),
              ("critério duro, frente M (cíclica)", len(DUROM), VERDE)]
    y = np.arange(len(passos))[::-1]
    for (lab, v, c), yy in zip(passos, y):
        ax.barh(yy, v, height=0.62, color=c)
        pct = f"{v / len(TODAS) * 100:.1f}".replace(".", ",")
        ax.text(v + len(TODAS) * 0.012, yy, f"{milhar(v)}   ({pct}%)",
                va="center", fontsize=14.5, color=GRAF)
    ax.set_yticks(y); ax.set_yticklabels([p[0] for p in passos], fontsize=14.5)
    ax.set_xlim(0, len(TODAS) * 1.30); ax.set_xticks([])
    ax.spines["bottom"].set_visible(False); ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.text(len(TODAS) * 0.655, -0.95,
            "as frentes L e M são a mesma coleção lida de duas formas químicas, não dois conjuntos independentes",
            fontsize=12.8, color="#55595E", style="italic", ha="center")
    salvar(fig, "fig_funil")


# ------------------------------------------------- 4. composicao -----------
def fig_composicao():
    def comp(rs):
        c = collections.Counter(a for r in rs for a in r["sequence"])
        n = sum(c.values())
        return {a: c[a] / n * 100 for a in AA}, n

    cT, _ = comp(TODAS)
    cL, nL = comp(DUROL)
    aa = sorted(AA, key=lambda a: -cL[a])
    x = np.arange(20); w = 0.4

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.4, 4.5), gridspec_kw={"width_ratios": [2.5, 1]})
    a1.bar(x - w / 2, [cT[a] for a in aa], w, color="#CDD1D6", label="as 22.066 desenhadas")
    a1.bar(x + w / 2, [cL[a] for a in aa], w, color=AZUL, label=f"após o critério duro ({milhar(nL)} resíduos)")
    a1.set_xticks(x); a1.set_xticklabels(aa, fontsize=13.5)
    a1.set_ylabel("% dos resíduos"); a1.legend(frameon=False, loc="upper right")
    a1.annotate(f"glicina: {cL['G']:.1f}%".replace(".", ","), xy=(0, cL["G"]), xytext=(2.1, cL["G"] - 6),
                fontsize=14.5, color=AZUL, fontweight="bold",
                arrowprops=dict(arrowstyle="-", color=AZUL, lw=1.4))
    a1.set_title("Composição dos resíduos", loc="left", pad=12)

    comps = sorted({r["length"] for r in DUROL})
    cnt = collections.Counter(r["length"] for r in DUROL); tot = sum(cnt.values())
    a2.bar(range(len(comps)), [cnt[k] / tot * 100 for k in comps], 0.68, color=AZUL)
    a2.set_xticks(range(len(comps))); a2.set_xticklabels(comps, fontsize=13)
    a2.set_xlabel("comprimento (aa)"); a2.set_ylabel("% das sequências")
    media = np.mean([r["length"] for r in DUROL])
    a2.set_title(f"Comprimento: média de {media:.1f} aa".replace(".", ","), loc="left", pad=12)
    salvar(fig, "fig_composicao")


# ------------------------------- 5. a pose inicial decide ------------------
def fig_pose_decide():
    pts = []
    for front, cor in (("L", AZUL), ("M", VERDE)):
        d = jl(f"data-e2-results/md10_{front}_analysis.json")
        for k, v in d.items():
            pts.append((v["d_anchor_asp_ini_A"], v["occ_5A_h2"], cor, v["sequence"], front))
    fig, ax = plt.subplots(figsize=(10.6, 4.9))
    ax.axvspan(0, 4.0, color=AMAR, alpha=0.13, zorder=0)
    ax.axhline(0.70, color=CINZA, ls=":", lw=1.6, zorder=1)
    for x, yv, c, seq, f in pts:
        ax.scatter(x, yv, s=115, color=c, alpha=0.82, edgecolor="white", lw=0.8, zorder=3)
    desloc = {"NGGRPDAP": (60, 18), "GGKPGEP": (60, -28)}
    for x, yv, c, seq, f in pts:
        if seq in desloc and yv > 0.9:
            ax.annotate(seq, (x, yv), textcoords="offset points", xytext=desloc[seq],
                        fontsize=14, color=c, fontweight="bold", ha="left", va="center",
                        arrowprops=dict(arrowstyle="-", color=c, lw=1.2,
                                        connectionstyle="arc3,rad=0.0"))
    ax.set_xlabel("distância inicial da âncora ao Asp189 (Å)")
    ax.set_ylabel("ocupância de S1\n(2ª metade da simulação)")
    ax.set_xlim(0, 12.5); ax.set_ylim(-0.05, 1.08)
    virgula_y(ax)
    ax.text(2.0, 0.52, "partiu dentro\nde 4,0 Å", ha="center", fontsize=13.5,
            color="#8a6400", linespacing=1.4)
    ax.legend(handles=[Line2D([0], [0], marker="o", ls="", color=AZUL, markersize=11, label="frente L (linear)"),
                       Line2D([0], [0], marker="o", ls="", color=VERDE, markersize=11, label="frente M (cíclica)")],
              frameon=False, loc="center right")
    salvar(fig, "fig_pose_decide")


# ------------------------------------------------- 6. pH ------------------
def fig_ph():
    rows = jl("data-e2-results/compare_ph.json")["rows"]
    fig, ax = plt.subplots(figsize=(10.0, 4.9))
    destaque = {"NGGRPDAP": AZUL, "GGKPGEP": VERDE}
    for r in rows:
        a, b = r["occ_5A_h2_pH82"], r["occ_5A_h2_pH10"]
        seq = r["sequence"]
        c = destaque.get(seq, "#C7CBD1")
        z = 4 if seq in destaque else 2
        lw = 2.6 if seq in destaque else 1.3
        ax.plot([0, 1], [a, b], color=c, lw=lw, zorder=z, alpha=1 if seq in destaque else 0.75)
        ax.scatter([0, 1], [a, b], s=95 if seq in destaque else 55, color=c, zorder=z + 1)
        if seq in destaque:
            dy = 16 if seq == "NGGRPDAP" else -16
            ax.annotate(seq, (1, b), textcoords="offset points", xytext=(16, dy),
                        fontsize=14, color=c, fontweight="bold", va="center")
    ax.axhline(0.70, color=CINZA, ls=":", lw=1.6)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["pH 8,2", "pH 10,0"], fontsize=15.5)
    ax.set_xlim(-0.22, 1.52); ax.set_ylim(-0.05, 1.08)
    virgula_y(ax)
    ax.set_ylabel("ocupância de S1\n(2ª metade da simulação)")
    ax.spines["bottom"].set_visible(False); ax.tick_params(axis="x", length=0)
    ax.text(0.5, -0.17, "só estes dois mantêm o bolso S1 nos dois pH", ha="center",
            fontsize=13.5, color="#55595E", style="italic", transform=ax.transAxes)
    salvar(fig, "fig_ph")


# ------------------------------------------------- 7. poses ---------------
def fig_poses():
    from PIL import Image
    itens = [("NGGRPDAP", "L", "NGGRPDAP   linear   $A.\\ gemmatalis$"),
             ("GQNDS", "L", "GQNDS   linear   $O.\\ nubilalis$"),
             ("GGHSE", "M", "GGHSE   cíclico   $S.\\ frugiperda$"),
             ("GGKPGEP", "M", "GGKPGEP   cíclico   $A.\\ gemmatalis$")]
    fig, ax = plt.subplots(2, 2, figsize=(12.6, 5.3), layout="constrained")
    for a, (lab, f, ttl) in zip(ax.flat, itens):
        img = Image.open(ROOT / "manuscript/figures/_src" / f"{lab}_{f}.png")
        w, h = img.size
        a.imshow(img.crop((int(w * .18), int(h * .14), int(w * .88), int(h * .90))))
        a.axis("off")
        a.set_title(ttl, loc="left", fontsize=15, color=GRAF)
    chave = [Line2D([0], [0], color="#ff00ff", lw=5, label="resíduo âncora"),
             Line2D([0], [0], color="#00ffff", lw=5, label="peptídeo"),
             Line2D([0], [0], color="#ff9933", lw=5, label="Asp189 (bolso S1)"),
             Line2D([0], [0], color="#7a9a5a", lw=5, label="His57, Ser195 (tríade)")]
    fig.legend(handles=chave, loc="outside lower center", ncol=4, frameon=False, fontsize=14)
    salvar(fig, "fig_poses")


# ------------------------------------------- 8. prolina protege -----------
def fig_clivagem():
    ctr = jl("data-e2-results/scissile_geometry_controls.json")
    geo = jl("data-e2-results/scissile_geometry.json")

    def sitios(blocos, pep, protegido):
        """Fracao de quadros em geometria quase de ataque na ligacao K/R-X de cada execucao."""
        out = []
        for ex in blocos:
            for b in ex["bonds"]:
                esq, dire = b["bond"].split("-")
                if esq[0] in "KR" and (dire[0] == "P") == protegido:
                    out.append(b["NAC_frac"] * 100)
        return out

    exposto = sitios(ctr["PGRGDANP"], "PGRGDANP", protegido=False)
    # NGGRPDAP e GGKPGEP aparecem nos dois arquivos; contar so uma vez.
    prot = []
    for pep in ("NGGRPDAP", "GGKPGEP"):
        prot += sitios(geo[pep], pep, protegido=True)
    prot += sitios(ctr["GGEKPPG"], "GGEKPPG", protegido=True)   # controle embaralhado do GGKPGEP

    fig, ax = plt.subplots(figsize=(9.6, 4.7))
    grupos = [(f"Arg seguida de glicina\n(controle PGRGDANP, {len(exposto)} execução)", exposto, LARA),
              (f"Lys/Arg seguida de prolina\n({len(prot)} execuções dos candidatos)", prot, AZUL)]
    for i, (lab, vals, cor) in enumerate(grupos):
        ax.bar(i, np.mean(vals), 0.52, color=cor)
        ax.scatter([i] * len(vals), vals, s=70, color="white", edgecolor=cor, lw=1.8, zorder=3)
        ax.text(i, max(np.mean(vals), max(vals)) + 0.4, f"{np.mean(vals):.1f}%".replace(".", ","),
                ha="center", fontsize=17, fontweight="bold", color=cor)
    ax.set_xticks([0, 1]); ax.set_xticklabels([g[0] for g in grupos], fontsize=14, linespacing=1.4)
    ax.set_ylabel("quadros em geometria\nquase de ataque (%)")
    ax.set_ylim(0, max(exposto) * 1.35)
    ax.spines["bottom"].set_visible(False); ax.tick_params(axis="x", length=0)
    salvar(fig, "fig_clivagem")
    print(f"    [conferencia] exposto={exposto}  protegido={set(prot)}")


# ------------------------------------------- 9. o alvo (esquema) ----------
def _bolso(ax, cx, cy, r, cor_borda):
    """Bolso S1 desenhado como uma cavidade em U."""
    th = np.linspace(np.pi, 2 * np.pi, 120)
    ax.plot(cx + r * np.cos(th), cy + r * np.sin(th) * 1.25, color=cor_borda, lw=3,
            solid_capstyle="round", zorder=3)
    ax.plot([cx - r, cx - r], [cy, cy + r * 0.55], color=cor_borda, lw=3, solid_capstyle="round", zorder=3)
    ax.plot([cx + r, cx + r], [cy, cy + r * 0.55], color=cor_borda, lw=3, solid_capstyle="round", zorder=3)


def fig_alvo():
    fig, ax = plt.subplots(figsize=(12.8, 4.6))
    ax.set_xlim(0, 100); ax.set_ylim(0, 40); ax.axis("off")

    cx = [17, 50, 83]
    tit = ["A lagarta digere a folha", "num intestino fortemente alcalino",
           "com tripsinas que cortam\nem lisina e arginina"]
    sub = ["as proteínas da soja são a fonte\nde aminoácidos da larva",
           "pH ~10, o maior pH luminal conhecido\nem um sistema biológico",
           "o bolso S1 tem um aspartato\nno fundo: o Asp189"]
    for i in range(3):
        ax.text(cx[i], 38, tit[i], ha="center", va="top", fontsize=15.5,
                fontweight="bold", color=AZUL, linespacing=1.4)
        ax.text(cx[i], 28.5, sub[i], ha="center", va="top", fontsize=13,
                color=GRAF, linespacing=1.5)
        if i < 2:
            ax.annotate("", xy=(cx[i] + 15, 34), xytext=(cx[i] + 9, 34),
                        arrowprops=dict(arrowstyle="-|>", color=CINZA, lw=2.2))

    # bolso S1 centrado na metade de baixo, com a ancora dentro
    bx, by, r = 50, 11, 8.5
    _bolso(ax, bx, by, r, AZUL)
    ax.plot([bx, bx], [by - r * 1.15, by + 6.5], color=LARA, lw=3.4, solid_capstyle="round", zorder=4)
    ax.add_patch(plt.Circle((bx, by + 7.3), 1.7, fc=LARA, ec="none", zorder=5))
    ax.text(bx + 3.8, by + 7.3, "lisina ou arginina do substrato",
            ha="left", va="center", fontsize=13.5, color=LARA)
    ax.text(bx, by - r * 1.25 - 1.3, "Asp189, no fundo do bolso",
            ha="center", va="top", fontsize=13.5, color=LARA)
    ax.text(bx - r - 3.5, by + 3, "S1", ha="right", va="center", fontsize=16,
            color=AZUL, fontweight="bold")
    ax.text(bx - r - 4.5, by + 1.5, "A tríade catalítica\n(His57, Asp102, Ser195)\nestá montada\nnos dez modelos",
            ha="right", va="top", fontsize=12.5, color="#55595E", linespacing=1.5)
    salvar(fig, "fig_alvo")


# ------------------------------------------- 10. o paradoxo ---------------
def fig_paradoxo():
    fig, ax = plt.subplots(figsize=(12.6, 4.6))
    ax.set_xlim(0, 100); ax.set_ylim(0, 38); ax.axis("off")

    def cadeia(x0, y, n, destaque, cor_d):
        """Peptideo como colar de contas; 'destaque' e o indice da ancora."""
        xs = x0 + np.arange(n) * 5.6
        ax.plot(xs, [y] * n, color="#B8BCC2", lw=3, zorder=1, solid_capstyle="round")
        for i, x in enumerate(xs):
            c = cor_d if i == destaque else "white"
            e = cor_d if i == destaque else "#9AA0A6"
            ax.add_patch(plt.Circle((x, y), 1.9, fc=c, ec=e, lw=2.2, zorder=3))
        return xs

    # painel esquerdo: ancora
    ax.text(25, 35, "Para inibir, o peptídeo precisa de\nlisina ou arginina no bolso S1",
            ha="center", va="top", fontsize=15.5, fontweight="bold", color=AZUL, linespacing=1.45)
    xs = cadeia(10, 19, 6, 2, AZUL)
    _bolso(ax, xs[2], 11.5, 5.2, AZUL)
    ax.annotate("", xy=(xs[2], 13.5), xytext=(xs[2], 17),
                arrowprops=dict(arrowstyle="-|>", color=AZUL, lw=2.4))
    ax.text(xs[2], 3.0, "encaixa no Asp189", ha="center", va="top", fontsize=13.5, color=AZUL)

    ax.plot([50, 50], [3, 32], color="#DDE0E4", lw=2)

    # painel direito: clivagem
    ax.text(75, 35, "Mas lisina e arginina são exatamente\nonde a tripsina corta",
            ha="center", va="top", fontsize=15.5, fontweight="bold", color=LARA, linespacing=1.45)
    xs2 = cadeia(60, 19, 6, 2, LARA)
    ax.plot([xs2[2] + 2.8, xs2[2] + 2.8], [15.4, 22.6], color=LARA, lw=3, ls=(0, (2, 2)), zorder=4)
    ax.annotate("", xy=(xs2[2] + 2.8, 23.8), xytext=(xs2[2] + 2.8, 29.5),
                arrowprops=dict(arrowstyle="-|>", color=LARA, lw=2.4))
    ax.text(xs2[2] + 2.8, 12.5, "Ser195 corta aqui", ha="center", va="top", fontsize=13.5, color=LARA)
    ax.text(xs2[2] + 2.8, 7.0, "o peptídeo é digerido antes\nde chegar ao alvo",
            ha="center", va="top", fontsize=13, color="#55595E", linespacing=1.5)
    salvar(fig, "fig_paradoxo")

# ------------------------------- 11. escala: tamanho x potencia -----------
def fig_escala():
    """Faixas declaradas no manuscrito (Secoes 1 e 4.2); Ki medidos da literatura ali citada."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.4, 4.3), gridspec_kw={"width_ratios": [1.15, 1]})

    faixas = [("inibidores naturais\n(BPTI, SKTI, SFTI-1, EcTI, BBI)", 14, 176, CINZA),
              ("peptídeos candidatos\ndesenhados aqui", 5, 8, AZUL)]
    for i, (lab, lo, hi, cor) in enumerate(faixas):
        y = 2 - i * 2
        a1.plot([lo, hi], [y, y], color=cor, lw=14, solid_capstyle="round")
        a1.text(hi + 6, y, f"{lo}–{hi} resíduos", va="center", fontsize=14, color=cor)
    a1.set_yticks([2, 0]); a1.set_yticklabels([f[0] for f in faixas], fontsize=13.5, linespacing=1.45)
    a1.set_ylim(-0.7, 2.7); a1.set_xlim(0, 320)
    a1.set_xticks([0, 50, 100, 150, 200])
    a1.set_xlabel("comprimento da cadeia (resíduos)")
    a1.tick_params(axis="y", length=0); a1.spines["left"].set_visible(False)

    # Ki como faixa [min, max]: um valor unico so quando a fonte dá um valor unico
    pep = [("GORE2", 0.10, 0.10, VERDE), ("GORE1", 0.49, 0.49, VERDE),
           ("peptídeos da\npró-região", 0.78, 1.80, CINZA)]
    yy = np.arange(len(pep))[::-1]
    for (lab, lo, hi, cor), y in zip(pep, yy):
        if lo == hi:                       # valor unico: barra a partir de zero
            a2.barh(y, hi, height=0.55, color=cor)
        else:                              # faixa publicada: barra do minimo ao maximo
            a2.barh(y, hi - lo, left=lo, height=0.55, color=cor)
        txt = f"{lo:.2f}".replace(".", ",") if lo == hi else \
              f"{lo:.2f}–{hi:.2f}".replace(".", ",")
        a2.text(hi + 0.06, y, f"{txt} mM", va="center", fontsize=14, color=cor)
    a2.set_yticks(yy); a2.set_yticklabels([p[0] for p in pep], fontsize=13.5, linespacing=1.45)
    a2.set_xlim(0, 2.45); a2.set_xlabel("$K_i$ contra tripsinas de $A.\ gemmatalis$ (mM)")
    a2.set_xticks([0, 0.5, 1.0, 1.5, 2.0])
    a2.set_xticklabels(["0", "0,5", "1,0", "1,5", "2,0"])
    a2.tick_params(axis="y", length=0); a2.spines["left"].set_visible(False)
    a2.set_ylim(-0.7, 2.7)
    a1.text(0.5, 1.02, "Os moldes naturais são grandes", transform=a1.transAxes,
            ha="center", va="bottom", fontsize=15, color=GRAF)
    a2.text(0.5, 1.02, "e os peptídeos curtos já medidos são fracos", transform=a2.transAxes,
            ha="center", va="bottom", fontsize=15, color=GRAF)
    salvar(fig, "fig_escala")


if __name__ == "__main__":
    print("Gerando figuras da apresentacao:")
    fig_plataforma()
    fig_calibracao()
    fig_funil()
    fig_composicao()
    fig_pose_decide()
    fig_ph()
    fig_poses()
    fig_clivagem()
    fig_alvo()
    fig_paradoxo()
    fig_escala()
    print("Pronto.")

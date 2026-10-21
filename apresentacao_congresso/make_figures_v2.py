"""Figuras novas da versao 2 do deck (fluxograma, resumo das MDs, estruturas reais).

Dados: mesmos JSON do manuscrito. Estruturas: renders PyMOL feitos no servidor a partir dos PDB
reais (1SFI, 1BBI, 1AVU) e das trajetorias de MD (render_nat.py, render_cand.py).

Uso (da raiz do projeto): python apresentacao_congresso/make_figures_v2.py <pasta dos renders>
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_slide_figures import (AMAR, AZUL, CINZA, DPI, GRAF, LARA, ROOT, VERDE, jl, salvar)  # noqa: E402
import make_slide_figures as base  # noqa: E402

REND = Path(sys.argv[1]) if len(sys.argv) > 1 else None
CLARO = "#F4F6F8"


def caixa(ax, x, y, w, h, titulo, linhas, cor, tsize=14.8, lsize=13.6):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.05",
                                fc="white", ec="#C9CDD3", lw=1.2))
    ax.add_patch(FancyBboxPatch((x, y), 0.09, h, boxstyle="round,pad=0,rounding_size=0.04",
                                fc=cor, ec=cor, lw=0))
    ax.text(x + 0.2, y + h - 0.16, titulo, fontsize=tsize, fontweight="bold", color=GRAF, va="top")
    ax.text(x + 0.2, y + h - 0.62, linhas, fontsize=lsize, color="#4A4F55", va="top", linespacing=1.4)


def seta(ax, p, q, cor="#55595E", rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=18, lw=1.8, color=cor,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0))


# ------------------------------------------------------------ fluxograma ----
def fig_fluxo():
    fig, ax = plt.subplots(figsize=(13.2, 6.4))
    ax.set_xlim(-0.5, 13.2)
    ax.set_ylim(0.3, 6.4)
    ax.axis("off")
    # linha 1: do alvo ao filtro
    w, h, y = 2.45, 1.75, 4.45
    xs = [0.1, 2.75, 5.4, 8.05, 10.7]
    passos = [("1  Mapear alvo", "8 tripsinas de lagartas\nsítio ativo e bolso S1\nvia moldes 2PTC e 1SFI", AMAR),
              ("2  Calibrar", "6 inibidores reais vs."+chr(10)+"iscas embaralhadas"+chr(10)+"(Boltz-2)", AMAR),
              ("3  Esqueletos", "RFdiffusion (difusão)\nancorado no bolso S1", AZUL),
              ("4  Sequências", "ProteinMPNN\nsem cisteína", AZUL),
              ("5  Filtrar por regra", "sem P1 que as proteases" + chr(10) + "do intestino cortam" + chr(10) + "(K R F Y W L M A V)", LARA)]
    for x, (t, l, c) in zip(xs, passos):
        caixa(ax, x, y, w, h, t, l, c)
    for a, b in zip(xs[:-1], xs[1:]):
        seta(ax, (a + w + 0.03, y + h / 2), (b - 0.03, y + h / 2))
    # bifurcacao L / M
    # linha 2: duas frentes
    for yy, cor, nome, sub in [(2.3, AZUL, "Frente L  ·  linear", "527 sequências"),
                               (0.5, VERDE, "Frente M  ·  cíclico", "543 sequências")]:
        ax.add_patch(FancyBboxPatch((0.1, yy), 13.0, 1.5, boxstyle="round,pad=0,rounding_size=0.06",
                                    fc=CLARO, ec="none"))
        ax.add_patch(FancyBboxPatch((0.1, yy), 0.1, 1.5, boxstyle="round,pad=0,rounding_size=0.04",
                                    fc=cor, ec=cor, lw=0))
        ax.text(0.4, yy + 1.1, nome, fontsize=17, fontweight="bold", color=cor, va="center")
        ax.text(0.4, yy + 0.62, sub, fontsize=14, color="#4A4F55", va="center")
        ax.text(0.4, yy + 0.28, "24 candidatos", fontsize=14, color="#4A4F55", va="center")
        bx = [3.4, 5.75, 8.1, 10.45]
        bw = 2.05
        itens = [("co-dobrar", "Boltz-2: 10 melhores\npor espécie → 3"),
                 ("MD 10 ns\npH 10,0", "GROMACS · CHARMM36"),
                 ("MD 10 ns\npH 8,2", "mesma pose inicial"),
                 ("ordenar", "MM-GBSA · PRODIGY\nΔ vs. embaralhados")]
        for x0, (t, l) in zip(bx, itens):
            ax.add_patch(FancyBboxPatch((x0, yy + 0.18), bw, 1.14, boxstyle="round,pad=0,rounding_size=0.05",
                                        fc="white", ec=cor, lw=1.6))
            ax.text(x0 + bw / 2, yy + 1.0, t, fontsize=14.5, fontweight="bold", color=GRAF, ha="center", va="center",
                    linespacing=1.15)
            ax.text(x0 + bw / 2, yy + 0.43, l, fontsize=12, color="#4A4F55", ha="center", va="center",
                    linespacing=1.2)
        for a, b in zip(bx[:-1], bx[1:]):
            seta(ax, (a + bw + 0.02, yy + 0.75), (b - 0.02, yy + 0.75), cor)
    # barramento: do filtro para as duas frentes
    xb = xs[-1] + w / 2
    ax.plot([xb, xb], [y - 0.03, 4.1], color="#55595E", lw=1.8)
    ax.plot([xb, -0.3], [4.1, 4.1], color="#55595E", lw=1.8)
    ax.plot([-0.3, -0.3], [4.1, 1.25], color="#55595E", lw=1.8)
    seta(ax, (-0.3, 3.05), (0.07, 3.05), AZUL)
    seta(ax, (-0.3, 1.25), (0.07, 1.25), VERDE)
    fig.tight_layout(pad=0.2)
    salvar(fig, "v2_fluxo")


# -------------------------------------------------------------- resumo MD ---
def fig_md_resumo():
    dados = {}
    for fr in ("L", "M"):
        for tag, arq in (("10,0", f"md10_{fr}_analysis"), ("8,2", f"md82_{fr}_analysis")):
            d = jl(f"data-e2-results/{arq}.json")
            vs = [v for k, v in d.items() if isinstance(v, dict) and "occ_5A_h2" in v and not k.endswith("b")]
            dados[(fr, tag)] = vs
    for k, v in dados.items():
        print("  MD", k, len(v), "simulacoes")
    fig, ax = plt.subplots(figsize=(11.2, 4.6))
    grupos = [("L", "10,0"), ("L", "8,2"), ("M", "10,0"), ("M", "8,2")]
    xs = [0, 1, 2.6, 3.6]
    for x, g in zip(xs, grupos):
        vs = dados[g]
        n = len(vs)
        ocup = sum(1 for v in vs if v["occ_5A_h2"] >= 0.70)
        cor = AZUL if g[0] == "L" else VERDE
        ax.bar(x, ocup, 0.72, color=cor)
        ax.bar(x, n - ocup, 0.72, bottom=ocup, color="#E3E6EA")
        ax.text(x, ocup + (n - ocup) + 0.5, f"{ocup} de {n}", ha="center", fontsize=15, color=GRAF, fontweight="bold")
    ax.set_xticks(xs)
    ax.set_xticklabels([f"pH {g[1]}" for g in grupos], fontsize=15)
    ax.text(0.5, -4.3, "Frente L (linear)", ha="center", fontsize=15, color=AZUL, fontweight="bold")
    ax.text(3.1, -4.3, "Frente M (cíclica)", ha="center", fontsize=15, color=VERDE, fontweight="bold")
    ax.set_ylim(0, 30)
    ax.set_ylabel("simulações com bolso S1 ocupado\n(ocupância ≥ 0,70 na 2ª metade)")
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(axis="x", length=0)
    salvar(fig, "v2_md_resumo")


# ------------------------------------------------ inibidores naturais -------
def fig_naturais():
    itens = [("nat_SFTI-1.png", "SFTI-1", "girassol", "14 resíduos", LARA),
             ("nat_BBI.png", "Bowman–Birk (BBI)", "soja", "71 resíduos", VERDE),
             ("nat_SKTI.png", "Kunitz (SKTI)", "soja", "172 resíduos", AZUL)]
    fig, ax = plt.subplots(1, 3, figsize=(13.2, 5.2), layout="constrained")
    for a, (arq, nome, fonte, tam, cor) in zip(ax, itens):
        a.imshow(Image.open(REND / arq))
        a.axis("off")
        a.set_title(nome, fontsize=17, fontweight="bold", color=cor, pad=2)
        a.text(0.5, -0.02, f"{fonte}  ·  {tam}", transform=a.transAxes, ha="center", va="top", fontsize=15,
               color=GRAF)
    salvar(fig, "v2_naturais")


def fig_ancoragem():
    im = Image.open(REND / "complexo_1SFI.png")
    fig, ax = plt.subplots(figsize=(10.4, 7.4))
    ax.imshow(im)
    ax.axis("off")
    ro = dict(fontsize=17, fontweight="bold", ha="left", va="center",
              bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85))
    ax.annotate("Asp189\n(fundo do bolso S1)", (430, 505), (95, 700), color="#C0392B", fontsize=22,
                fontweight="bold", bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.9), arrowprops=dict(arrowstyle="-", color="#C0392B", lw=1.6), ha="left")
    ax.annotate("Lys5 do inibidor (P1)", (600, 440), (140, 250), color=LARA, fontsize=22, fontweight="bold", bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.9),
                arrowprops=dict(arrowstyle="-", color=LARA, lw=1.6), ha="left")
    ax.annotate("Ser195", (770, 590), (830, 760), color="#B97900", fontsize=22, fontweight="bold", bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.9),
                arrowprops=dict(arrowstyle="-", color="#B97900", lw=1.6), ha="left")
    ax.annotate("His57", (905, 470), (1290, 250), color=AZUL, fontsize=22, fontweight="bold", bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.9),
                arrowprops=dict(arrowstyle="-", color=AZUL, lw=1.6), ha="left")
    fig.tight_layout(pad=0.1)
    salvar(fig, "v2_ancoragem")


def fig_poses_md():
    itens = [("NGGRPDAP", "linear", "A. gemmatalis", AZUL), ("GQNDS", "linear", "O. nubilalis", AZUL),
             ("GGKPGEP", "cíclico", "A. gemmatalis", VERDE), ("GGHSE", "cíclico", "S. frugiperda", VERDE)]
    for seq, forma, esp, cor in itens:
        im = Image.open(REND / f"pose_{seq}.png")
        w, h = im.size
        im = im.crop((int(w * .05), int(h * .12), int(w * .98), int(h * .96)))
        im.save(base.OUT / f"v2_pose_{seq}.png")
    print("  poses recortadas")


# ------------------------------------------- resultados por ferramenta ------
def fig_resultados():
    import math
    linhas = [("Mapear o sítio ativo", "Foldseek · moldes 2PTC e 1SFI", 10, "10 receptores", "20 de 20 pares aceitos", AMAR),
              ("Gerar esqueletos", "RFdiffusion", 880, "880", "esqueletos de 5 a 20 resíduos", AZUL),
              ("Escrever sequências", "ProteinMPNN", 22066, "22.066", "sequências únicas", AZUL),
              ("Aplicar o critério", "sem P1 clivável", 1070, "527 L  ·  543 M", "2,4% e 2,5% do total", LARA),
              ("Co-dobrar e escolher", "Boltz-2 + Δ vs. embaralhados", 48, "48", "24 por frente", VERDE),
              ("Simular", "GROMACS · 10 ns · pH 10,0 e 8,2", 96, "96", "simulações (48 × 2 pH)", VERDE),
              ("Ordenar", "MM-GBSA · PRODIGY", 4, "4", "candidatos finais", GRAF)]
    fig, ax = plt.subplots(figsize=(13.2, 5.6))
    ax.set_xlim(0, 13.2)
    ax.set_ylim(-0.6, len(linhas) - 0.4)
    ax.invert_yaxis()
    ax.axis("off")
    for i, (t, sub, v, num, leg, cor) in enumerate(linhas):
        ax.text(0.0, i - 0.12, t, fontsize=16, fontweight="bold", color=GRAF, va="center")
        ax.text(0.0, i + 0.22, sub, fontsize=12.5, color="#5A5F66", va="center")
        ax.barh(i, 0.35 + 5.0 * math.log10(v) / math.log10(22066), left=4.1, height=0.56, color=cor)
        x = 4.1 + 0.35 + 5.0 * math.log10(v) / math.log10(22066) + 0.2
        ax.text(x, i - 0.06, num, fontsize=17, fontweight="bold", color=cor if cor != AMAR else "#A87000", va="center")
        ax.text(x, i + 0.28, leg, fontsize=12.5, color="#5A5F66", va="center")
    ax.text(4.1, len(linhas) - 0.45, "comprimento das barras em escala logarítmica", fontsize=11.5, color="#8A9097",
            style="italic")
    fig.tight_layout(pad=0.2)
    salvar(fig, "v2_resultados")



if __name__ == "__main__":
    print("Figuras v2:")
    fig_fluxo()
    fig_md_resumo()
    fig_resultados()
    if REND:
        fig_naturais()
        fig_ancoragem()
        fig_poses_md()

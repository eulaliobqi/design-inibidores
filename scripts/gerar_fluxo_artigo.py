# -*- coding: utf-8 -*-
"""Fluxograma do estado do artigo (01/10/2026, 21h49). Numeros conferidos no servidor."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

C = {"done": "#b7e4c7", "run": "#ffe066", "queue": "#cfe3f5", "todo": "#e9ecef", "dec": "#f7d6c4"}
EDGE = {"done": "#2a9d8f", "run": "#c9a227", "queue": "#4a7fb5", "todo": "#adb5bd", "dec": "#c8553d"}

fig, ax = plt.subplots(figsize=(15.5, 10.4))
ax.set_xlim(0, 15.5); ax.set_ylim(0, 10.4); ax.axis("off")
plt.rcParams["font.size"] = 9


def box(x, y, w, h, title, body, st, fs=8.0, tfs=8.8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.045",
                                fc=C[st], ec=EDGE[st], lw=1.3))
    ax.text(x + w / 2, y + h - 0.21, title, ha="center", va="top", fontsize=tfs, fontweight="bold")
    if body:
        ax.text(x + w / 2, y + h - 0.47, body, ha="center", va="top", fontsize=fs, linespacing=1.38)


def arrow(x1, y1, x2, y2, style="-|>", color="#495057", lw=1.2, ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=13,
                                 color=color, lw=lw, linestyle=ls, shrinkA=2, shrinkB=2))


ax.text(0.1, 10.15, "Caminho até a submissão — estado em 01/10/2026, 22h30 — sem a campanha de pH",
        fontsize=13.5, fontweight="bold", va="top")
ax.text(0.1, 9.78, "Números conferidos nos arquivos do servidor. Caixa verde = concluído · amarela = em execução · "
                   "azul = na fila (dispara sozinha) · cinza = a fazer · laranja = decisão sua",
        fontsize=8.4, va="top", color="#495057")

# ---------------- FAIXA 1: concluído ----------------
ax.text(0.1, 9.42, "CONCLUÍDO", fontsize=10, fontweight="bold", color=EDGE["done"], va="top")
y1 = 7.85
box(0.1, y1, 2.45, 1.15, "Painel e calibração",
    "8 receptores + subsítios\nTM 0,946–0,957\nescada de escores", "done")
box(2.75, y1, 2.45, 1.15, "Geração e filtro duro",
    "880 esqueletos\n22.066 sequências\n→ L 527 · M 543", "done")
box(5.4, y1, 2.45, 1.15, "E1 · Boltz-2",
    "1.070 predições\nreprodutibilidade ρ 0,57\n(justifica o E2)", "done")
box(8.05, y1, 2.45, 1.15, "E2 · reescore 5×3",
    "80+80 candidatos\nρ(E1,E2) 0,80 / 0,74\nordem do top-10 não resolvida", "done")
box(10.7, y1, 2.3, 1.15, "E4 · QC de pose",
    "48/48 aprovados\ntríade íntegra\n→ top-3 por espécie", "done")
box(13.2, y1, 2.2, 1.15, "Auditoria",
    "sítio validado (8/8)\n5 erros corrigidos\ndesvios medidos", "done")
for x in (2.55, 5.2, 7.85, 10.5, 13.0):
    arrow(x, y1 + 0.57, x + 0.2, y1 + 0.57)

# ---------------- FAIXA 2: em execução ----------------
ax.text(0.1, 7.45, "EM EXECUÇÃO AGORA", fontsize=10, fontweight="bold", color=EDGE["run"], va="top")
y2 = 5.85
box(0.1, y2, 3.5, 1.3, "E6 · MD de triagem 10 ns  (screen two-fronts)",
    "16 de 48 concluídas e analisadas (L 13 · M 3)\nfaltam 32 → 40–56 h (medido: 75–105 min/MD)\ntriagem: 2 aprovados (L) · 0 (M)", "run", fs=8.2)
box(3.85, y2, 3.3, 1.3, "E7 · análise de cada MD",
    "laço incremental ligado:\nanalisa cada MD ao terminar\n(para sozinho no E7 do pipeline)", "run", fs=8.2)
arrow(3.6, y2 + 0.65, 3.85, y2 + 0.65)

box(7.45, y2, 3.6, 1.3, "Escala de referência dos controles",
    "CONCLUÍDA e já no manuscrito:\n5/5 iscas embaralhadas têm ocupância 1,00\n⇒ critério de S1 sem especificidade", "done", fs=8.2)
box(11.35, y2, 4.05, 1.3, "Correções do texto",
    "3.9 escala de referência + a pose inicial decide\n4.4 limitações (ix)–(xiv) · ranqueamento em camadas\nplano de análises corrigido · EN e PT refeitos", "done", fs=8.2)
arrow(11.05, y2 + 0.65, 11.35, y2 + 0.65)

# ---------------- FAIXA 3: fila ----------------
ax.text(0.1, 5.42, "NA FILA — dispara sozinha, sem você precisar agir", fontsize=10, fontweight="bold",
        color=EDGE["queue"], va="top")
y3 = 3.9
box(0.1, y3, 3.5, 1.25, "E3 · controles embaralhados",
    "1.413 predições → 15–20 h\n(recalculado pelo E2: 46 s por predição)\ndá o Δ pareado → libera os controles", "queue", fs=8.2)
box(3.85, y3, 3.3, 1.25, "Matriz 8×8 · E8 · E9",
    "especificidade cruzada do top-1\ncomparação L × M · lista de entrega\n~1 h", "queue", fs=8.2)
box(7.45, y3, 3.6, 1.25, "Controles de MD  (screen md-controls)",
    "5 MDs de 10 ns nas iscas DOS PRÓPRIOS\ncandidatos → 6–9 h (reusa o E3)\n⇒ TESTE DECISIVO da lista final", "queue", fs=8.2)
box(11.35, y3, 4.05, 1.25, "Campanha de pH — FORA DESTE ARTIGO",
    "cancelada em 01/10: 72 MDs, 4–5 dias\n(2/3 de todo o processamento restante)\nscripts prontos → vai para o artigo seguinte", "todo", fs=8.2)
arrow(3.6, y3 + 0.62, 3.85, y3 + 0.62)
arrow(1.85, y2, 1.85, y3 + 1.25, color=EDGE["queue"])
arrow(1.85, y3, 1.85, y3 - 0.33, color=EDGE["queue"], ls=(0, (4, 3)))
arrow(1.85, y3 - 0.33, 9.25, y3 - 0.33, color=EDGE["queue"], ls=(0, (4, 3)), style="-")
arrow(9.25, y3 - 0.33, 9.25, y3, color=EDGE["queue"])
ax.text(5.5, y3 - 0.3, "o E3 pronto libera os controles de MD", fontsize=7.6, color=EDGE["queue"], ha="center", va="bottom")



# ---------------- FAIXA 4: falta ----------------
ax.text(0.1, 3.5, "FALTA FAZER", fontsize=10, fontweight="bold", color="#495057", va="top")
y4 = 1.95
box(0.1, y4, 3.5, 1.3, "Fechar os resultados",
    "recopiar outputs → data-e2-results\nrefazer Figuras 9–13 com dados completos\ntrocar os [[PROVISÓRIO]] por texto final", "todo", fs=8.2)
box(3.85, y4, 3.3, 1.3, "Fechar Resumo e Discussão",
    "Resumo (337/350 palavras, cortar p/ caber)\n4.1 achados principais · 4.3 resistência × S1\nconferir Valaitis/Yang/Zhan/Severiche", "todo", fs=8.2)
box(7.45, y4, 3.6, 1.3, "Seções dos autores",
    "lista de autores e afiliações\ncontribuições · financiamento · COI\ndeclaração de IA · DOI do código", "todo", fs=8.2)
box(11.35, y4, 4.05, 1.3, "Submissão — Frontiers in Natural Products",
    "corpo 8.723/12.000 palavras ✓ · 69 refs ✓\nfiguras 300 dpi TIFF ✓\nconfirmar limite do resumo no sistema", "todo", fs=8.2)
for x in (3.6, 7.15, 11.05):
    arrow(x, y4 + 0.65, x + 0.3, y4 + 0.65)
arrow(0.75, y3, 0.75, y4 + 1.3)

# ---------------- decisões ----------------
box(0.1, 0.12, 15.3, 1.6, "TEMPO ATÉ PODER FECHAR O ARTIGO:  62–86 h de processamento  =  2,7 a 3,5 dias",
    "E6 (32 MDs, 40–56 h)  →  E3 (15–20 h)  →  controles de MD (6–9 h).  A matriz, o E8 e o E9 (~1 h) correm em paralelo aos controles; a escrita (~1 dia) corre junto.\n"
    "Decisões suas, que não dependem de processamento:   1. como tratar no artigo o achado de que a pose inicial decide a triagem (ocupância ≥ 0,70 só nos 3 que\n"
    "partiram a ≤ 3,5 Å do Asp189, e GQNDS passa sem resíduo básico);   2. o que fazer se a isca também ficar em S1;   3. escrever as seções dos autores.",
    "dec", fs=8.3, tfs=9.2)


fig.savefig(r"C:\Users\eulal\.claude\design-inibidores\docs\fluxo_artigo_2026-10-01.png",
            dpi=200, bbox_inches="tight", facecolor="white")
print("ok")

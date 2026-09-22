# scripts/gerar_fig5_especificidade.py
"""Figura 5 — Especificidade real: SI (indice de seletividade) vs. tripsina humana
e Apis mellifera, todos os 35 candidatos com docking real contra nao-alvos.

Dado real: outputs/specificity/specificity_results.json (servidor).
Achado central (artigo_resultados.md Secao 3.11): 0/35 candidatos atingem
SI >= 2.0 kcal/mol contra AMBOS os nao-alvos (limiar de aprovacao). Varios tem
SI negativo (ligam-se de fato MELHOR ao nao-alvo que ao alvo).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from scripts.figuras_utils import (
    CATEGORICAL, GRID_COLOR, STATUS, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    fetch_remote_json, require_key,
)

OUT_DIR = Path("outputs/figuras_artigo")
THRESHOLD = 2.0


def main():
    data = fetch_remote_json("~/design-inibidores/outputs/specificity/specificity_results.json")
    sel = require_key(data, "selectivity", "specificity_results.json")
    threshold = require_key(data, "threshold_kcal", "specificity_results.json")
    n_approved = require_key(data, "n_approved", "specificity_results.json")
    assert threshold == THRESHOLD, f"limiar mudou no servidor: {threshold}"

    seqs, si_human, si_apis = [], [], []
    for seq, v in sel.items():
        si = require_key(v, "selectivity_index", f"selectivity[{seq}]")
        seqs.append(seq)
        si_human.append(si["human_trypsin"])
        si_apis.append(si["apis_mellifera_trypsin"])
    si_human = np.array(si_human)
    si_apis = np.array(si_apis)
    n = len(seqs)

    fig, ax = plt.subplots(figsize=(9, 7.5))

    # Zona de aprovacao real (SI>=2.0 em ambos) — vazia, nenhum candidato cai nela.
    ax.axvspan(THRESHOLD, max(si_human.max(), THRESHOLD) + 1, ymin=0, ymax=1,
               color=STATUS["bom"], alpha=0.06, zorder=0)
    ax.axhspan(THRESHOLD, max(si_apis.max(), THRESHOLD) + 1, xmin=0, xmax=1,
               color=STATUS["bom"], alpha=0.06, zorder=0)
    ax.fill_betweenx([THRESHOLD, max(si_apis.max(), THRESHOLD) + 1], THRESHOLD,
                      max(si_human.max(), THRESHOLD) + 1, color=STATUS["bom"], alpha=0.10, zorder=0)

    ax.axvline(THRESHOLD, color=TEXT_SECONDARY, ls="--", lw=1.1, zorder=1)
    ax.axhline(THRESHOLD, color=TEXT_SECONDARY, ls="--", lw=1.1, zorder=1)
    ax.axvline(0, color=TEXT_MUTED, lw=0.8, zorder=1)
    ax.axhline(0, color=TEXT_MUTED, lw=0.8, zorder=1)

    # Cor: vermelho se SI negativo em pelo menos um eixo (liga-se melhor ao nao-alvo);
    # laranja se positivo mas abaixo do limiar em algum eixo (caso de todos os demais).
    danger = (si_human < 0) | (si_apis < 0)
    colors = np.where(danger, STATUS["critico"], CATEGORICAL["laranja"])

    ax.scatter(si_human, si_apis, c=colors, s=55, alpha=0.85, edgecolors="white",
               linewidths=0.6, zorder=3)

    for x, y, s in zip(si_human, si_apis, seqs):
        if x < 0 or y < 0:
            label = s if len(s) <= 14 else s[:14] + "…"
            ax.annotate(label, (x, y), textcoords="offset points", xytext=(6, 4),
                        fontsize=7.5, color=STATUS["critico"], zorder=4)

    ax.text(THRESHOLD + 0.05, max(si_apis.max(), THRESHOLD) + 0.85,
             "zona de aprovação\n(nenhum candidato aqui)", fontsize=8,
             color=STATUS["bom"], style="italic", va="top")

    ax.set_xlabel("SI vs. tripsina humana (1TRN) — kcal/mol", color=TEXT_PRIMARY)
    ax.set_ylabel("SI vs. tripsina de A. mellifera — kcal/mol", color=TEXT_PRIMARY)
    ax.set_title(
        f"Especificidade real: {n_approved}/{n} candidatos aprovados (SI ≥ {THRESHOLD:.1f} kcal/mol"
        " em ambos os não-alvos)\ndocking real, outputs/specificity/specificity_results.json",
        color=TEXT_PRIMARY, fontsize=11.5,
    )
    ax.grid(color=GRID_COLOR, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(GRID_COLOR)
    ax.spines["bottom"].set_color(GRID_COLOR)

    handles = [
        plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=CATEGORICAL["laranja"],
                    markersize=8, label="SI positivo em ambos, mas < 2,0 (não aprovado)"),
        plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=STATUS["critico"],
                    markersize=8, label="SI negativo em ≥1 não-alvo (liga melhor ao não-alvo)"),
    ]
    ax.legend(handles=handles, loc="upper left", frameon=False, fontsize=8)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "fig5_especificidade_SI.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, facecolor="white")
    print(f"\nSalvo: {out_path}")
    print(f"n={n} candidatos, {n_approved} aprovados, {danger.sum()} com SI negativo em >=1 nao-alvo")


if __name__ == "__main__":
    main()

# scripts/gerar_fig3_cross_species.py
"""Figura 3 — Heatmap real Vina (kcal/mol), TOP-13 x 11 especies.

Dado real: outputs/cross_species_docking/all_cross_species_results.json.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

from scripts.figuras_utils import (
    SEQUENTIAL_BLUE_FULL, SPECIES_LABELS, SPECIES_ORDER, TEXT_PRIMARY, TOP13, fetch_remote_json,
    require_key,
)

OUT_DIR = Path("outputs/figuras_artigo")


def main():
    data = fetch_remote_json(
        "~/design-inibidores/outputs/cross_species_docking/all_cross_species_results.json"
    )

    matrix = np.zeros((len(TOP13), len(SPECIES_ORDER)))
    for i, seq in enumerate(TOP13):
        for j, sp in enumerate(SPECIES_ORDER):
            sp_entry = require_key(data, sp, f"all_cross_species_results.json[{sp}]")
            val = require_key(sp_entry, seq, f"{seq} x {sp}")
            if val is None:
                raise RuntimeError(f"Vina ausente real para {seq} x {sp} — sem inferir, investigar")
            matrix[i, j] = val

    means = matrix.mean(axis=1)
    order = np.argsort(means)  # mais negativo (melhor afinidade media) primeiro
    matrix = matrix[order]
    seqs_sorted = [TOP13[i] for i in order]
    print("Ordem por Vina medio (mais negativo primeiro):")
    for seq, m in zip(seqs_sorted, means[order]):
        print(f"  {seq}: media={m:.2f}")

    # Escala sequencial: mais negativo (melhor) = mais escuro. Inverte o sinal para o cmap.
    cmap = LinearSegmentedColormap.from_list("seq_blue", SEQUENTIAL_BLUE_FULL[::-1])

    fig, ax = plt.subplots(figsize=(11, 7.5))
    im = ax.imshow(matrix, cmap=cmap, aspect="auto")

    ax.set_xticks(range(len(SPECIES_ORDER)))
    ax.set_xticklabels([SPECIES_LABELS[s] for s in SPECIES_ORDER], rotation=45, ha="right",
                        fontsize=8, color=TEXT_PRIMARY, style="italic")
    ax.set_yticks(range(len(seqs_sorted)))
    ax.set_yticklabels([s if len(s) <= 12 else s[:12] + "…" for s in seqs_sorted],
                        fontsize=8, color=TEXT_PRIMARY)
    ax.set_title("Docking real (Vina, kcal/mol) — TOP-13 × 11 espécies Lepidoptera-praga",
                  color=TEXT_PRIMARY, fontsize=12)

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, f"{matrix[i, j]:.1f}", ha="center", va="center", fontsize=6,
                     color="white" if matrix[i, j] < np.median(matrix) else TEXT_PRIMARY)

    cbar = fig.colorbar(im, ax=ax, shrink=0.7)
    cbar.set_label("Vina (kcal/mol) — mais negativo = maior afinidade", fontsize=9, color=TEXT_PRIMARY)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "fig3_cross_species.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, facecolor="white")
    print(f"\nSalvo: {out_path}")


if __name__ == "__main__":
    main()

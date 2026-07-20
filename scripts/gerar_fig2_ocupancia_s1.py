# scripts/gerar_fig2_ocupancia_s1.py
"""Figura 2 — Ocupancia real do bolso S1 (4/5/6 A), media n=3, por candidato.

Dado real: outputs/persistence_deep/persistence_summary.json. Reps com
{"error": ...} sao excluidos da media (nunca tratados como 0).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from scripts.figuras_utils import (
    GRID_COLOR, SEQUENTIAL_BLUE_3, TEXT_PRIMARY, TEXT_SECONDARY, TOP13, fetch_remote_json,
)

OUT_DIR = Path("outputs/figuras_artigo")
CUTOFFS = ["4A", "5A", "6A"]
CUTOFF_LABELS = ["4 Å", "5 Å", "6 Å"]


def main():
    data = fetch_remote_json("~/design-inibidores/outputs/persistence_deep/persistence_summary.json")

    rows = []
    for seq in TOP13:
        per_cutoff = {c: [] for c in CUTOFFS}
        for rep in ("rep1", "rep2", "rep3"):
            entry = data[seq].get(rep)
            if entry is None or "error" in entry:
                continue
            for c in CUTOFFS:
                per_cutoff[c].append(entry[f"occupancy_fraction_{c}"])
        means = {c: float(np.mean(v)) * 100 if v else None for c, v in per_cutoff.items()}
        rows.append((seq, means))
        print(f"{seq}: n={len(per_cutoff['4A'])} "
              f"4A={means['4A']:.1f}% 5A={means['5A']:.1f}% 6A={means['6A']:.1f}%")

    rows.sort(key=lambda r: r[1]["6A"], reverse=True)

    fig, ax = plt.subplots(figsize=(10, 6.5))
    x = np.arange(len(rows))
    width = 0.25
    for i, (cutoff, color, label) in enumerate(zip(CUTOFFS, SEQUENTIAL_BLUE_3, CUTOFF_LABELS)):
        vals = [r[1][cutoff] for r in rows]
        ax.bar(x + (i - 1) * width, vals, width=width, color=color, label=label, zorder=3)

    labels = [r[0] if len(r[0]) <= 10 else r[0][:10] + "…" for r in rows]
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8, color=TEXT_PRIMARY)
    ax.set_ylabel("Fração de frames com distância < corte (%)", color=TEXT_PRIMARY)
    ax.set_title("Ocupância real do bolso S1 — TOP-13 (n=3, 4/5/6 Å)", color=TEXT_PRIMARY, fontsize=12)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    vrrpr_idx = [r[0] for r in rows].index("VRRPR")
    ax.annotate("sai do bolso\n(cai entre réplicas)", xy=(vrrpr_idx, rows[vrrpr_idx][1]["6A"]),
                xytext=(vrrpr_idx, rows[vrrpr_idx][1]["6A"] + 15),
                ha="center", fontsize=8, color=TEXT_SECONDARY, style="italic",
                arrowprops={"arrowstyle": "->", "color": TEXT_SECONDARY, "lw": 1})

    ax.legend(frameon=False, fontsize=9, loc="upper right")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "fig2_ocupancia_s1.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, facecolor="white")
    print(f"\nSalvo: {out_path}")


if __name__ == "__main__":
    main()

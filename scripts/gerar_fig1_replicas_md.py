# scripts/gerar_fig1_replicas_md.py
"""Figura 1 — RMSD real medio +/- DP (n=3) por candidato, réplicas MD.

Dado real: rep1 historica (outputs/md/md_results.json) + rep2/rep3
(outputs/md_replicates/replicates_summary.json). Classificacao computada pela
mesma regra ja publicada (nao hardcodada por candidato).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from scripts.figuras_utils import (
    GRID_COLOR, STATUS, TEXT_PRIMARY, TEXT_SECONDARY, TOP13, classify_stability,
    fetch_remote_json, require_key,
)

OUT_DIR = Path("outputs/figuras_artigo")
STATUS_LABEL = {
    "ESTAVEL_REPRODUTIVEL": "Estável reprodutível",
    "MARGINAL_REPRODUTIVEL": "Marginal reprodutível",
    "ALTA_VARIANCIA": "Alta variância",
}
STATUS_COLOR = {
    "ESTAVEL_REPRODUTIVEL": STATUS["bom"],
    "MARGINAL_REPRODUTIVEL": STATUS["atencao"],
    "ALTA_VARIANCIA": STATUS["critico"],
}
REFUTED = {"RLREELKKAEEWLEKRRKEE", "VRTRR"}  # recorde de estabilidade ja refutado (Tabela 9n)


def main():
    md_results = fetch_remote_json("~/design-inibidores/outputs/md/md_results.json")
    replicates = fetch_remote_json("~/design-inibidores/outputs/md_replicates/replicates_summary.json")

    rows = []
    for seq in TOP13:
        rep1 = require_key(md_results, seq, f"md_results.json[{seq}]")["rmsd_avg_nm"]
        rep_seq = require_key(replicates, seq, f"replicates_summary.json[{seq}]")["replicates"]
        rep2 = require_key(rep_seq, "rep2", f"replicates_summary.json[{seq}].replicates[rep2]")["rmsd_avg_nm"]
        rep3 = require_key(rep_seq, "rep3", f"replicates_summary.json[{seq}].replicates[rep3]")["rmsd_avg_nm"]
        vals = np.array([rep1, rep2, rep3])
        mean, std = float(vals.mean()), float(vals.std(ddof=1))
        status = classify_stability(mean, std)
        rows.append((seq, mean, std, status))
        print(f"{seq}: n=3 mean={mean:.4f} std={std:.4f} status={status}")

    rows.sort(key=lambda r: r[1])  # RMSD medio ascendente

    fig, ax = plt.subplots(figsize=(9, 6.5))
    y = np.arange(len(rows))
    means = [r[1] for r in rows]
    stds = [r[2] for r in rows]
    colors = [STATUS_COLOR[r[3]] for r in rows]
    labels = [r[0] if len(r[0]) <= 10 else r[0][:10] + "…" for r in rows]

    ax.barh(y, means, xerr=stds, color=colors, edgecolor="none", height=0.6,
            error_kw={"ecolor": TEXT_SECONDARY, "elinewidth": 1.2, "capsize": 3})

    for i, (seq, mean, std, status) in enumerate(rows):
        if seq in REFUTED:
            ax.annotate("recorde refutado (n=3)", xy=(mean + std + 0.02, i),
                        va="center", fontsize=8, color=TEXT_SECONDARY, style="italic")

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9, color=TEXT_PRIMARY)
    ax.set_xlabel("RMSD médio ± DP (nm), n=3 réplicas reais", color=TEXT_PRIMARY)
    ax.set_title("Estabilidade real por réplicas — TOP-13 (n=3)", color=TEXT_PRIMARY, fontsize=12)
    ax.grid(axis="x", color=GRID_COLOR, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(GRID_COLOR)

    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in STATUS_COLOR.values()]
    ax.legend(handles, STATUS_LABEL.values(), loc="lower right", frameon=False, fontsize=8)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "fig1_replicas_md.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, facecolor="white")
    print(f"\nSalvo: {out_path}")


if __name__ == "__main__":
    main()

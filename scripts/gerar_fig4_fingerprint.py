# scripts/gerar_fig4_fingerprint.py
"""Figura 4 — Assinatura digital de interacao, 5 candidatos-chave.

Dado real: plip_deep_summary.json (triade, exceto SEEEVLAANEAYAAAHTAYN, ver
nota abaixo), persistence_summary.json (ocupancia 6A + RMSD local),
s2s3_summary.json (contato S2'/S3', sinal ja documentado como ruidoso).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from scripts.figuras_utils import STATUS, TEXT_MUTED, TEXT_PRIMARY, TEXT_SECONDARY, fetch_remote_json

OUT_DIR = Path("outputs/figuras_artigo")
CANDIDATES = ["SRTRR", "VRYRR", "VRRPR", "HRPRRPR", "SEEEVLAANEAYAAAHTAYN"]

# SEEEVLAANEAYAAAHTAYN: contato de triade real ja publicado (Secao 3.10b do artigo,
# mecanismo pi-cation via Tyr12), mas sem plip_deep_summary.json preservado no
# servidor (rodou em analise historica separada). Nao e valor fabricado: e o
# resultado real ja verificado e citado em artigo_resultados.md Tabela 9m.
SEEEVLAANE_TRIAD_HISTORICO = {"contacts_his_any": True, "contacts_asp_any": True, "contacts_ser_any": True}


def main():
    plip = fetch_remote_json("~/design-inibidores/outputs/plip_deep/plip_deep_summary.json")
    persistence = fetch_remote_json("~/design-inibidores/outputs/persistence_deep/persistence_summary.json")
    s2s3 = fetch_remote_json("~/design-inibidores/outputs/s2s3_deep/s2s3_summary.json")

    rows = []
    for seq in CANDIDATES:
        triad = plip[seq] if seq in plip else SEEEVLAANE_TRIAD_HISTORICO
        occ6 = [persistence[seq][r]["occupancy_fraction_6A"] for r in ("rep1", "rep2", "rep3")
                if "error" not in persistence[seq].get(r, {"error": 1})]
        rmsd_local = [persistence[seq][r]["local_rmsd_pocket_nm"] for r in ("rep1", "rep2", "rep3")
                      if "error" not in persistence[seq].get(r, {"error": 1})]
        s2s3_vals = [s2s3[seq][r]["contato_s2s3_fracao"] for r in ("rep1", "rep2", "rep3")
                     if "error" not in s2s3[seq].get(r, {"error": 1})]
        row = {
            "seq": seq,
            "triad": all([triad["contacts_his_any"], triad["contacts_asp_any"], triad["contacts_ser_any"]]),
            "occ6_pct": float(np.mean(occ6)) * 100,
            "rmsd_local": float(np.mean(rmsd_local)),
            "s2s3_pct": float(np.mean(s2s3_vals)) * 100,
        }
        rows.append(row)
        print(f"{seq}: triade={row['triad']} occ6={row['occ6_pct']:.1f}% "
              f"rmsd_local={row['rmsd_local']:.3f} s2s3={row['s2s3_pct']:.1f}%")

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.axis("off")

    n = len(rows)
    col_x = [0.20, 0.42, 0.62, 0.82]
    # Titulos 3 e 4 quebrados em 2 linhas: com wrap=True do matplotlib os textos
    # longos ("RMSD local bolso (nm)" e "Contato S2'/S3' (heuristica, sinal
    # ruidoso)") colidiam visualmente (nao ha wrap automatico por coluna, so por
    # borda de figura) - bug real pego na checagem visual do Step 3, corrigido
    # aqui sem alterar dado/logica/paleta.
    col_titles = ["Tríade His/Asp/Ser", "Ocupância S1 6Å", "RMSD local\nbolso (nm)",
                  "Contato S2'/S3'\n(heurística, sinal ruidoso)"]
    row_y = np.linspace(0.80, 0.10, n)

    for cx, title in zip(col_x, col_titles):
        ax.text(cx, 0.94, title, ha="center", va="center", fontsize=9,
                color=TEXT_PRIMARY, weight="bold", multialignment="center")

    max_rmsd = max(r["rmsd_local"] for r in rows)
    for ry, row in zip(row_y, rows):
        # Sequencias longas (20aa) em fontsize 9 colidiam com a marca de triade
        # em col_x[0] - mesmo bug de legibilidade do Step 3, corrigido reduzindo
        # a fonte apenas para rotulos longos (>10 caracteres).
        label_fontsize = 9 if len(row["seq"]) <= 10 else 7
        ax.text(0.02, ry, row["seq"], ha="left", va="center", fontsize=label_fontsize, color=TEXT_PRIMARY)

        mark = "✓" if row["triad"] else "✗"
        color = STATUS["bom"] if row["triad"] else STATUS["critico"]
        ax.text(col_x[0], ry, mark, ha="center", va="center", fontsize=13, color=color, weight="bold")

        bar_w = 0.14 * (row["occ6_pct"] / 100)
        ax.add_patch(plt.Rectangle((col_x[1] - 0.07, ry - 0.02), bar_w, 0.04, color=STATUS["bom"]))
        ax.text(col_x[1], ry + 0.045, f"{row['occ6_pct']:.0f}%", ha="center", fontsize=7, color=TEXT_SECONDARY)

        bar_w = 0.14 * (row["rmsd_local"] / max_rmsd)
        ax.add_patch(plt.Rectangle((col_x[2] - 0.07, ry - 0.02), bar_w, 0.04, color=STATUS["atencao"]))
        ax.text(col_x[2], ry + 0.045, f"{row['rmsd_local']:.2f}", ha="center", fontsize=7, color=TEXT_SECONDARY)

        bar_w = 0.14 * (row["s2s3_pct"] / 100)
        ax.add_patch(plt.Rectangle((col_x[3] - 0.07, ry - 0.02), bar_w, 0.04,
                                    color=TEXT_MUTED, alpha=0.5, hatch="//"))
        ax.text(col_x[3], ry + 0.045, f"{row['s2s3_pct']:.0f}%", ha="center", fontsize=7, color=TEXT_MUTED)

    ax.set_title("Assinatura digital de interação — 5 candidatos-chave",
                  color=TEXT_PRIMARY, fontsize=12, pad=10)
    ax.text(0.5, 0.02, "Coluna S2'/S3' com hachura = sinal de baixa confiabilidade "
                        "(heurística não validada, 5 frames/réplica)",
            ha="center", fontsize=7, color=TEXT_MUTED, style="italic")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "fig4_fingerprint.png"
    fig.savefig(out_path, dpi=300, facecolor="white")
    print(f"\nSalvo: {out_path}")


if __name__ == "__main__":
    main()

"""VisualizationAgent — Gera figuras automáticas para o relatório final."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns

from .base_agent import BaseAgent


class VisualizationAgent(BaseAgent):

    def run(self, ranking_df: pd.DataFrame, binding_site: dict) -> dict:
        figs = {}
        self.workdir.mkdir(parents=True, exist_ok=True)

        if ranking_df.empty:
            self.logger.warning("Ranking vazio — sem figuras a gerar.")
            return figs

        figs["bar_top20"]       = self._bar_top20(ranking_df)
        figs["heatmap_metrics"] = self._heatmap_metrics(ranking_df)
        figs["scatter_vina_sc"] = self._scatter_vina_sc(ranking_df)
        figs["length_dist"]     = self._length_distribution(ranking_df)
        figs["radar_top5"]      = self._radar_top5(ranking_df)
        figs["charge_hb"]       = self._charge_vs_hbond(ranking_df)

        self.logger.info(f"{len(figs)} figuras salvas em {self.workdir}")
        return figs

    # ─── Figuras ────────────────────────────────────────────────────────────

    def _bar_top20(self, df: pd.DataFrame) -> str:
        top = df.head(20)
        fig, ax = plt.subplots(figsize=(12, 5))
        colors = ["#27ae60" if i == 0 else "#2e86c1" for i in range(len(top))]
        ax.barh(top["sequence"].str[:12] + "…", top["final_score"], color=colors)
        ax.set_xlabel("Score Composto")
        ax.set_title("Top 20 Candidatos — Score Final")
        ax.invert_yaxis()
        fig.tight_layout()
        path = str(self.workdir / "bar_top20.png")
        fig.savefig(path, dpi=150); plt.close()
        return path

    def _heatmap_metrics(self, df: pd.DataFrame) -> str:
        top = df.head(30)
        metrics = ["vina_affinity", "rosetta_I_sc", "md_rmsd_nm",
                   "hbond_avg", "n_arg_lys", "net_charge", "final_score"]
        avail = [c for c in metrics if c in top.columns]
        sub = top[avail].set_index(top["sequence"].str[:10])
        sub_norm = (sub - sub.min()) / (sub.max() - sub.min() + 1e-9)

        fig, ax = plt.subplots(figsize=(10, max(6, len(top) * 0.3)))
        sns.heatmap(sub_norm.T, cmap="RdYlGn_r", ax=ax, annot=False,
                    linewidths=0.3, cbar_kws={"label": "normalizado"})
        ax.set_title("Heatmap de Métricas — Top 30")
        fig.tight_layout()
        path = str(self.workdir / "heatmap_metrics.png")
        fig.savefig(path, dpi=150); plt.close()
        return path

    def _scatter_vina_sc(self, df: pd.DataFrame) -> str:
        fig, ax = plt.subplots(figsize=(8, 6))
        mask_v = df["vina_affinity"].notna()
        mask_r = df["rosetta_I_sc"].notna()
        mask = mask_v & mask_r

        if mask.sum() > 0:
            sc = ax.scatter(
                df.loc[mask, "vina_affinity"],
                df.loc[mask, "rosetta_I_sc"],
                c=df.loc[mask, "final_score"],
                cmap="viridis", s=60, alpha=0.8
            )
            plt.colorbar(sc, ax=ax, label="Score Final")

            # Anotar top 5
            for _, row in df.head(5).iterrows():
                if pd.notna(row.get("vina_affinity")) and pd.notna(row.get("rosetta_I_sc")):
                    ax.annotate(row["sequence"][:8],
                                (row["vina_affinity"], row["rosetta_I_sc"]),
                                fontsize=7, alpha=0.8)
        else:
            ax.text(0.5, 0.5, "Dados insuficientes\n(ferramentas não instaladas)",
                    ha="center", va="center", transform=ax.transAxes, color="gray")

        ax.set_xlabel("Afinidade Vina (kcal/mol)")
        ax.set_ylabel("Rosetta I_sc")
        ax.set_title("Vina Affinity × Rosetta Interface Score")
        fig.tight_layout()
        path = str(self.workdir / "scatter_vina_sc.png")
        fig.savefig(path, dpi=150); plt.close()
        return path

    def _length_distribution(self, df: pd.DataFrame) -> str:
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))

        # Distribuição de tamanhos
        len_counts = df["length"].value_counts().sort_index()
        axes[0].bar(len_counts.index, len_counts.values, color="#2e86c1")
        axes[0].set_xlabel("Tamanho (aa)")
        axes[0].set_ylabel("N candidatos")
        axes[0].set_title("Distribuição de Tamanhos")

        # Score médio por tamanho
        mean_score = df.groupby("length")["final_score"].mean()
        axes[1].bar(mean_score.index, mean_score.values, color="#e67e22")
        axes[1].set_xlabel("Tamanho (aa)")
        axes[1].set_ylabel("Score médio")
        axes[1].set_title("Score Médio por Tamanho")

        fig.tight_layout()
        path = str(self.workdir / "length_distribution.png")
        fig.savefig(path, dpi=150); plt.close()
        return path

    def _radar_top5(self, df: pd.DataFrame) -> str:
        """Gráfico radar comparando 5 métricas dos top-5 candidatos."""
        top5 = df.head(5)
        categories = ["Afinidade\nVina", "Rosetta\nI_sc", "H-bonds",
                      "Estab.\nMD", "Básicos\nP1"]
        metric_cols = ["n_vina", "n_ros", "n_hb", "n_rmsd", "n_alk"]

        available = [c for c in metric_cols if c in top5.columns]
        if len(available) < 3:
            # Fallback: normalizar manualmente
            for c in metric_cols:
                if c not in top5.columns:
                    top5 = top5.copy()
                    top5[c] = 0.5

        N = len(categories)
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6"]

        for idx, (_, row) in enumerate(top5.iterrows()):
            values = [row.get(c, 0.5) for c in metric_cols]
            values += values[:1]
            ax.plot(angles, values, linewidth=2, color=colors[idx],
                    label=row["sequence"][:10])
            ax.fill(angles, values, alpha=0.15, color=colors[idx])

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, size=9)
        ax.set_ylim(0, 1)
        ax.set_title("Perfil dos Top-5 Candidatos", size=13, pad=15)
        ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=8)
        fig.tight_layout()
        path = str(self.workdir / "radar_top5.png")
        fig.savefig(path, dpi=150); plt.close()
        return path

    def _charge_vs_hbond(self, df: pd.DataFrame) -> str:
        fig, ax = plt.subplots(figsize=(7, 5))
        hb_col = "hbond_avg" if "hbond_avg" in df.columns else "n_arg_lys"
        ax.scatter(df["net_charge"], df[hb_col].fillna(0),
                   c=df["final_score"], cmap="plasma", s=50, alpha=0.7)
        ax.set_xlabel("Carga Líquida")
        ax.set_ylabel(hb_col)
        ax.set_title("Carga × H-bonds por comprimento")

        for length in df["length"].unique():
            sub = df[df["length"] == length]
            ax.annotate(f"{length}aa",
                        (sub["net_charge"].mean(), sub[hb_col].fillna(0).mean()),
                        fontsize=8, color="gray")
        fig.tight_layout()
        path = str(self.workdir / "charge_hbond.png")
        fig.savefig(path, dpi=150); plt.close()
        return path

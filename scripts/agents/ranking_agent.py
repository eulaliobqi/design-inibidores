"""RankingAgent — Integra todas as métricas e gera ranking composto.

Métricas integradas:
  - vina_affinity (kcal/mol): menor = melhor
  - rosetta_I_sc: menor = melhor
  - hbond_count: maior = melhor
  - md_rmsd: menor = melhor
  - n_arg_lys: maior = melhor (especificidade P1)
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .base_agent import BaseAgent
from ..utils import peptide_properties


class RankingAgent(BaseAgent):

    def run(self, sequences_data: dict, docking_results: dict,
            rosetta_results: dict, md_results: dict) -> pd.DataFrame:

        weights = self.config.get("ranking", {}).get("weights", {})
        w_vina   = weights.get("vina_affinity", 0.35)
        w_ros    = weights.get("rosetta_I_sc", 0.25)
        w_hb     = weights.get("hbond_count", 0.20)
        w_rmsd   = weights.get("md_rmsd", 0.10)
        w_alk    = weights.get("hydrophobicity", 0.10)

        rows = []

        # Consolidar todas as sequências únicas
        all_seqs = self._collect_sequences(sequences_data)

        for seq, meta in all_seqs.items():
            stem = f"len{meta['length']}_{seq[:8]}"

            # Docking
            dock = docking_results.get(stem, {})
            vina_aff = dock.get("best_affinity_kcal")

            # Rosetta
            ros = rosetta_results.get(stem, {})
            i_sc = ros.get("I_sc")

            # MD
            md = md_results.get(stem, {})
            rmsd = md.get("rmsd_avg_nm")
            hb = md.get("hbond_avg")

            # Propriedades
            props = peptide_properties(seq)

            rows.append({
                "sequence":          seq,
                "length":            meta["length"],
                "vina_affinity":     vina_aff,
                "rosetta_I_sc":      i_sc,
                "md_rmsd_nm":        rmsd,
                "hbond_avg":         hb,
                "n_arg_lys":         props["n_arg_lys"],
                "net_charge":        props["net_charge"],
                "frac_hydrophobic":  props["frac_hydrophobic"],
                "mw_da":             props["mw_da"],
            })

        df = pd.DataFrame(rows)

        if df.empty:
            self.logger.warning("Nenhuma sequência para rankear.")
            return df

        # Normalizar métricas (min-max → [0, 1])
        def norm(series: pd.Series, invert: bool = False) -> pd.Series:
            filled = series.fillna(series.median() if not series.dropna().empty else 0)
            mn, mx = filled.min(), filled.max()
            if mx == mn:
                return pd.Series([0.5] * len(filled), index=filled.index)
            n = (filled - mn) / (mx - mn)
            return (1 - n) if invert else n

        df["n_vina"]   = norm(df["vina_affinity"],    invert=True)
        df["n_ros"]    = norm(df["rosetta_I_sc"],      invert=True)
        df["n_hb"]     = norm(df["hbond_avg"].fillna(df["n_arg_lys"]), invert=False)
        df["n_rmsd"]   = norm(df["md_rmsd_nm"],        invert=True)
        df["n_alk"]    = norm(df["n_arg_lys"].astype(float), invert=False)

        df["final_score"] = (
            w_vina * df["n_vina"] +
            w_ros  * df["n_ros"]  +
            w_hb   * df["n_hb"]   +
            w_rmsd * df["n_rmsd"] +
            w_alk  * df["n_alk"]
        )

        df = df.sort_values("final_score", ascending=False).reset_index(drop=True)
        df.insert(0, "rank", df.index + 1)

        # Salvar CSV
        out_csv = self.workdir / "ranking.csv"
        df.to_csv(out_csv, index=False, float_format="%.4f")

        # Salvar JSON top-N
        top_n = self.config.get("ranking", {}).get("top_candidates", 20)
        top_json = df.head(top_n).to_dict(orient="records")
        (self.workdir / "ranking_top.json").write_text(
            json.dumps(top_json, indent=2, default=str)
        )

        self.logger.info(
            f"Ranking gerado: {len(df)} sequências. "
            f"Top-1: {df.iloc[0]['sequence']} (score={df.iloc[0]['final_score']:.3f})"
        )
        return df

    def _collect_sequences(self, sequences_data: dict) -> dict:
        """Retorna {seq: {length, backbone}} sem duplicatas."""
        seen = {}
        for stem, data in sequences_data.items():
            length = data["length"]
            for seq in data.get("sequences", []):
                if seq and seq not in seen:
                    seen[seq] = {"length": length, "backbone": stem}
        return seen

"""RankingAgent — Integra todas as métricas e gera ranking composto.

Métricas integradas:
  - vina_affinity (kcal/mol): menor = melhor
  - rosetta_I_sc: menor = melhor
  - hbond_count: maior = melhor
  - md_rmsd: menor = melhor (filtro duro: >1.0 nm = instável, penalizado)
  - n_arg_lys: maior = melhor (especificidade P1)

Lição aprendida (Fases 3+4):
  MD é filtro obrigatório — candidatos com melhor Vina/Rosetta podem ser
  instáveis em solvente (RMSD >0.5 nm). Flag md_stable adicionado.
  SARESIKKAYKTFLERYKKL: top-1 Vina (-14.58) mas marginal em MD (0.871 nm).
  RLREELKKAEEWLEKRRKEE: surgiu do OptimizationAgent como mais estável (0.294 nm).
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
        self.logger.info(f"Sequências únicas coletadas: {len(all_seqs)}")

        # Índice Rosetta por sequência (chave antiga: len{n}_{seq[:8]})
        ros_by_seq = {}
        for k, v in rosetta_results.items():
            ros_by_seq[v.get("sequence", "")] = v

        for seq, meta in all_seqs.items():
            # Chave legada para compatibilidade com outputs anteriores
            old_stem = f"len{meta['length']}_{seq[:8]}"
            # Docking: chave = sequência completa (novo padrão), fallback legado
            dock = docking_results.get(seq) or docking_results.get(old_stem, {})
            vina_aff = dock.get("best_affinity_kcal")

            # Rosetta
            ros = ros_by_seq.get(seq, {})
            i_sc = ros.get("I_sc")

            # MD (chave = sequência completa, fallback old_stem)
            md = md_results.get(seq, md_results.get(old_stem, {}))
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
            fs = series.astype(float)
            med = float(fs.dropna().median()) if fs.dropna().size > 0 else 0.0
            filled = fs.fillna(med)
            mn, mx = float(filled.min()), float(filled.max())
            if mx == mn:
                return pd.Series([0.5] * len(filled), index=filled.index)
            n = (filled - mn) / (mx - mn)
            return (1 - n) if invert else n

        df["n_vina"]   = norm(df["vina_affinity"],    invert=True)
        df["n_ros"]    = norm(df["rosetta_I_sc"],      invert=True)
        hb_filled = df["hbond_avg"].astype(float).fillna(df["n_arg_lys"].astype(float))
        df["n_hb"]     = norm(hb_filled, invert=False)
        df["n_rmsd"]   = norm(df["md_rmsd_nm"],        invert=True)
        df["n_alk"]    = norm(df["n_arg_lys"].astype(float), invert=False)

        df["final_score"] = (
            w_vina * df["n_vina"] +
            w_ros  * df["n_ros"]  +
            w_hb   * df["n_hb"]   +
            w_rmsd * df["n_rmsd"] +
            w_alk  * df["n_alk"]
        )

        # Classificação de estabilidade MD (Fases 3+4 validaram estes limiares)
        def md_stability(rmsd):
            if pd.isna(rmsd):
                return "sem_md"
            r = float(rmsd)
            if r < 0.5:
                return "estavel"
            if r <= 1.0:
                return "marginal"
            return "instavel"

        df["md_stable"] = df["md_rmsd_nm"].apply(md_stability)

        # Penalizar instáveis na pontuação final (lição: RMSD >1.0 descarta candidato)
        instavel_mask = df["md_stable"] == "instavel"
        df.loc[instavel_mask, "final_score"] *= 0.5

        df = df.sort_values("final_score", ascending=False).reset_index(drop=True)
        df.insert(0, "rank", df.index + 1)

        # Salvar CSV de ranking
        out_csv = self.workdir / "ranking.csv"
        df.to_csv(out_csv, index=False, float_format="%.4f")

        # Salvar JSON top-N
        top_n = self.config.get("ranking", {}).get("top_candidates", 20)
        top_json = df.head(top_n).to_dict(orient="records")
        (self.workdir / "ranking_top.json").write_text(
            json.dumps(top_json, indent=2, default=str)
        )

        # Salvar lista de estáveis separadamente (usada como parental pelo OptimizationAgent)
        stable = df[df["md_stable"] == "estavel"]
        if not stable.empty:
            (self.workdir / "ranking_stable.json").write_text(
                json.dumps(stable.head(top_n).to_dict(orient="records"), indent=2, default=str)
            )
            self.logger.info(f"Candidatos MD estáveis: {len(stable)} → ranking_stable.json")

        # Preencher labels no dataset ML
        self._fill_ml_labels(df)

        self.logger.info(
            f"Ranking gerado: {len(df)} sequências. "
            f"Top-1: {df.iloc[0]['sequence']} (score={df.iloc[0]['final_score']:.3f}) "
            f"[MD: {df.iloc[0]['md_stable']}]"
        )
        return df

    def _fill_ml_labels(self, ranking_df: pd.DataFrame):
        """Escreve vina_affinity_kcal, rosetta_I_sc e final_score no dataset ML CSV."""
        ml_csv = self.workdir.parent / "dataset" / "ml_training_dataset.csv"
        if not ml_csv.exists():
            return
        try:
            df_ml = pd.read_csv(ml_csv)
            score_map = ranking_df.set_index("sequence")[
                ["vina_affinity", "rosetta_I_sc", "final_score"]
            ].to_dict("index")

            df_ml["vina_affinity_kcal"] = df_ml["sequence"].map(
                lambda s: score_map.get(s, {}).get("vina_affinity", "")
            )
            df_ml["rosetta_I_sc"] = df_ml["sequence"].map(
                lambda s: score_map.get(s, {}).get("rosetta_I_sc", "")
            )
            df_ml["final_score"] = df_ml["sequence"].map(
                lambda s: score_map.get(s, {}).get("final_score", "")
            )
            df_ml.to_csv(ml_csv, index=False, float_format="%.6f")
            labeled = df_ml["vina_affinity_kcal"].notna().sum()
            self.logger.info(
                f"ML CSV atualizado: {labeled}/{len(df_ml)} sequências com labels "
                f"({ml_csv})"
            )
        except Exception as e:
            self.logger.error(f"Erro ao preencher labels ML: {e}")

    def _collect_sequences(self, sequences_data: dict) -> dict:
        """Retorna {seq: {length, backbone}} sem duplicatas."""
        seen = {}
        for stem, data in sequences_data.items():
            length = data["length"]
            for seq in data.get("sequences", []):
                if seq and seq not in seen:
                    seen[seq] = {"length": length, "backbone": stem}
        return seen

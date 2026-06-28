"""OptimizationAgent — Redesign iterativo dos melhores candidatos.

Estratégia:
  1. Pega os top_k candidatos do ranking (filtra por MD estável se disponível)
  2. Gera variantes por:
     a. Mutação pontual em posições P2-P5 (mantendo P1=Arg/Lys)
     b. Troca conservativa (isósteros)
     c. Extensão N/C-terminal com resíduos favoráveis
     d. Crossover entre 2 parentais (novo: Fase 4+)
  3. Prioriza variantes com maior n_arg_lys e KR_internal=0 (resistência proteolítica)

Lição aprendida (Fase 4):
  - Adicionar crossover produz candidatos não-óbvios (RLREELKKAEEWLEKRRKEE surgiu assim)
  - Filtrar por md_stable=True como parental reduz iterações desperdiçadas
  - KR_internal=0 é crítico para resistência a proteases intestinais de Lepidoptera
  - Perfil Glu/Leu pode indicar mecanismo de ligação alternativo (não P1-Asp apenas)
"""
import json
import random
from pathlib import Path

from .base_agent import BaseAgent
from ..utils import peptide_properties


# Grupos de isósteros para substituição conservativa
ISOSTERIC_GROUPS = [
    ["I", "L", "V"],           # alifáticos
    ["F", "Y", "W"],           # aromáticos
    ["S", "T"],                # polares pequenos
    ["K", "R"],                # básicos (P1: manter)
    ["D", "E"],                # ácidos
    ["N", "Q"],                # amida
    ["A", "G"],                # pequenos
]

# Resíduos favoráveis para extensões terminais de inibidores de tripsina
N_TERM_FAVORED = ["R", "K", "A", "G", "P"]
C_TERM_FAVORED = ["I", "L", "V", "A", "K", "R"]


class OptimizationAgent(BaseAgent):

    def run(self, ranked_df, iteration: int = 1) -> list[dict]:
        """
        ranked_df: pandas DataFrame com colunas [sequence, length, final_score, ...]
        Retorna lista de novos candidatos para próxima rodada.
        """
        import pandas as pd

        cfg = self.config.get("optimization", {})
        top_k = cfg.get("top_k", 10)
        mutation_rate = cfg.get("mutation_rate", 0.3)
        vary_pos = cfg.get("positions_to_vary", [2, 3, 4, 5])
        require_no_kr_internal = cfg.get("require_no_kr_internal", False)

        # Preferir candidatos MD estáveis como parentais (lição Fases 3+4)
        if "md_stable" in ranked_df.columns:
            stable = ranked_df[ranked_df["md_stable"] == "estavel"]
            top_pool = stable if len(stable) >= 3 else ranked_df
        else:
            top_pool = ranked_df

        # Selecionar top candidatos com P1=Arg/Lys
        top = top_pool[top_pool["sequence"].str[0].isin(["R", "K"])].head(top_k)

        new_candidates = []

        for _, row in top.iterrows():
            seq = row["sequence"]
            length = row.get("length", len(seq))

            # a) Mutações pontuais
            for _ in range(3):
                mutated = self._point_mutate(seq, vary_pos, mutation_rate)
                new_candidates.append({
                    "sequence": mutated,
                    "length": len(mutated),
                    "parent": seq,
                    "operation": "point_mutation",
                    "iteration": iteration,
                    "has_p1_basic": int(mutated[0] in "RK") if mutated else 0,
                    **peptide_properties(mutated),
                })

            # b) Substituição conservativa
            conservative = self._conservative_swap(seq, vary_pos)
            if conservative != seq:
                new_candidates.append({
                    "sequence": conservative,
                    "length": len(conservative),
                    "parent": seq,
                    "operation": "conservative_swap",
                    "iteration": iteration,
                    "has_p1_basic": int(conservative[0] in "RK") if conservative else 0,
                    **peptide_properties(conservative),
                })

            # c) Extensão terminal (apenas se length < 20)
            if length < 20:
                extended = self._extend_terminal(seq)
                new_candidates.append({
                    "sequence": extended,
                    "length": len(extended),
                    "parent": seq,
                    "operation": "terminal_extension",
                    "iteration": iteration,
                    "has_p1_basic": int(extended[0] in "RK") if extended else 0,
                    **peptide_properties(extended),
                })

        # d) Crossover entre pares de parentais estáveis (novo: Fases 4+)
        parent_seqs = list(top["sequence"])
        if len(parent_seqs) >= 2:
            for i in range(min(len(parent_seqs) - 1, 5)):
                crossed = self._crossover(parent_seqs[i], parent_seqs[i + 1])
                if crossed:
                    new_candidates.append({
                        "sequence": crossed,
                        "length": len(crossed),
                        "parent": f"{parent_seqs[i]}+{parent_seqs[i+1]}",
                        "operation": "crossover",
                        "iteration": iteration,
                        "has_p1_basic": int(crossed[0] in "RK") if crossed else 0,
                        **peptide_properties(crossed),
                    })

        # Filtrar: P1 deve ser R ou K, sem duplicatas
        # Opcional: filtrar KR-internos (resistência proteolítica)
        seen = set()
        filtered = []
        for c in new_candidates:
            s = c["sequence"]
            if s in seen or not s or s[0] not in "RK":
                continue
            if require_no_kr_internal:
                # Conta K/R em posições internas (exclui P1 e C-terminal)
                kr_internal = sum(1 for aa in s[1:-1] if aa in "KR")
                if kr_internal > 0:
                    continue
            seen.add(s)
            filtered.append(c)

        # Ordenar: preferir sem KR_interno, depois por n_arg_lys
        filtered.sort(key=lambda x: -(
            x.get("n_arg_lys", 0) +
            x.get("has_p1_basic", 0) * 2 -
            sum(1 for aa in x["sequence"][1:-1] if aa in "KR") * 0.5
        ))

        # Salvar
        (self.workdir / f"iter{iteration}_candidates.json").write_text(
            json.dumps(filtered, indent=2, default=bool)
        )
        self.logger.info(
            f"Iteração {iteration}: {len(filtered)} novos candidatos gerados "
            f"a partir de {len(top)} sequências parentais "
            f"({'MD estáveis' if 'md_stable' in ranked_df.columns else 'top ranking'})."
        )
        return filtered

    def _point_mutate(self, seq: str, vary_pos: list, rate: float) -> str:
        aa_pool = list("RKAGILMFWYVSTPNQDEH")
        seq = list(seq)
        for pos in vary_pos:
            idx = pos - 1  # 1-based → 0-based
            if idx < len(seq) and random.random() < rate:
                seq[idx] = random.choice(aa_pool)
        return "".join(seq)

    def _conservative_swap(self, seq: str, vary_pos: list) -> str:
        seq = list(seq)
        for pos in vary_pos:
            idx = pos - 1
            if idx >= len(seq):
                continue
            aa = seq[idx]
            for group in ISOSTERIC_GROUPS:
                if aa in group:
                    alternatives = [x for x in group if x != aa]
                    if alternatives:
                        seq[idx] = random.choice(alternatives)
                    break
        return "".join(seq)

    def _crossover(self, seq_a: str, seq_b: str) -> str:
        """Crossover de ponto único entre dois parentais de comprimento similar."""
        if len(seq_a) < 4 or len(seq_b) < 4:
            return ""
        short, long_ = (seq_a, seq_b) if len(seq_a) <= len(seq_b) else (seq_b, seq_a)
        cut = random.randint(2, len(short) - 2)
        child = short[:cut] + long_[cut:]
        # Garantir P1 básico
        if child[0] not in "RK":
            child = short[0] + child[1:]
        return child[:20]  # max 20 aa

    def _extend_terminal(self, seq: str) -> str:
        # Adicionar 1-2 resíduos na N ou C terminal
        n_add = random.randint(1, 2)
        if random.random() < 0.5:
            # N-terminal
            add = "".join(random.choice(N_TERM_FAVORED) for _ in range(n_add))
            return add + seq
        else:
            # C-terminal (P1 é o primeiro resíduo, não muda)
            add = "".join(random.choice(C_TERM_FAVORED) for _ in range(n_add))
            return seq + add

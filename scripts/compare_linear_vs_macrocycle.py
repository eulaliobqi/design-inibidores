"""
compare_linear_vs_macrocycle.py -- E8 do plano v3. Sem GPU. Compara as duas frentes (criterio duro de
nao-clivabilidade) com os resultados de E1:
  L = outputs/b23_cleavage_linear_hard.json   + data-b23-scoring/results/b23_boltz2_L_scores.json
  M = outputs/b23_cleavage_circular_hard.json + data-b23-scoring/results/b23_boltz2_M_scores.json
e, como teste de reprodutibilidade do Boltz-2, com as predicoes ciclicas antigas
(data-b23-scoring/results/b23_boltz2_scores.json; mesma sequencia+backbone, mesmo protocolo).
Saida: outputs/linear_vs_macrocycle.json
"""
import json
import statistics
from pathlib import Path

from scipy.stats import spearmanr

ROOT = Path(__file__).parent.parent
RES = ROOT / "data-b23-scoring" / "results"


def load(p):
    p = Path(p)
    return json.loads(p.read_text()) if p.exists() else {}


def keyed(d):
    return {sp: {(r["backbone"], r["sequence"]): r["confidence_score"] for r in rows} for sp, rows in d.items()}


def resistant(clv):
    return {sp: {(r["backbone"], r["sequence"]) for r in e["results"] if r["verdict"] == "RESISTENTE"}
            for sp, e in clv["by_species"].items()}


def corr(pairs):
    if len(pairs) < 3:
        return None
    a, b = zip(*pairs)
    return {"n": len(pairs), "spearman": float(spearmanr(a, b)[0]),
            "mean_diff_b_minus_a": statistics.mean(y - x for x, y in pairs),
            "mean_abs_diff": statistics.mean(abs(y - x) for x, y in pairs)}


def main():
    L = keyed(load(RES / "b23_boltz2_L_scores.json"))
    M = keyed(load(RES / "b23_boltz2_M_scores.json"))
    old = keyed(load(RES / "b23_boltz2_scores.json"))
    rl = resistant(load(ROOT / "outputs/b23_cleavage_linear_hard.json"))
    rm = resistant(load(ROOT / "outputs/b23_cleavage_circular_hard.json"))
    out = {"per_species": {}, "pooled": {}}
    lm, rep = [], []
    for sp in rl:
        common = rl[sp] & rm.get(sp, set())
        pl = [(M[sp][k], L[sp][k]) for k in common if k in M.get(sp, {}) and k in L.get(sp, {})]
        pr = [(old[sp][k], M[sp][k]) for k in rm.get(sp, ()) if k in old.get(sp, {}) and k in M.get(sp, {})]
        lm += pl
        rep += pr
        out["per_species"][sp] = {
            "n_L": len(rl[sp]), "n_M": len(rm.get(sp, ())), "n_em_ambos": len(common),
            "L_vs_M_mesma_sequencia": corr(pl), "M_novo_vs_M_antigo": corr(pr),
            "top3_L": sorted(((c, k[1]) for k, c in L.get(sp, {}).items() if k in rl[sp]), reverse=True)[:3],
            "top3_M": sorted(((c, k[1]) for k, c in M.get(sp, {}).items() if k in rm.get(sp, ())), reverse=True)[:3]}
    out["pooled"] = {"L_vs_M_mesma_sequencia": corr(lm),
                     "reprodutibilidade_Boltz2_M_novo_vs_antigo": corr(rep)}
    (ROOT / "outputs/linear_vs_macrocycle.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(json.dumps(out["pooled"], indent=2))


if __name__ == "__main__":
    main()

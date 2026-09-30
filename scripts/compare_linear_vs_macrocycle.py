"""
compare_linear_vs_macrocycle.py -- bracos de comparacao (manuscrito em forma linear; o
macrociclo e' o braco comparativo). Sem GPU. Le os resultados JA existentes:
  linear     : outputs/b23_cleavage_linear_strict.json + data-b23-scoring/results/b23_boltz2_linear_scores.json
  macrociclo : outputs/b23_cleavage_circular.json       + data-b23-scoring/results/b23_boltz2_scores.json
                                                          (+ Agemmatalis, top_candidates_circular_all8.json)
Saida: outputs/linear_vs_macrocycle.json com
  - contagem de classes por especie nas duas regras e sobreposicao dos RESISTENTE;
  - para sequencias RESISTENTE em ambas e pontuadas nos dois modos: correlacao de Spearman entre
    confidence_score do Boltz-2 (peptideo ciclico vs linear), diferenca media, concordancia de top-k;
  - top-1 por especie nos dois bracos.
"""
import json
from pathlib import Path

from scipy.stats import spearmanr

ROOT = Path(__file__).parent.parent


def load(p):
    return json.loads((ROOT / p).read_text())


def keyed(scores_by_sp):
    return {sp: {(r["backbone"], r["sequence"]): r for r in rows} for sp, rows in scores_by_sp.items()}


def resistant(clv):
    return {sp: {(r["backbone"], r["sequence"]) for r in e["results"] if r["verdict"] == "RESISTENTE"}
            for sp, e in clv["by_species"].items()}


def main():
    lin_clv, cir_clv = load("outputs/b23_cleavage_linear_strict.json"), load("outputs/b23_cleavage_circular.json")
    lin_sc = keyed(load("data-b23-scoring/results/b23_boltz2_linear_scores.json"))
    cir_sc = keyed(load("data-b23-scoring/results/b23_boltz2_scores.json"))
    lin_res, cir_res = resistant(lin_clv), resistant(cir_clv)

    out = {"per_species": {}, "pooled": {}}
    xs, ys = [], []
    for sp in lin_res:
        both = lin_res[sp] & cir_res.get(sp, set())
        pair = [(cir_sc[sp][k]["confidence_score"], lin_sc[sp][k]["confidence_score"])
                for k in both if k in cir_sc.get(sp, {}) and k in lin_sc.get(sp, {})]
        e = {"n_linear_resistente": len(lin_res[sp]), "n_circular_resistente": len(cir_res.get(sp, ())),
             "n_em_ambos": len(both), "n_pareados_boltz": len(pair)}
        if len(pair) > 2:
            c, l = zip(*pair)
            e["spearman_cyc_vs_lin"] = float(spearmanr(c, l)[0])
            e["media_dif_lin_menos_cyc"] = sum(b - a for a, b in pair) / len(pair)
            xs += c; ys += l
        for tag, sc, res in (("linear", lin_sc, lin_res), ("macrociclo", cir_sc, cir_res)):
            rows = [r for k, r in sc.get(sp, {}).items() if k in res.get(sp, ())]
            if rows:
                b = max(rows, key=lambda r: r["confidence_score"])
                e[f"top1_{tag}"] = {"sequence": b["sequence"], "confidence": b["confidence_score"]}
        out["per_species"][sp] = e
    if len(xs) > 2:
        out["pooled"] = {"n_pareados": len(xs), "spearman_cyc_vs_lin": float(spearmanr(xs, ys)[0]),
                         "media_dif_lin_menos_cyc": sum(b - a for a, b in zip(xs, ys)) / len(xs)}
    (ROOT / "outputs/linear_vs_macrocycle.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

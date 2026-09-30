"""
select_top_candidates.py -- escolhe, por especie, o candidato de maior confidence_score do
Boltz-2 ENTRE os classificados RESISTENTE pela regra de clivagem CIRCULAR (macrociclo
cabeca-cauda; ver analyze_cleavage.find_cleavage_sites(circular=True)).

Regra de selecao (a mesma do plano, so que aplicada ao conjunto corrigido): maior
confidence_score do Boltz-2 dentro do conjunto RESISTENTE. Nao ha nenhum outro criterio.

Entradas (relativas a ROOT):
  --cleavage   json de run_cleavage_b23.py com a regra circular
  --scores     data-b23-scoring/results/b23_boltz2_scores.json
  --manifests  data-b23-scoring/boltz_yaml/_manifests (stem <-> backbone/sequencia)
Saida: --out (json {especie: {sequence, backbone, confidence_score, pdb, ...}})

Uso: python scripts/select_top_candidates.py --cleavage outputs/b23_cleavage_circular.json \
        --out data-b23-scoring/results/top_candidates_circular.json
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cleavage", required=True)
    ap.add_argument("--scores", default="data-b23-scoring/results/b23_boltz2_scores.json")
    ap.add_argument("--manifests", default="data-b23-scoring/boltz_yaml/_manifests")
    ap.add_argument("--rule", default="linear-strict", choices=["linear-strict-hard", "circular-hard", "linear-strict", "linear", "circular"])
    ap.add_argument("--boltz-out-prefix", default="outputs/b23_boltz2")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    clv = json.loads((ROOT / args.cleavage).read_text())
    assert clv.get("rule") == args.rule, f"json de clivagem tem regra {clv.get('rule')!r}, esperado {args.rule!r}"
    scores = json.loads((ROOT / args.scores).read_text())

    out, report = {}, {}
    for sp, entry in clv["by_species"].items():
        resistant = {(r["backbone"], r["sequence"])
                     for r in entry["results"] if r["verdict"] == "RESISTENTE"}
        sc = scores.get(sp)
        if not sc:
            report[sp] = {"n_resistente": len(resistant), "n_pontuados": 0,
                          "nota": "sem scores Boltz-2 para esta especie"}
            continue
        kept = [c for c in sc if (c["backbone"], c["sequence"]) in resistant]
        not_scored = len(resistant) - len(kept)
        report[sp] = {"n_resistente": len(resistant), "n_pontuados_no_conjunto": len(kept),
                      "resistentes_sem_score": not_scored}
        if not kept:
            continue
        best = max(kept, key=lambda c: c["confidence_score"])
        manifest = json.loads((ROOT / args.manifests / f"{sp}.json").read_text())
        stems = [k for k, v in manifest.items()
                 if v["backbone"] == best["backbone"] and v["sequence"] == best["sequence"]]
        if len(stems) != 1:
            raise RuntimeError(f"{sp}: esperado 1 stem no manifest para {best['backbone']}/"
                               f"{best['sequence']}, achei {stems}")
        stem = stems[0]
        pdb = (f"{args.boltz_out_prefix}_{sp}/boltz_results_{sp}/predictions/{stem}/"
               f"{stem}_model_0.pdb")
        out[sp] = {"sequence": best["sequence"], "backbone": best["backbone"],
                   "confidence_score": best["confidence_score"],
                   "complex_plddt": best["complex_plddt"], "iptm": best["iptm"], "pdb": pdb}
    (ROOT / args.out).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / args.out).write_text(json.dumps({"rule": args.rule, "candidates": out,
                                             "report": report}, indent=2))
    for sp, v in out.items():
        print(f"{sp:13s} {v['sequence']:12s} {v['confidence_score']:.4f}  {v['backbone']}")
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()

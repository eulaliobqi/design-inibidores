"""
compare_controls.py -- candidato x controle embaralhado (MD de 10 ns, mesmo protocolo) e elegibilidade ao controle negativo.

Para cada candidato com controle em `outputs/md10_controls_{L,M}/analysis_summary.json`, compara a ocupancia de S1 a 5 A
na 2a metade (`occ_5A_h2`) com a do candidato em `outputs/md10_{L,M}/analysis_summary.json`.
  separa           : ocupancia do candidato > a do controle (diferenca > 0,10, so para leitura; nenhum limiar novo na decisao)
  eligible_negctrl : ocupancia do candidato >= 0,70 (criterio declarado) e >= a do proprio controle (regra do manuscrito, 3.9)
Saida: outputs/controls_decision.json e outputs/controls_decision.md. Nao decide a retirada do controle: essa leitura
(se os controles nao se separam, o controle e' retirado por completo) e' feita sobre o conjunto, apos ver a tabela.
Uso: python -m scripts.compare_controls [--negctrl]   (--negctrl: acrescenta a tabela das variantes Asp/Leu)
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
FIELDS = ("occ_5A_h2", "anchor_aa", "anchor_same_in_halves", "d_anchor_asp_fim_A", "peptide_rmsd_local_nm_final20pct")


def jl(p):
    p = ROOT / p
    return json.loads(p.read_text()) if p.exists() else {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--negctrl", action="store_true")
    a = ap.parse_args()
    dec, md = {}, ["# Candidatos x controles embaralhados (10 ns)\n"]
    for F in ("L", "M"):
        cand = jl(f"outputs/md10_{F}/analysis_summary.json")
        ctrl = jl(f"outputs/md10_controls_{F}/analysis_summary.json")
        neg = jl(f"outputs/md10_negctrl_{F}/analysis_summary.json") if a.negctrl else {}
        dec[F] = {}
        md += [f"\n## Frente {F}\n", "| candidato | seq | occ cand | ancora cand | controle | occ ctrl | ancora ctrl | separa | elegivel neg |",
               "|---|---|---|---|---|---|---|---|---|"]
        for ck, cv in sorted(ctrl.items()):
            key = ck.split("__ctrl_")[0]
            c = cand.get(key, {})
            if "error" in cv or "error" in c or "occ_5A_h2" not in c or "occ_5A_h2" not in cv:
                md.append(f"| {key} | {c.get('sequence')} | erro/ausente | | {ck} | | | | |")
                dec[F][key] = {"error": cv.get("error") or c.get("error") or "ausente", "eligible_negctrl": False}
                continue
            co, ko = c["occ_5A_h2"], cv["occ_5A_h2"]
            elig = bool(co >= 0.70 and co >= ko)
            dec[F][key] = {"sequence": c["sequence"], "cand": {k: c.get(k) for k in FIELDS},
                           "ctrl": {"key": ck, "sequence": cv["sequence"], **{k: cv.get(k) for k in FIELDS}},
                           "delta_occ": round(co - ko, 3), "separates": bool(co - ko > 0.10), "eligible_negctrl": elig}
            md.append(f"| {key} | {c['sequence']} | {co} | {c.get('anchor_aa')} | {cv['sequence']} | {ko} | "
                      f"{cv.get('anchor_aa')} | {'sim' if co - ko > 0.10 else 'nao'} | {'sim' if elig else 'nao'} |")
        if neg:
            md += [f"\n### Controle negativo (troca da ancora), frente {F}\n",
                   "| variante | seq | occ 2a metade | ancora | d ancora-Asp189 final (A) | ancora igual nas metades |", "|---|---|---|---|---|---|"]
            for nk, nv in sorted(neg.items()):
                md.append(f"| {nk} | {nv.get('sequence')} | {nv.get('occ_5A_h2', nv.get('error'))} | {nv.get('anchor_aa')} | "
                          f"{nv.get('d_anchor_asp_fim_A')} | {nv.get('anchor_same_in_halves')} |")
            dec[F + "_neg"] = neg
    sep = [v["separates"] for F in ("L", "M") for v in dec[F].values() if "separates" in v]
    md.append(f"\nControles com leitura: {len(sep)}; separam do candidato: {sum(sep)}.")
    (ROOT / "outputs/controls_decision.json").write_text(json.dumps(dec, indent=2))
    (ROOT / "outputs/controls_decision.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()

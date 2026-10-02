"""
rank_final_candidates.py -- lista final de peptideos candidatos a inibidores, por frente (L = linear, M = macrociclo), integrando
TODAS as evidencias computacionais, sem criar limiares novos (so os pre-registrados do plano v3):
  E0  nao clivavel pelo criterio duro (todos os candidatos o cumprem por construcao)
  E2  confianca media do Boltz-2 (15 predicoes)         E3  delta pareado contra 3 controles embaralhados (> 0)
  E4  QC de pose da estrutura inicial                    E7  MD de 10 ns: ocupancia de S1 >= 70% a 5 A na 2a metade e ancora
                                                             igual nas duas metades; macrociclo: anel integro (C-N <= 1,5 A, omega >= 150 em todos os quadros)
  campanha de pH (quando existir): ocupancia de S1 nas outras condicoes (robustez ao pH)
Camadas (declaradas em 01/10/2026, quando 12/48 MDs ja eram conhecidas; nenhum limiar novo):
  A  cumpre todos os criterios disponiveis (S1, QC, delta > 0 e, no macrociclo, anel estrito)     -> recomendado
  B  cumpre o criterio de S1 e falha exatamente um dos demais (anel estrito, delta <= 0 ou QC)     -> candidato com ressalva
  C  nao cumpre o criterio de S1 (simulado)                                                         -> sem ancoragem confirmada em 10 ns
  P  MD ainda nao disponivel                                                                        -> pendente
Dentro da camada: ocupancia de S1 (2a metade) decrescente, depois delta (E3), depois confianca (E2). Criterio faltante (ex.: E3 ainda
nao rodou) deixa o candidato marcado `provisorio`. A MD de 10 ns verifica estabilidade da pose; nao e' estimativa de afinidade.

LEITURA DAS CAMADAS (corrigida em 01/10/2026 pelo resultado dos controles, docs/PLANO_DE_ANALISES_2026-10-01.md):
camada A/B significa "sobreviveu a todos os filtros disponiveis", NAO "deve inibir". A ocupancia de S1 e' necessaria
e nao suficiente: nos 11 complexos da calibracao, as 5 iscas embaralhadas tambem a satisfazem. A evidencia decisiva
por candidato e' a coluna `ctrl_decoy_occ5_h2`: a ocupancia do controle embaralhado DO PROPRIO candidato, no mesmo
protocolo (`run_md_controls.py`). Enquanto ela nao existir, nenhum candidato passa de provisorio.
Uso: python scripts/rank_final_candidates.py --layout server|local --data data-e2-results --out outputs/ranking_final [--lang en|pt]
"""
import argparse
import csv
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parent.parent


def jl(p):
    p = Path(p)
    return json.loads(p.read_text()) if p.exists() else {}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--layout", choices=["server", "local"], default="server")
    ap.add_argument("--data", default="data-e2-results", help="(layout local) pasta com os JSON copiados")
    ap.add_argument("--out", default="outputs/ranking_final")
    ap.add_argument("--lang", default="en", choices=["en", "pt"])
    a = ap.parse_args()
    EN = a.lang == "en"
    T = (lambda en, pt: en if EN else pt)
    D = ROOT / a.data
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)

    def P(front, what):
        if a.layout == "local":
            return {"top": D / f"top_candidates_{front}.json", "qc": D / f"pose_qc_{front}.json",
                    "ana": D / f"md10_{front}_analysis.json", "delta": D / f"delta_paired_{front}.json",
                    "L10n": D / "mdph_L_ph10_analysis.json", "L82": D / "mdph_L_ph8.2_analysis.json",
                    "M82": D / "mdph_M_ph8.2_analysis.json"}[what]
        R, O = ROOT / "data-b23-scoring/results", ROOT / "outputs"
        return {"top": R / f"top_candidates_{front}.json", "qc": O / f"pose_qc_{front}.json",
                "ana": O / f"md10_{front}/analysis_summary.json", "delta": R / f"delta_paired_{front}.json",
                "L10n": O / "mdph_L_ph10/analysis_summary.json", "L82": O / "mdph_L_ph8.2/analysis_summary.json",
                "M82": O / "mdph_M_ph8.2/analysis_summary.json"}[what]

    # controle embaralhado do proprio candidato (mesmo protocolo), quando ja simulado
    def controls(front):
        q = (ROOT / a.data / f"md10_controls_{front}_analysis.json") if a.layout == "local" else (ROOT / f"outputs/md10_controls_{front}/analysis_summary.json")
        d = jl(q)
        out = {}
        for k, v in d.items():
            if "occ_5A_h2" in v:
                out.setdefault(k.split("__ctrl_")[0], []).append(v["occ_5A_h2"])
        return out

    rows = []
    for front in "LM":
        ctrl = controls(front)
        top = jl(P(front, "top")).get("candidates", {})
        qc, ana = jl(P(front, "qc")), jl(P(front, "ana"))
        delta = {r["stem"]: r for v in jl(P(front, "delta")).values() for r in v}
        extra = {"L": [("pH 10 neutral N-term", "L10n"), ("pH 8.2", "L82")], "M": [("pH 8.2", "M82")]}[front]
        extra_data = {lab: jl(P(front, k)) for lab, k in extra}
        for key, c in top.items():
            q, m = qc.get(key, {}), ana.get(key, {})
            stem = Path(c["pdb"]).parent.name
            d = delta.get(stem, {}).get("delta")
            has_md = "occ_5A_h2" in m
            s1 = (m.get("occ_5A_h2", 0) >= 0.7 and bool(m.get("anchor_same_in_halves"))) if has_md else None
            ring = m.get("ring_intact") if (has_md and front == "M") else None
            others = {"qc_pose": q.get("qc_pass"), "delta_gt0": (d > 0) if d is not None else None}
            if front == "M":
                others["ring_strict"] = ring
            n_fail = sum(v is False for v in others.values())
            pending = [k for k, v in others.items() if v is None]
            if not has_md:
                tier = "P"
            elif s1 and n_fail == 0:
                tier = "A"
            elif s1 and n_fail == 1:
                tier = "B"
            else:
                tier = "C"
            phs = {lab: (dd.get(key, {}).get("occ_5A_h2") if dd else None) for lab, dd in extra_data.items()}
            have_ph = [v for v in phs.values() if v is not None]
            rows.append({
                "front": front, "key": key, "species": c.get("species", key.split("__")[0]), "sequence": c["sequence"], "length": len(c["sequence"]),
                "has_KR": bool(set(c["sequence"]) & set("KR")), "confidence_E2": round(c["confidence_score"], 3),
                "delta_E3": None if d is None else round(d, 3), "qc_pose": q.get("qc_pass"),
                "start_dist_Asp189_A": q.get("pep_asp189_min_A"),
                "occ5_h2": m.get("occ_5A_h2"), "anchor": m.get("anchor_aa"), "anchor_same": m.get("anchor_same_in_halves"),
                "ring_strict": ring, "ring_frac_ge150": m.get("ring_omega_frac_ge150"),
                "ph_occ": phs, "ph_robust": (all(v >= 0.7 for v in have_ph) if have_ph and has_md and (m.get("occ_5A_h2", 0) >= 0.7) else None),
                "ctrl_decoy_occ5_h2": (max(ctrl[key]) if ctrl.get(key) else None),
                "ctrl_n": len(ctrl.get(key, [])),
                "tier": tier, "provisional": bool(pending) or not has_md, "pending": pending, "failed": [k for k, v in others.items() if v is False] + ([] if s1 in (True, None) else ["s1_occupancy"]),
            })
    order = {"A": 0, "B": 1, "C": 2, "P": 3}
    rows.sort(key=lambda r: (r["front"], order[r["tier"]], -(r["occ5_h2"] or 0), -(r["delta_E3"] if r["delta_E3"] is not None else -9), -r["confidence_E2"]))
    (out / "ranking_final.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False))
    with open(out / "ranking_final.csv", "w", newline="", encoding="utf-8") as f:
        cols = ["front", "tier", "provisional", "species", "sequence", "confidence_E2", "delta_E3", "qc_pose", "occ5_h2", "anchor", "anchor_same",
                "ring_strict", "ring_frac_ge150", "ctrl_decoy_occ5_h2", "ph_robust", "has_KR", "start_dist_Asp189_A", "failed", "pending", "key"]
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({**r, "failed": ";".join(r["failed"]), "pending": ";".join(r["pending"])})
    md = [f"# {T('Final candidate peptides', 'Peptídeos candidatos finais')} (01/10/2026)\n",
          T("Tiers: A = meets all available criteria; B = meets the S1 criterion and fails exactly one other; C = no confirmed S1 anchoring in 10 ns; P = MD pending. `provisional` = a criterion not yet available (e.g., E3).\n",
            "Camadas: A = cumpre todos os critérios disponíveis; B = cumpre o critério de S1 e falha exatamente um dos demais; C = sem ancoragem de S1 confirmada em 10 ns; P = MD pendente. `provisório` = falta um critério (ex.: E3).\n")]
    for front, nm in (("L", T("Linear", "Linear")), ("M", T("Macrocycle", "Macrociclo"))):
        md += [f"\n## {nm}\n", "| tier | " + T("species", "espécie") + " | " + T("sequence", "sequência") + " | E2 | Δ E3 | QC | S1 occ (2nd half) | anchor | ring | pH | notes |",
               "|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in [x for x in rows if x["front"] == front]:
            notes = ("provisional; " if r["provisional"] else "") + ("K/R at P1 protected by Pro; " if r["has_KR"] else "") + ("fails: " + ",".join(r["failed"]) if r["failed"] else "")
            md.append(f"| {r['tier']} | {r['species']} | `{r['sequence']}` | {r['confidence_E2']} | {r['delta_E3'] if r['delta_E3'] is not None else '–'} | "
                      f"{'✓' if r['qc_pose'] else '✗' if r['qc_pose'] is False else '–'} | {r['occ5_h2'] if r['occ5_h2'] is not None else '–'} | {r['anchor'] or '–'} | "
                      f"{'✓' if r['ring_strict'] else '✗' if r['ring_strict'] is False else '–'} | {'robust' if r['ph_robust'] else '–'} | {notes} |")
    (out / "ranking_final.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    # ---- figura: matriz de evidencias
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 8, "savefig.dpi": 300})
    fig, axes = plt.subplots(1, 2, figsize=(13, 9.5), gridspec_kw={"wspace": .55})
    TC = {"A": "#2a9d8f", "B": "#e9c46a", "C": "#c8553d", "P": "#bdbdbd"}
    for ax, front, nm in zip(axes, "LM", (T("Linear front", "Frente linear"), T("Macrocycle front", "Frente macrocíclica"))):
        rr = [r for r in rows if r["front"] == front]
        cols = [T("E2 conf.", "conf. E2"), T("Δ E3", "Δ E3"), "QC", T("S1 occ.", "ocup. S1"), T("anchor=", "âncora="), T("ring", "anel"), T("pH rob.", "pH rob.")]
        M = np.full((len(rr), len(cols)), np.nan)
        txt = [[""] * len(cols) for _ in rr]
        for i, r in enumerate(rr):
            M[i, 0] = (r["confidence_E2"] - .85) / .1; txt[i][0] = f"{r['confidence_E2']:.2f}"
            if r["delta_E3"] is not None:
                M[i, 1] = 1 if r["delta_E3"] > 0 else 0; txt[i][1] = f"{r['delta_E3']:+.2f}"
            if r["qc_pose"] is not None:
                M[i, 2] = 1 if r["qc_pose"] else 0; txt[i][2] = "✓" if r["qc_pose"] else "✗"
            if r["occ5_h2"] is not None:
                M[i, 3] = r["occ5_h2"]; txt[i][3] = f"{r['occ5_h2']:.2f}"
                M[i, 4] = 1 if r["anchor_same"] else 0; txt[i][4] = (r["anchor"] or "") + (" ✓" if r["anchor_same"] else " ✗")
            if r["ring_strict"] is not None:
                M[i, 5] = 1 if r["ring_strict"] else 0.15; txt[i][5] = "✓" if r["ring_strict"] else (f"✗ {r['ring_frac_ge150']:.3f}" if r["ring_frac_ge150"] else "✗")
            if r["ph_robust"] is not None:
                M[i, 6] = 1 if r["ph_robust"] else 0; txt[i][6] = "✓" if r["ph_robust"] else "✗"
        ax.imshow(np.ma.masked_invalid(M), aspect="auto", cmap="YlGn", vmin=0, vmax=1)
        for i in range(len(rr)):
            for j in range(len(cols)):
                if txt[i][j]:
                    v = M[i, j]
                    ax.text(j, i, txt[i][j], ha="center", va="center", fontsize=6.5,
                            color="white" if (not np.isnan(v) and v > 0.55) else "black")
        ax.set_xticks(range(len(cols))); ax.set_xticklabels(cols, rotation=40, ha="right")
        ax.set_yticks(range(len(rr)))
        ax.set_yticklabels([f"{r['tier']}  {r['species'][0]}. {r['species'][1:]}  {r['sequence']}" for r in rr], fontsize=6.5)
        for lab, r in zip(ax.get_yticklabels(), rr):
            lab.set_color(TC[r["tier"]] if r["tier"] != "P" else "gray")
            lab.set_fontweight("bold" if r["tier"] in "AB" else "normal")
        ax.set_title(nm, fontsize=10)
    fig.suptitle(T("Evidence matrix of the 48 final candidates (blank = not yet available; A/B/C/P = tiers; provisional while E3 and the MDs run)",
                   "Matriz de evidências dos 48 candidatos finais (vazio = ainda não disponível; A/B/C/P = camadas; provisório enquanto E3 e as MDs rodam)"), fontsize=9)
    fig.subplots_adjust(top=.93, left=.2, right=.97, bottom=.08)
    name = "Figure13_final_candidates" if EN else "fig13_candidatos_finais"
    fig.savefig(out / f"{name}.png"); fig.savefig(out / f"{name}.pdf")
    from PIL import Image
    Image.open(out / f"{name}.png").convert("RGB").save(out / f"{name}.tif", compression="tiff_lzw", dpi=(300, 300))
    cnt = {f: {t: sum(1 for r in rows if r["front"] == f and r["tier"] == t) for t in "ABCP"} for f in "LM"}
    print(json.dumps(cnt))


if __name__ == "__main__":
    main()

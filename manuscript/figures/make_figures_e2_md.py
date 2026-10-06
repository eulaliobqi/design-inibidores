"""Figuras dos resultados E2-E7 (re-pontuacao 5x3, QC de pose, MD de triagem 10 ns, CHARMM36). Uso:
    python make_figures_e2_md.py DATA_DIR OUT_DIR {en|pt}
DATA_DIR = data-e2-results/ (copias de outputs/ do servidor): b23_boltz2_E2_{L,M}_scores.json,
top_candidates_{L,M}.json, pose_qc_{L,M}.json, md10_{L,M}_summary.json, md10_{L,M}_analysis.json e
md_ts/{L,M}__{especie}__r{k}.npz (series temporais gravadas por analyze_md_top_candidates.py).
Todos os numeros vem dos arquivos; nada e digitado a mao. Funciona com dados parciais (E6 em curso):
reexecutar quando novas MDs terminarem.
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr

from frontiers_style import apply_style, mm_figsize, save_journal

D, O, LG = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
O.mkdir(parents=True, exist_ok=True)
EN = LG == "en"
apply_style()   # 8 pt e 180 mm: ver frontiers_style.py
CF = {"L": "#457b9d", "M": "#2a9d8f"}


def T(en, pt):
    return en if EN else pt


FNAME = {"L": T("linear", "linear"), "M": T("macrocycle", "macrociclo")}
SP = ["Sfrugiperda", "Slitura", "Onubilalis", "Dsaccharalis", "Cincludens", "Hvirescens", "Pxylostella", "Agemmatalis"]
SHORT = {s: s[0] + ". " + s[1:] for s in SP}


def load(n):
    p = D / n
    return json.load(open(p, encoding="utf-8")) if p.exists() else None


def letters(axs, dx=-0.22, dy=1.02):
    """Letras dos paineis fora da area de desenho. Convencao de revista: o painel e' identificado
    pela letra e descrito na legenda, nao por um titulo dentro da figura."""
    for a, L in zip(axs, "ABCD"):
        a.text(dx, dy, L, transform=a.transAxes, fontweight="bold", va="bottom", ha="left")


def save(fig, en, pt):
    name = T(en, pt)
    rep = save_journal(fig, O / name)
    plt.close(fig)
    return rep


# ---- Figura 9: re-pontuacao E2 (5 amostras x 3 sementes) ---------------------------------------
def fig_e2():
    E2 = {F: load(f"b23_boltz2_E2_{F}_scores.json") for F in "LM"}
    if not all(E2.values()):
        return None
    rows = {F: [r for sp in SP for r in E2[F][sp]] for F in "LM"}
    fig, ax = plt.subplots(1, 3, figsize=mm_figsize("double", 78),
                           gridspec_kw={"width_ratios": [1, 1.25, 1]}, layout="constrained")
    # a) confianca E1 (1 amostra) x E2 (media de 15)
    stats = {}
    for F in "LM":
        x = np.array([r["confidence_E1"] for r in rows[F]]); y = np.array([r["confidence_score"] for r in rows[F]])
        ax[0].scatter(x, y, s=14, alpha=.65, color=CF[F], edgecolor="none", label=FNAME[F])
        stats[F] = (spearmanr(x, y)[0], float((y - x).mean()), len(x))
    ax[0].plot([.8, 1], [.8, 1], ls=":", c="gray", lw=1)
    ax[0].set_xlim(.8, 1); ax[0].set_ylim(.8, 1)
    ax[0].set_xlabel(T("E1 confidence (1 sample)", "Confiança E1 (1 amostra)"))
    ax[0].set_ylabel(T("E2 confidence (mean of 15)", "Confiança E2 (média de 15)"))
    ax[0].legend(frameon=False, loc="upper left")
    ax[0].text(.995, .815, "\n".join(f"{FNAME[F]}: ρ = {stats[F][0]:.2f}, Δ = {stats[F][1]:+.3f}" for F in "LM"), ha="right")
    
    # b) por especie: media E2 de cada candidato, L x M
    for i, sp in enumerate(SP):
        for F, off in (("L", -.17), ("M", .17)):
            v = [r["confidence_score"] for r in E2[F][sp]]
            ax[1].scatter(np.full(len(v), i + off) + np.linspace(-.06, .06, len(v)), v, s=11, alpha=.7, color=CF[F], edgecolor="none")
            ax[1].hlines(np.mean(v), i + off - .13, i + off + .13, color="k", lw=1.2)
    ax[1].set_xticks(range(len(SP))); ax[1].set_xticklabels([SHORT[s] for s in SP], rotation=40, ha="right", style="italic")
    ax[1].set_ylabel(T("E2 confidence", "Confiança E2"))
    
    # c) fracao das 15 amostras que passam o QC de pose
    for F in "LM":
        q = np.array([r["n_samples_qc_pass"] / r["n_samples"] for r in rows[F]])
        ax[2].hist(q, bins=np.linspace(0, 1.0001, 16), alpha=.6, color=CF[F], label=f"{FNAME[F]} (n = {len(q)})")
    ax[2].set_xlabel(T("fraction passing pose QC", "fração aprovada no QC"))
    ax[2].set_ylabel(T("candidates", "candidatos")); ax[2].legend(frameon=False, loc="upper left")
    
    letters(ax)
    save(fig, "Figure9_E2_rescoring", "fig9_reescore_e2")
    return {F: {"rho": stats[F][0], "delta": stats[F][1], "n": stats[F][2],
                "qc_mean": float(np.mean([r["n_samples_qc_pass"] / r["n_samples"] for r in rows[F]]))} for F in "LM"}


# ---- Figura 10: top-3 selecionados e QC de pose ----------------------------------------------------
def fig_top3():
    TC = {F: load(f"top_candidates_{F}.json") for F in "LM"}
    QC = {F: load(f"pose_qc_{F}.json") for F in "LM"}
    if not all(TC.values()) or not all(QC.values()):
        return None
    fig, ax = plt.subplots(1, 2, figsize=mm_figsize("double", 76), layout="constrained")
    for F, off in (("L", -.18), ("M", .18)):
        for i, sp in enumerate(SP):
            ks = [f"{sp}__r{k}" for k in (1, 2, 3)]
            c = [TC[F]["candidates"][k]["confidence_score"] for k in ks]
            d = [QC[F][k]["pep_asp189_min_A"] for k in ks]
            xs = np.full(3, i + off) + np.array([-.07, 0, .07])
            ax[0].scatter(xs, c, s=18, color=CF[F], edgecolor="none", label=FNAME[F] if i == 0 else None)
            ax[1].scatter(xs, d, s=18, color=CF[F], edgecolor="none")
    for a in ax:
        a.set_xticks(range(len(SP))); a.set_xticklabels([SHORT[s] for s in SP], rotation=40, ha="right", style="italic")
    ax[0].set_ylabel(T("E2 confidence", "Confiança E2")); ax[0].legend(frameon=False)
    
    ax[1].axhline(5, ls="--", c="gray", lw=1)
    ax[1].set_ylabel(T("peptide–Asp189 distance (Å)", "distância peptídeo–Asp189 (Å)"))
    
    npass = sum(v["qc_pass"] for F in "LM" for v in QC[F].values()); ntot = sum(len(QC[F]) for F in "LM")
    ax[1].text(0.01, 0.97, f"QC: {npass}/{ntot}", transform=ax[1].transAxes, va="top")
    letters(ax)
    save(fig, "Figure10_top3_pose", "fig10_top3_pose")
    return {"qc_pass": npass, "qc_total": ntot}


# ---- Figura 11: MD de triagem 10 ns ------------------------------------------------------------------
def fig_md():
    AN = {F: load(f"md10_{F}_analysis.json") or {} for F in "LM"}
    ok = {F: {k: v for k, v in AN[F].items() if "error" not in v and "occ_5A_h2" in v} for F in "LM"}
    if not any(ok.values()):
        return None
    fig = plt.figure(figsize=mm_figsize("double", 185), layout="constrained")
    gs = fig.add_gridspec(3, 3, height_ratios=[1, .75, .75])
    a1, a2, a3 = (fig.add_subplot(gs[0, i]) for i in range(3))
    # (a,b) A. gemmatalis: distancia ancora-Asp189 e RMSD local, por tempo
    ls = {"r1": "-", "r2": "--", "r3": ":"}
    for F in "LM":
        for k in (1, 2, 3):
            p = D / "md_ts" / f"{F}__Agemmatalis__r{k}.npz"
            if not p.exists():
                continue
            z = np.load(p)
            da = z["d_res_asp"][:, z["d_res_asp"].mean(axis=0).argmin()]
            seq = AN[F].get(f"Agemmatalis__r{k}", {}).get("sequence", "")
            a1.plot(z["t_ns"], da / 1.0, ls[f"r{k}"], c=CF[F], lw=1.3, label=f"{F} r{k} {seq}")
            a2.plot(z["t_ns"], z["rmsd_local_nm"], ls[f"r{k}"], c=CF[F], lw=1.3)
    a1.axhline(5, ls="--", c="gray", lw=.8)
    a1.set_xlabel(T("time (ns)", "tempo (ns)")); a1.set_ylabel(T("anchor–Asp189 (Å)", "âncora–Asp189 (Å)"))

    a1.legend(frameon=False, ncol=1, loc="upper left", handlelength=1.4)
    a2.set_xlabel(T("time (ns)", "tempo (ns)")); a2.set_ylabel(T("peptide RMSD, Cα (nm)", "RMSD do peptídeo, Cα (nm)"))

    # (c) ocupancia do S1 a 5 A: 1a x 2a metade
    for F in "LM":
        for k, v in ok[F].items():
            mk = "o" if v["passes_screen"] else "x"
            a3.scatter(v["occ_5A_h1"], v["occ_5A_h2"], s=34, marker=mk, color=CF[F], alpha=.85, label=None)
    a3.plot([0, 1], [0, 1], ls=":", c="gray", lw=1); a3.axhline(.7, ls="--", c="gray", lw=.8)
    a3.text(.02, .72, "70%", color="gray")
    a3.set_xlim(-.03, 1.03); a3.set_ylim(-.03, 1.03)
    a3.set_xlabel(T("S1 occupancy, first half", "ocupância de S1, 1ª metade"))
    a3.set_ylabel(T("S1 occupancy, second half", "ocupância de S1, 2ª metade"))

    for F in "LM":
        a3.scatter([], [], color=CF[F], label=FNAME[F])
    a3.legend(frameon=False, loc="lower right")
    # (d) painel inferior: uma linha por frente (ocupancia 5 A 2a metade + Ser195 + qualquer contato)
    from matplotlib.patches import Patch
    bs = [fig.add_subplot(gs[1 + i, :]) for i in range(2)]
    for b, F in zip(bs, "LM"):
        items = [(F, k, v) for k, v in sorted(ok[F].items())]
        x = np.arange(len(items)); w = .27
        b.bar(x - w, [v["occ_5A_h2"] for _, _, v in items], w, color=CF[F])
        b.bar(x, [v["ser195_contact_frac_4.5A"] for _, _, v in items], w, color=CF[F], alpha=.55, hatch="//")
        b.bar(x + w, [v["contact_any_frac_4.5A"] for _, _, v in items], w, color=CF[F], alpha=.3, hatch="..")
        b.axhline(.7, ls="--", c="gray", lw=.8)
        b.set_xticks(x)
        b.set_xticklabels([SHORT[k.split("__")[0]].replace(". ", ".") + " " + v["sequence"] + ("" if F == "L" or "ring_intact" not in v else (" ✓" if v["ring_intact"] else " ✗")) for _, k, v in items], rotation=90, ha="center", fontsize=6)
        b.set_ylim(0, 1.05); b.set_xlim(-.7, len(items) - .3)
        b.set_ylabel(FNAME[F] + "\n" + T("fraction of frames", "fração dos quadros"))
    bs[0].legend(handles=[Patch(fc="gray", label=T("S1 occupancy ≤5 Å, 2nd half", "ocupância do S1 ≤5 Å, 2ª metade")),
                      Patch(fc="gray", alpha=.55, hatch="//", label=T("Ser195 contact ≤4.5 Å", "contato com Ser195 ≤4,5 Å")),
                      Patch(fc="gray", alpha=.3, hatch="..", label=T("any receptor contact ≤4.5 Å", "qualquer contato ≤4,5 Å"))],
             frameon=False, ncol=3, loc="lower center", bbox_to_anchor=(.5, 1.0), fontsize=7)
    b = bs[0]

    letters([a1, a2, a3, b])
    save(fig, "Figure11_MD_screen_10ns", "fig11_md_triagem_10ns")
    return {F: {"n_done": len(ok[F]), "n_pass": sum(v["passes_screen"] for v in ok[F].values())} for F in "LM"}


# ---- Figura S2: integridade do anel nas MDs ciclicas reais (CHARMM36) -----------------------------
def fig_s2_ring():
    AN = load("md10_M_analysis.json") or {}
    keys = [k for k, v in sorted(AN.items()) if "error" not in v and (D / "md_ts" / f"M__{k}.npz").exists()]
    if not keys:
        return None
    fig, ax = plt.subplots(1, 3, figsize=mm_figsize("double", 68), layout="constrained")
    stats = {}
    cols = plt.cm.tab10(np.arange(len(keys)))
    for c, k in zip(cols, keys):
        z = np.load(D / "md_ts" / f"M__{k}.npz")
        om = np.abs(z["ring_omega_deg"]); cn = z["ring_CN_A"]
        lab = f"{k.split('__')[0][0]}. {k.split('__')[0][1:]} r{k[-1]} {AN[k]['sequence']}"
        ax[0].plot(z["t_ns"], cn, lw=.8, color=c, label=lab)
        ax[1].plot(z["t_ns"], om, lw=.8, color=c)
        ax[2].hist(om, bins=np.linspace(130, 180, 51), histtype="step", color=c, lw=1.3)
        stats[k] = {"cn_max": float(cn.max()), "omega_min": float(om.min()), "frac_ge150": float((om >= 150).mean())}
    ax[0].axhline(1.5, ls="--", c="gray", lw=.8); ax[0].set_ylim(1.2, 1.6)
    ax[0].set_xlabel(T("time (ns)", "tempo (ns)")); ax[0].set_ylabel(T("closing C–N distance (Å)", "distância C–N de fechamento (Å)"))
    ax[0].legend(frameon=False, fontsize=7, loc="upper left")
    ax[1].axhline(150, ls="--", c="gray", lw=.8)
    ax[1].set_xlabel(T("time (ns)", "tempo (ns)")); ax[1].set_ylabel(T("|closing ω| (°)", "|ω de fechamento| (°)")); ax[1].set_ylim(135, 182)
    ax[2].axvline(150, ls="--", c="gray", lw=.8)
    ax[2].set_xlabel(T("|closing ω| (°)", "|ω de fechamento| (°)")); ax[2].set_ylabel(T("frames", "quadros"))
    fig.suptitle(T("Ring integrity in the cyclic CHARMM36 simulations (dashed: pre-registered limits, C–N ≤ 1.5 Å and ω ≥ 150°)",
                   "Integridade do anel nas simulações cíclicas com CHARMM36 (tracejado: limites pré-registrados, C–N ≤ 1,5 Å e ω ≥ 150°)"), fontsize=9)
    save(fig, "FigureS2_cyclic_ring_CHARMM36", "figS2_anel_ciclico_charmm36")
    return stats


def fig_controls():
    """Figura 13: candidatos x controles embaralhados (10 ns, mesmo protocolo). Funciona com dados parciais."""
    AN = {F: load(f"md10_{F}_analysis.json") or {} for F in "LM"}
    CT = {F: load(f"md10_controls_{F}_analysis.json") or {} for F in "LM"}
    pairs = []
    for F in "LM":
        for ck, cv in CT[F].items():
            c = AN[F].get(ck.split("__ctrl_")[0])
            if c and "occ_5A_h2" in c and "occ_5A_h2" in cv:
                pairs.append((F, ck.split("__ctrl_")[0], c, cv))
    if not pairs:
        return None
    fig, (a, b) = plt.subplots(1, 2, figsize=mm_figsize("double", 80), layout="constrained")
    ys = sorted(((cv["occ_5A_h2"], j) for j, (_, _, _, cv) in enumerate(pairs)))
    ypos, last = {}, -9
    for y, j in ys:  # rotulos a direita com espacamento minimo, para nao se sobreporem
        last = max(y, last + .075)
        ypos[j] = last
    for j, (F, key, c, cv) in enumerate(pairs):
        a.plot([0, 1], [c["occ_5A_h2"], cv["occ_5A_h2"]], "-o", c=CF[F], lw=1.3, ms=4)
        a.text(1.05, ypos[j], f'{c["sequence"]} → {cv["sequence"]}', va="center", fontsize=6.5)
    a.axhline(.7, ls="--", c="gray", lw=.8)
    a.set_xticks([0, 1]); a.set_xticklabels([T("candidate", "candidato"), T("shuffled control", "controle embaralhado")])
    a.set_xlim(-.15, 2.0); a.set_ylim(-.05, 1.3)
    a.set_ylabel(T("S1 occupancy at 5 Å, second half", "ocupância de S1 a 5 Å, 2ª metade"))
    for F in "LM":
        a.plot([], [], "-o", c=CF[F], ms=4, label=FNAME[F])
    a.legend(frameon=False, loc="upper left", ncol=2)
    for F in "LM":
        for k, v in AN[F].items():
            if "occ_5A_h2" in v:
                b.scatter(v["d_anchor_asp_ini_A"], v["occ_5A_h2"], s=16, color="#bbbbbb", edgecolor="none", zorder=1)
    b.scatter([], [], s=16, color="#bbbbbb", label=T("candidates (48)", "candidatos (48)"))
    seen = {}
    for F, key, c, cv in pairs:
        pt = (round(cv["d_anchor_asp_ini_A"], 1), round(cv["occ_5A_h2"], 1))
        dx = .18 * seen.get(pt, 0); seen[pt] = seen.get(pt, 0) + 1  # pontos coincidentes: leve deslocamento horizontal
        b.scatter(cv["d_anchor_asp_ini_A"] + dx, cv["occ_5A_h2"], s=46, marker="D", color=CF[F], edgecolor="k", lw=.6, zorder=3)
    b.scatter([], [], s=46, marker="D", color="w", edgecolor="k", lw=.6, label=T("shuffled controls", "controles embaralhados"))
    b.axhline(.7, ls="--", c="gray", lw=.8)
    b.set_xlabel(T("initial anchor–Asp189 distance (Å)", "distância inicial âncora–Asp189 (Å)"))
    b.set_ylabel(T("S1 occupancy at 5 Å, second half", "ocupância de S1 a 5 Å, 2ª metade"))
    b.legend(frameon=False, loc="upper right")
    letters([a, b], dx=-0.16)
    save(fig, "Figure13_shuffled_controls", "fig13_controles_embaralhados")
    return {"n_pairs": len(pairs)}


def fig_negctrl():
    """Figura 14: controle negativo por troca da ancora (Asp, Leu) frente ao candidato e ao controle embaralhado.
    Funciona com dados parciais: so desenha os candidatos cujas duas variantes terminaram."""
    AN = {F: load(f"md10_{F}_analysis.json") or {} for F in "LM"}
    CT = {F: load(f"md10_controls_{F}_analysis.json") or {} for F in "LM"}
    NG = {F: load(f"md10_negctrl_{F}_analysis.json") or {} for F in "LM"}
    rows = []
    for F in "LM":
        for k, c in AN[F].items():
            neg = {v: NG[F].get(f"{k}__neg_{v}") for v in ("ASP", "LEU")}
            ctl = next((cv for ck, cv in CT[F].items() if ck.startswith(k + "__ctrl_")), None)
            if all(neg.values()) and ctl and "occ_5A_h2" in c:
                rows.append((F, k, c, ctl, neg))
    if not rows:
        return None
    cats = [T("candidate", "candidato"), T("shuffled", "embaralhado"), "Asp", "Leu"]
    fig, (a, b) = plt.subplots(1, 2, figsize=mm_figsize("double", 95), layout="constrained")
    seen_f = {}
    handles = []
    for j, (F, k, c, ctl, neg) in enumerate(rows):
        n = seen_f.get(F, 0); seen_f[F] = n + 1
        mk, ls = (("o", "-"), ("s", "--"))[n % 2]
        recs = [c, ctl, neg["ASP"], neg["LEU"]]
        off = (j - (len(rows) - 1) / 2) * .1
        xs = np.arange(4) + off
        a.plot(xs, [r["occ_5A_h2"] for r in recs], ls, marker=mk, c=CF[F], lw=1.3, ms=4)
        h, = b.plot(xs, [r["d_anchor_asp_fim_A"] for r in recs], ls, marker=mk, c=CF[F], lw=1.3, ms=4,
                    label=f'{c["sequence"]} ({FNAME[F]})')
        handles.append(h)
        b.plot(xs, [r["d_anchor_asp_ini_A"] for r in recs], mk, mfc="w", c=CF[F], ms=4, lw=0)
    a.axhline(.7, ls="--", c="gray", lw=.8)
    b.axhline(5, ls="--", c="gray", lw=.8)
    for ax_ in (a, b):
        ax_.set_xticks(range(4)); ax_.set_xticklabels(cats)
        ax_.set_xlim(-.4, 3.4)
    a.set_ylim(-.05, 1.1)
    a.set_ylabel(T("S1 occupancy at 5 Å, second half", "ocupância de S1 a 5 Å, 2ª metade"))
    b.set_ylabel(T("anchor–Asp189 distance (Å)", "distância âncora–Asp189 (Å)"))
    h1, = b.plot([], [], "o", mfc="w", c="k", ms=4, lw=0, label=T("initial window (open)", "janela inicial (vazado)"))
    h2, = b.plot([], [], "o", c="k", ms=4, lw=0, label=T("final window (filled)", "janela final (cheio)"))
    fig.legend(handles=handles + [h1, h2], loc="outside lower center", ncol=3, frameon=False, fontsize=7.5)
    letters([a, b], dx=-0.16)
    save(fig, "Figure14_negative_control", "fig14_controle_negativo")
    return {"n_candidates": len(rows), "seqs": [r[2]["sequence"] for r in rows]}


if __name__ == "__main__":
    print("fig9 ", fig_e2())
    print("fig10", fig_top3())
    print("fig11", fig_md())
    print("figS2", fig_s2_ring())
    # Figs 13 e 14 (controles em MD) retiradas do artigo em 05/10/2026 (ver docs/ESTADO_2026-10-05.md);
    # as funcoes fig_controls() e fig_negctrl() ficam para consulta, as saidas estao em figures/_retiradas/.
    from PIL import Image
    for f in O.glob("*.png"):
        if f.name.startswith(("fig9", "fig10", "fig11", "figS2_anel", "fig13", "Figure9", "Figure10", "Figure11", "Figure13", "Figure14", "fig14", "FigureS2_cyclic_ring")):
            Image.open(f).convert("RGB").save(f.with_suffix(".tif"), compression="tiff_lzw", dpi=(300, 300))

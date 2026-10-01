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

D, O, LG = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
O.mkdir(parents=True, exist_ok=True)
EN = LG == "en"
plt.rcParams.update({"font.size": 10, "savefig.dpi": 300, "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 150})
CF = {"L": "#457b9d", "M": "#2a9d8f"}


def T(en, pt):
    return en if EN else pt


FNAME = {"L": T("linear", "linear"), "M": T("macrocycle", "macrociclo")}
SP = ["Sfrugiperda", "Slitura", "Onubilalis", "Dsaccharalis", "Cincludens", "Hvirescens", "Pxylostella", "Agemmatalis"]
SHORT = {s: s[0] + ". " + s[1:] for s in SP}


def load(n):
    p = D / n
    return json.load(open(p, encoding="utf-8")) if p.exists() else None


def letters(axs):
    for a, L in zip(axs, "ABCD"):
        a.text(-0.1, 1.06, L, transform=a.transAxes, fontsize=12, fontweight="bold", va="bottom")


def save(fig, en, pt):
    name = T(en, pt)
    fig.savefig(O / f"{name}.png"); fig.savefig(O / f"{name}.pdf"); plt.close(fig)


# ---- Figura 9: re-pontuacao E2 (5 amostras x 3 sementes) ---------------------------------------
def fig_e2():
    E2 = {F: load(f"b23_boltz2_E2_{F}_scores.json") for F in "LM"}
    if not all(E2.values()):
        return None
    rows = {F: [r for sp in SP for r in E2[F][sp]] for F in "LM"}
    fig, ax = plt.subplots(1, 3, figsize=(12.5, 4.1), gridspec_kw={"width_ratios": [1, 1.25, 1]})
    # a) confianca E1 (1 amostra) x E2 (media de 15)
    stats = {}
    for F in "LM":
        x = np.array([r["confidence_E1"] for r in rows[F]]); y = np.array([r["confidence_score"] for r in rows[F]])
        ax[0].scatter(x, y, s=14, alpha=.65, color=CF[F], edgecolor="none", label=FNAME[F])
        stats[F] = (spearmanr(x, y)[0], float((y - x).mean()), len(x))
    ax[0].plot([.8, 1], [.8, 1], ls=":", c="gray", lw=1)
    ax[0].set_xlim(.8, 1); ax[0].set_ylim(.8, 1)
    ax[0].set_xlabel(T("Boltz-2 confidence, E1 (1 sample)", "Confiança do Boltz-2, E1 (1 amostra)"))
    ax[0].set_ylabel(T("Boltz-2 confidence, E2 (mean of 15)", "Confiança do Boltz-2, E2 (média de 15)"))
    ax[0].legend(frameon=False, fontsize=8, loc="upper left")
    ax[0].text(.995, .815, "\n".join(f"{FNAME[F]}: ρ = {stats[F][0]:.2f}, Δ = {stats[F][1]:+.3f}" for F in "LM"), ha="right", fontsize=8)
    ax[0].set_title(T("Top-10 per species re-scored", "Top-10 por espécie re-pontuados"), fontsize=10)
    # b) por especie: media E2 de cada candidato, L x M
    for i, sp in enumerate(SP):
        for F, off in (("L", -.17), ("M", .17)):
            v = [r["confidence_score"] for r in E2[F][sp]]
            ax[1].scatter(np.full(len(v), i + off) + np.linspace(-.06, .06, len(v)), v, s=11, alpha=.7, color=CF[F], edgecolor="none")
            ax[1].hlines(np.mean(v), i + off - .13, i + off + .13, color="k", lw=1.2)
    ax[1].set_xticks(range(len(SP))); ax[1].set_xticklabels([SHORT[s] for s in SP], rotation=35, ha="right", style="italic")
    ax[1].set_ylabel(T("Boltz-2 confidence (E2)", "Confiança do Boltz-2 (E2)"))
    ax[1].set_title(T("By species (bar = mean; left linear, right macrocycle)", "Por espécie (barra = média; esq. linear, dir. macrociclo)"), fontsize=10)
    # c) fracao das 15 amostras que passam o QC de pose
    for F in "LM":
        q = np.array([r["n_samples_qc_pass"] / r["n_samples"] for r in rows[F]])
        ax[2].hist(q, bins=np.linspace(0, 1.0001, 16), alpha=.6, color=CF[F], label=f"{FNAME[F]} (n = {len(q)})")
    ax[2].set_xlabel(T("fraction of the 15 samples passing pose QC", "fração das 15 amostras que passam o QC de pose"))
    ax[2].set_ylabel(T("candidates", "candidatos")); ax[2].legend(frameon=False, fontsize=8, loc="upper left")
    ax[2].set_title(T("Pose QC within candidates", "QC de pose dentro dos candidatos"), fontsize=10)
    letters(ax)
    fig.tight_layout()
    save(fig, "Figure9_E2_rescoring", "fig9_reescore_e2")
    return {F: {"rho": stats[F][0], "delta": stats[F][1], "n": stats[F][2],
                "qc_mean": float(np.mean([r["n_samples_qc_pass"] / r["n_samples"] for r in rows[F]]))} for F in "LM"}


# ---- Figura 10: top-3 selecionados e QC de pose ----------------------------------------------------
def fig_top3():
    TC = {F: load(f"top_candidates_{F}.json") for F in "LM"}
    QC = {F: load(f"pose_qc_{F}.json") for F in "LM"}
    if not all(TC.values()) or not all(QC.values()):
        return None
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.1))
    for F, off in (("L", -.18), ("M", .18)):
        for i, sp in enumerate(SP):
            ks = [f"{sp}__r{k}" for k in (1, 2, 3)]
            c = [TC[F]["candidates"][k]["confidence_score"] for k in ks]
            d = [QC[F][k]["pep_asp189_min_A"] for k in ks]
            xs = np.full(3, i + off) + np.array([-.07, 0, .07])
            ax[0].scatter(xs, c, s=18, color=CF[F], edgecolor="none", label=FNAME[F] if i == 0 else None)
            ax[1].scatter(xs, d, s=18, color=CF[F], edgecolor="none")
    for a in ax:
        a.set_xticks(range(len(SP))); a.set_xticklabels([SHORT[s] for s in SP], rotation=35, ha="right", style="italic")
    ax[0].set_ylabel(T("Boltz-2 confidence (E2)", "Confiança do Boltz-2 (E2)")); ax[0].legend(frameon=False, fontsize=8)
    ax[0].set_title(T("Top-3 per species sent to MD", "Top-3 por espécie enviados à MD"), fontsize=10)
    ax[1].axhline(5, ls="--", c="gray", lw=1); ax[1].text(7.6, 5.15, T("5 Å cut", "corte 5 Å"), ha="right", fontsize=8, color="gray")
    ax[1].set_ylabel(T("min. distance, peptide to Asp189 carboxylate (Å)", "distância mín. peptídeo–carboxilato do Asp189 (Å)"))
    ax[1].set_title(T("Starting pose (all 48 pass pose QC)", "Pose inicial (as 48 passam o QC de pose)"), fontsize=10)
    npass = sum(v["qc_pass"] for F in "LM" for v in QC[F].values()); ntot = sum(len(QC[F]) for F in "LM")
    ax[1].text(0.01, 0.97, f"QC: {npass}/{ntot}", transform=ax[1].transAxes, va="top", fontsize=8)
    letters(ax)
    fig.tight_layout()
    save(fig, "Figure10_top3_pose", "fig10_top3_pose")
    return {"qc_pass": npass, "qc_total": ntot}


# ---- Figura 11: MD de triagem 10 ns ------------------------------------------------------------------
def fig_md():
    AN = {F: load(f"md10_{F}_analysis.json") or {} for F in "LM"}
    ok = {F: {k: v for k, v in AN[F].items() if "error" not in v and "occ_5A_h2" in v} for F in "LM"}
    if not any(ok.values()):
        return None
    fig = plt.figure(figsize=(12.5, 7.6))
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 1.05])
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
    a1.set_xlabel(T("time (ns)", "tempo (ns)")); a1.set_ylabel(T("anchor residue to Asp189 carboxylate (Å)", "resíduo-âncora ao carboxilato do Asp189 (Å)"))
    a1.set_title(T("A. gemmatalis, top-3", "A. gemmatalis, top-3"), fontsize=10, style="italic")
    a1.legend(frameon=False, fontsize=7, ncol=1, loc="upper left")
    a2.set_xlabel(T("time (ns)", "tempo (ns)")); a2.set_ylabel(T("local peptide RMSD, Cα (nm)", "RMSD local do peptídeo, Cα (nm)"))
    a2.set_title(T("Peptide pose drift (receptor-aligned)", "Deriva da pose do peptídeo (receptor alinhado)"), fontsize=10)
    # (c) ocupancia do S1 a 5 A: 1a x 2a metade
    for F in "LM":
        for k, v in ok[F].items():
            mk = "o" if v["passes_screen"] else "x"
            a3.scatter(v["occ_5A_h1"], v["occ_5A_h2"], s=34, marker=mk, color=CF[F], alpha=.85, label=None)
    a3.plot([0, 1], [0, 1], ls=":", c="gray", lw=1); a3.axhline(.7, ls="--", c="gray", lw=.8)
    a3.text(.02, .72, T("70% (pre-registered)", "70% (pré-registrado)"), fontsize=7, color="gray")
    a3.set_xlim(-.03, 1.03); a3.set_ylim(-.03, 1.03)
    a3.set_xlabel(T("S1 occupancy ≤5 Å, first half (0–5 ns)", "ocupância do S1 ≤5 Å, 1ª metade (0–5 ns)"))
    a3.set_ylabel(T("S1 occupancy ≤5 Å, second half (5–10 ns)", "ocupância do S1 ≤5 Å, 2ª metade (5–10 ns)"))
    a3.set_title(T("All finished MDs (o = passes, x = fails)", "Todas as MDs concluídas (o = passa, x = não passa)"), fontsize=10)
    for F in "LM":
        a3.scatter([], [], color=CF[F], label=FNAME[F])
    a3.legend(frameon=False, fontsize=8, loc="lower right")
    # (d) painel inferior: tabela-grafico por simulacao (ocupancia 5 A 2a metade + Ser195/His57 + RMSD local)
    b = fig.add_subplot(gs[1, :])
    items = [(F, k, v) for F in "LM" for k, v in sorted(ok[F].items())]
    x = np.arange(len(items)); w = .27
    b.bar(x - w, [v["occ_5A_h2"] for _, _, v in items], w, color=[CF[F] for F, _, _ in items], label=T("S1 occupancy ≤5 Å, 2nd half", "ocupância do S1 ≤5 Å, 2ª metade"))
    b.bar(x, [v["ser195_contact_frac_4.5A"] for _, _, v in items], w, color=[CF[F] for F, _, _ in items], alpha=.55, hatch="//", label=T("Ser195 contact ≤4.5 Å", "contato com Ser195 ≤4,5 Å"))
    b.bar(x + w, [v["contact_any_frac_4.5A"] for _, _, v in items], w, color=[CF[F] for F, _, _ in items], alpha=.3, hatch="..", label=T("any receptor contact ≤4.5 Å", "qualquer contato com o receptor ≤4,5 Å"))
    b.axhline(.7, ls="--", c="gray", lw=.8)
    b.set_xticks(x); b.set_xticklabels([f"{F} {k.replace('__', ' ')}\n{v['sequence']}" + ("" if F == "L" or "ring_intact" not in v else ("\nring ✓" if v["ring_intact"] else "\nring ✗")) for F, k, v in items], rotation=60, ha="right", fontsize=6.5)
    b.set_ylim(0, 1.25); b.set_ylabel(T("fraction of frames", "fração dos quadros"))
    from matplotlib.patches import Patch
    b.legend(handles=[Patch(fc="gray", label=T("S1 occupancy ≤5 Å, 2nd half", "ocupância do S1 ≤5 Å, 2ª metade")),
                      Patch(fc="gray", alpha=.55, hatch="//", label=T("Ser195 contact ≤4.5 Å", "contato com Ser195 ≤4,5 Å")),
                      Patch(fc="gray", alpha=.3, hatch="..", label=T("any receptor contact ≤4.5 Å", "qualquer contato ≤4,5 Å"))],
             frameon=False, fontsize=8, ncol=3, loc="upper center", bbox_to_anchor=(.5, 1.0))
    b.set_title(T("Per simulation (blue = linear, green = macrocycle); 10 ns × 1 replicate, descriptive screen only", "Por simulação (azul = linear, verde = macrociclo); 10 ns × 1 réplica, triagem descritiva"), fontsize=10)
    letters([a1, a2, a3, b])
    fig.tight_layout()
    save(fig, "Figure11_MD_screen_10ns", "fig11_md_triagem_10ns")
    return {F: {"n_done": len(ok[F]), "n_pass": sum(v["passes_screen"] for v in ok[F].values())} for F in "LM"}


# ---- Figura S2: integridade do anel nas MDs ciclicas reais (CHARMM36) -----------------------------
def fig_s2_ring():
    AN = load("md10_M_analysis.json") or {}
    keys = [k for k, v in sorted(AN.items()) if "error" not in v and (D / "md_ts" / f"M__{k}.npz").exists()]
    if not keys:
        return None
    fig, ax = plt.subplots(1, 3, figsize=(12.5, 3.6))
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
    fig.tight_layout()
    save(fig, "FigureS2_cyclic_ring_CHARMM36", "figS2_anel_ciclico_charmm36")
    return stats


if __name__ == "__main__":
    print("fig9 ", fig_e2())
    print("fig10", fig_top3())
    print("fig11", fig_md())
    print("figS2", fig_s2_ring())
    from PIL import Image
    for f in O.glob("*.png"):
        if f.name.startswith(("fig9", "fig10", "fig11", "figS2_anel", "Figure9", "Figure10", "Figure11", "FigureS2_cyclic_ring")):
            Image.open(f).convert("RGB").save(f.with_suffix(".tif"), compression="tiff_lzw", dpi=(300, 300))

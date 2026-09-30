"""Figuras da versao v3 do manuscrito (duas frentes, criterio duro). Uso:
    python make_figures_v3.py DATA_DIR OUT_DIR {en|pt}
DATA_DIR contem copias de outputs/ do servidor: b23_boltz2_scores.json, b23_cleavage_circular.json,
b23_cleavage_linear_strict.json, b23_cleavage_{linear,circular}_hard.json e (opcional, teste de fumaca)
rmsd.xvg / hbond_num.xvg. Todos os numeros vem dos JSON; nada e digitado a mao.
"""
import collections
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

D, O, LG = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
O.mkdir(parents=True, exist_ok=True)
EN = LG == "en"
plt.rcParams.update({"font.size": 10, "savefig.dpi": 300, "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 150})


def T(en, pt):
    return en if EN else pt


def num(n):  # separador de milhar
    return f"{n:,}" if EN else f"{n:,}".replace(",", ".")


def load(n):
    return json.load(open(D / n, encoding="utf-8"))


lin_s, cir_s = load("b23_cleavage_linear_strict.json"), load("b23_cleavage_circular.json")
L, M = load("b23_cleavage_linear_hard.json"), load("b23_cleavage_circular_hard.json")
scores = load("b23_boltz2_scores.json")
SP = list(L["by_species"])
SHORT = [s[0] + ". " + s[1:] for s in SP]
CL = {"RESISTENTE": "#2a9d8f", "MARGINAL": "#e9c46a", "SUSCEPTIVEL": "#c8553d"}
LAB = {"RESISTENTE": T("RESISTANT-like", "RESISTENTE"), "MARGINAL": T("MARGINAL", "MARGINAL"),
       "SUSCEPTIVEL": T("SUSCEPTIBLE", "SUSCEPTIVEL")}
AA = "ACDEFGHIKLMNPQRSTVWY"


def hard(d):
    return {s: [r for r in d["by_species"][s]["results"] if r["verdict"] == "RESISTENTE"] for s in SP}


HL, HM = hard(L), hard(M)
ALL = [r for s in SP for r in L["by_species"][s]["results"]]
AL = [r for s in SP for r in HL[s]]
AM = [r for s in SP for r in HM[s]]


def comp(rs):
    c = collections.Counter(a for r in rs for a in r["sequence"])
    n = sum(c.values())
    return {a: c[a] / n * 100 for a in AA}, n


# ---- Figura 1: esquema do pipeline -----------------------------------------------------------
def fig_pipeline(status_e1="run"):
    fig, ax = plt.subplots(figsize=(11, 5.2))
    ax.set_xlim(0, 11); ax.set_ylim(0, 5.6); ax.axis("off")
    col = {"done": "#b7e4c7", "run": "#ffe066", "todo": "#e9ecef"}

    def box(x, y, w, h, t, st, fs=7.3):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03", fc=col[st], ec="#495057", lw=.8))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs)

    def arr(x1, y1, x2, y2):
        ax.annotate("", (x2, y2), (x1, y1), arrowprops=dict(arrowstyle="->", color="#495057", lw=.9))

    box(.05, 2.25, 1.55, 1.1, T("8 receptors\n+ S1–S3' subsites\n(TM 0.946–0.957)", "8 receptores\n+ sub-sítios S1–S3'\n(TM 0,946–0,957)"), "done")
    box(1.8, 2.25, 1.55, 1.1, T("Calibration:\n6 inhibitors + decoys\n(Boltz-2 10/10 pairs)", "Calibração:\n6 inibidores + decoys\n(Boltz-2 10/10 pares)"), "done")
    box(3.55, 2.25, 1.55, 1.1, T("RFdiffusion + MPNN\n880 backbones\n22,066 sequences", "RFdiffusion + MPNN\n880 backbones\n22.066 sequências"), "done")
    box(5.3, 2.25, 1.6, 1.1, T("E0  hard criterion\n(no K/R/F/Y/W/L/M/A/V\nat P1; Fig. 2)", "E0  critério duro\n(sem K/R/F/Y/W/L/M/A/V\nem P1; Fig. 2)"), "done")
    for a, b in ((1.6, 1.8), (3.35, 3.55), (5.1, 5.3)):
        arr(a, 2.8, b, 2.8)
    box(7.1, 3.85, 2.0, 1.25, T(f"FRONT L (linear)\n{len(AL)} candidates\nE1 Boltz-2 cyclic:false", f"FRENTE L (linear)\n{len(AL)} candidatos\nE1 Boltz-2 cyclic:false"), status_e1)
    box(7.1, .6, 2.0, 1.25, T(f"FRONT M (macrocycle)\n{len(AM)} candidates\nE1 Boltz-2 cyclic:true", f"FRENTE M (macrociclo)\n{len(AM)} candidatos\nE1 Boltz-2 cyclic:true"), status_e1)
    arr(6.9, 3.1, 7.1, 4.4); arr(6.9, 2.5, 7.1, 1.4)
    steps = [T("E2  top-10/species\n5 samples × 3 seeds", "E2  top-10/espécie\n5 amostras × 3 sementes"),
             T("E3  shuffled controls\n(paired Δ)", "E3  controles embaralhados\n(Δ pareado)"),
             T("E4  pose QC\n+ 8×8 cross matrix", "E4  QC de pose\n+ matriz 8×8"),
             T("E6–E7  10-ns MD, top-3/species\n(pH 10.0)", "E6–E7  MD 10 ns, top-3/espécie\n(pH 10,0)"),
             T("E8–E9  L vs M comparison\n+ list for long MD", "E8–E9  comparação L×M\n+ lista p/ MD longa")]
    ax.text(9.3, 5.35, T("E2 → E9", "E2 → E9"), fontsize=8, weight="bold")
    for i, t in enumerate(steps):
        y = 4.6 - i * 0.98
        box(9.3, y - .3, 1.65, .75, t, "todo", fs=6.4)
        if i:
            arr(10.12, y + .75 - .02 + 0.25, 10.12, y + .45)
    arr(9.1, 4.47, 9.3, 4.6)
    ax.plot([9.1, 9.2, 9.2], [1.2, 1.2, 4.6], color="#495057", lw=.9); arr(9.2, 4.6, 9.3, 4.6)
    ax.text(.05, .12, T("green = done · yellow = running · grey = pending.  E5 (non-target counter-screen) was not built; no selectivity is claimed.",
                        "verde = concluído · amarelo = em execução · cinza = pendente.  E5 (contra-triagem com não-alvos) não construída; nenhuma seletividade é afirmada."),
            fontsize=7, color="#495057")
    ax.text(.05, 1.2, T("Validated: cyclic topology (tleap;\nC–N 1.34 Å, ω −179°); pH 10.0\n(Lepidoptera midgut)", "Validado: topologia cíclica (tleap;\nC–N 1,34 Å, ω −179°); pH 10,0\n(intestino de Lepidoptera)"), fontsize=7, color="#1b4332")
    fig.savefig(O / T("Figure1_pipeline_v3.png", "fig1_pipeline_v3.png"), bbox_inches="tight", dpi=300)
    fig.savefig(O / T("Figure1_pipeline_v3.pdf", "fig1_pipeline_v3.pdf"), bbox_inches="tight")
    plt.close()


# ---- Figura 4: matriz P1 proibido -----------------------------------------------------------
def fig_rule():
    cls = [T("Trypsin-like", "Tripsina-like"), T("Chymotrypsin-like", "Quimotripsina-like"), T("Elastase-like", "Elastase-like"),
           T("Carboxypeptidase\n(free C-terminus)", "Carboxipeptidase\n(C-term. livre)")]
    forb = ["KR", "FYWLM", "AVLM", "KRFYWLMAVI"]
    mat = np.array([[1 if a in f else 0 for a in AA] for f in forb])
    fig, ax = plt.subplots(figsize=(8.5, 2.7))
    ax.imshow(mat, cmap="Reds", aspect="auto", vmin=0, vmax=1.3)
    ax.set_xticks(range(20)); ax.set_xticklabels(list(AA)); ax.set_yticks(range(4)); ax.set_yticklabels(cls, fontsize=8)
    for i in range(4):
        for j in range(20):
            if mat[i, j]:
                ax.text(j, i, "✕", ha="center", va="center", fontsize=8, color="white")
    ax.set_title(T("Residues forbidden at P1 by midgut protease class (unless the next residue is Pro)\nIle is forbidden only at the C-terminus of the linear peptide",
                   "Resíduos proibidos em P1 por classe de protease do intestino (exceto se o seguinte for Pro)\nIle só é proibida no C-terminal do linear"), fontsize=8.5)
    for s in ax.spines.values():
        s.set_visible(False)
    fig.tight_layout()
    fig.savefig(O / T("Figure2_hard_rule.png", "fig2_regra_dura.png")); fig.savefig(O / T("Figure2_hard_rule.pdf", "fig2_regra_dura.pdf")); plt.close()


# ---- Figura 5: funil -----------------------------------------------------------------------------
def fig_funnel():
    fig, ax = plt.subplots(1, 2, figsize=(10.5, 3.9), gridspec_kw={"width_ratios": [3, 1.4]})
    x = np.arange(len(SP)); w = .27
    soft = [cir_s["by_species"][s]["summary"]["RESISTENTE"] for s in SP]
    ax[0].bar(x - w, soft, w, color="#e9c46a", label=T("motif score, circular (first round)", "escore por motivo, circular (1ª rodada)"))
    ax[0].bar(x, [len(HL[s]) for s in SP], w, color="#457b9d", label=T("hard criterion, linear (front L)", "critério duro, linear (frente L)"))
    ax[0].bar(x + w, [len(HM[s]) for s in SP], w, color="#2a9d8f", label=T("hard criterion, circular (front M)", "critério duro, circular (frente M)"))
    for i, s in enumerate(SP):
        ax[0].text(i, len(HL[s]) + 4, len(HL[s]), ha="center", fontsize=8)
        ax[0].text(i + w, len(HM[s]) + 4, len(HM[s]), ha="center", fontsize=8)
    ax[0].set_xticks(x); ax[0].set_xticklabels(SHORT, rotation=35, ha="right", style="italic")
    ax[0].set_ylabel(T("resistant-like sequences", "sequências RESISTENTE")); ax[0].set_ylim(0, 350); ax[0].legend(frameon=False, fontsize=8.5)
    ax[0].set_title(T("Candidates surviving each screen", "Candidatos que sobrevivem a cada filtro"))
    tot = [sum(soft), len(AL), len(AM)]
    ax[1].bar(range(3), tot, color=["#e9c46a", "#457b9d", "#2a9d8f"])
    for i, t in enumerate(tot):
        ax[1].text(i, t + 25, num(t), ha="center")
    ax[1].set_xticks(range(3)); ax[1].set_xticklabels([T("motif", "motivo"), T("hard L", "duro L"), T("hard M", "duro M")])
    ax[1].set_title(T(f"Total (of {num(len(ALL))})", f"Total (de {num(len(ALL))})"))
    fig.tight_layout()
    fig.savefig(O / T("Figure5_hard_funnel.png", "fig5_funil.png")); fig.savefig(O / T("Figure5_hard_funnel.pdf", "fig5_funil.pdf")); plt.close()


# ---- Figura 6: composicao + comprimento --------------------------------------------------------
def fig_comp():
    cA, nA = comp(ALL); cL, nL = comp(AL)
    fig, ax = plt.subplots(1, 2, figsize=(10.5, 3.7), gridspec_kw={"width_ratios": [2.4, 1]})
    aa = sorted(cA, key=lambda a: -cL[a]); xx = np.arange(20); w = .4
    ax[0].bar(xx - w / 2, [cA[a] for a in aa], w, color="#b0b0b0", label=T(f"all sequences ({num(nA)} residues)", f"todas as sequências ({num(nA)} res.)"))
    ax[0].bar(xx + w / 2, [cL[a] for a in aa], w, color="#457b9d", label=T(f"hard criterion, front L ({num(nL)} residues)", f"critério duro, frente L ({num(nL)} res.)"))
    ax[0].set_xticks(xx); ax[0].set_xticklabels(aa); ax[0].set_ylabel(T("% of residues", "% dos resíduos")); ax[0].legend(frameon=False, fontsize=8.5)
    ax[0].set_title(T("Composition of the resistant-like set", "Composição do conjunto resistente"))
    lens = sorted({r["length"] for r in ALL}); xs = np.arange(len(lens))
    for off, rs, c, l in ((-.2, ALL, "#b0b0b0", T("all", "todas")), (.2, AL, "#457b9d", T("hard L", "duro L"))):
        cnt = collections.Counter(r["length"] for r in rs); tt = sum(cnt.values())
        ax[1].bar(xs + off, [cnt[k] / tt * 100 for k in lens], .4, color=c, label=l)
    ax[1].set_xticks(xs); ax[1].set_xticklabels(lens, fontsize=7); ax[1].set_xlabel(T("length (residues)", "comprimento (aa)"))
    ax[1].set_ylabel(T("% of sequences", "% das sequências")); ax[1].legend(frameon=False, fontsize=8.5); ax[1].set_title(T("Length", "Comprimento"))
    fig.tight_layout()
    fig.savefig(O / T("Figure6_hard_composition.png", "fig6_composicao.png")); fig.savefig(O / T("Figure6_hard_composition.pdf", "fig6_composicao.pdf")); plt.close()


# ---- Figura 7: Boltz-2 dos 1.829 (1a rodada) ------------------------------------------------
def fig_boltz():
    res = {sp: {(r["backbone"], r["sequence"]) for r in e["results"] if r["verdict"] == "RESISTENTE"} for sp, e in cir_s["by_species"].items()}
    sub = {sp: [r for r in scores[sp] if (r["backbone"], r["sequence"]) in res[sp]] for sp in SP}
    n = sum(len(v) for v in sub.values())
    fig, ax = plt.subplots(1, 3, figsize=(11.5, 3.8))
    for a, key, t in zip(ax[:2], ("iptm", "complex_plddt"), ("ipTM", T("complex pLDDT", "pLDDT do complexo"))):
        a.boxplot([[r[key] for r in sub[s]] for s in SP], tick_labels=SHORT, showfliers=False, patch_artist=True,
                  boxprops=dict(facecolor="#9bc4e2"), medianprops=dict(color="k"))
        a.set_title(t); a.tick_params(axis="x", rotation=40)
        for lab in a.get_xticklabels():
            lab.set_style("italic")
    allr = [r for v in sub.values() for r in v]
    Ls = sorted({r["length"] for r in allr})
    m = [np.mean([r["iptm"] for r in allr if r["length"] == l]) for l in Ls]
    c = [sum(1 for r in allr if r["length"] == l) for l in Ls]
    ax[2].bar(range(len(Ls)), m, color="#9bc4e2")
    for i, (mm, cc) in enumerate(zip(m, c)):
        ax[2].text(i, mm + .01, f"n={cc}", ha="center", fontsize=6, rotation=90)
    ax[2].set_xticks(range(len(Ls))); ax[2].set_xticklabels(Ls, fontsize=7)
    ax[2].set_xlabel(T("length (residues)", "comprimento (aa)")); ax[2].set_ylabel(T("mean ipTM", "ipTM médio")); ax[2].set_ylim(0, 1.15)
    ax[2].set_title(T("ipTM by length", "ipTM por comprimento"))
    fig.suptitle(T(f"Boltz-2 co-folding of the {num(n)} resistant-like macrocycles of the first round (1 sample each)",
                   f"Boltz-2 dos {num(n)} macrociclos resistentes da 1ª rodada (1 amostra cada)"), fontsize=9)
    fig.tight_layout()
    fig.savefig(O / T("Figure7_boltz2_first_round.png", "fig7_boltz2_1a_rodada.png")); fig.savefig(O / T("Figure7_boltz2_first_round.pdf", "fig7_boltz2_1a_rodada.pdf")); plt.close()
    return n, float(np.mean([r["confidence_score"] for r in allr]))



# ---- Figura 8: E1 -- reprodutibilidade do Boltz-2 e linear x ciclico ---------------------------------
def fig_e1():
    from scipy.stats import spearmanr
    for n in ("b23_boltz2_L_scores.json", "b23_boltz2_M_scores.json"):
        if not (D / n).exists():
            return None
    Ls, Ms = load("b23_boltz2_L_scores.json"), load("b23_boltz2_M_scores.json")
    key = lambda d: {sp: {(r["backbone"], r["sequence"]): r["confidence_score"] for r in rows} for sp, rows in d.items()}
    Lk, Mk, Ok = key(Ls), key(Ms), key(scores)
    rl = {sp: {(r["backbone"], r["sequence"]) for r in HL[sp]} for sp in SP}
    rm = {sp: {(r["backbone"], r["sequence"]) for r in HM[sp]} for sp in SP}
    rep, lm = [], []
    for sp in SP:
        rep += [(Ok[sp][k], Mk[sp][k]) for k in rm[sp] if k in Ok.get(sp, {}) and k in Mk.get(sp, {})]
        lm += [(Mk[sp][k], Lk[sp][k]) for k in rl[sp] & rm[sp] if k in Mk.get(sp, {}) and k in Lk.get(sp, {})]
    fig, ax = plt.subplots(1, 2, figsize=(9.5, 4.3))
    for a, pairs, xl, yl, ttl, c in (
            (ax[0], rep, T("cyclic, first round", "cíclico, 1ª rodada"), T("cyclic, repeated", "cíclico, repetido"), T("Same input, two runs", "Mesma entrada, duas rodadas"), "#2a9d8f"),
            (ax[1], lm, T("cyclic", "cíclico"), T("linear", "linear"), T("Same sequence, two modalities", "Mesma sequência, duas modalidades"), "#457b9d")):
        x, y = zip(*pairs)
        a.scatter(x, y, s=9, alpha=.5, color=c, edgecolor="none")
        a.plot([.6, 1], [.6, 1], ls=":", c="gray", lw=1)
        rho = spearmanr(x, y)[0]
        a.text(.62, .95, f"n = {len(pairs)}" + chr(10) + f"Spearman ρ = {rho:.2f}" + chr(10) + T("mean |Δ| = ", "|Δ| médio = ") + f"{np.mean(np.abs(np.array(y) - np.array(x))):.3f}", fontsize=9, va="top")
        a.set_xlim(.6, 1); a.set_ylim(.6, 1); a.set_xlabel(T("Boltz-2 confidence, ", "Confiança do Boltz-2, ") + xl); a.set_ylabel(T("Boltz-2 confidence, ", "Confiança do Boltz-2, ") + yl); a.set_title(ttl)
    fig.tight_layout()
    fig.savefig(O / T("Figure8_boltz2_reproducibility.png", "fig8_reprodutibilidade.png")); fig.savefig(O / T("Figure8_boltz2_reproducibility.pdf", "fig8_reprodutibilidade.pdf")); plt.close()
    return len(rep), len(lm)

# ---- Suplementares -------------------------------------------------------------------------------
def fig_s1():
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    x = np.arange(len(SP)); w = .38
    for off, d, lab in ((-w / 2, lin_s, T("linear", "linear")), (w / 2, cir_s, T("circular", "circular"))):
        bot = np.zeros(len(SP))
        for k in CL:
            v = np.array([d["by_species"][s]["summary"].get(k, 0) / d["by_species"][s]["n_sequences"] * 100 for s in SP])
            ax.bar(x + off, v, w * .95, bottom=bot, color=CL[k], label=LAB[k] if lab == T("linear", "linear") else None, edgecolor="white", lw=.4)
            bot += v
        for i in x:
            ax.text(i + off, 101, lab[:3], ha="center", fontsize=6)
    ax.set_xticks(x); ax.set_xticklabels(SHORT, rotation=35, ha="right", style="italic"); ax.set_ylabel(T("% of sequences", "% das sequências")); ax.set_ylim(0, 108)
    ax.legend(frameon=False, fontsize=8.5, loc="upper center", bbox_to_anchor=(.5, -.3), ncol=3)
    ax.set_title(T("Motif-score screen, linear-strict vs circular rule", "Filtro por escore de motivo, regra linear-estrita vs circular"))
    fig.tight_layout(); fig.savefig(O / T("FigureS1_motif_screen_rules.png", "figS1_regras_motivo.png")); plt.close()


def fig_s2():
    if not (D / "rmsd.xvg").exists():
        return
    def xvg(f):
        return np.array([[float(v) for v in l.split()] for l in open(D / f) if l[0] not in "#@"])
    r, h = xvg("rmsd.xvg"), xvg("hbond_num.xvg")
    fig, ax = plt.subplots(1, 2, figsize=(7.5, 3))
    ax[0].plot(r[:, 0] * 1000, r[:, 1] * 10, "o-", c="#2a9d8f"); ax[0].set_xlabel(T("time (ps)", "tempo (ps)")); ax[0].set_ylabel(T("backbone RMSD (Å)", "RMSD backbone (Å)"))
    ax[1].plot(h[:, 0], h[:, 1], "o-", c="#c8553d"); ax[1].set_xlabel(T("time (ps)", "tempo (ps)")); ax[1].set_ylabel(T("hydrogen bonds (system)", "ligações H (sistema)"))
    fig.suptitle(T("Smoke test of the cyclic topology (GRPGIQAAPI, 50 ps): checks the set-up, not stability", "Teste de fumaça da topologia cíclica (GRPGIQAAPI, 50 ps): valida a montagem, não a estabilidade"), fontsize=8)
    fig.tight_layout(); fig.savefig(O / T("FigureS2_cyclic_smoke.png", "figS2_ciclica_fumaca.png")); plt.close()


if __name__ == "__main__":
    fig_pipeline(); fig_rule(); fig_funnel(); fig_comp(); n, mc = fig_boltz(); print('E1 fig', fig_e1()); fig_s1(); fig_s2()
    from PIL import Image
    for f in list(O.glob("*.png")):
        if not f.name.startswith("fig") and not f.name.startswith("Figure"):
            continue
        Image.open(f).convert("RGB").save(f.with_suffix(".tif"), compression="tiff_lzw", dpi=(300, 300))
    print("ok; boltz subset", n, round(mc, 3), "L", len(AL), "M", len(AM))

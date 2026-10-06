"""
audit_numbers.py -- recalcula, a partir dos arquivos de dados do repositorio, os numeros que o manuscrito (EN) afirma nas
Secoes 3.2, 3.3, 3.4, 3.5, 3.6 e 3.8, e imprime AFIRMADO x RECALCULADO. Nao altera nada.
Uso: python -m scripts.audit_numbers  ->  docs/dados/audit_numbers_2026-10-05.json e tabela no terminal.
O que NAO se recalcula aqui (dado so no servidor): reprodutibilidade E1 (rho 0,57 / 0,50), contagens 527/543 do criterio duro
e a composicao do conjunto duro; ficam na lista de pendencias da auditoria.
"""
import csv
import json
import statistics as st
from pathlib import Path

from scipy.stats import spearmanr

ROOT = Path(__file__).parent.parent
D = ROOT / "data-e2-results"
C = ROOT / "data-calibration-b05"
rows = []


def chk(secao, afirmado, recalculado, tol=0.0, nota=""):
    ok = (afirmado == recalculado) if tol == 0 else (abs(afirmado - recalculado) <= tol)
    rows.append({"secao": secao, "afirmado": afirmado, "recalculado": recalculado, "ok": bool(ok), "nota": nota})
    print(("OK   " if ok else "FALHA"), secao, "| afirmado:", afirmado, "| recalculado:", recalculado, nota)


def med(x):
    return st.median(x)


# ---------------------------------------------------------------- 3.2 calibracao
boltz = json.load(open(C / "boltz_calibration_summary.json"))
md = json.load(open(C / "md_metrics_pbc_corrected.json"))["systems"]
gb = json.load(open(C / "mmpbsa_calib_results.json"))
pr = json.load(open(D / "prodigy_calib.json"))
INH = ["SFTI1", "BBI", "BPTI", "EcTI", "SKTI"]
P = [(r, k) for r in ("bovine", "sfrug") for k in INH]
dc = [boltz[f"{r}__{k}"]["confidence"] - boltz[f"{r}__{k}_decoy"]["confidence"] for r, k in P]
chk("3.2 Boltz-2 confianca real>isca (pares)", 10, sum(x > 0 for x in dc))
chk("3.2 Boltz-2 diferenca minima", 0.042, round(min(dc), 3), 0.001)
chk("3.2 Boltz-2 diferenca maxima", 0.274, round(max(dc), 3), 0.001)
chk("3.2 Boltz-2 diferenca mediana", 0.190, round(med(dc), 3), 0.001)
real = [boltz[f"{r}__{k}"]["confidence"] for r, k in P]
dec = [boltz[f"{r}__{k}_decoy"]["confidence"] for r, k in P]
chk("3.2 conf inibidores min", 0.853, round(min(real), 3), 0.001)
chk("3.2 conf inibidores max", 0.986, round(max(real), 3), 0.001)
chk("3.2 conf iscas min", 0.628, round(min(dec), 3), 0.001)
chk("3.2 conf iscas max", 0.944, round(max(dec), 3), 0.001)
for m, nome in (("iptm", "ipTM"), ("plddt", "pLDDT")):
    try:
        dd = [boltz[f"{r}__{k}"][m] - boltz[f"{r}__{k}_decoy"][m] for r, k in P]
        chk(f"3.2 {nome} real>isca", 10, sum(x > 0 for x in dd))
        if m == "iptm":
            chk("3.2 ipTM menor margem", 0.005, round(min(dd), 3), 0.001)
    except KeyError:
        pass
rm = [md[f"{r}__{k}"]["ligand_rmsd_nm_last_third"] < md[f"{r}__{k}_decoy"]["ligand_rmsd_nm_last_third"] for r, k in P]
chk("3.2 RMSD do ligante real<isca", 9, sum(rm))
g = [gb[f"{r}__{k}"]["delta_g_total_kcal"] < gb[f"{r}__{k}_decoy"]["delta_g_total_kcal"] for r, k in P]
chk("3.2 MM-GBSA real melhor", 4, sum(g))
pg = [pr[f"{r}__{k}"]["dG_kcal_mean"] < pr[f"{r}__{k}_decoy"]["dG_kcal_mean"] for r, k in P]
chk("3.2 PRODIGY real melhor", 2, sum(pg))
tags = [t for t in md if t in gb]
rho = spearmanr([md[t]["receptor_residues_in_contact_mean"] for t in tags], [gb[t]["delta_g_total_kcal"] for t in tags])
chk("3.2 rho MM-GBSA x contatos", -0.93, round(float(rho.statistic), 2), 0.005)
chk("3.2 n sistemas MM-GBSA", 22, len(tags))
L = {"SFTI1": 14, "BBI": 71, "BPTI": 58, "EcTI": 168, "SKTI": 172, "ApTI": 176}
tl = [L[t.split("__")[1].replace("_decoy", "")] for t in tags]
rl = spearmanr(tl, [gb[t]["delta_g_total_kcal"] for t in tags])
chk("3.2 rho MM-GBSA x comprimento do ligante", -0.27, round(float(rl.statistic), 2), 0.01, f"P={rl.pvalue:.2f}")
t2 = [t for t in pr if t in md]
rp = spearmanr([pr[t]["ic_total_mean"] for t in t2], [pr[t]["dG_kcal_mean"] for t in t2])
chk("3.2 rho PRODIGY x contatos", -0.79, round(float(rp.statistic), 2), 0.005, f"n={len(t2)}")
more = sum(pr[f"{r}__{k}_decoy"]["ic_total_mean"] > pr[f"{r}__{k}"]["ic_total_mean"] for r, k in P)
chk("3.2 isca com mais contatos (PRODIGY)", 7, more, 0, "o par SKTI-Sf difere por 0,25 contato")

# ---------------------------------------------------------------- 3.3 campanha
fc = json.load(open(ROOT / "data-b23-scoring/results/filter_composition.json"))
chk("3.3 RESISTENTE", 1829, fc["RESISTENTE"]["n"])
chk("3.3 MARGINAL", 4987, fc["MARGINAL"]["n"])
chk("3.3 SUSCEPTIVEL", 15250, fc["SUSCEPTIVEL"]["n"])
chk("3.3 total de sequencias", 22066, sum(fc[k]["n"] for k in ("RESISTENTE", "MARGINAL", "SUSCEPTIVEL")))
chk("3.3 comprimento medio RESISTENTE", 7.05, fc["RESISTENTE"]["length_mean"], 0.005)
chk("3.3 RESISTENTE <=10 res (%)", 95.6, round(100 * fc["RESISTENTE"]["length_le_10_frac"], 1), 0.05)
chk("3.3 SUSCEPTIVEL comprimento medio", 15.74, fc["SUSCEPTIVEL"]["length_mean"], 0.005)
chk("3.3 SUSCEPTIVEL <=10 res (%)", 12.7, round(100 * fc["SUSCEPTIVEL"]["length_le_10_frac"], 1), 0.05)

# ---------------------------------------------------------------- 3.4 E2/E3/QC/matriz
E2 = {F: json.load(open(D / f"b23_boltz2_E2_{F}_scores.json")) for F in "LM"}
for F, (a, b) in (("L", (0.922, 0.900)), ("M", (0.911, 0.888))):
    v = [x for sp in E2[F].values() for x in sp]
    chk(f"3.4 E2 n candidatos {F}", 80, len(v))
    chk(f"3.4 E1 media (top 10/esp) {F}", a, round(st.mean(x["confidence_E1"] for x in v), 3), 0.001)
    chk(f"3.4 E2 media {F}", b, round(st.mean(x["confidence_score"] for x in v), 3), 0.001)
    r = spearmanr([x["confidence_E1"] for x in v], [x["confidence_score"] for x in v])
    chk(f"3.4 rho E1 x E2 {F}", {"L": 0.80, "M": 0.74}[F], round(float(r.statistic), 2), 0.005)
    chk(f"3.4 DP medio entre as 15 predicoes {F}", {"L": 0.019, "M": 0.022}[F], round(st.mean(x["confidence_sd"] for x in v), 3), 0.001)
    chk(f"3.4 todo candidato com >=1 amostra aprovada no QC {F}", 80, sum(x["n_samples_qc_pass"] >= 1 for x in v))
DP = {F: json.load(open(D / f"delta_paired_{F}.json")) for F in "LM"}
final = {F: json.load(open(D / f"top_candidates_{F}.json"))["candidates"] for F in "LM"}
for F, (npos, n, medd, nf, nfpos) in (("L", (63, 78, 0.013, 24, 23)), ("M", (60, 79, 0.014, 24, 22))):
    dl = [e["delta"] for sp in DP[F].values() for e in sp if e["delta"] is not None]
    chk(f"3.4 delta positivo {F}", npos, sum(x > 0 for x in dl))
    chk(f"3.4 candidatos com controle {F}", n, len(dl))
    chk(f"3.4 delta mediano {F}", medd, round(med(dl), 3), 0.001)
    key = {(e["sequence"], sp): e["delta"] for sp, lst in DP[F].items() for e in lst if e["delta"] is not None}
    fin = [key.get((v["sequence"], v["species"])) for v in final[F].values()]
    fin = [x for x in fin if x is not None]
    chk(f"3.4 finais com delta {F}", nf, len(fin))
    chk(f"3.4 finais com delta>0 {F}", nfpos, sum(x > 0 for x in fin))
for F in "LM":
    q = json.load(open(D / f"pose_qc_{F}.json"))
    chk(f"3.4 finais {F}: menor distancia peptideo-receptor >= 2,4 A", True, min(v["min_dist_pep_rec_A"] for v in q.values()) >= 2.4,
        nota=f"min={min(v['min_dist_pep_rec_A'] for v in q.values())}")
    chk(f"3.4 finais {F}: n", 24, len(q))
    chk(f"3.4 finais {F}: omega nao-trans (sem Pro)", 0, sum(v["omega_nonTrans_nonPro"] for v in q.values()))
mx = {F: json.load(open(D / f"matrix_{F}.json")) for F in "LM"}
for F, (own_hi, ) in (("L", (4,)), ("M", (3,))):
    byp = {}
    for v in mx[F].values():
        byp.setdefault(v["peptide_of"], {})[v["receptor"]] = v["confidence_score"]
    hi = sum(max(d, key=d.get) == p for p, d in byp.items() if p in d)
    chk(f"3.4 matriz {F}: receptor proprio da a maior confianca (de 8)", own_hi, hi, 0, f"n pept={len(byp)}, n predicoes={len(mx[F])}")
    own = [d[p] for p, d in byp.items() if p in d]
    oth = [x for p, d in byp.items() for r, x in d.items() if r != p]
    print("      media propria/outras:", round(st.mean(own), 3), round(st.mean(oth), 3))

# ---------------------------------------------------------------- 3.5 MD pH 10
A = {F: json.load(open(D / f"md10_{F}_analysis.json")) for F in "LM"}
for F, (i0, f0) in (("L", (5.72, 6.77)), ("M", (5.07, 6.11))):
    v = [x for x in A[F].values() if "occ_5A_h2" in x]
    chk(f"3.5 {F} n simulacoes analisadas", 24, len(v))
    chk(f"3.5 {F} d inicial mediana", i0, round(med([x["d_anchor_asp_ini_A"] for x in v]), 2), 0.005)
    chk(f"3.5 {F} d final mediana", f0, round(med([x["d_anchor_asp_fim_A"] for x in v]), 2), 0.005)
    chk(f"3.5 {F} ancora <=4 A na janela final", 2, sum(x["d_anchor_asp_fim_A"] <= 4 for x in v))
    chk(f"3.5 {F} ancora >10 A na janela final", {"L": 6, "M": 4}[F], sum(x["d_anchor_asp_fim_A"] > 10 for x in v))
    chk(f"3.5 {F} ancora igual nas metades", {"L": 21, "M": 24}[F], sum(x["anchor_same_in_halves"] for x in v))
    chk(f"3.5 {F} contato minimo com o receptor", {"L": 0.82, "M": 0.97}[F], round(min(x["contact_any_frac_4.5A"] for x in v), 2), 0.006)
    r = [x["peptide_rmsd_local_nm_final20pct"] for x in v]
    chk(f"3.5 {F} RMSD final mediano", {"L": 0.56, "M": 0.30}[F], round(med(r), 2), 0.006)
    chk(f"3.5 {F} RMSD minimo", {"L": 0.21, "M": 0.16}[F], round(min(r), 2), 0.006)
    chk(f"3.5 {F} RMSD maximo", {"L": 2.64, "M": 1.69}[F], round(max(r), 2), 0.006)
allv = [dict(x, front=F, key=k) for F in "LM" for k, x in A[F].items() if "occ_5A_h2" in x]
hi = [x for x in allv if x["occ_5A_h2"] >= 0.70]
chk("3.5 ocupancia >=0,70 (de 48)", 5, len(hi), 0, str(sorted(x["sequence"] for x in hi)))
close = [x for x in allv if x["d_anchor_asp_ini_A"] <= 4.0]
chk("3.5 simulacoes que partiram a <=4,0 A", 9, len(close))
chk("3.5 dessas, com ocupancia >=0,70", 5, sum(x["occ_5A_h2"] >= 0.70 for x in close))
far = [x for x in allv if x["d_anchor_asp_ini_A"] > 4.0]
chk("3.5 que partiram >4,0 A (n)", 39, len(far))
chk("3.5 dessas, com ocupancia >=0,70", 0, sum(x["occ_5A_h2"] >= 0.70 for x in far))
r1 = spearmanr([x["d_anchor_asp_ini_A"] for x in allv], [x["d_anchor_asp_fim_A"] for x in allv])
chk("3.5 rho distancia inicial x final", 0.63, round(float(r1.statistic), 2), 0.005)
r2 = spearmanr([x["d_anchor_asp_ini_A"] for x in allv], [x["occ_5A_h2"] for x in allv])
chk("3.5 rho distancia inicial x ocupancia", -0.63, round(float(r2.statistic), 2), 0.005)
cyc = [x for x in allv if x["front"] == "M"]
chk("3.5 aneis com C-N <= 1,462 A", 24, sum(x["ring_CN_max_A"] <= 1.462 for x in cyc), 0, f"max={max(x['ring_CN_max_A'] for x in cyc)}")
chk("3.5 aneis que cumprem o criterio estrito", 11, sum(x.get("ring_intact") is True for x in cyc))
bad = [x for x in cyc if not x.get("ring_intact")]
chk("3.5 aneis que falham", 13, len(bad))
chk("3.5 omega minimo (falhas) min", 137.2, round(min(x["ring_omega_abs_min_deg"] for x in bad), 1), 0.05)
chk("3.5 omega minimo (falhas) max", 149.9, round(max(x["ring_omega_abs_min_deg"] for x in bad), 1), 0.05)
chk("3.5 das 13, quantas com >=97,8% dos quadros acima de 150", 12, sum(x["ring_omega_frac_ge150"] >= 0.978 for x in bad))

# ---------------------------------------------------------------- 3.6 PRODIGY nas poses
pp = json.load(open(D / "prodigy_poses.json"))
R = {(r["front"], r["key"]): r for r in csv.DictReader(open(ROOT / "manuscript/figures/ranking_final.csv", encoding="utf-8"))}
g = [v["dG_kcal"] for v in pp.values()]
n = [len(R[(v["front"], v["key"])]["sequence"]) for v in pp.values()]
ic = [v["ic_total"] for v in pp.values()]
chk("3.6 PRODIGY pose: n", 48, len(g))
chk("3.6 PRODIGY pose: minimo", -12.2, min(g), 0.01)
chk("3.6 PRODIGY pose: maximo", -7.1, max(g), 0.01)
chk("3.6 PRODIGY pose: mediana (a mediana verdadeira de 48 valores)", -9.6, round(med(g), 2), 0.06)
chk("3.6 rho dG x comprimento", -0.60, round(float(spearmanr(g, n).statistic), 2), 0.005)
chk("3.6 rho dG x contatos", -0.62, round(float(spearmanr(g, ic).statistic), 2), 0.005)
# ---------------------------------------------------------------- Tabela 4
for F, k, seq, e2, d3, ini, fin, occ, pg_, per in (("L", "Agemmatalis__r2", "NGGRPDAP", 0.937, 0.030, 2.78, 2.74, 1.00, -11.1, -1.39),
                                                   ("L", "Onubilalis__r2", "GQNDS", 0.909, 0.013, 4.00, 3.77, 1.00, -9.0, -1.80),
                                                   ("M", "Sfrugiperda__r1", "GGHSE", 0.908, 0.015, 2.86, 3.07, 0.99, -8.8, -1.76),
                                                   ("M", "Agemmatalis__r2", "GGKPGEP", 0.923, 0.020, 2.71, 2.71, 1.00, -9.7, -1.39)):
    r = R[(F, k)]
    a = A[F][k]
    sp = r["species"]
    dd = {e["sequence"]: e["delta"] for e in DP[F][sp]}[seq]
    chk(f"T4 {seq} sequencia", seq, a["sequence"])
    chk(f"T4 {seq} E2", e2, round(float(r["confidence_E2"]), 3), 0.001)
    chk(f"T4 {seq} delta", d3, round(dd, 3), 0.001)
    chk(f"T4 {seq} d inicial", ini, round(a["d_anchor_asp_ini_A"], 2), 0.005)
    chk(f"T4 {seq} d final", fin, round(a["d_anchor_asp_fim_A"], 2), 0.005)
    chk(f"T4 {seq} ocupancia", occ, round(a["occ_5A_h2"], 2), 0.006)
    p = pp[f"{F}:{k}"]
    chk(f"T4 {seq} PRODIGY", pg_, p["dG_kcal"], 0.01)
    chk(f"T4 {seq} PRODIGY por residuo", per, round(p["dG_kcal"] / len(seq), 2), 0.006)

nf = sum(not r["ok"] for r in rows)
print(f"\n{len(rows)} verificacoes; {nf} falhas")
(ROOT / "docs/dados").mkdir(exist_ok=True)
(ROOT / "docs/dados/audit_numbers_2026-10-05.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))

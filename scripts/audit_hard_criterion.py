"""
audit_hard_criterion.py -- recalcula, a partir das 22.066 sequencias da campanha (outputs/b23_campaign_<especie>/dataset/
ml_training_dataset.csv, no servidor), os numeros do criterio duro de nao clivabilidade citados nas Secoes 3.3 e 4.3:
527 lineares, 543 ciclicas, por especie, 16 so-ciclicas, composicao (Gly 49,4%...), comprimento medio, 430 com <=8 residuos,
393 sem Ile no interior, K/R seguidos de Pro. Reimplementa a regra do ZERO a partir do texto dos Metodos (nao importa
analyze_cleavage), e compara com analyze_cleavage.hard_cleavage_sites: se as duas implementacoes divergirem, e' erro.
Uso: python -m scripts.audit_hard_criterion
"""
import csv
import json
from collections import Counter
from pathlib import Path

from scripts.analyze_cleavage import hard_cleavage_sites

ROOT = Path(__file__).parent.parent
SPECIES = ["Sfrugiperda", "Slitura", "Onubilalis", "Dsaccharalis", "Cincludens", "Hvirescens", "Pxylostella", "Agemmatalis"]
FORBID = set("KRFYWLMAV")


def hard_ok(seq, circular, forbid=FORBID):
    """Texto dos Metodos 2.4: nenhum resíduo proibido, a menos que o seguinte seja Pro; no linear o C-terminal
    tambem e' avaliado (nao pode estar no conjunto nem ser Ile); no macrociclo a ligacao de fechamento conta."""
    n = len(seq)
    for i in range(n):
        nxt = seq[(i + 1) % n] if (circular or i < n - 1) else None
        if seq[i] in forbid:
            if nxt is None:      # C-terminal livre do linear
                return False
            if nxt != "P":
                return False
    if not circular and seq[-1] == "I":
        return False
    return True


def main():
    seqs = {}
    for sp in SPECIES:
        p = ROOT / f"outputs/b23_campaign_{sp}/dataset/ml_training_dataset.csv"
        if not p.exists():
            print("sem dataset:", sp)
            continue
        with open(p, newline="") as f:
            seqs[sp] = sorted({r["sequence"] for r in csv.DictReader(f)})
    tot = sum(len(v) for v in seqs.values())
    print("sequencias unicas por especie (campanha):", {k: len(v) for k, v in seqs.items()}, "total", tot)
    res = {"total": tot}
    lin, cyc, lin_set, cyc_set = {}, {}, set(), set()
    mism = 0
    for sp, L in seqs.items():
        lin[sp] = [s for s in L if hard_ok(s, False)]
        cyc[sp] = [s for s in L if hard_ok(s, True)]
        for s in L:   # confere as duas implementacoes
            a = not hard_cleavage_sites(s, circular=False)
            b = not hard_cleavage_sites(s, circular=True)
            if a != hard_ok(s, False) or b != hard_ok(s, True):
                mism += 1
        lin_set |= {(sp, s) for s in lin[sp]}
        cyc_set |= {(sp, s) for s in cyc[sp]}
    res["linear_total"], res["cyclic_total"] = len(lin_set), len(cyc_set)
    res["linear_por_especie"] = {k: len(v) for k, v in lin.items()}
    res["ciclico_por_especie"] = {k: len(v) for k, v in cyc.items()}
    res["divergencias_entre_implementacoes"] = mism
    res["linear_dentro_do_ciclico"] = lin_set <= cyc_set
    only = sorted(cyc_set - lin_set)
    res["so_ciclicas"] = len(only)
    res["so_ciclicas_terminam_em_I"] = sum(s[-1] == "I" for _, s in only)
    res["so_ciclicas_terminam_em_proibido_seguido_de_P_inicial"] = sum(s[-1] in FORBID and s[0] == "P" for _, s in only)
    lens = [len(s) for _, s in lin_set]
    res["linear_comprimento_medio"] = round(sum(lens) / len(lens), 2)
    res["linear_<=8"] = sum(x <= 8 for x in lens)
    res["linear_faixa"] = [min(lens), max(lens)]
    comp = Counter("".join(s for _, s in lin_set))
    tot_res = sum(comp.values())
    res["linear_residuos"] = tot_res
    res["linear_composicao_%"] = {a: round(100 * c / tot_res, 1) for a, c in comp.most_common(8)}
    kr = [(s[i], s[i + 1] if i + 1 < len(s) else "-") for _, s in lin_set for i in range(len(s)) if s[i] in "KR"]
    res["linear_KR_total"] = len(kr)
    res["linear_KR_seguidos_de_P"] = sum(b == "P" for a, b in kr)
    res["linear_Arg_Pro_Lys_Pro"] = [sum(a == "R" and b == "P" for a, b in kr), sum(a == "K" and b == "P" for a, b in kr)]
    sens = set("KRFYWLMAVI")
    res["linear_sem_Ile_no_interior"] = sum(1 for sp, L in seqs.items() for s in L if hard_ok(s, False, sens) and True)
    # interior sem I: a regra de sensibilidade proibe I em qualquer posicao seguida de nao-Pro; no C-terminal ja proibia
    out = ROOT / "outputs/audit_hard_criterion.json"
    out.write_text(json.dumps(res, indent=1, ensure_ascii=False))
    print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()

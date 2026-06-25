"""
analyze_cleavage.py — Análise in silico de sítios de clivagem proteolítica.

Implementa as regras de clivagem do ExPASy PeptideCutter para as principais proteases
do trato intestinal de Lepidoptera e proteases humanas relevantes.

Conceito de P1-externo vs P1-interno:
  - P1-externo: Arg/Lys que serve de âncora no sítio S1 da tripsina-alvo
                (posição mais C-terminal da sequência ou conforme contexto estrutural)
  - P1-interno : outros Arg/Lys dentro da sequência → susceptíveis a clivagem pela tripsina

Um candidato com ZERO P1-internos é resistente à auto-digestão por tripsina.

Uso:
  python scripts/analyze_cleavage.py
  python scripts/analyze_cleavage.py --seq MKKQRENAKKVAEITLKKAK
  python scripts/analyze_cleavage.py --top 20  # analisar top-N do ranking
"""
import json
import sys
import argparse
from pathlib import Path


ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))


# ── Regras de clivagem ──────────────────────────────────────────────────────
# Fonte: ExPASy PeptideCutter + litertura gut proteases Lepidoptera
#   cut_after  : conjunto de aa após os quais ocorre clivagem
#   not_before  : clivagem NÃO ocorre se seguido destes aa
#   cut_before  : conjunto de aa ANTES dos quais ocorre clivagem (pepsin-style)
#   priority    : 1=alta, 2=média, 3=baixa relevância para trato intestinal de Lepidoptera

CLEAVAGE_RULES = {
    "Trypsin": {
        "desc":       "Tripsina: cleaves after K, R (except R↓P and K↓P)",
        "cut_after":  "KR",
        "not_before": "P",
        "priority":   1,
    },
    "Chymotrypsin_high": {
        "desc":       "Quimiotripsina (alta especificidade): cleaves after F, Y, W",
        "cut_after":  "FYW",
        "not_before": "P",
        "priority":   1,
    },
    "Chymotrypsin_low": {
        "desc":       "Quimiotripsina (baixa): cleaves after F, Y, W, M, L",
        "cut_after":  "FYWML",
        "not_before": "P",
        "priority":   2,
    },
    "Elastase": {
        "desc":       "Elastase-like: cleaves after A, G, S, V (broad)",
        "cut_after":  "AGSV",
        "not_before": "P",
        "priority":   2,
    },
    "LysC": {
        "desc":       "Endoproteinase Lys-C: cleaves after K only",
        "cut_after":  "K",
        "not_before": "",
        "priority":   3,
    },
    "ArgC": {
        "desc":       "Endoproteinase Arg-C (glutamyl peptidase I): cleaves after R",
        "cut_after":  "R",
        "not_before": "",
        "priority":   3,
    },
    "Pepsin_pH2": {
        "desc":       "Pepsina pH≤2: cleaves before F, L (not before P)",
        "cut_before": "FL",
        "not_before": "P",
        "priority":   2,  # relevante apenas para delivery oral humano
    },
}


def find_cleavage_sites(seq: str, rule: dict) -> list[int]:
    """
    Retorna lista de posições (0-based) onde ocorre clivagem.
    A clivagem é entre posição i e i+1, representada pelo índice i.
    """
    sites = []
    not_before = set(rule.get("not_before", ""))

    if "cut_after" in rule:
        cut_set = set(rule["cut_after"])
        for i, aa in enumerate(seq[:-1]):   # não conta clivagem após último resíduo
            next_aa = seq[i + 1]
            if aa in cut_set and next_aa not in not_before:
                sites.append(i)

    elif "cut_before" in rule:
        cut_set = set(rule["cut_before"])
        for i, aa in enumerate(seq[1:], start=1):
            next_aa = seq[i] if i < len(seq) else ""
            prev_aa = seq[i - 1]
            if aa in cut_set and (not next_aa or next_aa not in not_before):
                sites.append(i - 1)  # clivagem entre i-1 e i

    return sites


def classify_trypsin_sites(seq: str, sites: list[int]) -> dict:
    """
    Classifica sítios de clivagem de tripsina em:
      - p1_anchor : sítio mais C-terminal → posição de ancoramento desejada
      - internal  : todos os outros → susceptíveis a auto-digestão
    """
    if not sites:
        return {"p1_anchor": None, "internal": [], "n_internal": 0}

    p1_anchor = max(sites)   # sítio mais C-terminal = P1 de ancoramento
    internal  = [s for s in sites if s != p1_anchor]
    return {
        "p1_anchor": p1_anchor,
        "internal":  internal,
        "n_internal": len(internal),
    }


def susceptibility_score(analysis: dict) -> float:
    """
    Score de susceptibilidade proteolítica (0 = resistente, 1 = altamente susceptível).
    Ponderado por prioridade das proteases.
    """
    total_sites   = 0
    weighted_score = 0.0
    weights = {1: 1.0, 2: 0.6, 3: 0.3}

    for protease, data in analysis["by_protease"].items():
        n   = data["n_sites"]
        pri = CLEAVAGE_RULES[protease]["priority"]
        w   = weights.get(pri, 0.3)
        # Para tripsina: conta apenas internos (não o P1-âncora)
        if protease == "Trypsin":
            n_eff = data.get("trypsin_classification", {}).get("n_internal", n)
        else:
            n_eff = n
        weighted_score += w * n_eff
        total_sites    += n_eff

    # Normalizar: score 0–1 (satura em ~10 sítios ponderados)
    score = min(1.0, weighted_score / 10.0)
    return round(score, 3)


def resistance_verdict(score: float, n_internal_trypsin: int) -> str:
    if n_internal_trypsin == 0 and score < 0.3:
        return "RESISTENTE"
    elif n_internal_trypsin <= 1 and score < 0.5:
        return "MARGINAL"
    else:
        return "SUSCEPTIVEL"


def suggest_modifications(seq: str, trypsin_internal: list[int]) -> list[str]:
    """Sugere substituições nos P1-internos para aumentar resistência."""
    suggestions = []
    for pos in trypsin_internal:
        aa = seq[pos]
        if aa == "K":
            suggestions.append(
                f"Pos {pos+1} ({aa}→R): substituir K por R reduz probabilidade Lys-C; "
                f"ou K→Nle (norleucina) elimina clivagem mantendo hidrofobicidade"
            )
        elif aa == "R":
            suggestions.append(
                f"Pos {pos+1} ({aa}→Orn): substituir R por Ornitina (Orn) "
                f"remove guanidínio mas mantém basicidade"
            )
    if trypsin_internal:
        suggestions.append(
            "Alternativa global: ciclização N-C-terminal ou d-aminoácidos nas posições internas"
        )
    return suggestions


def analyze_sequence(seq: str) -> dict:
    seq = seq.strip().upper()
    n   = len(seq)

    by_protease = {}
    for protease, rule in CLEAVAGE_RULES.items():
        sites = find_cleavage_sites(seq, rule)
        entry = {
            "n_sites": len(sites),
            "positions": [s + 1 for s in sites],  # 1-based para leitura
        }
        if protease == "Trypsin":
            entry["trypsin_classification"] = classify_trypsin_sites(seq, sites)
        by_protease[protease] = entry

    n_internal = by_protease["Trypsin"]["trypsin_classification"]["n_internal"]
    susc_score = susceptibility_score({"by_protease": by_protease})
    verdict    = resistance_verdict(susc_score, n_internal)
    mods       = suggest_modifications(seq, by_protease["Trypsin"]["trypsin_classification"]["internal"])

    return {
        "sequence":              seq,
        "length":                n,
        "by_protease":           by_protease,
        "susceptibility_score":  susc_score,
        "trypsin_internal_sites": n_internal,
        "verdict":               verdict,
        "suggested_modifications": mods,
    }


def print_report(result: dict):
    seq = result["sequence"]
    v   = result["verdict"]
    v_color = {"RESISTENTE": "\033[92m", "MARGINAL": "\033[93m", "SUSCEPTIVEL": "\033[91m"}
    reset = "\033[0m"
    color = v_color.get(v, "")

    print(f"\n{'─'*60}")
    print(f"Sequência : {seq}  (len={result['length']})")
    print(f"Veredicto : {color}{v}{reset}  (score={result['susceptibility_score']})")
    print(f"P1-internos tripsina: {result['trypsin_internal_sites']}")
    print()
    print(f"{'Protease':<25} {'Sítios':<8} {'Posições (1-based)'}")
    print("─"*60)
    for protease, data in result["by_protease"].items():
        if CLEAVAGE_RULES[protease]["priority"] > 2:
            continue   # mostrar apenas alta/média prioridade
        pos_str = ",".join(str(p) for p in data["positions"]) or "—"
        print(f"{protease:<25} {data['n_sites']:<8} {pos_str}")
        if protease == "Trypsin" and data["n_sites"] > 0:
            tc = data["trypsin_classification"]
            print(f"  → P1-âncora (pos {tc['p1_anchor']+1 if tc['p1_anchor'] is not None else '—'}), "
                  f"Internos: {tc['n_internal']} "
                  f"(pos {[p+1 for p in tc['internal']]})")

    if result["suggested_modifications"]:
        print()
        print("Modificações sugeridas:")
        for mod in result["suggested_modifications"]:
            print(f"  • {mod}")


def main():
    parser = argparse.ArgumentParser(description="Análise de sítios de clivagem proteolítica")
    parser.add_argument("--seq",    type=str,  help="Analisar sequência específica")
    parser.add_argument("--top",    type=int,  default=None, help="Analisar top-N do ranking.csv")
    parser.add_argument("--json",   action="store_true", help="Saída em JSON")
    args = parser.parse_args()

    sequences = []

    if args.seq:
        sequences = [args.seq]

    elif args.top is not None:
        rank_file = ROOT / "outputs" / "ranking" / "ranking.csv"
        if not rank_file.exists():
            print(f"Arquivo não encontrado: {rank_file}")
            sys.exit(1)
        import csv
        with open(rank_file) as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i >= args.top:
                    break
                sequences.append(row["sequence"])

    else:
        # Default: analisar candidatos top-5 conhecidos do projeto
        sequences = [
            "MKKQRENAKKVAEITLKKAK",
            "GSRASARAYAARVRARRAAL",
            "GARKSIREYQKRVLERLKKK",
            "SLARKRAEENAKRFLERVKK",
            "AARASIRAAAARFRARRAAL",
        ]
        print("Analisando 5 candidatos MD do pipeline...")

    results = []
    for seq in sequences:
        if not seq:
            continue
        r = analyze_sequence(seq)
        results.append(r)
        if not args.json:
            print_report(r)

    # Resumo
    if not args.json:
        print(f"\n{'='*60}")
        print(f"RESUMO — {len(results)} sequências analisadas")
        print(f"{'Sequência':<25} {'Comprimento':<12} {'P1-int':<8} {'Score':<8} Veredicto")
        print("─"*60)
        for r in sorted(results, key=lambda x: x["susceptibility_score"]):
            v = r["verdict"]
            v_color = {"RESISTENTE": "\033[92m", "MARGINAL": "\033[93m", "SUSCEPTIVEL": "\033[91m"}
            c = v_color.get(v, ""); reset = "\033[0m"
            print(f"{r['sequence']:<25} {r['length']:<12} {r['trypsin_internal_sites']:<8} "
                  f"{r['susceptibility_score']:<8} {c}{v}{reset}")
    else:
        print(json.dumps(results, indent=2, ensure_ascii=False))

    # Salvar JSON
    out_path = ROOT / "outputs" / "cleavage_analysis.json"
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    if not args.json:
        print(f"\nResultados salvos em: {out_path}")


if __name__ == "__main__":
    main()

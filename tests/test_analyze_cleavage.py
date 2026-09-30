"""Testes da regra de clivagem, foco no modo circular (macrociclo cabeca-cauda)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from analyze_cleavage import CLEAVAGE_RULES, analyze_sequence, find_cleavage_sites  # noqa: E402

TRYP = CLEAVAGE_RULES["Trypsin"]


def test_linear_ignora_ultimo_residuo():
    # comportamento original preservado: K na ultima posicao nao e sitio no peptideo linear
    assert find_cleavage_sites("TGISGK", TRYP) == []
    assert analyze_sequence("TGISGK")["verdict"] == "RESISTENTE"


def test_circular_conta_sitio_do_fechamento():
    # K(6)-T(1): ligacao do fechamento e' sitio de tripsina
    assert find_cleavage_sites("TGISGK", TRYP, circular=True) == [5]
    r = analyze_sequence("TGISGK", circular=True)
    assert r["trypsin_internal_sites"] == 1 and r["verdict"] == "MARGINAL"


def test_circular_K_seguido_de_P_no_fechamento_nao_cliva():
    assert find_cleavage_sites("PGISGK", TRYP, circular=True) == []


def test_circular_ancora_geometrica_no_K_e_isenta():
    r = analyze_sequence("TGISGK", geometric_p1_1based=6, circular=True)
    assert r["trypsin_internal_sites"] == 0 and r["verdict"] == "RESISTENTE"


def test_circular_sem_geometria_nao_presume_ancora():
    # sem P1 geometrico, macrociclo nao tem terminal real -> nenhum K/R e' isento
    r = analyze_sequence("AKAAA", circular=True)
    assert r["trypsin_internal_sites"] == 1


def test_circular_sem_KR_igual_ao_linear_para_tripsina():
    assert analyze_sequence("GGDDG", circular=True)["trypsin_internal_sites"] == 0


# ── regressão: o modo linear tem que reproduzir EXATAMENTE a implementação original ──────────
def _legacy_find_cleavage_sites(seq, rule):
    """Cópia literal da implementação anterior à correção circular (2026-09-30)."""
    sites = []
    not_before = set(rule.get("not_before", ""))
    if "cut_after" in rule:
        cut_set = set(rule["cut_after"])
        for i, aa in enumerate(seq[:-1]):
            next_aa = seq[i + 1]
            if aa in cut_set and next_aa not in not_before:
                sites.append(i)
    elif "cut_before" in rule:
        cut_set = set(rule["cut_before"])
        for i, aa in enumerate(seq[1:], start=1):
            next_aa = seq[i] if i < len(seq) else ""
            if aa in cut_set and (not next_aa or next_aa not in not_before):
                sites.append(i - 1)
    return sites


def test_modo_linear_identico_ao_legado_em_sequencias_aleatorias():
    import random
    rng = random.Random(0)
    aas = "ACDEFGHIKLMNPQRSTVWY"
    for _ in range(3000):
        seq = "".join(rng.choice(aas) for _ in range(rng.randint(2, 20)))
        for name, rule in CLEAVAGE_RULES.items():
            assert find_cleavage_sites(seq, rule) == _legacy_find_cleavage_sites(seq, rule), (seq, name)


def test_circular_so_acrescenta_o_sitio_do_fechamento():
    import random
    rng = random.Random(1)
    aas = "ACDEFGHIKLMNPQRSTVWY"
    for _ in range(2000):
        seq = "".join(rng.choice(aas) for _ in range(rng.randint(3, 20)))
        n = len(seq)
        for name, rule in CLEAVAGE_RULES.items():
            lin = set(find_cleavage_sites(seq, rule))
            cir = set(find_cleavage_sites(seq, rule, circular=True))
            assert lin <= cir, (seq, name)
            # o único sítio novo possível é o do fechamento (i = n-1 para cut_after;
            # para pepsina (cut_before), o resíduo 0 gera o sítio n-1)
            assert cir - lin <= {n - 1}, (seq, name, cir - lin)

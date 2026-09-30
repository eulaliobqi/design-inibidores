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

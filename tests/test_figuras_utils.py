import pytest

from scripts.figuras_utils import classify_stability, require_key

def test_classify_estavel_reprodutivel():
    assert classify_stability(mean_nm=0.214, std_nm=0.025) == "ESTAVEL_REPRODUTIVEL"

def test_classify_marginal_por_dp_baixo_mas_media_alta():
    # SEEEVLAANEAYAAAHTAYN real: media 0.729, DP 0.041 -> falha o teto de media (<0.30)
    assert classify_stability(mean_nm=0.729, std_nm=0.041) == "MARGINAL_REPRODUTIVEL"

def test_classify_alta_variancia():
    # RLREELKKAEEWLEKRRKEE real: media 0.810, DP 0.606
    assert classify_stability(mean_nm=0.810, std_nm=0.606) == "ALTA_VARIANCIA"

def test_classify_marginal_dp_medio():
    # HRPRRPK real: media 0.421, DP 0.092 -> DP<0.10 mas nao <0.05, e media>0.30
    assert classify_stability(mean_nm=0.421, std_nm=0.092) == "MARGINAL_REPRODUTIVEL"

def test_require_key_retorna_valor_quando_presente():
    # md_results.json[SRTRR] real (formato do dado real usado na Fig 1)
    d = {"SRTRR": {"rmsd_avg_nm": 0.214}}
    assert require_key(d, "SRTRR", "md_results.json[SRTRR]") == {"rmsd_avg_nm": 0.214}

def test_require_key_levanta_runtimeerror_com_contexto_quando_ausente():
    d = {"SRTRR": {"rmsd_avg_nm": 0.214}}
    with pytest.raises(RuntimeError, match="VRRPR"):
        require_key(d, "VRRPR", "md_results.json[VRRPR]")

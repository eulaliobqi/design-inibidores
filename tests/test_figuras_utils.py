from scripts.figuras_utils import classify_stability

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

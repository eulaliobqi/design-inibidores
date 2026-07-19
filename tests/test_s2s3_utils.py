from scripts.s2s3_utils import define_s2s3_residues

def test_define_s2s3_residues_acr157_real_data():
    # Dado real de outputs/structure/binding_site.json, individual_sites[0] (ACR157)
    binding_site = {
        "triad_resseqs": {"HIS": 46, "ASP": 91, "SER": 203},
        "s1_asp_resseq": 187,
        "hotspot_resseqs": [44, 45, 46, 47, 83, 88, 91, 92, 188, 189, 201, 202, 203, 204, 218],
    }
    # Ser+1..Ser+15 = 204..218, excluindo vizinhança do S1 Asp (187 +-2 = 185-189)
    # e do proprio catalitico (201-203) -> sobra 204 e 218 no hotspot real
    assert define_s2s3_residues(binding_site) == [204, 218]

def test_define_s2s3_residues_excludes_s1_neighborhood():
    binding_site = {
        "triad_resseqs": {"HIS": 10, "ASP": 15, "SER": 20},
        "s1_asp_resseq": 25,  # dentro de Ser+1..Ser+15 (21-35) -> 25 +-2 (23-27) excluido
        "hotspot_resseqs": [21, 25, 26, 35, 40],
    }
    # 21: sobrevive (fora da zona 23-27). 25/26: excluidos (dentro da zona).
    # 35: sobrevive (ultimo residuo da janela Ser+15, fora da zona). 40: fora da janela.
    assert define_s2s3_residues(binding_site) == [21, 35]

"""Definição operacional dos subsítios S2'/S3' canônicos (Frente 3).

Sem estrutura cristalográfica com substrato ligado nos receptores deste projeto
(modelos AlphaFold/estruturais), não há posição canônica pronta. Heurística
geométrica+sequencial (aprovada pelo usuário, ver spec 2026-07-19): dos resíduos
já no hotspot 8 A de cada receptor, os que ficam na vizinhança sequencial da Ser
catalítica (Ser+1 a Ser+15) e fora da vizinhança imediata do Asp do bolso S1
(+-2 resíduos) são candidatos a revestir S2'/S3'. Ressalva explícita: é
aproximação, não validação estrutural externa — mesmo tratamento dado ao
mapeamento fraco do sítio S'2 no projeto irmão analise-alosterica.
"""

S2S3_WINDOW = 15
S1_EXCLUSION_RADIUS = 2


def define_s2s3_residues(binding_site: dict) -> list:
    ser = binding_site["triad_resseqs"]["SER"]
    s1_asp = binding_site["s1_asp_resseq"]
    hotspot = binding_site["hotspot_resseqs"]
    s1_zone = set(range(s1_asp - S1_EXCLUSION_RADIUS, s1_asp + S1_EXCLUSION_RADIUS + 1))
    candidates = [
        r for r in hotspot
        if ser < r <= ser + S2S3_WINDOW and r not in s1_zone
    ]
    return sorted(candidates)

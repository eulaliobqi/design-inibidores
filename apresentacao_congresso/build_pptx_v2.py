"""Versao 2 da apresentacao de congresso (15 slides + 1 de referencias).

Estrutura pedida pelo autor: problema (perda, manejo) -> solucao natural (peptideos inibidores,
ancoragem) -> resultados do grupo -> objetivos -> metodo (fluxograma, ferramentas, calibracao,
filtrados) -> dinamica -> melhores candidatos -> filme -> conclusao.

Regras: so dado real (manuscrito, JSON, PubMed/Crossref, PDB); referencia em todo slide;
fundo branco, paleta Okabe-Ito, titulo em frase afirmativa.

Uso (da raiz do projeto): python apresentacao_congresso/build_pptx_v2.py
"""
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

AQUI = Path(__file__).resolve().parent
FIG = AQUI / "figuras"
IMG = AQUI / "imagens"
SAIDA = AQUI / "Apresentacao_congresso_v2.pptx"

LARG, ALT = Inches(13.333), Inches(7.5)
MARGEM = Inches(0.78)

GRAF = RGBColor(0x1F, 0x23, 0x28)
AZUL = RGBColor(0x00, 0x72, 0xB2)
VERDE = RGBColor(0x2A, 0x9D, 0x8F)
LARA = RGBColor(0xD5, 0x5E, 0x00)
AMAR = RGBColor(0xA8, 0x70, 0x00)
CINZA = RGBColor(0x5A, 0x5F, 0x66)
CLARO = RGBColor(0x8A, 0x90, 0x97)
FUNDO = RGBColor(0xF4, 0xF6, 0xF8)
FONTE = "Segoe UI"


def caixa(slide, x, y, cx, cy, texto, tam, cor=GRAF, negrito=False, alinha=PP_ALIGN.LEFT,
          italico=False, espaco=1.0):
    tb = slide.shapes.add_textbox(x, y, cx, cy)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, linha in enumerate(texto.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = alinha
        p.line_spacing = espaco
        r = p.add_run()
        r.text = linha
        r.font.size = Pt(tam)
        r.font.bold = negrito
        r.font.italic = italico
        r.font.name = FONTE
        r.font.color.rgb = cor
    return tb


def regua(slide, x, y, cx, cor=AZUL, espessura=Pt(3)):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, cx, espessura)
    s.fill.solid()
    s.fill.fore_color.rgb = cor
    s.line.fill.background()
    s.shadow.inherit = False
    return s


def bloco(slide, x, y, cx, cy, cor=FUNDO):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, cx, cy)
    s.fill.solid()
    s.fill.fore_color.rgb = cor
    s.line.fill.background()
    s.shadow.inherit = False
    return s


def nova(prs, numero=None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    fundo = slide.background.fill
    fundo.solid()
    fundo.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    if numero is not None:
        caixa(slide, LARG - Inches(1.0), ALT - Inches(0.46), Inches(0.5), Inches(0.3),
              str(numero), 11, CLARO, alinha=PP_ALIGN.RIGHT)
    return slide


TOPO = Inches(1.95)


def titulo(slide, frase, apoio=None):
    global TOPO
    caixa(slide, MARGEM, Inches(0.52), LARG - 2 * MARGEM, Inches(1.0), frase, 25, GRAF, negrito=True, espaco=1.08)
    regua(slide, MARGEM, Inches(0.40), Inches(0.9))
    if apoio:
        caixa(slide, MARGEM, Inches(1.58), LARG - 2 * MARGEM, Inches(0.6), apoio, 15, CINZA, espaco=1.18)
        TOPO = Inches(2.35)
    else:
        TOPO = Inches(1.95)


LONGOS = []


def rodape(slide, texto):
    if len(texto) > 175:
        LONGOS.append((len(texto), texto[:60]))
    caixa(slide, MARGEM, ALT - Inches(0.55), LARG - 2 * MARGEM - Inches(0.7), Inches(0.4),
          texto, 10, CLARO, espaco=1.1)


def figura(slide, arquivo, topo, largura_max=None, altura_max=None, x=None):
    p = FIG / arquivo if (FIG / arquivo).exists() else IMG / arquivo
    w, h = Image.open(p).size
    largura_max = largura_max or (LARG - 2 * MARGEM)
    altura_max = altura_max or (Inches(6.85) - topo)
    esc = min(largura_max / w, altura_max / h)
    cx, cy = int(w * esc), int(h * esc)
    px = x if x is not None else int((LARG - cx) / 2)
    return slide.shapes.add_picture(str(p), px, topo + int((altura_max - cy) / 2), cx, cy)


def notas(slide, texto):
    slide.notes_slide.notes_text_frame.text = texto


def chip(slide, x, y, cx, numero, texto, cor, tam_n=30, tam_t=14.5, alt=Inches(1.05)):
    regua(slide, x, y, Inches(0.06), cor, alt)
    caixa(slide, x + Inches(0.22), y - Inches(0.02), cx - Inches(0.22), Inches(0.55), numero, tam_n, cor, negrito=True)
    caixa(slide, x + Inches(0.22), y + Inches(0.5), cx - Inches(0.22), alt, texto, tam_t, GRAF, espaco=1.18)


prs = Presentation()
prs.slide_width, prs.slide_height = LARG, ALT

# =============================================================== 1. capa ====
s = nova(prs)
regua(s, MARGEM, Inches(1.62), Inches(2.2), AZUL, Pt(4))
caixa(s, MARGEM, Inches(2.02), Inches(10.6), Inches(2.4),
      "Desenho Racional de Inibidores\nPeptídicos de Tripsinas contra\nLepidoptera por Inteligência\nArtificial Generativa",
      35, GRAF, negrito=True, espaco=1.12)
caixa(s, MARGEM, Inches(4.92), Inches(10.4), Inches(0.5),
      "Da tripsina digestiva ao peptídeo candidato ordenado: uma plataforma computacional", 16.5, CINZA)
caixa(s, MARGEM, Inches(5.82), Inches(9.0), Inches(1.0),
      "Eulálio Santos\nUniversidade Federal de Viçosa  ·  eulalio.santos@ufv.br", 14, GRAF, espaco=1.35)
caixa(s, LARG - MARGEM - Inches(2.6), Inches(6.28), Inches(2.6), Inches(0.3),
      "Outubro de 2026", 14, CLARO, alinha=PP_ALIGN.RIGHT)
notas(s, "15 s. Vou contar como saímos da enzima digestiva de uma lagarta até peptídeos candidatos ordenados, "
         "e o que cada número desse caminho sustenta.")

# ====================================================== 2. perda agricola ====
s = nova(prs, 2)
titulo(s, "Pragas e doenças tiram cerca de um quinto da soja mundial, e as lagartas estão entre as principais pragas")
_w, _h = Image.open(IMG / "desfolha.png").size
_alt = Inches(4.2)
_lar = int(_alt * _w / _h)
s.shapes.add_picture(str(IMG / "desfolha.png"), MARGEM, Inches(2.15), _lar, _alt)
_x = MARGEM + _lar + Inches(0.55)
_cx = LARG - _x - MARGEM
chip(s, _x, Inches(2.15), _cx, "21,4%",
     "da produtividade mundial da soja se perde para pragas e patógenos (faixa de 11,0 a 32,4%)", AZUL)
chip(s, _x, Inches(3.55), _cx, "US$ 17,7 bilhões por ano",
     "é o custo dos insetos-praga à agricultura brasileira, 7,7% da produção (todas as culturas)", LARA, tam_n=26)
chip(s, _x, Inches(4.95), _cx, "180,4 milhões de t",
     "de soja na safra 2025/26 do Brasil: é muito a proteger", VERDE, tam_n=26)
rodape(s, "Savary et al. 2019, Nat. Ecol. Evol. 3:430  ·  Oliveira et al. 2014, Crop Prot. 56:50  ·  "
          "Conab, set. 2026  ·  Carpane et al. 2022, PLOS ONE 17:e0271084  ·  imagem ilustrativa gerada por IA")
notas(s, "40 s. Savary 2019: estimativa de especialistas para pragas e patógenos juntos, 21,4% (11,0 a 32,4%) na soja. "
         "Oliveira 2014: todas as culturas e todos os insetos, não só lagartas: US$ 17,7 bilhões/ano e 7,7% da produção. "
         "Carpane 2022: lepidópteros são fatores limitantes da produtividade da soja na América do Sul. "
         "Não afirmar um percentual de perda só por lagartas: a literatura consultada não dá um número único.")

# ============================================================ 3. manejo ====
s = nova(prs, 3)
titulo(s, "O controle atual cobra um preço: resistência, refúgio e lagartas que escapam do Bt",
       "A pressão de seleção e a durabilidade das táticas atuais pedem uma ferramenta com outro modo de ação.")
col = (LARG - 2 * MARGEM - Inches(1.0)) / 3
for i, (palavra, tit, txt, cor) in enumerate([
    ("Resistência", "Inseticida químico",
     "Afeta organismos não alvo, pode provocar surtos de pragas e seleciona populações resistentes.", LARA),
    ("Refúgio", "Soja Bt (Cry1Ac)",
     "Evento de alta dose para a lagarta-da-soja, mas depende de refúgio e de plano de manejo para durar.", LARA),
    ("Escape", "Nem toda lagarta é contida",
     "Spodoptera eridania, S. cosmioides e S. frugiperda também desfolham a soja Bt (IPRO).", LARA),
]):
    x = MARGEM + i * (col + Inches(0.5))
    regua(s, x, Inches(3.0), col, cor, Pt(2.5))
    caixa(s, x, Inches(3.25), col, Inches(0.7), palavra, 32, cor, negrito=True)
    caixa(s, x, Inches(4.1), col, Inches(0.5), tit, 17, GRAF, negrito=True)
    caixa(s, x, Inches(4.65), col, Inches(1.8), txt, 15, GRAF, espaco=1.3)
rodape(s, "Ongaratto et al. 2021, J. Econ. Entomol. (doi 10.1093/jee/toab197)  ·  "
          "Carpane et al. 2022, PLOS ONE 17:e0271084 (doi 10.1371/journal.pone.0271084)")
notas(s, "35 s. O foco é o problema do manejo. Ser explícito: não estou afirmando que a lagarta-da-soja já é resistente "
         "ao Cry1Ac; estou dizendo que as duas táticas carregam custo de manejo (seleção, refúgio) e que, segundo "
         "Carpane 2022, as Spodoptera desfolham também a soja Bt IPRO.")

# ========================================== 4. peptideos/inibidores naturais ====
s = nova(prs, 4)
titulo(s, "A própria planta já se defende: inibidores de protease bloqueiam a digestão da lagarta",
       "O inibidor de Kunitz da soja reduziu a sobrevivência das larvas de A. gemmatalis em ensaio biológico.")
figura(s, "v2_naturais.png", TOPO, altura_max=Inches(3.95))
caixa(s, MARGEM, Inches(6.5), LARG - 2 * MARGEM, Inches(0.3),
      "mesma escala  ·  do peptídeo cíclico de 14 resíduos à proteína de 172: o menor é o mais barato de produzir",
      13, CINZA, italico=True, alinha=PP_ALIGN.CENTER)
rodape(s, "Luckett et al. 1999 (SFTI-1, PDB 1SFI)  ·  Werner & Wemmer 1992 (BBI, 1BBI)  ·  Song & Suh 1998 (SKTI, 1AVU)  ·  "
          "Almeida Barros et al. 2022, Pestic. Biochem. Physiol. 187:105188")
notas(s, "40 s. Mostrar as três estruturas reais do PDB na mesma escala: o SFTI-1 do girassol tem 14 resíduos e é cíclico; "
         "o Bowman-Birk da soja tem 71; o Kunitz da soja tem 172. As larvas se adaptam a inibidores vegetais, "
         "induzindo proteases insensíveis (Jongsma 1995): por isso interessa o peptídeo curto desenhado.")

# =========================================================== 5. ancoragem ====
s = nova(prs, 5)
titulo(s, "O inibidor ancora na tripsina: a lisina entra no bolso S1 e encontra o Asp189")
figura(s, "v2_ancoragem.png", TOPO, largura_max=Inches(7.4), altura_max=Inches(4.85), x=MARGEM)
_x = MARGEM + Inches(7.7)
_cx = LARG - _x - MARGEM
chip(s, _x, Inches(2.1), _cx, "P1 → S1", "O resíduo P1 do inibidor (Lys ou Arg) se insere no bolso S1 da tripsina", LARA, alt=Inches(1.0))
chip(s, _x, Inches(3.5), _cx, "Asp189", "A carga negativa no fundo do bolso atrai a cadeia lateral positiva", RGBColor(0xC0, 0x39, 0x2B), alt=Inches(1.0))
chip(s, _x, Inches(4.9), _cx, "Ser195 · His57", "A tríade catalítica fica ao lado da ligação que a enzima cortaria", AMAR, alt=Inches(1.0))
rodape(s, "Estrutura 1SFI: tripsina bovina + SFTI-1 (Luckett et al. 1999)  ·  Laskowski & Kato 1980  ·  "
          "Perona & Craik 1995  ·  Hedstrom 2002  ·  numeração da tripsina bovina")
notas(s, "40 s. Explicar para leigos: a tripsina corta a proteína depois de lisina ou arginina porque o fundo do bolso S1 "
         "tem um aspartato negativo. O inibidor canônico usa o mesmo encaixe, mas a ligação dele resiste ao corte. "
         "Guardar este fato: ele é o nó do desenho (o que ancora é o que a enzima corta).")

# ========================================================= 6. nosso grupo ====
s = nova(prs, 6)
titulo(s, "No nosso grupo, peptídeos curtos inibem as tripsinas e desorganizam o intestino da lagarta mais que o inibidor da soja",
       "Potência ainda milimolar: há espaço para desenhar peptídeos melhores.")
figura(s, "v2_grupo.png", TOPO, altura_max=Inches(4.3))
rodape(s, "Almeida Barros et al. 2021, Pest Manag. Sci. 77:1714 (GORE1, GORE2)  ·  "
          "Mariano et al. 2026, Arch. Insect Biochem. Physiol. 123:e70224  ·  Júnior et al. 2026, ibid. 123:e70223")
notas(s, "45 s. Resultados publicados do grupo, todos em A. gemmatalis. GORE1 e GORE2: inibidores competitivos reversíveis, "
         "Ki 0,49 e 0,10 mM, que prejudicam sobrevivência e desenvolvimento das larvas (Almeida Barros 2021). "
         "Peptídeos da pró-região do tripsinogênio: Ki 0,78 a 1,80 mM (Mariano 2026). "
         "Júnior 2026 (RNA-seq, bioquímica e histologia): o SKTI induziu serina-proteases e enzimas antioxidantes (compensação); "
         "o GORE-2 reprimiu proteases digestivas, induziu menos antioxidantes e causou mais lesão histológica. "
         "HONESTIDADE: não dizer que o peptídeo é mais potente que o inibidor vegetal; a vantagem medida é menor compensação "
         "fisiológica e maior lesão, não menor Ki.")

# ============================================================ 7. objetivos ====
s = nova(prs, 7)
titulo(s, "Objetivo: desenhar com IA generativa peptídeos curtos que inibam as tripsinas das lagartas e resistam à digestão")
for i, (n, txt, cor) in enumerate([
    ("1", "Mapear o sítio ativo das tripsinas de 8 lagartas-praga da soja", AMAR),
    ("2", "Gerar peptídeos de novo por difusão e filtrá-los por regras de não clivabilidade", AZUL),
    ("3", "Ordenar os candidatos por simulação: linear × cíclico, pH 10,0 × pH 8,2", VERDE),
]):
    y = Inches(2.3) + i * Inches(1.45)
    caixa(s, MARGEM, y - Inches(0.1), Inches(1.0), Inches(1.0), n, 54, cor, negrito=True)
    regua(s, MARGEM + Inches(1.0), y, Pt(3), cor, Inches(0.95))
    caixa(s, MARGEM + Inches(1.4), y + Inches(0.12), Inches(10.2), Inches(0.9), txt, 24, GRAF, espaco=1.15)
rodape(s, "Objetivos (i) a (vi) da Seção 1 do manuscrito  ·  trabalho inteiramente computacional")
notas(s, "30 s. Três objetivos, na ordem do que será mostrado: alvo, geração com filtro, simulação e ordenação. "
         "Frente L = peptídeo linear; frente M = peptídeo cíclico cabeça-cauda. Dois pH: 10,0 (intestino) e 8,2 (ensaio).")

# ========================================================== 8. fluxograma ====
s = nova(prs, 8)
titulo(s, "Do alvo ao candidato: IA generativa guiada por regras, em duas frentes e dois pH")
figura(s, "v2_fluxo.png", TOPO)
rodape(s, "RFdiffusion: Watson et al. 2023  ·  ProteinMPNN: Dauparas et al. 2022  ·  Boltz-2: Passaro et al. 2025  ·  "
          "GROMACS: Abraham et al. 2015  ·  CHARMM36: Huang & MacKerell 2013  ·  PRODIGY: Vangone & Bonvin 2015")
notas(s, "50 s. Percorrer o fluxo da esquerda para a direita. Mapear o alvo e calibrar; gerar esqueletos com RFdiffusion; "
         "escrever sequências com ProteinMPNN; filtrar por regra (nenhum resíduo que as proteases do intestino cortam em P1). "
         "O que sobra é lido de duas formas químicas: frente L (linear) e frente M (cíclica). Cada frente leva 24 candidatos "
         "a simulação de 10 ns em dois pH e a um ranking por MM-GBSA e PRODIGY.")

# =================================================== 9. resultados por etapa ====
s = nova(prs, 9)
titulo(s, "Cada ferramenta estreitou a busca: de 880 esqueletos a 4 candidatos")
figura(s, "v2_resultados.png", TOPO)
rodape(s, "Manuscrito, Seções 3.1 a 3.8 (Tabelas 1, 3 e 4)  ·  contagens de L e M são pares sequência–alvo; "
          "as 527 da frente L estão também na frente M")
notas(s, "45 s. Números resumidos, sem figuras ainda. Dez receptores (oito alvos e duas referências), 20 de 20 pares receptor–molde "
         "aceitos. 880 esqueletos; 22.066 sequências únicas; o critério duro deixou 527 lineares e 543 cíclicas (cerca de 2,4%). "
         "Escolhemos 24 por frente para simular; 48 complexos x 2 pH = 96 simulações de 10 ns; quatro candidatos sobreviveram "
         "a todos os filtros disponíveis.")

# ============================================================ 10. calibracao ====
s = nova(prs, 10)
titulo(s, "Antes de usar os escores, calibramos com inibidores reais e iscas embaralhadas")
figura(s, "fig_calibracao.png", TOPO, largura_max=Inches(6.9), altura_max=Inches(4.5), x=MARGEM)
_x = MARGEM + Inches(7.2)
_cx = LARG - _x - MARGEM
chip(s, _x, Inches(2.0), _cx, "10 de 10", "pares em que o inibidor real pontua acima da sua isca embaralhada", AZUL, alt=Inches(0.9), tam_t=14)
chip(s, _x, Inches(3.3), _cx, "só em pares", "as faixas se sobrepõem (0,853–0,986 × 0,628–0,944): confiança não é afinidade", LARA, alt=Inches(0.9), tam_t=14, tam_n=26)
chip(s, _x, Inches(4.6), _cx, "527 L · 543 M", "restam após o critério: sem K R F Y W L M A V em P1 e sem cisteína", VERDE, alt=Inches(0.9), tam_t=14, tam_n=26)
rodape(s, "Manuscrito, Seções 3.2 e 3.3 (Figura 2, Tabela 2)  ·  Boltz-2: Passaro et al. 2025  ·  "
          "6 inibidores: BPTI, SFTI-1, SKTI, BBI, EcTI, ApTI")
notas(s, "45 s. O Boltz-2 devolve uma confiança, não uma afinidade. Comparamos seis inibidores reais com iscas embaralhadas "
         "da mesma composição: o real ganhou em 10 de 10 pares, mas as faixas absolutas se sobrepõem; uma isca chegou a 0,944. "
         "Por isso, daqui em diante, cada candidato é comparado a controles pareados no mesmo receptor. "
         "Critérios: K, R, F, Y, W, L, M, A, V proibidos em P1 (tripsina, quimotripsina/elastase) e sem cisteína. "
         "Frentes restantes: 527 lineares e 543 cíclicas.")

# =========================================================== 11. filtrados ====
s = nova(prs, 11)
titulo(s, "Quem passou no filtro é curto e rico em glicina: 7,7 resíduos em média e 49,4% de glicina")
figura(s, "fig_composicao.png", TOPO, altura_max=Inches(3.4))
_cx = (LARG - 2 * MARGEM - Inches(0.8)) / 3
chip(s, MARGEM, Inches(5.5), _cx, "7,7 resíduos", "comprimento médio; 81,6% das lineares têm 8 ou menos", AZUL, alt=Inches(0.75), tam_t=13.5, tam_n=24)
chip(s, MARGEM + _cx + Inches(0.4), Inches(5.5), _cx, "49,4% Gly", "dos 4.060 resíduos, seguida de Ser (11,7%) e Pro (9,8%)", VERDE, alt=Inches(0.75), tam_t=13.5, tam_n=24)
chip(s, MARGEM + 2 * (_cx + Inches(0.4)), Inches(5.5), _cx, "9 de 4.060", "resíduos são K ou R (0,22%), cada um seguido de prolina", LARA, alt=Inches(0.75), tam_t=13.5, tam_n=24)
rodape(s, "Manuscrito, Seção 3.3 e Figura S3  ·  o enriquecimento em glicina é consequência da regra, não evidência de estabilidade")
notas(s, "40 s. Por que passaram: a regra proíbe os nove resíduos que as proteases do intestino assumem em P1, sobram resíduos "
         "pequenos (glicina, serina, prolina, treonina, aspartato). É o preço do filtro: ao proibir K e R, proíbe-se justamente "
         "o resíduo que melhor ancora em S1. Os poucos K/R que restam (0,22%) vêm protegidos por uma prolina seguinte, "
         "que é só uma barreira estatística, não proteção absoluta.")

# ============================================================== 12. dinamica ====
s = nova(prs, 12)
titulo(s, "A dinâmica confirmou poses, não ligação: poucos peptídeos mantêm o bolso S1, nas duas frentes e nos dois pH")
figura(s, "v2_md_resumo.png", TOPO, largura_max=Inches(6.6), altura_max=Inches(4.3), x=MARGEM)
_x = MARGEM + Inches(6.9)
_cx = LARG - _x - MARGEM
chip(s, _x, Inches(2.0), _cx, "5 de 9 × 0 de 39", "ocupância ≥ 0,70 em quem partiu a ≤ 4 Å do Asp189 × quem partiu mais longe", LARA, alt=Inches(0.95), tam_t=14, tam_n=26)
chip(s, _x, Inches(3.4), _cx, "pH sem efeito líquido", "pH 8,2 × 10,0: distância final P = 0,16; ocupância P = 0,88", AZUL, alt=Inches(0.95), tam_t=14, tam_n=26)
chip(s, _x, Inches(4.8), _cx, "2 de 48", "NGGRPDAP e GGKPGEP mantêm S1 nos dois pH", VERDE, alt=Inches(0.95), tam_t=14, tam_n=26)
rodape(s, "Manuscrito, Seções 3.5 e 3.7 (Figuras 5 e 7)  ·  GROMACS 2025.4, CHARMM36, 10 ns, uma execução por candidato e pH  ·  "
          "ocupância de S1: fração dos quadros da 2ª metade com a âncora a ≤ 5 Å do Asp189")
notas(s, "50 s. Frentes L (linear) e M (cíclica) e dois pH, 24 simulações em cada barra. No pH 10,0, 5 de 48 mantêm S1 "
         "(2 lineares, 3 cíclicas); no pH 8,2, 6 de 48 (1 linear, 5 cíclicas). A pose inicial decide: 5 de 9 que partiram a até 4 Å "
         "contra 0 de 39 mais longe. 10 ns verificam se uma pose sobrevive; não dão tempo de achar o bolso. Entre os pH não há "
         "diferença em nenhum teste pareado, e só dois peptídeos repetem S1 nos dois. Repetir a mesma simulação já muda a "
         "ocupância em mais de 0,5 em 3 de 16 pares: uma execução não decide.")

# =========================================================== 13. candidatos ====
s = nova(prs, 13)
titulo(s, "Melhores candidatos por frente: só NGGRPDAP e GGKPGEP mantêm o bolso S1 nos dois pH")
cands = [
    ("NGGRPDAP", "linear · A. gemmatalis", AZUL,
     [("S1", "1,00 | 0,98 (rep. 1,00)"), ("MM-GBSA", "−45,3 | −53,3"),
      ("PRODIGY", "−11,1"), ("Contatos", "Arg4–Asp189 (sal) · Pro5–Gly234 · Gly3–Gly215")]),
    ("GQNDS", "linear · O. nubilalis", AZUL,
     [("S1", "1,00 | 0,04 (rep. 0,73)"), ("MM-GBSA", "−18,2 | −2,0"),
      ("PRODIGY", "−9,0"), ("Contatos", "Gln2–Gln208 · Gln2–Gly232 · Asn3–Ser228")]),
    ("GGKPGEP", "cíclico · A. gemmatalis", VERDE,
     [("S1", "1,00 | 1,00 (rep. 1,00)"), ("MM-GBSA", "−35,4 | −27,7"),
      ("PRODIGY", "−9,7"), ("Contatos", "Lys3–Asp189 (sal) · Lys3–Gly236 · Lys3–Ile235")]),
    ("GGHSE", "cíclico · S. frugiperda", VERDE,
     [("S1", "0,99 | 0,00 (rep. 0,88)"), ("MM-GBSA", "−26,5 | −23,9"),
      ("PRODIGY", "−8,8"), ("Contatos", "His3–Asp189 · Gly2–Gln217 · His3–Ser220")]),
]
_gap = Inches(0.22)
_cw = int((LARG - 2 * MARGEM - 3 * _gap) / 4)
for i, (nome, sub, cor, linhas) in enumerate(cands):
    x = MARGEM + i * (_cw + _gap)
    regua(s, x, Inches(1.62), _cw, cor, Pt(3))
    caixa(s, x, Inches(1.72), _cw, Inches(0.4), nome, 19, cor, negrito=True)
    caixa(s, x, Inches(2.12), _cw, Inches(0.3), sub, 12.5, CINZA, italico=True)
    p = FIG / f"v2_pose_{nome}.png"
    w, h = Image.open(p).size
    ch = int(_cw * h / w)
    s.shapes.add_picture(str(p), x, Inches(2.5), _cw, ch)
    y = Inches(2.5) + ch + Inches(0.1)
    for rot, val in linhas:
        caixa(s, x, y, int(_cw * 0.32), Inches(0.3), rot, 11, CLARO)
        caixa(s, x + int(_cw * 0.32), y, int(_cw * 0.68), Inches(0.6), val, 12, GRAF, espaco=1.05)
        y += Inches(0.4) if rot != "Contatos" else Inches(0.7)
caixa(s, MARGEM, Inches(6.5), LARG - 2 * MARGEM, Inches(0.3),
      "Pose aos 10 ns (pH 10,0)  ·  S1 e MM-GBSA: pH 10,0 | pH 8,2  ·  S1 = ocupância na 2ª metade; rep. = repetição  ·  energias em kcal/mol",
      11, CLARO)
rodape(s, "Manuscrito, Tabela 4 e Seções 3.6 a 3.8  ·  MM-GBSA e PRODIGY ordenam candidatos, não estimam afinidade  ·  "
          "Asp189 = resíduo de S1 (Asp211, 207 e 214 no modelo); demais resíduos na numeração do modelo")
notas(s, "50 s. Dois candidatos por frente. NGGRPDAP (linear, A. gemmatalis): Arg em S1 seguida de prolina, com salt bridge a Asp189 "
         "em 100% dos quadros finais, MM-GBSA mais favorável das 48 simulações de pH 8,2. GQNDS (linear, O. nubilalis): ancora em Gln, "
         "mantém S1 em pH 10,0, mas não no pH 8,2 da execução principal (0,04) e só em parte na repetição (0,73). "
         "GGKPGEP (cíclico, A. gemmatalis): Lys em S1 seguida de prolina, menor distância final ao Asp189, 2,71 Å; anel abaixo do limite "
         "estrito de ω em pH 10,0. GGHSE (cíclico, S. frugiperda): única simulação de pH 10,0 que combinou ocupância com anel estrito; "
         "saiu de S1 no pH 8,2 (0,00) e voltou na repetição (0,88). Contatos: ligações de hidrogênio e pontes salinas "
         "≥ 70% dos quadros de 8 a 10 ns (pH 10,0). Nenhum candidato carrega alegação de seletividade ou atividade.")

# ================================================================ 14. filme ====
s = nova(prs, 14)
titulo(s, "Os quatro candidatos em movimento: 10 ns de dinâmica molecular (pH 10,0)")
_vw = LARG - 2 * MARGEM
_vh = int(_vw * 394 / 1360)
s.shapes.add_movie(str(IMG / "md_4candidatos_5s.mp4"), MARGEM, Inches(2.0), _vw, _vh,
                   poster_frame_image=str(IMG / "md_4candidatos_poster.png"), mime_type="video/mp4")
caixa(s, MARGEM, Inches(2.0) + _vh + Inches(0.2), _vw, Inches(0.8),
      "Quadros reais da trajetória, a cada 0,1 ns, alinhados no esqueleto do receptor.\n"
      "Vermelho: Asp189 (S1)  ·  amarelo: Ser195 e His57  ·  laranja: resíduo âncora do peptídeo",
      14, CINZA, alinha=PP_ALIGN.CENTER, espaco=1.3)
rodape(s, "Simulações: GROMACS 2025.4, CHARMM36, 10 ns, uma execução por candidato  ·  render: PyMOL  ·  "
          "NGGRPDAP e GQNDS (linear), GGKPGEP e GGHSE (cíclico)  ·  arquivo GIF: md_4candidatos_5s.gif")
notas(s, "20 s. Clique no vídeo para tocar (5 s). Cada quadro é um instante real da simulação, sem interpolação; o receptor está fixo. "
         "O GIF equivalente está na pasta imagens/ caso o vídeo não toque.")

# ============================================================== 15. conclusao ====
s = nova(prs, 15)
titulo(s, "Plataforma pronta, quatro candidatos ordenados e um teste decisivo pela frente")
_cw = (LARG - 2 * MARGEM - Inches(0.9)) / 3
for i, (n, t, cor) in enumerate([
    ("8 × 2 × 2", "espécies, frentes e pH: 96 simulações num fluxo reprodutível, do alvo ao ranking", AZUL),
    ("4 candidatos", "NGGRPDAP · GQNDS · GGKPGEP · GGHSE, ordenados por critérios declarados de antemão", VERDE),
    ("Próximo: o ensaio", "Ki e estabilidade em extrato de intestino, com o GORE2 como controle positivo", LARA),
]):
    x = MARGEM + i * (_cw + Inches(0.45))
    regua(s, x, Inches(1.95), _cw, cor, Pt(3))
    caixa(s, x, Inches(2.1), _cw, Inches(0.6), n, 26, cor, negrito=True)
    caixa(s, x, Inches(2.8), _cw, Inches(1.2), t, 15, GRAF, espaco=1.25)
_pw = Inches(8.4)
_ph = int(_pw * 394 / 1360)
s.shapes.add_picture(str(IMG / "md_4candidatos_poster.png"), int((LARG - _pw) / 2), Inches(4.05), _pw, _ph)
rodape(s, "Todos os resultados são computacionais: nenhum ensaio de atividade ou de seletividade foi feito  ·  "
          "Manuscrito, Seções 4.4, 4.5 e 5")
notas(s, "40 s. Mensagem final. A plataforma existe, roda para oito espécies e é transferível a outro alvo. Entrega quatro "
         "candidatos ordenados, sem alegação de atividade nem de seletividade. O próximo passo é enzimático: um candidato só interessa "
         "se o Ki medido nas mesmas condições ficar abaixo da faixa milimolar do GORE2, ou se persistir mais tempo no extrato "
         "de intestino. Obrigado.")

# ============================================================ 16. referencias ====
s = nova(prs, 16)
titulo(s, "Referências")
refs = [
    "Savary S et al. (2019) Nat Ecol Evol 3:430–439. doi:10.1038/s41559-018-0793-y",
    "Oliveira CM et al. (2014) Crop Prot 56:50–54. doi:10.1016/j.cropro.2013.10.022",
    "Carpane P et al. (2022) PLOS ONE 17:e0271084. doi:10.1371/journal.pone.0271084",
    "Ongaratto S et al. (2021) J Econ Entomol. doi:10.1093/jee/toab197",
    "Conab (2026) Acompanhamento da safra brasileira de grãos, set. 2026",
    "Luckett S et al. (1999) J Mol Biol 290:525–533. doi:10.1006/jmbi.1999.2891",
    "Werner MH, Wemmer DE (1992) Biochemistry 31:999–1010. doi:10.1021/bi00119a008",
    "Song HK, Suh SW (1998) J Mol Biol 275:347–363. doi:10.1006/jmbi.1997.1469",
    "Almeida Barros R et al. (2022) Pestic Biochem Physiol 187:105188. doi:10.1016/j.pestbp.2022.105188",
    "Laskowski M, Kato I (1980) Annu Rev Biochem 49:593–626. doi:10.1146/annurev.bi.49.070180.003113",
    "Perona JJ, Craik CS (1995) Protein Sci 4:337–360. doi:10.1002/pro.5560040301",
    "Hedstrom L (2002) Chem Rev 102:4501–4524. doi:10.1021/cr000033x",
    "Almeida Barros R et al. (2021) Pest Manag Sci 77:1714–1723. doi:10.1002/ps.6191",
    "Júnior NRS et al. (2026) Arch Insect Biochem Physiol 123:e70223. doi:10.1002/arch.70223",
    "Mariano GA et al. (2026) Arch Insect Biochem Physiol 123:e70224. doi:10.1002/arch.70224",
    "Dow JAT (1992) J Exp Biol 172:355–375. doi:10.1242/jeb.172.1.355",
    "Watson JL et al. (2023) Nature 620:1089–1100. doi:10.1038/s41586-023-06415-8",
    "Dauparas J et al. (2022) Science 378:49–56. doi:10.1126/science.add2187",
    "Passaro S et al. (2025) bioRxiv. doi:10.1101/2025.06.14.659707",
    "Abraham MJ et al. (2015) SoftwareX 1–2:19–25. doi:10.1016/j.softx.2015.06.001",
    "Huang J, MacKerell AD (2013) J Comput Chem 34:2135–2145. doi:10.1002/jcc.23354",
    "Vangone A, Bonvin AMJJ (2015) eLife 4:e07454. doi:10.7554/eLife.07454",
]
metade = (len(refs) + 1) // 2
for k, bloco_refs in enumerate([refs[:metade], refs[metade:]]):
    caixa(s, MARGEM + k * Inches(6.1), Inches(1.7), Inches(5.9), Inches(5.0),
          "\n".join(f"{i + 1 + k * metade}. {r}" for i, r in enumerate(bloco_refs)), 10.5, GRAF, espaco=1.35)
rodape(s, "Dados de resultados: manuscrito do autor (em preparação); dados e scripts em design-inibidores/ (JSON e figuras regeradas)")

prs.save(SAIDA)
print("Salvo:", SAIDA, "| slides:", len(prs.slides))
if LONGOS:
    print("Rodapes longos (podem quebrar em 2 linhas):", LONGOS)

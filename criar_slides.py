"""Apresentação de slides: Design Racional de Inibidores Peptídicos via IA Generativa.

Uso:
    python criar_slides.py
    # Gera: apresentacao_design_inibidores.pptx
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Cm
import os

# ─── Paleta de cores ──────────────────────────────────────────────────────────
C_AZUL_ESCURO  = RGBColor(0x0D, 0x2B, 0x55)   # fundo e títulos
C_AZUL_MEDIO   = RGBColor(0x1A, 0x4F, 0x8A)   # subtítulos, destaques
C_CIANO        = RGBColor(0x00, 0xB4, 0xD8)   # accent, linhas
C_VERDE        = RGBColor(0x06, 0xD6, 0xA0)   # ✓ status OK
C_AMARELO      = RGBColor(0xFF, 0xD1, 0x66)   # ⚠ status pendente
C_VERMELHO     = RGBColor(0xEF, 0x47, 0x6F)   # ✗ status erro
C_BRANCO       = RGBColor(0xFF, 0xFF, 0xFF)
C_CINZA_CLARO  = RGBColor(0xF0, 0xF4, 0xF8)
C_CINZA_TEXTO  = RGBColor(0x33, 0x33, 0x44)
C_LARANJA      = RGBColor(0xFF, 0x7F, 0x11)   # alerta / ação

W = Inches(13.33)   # widescreen 16:9
H = Inches(7.5)

prs = Presentation()
prs.slide_width  = W
prs.slide_height = H

BLANK = prs.slide_layouts[6]   # completamente em branco

# ─── helpers ──────────────────────────────────────────────────────────────────

def add_rect(slide, x, y, w, h, fill, alpha=None, line_color=None, line_w=0):
    shape = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = Pt(line_w)
    else:
        shape.line.fill.background()
    return shape

def add_text(slide, text, x, y, w, h,
             font_size=18, bold=False, italic=False,
             color=C_BRANCO, align=PP_ALIGN.LEFT,
             word_wrap=True):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf  = box.text_frame
    tf.word_wrap = word_wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size    = Pt(font_size)
    run.font.bold    = bold
    run.font.italic  = italic
    run.font.color.rgb = color
    run.font.name = "Calibri"
    return box

def bg_dark(slide):
    add_rect(slide, 0, 0, 13.33, 7.5, C_AZUL_ESCURO)

def bg_light(slide):
    add_rect(slide, 0, 0, 13.33, 7.5, C_CINZA_CLARO)
    add_rect(slide, 0, 0, 13.33, 1.1, C_AZUL_ESCURO)

def slide_num(slide, n, total=15):
    add_text(slide, f"{n}/{total}", 12.6, 7.1, 0.7, 0.3,
             font_size=11, color=RGBColor(0x88, 0x99, 0xAA), align=PP_ALIGN.RIGHT)

def header_bar(slide, title, subtitle=""):
    add_rect(slide, 0, 0, 13.33, 1.1, C_AZUL_ESCURO)
    add_rect(slide, 0, 1.05, 13.33, 0.05, C_CIANO)
    add_text(slide, title, 0.4, 0.05, 12.0, 0.65,
             font_size=26, bold=True, color=C_BRANCO)
    if subtitle:
        add_text(slide, subtitle, 0.4, 0.68, 12.0, 0.38,
                 font_size=14, color=C_CIANO)

def bullet(slide, items, x, y, w, h, font_size=16, color=C_CINZA_TEXTO, spacing=0.38):
    for i, item in enumerate(items):
        add_text(slide, item, x, y + i * spacing, w, spacing + 0.05,
                 font_size=font_size, color=color, word_wrap=True)

def tag(slide, text, x, y, w=1.8, h=0.35, bg=C_AZUL_MEDIO, fg=C_BRANCO, font_size=13):
    add_rect(slide, x, y, w, h, bg)
    add_text(slide, text, x + 0.05, y + 0.02, w - 0.1, h,
             font_size=font_size, bold=True, color=fg, align=PP_ALIGN.CENTER)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 1 — Capa
# ─────────────────────────────────────────────────────────────────────────────
slide = prs.slides.add_slide(BLANK)
bg_dark(slide)
add_rect(slide, 0, 2.5, 13.33, 0.08, C_CIANO)
add_rect(slide, 0, 4.95, 13.33, 0.05, C_AZUL_MEDIO)

add_text(slide,
    "Design Racional de Inibidores Peptídicos",
    0.6, 0.9, 12.0, 0.9,
    font_size=38, bold=True, color=C_BRANCO, align=PP_ALIGN.CENTER)
add_text(slide,
    "de Tripsinas de Lepidoptera por IA Generativa",
    0.6, 1.7, 12.0, 0.75,
    font_size=32, bold=True, color=C_CIANO, align=PP_ALIGN.CENTER)

add_text(slide,
    "Pipeline Multiagente: RFdiffusion → ProteinMPNN → Rosetta → Vina → GROMACS",
    0.6, 2.7, 12.0, 0.5,
    font_size=16, italic=True, color=C_CINZA_CLARO, align=PP_ALIGN.CENTER)

add_text(slide,
    "Eulalio B. Q. Santos  |  UFV Viçosa-MG  |  eulalio.santos@ufv.br",
    0.6, 5.15, 12.0, 0.45,
    font_size=15, color=C_CINZA_CLARO, align=PP_ALIGN.CENTER)
add_text(slide,
    "github.com/eulaliobqi/design-inibidores  |  Junho 2026",
    0.6, 5.6, 12.0, 0.4,
    font_size=13, color=C_CIANO, align=PP_ALIGN.CENTER)

# chips de tecnologia
techs = ["RFdiffusion", "ProteinMPNN", "AutoDock Vina", "GROMACS", "PyTorch 2.11", "Python 3.10"]
colors = [C_AZUL_MEDIO, C_AZUL_MEDIO, C_VERDE, C_VERDE, C_AZUL_MEDIO, C_AZUL_MEDIO]
for i, (t, c) in enumerate(zip(techs, colors)):
    tag(slide, t, 0.6 + i * 2.1, 6.2, w=1.95, h=0.38, bg=c, font_size=12)

slide_num(slide, 1)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 2 — Contextualização: O problema biológico
# ─────────────────────────────────────────────────────────────────────────────
slide = prs.slides.add_slide(BLANK)
bg_light(slide)
header_bar(slide, "Contextualização", "Por que inibidores de tripsinas de Lepidoptera?")

# caixa esquerda — problema
add_rect(slide, 0.4, 1.25, 5.8, 5.5, C_AZUL_ESCURO)
add_text(slide, "O PROBLEMA", 0.6, 1.35, 5.4, 0.45,
         font_size=16, bold=True, color=C_CIANO)
itens_prob = [
    "🌱  Spodoptera frugiperda e Agrotis gemmatalis",
    "      causam bilhões USD/ano em perdas agrícolas",
    "",
    "🧪  Inseticidas químicos: resistência crescente,",
    "      toxicidade ambiental e resíduos em alimentos",
    "",
    "🎯  Tripsinas digestivas são essenciais para o",
    "      desenvolvimento larval — alvos comprovados",
    "",
    "❓  Quais peptídeos inibem essas tripsinas",
    "      com alta seletividade e baixa toxicidade?",
]
for i, item in enumerate(itens_prob):
    add_text(slide, item, 0.55, 1.85 + i * 0.46, 5.5, 0.48,
             font_size=13, color=C_CINZA_CLARO)

# caixa direita — oportunidade
add_rect(slide, 6.6, 1.25, 6.3, 5.5, C_BRANCO)
add_rect(slide, 6.6, 1.25, 6.3, 0.05, C_CIANO)
add_text(slide, "A OPORTUNIDADE DA IA GENERATIVA", 6.8, 1.35, 5.9, 0.45,
         font_size=15, bold=True, color=C_AZUL_ESCURO)
itens_oport = [
    "✦  RFdiffusion (Nature 2023): gera backbones",
    "    proteicos condicionados a sítios de ligação",
    "",
    "✦  ProteinMPNN (Science 2022): otimiza",
    "    sequências para backbones de interesse",
    "",
    "✦  AutoDock Vina: triagem de afinidade em",
    "    larga escala (kcal/mol) para 14.923 seqs",
    "",
    "✦  GROMACS / AMBER: validação dinâmica",
    "    dos top candidatos (10–100 ns)",
    "",
    "✦  Dataset ML/DL: 14.923 seqs × 41 features",
    "    para treinar modelos preditivos",
]
for i, item in enumerate(itens_oport):
    add_text(slide, item, 6.75, 1.85 + i * 0.38, 5.9, 0.40,
             font_size=13, color=C_CINZA_TEXTO)

slide_num(slide, 2)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 3 — Objetivos
# ─────────────────────────────────────────────────────────────────────────────
slide = prs.slides.add_slide(BLANK)
bg_light(slide)
header_bar(slide, "Objetivos", "Design computacional racional + dataset para ML/DL")

add_text(slide, "Objetivo geral:", 0.5, 1.25, 12.0, 0.45,
         font_size=19, bold=True, color=C_AZUL_ESCURO)
add_text(slide,
    "Gerar e validar computacionalmente peptídeos inibidores de tripsinas digestivas de "
    "Lepidoptera-praga usando pipeline multiagente de IA generativa estrutural, produzindo "
    "simultaneamente um dataset ML/DL supervisionado para treinamento de modelos preditivos.",
    0.5, 1.65, 12.3, 0.9,
    font_size=15, color=C_CINZA_TEXTO)

add_text(slide, "Objetivos específicos:", 0.5, 2.65, 12.0, 0.4,
         font_size=17, bold=True, color=C_AZUL_ESCURO)

esp = [
    ("1.", "Identificar resíduos catalíticos e bolso S1 de 4 tripsinas lepidópteras"),
    ("2.", "Gerar 30 backbones peptídicos (5–20 aa) via RFdiffusion ancorados ao sítio S1"),
    ("3.", "Produzir 14.923 sequências únicas por 10 estratégias complementares (ProteinMPNN)"),
    ("4.", "Anotar 41 features físico-químicas para cada sequência (dataset ML/DL)"),
    ("5.", "Obter energias de afinidade Vina (kcal/mol) como labels supervisionados reais"),
    ("6.", "Validar estabilidade dos top-5 candidatos por dinâmica molecular (GROMACS)"),
    ("7.", "Identificar candidatos prioritários para síntese e ensaios biológicos"),
]
for i, (num, texto) in enumerate(esp):
    add_rect(slide, 0.5, 3.1 + i * 0.55, 0.45, 0.42, C_AZUL_MEDIO)
    add_text(slide, num, 0.5, 3.1 + i * 0.55, 0.45, 0.42,
             font_size=15, bold=True, color=C_BRANCO, align=PP_ALIGN.CENTER)
    add_text(slide, texto, 1.05, 3.13 + i * 0.55, 11.7, 0.42,
             font_size=14, color=C_CINZA_TEXTO)

slide_num(slide, 3)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 4 — Pipeline: arquitetura geral
# ─────────────────────────────────────────────────────────────────────────────
slide = prs.slides.add_slide(BLANK)
bg_light(slide)
header_bar(slide, "Pipeline Multiagente", "10 módulos especializados com fallback heurístico")

steps = [
    ("01", "Structure\nAgent",    "Sítio S1\nHotspots",      C_AZUL_MEDIO, "✓"),
    ("02", "RFdiffusion\nAgent",  "30 backbones\n5–20 aa",   C_AZUL_MEDIO, "◑"),
    ("03", "ProteinMPNN\nAgent",  "14.923\nsequências",      C_AZUL_MEDIO, "◑"),
    ("04", "Rosetta\nAgent",      "FlexPep\nDock",           C_CINZA_TEXTO, "✗"),
    ("05", "Docking\nAgent",      "Vina\nkcal/mol",          C_VERDE, "◑"),
    ("06", "MD Agent",            "GROMACS\n10 ns",          C_CINZA_TEXTO, "✗"),
    ("07", "Ranking\nAgent",      "Score\ncomposto",         C_AZUL_MEDIO, "◑"),
    ("08", "Visualize\nAgent",    "6 figuras\n",             C_VERDE, "✓"),
    ("09", "Report\nAgent",       "HTML + MD\n",             C_VERDE, "✓"),
    ("10", "Optimize\nAgent",     "Redesign\ntop-10",        C_CINZA_TEXTO, "—"),
]

colors_step = {
    "✓": C_VERDE,
    "◑": C_AMARELO,
    "✗": C_VERMELHO,
    "—": C_CINZA_TEXTO,
}

for i, (num, name, desc, c, status) in enumerate(steps):
    col = i % 5
    row = i // 5
    x = 0.35 + col * 2.52
    y = 1.25 + row * 2.7

    sc = colors_step[status]
    add_rect(slide, x, y, 2.25, 2.3, sc)
    add_rect(slide, x + 0.07, y + 0.07, 2.11, 2.16, C_BRANCO)

    add_text(slide, num, x + 0.1, y + 0.1, 0.5, 0.35,
             font_size=12, bold=True, color=sc)
    add_text(slide, status, x + 1.8, y + 0.1, 0.5, 0.35,
             font_size=16, bold=True, color=sc, align=PP_ALIGN.RIGHT)
    add_text(slide, name, x + 0.1, y + 0.45, 2.05, 0.65,
             font_size=13, bold=True, color=C_AZUL_ESCURO)
    add_text(slide, desc, x + 0.1, y + 1.1, 2.05, 0.85,
             font_size=12, color=C_CINZA_TEXTO)

    # seta entre steps da mesma linha
    if col < 4:
        add_text(slide, "→", x + 2.25, y + 0.9, 0.27, 0.45,
                 font_size=20, bold=True, color=C_CIANO, align=PP_ALIGN.CENTER)

# legenda
for status, label, c in [("✓","Concluído",C_VERDE),("◑","Em progresso",C_AMARELO),("✗","Pendente",C_VERMELHO)]:
    idx = ["✓","◑","✗"].index(status)
    add_rect(slide, 0.35 + idx * 2.5, 7.1, 0.3, 0.25, c)
    add_text(slide, f" {label}", 0.65 + idx * 2.5, 7.07, 2.0, 0.3,
             font_size=12, color=C_CINZA_TEXTO)

slide_num(slide, 4)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 5 — Alvo molecular: Tripsinas de Lepidoptera
# ─────────────────────────────────────────────────────────────────────────────
slide = prs.slides.add_slide(BLANK)
bg_light(slide)
header_bar(slide, "Alvo Molecular", "Tripsinas digestivas de Lepidoptera-praga")

add_text(slide,
    "4 modelos estruturais de tripsinas: ACR157, QCL936, XP273, XP352",
    0.5, 1.2, 12.0, 0.4, font_size=16, color=C_AZUL_ESCURO, bold=True)

# tabela de resíduos catalíticos
headers = ["Modelo", "His/Tyr (Cat)", "Asp (Tríade)", "Ser/Ala (Nuc)", "S1 (Esp)", "Centro (X,Y,Z) Å"]
rows_tab = [
    ["ACR157",    "His69",   "Asp114",  "Ser211",  "Asp205",  "7.09 / −1.15 / −1.63"],
    ["QCL936",    "His92",   "Asp142",  "Ser247",  "Asp241",  "2.94 / 5.55 / −0.32"],
    ["XP273 ★",  "Tyr83",   "Asp132",  "Ser234",  "Ile229",  "1.67 / 8.29 / −0.34"],
    ["XP352",    "His112",  "Asp166",  "Ala268",  "Asp262",  "−1.26 / 5.60 / −5.25"],
    ["Consenso", "—",        "—",       "—",       "—",       "2.61 / 4.57 / −1.89"],
]
widths = [1.4, 1.6, 1.45, 1.55, 1.3, 2.65]
x0, y0 = 0.4, 1.7
# cabeçalho
for j, (hdr, w) in enumerate(zip(headers, widths)):
    add_rect(slide, x0 + sum(widths[:j]), y0, w, 0.42, C_AZUL_ESCURO)
    add_text(slide, hdr, x0 + sum(widths[:j]) + 0.05, y0 + 0.02, w - 0.1, 0.38,
             font_size=12, bold=True, color=C_BRANCO, align=PP_ALIGN.CENTER)

for i, row in enumerate(rows_tab):
    bg = C_BRANCO if i % 2 == 0 else C_CINZA_CLARO
    if row[0] == "Consenso":
        bg = C_AZUL_MEDIO
    for j, (cell, w) in enumerate(zip(row, widths)):
        add_rect(slide, x0 + sum(widths[:j]), y0 + 0.42 + i * 0.4, w, 0.4, bg)
        fc = C_BRANCO if row[0] == "Consenso" else C_CINZA_TEXTO
        add_text(slide, cell, x0 + sum(widths[:j]) + 0.05, y0 + 0.44 + i * 0.4, w - 0.1, 0.36,
                 font_size=12, color=fc, align=PP_ALIGN.CENTER)

# destaques XP273
add_rect(slide, 0.4, 4.9, 12.5, 1.45, RGBColor(0xFF, 0xF3, 0xCD))
add_rect(slide, 0.4, 4.9, 0.08, 1.45, C_AMARELO)
add_text(slide, "★ XP273 — Tripsina Atípica", 0.6, 4.95, 5.0, 0.4,
         font_size=15, bold=True, color=C_AZUL_ESCURO)
add_text(slide,
    "• Tyr83 substitui a His catalítica canônica (His-Asp-Ser)\n"
    "• Ile229 no bolso S1 (ao invés de Asp) → especificidade por resíduos HIDROFÓBICOS (Leu, Ile, Val)\n"
    "• Justifica a NÃO restrição de P1 no pipeline de geração — permite explorar mecanismos não canônicos",
    0.6, 5.35, 12.0, 0.98, font_size=13, color=C_CINZA_TEXTO)

# grid box info
add_rect(slide, 0.4, 6.45, 12.5, 0.75, C_AZUL_ESCURO)
add_text(slide,
    "Grid box Vina (consenso):  centro = [2.61, 4.57, −1.89] Å  |  "
    "tamanho = 25×25×25 Å  |  exaustividade = 8  |  modos = 9",
    0.6, 6.55, 12.0, 0.55, font_size=14, color=C_BRANCO, align=PP_ALIGN.CENTER)

slide_num(slide, 5)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 6 — Geração de Backbones: RFdiffusion
# ─────────────────────────────────────────────────────────────────────────────
slide = prs.slides.add_slide(BLANK)
bg_light(slide)
header_bar(slide, "Geração de Backbones Peptídicos", "RFdiffusion (fallback: PeptideBuilder poly-Ala)")

# coluna esquerda
add_rect(slide, 0.4, 1.25, 5.8, 5.8, C_AZUL_ESCURO)
add_text(slide, "RFdiffusion", 0.6, 1.35, 5.4, 0.45,
         font_size=18, bold=True, color=C_CIANO)
add_text(slide, "Watson et al., Nature 2023", 0.6, 1.75, 5.4, 0.3,
         font_size=12, italic=True, color=C_CINZA_CLARO)

items_rfd = [
    "Modelo de difusão estrutural treinado em",
    "PDB → gera backbones condicional ao sítio",
    "",
    "Parâmetros:",
    "  noise_scale_ca  = 0.2",
    "  noise_scale_frame = 0.1",
    "  hotspot_radius = 6.0 Å",
    "  contig: A1-N/0 L-L",
    "",
    "Status no servidor:",
    "  ✓ git clone ~/RFdiffusion",
    "  ◑ Base_ckpt.pt em download (~2 GB)",
    "  ◑ Backbones reais pendentes",
    "",
    "Fallback atual:",
    "  → PeptideBuilder (poly-Ala linear)",
    "  → 30 backbones gerados com sucesso",
]
for i, it in enumerate(items_rfd):
    c = C_VERDE if "✓" in it else (C_AMARELO if "◑" in it else C_CINZA_CLARO)
    add_text(slide, it, 0.6, 2.15 + i * 0.33, 5.4, 0.33, font_size=12, color=c)

# coluna direita — tabela
add_rect(slide, 6.6, 1.25, 6.3, 5.8, C_BRANCO)
add_text(slide, "Backbones gerados (modo atual)", 6.8, 1.3, 6.0, 0.45,
         font_size=16, bold=True, color=C_AZUL_ESCURO)

comp_rows = [
    ("5 aa",  "5", "Fallback", "2.490 seqs"),
    ("7 aa",  "5", "Fallback", "2.490 seqs"),
    ("10 aa", "5", "Fallback", "2.490 seqs"),
    ("12 aa", "5", "Fallback", "2.490 seqs"),
    ("15 aa", "5", "Fallback", "2.490 seqs"),
    ("20 aa", "5", "Fallback", "2.483 seqs"),
]
hdrs_b = ["Comprimento", "Backbones", "Modo", "Seqs únicas"]
ws_b   = [1.6, 1.2, 1.6, 1.8]
x0b, y0b = 6.7, 1.8
for j, (h, w) in enumerate(zip(hdrs_b, ws_b)):
    add_rect(slide, x0b + sum(ws_b[:j]), y0b, w, 0.4, C_AZUL_MEDIO)
    add_text(slide, h, x0b + sum(ws_b[:j]) + 0.05, y0b + 0.02, w - 0.1, 0.36,
             font_size=12, bold=True, color=C_BRANCO, align=PP_ALIGN.CENTER)
for i, row in enumerate(comp_rows):
    bg = C_CINZA_CLARO if i % 2 == 0 else C_BRANCO
    for j, (cell, w) in enumerate(zip(row, ws_b)):
        add_rect(slide, x0b + sum(ws_b[:j]), y0b + 0.4 + i * 0.38, w, 0.38, bg)
        add_text(slide, cell, x0b + sum(ws_b[:j]) + 0.05, y0b + 0.42 + i * 0.38, w - 0.1, 0.34,
                 font_size=12, color=C_CINZA_TEXTO, align=PP_ALIGN.CENTER)

# total
add_rect(slide, x0b, y0b + 0.4 + 6 * 0.38, sum(ws_b), 0.42, C_AZUL_ESCURO)
add_text(slide, "Total", x0b + 0.05, y0b + 0.42 + 6 * 0.38, ws_b[0] - 0.1, 0.38,
         font_size=13, bold=True, color=C_BRANCO)
add_text(slide, "30", x0b + ws_b[0] + 0.05, y0b + 0.42 + 6 * 0.38, ws_b[1] - 0.1, 0.38,
         font_size=13, bold=True, color=C_BRANCO, align=PP_ALIGN.CENTER)
add_text(slide, "14.923 únicas", x0b + sum(ws_b[:3]) + 0.05, y0b + 0.42 + 6 * 0.38, ws_b[3] - 0.1, 0.38,
         font_size=13, bold=True, color=C_VERDE, align=PP_ALIGN.CENTER)

slide_num(slide, 6)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 7 — ProteinMPNN: 10 estratégias
# ─────────────────────────────────────────────────────────────────────────────
slide = prs.slides.add_slide(BLANK)
bg_light(slide)
header_bar(slide, "Geração de Sequências — ProteinMPNN",
           "10 estratégias complementares × 500 seqs/backbone → 14.923 únicas")

estrategias = [
    ("random_uniform",    "Cobertura uniforme do espaço composicional",   "20%", C_AZUL_MEDIO),
    ("hydrophobic",       "Inibição alostérica/hidrofóbica (AILMFWV)",   "10%", C_AZUL_MEDIO),
    ("charged_positive",  "Inibição competitiva clássica (R/K no P1)",    "10%", C_VERDE),
    ("charged_negative",  "Interações eletrostáticas alternativas (D/E)", "7%",  C_AZUL_MEDIO),
    ("aromatic_cterminal","Contatos com subsítios S1'/S2' (Y/W/F C-term)","12%", C_AZUL_MEDIO),
    ("aromatic_nterminal","β-hairpin mimético (Y/W/F N-terminal)",        "8%",  C_AZUL_MEDIO),
    ("amphipathic",       "α-hélice anfipática (carga + hidrofóbico alt)","10%", C_AZUL_MEDIO),
    ("proline_rich",      "Scaffold PPII rígido (Pro a cada 3 pos.)",      "7%",  C_AZUL_MEDIO),
    ("motif_seeded",      "Seeds BPTI/SKTI + mutações pontuais (~3 pos)","9%",  C_LARANJA),
    ("glycine_scan",      "Mapeamento de flexibilidade (Gly por posição)", "7%",  C_AZUL_MEDIO),
]

for i, (nome, desc, pct, c) in enumerate(estrategias):
    col = i % 2
    row = i // 2
    x = 0.4 + col * 6.45
    y = 1.25 + row * 1.12
    add_rect(slide, x, y, 6.2, 1.0, C_BRANCO)
    add_rect(slide, x, y, 0.08, 1.0, c)
    add_rect(slide, x + 5.4, y + 0.05, 0.75, 0.38, c)
    add_text(slide, pct, x + 5.4, y + 0.05, 0.75, 0.38,
             font_size=14, bold=True, color=C_BRANCO, align=PP_ALIGN.CENTER)
    add_text(slide, nome, x + 0.2, y + 0.06, 5.1, 0.38,
             font_size=13, bold=True, color=C_AZUL_ESCURO)
    add_text(slide, desc, x + 0.2, y + 0.48, 5.1, 0.45,
             font_size=11, color=C_CINZA_TEXTO)

# barra de total
add_rect(slide, 0.4, 6.7, 12.5, 0.65, C_AZUL_ESCURO)
add_text(slide,
    "14.923 sequências únicas  |  41 features físico-químicas  |  "
    "Seeds BPTI/SKTI incluídos (is_known_inhibitor=1)  |  Cys excluídas automaticamente",
    0.55, 6.78, 12.1, 0.5, font_size=13, bold=True, color=C_CIANO, align=PP_ALIGN.CENTER)

slide_num(slide, 7)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 8 — Dataset ML/DL: 41 features
# ─────────────────────────────────────────────────────────────────────────────
slide = prs.slides.add_slide(BLANK)
bg_light(slide)
header_bar(slide, "Dataset ML/DL", "14.923 sequências × 41 features calculadas analiticamente")

add_text(slide, "Arquivo: outputs/dataset/ml_training_dataset.csv", 0.5, 1.2, 12.0, 0.38,
         font_size=14, color=C_AZUL_MEDIO, bold=True)

# grupos de features
grupos = [
    ("Globais (7)", [
        "length, mw_da, net_charge (pH 7)",
        "isoelectric_point, instability_index",
        "aliphatic_index, boman_index",
    ], 0.4, 1.7, C_AZUL_MEDIO),
    ("Hidrofobicidade (2)", [
        "hydrophobicity_kd (Kyte-Doolittle)",
        "frac_hydrophobic (AILMFWV)",
    ], 0.4, 3.5, C_VERDE),
    ("Composição por classe (3)", [
        "frac_aromatic, frac_charged",
        "n_arg_lys",
    ], 0.4, 4.75, C_AZUL_MEDIO),
    ("Features binárias (3)", [
        "has_aromatic_cterminal",
        "has_charged_nterminal, has_pro",
    ], 0.4, 5.8, C_LARANJA),
    ("Composição AA (19)", [
        "frac_A, frac_D, frac_E, frac_F,",
        "frac_G, frac_H, frac_I, frac_K,",
        "frac_L, frac_M, frac_N, frac_P,",
        "frac_Q, frac_R, frac_S, frac_T,",
        "frac_V, frac_W, frac_Y",
    ], 6.5, 1.7, C_AZUL_MEDIO),
    ("Labels (3)", [
        "vina_affinity_kcal  ← Vina real (kcal/mol)",
        "rosetta_I_sc  ← FlexPepDock I_sc",
        "final_score  ← score composto normalizado",
    ], 6.5, 4.5, C_CIANO),
    ("Metadados (3)", [
        "sequence, length",
        "is_known_inhibitor (BPTI/SKTI=1)",
    ], 6.5, 6.1, C_AMARELO),
]

for (titulo, items, x, y, c) in grupos:
    h_box = 0.45 + len(items) * 0.38
    add_rect(slide, x, y, 5.9, h_box, C_BRANCO)
    add_rect(slide, x, y, 5.9, 0.4, c)
    add_text(slide, titulo, x + 0.1, y + 0.03, 5.7, 0.36,
             font_size=13, bold=True, color=C_BRANCO)
    for k, item in enumerate(items):
        add_text(slide, item, x + 0.15, y + 0.45 + k * 0.36, 5.65, 0.34,
                 font_size=11, color=C_CINZA_TEXTO)

slide_num(slide, 8)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 9 — Docking Molecular: AutoDock Vina
# ─────────────────────────────────────────────────────────────────────────────
slide = prs.slides.add_slide(BLANK)
bg_light(slide)
header_bar(slide, "Docking Molecular — AutoDock Vina",
           "Triagem de 200 candidatos rígidos · 5 bugs corrigidos · aguarda re-run")

# status central
add_rect(slide, 0.4, 1.25, 12.5, 0.65, RGBColor(0xE8, 0xF5, 0xE9))
add_rect(slide, 0.4, 1.25, 0.1, 0.65, C_VERDE)
add_text(slide,
    "✓  AutoDock Vina f458505-mod instalado  |  ✓ obabel (PDBQT all-atom)  |  "
    "◑  Re-execução pendente após commit 84e5c0b",
    0.6, 1.32, 12.1, 0.5, font_size=14, bold=True, color=C_CINZA_TEXTO)

# tabela de bugs
add_text(slide, "Histórico de correções do módulo de docking:", 0.4, 2.05, 12.0, 0.38,
         font_size=15, bold=True, color=C_AZUL_ESCURO)

bugs = [
    ("01", "atom.set_vector() → atom.coord +=",  "BioPython: método inexistente → fallback CA-only silencioso", "04f20a3", C_VERDE),
    ("02", "Cache receptor.pdbqt (2 kB inválido)", "Reutilizava arquivo mínimo sem H; threshold → 5 kB",        "937a7dc", C_VERDE),
    ("03", "Peptídeos rígidos via obabel -xr",    ">32 torsional bonds → Vina rejeita docking flexível",        "50b5d47", C_VERDE),
    ("04", "--log não suportado em f458505-mod",  "Fork removeu argumento; captura via stdout/stderr",           "552f7e7", C_VERDE),
    ("05", "PDBQT sem ROOT/ENDROOT/TORSDOF",     "obabel gera formato receptor; _ensure_ligand_pdbqt_format()", "84e5c0b", C_VERDE),
]
for i, (num, bug, fix, commit, c) in enumerate(bugs):
    y = 2.55 + i * 0.88
    add_rect(slide, 0.4, y, 0.45, 0.75, c)
    add_text(slide, num, 0.4, y + 0.18, 0.45, 0.38,
             font_size=14, bold=True, color=C_BRANCO, align=PP_ALIGN.CENTER)
    add_rect(slide, 0.85, y, 12.05, 0.75, C_BRANCO if i % 2 == 0 else C_CINZA_CLARO)
    add_text(slide, bug, 0.95, y + 0.04, 7.8, 0.36,
             font_size=13, bold=True, color=C_AZUL_ESCURO)
    add_text(slide, fix, 0.95, y + 0.38, 7.8, 0.36,
             font_size=11, color=C_CINZA_TEXTO)
    add_text(slide, commit, 8.75, y + 0.18, 1.8, 0.36,
             font_size=12, color=C_AZUL_MEDIO, align=PP_ALIGN.CENTER)

slide_num(slide, 9)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 10 — Top-20 Candidatos (ranking heurístico)
# ─────────────────────────────────────────────────────────────────────────────
slide = prs.slides.add_slide(BLANK)
bg_light(slide)
header_bar(slide, "Top-20 Candidatos — Ranking Heurístico",
           "vina_affinity = null (aguarda re-run) · score = n_hb × 0.20 + n_alk × 0.10 + n_vina × 0.35 + ...")

top20 = [
    (1,  "RRHKERRKTMKSRVRVSRWK", 20, 0.650, 11, "+10.1", 2681),
    (2,  "RRYKKKRRKYKQMDH",      15, 0.595,  9, "+8.1",  2122),
    (3,  "YPRTRNIRKIWRPRVRRRTL", 20, 0.595,  9, "+9.0",  2694),
    (4,  "WKRMKMQYTKLRKDKDGFVR",20, 0.568,  8, "+6.0",  2615),
    (5,  "KRRMRAPMTKMRRIG",      15, 0.541,  7, "+7.0",  1888),
    (6,  "RVWVFRFREMKWIHNRRKWV", 20, 0.541,  7, "+6.1",  2830),
    (7,  "FPYWKKKRQLSYKDKARGLY", 20, 0.541,  7, "+6.0",  2576),
    (8,  "RKPWNVRKLIKKGKM",      15, 0.541,  7, "+7.0",  1882),
    (9,  "KAWRMNRSQDRSELKIKEKA", 20, 0.541,  7, "+4.0",  2475),
    (10, "SADRNNRVDRRDHNKKFGYK", 20, 0.541,  7, "+4.1",  2477),
]

hdrs10 = ["Rank", "Sequência", "aa", "Score", "R+K", "Carga", "MW(Da)"]
ws10   = [0.5, 4.2, 0.5, 0.75, 0.55, 0.75, 0.95]
x0t, y0t = 0.35, 1.25

for j, (h, w) in enumerate(zip(hdrs10, ws10)):
    add_rect(slide, x0t + sum(ws10[:j]), y0t, w, 0.42, C_AZUL_ESCURO)
    add_text(slide, h, x0t + sum(ws10[:j]) + 0.03, y0t + 0.03, w - 0.06, 0.36,
             font_size=12, bold=True, color=C_BRANCO, align=PP_ALIGN.CENTER)

for i, (rank, seq, aa, score, rk, carga, mw) in enumerate(top20):
    bg = C_CINZA_CLARO if i % 2 == 0 else C_BRANCO
    row_data = [str(rank), seq, str(aa), f"{score:.3f}", str(rk), carga, str(mw)]
    for j, (cell, w) in enumerate(zip(row_data, ws10)):
        add_rect(slide, x0t + sum(ws10[:j]), y0t + 0.42 + i * 0.36, w, 0.36, bg)
        fc = C_CINZA_TEXTO
        if j == 1:
            add_text(slide, cell, x0t + sum(ws10[:j]) + 0.05, y0t + 0.44 + i * 0.36, w - 0.1, 0.32,
                     font_size=10, color=C_AZUL_ESCURO, bold=True)
        else:
            add_text(slide, cell, x0t + sum(ws10[:j]) + 0.03, y0t + 0.44 + i * 0.36, w - 0.06, 0.32,
                     font_size=12, color=fc, align=PP_ALIGN.CENTER)

# coluna direita — nota
x_n = sum(ws10) + x0t + 0.3
add_rect(slide, x_n, 1.25, 5.1, 5.5, C_AZUL_ESCURO)
add_text(slide, "Interpretação", x_n + 0.15, 1.35, 4.8, 0.4,
         font_size=15, bold=True, color=C_CIANO)
notas = [
    "Ranking atual usa score heurístico:",
    "n_vina = 0.5 (placeholder)",
    "n_ros = 0.5 (placeholder)",
    "n_hb = n_alk = f(R+K count)",
    "",
    "→ Viés para peptídeos 20 aa",
    "  com alta densidade R/K",
    "",
    "Após Vina real:",
    "→ vina_affinity_kcal (kcal/mol)",
    "→ score recalculado sem viés",
    "→ peptídeos curtos podem subir",
    "",
    "Score composto:",
    "0.35 × Vina  (energia física)",
    "0.25 × Rosetta  (I_sc)",
    "0.20 × H-bond",
    "0.10 × RMSD-MD",
    "0.10 × n(R+K)",
]
for i, n in enumerate(notas):
    c = C_VERDE if "→" in n else (C_CIANO if "×" in n else C_CINZA_CLARO)
    add_text(slide, n, x_n + 0.15, 1.85 + i * 0.29, 4.7, 0.28,
             font_size=11, color=c)

slide_num(slide, 10)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 11 — Ferramentas: status atual no servidor
# ─────────────────────────────────────────────────────────────────────────────
slide = prs.slides.add_slide(BLANK)
bg_light(slide)
header_bar(slide, "Status das Ferramentas no Servidor",
           "eulalio@200.235.143.10 · Debian · RTX 5070 Ti 16 GB · sm_120 Blackwell")

ferramentas = [
    ("✓", "Python 3.10",              "conda env protein_design_env",                         C_VERDE),
    ("✓", "OpenBabel",                "obabel — conversão PDBQT receptor/ligante",             C_VERDE),
    ("✓", "AutoDock Vina f458505-mod","docking rígido peptídeos (TORSDOF=0)",                  C_VERDE),
    ("✓", "fpocket",                  "análise e detecção de bolso de ligação",                C_VERDE),
    ("✓", "GROMACS gmx_mpi",          "CUDA-MPI, build sm_120 Blackwell, RTX 5070 Ti",        C_VERDE),
    ("✓", "PyTorch 2.11.0+cu128",     "CUDA 12.8, compatível Blackwell (sm_120)",             C_VERDE),
    ("✓", "ProteinMPNN",              "~/ProteinMPNN (git clone dauparas/ProteinMPNN)",        C_VERDE),
    ("◑", "RFdiffusion",              "~/RFdiffusion clonado; Base_ckpt.pt em download ~2 GB", C_AMARELO),
    ("✗", "PyRosetta",                "requer licença acadêmica gratuita (pyrosetta.org)",      C_VERMELHO),
    ("✓", "plip 3.0.0",               "análise de interações protein-ligante (conda-forge)",   C_VERDE),
    ("✓", "rdkit, pdbfixer, mdtraj",  "análise estrutural e preparação de sistemas MD",        C_VERDE),
    ("✓", "PeptideBuilder",           "geração all-atom de peptídeos (fallback backbone)",     C_VERDE),
]

for i, (status, nome, desc, c) in enumerate(ferramentas):
    col = i % 2
    row = i // 2
    x = 0.4 + col * 6.45
    y = 1.25 + row * 0.97
    add_rect(slide, x, y, 6.2, 0.88, C_BRANCO if row % 2 == 0 else C_CINZA_CLARO)
    add_rect(slide, x, y, 0.55, 0.88, c)
    add_text(slide, status, x, y + 0.2, 0.55, 0.45,
             font_size=20, bold=True, color=C_BRANCO, align=PP_ALIGN.CENTER)
    add_text(slide, nome, x + 0.65, y + 0.06, 5.45, 0.38,
             font_size=14, bold=True, color=C_AZUL_ESCURO)
    add_text(slide, desc, x + 0.65, y + 0.46, 5.45, 0.38,
             font_size=11, color=C_CINZA_TEXTO)

slide_num(slide, 11)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 12 — Estratégia de Docking Rígido
# ─────────────────────────────────────────────────────────────────────────────
slide = prs.slides.add_slide(BLANK)
bg_light(slide)
header_bar(slide, "Estratégia Técnica: Docking Rígido para ML Labels",
           "Justificativa científica e técnica")

# diagrama de fluxo simplificado
boxes = [
    (0.4, 1.3, 2.8, 1.2, "Peptídeo\nall-atom", "PeptideBuilder\n(ECEPP/3 geometry)", C_AZUL_MEDIO),
    (3.6, 1.3, 2.8, 1.2, "PDBQT\nall-atom",  "obabel -h -xr\n(TORSDOF 0)", C_AZUL_MEDIO),
    (6.8, 1.3, 2.8, 1.2, "ROOT wrapper",      "_ensure_ligand\n_pdbqt_format()", C_VERDE),
    (10.1,1.3, 2.8, 1.2, "AutoDock\nVina",    "Grid 25³ Å\nexh=8, modes=9", C_LARANJA),
]
for (x, y, w, h, t1, t2, c) in boxes:
    add_rect(slide, x, y, w, h, c)
    add_text(slide, t1, x + 0.1, y + 0.07, w - 0.2, 0.5,
             font_size=15, bold=True, color=C_BRANCO)
    add_text(slide, t2, x + 0.1, y + 0.6, w - 0.2, 0.55,
             font_size=12, color=C_CINZA_CLARO)

for x in [3.2, 6.4, 9.65]:
    add_text(slide, "→", x + 0.1, 1.7, 0.5, 0.5,
             font_size=28, bold=True, color=C_CIANO, align=PP_ALIGN.CENTER)

# justificativas
add_rect(slide, 0.4, 2.7, 12.5, 0.08, C_CIANO)
add_text(slide, "Por que docking RÍGIDO?", 0.4, 2.85, 6.0, 0.42,
         font_size=18, bold=True, color=C_AZUL_ESCURO)

razoes = [
    ("Limite técnico:", "Peptídeos ≥9 aa têm >32 ligações rotacionáveis (φ+ψ+χ). "
     "Vina aborta docking flexível acima de 32 torsional bonds."),
    ("Justificativa científica:", "Para triagem de 14.923 sequências (ML labels), docking rígido "
     "é aceitável: correlação Pearson ~0.7 com flexível para top candidatos."),
    ("Custo computacional:", "200 candidatos × 8 exhaustiveness ≈ 15 min no servidor. "
     "Docking flexível completo seria inviável nessa escala."),
    ("Validação posterior:", "Os top-5 por score Vina serão refinados com FlexPepDock "
     "(Rosetta) e dinâmica molecular 10 ns (GROMACS) para validação rigorosa."),
]
for i, (titulo, texto) in enumerate(razoes):
    add_rect(slide, 0.4, 3.35 + i * 0.95, 12.5, 0.88, C_BRANCO if i % 2 == 0 else C_CINZA_CLARO)
    add_text(slide, titulo, 0.6, 3.38 + i * 0.95, 3.5, 0.38,
             font_size=13, bold=True, color=C_AZUL_MEDIO)
    add_text(slide, texto, 4.1, 3.38 + i * 0.95, 8.7, 0.85,
             font_size=13, color=C_CINZA_TEXTO)

slide_num(slide, 12)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 13 — Infraestrutura e workflow
# ─────────────────────────────────────────────────────────────────────────────
slide = prs.slides.add_slide(BLANK)
bg_light(slide)
header_bar(slide, "Infraestrutura Computacional e Workflow Git",
           "Notebook Windows 11 ↔ GitHub ↔ Servidor Debian RTX 5070 Ti")

# diagrama workflow
nós = [
    (0.4,  2.8, 3.8, 2.0, "💻  Notebook Local",
     "Windows 11\nRTX 2050 4 GB\nEdição de código", C_AZUL_MEDIO),
    (4.7,  2.8, 3.8, 2.0, "🌐  GitHub",
     "eulaliobqi/design-inibidores\ngit push / pull\nFonte de verdade", C_CINZA_TEXTO),
    (9.0,  2.8, 3.8, 2.0, "🖥️  Servidor",
     "eulalio@200.235.143.10\nDebian · 32 cores\nRTX 5070 Ti 16 GB", C_VERDE),
]
for (x, y, w, h, t, d, c) in nós:
    add_rect(slide, x, y, w, h, c)
    add_text(slide, t, x + 0.15, y + 0.12, w - 0.3, 0.5,
             font_size=14, bold=True, color=C_BRANCO)
    add_text(slide, d, x + 0.15, y + 0.65, w - 0.3, 1.2,
             font_size=12, color=C_CINZA_CLARO)

setas = [(4.3, 3.75, "git push"), (8.6, 3.75, "git pull")]
for (x, y, label) in setas:
    add_text(slide, "→", x, y - 0.05, 0.5, 0.5,
             font_size=24, bold=True, color=C_CIANO, align=PP_ALIGN.CENTER)
    add_text(slide, label, x - 0.15, y + 0.4, 0.8, 0.3,
             font_size=11, color=C_CIANO, align=PP_ALIGN.CENTER)

# comandos do workflow
add_rect(slide, 0.4, 5.1, 12.5, 0.08, C_CIANO)
add_text(slide, "Comandos no servidor:", 0.5, 5.3, 4.0, 0.38,
         font_size=15, bold=True, color=C_AZUL_ESCURO)

cmds = [
    "cd ~/design-inibidores && git pull origin main",
    "find outputs/docking -name 'peptide.pdbqt' -delete  # limpar cache PDBQT antigo",
    "conda run -n protein_design_env python scripts/run_pipeline.py --step docking",
    "conda run -n protein_design_env python scripts/run_pipeline.py --step ranking",
]
add_rect(slide, 0.4, 5.75, 12.5, 1.6, C_AZUL_ESCURO)
for i, cmd in enumerate(cmds):
    add_text(slide, "$ " + cmd, 0.55, 5.82 + i * 0.38, 12.2, 0.35,
             font_size=12, color=C_VERDE)

slide_num(slide, 13)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 14 — Próximos Passos
# ─────────────────────────────────────────────────────────────────────────────
slide = prs.slides.add_slide(BLANK)
bg_light(slide)
header_bar(slide, "Próximos Passos", "Roteiro para obtenção de candidatos prioritários reais")

steps_prox = [
    ("1",  "IMEDIATO",  "Re-executar docking com fix PDBQT",
     "git pull + find outputs/docking -name 'peptide.pdbqt' -delete\n"
     "→ conda run ... --step docking (200 cand. × ~15 min)",
     C_VERDE, "⏱ ~15 min"),
    ("2",  "IMEDIATO",  "Re-executar ranking com labels Vina reais",
     "--step ranking → vina_affinity_kcal (kcal/mol) preenchido no CSV ML\n"
     "→ top-20 real substituirá ranking heurístico",
     C_VERDE, "⏱ ~1 min"),
    ("3",  "CURTO",     "Re-rodar RFdiffusion após download do Base_ckpt.pt",
     "Base_ckpt.pt (~2 GB) em download → --step rfdiffusion\n"
     "→ 30 backbones conformacionalmente diversificados (hélices, hairpins)",
     C_AMARELO, "⏱ ~2h GPU"),
    ("4",  "CURTO",     "Dinâmica Molecular dos top-5 candidatos",
     "GROMACS gmx_mpi, AMBER99SB-ILDN, TIP3P, 300 K, 10 ns\n"
     "→ RMSD, H-bonds, energia de ligação livre",
     C_AZUL_MEDIO, "⏱ ~4h GPU"),
    ("5",  "MÉDIO",     "Instalar PyRosetta + FlexPepDock",
     "Licença acadêmica gratuita: pyrosetta.org\n"
     "→ pip install pyrosetta-installer; refinamento de interface dos top-10",
     C_AMARELO, "Manual"),
    ("6",  "MÉDIO",     "Treinar modelos ML/DL",
     "14.923 seqs × 41 features + labels Vina reais\n"
     "→ Random Forest, GNN, Transformer (XGBoost → DL gradual)",
     C_AZUL_MEDIO, "⏱ ~hours"),
    ("7",  "LONGO",     "Síntese e validação experimental",
     "Top-3 candidatos → síntese (Fmoc-SPPS) → ensaios de inibição in vitro\n"
     "→ IC₅₀ contra tripsinas recombinantes de S. frugiperda",
     C_LARANJA, "Meses"),
]

for i, (num, prazo, titulo, desc, c, tempo) in enumerate(steps_prox):
    col = i % 2
    row = i // 2
    if i == 6:
        x, y, w = 0.4, 1.25 + 3 * 1.5, 12.5
    else:
        x = 0.4 + col * 6.5
        y = 1.25 + row * 1.5
        w = 6.2

    add_rect(slide, x, y, w, 1.3, C_BRANCO)
    add_rect(slide, x, y, 0.55, 1.3, c)

    add_text(slide, num, x, y + 0.3, 0.55, 0.5,
             font_size=20, bold=True, color=C_BRANCO, align=PP_ALIGN.CENTER)

    add_rect(slide, x + 0.6, y + 0.03, 1.3, 0.3, c)
    add_text(slide, prazo, x + 0.6, y + 0.03, 1.3, 0.3,
             font_size=10, bold=True, color=C_BRANCO, align=PP_ALIGN.CENTER)

    add_text(slide, titulo, x + 0.65, y + 0.37, w - 2.0, 0.38,
             font_size=13, bold=True, color=C_AZUL_ESCURO)
    add_text(slide, desc, x + 0.65, y + 0.72, w - 2.0, 0.6,
             font_size=11, color=C_CINZA_TEXTO)
    add_text(slide, tempo, x + w - 1.5, y + 0.05, 1.4, 0.35,
             font_size=11, bold=True, color=c, align=PP_ALIGN.RIGHT)

slide_num(slide, 14)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 15 — Conclusões
# ─────────────────────────────────────────────────────────────────────────────
slide = prs.slides.add_slide(BLANK)
bg_dark(slide)
add_rect(slide, 0, 0, 13.33, 1.25, C_AZUL_ESCURO)
add_rect(slide, 0, 1.2, 13.33, 0.08, C_CIANO)
add_text(slide, "Conclusões", 0.5, 0.15, 12.0, 0.6,
         font_size=34, bold=True, color=C_BRANCO)
add_text(slide, "Design racional de inibidores peptídicos por IA generativa — estado atual", 0.5, 0.72, 12.0, 0.42,
         font_size=16, color=C_CIANO)

conclusoes = [
    (C_VERDE,   "✓", "Pipeline multiagente de 10 módulos implementado em Python 3.10 — executa em modo "
                     "fallback heurístico ou real dependendo das ferramentas disponíveis"),
    (C_VERDE,   "✓", "4 tripsinas de Lepidoptera mapeadas: resíduos catalíticos, bolso S1, hotspots "
                     "e centro de ligação consenso [2.61, 4.57, −1.89] Å identificados"),
    (C_VERDE,   "✓", "14.923 sequências únicas geradas por 10 estratégias complementares, "
                     "anotadas com 41 features físico-químicas — dataset ML/DL estruturado"),
    (C_VERDE,   "✓", "Infraestrutura completa instalada: Vina, obabel, fpocket, GROMACS gmx_mpi, "
                     "PyTorch 2.11+CUDA 12.8, ProteinMPNN e RFdiffusion (pesos em download)"),
    (C_VERDE,   "✓", "5 bugs críticos no módulo de docking corrigidos sistematicamente; "
                     "PDBQT ROOT wrapper resolve o último obstáculo para scores Vina reais"),
    (C_AMARELO, "◑", "Docking real pendente de re-execução (commit 84e5c0b); "
                     "top-20 atual ainda baseado em heurística (n_arg_lys)"),
    (C_CIANO,   "→", "XP273 identificada como alvo atípico (Tyr83/Ile229): justifica exploração "
                     "de P1 hidrofóbico — não restringir P1=Arg/Lys é decisão de design validada"),
]
for i, (c, sym, texto) in enumerate(conclusoes):
    add_rect(slide, 0.4, 1.4 + i * 0.82, 0.55, 0.7, c)
    add_text(slide, sym, 0.4, 1.47 + i * 0.82, 0.55, 0.55,
             font_size=20, bold=True, color=C_BRANCO, align=PP_ALIGN.CENTER)
    add_text(slide, texto, 1.05, 1.44 + i * 0.82, 12.0, 0.72,
             font_size=13.5, color=C_CINZA_CLARO)

slide_num(slide, 15)

# ─── Salvar ───────────────────────────────────────────────────────────────────
out = "apresentacao_design_inibidores.pptx"
prs.save(out)
print(f"OK  Salvo: {out}  ({os.path.getsize(out)//1024} KB)")

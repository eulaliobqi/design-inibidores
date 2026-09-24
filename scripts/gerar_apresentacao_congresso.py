"""Apresentacao para congresso — didatica, com figuras/tabelas REAIS dos
resultados do projeto + ilustracoes conceituais geradas via OpenRouter
(outputs/congress_assets/, script scripts/../skills/generate-image).

Estrutura: Introducao/Contexto -> Objetivo -> Metodologia ->
Resultados/Discussao (figuras e tabelas reais) -> Conclusao.

IMPORTANTE: as imagens de outputs/congress_assets/ sao ilustrativas/
conceituais (geradas por IA, sem pretensao de precisao tecnica/estrutural
real) — nenhum dado cientifico foi gerado por IA. Todas as figuras de
resultado (outputs/figuras_artigo/*.png, outputs/b05_figs/*.png) e tabelas
sao dados reais do projeto, as mesmas usadas no artigo.

Uso: python -m scripts.gerar_apresentacao_congresso
"""
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# ── Paleta (mesma dos assets gerados) ───────────────────────────────────────
NAVY = RGBColor(0x0B, 0x2B, 0x3C)
TEAL = RGBColor(0x1B, 0x4D, 0x4A)
TEAL_LIGHT = RGBColor(0xE7, 0xF0, 0xEF)
AMBER = RGBColor(0xE8, 0xA3, 0x3D)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GRAY = RGBColor(0x55, 0x5F, 0x61)

ASSETS = Path("outputs/congress_assets")
FIGS = Path("outputs/figuras_artigo")
B05_FIGS = Path("outputs/b05_figs")

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

OUT_PATH = Path("apresentacao_congresso_design_inibidores.pptx")


def blank_slide(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def fill_bg(slide, color=WHITE):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color


def add_text(slide, x, y, w, h, text, size=18, color=NAVY, bold=False,
             italic=False, align=PP_ALIGN.LEFT, font="Calibri", anchor=None,
             line_spacing=1.15):
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    if anchor:
        tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(size)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.italic = italic
    p.font.name = font
    p.alignment = align
    p.line_spacing = line_spacing
    return box


def add_bullets(slide, x, y, w, h, items, size=16, color=NAVY, space_after=10):
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"›  {item}"
        p.font.size = Pt(size)
        p.font.color.rgb = color
        p.space_after = Pt(space_after)
        p.line_spacing = 1.15
    return box


def add_kicker(slide, text, x=Inches(0.6), y=Inches(0.35)):
    add_text(slide, x, y, Inches(6), Inches(0.4), text.upper(), size=13,
              color=AMBER, bold=True)


def add_footer(slide, page_no):
    add_text(slide, Inches(0.6), Inches(7.1), Inches(6), Inches(0.3),
              "Design Racional de Inibidores de Tripsina de Lepidoptera — UFV", size=9, color=GRAY)
    add_text(slide, Inches(12.3), Inches(7.1), Inches(0.6), Inches(0.3),
              str(page_no), size=9, color=GRAY, align=PP_ALIGN.RIGHT)


def rect(slide, x, y, w, h, color):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def picture_cover(slide, path, x, y, w, h):
    """Insere imagem preenchendo exatamente a caixa w x h, com crop real
    (pptx crop_left/right/top/bottom) no lado que sobra — sem distorcer
    proporção nem vazar da caixa."""
    from PIL import Image
    im = Image.open(path)
    img_ratio = im.width / im.height
    box_ratio = w / h
    pic = slide.shapes.add_picture(str(path), x, y, width=w, height=h)
    if img_ratio > box_ratio:
        # imagem mais larga que a caixa -> corta laterais
        visible_ratio = box_ratio / img_ratio
        crop = (1 - visible_ratio) / 2
        pic.crop_left = crop
        pic.crop_right = crop
    elif img_ratio < box_ratio:
        # imagem mais alta que a caixa -> corta topo/base
        visible_ratio = img_ratio / box_ratio
        crop = (1 - visible_ratio) / 2
        pic.crop_top = crop
        pic.crop_bottom = crop
    return pic


# ── Slides ───────────────────────────────────────────────────────────────

def slide_title(prs):
    s = blank_slide(prs)
    fill_bg(s, NAVY)
    pic = s.shapes.add_picture(str(ASSETS / "01_cover_hero.png"), 0, 0, width=SLIDE_W)
    if pic.height > SLIDE_H:
        pic.top = int(-(pic.height - SLIDE_H) / 2)
    band = rect(s, 0, Inches(5.35), SLIDE_W, Inches(2.15), NAVY)
    band.fill.fore_color.rgb = NAVY
    add_text(s, Inches(0.7), Inches(5.55), Inches(12), Inches(1.2),
              "Design Racional de Inibidores Peptídicos de Tripsinas de\nLepidoptera por IA Generativa",
              size=30, color=WHITE, bold=True, font="Calibri")
    add_text(s, Inches(0.7), Inches(6.65), Inches(12), Inches(0.6),
              "Estado do projeto — Universidade Federal de Viçosa (UFV) | Setembro de 2026",
              size=16, color=AMBER, italic=True)


def slide_split(prs, page_no, kicker, title, bullets, image_path, image_side="right",
                 title_size=30):
    s = blank_slide(prs)
    fill_bg(s, WHITE)
    text_x = Inches(0.6) if image_side == "right" else Inches(6.9)
    img_x = Inches(6.9) if image_side == "right" else Inches(0.0)
    col_w = Inches(6.0)
    add_kicker(s, kicker, x=text_x)
    add_text(s, text_x, Inches(0.7), col_w, Inches(1.3), title,
              size=title_size, color=NAVY, bold=True)
    add_bullets(s, text_x, Inches(2.15), col_w, Inches(4.5), bullets, size=17)
    picture_cover(s, image_path, img_x, Inches(0.0), Inches(6.433), SLIDE_H)
    add_footer(s, page_no)


def slide_statement(prs, page_no, kicker, title, statement):
    s = blank_slide(prs)
    fill_bg(s, TEAL)
    add_kicker(s, kicker, x=Inches(1.0), y=Inches(1.4))
    add_text(s, Inches(1.0), Inches(1.8), Inches(11.3), Inches(1.0), title,
              size=34, color=WHITE, bold=True)
    add_text(s, Inches(1.0), Inches(3.1), Inches(11.3), Inches(3.2), statement,
              size=22, color=TEAL_LIGHT, italic=False, line_spacing=1.35)
    add_footer_dark(s, page_no)


def add_footer_dark(slide, page_no):
    add_text(slide, Inches(0.6), Inches(7.1), Inches(6), Inches(0.3),
              "Design Racional de Inibidores de Tripsina de Lepidoptera — UFV", size=9, color=TEAL_LIGHT)
    add_text(slide, Inches(12.3), Inches(7.1), Inches(0.6), Inches(0.3),
              str(page_no), size=9, color=TEAL_LIGHT, align=PP_ALIGN.RIGHT)


def slide_figure(prs, page_no, kicker, title, fig_path, caption, fig_width=Inches(7.4)):
    s = blank_slide(prs)
    fill_bg(s, WHITE)
    add_kicker(s, kicker)
    add_text(s, Inches(0.6), Inches(0.7), Inches(12), Inches(0.9), title,
              size=27, color=NAVY, bold=True)

    from PIL import Image
    im = Image.open(fig_path)
    img_ratio = im.width / im.height
    max_h = Inches(4.95)  # y=1.7 ate y=6.65, deixa espaco pro rodape/legenda
    w_by_h = int(max_h * img_ratio)
    w = min(fig_width, w_by_h)
    pic = s.shapes.add_picture(str(fig_path), Inches(0.6), Inches(1.7), width=w)

    add_text(s, Inches(0.6), Inches(1.7) + pic.height + Inches(0.08), w, Inches(0.4),
              "Figura: dado real do projeto (não gerado por IA).", size=10, color=GRAY, italic=True)
    cap_x = Inches(0.6) + w + Inches(0.4)
    cap_w = SLIDE_W - cap_x - Inches(0.6)
    add_bullets(s, cap_x, Inches(1.9), cap_w, Inches(4.8), caption, size=16)
    add_footer(s, page_no)


def slide_table(prs, page_no, kicker, title, headers, rows, note=None, col_widths=None):
    s = blank_slide(prs)
    fill_bg(s, WHITE)
    add_kicker(s, kicker)
    add_text(s, Inches(0.6), Inches(0.7), Inches(12), Inches(0.9), title,
              size=27, color=NAVY, bold=True)

    n_cols = len(headers)
    n_rows = len(rows) + 1
    tbl_w = Inches(12.1)
    tbl_h = Inches(0.55 * n_rows)
    graphic_frame = s.shapes.add_table(n_rows, n_cols, Inches(0.6), Inches(1.9), tbl_w, tbl_h)
    table = graphic_frame.table
    if col_widths:
        total = sum(col_widths)
        for j, wfrac in enumerate(col_widths):
            table.columns[j].width = Emu(int(tbl_w * wfrac / total))

    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        for p in cell.text_frame.paragraphs:
            p.font.bold = True
            p.font.size = Pt(14)
            p.font.color.rgb = WHITE

    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            cell = table.cell(i, j)
            cell.text = str(val)
            cell.fill.solid()
            cell.fill.fore_color.rgb = TEAL_LIGHT if i % 2 == 0 else WHITE
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(13)
                p.font.color.rgb = NAVY

    if note:
        add_text(s, Inches(0.6), Inches(1.9) + tbl_h + Inches(0.3), Inches(12), Inches(1.2),
                  note, size=14, color=GRAY, italic=True)
    add_footer(s, page_no)


def slide_status(prs, page_no, kicker, title, items, status_label="EM ANDAMENTO"):
    s = blank_slide(prs)
    fill_bg(s, WHITE)
    add_kicker(s, kicker)
    add_text(s, Inches(0.6), Inches(0.7), Inches(9.5), Inches(0.9), title,
              size=27, color=NAVY, bold=True)
    badge = rect(s, Inches(10.6), Inches(0.75), Inches(2.1), Inches(0.55), AMBER)
    tf = badge.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = status_label
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.alignment = PP_ALIGN.CENTER
    add_bullets(s, Inches(0.6), Inches(1.8), Inches(12), Inches(4.8), items, size=17)
    add_footer(s, page_no)


def main():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    page = 1
    slide_title(prs)

    slide_split(
        prs, page := page + 1, "Contexto",
        "Lepidópteros-Praga e o Limite dos Métodos Atuais",
        [
            "Spodoptera frugiperda, Anticarsia gemmatalis e espécies afins causam perdas "
            "agrícolas expressivas em culturas de importância econômica",
            "Resistência crescente a toxinas Bt e a inseticidas químicos convencionais",
            "Necessidade real de estratégias complementares de controle, atuando sobre "
            "outros alvos fisiológicos do inseto",
        ],
        ASSETS / "02_contexto_problema.png", image_side="right",
    )

    slide_split(
        prs, page := page + 1, "Contexto",
        "Inibidores de Tripsina como Alvo Terapêutico",
        [
            "Tripsinas digestivas: enzimas centrais na digestão proteica de larvas de Lepidoptera",
            "Inibidores naturais tipo Kunitz/BPTI já têm efeito real documentado sobre "
            "sobrevivência larval",
            "Limitações recorrentes: suscetibilidade à autoclivagem e falta de especificidade "
            "real frente a organismos não-alvo",
        ],
        ASSETS / "03_contexto_estrategia.png", image_side="left",
    )

    slide_statement(
        prs, page := page + 1, "Objetivo",
        "Objetivo do Projeto",
        "Desenvolver, por um pipeline computacional multiagente, peptídeos inibidores de "
        "tripsinas de Lepidoptera-praga — com validação real em cada etapa, não apenas escore "
        "de docking estático — evoluindo de um design linear inicial para geração generativa "
        "por difusão estrutural, ancorada em geometria real do sítio catalítico.",
    )

    slide_split(
        prs, page := page + 1, "Metodologia",
        "Pipeline Computacional Multiagente",
        [
            "Geração estrutural de backbones peptídicos (RFdiffusion)",
            "Desenho de sequência sobre o backbone (ProteinMPNN)",
            "Refinamento de interface (Rosetta) e docking/scoring (Vina, Boltz-2)",
            "Validação: dinâmica molecular real, especificidade vs. não-alvos, resistência "
            "proteolítica in silico",
        ],
        ASSETS / "04_metodologia_pipeline.png", image_side="right",
    )

    slide_split(
        prs, page := page + 1, "Metodologia",
        "Painel de Alvos & Calibração da Escada de Scoring",
        [
            "7 espécies-alvo com especificidade tripsina confirmada por geometria estrutural "
            "real (S. frugiperda, S. litura, O. nubilalis, D. saccharalis, C. includens, "
            "H. virescens, P. xylostella)",
            "Escada de scoring calibrada contra 6 inibidores reais bem caracterizados (BPTI, "
            "SFTI-1, SKTI, Bowman-Birk, EcTI, ApTI) + decoys pareados",
        ],
        ASSETS / "05_painel_alvos.png", image_side="left",
    )

    slide_figure(
        prs, page := page + 1, "Resultados",
        "Qual Método Realmente Discrimina Inibidor Real de Decoy?",
        B05_FIGS / "figA_calibracao_b05_escada.png",
        [
            "Boltz-2 (confidence/pLDDT): 10/10 — único método validado",
            "RMSD de MD curta (2ns, complexo inteiro): 5/10 — equivalente a acaso",
            "MM-PBSA (trajetória única): 4/10 — pior que acaso",
            "Decisão: o loop de geração usa apenas Boltz-2 como scorer",
        ],
        fig_width=Inches(7.6),
    )

    slide_table(
        prs, page := page + 1, "Resultados",
        "Substituindo Heurística por Geometria Estrutural Real",
        ["Item", "Resultado"],
        [
            ["Método anterior", "Heurística de sequência (offset), com bug sistemático em 8/9 espécies"],
            ["Método novo (B1.4)", "Contato real em complexos cristalográficos (2PTC, 1SFI) + equivalência estrutural (foldseek TMalign)"],
            ["Combinações espécie×template aprovadas", "18/18 (TMscore 0,946–0,957; RMSD 1,18–1,41 Å)"],
            ["Resíduos de subsítio transferidos", "100% em todas as espécies"],
            ["Validação cruzada", "100% de concordância com método independente anterior (offset de sequência)"],
        ],
        note="Fonte: docs/bench/b14_subsites_reais.md — dado real, dois métodos totalmente "
             "independentes convergindo no mesmo resultado.",
        col_widths=[0.35, 0.65],
    )

    slide_figure(
        prs, page := page + 1, "Resultados — Achado Crítico",
        "Especificidade Real: A Lacuna Mais Importante",
        FIGS / "fig5_especificidade_SI.png",
        [
            "0/35 candidatos atingem margem de seletividade real (SI ≥ 2,0 kcal/mol) frente a "
            "tripsina humana e Apis mellifera",
            "Vários candidatos têm SI negativo — ligam-se de fato melhor ao não-alvo",
            "O bolso S1 da tripsina é estruturalmente conservado entre espécies — problema "
            "estrutural, não apenas de otimização",
        ],
        fig_width=Inches(6.6),
    )

    slide_figure(
        prs, page := page + 1, "Resultados",
        "Reprodutibilidade Importa: Réplicas Reais de Dinâmica Molecular",
        FIGS / "fig1_replicas_md.png",
        [
            "Candidatos \"mais estáveis\" por réplica única não se confirmam em réplicas "
            "independentes (n=3)",
            "Apenas 4 candidatos confirmaram estabilidade reprodutível: SRTRR, VRYRR, VRRPR, "
            "HRPRRPR",
            "Lição metodológica central do projeto: réplica única pode enganar",
        ],
        fig_width=Inches(6.8),
    )

    slide_status(
        prs, page := page + 1, "Resultados",
        "Pivô Atual — Geração por Difusão (RFdiffusion Cíclico)",
        [
            "Pausa temporária da linha de contrasseleção — foco agora em potência ampla contra "
            "o painel de Lepidoptera-praga",
            "Trilha A: macrociclo via RFdiffusion cíclico, ancorado nos hotspots reais de B1.4",
            "Piloto técnico validado ponta a ponta — fechamento N-C real confirmado (~1,3 Å)",
            "Campanha real em execução: 7 espécies × 5 comprimentos (8–16 aa) × 10 designs "
            "= 350 backbones",
            "Próximo passo: triagem dos candidatos gerados via Boltz-2",
        ],
    )

    slide_split(
        prs, page := page + 1, "Discussão",
        "O Que Este Projeto Ensina Sobre Rigor Computacional",
        [
            "Escore de docking isolado não basta — precisa de calibração contra controles reais",
            "Réplica única de dinâmica molecular pode enganar; variância real muda conclusões",
            "Heurísticas geométricas podem ter bugs sistemáticos — sempre validar contra "
            "estrutura/literatura real",
            "Especificidade deve ser objetivo desde o início do design, não filtro pós-hoc",
        ],
        ASSETS / "04_metodologia_pipeline.png", image_side="right", title_size=27,
    )

    slide_split(
        prs, page := page + 1, "Conclusão",
        "Estado Atual do Projeto",
        [
            "Escada de scoring calibrada: Boltz-2 é o único critério validado até aqui",
            "Geometria real dos subsítios mapeada para todo o painel (B1.4, 18/18 aprovados)",
            "Especificidade real segue como lacuna aberta (0/35 aprovados) — não resolvida, "
            "não escondida",
            "Campanha de geração por difusão em andamento, primeiro resultado amplo do V2",
        ],
        ASSETS / "06_conclusao_futuro.png", image_side="right", title_size=27,
    )

    slide_split(
        prs, page := page + 1, "Próximos Passos",
        "Próximos Passos",
        [
            "Triar os candidatos da campanha de difusão via Boltz-2",
            "Retomar, em módulo separado, a linha de contrasseleção (painel negativo ampliado)",
            "Avaliar resistência proteolítica dos candidatos mais promissores",
            "Contato: eulalio.santos@ufv.br — Universidade Federal de Viçosa (UFV)",
        ],
        ASSETS / "06_conclusao_futuro.png", image_side="left", title_size=27,
    )

    prs.save(str(OUT_PATH))
    print(f"Salvo: {OUT_PATH.resolve()} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()

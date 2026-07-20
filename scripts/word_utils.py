"""Conversao Markdown -> python-docx para o artigo_design_inibidores.docx.

Formatacao inline (negrito/italico/codigo) via markdown-it-py (tokenizer real,
nao regex proprio) para lidar corretamente com combinacoes dentro de celulas
de tabela e paragrafos. Estrutura de blocos (titulos/tabelas/paragrafos) e
percorrida linha-a-linha, dado o formato real e consistente dos 3 arquivos
fonte (ver plano).
"""
from markdown_it import MarkdownIt

_md_inline = MarkdownIt()


def add_inline_markdown(paragraph, text: str) -> None:
    """Adiciona texto com negrito/italico/codigo real (via tokens
    markdown-it-py) como runs no paragrafo python-docx."""
    tokens = _md_inline.parseInline(text)[0].children
    bold_depth = 0
    italic_depth = 0
    for tok in tokens:
        if tok.type == "strong_open":
            bold_depth += 1
        elif tok.type == "strong_close":
            bold_depth -= 1
        elif tok.type == "em_open":
            italic_depth += 1
        elif tok.type == "em_close":
            italic_depth -= 1
        elif tok.type == "code_inline":
            run = paragraph.add_run(tok.content)
            run.font.name = "Consolas"
            run.bold = (bold_depth > 0) or None
            run.italic = (italic_depth > 0) or None
        elif tok.type == "text" and tok.content:
            run = paragraph.add_run(tok.content)
            run.bold = (bold_depth > 0) or None
            run.italic = (italic_depth > 0) or None


def parse_markdown_table(lines: list) -> tuple:
    """Parseia um bloco de tabela Markdown real (header, separador '---',
    linhas de dado) em (headers, rows) de strings cruas (formatacao inline
    aplicada depois, na insercao no docx)."""
    def split_row(line: str) -> list:
        cells = line.strip().strip("|").split("|")
        return [c.strip() for c in cells]

    headers = split_row(lines[0])
    rows = [split_row(line) for line in lines[2:] if line.strip()]
    return headers, rows


def add_markdown_table(document, headers: list, rows: list) -> None:
    """Cria uma tabela real no docx, com negrito/italico/codigo reais em
    cada celula (via add_inline_markdown) — nao so texto plano."""
    table = document.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Light Grid Accent 1"
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.paragraphs[0].clear()
        add_inline_markdown(cell.paragraphs[0], h)
        for run in cell.paragraphs[0].runs:
            run.bold = True
    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            cell = table.cell(i, j)
            cell.paragraphs[0].clear()
            add_inline_markdown(cell.paragraphs[0], val)

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
    bold = False
    italic = False
    for tok in tokens:
        if tok.type == "strong_open":
            bold = True
        elif tok.type == "strong_close":
            bold = False
        elif tok.type == "em_open":
            italic = True
        elif tok.type == "em_close":
            italic = False
        elif tok.type == "code_inline":
            run = paragraph.add_run(tok.content)
            run.font.name = "Consolas"
        elif tok.type == "text" and tok.content:
            run = paragraph.add_run(tok.content)
            run.bold = bold or None
            run.italic = italic or None

from docx import Document
from scripts.word_utils import add_inline_markdown

def test_add_inline_markdown_plain_text():
    doc = Document()
    p = doc.add_paragraph()
    add_inline_markdown(p, "texto simples")
    assert len(p.runs) == 1
    assert p.runs[0].text == "texto simples"
    assert p.runs[0].bold is None
    assert p.runs[0].italic is None

def test_add_inline_markdown_bold_and_italic():
    doc = Document()
    p = doc.add_paragraph()
    add_inline_markdown(p, "**negrito** e *itálico* e normal")
    texts = [(r.text, bool(r.bold), bool(r.italic)) for r in p.runs]
    assert texts == [
        ("negrito", True, False),
        (" e ", False, False),
        ("itálico", False, True),
        (" e normal", False, False),
    ]

def test_add_inline_markdown_code_inline():
    doc = Document()
    p = doc.add_paragraph()
    add_inline_markdown(p, "roda `scripts/prep_pdbs.py` real")
    assert p.runs[1].text == "scripts/prep_pdbs.py"
    assert p.runs[1].font.name == "Consolas"

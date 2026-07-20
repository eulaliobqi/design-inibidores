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

def test_add_inline_markdown_code_inline_inherits_bold():
    doc = Document()
    p = doc.add_paragraph()
    add_inline_markdown(p, "**Bug (commit `e9024bc`):**")
    code_run = next(r for r in p.runs if r.text == "e9024bc")
    assert code_run.bold is True
    assert code_run.font.name == "Consolas"

def test_add_inline_markdown_same_type_nested_emphasis():
    doc = Document()
    p = doc.add_paragraph()
    add_inline_markdown(p, "**outer __inner__ outer**")
    texts = [(r.text, bool(r.bold)) for r in p.runs]
    assert texts == [
        ("outer ", True),
        ("inner", True),
        (" outer", True),
    ]

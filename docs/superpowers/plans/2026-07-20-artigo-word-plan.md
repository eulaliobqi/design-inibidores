# Artigo Completo em Word Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Gerar `artigo_design_inibidores.docx` consolidando `artigo_metodologia.md` + `artigo_resultados.md` + `references.md`, com Introdução e Conclusões novas e as 4 figuras da sessão anterior inseridas nas seções corretas.

**Architecture:** Um módulo de conversão reutilizável (`scripts/word_utils.py`) que transforma trechos de Markdown (cabeçalhos, parágrafos com negrito/itálico/código inline, tabelas) em elementos nativos do python-docx, mais um script de montagem (`scripts/gerar_artigo_word.py`) que lê os 3 arquivos fonte, escreve os 2 blocos de texto novo (Introdução/Conclusões) diretamente, e insere as 4 figuras já geradas nos pontos certos.

**Tech Stack:** Python 3.13 local, `python-docx` 1.2.0 (já instalado), `markdown-it-py` (já instalado — usado só para tokenizar formatação **inline** como negrito/itálico/código; a estrutura de blocos, mais simples e já conhecida pelo formato real dos arquivos-fonte, é percorrida linha-a-linha).

## Global Constraints

- Nunca fabricar conteúdo — Introdução cita só as 27 referências reais de `references.md` (por número `[N]`, nunca uma referência nova); Conclusões sintetizam só achados já documentados em `artigo_resultados.md`/memória do projeto, nenhum número novo.
- Citações mantêm o formato atual de `references.md` (numerado `[N]`, sem reformatar para ABNT/APA).
- Resultados e Discussão ficam combinados, seção-a-seção, exatamente como já estruturado em `artigo_resultados.md` — não separar em blocos distintos.
- Saída: `artigo_design_inibidores.docx` na raiz do repositório (`C:\Users\eulal\.claude\design-inibidores`).
- Figuras nas seções: `fig1_replicas_md.png`→3.11f, `fig2_ocupancia_s1.png`→3.11g, `fig4_fingerprint.png`→3.11i, `fig3_cross_species.png`→3.11j.

## Verificação técnica já feita nesta sessão (base para o código abaixo)

- **`markdown-it-py`** já instalado; `MarkdownIt().parseInline(text)` retorna um token `inline` cujos `.children` incluem `strong_open`/`strong_close` (negrito), `em_open`/`em_close` (itálico), `code_inline` (código, `.content` direto), e `text` (texto puro) — confirmado rodando localmente nesta sessão.
- **Estrutura real de `artigo_metodologia.md`**: título na linha 1, depois direto `## 2. Material e Métodos` (linha 3) e `### 2.1`...`### 2.12` (12 seções, linhas 5-233 até o fim do arquivo). Sem blockquote de preâmbulo.
- **Estrutura real de `artigo_resultados.md`**: título (linha 1), um blockquote `> **Status de preenchimento...**` (linhas 3-16, **não deve entrar no Word** — é um changelog de trabalho, não conteúdo do artigo), `---` (linha 18), depois `## 3. Resultados e Discussão` (linha 20) e `### 3.1`...`### 3.12` + `## 4. Conclusões Parciais` (linhas 22-1206). A partir da linha 1208 há um `## Referências` **embutido** (lista informal por categoria, sem numeração `[N]`) — **não usar essa lista**, a fonte de verdade para Referências é `references.md` (decisão já confirmada no brainstorming). O corpo a converter é, portanto, **linhas 20 a 1206** (para no `---` logo antes do `## Referências` embutido).
- **Formato real de tabela**: `**Tabela N.** legenda` numa linha isolada, depois `| col | col |` + `|---|---|` + linhas de dado — confirmado em `artigo_resultados.md:26-34` (Tabela 1) e `artigo_metodologia.md`.
- **Listas reais existem no corpo de resultados**, sem linha em branco entre itens consecutivos — confirmado em `artigo_resultados.md:122-123` (marcador `- `), `:143-145` (`- `), `:164-166` (`1. `/`2. `/`3. `). Cada item de lista é autocontido numa única linha (não quebra em continuação sem marcador). Isso **precisa** de tratamento explícito no conversor de bloco (Task 3) — sem ele, itens consecutivos seriam mesclados num único parágrafo corrido, perdendo a estrutura de lista (bug real, verificado nesta sessão antes de escrever o plano).
- **Formato real de `references.md`**: 8 categorias (`## I.` a `## VIII.`, linhas 7/46/73/99/124/140/162/187), 27 entradas `**[N]** Autores (Ano).\nTítulo (pode quebrar em várias linhas).\n*Journal* Vol(Issue):Páginas.\nDOI: ... | PubMed: ...\n> anotação em itálico (1-2 linhas, blockquote)` separadas por linha em branco.
- **Referências usadas na Introdução/Conclusões** (números reais, conferidos em `references.md`): `[1]` Patarroyo-Vargas/Oliveira 2017 (cinética *A. gemmatalis*), `[2]` Meriño-Cabrera 2020 (ApTI), `[3]` Fonseca 2023 (SBTI x milho Bt x *S. frugiperda*), `[6]` Zhou 2013 (cristal EcTI), `[8]` Tabosa 2020 (EcTI+Bt), `[9]` Saikhedkar 2019 (Pin-II ciclos), `[10]`/`[11]` (D-aa/ciclização, resistência proteolítica), `[14]` Sultana 2023 (SBTI x *H. zea*), `[17]` Watson 2023 (RFdiffusion), `[18]` Dauparas 2022 (ProteinMPNN), `[19]` (RFpeptides), `[20]`/`[21]`/`[22]` (manejo integrado/biopesticidas), `[23]` Trott/Olson 2010 (Vina), `[24]` Van der Spoel 2005 (GROMACS), `[25]` Chaudhury 2010 (PyRosetta), `[27]` Hedstrom 2002 (mecanismo serino-protease).

---

## Task 1: Conversão de formatação inline (negrito/itálico/código)

**Files:**
- Create: `scripts/word_utils.py`
- Test: `tests/test_word_utils.py`

**Interfaces:**
- Produces: `add_inline_markdown(paragraph, text: str) -> None` — usada pelas Tasks 2 e 3.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_word_utils.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_word_utils.py -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'scripts.word_utils'`

- [ ] **Step 3: Write minimal implementation**

```python
# scripts/word_utils.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_word_utils.py -v`
Expected: PASS (3 testes)

- [ ] **Step 5: Commit**

```bash
git add scripts/word_utils.py tests/test_word_utils.py
git commit -m "feat(artigo-word): formatação inline Markdown→docx (negrito/itálico/código)"
```

---

## Task 2: Conversão de tabelas Markdown

**Files:**
- Modify: `scripts/word_utils.py`
- Modify: `tests/test_word_utils.py`

**Interfaces:**
- Consumes: `add_inline_markdown` (Task 1).
- Produces: `parse_markdown_table(lines: list[str]) -> tuple[list[str], list[list[str]]]`, `add_markdown_table(document, headers: list[str], rows: list[list[str]]) -> None` — usadas pela Task 3.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_word_utils.py (adicionar ao final do arquivo)
from scripts.word_utils import parse_markdown_table, add_markdown_table

def test_parse_markdown_table_real_format():
    lines = [
        "| Modelo       | Res. catalítico 1 | Asp (tríade) |",
        "|--------------|-------------------|--------------|",
        "| ACR157       | His69             | Asp114       |",
        "| **Consenso** | —                 | —            |",
    ]
    headers, rows = parse_markdown_table(lines)
    assert headers == ["Modelo", "Res. catalítico 1", "Asp (tríade)"]
    assert rows == [
        ["ACR157", "His69", "Asp114"],
        ["**Consenso**", "—", "—"],
    ]

def test_add_markdown_table_creates_real_docx_table():
    doc = Document()
    headers = ["A", "B"]
    rows = [["1", "2"], ["3", "**4**"]]
    add_markdown_table(doc, headers, rows)
    table = doc.tables[0]
    assert len(table.rows) == 3  # header + 2 data rows
    assert table.cell(0, 0).paragraphs[0].runs[0].text == "A"
    assert table.cell(0, 0).paragraphs[0].runs[0].bold is True
    assert table.cell(2, 1).paragraphs[0].runs[0].text == "4"
    assert table.cell(2, 1).paragraphs[0].runs[0].bold is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_word_utils.py -v`
Expected: FAIL com `ImportError: cannot import name 'parse_markdown_table'`

- [ ] **Step 3: Write minimal implementation**

```python
# scripts/word_utils.py (adicionar ao final do arquivo)

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
    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            cell = table.cell(i, j)
            cell.paragraphs[0].clear()
            add_inline_markdown(cell.paragraphs[0], val)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_word_utils.py -v`
Expected: PASS (5 testes)

- [ ] **Step 5: Commit**

```bash
git add scripts/word_utils.py tests/test_word_utils.py
git commit -m "feat(artigo-word): conversão de tabelas Markdown→docx real"
```

---

## Task 3: Conversor de bloco (cabeçalhos/parágrafos/tabelas + inserção de figura)

**Files:**
- Modify: `scripts/word_utils.py`
- Modify: `tests/test_word_utils.py`

**Interfaces:**
- Consumes: `add_inline_markdown`, `parse_markdown_table`, `add_markdown_table` (Tasks 1-2).
- Produces: `convert_markdown_body(document, lines: list[str], figure_after_heading: dict[str, str] | None = None) -> None` — usada pela Task 4. `figure_after_heading` mapeia texto exato de um cabeçalho `###` para um path de imagem a inserir logo após o parágrafo seguinte a esse cabeçalho.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_word_utils.py (adicionar ao final do arquivo)
from scripts.word_utils import convert_markdown_body

def test_convert_markdown_body_headings_paragraphs_tables():
    lines = [
        "### 3.1 Título da Seção",
        "",
        "Um parágrafo com **negrito** real.",
        "",
        "**Tabela 1.** Legenda.",
        "",
        "| A | B |",
        "|---|---|",
        "| 1 | 2 |",
        "",
        "---",
        "",
        "### 3.2 Outra Seção",
        "",
        "Outro parágrafo.",
    ]
    doc = Document()
    convert_markdown_body(doc, lines)

    headings = [p.text for p in doc.paragraphs if p.style.name.startswith("Heading")]
    assert headings == ["3.1 Título da Seção", "3.2 Outra Seção"]
    assert len(doc.tables) == 1
    assert doc.tables[0].cell(1, 0).paragraphs[0].runs[0].text == "1"

def test_convert_markdown_body_handles_consecutive_list_items():
    # Formato real confirmado em artigo_resultados.md:143-145 — itens de lista
    # consecutivos, SEM linha em branco entre eles, cada um autocontido numa linha.
    lines = [
        "### Seção com lista",
        "",
        "- **Item A**: descrição do item A.",
        "- **Item B**: descrição do item B.",
        "- **Item C**: descrição do item C.",
        "",
        "1. Primeiro item numerado.",
        "2. Segundo item numerado.",
    ]
    doc = Document()
    convert_markdown_body(doc, lines)
    body_paragraphs = [p for p in doc.paragraphs if not p.style.name.startswith("Heading")]
    # 3 itens de bullet + 2 itens numerados = 5 paragrafos distintos (nao 2 parágrafos mesclados)
    assert len(body_paragraphs) == 5
    assert body_paragraphs[0].runs[0].text == "Item A"  # negrito preservado, marcador removido
    assert body_paragraphs[0].style.name == "List Bullet"
    assert body_paragraphs[3].style.name == "List Number"
    assert "Primeiro item numerado." in body_paragraphs[3].text

def test_convert_markdown_body_inserts_figure_after_heading():
    lines = [
        "### 3.11f Réplicas Reais de MD",
        "",
        "Parágrafo real da seção.",
        "",
        "### 3.11g Próxima Seção",
    ]
    doc = Document()
    convert_markdown_body(
        doc, lines,
        figure_after_heading={"3.11f Réplicas Reais de MD": "outputs/figuras_artigo/fig1_replicas_md.png"},
    )
    has_image = any(
        run._element.findall(".//{http://schemas.openxmlformats.org/drawingml/2006/main}blip")
        for p in doc.paragraphs for run in p.runs
    )
    assert has_image
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_word_utils.py -v`
Expected: FAIL com `ImportError: cannot import name 'convert_markdown_body'`

- [ ] **Step 3: Write minimal implementation**

Antes de rodar, criar uma imagem PNG real mínima de teste (o teste 2 acima referencia o path
real da Fig 1 que já existe em `outputs/figuras_artigo/fig1_replicas_md.png` desde a sessão
anterior — não precisa criar nada novo, o arquivo já existe no repo).

```python
# scripts/word_utils.py (adicionar ao final do arquivo)
from docx.shared import Inches


import re

_BULLET_RE = re.compile(r"^-\s+(.*)")
_NUMBERED_RE = re.compile(r"^\d+\.\s+(.*)")


def convert_markdown_body(document, lines: list, figure_after_heading: dict = None) -> None:
    """Percorre linhas de um corpo Markdown real (##/### cabecalhos,
    paragrafos, listas com marcador '- '/'N. ' (item por linha, sem quebra em
    continuacao — formato real confirmado em artigo_resultados.md), tabelas
    com legenda **Tabela N.**, '---' como separador ignorado) e monta o docx.
    figure_after_heading insere uma imagem logo apos o primeiro paragrafo de
    texto seguinte ao cabecalho indicado."""
    figure_after_heading = figure_after_heading or {}
    pending_figure = None
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i].rstrip("\n")
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped == "---":
            i += 1
            continue

        if stripped.startswith("### "):
            document.add_heading(stripped[4:].strip(), level=2)
            pending_figure = figure_after_heading.get(stripped[4:].strip())
            i += 1
            continue

        if stripped.startswith("## "):
            document.add_heading(stripped[3:].strip(), level=1)
            i += 1
            continue

        bullet_match = _BULLET_RE.match(stripped)
        if bullet_match:
            p = document.add_paragraph(style="List Bullet")
            add_inline_markdown(p, bullet_match.group(1))
            i += 1
            continue

        numbered_match = _NUMBERED_RE.match(stripped)
        if numbered_match:
            p = document.add_paragraph(style="List Number")
            add_inline_markdown(p, numbered_match.group(1))
            i += 1
            continue

        if stripped.startswith("**Tabela") or stripped.startswith("**Table"):
            caption_p = document.add_paragraph()
            add_inline_markdown(caption_p, stripped)
            i += 1
            # proxima linha nao-vazia deve ser a tabela
            while i < n and not lines[i].strip():
                i += 1
            table_lines = []
            while i < n and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            headers, rows = parse_markdown_table(table_lines)
            add_markdown_table(document, headers, rows)
            continue

        # paragrafo normal: junta linhas contiguas nao-vazias, nao-tabela,
        # nao-cabecalho, nao-lista (defensivo — no formato real observado,
        # listas sempre tem linha em branco antes, mas nao custa garantir)
        para_lines = [stripped]
        i += 1
        while (i < n and lines[i].strip()
               and not lines[i].strip().startswith(("#", "|", "**Tabela", "**Table", "---"))
               and not _BULLET_RE.match(lines[i].strip())
               and not _NUMBERED_RE.match(lines[i].strip())):
            para_lines.append(lines[i].strip())
            i += 1
        p = document.add_paragraph()
        add_inline_markdown(p, " ".join(para_lines))

        if pending_figure:
            document.add_picture(pending_figure, width=Inches(6.0))
            pending_figure = None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_word_utils.py -v`
Expected: PASS (8 testes)

- [ ] **Step 5: Commit**

```bash
git add scripts/word_utils.py tests/test_word_utils.py
git commit -m "feat(artigo-word): conversor de bloco Markdown→docx + listas + inserção de figura"
```

---

## Task 4: Script de montagem — capa, Introdução, Métodos, Resultados+figuras, Conclusões, Referências

**Files:**
- Create: `scripts/gerar_artigo_word.py`

**Interfaces:**
- Consumes: `convert_markdown_body`, `add_inline_markdown` de `scripts/word_utils.py` (Tasks 1-3).
- Produces: `artigo_design_inibidores.docx`.

- [ ] **Step 1: Write the script**

```python
# scripts/gerar_artigo_word.py
"""Monta o artigo completo em Word a partir de artigo_metodologia.md,
artigo_resultados.md e references.md — mais Introducao e Conclusoes novas
(redigidas nesta etapa, citando so material ja verificado).

Uso: python -m scripts.gerar_artigo_word
"""
import re
from pathlib import Path

from docx import Document
from docx.shared import Pt

from scripts.word_utils import add_inline_markdown, convert_markdown_body

OUT_PATH = Path("artigo_design_inibidores.docx")

FIGURE_AFTER_HEADING = {
    "3.11f Réplicas Reais de MD (n=3) — Reprodutibilidade da Estabilidade (2026-07-19)":
        "outputs/figuras_artigo/fig1_replicas_md.png",
    "3.11g Persistência Competitiva Real — Ocupância do Bolso S1 ao Longo da Trajetória (2026-07-19)":
        "outputs/figuras_artigo/fig2_ocupancia_s1.png",
    "3.11i Assinatura Digital de Interação — Síntese das Frentes 2+3 (2026-07-19)":
        "outputs/figuras_artigo/fig4_fingerprint.png",
    "3.11j Fechamento do R3 — Matriz Consolidada TOP-13 × 11 Espécies (2026-07-19)":
        "outputs/figuras_artigo/fig3_cross_species.png",
}

INTRODUCAO = """
Lepidópteros-praga como *Spodoptera frugiperda* e *Anticarsia gemmatalis* causam perdas
significativas em culturas de importância econômica, e a resistência crescente a toxinas Bt e a
inseticidas químicos tem motivado a busca por estratégias complementares de controle [3][14][20].
Inibidores de proteases digestivas — em particular de tripsinas, enzimas centrais na digestão
proteica de larvas de Lepidoptera — representam uma dessas estratégias, atuando diretamente sobre
a fisiologia digestiva do inseto [1][27].

Inibidores naturais do tipo Kunitz/BPTI já demonstraram atividade real contra tripsinas de
Lepidoptera, incluindo inibição não-competitiva tight-binding com efeito mensurável sobre
sobrevivência larval [2] e sinergia com toxinas Bt [8]. No entanto, esses inibidores enfrentam
limitações práticas recorrentes: suscetibilidade à própria clivagem proteolítica quando contêm
sítios internos reconhecíveis pela protease-alvo, o que motiva estratégias de proteção química
como substituição por D-aminoácidos e ciclização [9][10][11].

Ferramentas de IA generativa para design de proteínas — RFdiffusion, para geração de novos
esqueletos estruturais [17], e ProteinMPNN, para desenho de sequência sobre um esqueleto dado
[18], além de extensões recentes para macrociclos [19] — abrem uma via alternativa à triagem de
inibidores naturais: gerar candidatos peptídicos inéditos, ancorados computacionalmente ao sítio
catalítico do alvo, e validá-los com o mesmo rigor experimental in silico já estabelecido para
docking molecular [23], dinâmica molecular [24] e refinamento de interface [25][26].

Este trabalho descreve um pipeline computacional multiagente que integra essas ferramentas para
o design racional de novos peptídeos inibidores de tripsinas de Lepidoptera, com ênfase explícita
em validação real e reprodutível em cada etapa — não apenas escore de docking estático, mas
estabilidade em réplicas independentes de dinâmica molecular, persistência real de contato com o
sítio catalítico, especificidade frente a organismos não-alvo, e amplo espectro contra múltiplas
espécies-praga de Lepidoptera.
""".strip()

CONCLUSOES = """
O pipeline multiagente gerou e avaliou, com dado real em cada etapa, um espaço amplo de candidatos
a inibidor peptídico de tripsina: 330 esqueletos reais via RFdiffusion, mais de 120 mil sequências
via ProteinMPNN, e milhares de dockings reais contra o receptor primário e 11 espécies de
Lepidoptera-praga. Desse espaço, um subconjunto de 13 candidatos (TOP-13) foi submetido a teste
aprofundado — réplicas reais de dinâmica molecular, persistência de contato com o sítio catalítico,
tríade catalítica via PLIP, e matriz cross-species completa.

O achado metodológico mais importante deste trabalho é que a estabilidade avaliada por uma única
réplica de dinâmica molecular não é confiável isoladamente: os dois candidatos historicamente
classificados como "mais estáveis do pipeline" a partir de réplica única
(RLREELKKAEEWLEKRRKEE, 0,294 nm; VRTRR, 0,194 nm) mostraram desvio-padrão real de 0,606 nm e
0,360 nm quando testados em réplicas independentes — variação grande o suficiente para invalidar a
classificação original. Apenas quatro candidatos (SRTRR, VRYRR, VRRPR, HRPRRPR) confirmaram
estabilidade reprodutível (DP<0,05 nm) nas três réplicas reais.

A análise de persistência real do contato com o bolso catalítico S1 refinou ainda mais esse
quadro: `VRRPR`, apesar de estabilidade reprodutível por RMSD do complexo inteiro, na verdade perde
contato real com o sítio ao longo das réplicas (ocupância a 6 Å caindo de 67,6% para 0,15% entre
réplicas) — evidência de que baixa variância estrutural não implica permanência funcional no sítio
catalítico. `VRYRR` destacou-se como o único candidato com contato tipo salt-bridge real e
constante mesmo no corte mais estrito (4 Å) nas três réplicas.

Dois bloqueadores permanecem sem solução simultânea em nenhum candidato: especificidade real
(0/23 candidatos aprovados com margem de seletividade ≥2,0 kcal/mol frente a tripsina humana e
*Apis mellifera*) e resistência proteolítica universal entre os candidatos de maior afinidade
(susceptibilidade generalizada a autoclivagem por resíduos P1-internos básicos). Um candidato
(SEEEVLAANEAYAAAHTAYN) reuniu pela primeira vez resistência estrutural real (ausência de sítios
K/R internos), afinidade competitiva e estabilidade em MD — mas ainda sem margem de especificidade
comprovada.

A verificação cruzada e independente de cada etapa computacional — incluindo a identificação e
correção de um erro real no algoritmo de detecção de tríade catalítica para uma das espécies
testadas, e a confirmação de que as demais tríades (incluindo as dos quatro receptores primários)
correspondem de fato ao mínimo geométrico global entre resíduos His/Asp/Ser — foi tratada como
parte integrante do método, não como etapa opcional. Os candidatos reprodutivelmente estáveis e
com contato real confirmado (`SRTRR`, `VRYRR`, `VRRPR`, `HRPRRPR`) constituem a base mais sólida
para as próximas etapas do projeto, ainda pendentes de resolução de especificidade e resistência
proteolítica antes de qualquer indicação para síntese e validação experimental.
""".strip()


def add_references(document, references_path: Path) -> None:
    text = references_path.read_text(encoding="utf-8")
    entries = re.split(r"\n(?=\*\*\[\d+\]\*\*)", text.split("## I.", 1)[1] if "## I." in text else text)
    document.add_heading("Referências", level=1)
    for block in entries:
        block = block.strip()
        if not block or not block.startswith("**["):
            continue
        lines = [l for l in block.splitlines() if l.strip()]
        citation_lines = [l for l in lines if not l.strip().startswith(">")]
        p = document.add_paragraph()
        add_inline_markdown(p, " ".join(l.strip() for l in citation_lines))


def build_cover(document) -> None:
    title = document.add_heading(
        "Design Racional de Inibidores Peptídicos de Tripsinas de Lepidoptera por IA Generativa",
        level=0,
    )
    p = document.add_paragraph()
    p.add_run("Universidade Federal de Viçosa (UFV) — Viçosa-MG, Brasil").italic = True
    document.add_page_break()


def main():
    document = Document()
    style = document.styles["Normal"]
    style.font.size = Pt(11)

    build_cover(document)

    document.add_heading("Introdução", level=1)
    for para in INTRODUCAO.split("\n\n"):
        p = document.add_paragraph()
        add_inline_markdown(p, para.replace("\n", " "))

    metodologia_lines = Path("artigo_metodologia.md").read_text(encoding="utf-8").splitlines()
    convert_markdown_body(document, metodologia_lines[2:])  # pula titulo (linha 1) + linha em branco

    resultados_all = Path("artigo_resultados.md").read_text(encoding="utf-8").splitlines()
    resultados_body = resultados_all[19:1206]  # linhas 20-1206 (1-indexed) = corpo real, sem changelog/refs embutidas
    convert_markdown_body(document, resultados_body, figure_after_heading=FIGURE_AFTER_HEADING)

    document.add_heading("Conclusões", level=1)
    for para in CONCLUSOES.split("\n\n"):
        p = document.add_paragraph()
        add_inline_markdown(p, para.replace("\n", " "))

    add_references(document, Path("references.md"))

    document.save(str(OUT_PATH))
    print(f"Salvo: {OUT_PATH.resolve()}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Rodar e conferir**

Run: `python -m scripts.gerar_artigo_word`
Expected: `Salvo: ...\artigo_design_inibidores.docx`, sem traceback.

- [ ] **Step 3: Verificação de estrutura (script de conferência, não precisa ser um arquivo novo — rodar via `python -c`)**

```bash
python -c "
from docx import Document
d = Document('artigo_design_inibidores.docx')
headings = [p.text for p in d.paragraphs if p.style.name.startswith('Heading')]
print('Total de headings:', len(headings))
print('Total de tabelas:', len(d.tables))
print('Primeiros 5 headings:', headings[:5])
print('Últimos 5 headings:', headings[-5:])
assert 'Introdução' in headings
assert 'Conclusões' in headings
assert 'Referências' in headings
assert any('3.11f' in h for h in headings)
assert any('3.11j' in h for h in headings)
print('OK — estrutura básica presente')
"
```

Expected: `OK — estrutura básica presente`, contagem de tabelas próxima ao número de `**Tabela` /
`**Table` encontrados nos 2 arquivos-fonte (conferir manualmente com
`grep -c "^\*\*Tabela" artigo_metodologia.md artigo_resultados.md` e comparar).

- [ ] **Step 4: Conferir as 4 figuras foram inseridas**

```bash
python -c "
from docx import Document
d = Document('artigo_design_inibidores.docx')
n_images = sum(1 for rel in d.part.rels.values() if 'image' in rel.reltype)
print('Total de imagens embutidas:', n_images)
assert n_images == 4, f'esperado 4 imagens, achou {n_images}'
print('OK — 4 figuras embutidas')
"
```

Expected: `OK — 4 figuras embutidas`.

- [ ] **Step 5: Conferir que a Introdução só cita referências reais**

```bash
python -c "
import re
from pathlib import Path
intro = Path('scripts/gerar_artigo_word.py').read_text(encoding='utf-8')
intro_block = intro.split('INTRODUCAO = ')[1].split('CONCLUSOES')[0]
cited = set(int(n) for n in re.findall(r'\[(\d+)\]', intro_block))
real_refs = set(int(n) for n in re.findall(r'^\*\*\[(\d+)\]\*\*', Path('references.md').read_text(encoding='utf-8'), re.MULTILINE))
missing = cited - real_refs
print('Citadas na Introdução:', sorted(cited))
print('Existem em references.md:', missing == set())
assert not missing, f'Introdução cita referência inexistente: {missing}'
"
```

Expected: nenhuma referência ausente (`missing == set()` → `True`).

- [ ] **Step 6: Commit**

```bash
git add scripts/gerar_artigo_word.py artigo_design_inibidores.docx
git commit -m "feat(artigo-word): monta artigo_design_inibidores.docx completo"
```

---

## Limitação conhecida e aceita

`markdown-it-py` sem plugins não reconhece `~~riscado~~` (sintaxe GFM, fora do CommonMark core) —
confirmado nesta sessão: passa como texto literal (`~~texto~~`), sem quebrar a conversão. Afeta 2
ocorrências reais em `artigo_resultados.md` (candidatos descartados marcados com `~~`, Seção
3.8b) — aparecerão com os `~~` literais em vez de texto riscado no Word. Cosmético, não bloqueia
a legibilidade (o texto ao redor já deixa claro que são candidatos descartados); não vale a pena
adicionar um plugin de markdown-it só para 2 ocorrências.

## Self-Review (spec coverage)

- **Capa**: `build_cover()`, Task 4. ✓
- **Introdução nova, citando só refs reais**: `INTRODUCAO`, verificado no Step 5 da Task 4. ✓
- **Material e Métodos completo**: `convert_markdown_body` sobre `artigo_metodologia.md` inteiro, Task 4. ✓
- **Resultados e Discussão combinados, sem separar**: `convert_markdown_body` sobre o corpo real de `artigo_resultados.md` (linhas 20-1206), preservando a estrutura seção-a-seção existente. ✓
- **4 figuras nas seções corretas**: `FIGURE_AFTER_HEADING`, verificado no Step 4 da Task 4. ✓
- **Conclusões novas, sintetizando achados reais já documentados**: `CONCLUSOES`, Task 4 — nenhum número novo, todos já publicados em `artigo_resultados.md`/memória do projeto (réplicas MD, ocupância S1, especificidade 0/23, resistência 0/20, tríades verificadas). ✓
- **Referências no formato atual (numerado, sem reformatar)**: `add_references()`, Task 4 — reusa o texto real de `references.md`, só remove as linhas de anotação (`>`) para o corpo do artigo formal. ✓
- **Changelog/blockquote de status excluído**: `resultados_all[19:1206]` pula as linhas 1-19 (título + blockquote + `---`). ✓
- **Lista de referências embutida em `artigo_resultados.md` (linha 1208+) excluída**: corpo limitado a `[:1206]`. ✓
- **Listas reais (bullet/numeradas) preservadas como listas, não mescladas em parágrafo corrido**: tratamento explícito em `convert_markdown_body` (Task 3), testado contra o formato real confirmado em `artigo_resultados.md:143-145`. ✓

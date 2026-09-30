"""Monta manuscript_pt_src.md a partir de pt_parts/, resolve citacoes, insere figuras e painel de
conformidade, e gera o Word (pandoc + pos-processamento python-docx).
Uso: python build_docx_pt.py  ->  Manuscrito_PT_leitura.docx
"""
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

from docx import Document
from docx.enum.text import WD_COLOR_INDEX
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

HERE = Path(__file__).parent
sys.stdout.reconfigure(encoding="utf-8")

# ---------- 1. montar a fonte PT
parts = [(HERE / "pt_parts" / f"p{i}.md").read_text(encoding="utf-8") for i in range(1, 6)]
src = "\n".join(parts)

# caracteres suspeitos (CJK, cirilico, etc.)
bad = sorted({c for c in src if ord(c) > 0x2FFF or 0x0400 <= ord(c) <= 0x04FF or 0x0590 <= ord(c) <= 0x06FF})
if bad:
    raise SystemExit(f"caracteres nao latinos encontrados: {bad}")
(HERE / "manuscript_pt_src.md").write_text(src, encoding="utf-8")

# decimais com virgula nas tabelas 1 e 3 (Tabela 4 ja esta no formato PT)
lines, cur_tab = src.split("\n"), None
for i, l in enumerate(lines):
    m = re.match(r"\*\*Tabela (\d)\.", l)
    if m:
        cur_tab = int(m.group(1))
    if l.startswith("|") and cur_tab in (1, 3):
        lines[i] = re.sub(r"(?<=\d)\.(?=\d)", ",", l)
    if l.startswith("### ") and not l.startswith("### 3.3") and cur_tab == 3:
        cur_tab = None
src = "\n".join(lines)

# ---------- 2. citacoes
meta = json.load(open(HERE / "refs_meta.json", encoding="utf-8"))
refs = json.load(open(HERE / "refs_resolved.json", encoding="utf-8"))
used = []


def auth(k):
    m = meta[k]
    f = m["fam"]
    if m["n"] == 1:
        return f[0]
    if m["n"] == 2:
        return f"{f[0]} e {f[1]}"
    return f"{f[0]} et al."


def sub(mo):
    body = mo.group(1)
    if body.startswith("@"):
        k = body[1:]
        used.append(k)
        return f"{auth(k)} ({meta[k]['year']})"
    if body.startswith("#"):
        k = body[1:]
        used.append(k)
        return f"{auth(k)}, {meta[k]['year']}"
    keys = [x.strip() for x in body.split(";")]
    for k in keys:
        if k not in meta:
            raise SystemExit(f"citacao sem referencia: {k}")
        used.append(k)
    return "(" + "; ".join(f"{auth(k)}, {meta[k]['year']}" for k in keys) + ")"


src = re.sub(r"\{([@#]?[a-z0-9]+(?:;[a-z0-9 ]+)*)\}", sub, src)
cited = sorted(set(used), key=lambda k: (meta[k]["fam"][0].lower(), meta[k]["year"]))
unused = sorted(set(meta) - set(used))
if unused:
    raise SystemExit(f"referencias nao citadas: {unused}")

# ---------- 3. figuras inline (legendas extraidas de 'Legendas das figuras')
leg_block = src.split("## Legendas das figuras")[1]
legends = dict(re.findall(r"\*\*Figura (\d)\.\*\* (.*?)(?=\n\n\*\*Figura|\Z)", leg_block, flags=re.S))
src = src.split("\n---\n\n## Legendas das figuras")[0]
FIG = {1: "Figure1_pipeline.png", 2: "Figure2_calibration.png", 3: "Figure3_motif_screen.png"}


def img(n):
    return f"\n![**Figura {n}.** {legends[str(n)].strip()}](figures/{FIG[n]}){{width=16.5cm}}\n"


src = src.replace("\n---\n\n## 2 Material e métodos", img(1) + "\n---\n\n## 2 Material e métodos")
src = src.replace("\n### 3.4 A campanha de geração", img(2) + "\n### 3.4 A campanha de geração")
src = src.replace("\n### 3.6 Confiança do Boltz-2", img(3) + "\n### 3.6 Confiança do Boltz-2")

# marcadores pendentes -> span com estilo
src = re.sub(r"\[\[(.*?)\]\]", lambda m: '[' + m.group(1).replace("[", "(").replace("]", ")") + ']{custom-style="Pendente"}', src, flags=re.S)
src = re.sub(r"\[(LISTA DE AUTORES A COMPLETAR|A COMPLETAR|visibilidade do repositório[^\]]*)\]",
             lambda m: '[' + m.group(1) + ']{custom-style="Pendente"}', src)

# ---------- 4. metricas (do manuscrito em ingles, fonte de verdade para a submissao)
en = (HERE / "manuscript_src.md").read_text(encoding="utf-8")


def words(t):
    t = re.sub(r"\[\[.*?\]\]", "", t, flags=re.S)
    t = re.sub(r"\{[^}]*\}", "x", t)                       # cada citacao ~1 token
    t = "\n".join(l for l in t.split("\n") if not l.startswith(("|", "#", "**Table", "**Figure", "![")))
    return len(t.split())


abs_en = en.split("## Abstract")[1].split("## 1 Introduction")[0]
body_en = en.split("## 1 Introduction")[1].split("## Figure legends")[0]
abs_pt = parts[0].split("## Resumo")[1].split("## 1 Introdução")[0]
body_pt = "\n".join(parts[0].split("## 1 Introdução")[1:] + parts[1:4])
title_en = en.split("\n")[0].lstrip("# ").strip()
n_abs_en, n_body_en = words(abs_en.replace("---", "")), words(body_en)
n_abs_pt, n_body_pt = words(abs_pt.replace("---", "")), words(body_pt)
n_kw = len(re.search(r"\*\*Keywords:\*\* (.*)", en).group(1).split(","))
n_tab = len(re.findall(r"^\*\*Table \d\.", en, flags=re.M))
n_fig = len(re.findall(r"^\*\*Figure \d\.", en, flags=re.M))

panel = f"""
# Documento de leitura e avaliação manual

**Manuscrito:** {title_en}
**Destino:** *Frontiers in Natural Products* (Frontiers) — seção *Informatics and Computational Methods*
**Versão em português para leitura interna.** O texto para submissão é o manuscrito em inglês (`manuscript/manuscript.md`); esta tradução mantém os números idênticos, com vírgula decimal e ponto de milhar, e os rótulos de classe (RESISTENTE, MARGINAL, SUSCEPTIVEL) do código. As referências permanecem em inglês, como exige a revista.

## Como ler as marcações

- Trechos em **amarelo** marcam o que ainda depende de simulações em andamento ou de informação dos autores.
- Nada nesta versão foi inventado para preencher lacunas: os resultados de dinâmica molecular (Seção 3.7) e as frases que deles dependem estão pendentes.

## Painel de conformidade com as métricas da revista

| Requisito | Limite / padrão | Situação atual | Estado |
|---|---|---|---|
| Tipo de artigo | Original Research (IMRaD: Resumo, Introdução, Material e métodos, Resultados, Discussão) | Estrutura cumprida | OK |
| Extensão do texto principal | ≤ 12.000 palavras (Original Research) | {n_body_en:,} palavras no original em inglês (corpo sem tabelas, títulos e legendas; cada citação contada como uma palavra); tradução: {n_body_pt:,} | OK (há margem para a Seção 3.7) |
| Resumo | ≤ 350 palavras | {n_abs_en} palavras no original em inglês (sem o trecho pendente); tradução: {n_abs_pt} | OK (a frase de MD acrescentará cerca de 30 palavras) |
| Palavras-chave | 5–8 | {n_kw} | OK |
| Título | informativo e conciso | {len(title_en)} caracteres | conferir limite no site |
| Título curto | ≤ cerca de 50 caracteres | 50 caracteres | conferir no site |
| Figuras | resolução mínima de 300 dpi, arquivos separados | {n_fig} figuras (PNG 300 dpi e PDF vetorial, largura 180 mm); a Figura 4 (MD) depende da Seção 3.7 | pendente |
| Tabelas | editáveis, com legenda | {n_tab} tabelas | OK |
| Referências | estilo Frontiers (autor-ano), com DOI | {len(cited)} referências, todas resolvidas no Crossref/PubMed; nenhuma citada sem estar na lista, nenhuma na lista sem ser citada | OK |
| Declaração de disponibilidade de dados | obrigatória | código no repositório; falta confirmar visibilidade e DOI de arquivamento | pendente |
| Contribuições dos autores, financiamento, conflito de interesses, agradecimentos | obrigatórios | não redigidos | pendente |
| Declaração de uso de IA generativa | exigida pela Frontiers | não redigida | pendente |
| Declaração de ética | quando aplicável | não se aplica (sem animais, humanos ou dados pessoais) | a declarar |
| Lista de autores e afiliações | obrigatória | não preenchida | pendente |
| Adequação ao escopo | seção *Informatics and Computational Methods* existe na revista | trabalho computacional sobre inibidores de origem natural como controles | risco a verificar |

**Fonte e certeza dos limites.** Os limites acima vêm de páginas de tipos de artigo de outras revistas Frontiers e de resultados de busca sobre a *Frontiers in Natural Products* (existência da seção *Informatics and Computational Methods*, extensão de 12.000 palavras para Original Research). A página oficial de tipos de artigo da própria revista não pôde ser aberta nesta sessão; confira os limites de título, resumo e palavras-chave diretamente no site antes de submeter. **Risco de escopo:** a revista descreve a seção de atividades biológicas com "análise *in silico* acompanhada de validação experimental"; este trabalho é puramente computacional e não afirma atividade. Vale confirmar com a revista se um estudo puramente computacional é aceito nessa seção.

## Pendências antes da submissão

1. Seção 3.7 (dinâmica molecular de 50 ns dos melhores candidatos), frase de MD no Resumo e frase de MD na Seção 4.1: dependem de simulações em andamento no servidor.
2. Figura 4 (ocupância de S1 por espécie), a gerar quando as simulações terminarem.
3. Lista de autores, afiliações, contribuições, financiamento, conflito de interesses, declaração de IA generativa e DOI de arquivamento do código.
4. Decisão dos autores: refazer o desenho de sequências com o receptor fixo e permitindo um P1 básico (Seção 4.4 iv e 4.5).

"""

full = panel + "\n" + src + "\n\n## Referências\n\n" + "\n\n".join(refs[k] for k in cited) + "\n"
(HERE / "manuscript_pt.md").write_text(full, encoding="utf-8")

# ---------- 5. pandoc
out = HERE / "Manuscrito_PT_leitura.docx"
ref_doc = HERE / "_reference.docx"
if not ref_doc.exists():
    subprocess.run(["pandoc", "-o", str(ref_doc), "--print-default-data-file", "reference.docx"], check=True)
subprocess.run(["pandoc", str(HERE / "manuscript_pt.md"), "-f", "markdown+pipe_tables+subscript+superscript",
                "-o", str(out), f"--reference-doc={ref_doc}", f"--resource-path={HERE}"], check=True)

# ---------- 6. pos-processamento
doc = Document(str(out))
for s in doc.sections:
    s.left_margin = s.right_margin = Cm(2.5)
    s.top_margin = s.bottom_margin = Cm(2.5)
    ln = OxmlElement("w:lnNumType")
    ln.set(qn("w:countBy"), "1")
    ln.set(qn("w:restart"), "continuous")
    s._sectPr.append(ln)
    # numero de pagina no rodape
    p = s.footer.paragraphs[0] if s.footer.paragraphs else s.footer.add_paragraph()
    p.alignment = 1
    for tag, txt in (("begin", None), (None, "PAGE"), ("end", None)):
        r = p.add_run()
        if tag:
            fc = OxmlElement("w:fldChar")
            fc.set(qn("w:fldCharType"), tag)
            r._r.append(fc)
        else:
            it = OxmlElement("w:instrText")
            it.set(qn("xml:space"), "preserve")
            it.text = txt
            r._r.append(it)

for name in ("Normal", "Body Text", "First Paragraph", "Compact"):
    if name in [s.name for s in doc.styles]:
        st = doc.styles[name]
        st.font.name = "Times New Roman"
        st.font.size = Pt(12)
        st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        if name in ("Body Text", "First Paragraph"):
            st.paragraph_format.line_spacing = 1.5
            st.paragraph_format.space_after = Pt(6)
for name, size in (("Heading 1", 16), ("Heading 2", 14), ("Heading 3", 12), ("Title", 18)):
    if name in [s.name for s in doc.styles]:
        st = doc.styles[name]
        st.font.name = "Times New Roman"
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = None
        st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
if "Pendente" in [s.name for s in doc.styles]:
    doc.styles["Pendente"].font.highlight_color = WD_COLOR_INDEX.YELLOW
    doc.styles["Pendente"].font.bold = True

for t in doc.tables:
    t.style = "Table Grid" if "Table Grid" in [s.name for s in doc.styles] else t.style
    tbl = t._tbl
    tblPr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{edge}")
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), "4")
        e.set(qn("w:color"), "808080")
        borders.append(e)
    tblPr.append(borders)
    for row in t.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.line_spacing = 1.0
                for r in p.runs:
                    r.font.size = Pt(9)
    for cell in t.rows[0].cells:
        for p in cell.paragraphs:
            for r in p.runs:
                r.bold = True
for p in doc.paragraphs:
    if p.text.startswith("Desenho computacional e triagem"):
        p.paragraph_format.page_break_before = True
        break
doc.save(str(out))
print(f"ok -> {out.name} | corpo EN {n_body_en} palavras | resumo EN {n_abs_en} | PT corpo {n_body_pt} resumo {n_abs_pt} | refs {len(cited)}")

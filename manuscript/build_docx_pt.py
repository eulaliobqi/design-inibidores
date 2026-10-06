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
legends = dict(re.findall(r"\*\*Figura (S?\d+)\.\*\* (.*?)(?=\n\n\*\*Figura|\Z)", leg_block, flags=re.S))
src = src.split("\n---\n\n## Legendas das figuras")[0]
FIG = {"1": "figures/final/Figure1_pipeline.png", "2": "figures/final/Figure2_calibration.png",
       "3": "figures/pt/fig5_funil.png", "4": "figures/pt/fig8_reprodutibilidade.png",
       "5": "figures/pt/fig11_md_triagem_10ns.png", "6": "figures/final/Figure6_energy_ranking.png",
       "7": "figures/final/Figure7_pH_comparison.png", "8": "figures/final/Figure8_candidate_poses.png",
       "S10": "figures/final/FigureS10_energy_trajectories.png",
       "S1": "figures/pt/fig2_regra_dura.png", "S2": "figures/final/FigureS2_motif_screen.png",
       "S3": "figures/pt/fig6_composicao.png", "S4": "figures/pt/fig9_reescore_e2.png",
       "S5": "figures/pt/fig10_top3_pose.png", "S6": "figures/pt/figS2_anel_ciclico_charmm36.png",
       "S7": "figures/pt/fig12_candidatos_finais.png", "S8": "figures/pt/fig7_boltz2_1a_rodada.png",
       "S9": "figures/pt/figS1_regras_motivo.png"}


def img(n, w="16.5cm"):
    return f"\n![**Figura {n}.** {legends[n].strip()}]({FIG[n]}){{width={w}}}\n"


src = src.replace("\n---\n\n## 2 Material e métodos", img("1") + "\n---\n\n## 2 Material e métodos")
src = src.replace("\n### 3.3 Geração", img("2") + "\n### 3.3 Geração")
src = src.replace("\n### 3.4 Co-dobramento", img("3") + "\n### 3.4 Co-dobramento")
src = src.replace("\n### 3.5 Simulações", img("4") + "\n### 3.5 Simulações")
src = src.replace("\n### 3.6 Filtro de energia", img("5") + "\n### 3.6 Filtro de energia")
src = src.replace("\n### 3.7 pH 8,2", img("6") + "\n### 3.7 pH 8,2")
src = src.replace("\n### 3.8 Peptídeos", img("7") + "\n### 3.8 Peptídeos")
src = src.replace("\n---\n\n## 4 Discussão", img("8") + "\n---\n\n## 4 Discussão") if "\n---\n\n## 4 Discussão" in src else src.replace("\n## 4 Discussão", img("8") + "\n## 4 Discussão")
for fid in ("1", "2", "3", "4", "5", "6", "7", "8"):
    assert f"**Figura {fid}.**" in src, f"figura {fid} nao inserida"
src = src.rstrip() + "\n\n## Figuras suplementares\n" + "".join(img(k, "13cm") for k in ("S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10"))

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
short_en = re.search(r"\*\*Running title:\*\* (.*)", en).group(1).strip()
n_abs_en, n_body_en = words(abs_en.replace("---", "")), words(body_en)
n_abs_pt, n_body_pt = words(abs_pt.replace("---", "")), words(body_pt)
n_kw = len(re.search(r"\*\*Keywords:\*\* (.*)", en).group(1).split(","))
n_tab = len(re.findall(r"^\*\*Table \d\.", en, flags=re.M))
n_fig = len(re.findall(r"^\*\*Figure \d+\.", en, flags=re.M))
n_figs = len(re.findall(r"^\*\*Figure S\d\.", en, flags=re.M))

panel = f"""
# Documento de leitura e avaliação manual

**Manuscrito:** {title_en}
**Destino:** *Frontiers in Natural Products* (Frontiers) — seção *Informatics and Computational Methods*
**Versão em português para leitura interna.** O texto para submissão é o manuscrito em inglês (`manuscript/manuscript.md`); esta tradução mantém os números idênticos, com vírgula decimal e ponto de milhar, e os rótulos de classe (RESISTENTE, MARGINAL, SUSCEPTIVEL) do código. As referências permanecem em inglês, como exige a revista.

## Como ler as marcações

- Trechos em **amarelo** marcam o que ainda depende de simulações em andamento ou de informação dos autores.
- Nada nesta versão foi inventado para preencher lacunas: o que ainda depende de decisão ou de informação dos autores (lista de peptídeos recomendados, robustez ao pH) está marcado.

## Painel de conformidade com as métricas da revista

| Requisito | Limite / padrão | Situação atual | Estado |
|---|---|---|---|
| Tipo de artigo | Original Research (IMRaD: Resumo, Introdução, Material e métodos, Resultados, Discussão) | Estrutura cumprida | OK |
| Extensão do texto principal | ≤ 12.000 palavras (Original Research; página oficial de tipos de artigo da revista, conferida em 30/09/2026) | {n_body_en:,} palavras no original em inglês (corpo sem tabelas, títulos e legendas; cada citação contada como uma palavra); tradução: {n_body_pt:,} | OK (margem de {12000 - n_body_en:,} palavras) |
| Resumo | ≤ 350 palavras (convenção da Frontiers; a página da revista não especifica o número) | {n_abs_en} palavras no original em inglês (reescrito em 05/10/2026 para caber no limite); tradução: {n_abs_pt} | OK |
| Palavras-chave | 5–8 (diretrizes gerais da Frontiers) | {n_kw} | OK |
| Título | informativo e conciso; sem limite de caracteres na página da Frontiers | título oficial definido pelos autores, {len(title_en)} caracteres | OK |
| Título curto | ≤ cerca de 50 caracteres (prática da Frontiers; não especificado na página) | {len(short_en)} caracteres | OK |
| Figuras | 300 dpi no tamanho final; TIFF, JPEG ou EPS; RGB | {n_fig} figuras + {n_figs} suplementares em PNG, TIFF (LZW) e PDF vetorial a 300 dpi, largura 180 mm, RGB; as Figuras 13 e 14 (controles) foram retiradas | OK |
| Tabelas | editáveis, com legenda | {n_tab} tabelas | OK |
| Referências | autor-ano (Harvard), seis primeiros autores e "et al.", com DOI | {len(cited)} referências, todas com metadados conferidos no Crossref/PubMed; nenhuma citada sem estar na lista, nenhuma na lista sem ser citada | OK |
| Declaração de disponibilidade de dados | obrigatória | seção criada; falta confirmar visibilidade do repositório e DOI de arquivamento | pendente |
| Contribuições dos autores, financiamento, conflito de interesses, agradecimentos | obrigatórios | seções criadas, conteúdo a completar pelos autores | pendente |
| Declaração de uso de IA generativa | seção própria ("Generative AI statement") nos artigos de exemplo da revista | seção criada com rascunho no formato da revista, a confirmar pelos autores | pendente |
| Declaração de ética | exigida para estudos com animais ou humanos | seção criada: não se aplica | OK |
| Lista de autores e afiliações | obrigatória | não preenchida | pendente |
| Formato frente aos três artigos de exemplo da *Frontiers in Natural Products* (pasta `exemplos-papers`, 05/10/2026) | seções Conclusion, Generative AI statement e Supplementary material; resumo ≤ 350 palavras | seções criadas e resumo reescrito; Resultados e Discussão mantidos separados (os exemplos os fundem); lista de referências não reformatada (a produção da revista a reestiliza) | OK |
| Adequação ao escopo | seção *Informatics and Computational Methods* existe na revista | o título destaca inibidores naturais como moldes e padrões de calibração, mas o trabalho projeta peptídeos *de novo* e é só computacional; a revista pode exigir validação experimental | risco a verificar com o editor |

**Fonte e certeza dos limites.** Conferidos em 30/09/2026 nas páginas oficiais da Frontiers: extensão máxima de 12.000 palavras para *Original Research* na *Frontiers in Natural Products*; 5–8 palavras-chave; figuras a 300 dpi no tamanho final em TIFF, JPEG ou EPS; referências autor-ano com os seis primeiros autores; uso de IA generativa a ser reconhecido. **Não especificados nessas páginas:** limite de palavras do resumo (350 é a convenção da Frontiers, vista em outras revistas do grupo), limite de caracteres do título, número máximo de figuras/tabelas para *Original Research* e o tamanho do título curto. Confirme esses quatro pontos no sistema de submissão antes de enviar.

## Estado dos cálculos (06/10/2026, manhã)

| Etapa | Estado | Resultado até aqui |
|---|---|---|
| Painel de 8 espécies e subsítios | concluído | TM-score 0,946–0,957 nos 20 pares (Seção 3.1) |
| Calibração da escada de escores | concluída | Boltz-2 10/10; RMSD do ligante 9/10; MM-GBSA 4/10; PRODIGY 2/10; os dois últimos acompanham o tamanho da interface (Seção 3.2, Figura 2) |
| Geração e critério duro | concluídos | 22.066 sequências; 527 lineares e 543 cíclicas (Seção 3.3) |
| E1–E4 · Boltz-2, reescore, controles pareados, QC de pose, matriz 8 × 8 | concluídos | 48 candidatos finais; Δ positivo em 63/78 (L) e 60/79 (M), da ordem do ruído (Seção 3.4) |
| MD de 10 ns em pH 10,0 | concluída (48/48) | a ocupância de S1 acompanha a pose inicial (Seção 3.5, Figura 5) |
| Controles em MD (7 embaralhados; 8 de troca de âncora) | simulados e retirados do artigo (05/10) | a distância inicial explica o resultado; uma frase de divulgação em 3.5 |
| PRODIGY nas 48 poses | concluído | ΔG −12,2 a −7,1 kcal/mol; acompanha o comprimento (Seção 3.6, Figura 6) |
| MD de 10 ns em pH 8,2 (48) e execuções repetidas (16) | **em curso** (`md82-*`, `md82rest-*`, `noise-*`); 17 das 48 concluídas em 06/10, 17:15 (8 L e 9 M; as frentes terminam o 1º lote em horários diferentes) | 48 MDs: fim previsto entre a noite de 07/10 e a manhã de 08/10; repetidas: ≈ 09/10 (extrapolação do ritmo medido) |
| MM-GBSA e PRODIGY nas trajetórias (pH 8,2 e pH 10,0) e classificação final | **em curso** (`energy-queue`, `mmgbsa-md10`) | pendente (Seções 3.6 e 3.7) |
| Contrasseleção frente a proteases não alvo | não construída | sem ela, nenhuma seletividade é afirmada |

**Fila de cálculo:** o ritmo medido em 06/10 é de 1,3 a 2,7 h por MD (média ≈ 2,1 h) com as duas frentes juntas e a GPU compartilhada; a previsão do conjunto é extrapolação, não medida (a estimativa anterior, de 75 min por MD, vinha dos primeiros 14 min e estava otimista).

## Pendências antes da submissão

1. Resultados de pH 8,2, MM-GBSA e comparação com pH 10,0 (Seções 3.6 e 3.7, Figura 7); depois ajustar resumo, 4.1, 4.4 e 5.
2. Motivo do pH 8,2 (Seção 2.6) e lista de peptídeos recomendados.
3. Lista de autores, afiliações, contribuições, financiamento, conflito de interesses, declaração de IA generativa e DOI de arquivamento do código.
4. Revisar a auditoria metodológica e de código (`docs/AUDITORIA_2026-10-05.md`).
"""

full = panel + "\n" + src + "\n\n## Referências\n\n" + "\n\n".join(refs[k] for k in cited) + "\n"
(HERE / "manuscript_pt.md").write_text(full, encoding="utf-8")

# ---------- 5. pandoc
out = HERE / "Manuscrito_PT_leitura.docx"
alt = HERE / "Manuscrito_PT_leitura_novo.docx"
try:  # se o arquivo estiver aberto no Word, grava com sufixo em vez de falhar
    with open(out, "ab"):
        pass
except PermissionError:
    out = alt
    print("AVISO: Manuscrito_PT_leitura.docx esta aberto em outro programa; gravando em", out.name)
else:
    # o documento de leitura e' UM so': assim que o canonico volta a ser gravavel, a copia `_novo`
    # (e o arquivo de bloqueio que o Word deixa) sao removidos, para ninguem ler a versao errada.
    for extra in (alt, HERE / ("~$" + alt.name[2:])):
        if extra.exists():
            try:
                extra.unlink()
                print("removido:", extra.name)
            except OSError:
                print(f"AVISO: {extra.name} ainda esta aberto no Word; feche-o e rode de novo para apagar")
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

# Consolidação — 2026-11-01

Sessão de auditoria e correção do manuscrito Frontiers, mais versões em português
e material suplementar. Todo o trabalho é sobre documentos; nenhum cálculo novo
foi rodado.

## 1. Entrada

- `manuscript/Frontiers_ Eulálio 2026.odt` (12.502 palavras) — versão com
  **Introdução e Discussão reescritas manualmente** pelo usuário. Não estava
  versionada; foi commitada agora como base.
- `manuscript/Supplementary material - Eulálio frontiers.docx` — material
  suplementar montado manualmente pelo usuário (Tabelas S1–S2, Figuras S1–S8).

## 2. RAG

PDF novo acrescentado ao `eulalio-pos-doc` (servidor), collection
`tema1_peptideos_inibidores_tripsina`:

- `paulo2026rationally.pdf` = **Paulo et al. 2026, Pest Manag Sci, 10.1002/ps.71448**,
  "A rationally designed peptide targeting trypsin-like enzymes impairs feeding
  and redox homeostasis in *Anticarsia gemmatalis*". Eulálio é segundo autor.
  Artigo **distinto** do ps.70579 (`paulo2026peptidic.pdf`, já indexado).
- Indexado só esse arquivo (599 → 664 chunks, 65 novos). Não usei
  `index-one --force`: ele **não limpa a collection antes**, duplicaria os 599
  existentes, e `contextual_retrieval` está ligado (1 chamada de LLM por chunk).
- **Armadilha:** o Ollama da porta padrão (11434) está sem modelos.
  `nomic-embed-text` e `qwen3:14b` vivem na instância da **porta 11435**
  (`screen mb-ollama`). O `projects/eulalio-pos-doc.json` ainda aponta para
  11434 — `retrieve`/`index-one` falham com `model 'nomic-embed-text' not found`.
  Não alterei o config.
- O marcador `.done` não foi atualizado (continua com a contagem antiga).

## 3. Auditoria do manuscrito

Números conferidos **contra os JSONs reais**, não contra os docs. Confirmados:
calibração (Boltz-2 10/10, RMSD do ligante 9/10), as 48 ocupâncias e estatísticas
da §3.7 (Wilcoxon p = 0,16 / 0,88 / 0,63; ρ = 0,51 e 0,44), as réplicas, o 1,6%
de quase-ataque, as contagens de camadas e a composição do ranking.

Recalculei de forma independente a partir de `data-calibration-b05/` e
`data-e2-results/`: MM-GBSA 4/10 e ρ = −0,907 (n = 20 sistemas com contagem de
contatos; o valor documentado de −0,93 é com n = 22); PRODIGY 2/10 e ρ = −0,786.

### Defeitos encontrados

| # | Defeito | Situação |
|---|---|---|
| 1 | Resumo e Discussão afirmavam a calibração do MM-GBSA (4/10, ρ = −0,93) que **não existia mais** nos Métodos nem nos Resultados | corrigido |
| 2 | As **réplicas existem** (`md10b_*`, `md82b_*`, 8 sistemas × 2 pH) e são usadas na §3.8, mas os Métodos diziam "uma corrida por pH" | corrigido |
| 3 | **Figura 1 ausente** do documento (sem legenda, sem citação, imagem não inserida) | legenda e citação inseridas; **imagem ainda falta** |
| 4 | **Tabela 4 não existe** no .odt, embora a §3.8 a cite | conteúdo recuperado e conferido; **inserido só no PT** |
| 5 | §2.7 definia a ocupância como "4–6 Å"; o código usa `< 5 Å` | corrigido |
| 6 | `(PepPCBench, 2025)` sem autor e **fora da lista de referências** | → `(Zhai et al., 2025)`, 10.1021/acs.jcim.5c01084 |
| 7 | Kᵢ 0,10–1,41 mM citava Severiche-Castro 2023 (dioscorina de cará, **sem nenhum Kᵢ**) | → de Almeida Barros 2021/2022 + Schultz 2026; entrada órfã removida |
| 8 | **6 referências citadas nos Métodos e ausentes da lista** | acrescentadas e verificadas no Crossref |
| 9 | GGKPGEP é camada B e ficou fora do ranking da §3.6, mas entra na lista curta sem explicação | explicitado |
| 10 | GQNDS existe nas duas frentes; a §3.6 não distinguia | rotulado |
| 11 | "none of the differences exceeded the variability..." sem dado | trocado pela estatística real (3 de 16 pares > 0,5) |
| 12 | §3.7 abria alegando "more promising pest control agent" | suavizado |
| 13 | Frase sem sujeito na Discussão (ciclização); typo `QAPDFPTGPNQS4` | corrigidos |

O item 8 só apareceu num **cruzamento programático citação × lista de
referências** — a leitura não pegou. Faltavam UniProt Consortium 2025,
Huang & MacKerell 2013, Jorgensen 1983, Olsson 2011, Valdés-Tresanco 2021 e
Vangone & Bonvin 2015. Depois da correção: **zero órfãs, zero faltantes**.

### Falso alarme registrado

Na primeira leitura suspeitei que as réplicas da §3.8 (GGHSE 0,00/0,88;
GQNDS 0,73) fossem valores inventados, porque os Métodos diziam que havia uma
corrida por pH. **Os dois valores são reais** (`md82b_M` = 0,884, `md82b_L` =
0,725). O defeito era dos Métodos, não dos números.

## 4. Entregas

| Arquivo | O que é |
|---|---|
| `manuscript/Frontiers_ Eulálio 2026_corrigido.odt` | EN corrigido, 26 edições, 49 trechos em vermelho |
| `manuscript/Manuscrito_PT_corrigido.docx` | tradução integral do EN corrigido (14.164 palavras), mesmas marcas em vermelho, **já com a Tabela 4** |
| `manuscript/Supplementary material - Eulálio frontiers_corrigido.docx` | suplementar EN + Figura S9, tabelas traduzidas do PT, decimais com ponto, terminologia harmonizada |
| `manuscript/Material suplementar - Eulálio frontiers_PT.docx` | suplementar em português |

Vermelho = `#FF0000`. No .odt são os estilos `TRED` e `TREDI`.

A numeração suplementar S1–S8 que o usuário montou **já casava** com o
manuscrito; a S9 (geometria da ligação cindível) foi acrescentada porque a §3.8
corrigida passou a citá-la. Mapeamento texto → arquivo em `figures/final/`:
S1→S1, S2→S2, S3→S3, **S4→FigureS5_pose_quality**, S5→S6, S6→S7, S7→S8,
S8→FigureS10, S9→FigureS11. Ficaram sem citação `FigureS4_E2_rescoring` e
`FigureS9_motif_rules`.

## 5. Pendências

1. **Inserir a Tabela 4 no .odt em inglês.** Não foi feito porque o usuário
   estava com o arquivo aberto (lock `~$ontiers_...`); gravar agora seria
   sobrescrito no próximo "salvar" dele.
2. **Inserir a imagem da Figura 1** (`figures/final/Figure1_pipeline.png`) no EN
   e no PT — há marcador vermelho no lugar.
3. **Contagem de palavras**: EN foi de 12.502 → 13.918. A memória registra
   conferir o limite de ~12.000 da Frontiers.
4. **Legenda da Tabela S2 (EN)** ainda termina com procedência interna
   ("Data: data-lepidoptera-panel/...; script: make_table_s2.py"); foi **omitida
   no PT**. Os dois estão divergentes nesse ponto.
5. **Seção 4.4 Limitações** (dez itens) existe em `manuscript_src.md` e **não**
   no .odt. Oferecida ao usuário, sem resposta.
6. `manuscript/Supplementary_Figures_EN.docx` é um arquivo que montei antes de
   saber do suplementar manual. **Superado**, não commitado.
7. `Manuscrito_PT_leitura.docx` segue modificado e não commitado — alteração
   manual anterior do usuário, não mexi.

## 6. Linhagens do manuscrito (cuidado)

São duas, e divergem:

- **Markdown**: `manuscript_src.md` (EN, 12.063 p.) ↔ `manuscript_pt.md`
  (PT, 16.515 p.). Têm a §4.4 Limitações e usam a numeração suplementar S1–S11.
- **ODT/DOCX**: `Frontiers_ Eulálio 2026.odt` — Introdução e Discussão
  reescritas à mão, suplementares renumeradas S1–S8, sem Limitações.
  `Manuscrito_PT_revisado_figsEN.docx` (6.457 p.) é uma cópia de leitura bem
  mais curta, **não** o par em português do .odt.

O `Manuscrito_PT_corrigido.docx` entregue agora é o par em português da linhagem
ODT, não da linhagem markdown.

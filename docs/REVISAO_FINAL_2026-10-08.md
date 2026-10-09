# Revisão final do manuscrito — 08/10/2026

Escopo pedido: acertar o layout das figuras, conferir se a informação é real, se todas as referências existem, avaliar a qualidade científica, as discussões e os principais achados (literatura, RAG, estado da arte). Dica do usuário: metodologia sucinta e direta; o cerne são Resultados e Discussão.

## 1. Referências (84 na lista)

- **Existência:** as 82 referências originais foram resolvidas uma a uma no Crossref pelo DOI; 82/82 existem, e título e primeiro autor batem com o texto. Nenhuma citada sem estar na lista, nenhuma na lista sem ser citada (`render.py`).
- **Anos corrigidos para o ano de impressão:** Yang et al. 2012 → 2013 (Insect Sci 20(4)), Zhan et al. 2010 → 2011 (Arch Insect Biochem Physiol 76(3)). Patarroyo-Vargas 2017 mantido (PubMed: Protein Pept Lett 2017;24(11)).
- **Ambiguidade autor-ano resolvida:** Meriño-Cabrera et al. 2020a (ApTI) / 2020b (peptídeos miméticos); de Almeida Barros et al. 2022a (BPTI × SKTI) / 2022b (tripeptídeos). Antes, duas referências distintas apareciam como "2020" e "2022" no texto.
- **Afirmações conferidas contra os resumos (Europe PMC/Crossref):** GORE1/GORE2 Ki 0,49 e 0,10 mM; tripeptídeos Pin-II em pH alcalino; peptídeos bicíclicos 10× mais potentes; extratos de intestino de *H. virescens* pH 9,56–10,0 (a frase agora diz que é *H. virescens*); SBBI × SKTI em *A. gemmatalis* (Ki 1,4 nM × 0,25 nM); ApTI inibição tight-binding não competitiva; Kelly 2005 (cerca de seis ordens de grandeza); Wei 2019 (mobilidade × hidrólise); Xu 2025 (amostragem do MM/PBSA); Wan 2026 (Boltz-2: correlações fracas a moderadas com ESMACS) — a introdução dizia "a confiança não é afinidade" citando Wan, que avaliou a saída de **afinidade**; frase corrigida; Li 2026 (111 complexos cíclicos); Severiche-Castro 2026 (PEP-11, 100 ns em triplicata); Rettie 2025 (RFpeptides).
- **Referências novas e verificadas (DOI, Crossref/Europe PMC):** Mariano et al. 2026 (peptídeos da região pró do tripsinogênio contra *A. gemmatalis*; Ki 0,78–1,80 mM) e Júnior et al. 2026 (resposta transcricional de *A. gemmatalis* a SKTI e GORE-2). Ambas do mesmo grupo e muito próximas do tema.
- **Não verificado:** o motivo do pH 8,2 (Schultz et al. 2026, Tris-HCl pH 8,2) — o resumo não traz a condição do ensaio; a conferência exige o texto completo.
- **RAG `eulalio-pos-doc-rag`:** não consultado nesta sessão (fica no servidor, exige a VPN). A busca de literatura foi feita por Crossref, Europe PMC e OpenAlex.

## 2. Informação real (números conferidos)

- Tabela 1: as 11 entradas UniProt existem, com o organismo e o comprimento da tabela; os 10 modelos de pragas/referência estão anotados como "Chymotrypsin" no UniProt (o texto já avisa); P35045 (tripsina A) × P35046 (tripsina B) de *M. sexta*: a identidade de 96,1% é entre A e B, coerente com a legenda.
- Comparação de pH: todos os valores de 3.7/Fig. 7 conferem com `data-e2-results/compare_ph.{md,json}` (P = 0,158 e 0,875; ρ = 0,51, 0,44, 0,50, 0,60; 2 ambos / 3 só pH 10 / 4 só pH 8,2 / 39 nenhum).
- **Lacuna achada e corrigida:** "Δ positivo em 63 de 78 lineares e 60 de 79 cíclicos" não explicava por que 78/79 e não 80. Os arquivos mostram que 2 candidatos lineares e 1 cíclico são poli-glicina (GGGGGGG, GGGGGG, G14) e não têm controle embaralhado. Agora está no texto, junto com a observação de que poli-glicina entrou entre os dez melhores pela confiança da primeira predição.
- As Figs. 2, 3, 4, 6, 7 e S10 são geradas dos JSON/CSV do repositório e, regeneradas, reproduzem os números citados no texto (527/543, ρ = 0,57 e 0,50, 10/10, 4/10, 2/10, P = 0,16 e 0,88). As Tabelas 2–4 não foram regeneradas aqui; foram conferidas por amostragem contra as figuras (calibração 4/10 e 2/10, candidatos de 3.8).

## 3. Figuras: layout e adequação

Medidas da *Frontiers* mantidas em todas (180 mm, 300 dpi no tamanho final, texto ≥ 8 pt, TIF/PNG/PDF RGB; `frontiers_style.py`). Paleta Okabe–Ito (segura para daltonismo; Wong 2011).

Correções de layout:
| Figura | Problema | Correção |
|---|---|---|
| 3 | legenda sobre as barras; rótulos colados ("4141") | legenda no canto, rótulos verticais |
| 5 | legenda de A sobre as curvas; C sem legenda de ○/× | legenda das curvas no topo da figura; legenda de C com ○ passa / × não passa |
| 6 | cabeçalhos "PRODIGY pose/MD" colados; rótulos da painel A sobre pontos | cabeçalhos inclinados a 35°; rótulos com linhas de chamada |
| 7 | rótulos de A e B sobrepostos e abaixo do eixo; linhas lineares em cinza (legenda dizia azul) | rótulos espaçados com linhas de chamada; linear em azul |
| S2 | fontes de 6,5–7 pt (abaixo do piso) e rótulos colados | refeita (`make_figure_s2.py`) a 8 pt |
| S3, S8, S9 | marcas de comprimento e nomes de espécie colados; legenda sobre os nomes | rotação dos rótulos; legenda reposicionada |
| S4 | texto das estatísticas sobre os pontos | estatísticas dentro da legenda |
| S7 | nomes cortados na borda e sobrepostos ao painel vizinho | painéis empilhados verticalmente |
| S10 | rótulos sobre os pontos; legenda sobre rótulo | linhas de chamada; legenda no painel C |

Adequação à interpretação (Rougier et al. 2014; Weissgerber et al. 2015; Streit e Gehlenborg 2014; Wong 2011 — todos com DOI verificado no Crossref):
- **Boas:** Fig. 2 (gráfico de halteres: dados pareados, a recomendação para pares); Fig. 7A–B (linhas pareadas por candidato, em vez de barras com erro); Fig. 7C–E e S10 (dispersão com ρ e linha de identidade); Fig. 6B (matriz de postos com o número impresso e cor relativa ao tamanho do conjunto); Fig. 4 (dispersão de reprodutibilidade com a identidade).
- **Aceitáveis, com ressalva:** Fig. 5D (barras agrupadas de 48 candidatos × 3 métricas, densas; uma matriz de pontos ou mapa de calor seria mais legível, mas mudaria uma figura já citada em 3.5 e na legenda); Fig. 8 (poses de quadro único: ilustram a geometria inicial, não evidência; a legenda já diz que são poses iniciais do Boltz-2); Fig. 3 e S9 (contagens por barras; o essencial está na Tabela 3).
- **Tabela 4 (candidatos) e Fig. S7:** carregam a mensagem "sobreviveu aos filtros, não deve inibir"; cor por camada A/B/C.
- Versão PT: Figs. 6, 7, 8, S2, S9 e S10 continuam em inglês no `Manuscrito_PT_leitura.docx` (só 3, 4, 5, S1, S3–S8 têm versão PT). É leitura interna; o texto de submissão é o inglês.

## 4. Qualidade científica e achados

**O que o trabalho sustenta:** (i) a escada de escores foi calibrada com decoys: o Boltz-2 separa inibidor de decoy dentro do par (10/10), mas MM-GBSA (4/10) e PRODIGY (2/10) acompanham o tamanho da interface; (ii) o critério de não clivabilidade seleciona peptídeos curtos e ricos em glicina (527 L / 543 M); (iii) a ocupância de S1 em 10 ns segue a pose inicial; (iv) pH 8,2 e pH 10,0 não diferem e a diferença está dentro do ruído entre execuções.

**Pontos fracos reais (já assumidos no texto, convém manter à vista):**
1. Só computacional e sem contrasseleção: nenhuma seletividade nem atividade; para uma revista de produtos naturais pode pesar na triagem editorial.
2. Nenhum candidato tem evidência de ligação: as MDs são de 10 ns, uma execução; só NGGRPDAP e GGKPGEP repetem S1 e já começavam em S1.
3. A confiança do Boltz-2 premia sequências de baixa complexidade (poli-glicina entre as dez melhores; controles embaralhados de sequências ricas em Gly são quase idênticos ao candidato).
4. O critério "não clivável" é de motivo, sem medida de proteólise; a geometria de ataque da Ser195 não tem linha de base com substrato conhecido.
5. As referências de *potência* comparáveis (GORE1/2, Pin-II, região pró) são milimolares; o trabalho não oferece evidência de superar isso.

**Discussão:** acrescentado o parágrafo "Relação com trabalhos anteriores" (4.4): mesma classe de tamanho que GORE1/2, Pin-II e região pró (Ki 0,78–1,80 mM); o que o trabalho acrescenta é o critério explícito de não clivabilidade e a escada calibrada, não afinidade maior; o GORE2 é o controle positivo natural para o ensaio.

**Metodologia:** 2.6, 2.7 e 2.8 enxugadas (resultados movidos para Resultados/Discussão; parâmetros mantidos). Corpo em inglês ≈ 10,8 mil palavras no `render.py` (limite 12.000, margem confortável); resumo com 348 palavras (≤ 350).

## 5. Pendências que dependem dos autores

- Motivo do pH 8,2 (Seção 2.6): o candidato é Tris-HCl pH 8,2 (Schultz et al. 2026); confirmar no texto completo.
- Lista final de peptídeos recomendados e cortes: o manuscrito apresenta quatro selecionados (3.8, Tabela 4); a recomendação final é decisão dos autores.
- Autores, afiliações, contribuições, financiamento, conflito de interesses, declaração de IA, DOI de arquivamento do código.
- Opcional: linha de base da geometria de ataque com SFTI-1; ensaio de Ki com GORE2 como controle positivo.

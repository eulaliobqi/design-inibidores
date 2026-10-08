# Revisão geral do projeto — 07/10/2026

Revisão pedida pelo usuário: reprodutibilidade do código, organização, coerência entre título e texto, figuras nas métricas da revista, e correção de falhas e informações erradas.

## 1. O que foi conferido e está correto

| Item | Verificação | Resultado |
|---|---|---|
| Referências | os 77 DOIs consultados na API do Crossref; ano e título comparados com a lista formatada | **77/77 resolvem**, 0 divergências de ano ou título |
| Números do texto | `python -m scripts.audit_numbers` | **187 verificações, 0 falhas** |
| Tabela 3 e Seção 3.3 | recontagem contra `data-b23-scoring/results/filter_composition.json` | somas por espécie, 1.829/4.987/15.250, média de comprimento 7,05 e 15,74, fração K/R 4,3% — todas batem |
| Figuras | medidas nos TIF: largura, altura, dpi, modo de cor | **18/18** em 179,9 mm (duas colunas), 300 dpi, RGB, altura ≤ 185 mm (limite de 240) |
| Limites da revista | diretrizes oficiais da Frontiers e a página de tipos de artigo de *Frontiers in Natural Products* | corpo 9.869 palavras (limite 12.000), resumo 322 (limite 350), 8 palavras-chave (limite 8), 8 figuras + 4 tabelas no corpo |
| Testes | `python -m pytest tests -q` | 38 passaram |
| Citações | `render.py` | 77 citadas, nenhuma referência órfã, nenhuma chave `{...}` sobrando |

## 2. Falhas encontradas e corrigidas

### 2.1 Título afirmava o que o artigo nega (corrigido)
O título dizia **"De Novo Peptide Inhibitors"**, mas o resumo, a Seção 3.8 e a Conclusão declaram que nenhum peptídeo tem atividade ou seletividade demonstrada ("All results are computational; selectivity and activity were not tested"). O artigo entrega **candidatos que sobreviveram aos filtros**, não inibidores.

- EN: `From Natural Protease Inhibitors to De Novo **Candidate Peptides** Targeting Digestive Trypsins of Lepidopteran Pests`
- Título curto: `De novo candidate peptides against pest trypsins`
- PT: `De inibidores naturais de proteases a **peptídeos candidatos** de novo dirigidos às tripsinas digestivas de lepidópteros-praga`
- A frase de objetivo na Introdução (1, último parágrafo) foi ajustada no mesmo sentido, em EN e PT.

É a mudança de uma palavra; reverter é trivial se os autores preferirem o título anterior.

### 2.2 Figura 1 era um quadro de andamento do projeto, não uma figura de artigo (corrigido)
A versão anterior pintava as caixas de verde, amarelo e cinza com a legenda "green: done; yellow: running; grey: pending" — bookkeeping interno que anuncia ao revisor que o trabalho está incompleto. Refeita como **desenho do estudo**: caixas neutras, frentes L e M no azul e verde-azulado usados nas outras figuras, quatro linhas sem cruzamento de setas, e a ressalva de que não houve ensaio nem contrasseleção. Legenda reescrita em EN e PT.

### 2.3 Figura 6B comparava postos de conjuntos de tamanhos diferentes na mesma escala de cor (corrigido)
As duas frentes são classificadas em conjuntos distintos (23 lineares, 10 macrocíclicos), mas a cor usava uma escala única de 1 ao máximo. Um posto 10 é o **pior** da frente M e **intermediário** na frente L, e recebia a mesma cor: o bloco M parecia uniformemente melhor que o L por artefato de tamanho do conjunto. Agora a cor é o posto **relativo ao conjunto da própria frente** (0 = melhor) e o número impresso continua o posto bruto. De quebra, o texto das células passou a preto sobre fundo claro (antes era branco sobre amarelo). Legenda reescrita em EN e PT.

### 2.4 Faixa de pLDDT atribuída às espécies-praga estava errada (corrigido)
A Seção 3.1 dizia "Identity ... among the pests, and mean pLDDT from 88.9 to 92.2". Os extremos 88,9 e 92,2 são de *B. mori* e *M. sexta* — nenhuma das duas é alvo. Entre as oito pragas a faixa é **89,7–91,0** (`data-lepidoptera-panel/panel_v2.json`). Corrigido em EN e PT para separar as duas faixas.

### 2.5 Contagem de ocupância aparentemente contraditória entre 3.5 e 3.7 (corrigido)
A 3.5 diz "5 de 48" com ocupância ≥ 0,70 em pH 10,0; a 3.7 dizia "quatro em pH 10,0". Não é contradição — a 3.7 fala só dos 37 pares já disponíveis, e o quinto (GGGGH) ainda não tem execução de pH 8,2 — mas o texto não dizia isso. Explicitado em EN e PT.

### 2.6 README documentava um pipeline que não é o do artigo (corrigido)
Este é o defeito mais sério de reprodutibilidade, porque o *Data availability statement* aponta para este repositório. O `README.md` descrevia o desenho **inicial**: agentes Rosetta e AutoDock Vina, **P1 fixo em Arg/Lys** (o critério duro do artigo proíbe Arg e Lys), quatro PDBs de HADDOCK como entrada, e a frase "o pipeline nunca trava por ferramenta ausente" porque os agentes caem em heurística — exatamente o que a regra do projeto proíbe relatar como dado real. Quem clonasse o repositório para conferir o artigo encontraria instruções de outro trabalho.

O `README.md` foi reescrito para o pipeline do manuscrito: estado por etapa, comandos de reprodução (auditoria, figuras, montagem EN e PT, testes), tabela "item do artigo → dados → script", regras de método e estrutura real do repositório. As seções antigas foram para `docs/LEGADO_pipeline_multiagente.md`, com aviso no topo.

### 2.7 A renumeração das figuras não era reproduzível (corrigido)
Desde a reescrita de 05/10 os arquivos de `manuscript/figures/final/` eram cópias **manuais** das saídas dos geradores sob outros nomes (`Figure11_MD_screen_10ns` → `Figure5_MD_screen`, e mais onze). Nenhum script registrava o mapa: rodar os geradores devolvia a numeração antiga e não havia como casar figura com legenda. Criado `manuscript/figures/collect_final.py`, que contém o mapa das doze renomeações e reconstrói `final/` (conferido: 35 arquivos). Criado também `manuscript/figures/README.md` dizendo qual diretório é o oficial — havia três arquivos distintos chamados `Figure7_*` no diretório de trabalho, risco real de anexar a figura errada.

## 3. Pendências que continuam (não são falhas, são trabalho em curso)

1. **Resumo, 4.1, 4.2, 4.4 e 5 ainda descrevem só o pH 10,0.** A 3.7 existe e está marcada como provisória, mas o resumo não menciona a comparação de pH. Deve ser ajustado quando as 48 e o piso de ruído terminarem — reescrever agora com 37 pares seria refazer amanhã.
2. **3.6 e 3.7** seguem `[[PENDING]]`/`[[PROVISIONAL]]` até as 48 MDs, a fila de energia e o `noise-L/M`.
3. **Decisões dos autores:** motivo do pH 8,2 (o RAG do projeto indica que os ensaios cinéticos de Schultz 2026 usam Tris-HCl 0,1 M, CaCl2 20 mM, pH 8,2 — registrado no manuscrito como possibilidade a confirmar), lista final de peptídeos, MD longa, autoria, financiamento, conflito de interesse, declaração de IA generativa e DOI de arquivamento.
4. **Visibilidade do repositório.** O artigo cita `https://github.com/eulaliobqi/design-inibidores` como fonte dos dados; conferir se está público antes da submissão e arquivar uma versão (Zenodo) para ter DOI.
5. **Nota de redação 3** do manuscrito pede decisão: manter ou apagar o parágrafo que revela os controles em MD feitos e retirados.

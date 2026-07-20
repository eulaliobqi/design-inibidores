# Design — Figuras, Artigo Word e Apresentação (2026-07-20)

## Contexto

Após fechar as 4 frentes de análise (persistência S1, S2'/S3', fingerprint, expansão
taxonômica — spec `2026-07-19-priorizacao-eficacia-persistencia-fingerprint-design.md`) e as
confirmações pós-sessão (tríades, n=3 completo), o usuário pediu 3 entregáveis para consolidar o
trabalho até aqui:

1. **Figuras** — visualização dos resultados reais desta sessão
2. **Artigo completo em Word** — introdução, metodologia, resultados/discussão, conclusão,
   referências, a partir de `artigo_metodologia.md`/`artigo_resultados.md`/`references.md`
3. **Apresentação nova** — design moderno, via **API do Canva** (decisão do usuário, substitui
   qualquer abordagem PptxGenJS/python-pptx cogitada antes), figuras de internet/IA para
   ilustração, fluxogramas

São 3 subsistemas independentes. Esta spec cobre **apenas o primeiro (Figuras)** — os outros dois
recebem suas próprias specs em sequência (Figuras → Word → Apresentação, ordem aprovada pelo
usuário), já que o Word e a Apresentação vão reusar as figuras geradas aqui.

## Escopo desta spec: Figuras

### Fonte de dado

Direto dos JSONs reais no servidor — nunca dos números já formatados no artigo Markdown (risco de
erro de transcrição). Fontes:
- `outputs/md_replicates/replicates_summary.json` (réplicas MD n=3)
- `outputs/persistence_deep/persistence_summary.json` (ocupância S1, já com o fix de
  `REP1_DIR_OVERRIDE` e a MD real de `SARESIKKAYKTFLERYKKL` aplicados — n=3 completo para os 13)
- `outputs/cross_species_docking/all_cross_species_results.json` (matriz 13×11)
- Os mesmos 3 JSONs da Tabela 9q (fingerprint): PLIP de tríade (`outputs/plip_deep/`), persistência
  (acima), S2'/S3' (`outputs/s2s3_deep/`)

Cada script de figura busca o dado real na hora de gerar (via SSH ou cópia local do JSON,
decisão de implementação) — nunca copia valor já arredondado do Markdown.

### Ferramenta e paleta

Python + matplotlib (Opção A aprovada — sem camada de screenshot de HTML, já que o destino é
documento estático). Paleta e princípios da skill `dataviz` deste ambiente (`references/palette.md`
carregado nesta sessão), adaptados para saída estática/impressão (modo claro apenas, já que Word e
slides impressos/apresentados não alternam tema):

- **Paleta categórica** (ordem fixa, nunca ciclada): azul `#2a78d6`, verde `#008300`, magenta
  `#e87ba4`, amarelo `#eda100`, aqua `#1baf7a`, laranja `#eb6834`, violeta `#4a3aa7`, vermelho
  `#e34948`
- **Paleta de status** (reservada, nunca reusada como série): bom `#0ca30c`, atenção `#fab219`,
  sério `#ec835a`, crítico `#d03b3b` — usada para as classificações reais (estável reprodutível /
  marginal / alta variância), substituindo o semáforo ad-hoc das figuras antigas
  (`fase5_figs/figD_*.png`)
- **Sequencial** (heatmap/ocupância): rampa azul 100→700 (`references/palette.md`)
- **Tipografia**: sans-serif do sistema, sem serifada
- **Grades/eixos**: recessivos (cinza claro `#e1e0d9`), nunca dominantes
- **Sem eixo duplo** em nenhuma figura

### As 4 figuras

**Fig. 1 — Réplicas MD n=3.** Barras horizontais, RMSD médio ± DP (n=3) por candidato, ordenado por
RMSD ascendente. Cor de status por classificação real (ESTÁVEL REPRODUTÍVEL / marginal reprodutível
/ ALTA VARIÂNCIA, definição já usada na Tabela 9n — DP<0,05 / DP<0,10 / DP≥0,15).
`RLREELKKAEEWLEKRRKEE` e `VRTRR` (recorde de estabilidade refutado) marcados com anotação direta no
gráfico.

**Fig. 2 — Ocupância do bolso S1.** Barras agrupadas por candidato, 3 séries lado a lado (4Å/5Å/6Å),
rampa sequencial azul (clara→escura = corte mais largo). `VRRPR` anotado diretamente (achado
central: ocupância caindo 67,6%→32,9%→0,15% entre réplicas).

**Fig. 3 — Matriz cross-species.** Heatmap completo 13 candidatos × 11 espécies (143 células),
rampa sequencial azul (clara=afinidade fraca, escura=forte — Vina mais negativo = mais escuro).
Candidatos ordenados por média geral (Vina médio ascendente).

**Fig. 4 — Fingerprint (5 candidatos-chave).** Tabela visual, não heatmap numérico — colunas: tríade
catalítica (✓/✗ por resíduo His/Asp/Ser), ocupância S1 6Å (barra pequena inline), RMSD local do
bolso (barra pequena inline), contato S2'/S3' (barra pequena inline, marcada visualmente como
sinal de baixa confiabilidade — ex. opacidade reduzida ou hachura, não uma barra "normal" igual às
outras 3 colunas, para não implicar peso igual a um sinal já documentado como ruidoso).

### Saída

`outputs/figuras_artigo/fig1_replicas_md.png` ... `fig4_fingerprint.png` — 300 dpi, fundo branco,
legendas em português idênticas ao texto já publicado no artigo (`artigo_resultados.md`).

### Verificação

- Cada figura é lida (Read da imagem) antes de considerar pronta — checagem visual de
  sobreposição de rótulo, geometria, overflow (checklist da skill `dataviz`, passo 7).
- Os valores usados são impressos no console durante a geração e conferidos manualmente contra os
  números já publicados nas Tabelas 9n/9o/9r/9q do artigo — qualquer divergência é bug a investigar
  antes de aceitar a figura, nunca ajustar o número pra bater (dado sempre vem do JSON real).

### Fora de escopo desta spec

- Artigo Word completo (spec própria, próxima)
- Apresentação/Canva (spec própria, depois do Word)
- Legenda abaixo da figura nos slides — anotado como requisito de design para a spec da
  Apresentação, não se aplica à geração do PNG em si (a legenda vai na montagem do slide, não
  embutida na imagem)
- Regeneração de figuras já existentes de fases anteriores (`outputs/visualizations/`,
  `outputs/fase5_figs/`) — ficam como estão, não fazem parte deste pedido

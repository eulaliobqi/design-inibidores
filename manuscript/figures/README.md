# Figuras do manuscrito

**`final/` é o diretório oficial**: os arquivos ali têm a numeração citada no texto (Figuras 1–8, S1–S10) e são os que vão para a submissão. Todos saem em 180 mm de largura, 300 dpi, RGB, nos formatos TIF (exigido), PNG e PDF.

Os arquivos soltos neste diretório (`Figure9_E2_rescoring`, `Figure11_MD_screen_10ns`, `Figure12_final_candidates`, …) são as **saídas cruas dos geradores, com a numeração anterior à reescrita de 05/10/2026**. Eles continuam aqui porque `collect_final.py` os usa como origem — não são candidatos à submissão. Há três arquivos chamados `Figure7_*` neste diretório, de versões diferentes do artigo; sempre confira o nome em `final/` antes de anexar uma figura a qualquer coisa.

## Como refazer `final/`

```bash
cd manuscript
python figures/make_figures_final.py figures/final   # Figuras 1, 2, 6, 8
python figures/make_figures_ph.py    figures/final   # Figuras 7, S10
python figures/collect_final.py                      # renomeia as demais para final/
```

`collect_final.py --run` executa os dois primeiros passos sozinho. O mapa "nome do gerador → número final" vive dentro dele e é a única definição executável da renumeração.

## Especificação da revista

`frontiers_style.py` codifica as exigências da *Frontiers* conferidas nas diretrizes oficiais: largura de 85 mm (uma coluna) ou 180 mm (duas), 300 dpi **no tamanho final**, texto nunca abaixo de 8 pt, altura máxima de uma página, TIF/JPEG/EPS em RGB. `apply_style()` recusa fonte menor que 8 pt em vez de encolher a figura em silêncio, e `save_journal()` devolve a largura e a altura medidas para conferência.

A paleta é Okabe–Ito (segura para daltonismo) e é a mesma em todos os geradores: azul `#0072B2` = frente L (linear), verde-azulado `#2a9d8f` = frente M (macrociclo).

## Revisão de 08/10/2026

- Gerador novo: `make_figure_s2.py` (Figura S2, redesenhada a 8 pt). `make_figures.py` (antigo) não é mais origem da S2.
- Boas práticas conferidas na literatura (DOI verificados no Crossref): Rougier et al. 2014, *Ten simple rules for better figures* (10.1371/journal.pcbi.1003833); Weissgerber et al. 2015, *Beyond bar and line graphs* (10.1371/journal.pbio.1002128); Streit e Gehlenborg 2014, *Bar charts and box plots* (10.1038/nmeth.2807); Wong 2011, *Color blindness* (10.1038/nmeth.1618). Dados pareados em halteres/linhas, dispersão com identidade, paleta Okabe–Ito.
- Avaliação figura a figura e correções: `docs/REVISAO_FINAL_2026-10-08.md`, seção 3.

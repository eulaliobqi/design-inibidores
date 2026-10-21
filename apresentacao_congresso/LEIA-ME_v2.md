# Deck do SIA (v2) — como esta montado e o que conferir

**Arquivo final:** `Apresentacao_congresso_v2.pptx` (19 slides) + `Apresentacao_congresso_v2.pdf` (plano B; nao toca video).
Levar no pendrive: o `.pptx`, o `.pdf` e a pasta `imagens/` (os `.mp4` estao embutidos; os `.gif` equivalentes ficam so localmente).

**Ordem:** 1 capa · 2 ODS 2 · 3 perda agricola · 4 manejo · 5 inibidores naturais · 6 ancoragem · 7 grupo (GORE3) · 8 objetivos · 9 fluxograma · 10 animacao (RFdiffusion→ProteinMPNN→Boltz-2→MD) · 11 resultados por ferramenta · 12 calibracao · 13 filtrados · 14 dinamica · 15 melhores candidatos · 16 filme das 4 MDs · 17 conclusao · 18 5 referencias · 19 financiamento e agradecimentos.

**Regeneracao** (da raiz do projeto): `make_slide_figures.py` (figuras da v1) → `make_figures_v2.py <pasta dos renders>` → `make_fig_grupo.py` → `make_gif.py` / `make_anim.py` → `build_pptx_v2.py` (monta do zero). O arquivo editado a mao pelo autor NAO e regenerado: as rodadas seguintes foram aplicadas em cima dele por `edit_sia.py`, `edit_sia2.py`, `edit_slide7.py` (cada um guarda um backup `_antes_*.pptx`). Renders PyMOL e extracao das MDs rodam no servidor (`render_servidor/`, env conda `viz`).
Video com autoplay+loop: configurado via COM do PowerPoint (efeito "com anterior", atraso 0,3 s) nos slides 10 e 16.

**Regras de conteudo:** so dado real, com referencia no rodape; rodape/notas trazem as fontes (22 refs nas notas do slide 18; 5 no slide).
Numeros de perda: Savary 2019 (21,4%; 11,0–32,4%) e Oliveira 2014 (US$ 17,7 bi/ano; todas as culturas). NAO usar "28 kg/ha por 1% de desfolha" nem "ate 30% Embrapa" (sem fonte primaria).

**Pendencias de conferencia (autor):**
1. Slide 7: referencia/especie/concentracao das figuras do GORE3 (rodape cita so a familia GORE).
2. Conab 180,4 Mt e Ongaratto 2021 (slide 3-4) vieram do deck anterior, nao reverificados.
3. Resumo submetido ao SIA descreve o pipeline antigo (Vina/Rosetta, 4 modelos, 0/21-23 SI); o deck mostra a versao atual (8 especies, Boltz-2, 527/543, 96 MDs) — avisar na fala.
4. Logos de FAPEMIG/CAPES/CNPq foram obtidos do site da FAPEMIG e do manual de identidade do CNPq; trocar pelos arquivos oficiais se houver.
5. Testar o autoplay do video no computador da sala.

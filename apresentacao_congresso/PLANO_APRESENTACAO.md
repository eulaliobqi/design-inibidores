# Plano da apresentação — congresso, 10 minutos

**Título:** Desenho Racional de Inibidores Peptídicos de Tripsinas contra Lepidoptera por Inteligência Artificial Generativa

**Fonte dos dados:** `manuscript/manuscript_pt_src.md` (versão de 12/10/2026, commits `58c0fed` / `de3fe02`) e `manuscript/figures/final/`. Nenhum número deste plano foi digitado de memória: todos saem do manuscrito ou dos JSON em `data-figuras-base/` e `data-e2-results/`.

**Público:** misto — bioquímica, bioinformática, biologia e ouvintes leigos. Cada ferramenta (RFdiffusion, ProteinMPNN, Boltz-2, MM-GBSA) é explicada em uma linha, em linguagem funcional, antes de aparecer como nome próprio.

**Mensagem que fica (take-home):** *existe uma plataforma que vai da enzima-alvo ao peptídeo candidato ordenado, roda para oito espécies ao mesmo tempo e diz, em cada etapa, o que o número daquela etapa sustenta.* Os candidatos e a calibração entram como validação da plataforma.

---

## 1. Por que storytelling, e qual estrutura

Base verificada (DOI conferido no Crossref):

| Princípio adotado | Fonte |
|---|---|
| Narrativa aumenta compreensão e engajamento de público não especialista | Dahlstrom 2014, *PNAS* — [10.1073/pnas.1320645111](https://doi.org/10.1073/pnas.1320645111) |
| Artigos com estrutura mais narrativa são mais citados | Hillier, Kelly & Klinger 2016, *PLOS ONE* — [10.1371/journal.pone.0167983](https://doi.org/10.1371/journal.pone.0167983) |
| Apresentação curta = **uma** história focada; não cabe o artigo inteiro | Lortie 2017, *PLOS Comp Biol* — [10.1371/journal.pcbi.1005373](https://doi.org/10.1371/journal.pcbi.1005373) |
| Saber o público e o que ele deve lembrar antes de desenhar o slide | Bourne 2007, *PLOS Comp Biol* — [10.1371/journal.pcbi.0030077](https://doi.org/10.1371/journal.pcbi.0030077) |
| Contexto → lacuna → resultado → conclusão (C-C-C) como esqueleto | Mensh & Kording 2017, *PLOS Comp Biol* — [10.1371/journal.pcbi.1005619](https://doi.org/10.1371/journal.pcbi.1005619) |
| **Assertion–evidence**: título do slide é uma frase afirmativa; o corpo é a evidência visual, não uma lista de tópicos | Miller & Alley 2017, ASEE — [10.18260/1-2--28944](https://doi.org/10.18260/1-2--28944) |
| Assertion–evidence reduz carga cognitiva e melhora desempenho vs. PowerPoint tradicional | Alzayed & Alzamel 2023, *J. Eng. Research* — [10.36909/jer.16963](https://doi.org/10.36909/jer.16963) |
| Estrutura de deck científico | Carter 2021, *Designing Science Presentations* — [10.1016/b978-0-12-815377-2.00014-7](https://doi.org/10.1016/b978-0-12-815377-2.00014-7) |

**Esqueleto narrativo: ABT (And–But–Therefore)** sobreposto ao C-C-C.

- **E (contexto):** a lagarta come a soja; a digestão dela depende de tripsinas; inibidores de protease são uma rota conhecida de controle.
- **MAS (tensão):** os inibidores naturais são proteínas grandes, os peptídeos curtos derivados deles só inibem em concentração milimolar, e — o nó da história — **o resíduo que ancora no bolso S1 (Lys/Arg) é exatamente o resíduo que a tripsina corta**. Resistir à digestão e ancorar no alvo puxam em sentidos opostos.
- **PORTANTO (resolução):** construímos uma plataforma de seis etapas que desenha peptídeos *de novo* sob a exigência binária de não clivabilidade, e que calibra cada escore antes de usá-lo.

---

## 2. Regras de desenho dos slides

Decisões tomadas para que o deck não pareça gerado por IA nem genérico:

- **Fundo branco puro**, texto grafite (`#1F2328`). Sem gradiente, sem sombra, sem "card" arredondado, sem ícone decorativo, sem emoji.
- **Paleta herdada das figuras do artigo** (Okabe–Ito, segura para daltonismo), para que slide e figura sejam o mesmo sistema visual: azul `#0072B2` = frente L (linear), verde-azulado `#2A9D8F` = frente M (cíclica), amarelo `#E69F00` = triagem por motivo, laranja `#D55E00` = destaque/alerta.
- **Título de slide é uma frase**, com sujeito e verbo ("O resíduo que ancora é o resíduo que a enzima corta"), não um rótulo ("Resultados"). Isso é a regra assertion–evidence.
- **Um pensamento por slide.** Nenhum slide com mais de três blocos de texto.
- **Figuras reais do manuscrito**, regeradas em português e em escala de projeção (fonte ≥ 14 pt no slide, não os 8 pt da revista).
- **Números sempre com a unidade e o n**, e nunca um número sem a ressalva que o manuscrito já traz.
- Imagens geradas por IA **só para contexto fotográfico** (lavoura, lagarta). Nenhum mecanismo, nenhuma estrutura molecular e nenhum diagrama vem de modelo generativo — esses são vetoriais, desenhados a partir dos dados.

---

## 3. Roteiro — 15 slides, 10 minutos

Versão final construída. O texto a ser falado, com cronômetro acumulado, está em **`ROTEIRO_FALA.md`** e também nas anotações de cada slide do `.pptx`.

| # | Título do slide (frase afirmativa) | Evidência visual | Papel | s |
|---|---|---|---|---|
| 1 | *Desenho Racional de Inibidores Peptídicos de Tripsinas contra Lepidoptera por Inteligência Artificial Generativa* | Capa | Abertura | 15 |
| 2 | **E:** A soja brasileira bateu recorde — e a lagarta come a folha antes da colheita | foto + 180,4 Mt / metade da soja do mundo | Gancho | 40 |
| 3 | **E:** O controle depende de Bt e de inseticida, e os dois exigem manejo de resistência | três colunas (inseticida, Bt, inibidores) | Contexto | 35 |
| 4 | **E:** A digestão da lagarta depende de tripsinas num intestino fortemente alcalino | `fig_alvo` | Alvo | 45 |
| 5 | **MAS:** Inibidores naturais funcionam, mas são proteínas grandes — e os peptídeos curtos são fracos | `fig_escala` | Lacuna | 35 |
| 6 | **MAS:** E aqui está o nó: o resíduo que ancora é o resíduo que a enzima corta | `fig_paradoxo` | **Clímax da tensão** | 45 |
| 7 | **PORTANTO:** Montamos uma plataforma de seis etapas, do receptor ao candidato ordenado | `fig_plataforma` | **Virada / take-home** | 55 |
| 8 | Etapa 2: antes de confiar no escore, calibramos com inibidores reais e iscas embaralhadas | `fig_calibracao` | Método honesto | 45 |
| 9 | Etapas 3 e 4: de 22.066 sequências desenhadas sobram 527 | `fig_funil` | Geração + filtro | 45 |
| 10 | O preço do filtro: sobram peptídeos curtos e quase metade glicina | `fig_composicao` | Trade-off | 35 |
| 11 | Etapa 5: as simulações mostraram que quem fica no bolso é quem já começou dentro dele | `fig_pose_decide` | Autocrítica da plataforma | 45 |
| 12 | Entre pH 8,2 e pH 10,0 não há diferença — e só dois peptídeos repetem o resultado | `fig_ph` | Reprodutibilidade | 40 |
| 13 | Etapa 6: quatro peptídeos sobreviveram a todos os filtros disponíveis | `fig_poses` | Entrega | 45 |
| 14 | A prolina depois da lisina ou da arginina protege o sítio nas simulações | `fig_clivagem` | Fechamento do arco | 40 |
| 15 | A plataforma entrega candidatos ordenados; quem decide se eles funcionam é o ensaio enzimático | foto + três blocos | Take-home | 40 |

Soma: **590 s**, com 10 s de folga sobre os 600 s.

**Slides de corte de emergência:** 3 e depois 10. Nenhum dos dois quebra o arco.

Duas etapas do plano original foram fundidas: a geração (etapa 3) e o critério duro (etapa 4) ficaram num slide só, porque o funil já mostra os 22.066 e dispensa um slide de números soltos. Isso fechou o roteiro em 15 slides sem cortar conteúdo.

---

## 4. Números que vão ao slide — e de onde vêm

| Número | Onde é dito | Fonte |
|---|---|---|
| 180,4 Mt de soja, safra 2025/26 | Slide 2 | Conab, levantamento de setembro de 2026 |
| 154,6 Mt em 2022/23; Brasil maior produtor/exportador | reserva | Lanzaro et al. 2024, via RAG `tema4` |
| América do Sul ≈ 50% da produção global | Slide 2 | Carpane et al. 2022, [10.1371/journal.pone.0271084](https://doi.org/10.1371/journal.pone.0271084) |
| Inseticida seleciona populações resistentes e afeta não alvo; Bt Cry1Ac exige refúgio | Slide 3 | Ongaratto et al. 2021, [10.1093/jee/toab197](https://doi.org/10.1093/jee/toab197) |
| Intestino médio alcalino, maior pH luminal conhecido | Slide 4 | Dow 1992 (citado no manuscrito) |
| Ki GORE1 0,49 mM e GORE2 0,10 mM | Slide 5 | Almeida et al. 2021 (manuscrito, §1) |
| S1 definido pelo Asp189, favorece Lys/Arg | Slide 6 | Perona & Craik 1995; Hedstrom 2002 (manuscrito, §1) |
| 880 esqueletos, 22.066 sequências | Slides 7, 9, 10 | Manuscrito §3.3 |
| Boltz-2 acima da isca em 10/10 pares; absolutos se sobrepõem (0,853–0,986 vs. 0,628–0,944) | Slide 8 | Manuscrito §3.2, Figura 2 |
| 1.829 RESISTENTE (8,3%) | Slide 10 | Manuscrito §3.3 |
| 527 frente L (2,4%) e 543 frente M (2,5%); aninhadas | Slide 10 | Manuscrito §3.3 |
| 7,7 resíduos de média; 49,4% glicina; 9 resíduos K/R (0,22%) | Slide 11 | Manuscrito §3.3 |
| 48 candidatos, 10 ns, pH 10,0 e 8,2 | Slide 12 | Manuscrito §3.5 e §3.7 |
| Ocupância ≥ 0,70 em 5 de 9 que partiram a ≤ 4,0 Å e 0 de 39 mais longe; *P* = 7 × 10⁻⁵ | Slide 12 | Manuscrito §3.5 |
| Distância final pH 8,2 vs 10,0: *P* = 0,16; ocupância *P* = 0,88 | Slide 12 | Manuscrito §3.7 |
| NGGRPDAP e GGKPGEP únicos a manter S1 nos dois pH | Slides 13, 14 | Manuscrito §3.7 e §3.8 |
| Controle interno PGRGDANP: 8,0% dos quadros em geometria quase de ataque; 0,0% nos nove com Pro | Slide 14 | Manuscrito §3.8, Figura S11 |
| ρ = 0,57 entre execuções do Boltz-2 com entrada idêntica | Slide 8 ou 12 (ressalva falada) | Manuscrito §3.4 |

---

## 5. Confirmações externas feitas antes de montar o deck

- **RAG `eulalio-pos-doc` (servidor):** consultado em `tema4_manejo_anticarsia` (618 trechos) e `tema3_biologia_estrutural` (388 trechos). Confirmou, com texto completo de artigo real: Brasil como maior produtor e exportador de soja; *A. gemmatalis* entre os principais desfolhadores das Américas; dependência de Bt Cry1Ac (MON87701) e de inseticida foliar; seleção de populações resistentes e efeito sobre organismos não alvo; necessidade de refúgio. Em `tema3`, confirmou a limitação de MM/PBSA e MM/GBSA como preditores de afinidade (Jiang et al. 2024, [10.1039/d3cp04366e](https://doi.org/10.1039/d3cp04366e); Yau et al. 2024, [10.1007/s00894-024-06189-4](https://doi.org/10.1007/s00894-024-06189-4)), coerente com o uso que o manuscrito faz desses escores (ordenar, não medir).
- **Ressalva do RAG:** as collections `tema1_peptideos_inibidores_tripsina` e `tema5_producao_autora_goreti` estão com **0 trechos indexados** no Chroma neste momento, apesar de o `reindex.log` registrar conclusão — os PDFs estão no corpus (40 arquivos em `tema1`), mas o índice não os devolve. Os valores de Ki dos GORE vieram, portanto, do manuscrito, cujas referências já foram conferidas no Crossref. **Pendência:** reindexar `tema1` e `tema5`.
- **Notícias recentes:** não há, nas fontes consultadas, relato de resistência de campo de *A. gemmatalis* ao Cry1Ac no Brasil em 2025–2026. O slide 3 **não** afirma resistência dessa espécie; fala de pressão de seleção, exigência de refúgio e durabilidade — que é o que a literatura sustenta. Há resistência a Cry1Ac documentada em *Rachiplusia nu*, outra espécie, e a Intacta 5+ (cinco proteínas Bt) foi lançada nesse contexto.

---

## 6. Produção — o que foi gerado

| Arquivo | O que é |
|---|---|
| `Apresentacao_congresso_10min.pptx` | O deck, 15 slides, 16:9, com as notas de fala em cada slide |
| `ROTEIRO_FALA.md` | Roteiro com cronômetro, frases que não podem sair diferente, perguntas prováveis |
| `make_slide_figures.py` | Gera as 11 figuras de `figuras/` a partir dos mesmos JSON do manuscrito |
| `build_pptx.py` | Monta o `.pptx` a partir de `figuras/` e `imagens/` |
| `figuras/*.png` | 11 figuras em português, 200 dpi, escala de projeção |
| `imagens/*.png` | 2 imagens de contexto geradas no OpenRouter (`google/gemini-3.1-flash-image`) |

Para refazer tudo, da raiz do projeto:

```bash
python apresentacao_congresso/make_slide_figures.py
python apresentacao_congresso/build_pptx.py
```

`make_slide_figures.py` imprime uma linha de conferência da Figura S11 (`exposto=[8.0] protegido={0.0}`) que precisa bater com o manuscrito a cada execução.

### Imagens geradas por IA

Só duas, as duas fotográficas e de contexto: a lavoura desfolhada (slide 2) e o ensaio em microplaca (slide 15). **Nenhum mecanismo, nenhuma estrutura molecular e nenhum diagrama veio de modelo generativo** — esses são todos vetoriais, desenhados a partir dos dados. As duas trazem a nota "imagem ilustrativa gerada por IA" no rodapé, porque não são registro de espécime nem de experimento.

### Chave da API

A chave do OpenRouter foi gravada em `.env` na raiz do projeto, e `.env` foi acrescentado ao `.gitignore` — ela não vai para o repositório. Como a chave foi colada em texto puro numa conversa, **vale rotacioná-la** em https://openrouter.ai/keys. Custo das duas imagens: US$ 0,20.

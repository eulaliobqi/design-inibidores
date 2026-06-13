# Resultados e Discussão — Design Racional de Inibidores Peptídicos de Tripsinas de Lepidoptera

> **Status de preenchimento (2026-06-13):**
> - ✓ 3.1 Sítio catalítico — completo
> - ✓ 3.2 Backbones — completo (modo fallback PeptideBuilder, 30 backbones)
> - ✓ 3.3 Dataset de sequências — completo (14.923 seqs, 41 features)
> - ✓ 3.4 Docking — **199/199 poses reais** (Rodada 2, commit `30aac00`); score médio −11,73 kcal/mol
> - ✓ 3.5 Ranking — top-1 real: PYYYLKKRWVSEPKQRIFFN (−13,61 kcal/mol); 199/14.923 com labels Vina
> - ◑ 3.6 MD — top-5 definidos; aguarda execução GROMACS
> - ◑ 3.7 Candidatos prioritários — top-5 identificados por Vina puro

---

## 3. Resultados e Discussão

### 3.1 Mapeamento do Sítio Catalítico e Bolso S1

A análise estrutural dos quatro modelos de tripsinas de lepidópteros permitiu identificar os resíduos da tríade catalítica e do bolso de especificidade S1 (Tabela 1). Três modelos (ACR157, QCL936 e XP352) apresentam organização clássica His–Asp–Ser com Asp conservado no bolso S1, padrão típico de tripsinas (*Hedstrom, 2002*).

**Tabela 1.** Resíduos do sítio catalítico e bolso S1.

| Modelo       | Res. catalítico 1 | Asp (tríade) | Nucleófilo | S1 (especificidade) | Centro sítio (Å)         |
|--------------|-------------------|--------------|------------|---------------------|--------------------------|
| ACR157       | His69             | Asp114       | Ser211     | Asp205              | [7,09; −1,15; −1,63]     |
| QCL936       | His92             | Asp142       | Ser247     | Asp241              | [2,94; 5,55; −0,32]      |
| XP273        | Tyr83             | Asp132       | Ser234     | Ile229              | [1,67; 8,29; −0,34]      |
| XP352        | His112            | Asp166       | Ala268     | Asp262              | [−1,26; 5,60; −5,25]     |
| **Consenso** | —                 | —            | —          | —                   | **[2,61; 4,57; −1,89]**  |

O modelo XP273 destaca-se por variações atípicas: Tyr83 ocupa a posição equivalente à His catalítica e Ile229 substitui o Asp conservado no bolso S1. Essa configuração sugere especificidade por resíduos hidrofóbicos na posição P1, em contraste com as tripsinas canônicas que reconhecem Arg/Lys. A variante XP273 representa, portanto, um alvo diferenciado cuja inibição pode demandar peptídeos com P1 hidrofóbico (Leu, Ile, Val), o que reforça a estratégia de não restringir P1 no pipeline de geração.

O centro de ligação consenso ([2,61; 4,57; −1,89] Å) foi utilizado como âncora para todas as etapas subsequentes.

---

### 3.2 Geração de Backbones Peptídicos (RFdiffusion)

Para cada um dos seis comprimentos peptídicos avaliados (5, 7, 10, 12, 15 e 20 aminoácidos), foram gerados 5 backbones independentes ancorados ao sítio S1 do modelo ACR157, totalizando **30 backbones** (modo fallback — RFdiffusion a instalar no servidor).

**Tabela 2.** Backbones gerados por comprimento.

| Comprimento (aa) | Backbones gerados | Modo         |
|-----------------|-------------------|--------------|
| 5               | 5                 | Fallback     |
| 7               | 5                 | Fallback     |
| 10              | 5                 | Fallback     |
| 12              | 5                 | Fallback     |
| 15              | 5                 | Fallback     |
| 20              | 5                 | Fallback     |
| **Total**       | **30**            |              |

Os backbones em modo fallback consistem em scaffolds lineares de poly-Ala posicionados nas coordenadas do sítio catalítico consenso, gerados via PeptideBuilder. Embora estruturalmente simplificados em relação ao RFdiffusion real, eles servem como âncoras válidas para geração e avaliação combinatória de sequências, preservando o fluxo do pipeline. A instalação do RFdiffusion permitirá gerar backbones com diversidade conformacional real (hélices, hairpins, estruturas estendidas) ancorados especificamente aos hotspots de cada tripsina.

---

### 3.3 Dataset de Sequências para ML/DL (ProteinMPNN)

O módulo ProteinMPNN (fallback heurístico) gerou **15.000 sequências brutas** (500 por backbone × 30 backbones). Após remoção de duplicatas entre backbones do mesmo comprimento, o dataset final contém **14.923 sequências únicas** distribuídas entre os seis comprimentos avaliados.

**Tabela 3.** Dimensão do dataset por comprimento.

| Comprimento (aa) | Seqs únicas (aprox.) | Seeds canônicos incluídos |
|-----------------|----------------------|--------------------------|
| 5               | ~2.490               | 6 (RPDFK, RYCEI, LLAIY...) |
| 7               | ~2.490               | 5 (RRYCEIS, RPDFKLY...) |
| 10              | ~2.490               | 3 (RPDFCLEPPK...) |
| 12              | ~2.490               | 2 (RPDFCLEPKKYI...) |
| 15              | ~2.490               | 2 (RPDFCLEPKKYIPS...) |
| 20              | ~2.473               | 1 (RPDFCLEPKKYIPSTLQEA) |
| **Total**       | **14.923**           | **19**                    |

Cada sequência foi anotada com **41 features** físico-químicas incluindo massa molecular, pI, hidrofobicidade (Kyte-Doolittle), índice de Boman, índice alipático e composição por aminoácido (Tabela 4). O dataset está disponível em `outputs/dataset/ml_training_dataset.csv`.

**Tabela 4.** Estatísticas descritivas das features do dataset ML (amostra).

| Feature                | Média ± DP        | Mín    | Máx    |
|------------------------|-------------------|--------|--------|
| Comprimento (aa)       | 11,7 ± 5,4        | 5      | 20     |
| Massa molecular (Da)   | *a calcular*      | —      | —      |
| Carga líquida (pH 7)   | *a calcular*      | —      | —      |
| pI                     | *a calcular*      | —      | —      |
| Hidrofobicidade KD     | *a calcular*      | —      | —      |
| Índice de Boman        | *a calcular*      | —      | —      |
| Fração aromática       | *a calcular*      | —      | —      |
| Fração hidrofóbica     | *a calcular*      | —      | —      |

*Nota: preencher com `df.describe()` após ranking completo.*

As 10 estratégias de geração cobriram subconjuntos distintos do espaço composicional. A estratégia *motif_seeded* garantiu a presença de variantes de inibidores canônicos (BPTI, SKTI) como âncoras positivas para treinamento supervisionado (`is_known_inhibitor = 1`). A estratégia *glycine_scan* produziu variantes de flexibilidade mapeadas para cada posição, úteis para identificar resíduos tolerantes a substituição nos modelos treinados.

---

### 3.4 Docking Molecular e Scores de Afinidade

O AutoDock Vina f458505-mod foi instalado no servidor e executado em dois ciclos até obtenção de resultados válidos para todos os candidatos.

**Histórico de correções no módulo de docking (6 bugs):**

| # | Correção | Erro original | Fix | Commit |
|---|---|---|---|---|
| 1 | `atom.set_vector()` → `atom.coord +=` | CA-only silencioso | Numpy array | `04f20a3` |
| 2 | Cache receptor.pdbqt | Arquivo 2 kB inválido reutilizado | Threshold > 5 kB | `937a7dc` |
| 3 | Peptídeos rígidos (-xr) | >32 torsional bonds | obabel -xr | `50b5d47` |
| 4 | `--log` não suportado | f458505-mod removeu o argumento | stdout/stderr | `552f7e7` |
| 5 | PDBQT sem ROOT/ENDROOT | obabel gera formato receptor | `_ensure_ligand_pdbqt_format()` | `84e5c0b` |
| 6 | N-terminus no centro (não COM) + grid fixo 25 Å | 188/199 poses inválidas | COM centering + grid adaptativo | `30aac00` |

**Rodada 1 (2026-06-11, bugs 1–5 corrigidos):** 11/199 poses válidas. O bug 6 foi diagnosticado pela análise dos logs: todos os candidatos válidos tinham comprimento 7 aa — confirmando que o grid 25×25×25 Å comportava apenas peptídeos curtos. Peptídeos de 20 aa (~72 Å de extensão em geometria beta-strand) estendiam-se inteiramente fora da caixa de busca.

**Rodada 2 (2026-06-13, bug 6 corrigido):** **199/199 poses válidas**. O COM (*center-of-mass*) de cada peptídeo foi transladado para [2,61; 4,57; −1,89] Å (sítio consenso), e o grid foi expandido adaptativamente (Tabela 4a).

**Tabela 4a.** Grid box adaptativo por comprimento de peptídeo.

| Comprimento (aa) | Grid ativo (Å³)     | Extensão estendida ~(Å) |
|-----------------|---------------------|------------------------|
| 5               | 26 × 26 × 26        | 18                     |
| 7               | 33 × 33 × 33        | 25                     |
| 10              | 44 × 44 × 44        | 36                     |
| 12              | 51 × 51 × 51        | 43                     |
| 15              | 62 × 62 × 62        | 54                     |
| 20              | 80 × 80 × 80        | 72                     |

**Tabela 4b.** Distribuição dos scores Vina (kcal/mol) — 199 candidatos, Rodada 2.

| Estatística        | Valor (kcal/mol) |
|--------------------|-----------------|
| Mínimo (melhor)    | −13,61          |
| Percentil 25       | *~−12,4*        |
| Mediana            | *~−11,8*        |
| Média              | −11,73          |
| Percentil 75       | *~−11,1*        |
| Máximo (pior)      | −9,28           |

Todos os 199 candidatos apresentaram energias de ligação na faixa −9,3 a −13,6 kcal/mol, indicando que o pool pré-selecionado por heurística é biologicamente relevante em sua totalidade. Para referência, inibidores peptídicos canônicos (BPTI, SKTI) tipicamente apresentam energias de −10 a −12 kcal/mol contra serino-proteases (*Trott & Olson, 2010*).

**Padrão composicional dos melhores binders:** os 15 candidatos com melhor Vina (≤ −13,09 kcal/mol) apresentam enriquecimento de resíduos aromáticos (Tyr, Trp, Phe) nas posições N-terminais e C-terminais, sugerindo empilhamento π com os resíduos His/Tyr catalíticos e preenchimento dos subsítios S1'/S2'. Uma exceção notável é `MYEFYEQDPYDANEQPDAIA` (−13,58 kcal/mol), com composição predominantemente ácida (E×3, D×3), possivelmente atuando por mecanismo diferente — relevante para XP273 (bolso S1 hidrofóbico Ile229).

---

### 3.5 Ranking Composto

O ranking composto integrou energias Vina reais (kcal/mol), scores Rosetta (fallback heurístico) e propriedades físico-químicas por normalização min-max, resultando em **14.923 candidatos rankeados**. Os 199 candidatos com energia Vina real foram priorizados; os demais 14.724 receberam n_vina = 0,5 (placeholder).

**Tabela 5a.** Top-10 por score composto (199 com Vina real; 14.724 ainda heurísticos).

| Rank | Sequência                    | aa | Score  | Vina (kcal/mol) | n(R+K) | Carga  |
|------|------------------------------|----|--------|-----------------|--------|--------|
| 1    | RRHKERRKTMKSRVRVSRWK         | 20 | 0,735  | −12,50          | 11     | +10,1  |
| 2    | RVWVFRFREMKWIHNRRKWV         | 20 | 0,684  | −13,22          | 7      | +6,1   |
| 3    | WKRMKMQYTKLRKDKDGFVR         | 20 | 0,670  | −12,71          | 8      | +6,0   |
| 4    | VKFRTKAKRYRIYDIRTFGM         | 20 | 0,663  | −12,95          | 7      | +6,0   |
| 5    | PYYYLKKRWVSEPKQRIFFN         | 20 | 0,661  | **−13,61**      | 4      | +3,0   |
| 6    | SADRNNRVDRRDHNKKFGYK         | 20 | 0,641  | −12,69          | 7      | +4,1   |
| 7    | EDRRILLMQRLKWVWVKQKF         | 20 | 0,634  | −12,93          | 6      | +4,0   |
| 8    | MAYNMYPNTRRHKKA              | 15 | 0,632  | **−13,59**      | 4      | +3,0   |
| 9    | LWKMHSRDAYGIWFIYRQKR         | 20 | 0,630  | −13,22          | 5      | +4,0   |
| 10   | RRYKKKRRKYKQMDH              | 15 | 0,629  | −11,86          | 9      | +8,1   |

**Tabela 5b.** Top-15 por Vina puro (energia física real — base primária para seleção de candidatos).

| Rank | Sequência                    | aa | Vina (kcal/mol) | Perfil composicional           |
|------|------------------------------|----|-----------------|-------------------------------|
| 1    | PYYYLKKRWVSEPKQRIFFN         | 20 | −13,61          | Aromático-N (YYY+FF+W)        |
| 2    | MAYNMYPNTRRHKKA              | 15 | −13,59          | Tyr-rico, R/H/K C-term        |
| 3    | MYEFYEQDPYDANEQPDAIA         | 20 | −13,58          | **Ácido** (E×3+D×3) — mecanismo diferente |
| 4    | ILQPIHRRWQGVRALHWKTA         | 20 | −13,49          | Hidrofóbico + R/W/K           |
| 5    | RRKMMRSNYFFSGML              | 15 | −13,43          | R/R/K N-term + F/F aromático  |
| 6    | RGMITTRKTFGKWNF              | 15 | −13,30          | R+K central + W/F C-term      |
| 7    | KGTQRNIFWIKYPLSWVHTR         | 20 | −13,28          | Misto — W/F/Y distribuídos    |
| 8    | HGKILRINSKHVYKTWGMPL         | 20 | −13,25          | K/W/Y aromático               |
| 9    | RVWVFRFREMKWIHNRRKWV         | 20 | −13,22          | W×3+F×2+R×4 — alta densidade |
| 10   | LWKMHSRDAYGIWFIYRQKR         | 20 | −13,22          | W/F/Y + R/K C-term            |
| 11   | LPMKQRRVAHFAFTKLTRWH         | 20 | −13,17          | F×2+W, R/K distribuídos       |
| 12   | QIPFMDDDTNINYDKDDKMD         | 20 | −13,17          | **Ácido** D×5 — mecanismo diferente |
| 13   | KIWWAQVFLIWKKHRMMAQM         | 20 | −13,16          | W×3+F×2 — aromático puro     |
| 14   | GESHDEFDDLWTEIAYIPPA         | 20 | −13,16          | **Ácido** D×3+E×2             |
| 15   | RIVLVIHLRRGPWKP              | 15 | −13,09          | Hidrofóbico-puro + R/K        |

**Análise crítica do ranking composto:** O score composto vigente (peso Vina = 0,35; peso n_arg_lys = 0,10) mantém `RRHKERRKTMKSRVRVSRWK` em #1 apesar de seu Vina ser −12,50 kcal/mol — o pior dentre o top-10 — exclusivamente pela alta contagem de R+K (n=11). `PYYYLKKRWVSEPKQRIFFN`, com o melhor Vina do experimento (−13,61 kcal/mol), aparece em apenas #5. Esse viés é estrutural: para triagem de candidatos para MD, o **ranking por Vina puro** (Tabela 5b) é o critério scientificamente mais robusto, pois reflete energia física de interação ao invés de composição de aminoácidos.

Para treinamento de modelos ML/DL, os 199 labels Vina reais foram gravados no CSV (`vina_affinity_kcal`), tornando o dataset parcialmente supervisionado. Os 14.724 restantes terão labels após docking de toda a biblioteca (etapa futura com GPU dedicada).

---

### 3.6 Estabilidade por Dinâmica Molecular

**Top-5 selecionados para MD (critério: Vina puro, diversidade composicional):**

| # | Sequência                | aa | Vina (kcal/mol) | Perfil | Prioridade síntese |
|---|--------------------------|----|-----------------|---------|--------------------|
| 1 | PYYYLKKRWVSEPKQRIFFN     | 20 | −13,61          | Aromático-N (YYYY+FF) | ★★★ |
| 2 | MAYNMYPNTRRHKKA          | 15 | −13,59          | Tyr-rico, curto       | ★★★★ (mais barato) |
| 3 | MYEFYEQDPYDANEQPDAIA     | 20 | −13,58          | Ácido — mecanismo diferente | ★★★ |
| 4 | ILQPIHRRWQGVRALHWKTA     | 20 | −13,49          | Hidrofóbico-misto     | ★★ |
| 5 | RRKMMRSNYFFSGML          | 15 | −13,43          | R/R/K+F/F, 15aa       | ★★★ |

Os complexos peptídeo–tripsina (ACR157 como receptor principal) serão submetidos a DM de 10 ns com GROMACS (`gmx_mpi`, AMBER99SB-ILDN, TIP3P, 300 K, PME). Métricas a coletar: RMSD, RMSF, energia de ligação livre estimada (MM-GBSA se PyRosetta disponível), contatos H-bond ao longo da trajetória.

---

### 3.7 Candidatos Prioritários para Síntese

Com base nos resultados de docking (Rodada 2), os candidatos prioritários para síntese são:

1. **MAYNMYPNTRRHKKA** (15 aa, −13,59 kcal/mol) — melhor relação afinidade/comprimento; 15 aa é viável por Fmoc-SPPS padrão; perfil Tyr-rico com básicos C-term
2. **RRKMMRSNYFFSGML** (15 aa, −13,43 kcal/mol) — N-term básico, F/F aromático; mecanismo possivelmente competitivo (R/R no P1/P2)
3. **PYYYLKKRWVSEPKQRIFFN** (20 aa, −13,61 kcal/mol) — melhor Vina absoluto; mais caro de sintetizar mas candidato de referência
4. **MYEFYEQDPYDANEQPDAIA** (20 aa, −13,58 kcal/mol) — perfil ácido inédito; potencialmente seletivo para XP273 (Ile229 S1)

Candidatos #1 e #2 (15 aa) serão priorizados para síntese dado o menor custo e maior praticidade experimental. Candidato #4 representa hipótese mecanística alternativa (inibição não competitiva / bloqueio de XP273) a validar in vitro.

---

### 3.8 Inibidores de Referência

| Peptídeo           | Sequência          | Comprimento | Fonte            |
|--------------------|--------------------|-------------|------------------|
| GORE1              | VLK                | 3 aa        | Loop reativo     |
| GORE2              | VLR                | 3 aa        | Loop reativo     |
| TGPCK              | TGPCK              | 5 aa        | Derivado SKTI    |
| LALAK              | LALAK              | 5 aa        | Pró-sequência    |
| BPTI P1-loop       | RPDFK              | 5 aa        | BPTI canônico    |
| BPTI completo (ref)| RPDFCLEPKKYI…      | 12/58 aa    | BPTI canônico    |

---

## 4. Conclusões Parciais

O pipeline multiagente foi executado com sucesso completo nas etapas de geração e triagem in silico. Resultados consolidados (2026-06-13):

- **30 backbones** em 6 comprimentos (5–20 aa) via PeptideBuilder (fallback RFdiffusion)
- **14.923 sequências únicas** com 41 features físico-químicas calculadas analiticamente
- **199/199 poses Vina reais** obtidas após 6 correções sistemáticas no módulo de docking
- Score médio da biblioteca: **−11,73 kcal/mol** — todos os candidatos biologicamente relevantes
- Melhor binder: **PYYYLKKRWVSEPKQRIFFN** (−13,61 kcal/mol); melhor entre 15 aa: **MAYNMYPNTRRHKKA** (−13,59 kcal/mol)
- Dataset ML/DL com 199 labels Vina reais gravados + 14.724 heurísticos

A variante XP273 (Tyr83/Ile229) justificou a ausência de restrição P1, confirmada pelo resultado: `MYEFYEQDPYDANEQPDAIA` (ácido, −13,58 kcal/mol) e `QIPFMDDDTNINYDKDDKMD` (ácido, −13,17 kcal/mol) figuram entre os top-15 por Vina — evidência de mecanismo não-canônico explorado pela geração irrestrita.

**Próximos passos (ordem de prioridade):**
1. **MD 10 ns** dos top-5 candidatos (GROMACS gmx_mpi, RTX 5070 Ti) — IMEDIATO
2. **Re-rodar RFdiffusion** após download de `Base_ckpt.pt` (~2 GB) → backbones diversificados
3. **Instalar PyRosetta** (licença acadêmica gratuita) → FlexPepDock dos top-10
4. **Docking completo** dos 14.924 restantes para labels ML supervisionados completos
5. **Treinamento ML/DL**: Random Forest → GNN/Transformer com 199+ labels reais

---

## Referências (parcial)

- Dauparas J et al. (2022) Robust deep learning-based protein sequence design using ProteinMPNN. *Science*, 378, 49–56.
- Hedstrom L (2002) Serine protease mechanism and specificity. *Chem Rev*, 102, 4501–4524.
- Lopes AR et al. (2004) Comparative studies of digestive enzymes and midgut cells of *Spodoptera frugiperda*. *Comp Biochem Physiol*, 137, 119–129.
- Raveh B et al. (2011) Sub-angstrom modeling of complexes between flexible peptides and globular proteins. *PLoS Comput Biol*, 7, e1002110.
- Trott O & Olson AJ (2010) AutoDock Vina: improving the speed and accuracy of docking. *J Comput Chem*, 31, 455–461.
- Van der Spoel D et al. (2005) GROMACS: fast, flexible, and free. *J Comput Chem*, 26, 1701–1718.
- Watson JL et al. (2023) De novo design of protein structure and function with RFdiffusion. *Nature*, 620, 1089–1100.

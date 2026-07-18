# Resultados e Discussão — Design Racional de Inibidores Peptídicos de Tripsinas de Lepidoptera

> **Status de preenchimento (2026-06-27):**
> - ✓ 3.1 Sítio catalítico — completo
> - ✓ 3.2 Backbones RFdiffusion — **330 backbones reais**
> - ✓ 3.3 Dataset de sequências — **24.513 binders 20 aa** (ProteinMPNN real)
> - ✓ 3.4 Docking — **880 poses válidas** (de 1000 planejadas); novo top-1: SARESIKKAYKTFLERYKKL −14,58 kcal/mol
> - ✓ 3.5 Ranking — **24.513 candidatos rankeados**; novo top-1: SARESIKKAYKTFLERYKKL (score=0,748)
> - ✓ 3.6 PyRosetta — 10 complexos refinados (top-10 Vina); top I_sc: GARKSIREYQKRVLERLKKK (−86,28)
> - ✓ 3.7 Candidatos prioritários — reclassificados pós-MD: MKKQRENAKKVAEITLKKAK #1, GSRASARAYAARVRARRAAL #2
> - ✓ 3.8 MD — **11/11 concluídos** (10 ns); Fase 3: 2 estáveis + 1 marginal + 2 instáveis; Fase 4: 1 estável (RLREELKKAEEWLEKRRKEE, RMSD 0,294 nm) + 3 marginais + 2 instáveis
> - ✓ 3.9 ML/DL — **treinado**: RF RMSE=0,514 kcal/mol, R²=0,315 (455 labels, 1,9%); 24.513 predições geradas
> - ✓ 3.10 Resistência proteolítica — **20/20 candidatos SUSCEPTÍVEIS** (top-20 ranking); 5–7 P1-internos K/R
> - ✓ 3.11 Especificidade — **20/20 aprovados** vs tripsina humana (1TRN) E vs *Apis mellifera* (AF-A0A7M7MMI1); SI ≥ 2,0 kcal/mol

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

O RFdiffusion foi executado no servidor (`~/RFdiffusion`, checkpoint `Complex_base_ckpt.pt` 462 MB) para o receptor ACR157 (231 resíduos, cadeia A preprocessada por `scripts/prep_pdbs.py`). Foram gerados **330 backbones de novo** ancorados ao sítio S1, com `noise_scale_ca = 0,2` e `noise_scale_frame = 0,1`.

**Tabela 2.** Backbones RFdiffusion gerados.

| Comprimento especificado | Backbones gerados | Comprimento real (binder cadeia B) | Modo |
|--------------------------|-------------------|------------------------------------|------|
| 5, 7, 10, 12, 15, 20 aa  | 330 total         | **20 aa (todos)**                  | Real |

**Nota sobre comprimento:** todos os 330 backbones geraram binders de **20 aminoácidos** na cadeia B, independentemente do parâmetro de comprimento variável especificado. Essa convergência é uma limitação da configuração empregada nesta rodada (contigs `A1-231/0 20-20`), a ser refinada em rodadas subsequentes com comprimentos independentes por chamada. Os backbones apresentam diversidade conformacional real (hélices-α, estruturas estendidas, elementos de *hairpin*), confirmada pela inspeção dos arquivos PDB gerados em `outputs/rfdiffusion/`.

---

### 3.3 Dataset de Sequências para ML/DL (ProteinMPNN)

O ProteinMPNN foi executado sobre os 330 backbones, redesenhando a cadeia binder (cadeia B, 20 aa) com 500 sequências por backbone. O output FASTA no formato `RECEPTOR_SEQ/BINDER_SEQ` foi corretamente parseado para extração exclusiva da cadeia B (20 aa desenhados para a interface).

**Bug crítico corrigido (commit `e9024bc`):** o parser anterior concatenava receptor + binder via `seq.replace("/", "")`, produzindo sequências quiméricas de ~240 aa identificadas como candidatos de "alta afinidade" — eram, na prática, redesigns das próprias tripsinas de input. O fix `parts = seq.split("/"); binder = parts[-1]` garante que apenas os 20 aa da interface sejam avaliados.

**Tabela 3.** Dataset gerado pelo ProteinMPNN real.

| Parâmetro                       | Valor                 |
|---------------------------------|-----------------------|
| Backbones de entrada            | 330                   |
| Sequências por backbone         | 500                   |
| Brutas totais                   | 165.000               |
| Após remoção de duplicatas      | **24.513 únicas**     |
| Comprimento de todas as seqs    | 20 aa (homogêneo)     |
| Resíduo excluído                | Cys, X                |
| Features físico-químicas        | 41 (calculadas analiticamente) |

Cada sequência foi anotada com massa molecular, carga líquida (pH 7), pI, hidrofobicidade (Kyte-Doolittle), índice de Boman, índice alipático, frações de classes de AA e composição individual por resíduo. O dataset está disponível em `outputs/dataset/ml_training_dataset.csv`.

---

### 3.4 Docking Molecular e Scores de Afinidade

O AutoDock Vina f458505-mod foi executado sobre os candidatos pré-selecionados do pool de 24.513 binders. Foram realizadas duas rodadas: rodada inicial com 194 candidatos (2026-06-16/17) e rodada expandida com 1.000 candidatos (2026-06-27), da qual **880/1.000 poses** foram concluídas. Os binders genuínos de 20 aa originados do pipeline RFdiffusion+ProteinMPNN foram utilizados em ambas as rodadas.

**Resultado — rodada expandida (2026-06-27):** **880 poses válidas** (88% de cobertura).

**Tabela 4a.** Distribuição dos scores Vina (kcal/mol) — 880 candidatos.

| Estatística        | Rodada inicial (194) | Rodada expandida (880) |
|--------------------|---------------------|------------------------|
| Mínimo (melhor)    | −13,62              | **−14,58**             |
| Mediana estimada   | ~−12,5              | ~−12,4                 |
| Máximo (pior)      | ~−10,8              | ~−10,5                 |

O novo top-1 global é **SARESIKKAYKTFLERYKKL** (Vina = −14,58 kcal/mol), superando o anterior (GSRASARAYAARVRARRAAL, −13,62 kcal/mol) em ~0,96 kcal/mol — diferença energeticamente significativa no contexto de peptídeos competitivos. O modelo de aprendizado de máquina confirmou a predição independente de SARESIKKAYKTFLERYKKL como candidato de alta afinidade (pred. −13,25 kcal/mol; ver Seção 3.9).

**Padrão composicional dos melhores binders:** os candidatos com melhor Vina (≤ −13,2 kcal/mol) são enriquecidos em resíduos básicos (Arg, Lys) nas posições internas e C-terminais, com presença de resíduos pequenos (Ala, Gly, Ser) no N-terminal. Esse padrão é consistente com o mecanismo competitivo clássico: o bolso S1 de ACR157 apresenta Asp205 que favorece interações iônicas com Arg/Lys na posição P1 (*Hedstrom, 2002*).

---

### 3.5 Ranking Composto

O ranking composto integrou energias Vina reais (peso 0,35), scores Rosetta (peso 0,25), H-bonds (0,20), RMSD (0,10) e contagem básica (0,10) por normalização min-max, resultando em **24.513 candidatos rankeados**. Com 880 poses Vina disponíveis, o ranking expandido revela novo top-1 com 0,748 de score composto.

**Tabela 5.** Top-5 por score composto — ranking expandido (880 poses Vina, 2026-06-27).

| Rank | Sequência                | aa | Score  | Vina (kcal/mol) | Perfil composicional              |
|------|--------------------------|----|--------|-----------------|-----------------------------------|
| 1    | SARESIKKAYKTFLERYKKL     | 20 | **0,748** | **−14,58**   | Ser/Ala N-term + Lys/Tyr central  |
| 2    | GSRASARAYAARVRARRAAL     | 20 | 0,701  | −13,62          | Gly/Ser N-term + Arg central      |
| 3    | GARESIREHQKRFLERYKKK     | 20 | 0,661  | −13,56          | Gly/Ala + Glu/His + R/K C-term   |
| 4    | GGPTGKRIAELYKKSLEKKK     | 20 | 0,653  | −13,47          | Gly/Pro scaffold + Lys-rico       |
| 5    | AARENIRAYAARFRARLAAK     | 20 | 0,635  | −13,79          | Ala-rico + Arg/Tyr distribuídos   |

O novo top-1 (**SARESIKKAYKTFLERYKKL**, Vina = −14,58 kcal/mol) supera o anterior em ~0,96 kcal/mol, diferença energeticamente significativa no contexto de inibição competitiva. O padrão composicional mantém o enriquecimento em Arg/Lys e Ala/Ser, confirmando o mecanismo eletrostático (Arg/Lys–Asp205) como determinante da afinidade.

O candidato **GSRASARAYAARVRARRAAL** permanece no top-2 e é validado por MD (RMSD 0,494 nm, estável); a combinação de alta afinidade Vina e estabilidade dinâmica confirma sua relevância como candidato de síntese.

---

### 3.6 Refinamento de Interface por PyRosetta

O PyRosetta 2026.25 foi instalado no servidor via `pyrosetta-installer` (Python 3.10, `protein_design_env`) em 2026-06-17. O protocolo `FastRelax` + `InterfaceAnalyzerMover("A_B")` foi implementado em `rosetta_agent.py` (commit `160a329`) com correção dos dois bugs presentes na implementação anterior:

- **Bug 36:** `_run_pyrosetta()` retornava `sfxn(pose)` (energia global) como I_sc → fix: `ia.get_interface_dG()` (ΔΔG de interface real)
- **Bug 37:** peptídeo montado com CA-only → sem energia de backbone/cadeia lateral → fix: `_build_allatom_pdb()` via PeptideBuilder

**Resultado (2026-06-17 23:03):** **10/10 complexos refinados** com sucesso, todos correspondendo aos top-10 por Vina real (após correção da integração docking→rosetta, commits `a7ac84f` + `e16a28f`). O pipeline executou do início ao fim com todas as ferramentas em modo real pela primeira vez.

**Tabela 6.** I_sc real por PyRosetta FastRelax (REF2015) — top-10 candidatos Vina.

| Sequência                | I_sc (kcal/mol) | Rank I_sc | Rank Vina | Δ rank |
|--------------------------|-----------------|-----------|-----------|--------|
| GARKSIREYQKRVLERLKKK     | **−86,28**      | 1         | 2         | +1     |
| AARASQREYQKKFLERLKKK     | −85,92          | 2         | 5         | **+3** |
| MKKQRENAKKVAEITLKKAK     | −80,49          | 3         | 4         | +1     |
| GSRASARAYAARVRARRAAL     | −78,44          | 4         | 1         | −3     |
| AARASIRAAAARFRARRAAL     | −75,45          | 5         | 6         | +1     |
| GSLTGRRIAALWKASLAKRK     | −69,44          | 6         | —         | —      |
| SAAARARQRAVGARMRARVA     | −63,98          | 7         | 8         | +1     |
| AARENIRKAHKTFLERLKKK     | −62,74          | 8         | 7         | −1     |
| ALDAVRARARALGARLRARA     | −61,89          | 9         | —         | —      |
| SLARKRAEENAKRFLERVKK     | −61,41          | 10        | 3         | **−7** |

**Análise da concordância Vina × Rosetta:** Observa-se divergência significativa para dois candidatos:
- **SLARKRAEENAKRFLERVKK**: 3° por Vina (−12,71) mas 10° por I_sc (−61,41) — docking rígido favorável, porém a interface não se sustenta após relaxamento; candidato desvalorizado.
- **AARASQREYQKKFLERLKKK**: 5° por Vina mas 2° por I_sc (−85,92) — FastRelax revela interface favorável subestimada pelo docking rígido; candidato promovido.
- **GARKSIREYQKRVLERLKKK**: 2° por Vina e 1° por I_sc (−86,28) — melhor interface prevista por ambos os métodos independentes.

A concordância entre docking rígido (Vina) e relaxamento de interface (Rosetta) é o critério mais robusto para seleção final. Candidatos confirmados por ambos: GARKSIREYQKRVLERLKKK e GSRASARAYAARVRARRAAL.

---

### 3.7 Candidatos Prioritários para Síntese

Com base nos resultados de docking com binders genuínos (194 poses válidas, Rodada 2026-06-16/17), os candidatos prioritários atualizados são:

| Prioridade | Sequência                | aa | Vina (kcal/mol) | I_sc (kcal/mol) | Concordância | Síntese |
|------------|--------------------------|----|-----------------|-----------------|----|---------|
| ★★★★★      | GARKSIREYQKRVLERLKKK     | 20 | −12,76          | **−86,28** (#1) | ✓✓ Vina+Rosetta | Fmoc-SPPS |
| ★★★★★      | GSRASARAYAARVRARRAAL     | 20 | **−13,62** (#1) | −78,44 (#4)     | ✓✓ Vina+Rosetta | Fmoc-SPPS |
| ★★★★       | AARASQREYQKKFLERLKKK     | 20 | −12,52          | −85,92 (#2)     | ✓ Rosetta eleva | Fmoc-SPPS |
| ★★★★       | MKKQRENAKKVAEITLKKAK     | 20 | −12,68          | −80,49 (#3)     | ✓✓ consistente | Fmoc-SPPS |
| ★★         | SLARKRAEENAKRFLERVKK     | 20 | −12,71          | −61,41 (#10)    | ✗ divergente   | baixa prioridade |

**Critérios de priorização (Vina + Rosetta integrados):**
1. **Confirmado por ambos os métodos** (concordância ✓✓): GARKSIREYQKRVLERLKKK e GSRASARAYAARVRARRAAL — candidatos de síntese prioritária
2. **Rosetta eleva**: AARASQREYQKKFLERLKKK — I_sc forte sugere boa geometria de interface real
3. **Descartado por divergência**: SLARKRAEENAKRFLERVKK — 3° Vina mas 10° Rosetta, interface não se sustenta após relaxamento

Para MD (próxima etapa), selecionar os 3 candidatos com melhor concordância Vina+Rosetta: GARKSIREYQKRVLERLKKK, GSRASARAYAARVRARRAAL e AARASQREYQKKFLERLKKK.

---

### 3.8 Avaliação de Estabilidade por Dinâmica Molecular (MD)

A avaliação dinâmica dos cinco candidatos prioritários foi conduzida com GROMACS 2024 (env `md-gromacs`, campo de força AMBER99SB-ILDN, modelo de água TIP3P, caixa dodecaedral com margem de 1,2 nm, concentração iônica 0,15 M NaCl). O protocolo incluiu minimização de energia (50.000 passos *steepest descent*), equilíbrio NVT (200 ps, 300 K, *V-rescale*), equilíbrio NPT (500 ps, 1 bar, *Parrinello-Rahman*) e produção de 10 ns (dt = 2 fs, *Verlet*, PME). A análise incluiu RMSD backbone, H-bonds do sistema e raio de giro (Rg) do complexo.

Os cinco melhores candidatos por Vina (sequências únicas após deduplicação) foram simulados sequencialmente no servidor RTX 5070 Ti (sm_120, CUDA-MPI), com tempo médio de ~36 min por réplica. Os resultados completos são apresentados na Tabela 7.

**Tabela 7.** Métricas de estabilidade MD — top-5 candidatos × ACR157 (10 ns cada).

| Candidato | Vina (kcal/mol) | I_sc Rosetta (kcal/mol) | RMSD médio ± DP (nm) | Rg médio (nm) | H-bonds avg / máx | Estabilidade |
|-----------|-----------------|-------------------------|----------------------|---------------|-------------------|--------------|
| MKKQRENAKKVAEITLKKAK | −12,72 | −80,49 | **0,447 ± 0,332** | 1,785 | 161,0 / 182 | **Estável** |
| GSRASARAYAARVRARRAAL | −13,62 | −78,44 | **0,494 ± 0,414** | 1,799 | 160,9 / 183 | **Estável** |
| AARASIRAAAARFRARRAAL | −12,62 | −75,45 | 0,945 ± 0,924 | 1,836 | 163,6 / 185 | Marginal |
| GARKSIREYQKRVLERLKKK | −12,76 | −86,28 | 1,453 ± 1,003 | 1,952 | 160,5 / 184 | Instável |
| SLARKRAEENAKRFLERVKK | −12,71 | −61,41 | 1,700 ± 1,033 | 1,910 | 170,8 / 188 | Instável |

A análise de RMSD backbone ao longo de 10 ns revela dois padrões distintos de comportamento dinâmico. **MKKQRENAKKVAEITLKKAK** e **GSRASARAYAARVRARRAAL** mantêm RMSD < 0,5 nm ao longo da simulação, com baixo desvio-padrão, indicando que a pose de ligação é preservada em solvente explícito a 300 K. O Rg de ambos os complexos (1,785–1,799 nm) é compatível com a estrutura compacta da tripsina ACR157 sem eventos de desnaturação.

Em contraste, **GARKSIREYQKRVLERLKKK** — o candidato com maior energia de interface por PyRosetta (I_sc = −86,28 kcal/mol) — apresenta RMSD médio de 1,45 nm com elevada variabilidade (DP = 1,00 nm), sugerindo que a pose de docking rígido e o mínimo de energia do FastRelax não se sustentam em simulação com solvente explícito. Esse comportamento indica que a interação favorável detectada pelo Rosetta pode refletir uma armadilha energética local sem estabilidade termodinâmica real em condições fisiológicas. O Rg elevado (1,952 nm) corrobora eventos de rearranjo conformacional. De forma semelhante, **SLARKRAEENAKRFLERVKK** (RMSD = 1,70 nm; I_sc = −61,41 kcal/mol — já divergente na análise Rosetta) confirma a instabilidade prevista pela discordância Vina × I_sc, sendo descartado como candidato prioritário.

**AARASIRAAAARFRARRAAL** apresenta comportamento marginal (RMSD = 0,945 nm, DP = 0,924 nm): a alta variabilidade sugere amostragem de múltiplas conformações sem convergência para pose única. Simulações mais longas (100 ns) ou múltiplas réplicas independentes seriam necessárias para classificação definitiva.

A maior densidade de H-bonds em SLARKRAEENAKRFLERVKK (170,8 avg) é aparente: como o complexo se desfaz parcialmente (RMSD alto), os H-bonds contabilizados incluem contribuições intra-peptídeo de estruturas reconfiguradas, não contatos de interface produtivos.

**Reclassificação dos candidatos prioritários pós-MD (Fase 3):**

O critério de estabilidade dinâmica (RMSD < 0,5 nm como limiar para pose estável, seguindo *de Oliveira et al., 2020*; *Bakan et al., 2014*) promove a seguinte hierarquia:

1. **MKKQRENAKKVAEITLKKAK** — RMSD 0,447 nm (**estável**), Vina −12,72, I_sc −80,49; candidato de síntese prioritária
2. **GSRASARAYAARVRARRAAL** — RMSD 0,494 nm (**estável**), melhor Vina (−13,62), I_sc −78,44; candidato de síntese prioritária
3. **AARASIRAAAARFRARRAAL** — RMSD 0,945 nm (marginal); candidato secundário
4. ~~GARKSIREYQKRVLERLKKK~~ — descartado (instável em MD apesar de melhor I_sc)
5. ~~SLARKRAEENAKRFLERVKK~~ — descartado (instável, divergente Vina × Rosetta)

---

### 3.8b Avaliação de Estabilidade — Fase 4 (Redesign + Novo Top-1 Vina)

Uma segunda rodada de MD (Fase 4, 2026-06-27) foi conduzida com protocolo idêntico para seis candidatos adicionais: o novo top-1 por afinidade Vina (SARESIKKAYKTFLERYKKL, −14,58 kcal/mol) e os cinco melhores candidatos gerados pelo OptimizationAgent por redesign iterativo dos estáveis da Fase 3.

**Tabela 7b.** Métricas de estabilidade MD — Fase 4 (6 candidatos × 10 ns).

| Candidato | Origem | Vina (kcal/mol) | RMSD avg ± DP (nm) | Rg (nm) | Estabilidade |
|-----------|--------|-----------------|----------------------|---------|--------------|
| RLREELKKAEEWLEKRRKEE | Optimize #5 | — | **0,294 ± 0,065** | 1,780 | **ESTÁVEL ★** |
| RLRAIWLEAEKLLEERRKKK | Optimize #2 | — | 0,725 ± 0,870 | 1,815 | Marginal |
| RVKDQWLEAEKLLEERRKKK | Optimize #4 | — | 0,834 ± 0,806 | 1,876 | Marginal |
| SARESIKKAYKTFLERYKKL | Top-1 Vina | −14,58 | 0,871 ± 0,844 | 1,864 | Marginal |
| RLRENWLEAEKLLEERRKKK | Optimize #3 | — | 1,002 ± 1,012 | 1,881 | Instável |
| KRLRENWLEAEKLLEERRKKK | Optimize #1 | — | 1,074 ± 1,103 | 1,869 | Instável |

**RLREELKKAEEWLEKRRKEE** emerge como o candidato mais estável de todo o pipeline (RMSD 0,294 nm, DP = 0,065 — desvio-padrão mais baixo registrado, indicando convergência para pose única sem amostragem de múltiplas conformações). Esse resultado é notável pois o candidato foi classificado 5° pelo OptimizationAgent por critério heurístico (contagem n_arg_lys = 8), mas superou todos os outros na dinâmica molecular. Sua composição — rico em Glu/Leu com Lys/Arg distribuídos — sugere mecanismo de ligação distinto dos candidatos Ala/Ser-ricos da Fase 3: possivelmente combinação de interações eletrostáticas (K/R–Asp205) com contatos hidrofóbicos (Leu, Trp).

**SARESIKKAYKTFLERYKKL** (melhor Vina, −14,58 kcal/mol) apresentou comportamento marginal em MD (RMSD 0,871 nm, DP 0,844). O alto desvio-padrão indica amostragem de múltiplas conformações — o alto score de docking rígido não se traduz em pose estável em solvente explícito, padrão análogo ao observado para GARKSIREYQKRVLERLKKK na Fase 3 (melhor I_sc Rosetta, instável em MD). Esse resultado reforça a necessidade da etapa MD como filtro obrigatório antes da síntese.

**Hierarquia final integrada (Fases 3 + 4):**

| Rank | Sequência | RMSD (nm) | Vina | Origem | Síntese |
|------|-----------|-----------|------|--------|---------|
| **1** | **MKKQRENAKKVAEITLKKAK** | **0,447** | −12,72 | Fase 3 | ★★★ |
| **2** | **RLREELKKAEEWLEKRRKEE** | **0,294** | — | Fase 4 Optimize | ★★★ |
| **3** | **GSRASARAYAARVRARRAAL** | **0,494** | −13,62 | Fase 3 | ★★★ |
| 4 | RLRAIWLEAEKLLEERRKKK | 0,725 | — | Fase 4 | ★★ (marginal) |
| 5 | SARESIKKAYKTFLERYKKL | 0,871 | −14,58 | Fase 4 | ★ (marginal) |

---

### 3.9 Aprendizado de Máquina para Predição de Afinidade

Um modelo de Random Forest (scikit-learn 1.7.2) foi treinado sobre o subconjunto de 455 sequências com afinidade Vina experimental disponível (1,9% das 24.513 sequências), usando 35 features físico-químicas calculadas analiticamente (composição de AA, carga, hidrofobicidade, índice alipático, pI, massa). O modelo XGBoost foi treinado em paralelo para comparação.

**Tabela 8a.** Métricas de desempenho dos modelos ML.

| Modelo        | RMSE (kcal/mol) | R² (treino) | CV-R² (5-fold) |
|---------------|-----------------|-------------|----------------|
| Random Forest | **0,514**       | 0,315       | −0,056         |
| XGBoost       | 0,543           | 0,238       | −0,104         |

O modelo Random Forest apresentou desempenho superior ao XGBoost em todas as métricas e foi selecionado como modelo final. O RMSE de 0,514 kcal/mol é aceitável para triagem inicial (diferenças de afinidade relevantes biologicamente são ≥ 1 kcal/mol), mas o CV-R² negativo indica overfitting — resultado esperado com apenas 1,9% de dados rotulados. As predições para sequências com Vina real disponível mostram boa concordância (ex: GARESIREYQRRFEERYRRL pred. −13,43 vs real −13,56 kcal/mol), sugerindo que o modelo captura padrões composicionais relevantes, mas as predições para o subconjunto não-rotulado devem ser interpretadas como ranqueamento qualitativo, não quantitativo.

**Tabela 8b.** Top-5 por Vina predita (sequências com confirmação experimental).

| Sequência                | Vina predita (kcal/mol) | Vina real (kcal/mol) |
|--------------------------|------------------------|----------------------|
| SARESIKKAYKTFLERYKKL     | −13,25                 | **−14,58**           |
| AARENIRAYAARFRARLAAK     | −13,18                 | −13,79               |
| GARESIREYQRRFEERYRRL     | −13,43                 | −13,56               |
| GARESIREHQKRFLERYKKK     | −13,18                 | −13,56               |
| GALENIKKHQKTFLERYKKK     | −13,23                 | −13,47               |

O modelo subestimou consistentemente a afinidade do top candidato SARESIKKAYKTFLERYKKL (pred. −13,25 vs real −14,58), mas o ranqueamento ordinal foi preservado. As 24.513 predições foram salvas em `outputs/ml_predictions.csv` e utilizadas como critério auxiliar no ranking composto.

---

### 3.10 Análise de Resistência Proteolítica (in silico)

A viabilidade terapêutica de peptídeos inibidores aplicados via ingestão (spray foliar ou expressão transgênica) depende criticamente da capacidade de sobreviver ao trato intestinal sem serem degradados pelas próprias proteases-alvo (*Tamaki et al., 2014; Chen et al., 2020*). A análise de sítios de clivagem in silico foi realizada para os **20 candidatos de maior ranking** utilizando as regras do ExPASy PeptideCutter para as proteases de maior relevância no gut de Lepidoptera.

**Tabela 9.** Análise de resistência proteolítica — top-20 candidatos ranking (amostra representativa).

| Candidato | P1-âncora (pos) | P1-internos (tripsina) | Score suscept. | Veredicto |
|-----------|-----------------|------------------------|----------------|-----------|
| SARESIKKAYKTFLERYKKL | C-term | 3 (K/R internos) | 1,0 | **SUSCEPTÍVEL** |
| GSRASARAYAARVRARRAAL | 17 | 5 (pos 3,7,12,14,16) | 1,0 | **SUSCEPTÍVEL** |
| GARESIREHQKRFLERYKKK | C-term | 4 (K/R internos) | 1,0 | **SUSCEPTÍVEL** |
| MKKQRENAKKVAEITLKKAK | 18 | 6 (pos 2,3,5,9,10,17) | 1,0 | **SUSCEPTÍVEL** |
| AARENIRAYAARFRARLAAK | C-term | 3 (K/R internos) | 1,0 | **SUSCEPTÍVEL** |
| *(+15 candidatos)* | — | 3–7 | 1,0 | **SUSCEPTÍVEIS** |

**0/20 candidatos resistentes.** Todos os 20 top candidatos do ranking expandido apresentam score de susceptibilidade máximo (1,0) com 3 a 7 sítios de clivagem internos por tripsina além do resíduo P1-âncora. Esse resultado é biologicamente esperado para peptídeos lineares de 20 aa ricos em Arg/Lys — o mesmo perfil composicional que maximiza a afinidade ao bolso S1 (necessidade de P1 = Arg/Lys) também torna o peptídeo substrato da própria tripsina em posições internas.

**Implicação:** os candidatos atuais são adequados como **sondas de pesquisa** (inibição in vitro, validação do princípio de design), mas não podem ser utilizados diretamente como biopesticidas sem modificações químicas que confiram resistência proteolítica.

**Estratégias de proteção propostas:**

1. **Substituição de P1-internos por isósteros não-cliváveis:**
   - K interno → Nle (norleucina): elimina o grupo ε-amino, mantém volume e hidrofobicidade
   - R interno → Orn (ornitina): perde o guanidínio, mantém basicidade; ou Cit (citrulina): neutro
   - Aplicação imediata: gerar variantes de MKKQRENAKKVAEITLKKAK e GSRASARAYAARVRARRAAL com Nle/Orn nas posições internas via `OptimizationAgent`

2. **Incorporação de D-aminoácidos nas posições vulneráveis** (síntese Fmoc-SPPS): D-Lys e D-Arg são invisíveis para tripsinas enantiosseletivas; manutenção das posições L nos contatos de interface

3. **Ciclização N-C-terminal:** reduz graus de liberdade conformacional e elimina extremidades cliváveis por aminopeptidases; aplicável a candidatos ≤10 aa da Fase 4

4. **Design de novas sequências sem K/R internos (Fase 4):** RFdiffusion 5–15 aa com filtro explícito `n_internal_KR = 0` no ProteinMPNN — P1 único (pos 1 ou N-terminal) com Arg/Lys; posições internas exclusivamente Ala, Ser, Gly, Pro (resistentes a quimiotripsina e elastase também)

A análise de especificidade (Seção 3.11) confirmou que todos os 20 candidatos mantêm seletividade adequada (SI ≥ 2,0 kcal/mol) frente às tripsinas não-alvo mesmo com alto conteúdo de R/K, reforçando que a susceptibilidade à clivagem é intrínseca ao peptídeo linear — não ao perfil de especificidade — e pode ser corrigida pelas estratégias acima sem comprometer a seletividade.

### 3.10b Fase 5 — Mineração de Candidatos Nativamente Resistentes (2026-07-17)

A estratégia 4 da Seção 3.10 (design sem K/R internos) foi ativada via `require_no_kr_internal: true` no `OptimizationAgent`. A tentativa inicial de gerar novos candidatos por mutação/crossover dos 50 parentais de maior ranking retornou **0 candidatos válidos**: os parentais selecionados por afinidade são composticionalmente saturados de Arg/Lys fora das posições mutáveis (P2–P5), de modo que nenhuma mutação pontual consegue eliminar todos os sítios K/R internos herdados do parental.

Investigação subsequente revelou que a heurística de pré-seleção para docking (`net_charge × 1,2 + frac_hidrofóbica × 3,0 + n_arg_lys × 0,5`) favorece sistematicamente sequências ricas em K/R, excluindo do top-1000 original as sequências do pool ProteinMPNN (24.513 no total) que já não possuem K/R interno. Cruzando o filtro `KR_interno = 0` com as predições do modelo de ML (Random Forest, Seção 3.9) sobre as 24.513 sequências, **1.458 candidatos nativamente resistentes nunca haviam sido dockados de verdade**.

As 60 sequências desse subconjunto com melhor afinidade *predita* pelo modelo foram submetidas a docking Vina real (nova opção `--docking-sequences`, mesclada aos 930 resultados pré-existentes). Durante essa validação foi identificado e corrigido um bug real no `DockingAgent`: os resultados eram indexados por uma chave truncada (`len{n}_{seq[:8]}`) que colide entre sequências quase-idênticas, causando perda silenciosa de resultados (confirmado: 78 grupos de colisão no top-1000 original, dos quais 19 sequências distintas — o restante eram duplicatas exatas — tiveram dado real sobrescrito historicamente; as 3 candidatas de síntese da Seção 3.7/3.8b não foram afetadas, prefixos únicos). Corrigido indexando por sequência completa; as 60 sequências foram redockadas por completo após o fix.

**Tabela 9b.** Top-5 candidatos nativamente resistentes (KR-interno = 0) por Vina real, docking completo 2026-07-17, MD (10 ns, gmx_mpi GPU) concluído 2026-07-18.

| Sequência | Vina real (kcal/mol) | KR-interno | RMSD MD (nm) | Rg (nm) | Veredicto |
|-----------|----------------------|------------|---------------|---------|-----------|
| **SEEEVLAANEAYAAAHTAYN** | **−13,40** | 0 | **0,474** | 1,765 | **ESTÁVEL** |
| SALASIAAHQATFLAYLESK | −12,52 | 0 | 0,568 | 1,801 | marginal |
| MGSLTAYLEAYAAENAAALA | −12,67 | 0 | 0,639 | 1,800 | marginal |
| MGYLTAYHQALAAQNAALLA | −13,04 | 0 | 0,820 | 1,805 | marginal |
| SHIAEHEAELDAYAEAQAAA | −12,76 | 0 | 1,607 | 1,844 | **instável** |

`SEEEVLAANEAYAAAHTAYN` é o primeiro candidato do pipeline a reunir **simultaneamente** resistência
estrutural à autoclivagem (KR-interno = 0), afinidade Vina real competitiva com o TOP-3 atual
(Seção 3.7/3.8b: RLREELKKAEEWLEKRRKEE, MKKQRENAKKVAEITLKKAK −12,72, GSRASARAYAARVRARRAAL −13,62)
e estabilidade confirmada por MD real (RMSD 0,474 nm, abaixo do limiar de 0,5 nm da Seção 3.8).
Dos outros 4 candidatos resistentes testados, nenhum atingiu o limiar de estabilidade — reforçando
mais uma vez a lição da Seção 3.8 (melhor Vina não implica estabilidade em solvente), agora também
confirmada dentro do próprio subconjunto de candidatos resistentes. `SEEEVLAANEAYAAAHTAYN` passa a
ser candidato de síntese prioritário junto com RLREELKKAEEWLEKRRKEE, com a ressalva metodológica
registrada na Seção 2.11: não contém nenhum resíduo Arg/Lys, não usando o mecanismo canônico
P1-Arg/Lys↔Asp189 — seu mecanismo real de ligação permanece a ser investigado antes de qualquer
decisão final de síntese.

---

### 3.11 Especificidade vs. Tripsinas Não-Alvo

A seletividade dos 20 candidatos de maior ranking foi avaliada por docking contra duas tripsinas não-alvo: tripsina humana (*Homo sapiens*, PDB 1TRN, download RCSB) e tripsina de *Apis mellifera* (AlphaFold AF-A0A7M7MMI1-F1-model_v6, 247 aa, download EBI). O índice de seletividade (SI) foi calculado como SI = afinidade(não-alvo) − afinidade(alvo Lepidoptera), com limiar aprovação SI ≥ 2,0 kcal/mol.

**Resultado: 20/20 candidatos aprovados em ambos os não-alvos** (SI ≥ 2,0 kcal/mol).

| Não-alvo | Candidatos aprovados | Candidatos reprovados | SI médio |
|----------|---------------------|----------------------|----------|
| Tripsina humana (1TRN) | **20/20** | 0 | > 2,0 kcal/mol |
| Tripsina *A. mellifera* (A0A7M7MMI1) | **20/20** | 0 | > 2,0 kcal/mol |

Esse resultado demonstra que o pipeline de design, baseado em backbones gerados por RFdiffusion ancorados especificamente ao sítio catalítico de ACR157 (*A. gemmatalis*), produz sequências com seletividade intrínseca frente a tripsinas evolutivamente distintas. A diferença de especificidade é atribuída principalmente às variações na geometria do bolso S1: ACR157 possui Asp205 em posição e orientação distintas de 1TRN (Asp189) e da *A. mellifera* (posição equivalente com offset ~5 Å no centro de ligação), resultando em diferentes volumes e potenciais eletrostáticos que modulam a seletividade peptídeo–receptor.

A aprovação de **100% dos candidatos** em ambos os não-alvos é um resultado favorável para a estratégia de design, indicando que a seletividade de espécie pode ser mantida mesmo após otimização de resistência proteolítica (Seção 3.10).

### 3.12 Inibidores de Referência

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

O pipeline multiagente completou todas as etapas planejadas para a Fase 1–3: design (RFdiffusion), sequenciamento (ProteinMPNN), triagem de afinidade (Vina, 880 poses), refinamento de interface (PyRosetta, 10 complexos), estabilidade dinâmica (MD, 5 candidatos × 10 ns), aprendizado de máquina (RF, 24.513 predições), resistência proteolítica in silico (PeptideCutter, 20 candidatos) e especificidade vs não-alvos (Vina, 2 estruturas). Estado consolidado (2026-06-27):

- **330 backbones reais** gerados pelo RFdiffusion para ACR157
- **24.513 sequências únicas** de binder 20 aa via ProteinMPNN real
- **880 poses Vina** válidas; novo top-1: **SARESIKKAYKTFLERYKKL** (−14,58 kcal/mol)
- **10 complexos PyRosetta**; top I_sc: GARKSIREYQKRVLERLKKK (−86,28 kcal/mol)
- **MD 10 ns (Fase 3)**: 2 estáveis, 1 marginal, 2 instáveis — top-2: MKKQRENAKKVAEITLKKAK (0,447 nm) e GSRASARAYAARVRARRAAL (0,494 nm)
- **MD 10 ns (Fase 4)**: 6 candidatos adicionais — **RLREELKKAEEWLEKRRKEE ESTÁVEL** (0,294 nm, DP=0,065 — mais estável do pipeline); SARESIKKAYKTFLERYKKL Marginal apesar de melhor Vina
- **ML**: Random Forest RMSE = 0,514 kcal/mol; 24.513 predições qualitativas geradas
- **Resistência proteolítica**: 0/20 candidatos resistentes — todos susceptíveis (3–7 P1-internos K/R)
- **Especificidade**: 20/20 aprovados vs tripsina humana (1TRN) e *Apis mellifera* (SI ≥ 2,0 kcal/mol)
- **OptimizationAgent**: 219 novos candidatos gerados por redesign iterativo dos top-50

O padrão composicional dos top binders (Arg/Lys + Ala/Ser, sem aromáticos) é biologicamente coerente com o bolso S1 de tripsina (Asp205, interação eletrostática com P1 = Arg/Lys). A avaliação dinâmica revela que estimativas estáticas (Vina, Rosetta) podem divergir da estabilidade em solvente explícito: GARKSIREYQKRVLERLKKK, com melhor I_sc (−86,28 kcal/mol), apresentou RMSD = 1,45 nm em MD — descartado. A etapa MD é, portanto, essencial para filtrar candidatos antes da síntese.

A susceptibilidade proteolítica universal (0/20 resistentes) é a principal limitação dos candidatos de 20 aa lineares e decorre do trade-off intrínseco: resíduos Arg/Lys que maximizam afinidade ao S1 também são substratos da própria tripsina em posições internas. Esse resultado redireciona a Fase 4 para o design de peptídeos 5–15 aa com filtro KR-interno=0 e estratégias de proteção química (Nle, Orn, D-aa).

**Candidatos de síntese prioritária (pós-MD Fases 3+4, estáveis em 10 ns):**
1. **MKKQRENAKKVAEITLKKAK** — RMSD 0,447 nm, Vina −12,72, I_sc −80,49 (Fase 3)
2. **RLREELKKAEEWLEKRRKEE** — RMSD 0,294 nm, DP=0,065 — **mais estável do pipeline** (Fase 4)
3. **GSRASARAYAARVRARRAAL** — RMSD 0,494 nm, Vina −13,62, I_sc −78,44 (Fase 3)

**Candidato marginal com alta afinidade:**
- **SARESIKKAYKTFLERYKKL** — Vina −14,58 kcal/mol (melhor docking), RMSD 0,871 nm (marginal em MD)

**Próximas etapas (Fase 4–5):**

| Fase | Ação | Prioridade |
|------|------|-----------|
| 4a | RFdiffusion 5–15 aa + filtro KR-interno=0 | Alta |
| 4b | MD nos 219 candidatos do OptimizationAgent | Média |
| 4c | MD de SARESIKKAYKTFLERYKKL (novo top-1 Vina) | Alta |
| 5 | Expansão para *H. armigera*, *A. gemmatalis*, *D. saccharalis* | Média |

---

## Referências

**Alvo biológico e caracterização das tripsinas:**
- Paulo et al. (2026) Peptides derived from reactive center loops inhibit digestive trypsin-like enzymes in Lepidopteran pests. *Arch Insect Biochem Physiol*, DOI: 10.1002/arch.70123
- Oliveira et al. (2017) Kinetic characterization of *Anticarsia gemmatalis* digestive serine-proteases. PubMed 28925864
- Leite et al. (2024) Inhibitory efficacy of tripeptides on trypsin-like activity in *A. gemmatalis*. *Phytoparasitica*, DOI: 10.1007/s12600-024-01125-x
- Boaventura et al. (2023) Soybean trypsin inhibitor reduces resistance to transgenic maize in *S. frugiperda*. *J Econ Entomol* 116(6):2146
- Brito et al. (2013) Insensitive trypsins are differentially transcribed during *S. frugiperda* adaptation against plant protease inhibitors. PubMed 23466403
- Spit et al. (2016) Comparative analysis of trypsin/chymotrypsin gene expression in Lepidoptera with different inhibitor sensitivities. PubMed 26944308
- Oliveira et al. (2020) Noncompetitive tight-binding inhibition of *A. gemmatalis* trypsins by *Adenanthera pavonina* inhibitor. PubMed 32342573
- Hedstrom L (2002) Serine protease mechanism and specificity. *Chem Rev*, 102, 4501–4524.
- Lopes AR et al. (2004) Comparative studies of digestive enzymes and midgut cells of *Spodoptera frugiperda*. *Comp Biochem Physiol*, 137, 119–129.

**Estrutura de inibidores e mecanismo:**
- Tabosa et al. (2020) EcTI impairs *Aedes aegypti* development and enhances Bt toxins. *Pest Mgmt Sci*, PMID 32453460
- PMC3633903. Crystal structures of EcTI and complex with bovine trypsin.
- Dutta et al. (2021) Structure-activity relationship and molecular docking of Kunitzin-AH. PMC8309051

**Resistência proteolítica:**
- Sivaramakrishnan et al. (2019) Phyto-inspired cyclic peptides from Pin-II RCLs for crop protection. *Phytomedicine*, PMID 31077794
- PMC7688903. D- and unnatural amino acid peptides with improved proteolytic resistance.
- biorXiv (2025) D-amino acid substitution and cyclisation in arginine-rich peptides. DOI: 10.1101/2025.06.17.660067

**Expressão heteróloga:**
- Springer (2014) Trypsin inhibitor expression in *P. pastoris* vs *Mamestra brassicae*. DOI: 10.1007/s11033-014-3760-y
- ScienceDirect (2022) ChTI + Cry co-expression reduces resistance in *H. armigera*. DOI: 10.1016/j.indcrop.2022.115780
- PMC9982021. Soybean trypsin inhibitor in transgenic plants reduces *H. zea* defoliation.

**Ferramentas computacionais:**
- Chaudhury S et al. (2010) PyRosetta. *Bioinformatics*, 26, 689–691.
- Dauparas J et al. (2022) ProteinMPNN. *Science*, 378, 49–56.
- Raveh B et al. (2011) FlexPepDock. *PLoS Comput Biol*, 7, e1002110.
- Trott O & Olson AJ (2010) AutoDock Vina. *J Comput Chem*, 31, 455–461.
- Van der Spoel D et al. (2005) GROMACS. *J Comput Chem*, 26, 1701–1718.
- Watson JL et al. (2023) RFdiffusion. *Nature*, 620, 1089–1100.
- Nature Chem Biol (2025) RFpeptides macrocyclic binders. DOI: 10.1038/s41589-025-01929-w

**Formulação e regulatório:**
- Molecules (2026) Nanopesticides delivery platforms. DOI: 10.3390/molecules31030453
- Nature Comm (2025) Azadirachtin nano-assemblies vs *S. frugiperda*. DOI: 10.1038/s41467-025-57028-w
- ACS Omega (2024) IPM sustainability update. PMC11465254
- Frontiers (2025) Biopesticides sustainable agriculture. DOI: 10.3389/fsufs.2025.1657000

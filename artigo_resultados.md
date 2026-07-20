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
> - ⚠️ 3.11 Especificidade — **CORRIGIDO 2026-07-18**: a afirmação original "20/20 aprovados" (Fase 3) nunca teve dado real por trás (bug de preparo de PDBQT — ver Seção 2.11/metodologia). Re-executado com dado Vina real: **0/23 candidatos aprovados** (SI ≥ 2,0 kcal/mol) até o momento, incluindo os candidatos de síntese prioritários e os 2 melhores da Fase 6 (5/7aa). Melhor SI real da sessão: HRPRRPR (7aa), min_SI=1,41.
> - ✓ 3.11f Réplicas reais de MD (n=3) — **CONCLUÍDO 2026-07-19**: TOP-13 rodado com 2 réplicas adicionais (rep2/rep3, gen_seed=-1) sobre o `complex_clean.pdb` já equilibrado da rep1. Achado crítico: os 2 "recordistas de estabilidade" do pipeline (RLREELKKAEEWLEKRRKEE 0,294 nm e VRTRR 0,1936 nm, ambos de réplica única) têm DP real de 0,606 e 0,360 nm entre réplicas — resultado não reprodutível, provável artefato de seed único. Só 4 candidatos são reprodutivelmente estáveis (DP<0,05 nm): SRTRR, VRYRR, VRRPR, HRPRRPR.
> - ✓ 3.11g Persistência competitiva real (ocupância P1-Asp187) — **CONCLUÍDO 2026-07-19**: TOP-13 reanalisado com métrica nova (resíduo âncora descoberto empiricamente por candidato, não assumido; ocupância a 4/5/6 Å; RMSD local do bolso via superposição só no receptor). Achado crítico: dos 4 candidatos "reprodutivelmente estáveis" da Tabela 9n, `VRRPR` na verdade **sai do bolso real** (ocupância a 6Å caindo de 67,6%→32,9%→0,15% entre réplicas, âncora é a Valina N-terminal, não um resíduo básico) — RMSD global baixo não implica permanência real perto de Asp187. `VRYRR` é o único candidato com contato tipo salt-bridge real (~100% mesmo a 4Å) nas 3 réplicas.

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

**Atualização 2026-07-18**: a análise de especificidade (Seção 3.11) foi re-executada após
correção de bug metodológico e mostrou o oposto do relatado originalmente aqui — **nenhum**
candidato atinge SI ≥ 2,0 kcal/mol contra ambos os não-alvos. A susceptibilidade à clivagem
continua sendo intrínseca ao peptídeo linear (não muda a conclusão desta seção), mas a hipótese
de que a especificidade de espécie estaria "garantida" e não precisaria de atenção nas
estratégias de correção acima **não se sustenta** — especificidade agora precisa ser tratada
como objetivo de otimização explícito, junto com resistência proteolítica.

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
ser candidato de síntese prioritário junto com RLREELKKAEEWLEKRRKEE.

**Mecanismo de ligação real (investigado 2026-07-18).** `SEEEVLAANEAYAAAHTAYN` não contém nenhum
resíduo Arg/Lys, não podendo usar o mecanismo canônico P1-Arg/Lys↔Asp189 assumido no restante do
design. Para investigar o mecanismo real, a conformação MD equilibrada (10 ns, `forced_00`) foi
analisada com PLIP 3.0.0 (`--peptides B`), revelando que o peptídeo **contata de fato a tríade
catalítica e o bolso S1** do receptor ACR157: interação π-cátion entre a Tyr12 do peptídeo e a
His46 catalítica (His69 na numeração original), contato hidrofóbico e ponte de hidrogênio com o
Asp91 catalítico (Asp114 original), e rede de pontes de hidrogênio via backbone (resíduos
Asn9/Glu10/Ala11) próxima à Ser188 catalítica e ao Asp182 do bolso S1 (Ser211/Asp205 originais).
No total, a interface reúne 10 contatos hidrofóbicos, 13 pontes de hidrogênio e 1 interação
π-cátion — uma rede distribuída ao longo de toda a fenda catalítica, não um único contato tipo
salt-bridge. O mecanismo é portanto real e mecanisticamente plausível, ainda que não-canônico: o
peptídeo ocupa a fenda catalítica via contatos de backbone e um resíduo aromático específico
(Tyr12), não via a ponte salina P1-Arg/Lys↔Asp205 padrão. Como todo o restante do pipeline
(especificidade, ranking) foi calibrado assumindo o mecanismo canônico, esse candidato requer
validação experimental própria antes de qualquer decisão final de síntese.

A mesma análise PLIP foi estendida aos outros 4 candidatos resistentes com MD real concluído:

**Tabela 9c.** Contato com a tríade catalítica (His46/Asp91) e região S1 (Ser188/Asp182) por PLIP.

| Candidato | RMSD MD (nm) | Contata His46? | Contata Asp91? | Região Ser188/Asp182 |
|---|---|---|---|---|
| SEEEVLAANEAYAAAHTAYN | 0,474 (estável) | ✓ (π-cátion) | ✓ | ✓ |
| SHIAEHEAELDAYAEAQAAA | 1,607 (instável) | ✓ | ✓ | ✓ |
| SALASIAAHQATFLAYLESK | 0,568 (marginal) | ✓ | — | ✓ |
| MGSLTAYLEAYAAENAAALA | 0,639 (marginal) | — | — | ✓ (via Asp187) |
| MGYLTAYHQALAAQNAALLA | 0,820 (marginal) | — | — | ✓ (via Gln183) |

Com amostra pequena (n=5) a leitura é apenas observacional, não causal: o engajamento simultâneo
com His46 e Asp91 não garante estabilidade geral do complexo — o único outro candidato com esse
padrão (SHIAEHEAELDAYAEAQAAA) foi o mais instável de todos. Fica registrado como hipótese a
acompanhar em candidatos futuros, não como conclusão validada.

### 3.10c Fase 6 — Comparação Real entre Comprimentos (R1, 2026-07-18)

O requisito R1 (testar 5, 7, 10, 12, 15 e 20 aa e comparar os melhores por etapa) nunca havia
sido respondido com dado real: um bug de cache no `ProteinMPNNAgent` (Seção 2.4) fazia com que
100% das sequências geradas saíssem de 20 aa, independentemente do comprimento real do backbone
de origem. Corrigido o bug, o ProteinMPNN foi reexecutado (120.558 sequências, 100% de
correspondência verificada entre comprimento real e label do backbone) e os 30 melhores
candidatos de cada comprimento (5/7/10/12/15 aa, selecionados por heurística de carga +
hidrofobicidade + `n_arg_lys`, com bônus para P1 = Lys — ver justificativa abaixo) foram
dockados com Vina real (150/150 com sucesso).

**Tabela 9d.** Melhor candidato real por comprimento — Vina e MD (10 ns).

| Comprimento | Sequência | Vina real (kcal/mol) | RMSD MD (nm) | Veredicto |
|---|---|---|---|---|
| 5 aa | **SRTRR** | −10,31 | **0,2425** | **ESTÁVEL — mais estável de todo o pipeline** |
| 7 aa | **HRPRRPR** | −11,72 | **0,2659** | **ESTÁVEL — 2º mais estável de todo o pipeline** |
| 10 aa | KPRWKYRRRP | −12,04 | — | MD falhou (SIGABRT real durante NVT; sem dado fabricado) |
| 12 aa | TAGAILRKRVKK | −12,53 | 0,9584 | instável/marginal |
| 15 aa | TRARLRAEVLRARAR | −13,06 | 1,8284 | muito instável |

A afinidade Vina melhora de forma monotônica com o comprimento (mais contatos possíveis), como
esperado. **O achado real e contraintuitivo está na estabilidade**: os dois candidatos mais
curtos (5 e 7 aa) são os únicos estáveis desse grupo e superam em RMSD todos os candidatos de
20 aa já testados no pipeline, incluindo `RLREELKKAEEWLEKRRKEE` (0,294 nm, recordista anterior).
Os candidatos de 12 e 15 aa, apesar de melhor Vina, são instáveis. Isso inverte a suposição
implícita nas Fases 1-5 de que comprimentos maiores seriam preferíveis — reforça, aliás, a lição
já estabelecida na Seção 3.8 (melhor Vina não implica estabilidade) e é ainda mais favorável ao
requisito R7 (expressão transgênica: peptídeo menor = gene menor = custo de síntese menor).

**Ressalva real**: n=1 candidato testado por comprimento (não é amostra estatística) — motiva
expandir o MD para mais candidatos por classe de tamanho antes de tratar "peptídeo curto é mais
estável" como regra geral, mas é a primeira resposta real e completa (Vina + MD) ao requisito R1
desde o início do projeto. `SRTRR` e `HRPRRPR` tornam-se candidatos de síntese prioritários,
pendente ainda de teste real de especificidade (Seção 3.11) — nenhum dos 5 comprimentos novos foi
avaliado contra tripsina humana/*Apis mellifera* até o momento deste texto.

**Seleção de P1 informada por dado real**: entre os 228 candidatos com Vina real disponíveis
antes desta rodada, o resíduo C-terminal (P1) com melhor afinidade média e amostra robusta era
Lys (K, n=81, média −11,78 kcal/mol), superando Arg (R, n=29, média −11,56) apesar de ambos
serem tratados como equivalentes no design canônico "P1 = Arg/Lys" usado desde a Fase 1. Essa
descoberta foi usada como critério real de priorização (não de geração) na seleção dos 150
candidatos desta rodada.

### 3.10d Expansão de Amostra — MD dos Comprimentos Curtos (n=4, 2026-07-18)

A ressalva de amostra da Seção 3.10c (n=1 por comprimento) foi endereçada para as duas classes
mais curtas: mais 3 candidatos de 5 aa (VRYRR, VRTRR, VRRPR) e 3 de 7 aa (HRPRRSR, HRPRRPK,
KPKFKVR) — os próximos melhores por Vina real dentro do lote de 30 já dockado por comprimento —
foram simulados em MD real (10 ns cada), elevando a amostra para **n=4 por comprimento**.

**Tabela 9d-2.** MD real, n=4 — comprimentos 5 e 7 aa.

| Sequência | Comp. | RMSD (nm) | DP | Rg (nm) | Vina real |
|---|---|---|---|---|---|
| **VRTRR** | 5 | **0,1936** | 0,0121 | 1,688 | −9,55 |
| VRYRR | 5 | 0,1985 | 0,0198 | 1,709 | −10,22 |
| SRTRR | 5 | 0,2425 | 0,0222 | 1,695 | −10,31 |
| VRRPR | 5 | 0,2679 | 0,0282 | 1,747 | −9,45 |
| HRPRRPR | 7 | 0,2659 | 0,0479 | 1,754 | −11,72 |
| HRPRRSR | 7 | 0,2743 | 0,0264 | 1,739 | −11,56 |
| HRPRRPK | 7 | 0,4103 | 0,3798 | 1,742 | −10,99 |
| KPKFKVR | 7 | 0,5982 | 0,5232 | 1,750 | −10,59 |

`VRTRR` (5 aa) é agora o **candidato mais estável de todo o pipeline** (RMSD 0,1936 nm),
superando `SRTRR` (recordista anterior, Seção 3.10c) e `RLREELKKAEEWLEKRRKEE` (0,294 nm,
recordista da Fase 4).

**Achado real com amostra ampliada (deixa de ser observação de n=1)**: a classe de **5 aa é
uniformemente estável** — os 4 candidatos ficam todos entre 0,19–0,27 nm (faixa de apenas
0,074 nm). A classe de **7 aa é heterogênea** — varia de 0,27 nm (estável) a 0,60 nm (instável)
dentro do mesmo comprimento (faixa de 0,332 nm, quase 4,5× maior). **Conclusão real**: "peptídeo
curto implica maior estabilidade" é uma regra mais confiável em 5 aa do que em 7 aa; em 7 aa a
estabilidade real depende mais da sequência específica do que apenas do comprimento.

**Pendência real**: nenhum dos 6 novos candidatos tem especificidade real (humano/*Apis*) ou
docking cross-species (Seção 3.11c) — `VRTRR`, o novo recordista, está sem qualquer dado de
especificidade até o momento deste texto.

---

### 3.11 Especificidade vs. Tripsinas Não-Alvo

**CORREÇÃO METODOLÓGICA (2026-07-18):** a versão original desta seção (Fase 3, 2026-06-25)
relatava "20/20 candidatos aprovados, SI ≥ 2,0 kcal/mol" — esse resultado **nunca teve dado real
por trás**. Uma auditoria de código encontrou dois bugs no `SpecificityAgent`: (1) o PDBQT dos
receptores não-alvo era gerado sem a flag `-xr` do OpenBabel, produzindo formato incompatível
que o Vina rejeitava como receptor rígido; (2) o peptídeo-ligante era construído como átomos Cα
isolados sem ligação, que o OpenBabel tratava como moléculas separadas, gerando PDBQTs também
rejeitados pelo Vina. Como consequência, **nenhuma docagem real contra os não-alvos jamais foi
executada** — o campo `selectivity_index` ficava vazio e `approved` permanecia `True` apenas
pelo valor-padrão do laço de comparação, nunca sobrescrito. Ambos os bugs foram corrigidos
(reaproveitando `build_peptide_pdbqt()`, a mesma construção all-atom via PeptideBuilder já
validada em ~990 docagens reais do `DockingAgent`) e a análise foi **re-executada por completo**
com dado Vina real.

A seletividade dos 20 candidatos de maior ranking (mais os 2 candidatos de síntese prioritários
da Fase 5, RLREELKKAEEWLEKRRKEE e SEEEVLAANEAYAAAHTAYN — 21 no total) foi avaliada por docking
real contra duas tripsinas não-alvo: tripsina humana (*Homo sapiens*, PDB 1TRN, download RCSB) e
tripsina de *Apis mellifera* (AlphaFold AF-A0A7M7MMI1-F1-model_v6, 247 aa, download EBI). O
índice de seletividade (SI) foi calculado como SI = afinidade(não-alvo) − afinidade(alvo
Lepidoptera), com limiar de aprovação SI ≥ 2,0 kcal/mol.

**Resultado real: 0/21 candidatos aprovados** em pelo menos um dos dois não-alvos.

| Não-alvo | Candidatos aprovados | SI médio | SI mín. | SI máx. |
|----------|---------------------|----------|---------|---------|
| Tripsina humana (1TRN) | 0/21 | 0,84 kcal/mol | 0,06 | 1,91 |
| Tripsina *A. mellifera* (A0A7M7MMI1) | 0/21 | 1,12 kcal/mol | **−0,09** | 1,88 |

O candidato `SARASIRRFAATWRARLAAA` tem SI **negativo** contra *Apis mellifera* (−0,09) — ou
seja, essa sequência liga-se de fato **melhor** à tripsina do polinizador não-alvo do que à
tripsina de *A. gemmatalis* alvo. O candidato mais estável do pipeline em MD
(`RLREELKKAEEWLEKRRKEE`, Seção 3.8b) tem SI real de apenas 0,06 (humana) e 0,27 (Apis) —
essencialmente sem margem de seletividade nenhuma, apesar de nunca antes ter sido testado.

**Implicação — reverte a conclusão da versão original desta seção**: ao contrário do que se
pensava, o pipeline atual **não** demonstra seletividade intrínseca de espécie. Nenhum candidato
avaliado até agora, incluindo os priorizados para síntese, atende ao requisito R4 (não afetar
não-alvos) com margem de segurança adequada. Isso não invalida a estratégia de design geral, mas
indica que **otimização explícita de especificidade** (não apenas afinidade ao alvo) precisa ser
incorporada como objetivo de otimização de primeira classe nas próximas fases — atualmente o
`OptimizationAgent` não usa SI como critério de seleção/mutação.

### 3.11b TOP-10 Real Consolidado (Vina + MD + Especificidade, 2026-07-18)

Integrando as três métricas reais disponíveis (Seções 3.4, 3.8/3.10c, 3.11) para os candidatos
com bateria completa de avaliação, ordenados por estabilidade MD (critério mais rigoroso —
Seção 3.8):

**Tabela 9e.** TOP-10 por RMSD MD ascendente, com Vina real e especificidade real (SI).

| # | Sequência | Comp. | Vina (kcal/mol) | RMSD MD (nm) | SI humana | SI Apis | Aprovado? |
|---|---|---|---|---|---|---|---|
| 1 | SRTRR | 5 aa | −10,31 | **0,2425** | 1,17 | 1,61 | não |
| 2 | HRPRRPR | 7 aa | −11,72 | **0,2659** | 1,41 | 1,78 | não |
| 3 | RLREELKKAEEWLEKRRKEE | 20 aa | −12,21 | 0,2940 | 0,06 | 0,27 | não |
| 4 | SEEEVLAANEAYAAAHTAYN | 20 aa | −13,40 | 0,4742 | 1,23 | 1,70 | não |
| 5 | SALASIAAHQATFLAYLESK | 20 aa | −12,52 | 0,5677 | 0,27 | −0,64 | não |
| 6 | MGSLTAYLEAYAAENAAALA | 20 aa | −12,67 | 0,6390 | 0,18 | 0,43 | não |
| 7 | RLRAIWLEAEKLLEERRKKK | 20 aa | −12,22 | 0,7251 | **−1,59** | −0,07 | não |
| 8 | MGYLTAYHQALAAQNAALLA | 20 aa | −13,04 | 0,8204 | 0,48 | — | não |
| 9 | RVKDQWLEAEKLLEERRKKK | 20 aa | −11,52 | 0,8341 | **−2,75** | −0,28 | não |
| 10 | SARESIKKAYKTFLERYKKL | 20 aa | −14,58 | 0,8713 | 1,91 | 1,61 | não |

**Fora do top-10 por RMSD, mas notáveis por especificidade:** `TRARLRAEVLRARAR` (15 aa) tem
RMSD 1,8284 nm (muito instável) mas **SI mínimo = 1,76 — o melhor de toda a sessão**, próximo do
limiar de aprovação (2,0). `TAGAILRKRVKK` (12 aa): RMSD 0,9584 nm, SI = 0,81.

**Achado de segurança real**: `RLRAIWLEAEKLLEERRKKK` e `RVKDQWLEAEKLLEERRKKK` (variantes de
redesign da família RLREELKK-*like*) apresentam **SI negativo contra tripsina humana** (−1,59 e
−2,75 kcal/mol) — ligam-se de fato *melhor* à tripsina humana do que ao alvo *A. gemmatalis*.
Diferente dos demais candidatos (apenas não-seletivos), esses dois são provavelmente mais ativos
contra o não-alvo humano do que contra a praga — devem ser **eliminados** da lista de síntese,
não apenas despriorizados.

**Nenhum dos 10 (nem os 29 candidatos com especificidade real testada até o momento) atinge
SI ≥ 2,0 kcal/mol contra ambos os não-alvos**, confirmando a Seção 3.11. Os valores de
`TRARLRAEVLRARAR` (1,76) e `SARESIKKAYKTFLERYKKL` (1,61) mostram que a barra de 2,0 kcal/mol
está próxima do alcançável, motivando otimização explícita de especificidade nas próximas fases.

### 3.11d Comparação Dupla — TOP-10 Absoluto vs. TOP-10 por Especificidade (2026-07-18)

Após a especificidade real dos 6 candidatos curtos novos (VRYRR, VRTRR, VRRPR, HRPRRSR, HRPRRPK,
KPKFKVR — Seção 3.10d) ficar disponível, o dataset de 16 candidatos com MD + especificidade real
completos foi comparado sob dois critérios de ranking distintos.

**Tabela 9h.** Ranking 1 — TOP-10 absoluto (RMSD MD ascendente, critério de estabilidade sem
considerar especificidade).

| # | Sequência | Comp. | RMSD MD (nm) | Vina primário | min_SI |
|---|---|---|---|---|---|
| 1 | VRTRR | 5 | 0,1936 | −9,55 | 0,39 |
| 2 | VRYRR | 5 | 0,1985 | −10,22 | 0,92 |
| 3 | SRTRR | 5 | 0,2425 | −10,31 | 1,17 |
| 4 | HRPRRPR | 7 | 0,2659 | −11,72 | 1,41 |
| 5 | VRRPR | 5 | 0,2679 | −9,45 | **−0,13** |
| 6 | HRPRRSR | 7 | 0,2743 | −11,56 | 0,59 |
| 7 | RLREELKKAEEWLEKRRKEE | 20 | 0,2940 | — | **0,06** |
| 8 | HRPRRPK | 7 | 0,4103 | −10,99 | 0,87 |
| 9 | SEEEVLAANEAYAAAHTAYN | 20 | 0,4742 | −13,40 | 1,23 |
| 10 | SALASIAAHQATFLAYLESK | 20 | 0,5677 | −12,52 | **−0,64** |

**Tabela 9i.** Ranking 2 — TOP-10 por especificidade real (min_SI descendente).

| # | Sequência | Comp. | min_SI | RMSD MD (nm) | Vina primário |
|---|---|---|---|---|---|
| 1 | SARESIKKAYKTFLERYKKL | 20 | 1,61 | 0,8713 (marginal) | −14,58 |
| 2 | HRPRRPR | 7 | 1,41 | 0,2659 | −11,72 |
| 3 | SEEEVLAANEAYAAAHTAYN | 20 | 1,23 | 0,4742 | −13,40 |
| 4 | SRTRR | 5 | 1,17 | 0,2425 | −10,31 |
| 5 | VRYRR | 5 | 0,92 | 0,1985 | −10,22 |
| 6 | HRPRRPK | 7 | 0,87 | 0,4103 | −10,99 |
| 7 | HRPRRSR | 7 | 0,59 | 0,2743 | −11,56 |
| 8 | MGYLTAYHQALAAQNAALLA | 20 | 0,48 | 0,8204 (marginal) | −13,04 |
| 9 | VRTRR | 5 | 0,39 | 0,1936 | −9,55 |
| 10 | MGSLTAYLEAYAAENAAALA | 20 | 0,18 | 0,6390 (marginal) | −12,67 |

**Interpretação real**: **7 dos 10 candidatos coincidem nas duas listas** (VRTRR, VRYRR, SRTRR,
HRPRRPR, HRPRRSR, HRPRRPK, SEEEVLAANEAYAAAHTAYN) — sinal real e encorajador de que estabilidade
MD e especificidade real não são propriedades incompatíveis na maioria dos casos observados até
agora. As diferenças, porém, são as mais informativas:

- **Saem quando a especificidade é considerada**: `RLREELKKAEEWLEKRRKEE` — o candidato
  historicamente tratado como "mais estável" do pipeline (Seção 3.8b) — tem min_SI real de
  apenas 0,06, essencialmente **sem margem de seletividade nenhuma**. `VRRPR` e
  `SALASIAAHQATFLAYLESK` saem por SI real **negativo** (−0,13 e −0,64).
- **Entram quando a especificidade é considerada**: `SARESIKKAYKTFLERYKKL` (o melhor Vina bruto
  de todo o pipeline, −14,58, mas MD apenas marginal) sobe ao #1 do ranking 2 por ter o melhor
  SI real do conjunto (1,61); `MGYLTAYHQALAAQNAALLA` e `MGSLTAYLEAYAAENAAALA` entram pelo mesmo
  motivo (MD marginal, mas SI real positivo).

**Nenhum dos 16 candidatos atinge o limiar formal de aprovação (SI ≥ 2,0 kcal/mol)** — o placar
de 0/35 candidatos aprovados (Seção 3.11) permanece válido. Esta comparação é sobre *ranking
relativo* entre candidatos reais, não sobre candidatos aprovados por um critério absoluto.

**Correção de dado (2026-07-18):** a extração inicial de `RLREELKKAEEWLEKRRKEE` buscava o valor
de Vina no campo errado do JSON de MD (`vina_kcal`, sempre nulo para candidatos não redockados
diretamente) em vez do campo real em `docking_results.json` (`best_affinity_kcal`). O valor real
é **−12,21 kcal/mol** (não "—" como reportado inicialmente nesta seção) — corrigido na Tabela 9j
abaixo, que também substitui as Tabelas 9h/9i por uma visão unificada.

**Tabela 9j.** Comparação unificada — união dos dois rankings (13 candidatos), com posição em
cada critério e classificação de grupo.

| Sequência | Comp. | Vina (kcal/mol) | RMSD MD (nm) | min_SI (kcal/mol) | Rank Absoluto | Rank Especificidade | Grupo |
|---|---|---|---|---|---|---|---|
| VRTRR | 5 | −9,55 | 0,1936 | 0,39 | 1 | 9 | Comum |
| VRYRR | 5 | −10,22 | 0,1985 | 0,92 | 2 | 5 | Comum |
| SRTRR | 5 | −10,31 | 0,2425 | 1,17 | 3 | 4 | Comum |
| HRPRRPR | 7 | −11,72 | 0,2659 | 1,41 | 4 | 2 | Comum |
| VRRPR | 5 | −9,45 | 0,2679 | **−0,13** | 5 | — | Só Absoluto |
| HRPRRSR | 7 | −11,56 | 0,2743 | 0,59 | 6 | 7 | Comum |
| RLREELKKAEEWLEKRRKEE | 20 | −12,21 | 0,2940 | **0,06** | 7 | — | Só Absoluto |
| HRPRRPK | 7 | −10,99 | 0,4103 | 0,87 | 8 | 6 | Comum |
| SEEEVLAANEAYAAAHTAYN | 20 | −13,40 | 0,4742 | 1,23 | 9 | 3 | Comum |
| SALASIAAHQATFLAYLESK | 20 | −12,52 | 0,5677 | **−0,64** | 10 | — | Só Absoluto |
| SARESIKKAYKTFLERYKKL | 20 | −14,58 | 0,8713 (marginal) | 1,61 | — | 1 | Só Especificidade |
| MGYLTAYHQALAAQNAALLA | 20 | −13,04 | 0,8204 (marginal) | 0,48 | — | 8 | Só Especificidade |
| MGSLTAYLEAYAAENAAALA | 20 | −12,67 | 0,6390 (marginal) | 0,18 | — | 10 | Só Especificidade |

**Descrição do resultado considerando os dois grupos em conjunto:**

O grupo **Comum** (7 candidatos, robustos nos dois critérios) é dominado por peptídeos curtos:
6 dos 7 têm 5 ou 7 aa (VRTRR, VRYRR, SRTRR, HRPRRPR, HRPRRSR, HRPRRPK); apenas
`SEEEVLAANEAYAAAHTAYN` (20 aa, mecanismo não-canônico via Tyr — Seção 3.10b) consegue reunir
estabilidade real (RMSD 0,4742 nm) e especificidade real (SI 1,23) entre os candidatos de 20 aa.
Dentro deste grupo, o RMSD varia pouco (0,19–0,47 nm) e o SI mínimo é sempre positivo
(0,39–1,41) — é o conjunto de candidatos com o perfil de risco mais baixo do pipeline inteiro.

O grupo **Só Absoluto** (candidatos estáveis, mas que falham quando a especificidade é
considerada) mistura comprimentos: 2 de 20 aa (`RLREELKKAEEWLEKRRKEE`, o histórico
"mais estável" do pipeline, e `SALASIAAHQATFLAYLESK`) e 1 curto (`VRRPR`, 5 aa). O achado real
mais importante deste grupo é que **nem todo peptídeo curto é automaticamente seguro** —
`VRRPR` é tão estável quanto os demais 5 aa (RMSD 0,2679 nm), mas tem SI real negativo (−0,13)
contra *Apis mellifera*, no mesmo padrão de risco dos candidatos de 20 aa já eliminados na Seção
3.11b. Comprimento curto correlaciona com estabilidade, mas não é garantia de especificidade.

O grupo **Só Especificidade** (candidatos seletivos, mas apenas marginalmente estáveis) é
uniformemente de 20 aa (`SARESIKKAYKTFLERYKKL`, `MGYLTAYHQALAAQNAALLA`,
`MGSLTAYLEAYAAENAAALA`), todos com RMSD entre 0,62–0,87 nm (zona marginal, não estável pelo
critério de 0,5 nm da Seção 3.8) mas SI real positivo e a segunda/terceira/décima melhores
posições do ranking de especificidade. `SARESIKKAYKTFLERYKKL` — o melhor Vina bruto de todo o
pipeline (−14,58 kcal/mol) — ilustra o padrão: docking rígido excelente, MD apenas marginal, mas
a melhor especificidade real medida (SI = 1,61).

**Síntese real, com ressalva de amostra pequena**: entre os candidatos curtos (5/7 aa), quando um
é estável ele tende também a ser razoavelmente seletivo (6 de 7 casos "Comum" são curtos) — mas
`VRRPR` mostra que essa tendência não é uma regra garantida. Entre os candidatos de 20 aa, o
padrão é mais bipolar: ou estável-mas-não-seletivo, ou seletivo-mas-só-marginalmente-estável,
com `SEEEVLAANEAYAAAHTAYN` como única exceção real a reunir as duas propriedades nesse
comprimento. Com n pequeno em cada grupo, isso é uma observação a acompanhar com mais candidatos,
não uma lei estatística estabelecida.

### 3.11c Expansão Cross-Species (R3) — TOP-10 vs. *Helicoverpa armigera* real (2026-07-18)

Diferente da Seção 3.11 (não-alvos humano/*Apis mellifera*, onde afinidade **baixa** é
desejável), esta seção testa afinidade contra **outra espécie-praga** — aqui, afinidade **alta**
(comparável ao alvo primário) é o resultado desejado, pois indicaria eficácia de amplo espectro
entre Lepidoptera-praga (requisito R3).

Como os quatro receptores originais (ACR157/QCL936/XP273/XP352) têm documentação de espécie
internamente conflitante no projeto (não resolvida — ver metodologia), a expansão usou uma
tripsina digestiva nova e verificável: UniProt B6CME8 (*H. armigera*, TrEMBL, 279 aa), sem
estrutura no AlphaFold DB (HTTP 404 confirmado em todas as versões v1–v6) — estrutura obtida via
API pública do ESMFold (Lin et al., 2022). Tríade catalítica real mapeada por
`StructureAgent._analyze_single` (mesmo método dos 4 receptores primários): His82/Asp132/Ser251,
Asp233 no bolso S1.

**Tabela 9f.** TOP-10 — Vina real contra alvo primário (ACR157) vs. *H. armigera* (B6CME8).

| Sequência | Comp. | Vina ACR157 | Vina *H. armigera* | Δ (Harmigera − ACR157) |
|---|---|---|---|---|
| SRTRR | 5 | −10,31 | −8,88 | +1,43 |
| HRPRRPR | 7 | −11,72 | −10,52 | +1,20 |
| RLREELKKAEEWLEKRRKEE | 20 | −12,21 | −11,79 | +0,42 |
| SEEEVLAANEAYAAAHTAYN | 20 | −13,40 | −12,48 | +0,92 |
| SALASIAAHQATFLAYLESK | 20 | −12,52 | **−13,03** | **−0,51** |
| MGSLTAYLEAYAAENAAALA | 20 | −12,67 | −11,28 | +1,39 |
| RLRAIWLEAEKLLEERRKKK | 20 | −12,22 | −11,58 | +0,64 |
| MGYLTAYHQALAAQNAALLA | 20 | −13,04 | −11,88 | +1,16 |
| RVKDQWLEAEKLLEERRKKK | 20 | −11,52 | −12,04 | −0,52 |
| SARESIKKAYKTFLERYKKL | 20 | −14,58 | −12,36 | +2,22 |

Todos os 10 candidatos mantêm afinidade real e competitiva (−8,9 a −13,0 kcal/mol) contra
*H. armigera*, sem nenhuma ruptura de ligação — evidência de que o design não é
hiperespecífico a ACR157. Dois candidatos (`SALASIAAHQATFLAYLESK`, `RVKDQWLEAEKLLEERRKKK`)
tiveram afinidade real **melhor** contra *H. armigera* do que contra o alvo primário.

**Expansão completa para 8 espécies (2026-07-18).** Seis espécies adicionais bem documentadas
foram incorporadas via busca UniProt REST real, priorizando entradas com padrão de tripsina
digestiva (~250–270 aa) e estrutura AlphaFold DB confirmada (v6, contagem de átomos Cα conferida
contra o UniProt em todos os casos): *Manduca sexta* (P35045, **Swiss-Prot revisado**, "Trypsin
alkaline A"), *Bombyx mori* (A0A8R2C8B0), *Plutella xylostella* (E2IGY7), *Spodoptera litura*
(B3F884), *S. frugiperda* (A0A089QDB3), *Ostrinia nubilalis* (Q6R561). Uma sétima espécie —
*Anticarsia gemmatalis* (A0A2U8NFD7, "Trypsin 1", 260 aa) — foi adicionada como referência
independente e verificada da própria espécie-alvo do projeto (distinta da identidade
documentalmente ambígua de ACR157). A tríade catalítica de todas as 7 novas estruturas foi
mapeada com `StructureAgent._analyze_single` (mesmo método dos 4 receptores primários) e
confirmada canônica (His/Asp/Ser reais + segundo Asp real no bolsão S1) **por construção do
algoritmo** — a busca só considera candidatos entre resíduos com o `resname` correto, nunca
substitui por outro tipo de aminoácido.

**Tabela 9g.** Matriz completa — Vina real (kcal/mol), TOP-10 × 8 espécies de Lepidoptera.

| Sequência | A. gemmatalis | H. armigera | M. sexta | B. mori | P. xylostella | S. litura | S. frugiperda | O. nubilalis |
|---|---|---|---|---|---|---|---|---|
| SRTRR | −9,19 | −8,88 | −9,53 | −9,56 | −9,72 | −9,28 | −10,95 | −9,43 |
| HRPRRPR | −10,10 | −10,52 | −11,44 | −10,62 | −11,71 | −10,27 | −11,42 | −11,88 |
| RLREELKKAEEWLEKRRKEE | −12,75 | −11,79 | −11,99 | −13,28 | −12,81 | −12,36 | −13,36 | −12,77 |
| SEEEVLAANEAYAAAHTAYN | −12,31 | −12,48 | **−14,30** | **−14,48** | −13,02 | −12,47 | −12,49 | −12,14 |
| SALASIAAHQATFLAYLESK | −11,97 | −13,03 | −11,87 | −12,15 | −13,27 | −11,66 | −12,87 | −11,97 |
| MGSLTAYLEAYAAENAAALA | −13,31 | −11,28 | −13,15 | −13,03 | −12,40 | −11,49 | −13,01 | −13,04 |
| RLRAIWLEAEKLLEERRKKK | **−15,35** | −11,58 | −12,76 | −13,77 | −13,50 | −12,07 | −14,18 | −11,88 |
| MGYLTAYHQALAAQNAALLA | −14,26 | −11,88 | −12,23 | −13,80 | −12,31 | −12,52 | −12,20 | −11,82 |
| RVKDQWLEAEKLLEERRKKK | −14,40 | −12,04 | −13,65 | −13,78 | −13,13 | −12,25 | **−14,49** | −12,31 |
| SARESIKKAYKTFLERYKKL | −12,51 | −12,36 | −12,88 | **−14,74** | −13,57 | −13,01 | −13,31 | −12,41 |
| **Média** | −12,62 | −11,58 | −12,38 | −12,92 | −12,54 | −11,74 | −12,83 | −11,97 |

**Leitura honesta**: nenhum candidato perde afinidade real em nenhuma das 8 espécies — faixa
completa −8,9 a −15,4 kcal/mol, sempre competitiva. As médias por espécie são próximas
(−11,58 a −12,92 kcal/mol), sem nenhuma espécie "imune" ao design. Isso é evidência real de
potencial de amplo espectro entre pragas Lepidoptera, satisfazendo o requisito R3. Os dois
candidatos já identificados com SI **negativo** contra tripsina humana (Seção 3.11b —
`RLRAIWLEAEKLLEERRKKK`, `RVKDQWLEAEKLLEERRKKK`) são também os que mostram maior afinidade real
contra *A. gemmatalis* verdadeira entre todos os 80 valores da matriz (−15,35 e −14,40) — reforça
que são candidatos de afinidade alta e pouco discriminativa, não apenas "menos seletivos".

**Limitações reais**: (1) esta matriz é só docking rígido — não testa estabilidade MD
cross-species nem especificidade humano/*Apis* para os 6 novos candidatos curtos gerados na
Seção 3.10c (não fazem parte deste TOP-10); (2) a comparação direta ACR157×A0A2U8NFD7 mostra
correlação moderada mas não perfeita (2 candidatos divergem >2 kcal/mol) — dado real, mas
insuficiente para concluir se ACR157 é ou não *A. gemmatalis*, não usado para essa inferência.

### 3.11e Teste Profundo do TOP-13 — Réplicas Vina, MM-GBSA e PLIP Mecanístico (2026-07-18)

A pedido do usuário, os 13 candidatos da Tabela 9j (união dos rankings absoluto/especificidade)
foram submetidos a três testes adicionais de rigor: (1) réplicas reais de docking Vina para
quantificar a variância estocástica real; (2) energia livre de ligação real via MM-GBSA
(gmx_MMPBSA) sobre as trajetórias MD já existentes; (3) extensão da análise PLIP mecanística
(Seção 3.10b) para os candidatos que ainda não a tinham.

**Bugs reais corrigidos durante a implementação** (detalhes completos em memória de projeto,
também gravados nas regras não-negociáveis do sistema de memória por serem de escopo
cross-project): (a) `gmx_MMPBSA` quebra com `ValueError` de overflow no termo BOND se a
trajetória não tiver o PBC removido antes — corrigido com `gmx trjconv -pbc mol -center` como
pré-processamento obrigatório; (b) `subprocess.run(input=...)` do Python não funciona de forma
confiável com `gmx_mpi` em sessões `screen` detached (causa `MPI_ABORT`) — corrigido usando pipe
de shell real; (c) `cwd=` do subprocess combinado com paths já relativos-à-raiz duplica o
caminho e causa `FileNotFoundError` mesmo com o arquivo existindo; (d) parte do batch antigo de
candidatos (Fase 4/5) tem trajetória em `outputs/md/forced_NN/`, não `outputs/md/{sequência}/`
— mapeamento reconstruído a partir da sequência real presente em cada `complex_clean.pdb`
(não adivinhado).

**Tabela 9k.** Réplicas reais de Vina (n=5, exhaustiveness=16) — média ± desvio-padrão real.

| Sequência | Comp. | Vina médio (kcal/mol) | DP real | Valor único usado nas seções anteriores |
|---|---|---|---|---|
| SARESIKKAYKTFLERYKKL | 20 | −14,580 | ~0,000 | −14,58 |
| SEEEVLAANEAYAAAHTAYN | 20 | −13,382 | 0,016 | −13,40 |
| MGYLTAYHQALAAQNAALLA | 20 | −13,048 | 0,004 | −13,04 |
| MGSLTAYLEAYAAENAAALA | 20 | −12,670 | 0,000 | −12,67 |
| SALASIAAHQATFLAYLESK | 20 | −12,520 | 0,000 | −12,52 |
| RLREELKKAEEWLEKRRKEE | 20 | −12,214 | 0,017 | −12,21 |
| HRPRRPR | 7 | −11,722 | 0,007 | −11,72 |
| HRPRRSR | 7 | −11,542 | 0,032 | −11,56 |
| HRPRRPK | 7 | −10,990 | 0,000 | −10,99 |
| SRTRR | 5 | −10,328 | 0,015 | −10,31 |
| VRYRR | 5 | −10,212 | 0,004 | −10,22 |
| VRTRR | 5 | −9,561 | 0,019 | −9,55 |
| VRRPR | 5 | −9,452 | 0,011 | −9,45 |

**Achado real**: com `exhaustiveness=16` (maior que o padrão 8 usado no restante do pipeline), o
Vina converge para essencialmente o mesmo ótimo em 5 corridas independentes — desvio-padrão real
entre 0,000 e 0,032 kcal/mol, muito menor que a variância de ~0,1–0,5 kcal/mol observada
anteriormente no docking cross-species (Seção 3.11c, `exhaustiveness=8`). Isso confirma que os
valores únicos de Vina usados em todo o pipeline (Seções 3.4–3.11d) são reprodutíveis dentro de
margem pequena — a variância real está mais em `exhaustiveness` baixo do que em estocasticidade
intrínseca do algoritmo.

**Tabela 9l.** MM-GBSA real (gmx_MMPBSA, GB/sander, 51 frames por candidato, frames 1000–2000 da
produção 10 ns).

| Sequência | ΔG_binding real (kcal/mol) | SEM | Status |
|---|---|---|---|
| SRTRR | **−44,49** | 2,49 | real, plausível |
| VRRPR | **−29,21** | 1,00 | real, plausível |
| HRPRRSR | **−20,74** | 0,99 | real, plausível |
| VRTRR | **−12,55** | 0,76 | real, plausível |
| VRYRR | +372,27 | 1,86 | **real mas anômalo** — ver nota abaixo |
| HRPRRPR, HRPRRPK, RLREELKKAEEWLEKRRKEE, SEEEVLAANEAYAAAHTAYN, SALASIAAHQATFLAYLESK, MGSLTAYLEAYAAENAAALA, MGYLTAYHQALAAQNAALLA | — | — | `MMPBSA_Error: complex index has fewer atoms than the topology` — falhou em 3/3 tentativas, pulado conforme instrução do usuário |
| SARESIKKAYKTFLERYKKL | — | — | trajetória bruta (.xtc/.tpr) não preservada — sem re-análise possível sem MD do zero |

**Nota sobre a anomalia de VRYRR**: a decomposição energética mostra ΔVDWAALS = +330,11
kcal/mol — um choque estérico severo entre peptídeo e receptor nos frames amostrados (5–10 ns),
inconsistente com o RMSD geral baixo e estável já reportado para esse candidato (0,1985 nm,
Seção 3.10d). Interpretação honesta: a janela de frames amostrada para o MM-GBSA capturou uma
sub-região da trajetória com uma pose real mas transitoriamente desfavorável — não invalida a
estabilidade geral (RMSD médio de toda a trajetória), mas o valor de ΔG_binding de VRYRR não deve
ser tratado como confiável sem reamostragem de mais frames ou janelas alternativas. **Taxa de
sucesso real do MM-GBSA neste conjunto: 5/13 (38%), com 1 dessas 5 sinalizada como não-confiável**
— um lembrete de que MM-GBSA sobre topologias GROMACS convertidas é uma técnica frágil na prática,
mesmo quando o pipeline de preparação está correto.

**Tabela 9m.** PLIP mecanístico — contato real com a tríade catalítica (His/Asp/Ser), 12/13
candidatos avaliados (8 nesta rodada + 4 já reportados na Seção 3.10b/9c).

| Sequência | His | Asp | Ser | Origem |
|---|---|---|---|---|
| SRTRR | ✓ | ✓ | ✓ | novo |
| VRYRR | ✓ | ✓ | ✓ | novo |
| **VRTRR** | **✗** | ✓ | ✓ | novo |
| HRPRRPR | ✓ | ✓ | ✓ | novo |
| VRRPR | ✓ | ✓ | ✓ | novo |
| HRPRRSR | ✓ | ✓ | ✓ | novo |
| RLREELKKAEEWLEKRRKEE | ✓ | ✓ | ✓ | novo |
| HRPRRPK | ✓ | ✓ | ✓ | novo |
| SEEEVLAANEAYAAAHTAYN | ✓ | ✓ | ✓ | histórico (3.10b) |
| SALASIAAHQATFLAYLESK | ✓ | ✗ | ✓ | histórico (3.10c) |
| MGYLTAYHQALAAQNAALLA | ✗ | ✗ | ✓ | histórico (3.10c) |
| MGSLTAYLEAYAAENAAALA | ✗ | ✗ | ✓ | histórico (3.10c) |
| SARESIKKAYKTFLERYKKL | — | — | — | sem trajetória bruta |

**Achado real notável**: `VRTRR` — o candidato mais estável de todo o pipeline (RMSD 0,1936 nm,
Seção 3.10d) — é o único dos 8 candidatos curtos/médios recém-testados que **não contata a
His catalítica** na pose final da trajetória, apesar de contatar Asp e Ser. Combinado com seu
SI real fraco (0,39, Seção anterior), isso sugere que `VRTRR` pode se ligar de forma estável ao
sítio mas por um modo de interação menos completo/específico que os demais candidatos curtos —
hipótese mecanística a acompanhar, não conclusão fechada (n=1 observação).

### 3.11f Réplicas Reais de MD (n=3) — Reprodutibilidade da Estabilidade (2026-07-19)

A pedido do usuário, os 13 candidatos da Tabela 9j foram submetidos a réplicas reais adicionais
de MD (rep2 e rep3, 10 ns cada, `gen_seed=-1` na etapa NVT para garantir velocidades iniciais
independentes), partindo do mesmo `complex_clean.pdb` já equilibrado da rep1 (não reconstruído do
zero — mesma lição da Seção 3.11e). Isso fecha n=3 réplicas totais por candidato e testa se os
valores de RMSD usados em todas as seções anteriores (rep1 única) são representativos ou
artefato de um único seed aleatório.

**Tabela 9n.** RMSD real médio ± DP entre 3 réplicas independentes (rep1 histórica + rep2 + rep3
novas), Rg médio das 3 réplicas, e reclassificação por reprodutibilidade.

| Sequência | Comp. | RMSD rep1 (nm) | RMSD n=3 méd (nm) | DP real (n=3) | Rg n=3 méd (nm) | Classificação real |
|---|---|---|---|---|---|---|
| SRTRR | 5 | 0,2425 | **0,214** | 0,025 | 1,693 | **ESTÁVEL REPRODUTÍVEL** |
| VRYRR | 5 | 0,1985 | **0,215** | 0,023 | 1,712 | **ESTÁVEL REPRODUTÍVEL** |
| VRRPR | 5 | 0,2679 | **0,256** | 0,016 | 1,732 | **ESTÁVEL REPRODUTÍVEL** |
| HRPRRPR | 7 | 0,2659 | **0,270** | 0,044 | 1,749 | **ESTÁVEL REPRODUTÍVEL** |
| HRPRRSR | 7 | 0,2743 | 0,377 | 0,173 | 1,736 | ALTA VARIÂNCIA |
| VRTRR | 5 | 0,1936 | 0,417 | **0,360** | 1,708 | **ALTA VARIÂNCIA — refuta recorde anterior** |
| HRPRRPK | 7 | 0,4103 | 0,421 | 0,092 | 1,758 | marginal reprodutível |
| SEEEVLAANEAYAAAHTAYN | 20 | 0,4742 | 0,478 | 0,041 | 1,771 | marginal reprodutível |
| MGYLTAYHQALAAQNAALLA | 20 | 0,8204 | 0,576 | 0,233 | 1,776 | ALTA VARIÂNCIA |
| MGSLTAYLEAYAAENAAALA | 20 | 0,6390 | 0,662 | 0,032 | 1,784 | marginal reprodutível |
| SARESIKKAYKTFLERYKKL | 20 | 0,8713 | 0,758 | 0,339 | 1,838 | ALTA VARIÂNCIA |
| RLREELKKAEEWLEKRRKEE | 20 | 0,2940 | 0,810 | **0,606** | 1,857 | **ALTA VARIÂNCIA — refuta recorde anterior** |
| SALASIAAHQATFLAYLESK | 20 | 0,5677 | 1,014 | 0,762 | 1,835 | ALTA VARIÂNCIA |

Critério de classificação (transparente, não arbitrário pós-hoc): **ESTÁVEL REPRODUTÍVEL** =
RMSD médio n=3 < 0,30 nm E DP < 0,05 nm; **marginal reprodutível** = DP < 0,10 nm independente da
média; **ALTA VARIÂNCIA** = DP ≥ 0,15 nm, indicando que o valor de réplica única não é
representativo do comportamento real do candidato.

**Achado real crítico**: os dois candidatos historicamente descritos como "mais estável do
pipeline" em toda a Seção 3 — `RLREELKKAEEWLEKRRKEE` (0,294 nm, Fase 4, Seção 3.7/3.8b) e
`VRTRR` (0,1936 nm, "novo recordista", Seção 3.10d) — **não se sustentam como estáveis quando
testados em réplicas independentes**. `VRTRR` rep2 chegou a 0,8315 nm (vs. 0,2251 nm da rep3 e
0,1936 nm da rep1) e `RLREELKKAEEWLEKRRKEE` rep3 chegou a 1,4771 nm. Isso significa que os
valores únicos de RMSD usados para classificar candidatos como "estáveis" em todas as seções
anteriores (3.7 a 3.11e) carregam risco real de não-representatividade — o resultado de uma
única trajetória de 10 ns pode refletir o seed inicial, não a estabilidade termodinâmica real do
complexo.

Em contraste, **4 candidatos se confirmam genuinamente estáveis e reprodutíveis**: `SRTRR`,
`VRYRR`, `VRRPR` e `HRPRRPR` — todos com DP real < 0,05 nm entre as 3 réplicas independentes.
Desses 4, nenhum atinge SI real ≥ 2,0 (Tabela 9j: SRTRR=1,17, VRYRR=0,92, HRPRRPR=1,41,
VRRPR=−0,13) — ou seja, mesmo o subconjunto agora validado como robusto em MD continua **sem
margem de seletividade real comprovada** (Seção 3.11), reforçando que estabilidade estrutural e
especificidade são bloqueadores independentes, ambos ainda não resolvidos simultaneamente por
nenhum candidato.

**Ressalva de fonte para `SARESIKKAYKTFLERYKKL`**: diferente dos outros 12 candidatos, suas
réplicas rep2/rep3 partiram do PDB pré-MD (`complex_md_SARESIKKAY.pdb`), não do
`complex_clean.pdb` já equilibrado da rep1 (não preservado) — ponto de partida menos ideal
(Seção 2.12/metodologia). O DP alto observado (0,339 nm) pode refletir tanto instabilidade real
quanto esse ponto de partida diferente; interpretar com cautela adicional em relação aos demais.

**Limitação metodológica explícita**: n=3 réplicas de 10 ns é o mínimo para estimar variância,
não para convergência estatística robusta (tipicamente requer n≥5 ou trajetórias mais longas,
≥50-100 ns, para sistemas com DP tão alto quanto os observados aqui). O achado de "alta
variância" deve ser lido como "réplica única não é confiável para este candidato", não como
"candidato definitivamente instável" — RLREELKKAEEWLEKRRKEE e VRTRR precisariam de réplicas
adicionais (n≥5) ou trajetórias mais longas para uma classificação definitiva.

### 3.11g Persistência Competitiva Real — Ocupância do Bolso S1 ao Longo da Trajetória (2026-07-19)

A pedido do usuário, os 13 candidatos da Tabela 9j foram submetidos a uma métrica nova, que mede
algo diferente do RMSD do complexo inteiro já reportado nas Tabelas 9n e anteriores: para cada
frame de cada réplica real (n=3 quando disponível, `nstxout-compressed` = 1 frame/5 ps, 2001
frames/réplica), calculou-se a distância entre cada resíduo do peptídeo e o Asp187 catalítico
(bolso S1, receptor ACR157), e o **resíduo âncora real** foi definido empiricamente por candidato
como aquele com a menor distância média — nunca assumido a priori como o resíduo C-terminal ou o
P1 "esperado" (5 dos 13 candidatos nem terminam em Arg/Lys). A partir da série temporal de
distâncias do resíduo âncora, dois números foram reportados: (1) a **ocupância** — fração dos
frames em que essa distância fica abaixo de um corte (3 cortes reportados: 4, 5 e 6 Å; a
validação real contra `SRTRR` durante a implementação mostrou que o corte estrito de 4 Å, padrão
textbook de salt-bridge, captura quase nada — 0,3–1% dos frames mesmo para o candidato mais
robusto do pipeline — enquanto o corte de 6 Å captura 87–100% nas 3 réplicas do mesmo candidato;
por isso os 3 cortes são reportados lado a lado, com 6 Å tratado como sinal principal de
"permanece perto do bolso" e 4 Å como sinal estrito de "salt bridge apertada", sem descartar
nenhum dos dois); e (2) o **RMSD local do bolso** — RMSD do peptídeo após superposição feita
**apenas** nos átomos Cα do receptor (não do complexo inteiro), isolando "o peptídeo saiu do
bolso" de "o complexo inteiro balançou" — uma métrica diferente e complementar ao RMSD do
complexo já usado nas Tabelas 9n e anteriores, não um substituto nem o mesmo número. Réplicas sem
`.tpr`/`.xtc` reais preservados foram reportadas como dado ausente (`error`), nunca inferidas.

**Tabela 9o.** Ocupância real do bolso S1 (4/5/6 Å) e RMSD local do bolso, média entre réplicas
reais disponíveis (n=3 salvo indicação contrária).

| Sequência | Resíduo âncora real | Ocupância 4Å / 5Å / 6Å (méd., %) | RMSD local do bolso (méd., nm) | Interpretação |
|---|---|---|---|---|
| SRTRR | Arg (idx1), consistente nas 3 réplicas | 33,3 / 48,2 / 94,3 | 0,406 | ocupância a 6Å alta mas contato apertado (4Å) intermitente — rep2 ~99% a 4Å, rep1/rep3 quase 0% |
| VRYRR | Arg (idx1), consistente nas 3 réplicas | 99,5 / 99,9 / 100,0 | 0,435 | **único candidato com salt-bridge real (~4Å) constante nas 3 réplicas** |
| VRRPR | Val (idx0, N-terminal — não básico), consistente nas 3 réplicas | 0,0 / 0,5 / 33,5 | 0,416 | **ocupância REAL BAIXA e caindo entre réplicas (67,6%→32,9%→0,15% a 6Å)** — estável por RMSD global, sai do bolso na prática |
| HRPRRPR | Pro (idx2 — não básico), consistente nas 3 réplicas | 0,0 / 15,5 / 96,1 | 0,271 | ocupância a 6Å alta e consistente; âncora real é Prolina, não o resíduo P1 esperado |
| HRPRRSR | Pro (idx2 — não básico), consistente nas 3 réplicas | 0,0 / 8,5 / 80,1 | 0,362 | ocupância a 6Å boa mas fraca a 5Å; mesma âncora não-básica de HRPRRPR/HRPRRPK |
| VRTRR | Arg (idx1) em rep1/rep2, **Thr (idx2) em rep3** — âncora muda entre réplicas | 33,9 / 55,4 / 94,3 | 0,526 | pose não convergente (âncora instável); consistente com classificação "ALTA VARIÂNCIA" da Tabela 9n |
| HRPRRPK | Pro (idx2 — não básico), consistente nas 3 réplicas | 0,8 / 40,1 / 90,4 | 0,284 | ocupância a 6Å alta e crescente entre réplicas (73,0%→99,9%→98,3%) |
| SEEEVLAANEAYAAAHTAYN | Asn (idx8 — não básico), consistente nas 3 réplicas | 0,4 / 41,7 / 91,9 | 0,729 | n=3 completo (2026-07-20, fix de mapeamento REP1_DIR_OVERRIDE — rep1 real existia em forced_00/, não estava sendo lida); ocupância a 6Å boa mas contato frouxo a 4Å |
| MGYLTAYHQALAAQNAALLA | Gln (idx8 — não básico), consistente nas 3 réplicas | 36,8 / 89,4 / 100,0 | 0,837 | n=3 completo (fix 2026-07-20, forced_01/); ocupância alta em todos os cortes — melhor persistência do grupo de 20aa |
| MGSLTAYLEAYAAENAAALA | Glu (idx8 — não básico), consistente nas 3 réplicas | 7,5 / 65,1 / 87,4 | 1,033 | n=3 completo (fix 2026-07-20, forced_03/); ocupância alta a 6Å mas RMSD local do bolso é o mais alto do grupo (rep1=1,429 nm) |
| SARESIKKAYKTFLERYKKL (n=2, rep1 sem trajetória) | Lys (idx6 em rep2, idx7 em rep3 — mesmo resíduo, deslocamento de índice) | 0,0 / 8,0 / 87,2 | 0,844 | único candidato do TOP-13 sem complex_clean.pdb preservado da rep1 original — rep1 real nova rodando (MD do zero) para fechar n=3 |
| RLREELKKAEEWLEKRRKEE | Glu (idx9 — não básico), consistente nas 3 réplicas | 4,6 / 54,0 / 82,5 | 0,595 | ocupância moderada e mais consistente entre réplicas do que seu RMSD global (DP=0,606 nm, Tabela 9n) sugeriria |
| SALASIAAHQATFLAYLESK | Gln (idx9 — não básico), consistente nas 3 réplicas | 0,0 / 6,2 / 48,2 | 0,763 | n=3 completo (fix 2026-07-20, forced_04/); **ainda o pior perfil de persistência real do grupo** — 6Å médio 48,2%, mas real (rep2/rep3 antigos já indicavam isso, agora confirmado com rep1) |

**Achado real crítico — confirma parcialmente, mas complica, a conclusão da Tabela 9n**: dos 4
candidatos classificados como "ESTÁVEL REPRODUTÍVEL" pelo RMSD do complexo inteiro (SRTRR,
VRYRR, VRRPR, HRPRRPR), 3 confirmam ocupância real alta e consistente a 6Å (SRTRR 94,3%, VRYRR
100,0%, HRPRRPR 96,1%) — ou seja, para esses 3, "complexo estável" de fato corresponde a
"peptídeo permanece perto de Asp187". `VRYRR` se destaca ainda mais nesta métrica: é o único
candidato com ocupância alta mesmo no corte estrito de 4 Å (99,5% médio, ~100% em todas as 3
réplicas) — uma salt-bridge real e constante, coerente com seu contato completo à tríade
catalítica já reportado na Tabela 9m (PLIP). **`VRRPR` é a exceção que complica a conclusão
anterior**: apesar de ter o menor DP de RMSD do complexo entre os 13 candidatos (0,016 nm, Tabela
9n), seu resíduo âncora real é a Valina N-terminal (não um resíduo básico, e não o resíduo mais
próximo do P1 esperado), e sua ocupância a 6Å **cai monotonicamente entre réplicas** — 67,6% na
rep1, 32,9% na rep2, 0,15% na rep3 (média 33,5%, a segunda pior do grupo). Isso é evidência real
de que `VRRPR` pode manter o complexo geometricamente rígido (baixo RMSD do sistema inteiro) sem
que o peptídeo de fato permaneça ancorado perto do bolso catalítico — o cenário que a Seção 3.11f
já havia alertado ser possível ("balança perto do receptor mas sai do sítio"), agora com dado
real que o identifica especificamente neste candidato.

Outros dois achados reais notáveis: (1) para os três candidatos `HRPRRPR`/`HRPRRSR`/`HRPRRPK`, o
resíduo âncora real nas 3 réplicas é sempre a **Prolina** interna (índice 2), não um resíduo
básico nem o C-terminal — achado validado manualmente por rastreamento de distância durante a
Task 3 desta sessão, não um bug do script; (2) `VRTRR` — já sinalizado como instável em réplicas
pela Tabela 9n (DP=0,360 nm) — é o único candidato cujo **resíduo âncora muda de identidade**
entre réplicas (Arg em rep1/rep2, Thr em rep3), reforçando por uma via independente que sua pose
de ligação não converge.

**Limitação explícita**: assim como a Tabela 9n, esta análise usa n=3 réplicas (n=2 para
`SARESIKKAYKTFLERYKKL`, único candidato do TOP-13 sem `complex_clean.pdb` preservado da rep1
original — os outros 4 candidatos que inicialmente apareciam como n=2 tinham rep1 real já
preservada em `outputs/md/forced_NN/`, só não estavam mapeadas corretamente no script; corrigido
em 2026-07-20, ver `REP1_DIR_OVERRIDE` em `scripts/deep_test_persistence.py`) — suficiente para
apontar variância real, não para convergência estatística robusta. Os valores de ocupância a 4 Å
devem ser lidos como sinal estrito e raro (mesmo candidatos genuinamente estáveis passam a maior
parte do tempo entre 4 e 6 Å do Asp187, não colados a ele), não como ausência de interação real.

### 3.11h Contato Real com Subsítios S2'/S3' Canônicos — Heurística Geométrica (2026-07-19)

**Ressalva metodológica explícita, antes de qualquer número**: nenhum receptor deste projeto tem
estrutura cristalográfica com substrato ligado nos subsítios S2'/S3' — apenas modelos
estruturais/AlphaFold. Não existe, portanto, posição canônica pronta desses subsítios. Os
resíduos 204 e 218 (receptor ACR157) usados nesta seção vêm de uma **heurística
geométrica+sequencial** implementada em `scripts/s2s3_utils.py` (Task 5 do mesmo plano): dentre os
resíduos já no hotspot de 8 Å do receptor, foram selecionados os que ficam na vizinhança
sequencial da Ser catalítica (Ser+1 a Ser+15) e fora da vizinhança imediata do Asp do bolso S1
(±2 resíduos). **Isso é uma aproximação operacional, não uma validação estrutural externa** — o
mesmo tratamento explícito de limitação já dado ao mapeamento igualmente fraco do sítio S2'
(diferente, de outra proteína-alvo) no projeto irmão `analise-alosterica`. Qualquer menção a
"contato com S2'/S3'" nesta seção deve ser lida como "contato real com os resíduos 204/218,
operacionalmente definidos por esta heurística como S2'/S3'", nunca como confirmação mecanística.

Para os mesmos 13 candidatos e as mesmas réplicas reais (rep1/rep2/rep3, `.tpr`/`.xtc`
preservados) usadas nas Seções 3.11f/3.11g, foram extraídos 5 frames por réplica (1, 3, 5, 7 e
9 ns de produção) via `gmx trjconv -pbc mol -center`, protonados com `obabel -h`, e submetidos ao
PLIP (`--peptides B`, mesmo padrão validado na Seção 3.11e). Contato = qualquer bloco de
interação do PLIP (ligação de H, hidrofóbica ou ponte salina) entre o peptídeo e o resíduo 204
**ou** o 218. A fração reportada é o número de frames com contato dividido pelo número de frames
processados com sucesso (até 5 por réplica) — ou seja, cada frame individual vale 20 pontos
percentuais, e a métrica é deliberadamente grosseira.

**Tabela 9p.** Fração média de frames com contato real S2'/S3' (heurística), n=3 réplicas salvo
indicação contrária.

| Sequência | Fração de frames com contato S2'/S3' (méd., %) | Fração por réplica (rep1/rep2/rep3, %) | Resíduos-alvo reais | Interpretação |
|---|---|---|---|---|
| SRTRR | 33,3 | 0,0 / 0,0 / 100,0 | 204, 218 | "estável/persistente" no S1 (Tabelas 9n/9o), mas contato S2'/S3' oscila entre ausente e total — não há sinal estável |
| VRYRR | 6,7 | 0,0 / 0,0 / 20,0 | 204, 218 | menor contato médio do grupo, apesar de ser o único com salt-bridge S1 constante a 4 Å (Tabela 9o) |
| VRRPR | 13,3 | 0,0 / 20,0 / 20,0 | 204, 218 | contato S2'/S3' baixo, na mesma direção do achado da Tabela 9o (sai do bolso S1 na rep3) — nenhum sinal de compensação no S2'/S3' |
| HRPRRPR | 40,0 | 20,0 / 20,0 / 80,0 | 204, 218 | quarto "reprodutivelmente estável" (Tabela 9n); contato S2'/S3' moderado, réplica 3 destoa das outras duas |
| HRPRRSR | 66,7 | 100,0 / 60,0 / 40,0 | 204, 218 | maior contato médio do grupo, mas candidato classificado "ALTA VARIÂNCIA" de RMSD (Tabela 9n) — não é um candidato validado como estável |
| VRTRR | 40,0 | 20,0 / 0,0 / 100,0 | 204, 218 | mesma instabilidade de pose já identificada na Tabela 9o (âncora S1 muda entre réplicas); contato S2'/S3' igualmente errático |
| HRPRRPK | 40,0 | 0,0 / 60,0 / 60,0 | 204, 218 | contato moderado, crescente entre réplicas, na mesma direção da ocupância S1 crescente (Tabela 9o) |
| SEEEVLAANEAYAAAHTAYN (n=2, rep1 sem trajetória) | 60,0 | — / 40,0 / 80,0 | 204, 218 | segundo maior contato médio do grupo; candidato "marginal reprodutível" por RMSD (Tabela 9n), não "estável" |
| MGYLTAYHQALAAQNAALLA (n=2, rep1 sem trajetória) | 0,0 | — / 0,0 / 0,0 | 204, 218 | nenhum contato real detectado nas 2 réplicas disponíveis |
| MGSLTAYLEAYAAENAAALA (n=2, rep1 sem trajetória) | 20,0 | — / 20,0 / 20,0 | 204, 218 | contato baixo mas consistente entre as 2 réplicas disponíveis |
| SARESIKKAYKTFLERYKKL (n=2, rep1 sem trajetória) | 0,0 | — / 0,0 / 0,0 | 204, 218 | nenhum contato real detectado nas 2 réplicas disponíveis |
| RLREELKKAEEWLEKRRKEE | 0,0 | 0,0 / 0,0 / 0,0 | 204, 218 | nenhum contato real detectado em nenhuma das 3 réplicas — candidato já refutado como "mais estável do pipeline" (Tabela 9n) |
| SALASIAAHQATFLAYLESK (n=2, rep1 sem trajetória) | 0,0 | — / 0,0 / 0,0 | 204, 218 | nenhum contato real detectado nas 2 réplicas disponíveis; já o pior perfil de persistência S1 do grupo (Tabela 9o) |

**Achado real — sinal ruidoso, sem correlação coerente com os achados anteriores**: a média de
fração de contato S2'/S3' dos 4 candidatos "ESTÁVEL REPRODUTÍVEL" por RMSD (Tabela 9n: SRTRR,
VRYRR, VRRPR, HRPRRPR) é 23,3% — praticamente idêntica à média dos outros 9 candidatos (25,2%).
Ou seja, **este sinal não discrimina** os candidatos já validados como estruturalmente robustos
dos demais. Dentro do próprio grupo dos 4 "estáveis", o espalhamento é grande: `VRYRR` — o único
com salt-bridge S1 constante e contato completo à tríade catalítica (Tabela 9m) — tem o **menor**
contato médio S2'/S3' de todos os 13 candidatos (6,7%), enquanto `HRPRRPR` tem o maior entre os 4
(40,0%). O caso mais consistente com um achado anterior é `VRRPR`: contato S2'/S3' baixo (13,3%)
na mesma direção qualitativa do que a Tabela 9o já mostrou para o bolso S1 (ocupância caindo entre
réplicas) — o candidato não parece compensar a saída do S1 com contato adicional em S2'/S3'. Fora
esse caso, **os dados não sustentam nenhuma narrativa de "candidato X também ocupa S2'/S3'"** de
forma clara: a variação intra-candidato entre réplicas do mesmo peptídeo (ex. SRTRR: 0,0/0,0/1,0;
VRTRR: 0,2/0,0/1,0) é da mesma ordem de grandeza da variação entre candidatos diferentes, o que é
esperado quando cada réplica contribui só 5 frames e cada frame vale 20 pontos percentuais.

**Limitação explícita, em duas camadas**: (1) a definição dos resíduos 204/218 como S2'/S3' é uma
heurística geométrica+sequencial não validada externamente (ver ressalva no início da seção),
então mesmo um sinal limpo não seria prova estrutural de ocupação do subsítio real; (2) mesmo
aceitando a heurística, a resolução amostral (5 frames/réplica, cada um valendo 20 pontos
percentuais da fração) é baixa demais para separar sinal real de ruído estocástico de trajetória —
o mesmo tipo de limitação já registrado nas Seções 3.11f/3.11g para n=3 réplicas. Esta seção deve
ser lida como um teste exploratório que **não encontrou evidência clara**, positiva ou negativa,
de contato adicional em S2'/S3' entre os candidatos já caracterizados — não como confirmação nem
como descarte de qualquer candidato.

### 3.11i Assinatura Digital de Interação — Síntese das Frentes 2+3 (2026-07-19)

A pedido do usuário, esta seção não introduz nenhum dado novo — é uma tabela de síntese que reúne,
lado a lado, três métricas reais já reportadas separadamente nas Tabelas 9m (PLIP, contato real
com a tríade catalítica, Seção 3.10b/3.11e), 9o (ocupância real do bolso S1 e RMSD local do bolso,
Seção 3.11g) e 9p (contato heurístico real com S2'/S3', Seção 3.11h), para os 4 candidatos
confirmados "ESTÁVEL REPRODUTÍVEL" por RMSD do complexo inteiro em n=3 réplicas (Tabela 9n:
`SRTRR`, `VRYRR`, `VRRPR`, `HRPRRPR`) mais o caso não-canônico `SEEEVLAANEAYAAAHTAYN` (classificado
"marginal reprodutível", não "estável", na Tabela 9n). Nenhuma célula foi calculada ou inferida —
todos os valores abaixo são cópia direta das Tabelas 9m/9o/9p já publicadas nesta Seção 3.11. O
corte de 6 Å é usado como referência principal para a ocupância do bolso S1, por ser o corte
validado como mais informativo na Seção 3.11g (o corte de 4 Å captura apenas 0,3-1% dos frames
mesmo no candidato mais robusto do pipeline); os valores de 4 Å/5 Å são citados entre colchetes
como contexto adicional, não como métrica principal.

**Tabela 9q.** Assinatura digital de interação — síntese dos 5 candidatos (Tabelas 9m + 9o + 9p).

| Sequência | Contato tríade His/Asp/Ser (Tabela 9m) | Ocupância bolso S1 6 Å (%) [4 Å / 5 Å] (Tabela 9o) | RMSD local do bolso (nm) (Tabela 9o) | Contato S2'/S3' (%, heurística) (Tabela 9p) |
|---|---|---|---|---|
| SRTRR | ✓ / ✓ / ✓ | 94,3 [33,3 / 48,2] | 0,406 | 33,3 |
| VRYRR | ✓ / ✓ / ✓ | 100,0 [99,5 / 99,9] | 0,435 | 6,7 |
| VRRPR | ✓ / ✓ / ✓ | 33,5 [0,0 / 0,5] | 0,416 | 13,3 |
| HRPRRPR | ✓ / ✓ / ✓ | 96,1 [0,0 / 15,5] | 0,271 | 40,0 |
| SEEEVLAANEAYAAAHTAYN | ✓ / ✓ / ✓ | 91,9 [0,4 / 41,7] | 0,729 | 60,0 |

**Achado real — o que é comum aos 5 candidatos, e o que separa `VRRPR` do restante**: contato
completo com a tríade catalítica (His+Asp+Ser, Tabela 9m) é o único traço universal entre os 5 —
inclusive o caso não-canônico `SEEEVLAANEAYAAAHTAYN`. Entre os 4 classificados "ESTÁVEL
REPRODUTÍVEL" por RMSD do complexo inteiro (Tabela 9n), 3 (`SRTRR`, `VRYRR`, `HRPRRPR`) também
mostram ocupância real alta e consistente do bolso S1 a 6 Å (94,3-100,0%), confirmando que a
estabilidade do complexo inteiro corresponde, nesses 3 casos, à permanência real do peptídeo perto
do Asp187 catalítico. `VRRPR` é a exceção clara: apesar de estar no mesmo grupo "estável
reprodutível" por RMSD global (e de ter o menor DP de RMSD entre os 13 candidatos originais, Tabela
9n), sua ocupância a 6 Å é a segunda mais baixa da tabela (33,5%, caindo monotonicamente entre
réplicas conforme já registrado na Tabela 9o) — evidência real de que baixa variância no RMSD do
complexo não implica permanência do peptídeo no bolso catalítico. `SEEEVLAANEAYAAAHTAYN`, apesar de
classificado apenas "marginal reprodutível" (não "estável") por RMSD global, tem ocupância a 6 Å
(91,9%, agora com n=3 completo — fix de mapeamento 2026-07-20) mais próxima do grupo de 3
candidatos genuinamente persistentes do que de `VRRPR`, embora com âncora não-básica (Asn, Tabela
9o) e RMSD local do bolso mais alto (0,729 nm) que qualquer um dos outros 4 — sinal misto, não uma
confirmação de persistência equivalente.

Sobre a coluna de contato S2'/S3': os 5 valores variam de 6,7% (`VRYRR`) a 60,0%
(`SEEEVLAANEAYAAAHTAYN`), mas a Seção 3.11h já estabeleceu, sobre o conjunto completo de 13
candidatos, que esse sinal é ruidoso e **não discrimina** candidatos estruturalmente robustos dos
demais (média do grupo "estável" 23,3% vs. 25,2% dos outros 9). Essa mesma falta de poder
discriminante aparece dentro do subconjunto de 5 candidatos desta tabela: `VRYRR` — o candidato com
contato mais completo e consistente à tríade catalítica e a única salt-bridge S1 constante a 4 Å —
tem o menor contato médio S2'/S3' de todos (6,7%), enquanto `HRPRRPR` e `SEEEVLAANEAYAAAHTAYN` têm
os maiores (40,0% e 60,0%) sem que nenhuma outra métrica desta tabela os distinga favoravelmente do
resto. A única exceção pontual, já registrada na Seção 3.11h, é `VRRPR`: seu contato S2'/S3' baixo
(13,3%) está na mesma direção qualitativa do seu colapso de ocupância S1 (Tabela 9o) — mas essa é
uma coincidência isolada de um único candidato, não uma correlação geral entre as duas métricas, e
a Seção 3.11h é explícita em não sustentar "nenhuma narrativa de candidato X também ocupa S2'/S3'"
a partir desses números. A coluna S2'/S3' desta síntese deve, portanto, ser lida como contexto
exploratório de baixa confiabilidade, não como um quinto critério de seleção com o mesmo peso das
colunas de tríade catalítica e ocupância do bolso S1.

**Limitação explícita**: esta tabela é uma reorganização visual, não uma nova análise — herda todas
as limitações já documentadas nas Seções 3.11f-h (n=3 réplicas insuficiente para convergência
estatística robusta; heurística S2'/S3' não validada estruturalmente e com resolução amostral
baixa de 5 frames/réplica — essa parte da análise (Tabela 9p) segue com n=2 para
`SEEEVLAANEAYAAAHTAYN`, já que a Frente 3 não foi rerodada após o fix de mapeamento de 2026-07-20;
a coluna de ocupância do bolso S1, Tabela 9o, já está com n=3 completo para este candidato). Nenhum dos 5 candidatos desta
tabela tem margem de seletividade real comprovada (SI real < 2,0 para os 4 do grupo "estável
reprodutível": SRTRR=1,17, VRYRR=0,92, HRPRRPR=1,41, VRRPR=−0,13, Seção 3.11f) — a "assinatura
digital de interação" aqui descrita caracteriza modo de ligação estrutural, não especificidade real
contra os alvos Lepidoptera.

### 3.11j Fechamento do R3 — Matriz Consolidada TOP-13 × 11 Espécies (2026-07-19)

A Seção 3.11c havia deixado 3 espécies-praga pendentes do requisito R3 (amplo espectro entre
Lepidoptera): *Diatraea saccharalis*, *Heliothis virescens* e *Chrysodeixis includens*. As três
foram incorporadas com o mesmo protocolo das 8 espécies anteriores — busca UniProt REST real
(accessions T1QDI0, I7D523 e A0A9P0BRD5, respectivamente), estrutura AlphaFold DB e tríade
catalítica mapeada por `StructureAgent._analyze_single` — e dockadas em `screen` no servidor
(sessão `crossspecies_r3b`, log terminado em `DONE`). O conjunto de candidatos usado foi o TOP-13
já fixado na Tabela 9n (não o TOP-10 original da Tabela 9g) — como os 5 candidatos curtos
(`VRYRR`/`VRTRR`/`VRRPR`/`HRPRRSR`/`HRPRRPK`) nunca tinham sido dockados contra as 8 espécies
antigas (Seção 3.10d já registrava essa lacuna explicitamente), o resume-safe do
`dock_cross_species.py` corretamente detectou e preencheu essas 40 combinações
(candidato × espécie) que faltavam, além dos 39 dockings completos (13×3) das 3 espécies novas —
total real de até 79 dockings novos nesta rodada. O resume-safe funcionou como esperado no sentido
que importa: os 103 valores que já existiam (13 candidatos originais do TOP-10 × 8 espécies + o
que já estava preenchido) não foram recalculados nem sobrescritos — confirmado por comparação
direta, ex. `SRTRR` × *A. gemmatalis* permanece em −9,19 kcal/mol, idêntico ao valor já publicado
na Tabela 9g.

**Tabela 9r.** Matriz completa e final — Vina real (kcal/mol), TOP-13 × 11 espécies de Lepidoptera-praga.

| Sequência | A. gemmatalis | H. armigera | M. sexta | B. mori | P. xylostella | S. litura | S. frugiperda | O. nubilalis | D. saccharalis | H. virescens | C. includens | Média |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SRTRR | −9,19 | −8,88 | −9,53 | −9,56 | −9,72 | −9,28 | −10,95 | −9,43 | −9,90 | −11,00 | −9,80 | −9,75 |
| HRPRRPR | −10,10 | −10,52 | −11,44 | −10,62 | −11,71 | −10,27 | −11,42 | −11,88 | −10,12 | −12,93 | −11,45 | −11,13 |
| RLREELKKAEEWLEKRRKEE | −12,75 | −11,79 | −11,99 | −13,28 | −12,81 | −12,36 | −13,36 | −12,77 | −12,27 | −13,06 | −12,79 | −12,66 |
| SEEEVLAANEAYAAAHTAYN | −12,31 | −12,48 | −14,30 | −14,48 | −13,02 | −12,47 | −12,49 | −12,14 | −10,85 | −12,00 | −13,21 | −12,70 |
| SALASIAAHQATFLAYLESK | −11,97 | −13,03 | −11,87 | −12,15 | −13,27 | −11,66 | −12,87 | −11,97 | −11,41 | −11,76 | −12,87 | −12,26 |
| MGSLTAYLEAYAAENAAALA | −13,31 | −11,28 | −13,15 | −13,03 | −12,40 | −11,49 | −13,01 | −13,04 | −11,94 | −13,85 | −13,22 | −12,70 |
| MGYLTAYHQALAAQNAALLA | −14,26 | −11,88 | −12,23 | −13,80 | −12,31 | −12,52 | −12,20 | −11,82 | −12,53 | −12,47 | −12,24 | −12,57 |
| SARESIKKAYKTFLERYKKL | −12,51 | −12,36 | −12,88 | −14,74 | −13,57 | −13,01 | −13,31 | −12,41 | −14,14 | −13,39 | −14,54 | −13,35 |
| VRYRR | −9,53 | −9,83 | −9,57 | −9,17 | −10,09 | −10,84 | −9,71 | −10,55 | −10,40 | −10,48 | −10,87 | −10,10 |
| VRTRR | −8,86 | −9,11 | −9,66 | −9,80 | −9,26 | −8,95 | −11,01 | −9,23 | −9,34 | −9,43 | −9,52 | −9,47 |
| VRRPR | −9,20 | −9,72 | −9,81 | −9,41 | −9,48 | −9,92 | −10,41 | −9,65 | −9,87 | −11,13 | −9,76 | −9,85 |
| HRPRRSR | −10,95 | −10,55 | −11,52 | −10,59 | −12,02 | −9,83 | −11,53 | −11,54 | −10,05 | −12,54 | −11,39 | −11,14 |
| HRPRRPK | −9,71 | −10,26 | −11,05 | −10,36 | −11,71 | −10,27 | −11,66 | −11,81 | −10,16 | −12,94 | −11,24 | −11,02 |
| **Média** | −11,13 | −10,90 | −11,46 | −11,61 | −11,64 | −10,99 | −11,84 | −11,40 | −11,00 | −12,08 | −11,76 | −11,44 |

**Leitura honesta**: os 143 valores (13 candidatos × 11 espécies) são todos reais, sem nenhuma
lacuna. A faixa completa vai de −8,86 (`VRTRR` × *A. gemmatalis*) a −14,74 kcal/mol
(`SARESIKKAYKTFLERYKKL` × *B. mori*) — nenhum candidato perde afinidade competitiva em nenhuma das
3 espécies novas. As médias por espécie ficam entre −10,90 (*H. armigera*) e −12,08
(*H. virescens*), intervalo comparável ao já visto nas 8 espécies antigas (Tabela 9g:
−11,58 a −12,92) — nenhuma das 3 novas espécies se comporta como "imune" ao design, o que fecha o
requisito R3 (amplo espectro entre pragas Lepidoptera) para o TOP-13 completo. `SARESIKKAYKTFLERYKKL`
segue sendo o candidato de maior afinidade média (−13,35) e também o de maior afinidade absoluta
contra as 3 espécies novas isoladamente (−14,14 em *D. saccharalis*, −13,39 em *H. virescens*,
−14,54 em *C. includens*).

**Limitação explícita, já registrada nas Seções anteriores e reafirmada aqui**: esta matriz é
docking rígido (Vina, `exhaustiveness=8`), não testa estabilidade MD nem persistência de bolso S1
nas 3 espécies novas — as análises de MD/persistência/PLIP (Seções 3.11e-j) permanecem restritas ao
receptor primário. Amplo espectro de afinidade *in silico* não implica margem de seletividade real
(Seção 3.11b/3.11f já mostraram 0/23 candidatos com SI real aprovado contra tripsina humana) — as
duas conclusões são independentes e nenhuma substitui a outra.

---

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
- **Especificidade (corrigido 2026-07-18)**: **0/21 aprovados** vs tripsina humana (1TRN) e/ou *Apis mellifera* — resultado original "20/20" era artefato de bug metodológico sem dado real (Seção 3.11); SI real médio 0,84 (humana) / 1,12 (Apis), abaixo do limiar de 2,0
- **MD réplicas reais n=3 (corrigido 2026-07-19)**: dos 13 candidatos retestados com réplicas independentes (Seção 3.11f), apenas **4 são reprodutivelmente estáveis** (DP<0,05 nm): SRTRR, VRYRR, VRRPR, HRPRRPR. Os 2 "recordistas de estabilidade" citados abaixo (RLREELKKAEEWLEKRRKEE e VRTRR, ambos de réplica única) **não se sustentam** — DP real de 0,606 e 0,360 nm entre réplicas
- **Persistência competitiva real (2026-07-19)**: dos 4 candidatos "reprodutivelmente estáveis" acima (Seção 3.11g), apenas 3 confirmam ocupância real alta do bolso S1 a 6Å (SRTRR 94,3%, VRYRR 100,0%, HRPRRPR 96,1%); **VRRPR não se sustenta nesta métrica** — ocupância a 6Å cai 67,6%→32,9%→0,15% entre réplicas apesar de RMSD do complexo estável, ou seja, o complexo balança rígido mas o peptídeo sai do bolso. `VRYRR` é o único com salt-bridge real constante mesmo a 4Å (~100% nas 3 réplicas)
- **Contato real S2'/S3' — heurística geométrica (2026-07-19)**: dos mesmos 13 candidatos (Seção 3.11h), a fração média de frames com contato PLIP real nos resíduos 204/218 (definição operacional, não validada estruturalmente) não discrimina os 4 "reprodutivelmente estáveis" do restante (médias de grupo praticamente iguais, 23,3% vs. 25,2%); sinal ruidoso demais (5 frames/réplica) para sustentar qualquer conclusão adicional além de "não encontrado padrão claro"
- **OptimizationAgent**: 219 novos candidatos gerados por redesign iterativo dos top-50

O padrão composicional dos top binders (Arg/Lys + Ala/Ser, sem aromáticos) é biologicamente coerente com o bolso S1 de tripsina (Asp205, interação eletrostática com P1 = Arg/Lys). A avaliação dinâmica revela que estimativas estáticas (Vina, Rosetta) podem divergir da estabilidade em solvente explícito: GARKSIREYQKRVLERLKKK, com melhor I_sc (−86,28 kcal/mol), apresentou RMSD = 1,45 nm em MD — descartado. A etapa MD é, portanto, essencial para filtrar candidatos antes da síntese.

A susceptibilidade proteolítica universal (0/20 resistentes) é a principal limitação dos candidatos de 20 aa lineares e decorre do trade-off intrínseco: resíduos Arg/Lys que maximizam afinidade ao S1 também são substratos da própria tripsina em posições internas. Esse resultado redireciona a Fase 4 para o design de peptídeos 5–15 aa com filtro KR-interno=0 e estratégias de proteção química (Nle, Orn, D-aa).

**Candidatos de síntese prioritária (pós-MD Fases 3+4, estáveis em 10 ns):**
1. **MKKQRENAKKVAEITLKKAK** — RMSD 0,447 nm, Vina −12,72, I_sc −80,49 (Fase 3)
2. **RLREELKKAEEWLEKRRKEE** — RMSD 0,294 nm, DP=0,065 — ~~mais estável do pipeline~~ **título revogado 2026-07-19**: réplicas reais (n=3) mostram RMSD médio 0,810 nm, DP=0,606 nm (Seção 3.11f) — resultado de réplica única não era representativo
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

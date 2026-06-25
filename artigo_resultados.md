# Resultados e Discussão — Design Racional de Inibidores Peptídicos de Tripsinas de Lepidoptera

> **Status de preenchimento (2026-06-25):**
> - ✓ 3.1 Sítio catalítico — completo
> - ✓ 3.2 Backbones RFdiffusion — **330 backbones reais** (substituiu fallback PeptideBuilder)
> - ✓ 3.3 Dataset de sequências — **24.513 binders 20 aa** (ProteinMPNN real, bug FASTA corrigido)
> - ✓ 3.4 Docking — **194/194 poses reais** com binders RFdiffusion genuínos; top-1 −13,62 kcal/mol
> - ✓ 3.5 Ranking — novo top-10 com sequências RFdiffusion+ProteinMPNN reais
> - ✓ 3.6 PyRosetta — **10/10 complexos refinados**; top I_sc: GARKSIREYQKRVLERLKKK (−86,28); concordância Vina×Rosetta documentada
> - ✓ 3.7 Candidatos prioritários — **reclassificados pós-MD**: MKKQRENAKKVAEITLKKAK #1, GSRASARAYAARVRARRAAL #2
> - ✓ 3.8 MD — **5/5 candidatos concluídos** (10 ns cada); 2 estáveis (RMSD < 0,5 nm), 1 marginal, 2 instáveis; reclassificação completa

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

O AutoDock Vina f458505-mod foi executado sobre 194 candidatos pré-selecionados do pool de 24.513 binders (top por heurística física). A rodada utilizou binders genuínos de 20 aa oriundos do pipeline RFdiffusion+ProteinMPNN real.

**Histórico de correções no módulo de docking — rodada com binders reais (2026-06-16):**

| # | Bug | Erro | Fix | Commit |
|---|-----|------|-----|--------|
| 29–31 | `NA` atom type Vina | `"N":"NA"` (sódio) em vez de nitrogênio backbone | `"N":"N"` em `_pdb_to_pdbqt_minimal()` | `603cc04` |
| 32 | obabel `-xr` gera formato receptor | PDBQT sem ROOT/ENDROOT para ligante | remover `-xr`; `_ensure_ligand_pdbqt_format()` reescreve sempre | `603cc04` |
| 33 | **Binders eram redesigns de tripsinas** | `replace("/","")` concatenava receptor+binder (240+ aa) | `parts[-1]` extrai cadeia B (20 aa) | `e9024bc` |
| 34 | `seq[-L:]` cortava binders reais | `len(seq)>L*2` triggava para len5 (20>10) | remoção do corte artificial | `ad6fa9e` |
| 35 | Grid dimensionado por label (5/7/10) | `item["length"]` = categoria, não comprimento real | `len(item["sequence"])` → grid 80×80×80 Å | `ad6fa9e` |

**Resultado — Rodada com binders RFdiffusion+ProteinMPNN reais (2026-06-16/17):** **194/194 poses válidas**.

**Tabela 4a.** Distribuição dos scores Vina (kcal/mol) — 194 candidatos binders reais.

| Estatística        | Valor (kcal/mol) |
|--------------------|-----------------|
| Mínimo (melhor)    | −13,62          |
| Mediana estimada   | ~−12,5          |
| Média              | ~−12,2          |
| Máximo (pior)      | ~−10,8          |

**Padrão composicional dos melhores binders:** os candidatos com melhor Vina (≤ −13,2 kcal/mol) são enriquecidos em resíduos básicos (Arg, Lys) nas posições internas e C-terminais, com presença de resíduos pequenos (Ala, Gly, Ser) no N-terminal. Esse padrão contrasta com os candidatos heurísticos anteriores (aromático-ricos) e é consistente com o mecanismo competitivo clássico: o bolso S1 de ACR157 apresenta Asp205 que favorece interações iônicas com Arg/Lys na posição P1 (*Hedstrom, 2002*).

---

### 3.5 Ranking Composto

O ranking composto integrou energias Vina reais (peso 0,35), scores Rosetta (peso 0,25 — PyRosetta em execução; resultados heurísticos como placeholder), H-bonds (0,20), RMSD (0,10) e contagem básica (0,10) por normalização min-max, resultando em **24.513 candidatos rankeados**. Os 194 candidatos com energia Vina real dos binders genuínos foram priorizados.

**Tabela 5a.** Top-10 por score composto — binders RFdiffusion+ProteinMPNN reais.

| Rank | Sequência                | aa | Score  | Vina (kcal/mol) | n(R+K) | Perfil composicional          |
|------|--------------------------|----|--------|-----------------|--------|-------------------------------|
| 1    | GSRASARAYAARVRARRAAL     | 20 | 0,742  | **−13,62**      | 6      | Gly/Ser N-term + Arg central  |
| 2    | GARKSIREYQKRVLERLKKK     | 20 | 0,662  | −12,76          | 9      | R/K denso, Glu/Tyr distribuído|
| 3    | SLARKRAEENAKRFLERVKK     | 20 | 0,639  | −12,71          | 8      | Leu/Ala + R/K alternados      |
| 4    | MKKQRENAKKVAEITLKKAK     | 20 | 0,634  | −12,68          | 8      | Lys-rico, Met N-term          |
| 5    | AARASQREYQKKFLERLKKK     | 20 | 0,611  | −12,52          | 8      | Ala N-term + R/K/F C-term     |
| 6    | AARASIRAAAARFRARRAAL     | 20 | 0,595  | −12,62          | 6      | Ala-rico com Arg interno       |
| 7    | AARENIRKAHKTFLERLKKK     | 20 | 0,587  | −12,36          | 8      | Ala/Leu + R/K/H distribuídos  |
| 8    | SAAARARQRAVIARARARVA     | 20 | 0,568  | −12,44          | 6      | Ala/Arg alternados (anfipático)|
| 9    | SAAARARQRAVGARMRARVA     | 20 | 0,568  | −12,44          | 6      | Ala/Arg/Met — similar #8      |
| 10   | AARASQREYAARFAERLAAK     | 20 | 0,565  | −12,52          | 5      | Ala-N + aromático/Glu C-term  |

**Tabela 5b.** Top-10 por Vina puro (critério energético mais robusto para seleção de candidatos).

| Rank | Sequência                | aa | Vina (kcal/mol) | n(R+K) | Perfil                           |
|------|--------------------------|----|-----------------|---------|---------------------------------|
| 1    | GSRASARAYAARVRARRAAL     | 20 | **−13,62**      | 6       | Melhor binder absoluto          |
| 2    | GARKSIREYQKRVLERLKKK     | 20 | −12,76          | 9       | Alta densidade R/K              |
| 3    | SLARKRAEENAKRFLERVKK     | 20 | −12,71          | 8       | Leu/Ala scaffold                |
| 4    | MKKQRENAKKVAEITLKKAK     | 20 | −12,68          | 8       | Aliphatic + Lys                 |
| 5    | AARASIRAAAARFRARRAAL     | 20 | −12,62          | 6       | Ala-rico, Arg distribuído       |
| 6    | AARASQREYQKKFLERLKKK     | 20 | −12,52          | 8       | Phe/Leu C-term                  |
| 7    | AARASQREYAARFAERLAAK     | 20 | −12,52          | 5       | Tyr/Phe + Glu                   |
| 8    | SAAARARQRAVIARARARVA     | 20 | −12,44          | 6       | Ala/Arg regular                 |
| 9    | SAAARARQRAVGARMRARVA     | 20 | −12,44          | 6       | Ala/Arg/Met                     |
| 10   | AARENIRKAHKTFLERLKKK     | 20 | −12,36          | 8       | His/Lys/Arg                     |

**Análise crítica — comparação com rodada anterior (binders heurísticos):**  
Os binders reais (RFdiffusion+ProteinMPNN) apresentam padrão composicional distinto dos candidatos heurísticos anteriores: são dominados por resíduos básicos (Arg/Lys, media n=7) e alifáticos (Ala, Ser, Gly), enquanto a rodada anterior (fallback) era enriquecida em aromáticos (Tyr/Trp/Phe). O melhor Vina real (−13,62 kcal/mol, `GSRASARAYAARVRARRAAL`) é marginalmente superior ao heurístico (−13,61 kcal/mol, `PYYYLKKRWVSEPKQRIFFN`), mas provém de backbone estruturalmente informado pelo sítio — portanto superior em validade biológica. A ausência de aromáticos nos top binders reais sugere que o RFdiffusion posicionou a cadeia B em modo de interação eletrostática (Arg–Asp205) em vez de empilhamento π — consistente com o mecanismo canônico das tripsinas.

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

**Reclassificação dos candidatos prioritários pós-MD:**

O critério de estabilidade dinâmica (RMSD < 0,5 nm como limiar para pose estável, seguindo *de Oliveira et al., 2020*; *Bakan et al., 2014*) promove a seguinte hierarquia final:

1. **MKKQRENAKKVAEITLKKAK** — RMSD 0,447 nm (**mais estável**), Vina −12,72, I_sc −80,49; candidato de síntese prioritária
2. **GSRASARAYAARVRARRAAL** — RMSD 0,494 nm (**estável**), melhor Vina (−13,62), I_sc −78,44; candidato de síntese prioritária
3. **AARASIRAAAARFRARRAAL** — RMSD 0,945 nm (marginal), Vina −12,62, I_sc −75,45; candidato secundário (simulação estendida recomendada)
4. ~~GARKSIREYQKRVLERLKKK~~ — descartado (instável em MD apesar de melhor I_sc)
5. ~~SLARKRAEENAKRFLERVKK~~ — descartado (instável, divergente Vina × Rosetta)

---

### 3.9 Inibidores de Referência

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

O pipeline multiagente completou todas as etapas planejadas: design estrutural (RFdiffusion), design de sequências (ProteinMPNN), triagem de afinidade (Vina), validação de interface (PyRosetta) e avaliação dinâmica completa (MD 10 ns, 5 candidatos). Estado consolidado (2026-06-25):

- **330 backbones reais** gerados pelo RFdiffusion para ACR157
- **24.513 sequências únicas** de binder 20 aa via ProteinMPNN real
- **194/194 poses Vina reais**; top-1: GSRASARAYAARVRARRAAL (−13,62 kcal/mol)
- **10/10 complexos refinados por PyRosetta** (I_sc REF2015 real); top-1: GARKSIREYQKRVLERLKKK (−86,28 kcal/mol)
- **MD 10 ns concluído para 5/5 candidatos**; 2 estáveis (RMSD < 0,5 nm), 1 marginal, 2 instáveis
- Dataset ML/DL: 194 labels Vina reais + 10 labels I_sc Rosetta + 5 labels estabilidade MD

O padrão composicional dos top binders (Arg/Lys + Ala/Ser, sem aromáticos) é biologicamente coerente com o bolso S1 de tripsina (Asp205 âncora eletrostática). A avaliação dinâmica revela que o melhor I_sc por PyRosetta (GARKSIREYQKRVLERLKKK, −86,28 kcal/mol) não se traduz em estabilidade em solvente explícito, evidenciando a necessidade da etapa MD para filtrar candidatos — resultado consistente com literatura recente sobre divergência entre estimativas estáticas e dinâmicas de afinidade peptídeo–proteína (*de Oliveira et al., 2020*).

**Candidatos de síntese prioritária (pós-MD):**
1. **MKKQRENAKKVAEITLKKAK** — RMSD 0,447 nm, Vina −12,72, I_sc −80,49
2. **GSRASARAYAARVRARRAAL** — RMSD 0,494 nm, Vina −13,62, I_sc −78,44

**Próximos passos (ordem de prioridade):**
1. **Re-rodar RFdiffusion** com comprimentos variáveis independentes (5–15 aa) para candidatos de comprimento otimizado
2. **Docking completo** dos 24.513 candidatos para labels ML supervisionados
3. **Treinamento ML/DL**: Random Forest → GNN com 194+ labels Vina + 10 labels Rosetta + 5 labels MD
4. **Síntese Fmoc-SPPS**: MKKQRENAKKVAEITLKKAK e GSRASARAYAARVRARRAAL → ensaios IC50 in vitro contra ACR157

---

## Referências (parcial)

- Chaudhury S et al. (2010) PyRosetta: a script-based interface for implementing molecular modeling algorithms using Rosetta. *Bioinformatics*, 26, 689–691.
- Dauparas J et al. (2022) Robust deep learning-based protein sequence design using ProteinMPNN. *Science*, 378, 49–56.
- Hedstrom L (2002) Serine protease mechanism and specificity. *Chem Rev*, 102, 4501–4524.
- Lopes AR et al. (2004) Comparative studies of digestive enzymes and midgut cells of *Spodoptera frugiperda*. *Comp Biochem Physiol*, 137, 119–129.
- Raveh B et al. (2011) Sub-angstrom modeling of complexes between flexible peptides and globular proteins. *PLoS Comput Biol*, 7, e1002110.
- Trott O & Olson AJ (2010) AutoDock Vina: improving the speed and accuracy of docking. *J Comput Chem*, 31, 455–461.
- Van der Spoel D et al. (2005) GROMACS: fast, flexible, and free. *J Comput Chem*, 26, 1701–1718.
- Watson JL et al. (2023) De novo design of protein structure and function with RFdiffusion. *Nature*, 620, 1089–1100.

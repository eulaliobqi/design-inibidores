# Resultados e Discussão — Design Racional de Inibidores Peptídicos de Tripsinas de Lepidoptera

> **Status de preenchimento (2026-06-10):**
> - ✓ 3.1 Sítio catalítico — completo
> - ✓ 3.2 Backbones — completo (modo fallback)
> - ✓ 3.3 Dataset de sequências — completo (14.923 seqs, 41 features)
> - ✓ 3.4 Docking heurístico — completo (14.923 poses)
> - ◑ 3.5 Ranking — completo heurístico; aguarda Vina/Rosetta reais
> - ✗ 3.6 MD — aguarda Vina instalado para selecionar top candidatos reais
> - ✗ 3.7 Candidatos prioritários — aguarda scores reais

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

Na ausência do AutoDock Vina instalado, as 14.923 sequências únicas receberam **scores heurísticos de afinidade** calculados como função multi-fator:

$$\hat{E}_{dock} = -(n_{RK} \times 1{,}2 + f_{H} \times n \times 0{,}5 + |B| \times 0{,}3 + n \times 0{,}1)$$

onde $n_{RK}$ = número de Arg+Lys, $f_H$ = fração hidrofóbica, $B$ = índice de Boman, $n$ = comprimento. Esses scores constituem **labels proxy** para o treinamento inicial de modelos ML; a instalação do Vina substituirá esses valores por energias de docking físicas (kcal/mol).

**14.923 poses heurísticas** foram calculadas e armazenadas em `outputs/docking/docking_results.json`. Os scores foram integrados ao dataset ML CSV nas colunas `vina_affinity_kcal` e `final_score`.

---

### 3.5 Ranking Composto

O ranking integrou scores de docking heurístico, Rosetta (10 candidatos) e propriedades físico-químicas por normalização min-max, resultando em **14.923 candidatos rankeados**.

**Tabela 5.** Top-10 candidatos por score composto heurístico.

| Rank | Sequência              | Tam (aa) | Score | n(R+K) | Frac. Hidrofóbica |
|------|------------------------|----------|-------|--------|-------------------|
| 1    | RMKERAVVKLRRMIKRWRRE   | 20       | 0,988 | 10     | 0,35              |
| 2    | DRRIIKRFGVSQKRTRVMKQ   | 20       | 0,720 | 7      | 0,35              |
| 3    | WALRKVHVKRRMRRTIWIIS   | 20       | 0,687 | 8      | 0,40              |
| 4    | IRKDFVETIRWKKWTTKIKI   | 20       | 0,639 | 6      | 0,40              |
| 5    | IMQTAAPFWNNFRRRKRKRS   | 20       | 0,601 | 6      | 0,35              |
| 6–20 | *a completar após ranking completo* | | | | |

**Nota interpretativa:** O top-ranking heurístico é dominado por peptídeos de 20 aa com alta densidade de R/K, pois o score heurístico favorece resíduos básicos por contagens absolutas. Este viés é esperado e intrínseco ao modo fallback — não reflete necessariamente o ranking por scores Vina/Rosetta reais, onde peptídeos curtos com melhor complementaridade geométrica podem superar os de 20 aa. O dataset ML permitirá treinar modelos que corrijam esse viés.

---

### 3.6 Estabilidade por Dinâmica Molecular

*[Aguarda instalação do Vina para seleção dos top candidatos reais antes da MD]*

Os cinco melhores candidatos reais por modelo de tripsina serão submetidos a simulações de DM de 10 ns com GROMACS (AMBER99SB-ILDN, TIP3P, 300 K). O servidor dispõe de `gmx_mpi` (CUDA-MPI, RTX 5070 Ti).

---

### 3.7 Candidatos Prioritários para Síntese

*[A completar após instalação das ferramentas reais — Vina + Rosetta]*

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

O pipeline multiagente foi executado com sucesso em modo *fallback* heurístico, produzindo:
- **30 backbones** em 6 comprimentos (5–20 aa)
- **14.923 sequências únicas** com 41 features físico-químicas
- Dataset ML/DL (`ml_training_dataset.csv`) com labels proxy de docking e score composto

A variante XP273 foi identificada como alvo atípico, justificando a remoção da restrição P1=Arg/Lys e a inclusão de estratégias hidrofóbicas no gerador de sequências.

O próximo passo crítico é a instalação do AutoDock Vina no servidor para substituição dos labels proxy por energias de docking reais, que constitui o dado supervisionado primário para treinamento dos modelos ML/DL.

---

## Referências (parcial)

- Dauparas J et al. (2022) Robust deep learning-based protein sequence design using ProteinMPNN. *Science*, 378, 49–56.
- Hedstrom L (2002) Serine protease mechanism and specificity. *Chem Rev*, 102, 4501–4524.
- Lopes AR et al. (2004) Comparative studies of digestive enzymes and midgut cells of *Spodoptera frugiperda*. *Comp Biochem Physiol*, 137, 119–129.
- Raveh B et al. (2011) Sub-angstrom modeling of complexes between flexible peptides and globular proteins. *PLoS Comput Biol*, 7, e1002110.
- Trott O & Olson AJ (2010) AutoDock Vina: improving the speed and accuracy of docking. *J Comput Chem*, 31, 455–461.
- Van der Spoel D et al. (2005) GROMACS: fast, flexible, and free. *J Comput Chem*, 26, 1701–1718.
- Watson JL et al. (2023) De novo design of protein structure and function with RFdiffusion. *Nature*, 620, 1089–1100.

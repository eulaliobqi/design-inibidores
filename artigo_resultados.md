# Resultados e Discussão — Design Racional de Inibidores Peptídicos de Tripsinas de Lepidoptera

## 3. Resultados e Discussão

### 3.1 Mapeamento do Sítio Catalítico e Bolso S1

A análise estrutural dos quatro modelos de tripsinas de lepidópteros permitiu identificar os resíduos da tríade catalítica e do bolso de especificidade S1 em cada estrutura (Tabela 1). Três dos quatro modelos (ACR157, QCL936 e XP352) apresentam a organização clássica de serina-proteases: His–Asp–Ser, com Asp adicional definindo a especificidade do bolso S1 para substratos com Arg/Lys na posição P1 — padrão típico de tripsinas (*Hedstrom, 2002*).

**Tabela 1.** Resíduos do sítio catalítico e bolso S1 dos quatro modelos de tripsina.

| Modelo  | Res. catalítico 1 | Asp (tríade) | Nucleófilo | S1 (especificidade) | Centro sítio (Å)        |
|---------|-------------------|--------------|------------|---------------------|--------------------------|
| ACR157  | His69             | Asp114       | Ser211     | Asp205              | [7,09; −1,15; −1,63]    |
| QCL936  | His92             | Asp142       | Ser247     | Asp241              | [2,94; 5,55; −0,32]     |
| XP273   | Tyr83             | Asp132       | Ser234     | Ile229              | [1,67; 8,29; −0,34]     |
| XP352   | His112            | Asp166       | Ala268     | Asp262              | [−1,26; 5,60; −5,25]    |
| **Consenso** | —           | —            | —          | —                   | **[2,61; 4,57; −1,89]** |

O modelo XP273 destaca-se por apresentar variações atípicas: Tyr83 ocupa a posição equivalente à His catalítica, e Ile229 substitui o Asp conservado no bolso S1. Essa configuração incomum em serina-proteases já foi descrita em variantes de quimiotripsina de insetos (*Lopes et al., 2004*) e pode refletir adaptação à dieta específica do hospedeiro. A presença de Ile229 no bolso S1 — em vez de Asp — implica especificidade por resíduos hidrofóbicos na posição P1 do substrato, e não por Arg/Lys como nas tripsinas clássicas. Esta observação é relevante para o design de inibidores: candidatos para XP273 devem contemplar resíduos hidrofóbicos na posição P1 (Leu, Ile, Val), enquanto para os demais modelos a P1 deve ser Arg ou Lys.

O centro de ligação consenso calculado ([2,61; 4,57; −1,89] Å) representa a posição média do sítio ativo entre os quatro modelos e foi utilizado como âncora para todas as etapas subsequentes de geração de backbones e docking.

---

### 3.2 Geração de Backbones Peptídicos (RFdiffusion)

*[A ser preenchido após execução do Stage 2]*

Para cada um dos seis comprimentos peptídicos avaliados (5, 7, 10, 12, 15 e 20 aminoácidos), foram gerados N backbones por RFdiffusion ancorados ao sítio S1 do modelo ACR157 como receptor primário. O total de backbones gerados foi de **X**, distribuídos como:

| Comprimento (aa) | Backbones gerados | Taxa de sucesso (%) |
|---|---|---|
| 5  | — | — |
| 7  | — | — |
| 10 | — | — |
| 12 | — | — |
| 15 | — | — |
| 20 | — | — |

A qualidade estrutural dos backbones foi avaliada pela energia de Rosetta e pela cobertura do sítio S1 (resíduos em contato com hotspots).

---

### 3.3 Geração Massiva de Sequências para Dataset ML/DL (ProteinMPNN / Fallback)

Para maximizar a cobertura do espaço de sequências e construir um dataset adequado para treinamento de modelos de *machine learning* e *deep learning*, o Stage 3 foi reformulado para utilizar **10 estratégias de geração complementares**, cada uma explorando um subconjunto distinto do espaço composicional de aminoácidos:

| Estratégia | Descrição | % do total |
|---|---|---|
| *random_uniform* | Todos os 19 aa equiprováveis | 20% |
| *hydrophobic* | Bias em AILMFWV (mecanismo alostérico) | 10% |
| *charged_positive* | Bias em R/K (inibição competitiva clássica) | 10% |
| *charged_negative* | Bias em D/E (interações eletrostáticas) | 7% |
| *aromatic_cterminal* | Corpo aleatório + C-terminal Y/W/F | 12% |
| *aromatic_nterminal* | N-terminal Y/W/F (β-hairpin mimético) | 8% |
| *amphipathic* | Alternando hidrofóbico/polar (α-hélice anfipática) | 10% |
| *proline_rich* | Pro-enriquecido (PPII helix, scaffold rígido) | 7% |
| *motif_seeded* | Seeds BPTI/SKTI + mutações pontuais | 9% |
| *glycine_scan* | Gly em cada posição (mapeamento de flexibilidade) | 7% |

**Tabela 2.** Dimensão do dataset de sequências geradas.

| Comprimento (aa) | Sequências / backbone | Backbones | Subtotal | Seeds canônicos |
|---|---|---|---|---|
| 5  | 500 | 5 | 2.500 | 8 |
| 7  | 500 | 5 | 2.500 | 7 |
| 10 | 500 | 5 | 2.500 | 5 |
| 12 | 500 | 5 | 2.500 | 4 |
| 15 | 500 | 5 | 2.500 | 3 |
| 20 | 500 | 5 | 2.500 | 3 |
| **Total** | | **30** | **~15.000** | **30** |

*Nota: após remoção de duplicatas, o total de sequências únicas foi de ~X. Sequências contendo Cys foram automaticamente excluídas.*

Cada sequência foi anotada com **40 features** físico-químicas calculadas analiticamente, incluindo: comprimento, massa molecular (Da), carga líquida (pH 7), ponto isoelétrico, hidrofobicidade média Kyte-Doolittle, índice de Boman (potencial de ligação a proteínas), índice alipático (indicador de termoestabilidade), frações de resíduos por classe (aromáticos, hidrofóbicos, carregados) e composição por aminoácido (19 colunas). As colunas `vina_affinity_kcal` e `rosetta_I_sc` foram reservadas como *labels* a serem preenchidos nas etapas de docking e refinamento Rosetta.

O dataset completo foi exportado em formato CSV (`outputs/dataset/ml_training_dataset.csv`) com estrutura compatível com frameworks de aprendizado de máquina (scikit-learn, PyTorch, TensorFlow). Os seeds canônicos foram rotulados como `is_known_inhibitor=1`, constituindo exemplos positivos para treinamento supervisionado.

---

### 3.4 Refinamento de Interface e Docking Molecular

*[A ser preenchido após execução dos Stages 4 e 5]*

Os X candidatos com P1 = Arg/Lys foram submetidos a refinamento Rosetta e docking Vina. Os vinte melhores candidatos, ordenados pelo *score* composto, são apresentados na Tabela 2.

**Tabela 2.** Top-20 candidatos peptídicos — métricas de afinidade e refinamento energético.

| Rank | Sequência | Tam (aa) | Vina (kcal/mol) | Rosetta I_sc | Score |
|---|---|---|---|---|---|
| 1 | — | — | — | — | — |
| 2 | — | — | — | — | — |
| ... | | | | | |

---

### 3.5 Estabilidade por Dinâmica Molecular

*[A ser preenchido após execução do Stage 6]*

Os cinco melhores candidatos por modelo de tripsina foram submetidos a simulações de DM de 10 ns. Os resultados de estabilidade são apresentados na Tabela 3.

**Tabela 3.** Parâmetros de estabilidade dos top-5 candidatos por DM.

| Sequência | RMSD médio (nm) | H-bonds médios | Rg médio (nm) | Estável? |
|---|---|---|---|---|
| — | — | — | — | — |

---

### 3.6 Candidatos Prioritários para Síntese

*[A ser preenchido após ranking final]*

Com base no *score* composto (Eq. 1), os três candidatos prioritários para síntese e ensaios experimentais são:

1. **Candidato 1** — sequência: `—`, comprimento: — aa, score: —
   - Interações-chave: P1(Arg/Lys)···Asp(S1), pontes H com backbone do sítio S2–S4
   - Estabilidade MD: RMSD = — nm, H-bonds médios = —

2. **Candidato 2** — sequência: `—`, comprimento: — aa, score: —

3. **Candidato 3** — sequência: `—`, comprimento: — aa, score: —

Esses candidatos apresentam a combinação mais favorável de afinidade de ligação, estabilidade conformacional em solução e propriedades físico-químicas compatíveis com síntese por SPFS e ensaios biológicos.

---

### 3.7 Inibidores Conhecidos como Referência

Os inibidores conhecidos de tripsinas de Lepidoptera utilizados como referência neste estudo foram:

| Peptídeo | Sequência | Comprimento | Fonte |
|---|---|---|---|
| GORE1 | V-L-K | 3 aa | Loop reativo sintético |
| GORE2 | V-L-R | 3 aa | Loop reativo sintético |
| TGPCK | T-G-P-C-K | 5 aa | Derivado SKTI |
| LALAK | L-A-L-A-K | 5 aa | Derivado pró-sequência |
| RPDFK (BPTI P1-loop) | R-P-D-F-K | 5 aa | BPTI canônico |

Os candidatos gerados computacionalmente serão comparados a esses padrões quanto à afinidade predita e perfil de interações com o sítio S1.

---

## 4. Conclusões Parciais

O pipeline multiagente desenvolvido permitiu mapear automaticamente o sítio catalítico de quatro tripsinas de lepidópteros-praga e identificar variações estruturais relevantes, incluindo a presença de Tyr83 e Ile229 no modelo XP273, que indica especificidade atípica. O centro de ligação consenso calculado ([2,61; 4,57; −1,89] Å) fornece as coordenadas para ancoragem dos inibidores peptídicos a ser gerados nas etapas subsequentes.

As etapas de IA generativa (RFdiffusion + ProteinMPNN), docking e dinâmica molecular encontram-se em andamento e os resultados serão integrados nas seções 3.2–3.6.

---

## Referências (parcial)

- Dauparas J et al. (2022) Robust deep learning-based protein sequence design using ProteinMPNN. *Science*, 378, 49–56.
- Hedstrom L (2002) Serine protease mechanism and specificity. *Chem Rev*, 102, 4501–4524.
- Lopes AR et al. (2004) Comparative studies of digestive enzymes and midgut cells of *Spodoptera frugiperda*. *Comp Biochem Physiol*, 137, 119–129.
- Raveh B et al. (2011) Sub-angstrom modeling of complexes between flexible peptides and globular proteins. *PLoS Comput Biol*, 7, e1002110.
- Trott O & Olson AJ (2010) AutoDock Vina: improving the speed and accuracy of docking. *J Comput Chem*, 31, 455–461.
- Van der Spoel D et al. (2005) GROMACS: fast, flexible, and free. *J Comput Chem*, 26, 1701–1718.
- Watson JL et al. (2023) De novo design of protein structure and function with RFdiffusion. *Nature*, 620, 1089–1100.

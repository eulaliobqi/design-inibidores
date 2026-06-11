# Metodologia Computacional — Design Racional de Inibidores Peptídicos de Tripsinas de Lepidoptera por IA Generativa

## 2. Material e Métodos

### 2.1 Estruturas-Alvo

Foram utilizados quatro modelos estruturais tridimensionais de tripsinas digestivas de lepidópteros-praga, denominados ACR157, QCL936, XP273 e XP352, obtidos por modelagem comparativa e refinamento por docking proteína-proteína (HADDOCK). As estruturas foram validadas previamente por análise geométrica (PROCHECK) e verificação de energia (VERIFY_3D).

### 2.2 Identificação do Sítio Catalítico e Bolso S1

O sítio ativo de cada tripsina foi mapeado com base nos resíduos catalíticos identificados por inspeção estrutural e verificação de conservação de sequência:

| Modelo  | Res. 1 (nucleofílico) | Asp (tríade) | Ser/Ala (tríade) | Esp. S1    |
|---------|----------------------|--------------|------------------|------------|
| ACR157  | His69                | Asp114       | Ser211           | Asp205     |
| QCL936  | His92                | Asp142       | Ser247           | Asp241     |
| XP273   | Tyr83*               | Asp132       | Ser234           | Ile229*    |
| XP352   | His112               | Asp166       | Ala268           | Asp262     |

*XP273 apresenta variações atípicas: Tyr83 em posição equivalente à His catalítica e Ile229 no bolso S1, sugerindo especificidade diferenciada das tripsinas canônicas.

As coordenadas cartesianas do centro de cada sítio foram calculadas como a média dos centróides dos resíduos da tríade. O centro de ligação consenso entre os quatro modelos:

**Centro consenso (X, Y, Z):** 2,607 / 4,572 / −1,885 Å

Os resíduos dentro de raio de 8,0 Å do centro consenso foram definidos como *hotspots* para ancoragem dos peptídeos.

### 2.3 Geração de Backbones Peptídicos por IA Generativa (RFdiffusion)

Backbones peptídicos foram gerados pelo modelo RFdiffusion (*Watson et al., Nature, 2023*), um modelo de difusão estrutural treinado para gerar conformações proteicas condicionadas a sítios de ligação. Para cada comprimento peptídico (5, 7, 10, 12, 15 e 20 aminoácidos), foram gerados 5 backbones independentes ancorados aos *hotspots* do sítio S1, totalizando 30 backbones.

O processo foi configurado com:
- `noise_scale_ca = 0.2` — ruído nas posições Cα
- `noise_scale_frame = 0.1` — ruído nos frames de orientação
- Mapa de contigs: `A1-N/0 L-L`, onde N = resíduos do receptor, L = comprimento peptídico
- Hotspot radius: 6,0 Å em torno do sítio S1

Na ausência do RFdiffusion instalado, o módulo opera em modo *fallback* gerando backbones lineares de poly-Ala via PeptideBuilder, posicionados nas coordenadas consenso do sítio, para não interromper o fluxo do pipeline.

### 2.4 Geração Massiva de Sequências para Dataset ML/DL

Para maximizar a cobertura do espaço de sequências e produzir um dataset para treinamento de modelos de *machine learning* e *deep learning*, o módulo ProteinMPNN (*Dauparas et al., Science, 2022*) foi configurado para gerar **500 sequências por backbone**, totalizando 15.000 candidatos brutos por rodada.

As sequências foram produzidas por **10 estratégias de geração complementares**:

| Estratégia          | Mecanismo de inibição explorado       | % orçamento |
|---------------------|---------------------------------------|-------------|
| *random_uniform*    | Cobertura uniforme do espaço          | 20%         |
| *hydrophobic*       | Inibição alostérica/hidrofóbica       | 10%         |
| *charged_positive*  | Inibição competitiva clássica (R/K)   | 10%         |
| *charged_negative*  | Interações eletrostáticas (D/E)       | 7%          |
| *aromatic_cterminal*| Contatos com subsítios S1'/S2'        | 12%         |
| *aromatic_nterminal*| β-hairpin mimético (Y/W/F N-term)     | 8%          |
| *amphipathic*       | α-hélice anfipática                   | 10%         |
| *proline_rich*      | Scaffold PPII rígido                  | 7%          |
| *motif_seeded*      | Seeds BPTI/SKTI + mutações pontuais   | 9%          |
| *glycine_scan*      | Mapeamento de flexibilidade (Gly)     | 7%          |

Sequências contendo Cys foram automaticamente excluídas. Os inibidores canônicos BPTI, SKTI e derivados foram incluídos como *seeds* em cada comprimento. Após remoção de duplicatas entre backbones do mesmo comprimento, o dataset final continha **14.923 sequências únicas**.

Não foram aplicadas restrições de aminoácido na posição P1, permitindo explorar mecanismos de inibição além do competitivo clássico (modulação alostérica, bloqueio estérico, inibição mista).

### 2.5 Anotação de Features Físico-Químicas para ML/DL

Cada sequência foi anotada com **41 features** calculadas analiticamente (sem dependência de ferramentas externas):

- **Massa molecular** (Da) — soma de massas residuais + H₂O
- **Carga líquida** (pH 7) — soma de contribuições ionizáveis
- **Ponto isoelétrico (pI)** — busca binária na curva de titulação (pK: Asp=3,65; Glu=4,25; His=6,00; Tyr=10,07; Lys=10,53; Arg=12,48)
- **Hidrofobicidade** (média escala Kyte-Doolittle)
- **Índice de Boman** — potencial de ligação a proteínas (*Boman, 2003*)
- **Índice alipático** — indicador de termoestabilidade (100 × [A + 2,9V + 3,9(I+L)] / n)
- **Índice de instabilidade** (aproximado)
- **Frações por classe:** aromáticos (Y/F/W/H), hidrofóbicos (A/I/L/M/F/W/V), carregados (R/K/D/E)
- **Composição por aminoácido:** fração de cada um dos 19 aminoácidos não-Cys
- **Features binárias:** presença de C-terminal aromático, N-terminal carregado, Pro

O dataset foi exportado em formato CSV (`outputs/dataset/ml_training_dataset.csv`) com colunas de label (`vina_affinity_kcal`, `rosetta_I_sc`, `final_score`) a serem preenchidas nas etapas de validação.

### 2.6 Refinamento de Interface por Rosetta

Os complexos tripsina-peptídeo foram submetidos a refinamento energético pelo protocolo FlexPepDock do Rosetta (*Raveh et al., PLoS Comp Biol, 2011*). Em modo *fallback*, os 10 melhores candidatos por heurística receberam scores estimados baseados em composição de aminoácidos. O *interface score* (I_sc, REF2015) foi registrado como feature secundária.

### 2.7 Validação por Docking Molecular

A afinidade de ligação ao sítio S1 foi estimada por docking molecular rígido com AutoDock Vina f458505-mod (*Trott & Olson, J. Comput. Chem., 2010*). A *grid box* foi centrada nas coordenadas consenso (25 × 25 × 25 Å; exaustividade = 8). O protocolo adota **docking rígido** para os peptídeos candidatos, pois sequências com comprimento ≥ 9 aa possuem mais de 32 ligações rotacionáveis (φ + ψ + cadeia lateral), excedendo o limite interno do Vina para docking flexível. A modalidade rígida (TORSDOF = 0) é adequada para a geração de *labels* de triagem em larga escala (correlação Pearson ~0,7 com docking flexível completo para top candidatos).

**Preparação dos ligantes e receptor:**
Os peptídeos foram construídos em modo *all-atom* via PeptideBuilder, com geometria de ligação ECEPP/3, centrados nas coordenadas do sítio catalítico. A conversão para formato PDBQT foi realizada com OpenBabel (`-xr -h`: rígido + hidrogênios polares). O receptor em PDBQT foi preparado com OpenBabel (`-xr -h`). Para garantir conformidade com o formato de ligante PDBQT requerido pelo Vina, os blocos `ROOT/ENDROOT/TORSDOF 0` são adicionados automaticamente ao arquivo gerado pelo OpenBabel quando ausentes (método `_ensure_ligand_pdbqt_format()`).

Em modo *fallback* (Vina não disponível), scores heurísticos foram calculados como função da carga básica, hidrofobicidade e índice de Boman, constituindo labels proxy para o treinamento inicial de modelos ML/DL.

### 2.8 Dinâmica Molecular

Os 10 melhores complexos foram submetidos a DM de 10 ns em GROMACS (*Van der Spoel et al., J. Comput. Chem., 2005*), campo de força AMBER99SB-ILDN, água TIP3P, 300 K, 1 bar. O protocolo incluiu minimização de energia (50.000 passos), equilibração NVT (50 ps) e NPT (50 ps), e produção MD (passo 2 fs, PME). Instalação no servidor: `gmx_mpi` + `mpirun -np 1` (build CUDA-MPI, GPU RTX 5070 Ti).

### 2.9 Ranking Composto e Seleção de Candidatos

Um *score* composto integra as métricas por normalização min-max:

$$S_{final} = 0{,}35 \cdot S_{Vina} + 0{,}25 \cdot S_{Rosetta} + 0{,}20 \cdot S_{H\text{-}bond} + 0{,}10 \cdot S_{RMSD} + 0{,}10 \cdot S_{básicos}$$

Os scores são reescritos nas colunas de label do CSV ML após o ranking, tornando o dataset supervisionado disponível para treinamento.

### 2.10 Implementação Computacional

Pipeline implementado em Python 3.10 como sistema **multiagente** com 10 módulos especializados (BaseAgent → agentes derivados). Cada agente opera em modo *real* (ferramenta instalada) ou *fallback* heurístico (pipeline não bloqueia). Ambiente conda `protein_design_env`, executado no servidor Debian com RTX 5070 Ti 16 GB via `conda run`. Código-fonte: https://github.com/eulaliobqi/design-inibidores

**Infraestrutura:**
- Servidor: `eulalio@200.235.143.10`, Debian, 32 cores, RTX 5070 Ti 16 GB
- Notebook local: Windows 11, RTX 2050 4 GB
- Workflow git: edição local → commit → push GitHub → `git pull` no servidor → execução

**Ferramentas instaladas no servidor (atualizado 2026-06-11):**

| Ferramenta | Status | Versão/Notas |
|---|---|---|
| Python 3.10 | ✓ | conda env `protein_design_env` |
| numpy, pandas, biopython, matplotlib | ✓ | ambiente base |
| PeptideBuilder | ✓ | geração all-atom de peptídeos |
| rdkit, pdbfixer, mdtraj, MDAnalysis | ✓ | análise estrutural |
| plip 3.0.0 | ✓ | análise de interações proteína-ligante |
| OpenBabel | ✓ | conversão PDBQT (obabel) |
| AutoDock Vina f458505-mod | ✓ | docking rígido de peptídeos |
| fpocket | ✓ | análise de bolso de ligação |
| GROMACS gmx_mpi | ✓ | CUDA-MPI, build sm_120 Blackwell |
| PyTorch 2.11.0+cu128 | ✓ | CUDA 12.8, RTX 5070 Ti (Blackwell) |
| ProteinMPNN | ✓ | `~/ProteinMPNN` (git clone) |
| RFdiffusion | ✓ clonado | `~/RFdiffusion`; pesos Base_ckpt.pt em download |
| PyRosetta | ✗ | requer licença academia (pyrosetta.org) |

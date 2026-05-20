# Design de Inibidores Peptídicos de Tripsina de Lepidoptera

Pipeline multiagente em Python para design racional de inibidores peptídicos contra tripsinas digestivas de lagartas-praga (*Spodoptera*, *Helicoverpa*, etc.).

Dado um conjunto de estruturas 3D da enzima-alvo, o pipeline mapeia automaticamente o sítio de ligação, gera novos peptídeos inibidores de diferentes tamanhos (5–20 aa) por IA estrutural, avalia cada candidato com múltiplas ferramentas computacionais e entrega um ranking final com relatório HTML.

---

## Contexto biológico

As tripsinas digestivas são serina-proteases essenciais para lagartas-praga. Inibidores do tipo Kunitz e BPTI bloqueam o sítio S1 da enzima competindo com o substrato. Este pipeline projeta novos inibidores peptídicos curtos com:

- **P1 = Arg ou Lys** — especificidade pelo bolso S1 (Asp específico de tripsina)
- **Comprimentos variados** — 5, 7, 10, 12, 15 e 20 aminoácidos
- **Alta afinidade e estabilidade conformacional** verificadas por MD

---

## Fluxo do pipeline

```
4 estruturas PDB (data-trypsin/)
          │
          ▼
  STAGE 1 ── Análise Estrutural
  Mapeia sítio S1: tríade His-Asp-Ser, bolso S1
  → binding_site.json, hotspots.json
          │
          ▼
  STAGE 2 ── RFdiffusion
  Gera backbones peptídicos 3D (5–20 aa)
  ancorados nos hotspots do sítio S1
          │
          ▼
  STAGE 3 ── ProteinMPNN
  Projeta sequências para cada backbone
  P1 fixo = Arg/Lys; seeds com motivos Kunitz
          │
          ▼
  STAGE 4 ── Rosetta / PyRosetta
  Refina energia da interface peptídeo–tripsina
  FlexPepDock + FastRelax
          │
          ▼
  STAGE 5 ── AutoDock Vina
  Valida afinidade de ligação (kcal/mol)
  Grid centrado no sítio S1 mapeado
          │
          ▼
  STAGE 6 ── GROMACS (MD 10 ns)
  Avalia estabilidade dinâmica dos top-5
  RMSD, H-bonds, raio de giro
          │
          ▼
  STAGE 7 ── Ranking
  Score composto: Vina(35%) + Rosetta(25%)
  + H-bonds(20%) + RMSD(10%) + Básicos(10%)
  → ranking.csv
          │
          ▼
  STAGE 8/9 ── Visualizações + Relatório
  6 figuras automáticas + report.html
```

**Cada agente detecta se a ferramenta está instalada e usa heurísticas como fallback** — o pipeline nunca trava por ferramenta ausente.

---

## Estrutura do repositório

```
design-inibidores/
│
├── scripts/                      # Pipeline executável
│   ├── run_pipeline.py           # Orquestrador principal (CLI)
│   ├── utils.py                  # Detecção de ferramentas, parse PDB
│   └── agents/
│       ├── structure_agent.py    # Mapeamento do sítio S1
│       ├── rfdiffusion_agent.py  # Geração de backbones
│       ├── proteinmpnn_agent.py  # Design de sequências
│       ├── rosetta_agent.py      # Refinamento de interface
│       ├── docking_agent.py      # Docking molecular (Vina)
│       ├── md_agent.py           # Dinâmica molecular (GROMACS)
│       ├── optimization_agent.py # Redesign iterativo
│       ├── ranking_agent.py      # Score composto + ranking
│       ├── visualization_agent.py# Figuras automáticas
│       └── report_agent.py       # Relatório HTML/Markdown
│
├── data-trypsin/                 # Estruturas 3D de entrada (HADDOCK)
│   ├── ACR157-final.pdb
│   ├── QCL936-final.pdb
│   ├── XP273-final.pdb
│   └── XP352-final.pdb
│
├── config.yaml                   # Parâmetros de todas as etapas
├── environment.yml               # Ambiente Mamba/Conda
├── executavel.sh                 # Script de instalação e execução
└── checkpoint.py                 # Gerenciador de checkpoints
```

---

## Instalação — passo a passo

### Pré-requisitos

- Linux/macOS (ou WSL2 no Windows)
- [Miniforge](https://github.com/conda-forge/miniforge/releases) ou Anaconda
- GPU NVIDIA com CUDA ≥ 11.8 (recomendado para RFdiffusion e GROMACS)

### Passo 1 — Clonar o repositório

```bash
git clone https://github.com/eulaliobqi/design-inibidores.git
cd design-inibidores
```

### Passo 2 — Criar o ambiente Conda

```bash
mamba env create -f environment.yml
conda activate protein_design_env
```

> Se `mamba` não estiver disponível: `conda env create -f environment.yml`

### Passo 3 — Instalar ferramentas externas (opcionais)

O pipeline funciona sem essas ferramentas (usa heurísticas), mas com elas produz resultados reais.

#### RFdiffusion (design de backbones por difusão)

```bash
git clone https://github.com/RosettaCommons/RFdiffusion.git $HOME/RFdiffusion
cd $HOME/RFdiffusion
pip install -e .
# Baixar pesos do modelo:
bash scripts/download_models.sh $HOME/RFdiffusion/models
```

#### ProteinMPNN (design de sequências)

```bash
git clone https://github.com/dauparas/ProteinMPNN.git $HOME/ProteinMPNN
```
> Não requer instalação adicional — apenas clone.

#### PyRosetta (refinamento de interface)

```bash
pip install pyrosetta-installer
python -c "import pyrosetta_installer; pyrosetta_installer.install_pyrosetta()"
```
> Licença gratuita para academia: [pyrosetta.org/downloads](https://www.pyrosetta.org/downloads)

#### AutoDock Vina (docking)

```bash
conda install -c conda-forge vina
```

#### GROMACS (dinâmica molecular)

```bash
conda install -c conda-forge gromacs
```

### Passo 4 — Verificar instalação

```bash
bash executavel.sh check
```

Saída esperada:

```
  Ferramentas detectadas:
    fpocket         ✓
    vina            ✓
    gromacs         ✓
    rfdiffusion     ✓
    proteinmpnn     ✓
    rosetta         ✓
```

---

## Execução

### Modo rápido — sem MD (5–15 min)

Gera candidatos e ranking sem simulação molecular. Ideal para triagem inicial.

```bash
bash executavel.sh design
```

Ou equivalente:

```bash
python scripts/run_pipeline.py --config config.yaml --step all
```

### Pipeline completo — com MD (~horas, depende do servidor)

```bash
bash executavel.sh all
```

### Retomar após interrupção

O pipeline salva checkpoints após cada etapa. Para continuar de onde parou:

```bash
bash executavel.sh resume
```

Ou:

```bash
python scripts/run_pipeline.py --config config.yaml --step all --resume
```

### Executar etapa específica

```bash
# Apenas mapear o sítio de ligação
python scripts/run_pipeline.py --config config.yaml --step structure

# Apenas gerar sequências (após structure e rfdiffusion)
python scripts/run_pipeline.py --config config.yaml --step mpnn --resume

# Apenas gerar relatório a partir de resultados existentes
python scripts/run_pipeline.py --config config.yaml --step report --resume
```

### Redesign iterativo

Após o ranking, gera variantes dos melhores candidatos por mutação e extensão:

```bash
bash executavel.sh optimize 1   # iteração 1
bash executavel.sh optimize 2   # iteração 2
```

---

## Saídas

```
outputs/
│
├── structure/
│   ├── binding_site.json         ← sítio S1 mapeado (centro XYZ, hotspots)
│   └── hotspots.json
│
├── rfdiffusion/
│   ├── len_5/backbone_*.pdb      ← backbones gerados (5 aa)
│   ├── len_10/backbone_*.pdb
│   └── ...
│
├── proteinmpnn/
│   ├── all_sequences.fasta       ← todas as sequências geradas
│   └── sequences_properties.json
│
├── rosetta/
│   └── rosetta_scores.json       ← I_sc por candidato
│
├── docking/
│   └── docking_results.json      ← afinidade Vina (kcal/mol) por candidato
│
├── md/
│   └── md_results.json           ← RMSD, H-bonds, Rg por candidato
│
├── ranking/
│   ├── ranking.csv               ← tabela final ordenada ★
│   └── ranking_top.json
│
├── visualizations/
│   ├── bar_top20.png
│   ├── heatmap_metrics.png
│   ├── scatter_vina_sc.png
│   ├── length_distribution.png
│   ├── radar_top5.png
│   └── charge_hbond.png
│
└── reports/
    ├── report.html               ← relatório navegável ★
    └── report.md
```

### Exemplo de `ranking.csv`

```
rank,sequence,length,vina_affinity,rosetta_I_sc,md_rmsd_nm,hbond_avg,n_arg_lys,final_score
1,RPDFCLEPKK,10,-9.4,-8.2,0.12,4.3,2,0.891
2,RRYCEIFARR,10,-8.7,-7.1,0.15,3.8,3,0.843
3,RLYSQFP,7,-8.1,-6.8,0.18,3.1,2,0.762
4,RGSKYFP,7,-7.6,-6.3,0.21,2.9,1,0.701
5,RYCEI,5,-6.9,-5.8,0.24,2.4,1,0.631
```

---

## Parâmetros principais (`config.yaml`)

| Parâmetro | Padrão | Descrição |
|---|---|---|
| `rfdiffusion.num_designs` | 50 | Backbones gerados por comprimento |
| `rfdiffusion.contig_lengths` | [5,7,10,12,15,20] | Tamanhos de peptídeos (aa) |
| `proteinmpnn.num_seq_per_target` | 30 | Sequências por backbone |
| `proteinmpnn.sampling_temp` | 0.1 | Temperatura de amostragem (0.1=conservador) |
| `docking.exhaustiveness` | 32 | Exaustividade do Vina (maior=mais preciso) |
| `md.simulation_ns` | 10 | Duração da simulação MD |
| `ranking.weights.vina_affinity` | 0.35 | Peso Vina no score composto |
| `optimization.max_iterations` | 3 | Rodadas de redesign iterativo |

---

## Ferramentas utilizadas

| Ferramenta | Função | Referência |
|---|---|---|
| **RFdiffusion** | Design de backbones por difusão generativa | Watson et al., *Nature* 2023 |
| **ProteinMPNN** | Design de sequências em backbone fixo | Dauparas et al., *Science* 2022 |
| **PyRosetta / Rosetta** | Refinamento de interface FlexPepDock | Raveh et al., *PLoS Comp Biol* 2011 |
| **AutoDock Vina** | Docking molecular | Trott & Olson, *JCC* 2010 |
| **GROMACS** | Dinâmica molecular | Van der Spoel et al., *JCC* 2005 |
| **AMBER99SB-ILDN** | Campo de força para MD | Lindorff-Larsen et al., *Proteins* 2010 |
| **fpocket** | Detecção automática de bolsos | Le Guilloux et al., *BMC Bioinf* 2009 |
| **MDTraj / MDAnalysis** | Análise de trajetórias | McGibbon et al., *Biophys J* 2015 |

---

## Estratégia de inibição

Os candidatos são desenhados para bloquear a tripsina de lepidóptero por:

1. **Ocupação do bolso S1** — Arg/Lys em P1 forma ponte de sal com o Asp específico de tripsina
2. **Bloqueio da tríade catalítica** (His–Asp–Ser) por impedimento estérico
3. **Maximização de H-bonds** com o backbone da enzima em P2–P5
4. **Resistência à autoproteólise** — resíduo volumoso em P1'

---

## Próximos passos experimentais

- [ ] Síntese e purificação dos top-3 candidatos
- [ ] Ensaios de inibição enzimática: Ki e IC50 com tripsina de lepidóptero
- [ ] Análise de estabilidade por dicroísmo circular (CD)
- [ ] Bioensaios com lagartas (*S. frugiperda*, *H. armigera*)
- [ ] MD longa (200 ns) nos 2 melhores candidatos

---

## Contato

**Eulalio Santos** — eulalio.santos@ufv.br  
Universidade Federal de Viçosa

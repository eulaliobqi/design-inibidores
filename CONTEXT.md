# CONTEXT.md
# Projeto: Engenharia de Inibidores Peptídicos contra Tripsina usando IA Estrutural

## Visão Geral

Este projeto tem como objetivo desenvolver um pipeline profissional de engenharia de proteínas para desenhar inibidores peptídicos altamente específicos contra tripsinas digestivas de lagartas-praga utilizando inteligência artificial estrutural, bioinformática molecular e refinamento energético.

O foco principal é gerar peptídeos ligantes curtos variando de 3 até 20 aminoácidos, priorizando:

- alta afinidade pelo sítio catalítico;
- estabilidade conformacional;
- resistência proteolítica;
- especificidade molecular;
- potencial aplicação agrícola e biotecnológica.

O pipeline integrará:

- RFdiffusion
- ProteinMPNN
- Rosetta Design / FlexPepDock
- Docking molecular
- Dinâmica molecular
- Análises energéticas
- Otimização iterativa via IA

Todo o ambiente será organizado em um único ambiente Mamba/Conda reproduzível.

---

# Objetivos Científicos

## Objetivo principal

Desenvolver inibidores peptídicos de tripsina utilizando desenho racional guiado por IA estrutural.

## Objetivos específicos

1. Identificar resíduos catalíticos da tripsina
2. Mapear o sítio S1 e regiões adjacentes
3. Gerar peptídeos estruturais utilizando RFdiffusion
4. Otimizar sequências com ProteinMPNN
5. Refinar interfaces com Rosetta
6. Avaliar afinidade e estabilidade
7. Realizar otimização iterativa
8. Priorizar candidatos para validação experimental

---

# Estratégia Estrutural

A tripsina possui preferência por resíduos básicos:

- Arginina (R)
- Lisina (K)

O pipeline deverá explorar:

- ocupação profunda do bolso S1;
- interação com Asp189;
- bloqueio funcional da tríade catalítica;
- maximização de H-bonds;
- otimização hidrofóbica;
- redução de clashes estéricos.

---

# Pipeline Principal

Estrutura alvo
↓
Preparação estrutural
↓
RFdiffusion
↓
ProteinMPNN
↓
Rosetta FlexPepDock
↓
Docking molecular
↓
Dinâmica molecular
↓
MMGBSA/MMPBSA
↓
Ranking final

---

# Organização do Projeto

## Estrutura esperada

project/
├── data/
├── models/
├── configs/
├── scripts/
├── notebooks/
├── outputs/
├── logs/
├── docking/
├── md/
├── analysis/
└── docs/

---

# Ambiente Computacional

## Ambiente único

Nome sugerido:

protein_design_env

## Gerenciador

- Mamba
- Conda

## Python

- Python 3.10

---

# Softwares Principais

## IA estrutural

- RFdiffusion
- ProteinMPNN

## Refinamento

- Rosetta
- FlexPepDock

## Docking

- AutoDock Vina
- HADDOCK

## Dinâmica molecular

- GROMACS

## Visualização

- PyMOL
- ChimeraX

---

# Estratégias Avançadas

## Explorar múltiplos comprimentos peptídicos

Faixas:

- 3–5 aa
- 6–10 aa
- 11–15 aa
- 16–20 aa

Objetivo:
avaliar impacto do tamanho sobre:

- afinidade;
- flexibilidade;
- estabilidade;
- ocupação do sítio.

---

# Estratégias de Otimização

## RFdiffusion

Explorar:

- número de designs;
- hotspot residues;
- noise scales;
- contigs;
- backbone diversification.

## ProteinMPNN

Explorar:

- sampling_temp;
- num_seq_per_target;
- fixed residues;
- bias_AA_jsonl;
- omit_AAs;
- cadeia fixa vs flexível.

## Rosetta

Explorar:

- FlexPepDock refinement;
- side-chain repacking;
- FastRelax;
- minimização energética;
- interface redesign.

---

# Métricas Importantes

## Estruturais

- RMSD
- RMSF
- SASA
- Radius of gyration

## Energéticas

- ΔG
- Interface score
- fa_atr
- fa_rep

## Interações

- H-bonds
- salt bridges
- hydrophobic contacts

---

# Critérios de Seleção

Os melhores candidatos deverão apresentar:

- forte ocupação do sítio S1;
- baixa energia de interface;
- estabilidade dinâmica;
- persistência de H-bonds;
- baixa repulsão estérica;
- alta complementaridade.

---

# Estratégia Iterativa

O pipeline deverá ser automatizado para permitir:

1. geração
2. avaliação
3. refinamento
4. re-ranking
5. redesign automático

---

# Integração com Claude Code

Claude Code será utilizado para:

- automação de scripts;
- organização modular;
- debugging;
- criação de pipelines;
- parsing de resultados;
- análise estrutural;
- criação de relatórios;
- geração de visualizações;
- integração com GitHub.

---

# Filosofia do Projeto

O pipeline deve ser:

- modular;
- reproduzível;
- escalável;
- automatizado;
- profissional;
- compatível com HPC e GPU.


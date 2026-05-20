# SKILL.md
# Skill Document — Claude Code
# Pipeline de Engenharia de Inibidores Peptídicos

## Papel do Claude Code

Claude Code atuará como engenheiro computacional e assistente de bioinformática estrutural responsável por:

- desenvolver scripts;
- automatizar pipelines;
- integrar ferramentas;
- interpretar outputs;
- otimizar parâmetros;
- organizar resultados.

---

# Objetivo Técnico

Construir um pipeline completo e reproduzível para gerar inibidores peptídicos de tripsina usando:

- RFdiffusion
- ProteinMPNN
- Rosetta FlexPepDock
- Docking molecular
- Dinâmica molecular

---

# Requisitos do Projeto

## Ambiente único

Criar um único ambiente Mamba contendo:

- CUDA
- PyTorch
- RFdiffusion
- ProteinMPNN
- Rosetta wrappers
- GROMACS
- ferramentas auxiliares

---

# Organização obrigatória

O projeto deve seguir:

project/
├── configs/
├── scripts/
├── outputs/
├── logs/
├── notebooks/
├── data/
├── analysis/
├── docking/
├── md/
└── docs/

---

# Responsabilidades do Claude Code

## 1. Setup do ambiente

Criar:

- environment.yml
- scripts de instalação
- validação GPU
- testes de dependências

---

## 2. RFdiffusion

### Objetivos

- gerar peptídeos 3–20 aa;
- otimizar interação com sítio catalítico;
- explorar múltiplos backbones.

### Automatizar

- geração de contigs;
- hotspot residues;
- batch generation;
- múltiplos seeds;
- paralelização GPU.

### Resíduos críticos

Priorizar:

- Asp189
- Ser195
- His57

---

# Parâmetros RFdiffusion

Explorar:

- inference.num_designs
- diffuser.T
- denoiser.noise_scale_ca
- denoiser.noise_scale_frame
- ppi.hotspot_res
- contig lengths

---

# Comprimentos peptídicos

Executar múltiplas rodadas:

- 3–5 aa
- 6–10 aa
- 11–15 aa
- 16–20 aa

---

# 3. ProteinMPNN

## Objetivos

- otimizar sequência;
- maximizar estabilidade;
- melhorar complementaridade.

## Automatizar

- geração massiva de sequências;
- comparação de scores;
- seleção automática.

---

# Estratégias MPNN

## Fixar resíduos

Fixar Arg/Lys no P1.

## Explorar

- sampling_temp
- backbone_noise
- bias_AA_jsonl
- omit_AAs

---

# 4. Rosetta

## Objetivos

- refinamento energético;
- otimização da interface;
- minimização estrutural.

## Ferramentas

- FlexPepDock
- FastRelax
- InterfaceAnalyzer

---

# Métricas críticas

## Interface

Priorizar:

- I_sc
- ΔΔG
- fa_atr
- shape complementarity

---

# 5. Docking

Automatizar:

- preparação PDBQT;
- grids;
- batch docking;
- parsing de scores.

Ferramentas:

- AutoDock Vina
- HADDOCK

---

# 6. Dinâmica Molecular

## Objetivos

- avaliar estabilidade temporal;
- persistência de interação;
- comportamento conformacional.

## Ferramentas

- GROMACS

---

# Métricas MD

- RMSD
- RMSF
- SASA
- H-bonds
- Radius of gyration

---

# 7. Pós-processamento

Claude Code deverá:

- extrair scores;
- gerar rankings;
- produzir tabelas;
- gerar gráficos;
- comparar variantes.

---

# 8. Visualização

Gerar:

- imagens PyMOL;
- mapas de interface;
- heatmaps;
- gráficos energéticos.

---

# 9. Automação

O pipeline deve permitir:

- execução por etapas;
- retomada automática;
- logs detalhados;
- checkpoints.

---

# 10. Programação

## Linguagem principal

Python

## Scripts auxiliares

- Bash
- YAML
- JSON

---

# 11. Boas práticas

## Reprodutibilidade

Obrigatório:

- seeds fixas;
- logs completos;
- versionamento;
- configs salvas.

---

# 12. Integração GitHub

Claude Code deverá:

- criar commits organizados;
- gerar README;
- documentar scripts;
- manter estrutura limpa.

---

# 13. Critérios de Sucesso

Os melhores peptídeos deverão:

- ocupar S1;
- interagir com Asp189;
- apresentar baixa energia;
- manter estabilidade dinâmica;
- possuir alta complementaridade.

---

# 14. Objetivo Final

Gerar candidatos reais para:

- síntese peptídica;
- ensaios enzimáticos;
- expressão heteróloga;
- bioinseticidas;
- transgenia vegetal.


# Design de peptídeos candidatos contra tripsinas digestivas de lepidópteros-praga

Repositório do manuscrito **"From Natural Protease Inhibitors to De Novo Candidate Peptides Targeting Digestive Trypsins of Lepidopteran Pests"** (`manuscript/`), submetido como *Original Research* a *Frontiers in Natural Products*.

Triagem computacional em duas frentes — peptídeos lineares (**L**) e macrociclos cabeça-cauda (**M**) — contra as tripsinas digestivas de oito lepidópteros-praga da soja, com **critério duro de não clivagem** pelas proteases do intestino médio. **Todo o resultado é computacional: não há ensaio de inibição, nem de estabilidade, nem contrasseleção contra proteases não alvo.** Os peptídeos da lista final sobreviveram aos filtros disponíveis; nenhum tem atividade ou seletividade demonstrada.

> **Aviso sobre a documentação antiga.** As seções em [`docs/LEGADO_pipeline_multiagente.md`](docs/LEGADO_pipeline_multiagente.md) descrevem o pipeline multiagente inicial (Rosetta, AutoDock Vina, P1 fixo em Arg/Lys, quatro PDBs de HADDOCK) que **não foi usado no manuscrito** — o critério duro, inclusive, proíbe Arg e Lys. Ficam como histórico. Para reproduzir o artigo, use somente este README.

---

## Estado (07/10/2026)

| Etapa | Estado |
|---|---|
| Painel de 8 receptores e transferência de subsítios (2PTC, 1SFI) | concluída |
| Calibração da escada de escores (Boltz-2, MD, MM-GBSA, PRODIGY) com 6 inibidores naturais e iscas embaralhadas | concluída; MM-GBSA separou 4/10 pares e PRODIGY 2/10 |
| Geração (880 esqueletos, 22.066 sequências) e critério duro | 527 lineares e 543 cíclicas |
| Boltz-2 E1 (co-dobramento), E2 (reescore 5×3), E3 (controles pareados), E4 (QC de pose) | concluídos; Δ pareado positivo em 63/78 (L) e 60/79 (M), da ordem do ruído |
| Matriz cruzada 8×8 | concluída; sem preferência espécie-específica |
| MD 10 ns dos 48 candidatos, pH 10,0 | concluída; a ocupância de S1 acompanha a pose inicial |
| MD 10 ns dos 48 candidatos, pH 8,2 | **em andamento (44/48 em 07/10 20:50)** |
| MM-GBSA e PRODIGY nas trajetórias de pH 10,0 | concluídos (48/48) |
| Piso de ruído (16 execuções repetidas, `noise-L/M`) | pendente |
| Controles em MD (7 embaralhados, 8 de troca de âncora) | concluídos e **retirados** do artigo: a distância inicial explicava o resultado |

Seções do manuscrito ainda marcadas `[[PENDING]]`/`[[PROVISIONAL]]`: 3.6 (ranking com todas as etapas), 3.7 (comparação de pH, hoje com 37 dos 48 pares), motivo do pH 8,2, autoria, financiamento e DOI de arquivamento.

---

## Reproduzir o manuscrito

```bash
mamba env create -f environment.yml && conda activate protein_design_env
```

O `environment.yml` já traz a seção `pip:` (MDAnalysis, MDTraj, PLIP e outros); nada precisa ser instalado à parte para a auditoria, as figuras e a montagem do manuscrito. As ferramentas de GPU (RFdiffusion, ProteinMPNN, PyRosetta) ficam comentadas no fim do arquivo e só são necessárias para refazer a geração.

### 1. Conferir os números do texto contra os dados

```bash
python -m scripts.audit_numbers
```

Recalcula, a partir de `data-calibration-b05/` e `data-e2-results/`, os números afirmados nas Seções 3.2–3.6 e 3.8 e imprime `AFIRMADO × RECALCULADO`. Em 07/10/2026: **187 verificações, 0 falhas.** Não recalcula o que só existe no servidor (ρ de reprodutibilidade do E1 e a composição do conjunto duro); isso está na lista de pendências dentro do próprio script.

### 2. Gerar as figuras

```bash
cd manuscript
python figures/make_figures_final.py figures/final   # Figuras 1, 2, 6 e 8
python figures/make_figures_ph.py    figures/final   # Figuras 7 e S10
python figures/collect_final.py                      # renumeração de 05/10 -> figures/final/
```

`figures/collect_final.py` é a definição executável do mapa "saída do gerador → número no manuscrito"; sem ele, os geradores antigos (`make_figures_v3.py`, `make_figures_e2_md.py`, `scripts/rank_final_candidates.py`) produzem os nomes anteriores à renumeração. Todas as figuras saem em 180 mm, 300 dpi, RGB, TIF+PNG+PDF, com piso de 8 pt — as exigências da *Frontiers* estão codificadas em `manuscript/figures/frontiers_style.py`, que recusa fonte menor que o mínimo.

### 3. Montar o manuscrito

```bash
cd manuscript
python render.py          # manuscript_src.md -> manuscript.md (resolve citações, monta as referências)
python build_docx_pt.py   # pt_parts/*.md -> manuscript_pt_src.md + Manuscrito_PT_leitura.docx
```

`render.py` falha se uma citação não tiver referência e avisa se sobrar chave `{...}`. Ele também imprime a contagem de palavras do corpo (limite de 12.000 da revista).

### 4. De onde vem cada item do artigo

| Item | Dados | Script |
|---|---|---|
| Tabela 1, Tabela S1 (painel e subsítios) | `data-lepidoptera-panel/`, `data-subsites-b14/` | `scripts/fetch_lepidoptera_af.py`, `scripts/map_subsites_b14.py` |
| Figura 2, Tabela 2 (calibração) | `data-calibration-b05/`, `data-e2-results/prodigy_calib.json` | `scripts/mmpbsa_calib.py`, `scripts/prodigy_calib_eval.py` |
| Tabela 3, Figura 3, S2, S3, S9 (geração e critério duro) | `data-b23-scoring/` | `scripts/run_diffusion_campaign.py`, `scripts/run_cleavage_b23.py`, `scripts/audit_hard_criterion.py` |
| Figura 4, S4, S5, S8 (Boltz-2 E1–E4) | `data-b23-scoring/results/` | `scripts/score_boltz2_b23.py`, `scripts/rescore_boltz2_topk.py`, `scripts/pose_qc.py` |
| Figura 5, S6 (MD de pH 10,0) | `data-e2-results/md10_{L,M}_analysis.json` | `scripts/run_md_top_candidates.py`, `scripts/analyze_md_top_candidates.py` |
| Figura 6, S7, Tabela 4 (energia e ranking) | `data-e2-results/`, `manuscript/figures/ranking_final.csv` | `scripts/prodigy_scores.py`, `scripts/rank_energy_stages.py`, `scripts/rank_final_candidates.py` |
| Figura 7, S10 (pH 8,2 × pH 10,0) | `data-e2-results/*_parcial_2026-10-07.json`, `compare_ph.json` | `scripts/run_md_ph_campaign.py`, `scripts/mmgbsa_md82.py`, `scripts/compare_ph.py` |

As pastas `data-*` guardam as cópias dos resultados do servidor usadas nas figuras e tabelas; os scripts que rodam GPU (RFdiffusion, Boltz-2, GROMACS, gmx_MMPBSA) precisam do servidor e das ferramentas externas, mas as figuras e a auditoria rodam só com os dados do repositório.

### 5. Testes

```bash
python -m pytest tests -q     # 38 testes
```

---

## Regras de método adotadas no projeto

- Corrigir a PBC (`gmx trjconv -pbc mol -center`) antes de qualquer RMSD ou análise de contato: receptor e peptídeo são moléculas separadas e podem ser escritas em imagens periódicas diferentes (num caso real a distância entre centros de massa chegou a 94,8 Å numa caixa de 116 Å com as moléculas em contato).
- Nenhuma referência entra sem verificação no Crossref ou PubMed. As 77 referências do manuscrito resolvem no Crossref, com ano e título conferidos.
- A ocupância de S1 é descrição, não critério: ela acompanha a pose inicial proposta pelo Boltz-2.
- Limiares pré-registrados em `docs/PLANO_LINEAR_2026-09-30.md`; nenhum muda depois de ver os dados. A única exceção está declarada na Seção 2.7 do manuscrito.
- Controle que não separa do candidato é retirado por completo das análises, camadas e figuras.
- Predição de heurística ou de modelo nunca é relatada como dado real medido.

---

## Estrutura do repositório

```
design-inibidores/
├── manuscript/              # manuscrito, figuras e geradores
│   ├── manuscript_src.md    # fonte EN (citações {chave}) -> render.py -> manuscript.md
│   ├── pt_parts/p1..p5.md   # fonte PT -> build_docx_pt.py
│   ├── refs_resolved.json   # 77 referências formatadas (DOI conferido no Crossref)
│   ├── figures/final/       # figuras com a numeração do artigo (TIF/PNG/PDF, 180 mm, 300 dpi)
│   └── figures/*.py         # geradores + frontiers_style.py + collect_final.py
├── data-lepidoptera-panel/  # modelos AlphaFold, identidades, sítios catalíticos
├── data-subsites-b14/       # subsítios S4-S3' transferidos de 2PTC e 1SFI
├── data-calibration-b05/    # calibração: Boltz-2, MD, MM-GBSA das 22 montagens
├── data-b23-scoring/        # campanha de geração, critério duro e escores Boltz-2
├── data-e2-results/         # resultados de MD, MM-GBSA, PRODIGY e comparação de pH
├── scripts/                 # pipeline do manuscrito (ver a tabela acima)
├── docs/                    # planos pré-registrados, consolidações diárias, auditorias
├── tests/                   # testes unitários dos utilitários
└── environment.yml          # ambiente Mamba/Conda (protein_design_env)
```

---

## Ferramentas externas

RFdiffusion 1.1.0, ProteinMPNN `v_48_020`, Boltz-2 2.2.1, ColabFold (MSA), Foldseek (TM-align), GROMACS 2025.4 com CHARMM36, PDB2PQR 3.6.2 + PROPKA 3, gmx_MMPBSA, PRODIGY, MDAnalysis 2.9.0. Versões, parâmetros e citações estão na Seção 2 do manuscrito; o hardware usado está na Seção 2.9 (uma RTX 5070 Ti de 16 GB, 32 núcleos).

---

## Contato

**Eulalio Santos** — eulalio.santos@ufv.br
Universidade Federal de Viçosa

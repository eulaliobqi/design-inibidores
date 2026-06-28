# Pipeline de Design Racional de Inibidores Peptídicos de Tripsina de Lepidoptera

**Projeto:** design-inibidores | **Repositório:** github.com/eulaliobqi/design-inibidores  
**Status:** Fases 1–4 concluídas | TOP-3 síntese definidos | Fase 5 (RFpeptides/ciclização) planejada  
**Última atualização:** 2026-06-28

---

## 1. Contexto e Problema Biológico

Tripsinas digestivas de Lepidoptera (especialmente *Spodoptera frugiperda* e *Anticarsia gemmatalis*) são
a principal enzima digestiva no gut alcalino (pH 8–10) das lagartas. Sua inibição bloqueia:
- Digestão de proteínas da planta hospedeira
- Disponibilidade de aminoácidos essenciais
- Crescimento larval → mortalidade ou inibição de ecdise

**Referências fundantes:**
- Paulo et al. (2026): Peptídeos derivados de Reactive Center Loops (RCL) de BPTI/SKTI inibem
  tripsinas digestivas de *A. gemmatalis* — DOI: 10.1002/arch.70123
- Oliveira et al. (2017): Caracterização cinética das serina proteases de *A. gemmatalis*
  (PubMed 28925864)
- Leite et al. (2024): Tripeptídeos inibitórios de atividade trypsin-like em *A. gemmatalis*
  (Springer, DOI: 10.1007/s12600-024-01125-x)
- Brito et al. (2013): *S. frugiperda* expressa tripsinas insensíveis como mecanismo de
  resistência a inibidores de plantas (PubMed 23466392)

---

## 2. Características Essenciais do Inibidor Ideal

### R1 — Baixa energia de ligação ao sítio S1
- Target: ΔG < −12 kcal/mol (Vina rígido)
- Mecanismo: P1=Arg/Lys ocupa bolso S1 eletronegativo (Asp205 em *A. gemmatalis*)
- Melhor resultado obtido: SARESIKKAYKTFLERYKKL (−14.58 kcal/mol)
- **Referência:** Watson et al. (2023) Nature 620:1089 — RFdiffusion para design de binders

### R2 — Especificidade para Lepidoptera (não inibir tripsinas humanas/benéficas)
- Selectivity Index (SI) = aff_não-alvo − aff_alvo ≥ 2.0 kcal/mol
- Não-alvos avaliados: tripsina humana (1TRN) + *Apis mellifera* (AlphaFold A0A7M7MMI1 v6)
- Resultado: 20/20 candidatos aprovados (Fase 3)
- **Referência:** Oliveira et al. (2020): ApTI Kunitz tem inibição tight-binding não-competitiva
  seletiva para *A. gemmatalis* (PubMed 32342573)

### R3 — Estabilidade conformacional em solução (MD obrigatório)
- Limiar validado: RMSD backbone < 0.5 nm = estável; 0.5–1.0 nm = marginal; > 1.0 nm = instável
- **LIÇÃO CRÍTICA:** Melhor afinidade Vina ≠ estabilidade em solvente
  - SARESIKKAYKTFLERYKKL: top-1 Vina (−14.58) mas RMSD 0.871 nm (marginal)
  - RLREELKKAEEWLEKRRKEE: surgiu como 5° por heurística mas mais estável do pipeline (0.294 nm)
- TOP-3 síntese pós-MD Fases 3+4:
  1. MKKQRENAKKVAEITLKKAK (RMSD 0.447 nm) — Fase 3
  2. RLREELKKAEEWLEKRRKEE (RMSD 0.294 nm ★) — Fase 4 Optimize
  3. GSRASARAYAARVRARRAAL (RMSD 0.494 nm) — Fase 3

### R4 — Resistência proteolítica no gut de Lepidoptera
- Problema detectado: 0/20 candidatos resistentes — todos possuem 3–7 K/R internos
- K/R interno = sítio de clivagem por tripsina própria do gut
- **Estratégias para Fase 5:**
  - D-aminoácidos em posições P1'-P3' (Sivaramakrishnan et al. 2019: ciclização + D-aa → 10× melhor)
  - Nle (norleucina) ou Orn (ornitidina) como miméticos de Lys sem sítio de clivagem
  - N-metilação de resíduos K/R internos
  - Ciclização head-to-tail (elimina exopeptidases terminais)
  - **Referências:** PMC7688903 (D-aa proteolytic resistance); biorXiv 2025/06/17.660067
    (D-aa + ciclização em peptídeos ricos em Arg)

### R5 — Expressão heteróloga viável
- Plataformas validadas na literatura:
  - *E. coli*: ChTI expresso com 5.5 U/mg (ScienceDirect DOI: 10.1016/j.indcrop.2022.115780)
  - *Pichia pastoris*: inibidor de trigo com LC50 15 µg/mL (Springer DOI: 10.1007/s11033-014-3760-y)
  - Plantas transgênicas: KTI/SKTI em soja e *Arabidopsis* reduz desfolha por *H. zea*
    (PMC9982021)
- Recomendação: Para peptídeos <30 aa, síntese química Fmoc-SPPS é mais eficiente
- Para inibidores Kunitz completos (>50 aa): *P. pastoris* com sinal α-MF

### R6 — Adjuvantes para formulação e aplicação
- Encapsulação em PLGA/quitosana: aumenta rainfastness e libera lentamente no gut larval
  (Molecules 2026, DOI: 10.3390/molecules31030453)
- Nano-assembleias com adjuvante anfifílico: melhoram adesão foliar, reduzem foto-degradação
  (Nature Comm. 2025, DOI: 10.1038/s41467-025-57028-w)
- Protetores UV para biopesticidas proteicos: cera + TiO2 (PMC7411030)
- Sinergismo com Bt (Bacillus thuringiensis): EcTI potencializa 3× toxinas Bt
  (Pest Mgmt Science 2020, PMID 32453460) — combinar inibidor peptídico + Bt Cry1Ac

### R7 — Manejo integrado sustentável
- Regulatório: biopesticidas têm registro mais rápido (EUA: 12–18 meses vs 36 para químicos)
  (Frontiers 2025, DOI: 10.3389/fsufs.2025.1657000)
- Mercado: USD 15.66 bi até 2029, CAGR 15.2% (ACS Omega 2024, PMC11465254)
- Compatível com polinizadores: SI ≥ 2.0 kcal/mol para *Apis mellifera* validado no pipeline

---

## 3. Arquitetura do Pipeline (12 Agentes)

```
DATA                   COMPUTE                 OUTPUTS
────────               ──────────────────────  ────────────────────────
4 PDBs tripsina  →  [1] StructureAgent      →  binding_site.json
                        ↓
                    [2] RFdiffusionAgent     →  330 backbones (5-15 aa)
                        ↓
                    [3] ProteinMPNNAgent     →  24,513 sequências únicas
                        ↓ (top 1000)
                    [4] RosettaAgent         →  I_sc por complexo
                        ↓
                    [5] DockingAgent         →  880 poses Vina
                        ↓
                    [6] RankingAgent         →  ranking.csv + md_stable flag
                        ↓
                    [7] MDAgent (top-5/N)    →  RMSD/Rg/H-bonds 10 ns
                        ↓
                    [8] SpecificityAgent     →  SI vs 1TRN + Apis
                        ↓
                    [9] CleavageAgent        →  P1-interno flags
                        ↓
                    [10] OptimizationAgent   →  variantes + crossover
                        ↓
                    [11] train_ml.py         →  RF RMSE=0.514, 24k predições
                        ↓
                    [12] ReportAgent         →  report.md + report.html
```

---

## 4. Comandos Validados em Produção

### Setup (servidor: eulalio@200.235.143.10)
```bash
# Sempre antes de rodar
screen -S pipeline
git pull
conda activate protein_design_env
```

### Execução por etapa (ordem recomendada)
```bash
python scripts/run_pipeline.py --step structure
python scripts/run_pipeline.py --step rfdiffusion
python scripts/run_pipeline.py --step mpnn
python scripts/run_pipeline.py --step rosetta
python scripts/run_pipeline.py --step docking
python scripts/run_pipeline.py --step ranking
python scripts/run_pipeline.py --step md
# MD com sequências forçadas:
python scripts/run_pipeline.py --step md --md-sequences SEQ1 SEQ2 SEQ3
python scripts/run_pipeline.py --step specificity
python scripts/run_pipeline.py --step cleavage
python scripts/run_pipeline.py --step optimize
python scripts/train_ml.py
```

### Limpar checkpoint para re-rodar etapa
```python
import json
d = json.loads(open("outputs/checkpoint.json").read())
d.pop("md", None)   # ou outra etapa
open("outputs/checkpoint.json", "w").write(json.dumps(d))
```

---

## 5. Parâmetros Validados em Produção

| Componente | Parâmetro | Valor Validado | Nota |
|------------|-----------|----------------|------|
| RFdiffusion | contig_lengths | [5,7,10,12,15] | 20 removido (muito susceptível) |
| ProteinMPNN | num_seq_per_target | 500 | ~24k seqs únicas total |
| Docking | top_for_docking | 1000 | Labels ML suficientes |
| Docking | exhaustiveness | 8 | Padrão adequado |
| Docking | grid adaptivo | base=40Å + len×3.6 | Crítico para peptídeos >10aa |
| MD | forcefield | amber99sb-ildn | AMBER para peptídeos em água |
| MD | water | TIP3P | Compatível com AMBER ff |
| MD | temperature | 300 K | Temperatura ambiente |
| MD | gmx binary | ~/miniforge3/envs/md-gromacs/bin/gmx_mpi | Prioridade no servidor |
| Specificity | threshold | 2.0 kcal/mol | Validado vs 1TRN + Apis |
| Specificity | Apis UniProt | A0A7M7MMI1 | CORRIGIDO (Q9GYL5 dava 404) |
| AlphaFold | versão | v6 (fallback v4/v3/v2) | EBI mudou para model_v6 |
| Ranking | md_weight | 0.15 + penalidade ×0.5 | Instáveis (>1.0nm) penalizados |
| ML | modelo | Random Forest | RMSE=0.514, CV-R²=-0.056 |

---

## 6. Bugs Críticos Corrigidos

| Commit | Agente | Descrição | Fix |
|--------|--------|-----------|-----|
| 342db6a | SpecificityAgent | `TypeError: '<' not supported NoneType float` | `key=lambda x: x.get(...) or 0` |
| c3d9416 | SpecificityAgent | Apis mellifera Q9GYL5 → 404 | Novo accession A0A7M7MMI1 |
| 5166a6c | SpecificityAgent | AlphaFold v6 404 | Loop `for v in ("v6","v4","v3","v2")` |
| 1b6e3f5 | MDAgent + run_pipeline | MD sempre usava top-5 Vina, sem override | `--md-sequences` arg + `forced_sequences` |
| — | MDAgent | Campos MD: `rmsd_mean_nm` (errado) | Correto: `rmsd_avg_nm`, `rg_avg_nm` |
| — | MDAgent | gmx_mpi não encontrado sem CUDA | test_binary() + conda run fallback |

---

## 7. Lições Aprendidas (Fases 1–4)

1. **MD é filtro obrigatório**, não opcional. Candidatos com melhor Vina/Rosetta falharam em MD.
2. **AlphaFold EBI muda versões** — implementar fallback v6→v4→v3→v2 em todos os downloads.
3. **OptimizationAgent pode superar docking heurístico** — RLREELKKAEEWLEKRRKEE (mais estável)
   veio do redesign, não do docking direto.
4. **Resistência proteolítica é problema não resolvido** — 0/20 resistentes. Fase 5 obrigatória.
5. **Crossover entre parentais** produz candidatos mais diversos que mutação pontual isolada.
6. **Composição Glu/Leu** (RLREELKKAEEWLEKRRKEE) sugere mecanismo de ligação não-P1 —
   abrir design para diferentes perfis de aminoácidos além de R/K-rico.
7. **git pull antes de rodar** — servidor sempre pode ter versão desatualizada.

---

## 8. Próximas Fases Planejadas

### Fase 5 — Resistência proteolítica (Fase 4a RFpeptides)
- RFdiffusion 5–15 aa com filtro KR_interno=0
- RFpeptides (Nature Chem Biol 2025, DOI: 10.1038/s41589-025-01929-w) para peptídeos macrocíclicos
- Incorporar D-aminoácidos via pós-processamento (substituir K/R internos por D-Arg, Nle, Orn)

### Fase 6 — Validação in vitro
- Síntese Fmoc-SPPS dos TOP-3:
  1. MKKQRENAKKVAEITLKKAK
  2. RLREELKKAEEWLEKRRKEE
  3. GSRASARAYAARVRARRAAL
- IC50 por ensaio de inibição fluorimétrico (substrato Boc-Phe-Ser-Arg-MCA)
- Bioensaio larval em dieta artificial (*S. frugiperda*, *A. gemmatalis*)

### Fase 7 — Formulação
- Encapsulação em nanopartículas PLGA ou quitosana
- Testes de estabilidade UV e rainfastness
- Sinergismo com Bt Cry1Ac (base: EcTI + Bt = 3× atividade)

---

## 9. Referências Bibliográficas

### Alvo Biológico
1. Paulo et al. (2026). Peptides from RCL inhibit Lepidopteran digestive trypsins.
   *Arch Insect Biochem Physiol*. DOI: 10.1002/arch.70123
2. Oliveira et al. (2017). Kinetic characterization of *A. gemmatalis* serine proteases.
   PubMed 28925864
3. Leite et al. (2024). Tripeptide inhibitors of *A. gemmatalis*. *Phytoparasitica*.
   DOI: 10.1007/s12600-024-01125-x
4. Boaventura et al. (2023). SKTI reduces *S. frugiperda* resistance to transgenic maize.
   *J Econ Entomol* 116(6):2146. doi.org/10.1093/jee/toad162
5. Brito et al. (2013). Insensitive trypsins in *S. frugiperda* adaptation against inhibitors.
   PubMed 23466403
6. Spit et al. (2016). Trypsin/chymotrypsin genes Lepidoptera × inhibitor sensitivity.
   PubMed 26944308
7. Oliveira et al. (2020). Non-competitive tight-binding inhibition by ApTI in *A. gemmatalis*.
   PubMed 32342573

### Estrutura e Mecanismo de Inibidores
8. Tabosa et al. (2020). EcTI enhances Bt toxins 3× vs *Aedes*. *Pest Mgmt Sci*. PMID 32453460
9. PMC3633903. Crystal structure EcTI + bovine trypsin complex.
10. Dutta et al. (2021). Kunitzin-AH SAR + molecular docking. PMC8309051

### Resistência Proteolítica
11. Sivaramakrishnan et al. (2019). Phyto-inspired cyclic peptides Pin-II RCL. *Phytomedicine*.
    PMID 31077794
12. PMC7688903. D-amino acid substitution improved proteolytic resistance.
13. biorXiv 2025. D-aa + cyclisation arginine-rich peptides. DOI: 10.1101/2025.06.17.660067

### Expressão Heteróloga
14. Springer 2014. Trypsin inhibitor *P. pastoris* vs *Mamestra brassicae*.
    DOI: 10.1007/s11033-014-3760-y
15. ScienceDirect 2022. ChTI + Cry co-expression eliminates resistance. DOI: 10.1016/j.indcrop.2022.115780
16. PMC9982021. SKTI transgenic soybean/Arabidopsis reduces *H. zea* defoliation.

### Formulação e Adjuvantes
17. Molecules 2026. Nanopesticides delivery platforms review. DOI: 10.3390/molecules31030453
18. Nature Comm 2025. Azadirachtin nano-assemblies vs *S. frugiperda*.
    DOI: 10.1038/s41467-025-57028-w
19. PMC7411030. Baculovirus UV protection formulation.

### Ferramentas Computacionais
20. Watson et al. (2023). De novo protein design with RFdiffusion. *Nature* 620:1089.
    DOI: 10.1038/s41586-023-06415-8
21. Dauparas et al. (2022). ProteinMPNN robust sequence design. *Science* 378:49.
    DOI: 10.1126/science.add2187
22. Nature Chem Biol 2025. RFpeptides macrocyclic binders.
    DOI: 10.1038/s41589-025-01929-w
23. Nature 2025. RFdiffusion atomically accurate antibody design.
    DOI: 10.1038/s41586-025-09721-5

### Regulatório e Mercado
24. ACS Omega 2024. IPM sustainability update. PMC11465254
25. Frontiers 2025. Biopesticides sustainable agriculture. DOI: 10.3389/fsufs.2025.1657000
26. Frontiers 2026. Biopesticides biological control advances. DOI: 10.3389/fsufs.2026.1805083

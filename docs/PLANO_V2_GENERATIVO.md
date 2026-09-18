# PLANO V2 — Design generativo de inibidores peptídicos seletivos de tripsina de Lepidoptera

**Replanejamento do zero** | 2026-09-17 | servidor `eulalio@200.235.143.10` (RTX 5070 Ti 16 GB, 32 cores)
Fontes: resultados reais das Fases 1–6 deste repositório + `LNCC-projeto/prompt_otimizado.md`

---

## 0. TL;DR — o que muda em relação ao V1

| Dimensão | V1 (Fases 1–6) | V2 (este plano) |
|---|---|---|
| Especificidade | filtro **pós-hoc**, no fim → 0/23 aprovados | **objetivo da função de geração** (loop de contrasseleção, Bloco 2.7) |
| Determinantes de seletividade | nunca mapeados; S1 é conservado entre todas as tripsinas | **Bloco 1.5 mapeia antes de gerar**; se não houver diferença explorável, o design muda de sítio |
| Scoring principal | Vina rígido (ruído da ordem de ±1 kcal/mol para peptídeo de 20 aa) | escada calibrada: pré-filtro barato → co-dobramento (Boltz-2/Protenix) → MD + MM-PBSA → alquímico |
| Calibração | limiar SI ≥ 2,0 kcal/mol arbitrário | limiar **derivado de controles reais** (BPTI, SFTI-1, SKTI, ApTI) no Bloco 0.5 |
| Resistência proteolítica | linear, K/R interno → 0/20 resistentes | **macrociclo/bicíclico por construção** (RFpeptides, enxerto SFTI-1) |
| Alvos | 4 receptores de espécie indocumentada | painel com **accession verificável**, alvos e antialvos (Blocos 1.1–1.2) |
| Escala | 24 mil sequências, 1 métrica fraca | **menos candidatos, mais evidência por candidato** |

**Regra estruturante:** nenhum bloco ocupa mais de ~24 h de GPU sem checkpoint e sem critério go/no-go explícito.

---

## 1. Diagnóstico honesto do V1 — por que 0/23

1. **O S1 da tripsina é conservado.** Peptídeo linear rico em Arg/Lys ancorado em S1 liga tripsina de lagarta, humana e de abelha igualmente bem. O resultado real (SI médio 0,84 kcal/mol vs. humana e 1,12 vs. *Apis*; um candidato com SI **negativo** contra *Apis*) não é bug: é a consequência física de desenhar para o subsítio errado.
2. **Auto-substrato.** Todo P1 Arg/Lys interno é sítio de clivagem da própria tripsina-alvo → 0/20 resistentes. Peptídeo linear L-canônico rico em K/R é substrato por definição.
3. **Métrica sem calibração.** Vina rígido foi usado como fonte de verdade para ranquear e para decidir seletividade. Diferenças de 0,5–1,5 kcal/mol entre receptores estão dentro do erro do método — o V1 nunca verificou se a escada de scoring reproduz um inibidor conhecido.
4. **Estabilidade ≠ eficácia.** As réplicas (n=3) refutaram os recordistas de réplica única; a ocupância real de S1 caiu de 67,6% para 0,15% entre réplicas em `VRRPR`, com RMSD do complexo aparentemente estável.
5. **Nada disso é desperdício:** a infraestrutura real (MD com réplicas, PLIP, persistência, matriz cross-species 13×11, banco ML) é a base de validação do V2. O que muda é **o que se gera e como se decide**.

---

## 2. Hipótese reformulada

> A seletividade de um inibidor peptídico de tripsina digestiva de Lepidoptera **não pode vir do bolso S1**; ela precisa vir (a) de contatos em subsítios primados/exossítios variáveis entre espécies, (b) da complementaridade eletrostática ao intestino alcalino (pH 9–10), que não existe no duodeno humano (pH ~7–8) nem na abelha, ou (c) de ambas — e só é alcançável se a penalidade por afinidade ao painel negativo entrar **na função objetivo da geração**, não como filtro final.

**Critérios de sucesso do V2 (declarados antes de gerar):**

| Critério | Métrica | Limiar |
|---|---|---|
| S1 — afinidade ao alvo | ΔG MM-PBSA (n=3) | melhor que o controle SKTI no mesmo protocolo |
| S2 — margem de seletividade | ΔΔG (alvo − pior antialvo), MESMO protocolo | **limiar definido no Bloco 0.5**, ≥ 2× o desvio-padrão dos controles |
| S3 — estabilidade | RMSD backbone e ocupância de bolso, n=3 | ocupância ≥ 70% a 5 Å nas 3 réplicas |
| S4 — resistência proteolítica | sítios cindíveis acessíveis em MD | zero P1 interno exposto e geometricamente competente |
| S5 — exequibilidade | síntese Fmoc-SPPS + solubilidade + toxicidade | sem bloqueio previsto |

**Declaração honesta:** "seletividade >1000×" (meta do prompt LNCC) **não é demonstrável in silico**. O V2 entrega margem computacional com barra de erro e um plano experimental que a mede. Qualquer texto que afirme seletividade sem ensaio é fabricação.

---

## 3. Infra real — auditada no servidor em 2026-09-17

| Componente | Estado real | Ação |
|---|---|---|
| GPU | RTX 5070 Ti 16 GB, driver 595.58.03, **sm_120 (Blackwell)** | — |
| `protein_design_env` | torch 2.12.0.dev+cu128 (arch inclui sm_120); `pyrosetta` ok; `se3_transformer` ok; **dgl 2.4.0+cu124** | testar RFdiffusion na GPU (B0.2) |
| RFdiffusion | instalado, **só `Complex_base_ckpt.pt`** | baixar `ActiveSite_ckpt`, `Base_ckpt`, `Complex_beta` e o checkpoint cíclico (B0.2) |
| `boltz2-env` | torch 2.13+cu130 sm_120; **pesos `boltz2_conf.ckpt` + `boltz2_aff.ckpt` presentes** | pronto |
| `protenix` | 2.0.0, torch 2.13+cu130 sm_120 (reprodução aberta do AF3) | validação ortogonal (B3.3) |
| `ligandmpnn_env` | torch 2.2.1+**cu121, sem sm_120** | reinstalar com cu128 (B0.3) |
| `BindCraft` | **env sem jax** — quebrado | consertar ou descartar formalmente (B0.3) |
| `md-gromacs` | GROMACS 2025.4 com CUDA (`gmx_mpi`) | pronto |
| `mmgbsa-env` | gmx_MMPBSA (py 3.11) | pronto |
| Outros | `haddock3` 2026.7.0, Vina, ProteinMPNN, `foldseek` (env `structure`), `mmseqs` (env `annotation`) | pronto |

**Limitação de hardware que molda o plano:** 16 GB de VRAM e **uma** GPU. Nada de "MD de centenas de complexos em paralelo" (premissa do prompt LNCC, escrito para 8× H200). O plano é dimensionado pelo *throughput real medido* no Bloco 0.4.

---

## 4. Orçamento computacional (a recalibrar no Bloco 0.4)

| Etapa | Ordem de grandeza | Onde roda |
|---|---|---|
| RFdiffusion / RFpeptides | segundos a minutos por backbone | GPU, lotes noturnos |
| ProteinMPNN | milhares de seqs/hora | GPU, batch 25 (já validado) |
| Vina (pré-filtro) | ~30–90 s/pose | **CPU, 32 cores** — não ocupa GPU |
| Boltz-2 co-dobramento (~250 aa) | ~1–4 min/seed | GPU; **é o gargalo real** |
| MD GROMACS (~40–60 k átomos) | a medir; estimativa 80–200 ns/dia | GPU |
| MM-PBSA | minutos a horas por trajetória | CPU |

**Regra de triagem (funil, não varredura):** ~10³ sequências no barato → ~10² no co-dobramento → ~10 em MD n=3 → 2–3 no alquímico. O V1 fez o inverso (24 mil sequências com evidência rasa em todas).

---

## 5. Blocos

Cada bloco: **objetivo · método · saída · go/no-go**. O `→` indica dependência obrigatória.

### FASE 0 — Fundação e calibração (sem isso, nada depois é interpretável)

**B0.1 — Registro do estado do stack** *(feito em 2026-09-17, ver §3)*
Saída: tabela da §3 versionada no repositório.

**B0.2 — RFdiffusion em Blackwell + pesos faltantes**
Rodar um design trivial (peptídeo de 10 aa, contig fixo) em `protein_design_env`. Se `dgl 2.4.0+cu124` falhar em sm_120, testar (i) camadas de grafo em CPU, (ii) rebuild do dgl para cu128, (iii) fallback CPU cronometrado. Baixar os checkpoints faltantes do repositório oficial — `ActiveSite_ckpt.pt` é o relevante para ancoragem em sítio catalítico.
Saída: `docs/bench/rfdiff_sm120.md` com tempo real por design.
**Go/no-go:** se RFdiffusion não rodar em tempo aceitável, as Trilhas A e C migram para geração por *hallucination*/MPNN sobre backbones de inibidores conhecidos — plano B declarado agora, não improvisado depois.

**B0.3 — Consertar LigandMPNN e decidir sobre BindCraft**
LigandMPNN: recriar env com torch cu128 (sm_120). BindCraft: instalar `jax[cuda12]` ou **descartar formalmente** (foi feito para binders ≥50 aa; corresponde apenas à Trilha C, opcional).
Saída: envs funcionais ou decisão documentada.

**B0.4 — Benchmark de throughput real** → dimensiona todo o resto
Medir no hardware real: (a) Boltz-2, s/seed para tripsina (~230 aa) + peptídeo de 14 aa; (b) GROMACS, ns/dia para esse complexo solvatado; (c) Vina, s/pose em 32 cores; (d) viabilidade de 2 jobs de MD concorrentes na mesma GPU.
Saída: `docs/bench/throughput.md` + **tamanho máximo de campanha por fase**.
**Go/no-go:** se MD < 50 ns/dia, produção cai para 50 ns × n=3 e a decisão passa a priorizar ocupância/persistência em vez de ΔG absoluto.

**B0.5 — Painel de controles e calibração da escada de scoring** ★ *bloco mais importante da Fase 0*
Entrada: inibidores reais de tripsina com dado experimental publicado — BPTI, SFTI-1 (bicíclico, 14 aa), SKTI, ApTI, EcTI, Bowman-Birk — mais decoys (peptídeos de composição semelhante sem atividade) e um não-inibidor.
Método: passar **todos** pela escada completa (Vina → Boltz-2 → MD curta → MM-PBSA) contra tripsina bovina/humana e contra o alvo Lepidoptera primário.
Saída, por métrica: (i) separa inibidor de decoy? (ii) qual o desvio-padrão? (iii) **qual valor de ΔΔG corresponde a uma diferença de seletividade experimentalmente conhecida?**
**Go/no-go:** métrica que não separa controle de decoy **não entra na decisão do V2** — inclusive o Vina, se for o caso.

**B0.6 — Infraestrutura de dados e proveniência**
Substituir o `checkpoint.json` monolítico (180 MB, já corrompido uma vez) por parquet/DuckDB + manifesto por execução (SHA do git, versão de cada ferramenta, seeds, data). Escrita atômica (fix `ce5d209` já existe) e *lock* entre steps concorrentes.
Saída: `outputs/db/` + `scripts/run_manifest.py`. **Go:** qualquer número do artigo reproduzível a partir do manifesto.

### FASE 1 — Alvos e antialvos verificáveis (rebase científico)

**B1.1 — Curadoria de tripsinas digestivas de Lepidoptera**
≥6 espécies (*S. frugiperda*, *H. armigera*, *A. gemmatalis*, *C. includens*, *D. saccharalis*, *P. xylostella*), priorizando sequências com **evidência de expressão no intestino médio** e accession UniProt/NCBI verificável. Anotar explicitamente as tripsinas "insensíveis a inibidor" descritas em *S. frugiperda* (Brito et al. 2013) — são o mecanismo de escape e precisam entrar como alvo, não ser ignoradas.
**Os 4 receptores legados (ACR157/QCL936/XP273/XP352) são aposentados** como alvos primários: a espécie de origem tem documentação conflitante no próprio repositório. Podem permanecer como conjunto de comparação histórica, rotulados como tal.

**B1.2 — Painel negativo de contrasseleção**
Mamíferos: PRSS1/PRSS2/PRSS3 humanas, quimotripsina, elastase, trombina, FXa, calicreína. Polinizadores: *Apis mellifera*, *Bombus terrestris*. Inimigos naturais: *Trichogramma*, *Cotesia*, *Chrysoperla*. Ambientais: *Danio rerio*, *Gallus gallus*, *Eisenia fetida*. Todos com accession verificável.
**Subconjunto "núcleo duro"** (3–4 proteases) entra em *todo* bloco de scoring; o restante entra só nos finalistas — restrição de orçamento declarada, não silenciosa.

**B1.3 — Estruturas + QC automático**
AFDB (fallback v6→v4→v3→v2, bug já conhecido) e, quando ausente, Boltz-2/Protenix. QC obrigatório: pLDDT por resíduo na interface, tríade catalítica por **mínimo global** (reusar o teste que detectou o bug isolado de *H. virescens*), geometria do loop de ativação.
**Go:** estrutura que não passa no QC não entra no painel.

**B1.4 — Mapeamento REAL dos subsítios por template cristalográfico** → substitui a heurística "204/218"
Superpor cada receptor a complexos cristalográficos de referência (tripsina–BPTI; tripsina–SFTI-1) com US-align/Foldseek; transferir por equivalência estrutural a definição de S1–S4 e S1'–S3' **e dos resíduos de exossítio em contato no complexo real**.
Saída: `outputs/sites/subsites_by_receptor.json` com proveniência (template, RMSD da superposição, resíduo equivalente).
**Go/no-go:** se a superposição não for confiável (RMSD alto, loops ausentes), o receptor sai do painel — em vez de gerar mais um número heurístico.

**B1.5 — Mapa de determinantes de seletividade** ★ *o bloco que nunca existiu no V1*
(a) Matriz posicional alvo × antialvo restrita aos resíduos de interface de B1.4; (b) eletrostática de superfície (APBS/pdb2pqr, `--titration-state-method propka`) a **pH 9,5 (intestino de lagarta) vs 7,4**; (c) diferenças de comprimento e conformação dos loops de superfície do enovelamento quimotripsina; (d) ranquear 3–5 "diferenças exploráveis" por (magnitude da diferença × proximidade ao sítio catalítico × conservação dentro de Lepidoptera).
Saída: relatório + hotspots para condicionar a geração.
**Go/no-go científico:** se nenhuma diferença explorável estiver ao alcance de um peptídeo ancorado em S1, a geração passa obrigatoriamente a mirar **exossítio/interface estendida** — e isso fica registrado como achado, porque é resultado publicável por si só e explica o 0/23 do V1.

**B1.6 — pH e protonação**
Construir cada receptor no seu pH fisiológico real (alvo 9,5; humana ~8; abelha ~7): a diferença de carga do sítio é, ela própria, uma alavanca de seletividade. Aplicar o mesmo tratamento ao peptídeo (estado das His, N/C-terminal).

### FASE 2 — Geração com contrasseleção embutida

**B2.1 — Definição das trilhas e corte de orçamento**

| Trilha | Scaffold | Resolve | Custo |
|---|---|---|---|
| **A** | macrociclo 8–16 aa (RFpeptides / RFdiffusion cíclico) | proteólise por construção; interface maior que a do linear | médio |
| **B** | enxerto em SFTI-1 (bicíclico de 14 aa: cabeça-cauda + 1 dissulfeto) | inibidor de tripsina validado na literatura; redesenhar a face não-catalítica para seletividade | **baixo — começar por aqui** |
| **C** | mini-binder 40–65 aa (exossítio + S1) | máxima área de interface, maior chance de seletividade real | alto |

Nota: Cys/dissulfeto foi abandonado no V1 por custo de implementação (mutação ingênua via PeptideBuilder). Na Trilha B o dissulfeto vem **do scaffold**, não de mutação — o problema técnico anterior não se repete.

**B2.2 — Trilha B primeiro** (menor risco): enxerto do *reactive center loop* + redesign da face oposta, condicionado aos hotspots de B1.5.
**B2.3 — Trilha A:** RFdiffusion/RFpeptides cíclico ancorado em S1 + determinante de seletividade.
**B2.4 — Trilha C** (condicional a B0.2/B0.3): binder de interface estendida.

**B2.5 — Design de sequência com restrições duras**
ProteinMPNN (pesos *soluble*) e/ou LigandMPNN. Restrições: **zero K/R interno exceto o P1 designado**; Cys apenas como par de dissulfeto declarado; viés de contato nos resíduos determinantes; temperatura variável para diversidade.

**B2.6 — Filtros baratos antes de gastar GPU**
Solubilidade/agregação, imunogenicidade, toxicidade (ToxinPred3/AllerTOP), complexidade de síntese, comprimento. Rodam em CPU e cortam a maior parte do pool.

**B2.7 — LOOP DE CONTRASSELEÇÃO** ★ *núcleo metodológico e novidade publicável*
Objetivo por sequência: `margem = score_alvo − max(score_painel_núcleo) − penalidades`.
Implementação realista em 1 GPU: otimização evolutiva/recozimento sobre a sequência (mutação guiada por MPNN + crossover — o V1 já mostrou que crossover produz diversidade útil), avaliando a margem com o scorer mais barato que **passou na calibração B0.5**, em 2–4 ciclos. Só sequências com margem positiva avançam.
**Decisão honesta declarada:** *não* faremos RL de ProGen2 do zero (premissa do prompt LNCC, escrita para 8× H200). O ganho científico está na **função objetivo com contrasseleção**, não em o otimizador ser RL.
Saída: população final + curva de margem por ciclo — se a margem não melhorar, é resultado negativo real e vai para o artigo.

**B2.8 — Diversidade e novidade**
Clusterizar (mmseqs/foldseek), exigir distância mínima entre finalistas, checar similaridade com toxinas conhecidas e com inibidores já patenteados.

### FASE 3 — Escada de scoring física

**B3.1 — Pré-filtro em CPU** (Vina/gnina, 32 cores) — rotulado *baixa confiança*, usado só para ordenar, nunca para aprovar.
**B3.2 — Co-dobramento com Boltz-2**, n=5 seeds, alvo + painel núcleo; métricas ipTM, PAE de interface, pLDDT.
*Ressalva técnica:* o cabeçote de afinidade do Boltz-2 (`boltz2_aff.ckpt`) foi treinado para ligantes pequenos — **não** reportar seu valor como afinidade de peptídeo; usar as métricas de confiança de interface, calibradas em B0.5.
**B3.3 — Validação ortogonal com Protenix 2.0** nos melhores; concordância entre dois modelos independentes como critério de confiança.
**B3.4 — HADDOCK3** com restrições de interface para os finalistas (refinamento + score independente).
**B3.5 — MD n=3**, dimensionada por B0.4: campo de força moderno (ff19SB/OPC ou CHARMM36m) — `amber99sb-ildn` do V1 é legado; parâmetros específicos para macrociclo/dissulfeto/D-aa/Nle/Orn; pH de B1.6.
**B3.6 — MM-PB(GB)SA + entropia de interação** (gmx_MMPBSA; aplicar o fix de PBC `trjconv -pbc mol -center`, env `mmgbsa-env`, py 3.11, entrada por pipe do shell em `screen` — todos já registrados na memória do projeto). **Alvo e antialvos no mesmo protocolo**, para cancelamento parcial de erro no ΔΔG.
**B3.7 — Persistência, ocupância e fingerprint** (PLIP/ProLIF; reusar `deep_test_persistence.py`) com **frames suficientes** — 5 frames/réplica do V1 não separaram sinal de ruído.
**B3.8 — (stretch) ΔG alquímico ou PMF de dissociação** para 2–3 finalistas, apenas se B0.4 mostrar orçamento.

### FASE 4 — Resistência proteolítica de verdade

**B4.1 — Predição de clivagem** pelo painel de proteases do intestino alcalino (reusar `analyze_cleavage.py`).
**B4.2 — Suscetibilidade estrutural em MD:** exposição (SASA) e competência geométrica (distância e orientação em relação à Ser catalítica) de cada sítio cindível, nas conformações **ligada e livre** — sinal físico, não só regra de sequência. Um K/R interno enterrado em macrociclo rígido não equivale a um exposto em peptídeo linear.
**B4.3 — Química de proteção** para o que sobrar: D-aa, Nle/Orn, N-metilação — com reparametrização correta e re-teste, não substituição no papel.

### FASE 5 — Decisão e entrega

**B5.1 — Pareto multiobjetivo (NSGA-II)** só sobre métricas **reais**, cada coluna com proveniência (real medido / predito / ausente) — padrão já criado em `build_ml_database.py`.
**B5.2 — Dossiê de 5–10 candidatos** com incerteza explícita e predições falsificáveis por ensaio.
**B5.3 — Plano experimental:** síntese Fmoc-SPPS (macrociclo/bicíclico), IC50 fluorimétrico contra extrato intestinal de lagarta **e** tripsina humana **e** *Apis* no mesmo ensaio (seletividade **medida**), bioensaio larval em dieta artificial.
**B5.4 — Artigo:** atualizar `artigo_metodologia.md` e `artigo_resultados.md`. A contribuição publicável do V2 é o **método de contrasseleção calibrada** + o achado (positivo ou negativo) sobre a existência de determinantes de seletividade em tripsinas digestivas.

### FASE 6 — ML/DL (paralela, opcional)

**B6.1** Reconstruir o banco com labels novos (co-dobramento, MM-GBSA) + embeddings ESM-2; split por **cluster de sequência**, nunca aleatório (o V1 teve CV-R² = −0,056, isto é, pior que prever a média).
**B6.2** Surrogate rápido para pré-triagem dentro do loop B2.7, treinado só com dado real.

---

## 6. Dependências (DAG resumido)

```
B0.1 ─┬─ B0.2 ─┬───────────────┐
      ├─ B0.3 ─┘               │
      ├─ B0.4 ──────────────┐  │
      └─ B0.6               │  │
B1.1 ─┬─ B1.3 ─ B1.4 ─ B1.5 ┼──┼─ B2.1 ─┬─ B2.2 (Trilha B) ─┐
B1.2 ─┘              B1.6 ──┘  │        ├─ B2.3 (Trilha A) ─┤
B0.5 ★ (precisa de B1.3) ──────┴────────┴─ B2.4 (Trilha C) ─┤
                                                            │
                                   B2.5 ─ B2.6 ─ B2.7 ★ ─ B2.8
                                                            │
                        B3.1 ─ B3.2 ─ B3.3 ─ B3.4 ─ B3.5 ─ B3.6 ─ B3.7 ─ (B3.8)
                                                            │
                                            B4.1 ─ B4.2 ─ B4.3
                                                            │
                                     B5.1 ─ B5.2 ─ B5.3 ─ B5.4
```

Caminho crítico: **B0.5 (calibração) → B1.5 (determinantes) → B2.7 (loop)**. Os três blocos marcados com ★ são os que decidem se o V2 terá resultado diferente do V1.

---

## 7. Riscos e tratamento

| Risco | Probabilidade | Tratamento no plano |
|---|---|---|
| Não existe determinante de seletividade explorável | **alta** | B1.5 descobre isso em dias, antes de gastar GPU; vira resultado publicável e redireciona para exossítio |
| RFdiffusion não roda em sm_120 (dgl cu124) | média | B0.2 testa cedo; plano B declarado (Trilha B não depende de RFdiffusion) |
| Co-dobramento não separa inibidor de decoy | média | B0.5 detecta; se falhar, a decisão recai sobre MD + MM-PBSA e o funil estreita |
| Orçamento de MD estoura | **alta** | B0.4 mede antes; produção dimensionada, não prometida |
| Macrociclo com parâmetros de MD errados | média | B3.5 valida a parametrização contra SFTI-1 experimental antes dos designs |
| Repetir a falha do V1 de reportar predição como dado real | média | proveniência por coluna (B0.6) + regra de memória já vigente no projeto |

---

## 8. Regras operacionais (não-negociáveis, já validadas neste projeto)

- `screen -S <nome>` antes de qualquer execução longa; `git pull` no servidor antes de rodar.
- `mamba`, nunca `conda`, para resolver ambientes; `gmx_mpi` + `mpirun -np 1`; `python=3.11` com gmx_MMPBSA.
- gmx_MMPBSA: `trjconv -pbc mol -center` antes; env `mmgbsa-env`; entrada por pipe do shell (o `input=` falha em `screen`).
- `pdb2pqr --titration-state-method propka`.
- Fluxo: editar no Windows → commit → push → `git pull` no servidor → executar. Commit incremental a cada bloco concluído.
- **Nunca** reportar predição de ML/heurística como dado real medido; atualizar a memória do projeto **e** os arquivos do artigo ao fim de cada bloco.

---

## 9. Referências

DOIs já verificados neste repositório (ver `references.md` e `WORKFLOW.md`): RFdiffusion — Watson et al. 2023, *Nature* 620:1089, DOI 10.1038/s41586-023-06415-8; ProteinMPNN — Dauparas et al. 2022, *Science* 378:49, DOI 10.1126/science.add2187; RFpeptides (binders macrocíclicos) — *Nat Chem Biol* 2025, DOI 10.1038/s41589-025-01929-w; tripsinas insensíveis em *S. frugiperda* — Brito et al. 2013, PubMed 23466392; ApTI seletivo — Oliveira et al. 2020, PubMed 32342573.

Ferramentas citadas **sem DOI verificado neste documento** (verificar antes de entrar no artigo): Boltz-2, Protenix 2.0, LigandMPNN, BindCraft, HADDOCK3, US-align, Foldseek, ToxinPred3, APBS/PROPKA. Os PDBs de referência (complexos tripsina–BPTI e tripsina–SFTI-1) devem ser confirmados no Bloco 1.4 antes de uso.

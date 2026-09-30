# Plano final — manuscrito em forma LINEAR (v2, 30/09/2026)

**Decisão do autor:** só peptídeos **lineares** no manuscrito (coerente com o grupo: GORE1–5,
di/tripeptídeos, PEP-11). Resistência às enzimas digestivas = **ausência de resíduos clivaveis**.
O macrociclo vira **braço de comparação** (resultados já obtidos, intocados) e **sugestão de
otimização**. Nada foi disparado no servidor; este documento é o plano a executar.

## 1. Insights das análises antigas (V1: AutoDock Vina, Rosetta, MD 10 ns, especificidade)

Uso: orientar a metodologia. Os números do V1 **não entram no manuscrito** (regra da revisão de
30/09; o RMSD de MD do V1 é artefato de PBC).

| # | Insight (fonte) | Consequência no plano |
|---|---|---|
| I1 | **Vina melhora monotonicamente com o comprimento** (5 aa −10,3 → 15 aa −13,1; Tab. 9d) — o mesmo viés de tamanho do MM-GBSA (ρ = −0,93 com área de contato, 30/09) | Nenhum escore comparado entre comprimentos sem controle; Boltz-2 sempre **pareado** com controle embaralhado do mesmo comprimento/composição |
| I2 | **Melhor escore ≠ complexo estável**: SARESIKKAYKTFLERYKKL (melhor Vina, −14,58) foi marginal em MD; GARKSIREYQKRVLERLKKK (melhor I_sc) instável | Top-1 por um único escore é frágil → MD obrigatória e **critério de S1 pré-declarado** (≥70% a 5 Å) |
| I3 | Vina reproduz-se bem (DP ≤ 0,03 kcal/mol com exhaustiveness 16) mas falhou em ligante grande (97 GB de RAM), e **não foi validado na escada de calibração** (B0.5: só Boltz-2 separa 10/10) | **Vina fora da cadeia** (nem como escore nem como desempate); Boltz-2 é o único escore validado, e só pareado |
| I4 | **Especificidade real: 0/35 aprovados** (SI ≥ 2,0 vs tripsina humana e *Apis*), alguns com SI negativo; o S1 é conservado; resultados anteriores ao fix de PDBQT eram falsos | Nenhuma afirmação de seletividade no texto; contra-triagem **exploratória** com Boltz-2 (Etapa E5), rotulada como não calibrada para seletividade |
| I5 | **Âncora real ≠ P1 esperado**: nas réplicas, a âncora foi Pro, Gln, Glu, Val ou mudou de identidade entre réplicas (VRTRR, SARESIKKAYKTFLERYKKL); VRRPR tinha RMSD baixo e saía do bolso (67,6→0,15% a 6 Å) | Manter âncora definida empiricamente (já na Seção 2.9), cortes 4/5/6 Å lado a lado e **réplicas adaptativas** (E7) |
| I6 | Só **VRYRR** (contém Arg) teve salt-bridge constante a 4 Å; SRTRR/HRPRRPR ocuparam S1 a 6 Å — candidatos com K/R foram os de S1 mais claro | O filtro estrito (zero sítios) elimina esse perfil. Dois mecanismos de mitigação, ambos pré-declarados: **estrato B** (K/R seguido de Pro, não clivável por tripsina: 61 sequências) e **braço de sensibilidade** (E6: custo do critério estrito) |
| I7 | Peptídeos curtos (5 aa) foram uniformemente estáveis, 7 aa heterogêneos (RMSD do V1, inválido por PBC) | Tratar como hipótese: o 5–8 aa dominante no filtro não garante estabilidade; medir por ocupância |
| I8 | Convenções do **projeto do grupo** (`GOREs-boltz`, `Milena-MD`): pH 8,2, K⁺ 0,10 M, caixa cúbica 2,0 nm, CHARMM36 (feb2026), detecção de plateau, Boltz-2 com 5 amostras de difusão + `--use_potentials` + sementes em réplica, **limiares de QC pré-registrados** (clash <2,2 Å, ω trans, quiralidade L, tríade mantida, P1 básico ≤4,5 Å de Asp189) | Harmonizar com o grupo (E3, E7); congelar critérios **antes** de abrir resultados (seção 4) |
| I9 | A GPU está a **98%** por jobs do grupo (`gores-S`, `md-gore3-rep1-redo`, triplicatas dn2954) | Estimativas de tempo abaixo são para GPU livre; com compartilhamento, contar 1,5–2× |

## 2. Dados já calculados (filtro linear estrito, 8 espécies, 22.066 sequências)

RESISTENTE **2.542** (11,5%; 2.503 únicas), MARGINAL 4.968, SUSCEPTIVEL 14.556. Por espécie: Sf 227, Sl 301,
On 323, Ds 326, Ci 318, Hv 300, Px 398, Ag 349. Comprimento médio 6,98 aa (5: 648; 6: 514; 7: 525; 8: 516; 10: 243;
12: 82; ≥14: 14); 96,2% ≤10 aa. Só **61 (2,4%)** têm K/R — todos seguidos de Pro; 382 têm sinalizador de
exopeptidase terminal (informativo). Braço macrocíclico: 1.829 RESISTENTE (8,3%). MARGINAL com exatamente 1 sítio
de tripsina e K/R: 2.207 (base do braço de sensibilidade).

## 3. Metodologia final — etapas

| Etapa | O quê | Escolhas (melhor metodologia) | Custo* | Estado |
|---|---|---|---|---|
| E0 | Filtro de clivagem linear estrito | zero sítios de qualquer regra com score <0,3; K/R C-terminal conta (CPB); sem isenção de âncora | feito | `outputs/b23_cleavage_linear_strict.json` |
| E1 | **Triagem Boltz-2 linear** dos 2.542 | `cyclic:false`, 1 amostra, 3 recycles (mesmo protocolo do braço macrocíclico → comparação justa) | ~6 h | script pronto |
| E2 | **Re-pontuação robusta** do top-20 por espécie (160 candidatos) | 5 amostras de difusão × 3 sementes, `--use_potentials`, 200 sampling steps (protocolo do grupo); escore = média das sementes | ~1,5 h | **a construir** |
| E3 | **Controle pareado**: para cada um dos 160, 3 embaralhamentos (mesma composição, `seed` fixa) com o mesmo protocolo de E2 | Δ = escore(candidato) − média(controles); reporta a fração com Δ > 0; usado para **interpretar** (não para trocar a regra de seleção) | ~1,5 h | **a construir** |
| E4 | **QC de pose** (limiares pré-registrados do grupo) + matriz cruzada 8×8 (top-1 de cada espécie contra os 8 receptores) | clash, ω, quiralidade, tríade, S1 (≤4,5 Å de Asp189); 64 predições | ~0,5 h | **a construir** |
| E5 | **Contra-triagem exploratória** (seletividade) | top-1 por espécie contra receptores não-alvo já usados no V1 (1TRN humana, *Apis*) + tripsina bovina (1SFI); margem = escore alvo − máx. não-alvo; **rotulada exploratória**: Boltz-2 foi validado real×decoy, não alvo×não-alvo | ~0,5 h | **a construir** |
| E6 | **Braço de sensibilidade** (custo do critério estrito) | amostra estratificada de 200 sequências MARGINAL com 1 sítio K/R; mesmo Boltz-2 de E1; compara Δ de confiança e fração com P1 básico em S1 | ~0,5 h | **a construir** |
| E7 | **MD do top-1 por espécie** | primário: pipeline do grupo `Milena-MD` (CHARMM36 feb2026, pH 8,2, 0,10 M KCl, caixa cúbica 2,0 nm, plateau); 100 ns; partida = predição linear de E2; sem MM-GBSA (não validado, ver I1/B0.5). **Réplicas adaptativas:** *A. gemmatalis* ×3; demais ×1, e +2 réplicas só para quem atingir S1 ≥70% a 5 Å | 8 + 2 + até 2×(n aprovados) simulações, ~4 h cada → ≥ 40 h | **a construir** (samplesheet + módulo de análise S1) |
| E8 | Análise MD | ocupância do S1 (4/5/6 Å, por metades), contato com Ser/His catalíticas, RMSD local com PBC, identidade da âncora por réplica | minutos | análise pronta, adaptar entrada |
| E9 | **Comparação com o braço macrocíclico** | sobreposição dos RESISTENTE, ρ de Spearman da confiança cíclico×linear nas sequências comuns, top-1 nos dois braços | segundos | script pronto |

*GPU livre. Com os jobs do grupo: multiplicar por 1,5–2. **Total estimado ≈ 50–55 h (GPU livre).**

Observações de método:
- **Seleção do top-1 (regra declarada, não muda):** maior confiança do Boltz-2 entre os RESISTENTE; em E2 a
  confiança passa a ser a média das sementes. E3 só informa se o top-1 supera os controles; se não superar, o texto
  diz isso, e a regra não é alterada depois de ver os dados.
- **Por que MD do grupo e não o `MDAgent` antigo:** campo de força moderno (CHARMM36) para peptídeos curtos e
  desordenados, parâmetros iguais aos do grupo (comparabilidade com GORE), e partida/topologia lineares coerentes.
  Alternativa descartada por custo de mudança: manter AMBER99SB-ILDN/pH 10 (já codificado, 50 ns).
- **pH:** o grupo fixou 8,2; o manuscrito atual usa 10,0 (intestino alcalino de Lepidoptera). Recomendo 8,2 para o
  MD (harmonização) e citar a faixa alcalina na Discussão; a diferença afeta sobretudo His57.

## 4. Critérios congelados antes de abrir qualquer resultado (pré-registro)

1. Conjunto candidato: RESISTENTE do filtro linear estrito (E0). Sem mais cortes.
2. Top-1 = maior confiança média (E2) entre os RESISTENTE da espécie.
3. "S1 ancorado" = ocupância ≥70% a 5 Å do Asp189-equivalente, âncora definida empiricamente; 4 e 6 Å reportados.
4. QC de pose: clash <2,2 Å = 0 pares; ω |≥150°|; quiralidade L; tríade mantida; contato com P1 básico ≤4,5 Å só é
   exigido quando há K/R (não é critério de exclusão para os demais).
5. Nenhum limiar é alterado depois de ver dados; qualquer mudança vai registrada em "emendas" neste arquivo.

## 5. Reescrita do manuscrito (em paralelo ao servidor)

Título/Abstract/Palavras-chave → linear; Introdução reenquadrada no grupo e na tensão P1 básico × clivagem; Métodos
2.4–2.9 (sementes cíclicas, filtro estrito, Boltz-2 linear, E2–E7); Resultados 3.4–3.8 (3.8 = comparação com o
macrociclo) e Discussão (4.3 defende o critério e expõe seu custo com os dados de E6; 4.5 macrociclização, D-aa/Nle/Orn,
*capping*); Limitações (exopeptidases, backbones sob fechamento, ProteinMPNN sem receptor fixo, Boltz-2 não validado em
5–8 aa, seletividade exploratória); Fig. 3 recalculada; Fig. 1; versão PT.

## 6. Literatura (nenhuma referência sem Crossref/PubMed)

RAG (servidor): Saikhedkar 2019, Kelly 2005, Laskowski 2000, Patarroyo-Vargas 2017/2020, Almeida 2021/2022,
Meriño-Cabrera 2022, Schultz 2026; novas candidatas: Paulo 2026 (GORE3), Severi-Castro 2026 (PEP-11). A verificar:
SFTI-1 acíclico; carboxi/aminopeptidases do intestino médio de Lepidoptera; exceções da regra K/R–Pro da tripsina;
hidrólise lenta em inibidores canônicos; sequências e Ki de GORE1–5 (extrair dos PDFs do corpus).

## 7. Decisões pendentes do autor (recomendação em negrito)

1. Disparar E1 já (6 h, independente das demais) enquanto as etapas a construir são escritas? **Sim.**
2. MD final: pipeline do grupo CHARMM36 pH 8,2 (**recomendado**) ou `MDAgent` antigo (AMBER99SB-ILDN, pH 10)?
3. Incluir GORE1/GORE2 como pontos de referência descritivos (não calibração) nos mesmos receptores? O autor já
   cortou a calibração de potência contra a série GORE em 28/09; **padrão: não incluir**.
4. Extremidades livres (carregadas, como nos ensaios do grupo — **recomendado**) ou protegidas (Ac/NH₂)?
5. E5 (contra-triagem exploratória): manter no texto como exploratória (**recomendado**, dado o peso permanente da
   especificidade) ou omitir?

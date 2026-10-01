# Estado consolidado — 01/10/2026 (tarde)

Complementa `ESTADO_CONSOLIDADO_2026-09-30.md` e `PLANO_LINEAR_2026-09-30.md`. Nenhum limiar pré-registrado foi alterado.

## 1. O que aconteceu desde 30/09
- **E2 concluído** (frentes L e M; 5 amostras × 3 sementes, com potenciais), **E2qc/E2b/E4 concluídos** às 01:17; **E6 (MD 10 ns, CHARMM36) em curso** desde 01:17 (`screen two-fronts`, log `outputs/e1_fix_pipeline.log`).
- Às 13:44: 11 de 48 MDs concluídas, nenhuma com erro (L: *A. gemmatalis* ×3, *S. frugiperda* ×3, *S. litura* ×2; M: *A. gemmatalis* ×3). Faltam ~37 (≈ 25 h, GPU compartilhada).
- **E7 testado pela primeira vez em trajetória CHARMM real** (CPU, fora do pipeline): funciona; achou e corrigiu um bug (§4).
- Figuras novas 9, 10, 11 e S2 (CHARMM36); manuscrito EN e PT atualizados; laço incremental de análise ligado no servidor.

## 2. Resultados (todos conferidos nos JSON; `data-e2-results/`)
| Item | Resultado |
|---|---|
| E2, confiança média dos top-10 | L 0,922 → 0,900; M 0,911 → 0,888 (Δ −0,021 / −0,023: regressão à média); ρ(E1,E2) = 0,80 / 0,74 |
| Ruído dentro do candidato | DP de 0,019 (L) e 0,022 (M) entre as 15 predições, da ordem da dispersão dentro de uma espécie: **a ordem dentro do top-10 não é resolvida** |
| L × M (22 sequências comuns nos top-10) | ρ = 0,60; M abaixo de L em 0,016 |
| QC de pose | 80/80 candidatos com ≥ 1 amostra aprovada; fração média das amostras aprovadas 0,98 (L) / 0,95 (M); **não comparável** aos 18% do E1 (outro conjunto, com potenciais) |
| Top-3 por espécie (48) | 48/48 passam o QC; tríade íntegra (His57–Ser195 2,4–3,4 Å); distância inicial ao Asp189 ≤ 5 Å em 9/24 (L) e 18/24 (M) |
| K/R nos 48 finais | só 3: NGGRPDAP (L), PISQIDSGSR e GGKPGEP (M) |
| Sequências iguais nos dois top-3 | 3/24: GQNDS (*O. nubilalis*), NGGTT (*H. virescens*), GGSQSS (*A. gemmatalis*) |
| **MD 10 ns, triagem pré-registrada (provisório, 11/48)** | **L: 1/8 passa** (NGGRPDAP, Arg4 em S1 a 2,7 Å, ocupância 1,00/1,00); GTDEN 0,61/0,63 falha na ocupância; demais ≤ 0,07. **M: 0/3** (GGKPGEP, Lys3 em S1, ocupância 1,00/1,00, falha só no critério do anel) |
| Anel (M, 3 simulações) | C–N máx 1,43–1,45 Å (≤ 1,5); ω mínimo 144,5° / 147,7° / 149,0° (critério: ≥ 150° em todos os quadros); **\|ω\| ≥ 150° em 99,6–99,8% dos quadros, nunca < 140°** |
| Dissociação | nenhuma: em 11/11 o peptídeo ficou < 4,5 Å do receptor em todos os quadros (sair de S1 ≠ dissociar) |
| Contato com Ser195/His57 | 0,70–1,00 / 0,54–1,00 mesmo com a âncora longe de S1: **não discrimina** candidatos |
| Rg ~2 nm (pendência de 30/09) | Rg inicial de receptor + peptídeo = 1,67–1,86 nm em 3 sistemas, receptores de 259–268 resíduos: compatível com tripsina-like; **sem anomalia** |

## 3. Revisão crítica (o que o conjunto sustenta e o que não)
1. **Só candidatos com resíduo básico ancorado em S1, protegido por Pro em P1′, ficaram em S1**; os sem K/R saíram do bolso ou nunca entraram. Reforça a tensão resistência × S1 canônico (Discussão 4.3) e o achado I6 do V1. Ainda provisório (2 de 11).
2. **Confusão com a pose inicial:** os dois que passam começaram a ≤ 3,5 Å do Asp189; os quatro sem K/R que começaram a 4,1–4,3 Å terminaram com 0,00–0,63. Em 10 ns a MD testa a **estabilidade da pose de partida do Boltz-2**, não a capacidade de encontrar S1. O texto já diz "descrições de trajetórias únicas".
3. **Sem E3 não há evidência de que a confiança dos candidatos supere a de controles embaralhados** (a calibração mostrou isca com 0,944). E3 roda depois das MDs.
4. **Critério do anel é uma estatística de cauda** (mínimo de 501 quadros). Os três anéis estão íntegros na prática; o critério foi aplicado como registrado e a decisão de emendá-lo é dos autores (seria emenda pós-dados, a registrar).
5. Ruído do Boltz-2 e viés de seleção (regressão à média) estão declarados; E2 não resolve a ordem do top-10.
6. Pendentes inalterados: E5 (contratriagem) não construída ⇒ **nenhuma seletividade afirmada**; extremidades do linear em pH 10 (NH₃⁺/COO⁻ como limitação).

## 4. Incidentes e correções desta sessão
- **E7 × CHARMM:** o seletor `protein` do MDAnalysis ignora `GLUP` (Glu protonado do CHARMM36); em *A. gemmatalis* r3 (GTDEN) o Glu sumia do peptídeo e a checagem de sequência falhava. Corrigido em `analyze_md_top_candidates.py` (inclui os nomes de `_STD_RES`); todas as simulações concluídas foram reanalisadas (a versão antiga ficou em `analysis_summary_prefix_glup_bug.json`). Nos receptores analisados o número de resíduos não mudou (260/266).
- `analyze_md_top_candidates.py` agora grava `analysis_timeseries.npz` por simulação (para as figuras). Só esse arquivo mudou no servidor; `md_agent.py`/runner **não** foram tocados (o pipeline reinicia o runner a cada lote).

## 5. Plano das próximas etapas (e estado)
| # | Etapa | Quem/onde | Estado |
|---|---|---|---|
| 1 | Terminar E6 (≈ 37 MDs: restante de L, depois M) | `screen two-fronts` (automático) | **em curso**, ≈ 25 h |
| 2 | Análise E7 incremental de cada MD ao terminar | laço `/tmp/e7_incremental.sh` (CPU, `nice`); para sozinho quando o pipeline chegar ao `[E7]` | **ligado** |
| 3 | E7 final, E3 (controles), matriz 8 × 8, E8 (L × M), E9 (lista para a MD longa) | pipeline | após o E6 |
| 3b | Campanha de pH: L pH 10 N-terminal neutro, L pH 8,2, M pH 8,2 (72 MDs, A. gemmatalis primeiro) + Figura 12 | `screen ph-campaign` | espera `TWO_FRONTS_ALL_DONE` |
| 4 | Reexecutar `make_figures_e2_md.py` com os dados completos (copiar `outputs/` → `data-e2-results/`); figura L × M; fechar 3.8–3.10, Resumo, 4.1/4.3 | local | após o item 3 |
| 5 | Decisões (01/10): critério do anel **mantido** + fração de quadros com \|ω\| ≥ 150° como secundário pós-dados; **pipeline atual permanece**; depois, campanha `run_ph_campaign.sh` com N-terminal neutro do linear em pH 10 (pKa 7,7; Grimsley 2009) e pH 8,2 (linear e macrociclo), comparação pareada e Figura 12 (`compare_ph_conditions.py`); réplicas com pose alternativa só depois | autor | **agendado** (`screen ph-campaign`, espera o fim do pipeline) |
| 6 | Pendências editoriais (autores, DOI do código, IA, financiamento) | autores | aberto |

Recuperação: se o E6 parar, olhar `outputs/e1_fix_pipeline.log` e `outputs/md10_*/summary.json` (`status: erro`); **nunca** `pkill -f` na linha do ssh nem `screen -X quit` (ver memória `feedback_ssh_servidor_cuidados`).

## 6. Arquivos novos
`data-e2-results/` (JSON e séries temporais), `manuscript/figures/make_figures_e2_md.py`, `manuscript/figures/{Figure9,Figure10,Figure11,FigureS2_cyclic_ring}*` (EN) e `figures/pt/fig9,fig10,fig11,figS2_anel*` (PT; cópia em `figures_ready_2026-10-01/`). As Figuras 9 e 10 usam dados finais (E2/E4 concluídos); a 11 e a S2 usam dados **provisórios** (11/48 MDs) e a legenda da 11 diz isso.

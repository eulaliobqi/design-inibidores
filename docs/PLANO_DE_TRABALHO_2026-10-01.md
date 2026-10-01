# Plano de trabalho — atualizado em 01/10/2026 (fim da tarde)

Consolida o que foi feito e o que falta. Fontes: `ESTADO_CONSOLIDADO_2026-09-30.md`, `ESTADO_CONSOLIDADO_2026-10-01.md`, `PLANO_LINEAR_2026-09-30.md` (§6 emendas). **Nenhum limiar pré-registrado foi alterado.**

## 1. Onde estamos
| Bloco | Estado |
|---|---|
| Painel de 8 espécies, subsítios, calibração, geração, filtros (L = 527, M = 543) | concluído |
| E1 (Boltz-2 nas duas frentes, 1.070 predições) | concluído |
| E2 (reescore 5 × 3) e E4 (QC de pose) | concluídos: 48 candidatos finais, 48/48 passam no QC |
| E6 (MD de 10 ns, CHARMM36, pH 10) | **em curso: 12/48** (L 9, M 3), 0 erros; ~36 restantes (~25 h) |
| E7 (análise da MD) | testado em trajetória real; laço incremental no servidor analisa cada MD ao terminar |
| E3 (controles embaralhados), matriz 8 × 8, E8, E9 | aguardam o fim do E6 (mesmo pipeline) |
| Campanha de pH (linear pH 10 N-terminal neutro, linear pH 8,2, macrociclo pH 8,2; 72 MDs) | **agendada** (`screen ph-campaign`, espera `TWO_FRONTS_ALL_DONE`) |
| Manuscrito EN/PT | 3.8 preenchida; 3.9/3.10 provisórias (`[[INTERIM]]`); Figuras 9–11 e S2 geradas; Resumo e 4.1 pendentes |

**Resultado provisório da triagem (12/48):** linear 1/9 passa (NGGRPDAP, Arg4 em S1 a 2,7 Å); macrociclo 0/3 (GGKPGEP, Lys3 em S1, falha só no ω do anel: mínimo 144,5° contra 150°; |ω| ≥ 150° em 99,6–99,8% dos quadros). Só K/R ancorado em S1 e protegido por Pro em P1′ ficou no bolso; os dois partiram a ≤ 3,5 Å do Asp189. Nenhuma dissociação nas 12.

## 2. Decisões vigentes (registro)
1. Critério do anel: **estrito e mantido**; fração de quadros com |ω| ≥ 150° só como descrição secundária pós-dados (respaldo: σ(ω) ≈ 6°, MacArthur e Thornton 1996, 10.1006/jmbi.1996.0705).
2. **Pipeline atual permanece** (decisão do autor, 01/10); parar/relançar foi negado pelo classificador de permissões e não será tentado sem autorização explícita.
3. **N-terminal do linear neutro em pH alto** (pKa 7,7 ± 0,5; Grimsley 2009, 10.1002/pro.19), regra pH − 7,7 ≥ 2, Pro inicial mantém PRO-NH2+ (1 de 24); implementado (commit b25bbe8). As 24 MDs lineares em curso usam NH₃⁺ e viram o braço de referência.
4. **Duas faixas de pH** (10,0 e 8,2) comparadas depois, com análise pareada e Figura 12; 8,2 = protocolo do grupo e limite inferior da faixa alcalina adotada (variável `PH_LOW`).
5. Réplicas com pose inicial alternativa: só depois do E6/campanha, apenas para quem falhou sem chegar a S1.

## 3. Cronograma e dependências
| # | Etapa | Depende de | Duração estimada | Responsável |
|---|---|---|---|---|
| 1 | Terminar E6 (36 MDs) | — | ~25 h | pipeline (automático) |
| 2 | E7 final (L e M; o braço linear com NH₃⁺ é o próprio `md10_L`) | 1 | minutos | pipeline |
| 3 | E3 (controles embaralhados 3 sementes × 2 frentes), matriz 8 × 8 | 2 | ~6 h (GPU, Boltz) | pipeline |
| 4 | E8 (L × M) e E9 (lista para a MD longa) | 3 | minutos | pipeline |
| 5 | **Campanha de pH** — fase 1: A. gemmatalis nas 3 condições (9 MDs) + Figura 12 parcial | 4 | ~7 h | `ph-campaign` |
| 6 | Campanha de pH — fase 2: demais espécies (63 MDs) + Figura 12 final | 5 | ~2–3 dias | `ph-campaign` |
| 7 | Recopiar `outputs/` → `data-e2-results/`, rodar `make_figures_e2_md.py`; figura L × M; trocar `[[INTERIM]]`; escrever 3.9, 3.10 e a seção de pH; fechar Resumo, 4.1 e 4.3 | 4 (parte), 6 (pH) | 1 dia | local |
| 8 | Réplicas com semente/pose alternativa nos candidatos relevantes (escolha após ver 4–6) | 6 | a definir | autor decide |
| 9 | MD longa dos melhores (lista do E9) | 4 | — | autor |
| 10 | Pendências editoriais: autores, afiliações, contribuições, financiamento, conflito de interesses, IA generativa, DOI do código, conferir Valaitis/Yang/Zhan/Severiche no texto completo | — | — | autores |

Caminho crítico: 1 → 3 → 5 → 6 → 7 ≈ 4–5 dias de relógio com a GPU compartilhada. A Figura 12 parcial (fase 5) chega ~2 dias antes do fim.

## 4. Riscos e mitigação
| Risco | Mitigação |
|---|---|
| Confusão entre pose inicial e capacidade de encontrar S1 (os que passam partiram a ≤ 3,5 Å) | declarado no texto; item 8 (poses alternativas); MD de 10 ns = estabilidade da pose |
| Uma réplica por candidato | resultados descritivos; comparação de pH por tendência entre candidatos, não por candidato |
| GPU compartilhada com jobs do grupo (OOM com duas cargas) | uma carga por vez; campanha só depois do pipeline; sequência única |
| E3 pode mostrar que a confiança não supera a de controles embaralhados | resultado será reportado como está; texto já cauteloso (isca de 0,944) |
| Escopo: trabalho só computacional, revista pode pedir validação | decisão dos autores; declarado em 4.4 |
| Falha de MD isolada | runner marca `status: erro` e continua; conferir `summary.json` |

## 5. Como recuperar
- Pipeline: `outputs/e1_fix_pipeline.log`; campanha: `outputs/ph_campaign.log`; MDs: `outputs/md10_*/summary.json`, `outputs/mdph_*/summary.json`; análise: `analysis_summary.json` e `analysis_timeseries.npz` em cada pasta.
- **Nunca** `pkill -f` na linha do ssh nem `screen -X quit` (ver memória `feedback_ssh_servidor_cuidados`); parar/relançar só com autorização explícita do autor.
- Figuras: `manuscript/figures/make_figures_e2_md.py DATA OUT en|pt`; comparação de pH: `scripts/compare_ph_conditions.py --root outputs --out outputs/ph_comparison [--lang pt]`.
- Manuscrito: EN `manuscript_src.md` → `render.py`; PT `pt_parts/` → `build_docx_pt.py`.

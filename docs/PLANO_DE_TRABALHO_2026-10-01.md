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
5. **Sem réplicas** (decisão do autor, 01/10): o prazo de submissão é curto e as MDs servem para **verificar a estabilidade** da pose, não para estimar afinidade; uma réplica de 10 ns por candidato é o desenho final e as conclusões são descritivas. **Objetivo final: a lista dos melhores peptídeos com potencial inibidor, com base em dados computacionais** (ranqueamento em camadas, `scripts/rank_final_candidates.py`, Figura 13).

## 3. Cronograma e dependências (recalculado em 01/10, com tempos medidos)

**Ritmo medido em 16 simulações:** 75–105 min por MD (produção de 69 min em média, 98 min nas cinco últimas; o
resto é montagem e equilíbrio). A variação é disputa de GPU com os jobs do grupo. O E3 foi recalculado a partir do
E2 (480 predições em 6,2 h, 46 s cada): com 1.413 predições, custa **15–20 h**, e não as ~6 h do plano v3.

| # | Etapa | Depende de | Custo medido | Responsável |
|---|---|---|---|---|
| 1 | Terminar o E6 (32 MDs) | — | **40–56 h** | pipeline (automático) |
| 2 | E7 final (L e M) | 1 | minutos | pipeline |
| 3 | E3 (1.413 predições) | 2 | **15–20 h** | pipeline |
| 4 | Matriz 8 × 8, E8 (L × M), E9 (lista de entrega) | 3 | ~1 h | pipeline |
| 5 | **Controles de MD** (5 MDs nas iscas dos próprios candidatos) | 3 | **6–9 h** | `screen md-controls` |
| 6 | Refazer Figuras 9–13, trocar os `[[PROVISÓRIO]]`, escrever 3.9/3.10/3.11, Resumo, 4.1 e 4.3 | 4 e 5 | ~1 dia (sem GPU) | local |
| 7 | Seções dos autores e submissão | — | — | autores |

**Total de processamento até poder fechar o artigo: 62–86 h, ou seja, 2,7 a 3,5 dias.** O item 6 corre em paralelo
ao fim do processamento. Caminho crítico: 1 → 3 → 5, com o 4 em paralelo ao 5.

**Fora deste artigo (decisão do autor, 01/10):** a campanha de duas faixas de pH (72 simulações, 4–5 dias, dois
terços de todo o processamento restante) foi **cancelada** e fica para um artigo seguinte. Os scripts
(`run_ph_campaign.sh`, `run_md_ph_campaign.py`, `compare_ph_conditions.py`) e a regra do N-terminal dependente do pH
continuam versionados e prontos. Consequência para o texto: todas as simulações deste artigo compartilham um só
estado de protonação, o que as mantém comparáveis entre si; a comparação de pH e de carga do N-terminal passa a ser
trabalho futuro (Seção 4.5), e o NH₃⁺ do peptídeo linear em pH 10 continua declarado como limitação (4.4 viii).

## 4. Riscos e mitigação
| Risco | Mitigação |
|---|---|
| Confusão entre pose inicial e capacidade de encontrar S1 (os que passam partiram a ≤ 3,5 Å) | declarado no texto como limitação; MD de 10 ns = estabilidade da pose prevista |
| Uma réplica por candidato (sem réplicas, por decisão) | resultados descritivos; comparação de pH por tendência entre candidatos, não por candidato; MDs são verificação de estabilidade |
| GPU compartilhada com jobs do grupo (OOM com duas cargas) | uma carga por vez; com a campanha de pH cancelada, só o pipeline e, depois do E3, os controles disputam a GPU |
| E3 pode mostrar que a confiança não supera a de controles embaralhados | resultado será reportado como está; texto já cauteloso (isca de 0,944) |
| Escopo: trabalho só computacional, revista pode pedir validação | decisão dos autores; declarado em 4.4 |
| Falha de MD isolada | runner marca `status: erro` e continua; conferir `summary.json` |

## 5. Como recuperar
- Pipeline: `outputs/e1_fix_pipeline.log`; campanha: `outputs/ph_campaign.log`; MDs: `outputs/md10_*/summary.json`, `outputs/mdph_*/summary.json`; análise: `analysis_summary.json` e `analysis_timeseries.npz` em cada pasta.
- **Nunca** `pkill -f` na linha do ssh nem `screen -X quit` (ver memória `feedback_ssh_servidor_cuidados`); parar/relançar só com autorização explícita do autor.
- Figuras: `manuscript/figures/make_figures_e2_md.py DATA OUT en|pt`; comparação de pH: `scripts/compare_ph_conditions.py --root outputs --out outputs/ph_comparison [--lang pt]`.
- Manuscrito: EN `manuscript_src.md` → `render.py`; PT `pt_parts/` → `build_docx_pt.py`.

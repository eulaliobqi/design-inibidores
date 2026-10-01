# Auditoria técnica e plano de correções — 01/10/2026

Revisão independente do que foi produzido até aqui, confrontando o protocolo com a prática padrão
(GROMACS/CHARMM36 e boas práticas de simulação). Cada item diz **o que foi verificado de fato**, com o número
medido, e o que **não** foi verificado. Referências conferidas no Crossref.

---

## 1. Verificado e correto (nenhuma ação)

| # | Verificação | Resultado medido |
|---|---|---|
| V1 | **Mapeamento do sítio catalítico nos 8 receptores** (o mais crítico: toda a métrica de S1 depende dele) | O Asp de S1 é mesmo ASP nos 8; His57 Nε2–Ser195 Oγ = **2,38–3,40 Å** (ligação de hidrogênio catalítica); Asp189–Ser195 = **9,97–10,92 Å**, compatível com tripsina bovina (≈10 Å). O bug isolado de *H. virescens* de uma fase anterior **não** está presente. |
| V2 | Diedro ω do fechamento do anel (CA(n)–C(n)–N(1)–CA(1)) | Ordem dos vetores correta; átomos tornados contíguos por imagem mínima antes do cálculo. |
| V3 | Correção de PBC e referencial do RMSD local | Peptídeo tornado inteiro e trazido para a imagem mais próxima do Asp-S1; rotação do receptor aplicada no mesmo referencial da estrutura de referência. Consistente. |
| V4 | Chave de junção do E3 (`stem`) entre `rescore_boltz2_topk.delta`, `deliver_md_long` e `rank_final_candidates` | Idêntica nos três (`<especie>__<backbone>__<idx>`). Não vai falhar silenciosamente quando o E3 rodar. |
| V5 | CHARMM36: vdW force-switch 1,0–1,2 nm e `DispCorr = no` | Correto e exigido por este campo de força. |

## 2. Erros encontrados e corrigidos nesta revisão

| # | Erro | Evidência | Correção |
|---|---|---|---|
| **F1** | **Equilibração NPT usava Parrinello-Rahman**, embora o cabeçalho do próprio template dissesse "Berendsen" — o código contradizia o comentário. PR não tem relaxação de 1ª ordem e pode oscilar partindo de estado não equilibrado; para equilibração usa-se barostato de relaxação. | `scripts/agents/md_agent.py` linha 91 (comentário) × 110 (código); `npt.mdp` das 48 corridas. | Trocado para **C-rescale**, que amostra o ensemble correto e é o sucessor recomendado do Berendsen (Bernetti e Bussi 2020, [10.1063/5.0020514](https://doi.org/10.1063/5.0020514)). Produção segue Parrinello-Rahman. |
| **F2** | **`refcoord_scaling` ausente** com position restraints + acoplamento de pressão: as coordenadas de referência não acompanham o reescalonamento da caixa. | `npt.log` das corridas: `refcoord-scaling = No`. | Acrescentado `refcoord_scaling = com`. |
| **F3** | Validação do sítio aceitava resíduo errado: `startswith("AS")` casa **ASN**, que tem OD1 mas não OD2 — devolveria meio carboxilato sem erro. | `analyze_md_top_candidates.get()`. | Comparação exata do nome + conferência do número de átomos selecionados. (Na prática os 8 receptores têm ASP, V1; o risco era latente.) |
| **F4** | Chave `peptide_rmsd_local_nm_last10ns` continha, na verdade, os **últimos 20%** (2 ns numa corrida de 10 ns) — nome correto só para as corridas antigas de 50 ns. | Código: `late = t_ns >= 0.8 * t_ns.max()`. | Renomeada para `final20pct`; as janelas `early`/`late` passam a ser gravadas em ns no próprio JSON. Nenhum número do manuscrito vinha desta chave. |
| **F5** | Métodos 2.9 relatava valores "no início" e "no fim" sem definir as janelas. | Seção 2.9 × Seção 3.9. | Janelas definidas no texto (EN e PT): início = primeiros 4% (0,4 ns), fim = últimos 20% (2 ns). |

**Alcance de F1/F2, medido:** densidade **1022–1033 kg/m³** com RMSD ≈2 kg/m³ (**0,2%**) e deriva <1,2 kg/m³;
volume com RMSD ≈0,2% (3 sistemas, NPT e produção). **Não houve oscilação de caixa nem artefato mensurável** — os
dois desvios são reais em relação à prática padrão, mas não produziram efeito detectável nestas corridas, e as 48
MDs **não precisam ser refeitas**.

**Decisão sobre F1/F2:** **não corrigir agora.** Trocar o barostato no meio deixaria parte das simulações num
protocolo e parte noutro e, pior, confundiria a campanha de pH, cuja única variável deve ser o pH/N-terminal. A
correção fica registrada no código (comentário em `md_agent.py`) e se aplica à MD longa e a trabalhos futuros.

### F6 — Risco de troca de protocolo no meio do conjunto (encontrado e eliminado)
A regra do N-terminal neutro foi enviada ao servidor às 15:18 com `nterm="auto"` por padrão. O processo do runner
da frente linear começou às **08:56**, antes disso, e por isso manteve o módulo antigo em memória: as 13 MDs
lineares saíram **todas** com N-terminal carregado (`GLY-NH3+`/`NH3+`/`PRO-NH2+`, `nterm_neutral` ausente em todos
os `build_report.json`, inclusive o de 19:48). O conjunto está uniforme — **por acaso de carregamento de módulo,
não por desenho**: bastava o pipeline iniciar um processo novo para o protocolo mudar no meio. Corrigido: o padrão
de `build_system_charmm.build` passou a ser `nterm="charged"` e o modo virou parâmetro explícito
(`md.nterm`), que só a campanha de pH pede como `auto`; o modo usado fica gravado no resumo de cada simulação.

## 3. Fragilidades de método (decisão necessária, não são bugs)

| # | Fragilidade | Quantificação / base |
|---|---|---|
| **W1** | **Não há controle positivo nem negativo nas MDs.** O limiar de 70% de ocupância de S1 não tem escala de referência: não se sabe quanto um inibidor real marca no mesmo protocolo. É a maior lacuna para a afirmação final. | — |
| **W2** | **Os controles embaralhados do E3 são fracos nos candidatos ricos em Gly** (embaralhar `GGGGH` quase não muda a sequência). | Medido: identidade média candidato × embaralhado **0,35 (L)** e **0,29 (M)**; **5 candidatos ≥60%** idênticos aos próprios controles (GPGGGTG, HGGGGSG, GISGS, GHHGGG, GGHGGG); **6 candidatos** têm só 2 controles distintos dos 3 gerados. |
| **W3** | **O critério "Δ > 0" não tem limiar de incerteza.** O desvio-padrão interno de um candidato no E2 é ≈0,02, então um Δ de +0,005 é ruído. | DP médio no E2: 0,019 (L), 0,022 (M). |
| **W4** | **Uma réplica por candidato.** Trajetórias únicas produzem conclusões falso-positivas — é exatamente o ponto de Knapp, Ospina e Deane 2018 ([10.1021/acs.jctc.8b00391](https://doi.org/10.1021/acs.jctc.8b00391), JCTC 14:6127). O autor decidiu não fazer réplicas (prazo). | A correção aqui é **de enquadramento**, não de cálculo: a entrega é uma lista priorizada para teste experimental, não uma afirmação de que os peptídeos inibem. |
| **W5** | **A âncora é escolhida post hoc** (resíduo de menor distância média) e depois a ocupância dela é medida — circularidade leve que infla a ocupância frente a um resíduo pré-especificado. | Declarar como escolha descritiva. |
| **W6** | **10 ns testam a estabilidade da pose prevista, não a capacidade de encontrar S1.** Os dois candidatos que passaram partiram a ≤3,5 Å do Asp189; os que partiram a 4,1–4,3 Å terminaram entre 0,00 e 0,63. | Confundimento já observado nos dados; precisa estar explícito. |

## 4. Plano de correções, por valor sobre custo

| P | Ação | Custo | Depende de |
|---|---|---|---|
| **P1** | ~~Medir o efeito de F1/F2~~ **feito**: sem artefato (densidade estável a 0,2%). Resta **declarar** o desvio e a medição nos Métodos. | ~15 min, sem GPU | — |
| **P2** | **Controles de MD** (resolve W1): rodar o mesmo protocolo de 10 ns em 2–3 complexos **que o projeto já tem**, da calibração — um inibidor natural (BPTI–tripsina, 2PTC; e/ou SFTI-1) e uma isca embaralhada. Dá a escala do limiar de 70% e transforma "70% é arbitrário" em "70% contra X% de um inibidor real". | ~2–3 simulações (≈3 h de GPU) | servidor; decisão do autor |
| **P3** | Declarar W2, W3, W5 e W6 no manuscrito com os números já medidos (tabela acima); acrescentar ao Δ do E3 o tamanho de efeito (Δ dividido pela dispersão), mantendo "Δ > 0" como critério pré-registrado. | ~1 h, sem GPU | — |
| **P4** | Reenquadrar 3.12/Resumo conforme W4: a saída é uma **lista priorizada para teste experimental**, com o ranking de camadas como triagem de estabilidade; citar Knapp 2018 ao justificar por que não se infere afinidade. | ~1 h, sem GPU | — |
| **P5** | Se o prazo apertar, **cortar parte da campanha de pH antes de cortar P2**: a comparação de pH é um refinamento; os controles são o que sustenta a lista final. | decisão | autor |

**Recomendação:** P1, P3 e P4 são gratuitos e devem entrar. P2 custa ~3 h de GPU e é o item que mais muda a
solidez da entrega final — vale mais que 20 das 72 simulações da campanha de pH.

## 5. O que esta auditoria **não** cobriu
- Efeito empírico de F1/F2 nas 48 corridas (servidor fora do ar durante a checagem).
- Qualidade das predições do Boltz-2 em si (não há estrutura experimental destes complexos para comparar).
- Revisão linha a linha de `pose_qc.py`, `rescore_boltz2_topk.py` e `build_system_charmm.py` (só as interfaces usadas pelos resultados).
- Conferência no texto completo das citações Valaitis, Yang, Zhan e Severiche (pendência antiga).

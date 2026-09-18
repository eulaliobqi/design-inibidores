# B0.5 — Consolidação final: figura, tabela e decisão de scoring

**Data:** 2026-09-18 | Fecha o bloco ★ B0.5 do `docs/PLANO_V2_GENERATIVO.md`. Reúne os 4 rungs da
escada de calibração (Boltz-2, HADDOCK3, MD/RMSD, MM-PBSA) rodados nas sessões anteriores —
ver `b05_calibracao_haddock3_boltz2.md`, `b05_completo_5controles_apti.md`,
`b05_md_curta_completo.md`, `b05_mmpbsa_completo.md` para o detalhe metodológico e os bugs
corrigidos em cada etapa. Este documento só consolida: nenhum dado novo foi gerado aqui.

## Figura

`outputs/b05_figs/figA_calibracao_b05_escada.png` (+ `.pdf` vetorial, `.manifest.json` de
proveniência) — painéis A-C comparam real vs. decoy por inibidor/receptor em cada método
(Boltz-2 confidence, RMSD médio, MM-PBSA ΔG); painel D resume a taxa de separação por método
contra a linha de acaso (50%). Cores redundantes com marcador (círculo azul = tripsina bovina,
quadrado laranja = *S. frugiperda*; preenchido = inibidor real, vazio = decoy; linha tracejada
= decoy venceu o real). ApTI (sem decoy pareado nos dois receptores) fica fora dos painéis A-D
por não ter par para comparar, mas está na tabela completa.

## Tabela

`outputs/b05_figs/tabela_consolidada_b05.csv` (formato de dados) e
`outputs/b05_figs/tabela_consolidada_b05.md` (leitura) — 22 linhas, uma por sistema, com todas
as métricas lado a lado: Boltz-2 (confidence/ipTM/pLDDT), HADDOCK3 (score rigidbody, só para os
10 reais, sem decoy pareado nesse rung), RMSD médio + H-bonds + Rg (MD 2ns), MM-PBSA ΔG_TOTAL ±
SEM (GB, trajetória única).

## Resultado consolidado — taxa de separação real-vs-decoy por método (n=10 pares/método)

| Método | Separou corretamente | Nota |
|---|---|---|
| **Boltz-2** (confidence_score/pLDDT) | **10/10** | único método validado nesta calibração |
| HADDOCK3 | não testado | sem decoys pareados neste rung |
| RMSD (MD 2ns, complexo inteiro) | 5/10 | equivalente a acaso — limite herdado do V1 (não separa cadeias) |
| MM-PBSA (GB, trajetória única) | 4/10 | **pior que acaso** — decoy "vence" por até +144,8 kcal/mol em 1 par |

## Decisão registrada

Usuário confirmou (2026-09-18): **o loop de contrasseleção B2.7 usa só Boltz-2**
(`confidence_score`/pLDDT) como scorer da margem `margem = score_alvo − max(score_painel) −
penalidades`. Já refletido em `docs/PLANO_V2_GENERATIVO.md` §B2.7 (commit `425db5a`).

**Pendência sinalizada, não resolvida aqui**: os critérios de sucesso S1/S3 do plano ainda
listam ΔG MM-PBSA e RMSD/ocupância como validação *final* (n=3 réplicas, presumivelmente
protocolo mais longo que o calibrado aqui). Precisa de revisão futura à luz deste resultado —
ver `memory/project_plano_v2_generativo.md`.

## B0.5 — encerrado

Todos os 4 rungs da escada rodados nos 22 sistemas do painel de calibração (2 receptores × 6
inibidores reais + 10 decoys pareados). Bloco ★ do plano concluído. Próximos passos naturais:
**B1.2** (painel negativo completo) e **B1.5** (determinantes de seletividade alvo×antialvo),
ambos bloqueando o loop B2.7.

# B0.5 — painel completo: 6/6 controles reais no Boltz-2, 5/5 no HADDOCK3 (verificado)

**Data:** 2026-09-18 | continuação de `b05_calibracao_haddock3_boltz2.md`

## ApTI modelado (Boltz-2) — painel de 6 controles completo

ApTI (P09941 cadeia α + P09942 cadeia β, *Adenanthera pavonina*) não tem PDB experimental.
Modelei via Boltz-2 (co-dobramento de 3 cadeias: receptor + α + β) contra os 2 receptores:

| Par | confidence_score | ipTM | pLDDT |
|---|---|---|---|
| ApTI × tripsina bovina | 0.923 | 0.893 | 0.931 |
| ApTI × *S. frugiperda* | 0.850 | 0.775 | 0.869 |

Valores na mesma faixa dos outros 5 controles reais (0,85-0,99) — consistente com ApTI ser
mesmo um inibidor real de tripsina. **Não gerei decoy para ApTI** (ficaria para uma rodada
futura se precisar fechar 6/6 com decoy também).

## HADDOCK3 — sítios reativos REAIS verificados por complexo experimental (não literatura)

Em vez de confiar em números de memória para SKTI/Bowman-Birk/EcTI, baixei os complexos
experimentais reais do RCSB e identifiquei o resíduo P1 por contato direto (<6 Å) com o Ser
catalítico real de cada estrutura:

| Controle | Complexo real usado | P1 real identificado por contato | Bate com o que eu tinha em mente? |
|---|---|---|---|
| SKTI | **1AVX** (SKTI × tripsina) | **Arg63** | sim, mas MEDIDO agora, não assumido |
| Bowman-Birk | **1D6R** (BBI × tripsinogênio) | **Lys16** | sim, mas MEDIDO agora, não assumido |
| EcTI | **4J2Y** (EcTI × tripsina) | **Arg64** | sim, mas MEDIDO agora, não assumido |

Isso é o padrão certo: eu tinha esses números "de memória" da sessão anterior de research, mas
não ia usá-los numa restrição real sem confirmar — e a confirmação direta (achar os complexos
de verdade e medir contato) é mais forte que qualquer citação de literatura.

**Bug real encontrado e corrigido:** as primeiras 6 corridas (SKTI/BBI/EcTI × 2 receptores)
falharam com `ValueError: Chain/seg IDs are not unique` — eu tinha esquecido de renomear a
cadeia do ligante de A (herdada do PDB original) para B antes de montar o sistema HADDOCK3 (só
tinha feito isso certo para BPTI/SFTI-1 na rodada anterior). Corrigido, as 6 rodaram limpo.

## HADDOCK3 completo: 5/5 inibidores reais × 2 receptores

| Controle | × tripsina bovina | × *S. frugiperda* |
|---|---|---|
| BPTI | -17.6 | -25.8 |
| SFTI-1 | -31.6 | -27.7 |
| SKTI | -26.2 | **-58.5** |
| Bowman-Birk | -11.6 | -22.3 |
| EcTI | -20.9 | **-58.0** |

Nenhum incidente de memória em nenhuma das 10 corridas (~20-25s cada, ~5GB RAM). **Ainda sem
decoys no HADDOCK3** — o rung que realmente respondeu "separa inibidor de decoy?" com robustez
(10/10) foi o Boltz-2 (ver doc anterior); o HADDOCK3 fica como segunda fonte de sinal
(concordância qualitativa: SKTI e EcTI pontuam muito mais forte contra *S. frugiperda* que os
outros três, o que é plausível mas não comparado a decoy ainda).

## Estado real de B0.5 agora

- **Boltz-2**: 6/6 controles reais rodados (5 com decoy pareado, 22 predições no total); métrica
  `confidence_score`/`pLDDT` separa real de decoy em 10/10 pares testados. **Rung com Go
  confirmado.**
- **HADDOCK3**: 5/5 controles reais rodados × 2 receptores (10 pares), com sítios reativos
  verificados experimentalmente, sem decoys ainda.
- **MD curta + MM-PBSA**: não iniciado — é o próximo item da escada e, por ordem de grandeza
  (GROMACS real leva horas por réplica mesmo sem contenção de GPU, ver B0.4), é uma campanha
  bem maior que tudo que rodou até agora nesta sessão.

Arquivos: `data-calibration-b05/boltz_calibration_summary.json` (22 entradas),
`data-calibration-b05/haddock3_scores.json` (10 entradas).

# B0.5 — calibração real: HADDOCK3 (rígido) + Boltz-2 (co-dobramento), inibidor vs. decoy

**Data:** 2026-09-18 | **Servidor:** eulalio@200.235.143.10, GPU livre durante toda a corrida
(Ollama sem modelo carregado, 0%/8MiB)

## Contexto

Depois do incidente de memória do Vina (`b05_incidente_vina_memoria.md`), o usuário escolheu
trocar para **HADDOCK3** no rung de docking rígido. Rodei HADDOCK3 para os 2 controles com sítio
reativo verificado (BPTI, SFTI-1) contra os 2 receptores (tripsina bovina real via 1SFI,
*S. frugiperda* via AlphaFold A0A089QDB3), e depois **Boltz-2** (co-dobramento nativo, sem
precisar de restrição de sítio) para o painel completo: 5 controles reais + 5 decoys (mesma
composição, sequência embaralhada) × 2 receptores = 20 predições.

## HADDOCK3 (rígido, `sampling=48`) — 4 corridas, sem incidente

Restrições AIR geradas via `haddock3-restraints active_passive_to_ambig`, usando resíduos
reais verificados nesta sessão: receptor bovino (His57/Asp102/Asp189/Ser195 + pocket 191-193,
213-227, todos confirmados diretamente na estrutura 1SFI), receptor *S. frugiperda* (His70/
Asp114/Asp214/Ser220, confirmados por motivo de sequência), ligante BPTI (Lys15-Ala16, sítio
reativo clássico, confirmado na estrutura real) e SFTI-1 (Lys5, sítio reativo clássico,
confirmado na sequência madura).

| Par | Melhor score HADDOCK (rigidbody) |
|---|---|
| BPTI × tripsina bovina | -17.6 |
| SFTI-1 × tripsina bovina | -31.6 |
| BPTI × *S. frugiperda* | -25.8 |
| SFTI-1 × *S. frugiperda* | -27.7 |

Cada corrida levou ~18-20s, memória estável (~4-5GB, nada anômalo). SKTI/Bowman-Birk/EcTI/ApTI
e os 5 decoys **não entraram no rung HADDOCK3** nesta sessão — identificar o resíduo reativo
real de cada um exigiria confirmar números de literatura que eu não tinha 100% verificados
nesta sessão (risco de fabricação); em vez de arriscar isso, usei Boltz-2 para o painel
completo, que não exige essa informação (co-dobra a partir só da sequência).

## Boltz-2 (co-dobramento, `diffusion_samples=1`) — 20/20 predições, sem incidente

Cada predição: MSA real via servidor público MMseqs2 (~50s) + inferência GPU (~10s). Nenhum
problema de memória (GPU ficou em 0% quando ociosa entre chamadas, uso normal durante
inferência). Resultado completo em `data-calibration-b05/boltz_calibration_summary.json`.

### Real vs. decoy — `confidence_score` (métrica composta do Boltz-2)

| Controle | bovina real | bovina decoy | Δ | *S. frugiperda* real | *S. frugiperda* decoy | Δ |
|---|---|---|---|---|---|---|
| BPTI | 0.962 | 0.796 | +0.166 | 0.877 | 0.755 | +0.122 |
| SFTI-1 | 0.986 | 0.944 | +0.042 | 0.933 | 0.869 | +0.064 |
| SKTI | 0.954 | 0.680 | +0.274 | 0.854 | 0.628 | +0.226 |
| Bowman-Birk | 0.931 | 0.794 | +0.137 | 0.862 | 0.650 | +0.212 |
| EcTI | 0.934 | 0.687 | +0.247 | 0.868 | 0.637 | +0.231 |

**`confidence_score` separa real de decoy em 10/10 pares** (real sempre maior, mesmo no caso
mais apertado, SFTI-1 × bovina, Δ=+0.042). **Vai para a decisão do V2.**

### Quebra por sub-métrica (nem tudo se comporta igual)

- **pLDDT do complexo**: separa 10/10 também, com boa margem em todos os casos (menor Δ ainda
  assim é +0.026, SFTI-1×bovina).
- **ipTM**: separa 9/10, mas **SKTI × *S. frugiperda* é limítrofe** (real=0.711, decoy=0.706,
  Δ=+0.005 — dentro do ruído). Isso é um achado real e específico: para esse par, o ipTM
  sozinho **não deveria entrar como métrica decisiva** (viola a regra de go/no-go do B0.5: "métrica
  que não separa controle de decoy não entra na decisão"), mas o `confidence_score` composto
  (que soma pTM+ipTM+pLDDT) ainda separa esse mesmo par com folga (0.854 vs. 0.628) porque o
  pLDDT compensa.

## Decisão (Go parcial)

**Go para `confidence_score` e `pLDDT` do Boltz-2** como métricas de triagem em B2-B3 — separam
inibidor real de decoy em 100% dos 10 pares testados, incluindo contra o alvo primário real
(*S. frugiperda*), não só contra a referência bovina.

**Ressalva sobre ipTM isolado**: não usar como único critério de corte sem o pLDDT/score
composto — pelo menos 1/10 casos reais (SKTI × *S. frugiperda*) não teria sido separado só por
ipTM.

**HADDOCK3 rígido**: sinal na direção certa nos 4 pares testados (SFTI-1 sempre pontua melhor
que BPTI nos dois receptores, consistente com SFTI-1 ser um inibidor mais compacto/otimizado),
mas **a amostra é pequena (4 pares, sem decoy nenhum ainda)** — não dá para declarar go/no-go
com só isso. Pendência: confirmar os resíduos reativos reais de SKTI (Arg63 citado na
literatura, não reverificado nesta sessão), Bowman-Birk (domínio tripsina-reativo, Lys16 citado,
não reverificado) e EcTI antes de rodar HADDOCK3 com eles + gerar decoys estruturados (não
CA-only) via Boltz-2 para poder dockar no HADDOCK3 também.

## Pendências reais para fechar B0.5 por completo

1. ApTI (P09941/P09942) ainda não entrou — não tem PDB, precisa ser modelado (Boltz-2, sem
   receptor, só para gerar a estrutura) antes de entrar no painel.
2. MD curta + MM-PBSA (últimos 2 rungs da escada do plano) ainda não rodados para nenhum
   controle — são o próximo passo natural, mas são uma campanha bem mais longa (GROMACS,
   ver B0.4: mesmo sem contenção, MD real leva horas por réplica).
3. HADDOCK3 com os controles restantes (SKTI/BBI/EcTI) + decoys, para ter uma amostra do rung
   rígido do mesmo tamanho que o rung Boltz-2.

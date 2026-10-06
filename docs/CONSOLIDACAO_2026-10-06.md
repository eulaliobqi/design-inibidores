# Consolidação em 06/10/2026 (tarde): retomada, MDs parciais de pH 8,2, correções da fila de energia

## 1. Retomada
- O fechamento do terminal derrubou a VPN da UFV, não o servidor. Reconexão com `openvpn-gui.exe --connect vpn-UFV-config.ovpn`. Os screens (`md82-L/M`, `md82rest-L/M`, `energy-queue`, `noise-L/M`) sobreviveram.
- Ritmo real das MDs de pH 8,2: 1,3–2,7 h cada (média ≈ 2,1 h); a estimativa de 70 min estava errada. 16/48 concluídas às 17:00. Previsão (extrapolação): 48 MDs entre a noite de 07/10 e a manhã de 08/10; `noise-L/M` ≈ 09/10. Recheque `nvidia-smi` (GPU compartilhada com o `gore`).
- Manuscrito EN: rótulos RESISTENTE/MARGINAL/SUSCEPTIVEL → *resistant-like/marginal/susceptible* (aee0ede); citações (77), referências cruzadas e a frase da 3.8 conferidas contra os dados. PT conferido contra o EN (números iguais); painel do docx atualizado (349c15b).

## 2. Defeitos achados e corrigidos na fila de energia
| # | defeito | efeito | correção |
|---|---|---|---|
| 1 | `md_pbc_sub.xtc` só era criado na análise, rodada depois do MM-GBSA em `queue_energy.sh` | `mmgbsa_md82` = `sem_trajetoria` para todas, também na passada final | `process()` cria o arquivo com `pbc_traj` |
| 2 | cache `result.json` com ΔG nulo (teste de 05/10) + `main` tratava `real` como pronto | NGGRPDAP pH 10 sem ΔG | cache só vale com ΔG; `.dat` existente não é refeito; real = −45,34 (SD 4,14) |
| 3 | `prodigy_scores._frame_to_complex` sem `CYS2`, `OT1`, `OT2` | PRODIGY nas trajetórias = `None` em todas as MDs | mapa ampliado; `--backfill-prodigy` preencheu 48 (pH 10) + 16 (pH 8,2) |

Salvaguarda: o preenchimento relê o JSON antes de gravar e reaproveita o `result.json`; mesmo assim a fila sobrescreveu 5 entradas L durante o preenchimento, reparadas em seguida. Novas entradas já saem completas.

## 3. Resultados (16 MDs de pH 8,2 prontas × as mesmas de pH 10; n = 16, uma execução por pH, finalistas, não amostra aleatória)
| métrica | mediana pH 8,2 | mediana pH 10 | Wilcoxon P | ρ entre pH (P) |
|---|---|---|---|---|
| distância final âncora–Asp189 (Å) | 6,51 | 5,83 | 0,60 | +0,37 (0,16) |
| ocupância 2ª metade (5 Å) | 0,01 | 0,04 | 0,53 | +0,30 (0,25) |
| RMSD final do peptídeo (nm) | 0,31 | 0,31 | 0,40 | +0,17 (0,52) |
| MM-GBSA ΔG (kcal/mol) | −25,2 | −26,5 | 0,60 | **+0,73 (0,001)** |
| PRODIGY nos quadros ΔG (kcal/mol) | −8,48 | −8,58 | 0,46 | **+0,64 (0,007)** |

- **Ocupância ≥ 0,70:** 1 de 16 em pH 8,2 (NGGRPDAP) e 3 de 16 em pH 10 (NGGRPDAP, GQNDS L, GGHSE).
- **NGGRPDAP (L, *A. gemmatalis*) é o único que se repete:** ocupância 0,98 (pH 8,2) e 1,00 (pH 10), distância final 2,84 e 2,74 Å, MM-GBSA −53,3 e −45,3 kcal/mol, PRODIGY −10,1 e −9,5; primeiro do MM-GBSA nos dois pH. Mecanismo canônico (Arg seguida de Pro em S1). Um único par: não é evidência de seletividade nem de atividade.
- **GQNDS (L) e GGHSE (M) não se repetem:** GQNDS L ficou em S1 só na 1ª metade (0,97 → 0,04; MM-GBSA −2,0 contra −18,2), GGHSE saiu (final 8,61 Å, ocupância 0,00; |ω|min 149,5°, a 0,5° do limite do anel). GTDTG (0,68) e IYPETG (0,57) fizeram o inverso. Ambos foram incluídos nos finalistas **por ocupância alta em pH 10** (regressão à média esperada).
- **Escores de energia concordam entre pH (ρ 0,64–0,73) e a ocupância e as distâncias não (ρ 0,2–0,4):** o que o MM-GBSA/PRODIGY medem (tamanho e carga da interface) é estável entre condições; a posição do peptídeo em 10 ns é largamente estocástica. Coerente com a calibração (MM-GBSA e PRODIGY não separam inibidor de isca; ρ com o tamanho da interface −0,93 e −0,79).
- **MM-GBSA das 48 trajetórias de pH 10:** mediana −24,8 (−65,0 a −4,1); com K/R (3 peptídeos) mediana −45,3 contra −23,2 (Mann-Whitney P = 0,014); ρ com a distância final +0,37 (P = 0,01). PRODIGY nos quadros (48): mediana −8,2 (−11,4 a −6,5); ρ com o comprimento −0,37 e com o MM-GBSA +0,61.

## 4. O que isso muda no manuscrito (a escrever quando as 48 + `noise` terminarem; nada disso entrou ainda)
1. 3.5/3.7: a conclusão "a ocupância acompanha a pose inicial e não discrimina" sai reforçada; o que se reproduz entre pH são os escores de energia, não a posição.
2. 3.8: "GGHSE é o único com ocupância e anel estrito" vale só para pH 10; GGHSE e GQNDS exigem ressalva; NGGRPDAP passa a ser o candidato com respaldo nos dois pH.
3. Piso de ruído (`noise-L/M`) é necessário antes de atribuir qualquer diferença ao pH; sem ele, tudo acima é compatível com ruído de execução.
4. Descrever o PRODIGY nos quadros (30 por trajetória) e o MM-GBSA na 2.8 já com os dois defeitos corrigidos; dados parciais em `data-e2-results/*_parcial_2026-10-06.json`, MM-GBSA/PRODIGY de pH 10 final em `data-e2-results/mmgbsa_md10_{L,M}.json`.

## 5. Pendências
- Esperar as 32 MDs restantes de pH 8,2 e as 16 do `noise`; a fila de energia roda MM-GBSA/PRODIGY conforme terminam e, ao fim, a análise e o ranking (`outputs/ranking_energy_final_all.*`, marcador `QUEUE_ENERGY_DONE`); depois `scripts/compare_ph.py` à mão.
- Motivo do pH 8,2 (a cargo do usuário), lista final de peptídeos, MD longa dos entregues (decidir se NGGRPDAP entra como prioridade), 3.6–3.7, Fig. 8, resumo/4.1/4.4/5 (EN e PT), revisão linha a linha do PT.

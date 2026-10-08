# Consolidação em 07/10/2026 (tarde): 37 de 48 MDs de pH 8,2 integradas

## 1. Retomada
- A VPN estava presa em `SIGHUP[soft,tun-abort]` desde 23:15 de 06/10 (precisa de administrador); o usuário reconectou pelo ícone. O servidor e os screens não caíram (`md82rest-L/M`, `energy-queue`, `noise-L/M`).
- Ritmo medido em 07/10 pelas datas dos `md.gro`: 1,6–3,4 h por MD (média ≈ 2,1–2,6 h). Às 12:52: **37 de 48 concluídas (L 17, M 20)**; em curso `Cincludens__r1` (L, 78%) e `Pxylostella__r1` (M, 18%). Previsão: frente M ≈ 20–22 h de 07/10; frente L ≈ 01–05 h de 08/10 (mais provável 01–03 h, a L acelera quando a M termina); `noise-L/M` depois (≈ 09/10).
- A `energy-queue` ainda aguarda (`mmgbsa_md82_{L,M}.json` já têm 17 e 20 entradas, todas `real`, todas com `PRODIGY_md`). A análise parcial foi rodada à mão: `analyze_md_top_candidates --md-dir outputs/md82_{L,M}` e `compare_ph` (saídas `outputs/analyze_md82_*_0710.log`, `outputs/compare_ph_0710.log`). A fila refaz a análise ao fim.

## 2. Resultados com 37 pares (17 L + 20 M; uma execução por pH; finalistas, não amostra aleatória)
| métrica | mediana pH 8,2 | mediana pH 10,0 | Wilcoxon P | ρ entre pH (P) |
|---|---|---|---|---|
| distância final âncora–Asp189 (Å) | 6,47 | 6,26 | 0,48 | 0,62 (<0,001) |
| ocupância 2ª metade (5 Å) | 0,02 | 0,01 | 0,93 | 0,46 (0,004) |
| RMSD final do peptídeo (nm) | 0,43 | 0,35 | 0,28 | 0,37 (0,026) |
| MM-GBSA ΔG (kcal/mol) | −25,9 | −27,0 | 0,16 | 0,58 (<0,001) |
| PRODIGY nos quadros (kcal/mol) | −8,43 | −8,39 | 0,86 | 0,67 (<0,001) |

- **Ocupância ≥ 0,70:** 4 em pH 8,2 (NGGRPDAP, GGKPGEP, PISQIDSGSR, GENGGPG) e 4 em pH 10,0 (NGGRPDAP, GGKPGEP, GQNDS L, GGHSE). Nos dois: só NGGRPDAP e GGKPGEP; só pH 8,2: 2; só pH 10,0: 2; nenhum: 31. |Δocupância| > 0,5 em 5 pares, nos dois sentidos → posição em 10 ns largamente estocástica.
- **Novo: PISQIDSGSR (M, *C. includens*, macrociclo, âncora Arg):** ocupância 1,00 e 2,80 Å em pH 8,2; 0,33 e 5,21 Å em pH 10,0; MM-GBSA −42,5 / −65,0 (o mais favorável de pH 10,0 nas 48). Não repete, logo não entra como quinto candidato; vale como mais um exemplo de Arg que chega a S1 quando posicionada.
- **GENGGPG (M, *S. frugiperda*)**: 0,85 (pH 8,2) × 0,41 (pH 10,0), partiu a 4,57 Å (única das 4 de pH 8,2 que não partiu a < 4,0 Å).
- **Pose inicial:** das 4 com ocupância ≥ 0,70 em pH 8,2, 3 partiram a < 4,0 Å (3 de 6 que partiram assim; 1 de 31 que partiram mais longe).
- **K/R:** em pH 8,2 os 3 com âncora K/R têm MM-GBSA mediana −42,5 contra −25,0 (Mann-Whitney P = 0,038); em pH 10,0 −45,3 contra −26,6.
- **NGGRPDAP** é o 1º do MM-GBSA em pH 8,2 (−53,3) e o 5º em pH 10,0 (−45,3); a frase "o mais favorável nos dois pH" (n = 17) foi corrigida.
- GQNDS (L) e GGHSE (M) seguem sem repetir; GTDTG 0,68 e IYPETG 0,57 em pH 8,2.
- Conclusão que se mantém e se reforça: o que se reproduz entre pH são os escores de energia (ρ 0,58–0,67) e, em menor grau, a distância; a ocupância é guiada pela pose inicial. Sem `noise-L/M` nada disso é atribuível ao pH.

## 3. Arquivos atualizados
- `data-e2-results/{md82_{L,M}_analysis,mmgbsa_md82_{L,M}}_parcial_2026-10-07.json`, `compare_ph.{json,csv,md}` (n = 37).
- `manuscript/figures/make_figures_ph.py` (lê os parciais de 07/10; P < 0,001 em vez de "P = 0,000") → Figura 7 (n = 37) e S10 regeneradas em `manuscript/figures/final/`.
- Manuscrito EN (`manuscript_src.md`) e PT (`pt_parts/p2.md`, `p3.md`, `p5.md`): 3.7 reescrito com 37 pares (continua PROVISIONAL), frase da 3.8, legenda da Fig. 7, nota do 2.6; docx e `manuscript.md` reconstruídos. `scripts/audit_numbers.py`: 187 verificações, 0 falhas (os números novos de 3.7 vêm do script de análise de 07/10, ainda fora do auditor).

## 4. Consulta ao RAG (`eulalio-pos-doc`, `rag_toolkit.py retrieve`, coleção `tema1`)
- Achado útil para o **motivo do pH 8,2 (PENDING, decisão do usuário):** Schultz et al. 2026 (`schultz2026synthetic.pdf`, p. 4): ensaios cinéticos com DL-BApNA em Tris-HCl 0,1 M, CaCl2 20 mM, **pH 8,2**. Colocado no manuscrito como possibilidade a confirmar, dentro do marcador PENDING.
- Paulo et al. 2026 (pentapeptídeos de RCL contra *A. gemmatalis*) e Jongsma 1995 já estão citados; nada novo foi afirmado a partir deles. As buscas por pH do intestino médio devolveram só trechos sobre PnBBI e *H. armigera* (Lokya 2020), não usados.

## 5. Pendências
Mesmas de `docs/RETOMADA_2026-10-07.md`: esperar as 11 MDs restantes, a `energy-queue` (`QUEUE_ENERGY_DONE`) e o `noise`; então 3.6/3.7 definitivos, resumo, 4.1, 4.2, 4.4, 5, Tabela 4, Fig. 6, lista final de peptídeos e decisões do usuário (motivo do pH, MD longa, cortes, autoria).

## 6. Adendo (07/10, 17:58): estado do servidor ao fim da tarde
- **41 de 48 MDs de pH 8,2 prontas (L 19, M 22)**; em curso `Cincludens__r3` (L, 81%) e `Agemmatalis__r1` (M, recém-iniciada). Ritmo medido de 12:52 a 17:58: 4 MDs em 5,1 h, ≈ 2,5 h por MD por frente (mais lento que os 2,1 h assumidos). GPU 88%, 60 °C.
- **Previsão (estimativa):** frente M ≈ 22–23 h de 07/10; frente L ≈ 03–05 h de 08/10; `energy-queue` dispara só depois da última MD (manhã de 08/10; log ainda "aguardando"); `noise-L/M` sem saída ainda (nenhum `md82b_*`/`md10b_*`), começa depois, ≈ 09/10 ou mais tarde.
- **Decisão do usuário:** não reintegrar a análise parcial agora; esperar as 48. A integração vigente no manuscrito, nos dados e nas figuras continua sendo a de 37 pares (`_parcial_2026-10-07`).
- **Ao retomar:** seguir `docs/RETOMADA_2026-10-07.md` (seções 1, 2 e 4). Conferir `ls outputs | grep DONE` (`MD82ALL_L_DONE`, `MD82ALL_M_DONE`, `QUEUE_ENERGY_DONE`); se a fila de energia não tiver rodado, `outputs/mmgbsa_md82_{L,M}.json` devem ter 24 entradas `real` com `PRODIGY_md` cada.

## 7. Adendo (07/10, 22:43): estado do servidor à noite e o que esperar de manhã
- **44 de 48 MDs de pH 8,2 prontas (L 21, M 23)**, medidas pela presença de `md.gro`. Em curso: `Pxylostella__r1` (L, passo 4,10 M de 5 M, ≈ 82%) e `Agemmatalis__r3` (M, passo 4,51 M, ≈ 90% pelo checkpoint de 22:32; última da frente M). Ainda não iniciadas, ambas da frente L: `Agemmatalis__r1` e `Pxylostella__r3`.
- **Fila de energia:** `mmgbsa_md82_L.json` com 21 e `_M.json` com 23 entradas, todas `status: "real"`, 126 quadros, campo `dG_gb_kcal`. O `queue_energy.log` continua em "aguardando" (46 de 48 *iniciadas*); a passada final só ocorre depois de `MD82ALL_L_DONE` e `MD82ALL_M_DONE`.
- **Previsão (estimativa, não medida):** `MD82ALL_M_DONE` por volta das 23 h de 07/10 (a conferir); as duas últimas da L por volta de 04 h de 08/10, mais lentas porque dividirão a GPU com o `noise-M`; `QUEUE_ENERGY_DONE` ≈ 05–06 h de 08/10; piso de ruído (`noise-L/M`, 16 MDs) ≈ madrugada de 09/10. Nenhum marcador `*_DONE` existia às 22:43.
- **Decisão do usuário (mantida):** não reintegrar parcial; a integração vigente no manuscrito, dados e figuras segue a de 37 pares (`_parcial_2026-10-07`). Nada foi alterado no servidor nem nos números do manuscrito nesta rodada.
- **Ao voltar (08/10):** `ssh eulalio@200.235.143.10 'ls ~/design-inibidores/outputs | grep DONE'` → esperado `MD82ALL_L_DONE`, `MD82ALL_M_DONE`, `QUEUE_ENERGY_DONE`; `NOISE_{L,M}_DONE` só depois. Se os três primeiros existirem, seguir `docs/RETOMADA_2026-10-07.md` §2.1, 2.2, 2.4 (48 pares); 3.6/3.7 definitivos e o resto do texto só após o piso de ruído (§2.3, 2.5).

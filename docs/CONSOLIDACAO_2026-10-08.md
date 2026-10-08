# Consolidação de 08/10/2026: 48 de 48 MDs de pH 8,2 integradas

## 1. Estado do servidor (08/10, ≈ 15:00)
- `md82_L` e `md82_M`: 24 MDs cada (48/48). `energy-queue` terminou (`QUEUE_ENERGY_DONE`, 03:40). `mmgbsa_md82_{L,M}.json`: 24/24 entradas `real`, todas com `PRODIGY_md`. `ranking_energy_final_all.{json,csv}` regenerado às 03:40.
- Piso de ruído (`noise-L`, 16 MDs de segunda semente): `md82b_L/M` e `md10b_M` com 4 pastas; `md10b_L` na 4ª MD (10 ns de produção em curso às 14:55). Falta só esta; depois rodar `analyze` nas pastas `*b_*` e refazer `compare_ph` (ele grava `noise_floor_same_pH_other_seed`).

## 2. Resultado (compare_ph, 48 pares; `data-e2-results/compare_ph.*`)
| métrica | mediana pH 8,2 vs 10,0 | Wilcoxon P | ρ entre pH |
|---|---|---|---|
| distância final âncora–Asp189 (Å) | 6,40 vs 6,62 | 0,16 | 0,51 |
| ocupância S1 5 Å, 2ª metade | 0,01 vs 0,00 | 0,88 | 0,44 |
| RMSD local final (nm) | 0,43 vs 0,40 | 0,63 | 0,33 |
| MM-GBSA ΔG (kcal/mol) | −26,7 vs −24,8 | 0,80 | 0,50 |
| PRODIGY nos quadros (kcal/mol) | −8,38 vs −8,21 | 0,18 | 0,60 |

- Ocupância ≥ 0,70: seis em pH 8,2 (NGGRPDAP, GGKPGEP, PISQIDSGSR, GENGGPG, GGHGGG, GGSDHT) e cinco em pH 10,0 (NGGRPDAP, GGKPGEP, GQNDS linear, GGHSE, GGGGH); nos dois: só NGGRPDAP e GGKPGEP; 4 só em 8,2, 3 só em 10,0, 39 em nenhum. Diferença > 0,5 em nove pares, nos dois sentidos. Mesma âncora em 46/48.
- Pose inicial decide de novo: 5 das 9 MDs de pH 8,2 que partiram a ≤ 4,0 Å atingiram ocupância ≥ 0,70 contra 1 das 39 que partiram mais longe (GENGGPG, 4,57 Å); Fisher P = 4×10⁻⁴; ρ(distância inicial, ocupância) = −0,60.
- MM-GBSA com âncora K/R (NGGRPDAP, GGKPGEP, PISQIDSGSR): −42,5 vs −25,9 nos outros 45 (Mann–Whitney P = 0,041).
- Ranking com seis etapas (33 candidatos): linear NGGRPDAP 6,7, GSNIN 7,0, PTTTQT 7,4, SGPIG 7,8, TDETG 8,2; cíclico SGSTDIE 3,2, GQNDS 4,1, IYPETG 4,5, GGHSE 4,9, GGSTDID 5,2. GGKPGEP não entra (não passou nos portões).
- Leitura: sem diferença atribuível ao pH em nenhum teste pareado; só NGGRPDAP e GGKPGEP mantêm S1 nos dois pH. Sem o piso de ruído, nada disso é atribuível ao pH.

## 3. O que mudou nos arquivos
- `data-e2-results/`: finais `mmgbsa_md82_{L,M}.json`, `md82_{L,M}_analysis.json`, `md82_{L,M}_summary.json`, `ranking_energy_final_all.*`, `compare_ph.*`. Os `*_parcial_2026-10-0{6,7}.json` seguem na pasta (não apagados; nada os usa).
- Figuras: Fig. 6 agora com seis etapas (gerador lê `data-e2-results/ranking_energy_final_all.json`; rótulos encurtados), Fig. 7 e S10 regeneradas com n = 48, sem "provisional".
- Manuscrito EN e PT: 3.6 (pH 8,2 e ranking), 3.7 (reescrita com 48), 3.8, Tabela 4, legendas 6 e 7, 2.8, resumo, 4.1, 4.4(vi), 5, notas. `audit_numbers.py`: 187 verificações, 0 falhas. Resumo EN 348 palavras.
- Pendências no texto: PENDING do motivo do pH 8,2 (2.6) e do piso de ruído (3.7); autores/CRediT/financiamento/CoI/IA/DOI.
- O `Manuscrito_PT_leitura.docx` estava aberto no Word: a versão nova foi gravada como `Manuscrito_PT_leitura_novo.docx`.

## 4. Próximos passos
1. Quando `noise-L` terminar: analisar `md82b_*`/`md10b_*`, `python -m scripts.compare_ph` no servidor, copiar `compare_ph.*`, completar o PENDING de 3.7 e o 4.4(vi) (EN e PT), reconstruir e auditar.
2. Decisões do usuário: motivo do pH 8,2 (candidato: tampão Tris pH 8,2 dos ensaios de Schultz 2026), prioridade para MD longa (NGGRPDAP e GGKPGEP), lista final e cortes.

# B0.5 — MM-PBSA (GB, trajetória única): 22/22 sistemas, resultado negativo real

**Data:** 2026-09-18 | Continuação de `b05_md_curta_completo.md`. Campanha `scripts/mmpbsa_calib.py`
(`screen mmpbsa-calib`) terminou os 22 sistemas sem falhas (`MMPBSA_CALIB_ALL_DONE`,
22/22 `status: real`). GB (`igb=5`, `saltcon=0.150`), 45 frames do último terço já equilibrado
(frames 268–400 de 401, `interval=3`) — protocolo recalibrado para a trajetória real de 2 ns
(ver bugs corrigidos abaixo).

## 3 bugs reais corrigidos antes deste resultado (registrar para qualquer reuso futuro)

1. **Grupos de índice**: `splitch 1` (usado no script antigo `deep_test_mmpbsa.py`) não produz
   2 grupos por cadeia aqui — produz até 10 fragmentos (`Protein_chain1..10`), porque o `gmx`
   detecta quebras de conectividade (gaps de loop) dentro da mesma cadeia PDB como "chains"
   separadas. Fix: grupos custom por intervalo de átomos (`a 1-N_A`, `a N_A+1-N_A+N_lig`), usando
   a contagem real do `[atoms]` de cada `topol_Protein_chain_X.itp` — ficam sempre nas 2 últimas
   posições do `.ndx`.
2. **ApTI tem 3 cadeias reais** (`Protein_chain_A/B/C`, não A/B) — é um inibidor bifuncional de
   2 domínios. Usar só a cadeia B como "ligante" deixa a C fora do índice → erro real do
   gmx_MMPBSA `"complex index has fewer atoms than the topology"`. Fix: ligante = soma de todas
   as cadeias após a A (receptor, sempre a 1ª no `[molecules]`).
3. **`mmpbsa.in` herdado tinha `startframe=1000, endframe=2000`**, calibrado para trajetórias de
   10 ns/2001 frames — esta campanha é de 2 ns/401 frames → `TrajError: start frame (1000) >
   total frames (401)` em 100% dos sistemas na 1ª tentativa. Fix: `startframe=268, endframe=400,
   interval=3`.

## Resultado real — ΔG_TOTAL (kcal/mol, GB, sander), mais negativo = ligação mais forte

| Sistema | ΔG_TOTAL | SEM |
|---|---|---|
| bovine\_\_SFTI1 | −70,24 | 0,95 |
| bovine\_\_SFTI1_decoy | −64,76 | 0,74 |
| bovine\_\_ApTI | −69,29 | 1,07 |
| bovine\_\_BBI | −66,11 | 0,69 |
| bovine\_\_BBI_decoy | −68,47 | 1,08 |
| bovine\_\_BPTI | −68,80 | 0,87 |
| bovine\_\_BPTI_decoy | −52,49 | 1,19 |
| bovine\_\_EcTI | −72,66 | 0,73 |
| bovine\_\_EcTI_decoy | −78,97 | 0,88 |
| bovine\_\_SKTI | −77,36 | 0,90 |
| bovine\_\_SKTI_decoy | **−103,00** | 1,01 |
| sfrug\_\_ApTI | −92,56 | 0,86 |
| sfrug\_\_BBI | −88,64 | 0,84 |
| sfrug\_\_BBI_decoy | **−151,20** | 1,18 |
| sfrug\_\_BPTI | −112,71 | 1,00 |
| sfrug\_\_BPTI_decoy | −131,58 | 1,14 |
| sfrug\_\_EcTI | −78,89 | 1,10 |
| sfrug\_\_EcTI_decoy | **−223,69** | 1,56 |
| sfrug\_\_SFTI1 | −86,05 | 0,96 |
| sfrug\_\_SFTI1_decoy | −83,95 | 0,78 |
| sfrug\_\_SKTI | −129,20 | 1,19 |
| sfrug\_\_SKTI_decoy | −128,62 | 1,51 |

## Achado real — MM-PBSA (GB, trajetória única, 2ns) é PIOR que acaso como discriminador: 4/10

| Receptor | Inibidor | ΔG real | ΔG decoy | Diferença | Veredito |
|---|---|---|---|---|---|
| bovine | SFTI1 | −70,24 | −64,76 | −5,5 (real mais forte) | OK |
| bovine | BBI | −66,11 | −68,47 | +2,4 (decoy mais forte) | **ERRADO** |
| bovine | BPTI | −68,80 | −52,49 | −16,3 (real mais forte) | OK |
| bovine | EcTI | −72,66 | −78,97 | +6,3 (decoy mais forte) | **ERRADO** |
| bovine | SKTI | −77,36 | −103,00 | +25,6 (decoy MUITO mais forte) | **ERRADO** |
| sfrug | SFTI1 | −86,05 | −83,95 | −2,1 (real mais forte, margem pequena) | OK |
| sfrug | BBI | −88,64 | −151,20 | +62,6 (decoy MUITO mais forte) | **ERRADO** |
| sfrug | BPTI | −112,71 | −131,58 | +18,9 (decoy mais forte) | **ERRADO** |
| sfrug | EcTI | −78,89 | −223,69 | +144,8 (decoy ABSURDAMENTE mais forte) | **ERRADO** |
| sfrug | SKTI | −129,20 | −128,62 | −0,6 (empate técnico) | OK |

**Total: 4/10 corretos, 6/10 errados — pior que os 5/10 (~acaso) do RMSD e muito pior que os
10/10 do Boltz-2.** Não é ruído pequeno: em 3 pares o decoy "vence" por dezenas a mais de cem
kcal/mol (`sfrug__EcTI_decoy`: +144,8 kcal/mol mais favorável que o real; `sfrug__BBI_decoy`:
+62,6; `bovine__SKTI_decoy`: +25,6).

**Não estou escondendo isso nem forçando leitura otimista — é o achado central desta etapa.**
Com a escada completa (Boltz-2 → HADDOCK3 → RMSD → MM-PBSA), **só o Boltz-2 (confidence_score/
pLDDT) separou real de decoy de forma confiável (10/10)** nesta calibração. Os dois métodos de
MD (RMSD do complexo inteiro e MM-PBSA de trajetória única/GB) **não devem ser usados como
critério de go/no-go** no estado atual do pipeline.

### Hipóteses não confirmadas sobre a causa (não apresentar como fato)

Cruzando com Rg/RMSD já registrados em `b05_md_curta_completo.md`: os 3 piores casos (EcTI/BBI
decoy em *S. frugiperda*, SKTI decoy bovina) não têm um padrão geométrico único e óbvio —
`sfrug__EcTI_decoy` tem Rg menor que o real (3,02 vs 4,24 nm, sugerindo colapso não-específico
do complexo) mas `sfrug__BBI_decoy` tem Rg MAIOR (2,60 vs 2,04). Não verifiquei decomposição
por resíduo nem conferi se a MM-PBSA de trajetória única (sem termo de entropia, sem
reamostragem bound/unbound separada) está simplesmente correlacionando com área de contato
total em vez de especificidade real — isso é uma limitação conhecida na literatura do método
para interfaces proteína-proteína (ao contrário do uso usual do MM-PBSA para molécula pequena,
onde costuma ser mais confiável), mas não testei essa hipótese diretamente aqui.

## Estado consolidado de B0.5 (toda a escada de calibração)

| Rung | Separa real de decoy? |
|---|---|
| Boltz-2 (confidence_score/pLDDT) | **10/10 — confiável** |
| HADDOCK3 (score, sem decoys pareados neste rung) | não testado com decoy |
| RMSD (MD 2ns, complexo inteiro) | 5/10 — ~acaso, não confiável |
| MM-PBSA (GB, trajetória única, 2ns) | 4/10 — pior que acaso, não confiável |

**Recomendação para o usuário decidir**: a calibração real não dá suporte a usar RMSD ou
MM-PBSA (nesta implementação) como critério de corte em B2/B3 — só o Boltz-2 está validado.
Opções a considerar (não decidido aqui): (a) seguir só com Boltz-2 como discriminador na
próxima fase, (b) investir em corrigir a metodologia de MD/MM-PBSA (trajetória mais longa,
correção de entropia, MM-PBSA com decomposição por resíduo) antes de confiar nela, ou (c)
aceitar RMSD/MM-PBSA só como filtro de QC (a simulação não colapsou?), não como score.

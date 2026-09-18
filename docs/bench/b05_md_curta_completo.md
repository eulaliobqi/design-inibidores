# B0.5 — MD curta (2 ns): campanha completa (22/22 sistemas)

**Data:** 2026-09-18 | Continuação de `b05_md_curta_parcial.md` (corte anterior em 12/22). A
campanha (`screen b05-md-full`, disparada via `scripts/run_calib_md.py ALL 2.0`) terminou os
22 sistemas restantes sem falhas (`MD_ALL_DONE`, `md_calib_results.json` com 22/22 entradas
`status: OK`). GPU ociosa ao final (0% util, 8 MiB usados) — confirma que não ficou nada preso.

## Resultado completo — 22 sistemas (2 receptores × 6 inibidores × real/decoy, ApTI sem decoy)

| Sistema | RMSD médio (nm) | RMSD std | H-bonds médio | Rg médio (nm) |
|---|---|---|---|---|
| bovine\_\_SFTI1 | 0,744 | 0,813 | 172,6 | 1,653 |
| bovine\_\_SFTI1_decoy | 0,306 | 0,532 | 155,6 | 1,642 |
| bovine\_\_ApTI | 0,148 | 0,029 | 270,3 | 2,216 |
| bovine\_\_BBI | 0,179 | 0,142 | 190,0 | 1,978 |
| bovine\_\_BBI_decoy | **1,862** | 0,442 | 188,4 | 2,744 |
| bovine\_\_BPTI | 0,229 | 0,080 | 189,0 | 2,624 |
| bovine\_\_BPTI_decoy | 0,221 | 0,040 | 182,2 | 1,824 |
| bovine\_\_EcTI | 0,103 | 0,014 | 270,9 | 2,208 |
| bovine\_\_EcTI_decoy | 0,212 | 0,050 | 268,3 | 2,226 |
| bovine\_\_SKTI | 0,115 | 0,015 | 271,0 | 2,220 |
| bovine\_\_SKTI_decoy | 0,168 | 0,022 | 270,5 | 2,100 |
| sfrug\_\_ApTI | 0,460 | 0,802 | 311,3 | 2,266 |
| sfrug\_\_BBI | 0,283 | 0,574 | 228,4 | 2,044 |
| sfrug\_\_BBI_decoy | 0,523 | 0,553 | 237,5 | 2,601 |
| sfrug\_\_BPTI | 0,212 | 0,213 | 225,7 | 1,952 |
| sfrug\_\_BPTI_decoy | 0,207 | 0,327 | 227,3 | 1,889 |
| sfrug\_\_EcTI | 0,467 | 0,202 | 308,4 | 4,242 |
| sfrug\_\_EcTI_decoy | **1,652** | 1,688 | 300,2 | 3,022 |
| sfrug\_\_SFTI1 | 0,505 | 0,702 | 199,4 | 1,770 |
| sfrug\_\_SFTI1_decoy | 0,165 | 0,026 | 202,3 | 1,749 |
| sfrug\_\_SKTI | **4,449** | 2,434 | 314,8 | 4,244 |
| sfrug\_\_SKTI_decoy | 0,216 | 0,032 | 298,6 | 2,212 |

## Achado real — RMSD do complexo inteiro NÃO discrimina real de decoy (5/10 pares corretos, ~acaso)

Com a campanha completa (10 pares real/decoy, ApTI sem decoy nos dois receptores), o sinal
piorou em relação ao corte parcial (que tinha 3/5 certo, 1/5 empate, 1/5 errado, só do lado
bovino):

| Receptor | Inibidor | RMSD real | RMSD decoy | Veredito |
|---|---|---|---|---|
| bovine | SFTI1 | 0,744 | 0,306 | **ERRADO** (real 2,4× menos "estável") |
| bovine | BBI | 0,179 | 1,862 | OK |
| bovine | BPTI | 0,229 | 0,221 | **ERRADO** (empate técnico) |
| bovine | EcTI | 0,103 | 0,212 | OK |
| bovine | SKTI | 0,115 | 0,168 | OK |
| sfrug | SFTI1 | 0,505 | 0,165 | **ERRADO** |
| sfrug | BBI | 0,283 | 0,523 | OK |
| sfrug | BPTI | 0,212 | 0,207 | **ERRADO** (empate técnico) |
| sfrug | EcTI | 0,467 | 1,652 | OK |
| sfrug | SKTI | 4,449 | 0,216 | **ERRADO** (o pior caso: real 20× mais instável) |

**Total: 5/10 corretos, 5/10 errados — equivalente a chance (50%).** O lado *S. frugiperda*
piorou especificamente por `sfrug__SKTI` (RMSD real = 4,449 nm ± 2,434, um outlier grave — o
complexo real "derreteu" em 2ns enquanto o decoy ficou estável em 0,216 nm). Isso **confirma a
hipótese já registrada no corte parcial**: RMSD do complexo inteiro (backbone ajustado como
bloco único, sem separar cadeia receptor/ligante — limite herdado do `MDAgent._analyze_trajectory`
do V1) não isola a interface e é dominado por deriva/rotação do receptor grande, não é um
discriminador confiável real-vs-decoy sozinho. H-bonds e Rg (mesmo problema de grupo "Protein"
inteiro) também não mostram separação sistemática visível a olho nos dados acima.

**Conclusão prática**: RMSD de 2ns aqui serve só como QC de "a simulação não explodiu/ficou
fisicamente razoável", não como critério de calibração go/no-go. O degrau decisivo continua
sendo MM-PBSA (energia de ligação real), consistente com o que já estava registrado.

## MM-PBSA — rodando em background no servidor

Disparado `scripts/mmpbsa_calib.py` (novo, adaptado de `scripts/deep_test_mmpbsa.py` — mesmos
fixes conhecidos: `trjconv -pbc mol -center` antes do MMPBSA, env `mmgbsa-env` + PATH com
`gmx_mpi` de `md-gromacs`, pipe de shell em vez de `subprocess input=`) em
`screen -S mmpbsa-calib` para os 22 sistemas. **Diferença do script antigo**: os grupos de
índice receptor/ligante (`-cg`) são resolvidos dinamicamente pelo nome no `.ndx`
(`Protein_chain_A`/`Protein_chain_B`), não fixos em `17 18` — a contagem de grupos padrão do
`gmx` varia por sistema (íons diferentes por pH/propka entre bovina pH 8,0 e *S. frugiperda*
pH 10,0). `startframe=1000, endframe=2000, interval=20` (GB, `igb=5`, `saltcon=0.150`, mesmo
protocolo já validado). Resultados progressivos em
`data-calibration-b05/md_calib/mmpbsa_calib_results.json`; log em
`data-calibration-b05/mmpbsa_calib.log`.

## Pendências reais

1. MM-PBSA ainda rodando (22 sistemas, ETA não medido ainda — checar progresso).
2. Go/no-go real de B0.5 só deve ser declarado com MM-PBSA, não com este RMSD.
3. Se formos usar RMSD como sinal de calibração no futuro, precisa recalcular com ajuste pelo
   backbone do receptor isolado + RMSD do ligante nesse referencial (não feito aqui).

# pH 8,2 x pH 10,0 (37 candidatos pareados)

| metrica | n | mediana(8,2 - 10) | media | dp | Wilcoxon p | rho Spearman entre pH |
|---|---|---|---|---|---|---|
| distancia final ancora-Asp189 (A) | 37 | 0.000 | -0.532 | 3.658 | 0.484 | 0.62 |
| ocupancia de S1 a 5 A, 2a metade | 37 | 0.000 | -0.013 | 0.327 | 0.929 | 0.46 |
| RMSD local final do peptideo (nm) | 37 | 0.039 | 0.006 | 0.315 | 0.284 | 0.37 |
| fracao de quadros com contato com o receptor | 37 | 0.000 | 0.001 | 0.006 |  | -0.04 |
| fracao com contato com a Ser catalitica | 37 | -0.002 | -0.014 | 0.279 | 0.52 | 0.31 |
| fracao com contato com a His catalitica | 37 | -0.010 | -0.050 | 0.315 | 0.306 | 0.47 |
| MM-GBSA dG (kcal/mol) | 37 | 1.670 | 2.983 | 11.707 | 0.158 | 0.58 |
| PRODIGY dG nos quadros (kcal/mol) | 37 | -0.113 | 0.041 | 0.848 | 0.858 | 0.67 |

{
 "n_pairs": 37,
 "agreement": {
  "occupancy_ge_0.70": {
   "both": 2,
   "only_pH10": 2,
   "only_pH82": 2,
   "neither": 31
  },
  "same_anchor_residue": 36
 },
 "protonation_states_differing_per_system": {
  "median": 1,
  "min": 0,
  "max": 3
 }
}
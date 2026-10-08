# pH 8,2 x pH 10,0 (48 candidatos pareados)

| metrica | n | mediana(8,2 - 10) | media | dp | Wilcoxon p | rho Spearman entre pH |
|---|---|---|---|---|---|---|
| distancia final ancora-Asp189 (A) | 48 | -0.145 | -1.052 | 4.273 | 0.158 | 0.51 |
| ocupancia de S1 a 5 A, 2a metade | 48 | 0.000 | 0.010 | 0.374 | 0.875 | 0.44 |
| RMSD local final do peptideo (nm) | 48 | 0.021 | -0.055 | 0.339 | 0.626 | 0.33 |
| fracao de quadros com contato com o receptor | 48 | 0.000 | 0.002 | 0.008 |  | 0.35 |
| fracao com contato com a Ser catalitica | 48 | -0.001 | 0.032 | 0.316 | 0.758 | 0.27 |
| fracao com contato com a His catalitica | 48 | 0.000 | 0.010 | 0.349 | 0.827 | 0.44 |
| MM-GBSA dG (kcal/mol) | 48 | 0.150 | 0.766 | 12.016 | 0.796 | 0.50 |
| PRODIGY dG nos quadros (kcal/mol) | 48 | -0.203 | -0.127 | 0.948 | 0.184 | 0.60 |

{
 "n_pairs": 48,
 "agreement": {
  "occupancy_ge_0.70": {
   "both": 2,
   "only_pH10": 3,
   "only_pH82": 4,
   "neither": 39
  },
  "same_anchor_residue": 46
 },
 "protonation_states_differing_per_system": {
  "median": 1.0,
  "min": 0,
  "max": 3
 }
}
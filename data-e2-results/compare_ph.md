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
 },
 "noise_floor_same_pH_other_seed": {
  "pH10": {
   "d_anchor_asp_fim_A": {
    "n": 8,
    "median_abs_diff": 0.30999999999999983
   },
   "occ_5A_h2": {
    "n": 8,
    "median_abs_diff": 0.03200000000000003
   },
   "peptide_rmsd_local_nm_final20pct": {
    "n": 8,
    "median_abs_diff": 0.11449999999999999
   },
   "contact_any_frac_4.5A": {
    "n": 8,
    "median_abs_diff": 0.0
   },
   "ser195_contact_frac_4.5A": {
    "n": 8,
    "median_abs_diff": 0.038000000000000034
   },
   "his57_contact_frac_4.5A": {
    "n": 8,
    "median_abs_diff": 0.007000000000000006
   }
  },
  "pH82": {
   "d_anchor_asp_fim_A": {
    "n": 8,
    "median_abs_diff": 1.37
   },
   "occ_5A_h2": {
    "n": 8,
    "median_abs_diff": 0.045500000000000006
   },
   "peptide_rmsd_local_nm_final20pct": {
    "n": 8,
    "median_abs_diff": 0.11300000000000002
   },
   "contact_any_frac_4.5A": {
    "n": 8,
    "median_abs_diff": 0.0
   },
   "ser195_contact_frac_4.5A": {
    "n": 8,
    "median_abs_diff": 0.1785
   },
   "his57_contact_frac_4.5A": {
    "n": 8,
    "median_abs_diff": 0.1905
   }
  }
 },
 "between_pH_median_abs_diff": {
  "d_anchor_asp_fim_A": 1.3599999999999999,
  "occ_5A_h2": 0.04000000000000001,
  "peptide_rmsd_local_nm_final20pct": 0.1805,
  "contact_any_frac_4.5A": 0.0,
  "ser195_contact_frac_4.5A": 0.0695,
  "his57_contact_frac_4.5A": 0.14950000000000002
 }
}
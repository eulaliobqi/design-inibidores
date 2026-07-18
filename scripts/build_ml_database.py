"""build_ml_database.py — Consolida um banco de dados único para treino de ML/DL,
juntando todas as fontes reais já geradas pelo pipeline por sequência.

Regra dura (sessão 2026-07-17/18): nunca confundir dado real com predição. Cada coluna
tem proveniência explícita registrada em consolidated_training_database.provenance.json.

Fontes:
  outputs/dataset/ml_training_dataset.csv   — base: sequence + 41 features físico-químicas
  outputs/docking/docking_results.json      — Vina REAL (fonte de verdade, não o CSV stale)
  outputs/ml_predictions.csv                — Vina PREDITO (Random Forest)
  outputs/md/md_results.json                — RMSD/Rg/H-bond REAL (MD 10ns)
  outputs/specificity/specificity_results.json — SI REAL vs 1TRN/Apis (corrigido 2026-07-18)

Uso: conda run -n protein_design_env python scripts/build_ml_database.py
"""
import json
from pathlib import Path

import pandas as pd

BASE = Path("outputs")
OUT_CSV = BASE / "dataset" / "consolidated_training_database.csv"
OUT_PROV = BASE / "dataset" / "consolidated_training_database.provenance.json"


def kr_internal(seq: str) -> int:
    """Sítios K/R internos (exclui P1 e C-terminal) — mesma lógica de analyze_cleavage.py."""
    if not isinstance(seq, str) or len(seq) < 3:
        return -1
    return sum(1 for aa in seq[1:-1] if aa in "KR")


def main():
    df = pd.read_csv(BASE / "dataset" / "ml_training_dataset.csv")
    print(f"Base: {len(df)} sequências, {len(df.columns)} colunas")

    # ── Vina REAL — fonte de verdade é docking_results.json, não o CSV (stale) ──
    dock = json.loads((BASE / "docking" / "docking_results.json").read_text())
    seq_vina_real: dict = {}
    for v in dock.values():
        seq = v.get("sequence")
        aff = v.get("best_affinity_kcal")
        if seq and aff is not None:
            seq_vina_real[seq] = aff  # última ocorrência vence (todas equivalentes p/ mesma seq)
    df["vina_affinity_kcal"] = df["sequence"].map(seq_vina_real)  # sobrescreve coluna stale
    n_real_vina = df["vina_affinity_kcal"].notna().sum()
    print(f"Vina REAL (docking_results.json): {n_real_vina} sequências")

    # ── Vina PREDITO (ML) — nunca confundir com real ──
    pred = pd.read_csv(BASE / "ml_predictions.csv")[["sequence", "predicted_vina_kcal"]]
    df = df.merge(pred, on="sequence", how="left")
    print(f"Vina PREDITO (ml_predictions.csv): {df['predicted_vina_kcal'].notna().sum()} sequências")

    # ── Resistência a autoclivagem (cálculo real, determinístico) ──
    df["kr_internal"] = df["sequence"].apply(kr_internal)
    df["resistente_kr0"] = df["kr_internal"] == 0
    print(f"Resistentes (KR-interno=0): {int(df['resistente_kr0'].sum())} sequências")

    # ── MD real ──
    md_path = BASE / "md" / "md_results.json"
    md_rmsd, md_rg, md_hbond = {}, {}, {}
    if md_path.exists():
        md = json.loads(md_path.read_text())
        for v in md.values():
            seq = v.get("sequence")
            if not seq:
                continue
            md_rmsd[seq] = v.get("rmsd_avg_nm")
            md_rg[seq] = v.get("rg_avg_nm")
            md_hbond[seq] = v.get("hbond_avg")
    df["md_rmsd_nm"] = df["sequence"].map(md_rmsd)
    df["md_rg_nm"] = df["sequence"].map(md_rg)
    df["md_hbond_avg"] = df["sequence"].map(md_hbond)
    df["md_stable"] = df["md_rmsd_nm"].apply(
        lambda x: True if pd.notna(x) and x < 0.5 else (False if pd.notna(x) else None)
    )
    print(f"MD REAL: {df['md_rmsd_nm'].notna().sum()} sequências")

    # ── Especificidade real (corrigida 2026-07-18) ──
    spec_path = BASE / "specificity" / "specificity_results.json"
    si_human, si_apis, spec_approved = {}, {}, {}
    if spec_path.exists():
        spec = json.loads(spec_path.read_text())
        for seq, v in spec.get("selectivity", {}).items():
            sis = v.get("selectivity_index", {})
            si_human[seq] = sis.get("human_trypsin")
            si_apis[seq] = sis.get("apis_mellifera_trypsin")
            spec_approved[seq] = v.get("approved")
    df["specificity_SI_human"] = df["sequence"].map(si_human)
    df["specificity_SI_apis"] = df["sequence"].map(si_apis)
    df["specificity_approved"] = df["sequence"].map(spec_approved)
    print(f"Especificidade REAL: {df['specificity_approved'].notna().sum()} sequências")

    # ── PLIP: contato com tríade catalítica real (só candidatos analisados manualmente
    #    nesta sessão — não é factível rodar PLIP nos 24.513, fica marcado como ausente
    #    para o resto) ──
    plip_catalytic = {
        "SEEEVLAANEAYAAAHTAYN": True,
        "SHIAEHEAELDAYAEAQAAA": True,
        "SALASIAAHQATFLAYLESK": True,
        "MGSLTAYLEAYAAENAAALA": False,
        "MGYLTAYHQALAAQNAALLA": False,
    }
    df["plip_contata_triade_catalitica"] = df["sequence"].map(plip_catalytic)
    print(f"PLIP (amostra manual): {df['plip_contata_triade_catalitica'].notna().sum()} sequências")

    # ── Features extras p/ testar hipótese Tyr-terminal (usa has_aromatic_cterminal já
    #    existente no CSV base, que inclui Y/F/W; adiciona versão estrita só-Tyr) ──
    df["has_tyr_cterminal"] = df["sequence"].str[-1] == "Y"
    df["n_tyr"] = df["sequence"].str.count("Y")

    df.to_csv(OUT_CSV, index=False)
    print(f"\nSalvo: {OUT_CSV} ({len(df)} linhas, {len(df.columns)} colunas)")

    provenance = {
        "real_medido": [
            "sequence", "length", "mw_da", "net_charge", "isoelectric_point",
            "hydrophobicity_kd", "boman_index", "instability_index", "aliphatic_index",
            "frac_aromatic", "frac_hydrophobic", "frac_charged", "n_arg_lys", "n_asp_glu",
            "n_aromatic", "has_aromatic_cterminal", "has_charged_nterminal", "has_pro",
            "kr_internal", "resistente_kr0", "has_tyr_cterminal", "n_tyr",
            "vina_affinity_kcal (docking_results.json, real Vina — não confundir com predicted_vina_kcal)",
            "rosetta_I_sc (apenas 50 seqs)",
            "md_rmsd_nm", "md_rg_nm", "md_hbond_avg", "md_stable (apenas 12 seqs)",
            "specificity_SI_human, specificity_SI_apis, specificity_approved (apenas top-22 seqs, corrigido 2026-07-18)",
        ],
        "predito_ML_nao_medido": ["predicted_vina_kcal (Random Forest treinado sobre vina_affinity_kcal real)"],
        "amostra_manual_nao_generalizavel": [
            "plip_contata_triade_catalitica (só 5 sequências analisadas manualmente nesta sessão, PLIP)"
        ],
        "placeholder_sem_dado": ["is_known_inhibitor (sempre 0, nunca populado — não usar)"],
        "cobertura": {
            "total_sequencias": int(len(df)),
            "com_vina_real": int(n_real_vina),
            "com_md_real": int(df["md_rmsd_nm"].notna().sum()),
            "com_specificity_real": int(df["specificity_approved"].notna().sum()),
            "com_plip_real": int(df["plip_contata_triade_catalitica"].notna().sum()),
        },
    }
    OUT_PROV.write_text(json.dumps(provenance, indent=2, ensure_ascii=False))
    print(f"Proveniência: {OUT_PROV}")


if __name__ == "__main__":
    main()

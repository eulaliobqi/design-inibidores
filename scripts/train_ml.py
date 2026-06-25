"""
Treina Random Forest + XGBoost para prever afinidade Vina a partir de features físico-químicas.

Entrada : outputs/dataset/ml_training_dataset.csv
          (requer ≥200 labels vina_affinity_kcal preenchidos — ideal: ≥500)

Saída   : models/rf_vina.pkl
          models/xgb_vina.pkl
          outputs/ml_predictions.csv   (todas as 24k seqs + predicted_vina)
          outputs/ml_top100_predicted.csv
          outputs/ml_feature_importance.png
"""

import sys
import json
import pickle
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ── paths ──────────────────────────────────────────────────────────────────
ROOT   = Path(__file__).resolve().parent.parent
DATA   = ROOT / "outputs" / "dataset" / "ml_training_dataset.csv"
MODELS = ROOT / "models"
OUT    = ROOT / "outputs"

MODELS.mkdir(exist_ok=True)

# ── feature columns ─────────────────────────────────────────────────────────
ID_COLS   = ["sequence", "length", "backbone", "is_known_inhibitor"]
LABEL_COL = "vina_affinity_kcal"
SKIP_COLS = ID_COLS + [LABEL_COL, "rosetta_I_sc", "final_score", "md_rmsd_nm", "hbond_avg"]


def load_data():
    df = pd.read_csv(DATA)
    labeled = df[df[LABEL_COL].notna()].copy()
    print(f"Total sequences : {len(df):>6}")
    print(f"Labeled (Vina)  : {len(labeled):>6}  ({100*len(labeled)/len(df):.1f}%)")
    if len(labeled) < 50:
        sys.exit("Poucos labels (<50). Rode --step docking com top_for_docking >= 500 antes.")
    return df, labeled


def prepare_features(df, labeled):
    feat_cols = [c for c in labeled.columns if c not in SKIP_COLS
                 and pd.api.types.is_numeric_dtype(labeled[c])]
    print(f"Features        : {len(feat_cols)}")
    X = labeled[feat_cols].fillna(0).values
    y = labeled[LABEL_COL].values
    return feat_cols, X, y, df[feat_cols].fillna(0)


def train_and_evaluate(X, y, feat_cols):
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import cross_val_score, train_test_split
    from sklearn.metrics import mean_squared_error, r2_score

    try:
        from xgboost import XGBRegressor
        use_xgb = True
    except ImportError:
        use_xgb = False
        print("xgboost não instalado — usando apenas Random Forest")

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

    # Random Forest
    rf = RandomForestRegressor(n_estimators=300, max_depth=None, min_samples_leaf=2,
                               n_jobs=-1, random_state=42)
    rf.fit(X_tr, y_tr)
    y_pred_rf = rf.predict(X_te)
    rmse_rf = np.sqrt(mean_squared_error(y_te, y_pred_rf))
    r2_rf   = r2_score(y_te, y_pred_rf)
    cv_rf   = cross_val_score(rf, X, y, cv=5, scoring="r2").mean()
    print(f"\nRandom Forest  — RMSE: {rmse_rf:.3f} kcal/mol | R²: {r2_rf:.3f} | CV-R²: {cv_rf:.3f}")

    with open(MODELS / "rf_vina.pkl", "wb") as f:
        pickle.dump(rf, f)

    best_model, best_name, best_rmse = rf, "RandomForest", rmse_rf

    if use_xgb:
        xgb = XGBRegressor(n_estimators=500, learning_rate=0.05, max_depth=6,
                           subsample=0.8, colsample_bytree=0.8,
                           random_state=42, verbosity=0)
        xgb.fit(X_tr, y_tr)
        y_pred_xgb = xgb.predict(X_te)
        rmse_xgb = np.sqrt(mean_squared_error(y_te, y_pred_xgb))
        r2_xgb   = r2_score(y_te, y_pred_xgb)
        cv_xgb   = cross_val_score(xgb, X, y, cv=5, scoring="r2").mean()
        print(f"XGBoost        — RMSE: {rmse_xgb:.3f} kcal/mol | R²: {r2_xgb:.3f} | CV-R²: {cv_xgb:.3f}")
        with open(MODELS / "xgb_vina.pkl", "wb") as f:
            pickle.dump(xgb, f)
        if rmse_xgb < best_rmse:
            best_model, best_name, best_rmse = xgb, "XGBoost", rmse_xgb

    print(f"\nMelhor modelo: {best_name} (RMSE {best_rmse:.3f} kcal/mol)")

    # feature importance
    _plot_importance(rf, feat_cols)

    return best_model


def _plot_importance(model, feat_cols):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        imp = pd.Series(model.feature_importances_, index=feat_cols).sort_values(ascending=False)
        top = imp.head(20)

        fig, ax = plt.subplots(figsize=(8, 6))
        top.plot.barh(ax=ax, color="#1565C0")
        ax.set_xlabel("Importância (Random Forest)")
        ax.set_title("Top-20 features preditoras de afinidade Vina")
        ax.invert_yaxis()
        plt.tight_layout()
        fig.savefig(OUT / "ml_feature_importance.png", dpi=150)
        plt.close()
        print(f"Feature importance salva: {OUT / 'ml_feature_importance.png'}")
    except Exception as e:
        print(f"Plot ignorado ({e})")


def predict_all(model, df_all, X_all, feat_cols):
    preds = model.predict(X_all)
    out = df_all[["sequence", "length"]].copy() if "sequence" in df_all.columns else df_all[[]].copy()
    out["predicted_vina_kcal"] = preds
    # adiciona labels reais quando disponíveis
    if LABEL_COL in df_all.columns:
        out["vina_real_kcal"] = df_all[LABEL_COL].values

    out_sorted = out.sort_values("predicted_vina_kcal")
    out_sorted.to_csv(OUT / "ml_predictions.csv", index=False)
    out_sorted.head(100).to_csv(OUT / "ml_top100_predicted.csv", index=False)

    print(f"\nPredições salvas: {OUT / 'ml_predictions.csv'}  ({len(out_sorted)} seqs)")
    print(f"Top-100 preditas: {OUT / 'ml_top100_predicted.csv'}")
    print(f"\nTop-10 por predicted_vina_kcal:")
    cols = ["sequence", "predicted_vina_kcal"] + (["vina_real_kcal"] if "vina_real_kcal" in out_sorted.columns else [])
    print(out_sorted[cols].head(10).to_string(index=False))

    # salvar métricas em JSON
    metrics = {
        "n_sequences_total": len(out_sorted),
        "n_labeled": int(out_sorted["vina_real_kcal"].notna().sum()) if "vina_real_kcal" in out_sorted.columns else 0,
        "predicted_vina_range": [float(preds.min()), float(preds.max())],
        "top1_sequence": str(out_sorted.iloc[0]["sequence"]),
        "top1_predicted_vina": float(out_sorted.iloc[0]["predicted_vina_kcal"]),
    }
    (OUT / "ml_metrics.json").write_text(json.dumps(metrics, indent=2))


def main():
    print("=" * 60)
    print("  ML Training — Predição de Afinidade Vina")
    print("=" * 60)

    df, labeled = load_data()
    feat_cols, X_lab, y_lab, X_all = prepare_features(df, labeled)
    best_model = train_and_evaluate(X_lab, y_lab, feat_cols)
    predict_all(best_model, df, X_all.values, feat_cols)

    print("\nConcluido.")


if __name__ == "__main__":
    main()

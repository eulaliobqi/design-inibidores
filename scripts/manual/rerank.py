"""
rerank.py — Re-gera ranking integrado com docking_results.json + rosetta_scores.json.

Uso: conda run -n protein_design_env python rerank.py
"""
import json
from pathlib import Path
import pandas as pd

BASE   = Path("outputs")
DOCK   = BASE / "docking_results.json"
ROS    = BASE / "rosetta_scores.json"
CSV    = BASE / "ranking" / "ranking.csv"
TOP    = BASE / "ranking" / "ranking_top.json"
ML_CSV = BASE / "dataset" / "ml_training_dataset.csv"

# Pesos (config.yaml)
W_VINA = 0.50
W_ROS  = 0.20
W_HB   = 0.15
W_RMSD = 0.10
W_ALK  = 0.05

# ── Carregar JSONs ──────────────────────────────────────────────
dock = json.loads(DOCK.read_text())
ros  = json.loads(ROS.read_text())

# Melhor Vina por sequência (usa min entre len5/len7/… do mesmo peptídeo)
best_vina: dict[str, float] = {}
for v in dock.values():
    seq = v["sequence"]
    aff = v["best_affinity_kcal"]
    if seq not in best_vina or aff < best_vina[seq]:
        best_vina[seq] = aff

# I_sc por sequência
ros_by_seq: dict[str, float] = {v["sequence"]: v["I_sc"] for v in ros.values()}

print(f"Docking:  {len(best_vina)} sequências únicas")
print(f"Rosetta:  {len(ros_by_seq)} complexos")

# ── Atualizar ranking.csv ──────────────────────────────────────
df = pd.read_csv(CSV)
print(f"Ranking:  {len(df)} sequências (antes: {df['vina_affinity'].notna().sum()} com Vina)")

df["vina_affinity"] = df["sequence"].map(best_vina)
df["rosetta_I_sc"]  = df["sequence"].map(ros_by_seq)
# MD ainda não disponível localmente — mantém None
# df["md_rmsd_nm"] já é None para todos

# ── Recalcular score composto ──────────────────────────────────
def norm(series: pd.Series, invert: bool = False) -> pd.Series:
    fs = series.astype(float)
    med = float(fs.dropna().median()) if fs.dropna().size > 0 else 0.0
    filled = fs.fillna(med)
    mn, mx = float(filled.min()), float(filled.max())
    if mx == mn:
        return pd.Series([0.5] * len(filled), index=filled.index)
    n = (filled - mn) / (mx - mn)
    return (1 - n) if invert else n

df["n_vina"]  = norm(df["vina_affinity"], invert=True)
df["n_ros"]   = norm(df["rosetta_I_sc"],  invert=True)
hb_proxy      = df["hbond_avg"].astype(float).fillna(df["n_arg_lys"].astype(float))
df["n_hb"]    = norm(hb_proxy,            invert=False)
df["n_rmsd"]  = norm(df["md_rmsd_nm"],    invert=True)
df["n_alk"]   = norm(df["n_arg_lys"].astype(float), invert=False)

df["final_score"] = (
    W_VINA * df["n_vina"]  +
    W_ROS  * df["n_ros"]   +
    W_HB   * df["n_hb"]    +
    W_RMSD * df["n_rmsd"]  +
    W_ALK  * df["n_alk"]
)

df = df.sort_values("final_score", ascending=False).reset_index(drop=True)
df["rank"] = df.index + 1

# ── Salvar ranking.csv e ranking_top.json ──────────────────────
df.to_csv(CSV, index=False, float_format="%.4f")
top20 = df.head(20).to_dict(orient="records")
TOP.write_text(json.dumps(top20, indent=2, default=str))

print(f"Após:     {df['vina_affinity'].notna().sum()} com Vina, {df['rosetta_I_sc'].notna().sum()} com Rosetta")

# ── Atualizar ml_training_dataset.csv ─────────────────────────
if ML_CSV.exists():
    df_ml = pd.read_csv(ML_CSV)
    score_map = df.set_index("sequence")[["vina_affinity", "rosetta_I_sc", "final_score"]].to_dict("index")
    df_ml["vina_affinity_kcal"] = df_ml["sequence"].map(
        lambda s: score_map.get(s, {}).get("vina_affinity"))
    df_ml["rosetta_I_sc"] = df_ml["sequence"].map(
        lambda s: score_map.get(s, {}).get("rosetta_I_sc"))
    df_ml["final_score"] = df_ml["sequence"].map(
        lambda s: score_map.get(s, {}).get("final_score"))
    df_ml.to_csv(ML_CSV, index=False, float_format="%.6f")
    labeled = df_ml["vina_affinity_kcal"].notna().sum()
    print(f"ML CSV:   {labeled}/{len(df_ml)} sequências com labels")

# ── Relatório final ────────────────────────────────────────────
print()
print("TOP 10 CANDIDATOS (Vina 50% + I_sc 20% + propriedades 30%)")
print(f"{'#':>2}  {'Sequência':<22}  {'Vina':>8}  {'I_sc':>8}  {'Score':>7}")
print("-" * 57)
for _, r in df.head(10).iterrows():
    vina_s = f"{r['vina_affinity']:.2f}" if pd.notna(r["vina_affinity"]) else "  N/A"
    isc_s  = f"{r['rosetta_I_sc']:.2f}"  if pd.notna(r["rosetta_I_sc"])  else "  N/A"
    print(f"{int(r['rank']):>2}  {r['sequence']:<22}  {vina_s:>8}  {isc_s:>8}  {r['final_score']:>7.3f}")

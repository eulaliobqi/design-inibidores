"""
run_cleavage_b23.py — A3 do plano de retomada (2026-09-24): filtro real de resistência a
protease sobre as sequências da campanha B2.3, usando o P1-âncora geométrico (A2,
compute_geometric_p1.py) em vez da heurística linear "mais C-terminal" — os candidatos são
macrociclos, sem terminal real.

Lê outputs/b23_campaign_<especie>/dataset/ml_training_dataset.csv (coluna `backbone`,
formato "len{L}_design_{i}") + data-lepidoptera-panel/geometric_p1_b23.json, roda
analyze_cleavage.analyze_sequence com o P1 geométrico certo por backbone, e consolida
RESISTENTE / MARGINAL / SUSCEPTIVEL por espécie e no total.

Uso:
  python scripts/run_cleavage_b23.py --species all7 \
      --campaign-dir outputs/b23_campaign --geometric-p1 data-lepidoptera-panel/geometric_p1_b23.json \
      --out outputs/b23_cleavage_analysis.json
"""
import argparse
import csv
import json
from pathlib import Path

from analyze_cleavage import analyze_sequence

ROOT = Path(__file__).parent.parent
SPECIES_7 = ["Sfrugiperda", "Slitura", "Onubilalis", "Dsaccharalis",
             "Cincludens", "Hvirescens", "Pxylostella"]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--species", nargs="+", default=SPECIES_7)
    ap.add_argument("--campaign-dir", type=str, default="outputs/b23_campaign")
    ap.add_argument("--geometric-p1", type=str, default="data-lepidoptera-panel/geometric_p1_b23.json")
    ap.add_argument("--out", type=str, default="outputs/b23_cleavage_analysis.json")
    args = ap.parse_args()

    geo = json.loads((ROOT / args.geometric_p1).read_text())

    all_results = {}
    summary_total = {"RESISTENTE": 0, "MARGINAL": 0, "SUSCEPTIVEL": 0}
    n_no_geo = 0

    for species in args.species:
        csv_path = ROOT / f"{args.campaign_dir}_{species}" / "dataset" / "ml_training_dataset.csv"
        if not csv_path.exists():
            print(f"[{species}] dataset não encontrado: {csv_path} — pulando")
            continue

        backbones = geo.get(species, {}).get("backbones", {})
        species_results = []
        summary_sp = {"RESISTENTE": 0, "MARGINAL": 0, "SUSCEPTIVEL": 0}

        with open(csv_path, newline="") as f:
            for row in csv.DictReader(f):
                seq = row["sequence"]
                backbone_id = row["backbone"]
                geo_entry = backbones.get(backbone_id)
                p1_1based = None
                if geo_entry and "error" not in geo_entry:
                    p1_1based = geo_entry["p1_position_1based"]
                else:
                    n_no_geo += 1

                r = analyze_sequence(seq, geometric_p1_1based=p1_1based)
                r["backbone"] = backbone_id
                r["geometric_p1_1based"] = p1_1based
                species_results.append(r)
                summary_sp[r["verdict"]] += 1
                summary_total[r["verdict"]] += 1

        all_results[species] = {"n_sequences": len(species_results), "summary": summary_sp,
                                 "results": species_results}
        print(f"[{species}] {len(species_results)} sequências — "
              f"RESISTENTE={summary_sp['RESISTENTE']} MARGINAL={summary_sp['MARGINAL']} "
              f"SUSCEPTIVEL={summary_sp['SUSCEPTIVEL']}")

    out_path = ROOT / args.out
    out_path.parent.mkdir(exist_ok=True, parents=True)
    out_path.write_text(json.dumps({"summary_total": summary_total, "by_species": all_results},
                                    indent=2, ensure_ascii=False))

    total = sum(summary_total.values())
    print(f"\n{'='*60}")
    print(f"TOTAL ({total} sequências reais analisadas):")
    for v, n in summary_total.items():
        pct = 100 * n / total if total else 0
        print(f"  {v:<12} {n:>6}  ({pct:.1f}%)")
    if n_no_geo:
        print(f"\nAVISO: {n_no_geo} sequências sem P1 geométrico disponível "
              f"(backbone não encontrado em geometric_p1_b23.json) — analisadas sem âncora, "
              f"todo K/R interno contou como susceptível.")
    print(f"\nSalvo em: {out_path}")


if __name__ == "__main__":
    main()

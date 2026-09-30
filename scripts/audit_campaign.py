"""
audit_campaign.py -- auditoria independente dos numeros da campanha B2.3, lidos dos arquivos
reais (nao de documentos): backbones por especie/comprimento, fechamento N-C do macrociclo,
comprimento da cadeia B, hotspot EFETIVAMENTE usado (do .trb do RFdiffusion) e sequencias do
ProteinMPNN (contagem, unicidade, comprimento igual ao do backbone de origem).

Uso (servidor): python -m scripts.audit_campaign [--out data-b23-scoring/results/campaign_audit.json]
"""
import csv
import json
import pickle
import sys
from pathlib import Path

import numpy as np
from Bio.PDB import PDBParser

ROOT = Path(__file__).parent.parent
SPECIES = ["Sfrugiperda", "Slitura", "Onubilalis", "Dsaccharalis", "Cincludens", "Hvirescens",
           "Pxylostella", "Agemmatalis"]


def nc_distance(pdb: Path):
    s = PDBParser(QUIET=True).get_structure("x", str(pdb))
    chains = {c.id: [r for r in c if r.id[0] == " "] for c in s[0]}
    b = chains.get("B") or list(chains.values())[-1]
    return len(b), float(b[0]["N"] - b[-1]["C"]), len(chains.get("A", []))


def main():
    out = {}
    for sp in SPECIES:
        base = ROOT / "outputs" / f"b23_campaign_{sp}"
        rfd = base / "rfdiffusion"
        n_bb, per_len, nc, bad_len, hot = 0, {}, [], 0, set()
        for ldir in sorted(rfd.glob("len_*"), key=lambda p: int(p.name.split("_")[1])):
            L = int(ldir.name.split("_")[1])
            for pdb in sorted(ldir.glob("design_*.pdb")):
                if "_traj" in pdb.stem:
                    continue
                n_b, d, n_a = nc_distance(pdb)
                n_bb += 1
                per_len[L] = per_len.get(L, 0) + 1
                nc.append(d)
                bad_len += int(n_b != L)
                trb = pdb.with_suffix(".trb")
                if trb.exists():
                    try:
                        conf = pickle.load(open(trb, "rb")).get("config", {})
                        hs = conf.get("ppi", {}).get("hotspot_res")
                        if hs:
                            hot.add(tuple(hs))
                    except Exception as e:  # noqa: BLE001
                        hot.add(("trb_erro", str(e)[:60]))
        csv_path = base / "dataset" / "ml_training_dataset.csv"
        seqs, uniq, mism = 0, set(), 0
        if csv_path.exists():
            for row in csv.DictReader(open(csv_path, newline="")):
                seqs += 1
                uniq.add(row["sequence"])
                mism += int(len(row["sequence"]) != int(row["length"]))
        out[sp] = {
            "backbones": n_bb, "per_length": per_len, "chain_B_length_mismatch": bad_len,
            "nc_min_A": round(min(nc), 2) if nc else None, "nc_max_A": round(max(nc), 2) if nc else None,
            "nc_n_gt_2A": int(sum(x > 2.0 for x in nc)),
            "receptor_residues_chainA": n_a if n_bb else None,
            "hotspots_in_trb": sorted(map(list, hot)),
            "sequences_rows": seqs, "sequences_unique": len(uniq), "seq_len_vs_length_mismatch": mism,
        }
        print(sp, json.dumps(out[sp]), flush=True)
    dest = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else \
        ROOT / "data-b23-scoring" / "results" / "campaign_audit.json"
    dest.write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

"""
run_md_ph_campaign.py -- MD de triagem (10 ns, 1 replica) dos top-3 por especie num pH escolhido (--ph).

Identico a run_md_top_candidates.py (mesma montagem CHARMM36, mesmo protocolo), exceto que sobrescreve
`md.gut_ph` do config.yaml. A protonacao das cadeias laterais (PROPKA) e o estado do N-terminal do peptideo
linear seguem o pH: `build_system_charmm.build(nterm="auto")` deixa o N-terminal NEUTRO quando
pH - 7,7 >= 2 (pKa medio do N-terminal 7,7 +- 0,5; Grimsley, Scholtz e Pace 2009, doi 10.1002/pro.19), ou seja,
neutro em pH 10 e carregado (NH3+) em pH 8,2. O 1o residuo Pro fica PRO-NH2+ (sem patch neutro no campo).
O macrociclo nao tem extremidades. O resumo de cada simulacao grava o pH e o estado do N-terminal.

Uso: python -m scripts.run_md_ph_campaign --candidates data-b23-scoring/results/top_candidates_L.json \
        --workdir outputs/mdph_L_ph10 --front L --ph 10.0 [--species Agemmatalis ...]
"""
import argparse
import json
import logging
from pathlib import Path

import yaml

from scripts.agents.md_agent import MDAgent

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
ROOT = Path(__file__).parent.parent


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--candidates", required=True)
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--front", choices=["L", "M"], required=True)
    ap.add_argument("--ph", type=float, required=True)
    ap.add_argument("--species", nargs="+")
    ap.add_argument("--ns", type=int, default=10)
    ap.add_argument("--nterm", choices=["auto", "charged", "neutral"], default="auto")
    args = ap.parse_args()

    workdir = ROOT / args.workdir
    candidates = json.loads((ROOT / args.candidates).read_text())["candidates"]
    if args.species:
        candidates = {k: v for k, v in candidates.items() if k in args.species or v.get("species") in args.species}

    config = yaml.safe_load(open(ROOT / "config.yaml"))
    config.setdefault("md", {})["gut_ph"] = args.ph
    # "auto": N-terminal do linear neutro quando pH - 7,7 >= 2 (neutro em pH 10, NH3+ em pH 8,2).
    config["md"]["nterm"] = args.nterm
    agent = MDAgent("MDAgent_ph_campaign", config, str(workdir))
    workdir.mkdir(parents=True, exist_ok=True)
    temp = config["md"].get("temperature", 300)

    summary_path = workdir / "summary.json"
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}
    for key, meta in candidates.items():
        if summary.get(key, {}).get("status") == "done":
            print(f"[{key}] ja concluido, pulando")
            continue
        src = ROOT / meta["pdb"]
        if not src.exists():
            summary[key] = {"status": "sem_fonte_real"}
            summary_path.write_text(json.dumps(summary, indent=2))
            continue
        out_dir = workdir / key
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"[{key}] iniciando MD 1x{args.ns}ns pH {args.ph} (seq={meta['sequence']})...")
        try:
            result = agent._run_gromacs(str(src), out_dir, args.ns, temp, meta["sequence"], cyclic=args.front == "M")
            nn = None
            rep = out_dir / "build_report.json"
            if rep.exists():
                nn = json.loads(rep.read_text()).get("nterm_neutral")
            summary[key] = {
                "status": "erro" if result.get("error") else "done",
                "sequence": meta["sequence"], "backbone": meta["backbone"],
                "confidence_score": meta["confidence_score"], "source_pdb": meta["pdb"],
                "ns": args.ns, "cyclic": args.front == "M", "front": args.front,
                "ph": args.ph, "nterm_mode": args.nterm, "nterm_neutral": nn, **result,
            }
            print(f"[{key}] concluido: {result}")
        except Exception as e:  # noqa: BLE001
            print(f"[{key}] ERRO: {e}")
            summary[key] = {"status": "erro", "erro": str(e)}
        summary_path.write_text(json.dumps(summary, indent=2))
    print("MD_PH_CAMPAIGN_ALL_DONE")


if __name__ == "__main__":
    main()

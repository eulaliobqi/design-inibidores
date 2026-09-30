"""
score_boltz2_b23.py -- pontua com Boltz-2 (unico scorer validado em B0.5, 10/10 real-vs-
decoy) os candidatos RESISTENTE a protease da campanha B2.3 (outputs/b23_cleavage_analysis.json).

Usa MSA real pre-calculado do receptor (precompute_receptor_msa.py, uma vez por especie --
evita 2.360 chamadas repetidas ao servidor MMseqs2 pro mesmo receptor fixo) e msa: empty
(single-sequence) pro peptideo desenhado (de novo, sem homologos reais). Peptideo LINEAR por
padrao desde 2026-09-30 (--cyclic reproduz o cyclic: true usado ate 2026-09-29).

Uso:
  # 1) gerar os yaml de entrada (rapido, sem GPU)
  python scripts/score_boltz2_b23.py write-yaml --species Sfrugiperda --limit 20
  # 2) rodar boltz predict por especie (env boltz2-env, GPU)
  boltz predict data-b23-scoring/boltz_yaml/Sfrugiperda --model boltz2 \
      --out_dir outputs/b23_boltz2_Sfrugiperda --output_format pdb
  # 3) consolidar os confidence_*.json em um JSON so
  python scripts/score_boltz2_b23.py collect --species Sfrugiperda
"""
import argparse
import json
from pathlib import Path

from Bio.PDB import PDBParser, PPBuilder

ROOT = Path(__file__).parent.parent
SPECIES_7 = ["Sfrugiperda", "Slitura", "Onubilalis", "Dsaccharalis",
             "Cincludens", "Hvirescens", "Pxylostella"]

SPECIES_PDB = {
    "Sfrugiperda": "Sfrugiperda-A0A089QDB3-AlphaFold.pdb",
    "Slitura": "Slitura-B3F884-AlphaFold.pdb",
    "Onubilalis": "Onubilalis-Q6R561-AlphaFold.pdb",
    "Dsaccharalis": "Dsaccharalis-T1QDI0-AlphaFold.pdb",
    "Cincludens": "Cincludens-A0A9P0BRD5-AlphaFold.pdb",
    "Hvirescens": "Hvirescens-I7D523-AlphaFold.pdb",
    "Pxylostella": "Pxylostella-E2IGY7-AlphaFold.pdb",
    "Agemmatalis": "Agemmatalis-A0A2U8NFD7-AlphaFold.pdb",
}


def get_receptor_sequence(species: str) -> str:
    pdb_path = ROOT / "data-lepidoptera-panel" / SPECIES_PDB[species]
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure(species, str(pdb_path))
    ppb = PPBuilder()
    return "".join(str(pp.get_sequence()) for pp in ppb.build_peptides(structure))


def load_resistant(species: str, cleavage_json: Path):
    d = json.loads(cleavage_json.read_text())
    results = d["by_species"][species]["results"]
    return [r for r in results if r["verdict"] == "RESISTENTE"]


def write_yaml(args):
    receptor_seq = get_receptor_sequence(args.species)
    msa_path = (ROOT / args.msa_cache_dir / f"receptor_{args.species}.csv").resolve()
    if not msa_path.exists():
        raise FileNotFoundError(
            f"MSA cache nao encontrado em {msa_path} -- rode precompute_receptor_msa.py antes."
        )

    candidates = load_resistant(args.species, ROOT / args.cleavage_json)
    if args.limit:
        candidates = candidates[: args.limit]

    out_dir = ROOT / args.yaml_dir / args.species
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_dir = ROOT / args.yaml_dir / "_manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)

    cyc = "      cyclic: true\n" if args.cyclic else ""   # padrão linear desde 2026-09-30
    manifest = {}
    for idx, cand in enumerate(candidates):
        stem = f"{args.species}__{cand['backbone']}__{idx}"
        yaml_text = f"""version: 1
sequences:
  - protein:
      id: A
      sequence: {receptor_seq}
      msa: {msa_path}
  - protein:
      id: B
      sequence: {cand['sequence']}
{cyc}      msa: empty
"""
        (out_dir / f"{stem}.yaml").write_text(yaml_text)
        manifest[stem] = {
            "species": args.species,
            "backbone": cand["backbone"],
            "sequence": cand["sequence"],
            "length": cand["length"],
            "susceptibility_score": cand["susceptibility_score"],
        }

    manifest_path = manifest_dir / f"{args.species}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"[{args.species}] {len(candidates)} yaml escritos em {out_dir} (manifest: {manifest_path})")


def collect(args):
    out_boltz_dir = ROOT / f"{args.boltz_out_prefix}_{args.species}"
    manifest_path = ROOT / args.yaml_dir / "_manifests" / f"{args.species}.json"
    manifest = json.loads(manifest_path.read_text())

    pred_dirs = list(out_boltz_dir.glob("boltz_results_*/predictions"))
    if not pred_dirs:
        raise FileNotFoundError(f"Nenhum boltz_results_*/predictions encontrado em {out_boltz_dir}")

    results = []
    n_missing = 0
    for stem, meta in manifest.items():
        conf_path = None
        for pred_dir in pred_dirs:
            cand = pred_dir / stem / f"confidence_{stem}_model_0.json"
            if cand.exists():
                conf_path = cand
                break
        if conf_path is None:
            n_missing += 1
            continue
        conf = json.loads(conf_path.read_text())
        results.append({
            **meta,
            "confidence_score": conf.get("confidence_score"),
            "complex_plddt": conf.get("complex_plddt"),
            "iptm": conf.get("iptm"),
            "ligand_iptm": conf.get("ligand_iptm"),
            "protein_iptm": conf.get("protein_iptm"),
        })

    results.sort(key=lambda r: r["confidence_score"] or -1, reverse=True)
    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    existing = {}
    if out_path.exists():
        existing = json.loads(out_path.read_text())
    existing[args.species] = results
    out_path.write_text(json.dumps(existing, indent=2))
    print(f"[{args.species}] {len(results)} pontuados, {n_missing} faltando -> {out_path}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("write-yaml")
    p1.add_argument("--species", required=True, choices=SPECIES_7 + ["Agemmatalis"])
    p1.add_argument("--cleavage-json", default="outputs/b23_cleavage_analysis.json")
    p1.add_argument("--msa-cache-dir", default="data-b23-scoring/msa_cache")
    p1.add_argument("--yaml-dir", default="data-b23-scoring/boltz_yaml")
    p1.add_argument("--limit", type=int, default=0)
    p1.add_argument("--cyclic", action="store_true",
                    help="Declara o peptideo como macrociclo cabeca-cauda (comportamento ate 2026-09-29). "
                         "Padrao: peptideo linear.")
    p1.set_defaults(func=write_yaml)

    p2 = sub.add_parser("collect")
    p2.add_argument("--species", required=True, choices=SPECIES_7 + ["Agemmatalis"])
    p2.add_argument("--yaml-dir", default="data-b23-scoring/boltz_yaml")
    p2.add_argument("--boltz-out-prefix", default="outputs/b23_boltz2")
    p2.add_argument("--out", default="outputs/b23_boltz2_scores.json")
    p2.set_defaults(func=collect)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

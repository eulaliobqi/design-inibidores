"""
precompute_receptor_msa.py -- pre-requisito do B2.7/scoring: calcula o MSA real do
receptor (via servidor MMseqs2, o mesmo usado pelo boltz --use_msa_server) UMA VEZ por
especie, e salva em CSV no formato aceito pelo boltz (msa: <path>.csv custom). Evita
2.360 chamadas repetidas ao servidor MSA para o mesmo receptor fixo por especie --
so o peptideo desenhado (sem homologos reais) usa msa: empty (single-sequence).

Sequencia extraida direto do PDB real do painel (data-lepidoptera-panel/*.pdb), nao de
memoria/heuristica.

Uso (env boltz2-env, tem requests/mmseqs2 client do boltz):
  python scripts/precompute_receptor_msa.py --out-dir data-b23-scoring/msa_cache
"""
import argparse
from pathlib import Path

from Bio.PDB import PDBParser, PPBuilder

from boltz.main import compute_msa

ROOT = Path(__file__).parent.parent

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
    seq = "".join(str(pp.get_sequence()) for pp in ppb.build_peptides(structure))
    return seq


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--species", nargs="+", default=list(SPECIES_PDB.keys()))
    ap.add_argument("--out-dir", type=str, default="data-b23-scoring/msa_cache")
    ap.add_argument("--msa-server-url", type=str, default="https://api.colabfold.com")
    args = ap.parse_args()

    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    for species in args.species:
        seq = get_receptor_sequence(species)
        target_id = f"receptor_{species}"
        final_csv = out_dir / f"{target_id}.csv"
        if final_csv.exists():
            print(f"[{species}] MSA ja existe em {final_csv} -- pulando")
            continue
        print(f"[{species}] calculando MSA real ({len(seq)} aa) via {args.msa_server_url}")
        compute_msa(
            data={target_id: seq},
            target_id=target_id,
            msa_dir=out_dir,
            msa_server_url=args.msa_server_url,
            msa_pairing_strategy="greedy",
        )
        if final_csv.exists():
            print(f"[{species}] OK -> {final_csv}")
        else:
            print(f"[{species}] ERRO: {final_csv} nao foi gerado")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Piloto B2.3 (Trilha A) — geração macrocíclica via RFdiffusion ancorada nos
hotspots reais de B1.4 (S1+S2 do template escolhido), redesign de sequência
via ProteinMPNN.

Sem contrasseleção nesta fase (decisão do usuário, 2026-09-23): foco em
potência ampla contra o painel de Lepidoptera, não seletividade alvo×antialvo.
B1.2 (painel negativo) e B1.5 (determinantes de seletividade) ficam
arquivados para outra parte do projeto — ver
C:\\Users\\eulal\\.claude\\plans\\sharded-conjuring-lecun.md.

Script leve e dedicado (não reaproveita o orquestrador de 12 estágios do V1
em scripts/run_pipeline.py — aquele inclui Rosetta/Vina/especificidade/MD,
que não fazem parte deste piloto).

Uso:
  python scripts/run_diffusion_campaign.py --species Sfrugiperda --num-designs 5
"""
import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from scripts.agents import RFdiffusionAgent, ProteinMPNNAgent  # noqa: E402

SUBSITES_JSON = ROOT / "data-lepidoptera-panel" / "subsites_by_receptor.json"
PANEL_DIR = ROOT / "data-lepidoptera-panel"

RECEPTOR_FILES = {
    "Sfrugiperda": "Sfrugiperda-A0A089QDB3-AlphaFold.pdb",
    "Slitura": "Slitura-B3F884-AlphaFold.pdb",
    "Onubilalis": "Onubilalis-Q6R561-AlphaFold.pdb",
    "Dsaccharalis": "Dsaccharalis-T1QDI0-AlphaFold.pdb",
    "Cincludens": "Cincludens-A0A9P0BRD5-AlphaFold.pdb",
    "Hvirescens": "Hvirescens-I7D523-AlphaFold.pdb",
    "Pxylostella": "Pxylostella-E2IGY7-AlphaFold.pdb",
    "Msexta": "Msexta-P35045-AlphaFold.pdb",
    "Bmori": "Bmori-A0A8R2C8B0-AlphaFold.pdb",
}


def load_hotspots(species: str, template: str, subsites: tuple[str, ...]) -> list[int]:
    data = json.loads(SUBSITES_JSON.read_text())
    tdata = data["receptors"][species]["templates"][template]
    if tdata["status"] != "go":
        raise RuntimeError(f"{species} x {template}: status={tdata['status']} — não usar hotspots deste template")
    resnums = set()
    for sl in subsites:
        for entry in tdata["subsites"][sl]:
            recv = entry.get("receptor")
            if recv:
                num = int("".join(ch for ch in recv if ch.isdigit()))
                resnums.add(num)
    return sorted(resnums)


def receptor_centroid(pdb_path: Path, resnums: list[int]) -> list[float]:
    from Bio.PDB import PDBParser
    import numpy as np

    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("x", str(pdb_path))
    coords = [
        res["CA"].coord for res in structure[0]["A"]
        if res.id[1] in resnums and "CA" in res
    ]
    if not coords:
        return [0.0, 0.0, 0.0]
    return [float(x) for x in np.mean(coords, axis=0)]


def check_cyclic_geometry(pdb_path: Path):
    """Distância N(res1)-C(resN) — QC do fechamento macrocíclico real.
    Referência B0.2 (docs/bench/rfdiff_sm120.md): 1.241A observado, ~1.33A esperado.

    A saída do RFdiffusion em modo binder (Complex_base_ckpt) tem DUAS cadeias:
    A = receptor (alvo, ~230-270aa), B = peptídeo desenhado (o macrociclo real) —
    confirmado por inspeção direta (bug real encontrado no piloto B2.3: medir a
    cadeia A por engano dá N-C ~90A, sem sentido nenhum pra ciclização)."""
    from Bio.PDB import PDBParser

    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("x", str(pdb_path))
    model = structure[0]
    chain_id = "B" if "B" in model else list(model.child_dict.keys())[-1]
    residues = [r for r in model[chain_id] if r.id[0] == " "]
    if len(residues) < 2:
        return None
    try:
        return float(residues[0]["N"] - residues[-1]["C"])
    except KeyError:
        return None


# 7 alvos primários do painel (panel_v2.json) — exclui Msexta (referência) e Bmori
# (painel negativo B1.2, fora de escopo desta fase de potência ampla).
ALL_PRIMARY_SPECIES = [
    "Sfrugiperda", "Slitura", "Onubilalis", "Dsaccharalis",
    "Cincludens", "Hvirescens", "Pxylostella",
]


def run_for_species(species: str, args) -> None:
    receptor_pdb = PANEL_DIR / RECEPTOR_FILES[species]
    hotspots = load_hotspots(species, args.template, tuple(args.subsites))
    print(f"\n{'='*60}\nAlvo: {species} ({receptor_pdb.name})")
    print(f"Hotspots reais (B1.4, {'+'.join(args.subsites)}, template {args.template}): {hotspots}")
    center = receptor_centroid(receptor_pdb, hotspots)
    print(f"Centroide: {center}")

    config = yaml.safe_load((ROOT / "config.yaml").read_text())
    config["rfdiffusion"] = {
        **config.get("rfdiffusion", {}),
        "contig_lengths": args.lengths,
        "num_designs": args.num_designs,
        "cyclic": True,
    }

    out_base = ROOT / "outputs" / f"b23_campaign_{species}"
    rfd_agent = RFdiffusionAgent("RFdiffusionAgent", config, out_base / "rfdiffusion")
    binding_site = {"consensus_center_xyz": center, "hotspot_residues": hotspots}
    backbones = rfd_agent.run(str(receptor_pdb), binding_site)

    total = sum(len(v) for v in backbones.values())
    print(f"\n{total} backbones gerados. QC de fechamento macrocíclico (N-C, esperado 1.2-1.4A):")
    n_ok = 0
    for length, pdbs in backbones.items():
        for pdb in pdbs:
            d = check_cyclic_geometry(Path(pdb))
            ok = d is not None and d < 2.0
            n_ok += int(ok)
            print(f"  {Path(pdb).name}: N-C={d} {'OK' if ok else 'FALHOU'}")
    print(f"Macrociclos reais confirmados: {n_ok}/{total}")

    if total == 0:
        print(f"{species}: nenhum backbone gerado — pulando ProteinMPNN.")
        return

    mpnn_config = dict(config)
    mpnn_config["proteinmpnn"] = {**config.get("proteinmpnn", {}), "num_seq_per_target": args.num_seq_per_target}
    mpnn_agent = ProteinMPNNAgent("ProteinMPNNAgent", mpnn_config, out_base / "proteinmpnn")
    mpnn_agent.run(backbones, str(receptor_pdb))

    print(f"{species} concluído: {out_base}/")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--species", default="Sfrugiperda",
                     choices=sorted(RECEPTOR_FILES) + ["all7"],
                     help="'all7' roda os 7 alvos primários do painel em sequência")
    ap.add_argument("--template", default="1SFI_SFTI1", choices=["1SFI_SFTI1", "2PTC_BPTI"])
    ap.add_argument("--subsites", nargs="+", default=["S1", "S2"],
                     help="Subsítios de B1.4 usados como hotspot (default: S1 S2)")
    ap.add_argument("--lengths", nargs="+", type=int, default=[8, 10, 12, 14, 16],
                     help="Comprimentos de macrociclo (aa), faixa Trilha A do plano é 8-16")
    ap.add_argument("--num-designs", type=int, default=10)
    ap.add_argument("--num-seq-per-target", type=int, default=30)
    args = ap.parse_args()

    species_list = ALL_PRIMARY_SPECIES if args.species == "all7" else [args.species]
    failed = []
    for i, species in enumerate(species_list, 1):
        print(f"\n### [{i}/{len(species_list)}] {species} ###")
        try:
            run_for_species(species, args)
        except Exception as e:
            print(f"ERRO em {species}: {e} — continuando com o próximo alvo")
            failed.append(species)

    print(f"\n{'='*60}\nCampanha concluída. {len(species_list) - len(failed)}/{len(species_list)} alvos OK.")
    if failed:
        print(f"Falharam: {failed}")


if __name__ == "__main__":
    main()

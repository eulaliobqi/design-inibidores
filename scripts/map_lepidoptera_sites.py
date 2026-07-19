import json
import logging
from pathlib import Path

import yaml

from scripts.agents.structure_agent import StructureAgent

logging.basicConfig(level=logging.WARNING)

config = yaml.safe_load(open("config.yaml"))

STRUCTS = {
    "Msexta": ("data-nontargets/Msexta-P35045-AlphaFold.pdb", "P35045", "Manduca sexta"),
    "Bmori": ("data-nontargets/Bmori-A0A8R2C8B0-AlphaFold.pdb", "A0A8R2C8B0", "Bombyx mori"),
    "Pxylostella": ("data-nontargets/Pxylostella-E2IGY7-AlphaFold.pdb", "E2IGY7", "Plutella xylostella"),
    "Slitura": ("data-nontargets/Slitura-B3F884-AlphaFold.pdb", "B3F884", "Spodoptera litura"),
    "Sfrugiperda": ("data-nontargets/Sfrugiperda-A0A089QDB3-AlphaFold.pdb", "A0A089QDB3", "Spodoptera frugiperda"),
    "Onubilalis": ("data-nontargets/Onubilalis-Q6R561-AlphaFold.pdb", "Q6R561", "Ostrinia nubilalis"),
    "Dsaccharalis": ("data-nontargets/Dsaccharalis-T1QDI0-AlphaFold.pdb", "T1QDI0", "Diatraea saccharalis"),
    "Hvirescens": ("data-nontargets/Hvirescens-I7D523-AlphaFold.pdb", "I7D523", "Heliothis virescens"),
    "Cincludens": ("data-nontargets/Cincludens-A0A9P0BRD5-AlphaFold.pdb", "A0A9P0BRD5", "Chrysodeixis includens"),
}

agent = StructureAgent("StructureAgent_multi", config, "outputs/structure_multi")

summary = {}
for tag, (pdb_path, acc, species) in STRUCTS.items():
    site = agent._analyze_single(pdb_path)
    out_dir = Path(f"outputs/structure_{tag.lower()}")
    out_dir.mkdir(parents=True, exist_ok=True)
    ok = site is not None and site.get("triad_resseqs") and all(site["triad_resseqs"].values())
    if ok:
        out = {
            "n_structures": 1,
            "consensus_center_xyz": site["center_xyz"],
            "hotspot_residues": site["hotspot_resseqs"],
            "individual_sites": [site],
            "note": (
                f"{species} (UniProt {acc}), estrutura AlphaFold DB real (v6). "
                "Deteccao real via StructureAgent._analyze_single, mesmo metodo validado "
                "nos 4 receptores primarios. Gerado 2026-07-18 para docking cross-species TOP-10 (R3)."
            ),
        }
        (out_dir / "binding_site.json").write_text(json.dumps(out, indent=2))
        summary[tag] = {"status": "OK", "acc": acc, "species": species, **site}
        print(f"{tag} ({species}, {acc}): triade={site['triad_resseqs']} S1_Asp={site['s1_asp_resseq']} centro={site['center_xyz']}")
    else:
        summary[tag] = {"status": "FALHOU_TRIADE", "acc": acc, "species": species, "raw": site}
        print(f"{tag} ({species}, {acc}): FALHOU deteccao de triade real -- {site}")

Path("outputs/structure_multi").mkdir(parents=True, exist_ok=True)
Path("outputs/structure_multi/summary.json").write_text(json.dumps(summary, indent=2))
print("\nResumo salvo em outputs/structure_multi/summary.json")

"""
run_md_top_candidates.py -- MD real (1 replica, 50ns producao) para o melhor candidato
(maior confidence_score do Boltz-2, ver data-b23-scoring/results/b23_boltz2_scores.json)
de cada uma das 7 especies da campanha B2.3.

Reusa MDAgent._run_gromacs() direto (mesmo protocolo validado em B0.5: pdb2gmx->editconf->
solvate->genion->minim->NVT->NPT->producao), forcefield amber99sb-ildn/tip3p (default do
projeto, config.yaml), pH real do intestino alcalino de Lepidoptera (gut_ph=10.0,
config.yaml, ver comentario la: baseado em Manduca sexta). Complexo de partida = predicao
COMPLETA do Boltz-2 (com side-chains reais, nao o backbone-only do RFdiffusion).

Uso: conda run -n protein_design_env python -m scripts.run_md_top_candidates
"""
import json
import logging
from pathlib import Path

import yaml

from scripts.agents.md_agent import MDAgent

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")

ROOT = Path(__file__).parent.parent
WORKDIR = ROOT / "outputs" / "md_top_candidates"

# Melhor candidato (maior confidence_score) por especie, campanha B2.7 (2026-09-28)
TOP_CANDIDATES = {
    "Sfrugiperda": {
        "sequence": "GIFDDIG",
        "backbone": "len7_design_9",
        "confidence_score": 0.9561083912849426,
        "pdb": "outputs/b23_boltz2_Sfrugiperda/boltz_results_Sfrugiperda/predictions/"
               "Sfrugiperda__len7_design_9__243/Sfrugiperda__len7_design_9__243_model_0.pdb",
    },
    "Slitura": {
        "sequence": "TGISGK",
        "backbone": "len6_design_6",
        "confidence_score": 0.9027059674263,
        "pdb": "outputs/b23_boltz2_Slitura/boltz_results_Slitura/predictions/"
               "Slitura__len6_design_6__226/Slitura__len6_design_6__226_model_0.pdb",
    },
    "Onubilalis": {
        "sequence": "NNNFGS",
        "backbone": "len6_design_0",
        "confidence_score": 0.9295428395271301,
        "pdb": "outputs/b23_boltz2_Onubilalis/boltz_results_Onubilalis/predictions/"
               "Onubilalis__len6_design_0__243/Onubilalis__len6_design_0__243_model_0.pdb",
    },
    "Dsaccharalis": {
        "sequence": "SSNINGK",
        "backbone": "len7_design_5",
        "confidence_score": 0.9541576504707336,
        "pdb": "outputs/b23_boltz2_Dsaccharalis/boltz_results_Dsaccharalis/predictions/"
               "Dsaccharalis__len7_design_5__361/Dsaccharalis__len7_design_5__361_model_0.pdb",
    },
    "Cincludens": {
        "sequence": "NNGGG",
        "backbone": "len5_design_2",
        "confidence_score": 0.9478680491447449,
        "pdb": "outputs/b23_boltz2_Cincludens/boltz_results_Cincludens/predictions/"
               "Cincludens__len5_design_2__150/Cincludens__len5_design_2__150_model_0.pdb",
    },
    "Hvirescens": {
        "sequence": "RPLNSATG",
        "backbone": "len8_design_5",
        "confidence_score": 0.9296861886978149,
        "pdb": "outputs/b23_boltz2_Hvirescens/boltz_results_Hvirescens/predictions/"
               "Hvirescens__len8_design_5__81/Hvirescens__len8_design_5__81_model_0.pdb",
    },
    "Pxylostella": {
        "sequence": "GGHTGA",
        "backbone": "len6_design_8",
        "confidence_score": 0.9313074350357056,
        "pdb": "outputs/b23_boltz2_Pxylostella/boltz_results_Pxylostella/predictions/"
               "Pxylostella__len6_design_8__331/Pxylostella__len6_design_8__331_model_0.pdb",
    },
}


def main():
    config = yaml.safe_load(open(ROOT / "config.yaml"))
    agent = MDAgent("MDAgent_top_candidates", config, str(WORKDIR))
    WORKDIR.mkdir(parents=True, exist_ok=True)

    ns = 50
    temp = config.get("md", {}).get("temperature", 300)

    summary_path = WORKDIR / "summary.json"
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}

    for species, meta in TOP_CANDIDATES.items():
        if summary.get(species, {}).get("status") == "done":
            print(f"[{species}] ja concluido, pulando")
            continue

        src = ROOT / meta["pdb"]
        if not src.exists():
            print(f"[{species}] PDB fonte nao encontrado: {src}, pulando")
            summary[species] = {"status": "sem_fonte_real"}
            summary_path.write_text(json.dumps(summary, indent=2))
            continue

        out_dir = WORKDIR / species
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"[{species}] iniciando MD 1x{ns}ns (seq={meta['sequence']}, "
              f"confidence_score={meta['confidence_score']:.4f})...")
        try:
            result = agent._run_gromacs(str(src), out_dir, ns, temp, meta["sequence"])
            summary[species] = {
                "status": "done",
                "sequence": meta["sequence"],
                "backbone": meta["backbone"],
                "confidence_score": meta["confidence_score"],
                "source_pdb": meta["pdb"],
                "ns": ns,
                **result,
            }
            print(f"[{species}] concluido: {result}")
        except Exception as e:
            print(f"[{species}] ERRO: {e}")
            summary[species] = {"status": "erro", "erro": str(e)}
        summary_path.write_text(json.dumps(summary, indent=2))

    print("MD_TOP_CANDIDATES_ALL_DONE")


if __name__ == "__main__":
    main()

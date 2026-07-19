"""deep_test_md_replicates.py — Réplicas reais de MD (n>=3) para o TOP-13 (Tabela 9j).

Reusa MDAgent._run_gromacs() diretamente (mesmo protocolo validado: pdb2gmx->editconf->solvate->
genion->minim->NVT->NPT->produção 10ns, gen_seed=-1 na NVT garante velocidades iniciais
independentes a cada chamada — replicas genuinamente independentes, não repetição determinística).

Parte do mesmo complex_clean.pdb JÁ EQUILIBRADO/validado da réplica 1 (não reconstrói via
PeptideBuilder do zero — lição da Fase 5/dissulfeto: reconstrução do zero não preserva geometria
real). Roda 2 réplicas adicionais por candidato (rep2, rep3) para chegar a n=3 total por
candidato (rep1 = resultado já existente em outputs/md/{seq ou forced_NN}/).

Uso: conda run -n protein_design_env python -m scripts.deep_test_md_replicates
(precisa ser `-m scripts.X`, não `python scripts/X.py` — o import
`from scripts.agents...` só resolve com a raiz do repo em sys.path, o que só
acontece com invocação de módulo; bug real corrigido 2026-07-18: ModuleNotFoundError)
"""
import json
import logging
from pathlib import Path

import yaml

from scripts.agents.md_agent import MDAgent

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")

CANDIDATES = [
    "SRTRR", "HRPRRPR", "RLREELKKAEEWLEKRRKEE", "SEEEVLAANEAYAAAHTAYN",
    "SALASIAAHQATFLAYLESK", "MGSLTAYLEAYAAENAAALA", "MGYLTAYHQALAAQNAALLA",
    "SARESIKKAYKTFLERYKKL", "VRYRR", "VRTRR", "VRRPR", "HRPRRSR", "HRPRRPK",
]

# Fonte do complex PDB já equilibrado/validado (réplica 1) para cada candidato.
SOURCE_PDB = {
    "RLREELKKAEEWLEKRRKEE": "outputs/md/forced_05/complex_clean.pdb",
    "SEEEVLAANEAYAAAHTAYN": "outputs/md/forced_00/complex_clean.pdb",
    "SALASIAAHQATFLAYLESK": "outputs/md/forced_04/complex_clean.pdb",
    "MGSLTAYLEAYAAENAAALA": "outputs/md/forced_03/complex_clean.pdb",
    "MGYLTAYHQALAAQNAALLA": "outputs/md/forced_01/complex_clean.pdb",
    "SARESIKKAYKTFLERYKKL": "outputs/md/complex_md_SARESIKKAY.pdb",  # pré-MD, sem complex_clean preservado
}
for seq in CANDIDATES:
    SOURCE_PDB.setdefault(seq, f"outputs/md/{seq}/complex_clean.pdb")

N_REPLICATES_TOTAL = 3  # rep1 já existe; roda rep2 e rep3
WORKDIR = Path("outputs/md_replicates")


def main():
    config = yaml.safe_load(open("config.yaml"))
    agent = MDAgent("MDAgent_replicates", config, str(WORKDIR))
    WORKDIR.mkdir(parents=True, exist_ok=True)

    ns = config.get("md", {}).get("simulation_ns", 10)
    temp = config.get("md", {}).get("temperature", 300)

    summary_path = WORKDIR / "replicates_summary.json"
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}

    for seq in CANDIDATES:
        src = Path(SOURCE_PDB[seq])
        if not src.exists():
            print(f"[{seq}] SEM complex_pdb fonte real ({src}), pulando")
            summary.setdefault(seq, {})["status"] = "sem_fonte_real"
            summary_path.write_text(json.dumps(summary, indent=2))
            continue

        seq_results = summary.get(seq, {"replicates": {}})
        for rep in range(2, N_REPLICATES_TOTAL + 1):
            rep_key = f"rep{rep}"
            if rep_key in seq_results.get("replicates", {}):
                print(f"[{seq}] {rep_key} já concluída, pulando")
                continue

            out_dir = WORKDIR / seq / rep_key
            out_dir.mkdir(parents=True, exist_ok=True)
            print(f"[{seq}] iniciando {rep_key} (fonte real: {src})...")
            try:
                result = agent._run_gromacs(str(src), out_dir, ns, temp, seq)
                seq_results.setdefault("replicates", {})[rep_key] = result
                print(f"[{seq}] {rep_key} REAL concluída: RMSD={result.get('rmsd_avg_nm')} "
                      f"Rg={result.get('rg_avg_nm')}")
            except Exception as e:
                print(f"[{seq}] {rep_key} FALHOU (erro real): {e}")
                seq_results.setdefault("replicates", {})[rep_key] = {"status": "falhou", "erro": str(e)[:500]}

            summary[seq] = seq_results
            summary_path.write_text(json.dumps(summary, indent=2, default=str))

    print(f"\nSalvo: {summary_path}")


if __name__ == "__main__":
    main()

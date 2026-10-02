"""
run_md_controls.py -- controles de MD com o MESMO protocolo dos candidatos (10 ns, CHARMM36, pH 10).

Motivo (auditoria de 01/10/2026): a triagem usa "ocupancia de S1 >= 70% a 5 A na 2a metade" sem nenhuma escala de
referencia. A analise dos complexos da calibracao (`analyze_md_controls.py`, 2 ns/AMBER) mostrou que as 5 iscas
embaralhadas disponiveis atingem ocupancia 1,00, com ancora Lys ou Arg -- ou seja, o criterio **nao discrimina**
naquele conjunto. Falta o teste no protocolo e no tamanho certos: iscas do MESMO tamanho e composicao dos
candidatos, partindo de uma predicao do Boltz-2 como eles.

Controle negativo pareado por tamanho: para cada candidato escolhido, usa a predicao do Boltz-2 de um dos seus
**controles embaralhados do E3** (mesma composicao, mesmo comprimento, mesmo receptor) e roda a mesma MD de 10 ns.
Se a isca tambem ficar em S1, a ocupancia nao sustenta afirmacao de ligacao para aquele candidato -- e isso precisa
estar no manuscrito.

Nao custa Boltz-2 extra: reaproveita `outputs/b23_boltz2_E3_{L,M}_s{seed}_{especie}/`, que o proprio pipeline gera.

Uso: python -m scripts.run_md_controls --front L --candidates Agemmatalis__r2 [Sfrugiperda__r1 ...] [--ns 10]
     [--workdir outputs/md10_controls_L] [--n-decoys 1]
"""
import argparse
import json
from pathlib import Path

import yaml

from scripts.agents.md_agent import MDAgent

ROOT = Path(__file__).parent.parent
RES = ROOT / "data-b23-scoring" / "results"


def decoy_predictions(front: str, species: str, parent_stem: str):
    """Predicoes do Boltz-2 dos controles embaralhados daquele candidato, melhor confianca primeiro."""
    man = json.loads((RES / f"manifest_E3_{front}.json").read_text())
    stems = [k for k, v in man.items() if v["parent"] == parent_stem]
    found = []
    for stem in stems:
        for seed in (1, 2, 3):
            d = ROOT / f"outputs/b23_boltz2_E3_{front}_s{seed}_{species}/boltz_results_{species}/predictions/{stem}"
            pdbs = sorted(d.glob("*_model_0.pdb"))
            if not pdbs:
                continue
            conf = None
            cj = sorted(d.glob("confidence_*_model_0.json"))
            if cj:
                try:
                    conf = json.loads(cj[0].read_text()).get("confidence_score")
                except Exception:  # noqa: BLE001
                    pass
            found.append({"stem": stem, "sequence": man[stem]["sequence"], "seed": seed,
                          "pdb": str(pdbs[0].relative_to(ROOT)), "confidence_score": conf or 0.0})
    found.sort(key=lambda r: -r["confidence_score"])
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--front", choices=["L", "M"], required=True)
    ap.add_argument("--candidates", nargs="+", required=True, help="chaves de top_candidates_<front>.json")
    ap.add_argument("--workdir", default=None)
    ap.add_argument("--ns", type=int, default=10)
    ap.add_argument("--n-decoys", type=int, default=1, help="quantos controles por candidato")
    a = ap.parse_args()

    workdir = ROOT / (a.workdir or f"outputs/md10_controls_{a.front}")
    workdir.mkdir(parents=True, exist_ok=True)
    top = json.loads((RES / f"top_candidates_{a.front}.json").read_text())["candidates"]
    config = yaml.safe_load(open(ROOT / "config.yaml"))
    # mesmo protocolo dos candidatos: pH do config, N-terminal carregado (default explicito)
    agent = MDAgent("MDAgent_controls", config, str(workdir))
    temp = config.get("md", {}).get("temperature", 300)

    summary_path = workdir / "summary.json"
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}
    for key in a.candidates:
        if key not in top:
            print(f"[{key}] nao esta em top_candidates_{a.front}.json, pulando")
            continue
        c = top[key]
        sp = c.get("species", key.split("__")[0])
        parent = Path(c["pdb"]).parent.name
        decoys = decoy_predictions(a.front, sp, parent)
        if not decoys:
            print(f"[{key}] nenhuma predicao de controle encontrada (o E3 ja rodou?)")
            continue
        for d in decoys[:a.n_decoys]:
            ck = f"{key}__ctrl_{d['stem'].split('__')[-1]}"
            if summary.get(ck, {}).get("status") == "done":
                print(f"[{ck}] ja concluido, pulando")
                continue
            out_dir = workdir / ck
            out_dir.mkdir(parents=True, exist_ok=True)
            print(f"[{ck}] controle embaralhado de {c['sequence']} -> {d['sequence']} "
                  f"(conf {d['confidence_score']:.3f}); MD 1x{a.ns}ns...", flush=True)
            try:
                r = agent._run_gromacs(str(ROOT / d["pdb"]), out_dir, a.ns, temp, d["sequence"],
                                       cyclic=a.front == "M")
                summary[ck] = {"status": "erro" if r.get("error") else "done", "sequence": d["sequence"],
                               "control_of": key, "parent_sequence": c["sequence"], "parent_stem": parent,
                               "species": sp, "backbone": c.get("backbone"),
                               "confidence_score": d["confidence_score"], "source_pdb": d["pdb"],
                               "ns": a.ns, "cyclic": a.front == "M", "front": a.front, "role": "decoy_control", **r}
                print(f"[{ck}] concluido: {r}", flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"[{ck}] ERRO: {e}")
                summary[ck] = {"status": "erro", "erro": str(e), "control_of": key}
            summary_path.write_text(json.dumps(summary, indent=2))
    print("MD_CONTROLS_ALL_DONE")


if __name__ == "__main__":
    main()

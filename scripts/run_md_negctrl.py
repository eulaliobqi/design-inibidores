"""
run_md_negctrl.py -- controle negativo por troca da ancora (Secao 3.9 do manuscrito, regra declarada antes das corridas).

Para cada candidato elegivel, o residuo-ancora do peptideo e' trocado por Asp (ionizado em pH 10, repelido pelo Asp189 do S1)
e por Leu (nao cognato, apolar), MANTENDO a pose inicial (mesmas coordenadas do esqueleto, cadeia lateral reconstruida
com PDBFixer), e a MD de 10 ns e' rodada no mesmo protocolo dos candidatos. Leitura: distancia ancora-Asp189 e perda da
ponte salina (`analyze_md_top_candidates`, mesmos criterios). NAO usa MM-GBSA (nao separou inibidores de iscas, Secao 3.3).

Regra de decisao (fixada antes): se nenhuma das duas variantes sai de S1 em 10 ns, ou se os controles embaralhados nao se
separam dos candidatos, o controle nao traz informacao e e' retirado das analises, das camadas e das figuras.

Elegibilidade (`compare_controls.py`, definida aqui antes de ver os resultados dos controles): ocupancia na 2a metade >= 0,70
e >= a do proprio controle embaralhado.

Uso: python -m scripts.run_md_negctrl --front L --candidates Onubilalis__r2 [...] [--ns 10] [--dry-run]
     python -m scripts.run_md_negctrl --front L --from-decision outputs/controls_decision.json
"""
import argparse
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
RES = ROOT / "data-b23-scoring" / "results"
VARIANTS = {"ASP": "D", "LEU": "L"}
THREE = {"G": "GLY", "A": "ALA", "S": "SER", "P": "PRO", "V": "VAL", "T": "THR", "C": "CYS", "L": "LEU", "I": "ILE",
         "N": "ASN", "D": "ASP", "Q": "GLN", "K": "LYS", "E": "GLU", "M": "MET", "H": "HIS", "F": "PHE", "R": "ARG",
         "Y": "TYR", "W": "TRP"}


def mutate(src_pdb: Path, out_pdb: Path, pep_chain: str, resid: int, old_aa: str, new3: str, cyclic: bool) -> dict:
    """Troca um residuo do peptideo mantendo as coordenadas do esqueleto; devolve verificacoes."""
    from openmm.app import PDBFile
    from pdbfixer import PDBFixer

    fx = PDBFixer(filename=str(src_pdb))
    n_before = {c.id: sum(1 for _ in c.atoms()) for c in fx.topology.chains()}
    had_oxt = {c.id for c in fx.topology.chains() for r in c.residues() for at in r.atoms() if at.name == "OXT"}
    import numpy as np
    from openmm import unit
    xyz0 = np.array(fx.positions.value_in_unit(unit.nanometer))
    pos0 = {(at.residue.chain.id, at.residue.index, at.name): xyz0[at.index] for at in fx.topology.atoms()}
    fx.applyMutations([f"{THREE[old_aa]}-{resid}-{new3}"], pep_chain)
    fx.missingResidues = {}
    fx.findMissingAtoms()
    fx.addMissingAtoms()
    # O PDBFixer acrescenta OXT a todo C-terminal; os PDBs do Boltz-2 nao o tem e o protocolo dos candidatos parte deles
    # como estao (pdb2gmx trata os terminais; no macrociclo o fechamento cabeca-cauda nao tem OXT). Remove os OXT novos.
    from openmm.app import Modeller
    m = Modeller(fx.topology, fx.positions)
    m.delete([at for at in m.topology.atoms() if at.name == "OXT" and at.residue.chain.id not in had_oxt])
    fx.topology, fx.positions = m.topology, m.positions
    n_after = {c.id: sum(1 for _ in c.atoms()) for c in fx.topology.chains()}
    chk = {"atoms_before": n_before, "atoms_after": n_after}
    others = [k for k in n_before if k != pep_chain]
    chk["receptor_unchanged"] = all(n_before[k] == n_after.get(k) for k in others)
    xyz1 = np.array(fx.positions.value_in_unit(unit.nanometer))
    moved = [1 for at in fx.topology.atoms() if at.name in ("N", "CA", "C", "O")
             and (at.residue.chain.id, at.residue.index, at.name) in pos0
             and np.abs(xyz1[at.index] - pos0[(at.residue.chain.id, at.residue.index, at.name)]).max() > 1e-4]
    chk["backbone_moved"] = len(moved)
    with open(out_pdb, "w") as fh:
        PDBFile.writeFile(fx.topology, fx.positions, fh, keepIds=True)
    return chk


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--front", choices=["L", "M"], required=True)
    ap.add_argument("--candidates", nargs="*", default=[])
    ap.add_argument("--from-decision", default=None, help="outputs/controls_decision.json (candidatos elegiveis)")
    ap.add_argument("--ns", type=int, default=10)
    ap.add_argument("--workdir", default=None)
    ap.add_argument("--dry-run", action="store_true", help="so monta os PDBs mutados e as verificacoes")
    a = ap.parse_args()

    cands = list(a.candidates)
    if a.from_decision:
        dec = json.loads(Path(a.from_decision).read_text())
        cands += [k for k, v in dec.get(a.front, {}).items() if v.get("eligible_negctrl")]
    if not cands:
        print(f"[negctrl:{a.front}] nenhum candidato elegivel; nada a fazer")
        print("MD_NEGCTRL_ALL_DONE")
        return

    workdir = ROOT / (a.workdir or f"outputs/md10_negctrl_{a.front}")
    workdir.mkdir(parents=True, exist_ok=True)
    cand_summary = json.loads((ROOT / f"outputs/md10_{a.front}/summary.json").read_text())
    cand_analysis = json.loads((ROOT / f"outputs/md10_{a.front}/analysis_summary.json").read_text())
    summary_path = workdir / "summary.json"
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}
    agent = temp = None
    if not a.dry_run:
        from scripts.agents.md_agent import MDAgent
        config = yaml.safe_load(open(ROOT / "config.yaml"))
        agent = MDAgent("MDAgent_negctrl", config, str(workdir))
        temp = config.get("md", {}).get("temperature", 300)

    for key in cands:
        cs, ca = cand_summary[key], cand_analysis[key]
        seq, idx, old = cs["sequence"], int(ca["anchor_idx"]), ca["anchor_aa"]
        cyclic = a.front == "M"
        for new3, new1 in VARIANTS.items():
            if old == new1:
                print(f"[{key}] ancora ja e' {new3}; variante pulada")
                continue
            ck = f"{key}__neg_{new3}"
            if summary.get(ck, {}).get("status") == "done":
                print(f"[{ck}] ja concluido, pulando")
                continue
            out_dir = workdir / ck
            out_dir.mkdir(parents=True, exist_ok=True)
            new_seq = seq[:idx] + new1 + seq[idx + 1:]
            pdb = out_dir / "start_mutated.pdb"
            chk = mutate(ROOT / cs["source_pdb"], pdb, "B", idx + 1, old, new3, cyclic)
            print(f"[{ck}] {seq} -> {new_seq} (ancora {old}{idx + 1} -> {new1}); verificacoes: {chk}", flush=True)
            if not chk["receptor_unchanged"]:
                summary[ck] = {"status": "erro", "erro": "receptor alterado pelo PDBFixer", **chk}
                summary_path.write_text(json.dumps(summary, indent=2))
                continue
            if a.dry_run:
                continue
            try:
                r = agent._run_gromacs(str(pdb), out_dir, a.ns, temp, new_seq, cyclic=cyclic)
                summary[ck] = {"status": "erro" if r.get("error") else "done", "sequence": new_seq,
                               "control_of": key, "parent_sequence": seq, "anchor_idx": idx, "anchor_from": old,
                               "anchor_to": new1, "species": cs.get("species", key.split("__")[0]),
                               "source_pdb": cs["source_pdb"], "ns": a.ns, "cyclic": cyclic, "front": a.front,
                               "role": "negative_control_anchor_swap", **r}
                print(f"[{ck}] concluido: {r}", flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"[{ck}] ERRO: {e}", flush=True)
                summary[ck] = {"status": "erro", "erro": str(e), "control_of": key}
            summary_path.write_text(json.dumps(summary, indent=2))
    print("MD_NEGCTRL_ALL_DONE")


if __name__ == "__main__":
    main()

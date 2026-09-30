"""
recompute_b05_md_metrics.py -- recalcula, com PBC tratado corretamente, as metricas de MD curta
(2 ns) da calibracao B0.5 (22 sistemas: 2 receptores x [6 inibidores reais + 5 decoys]).

Motivo (correcao 2026-09-30): o "RMSD do complexo inteiro" reportado em B0.5 (5/10 pares
corretos, ~acaso) foi calculado por `gmx rms` no md.xtc BRUTO. Em MD de sistema receptor+ligante
(moleculas separadas), o mdrun escreve as coordenadas empacotadas na caixa e o ligante pode cair
noutra imagem periodica; o RMSD infla por salto de imagem, nao por instabilidade (verificado no
top-candidato de C. includens: distancia bruta entre centros de massa ate 95 A, mediana 44,7 A,
caixa de 116 A, enquanto o peptideo estava em contato o tempo todo). O resultado 5/10 nao
pode, portanto, ser lido como propriedade da metrica. Este script repete a avaliacao com uma
metrica de interface bem definida:

  - RMSD do backbone do LIGANTE apos superposicao nos C-alfa do RECEPTOR (referencia = 1o quadro
    da producao), com o ligante desempacotado por imagem minima -> estabilidade da pose
  - numero medio de residuos do receptor a <4.5 A de qualquer atomo pesado do ligante (area de
    contato), e fracao de quadros com contato
  - distancia entre centros de massa receptor-ligante (deteccao de dissociacao)

Metricas e direcao esperada declaradas ANTES de ver o resultado: real deve ter RMSD do ligante
MENOR e contato MAIOR que o decoy pareado. Sao 10 pares (5 inibidores x 2 receptores); os dois
receptores compartilham o mesmo decoy, entao os pares NAO sao independentes.

Uso (servidor): ~/miniforge3/envs/protein_design_env/bin/python -m scripts.recompute_b05_md_metrics
"""
import json
from pathlib import Path

import MDAnalysis as mda
import numpy as np
from MDAnalysis.analysis import align
from MDAnalysis.lib.distances import capped_distance, minimize_vectors

ROOT = Path(__file__).parent.parent
MD_CALIB = ROOT / "data-calibration-b05" / "md_calib"
OUT = ROOT / "data-calibration-b05" / "md_metrics_pbc_corrected.json"
PAIRS = ["SFTI1", "BBI", "BPTI", "EcTI", "SKTI"]
RECEPTORS = ["bovine", "sfrug"]


def unwrap_group(pos, box):
    return pos[0] + minimize_vectors(pos - pos[0], box)


def analyze_system(tag: str) -> dict:
    run = MD_CALIB / tag
    xtc = run / "md_pbc.xtc"
    if not xtc.exists():
        return {"error": f"md_pbc.xtc ausente em {run}"}
    u = mda.Universe(str(run / "md.tpr"), str(xtc))
    segs = u.select_atoms("protein").segments
    if len(segs) < 2:
        return {"error": f"esperado >=2 segmentos de proteina, achei {len(segs)}"}
    rec = segs[0].atoms.select_atoms("protein")
    lig = sum((s.atoms for s in segs[1:]), segs[0].atoms[:0]).select_atoms("protein")
    rec_ca = rec.select_atoms("name CA")
    lig_bb = lig.select_atoms("backbone")
    lig_heavy = lig.select_atoms("not name H*")
    rec_heavy = rec.select_atoms("not name H*")

    u.trajectory[0]
    ref_rec = rec_ca.positions.copy()
    ref_c = ref_rec.mean(axis=0)
    box0 = u.trajectory.ts.dimensions
    ref_lig = unwrap_group(lig_bb.positions.copy(), box0) - ref_c

    rmsd, n_res_contact, com = [], [], []
    for ts in u.trajectory:
        box = ts.dimensions
        com.append(float(np.linalg.norm(rec.center_of_mass() - lig.center_of_mass())))
        rot, _ = align.rotation_matrix(rec_ca.positions - rec_ca.positions.mean(axis=0),
                                       ref_rec - ref_c)
        lp = unwrap_group(lig_bb.positions, box)
        # traz o ligante para a imagem mais proxima do receptor
        off = lp.mean(axis=0) - rec.center_of_geometry()
        lp = lp + (minimize_vectors(off[None, :], box)[0] - off)
        moved = (lp - rec_ca.positions.mean(axis=0)) @ rot.T
        rmsd.append(float(np.sqrt(np.mean(np.sum((moved - ref_lig) ** 2, axis=1)))) / 10.0)
        pairs = capped_distance(lig_heavy.positions, rec_heavy.positions, 4.5, box=box,
                                return_distances=False)
        res_idx = {rec_heavy.resindices[j] for j in pairs[:, 1]} if len(pairs) else set()
        n_res_contact.append(len(res_idx))

    n = len(rmsd)
    last = slice(int(n * 2 / 3), n)   # ultimo terco (mesma janela do MM-PBSA)
    return {
        "n_frames": n, "n_ligand_residues": int(len(lig.residues)),
        "ligand_rmsd_nm_mean": round(float(np.mean(rmsd)), 3),
        "ligand_rmsd_nm_last_third": round(float(np.mean(rmsd[last])), 3),
        "receptor_residues_in_contact_mean": round(float(np.mean(n_res_contact)), 1),
        "contact_frac": round(float(np.mean(np.array(n_res_contact) > 0)), 3),
        "com_dist_A_median": round(float(np.median(com)), 1),
        "com_dist_A_max": round(float(np.max(com)), 1),
    }


def main():
    res = {}
    for rec in RECEPTORS:
        for inh in PAIRS + ["ApTI"]:
            for suffix in ("", "_decoy"):
                if inh == "ApTI" and suffix:
                    continue
                tag = f"{rec}__{inh}{suffix}"
                try:
                    res[tag] = analyze_system(tag)
                except Exception as e:  # noqa: BLE001
                    res[tag] = {"error": f"{type(e).__name__}: {e}"}
                print(tag, json.dumps(res[tag]), flush=True)

    # Separacao real vs decoy (direcao declarada acima)
    verdicts = {}
    for rec in RECEPTORS:
        for inh in PAIRS:
            r, d = res.get(f"{rec}__{inh}", {}), res.get(f"{rec}__{inh}_decoy", {})
            if "error" in r or "error" in d or not r or not d:
                verdicts[f"{rec}__{inh}"] = "sem_dado"
                continue
            verdicts[f"{rec}__{inh}"] = {
                "rmsd_ok": r["ligand_rmsd_nm_last_third"] < d["ligand_rmsd_nm_last_third"],
                "contact_ok": r["receptor_residues_in_contact_mean"]
                > d["receptor_residues_in_contact_mean"],
            }
    n_rmsd = sum(1 for v in verdicts.values() if isinstance(v, dict) and v["rmsd_ok"])
    n_cont = sum(1 for v in verdicts.values() if isinstance(v, dict) and v["contact_ok"])
    n_valid = sum(1 for v in verdicts.values() if isinstance(v, dict))
    summary = {"pairs_valid": n_valid, "rmsd_real_lower_than_decoy": n_rmsd,
               "contact_real_higher_than_decoy": n_cont}
    OUT.write_text(json.dumps({"summary": summary, "verdicts": verdicts, "systems": res},
                              indent=2))
    print("RESUMO", json.dumps(summary))


if __name__ == "__main__":
    main()

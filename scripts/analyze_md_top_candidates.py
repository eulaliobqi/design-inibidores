"""
analyze_md_top_candidates.py -- analise das MDs de 50 ns (1 replica) do melhor candidato
Boltz-2 por especie (outputs/md_top_candidates/{species}/, ver run_md_top_candidates.py).

Metricas por especie (todas de trajetoria real, nenhuma predicao):
  - ocupancia da ancora no Asp-S1 (residuo do peptideo mais proximo do carboxilato do Asp189
    do template 2PTC, mapeado por receptor em data-lepidoptera-panel/subsites_by_receptor.json)
    a 4/5/6 A, global e por metade (0-25 / 25-50 ns) -> convergencia intra-corrida
  - contato do peptideo com a Ser catalitica (OG) e His do triade (NE2) a 4.5 A
  - RMSD local do peptideo (CA, superposicao so nos CA do receptor) medio e nos ultimos 10 ns
  - fracao de frames com qualquer contato peptideo-receptor <4.5 A (dissociacao)
  - distancia peptideo-Asp-S1 no inicio (0-2 ns) vs fim (48-50 ns)

Robustez a PBC (correcao 2026-09-30): a trajetoria de entrada passa por `trjconv -pbc mol -center`,
mas a cadeia do peptideo (molecula separada) ainda pode cair noutra imagem periodica do receptor
em alguns quadros (ex.: D. saccharalis, 3/501 quadros a ~97 A). Por isso, em cada quadro os
atomos do peptideo sao (i) tornados inteiros por imagem minima em relacao ao primeiro atomo e
(ii) transladados para a imagem mais proxima do carboxilato do Asp-S1 antes do calculo de RMSD.
As distancias usam distance_array(..., box=) (imagem minima) e nao dependem disso.

Uso (servidor):
  ~/miniforge3/envs/protein_design_env/bin/python -m scripts.analyze_md_top_candidates       [--md-dir outputs/md_top_candidates] [ESPECIE ...]
"""
import json
import subprocess
import sys
from pathlib import Path

import MDAnalysis as mda
import numpy as np
from MDAnalysis.analysis import align
from MDAnalysis.lib.distances import distance_array, minimize_vectors

GMX = "/home/eulalio/miniforge3/envs/md-gromacs/bin/gmx_mpi"
ROOT = Path(__file__).parent.parent
MD_DIR = ROOT / "outputs" / "md_top_candidates"   # sobrescrito por --md-dir
PANEL = ROOT / "data-lepidoptera-panel" / "subsites_by_receptor.json"
DT_PS = 100  # subamostra: 500 frames em 50 ns


def receptor_residues(species: str) -> dict:
    t = json.loads(PANEL.read_text())["receptors"][species]["templates"]["2PTC_BPTI"]
    m = {}
    for grp in t["subsites"].values():
        for x in grp:
            m[x["ref"]] = x["receptor"]
    m["SER195"] = t["catalytic_ser_receptor"]["receptor"]
    return m


def resnum(name: str) -> int:
    return int("".join(c for c in name if c.isdigit()))


def pbc_traj(sp_dir: Path) -> Path:
    out = sp_dir / "md_pbc_sub.xtc"
    if out.exists() and out.stat().st_size > 1000:
        return out
    cmd = (f"printf '1\\n0\\n' | {GMX} trjconv -s {sp_dir/'md.tpr'} -f {sp_dir/'md.xtc'} "
           f"-o {out} -pbc mol -center -dt {DT_PS}")
    subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=3600)
    if not out.exists() or out.stat().st_size < 1000:
        raise RuntimeError(f"trjconv falhou em {sp_dir}")
    return out


def analyze(species: str, seq: str) -> dict:
    sp_dir = MD_DIR / species
    res_map = receptor_residues(species)
    u = mda.Universe(str(sp_dir / "md.tpr"), str(pbc_traj(sp_dir)))
    prot = u.select_atoms("protein")
    n_rec = len(prot.residues) - len(seq)
    rec, pep = prot.residues[:n_rec], prot.residues[n_rec:]
    if "".join(mda.lib.util.convert_aa_code(r.resname) for r in pep) != seq:
        return {"error": "sequencia do peptideo na trajetoria != sequencia esperada"}

    def get(refname, atoms, expect_resname):
        num = resnum(res_map[refname])
        sel = rec[rec.resids == num]
        if len(sel) != 1 or not sel[0].resname.startswith(expect_resname):
            found = sel[0].resname if len(sel) else None
            raise ValueError(f"{refname}->{res_map[refname]}: resid {num} = {found}")
        return sel.atoms.select_atoms(f"name {atoms}")

    asp = get("ASP189", "OD1 OD2", "AS")
    ser = get("SER195", "OG", "SER")
    his = get("HIS57", "NE2", "HI")

    def unwrap_peptide(pos, anchor, box):
        """Torna o peptideo inteiro (imagem minima relativa ao 1o atomo) e o traz para a imagem
        mais proxima de `anchor` (centroide do carboxilato do Asp-S1)."""
        whole = pos[0] + minimize_vectors(pos - pos[0], box)
        offset = whole.mean(axis=0) - anchor
        shift = minimize_vectors(offset[None, :], box)[0] - offset
        return whole + shift

    rec_ca = rec.atoms.select_atoms("name CA")
    ref_rec = rec_ca.positions.copy()
    ref_c = ref_rec.mean(axis=0)
    pep_ca = pep.atoms.select_atoms("name CA")
    u.trajectory[0]
    ref_pep = unwrap_peptide(pep_ca.positions.copy(), asp.positions.mean(axis=0),
                             u.trajectory.ts.dimensions) - ref_c
    pep_heavy = [r.atoms.select_atoms("not name H*") for r in pep]
    pep_all_heavy = pep.atoms.select_atoms("not name H*")
    rec_heavy = rec.atoms.select_atoms("not name H*")

    d_res, t_ns, rmsd_loc, contact_any, d_ser, d_his, d_com = [], [], [], [], [], [], []
    for ts in u.trajectory:
        box = ts.dimensions
        t_ns.append(ts.time / 1000.0)
        d_com.append(float(np.linalg.norm(rec.atoms.center_of_mass() - pep.atoms.center_of_mass())))
        d_res.append([distance_array(h.positions, asp.positions, box=box).min() for h in pep_heavy])
        d_ser.append(distance_array(pep_all_heavy.positions, ser.positions, box=box).min())
        d_his.append(distance_array(pep_all_heavy.positions, his.positions, box=box).min())
        contact_any.append(bool((distance_array(pep_all_heavy.positions, rec_heavy.positions,
                                                 box=box) < 4.5).any()))
        rot, _ = align.rotation_matrix(rec_ca.positions - rec_ca.positions.mean(axis=0),
                                       ref_rec - ref_c)
        pep_pos = unwrap_peptide(pep_ca.positions, asp.positions.mean(axis=0), box)
        moved = (pep_pos - rec_ca.positions.mean(axis=0)) @ rot.T
        rmsd_loc.append(float(np.sqrt(np.mean(np.sum((moved - ref_pep) ** 2, axis=1)))) / 10.0)

    d_res, t_ns = np.array(d_res), np.array(t_ns)
    anchor = int(d_res.mean(axis=0).argmin())
    da = d_res[:, anchor]
    half = t_ns < t_ns.max() / 2
    late, early = t_ns >= t_ns.max() - 10, t_ns <= 2
    rmsd_loc = np.array(rmsd_loc)
    out = {
        "n_frames": int(len(t_ns)), "receptor_residues": int(n_rec),
        "s1_asp": res_map["ASP189"], "anchor_idx": anchor, "anchor_aa": seq[anchor],
        "d_anchor_asp_mean_A": round(float(da.mean()), 2),
        "d_anchor_asp_ini_A": round(float(da[early].mean()), 2),
        "d_anchor_asp_fim_A": round(float(da[late].mean()), 2),
        "com_dist_pep_rec_A_median": round(float(np.median(d_com)), 1),
        "n_frames_image_jump_gt30A": int((np.array(d_com) > 30).sum()),
        "peptide_rmsd_local_nm_mean": round(float(rmsd_loc.mean()), 3),
        "peptide_rmsd_local_nm_last10ns": round(float(rmsd_loc[late].mean()), 3),
        "contact_any_frac_4.5A": round(float(np.mean(contact_any)), 3),
        "ser195_contact_frac_4.5A": round(float((np.array(d_ser) < 4.5).mean()), 3),
        "his57_contact_frac_4.5A": round(float((np.array(d_his) < 4.5).mean()), 3),
    }
    for c in (4, 5, 6):
        out[f"occ_{c}A"] = round(float((da < c).mean()), 3)
        out[f"occ_{c}A_h1"] = round(float((da[half] < c).mean()), 3)
        out[f"occ_{c}A_h2"] = round(float((da[~half] < c).mean()), 3)
    return out


def main():
    global MD_DIR
    args = sys.argv[1:]
    if args[:1] == ["--md-dir"]:
        MD_DIR = ROOT / args[1]
        args = args[2:]
    out_file = MD_DIR / "analysis_summary.json"
    summary = json.loads((MD_DIR / "summary.json").read_text())
    species = args or list(summary)
    res = json.loads(out_file.read_text()) if out_file.exists() else {}
    for sp in species:
        seq = summary[sp]["sequence"]
        try:
            res[sp] = {"sequence": seq, **analyze(sp, seq)}
        except Exception as e:  # noqa: BLE001 - reporta por especie, nao aborta o lote
            res[sp] = {"sequence": seq, "error": f"{type(e).__name__}: {e}"}
        print(sp, json.dumps(res[sp]), flush=True)
        out_file.write_text(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()

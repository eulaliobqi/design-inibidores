"""
deliver_md_long.py -- E9 do plano v3. Reune, por frente (L = linear, M = macrociclo), QC de pose (E4),
triagem de MD de 10 ns (E7), Delta pareado contra controles embaralhados (E3) e produz:
  outputs/delivery_md_long/report.md         tabela de todos os candidatos com cada criterio
  outputs/delivery_md_long/report.json
  outputs/delivery_md_long/{chave}/receptor.pdb, ligand.pdb   (complexo Boltz-2 de partida separado por cadeia)
  outputs/delivery_md_long/samplesheet_{L,M}.csv              entrada do pipeline Milena-MD (MD longa)
Criterios pre-registrados (plano v3): QC de pose aprovado; passes_screen da MD (ocupancia do S1 >=70%
a 5 A na 2a metade, ancora igual nas duas metades, anel integro no macrociclo); Delta pareado > 0.
Um candidato entra na lista se cumpre todos; os demais ficam no relatorio com o criterio que falhou.
Nota: a topologia cíclica do Milena-MD (CHARMM36) nao existe; a MD longa do macrociclo deve usar
scripts/build_system_charmm.py (CHARMM36), nao o samplesheet do Milena-MD.
"""
import json
from pathlib import Path

from analyze_md_top_candidates import receptor_residues, resnum

ROOT = Path(__file__).parent.parent
RES = ROOT / "data-b23-scoring" / "results"
OUT = ROOT / "outputs" / "delivery_md_long"


def load(p):
    p = Path(p)
    return json.loads(p.read_text()) if p.exists() else {}


def split_complex(pdb: Path, dst: Path):
    dst.mkdir(parents=True, exist_ok=True)
    rec, lig = [], []
    for l in pdb.read_text().splitlines():
        if l.startswith(("ATOM", "HETATM")):
            (rec if l[21] == "A" else lig).append(l)
    (dst / "receptor.pdb").write_text("\n".join(rec + ["TER", "END"]) + "\n")
    (dst / "ligand.pdb").write_text("\n".join(lig + ["TER", "END"]) + "\n")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report, md_lines = {}, ["# Lista de entrega para MD longa\n"]
    for front, name in (("L", "linear"), ("M", "macrociclo")):
        top = load(RES / f"top_candidates_{front}.json").get("candidates", {})
        qc = load(ROOT / f"outputs/pose_qc_{front}.json")
        ana = load(ROOT / f"outputs/md10_{front}/analysis_summary.json")
        delta = {r["stem"]: r for v in load(RES / f"delta_paired_{front}.json").values() for r in v}
        rows, sheet = [], ["sample_id,receptor,ligand,triad_1,triad_2,triad_3,triad_4"]
        for key, c in top.items():
            sp = c.get("species", key.split("__")[0])
            q, a = qc.get(key, {}), ana.get(key, {})
            stem = Path(c["pdb"]).parent.name
            d = delta.get(stem, {}).get("delta")
            crit = {"qc_pose": q.get("qc_pass"), "md10ns_screen": a.get("passes_screen"),
                    "delta_pareado_gt0": (d > 0) if d is not None else None}
            ok = all(v is True for v in crit.values())
            rows.append({"key": key, "sequence": c["sequence"], "confidence": round(c["confidence_score"], 3),
                         "delta": None if d is None else round(d, 3),
                         "occ5A_h2": a.get("occ_5A_h2"), "anchor_same": a.get("anchor_same_in_halves"),
                         "ring_intact": a.get("ring_intact"), "criteria": crit, "deliver": ok})
            if ok:
                dst = OUT / key
                split_complex(ROOT / c["pdb"], dst)
                rm = receptor_residues(sp)
                sheet.append(f"{key.lower()},{dst/'receptor.pdb'},{dst/'ligand.pdb'},"
                             f"{resnum(rm['HIS57'])},,{resnum(rm['SER195'])},{resnum(rm['ASP189'])}")
        report[front] = rows
        (OUT / f"samplesheet_{front}.csv").write_text("\n".join(sheet) + "\n")
        md_lines += [f"\n## Frente {front} ({name})\n",
                     "| chave | sequencia | conf. | Delta | ocup.5A (2a metade) | ancora igual | anel | QC | MD 10 ns | Delta>0 | entrega |",
                     "|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            cr = r["criteria"]
            md_lines.append(f"| {r['key']} | {r['sequence']} | {r['confidence']} | {r['delta']} | {r['occ5A_h2']} | "
                            f"{r['anchor_same']} | {r['ring_intact']} | {cr['qc_pose']} | {cr['md10ns_screen']} | "
                            f"{cr['delta_pareado_gt0']} | {'SIM' if r['deliver'] else 'nao'} |")
    (OUT / "report.json").write_text(json.dumps(report, indent=2))
    (OUT / "report.md").write_text("\n".join(md_lines) + "\n")
    n = {f: sum(r["deliver"] for r in rows) for f, rows in report.items()}
    print("entregues:", n, "->", OUT)


if __name__ == "__main__":
    main()

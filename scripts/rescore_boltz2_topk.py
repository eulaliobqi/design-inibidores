"""
rescore_boltz2_topk.py -- E2/E3 do plano v3 (docs/PLANO_LINEAR_2026-09-30.md).

E2: re-pontua o top-k (por especie e frente) da triagem E1 com o protocolo robusto do grupo
    (5 amostras de difusao x N sementes, --use_potentials, 200 passos). Escore = media de todas as
    predicoes; o PDB de partida da MD e' a melhor amostra individual.
pick-qc: troca o PDB inicial pela melhor amostra que passa no QC de pose (pos-E2).
E3: controles pareados -- `n_decoys` embaralhamentos de cada candidato (mesma composicao, mesmo
    comprimento, semente fixa por sequencia), mesmo protocolo; Delta = escore(candidato) - media(controles).
    O Boltz-2 foi validado real-vs-decoy apenas em pares (calibracao B0.5): por isso Delta, nao o valor absoluto.

Subcomandos:
  prepare --front L|M [--k 10] [--n-decoys 3]   escreve os yaml de E2 e E3 + manifestos
  collect --front L|M --tag E2|E3 --seeds 1 2 3  consolida confianca por candidato
  delta   --front L|M                            junta E2 e E3 (Delta pareado)
O `boltz predict` e' chamado pelo script de pipeline (um diretorio de saida por semente).
"""
import argparse
import hashlib
import json
import random
import statistics
from pathlib import Path

from score_boltz2_b23 import get_receptor_sequence

ROOT = Path(__file__).parent.parent
RES = ROOT / "data-b23-scoring" / "results"


def e1_paths(front):
    return (RES / f"b23_boltz2_{front}_scores.json",
            ROOT / ("outputs/b23_cleavage_linear_hard.json" if front == "L"
                    else "outputs/b23_cleavage_circular_hard.json"))


def yaml_text(receptor_seq, msa, pep, cyclic):
    cyc = "      cyclic: true\n" if cyclic else ""
    return ("version: 1\nsequences:\n  - protein:\n      id: A\n"
            f"      sequence: {receptor_seq}\n      msa: {msa}\n  - protein:\n      id: B\n"
            f"      sequence: {pep}\n{cyc}      msa: empty\n")


def shuffled(seq, j):
    if len(set(seq)) == 1:
        return None
    rng = random.Random(int(hashlib.md5(f"{seq}|{j}".encode()).hexdigest()[:8], 16))
    for _ in range(50):
        s = list(seq)
        rng.shuffle(s)
        s = "".join(s)
        if s != seq:
            return s
    return None


def prepare(a):
    sc_path, clv_path = e1_paths(a.front)
    scores = json.loads(sc_path.read_text())
    clv = json.loads(clv_path.read_text())
    cyclic = a.front == "M"
    for tag in ("E2", "E3"):
        (RES / f"boltz_yaml_{tag}_{a.front}").mkdir(parents=True, exist_ok=True)
    man = {"E2": {}, "E3": {}}
    for sp, entry in clv["by_species"].items():
        ok = {(r["backbone"], r["sequence"]) for r in entry["results"] if r["verdict"] == "RESISTENTE"}
        ranked, seen = [], set()
        for c in sorted((c for c in scores.get(sp, []) if (c["backbone"], c["sequence"]) in ok),
                        key=lambda c: c["confidence_score"], reverse=True):
            if c["sequence"] not in seen:
                seen.add(c["sequence"])
                ranked.append(c)
            if len(ranked) == a.k:
                break
        rseq = get_receptor_sequence(sp)
        msa = (ROOT / "data-b23-scoring/msa_cache" / f"receptor_{sp}.csv").resolve()
        for rank, c in enumerate(ranked, start=1):
            stem = f"{sp}__{c['backbone']}__{rank}"
            d2 = RES / f"boltz_yaml_E2_{a.front}" / sp
            d2.mkdir(parents=True, exist_ok=True)
            (d2 / f"{stem}.yaml").write_text(yaml_text(rseq, msa, c["sequence"], cyclic))
            man["E2"][stem] = {"species": sp, "backbone": c["backbone"], "sequence": c["sequence"],
                               "length": len(c["sequence"]), "rank_E1": rank,
                               "confidence_E1": c["confidence_score"]}
            for j in range(1, a.n_decoys + 1):
                dec = shuffled(c["sequence"], j)
                if dec is None:
                    continue
                d3 = RES / f"boltz_yaml_E3_{a.front}" / sp
                d3.mkdir(parents=True, exist_ok=True)
                ds = f"{stem}__d{j}"
                (d3 / f"{ds}.yaml").write_text(yaml_text(rseq, msa, dec, cyclic))
                man["E3"][ds] = {"species": sp, "parent": stem, "sequence": dec, "decoy": j}
    for tag in ("E2", "E3"):
        (RES / f"manifest_{tag}_{a.front}.json").write_text(json.dumps(man[tag], indent=2))
        print(tag, a.front, len(man[tag]), "yaml")
    # manifestos por especie no formato que select_top_candidates.py espera (stem -> backbone/sequencia)
    md = RES / f"manifests_E2_{a.front}"
    md.mkdir(exist_ok=True)
    for sp in {m["species"] for m in man["E2"].values()}:
        (md / f"{sp}.json").write_text(json.dumps(
            {k: v for k, v in man["E2"].items() if v["species"] == sp}, indent=2))


def collect(a):
    man = json.loads((RES / f"manifest_{a.tag}_{a.front}.json").read_text())
    per, best = {}, {}
    for stem, meta in man.items():
        sp = meta["species"]
        rows = []
        for seed in a.seeds:
            pdir = ROOT / f"outputs/b23_boltz2_{a.tag}_{a.front}_s{seed}_{sp}/boltz_results_{sp}/predictions/{stem}"
            for f in sorted(pdir.glob(f"confidence_{stem}_model_*.json")):
                j = json.loads(f.read_text())
                m = int(f.stem.rsplit("_", 1)[1])
                rows.append((j["confidence_score"], j.get("complex_plddt"), j.get("iptm"),
                             str((pdir / f"{stem}_model_{m}.pdb").relative_to(ROOT))))
        if rows:
            per[stem] = rows
    out = {}
    for stem, rows in per.items():
        meta = man[stem]
        cs = [r[0] for r in rows]
        top = max(rows, key=lambda r: r[0])
        out.setdefault(meta["species"], []).append({
            **meta, "backbone": meta.get("backbone"), "sequence": meta["sequence"],
            "confidence_score": statistics.mean(cs),
            "confidence_sd": statistics.pstdev(cs) if len(cs) > 1 else 0.0,
            "confidence_max": top[0], "n_pred": len(cs),
            "complex_plddt": statistics.mean(r[1] for r in rows if r[1] is not None),
            "iptm": statistics.mean(r[2] for r in rows if r[2] is not None), "pdb": top[3],
            "stem": stem})
    for sp in out:
        out[sp].sort(key=lambda r: r["confidence_score"], reverse=True)
    (RES / f"b23_boltz2_{a.tag}_{a.front}_scores.json").write_text(json.dumps(out, indent=2))
    print(a.tag, a.front, {sp: len(v) for sp, v in out.items()})


def delta(a):
    e2 = json.loads((RES / f"b23_boltz2_E2_{a.front}_scores.json").read_text())
    e3p = RES / f"b23_boltz2_E3_{a.front}_scores.json"
    e3 = json.loads(e3p.read_text()) if e3p.exists() else {}
    dec = {}
    for rows in e3.values():
        for r in rows:
            dec.setdefault(r["parent"], []).append(r["confidence_score"])
    res = {}
    for sp, rows in e2.items():
        for r in rows:
            d = dec.get(r["stem"])
            res.setdefault(sp, []).append({
                "stem": r["stem"], "sequence": r["sequence"], "E2_mean": r["confidence_score"],
                "decoy_mean": statistics.mean(d) if d else None, "n_decoys": len(d or []),
                "delta": (r["confidence_score"] - statistics.mean(d)) if d else None})
    (RES / f"delta_paired_{a.front}.json").write_text(json.dumps(res, indent=2))
    allv = [x["delta"] for v in res.values() for x in v if x["delta"] is not None]
    if allv:
        print(f"{a.front}: {len(allv)} candidatos com controle; Delta>0 em {sum(v > 0 for v in allv)} "
              f"(mediana {statistics.median(allv):.3f})")


def pick_qc(a):
    """Estrutura inicial da MD = amostra de MAIOR confianca entre as que PASSAM no QC de pose (pose_qc.qc_pose,
    limiares pre-registrados, inalterados), entre todas as amostras e sementes do E2. Se nenhuma passa, mantem a de
    maior confianca e marca `pdb_qc_pass: false`. O escore do candidato (media) e o ranking nao mudam.
    Roda em protein_design_env (pose_qc importa MDAnalysis)."""
    from pose_qc import qc_pose
    f = RES / f"b23_boltz2_E2_{a.front}_scores.json"
    data = json.loads(f.read_text())
    cyc = a.front == "M"
    n_ok = n_tot = 0
    for sp, rows in data.items():
        for r in rows:
            stem = r["stem"]
            samples = []
            for seed in a.seeds:
                pdir = ROOT / f"outputs/b23_boltz2_E2_{a.front}_s{seed}_{sp}/boltz_results_{sp}/predictions/{stem}"
                for cf in sorted(pdir.glob(f"confidence_{stem}_model_*.json")):
                    m = int(cf.stem.rsplit("_", 1)[1])
                    pdb = pdir / f"{stem}_model_{m}.pdb"
                    if pdb.exists():
                        samples.append((json.loads(cf.read_text())["confidence_score"], pdb))
            samples.sort(key=lambda s: -s[0])
            chosen, n_pass = None, 0
            for conf, pdb in samples:
                q = qc_pose(pdb, sp, cyc)
                if q["qc_pass"]:
                    n_pass += 1
                    if chosen is None:
                        chosen = (conf, pdb, q)
            r["n_samples"] = len(samples)
            r["n_samples_qc_pass"] = n_pass
            r["pdb_qc_pass"] = chosen is not None
            if chosen is not None:
                r["pdb"] = str(chosen[1].relative_to(ROOT))
                r["pdb_confidence"] = chosen[0]
            n_tot += 1
            n_ok += chosen is not None
    f.write_text(json.dumps(data, indent=2))
    print(f"pick-qc {a.front}: {n_ok}/{n_tot} candidatos com >=1 amostra aprovada no QC")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--front", choices=["L", "M"], required=True)
    p.add_argument("--k", type=int, default=10)
    p.add_argument("--n-decoys", type=int, default=3)
    p.set_defaults(func=prepare)
    p = sub.add_parser("collect")
    p.add_argument("--front", choices=["L", "M"], required=True)
    p.add_argument("--tag", choices=["E2", "E3"], required=True)
    p.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    p.set_defaults(func=collect)
    p = sub.add_parser("pick-qc")
    p.add_argument("--front", choices=["L", "M"], required=True)
    p.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    p.set_defaults(func=pick_qc)
    p = sub.add_parser("delta")
    p.add_argument("--front", choices=["L", "M"], required=True)
    p.set_defaults(func=delta)
    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()

"""
analyze_md_controls.py -- escala de referencia para a ocupancia de S1: aplica a MESMA analise dos candidatos
(`analyze_md_top_candidates.analyze`) aos complexos da calibracao B0.5, que usam o MESMO receptor de
*S. frugiperda* (266 residuos) e contem inibidores naturais reais e suas iscas embaralhadas.

Serve para responder "70% de ocupancia e' muito ou pouco?", que nenhum numero do estudo respondia.

RESSALVA IMPORTANTE: as trajetorias da calibracao sao de **2 ns**, campo de forca **AMBER99SB-ILDN** e outro pH,
enquanto a triagem usa 10 ns e CHARMM36 a pH 10. Portanto esta e' uma referencia **preliminar**, de protocolo
diferente; a referencia definitiva vem de `run_md_controls.sh` (mesmo protocolo dos candidatos). As janelas
(metades, final) sao proporcionais a' trajetoria, entao "2a metade" aqui e' 1-2 ns.

Uso: python -m scripts.analyze_md_controls [--md-dir data-calibration-b05/md_calib] [--receptor Sfrugiperda]
     [--out outputs/controls_calibration.json] [--prefix sfrug__]
"""
import argparse
import json
from pathlib import Path

import MDAnalysis as mda

from scripts import analyze_md_top_candidates as A

ROOT = Path(__file__).parent.parent


def peptide_sequence(tpr: Path, n_expected_receptor: int | None = None) -> str | None:
    """Sequencia da cadeia do peptideo lida da propria topologia (o menor segmento proteico)."""
    u = mda.Universe(str(tpr))
    prot = u.select_atoms("protein or resname " + " ".join(sorted(A._STD_RES)))
    segs = [s for s in prot.segments if len(s.residues)]
    if len(segs) < 2:
        return None
    pep = min(segs, key=lambda s: len(s.residues))
    try:
        return "".join(mda.lib.util.convert_aa_code(A.std_resname(r.resname)) for r in pep.residues)
    except Exception:  # noqa: BLE001 - residuo nao padrao (ex.: ligante)
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--md-dir", default="data-calibration-b05/md_calib")
    ap.add_argument("--receptor", default="Sfrugiperda")
    ap.add_argument("--prefix", default="sfrug__")
    ap.add_argument("--out", default="outputs/controls_calibration.json")
    a = ap.parse_args()

    A.MD_DIR = ROOT / a.md_dir
    out_path = ROOT / a.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    res = json.loads(out_path.read_text()) if out_path.exists() else {}

    keys = sorted(d.name for d in (ROOT / a.md_dir).iterdir()
                  if d.is_dir() and d.name.startswith(a.prefix) and (d / "md.tpr").exists() and (d / "md.xtc").exists())
    print(f"{len(keys)} sistemas em {a.md_dir} com prefixo {a.prefix}")
    for k in keys:
        seq = peptide_sequence(ROOT / a.md_dir / k / "md.tpr")
        if not seq:
            res[k] = {"error": "nao foi possivel ler a sequencia do peptideo"}
            print(k, res[k])
            continue
        try:
            r = A.analyze(k, seq, cyclic=None, receptor=a.receptor)
            res[k] = {"sequence": seq, "n_res_peptide": len(seq),
                      "class": "decoy" if k.endswith("_decoy") else "inibidor", **r}
        except Exception as e:  # noqa: BLE001
            res[k] = {"sequence": seq, "error": f"{type(e).__name__}: {e}"}
        print(k, json.dumps({x: res[k].get(x) for x in ("class", "occ_5A_h2", "anchor_aa", "contact_any_frac_4.5A", "error")}), flush=True)
        out_path.write_text(json.dumps(res, indent=2))

    ok = {k: v for k, v in res.items() if "occ_5A_h2" in v}
    inh = [v["occ_5A_h2"] for v in ok.values() if v.get("class") == "inibidor"]
    dec = [v["occ_5A_h2"] for v in ok.values() if v.get("class") == "decoy"]
    print(f"\nreferencia preliminar (2 ns, AMBER): inibidores n={len(inh)} ocupancia 5 A na 2a metade "
          f"{sorted(round(x, 2) for x in inh)}")
    print(f"                                     iscas       n={len(dec)} {sorted(round(x, 2) for x in dec)}")


if __name__ == "__main__":
    main()

"""B1.4 — Mapeamento REAL dos subsitios (S1-S4/S1'-S3' + exossitio) por template
cristalografico, via contatos reais (Bio.PDB, cutoff de distancia) + equivalencia
estrutural real (foldseek --alignment-type 1, TMalign).

Substitui a heuristica "204/218" e a triade catalitica detectada por
scripts/agents/structure_agent.py::_find_catalytic_triad, que tem um offset
sistematico de +15/+16 residuos confirmado em 8/9 especies do painel (ver
docs/bench/b1x_confirmacao_especificidade_tripsina.md). Aqui a definicao dos
subsitios vem de contato real em complexo cristalografico (2PTC = tripsina
bovina-BPTI, 1SFI = tripsina bovina-SFTI-1), e a transferencia para cada
receptor de Lepidoptera usa correspondencia estrutural real (foldseek TMalign),
nao offset de sequencia assumido.

P1 de cada inibidor tambem e achado por geometria real (residuo cujo carbono
carbonila fica mais perto do OG de uma Ser do proprio receptor), nao citado de
memoria/literatura sem verificacao.

Roda no servidor, env `structure` (tem foldseek + biopython):
    python scripts/map_subsites_b14.py

Saida: outputs/sites/subsites_by_receptor.json (nao versionado, padrao do repo)
       + copia versionada em data-lepidoptera-panel/subsites_by_receptor.json
         (segue o padrao ja usado por data-calibration-b05/).
"""
import json
import subprocess
import urllib.request
from pathlib import Path

from Bio.PDB import PDBIO, PDBParser, Select

CONTACT_CUTOFF = 4.5  # Angstrom — contato real de subsitio
CATALYTIC_SER_CUTOFF = 4.5  # Angstrom — geometria plausivel de ataque nucleofilico
TMSCORE_GO_THRESHOLD = 0.5
RMSD_GO_THRESHOLD = 3.0

REF_COMPLEXES = {
    "2PTC_BPTI": {"pdb_id": "2PTC", "trypsin_chain": "E", "inhibitor_chain": "I"},
    "1SFI_SFTI1": {"pdb_id": "1SFI", "trypsin_chain": "A", "inhibitor_chain": "I"},
}

RECEPTORS = {
    "Sfrugiperda": "Sfrugiperda-A0A089QDB3-AlphaFold.pdb",
    "Slitura": "Slitura-B3F884-AlphaFold.pdb",
    "Onubilalis": "Onubilalis-Q6R561-AlphaFold.pdb",
    "Dsaccharalis": "Dsaccharalis-T1QDI0-AlphaFold.pdb",
    "Cincludens": "Cincludens-A0A9P0BRD5-AlphaFold.pdb",
    "Hvirescens": "Hvirescens-I7D523-AlphaFold.pdb",
    "Pxylostella": "Pxylostella-E2IGY7-AlphaFold.pdb",
    "Msexta": "Msexta-P35045-AlphaFold.pdb",
    "Bmori": "Bmori-A0A8R2C8B0-AlphaFold.pdb",
}

PANEL_DIR = Path("data-lepidoptera-panel")
REF_DIR = Path("data-subsites-b14/refs")
WORK_DIR = Path("data-subsites-b14/work")
OUT_JSON = Path("outputs/sites/subsites_by_receptor.json")
OUT_JSON_VERSIONED = Path("data-lepidoptera-panel/subsites_by_receptor.json")

SUBSITE_LABELS = ["S4", "S3", "S2", "S1", "S1'", "S2'", "S3'"]
P_LABELS = ["P4", "P3", "P2", "P1", "P1'", "P2'", "P3'"]
P_OFFSETS = [-3, -2, -1, 0, 1, 2, 3]


def fetch_pdb(pdb_id: str, out_path: Path) -> None:
    if out_path.exists() and out_path.stat().st_size > 1000:
        return
    out_path.parent.mkdir(parents=True, exist_ok=True)
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    with urllib.request.urlopen(url, timeout=30) as r:
        out_path.write_bytes(r.read())


def chain_residues(structure, chain_id):
    return [res for res in structure[0][chain_id] if res.id[0] == " "]


def min_dist(res_a, res_b) -> float:
    d = None
    for atom_a in res_a:
        for atom_b in res_b:
            dd = atom_a - atom_b
            if d is None or dd < d:
                d = dd
    return d


def find_p1(trypsin_residues, inhibitor_residues):
    best = None
    for ser in trypsin_residues:
        if ser.get_resname() != "SER" or "OG" not in ser:
            continue
        og = ser["OG"]
        for inhib_res in inhibitor_residues:
            if "C" not in inhib_res:
                continue
            d = og - inhib_res["C"]
            if best is None or d < best[0]:
                best = (d, ser, inhib_res)
    return best


def get_subsite_definitions(tag: str, cfg: dict) -> dict:
    parser = PDBParser(QUIET=True)
    pdb_path = REF_DIR / f"{cfg['pdb_id']}.pdb"
    fetch_pdb(cfg["pdb_id"], pdb_path)
    structure = parser.get_structure(cfg["pdb_id"], pdb_path)
    tryp_res = chain_residues(structure, cfg["trypsin_chain"])
    inhib_res = chain_residues(structure, cfg["inhibitor_chain"])

    found = find_p1(tryp_res, inhib_res)
    if found is None:
        raise RuntimeError(f"{tag}: nenhuma Ser encontrada na cadeia de tripsina")
    dist, catalytic_ser, p1_res = found
    if dist > CATALYTIC_SER_CUTOFF:
        raise RuntimeError(
            f"{tag}: melhor par Ser-OG/inibidor-C a {dist:.2f}A (> {CATALYTIC_SER_CUTOFF}A) — QC falhou, P1 nao confiavel"
        )

    p1_idx = inhib_res.index(p1_res)
    positions = {}
    for label, off in zip(P_LABELS, P_OFFSETS):
        idx = p1_idx + off
        if 0 <= idx < len(inhib_res):
            positions[label] = inhib_res[idx]

    core_ids = {id(r) for r in positions.values()}
    subsites = {}
    for p_label, subsite_label in zip(P_LABELS, SUBSITE_LABELS):
        res = positions.get(p_label)
        if res is None:
            subsites[subsite_label] = {"inhibitor_residue": None, "trypsin_contacts": []}
            continue
        contacts = sorted({
            f"{t.get_resname()}{t.id[1]}" for t in tryp_res if min_dist(t, res) <= CONTACT_CUTOFF
        })
        subsites[subsite_label] = {
            "inhibitor_residue": f"{res.get_resname()}{res.id[1]}",
            "trypsin_contacts": contacts,
        }

    exosite_contacts = set()
    for res in inhib_res:
        if id(res) in core_ids:
            continue
        for t in tryp_res:
            if min_dist(t, res) <= CONTACT_CUTOFF:
                exosite_contacts.add(f"{t.get_resname()}{t.id[1]}")
    subsites["exosite"] = {"trypsin_contacts": sorted(exosite_contacts)}

    return {
        "subsites": subsites,
        "catalytic_ser": f"{catalytic_ser.get_resname()}{catalytic_ser.id[1]}",
        "catalytic_ser_p1_dist_A": round(dist, 2),
        "trypsin_chain_pdb": str(pdb_path),
        "trypsin_chain_id": cfg["trypsin_chain"],
    }


def extract_chain_pdb(pdb_path: Path, chain_id: str, out_path: Path) -> None:
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("x", pdb_path)

    class ChainSelect(Select):
        def accept_chain(self, chain):
            return chain.id == chain_id

        def accept_residue(self, residue):
            return residue.id[0] == " "

    io = PDBIO()
    io.set_structure(structure)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    io.save(str(out_path), ChainSelect())


def run_foldseek_tmalign(query_pdb: Path, target_pdb: Path, work_dir: Path):
    work_dir.mkdir(parents=True, exist_ok=True)
    out_tsv = work_dir / f"{query_pdb.stem}__{target_pdb.stem}.tsv"
    tmp = work_dir / f"tmp_{query_pdb.stem}_{target_pdb.stem}"
    tmp.mkdir(exist_ok=True, parents=True)
    cols = "query,target,qstart,qend,tstart,tend,qaln,taln,rmsd,alntmscore,qtmscore,ttmscore,prob"
    cmd = [
        "foldseek", "easy-search", str(query_pdb), str(target_pdb), str(out_tsv), str(tmp),
        "--alignment-type", "1", "--format-output", cols, "-e", "1000",
        "--exhaustive-search", "1",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        return None, res.stderr
    lines = [l for l in out_tsv.read_text().strip().splitlines() if l.strip()]
    if not lines:
        return None, "sem alinhamento retornado"
    keys = cols.split(",")
    best = max(lines, key=lambda l: float(dict(zip(keys, l.split("\t")))["alntmscore"]))
    return dict(zip(keys, best.split("\t"))), None


def index_to_resnum(pdb_path: Path, chain_id: str):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("x", pdb_path)
    residues = chain_residues(structure, chain_id)
    return [(r.get_resname(), r.id[1]) for r in residues]


def build_correspondence(aln: dict, t_index, q_index):
    """indice(0-based) na cadeia-alvo (referencia) -> indice(0-based) na cadeia-query (receptor)."""
    qi = int(aln["qstart"]) - 1
    ti = int(aln["tstart"]) - 1
    mapping = {}
    for qc, tc in zip(aln["qaln"], aln["taln"]):
        if qc != "-" and tc != "-":
            mapping[ti] = qi
        if qc != "-":
            qi += 1
        if tc != "-":
            ti += 1
    return mapping


def resnum_lookup(index_list):
    """(resname, resnum) -> indice 0-based na lista, para o lado da REFERENCIA (target foldseek)."""
    d = {}
    for i, (resname, resnum) in enumerate(index_list):
        d[f"{resname}{resnum}"] = i
    return d


def transfer_residue(ref_tag: str, t_lookup: dict, mapping: dict, q_index: list):
    idx = t_lookup.get(ref_tag)
    if idx is None:
        return {"ref": ref_tag, "receptor": None, "status": "residuo_ref_nao_encontrado_na_cadeia_extraida"}
    q_idx = mapping.get(idx)
    if q_idx is None:
        return {"ref": ref_tag, "receptor": None, "status": "sem_correspondencia_estrutural_gap_no_alinhamento"}
    if q_idx >= len(q_index):
        return {"ref": ref_tag, "receptor": None, "status": "indice_fora_do_receptor"}
    resname, resnum = q_index[q_idx]
    return {"ref": ref_tag, "receptor": f"{resname}{resnum}", "status": "ok"}


def main():
    REF_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)

    print("== Fase 1: definindo subsitios reais nos complexos de referencia ==")
    ref_defs = {}
    ref_trypsin_pdbs = {}
    for tag, cfg in REF_COMPLEXES.items():
        d = get_subsite_definitions(tag, cfg)
        ref_defs[tag] = d
        chain_pdb = REF_DIR / f"{tag}_trypsin_chain.pdb"
        extract_chain_pdb(Path(d["trypsin_chain_pdb"]), d["trypsin_chain_id"], chain_pdb)
        ref_trypsin_pdbs[tag] = chain_pdb
        print(f"{tag}: Ser catalitica real = {d['catalytic_ser']} "
              f"(dist ao C carbonila do P1 = {d['catalytic_ser_p1_dist_A']}A)")
        for sl in SUBSITE_LABELS:
            print(f"  {sl}: inibidor={d['subsites'][sl]['inhibitor_residue']} "
                  f"contatos_tripsina={d['subsites'][sl]['trypsin_contacts']}")
        print(f"  exossitio: {d['subsites']['exosite']['trypsin_contacts']}")

    print("\n== Fase 2: foldseek TMalign receptor x referencia + transferencia de subsitios ==")
    results = {}
    for species, fname in RECEPTORS.items():
        query_pdb = PANEL_DIR / fname
        if not query_pdb.exists():
            print(f"{species}: PDB nao encontrado ({query_pdb}), pulando")
            continue
        q_index = index_to_resnum(query_pdb, "A")
        results[species] = {"templates": {}}

        for tag in REF_COMPLEXES:
            target_pdb = ref_trypsin_pdbs[tag]
            aln, err = run_foldseek_tmalign(query_pdb, target_pdb, WORK_DIR)
            if aln is None:
                results[species]["templates"][tag] = {"status": "falhou", "erro": err}
                print(f"{species} x {tag}: FALHOU ({err})")
                continue

            t_index = index_to_resnum(target_pdb, ref_defs[tag]["trypsin_chain_id"])
            t_lookup = resnum_lookup(t_index)
            mapping = build_correspondence(aln, t_index, q_index)

            rmsd = float(aln["rmsd"])
            tmscore = float(aln["alntmscore"])
            go = tmscore >= TMSCORE_GO_THRESHOLD and rmsd <= RMSD_GO_THRESHOLD

            subsite_transfer = {}
            n_matched = 0
            n_total = 0
            for sl in SUBSITE_LABELS + ["exosite"]:
                refs = ref_defs[tag]["subsites"][sl]["trypsin_contacts"]
                transferred = [transfer_residue(r, t_lookup, mapping, q_index) for r in refs]
                subsite_transfer[sl] = transferred
                n_total += len(transferred)
                n_matched += sum(1 for x in transferred if x["status"] == "ok")

            catalytic_transfer = transfer_residue(ref_defs[tag]["catalytic_ser"], t_lookup, mapping, q_index)

            results[species]["templates"][tag] = {
                "status": "go" if go else "no-go",
                "rmsd_A": round(rmsd, 3),
                "tmscore": round(tmscore, 3),
                "prob": round(float(aln.get("prob", 0.0)), 4),
                "residuos_transferidos": f"{n_matched}/{n_total}",
                "catalytic_ser_receptor": catalytic_transfer,
                "subsites": subsite_transfer,
            }
            print(f"{species} x {tag}: TMscore={tmscore:.3f} RMSD={rmsd:.2f}A "
                  f"transferidos={n_matched}/{n_total} -> {'GO' if go else 'NO-GO'}")

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({"ref_definitions": {
        tag: {k: v for k, v in d.items() if k != "trypsin_chain_pdb"} for tag, d in ref_defs.items()
    }, "receptors": results}, indent=2, ensure_ascii=False))
    OUT_JSON_VERSIONED.write_text(OUT_JSON.read_text())
    print(f"\nSalvo: {OUT_JSON} (+ copia versionada {OUT_JSON_VERSIONED})")


if __name__ == "__main__":
    main()

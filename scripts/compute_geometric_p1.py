"""
compute_geometric_p1.py — P1-âncora geométrico para macrociclos (A2 do plano de retomada).

Problema real: `analyze_cleavage.py` original assume peptídeo LINEAR e usa o sítio de
tripsina mais C-terminal da sequência como "P1-âncora" (isento da contagem de
susceptibilidade). Os candidatos da campanha B2.3 são MACROCICLOS (cabeça-cauda) — não
têm terminal real, então "mais C-terminal" não tem significado estrutural nenhum.

Fix: usar a mesma lógica geométrica real já usada em B1.4 (mapeamento de subsítios) —
o resíduo do peptídeo mais próximo da Ser catalítica do receptor na pose PREVISTA (não a
posição na sequência escrita). O backbone gerado pelo RFdiffusion em modo binder já é a
pose condicionada aos hotspots reais (cadeia A=receptor, cadeia B=peptídeo desenhado) —
não precisa de docking adicional.

Limitação real, documentada: o PDB do RFdiffusion é backbone-only (N, CA, C, O — sem
side-chains), então não existe átomo OG de Ser real nesse estágio (diferente de B1.4, que
usava a estrutura cristalográfica COMPLETA com side-chains). Proxy usado aqui: distância
CA(peptídeo) → CA(Ser catalítica do receptor). É uma aproximação ao nível de backbone, não
o mesmo Ser-OG↔C-carbonila de B1.4 — mas identifica o mesmo resíduo na prática esperada
(a posição do peptídeo mais encaixada no bolso S1), já que a cadeia lateral da Ser é curta
(~2,5Å de CA a OG) frente às distâncias entre resíduos do peptídeo (tipicamente >3,5Å CA-CA).

Uso:
  python scripts/compute_geometric_p1.py --species all7 \
      --campaign-dir outputs/b23_campaign --out data-lepidoptera-panel/geometric_p1_b23.json
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
SUBSITES_FILE = ROOT / "data-lepidoptera-panel" / "subsites_by_receptor.json"
SPECIES_7 = ["Sfrugiperda", "Slitura", "Onubilalis", "Dsaccharalis",
             "Cincludens", "Hvirescens", "Pxylostella"]
TEMPLATE = "1SFI_SFTI1"  # mesmo template usado pra gerar os hotspots da campanha B2.3


def parse_ca_coords(pdb_path: Path) -> dict:
    """Retorna {(chain_id, resnum): (x,y,z)} para todos os átomos CA do PDB."""
    coords = {}
    with open(pdb_path) as f:
        for line in f:
            if not line.startswith("ATOM"):
                continue
            atom_name = line[12:16].strip()
            if atom_name != "CA":
                continue
            chain_id = line[21]
            resnum = int(line[22:26])
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])
            coords[(chain_id, resnum)] = (x, y, z)
    return coords


def dist(a: tuple, b: tuple) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5


def geometric_p1_for_backbone(pdb_path: Path, catalytic_ser_resnum: int, peptide_len: int) -> dict:
    coords = parse_ca_coords(pdb_path)
    ser_ca = coords.get(("A", catalytic_ser_resnum))
    if ser_ca is None:
        return {"error": f"Ser catalitica (resnum {catalytic_ser_resnum}) nao encontrada na cadeia A"}

    dists = []
    for pos in range(1, peptide_len + 1):
        pep_ca = coords.get(("B", pos))
        if pep_ca is None:
            return {"error": f"Residuo B{pos} ausente no backbone"}
        dists.append((pos, dist(ser_ca, pep_ca)))

    pos_closest, d_closest = min(dists, key=lambda t: t[1])
    return {
        "p1_position_1based": pos_closest,
        "distance_ca_ca_A": round(d_closest, 2),
        "all_distances_A": {p: round(d, 2) for p, d in dists},
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--species", nargs="+", default=SPECIES_7,
                     help="Lista de espécies, ou omitir para rodar as 7 primárias")
    ap.add_argument("--campaign-dir", type=str, default="outputs/b23_campaign",
                     help="Prefixo do diretório de outputs (ex.: outputs/b23_campaign -> "
                          "outputs/b23_campaign_<especie>/rfdiffusion)")
    ap.add_argument("--out", type=str, default="data-lepidoptera-panel/geometric_p1_b23.json")
    args = ap.parse_args()

    subsites = json.loads(SUBSITES_FILE.read_text())
    receptors = subsites["receptors"]

    result = {}
    n_ok, n_err = 0, 0
    for species in args.species:
        cat_ser_str = receptors[species]["templates"][TEMPLATE]["catalytic_ser_receptor"]["receptor"]
        cat_ser_resnum = int("".join(c for c in cat_ser_str if c.isdigit()))

        rfdiff_dir = ROOT / f"{args.campaign_dir}_{species}" / "rfdiffusion"
        if not rfdiff_dir.exists():
            print(f"[{species}] diretório não encontrado: {rfdiff_dir} — pulando")
            continue

        species_result = {}
        for len_dir in sorted(rfdiff_dir.glob("len_*")):
            peptide_len = int(len_dir.name.split("_")[1])
            for pdb_path in sorted(len_dir.glob("design_*.pdb")):
                # formato deve bater com a coluna "backbone" do dataset ML (sem "_" após "len")
                backbone_id = f"len{peptide_len}_{pdb_path.stem}"
                r = geometric_p1_for_backbone(pdb_path, cat_ser_resnum, peptide_len)
                species_result[backbone_id] = r
                if "error" in r:
                    n_err += 1
                    print(f"[{species}/{backbone_id}] ERRO: {r['error']}")
                else:
                    n_ok += 1
        result[species] = {
            "catalytic_ser_resnum_chainA": cat_ser_resnum,
            "backbones": species_result,
        }
        print(f"[{species}] {len(species_result)} backbones processados "
              f"(Ser catalítica real = A{cat_ser_resnum})")

    out_path = ROOT / args.out
    out_path.parent.mkdir(exist_ok=True, parents=True)
    out_path.write_text(json.dumps(result, indent=2))
    print(f"\nTotal: {n_ok} backbones OK, {n_err} com erro.")
    print(f"Salvo em: {out_path}")


if __name__ == "__main__":
    main()

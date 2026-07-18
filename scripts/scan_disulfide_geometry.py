"""scan_disulfide_geometry.py — Varre estrutura MD REAL (pós-produção, GROMACS)
em busca de pares de resíduos geometricamente compatíveis com uma ponte dissulfeto
(Cbeta-Cbeta 3,5-7,5 A), como triagem inicial no estilo Disulfide-by-Design.

Não substitui validação estrutural completa (ex. RoseTTAFold All-Atom) — é um
primeiro filtro geométrico sobre uma conformação já simulada de verdade (10 ns),
não uma estrutura ingênua/não-relaxada.

Uso:
  conda run -n protein_design_env python scripts/scan_disulfide_geometry.py \
      outputs/md/forced_05 RLREELKKAEEWLEKRRKEE
"""
import subprocess
import sys
from pathlib import Path

import numpy as np


def extract_snapshot_pdb(md_dir: Path) -> Path:
    out_pdb = md_dir / "snapshot_final.pdb"
    if out_pdb.exists():
        return out_pdb
    p = subprocess.run(
        ["gmx", "trjconv", "-s", str(md_dir / "md.tpr"), "-f", str(md_dir / "md.gro"),
         "-o", str(out_pdb), "-pbc", "mol", "-center"],
        input="1\n1\n", capture_output=True, text=True, timeout=60,
    )
    if p.returncode != 0 or not out_pdb.exists():
        raise RuntimeError(f"gmx trjconv falhou (rc={p.returncode}): {p.stderr[-600:]}")
    return out_pdb


def parse_chain_P(pdb_path: Path) -> dict:
    """Retorna {resnum: {'resname':.., 'CA':xyz, 'CB':xyz|None}} para a cadeia P (peptídeo)."""
    residues: dict = {}
    for line in pdb_path.read_text(errors="replace").splitlines():
        if not line.startswith(("ATOM", "HETATM")):
            continue
        chain = line[21]
        if chain != "P":
            continue
        atomname = line[12:16].strip()
        if atomname not in ("CA", "CB"):
            continue
        resname = line[17:20].strip()
        resnum = int(line[22:26])
        x, y, z = float(line[30:38]), float(line[38:46]), float(line[46:54])
        d = residues.setdefault(resnum, {"resname": resname})
        d[atomname] = np.array([x, y, z])
    return residues


def scan(residues: dict, seq: str, edge_exclude: int = 2) -> list:
    positions = sorted(residues.keys())
    n = len(seq)
    results = []
    for a_idx, i in enumerate(positions):
        if i <= edge_exclude or i > n - edge_exclude:
            continue
        pi = residues[i].get("CB", residues[i].get("CA"))
        if pi is None:
            continue
        for j in positions[a_idx + 1:]:
            if j <= edge_exclude or j > n - edge_exclude:
                continue
            if j - i < 2:
                continue
            pj = residues[j].get("CB", residues[j].get("CA"))
            if pj is None:
                continue
            dist = float(np.linalg.norm(pi - pj))
            if 3.5 <= dist <= 7.5:
                results.append((i, seq[i - 1], j, seq[j - 1], round(dist, 2)))
    return sorted(results, key=lambda x: x[-1])


def main():
    md_dir = Path(sys.argv[1])
    seq = sys.argv[2]

    snapshot = extract_snapshot_pdb(md_dir)
    residues = parse_chain_P(snapshot)
    print(f"Cadeia P (peptídeo): {len(residues)}/{len(seq)} resíduos extraídos de {snapshot}")
    if len(residues) < len(seq):
        print("AVISO: menos resíduos extraídos que o esperado — verificar snapshot/cadeia.")

    pairs = scan(residues, seq)
    print(f"\n{len(pairs)} pares Cβ-Cβ compatíveis com dissulfeto (3,5-7,5 Å, "
          f"excluindo 2 residuos de borda em cada extremidade):")
    print(f"{'Pos i':<8}{'AA i':<6}{'Pos j':<8}{'AA j':<6}{'Dist (Å)'}")
    for i, ai, j, aj, d in pairs[:20]:
        print(f"{i:<8}{ai:<6}{j:<8}{aj:<6}{d}")

    if not pairs:
        print("\nNenhum par geometricamente compatível na conformação simulada — "
              "essa conformação linear não se presta a engenharia direta de dissulfeto.")


if __name__ == "__main__":
    main()

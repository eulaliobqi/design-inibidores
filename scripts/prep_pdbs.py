#!/usr/bin/env python3
"""Preprocess trypsin PDB files: add chain A, renumber residues from 1.

Run once on the server before the pipeline:
    cd ~/design-inibidores
    python scripts/prep_pdbs.py

Writes *-A.pdb alongside each *-final.pdb.
"""
from pathlib import Path


def preprocess_pdb(src: Path, dst: Path) -> None:
    text = src.read_text(errors="replace")
    raw_lines = text.splitlines(keepends=True)

    # Collect ATOM residue numbers to find offset
    res_nums = []
    for line in raw_lines:
        if line.startswith("ATOM"):
            try:
                res_nums.append(int(line[22:26]))
            except ValueError:
                pass

    if not res_nums:
        print(f"  WARN: sem registros ATOM em {src.name}")
        return

    offset = min(res_nums) - 1          # resíduo mínimo → 1
    seen_res = set()

    out = []
    for line in raw_lines:
        rec = line[:6].strip()
        if rec in ("ATOM", "HETATM", "TER"):
            try:
                old_res = int(line[22:26])
            except ValueError:
                continue
            new_res = old_res - offset
            # Col 21 (0-idx) = chain; cols 22:26 (0-idx) = residue number
            new_line = line[:21] + "A" + f"{new_res:4d}" + line[26:]
            out.append(new_line)
            if rec == "ATOM":
                seen_res.add(new_res)
        elif rec in ("REMARK", "HEADER", "TITLE", "SEQRES", "SSBOND", "CONECT"):
            out.append(line)

    out.append("END\n")
    dst.write_text("".join(out))

    n_res = len(seen_res)
    last = max(seen_res)
    print(f"  {src.name:25s} → {dst.name:20s}  chain A, {n_res} resíduos  A1-{last}")


def main():
    data_dir = Path("data-trypsin")
    pdbs = sorted(data_dir.glob("*-final.pdb"))
    if not pdbs:
        print("Nenhum *-final.pdb encontrado em data-trypsin/")
        return

    print("Preprocessando PDB files...\n")
    for pdb in pdbs:
        stem = pdb.stem.replace("-final", "")
        dst = pdb.parent / f"{stem}-A.pdb"
        preprocess_pdb(pdb, dst)

    print("\nConcluído. Atualize config.yaml para usar os arquivos *-A.pdb.")


if __name__ == "__main__":
    main()

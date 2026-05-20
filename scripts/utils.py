"""Utilitários compartilhados: detecção de ferramentas, parsing PDB, helpers."""
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional


# ─────────────────────────────────────────────────────────────
# Detecção de ferramentas externas
# ─────────────────────────────────────────────────────────────

def find_tool(name: str, extra_paths: list[str] = None) -> Optional[str]:
    """Retorna o caminho do executável se encontrado, None caso contrário."""
    if shutil.which(name):
        return shutil.which(name)
    for p in (extra_paths or []):
        expanded = Path(os.path.expandvars(os.path.expanduser(p)))
        candidate = expanded / name
        if candidate.exists():
            return str(candidate)
    return None


def find_rfdiffusion(config: dict) -> Optional[Path]:
    paths = config.get("rfdiffusion", {}).get("install_paths", [])
    for p in paths:
        expanded = Path(os.path.expandvars(os.path.expanduser(str(p))))
        script = expanded / "run_inference.py"
        if script.exists():
            return expanded
    return None


def find_proteinmpnn(config: dict) -> Optional[Path]:
    paths = config.get("proteinmpnn", {}).get("install_paths", [])
    for p in paths:
        expanded = Path(os.path.expandvars(os.path.expanduser(str(p))))
        script = expanded / "protein_mpnn_run.py"
        if script.exists():
            return expanded
    return None


def find_rosetta(config: dict) -> Optional[Path]:
    paths = config.get("rosetta", {}).get("install_paths", [])
    for p in paths:
        expanded = Path(os.path.expandvars(os.path.expanduser(str(p))))
        for bin_name in ["FlexPepDocking.static.linuxgccrelease",
                         "FlexPepDocking.default.linuxgccrelease"]:
            candidate = expanded / "main/source/bin" / bin_name
            if candidate.exists():
                return expanded
    # Tentar PyRosetta
    try:
        import pyrosetta  # noqa
        return Path("pyrosetta")
    except ImportError:
        pass
    return None


def check_gromacs() -> bool:
    return shutil.which("gmx") is not None or shutil.which("gmx_mpi") is not None


def check_vina() -> bool:
    return shutil.which("vina") is not None or shutil.which("autodock_vina") is not None


def check_fpocket() -> bool:
    return shutil.which("fpocket") is not None


def tool_summary(config: dict) -> dict:
    """Retorna dict com status de cada ferramenta."""
    return {
        "fpocket":      check_fpocket(),
        "vina":         check_vina(),
        "gromacs":      check_gromacs(),
        "rfdiffusion":  find_rfdiffusion(config) is not None,
        "proteinmpnn":  find_proteinmpnn(config) is not None,
        "rosetta":      find_rosetta(config) is not None,
    }


# ─────────────────────────────────────────────────────────────
# Utilitários PDB
# ─────────────────────────────────────────────────────────────

def load_pdb_atoms(pdb_path: str) -> list[dict]:
    """Lê ATOM records de um PDB como lista de dicts."""
    atoms = []
    with open(pdb_path) as fh:
        for line in fh:
            if not line.startswith("ATOM"):
                continue
            try:
                atoms.append({
                    "serial":  int(line[6:11]),
                    "name":    line[12:16].strip(),
                    "resname": line[17:20].strip(),
                    "chain":   line[21].strip(),
                    "resseq":  int(line[22:26]),
                    "x":       float(line[30:38]),
                    "y":       float(line[38:46]),
                    "z":       float(line[46:54]),
                })
            except (ValueError, IndexError):
                continue
    return atoms


def get_residues(atoms: list[dict]) -> dict[int, dict]:
    """Agrupa atoms por resseq → {resseq: {resname, atoms, centroid}}."""
    residues: dict[int, dict] = {}
    for a in atoms:
        rid = a["resseq"]
        if rid not in residues:
            residues[rid] = {"resname": a["resname"], "atoms": []}
        residues[rid]["atoms"].append(a)
    import numpy as np
    for rid, r in residues.items():
        coords = [[a["x"], a["y"], a["z"]] for a in r["atoms"]]
        r["centroid"] = list(np.mean(coords, axis=0))
    return residues


def write_pdb_atoms(atoms: list[dict], path: str):
    with open(path, "w") as f:
        for a in atoms:
            f.write(
                f"ATOM  {a['serial']:5d} {a['name']:<4s} {a['resname']:<3s} "
                f"{a.get('chain','A'):1s}{a['resseq']:4d}    "
                f"{a['x']:8.3f}{a['y']:8.3f}{a['z']:8.3f}"
                f"  1.00  0.00           {a['name'][0]:1s}\n"
            )
        f.write("END\n")


# ─────────────────────────────────────────────────────────────
# Peptídeos
# ─────────────────────────────────────────────────────────────

AA_1TO3 = {
    'A': 'ALA', 'R': 'ARG', 'N': 'ASN', 'D': 'ASP', 'C': 'CYS',
    'Q': 'GLN', 'E': 'GLU', 'G': 'GLY', 'H': 'HIS', 'I': 'ILE',
    'L': 'LEU', 'K': 'LYS', 'M': 'MET', 'F': 'PHE', 'P': 'PRO',
    'S': 'SER', 'T': 'THR', 'W': 'TRP', 'Y': 'TYR', 'V': 'VAL',
}
AA_3TO1 = {v: k for k, v in AA_1TO3.items()}


def seq3to1(seq3: str) -> str:
    return ''.join(AA_3TO1.get(aa, 'X') for aa in seq3.split())


def parse_fasta(fasta_path: str) -> list[tuple[str, str]]:
    """Retorna lista de (header, sequence)."""
    seqs = []
    header, seq = None, []
    with open(fasta_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                if header:
                    seqs.append((header, ''.join(seq)))
                header, seq = line[1:], []
            else:
                seq.append(line)
    if header:
        seqs.append((header, ''.join(seq)))
    return seqs


def write_fasta(sequences: list[tuple[str, str]], path: str):
    with open(path, "w") as f:
        for header, seq in sequences:
            f.write(f">{header}\n{seq}\n")


def peptide_properties(seq: str) -> dict:
    """Calcula propriedades básicas de um peptídeo."""
    mw_table = {
        'A': 89.09,  'R': 174.20, 'N': 132.12, 'D': 133.10, 'C': 121.16,
        'Q': 146.15, 'E': 147.13, 'G': 75.03,  'H': 155.16, 'I': 131.17,
        'L': 131.17, 'K': 146.19, 'M': 149.21, 'F': 165.19, 'P': 115.13,
        'S': 105.09, 'T': 119.12, 'W': 204.23, 'Y': 181.19, 'V': 117.15,
    }
    charge_table = {'R': +1, 'K': +1, 'H': +0.1, 'D': -1, 'E': -1}
    hydrophobic = set('AILMFWVP')

    mw = sum(mw_table.get(aa, 110) for aa in seq) - 18.02 * (len(seq) - 1)
    charge = sum(charge_table.get(aa, 0) for aa in seq)
    frac_hydrophobic = sum(1 for aa in seq if aa in hydrophobic) / len(seq)
    n_arg_lys = sum(1 for aa in seq if aa in 'RK')

    return {
        "sequence": seq,
        "length": len(seq),
        "mw_da": round(mw, 2),
        "net_charge": round(charge, 2),
        "frac_hydrophobic": round(frac_hydrophobic, 3),
        "n_arg_lys": n_arg_lys,
        "has_p1_basic": seq[0] in 'RK' if seq else False,
    }

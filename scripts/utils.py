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
        # repo v1 (2023): scripts/run_inference.py; older: run_inference.py at root
        for rel in ("scripts/run_inference.py", "run_inference.py"):
            if (expanded / rel).exists():
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
    if shutil.which("gmx") or shutil.which("gmx_mpi"):
        return True
    # Buscar em caminhos padrão de instalação HPC / CUDA-MPI
    candidates = [
        "/usr/local/gromacs/bin/gmx_mpi",
        "/usr/local/gromacs/bin/gmx",
        "/opt/gromacs/bin/gmx_mpi",
        "/opt/gromacs/bin/gmx",
        Path.home() / "gromacs/bin/gmx_mpi",
        Path.home() / "gromacs/bin/gmx",
    ]
    if any(Path(p).exists() for p in candidates):
        return True
    # Último recurso: tentar executar
    try:
        r = subprocess.run(["gmx_mpi", "--version"],
                           capture_output=True, timeout=5)
        return r.returncode == 0
    except Exception:
        return False


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


def build_peptide_pdbqt(sequence: str, center: list, out_dir, logger=None) -> Optional[Path]:
    """Constrói PDBQT rígido do peptídeo para Vina (all-atom via PeptideBuilder + obabel).

    Extraído de DockingAgent._build_peptide_pdbqt (validado em ~990 docagens reais nesta
    sessão) para reuso em outros agentes (ex. SpecificityAgent, que tinha implementação
    própria com átomos CA isolados sem ligação — obabel tratava cada átomo como molécula
    separada, gerando múltiplos blocos ROOT que o Vina rejeitava).
    """
    out_dir = Path(out_dir)
    pdb_path = out_dir / "peptide.pdb"
    pdbqt_path = out_dir / "peptide.pdbqt"

    built = _build_allatom_pdb(sequence, center, pdb_path, logger)

    if built and shutil.which("obabel"):
        # Sem -xr: obabel em modo ligante gera tipos AD4 corretos (N, OA, SA).
        proc = subprocess.run(
            ["obabel", str(pdb_path), "-O", str(pdbqt_path), "-h"],
            capture_output=True, timeout=60
        )
        if proc.returncode == 0 and pdbqt_path.exists() and pdbqt_path.stat().st_size > 100:
            _ensure_ligand_pdbqt_format(pdbqt_path)
            return pdbqt_path
        if logger:
            logger.warning(f"obabel peptide falhou ({sequence[:8]}): {proc.stderr[:80]}")

    if logger:
        logger.warning(f"Peptide PDBQT fallback (CA-only): {sequence[:8]}")
    return _write_ca_pdbqt(sequence, center, pdbqt_path)


def _build_allatom_pdb(sequence: str, center: list, pdb_path: Path, logger=None) -> bool:
    """Gera PDB all-atom via PeptideBuilder (Ala como fallback por resíduo)."""
    try:
        import PeptideBuilder
        from PeptideBuilder import Geometry
        import Bio.PDB
        import numpy as np

        first_aa = sequence[0] if sequence[0] != "B" else "A"
        try:
            geo = Geometry.geometry(first_aa)
        except Exception:
            geo = Geometry.geometry("A")
        structure = PeptideBuilder.initialize_res(geo)

        for aa in sequence[1:]:
            try:
                g = Geometry.geometry(aa)
            except Exception:
                g = Geometry.geometry("A")
            PeptideBuilder.add_residue(structure, g)

        target = np.array([float(v) for v in center])
        coords = np.array([a.coord for a in structure.get_atoms()])
        com = coords.mean(axis=0)
        offset = target - com
        for atom in structure.get_atoms():
            atom.coord += offset

        io = Bio.PDB.PDBIO()
        io.set_structure(structure)
        io.save(str(pdb_path))
        return True
    except Exception as e:
        if logger:
            logger.warning(f"PeptideBuilder falhou ({sequence[:6]}): {e}")
        return False


def _ensure_ligand_pdbqt_format(pdbqt_path: Path):
    """Força formato ligante rígido: apenas ATOM/HETATM dentro de ROOT/ENDROOT/TORSDOF 0."""
    content = pdbqt_path.read_text()
    atom_lines = [l for l in content.splitlines() if l.startswith(("ATOM", "HETATM"))]
    if not atom_lines:
        return
    with open(pdbqt_path, "w") as f:
        f.write("ROOT\n")
        for line in atom_lines:
            f.write(line.rstrip() + "\n")
        f.write("ENDROOT\n")
        f.write("TORSDOF 0\n")


def _write_ca_pdbqt(sequence: str, center: list, pdbqt_path: Path) -> Path:
    """PDBQT CA-only como último recurso."""
    cx, cy, cz = center
    ad4 = {"R": "N", "K": "N", "H": "N", "D": "OA", "E": "OA", "S": "OA", "T": "OA",
           "Y": "OA", "N": "NA", "Q": "NA", "W": "A", "F": "A", "P": "A"}
    with open(pdbqt_path, "w") as f:
        f.write("ROOT\n")
        for i, aa in enumerate(sequence):
            resname = AA_1TO3.get(aa, "ALA")
            atype = ad4.get(aa, "C")
            f.write(f"ATOM  {i+1:5d}  CA  {resname} B{i+1:4d}    "
                    f"{cx+i*3.8:8.3f}{cy:8.3f}{cz:8.3f}  1.00  0.00"
                    f"    0.000 {atype}\n")
        f.write("ENDROOT\nTORSDOF 0\n")
    return pdbqt_path


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
    """Calcula propriedades físico-químicas completas para dataset ML/DL."""
    if not seq:
        return {}

    # Molecular weight (residue masses, not free amino acids)
    mw_residue = {
        'A': 71.08,  'R': 156.19, 'N': 114.10, 'D': 115.09, 'C': 103.14,
        'Q': 128.13, 'E': 129.12, 'G': 57.05,  'H': 137.14, 'I': 113.16,
        'L': 113.16, 'K': 128.17, 'M': 131.20, 'F': 147.18, 'P': 97.12,
        'S': 87.08,  'T': 101.10, 'W': 186.21, 'Y': 163.18, 'V': 99.13,
    }
    # Kyte-Doolittle hydrophobicity scale
    kd_scale = {
        'A': 1.8,  'R': -4.5, 'N': -3.5, 'D': -3.5, 'C': 2.5,
        'Q': -3.5, 'E': -3.5, 'G': -0.4, 'H': -3.2, 'I': 4.5,
        'L': 3.8,  'K': -3.9, 'M': 1.9,  'F': 2.8,  'P': -1.6,
        'S': -0.8, 'T': -0.7, 'W': -0.9, 'Y': -1.3, 'V': 4.2,
    }
    # Boman index scale (protein-binding potential, Boman 2003)
    boman_scale = {
        'A': 1.15,  'R': 1.91,  'N': 1.91,  'D': -0.12, 'C': 1.36,
        'Q': 1.22,  'E': -0.74, 'G': 1.15,  'H': 0.11,  'I': -1.12,
        'L': -1.25, 'K': 2.02,  'M': -1.02, 'F': -1.71, 'P': 0.14,
        'S': 1.28,  'T': 1.22,  'W': -1.85, 'Y': -1.13, 'V': -0.46,
    }

    n = len(seq)
    mw = sum(mw_residue.get(aa, 111.1) for aa in seq) + 18.02
    hydrophobicity_kd = sum(kd_scale.get(aa, 0) for aa in seq) / n
    boman = sum(boman_scale.get(aa, 0) for aa in seq) / n

    # Net charge at pH 7 (approximate)
    charge = (sum(1 for aa in seq if aa in 'RK')
              - sum(1 for aa in seq if aa in 'DE')
              + sum(0.1 for aa in seq if aa == 'H'))
    # Add N-term (+1) and C-term (-1) at pH 7 → net 0 contribution

    # Aliphatic index: 100 × (A + 2.9×V + 3.9×(I+L)) / n
    aliphatic = 100 * (
        seq.count('A') / n
        + 2.9 * seq.count('V') / n
        + 3.9 * (seq.count('I') + seq.count('L')) / n
    )

    # Instability index (simplified Guruprasad): penalizes DGSW dipeptides
    _instab_pairs = {('D','G'):1,('G','W'):1,('W','N'):1,('N','T'):1}
    instab = 0.0
    for i in range(len(seq) - 1):
        pair = (seq[i], seq[i+1])
        instab += _instab_pairs.get(pair, 0) * 10
    instab_approx = (instab / n) * 10 if n > 1 else 0.0

    # Isoelectric point (binary search)
    pI = _calc_pi(seq)

    # Composition fractions
    aromatic = set('YFWH')
    hydrophobic_set = set('AILMFWV')
    charged_set = set('RKDE')

    frac_aromatic = sum(1 for aa in seq if aa in aromatic) / n
    frac_hydrophobic = sum(1 for aa in seq if aa in hydrophobic_set) / n
    frac_charged = sum(1 for aa in seq if aa in charged_set) / n
    n_arg_lys = sum(1 for aa in seq if aa in 'RK')
    n_asp_glu = sum(1 for aa in seq if aa in 'DE')
    n_aromatic = sum(1 for aa in seq if aa in 'YWF')

    props = {
        "sequence": seq,
        "length": n,
        "mw_da": round(mw, 2),
        "net_charge": round(charge, 2),
        "isoelectric_point": round(pI, 2),
        "hydrophobicity_kd": round(hydrophobicity_kd, 3),
        "boman_index": round(boman, 3),
        "instability_index": round(instab_approx, 2),
        "aliphatic_index": round(aliphatic, 2),
        "frac_aromatic": round(frac_aromatic, 4),
        "frac_hydrophobic": round(frac_hydrophobic, 4),
        "frac_charged": round(frac_charged, 4),
        "n_arg_lys": n_arg_lys,
        "n_asp_glu": n_asp_glu,
        "n_aromatic": n_aromatic,
        "has_aromatic_cterminal": int(seq[-1] in 'YWF') if seq else 0,
        "has_charged_nterminal": int(seq[0] in 'RKD') if seq else 0,
        "has_pro": int('P' in seq),
    }
    # Per-residue fractions (feature columns for ML)
    for aa in "ADEFGHIKLMNPQRSTVWY":
        props[f"frac_{aa}"] = round(seq.count(aa) / n, 4)
    return props


def _calc_pi(seq: str) -> float:
    """Calcula pI por busca binária na curva de titulação."""
    pk_pos = {'R': 12.48, 'K': 10.53, 'H': 6.00}
    pk_neg = {'D': 3.65, 'E': 4.25, 'Y': 10.07, 'C': 8.18}
    pK_nterm = 8.0
    pK_cterm = 3.10

    def charge_at(ph):
        q = 1.0 / (1.0 + 10 ** (ph - pK_nterm))   # N-terminus +
        q -= 1.0 / (1.0 + 10 ** (pK_cterm - ph))   # C-terminus -
        for aa in seq:
            if aa in pk_pos:
                q += 1.0 / (1.0 + 10 ** (ph - pk_pos[aa]))
            if aa in pk_neg:
                q -= 1.0 / (1.0 + 10 ** (pk_neg[aa] - ph))
        return q

    lo, hi = 0.0, 14.0
    for _ in range(100):
        mid = (lo + hi) / 2.0
        if charge_at(mid) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0

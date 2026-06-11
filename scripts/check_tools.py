"""Diagnóstico completo das ferramentas do pipeline.

Uso:
    conda run -n protein_design_env python scripts/check_tools.py
"""
import importlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path.home()

# ─── helpers ──────────────────────────────────────────────────────────────────

def ok(msg):   print(f"  \033[32m✓\033[0m  {msg}")
def fail(msg): print(f"  \033[31m✗\033[0m  {msg}")
def warn(msg): print(f"  \033[33m⚠\033[0m  {msg}")
def head(msg): print(f"\n\033[1m{msg}\033[0m")

def which(cmd):
    return shutil.which(cmd)

def run(cmd, timeout=10):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode == 0, (r.stdout + r.stderr).strip()
    except Exception as e:
        return False, str(e)

def try_import(mod):
    try:
        m = importlib.import_module(mod)
        ver = getattr(m, "__version__", "?")
        return True, ver
    except ImportError as e:
        return False, str(e)

# ─── 1. Python env ────────────────────────────────────────────────────────────

head("1. Ambiente Python")
ok(f"Python {sys.version.split()[0]} — {sys.executable}")
prefix = os.environ.get("CONDA_PREFIX", "?")
print(f"     Conda prefix: {prefix}")

# ─── 2. Dependências Python críticas ─────────────────────────────────────────

head("2. Dependências Python")
deps = [
    ("numpy",         "numpy"),
    ("scipy",         "scipy"),
    ("pandas",        "pandas"),
    ("biopython",     "Bio"),
    ("rdkit",         "rdkit"),
    ("matplotlib",    "matplotlib"),
    ("pyyaml",        "yaml"),
    ("jinja2",        "jinja2"),
    ("PeptideBuilder","PeptideBuilder"),
    ("pdbfixer",      "pdbfixer"),
    ("mdtraj",        "mdtraj"),
    ("mdanalysis",    "MDAnalysis"),
    ("plip",          "plip"),
]
for name, mod in deps:
    ok_, ver = try_import(mod)
    if ok_:
        ok(f"{name} {ver}")
    else:
        fail(f"{name} — {ver}")

# ─── 3. Teste PeptideBuilder ──────────────────────────────────────────────────

head("3. PeptideBuilder — teste all-atom")
try:
    import PeptideBuilder
    from PeptideBuilder import Geometry
    import Bio.PDB
    import numpy as np

    geo = Geometry.geometry("A")
    structure = PeptideBuilder.initialize_res(geo)
    for aa in "RK":
        try:
            g = Geometry.geometry(aa)
        except Exception:
            g = Geometry.geometry("A")
        PeptideBuilder.add_residue(structure, g)

    # Testar atom.coord (o método correto)
    offset = np.array([1.0, 2.0, 3.0])
    for atom in structure.get_atoms():
        atom.coord += offset

    n_atoms = sum(1 for _ in structure.get_atoms())
    ok(f"PeptideBuilder gera estrutura all-atom — {n_atoms} átomos para ARK")
except Exception as e:
    fail(f"PeptideBuilder falhou: {e}")

# ─── 4. obabel ────────────────────────────────────────────────────────────────

head("4. OpenBabel")
ob = which("obabel")
if ob:
    ok_, ver_out = run(["obabel", "--version"])
    ver = ver_out.split("\n")[0] if ver_out else "?"
    ok(f"obabel encontrado: {ob}")
    print(f"     {ver}")

    # Teste SMILES → PDBQT
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test.pdbqt"
        ok2, _ = run(["obabel", "-ismi", "CCC", "-O", str(out), "--gen3d", "-h"])
        if ok2 and out.exists() and out.stat().st_size > 10:
            ok("Conversão SMILES→PDBQT funcional")
        else:
            warn("obabel instalado mas conversão SMILES→PDBQT falhou")
else:
    fail("obabel NÃO encontrado no PATH")
    conda_ob = HOME / "miniforge3/envs/protein_design_env/bin/obabel"
    if conda_ob.exists():
        warn(f"obabel está no env mas não no PATH: {conda_ob}")
        warn("Solução: usar caminho absoluto ou verificar conda run")

# ─── 5. AutoDock Vina ─────────────────────────────────────────────────────────

head("5. AutoDock Vina")
vina = which("vina") or which("autodock_vina")
if vina:
    ok_, ver_out = run([vina, "--version"])
    ver = ver_out.split("\n")[0] if ver_out else "?"
    ok(f"vina encontrado: {vina}")
    print(f"     {ver}")
else:
    fail("vina NÃO encontrado")
    warn("Instalar: mamba install -n protein_design_env -c conda-forge vina -y")

# ─── 6. GROMACS ───────────────────────────────────────────────────────────────

head("6. GROMACS")
gmx_found = None
for candidate in ["gmx_mpi", "gmx"]:
    p = which(candidate)
    if p:
        gmx_found = (candidate, p)
        break

if not gmx_found:
    # Busca manual
    search_paths = [
        HOME / "gromacs/bin/gmx_mpi",
        HOME / "gromacs/bin/gmx",
        Path("/usr/local/gromacs/bin/gmx_mpi"),
        Path("/opt/gromacs/bin/gmx_mpi"),
        Path("/usr/bin/gmx_mpi"),
        Path("/usr/bin/gmx"),
    ]
    for sp in search_paths:
        if sp.exists():
            gmx_found = (sp.name, str(sp))
            break

if gmx_found:
    cmd_name, cmd_path = gmx_found
    ok_, ver_out = run([cmd_path, "--version"])
    ver_line = next((l for l in ver_out.splitlines() if "GROMACS" in l.upper()), ver_out[:60])
    ok(f"{cmd_name} encontrado: {cmd_path}")
    print(f"     {ver_line}")
    if cmd_name == "gmx_mpi":
        ok("gmx_mpi (CUDA-MPI build) — compatível com servidor")
    else:
        warn("gmx serial detectado — no servidor usar gmx_mpi + mpirun -np 1")
else:
    fail("GROMACS NÃO encontrado em nenhum caminho padrão")
    # Verificar se existe ~/gromacs
    if (HOME / "gromacs").exists():
        contents = list((HOME / "gromacs").iterdir())[:5]
        warn(f"Diretório ~/gromacs existe: {[c.name for c in contents]}")
        warn("Verifique se o binário está em ~/gromacs/bin/")
    warn("Instalar via conda: mamba install -n protein_design_env -c conda-forge gromacs -y")

# Testar mpirun
mpi = which("mpirun")
if mpi:
    ok(f"mpirun encontrado: {mpi}")
else:
    warn("mpirun não encontrado (necessário para gmx_mpi)")

# ─── 7. fpocket ───────────────────────────────────────────────────────────────

head("7. fpocket")
fp = which("fpocket")
if fp:
    ok_, ver_out = run([fp, "--help"])
    ok(f"fpocket encontrado: {fp}")
else:
    fail("fpocket NÃO encontrado")
    warn("Instalar: mamba install -n protein_design_env -c conda-forge fpocket -y")

# ─── 8. RFdiffusion ───────────────────────────────────────────────────────────

head("8. RFdiffusion")
rf_paths = [
    HOME / "RFdiffusion",
    HOME / "tools/RFdiffusion",
    Path("/opt/RFdiffusion"),
]
rf_found = None
for p in rf_paths:
    if (p / "run_inference.py").exists():
        rf_found = p
        break

if rf_found:
    ok(f"RFdiffusion encontrado: {rf_found}")
    # Verificar modelo de pesos
    weights_dir = rf_found / "models"
    if weights_dir.exists():
        models = list(weights_dir.glob("*.pt"))
        if models:
            ok(f"Pesos: {[m.name for m in models[:3]]}")
        else:
            warn("Diretório models/ existe mas sem arquivos .pt")
    else:
        warn("Diretório models/ não encontrado — baixar pesos!")
        warn("  bash scripts/download_rfdiffusion_weights.sh")
else:
    fail("RFdiffusion NÃO encontrado")
    warn("Instalar:")
    warn("  git clone https://github.com/RosettaCommons/RFdiffusion ~/RFdiffusion")
    warn("  conda run -n protein_design_env pip install ~/RFdiffusion/")
    warn("  # + baixar pesos (~2 GB)")

# ─── 9. ProteinMPNN ───────────────────────────────────────────────────────────

head("9. ProteinMPNN")
mpnn_paths = [
    HOME / "ProteinMPNN",
    HOME / "tools/ProteinMPNN",
    Path("/opt/ProteinMPNN"),
]
mpnn_found = None
for p in mpnn_paths:
    if (p / "protein_mpnn_run.py").exists():
        mpnn_found = p
        break

if mpnn_found:
    ok(f"ProteinMPNN encontrado: {mpnn_found}")
else:
    fail("ProteinMPNN NÃO encontrado")
    warn("Instalar:")
    warn("  git clone https://github.com/dauparas/ProteinMPNN ~/ProteinMPNN")

# ─── 10. Rosetta / PyRosetta ─────────────────────────────────────────────────

head("10. Rosetta / PyRosetta")
ok_, ver = try_import("pyrosetta")
if ok_:
    ok(f"PyRosetta {ver}")
else:
    fail("PyRosetta não instalado")
    warn("Licença gratuita academia: https://www.pyrosetta.org/downloads")
    warn("  conda run -n protein_design_env pip install pyrosetta-installer")
    warn("  conda run -n protein_design_env python -c \"import pyrosetta_installer; pyrosetta_installer.install_pyrosetta()\"")

# ─── 11. GPU ──────────────────────────────────────────────────────────────────

head("11. GPU (CUDA)")
ok_, gpu_out = run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"])
if ok_:
    for line in gpu_out.splitlines():
        ok(f"GPU: {line.strip()}")
else:
    warn("nvidia-smi não disponível")

# Verificar PyTorch + CUDA
ok_, pt_ver = try_import("torch")
if ok_:
    try:
        import torch
        cuda_avail = torch.cuda.is_available()
        if cuda_avail:
            ok(f"PyTorch {pt_ver} + CUDA disponível ({torch.cuda.get_device_name(0)})")
        else:
            warn(f"PyTorch {pt_ver} instalado mas CUDA não disponível")
    except Exception:
        ok(f"PyTorch {pt_ver}")
else:
    warn("PyTorch não instalado (necessário para RFdiffusion e ProteinMPNN)")
    warn("  mamba install -n protein_design_env -c pytorch -c nvidia pytorch pytorch-cuda=12.1 -y")

# ─── Resumo ───────────────────────────────────────────────────────────────────

print("\n" + "═"*60)
print("  RESUMO — ferramentas críticas para próximos passos")
print("═"*60)

tools_status = {
    "obabel (PDBQT)":    bool(which("obabel")),
    "vina (docking)":    bool(which("vina") or which("autodock_vina")),
    "GROMACS (MD)":      bool(gmx_found),
    "fpocket (bolso)":   bool(which("fpocket")),
    "RFdiffusion":       bool(rf_found),
    "ProteinMPNN":       bool(mpnn_found),
    "PyRosetta":         try_import("pyrosetta")[0],
    "PeptideBuilder":    try_import("PeptideBuilder")[0],
    "PyTorch":           try_import("torch")[0],
}

for tool, status in tools_status.items():
    if status:
        ok(tool)
    else:
        fail(tool)

print()

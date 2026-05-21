#!/usr/bin/env bash
# ============================================================
# setup.sh — Instalação do ambiente e ferramentas
# Design de Inibidores Peptídicos de Tripsina de Lepidoptera
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_NAME="protein_design_env"

echo "═══════════════════════════════════════════════════════"
echo "  Design de Inibidores de Tripsina — Lepidoptera"
echo "  Setup de Ambiente"
echo "═══════════════════════════════════════════════════════"

# ── Detecta mamba/conda ──────────────────────────────────────
CONDA_CMD=""
for cmd in mamba conda; do
    if command -v "$cmd" &>/dev/null; then
        CONDA_CMD="$cmd"
        break
    fi
done
if [ -z "${CONDA_CMD}" ]; then
    echo "ERRO: mamba ou conda não encontrado."
    echo "Instale o Miniforge: https://github.com/conda-forge/miniforge"
    exit 1
fi
echo "Usando: $CONDA_CMD"

# ── Flag --clean: remove ambiente existente ──────────────────
if [[ "${1:-}" == "--clean" ]]; then
    echo ""
    echo ">>> --clean: removendo ambiente '${ENV_NAME}'..."
    $CONDA_CMD env remove -n "$ENV_NAME" --yes 2>/dev/null || true
    echo "    Ambiente removido."
fi

# ── Instala ou atualiza o ambiente ───────────────────────────
install_env() {
    local yml="$1"
    local env_name
    env_name=$(grep "^name:" "$yml" | awk '{print $2}')
    if $CONDA_CMD env list | grep -q "^${env_name}[[:space:]]"; then
        echo "  Ambiente '${env_name}' existe — atualizando..."
        $CONDA_CMD env update -n "$env_name" -f "$yml" --prune
    else
        echo "  Criando '${env_name}'..."
        $CONDA_CMD env create -f "$yml"
    fi
}

echo ""
echo "Instalando ambiente Conda/Mamba..."
install_env "$SCRIPT_DIR/environment.yml"

# ── Pacotes pip extras (instalados com conda run) ────────────
echo ""
echo "Instalando pacotes pip extras..."
$CONDA_CMD run -n "$ENV_NAME" pip install --quiet \
    biopandas \
    pdbfixer \
    PeptideBuilder \
    plip \
    markdown \
    || echo "  Aviso: alguns pacotes pip falharam (não críticos)"

# ── Estrutura de diretórios de saída ─────────────────────────
echo ""
echo "Criando estrutura de diretórios..."
for d in outputs/structure \
          outputs/rfdiffusion \
          outputs/proteinmpnn \
          outputs/rosetta \
          outputs/docking \
          outputs/md \
          outputs/ranking \
          outputs/visualizations \
          outputs/reports \
          outputs/optimization \
          logs; do
    mkdir -p "$SCRIPT_DIR/$d"
done

# ── Validação ────────────────────────────────────────────────
echo ""
echo "Validando instalação..."

validate_tool() {
    local tool="$1"
    if $CONDA_CMD run -n "$ENV_NAME" which "$tool" &>/dev/null; then
        echo "  ✓ $tool"
    else
        echo "  ✗ $tool — não encontrado em ${ENV_NAME}"
    fi
}

validate_python_pkg() {
    local pkg="$1"
    local import="${2:-$1}"
    if $CONDA_CMD run -n "$ENV_NAME" python -c "import ${import}" &>/dev/null; then
        echo "  ✓ $pkg (python)"
    else
        echo "  ✗ $pkg (python) — não encontrado"
    fi
}

validate_tool gmx
validate_tool vina
validate_tool fpocket
validate_python_pkg numpy
validate_python_pkg pandas
validate_python_pkg biopython Bio
validate_python_pkg mdtraj
validate_python_pkg matplotlib
validate_python_pkg rdkit
validate_python_pkg PeptideBuilder

# Ferramentas opcionais (não causam erro)
echo ""
echo "Ferramentas opcionais (instalar manualmente se necessário):"
for dir in "$HOME/RFdiffusion" "$HOME/rf_diffusion" /opt/RFdiffusion; do
    if [ -d "$dir" ]; then
        echo "  ✓ RFdiffusion  ($dir)"
        break
    fi
done
if ! compgen -G "$HOME/RFdiffusion" &>/dev/null && \
   ! compgen -G "/opt/RFdiffusion" &>/dev/null; then
    echo "  ~ RFdiffusion  (não instalado — usar heurística)"
fi

for dir in "$HOME/ProteinMPNN" /opt/ProteinMPNN; do
    if [ -d "$dir" ]; then
        echo "  ✓ ProteinMPNN  ($dir)"
        break
    fi
done
if ! compgen -G "$HOME/ProteinMPNN" &>/dev/null && \
   ! compgen -G "/opt/ProteinMPNN" &>/dev/null; then
    echo "  ~ ProteinMPNN  (não instalado — usar heurística)"
fi

if $CONDA_CMD run -n "$ENV_NAME" python -c "import pyrosetta" &>/dev/null 2>&1; then
    echo "  ✓ PyRosetta"
else
    echo "  ~ PyRosetta    (não instalado — usar heurística)"
fi

# ── Versões ──────────────────────────────────────────────────
echo ""
GMX_VER=$($CONDA_CMD run -n "$ENV_NAME" gmx --version 2>&1 | grep "GROMACS version" | awk '{print $NF}' || echo "N/A")
VINA_VER=$($CONDA_CMD run -n "$ENV_NAME" vina --version 2>&1 | head -1 || echo "N/A")
PY_VER=$($CONDA_CMD run -n "$ENV_NAME" python --version 2>&1 || echo "N/A")
echo "  Python  : $PY_VER"
echo "  GROMACS : $GMX_VER"
echo "  Vina    : $VINA_VER"

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  Setup concluído!"
echo ""
echo "  Próximos passos:"
echo "  1. Verifique as ferramentas acima"
echo "  2. Execute: bash executavel.sh check"
echo "  3. Execute: bash executavel.sh design"
echo ""
echo "  Para recriar o ambiente do zero:"
echo "  bash setup.sh --clean"
echo "═══════════════════════════════════════════════════════"

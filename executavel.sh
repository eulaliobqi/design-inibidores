#!/bin/bash
# =============================================================================
# executavel.sh — Script de instalação e execução do pipeline
# Design de Inibidores Peptídicos de Tripsina de Lepidoptera
# =============================================================================
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# ─────────────────────────────────────────────────────────────
# PARTE 1: Criar e ativar ambiente
# ─────────────────────────────────────────────────────────────
echo ">>> Criando ambiente Mamba..."
mamba env create -f environment.yml --yes || conda env create -f environment.yml --yes
conda activate protein_design_env

# ─────────────────────────────────────────────────────────────
# PARTE 2: Instalar ferramentas externas (manual)
# ─────────────────────────────────────────────────────────────

# RFdiffusion (requer CUDA)
# git clone https://github.com/RosettaCommons/RFdiffusion.git $HOME/RFdiffusion
# cd $HOME/RFdiffusion && pip install -e .

# ProteinMPNN
# git clone https://github.com/dauparas/ProteinMPNN.git $HOME/ProteinMPNN

# PyRosetta (licença gratuita academia: pyrosetta.org/downloads)
# python -c "import pyrosetta_installer; pyrosetta_installer.install_pyrosetta()"

# Verificar GPU
echo ">>> Verificando GPU..."
nvidia-smi 2>/dev/null && echo "GPU disponível" || echo "GPU não detectada (CPU mode)"

# ─────────────────────────────────────────────────────────────
# PARTE 3: Executar pipeline
# ─────────────────────────────────────────────────────────────

case "${1:-all}" in

  "check")
    # Verifica ferramentas sem executar
    python scripts/run_pipeline.py --config config.yaml --dry-run
    ;;

  "structure")
    # Apenas mapear o sítio S1
    python scripts/run_pipeline.py --config config.yaml --step structure
    ;;

  "design")
    # Gerar e ranquear candidatos (sem MD)
    python scripts/run_pipeline.py --config config.yaml --step structure
    python scripts/run_pipeline.py --config config.yaml --step rfdiffusion --resume
    python scripts/run_pipeline.py --config config.yaml --step mpnn --resume
    python scripts/run_pipeline.py --config config.yaml --step rosetta --resume
    python scripts/run_pipeline.py --config config.yaml --step docking --resume
    python scripts/run_pipeline.py --config config.yaml --step ranking --resume
    python scripts/run_pipeline.py --config config.yaml --step visualize --resume
    python scripts/run_pipeline.py --config config.yaml --step report --resume
    ;;

  "all")
    # Pipeline completo (com MD)
    python scripts/run_pipeline.py \
      --config config.yaml \
      --step all
    ;;

  "resume")
    # Retomar do último checkpoint
    python scripts/run_pipeline.py \
      --config config.yaml \
      --step all \
      --resume
    ;;

  "optimize")
    # Redesign iterativo (após ranking concluído)
    ITER="${2:-1}"
    python scripts/run_pipeline.py \
      --config config.yaml \
      --step optimize \
      --iter "$ITER" \
      --resume
    ;;

  "report")
    # Apenas gerar relatório final
    python scripts/run_pipeline.py \
      --config config.yaml \
      --step report \
      --resume
    ;;

  *)
    echo "Uso: $0 [check|structure|design|all|resume|optimize|report]"
    echo ""
    echo "  check     — verifica ferramentas instaladas"
    echo "  structure — apenas mapeia o sítio S1"
    echo "  design    — gera candidatos sem MD (rápido)"
    echo "  all       — pipeline completo com MD"
    echo "  resume    — retoma do último checkpoint"
    echo "  optimize  — redesign iterativo (arg: iteração)"
    echo "  report    — gera relatório dos resultados existentes"
    ;;

esac

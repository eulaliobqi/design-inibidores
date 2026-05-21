#!/usr/bin/env bash
# ============================================================
# executavel.sh — Execução do pipeline de design de inibidores
# Design de Inibidores Peptídicos de Tripsina de Lepidoptera
# ============================================================
# Requer ambiente instalado: bash setup.sh
# Não ativa o ambiente — usa 'conda run' em cada chamada.
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_NAME="protein_design_env"

# ── Detecta conda/mamba ──────────────────────────────────────
CONDA_CMD=""
for cmd in mamba conda; do
    if command -v "$cmd" &>/dev/null; then
        CONDA_CMD="$cmd"
        break
    fi
done
if [ -z "${CONDA_CMD}" ]; then
    echo "ERRO: conda/mamba não encontrado. Execute: bash setup.sh"
    exit 1
fi

# Verifica se o ambiente existe
if ! $CONDA_CMD env list | grep -q "^${ENV_NAME}[[:space:]]"; then
    echo "ERRO: ambiente '${ENV_NAME}' não encontrado."
    echo "Execute primeiro: bash setup.sh"
    exit 1
fi

RUN="$CONDA_CMD run --no-capture-output -n $ENV_NAME"
PY="$RUN python $SCRIPT_DIR/scripts/run_pipeline.py --config $SCRIPT_DIR/config.yaml"

# ── Ações ────────────────────────────────────────────────────
case "${1:-all}" in

  "check")
    echo ">>> Verificando GPU..."
    $RUN nvidia-smi 2>/dev/null && echo "GPU disponível" || echo "GPU não detectada (CPU mode)"
    echo ""
    $PY --dry-run
    ;;

  "structure")
    $PY --step structure
    ;;

  "design")
    # Etapas 1–8 sem MD (rápido: 5–15 min)
    $PY --step structure
    $PY --step rfdiffusion --resume
    $PY --step mpnn        --resume
    $PY --step rosetta     --resume
    $PY --step docking     --resume
    $PY --step ranking     --resume
    $PY --step visualize   --resume
    $PY --step report      --resume
    ;;

  "all")
    # Pipeline completo com MD (~horas)
    $PY --step all
    ;;

  "resume")
    $PY --step all --resume
    ;;

  "optimize")
    ITER="${2:-1}"
    $PY --step optimize --iter "$ITER" --resume
    ;;

  "report")
    $PY --step report --resume
    ;;

  *)
    echo "Uso: bash executavel.sh [check|structure|design|all|resume|optimize <N>|report]"
    echo ""
    echo "  check        — verifica ferramentas e GPU"
    echo "  structure    — mapeia o sítio S1 nos 4 PDBs"
    echo "  design       — gera e rankeia candidatos sem MD (rápido)"
    echo "  all          — pipeline completo com MD"
    echo "  resume       — retoma do último checkpoint"
    echo "  optimize <N> — redesign iterativo (N = iteração)"
    echo "  report       — gera relatório dos resultados existentes"
    ;;

esac

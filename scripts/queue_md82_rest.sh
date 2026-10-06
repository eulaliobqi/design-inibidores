#!/bin/bash
# queue_md82_rest.sh FRONT -- completa as MDs de 10 ns em pH 8,2 dos 24 candidatos finais da frente (L ou M): espera a
# primeira leva (finalistas, md82-FRONT) terminar e roda as demais; o runner pula as que ja estao concluidas.
# Marcador final: MD82ALL_<FRONT>_DONE em outputs/md82_<FRONT>_rest.log.
# Uso: screen -dmS md82rest-L bash -c 'cd ~/design-inibidores && bash scripts/queue_md82_rest.sh L >> outputs/md82_L_rest.log 2>&1'
# (sem `set -u`: o gromacs_deactivate.sh do env referencia variaveis nao definidas.)
F=$1
cd "$(dirname "$0")/.."
source ~/miniforge3/etc/profile.d/conda.sh
conda activate protein_design_env
echo "[rest-$F] $(date) aguardando MD82_${F}_DONE"
until grep -q "MD82_${F}_DONE" outputs/md82_$F.log 2>/dev/null; do sleep 300; done
KEYS=$(python -c "import json;print(' '.join(json.load(open('outputs/md10_$F/summary.json')).keys()))")
echo "[rest-$F] $(date) 24 candidatos: $KEYS"
python -m scripts.run_md_ph_campaign --candidates data-b23-scoring/results/top_candidates_$F.json --workdir outputs/md82_$F --front $F --ph 8.2 --ns 10 --keys $KEYS
echo "MD82ALL_${F}_DONE $(date)"

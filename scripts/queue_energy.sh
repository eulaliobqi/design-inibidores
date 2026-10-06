#!/bin/bash
# queue_energy.sh -- etapa de energia: MM-GBSA (GB) + PRODIGY nos quadros das MDs de pH 8,2, rodados conforme cada MD termina,
# e ranking final por etapa e agregado. Marcador final: QUEUE_ENERGY_DONE em outputs/queue_energy.log.
# Uso: screen -dmS energy-queue bash -c 'cd ~/design-inibidores && bash scripts/queue_energy.sh >> outputs/queue_energy.log 2>&1'
# (sem `set -u`: o gromacs_deactivate.sh do env referencia variaveis nao definidas.)
cd "$(dirname "$0")/.."
source ~/miniforge3/etc/profile.d/conda.sh
conda activate protein_design_env
echo "[energy] $(date) iniciado"
while true; do
  for F in L M; do
    python -m scripts.mmgbsa_md82 --front $F >> outputs/mmgbsa_md82_$F.log 2>&1
  done
  if grep -q MD82_L_DONE outputs/md82_L.log && grep -q MD82_M_DONE outputs/md82_M.log; then
    # uma passada final depois que as duas MDs terminaram (pega as ultimas)
    for F in L M; do python -m scripts.mmgbsa_md82 --front $F >> outputs/mmgbsa_md82_$F.log 2>&1; done
    break
  fi
  echo "[energy] $(date) aguardando MDs de pH 8,2"
  sleep 1200
done
python -m scripts.rank_energy_stages --stages all --pool finalists --out outputs/ranking_energy_final
echo "QUEUE_ENERGY_DONE $(date)"

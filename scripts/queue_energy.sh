#!/bin/bash
# queue_energy.sh -- etapa de energia sobre as MDs de 10 ns em pH 8,2 dos 48 candidatos finais: MM-GBSA (GB) + PRODIGY nos
# quadros, rodados conforme cada MD termina; ao fim, analise das trajetorias (mesmos criterios da Secao 2.9) e ranking por
# etapa e agregado. Marcador final: QUEUE_ENERGY_DONE em outputs/queue_energy.log.
# Espera os marcadores MD82ALL_L_DONE e MD82ALL_M_DONE de queue_md82_rest.sh.
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
  if grep -q MD82ALL_L_DONE outputs/md82_L_rest.log 2>/dev/null && grep -q MD82ALL_M_DONE outputs/md82_M_rest.log 2>/dev/null; then
    for F in L M; do python -m scripts.mmgbsa_md82 --front $F >> outputs/mmgbsa_md82_$F.log 2>&1; done
    break
  fi
  echo "[energy] $(date) aguardando as MDs de pH 8,2 ($(ls outputs/md82_L outputs/md82_M 2>/dev/null | grep -c '__r') de 48 iniciadas)"
  sleep 1200
done
for F in L M; do
  python -m scripts.analyze_md_top_candidates --md-dir outputs/md82_$F >> outputs/analyze_md82_$F.log 2>&1
done
python -m scripts.rank_energy_stages --stages all --pool gated --md-source md82 --out outputs/ranking_energy_final
echo "QUEUE_ENERGY_DONE $(date)"

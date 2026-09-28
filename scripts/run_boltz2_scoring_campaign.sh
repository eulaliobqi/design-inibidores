#!/bin/bash
# run_boltz2_scoring_campaign.sh -- pontua com Boltz-2 todos os candidatos RESISTENTE
# a protease da campanha B2.3 (outputs/b23_cleavage_analysis.json), especie por especie.
# Roda em screen (regra do projeto: nunca nohup & para jobs longos, ver CLAUDE.md).
#
# Uso: screen -S b23-boltz2-scoring
#      bash scripts/run_boltz2_scoring_campaign.sh
set -e
cd ~/design-inibidores
source ~/miniforge3/etc/profile.d/conda.sh
conda activate boltz2-env

SPECIES="Sfrugiperda Slitura Onubilalis Dsaccharalis Cincludens Hvirescens Pxylostella"

for sp in $SPECIES; do
  echo "============================================================"
  echo "[$sp] $(date) -- write-yaml"
  python scripts/score_boltz2_b23.py write-yaml --species "$sp"

  echo "[$sp] $(date) -- boltz predict"
  boltz predict "data-b23-scoring/boltz_yaml/$sp" --model boltz2 \
      --out_dir "outputs/b23_boltz2_$sp" --output_format pdb --preprocessing-threads 4

  echo "[$sp] $(date) -- collect"
  python scripts/score_boltz2_b23.py collect --species "$sp"

  echo "[$sp] concluido: outputs/b23_boltz2_$sp/"
done

echo "============================================================"
echo "BOLTZ2_SCORING_ALL_DONE $(date)"

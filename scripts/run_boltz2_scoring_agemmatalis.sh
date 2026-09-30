#!/bin/bash
# run_boltz2_scoring_agemmatalis.sh -- MSA do receptor + scoring Boltz-2 dos candidatos
# RESISTENTE de Anticarsia gemmatalis (8a especie). Mesmo protocolo de
# run_boltz2_scoring_campaign.sh, com cleavage json proprio.
# Uso: screen -S b27-boltz2-agem ; bash scripts/run_boltz2_scoring_agemmatalis.sh
set -e
cd ~/design-inibidores
source ~/miniforge3/etc/profile.d/conda.sh
sp=Agemmatalis
CLV=outputs/b23_cleavage_analysis_Agemmatalis.json

conda activate boltz2-env
echo "[$sp] $(date) -- MSA receptor"
python scripts/precompute_receptor_msa.py --species $sp
echo "[$sp] $(date) -- write-yaml"
python scripts/score_boltz2_b23.py write-yaml --species $sp --cleavage-json $CLV
echo "[$sp] $(date) -- boltz predict"
boltz predict "data-b23-scoring/boltz_yaml/$sp" --model boltz2 \
    --out_dir "outputs/b23_boltz2_$sp" --output_format pdb --preprocessing-threads 4
echo "[$sp] $(date) -- collect"
python scripts/score_boltz2_b23.py collect --species $sp
echo "BOLTZ2_AGEM_DONE $(date)"

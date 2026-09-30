#!/bin/bash
# run_e1_boltz2_two_fronts.sh -- E1 do plano v3: Boltz-2 (1 amostra, protocolo identico ao braco
# macrociclico anterior) dos candidatos RESISTENTE pelo criterio DURO (nenhum sitio para tripsina /
# quimotripsina-like / elastase-like de Lepidoptera), nas duas frentes:
#   L (linear, cyclic:false)  e  M (macrociclo, cyclic:true).
# Resume-safe. Uso: screen -S e1-two-fronts ; bash scripts/run_e1_boltz2_two_fronts.sh
set -e
cd ~/design-inibidores
source ~/miniforge3/etc/profile.d/conda.sh
SP8="Sfrugiperda Slitura Onubilalis Dsaccharalis Cincludens Hvirescens Pxylostella Agemmatalis"

conda activate protein_design_env
[ -f outputs/b23_cleavage_linear_hard.json ] || ( cd scripts && python run_cleavage_b23.py --species $SP8 \
   --geometric-p1 data-lepidoptera-panel/geometric_p1_all8.json --out outputs/b23_cleavage_linear_hard.json )
[ -f outputs/b23_cleavage_circular_hard.json ] || ( cd scripts && python run_cleavage_b23.py --species $SP8 --circular \
   --geometric-p1 data-lepidoptera-panel/geometric_p1_all8.json --out outputs/b23_cleavage_circular_hard.json )

conda activate boltz2-env
for front in L M; do
  if [ $front = L ]; then CLV=outputs/b23_cleavage_linear_hard.json;   YAML=data-b23-scoring/boltz_yaml_L; BOUT=outputs/b23_boltz2_L; CYC="";
  else                     CLV=outputs/b23_cleavage_circular_hard.json; YAML=data-b23-scoring/boltz_yaml_M; BOUT=outputs/b23_boltz2_M; CYC="--cyclic"; fi
  SCORES=data-b23-scoring/results/b23_boltz2_${front}_scores.json
  for sp in $SP8; do
    python scripts/score_boltz2_b23.py write-yaml --species $sp --cleavage-json $CLV --yaml-dir $YAML $CYC
    n_yaml=$(ls $YAML/$sp/*.yaml | wc -l)
    n_done=$(ls ${BOUT}_$sp/boltz_results_$sp/predictions 2>/dev/null | wc -l)
    if [ "$n_done" -lt "$n_yaml" ]; then
      echo "[$front:$sp] $(date) boltz predict ($n_done/$n_yaml prontos)"
      boltz predict "$YAML/$sp" --model boltz2 --out_dir "${BOUT}_$sp" --output_format pdb --preprocessing-threads 4
    fi
    python scripts/score_boltz2_b23.py collect --species $sp --yaml-dir $YAML --boltz-out-prefix $BOUT --out $SCORES
  done
done
echo "E1_TWO_FRONTS_DONE $(date)"

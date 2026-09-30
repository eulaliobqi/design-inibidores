#!/bin/bash
# run_linear_pipeline.sh -- cadeia do manuscrito em forma LINEAR (decisao de escopo 2026-09-30):
# clivagem linear estrita (8 especies) -> Boltz-2 com peptideo linear -> top-1 por especie ->
# MD 50 ns (topologia linear, coerente com o complexo de partida) -> A. gemmatalis em 3 replicas ->
# analise -> comparacao linear x macrociclo. Resume-safe (cada etapa pula o que ja existe).
# Os resultados macrociclicos (cyclic:true, regra circular) permanecem em seus diretorios
# como bracos de COMPARACAO e nao sao tocados.
# Uso: screen -S linear-pipeline ; bash scripts/run_linear_pipeline.sh
set -e
cd ~/design-inibidores
source ~/miniforge3/etc/profile.d/conda.sh
SP8="Sfrugiperda Slitura Onubilalis Dsaccharalis Cincludens Hvirescens Pxylostella Agemmatalis"
CLV=outputs/b23_cleavage_linear_strict.json
YAML=data-b23-scoring/boltz_yaml_linear
BOUT=outputs/b23_boltz2_linear
SCORES=data-b23-scoring/results/b23_boltz2_linear_scores.json
TOP=data-b23-scoring/results/top_candidates_linear.json
MDDIR=outputs/md_top_candidates_linear

conda activate protein_design_env
echo "[1] $(date) clivagem linear estrita"
if [ ! -f $CLV ]; then
  ( cd scripts && python run_cleavage_b23.py --species $SP8 \
      --geometric-p1 data-lepidoptera-panel/geometric_p1_all8.json --out $CLV )
fi

conda activate boltz2-env
for sp in $SP8; do
  echo "[2:$sp] $(date) write-yaml (linear)"
  [ -f data-b23-scoring/msa_cache/receptor_$sp.csv ] || python scripts/precompute_receptor_msa.py --species $sp
  python scripts/score_boltz2_b23.py write-yaml --species $sp --cleavage-json $CLV --yaml-dir $YAML
  n_yaml=$(ls $YAML/$sp/*.yaml | wc -l)
  n_done=$(ls $BOUT"_"$sp/boltz_results_$sp/predictions 2>/dev/null | wc -l)
  if [ "$n_done" -lt "$n_yaml" ]; then
    echo "[2:$sp] $(date) boltz predict ($n_done/$n_yaml ja prontos)"
    boltz predict "$YAML/$sp" --model boltz2 --out_dir "${BOUT}_$sp" --output_format pdb \
        --preprocessing-threads 4
  fi
  python scripts/score_boltz2_b23.py collect --species $sp --yaml-dir $YAML \
      --boltz-out-prefix $BOUT --out $SCORES
done

conda activate protein_design_env
echo "[3] $(date) top-1 por especie (RESISTENTE linear estrito, maior confidence_score)"
python scripts/select_top_candidates.py --rule linear-strict --cleavage $CLV --scores $SCORES \
    --manifests $YAML/_manifests --boltz-out-prefix $BOUT --out $TOP

echo "[4] $(date) MD 50 ns, topologia linear: A. gemmatalis primeiro, depois as demais"
python -m scripts.run_md_top_candidates --candidates $TOP --workdir $MDDIR --species Agemmatalis
python -m scripts.run_md_top_candidates --candidates $TOP --workdir $MDDIR

echo "[5] $(date) A. gemmatalis: replicas 2 e 3 (velocidades iniciais com semente aleatoria)"
for r in 2 3; do
  python -m scripts.run_md_top_candidates --candidates $TOP --workdir ${MDDIR}_rep$r --species Agemmatalis
done

echo "[6] $(date) analise (ocupancia S1, triade, RMSD local com PBC)"
for d in $MDDIR ${MDDIR}_rep2 ${MDDIR}_rep3; do
  python -m scripts.analyze_md_top_candidates --md-dir $d
done

echo "[7] $(date) comparacao linear x macrociclo"
python scripts/compare_linear_vs_macrocycle.py
echo "LINEAR_PIPELINE_ALL_DONE $(date)"

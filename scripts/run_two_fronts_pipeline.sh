#!/bin/bash
# run_two_fronts_pipeline.sh -- cadeia E2..E9 do plano v3 (docs/PLANO_LINEAR_2026-09-30.md), duas frentes:
#   L = peptideo linear   M = macrociclo cabeca-cauda (topologia ciclica via tleap)
# Pre-requisito: E1 concluido (scripts/run_e1_boltz2_two_fronts.sh). Este script ESPERA o E1.
# Resume-safe. MD de triagem de 10 ns, top-3 por especie e frente; o autor roda a MD longa nos melhores.
# Uso: screen -S two-fronts ; bash scripts/run_two_fronts_pipeline.sh
set -e
cd ~/design-inibidores
source ~/miniforge3/etc/profile.d/conda.sh
SP8="Sfrugiperda Slitura Onubilalis Dsaccharalis Cincludens Hvirescens Pxylostella Agemmatalis"
RES=data-b23-scoring/results
BOLTZ_ROBUST="--model boltz2 --diffusion_samples 5 --recycling_steps 3 --sampling_steps 200 --use_potentials --output_format pdb --preprocessing-threads 4"
# boltz predict com timeout e 1 nova tentativa (em 30/09 o pre-processamento travou 56 min sem erro; o Boltz retoma do que ja processou)
bz() { timeout 3h boltz predict "$@" || { echo "[bz] falhou/timeout, nova tentativa: $*"; timeout 3h boltz predict "$@"; }; }
rule_of() { [ "$1" = L ] && echo linear-strict-hard || echo circular-hard; }
clv_of()  { [ "$1" = L ] && echo outputs/b23_cleavage_linear_hard.json || echo outputs/b23_cleavage_circular_hard.json; }

echo "[0] $(date) aguardando E1..."
until grep -q E1_TWO_FRONTS_DONE outputs/e1_two_fronts.log 2>/dev/null; do sleep 300; done

conda activate boltz2-env
for F in L M; do
  echo "[E2:$F] $(date) prepare (top-10 + 3 controles embaralhados)"
  ( cd scripts && python rescore_boltz2_topk.py prepare --front $F --k 10 --n-decoys 3 )
  for seed in 1 2 3; do
    for sp in $SP8; do
      out=outputs/b23_boltz2_E2_${F}_s${seed}_$sp
      n_yaml=$(ls $RES/boltz_yaml_E2_$F/$sp/*.yaml 2>/dev/null | wc -l)
      n_done=$(ls $out/boltz_results_$sp/predictions 2>/dev/null | wc -l)
      [ "$n_yaml" -gt 0 ] && [ "$n_done" -lt "$n_yaml" ] && \
        bz $RES/boltz_yaml_E2_$F/$sp $BOLTZ_ROBUST --seed $seed --out_dir $out
    done
  done
  ( cd scripts && python rescore_boltz2_topk.py collect --front $F --tag E2 --seeds 1 2 3 )
done

conda activate protein_design_env
for F in L M; do
  echo "[E2b:$F] $(date) top-3 por especie (maior confianca media, sequencias distintas)"
  python scripts/select_top_candidates.py --rule $(rule_of $F) --k 3 --cleavage $(clv_of $F) \
      --scores $RES/b23_boltz2_E2_${F}_scores.json --manifests $RES/manifests_E2_$F \
      --out $RES/top_candidates_$F.json
  echo "[E4:$F] $(date) QC de pose"
  ( cd scripts && python pose_qc.py qc --candidates ../$RES/top_candidates_$F.json --front $F --out ../outputs/pose_qc_$F.json )
done

echo "[E6] $(date) MD de triagem 10 ns (A. gemmatalis primeiro), frentes L e M"
for F in L M; do
  python -m scripts.run_md_top_candidates --candidates $RES/top_candidates_$F.json --workdir outputs/md10_$F \
      --ns 10 --front $F --species Agemmatalis
done
for F in L M; do
  python -m scripts.run_md_top_candidates --candidates $RES/top_candidates_$F.json --workdir outputs/md10_$F \
      --ns 10 --front $F
done
echo "[E7] $(date) analise da MD"
for F in L M; do
  python -m scripts.analyze_md_top_candidates --md-dir outputs/md10_$F
done

conda activate boltz2-env
for F in L M; do
  echo "[E3:$F] $(date) controles embaralhados (3 sementes)"
  for seed in 1 2 3; do
    for sp in $SP8; do
      out=outputs/b23_boltz2_E3_${F}_s${seed}_$sp
      n_yaml=$(ls $RES/boltz_yaml_E3_$F/$sp/*.yaml 2>/dev/null | wc -l)
      n_done=$(ls $out/boltz_results_$sp/predictions 2>/dev/null | wc -l)
      [ "$n_yaml" -gt 0 ] && [ "$n_done" -lt "$n_yaml" ] && \
        bz $RES/boltz_yaml_E3_$F/$sp $BOLTZ_ROBUST --seed $seed --out_dir $out
    done
  done
  ( cd scripts && python rescore_boltz2_topk.py collect --front $F --tag E3 --seeds 1 2 3 && python rescore_boltz2_topk.py delta --front $F )
  echo "[E4m:$F] $(date) matriz cruzada 8x8 (top-1)"
  ( cd scripts && python pose_qc.py matrix-prepare --candidates ../$RES/top_candidates_$F.json --front $F )
  for tsp in $SP8; do
    [ -d $RES/boltz_yaml_matrix_$F/$tsp ] && bz $RES/boltz_yaml_matrix_$F/$tsp --model boltz2 \
        --out_dir outputs/b23_boltz2_matrix_${F}_$tsp --output_format pdb --preprocessing-threads 4
  done
  ( cd scripts && python pose_qc.py matrix-collect --front $F )
done

conda activate protein_design_env
echo "[E8,E9] $(date) comparacao e lista de entrega"
python scripts/compare_linear_vs_macrocycle.py
( cd scripts && python deliver_md_long.py )
echo "TWO_FRONTS_ALL_DONE $(date)"

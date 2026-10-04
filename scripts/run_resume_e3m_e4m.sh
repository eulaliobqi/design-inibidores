#!/bin/bash
# run_resume_e3m_e4m.sh -- retoma o pipeline de duas frentes apos a falha de 04/10 04:09: o E4m (pose_qc matrix-prepare)
# rodou sob boltz2-env, que nao tem MDAnalysis. Aqui: E3 da frente M, delta M, e E4m de L e M com cada passo no env certo.
# Uso: screen -S resume-e3m ; bash scripts/run_resume_e3m_e4m.sh
set -e
cd ~/design-inibidores
source ~/miniforge3/etc/profile.d/conda.sh
SP8="Sfrugiperda Slitura Onubilalis Dsaccharalis Cincludens Hvirescens Pxylostella Agemmatalis"
RES=data-b23-scoring/results
BOLTZ_ROBUST="--model boltz2 --diffusion_samples 5 --recycling_steps 3 --sampling_steps 200 --use_potentials --output_format pdb --preprocessing-threads 1"
bz() { timeout 50m boltz predict "$@" || { echo "[bz] falhou/timeout, nova tentativa: $*"; timeout 50m boltz predict "$@"; }; }
bzfill() {
  local ydir=$1 sp=$2 out=$3; shift 3
  local ny nd try
  ny=$(ls $ydir/*.yaml 2>/dev/null | wc -l)
  for try in 1 2 3; do
    nd=$(ls $out/boltz_results_$sp/predictions 2>/dev/null | wc -l)
    if [ "$ny" -le 0 ] || [ "$nd" -ge "$ny" ]; then return 0; fi
    [ "$try" -gt 1 ] && echo "[bzfill] $(date) $out: $nd/$ny, tentativa $try"
    bz "$ydir" "$@" --out_dir "$out"
  done
  nd=$(ls $out/boltz_results_$sp/predictions 2>/dev/null | wc -l)
  [ "$nd" -lt "$ny" ] && echo "[bzfill] AVISO $out: $nd/$ny predicoes apos 3 tentativas"
  return 0
}
echo "[resume] $(date) E3:M"
conda activate boltz2-env
F=M
for seed in 1 2 3; do for sp in $SP8; do
  bzfill $RES/boltz_yaml_E3_$F/$sp $sp outputs/b23_boltz2_E3_${F}_s${seed}_$sp $BOLTZ_ROBUST --seed $seed
done; done
( cd scripts && python rescore_boltz2_topk.py collect --front M --tag E3 --seeds 1 2 3 && python rescore_boltz2_topk.py delta --front M )
echo "[resume] $(date) E3:M concluido (delta_paired_M)"
for F in L M; do
  echo "[E4m:$F] $(date) matriz cruzada 8x8 (top-1)"
  conda activate protein_design_env
  ( cd scripts && python pose_qc.py matrix-prepare --candidates ../$RES/top_candidates_$F.json --front $F )
  conda activate boltz2-env
  for tsp in $SP8; do
    [ -d $RES/boltz_yaml_matrix_$F/$tsp ] && bz $RES/boltz_yaml_matrix_$F/$tsp --model boltz2 \
        --out_dir outputs/b23_boltz2_matrix_${F}_$tsp --output_format pdb --preprocessing-threads 1
  done
  conda activate protein_design_env
  ( cd scripts && python pose_qc.py matrix-collect --front $F )
done
echo "[E8,E9] $(date) comparacao e lista de entrega"
python scripts/compare_linear_vs_macrocycle.py
( cd scripts && python deliver_md_long.py )
echo "TWO_FRONTS_ALL_DONE $(date)"

#!/bin/bash
# run_e6_resume_nterm.sh -- retoma o E6 em diante (plano v3) depois da decisao de 01/10/2026 de simular o peptideo LINEAR
# com N-terminal NEUTRO (NH2; no pH 10 o pKa medio do alfa-amino, 7,7, deixa <1% protonado; Grimsley, Scholtz e Pace
# 2009, doi 10.1002/pro.19). As MDs lineares anteriores (NH3+) ficam em outputs/md10_L_nh3 como braco de comparacao.
# A frente M (macrociclo, sem terminais) nao muda e retoma de onde estava (o runner pula `status: done`).
# Ordem: L de A. gemmatalis (efeito do N-terminal cedo) -> M restante -> L restante -> E7 -> E3/matriz -> E8/E9.
# Uso: screen -dmS two-fronts-v2 bash -c 'bash scripts/run_e6_resume_nterm.sh >> outputs/e1_fix_pipeline.log 2>&1'
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

conda activate protein_design_env
echo "[E6b] $(date) retomada: linear com N-terminal neutro (NH2/GLY-NH2; Pro inicial mantem PRO-NH2+), A. gemmatalis primeiro"
python -m scripts.run_md_top_candidates --candidates $RES/top_candidates_L.json --workdir outputs/md10_L \
    --ns 10 --front L --species Agemmatalis
echo "[E6b] $(date) macrociclo restante"
python -m scripts.run_md_top_candidates --candidates $RES/top_candidates_M.json --workdir outputs/md10_M --ns 10 --front M
echo "[E6b] $(date) linear restante"
python -m scripts.run_md_top_candidates --candidates $RES/top_candidates_L.json --workdir outputs/md10_L --ns 10 --front L
echo "[E7] $(date) analise da MD"
for F in L M; do
  python -m scripts.analyze_md_top_candidates --md-dir outputs/md10_$F
done
python -m scripts.analyze_md_top_candidates --md-dir outputs/md10_L_nh3

conda activate boltz2-env
for F in L M; do
  echo "[E3:$F] $(date) controles embaralhados (3 sementes)"
  for seed in 1 2 3; do
    for sp in $SP8; do
      out=outputs/b23_boltz2_E3_${F}_s${seed}_$sp
      bzfill $RES/boltz_yaml_E3_$F/$sp $sp $out $BOLTZ_ROBUST --seed $seed
    done
  done
  ( cd scripts && python rescore_boltz2_topk.py collect --front $F --tag E3 --seeds 1 2 3 && python rescore_boltz2_topk.py delta --front $F )
  echo "[E4m:$F] $(date) matriz cruzada 8x8 (top-1)"
  ( cd scripts && python pose_qc.py matrix-prepare --candidates ../$RES/top_candidates_$F.json --front $F )
  for tsp in $SP8; do
    [ -d $RES/boltz_yaml_matrix_$F/$tsp ] && bz $RES/boltz_yaml_matrix_$F/$tsp --model boltz2 \
        --out_dir outputs/b23_boltz2_matrix_${F}_$tsp --output_format pdb --preprocessing-threads 1
  done
  ( cd scripts && python pose_qc.py matrix-collect --front $F )
done

conda activate protein_design_env
echo "[E8,E9] $(date) comparacao e lista de entrega"
python scripts/compare_linear_vs_macrocycle.py
( cd scripts && python deliver_md_long.py )
echo "TWO_FRONTS_ALL_DONE $(date)"

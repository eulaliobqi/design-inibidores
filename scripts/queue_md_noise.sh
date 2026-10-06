#!/bin/bash
# queue_md_noise.sh FRONT -- piso de ruido da comparacao pH 8,2 x pH 10,0: segunda execucao (outra semente) de 4 candidatos
# por frente em cada pH (md82b_<F> e md10b_<F>). Espera a MD82ALL_<F>_DONE de queue_md82_rest.sh.
# O pH 10 usa --nterm charged (NH3+ no linear), como as 48 MDs originais de pH 10; em pH 8,2 "auto" tambem da NH3+.
# Marcador final: NOISE_<FRONT>_DONE em outputs/md_noise_<FRONT>.log.
# Uso: screen -dmS noise-L bash -c 'cd ~/design-inibidores && bash scripts/queue_md_noise.sh L >> outputs/md_noise_L.log 2>&1'
F=$1
cd "$(dirname "$0")/.."
source ~/miniforge3/etc/profile.d/conda.sh
conda activate protein_design_env
if [ "$F" = "L" ]; then KEYS="Agemmatalis__r2 Onubilalis__r2 Dsaccharalis__r1 Onubilalis__r1"; else KEYS="Sfrugiperda__r1 Agemmatalis__r2 Dsaccharalis__r3 Cincludens__r2"; fi
echo "[noise-$F] $(date) aguardando MD82ALL_${F}_DONE"
until grep -q "MD82ALL_${F}_DONE" outputs/md82_${F}_rest.log 2>/dev/null; do sleep 300; done
echo "[noise-$F] $(date) pH 8,2, segunda semente: $KEYS"
python -m scripts.run_md_ph_campaign --candidates data-b23-scoring/results/top_candidates_$F.json --workdir outputs/md82b_$F --front $F --ph 8.2 --ns 10 --keys $KEYS
echo "[noise-$F] $(date) pH 10,0, segunda semente: $KEYS"
python -m scripts.run_md_ph_campaign --candidates data-b23-scoring/results/top_candidates_$F.json --workdir outputs/md10b_$F --front $F --ph 10.0 --ns 10 --nterm charged --keys $KEYS
echo "NOISE_${F}_DONE $(date)"

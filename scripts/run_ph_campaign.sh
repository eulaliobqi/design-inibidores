#!/bin/bash
# run_ph_campaign.sh -- comparacao de duas faixas de pH (e do estado do N-terminal do linear), DEPOIS do pipeline atual.
# Espera TWO_FRONTS_ALL_DONE (o pipeline em curso segue como esta, sem ser parado). Condicoes (top-3 por especie, 10 ns, CHARMM36):
#   L  pH 10,0  N-terminal NEUTRO   -> outputs/mdph_L_ph10   (a MD original em outputs/md10_L usou NH3+ nesse pH)
#   L  pH  8,2  N-terminal NH3+     -> outputs/mdph_L_ph8.2  (pH do protocolo do grupo; 24% do N-terminal neutro, pKa 7,7)
#   M  pH  8,2  (sem terminais)     -> outputs/mdph_M_ph8.2  (a MD original do macrociclo, pH 10, esta em outputs/md10_M)
# Ordem: A. gemmatalis nas tres condicoes (graficos cedo), depois as demais especies. Resume-safe (o runner pula `done`).
# Uso: screen -dmS ph-campaign bash -c 'bash scripts/run_ph_campaign.sh >> outputs/ph_campaign.log 2>&1'
cd ~/design-inibidores
source ~/miniforge3/etc/profile.d/conda.sh
PH_HIGH=10.0
PH_LOW=8.2
RES=data-b23-scoring/results
echo "[ph] $(date) aguardando o fim do pipeline (TWO_FRONTS_ALL_DONE)..."
until grep -q TWO_FRONTS_ALL_DONE outputs/e1_fix_pipeline.log 2>/dev/null; do sleep 600; done
conda activate protein_design_env
run() {  # front ph workdir [especies...]
  local F=$1 PH=$2 WD=$3; shift 3
  python -m scripts.run_md_ph_campaign --candidates $RES/top_candidates_$F.json --workdir $WD --front $F --ph $PH "$@"
}
echo "[ph] $(date) fase 1: A. gemmatalis nas tres condicoes"
run L $PH_HIGH outputs/mdph_L_ph10 --species Agemmatalis
run L $PH_LOW  outputs/mdph_L_ph8.2 --species Agemmatalis
run M $PH_LOW  outputs/mdph_M_ph8.2 --species Agemmatalis
for W in mdph_L_ph10 mdph_L_ph8.2 mdph_M_ph8.2; do python -m scripts.analyze_md_top_candidates --md-dir outputs/$W; done
python scripts/compare_ph_conditions.py --root outputs --out outputs/ph_comparison || true
echo "[ph] $(date) fase 2: demais especies"
run L $PH_HIGH outputs/mdph_L_ph10
run L $PH_LOW  outputs/mdph_L_ph8.2
run M $PH_LOW  outputs/mdph_M_ph8.2
for W in mdph_L_ph10 mdph_L_ph8.2 mdph_M_ph8.2; do python -m scripts.analyze_md_top_candidates --md-dir outputs/$W; done
python scripts/compare_ph_conditions.py --root outputs --out outputs/ph_comparison
echo "PH_CAMPAIGN_DONE $(date)"

#!/bin/bash
# queue_final_md.sh -- fila das etapas finais de MD (preparada em 04/10/2026, aguardando o md-controls).
# 1) espera MD_CONTROLS_DONE de outputs/md_controls.log (o lote 1 do run_md_controls.sh);
# 2) lote 2 de controles embaralhados para os candidatos entregues que o lote 1 nao cobre: GQNDS (L, Onubilalis__r2) e
#    GGHSE (M, Sfrugiperda__r1); frentes L e M em paralelo (workdirs distintos);
# 3) analise dos controles e comparacao candidato x controle (regra de elegibilidade ao controle negativo);
# 4) controle negativo (ancora -> Asp e -> Leu) para os elegiveis, L e M em paralelo; analise;
# 5) tabela final em outputs/controls_decision.{json,md}. Marcador final: QUEUE_FINAL_MD_DONE.
# Uso: screen -dmS md-final-queue bash -c 'cd ~/design-inibidores && bash scripts/queue_final_md.sh >> outputs/queue_final_md.log 2>&1'
set -u
cd "$(dirname "$0")/.."
source ~/miniforge3/etc/profile.d/conda.sh
echo "[queue] $(date) aguardando MD_CONTROLS_DONE..."
until grep -q "MD_CONTROLS_DONE" outputs/md_controls.log 2>/dev/null; do sleep 300; done
set +u  # gromacs_deactivate.sh do env referencia OLD_GMX* nao definidas: com set -u o script morria no activate
conda activate protein_design_env
set -u
echo "[queue] $(date) lote 2 de controles embaralhados (GQNDS, GGHSE)"
python -m scripts.run_md_controls --front L --ns 10 --candidates Onubilalis__r2 > outputs/queue_ctrl2_L.log 2>&1 &
python -m scripts.run_md_controls --front M --ns 10 --candidates Sfrugiperda__r1 > outputs/queue_ctrl2_M.log 2>&1 &
wait
for F in L M; do python -m scripts.analyze_md_top_candidates --md-dir outputs/md10_controls_$F; done
python -m scripts.compare_controls
echo "[queue] $(date) controle negativo (troca da ancora) para os elegiveis"
python -m scripts.run_md_negctrl --front L --from-decision outputs/controls_decision.json --ns 10 > outputs/queue_neg_L.log 2>&1 &
python -m scripts.run_md_negctrl --front M --from-decision outputs/controls_decision.json --ns 10 > outputs/queue_neg_M.log 2>&1 &
wait
for F in L M; do [ -f outputs/md10_negctrl_$F/summary.json ] && python -m scripts.analyze_md_top_candidates --md-dir outputs/md10_negctrl_$F; done
python -m scripts.compare_controls --negctrl
echo "QUEUE_FINAL_MD_DONE $(date)"

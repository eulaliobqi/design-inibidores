#!/bin/bash
# pos_md_M.sh -- espera a ultima MD da frente M e encadeia analise + ranking.
# Uso: screen -dmS pos-md-m bash -c 'bash scripts/pos_md_M.sh >> outputs/pos_md_M.log 2>&1'
cd ~/design-inibidores
source ~/miniforge3/etc/profile.d/conda.sh
PID=2320624   # python -m scripts.run_md_top_candidates --front M
echo "[pos] $(date) aguardando PID $PID (run_md_top_candidates M)"
while kill -0 $PID 2>/dev/null; do sleep 120; done
N=$(python3 -c "
import json
d=json.load(open('outputs/md10_M/summary.json'))
print(sum(v.get('status')=='done' for v in d.values()))")
echo "[pos] $(date) processo terminou; M done=$N"
if [ "$N" -lt 24 ]; then echo "[pos] ABORTA: M=$N/24 (conferir erros em summary.json)"; exit 1; fi
conda activate protein_design_env
for F in L M; do
  echo "[pos] $(date) analyze md10_$F"
  python -m scripts.analyze_md_top_candidates --md-dir outputs/md10_$F || { echo "[pos] FALHOU analyze $F"; exit 2; }
done
OUT=outputs/ranking_final_$(date +%d%m_%H%M)
echo "[pos] $(date) ranking -> $OUT"
python scripts/rank_final_candidates.py --layout server --out $OUT --lang pt || { echo "[pos] FALHOU ranking"; exit 3; }
echo "POS_MD_M_DONE $(date) $OUT"

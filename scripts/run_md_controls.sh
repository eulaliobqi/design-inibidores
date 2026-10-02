#!/bin/bash
# run_md_controls.sh -- controles de MD pareados por tamanho, no mesmo protocolo dos candidatos.
# Espera o E3 (que gera as predicoes dos controles embaralhados) e roda 10 ns em 1 controle por candidato
# escolhido. Prioridade: os candidatos que PASSARAM na triagem -- se a isca deles tambem ficar em S1, a
# ocupancia nao sustenta afirmacao de ligacao. Depois, um candidato que falhou (referencia baixa).
# Uso: screen -dmS md-controls bash -c 'bash scripts/run_md_controls.sh >> outputs/md_controls.log 2>&1'
cd ~/design-inibidores
source ~/miniforge3/etc/profile.d/conda.sh
echo "[ctrl] $(date) aguardando o E3 (delta_paired_L.json)..."
until [ -f data-b23-scoring/results/delta_paired_L.json ] && [ -f data-b23-scoring/results/delta_paired_M.json ]; do sleep 600; done
conda activate protein_design_env
echo "[ctrl] $(date) controles da frente L"
python -m scripts.run_md_controls --front L --ns 10 --candidates Agemmatalis__r2 Agemmatalis__r3 Sfrugiperda__r1
echo "[ctrl] $(date) controles da frente M"
python -m scripts.run_md_controls --front M --ns 10 --candidates Agemmatalis__r2 Agemmatalis__r1
for F in L M; do python -m scripts.analyze_md_top_candidates --md-dir outputs/md10_controls_$F; done
echo "MD_CONTROLS_DONE $(date)"

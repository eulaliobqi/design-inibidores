#!/bin/bash
# run_e1_fix_then_pipeline.sh -- espera o E1, refaz predicoes que faltarem (o script do E1 e' retomavel:
# so roda boltz nos YAMLs sem predicao) e so entao dispara o pipeline E2-E9.
# Motivo: em 30/09 uma predicao da frente M (Dsaccharalis__len6_design_9__51) falhou no pre-processamento do
# Boltz ("'PosixPath' object has no attribute 'islower'") e o E1 seguiu sem ela.
# Uso: screen -S e1-fix ; bash scripts/run_e1_fix_then_pipeline.sh
cd ~/design-inibidores
SP8="Sfrugiperda Slitura Onubilalis Dsaccharalis Cincludens Hvirescens Pxylostella Agemmatalis"
echo "[fix] $(date) aguardando E1..."
until grep -q E1_TWO_FRONTS_DONE outputs/e1_two_fronts.log 2>/dev/null; do sleep 120; done
count_missing() {
  local m=0 ny nd
  for f in L M; do for sp in $SP8; do
    ny=$(ls data-b23-scoring/boltz_yaml_$f/$sp/*.yaml 2>/dev/null | wc -l)
    nd=$(ls outputs/b23_boltz2_${f}_$sp/boltz_results_$sp/predictions 2>/dev/null | wc -l)
    [ "$nd" -lt "$ny" ] && m=$((m + ny - nd))
  done; done
  echo $m
}
echo "[fix] $(date) E1 concluiu; predicoes faltantes: $(count_missing)"
for try in 1 2 3; do
  [ "$(count_missing)" -eq 0 ] && break
  echo "[fix] $(date) tentativa $try de refazer as faltantes"
  bash scripts/run_e1_boltz2_two_fronts.sh > outputs/e1_retry_$try.log 2>&1 || true
  echo "[fix] $(date) faltantes apos a tentativa $try: $(count_missing)"
done
echo "[fix] $(date) faltantes finais: $(count_missing) -> disparando o pipeline E2-E9"
bash scripts/run_two_fronts_pipeline.sh

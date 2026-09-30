#!/bin/bash
# run_b27_corrected_pipeline.sh -- refaz, com a regra de clivagem CIRCULAR e a MD com PBC
# corrigido, a cadeia B2.7: clivagem (8 especies) -> MSA+Boltz-2 de A. gemmatalis -> top-1 por
# especie -> MD 50 ns -> analise. Resume-safe (cada etapa pula o que ja existe).
# Uso: screen -S b27-corrected ; bash scripts/run_b27_corrected_pipeline.sh
set -e
cd ~/design-inibidores
source ~/miniforge3/etc/profile.d/conda.sh
SP8="Sfrugiperda Slitura Onubilalis Dsaccharalis Cincludens Hvirescens Pxylostella Agemmatalis"
CLV=outputs/b23_cleavage_circular.json
TOP=data-b23-scoring/results/top_candidates_circular.json
MDDIR=outputs/md_top_candidates_circular

conda activate protein_design_env
echo "[1] $(date) geometric P1 das 8 especies"
python - <<'PY'
import json
a=json.load(open("data-lepidoptera-panel/geometric_p1_b23.json"))
b=json.load(open("data-lepidoptera-panel/geometric_p1_agem.json"))
a.update(b)
json.dump(a,open("data-lepidoptera-panel/geometric_p1_all8.json","w"),indent=2)
print("especies:",sorted(a))
PY
echo "[2] $(date) clivagem circular"
( cd scripts && python run_cleavage_b23.py --species $SP8 \
    --geometric-p1 data-lepidoptera-panel/geometric_p1_all8.json --out $CLV )

echo "[3] $(date) Boltz-2 A. gemmatalis"
bash scripts/run_boltz2_scoring_agemmatalis.sh

conda activate protein_design_env
echo "[4] $(date) selecao top-1 (RESISTENTE circular, maior confidence_score)"
python scripts/select_top_candidates.py --cleavage $CLV --out $TOP

echo "[5] $(date) reaproveita MD ja feitas p/ candidatos identicos (mesma sequencia+backbone)"
python - <<'PY'
import json, os
from pathlib import Path
top=json.load(open("data-b23-scoring/results/top_candidates_circular.json"))["candidates"]
old=json.load(open("outputs/md_top_candidates/summary.json"))
new=Path("outputs/md_top_candidates_circular"); new.mkdir(parents=True,exist_ok=True)
sp=new/"summary.json"; summary=json.load(open(sp)) if sp.exists() else {}
for s,c in top.items():
    o=old.get(s)
    if o and o.get("status")=="done" and o["sequence"]==c["sequence"] and o["backbone"]==c["backbone"] and s not in summary:
        link=new/s
        if not link.exists(): os.symlink(Path("../md_top_candidates")/s, link)
        e={k:v for k,v in o.items() if not k.startswith("rmsd_")}   # RMSD bruto antigo = artefato de PBC
        e["reused_from"]="outputs/md_top_candidates"
        summary[s]=e; print("reaproveitado:",s,c["sequence"])
json.dump(summary,open(sp,"w"),indent=2)
PY

echo "[6] $(date) MD 50 ns: A. gemmatalis primeiro, depois as demais"
python -m scripts.run_md_top_candidates --candidates $TOP --workdir $MDDIR --species Agemmatalis
python -m scripts.run_md_top_candidates --candidates $TOP --workdir $MDDIR

echo "[7] $(date) analise (ocupancia S1, triade, RMSD local com PBC robusto)"
python -m scripts.analyze_md_top_candidates --md-dir $MDDIR
echo "B27_CORRECTED_ALL_DONE $(date)"

"""Gera Manuscript_EN.docx a partir de manuscript.md (ja renderizado por render.py): figuras inline com
legendas, tabelas suplementares, sem as notas de rascunho. Uso: python render.py && python build_docx_en.py"""
import re
import subprocess
import sys
from pathlib import Path

from docx_post import postprocess

HERE = Path(__file__).parent
sys.stdout.reconfigure(encoding="utf-8")
src = (HERE / "manuscript.md").read_text(encoding="utf-8").replace("\r\n", "\n")

# notas de rascunho nao vao para o documento
src = src.split("\n---\n\n## Drafting notes")[0]
# referencias ficam antes das legendas no arquivo; separa blocos
head, rest = src.split("\n---\n\n## Figure legends")
leg_block, refs_block = rest.split("\n---\n\n## References")
legends = dict(re.findall(r"\*\*Figure (S?\d+)\.\*\* (.*?)(?=\n\n\*\*Figure|\n\n\*\*Table|\Z)", leg_block, flags=re.S))
sup_tab = leg_block[leg_block.index("**Table S1.**"):].strip()

F = "figures/final/"
FIG = {"1": "Figure1_pipeline", "2": "Figure2_calibration", "3": "Figure3_hard_funnel", "4": "Figure4_boltz2_reproducibility",
       "5": "Figure5_MD_screen", "6": "Figure6_energy_ranking", "7": "Figure7_pH_comparison", "8": "Figure8_candidate_poses",
       "S1": "FigureS1_hard_rule", "S2": "FigureS2_motif_screen", "S3": "FigureS3_hard_composition", "S4": "FigureS4_E2_rescoring",
       "S5": "FigureS5_pose_quality", "S6": "FigureS6_ring_integrity", "S7": "FigureS7_tiers_matrix", "S8": "FigureS8_boltz2_first_round",
       "S9": "FigureS9_motif_rules", "S10": "FigureS10_energy_trajectories", "S11": "FigureS11_scissile_protection"}
for k, v in FIG.items():
    assert (HERE / F / (v + ".png")).exists(), v
    assert k in legends, f"legenda ausente: {k}"


def img(n, w="16.5cm"):
    return f"\n![**Figure {n}.** {legends[n].strip()}]({F}{FIG[n]}.png){{width={w}}}\n"


anchors = [("1", "\n---\n\n## 2 Materials and methods"), ("2", "\n### 3.3 Generation"), ("3", "\n### 3.4 Co-folding"),
           ("4", "\n### 3.5 Ten-nanosecond"), ("5", "\n### 3.6 Energy filter"), ("6", "\n### 3.7 pH 8.2"),
           ("7", "\n### 3.8 Candidate"), ("8", "\n---\n\n## 4 Discussion")]
for n, a in anchors:
    assert head.count(a) == 1, a
    head = head.replace(a, img(n) + a)
supp = "\n\n## Supplementary figures\n" + "".join(img(k, "13cm") for k in ("S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10", "S11"))
supp += "\n\n## Supplementary tables\n\n" + sup_tab + "\n"
full = head.rstrip() + "\n\n---\n\n## References" + refs_block.rstrip() + supp
full = re.sub(r"\[\[(.*?)\]\]", lambda m: "[" + m.group(1).replace("[", "(").replace("]", ")") + ']{custom-style="Pendente"}', full, flags=re.S)
full = re.sub(r"\[(AUTHOR LIST TO BE COMPLETED|TO BE COMPLETED)\]", lambda m: "[" + m.group(1) + ']{custom-style="Pendente"}', full)
md = HERE / "_docx_en_tmp.md"
md.write_text(full, encoding="utf-8")

out = HERE / "Manuscript_EN.docx"
try:
    with open(out, "ab"):
        pass
except PermissionError:
    out = HERE / "Manuscript_EN_novo.docx"
    print("AVISO: Manuscript_EN.docx esta aberto; gravando em", out.name)
subprocess.run(["pandoc", str(md), "-f", "markdown+pipe_tables+subscript+superscript", "-o", str(out),
                f"--reference-doc={HERE / '_reference.docx'}", f"--resource-path={HERE}"], check=True)
postprocess(out, "From Natural Protease Inhibitors")
print("ok ->", out.name)

md.unlink()

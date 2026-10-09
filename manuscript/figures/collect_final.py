"""Monta `manuscript/figures/final/` com a numeracao do manuscrito.

Por que isto existe: na reescrita de 05/10/2026 as figuras foram renumeradas, e ate 07/10 a
renumeracao so existia como copia manual de arquivos -- nenhum script levava da saida dos
geradores aos nomes citados no texto. Quem clonasse o repositorio e rodasse os geradores obtinha
os nomes antigos e nao conseguia casar figura com legenda. Este script fecha essa lacuna: ele e'
a unica definicao executavel do mapa "gerador -> numero final".

Quatro geradores produzem as figuras:
  make_figures_final.py  -> Figuras 1, 2, 6 e 8, gravadas direto em figures/final/
  make_figures_ph.py     -> Figura 7 e S10, gravadas direto em figures/final/
  make_figures_v3.py     -> Figuras 3, 4, S1, S3, S8 e S9, com os nomes antigos em figures/
  make_figure_s2.py      -> Figura S2 (Figure4_motif_screen), redesenhada em 08/10/2026
  make_figure_s11.py     -> Figura S11 (geometria de ataque: sitio protegido x exposto), 09/10/2026; grava direto em final/
  make_figures_e2_md.py  -> Figuras 5, S4, S5, S6, com os nomes antigos em figures/
  scripts/rank_final_candidates.py -> Figura S7, com o nome antigo em figures/

Uso:
    python figures/collect_final.py            # so copia o que ja foi gerado
    python figures/collect_final.py --run      # roda tambem os dois geradores diretos
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FINAL = HERE / "final"
EXT = (".png", ".pdf", ".tif")

# nome antigo do gerador -> numero no manuscrito (05/10/2026)
RENAMES = {
    "Figure5_hard_funnel": "Figure3_hard_funnel",
    "Figure8_boltz2_reproducibility": "Figure4_boltz2_reproducibility",
    "Figure11_MD_screen_10ns": "Figure5_MD_screen",
    "Figure2_hard_rule": "FigureS1_hard_rule",
    "Figure4_motif_screen": "FigureS2_motif_screen",
    "Figure6_hard_composition": "FigureS3_hard_composition",
    "Figure9_E2_rescoring": "FigureS4_E2_rescoring",
    "Figure10_top3_pose": "FigureS5_pose_quality",
    "FigureS2_cyclic_ring_CHARMM36": "FigureS6_ring_integrity",
    "Figure12_final_candidates": "FigureS7_tiers_matrix",
    "Figure7_boltz2_first_round": "FigureS8_boltz2_first_round",
    "FigureS1_motif_screen_rules": "FigureS9_motif_rules",
}
# gravadas direto em figures/final/ pelos geradores que recebem o diretorio de saida
DIRECT = {
    "make_figures_final.py": ["Figure1_pipeline", "Figure2_calibration",
                              "Figure6_energy_ranking", "Figure8_candidate_poses"],
    "make_figures_ph.py": ["Figure7_pH_comparison", "FigureS10_energy_trajectories"],
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true",
                    help="roda make_figures_final.py e make_figures_ph.py antes de copiar")
    args = ap.parse_args()
    FINAL.mkdir(parents=True, exist_ok=True)

    if args.run:
        for gen in DIRECT:
            print(f"-> {gen}")
            subprocess.run([sys.executable, str(HERE / gen), str(FINAL)], check=True, cwd=HERE.parent)

    copied, missing = 0, []
    for old, new in RENAMES.items():
        found = False
        for ext in EXT:
            src = HERE / f"{old}{ext}"
            if src.exists():
                shutil.copy2(src, FINAL / f"{new}{ext}")
                copied += 1
                found = True
        if not found:
            missing.append(old)

    for gen, stems in DIRECT.items():
        for st in stems:
            if not (FINAL / f"{st}.tif").exists():
                missing.append(f"{st} (rode {gen})")

    print(f"copiados: {copied} arquivos; renomeacoes no mapa: {len(RENAMES)}")
    if missing:
        print("FALTANDO:", ", ".join(missing))
        return 1
    print("figures/final/ completo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

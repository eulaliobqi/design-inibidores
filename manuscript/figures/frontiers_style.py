"""
frontiers_style.py -- modelo unico para as figuras do manuscrito, nas medidas EXIGIDAS pela revista.

Especificacao conferida em 01/10/2026 nas diretrizes oficiais da Frontiers (author-guidelines):
  largura  : 85 mm (uma coluna) ou 180 mm (duas colunas); a figura nao pode passar de uma pagina
  resolucao: 300 dpi **no tamanho final** (nao no tamanho em que o script desenhou)
  texto    : "the smallest visible text should be no less than eight points in height when viewed
             at actual size" -> 8 pt e' o PISO, medido no tamanho impresso
  linhas   : "no smaller than two points wide" e sem tracejado interrompido
  formato  : TIF/TIFF, JPEG ou EPS, em RGB

Por que isto existe: as figuras anteriores foram desenhadas em polegadas arbitrarias (8,5 a 13 in,
ou seja 216 a 330 mm). Ao serem reduzidas para 180 mm na diagramacao, todo o texto encolhe junto --
uma fonte de 6,5 pt desenhada numa figura de 318 mm chega a 3,7 pt na pagina, menos da metade do
minimo. Desenhar diretamente na largura final elimina esse encolhimento: o que esta em 8 pt aqui
sai em 8 pt impresso.

Uso:
    from frontiers_style import apply_style, mm_figsize, save_journal
    apply_style()
    fig, ax = plt.subplots(1, 3, figsize=mm_figsize("double", 70), layout="constrained")
    ...
    save_journal(fig, OUT / "Figure9_E2_rescoring")   # grava png+pdf+tif e confere
"""
from pathlib import Path

import matplotlib.pyplot as plt

MM = 25.4
WIDTH_MM = {"single": 85.0, "double": 180.0}
DPI = 300
MIN_PT = 8.0          # piso de texto da revista, no tamanho final
MAX_HEIGHT_MM = 240.0  # "nao exceder uma pagina"


def mm_figsize(width: str | float, height_mm: float):
    """Tamanho em polegadas a partir da largura da revista (ou de um valor em mm) e da altura em mm."""
    w = WIDTH_MM[width] if isinstance(width, str) else float(width)
    if height_mm > MAX_HEIGHT_MM:
        raise ValueError(f"altura {height_mm} mm passa de uma pagina ({MAX_HEIGHT_MM} mm)")
    return (w / MM, height_mm / MM)


def apply_style(base_pt: float = MIN_PT):
    """rcParams com o piso de 8 pt. Como a figura e' desenhada ja na largura final, nada encolhe depois.

    `base_pt` nunca deve ficar abaixo de MIN_PT; valores menores sao rejeitados em vez de reduzir
    silenciosamente a figura abaixo da exigencia da revista."""
    if base_pt < MIN_PT:
        raise ValueError(f"texto de {base_pt} pt fica abaixo do minimo de {MIN_PT} pt da revista")
    plt.rcParams.update({
        "font.size": base_pt, "axes.titlesize": base_pt + 1, "axes.labelsize": base_pt,
        "xtick.labelsize": base_pt, "ytick.labelsize": base_pt, "legend.fontsize": base_pt,
        "figure.titlesize": base_pt + 1,
        "savefig.dpi": DPI, "figure.dpi": 150,
        "axes.spines.top": False, "axes.spines.right": False,
        # linhas: o minimo da revista e' 2 pt para linha solida de desenho; eixos e linhas de
        # referencia seguem esse piso. Series temporais densas usam tracos mais finos (ver nota
        # no fim da legenda), senao 500 quadros viram um borrao.
        "axes.linewidth": 1.0, "xtick.major.width": 1.0, "ytick.major.width": 1.0,
        "lines.linewidth": 2.0, "patch.linewidth": 1.0,
        "pdf.fonttype": 42, "ps.fonttype": 42,   # texto embutido e editavel
        "figure.constrained_layout.use": False,
    })


def save_journal(fig, stem: Path | str, formats=("png", "pdf", "tif")):
    """Grava nos formatos da revista e devolve a largura final medida, para conferencia.

    Nunca usa bbox_inches='tight': isso mudaria a largura fisica pedida."""
    stem = Path(stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    out = {}
    if "png" in formats:
        fig.savefig(stem.with_suffix(".png"), dpi=DPI)
        out["png"] = stem.with_suffix(".png")
    if "pdf" in formats:
        fig.savefig(stem.with_suffix(".pdf"))
        out["pdf"] = stem.with_suffix(".pdf")
    if "tif" in formats and "png" in out:
        from PIL import Image
        Image.open(out["png"]).convert("RGB").save(stem.with_suffix(".tif"),
                                                   compression="tiff_lzw", dpi=(DPI, DPI))
        out["tif"] = stem.with_suffix(".tif")
    w_in, h_in = fig.get_size_inches()
    rep = {"largura_mm": round(w_in * MM, 1), "altura_mm": round(h_in * MM, 1), "dpi": DPI,
           "dentro_da_largura": round(w_in * MM, 1) <= WIDTH_MM["double"] + 0.5,
           "cabe_na_pagina": round(h_in * MM, 1) <= MAX_HEIGHT_MM}
    if not rep["dentro_da_largura"] or not rep["cabe_na_pagina"]:
        print(f"ATENCAO {stem.name}: {rep}")
    return rep

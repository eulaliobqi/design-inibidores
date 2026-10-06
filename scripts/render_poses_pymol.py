"""
render_poses_pymol.py -- paineis estruturais (PyMOL, headless) dos peptideos candidatos no sitio catalitico: pose inicial do
Boltz-2 (complex_clean.pdb; cadeia A = receptor, cadeia B = peptideo), com Asp189 (S1), His57 e Ser195 em bastoes, o peptideo em
bastoes, o residuo ancora (o do peptideo mais proximo do carboxilato do Asp189) rotulado e a distancia ancora-Asp189 tracejada.

Uso (servidor):  ~/miniforge3/envs/viz/bin/pymol -cq scripts/render_poses_pymol.py -- OUTDIR
Os residuos catalíticos vem da Tabela 1 (Ser catalitica e Asp189-equivalente por especie); a His57 e' a His cujo Ne2/Nd1
fica mais perto do Og da Ser.
"""
import math
import sys
from pathlib import Path

from pymol import cmd

ROOT = Path.cwd()
OUT = Path(sys.argv[-1]) if len(sys.argv) > 1 else ROOT / "outputs/pose_renders"
OUT.mkdir(parents=True, exist_ok=True)
# (rotulo, frente, chave, resid da Ser catalitica, resid do Asp189-eq.)
JOBS = [
    ("NGGRPDAP", "L", "Agemmatalis__r2", 217, 211),
    ("GQNDS", "L", "Onubilalis__r2", 213, 207),
    ("GGHSE", "M", "Sfrugiperda__r1", 220, 214),
    ("GGKPGEP", "M", "Agemmatalis__r2", 217, 211),
]


def dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


for label, F, key, ser, asp in JOBS:
    cmd.reinitialize()
    pdb = ROOT / f"outputs/md10_{F}/{key}/complex_clean.pdb"
    cmd.load(str(pdb), "cx")
    cmd.hide("everything")
    cmd.bg_color("white")
    cmd.set("ray_opaque_background", 1)
    cmd.set("antialias", 2)
    cmd.set("cartoon_fancy_helices", 1)
    cmd.set("cartoon_transparency", 0.0)
    cmd.set("stick_radius", 0.17)
    cmd.set("depth_cue", 0)
    cmd.set("ray_shadow", 0)
    cmd.set("label_size", 22)
    cmd.set("label_font_id", 7)
    cmd.set("label_color", "black")
    cmd.set("dash_gap", 0.25)
    cmd.set("dash_width", 3)
    cmd.show("cartoon", "chain A")
    cmd.color("grey70", "chain A")
    # residuos catalíticos
    cmd.select("sasp", f"chain A and resi {asp}")
    cmd.select("sser", f"chain A and resi {ser}")
    og = cmd.get_model("sser and name OG").atom[0].coord
    best, hisres = 99.0, None
    for at in cmd.get_model("chain A and resn HIS and (name NE2 or name ND1)").atom:
        d = dist(at.coord, og)
        if d < best:
            best, hisres = d, at.resi
    cmd.select("shis", f"chain A and resi {hisres}")
    cmd.show("sticks", "sasp or sser or shis")
    cmd.color("tv_orange", "sasp and elem C")
    cmd.color("smudge", "sser and elem C")
    cmd.color("smudge", "shis and elem C")
    cmd.util.cnc("sasp or sser or shis")
    # peptideo e ancora
    cmd.show("sticks", "chain B")
    cmd.color("cyan", "chain B and elem C")
    cmd.util.cnc("chain B")
    oxy = cmd.get_model("sasp and (name OD1 or name OD2)").atom
    best_a, anchor, pair = 99.0, None, None
    for at in cmd.get_model("chain B").atom:
        for o in oxy:
            d = dist(at.coord, o.coord)
            if d < best_a:
                best_a, anchor, pair = d, at, o
    cmd.select("sanc", f"chain B and resi {anchor.resi}")
    cmd.color("magenta", "sanc and elem C")
    cmd.distance("dd", f"chain B and resi {anchor.resi} and name {anchor.name}", f"chain A and resi {asp} and name {pair.name}")
    cmd.hide("labels", "dd")
    # so o entorno do peptideo (cartoon fino do receptor num raio de 12 A), sem superficie e sem rotulos
    cmd.select("near", "chain A within 12 of chain B")
    cmd.hide("cartoon", "chain A and not near")
    cmd.set("cartoon_tube_radius", 0.25)
    cmd.set("cartoon_transparency", 0.35)
    cmd.show("sticks", "sasp or sser or shis")
    cmd.orient("chain B or sasp or sser")
    cmd.zoom("chain B or sasp or sser or shis", 6)
    cmd.clip("slab", 200)
    cmd.ray(1500, 1100)
    cmd.png(str(OUT / f"{label}_{F}.png"), dpi=300)
    print(label, F, key, "ancora", anchor.resn, anchor.resi, "d=%.2f" % best_a, "His", hisres, flush=True)
cmd.quit()

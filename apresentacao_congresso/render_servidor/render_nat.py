"""Renderiza no servidor: inibidores naturais isolados (mesma escala) e o complexo 1SFI (tripsina + SFTI-1)."""
import os
from pymol import cmd

OUT = os.path.expanduser('~/ppt_render')
os.makedirs(OUT, exist_ok=True)
PDB = os.path.expanduser('~/ppt_pdb')

cmd.bg_color('white')
cmd.set('ray_opaque_background', 1)
cmd.set('antialias', 2)
cmd.set('ray_shadows', 0)
cmd.set('depth_cue', 0)
cmd.set('cartoon_fancy_helices', 1)
cmd.set('cartoon_side_chain_helper', 1)
cmd.set('specular', 0.15)
cmd.set('ray_trace_mode', 1)
cmd.set('ray_trace_gain', 0.5)

AZUL, VERDE, LARANJA, AMARELO, VERM, CINZA = '0x0072B2', '0x2A9D8F', '0xD55E00', '0xE69F00', '0xC0392B', '0xBFC4CA'
for n, h in [('azul', 0x0072B2), ('verde', 0x2A9D8F), ('laranja', 0xD55E00), ('amarelo', 0xE69F00),
             ('verm', 0xC0392B), ('cinza', 0xBFC4CA), ('grafite', 0x1F2328), ('rosa', 0xCC79A7)]:
    cmd.set_color(n, [(h >> 16 & 255) / 255, (h >> 8 & 255) / 255, (h & 255) / 255])


def fixed_view(sel, dist):
    cmd.orient(sel)
    v = list(cmd.get_view())
    v[11] = -dist
    v[15] = dist * 0.5
    v[16] = dist * 1.5
    cmd.set_view(v)


# --- inibidores isolados, mesma escala -------------------------------------
itens = [('SFTI-1', '1SFI', 'chain I', 'laranja'),
         ('BBI', '1BBI', 'chain A', 'verde'),
         ('SKTI', '1AVU', 'chain A', 'azul')]
for nome, pdb, sel, cor in itens:
    cmd.reinitialize()
    cmd.bg_color('white')
    cmd.set('ray_opaque_background', 1)
    cmd.set('antialias', 2)
    cmd.set('ray_shadows', 0)
    cmd.set('depth_cue', 0)
    for n, h in [('azul', 0x0072B2), ('verde', 0x2A9D8F), ('laranja', 0xD55E00), ('amarelo', 0xE69F00)]:
        cmd.set_color(n, [(h >> 16 & 255) / 255, (h >> 8 & 255) / 255, (h & 255) / 255])
    cmd.load(f'{PDB}/{pdb}.pdb', 'm')
    cmd.remove('not (' + sel + ') or solvent or hetatm')
    cmd.remove('not alt ""+A')
    cmd.hide('everything')
    cmd.show('cartoon')
    cmd.color(cor, 'm')
    if nome == 'SFTI-1':
        cmd.show('sticks', 'm')
        cmd.set('stick_radius', 0.18)
    cmd.set('cartoon_loop_radius', 0.4 if nome != 'SFTI-1' else 0.5)
    # dissulfetos
    cmd.show('sticks', 'resn CYS and not name N+C+O')
    cmd.color('amarelo', 'resn CYS and elem S')
    fixed_view('m', 150)
    cmd.png(f'{OUT}/nat_{nome}.png', 700, 700, dpi=150, ray=1)
    print(nome, cmd.count_atoms('m and name CA'), 'residuos')

# --- complexo 1SFI: ancoragem do P1 em S1 -----------------------------------
cmd.reinitialize()
cmd.bg_color('white')
cmd.set('ray_opaque_background', 1)
cmd.set('antialias', 2)
cmd.set('ray_shadows', 0)
cmd.set('depth_cue', 0)
for n, h in [('azul', 0x0072B2), ('laranja', 0xD55E00), ('amarelo', 0xE69F00), ('verm', 0xC0392B),
             ('cinza', 0xD7DADF), ('grafite', 0x1F2328)]:
    cmd.set_color(n, [(h >> 16 & 255) / 255, (h >> 8 & 255) / 255, (h & 255) / 255])
cmd.load(f'{PDB}/1SFI.pdb', 'c')
cmd.remove('solvent or hetatm')
cmd.remove('not alt ""+A')
cmd.create('enz', 'c and chain A')
cmd.create('inh', 'c and chain I')
cmd.delete('c')
cmd.hide('everything')
lys = 'inh and resn LYS'
cmd.show('cartoon', 'enz')
cmd.color('cinza', 'enz')
cmd.set('cartoon_transparency', 0.0)
cmd.set('cartoon_loop_radius', 0.25)
cmd.show('cartoon', 'inh')
cmd.color('laranja', 'inh')
cmd.set('cartoon_loop_radius', 0.3, 'inh')
cmd.show('sticks', lys)
cmd.color('laranja', lys + ' and elem C')
cmd.show('sticks', 'enz and resi 189')
cmd.color('verm', 'enz and resi 189 and elem C')
cmd.show('sticks', 'enz and resi 57+195')
cmd.color('amarelo', 'enz and resi 195 and elem C')
cmd.color('azul', 'enz and resi 57 and elem C')
cmd.set('stick_radius', 0.26)
cmd.distance('salt', lys + ' and name NZ', 'enz and resi 189 and name OD1+OD2', 4.0)
cmd.hide('labels', 'salt')
cmd.set('dash_color', 'grafite')
cmd.set('dash_gap', 0.3)
cmd.set('dash_radius', 0.09)
foco = lys + ' or enz and resi 189+195+57'
cmd.orient(foco)
cmd.zoom(foco, 9)
cmd.clip('slab', 14)
cmd.png(f'{OUT}/complexo_1SFI.png', 1400, 1000, dpi=150, ray=1)
import json, math
v = cmd.get_view()
R = [v[0:3], v[3:6], v[6:9]]
cam = v[9:12]
org = v[12:15]
alvo = {'Asp189 (S1)': 'enz and resi 189 and name CG', 'Ser195': 'enz and resi 195 and name OG',
        'His57': 'enz and resi 57 and name NE2', 'Lys P1': lys + ' and name CE'}
W, H = 1400, 1000
f = (H / 2) / math.tan(math.radians(20) / 2)
pos = {}
for k, q in alvo.items():
    x, y, z = cmd.get_atom_coords(q)
    d = [x - org[0], y - org[1], z - org[2]]
    c = [sum(R[i][j] * d[j] for j in range(3)) + cam[i] for i in range(3)]
    pos[k] = [W / 2 + f * c[0] / (-c[2]), H / 2 - f * c[1] / (-c[2])]
json.dump(pos, open(f'{OUT}/complexo_1SFI_labels.json', 'w'))
print(pos)
print('ok')

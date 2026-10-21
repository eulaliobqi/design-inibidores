"""Renderiza as 4 etapas da animacao (GGKPGEP, A. gemmatalis) no mesmo referencial e na mesma vista."""
import os
import sys
from pymol import cmd

FR = os.path.expanduser('~/ppt_frames')
AN = os.path.expanduser('~/ppt_anim')
OUT = os.path.expanduser('~/ppt_anim_out')
for d in ('s1', 's3', 's4'):
    os.makedirs(f'{OUT}/{d}', exist_ok=True)
SZ = int(sys.argv[1]) if len(sys.argv) > 1 else 560
ASP = 211        # Asp189 de S1 no modelo de A. gemmatalis

cmd.bg_color('white')
for k, v in dict(ray_opaque_background=1, antialias=2, ray_shadows=0, depth_cue=0, specular=0.1,
                 stick_radius=0.2, two_sided_lighting=1, surface_quality=0, transparency=0.3).items():
    cmd.set(k, v)
for n, h in [('azul', 0x0072B2), ('verde', 0x2A9D8F), ('laranja', 0xD55E00), ('amarelo', 0xE69F00),
             ('verm', 0xC0392B), ('cinza', 0xC9CDD3), ('ruido', 0x9AA0A6)]:
    cmd.set_color(n, [(h >> 16 & 255) / 255, (h >> 8 & 255) / 255, (h & 255) / 255])

cmd.load(f'{FR}/GGKPGEP.pdb', 'md')
cmd.remove('elem H')
n = cmd.count_states('md')
cmd.select('rec', 'md and chain R')
cmd.select('pep', 'md and chain P')
cmd.hide('everything')
cmd.show('surface', 'rec')
cmd.color('cinza', 'rec')
cmd.set('state', 1)
cmd.orient('pep or (rec and resi %d)' % ASP)
cmd.zoom('pep or (rec and resi %d)' % ASP, 7)
cmd.clip('slab', 10)
V = cmd.get_view()
nrf0 = len([f for f in os.listdir(AN) if f.startswith('rf_')])
cmd.load(f'{AN}/rf_{nrf0 - 1:02d}.pdb', 'rfF')
cmd.orient('rfF')
cmd.zoom('rfF', 9)
cmd.clip('slab', 14)
V1 = cmd.get_view()          # vista de frente para o anel do esqueleto final
cmd.delete('rfF')
cmd.set_view(V)


def cor_mistura(t):
    a, b = (0.60, 0.63, 0.65), (0.165, 0.616, 0.561)
    return [a[i] + (b[i] - a[i]) * t for i in range(3)]


# etapa 1: denoising real do RFdiffusion (50 passos)
nrf = len([f for f in os.listdir(AN) if f.startswith('rf_')])
for k in range(nrf):
    cmd.load(f'{AN}/rf_{k:02d}.pdb', 'rf')
    t = k / (nrf - 1)
    cmd.set_color('cmix', cor_mistura(t))
    cmd.show('sticks', 'rf')
    cmd.show('spheres', 'rf and name CA')
    cmd.set('sphere_scale', 0.32, 'rf')
    cmd.set('stick_radius', 0.27, 'rf')
    cmd.color('cmix', 'rf')
    cmd.set_view(V1)
    cmd.png(f'{OUT}/s1/f{k:02d}.png', SZ, SZ, dpi=100, ray=1)
    cmd.delete('rf')
print('etapa 1 ok', nrf)

# etapa 3: complexo co-dobrado (pose do Boltz-2 ~ quadro 1 da MD), atomos completos
cmd.set('state', 1)
cmd.show('sticks', 'pep')
cmd.color('verde', 'pep and elem C')
cmd.color('laranja', 'pep and resn LYS and elem C')
cmd.show('sticks', 'rec and resi %d' % ASP)
cmd.color('verm', 'rec and resi %d and elem C' % ASP)
cmd.set('stick_radius', 0.26, 'pep')
cmd.set_view(V)
cmd.png(f'{OUT}/s3/boltz.png', SZ, SZ, dpi=100, ray=1)

# etapa 4: MD real, 101 estados -> 51 quadros
for i, st in enumerate(range(1, n + 1, 2)):
    cmd.set('state', st)
    cmd.set_view(V)
    cmd.png(f'{OUT}/s4/f{i:02d}.png', SZ, SZ, dpi=100, ray=1)
print('etapa 4 ok')

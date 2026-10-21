"""Renderiza no servidor as poses estaticas (10 ns) e os quadros do GIF dos 4 candidatos (pH 10,0)."""
import os, sys, json
from pymol import cmd

FR = os.path.expanduser('~/ppt_frames')
OUT = os.path.expanduser('~/ppt_render')
os.makedirs(OUT, exist_ok=True)
MODO = sys.argv[1] if len(sys.argv) > 1 else 'ambos'
CANDS = {  # seq: (frente, resid S1 Asp, cor do peptideo)
    'NGGRPDAP': ('L', 211, 'azul'), 'GQNDS': ('L', 207, 'azul'),
    'GGKPGEP': ('M', 211, 'verde'), 'GGHSE': ('M', 214, 'verde')}
CORES = [('azul', 0x0072B2), ('verde', 0x2A9D8F), ('laranja', 0xD55E00), ('amarelo', 0xE69F00),
         ('verm', 0xC0392B), ('cinza', 0xC9CDD3), ('grafite', 0x1F2328)]


def setup():
    cmd.reinitialize()
    cmd.bg_color('white')
    for k, v in dict(ray_opaque_background=1, antialias=2, ray_shadows=0, depth_cue=0, specular=0.1,
                     cartoon_loop_radius=0.28, stick_radius=0.22, dash_gap=0.3, dash_radius=0.07).items():
        cmd.set(k, v)
    for n, h in CORES:
        cmd.set_color(n, [(h >> 16 & 255) / 255, (h >> 8 & 255) / 255, (h & 255) / 255])


def nome(resn):
    return {'HSD': 'His', 'HSE': 'His', 'HSP': 'His', 'HIS': 'His'}.get(resn, resn[:3].capitalize())


for seq, (frente, s1, cor) in CANDS.items():
    setup()
    cmd.load(f'{FR}/{seq}.pdb', 'm')
    n = cmd.count_states('m')
    cas = []
    cmd.iterate('m and chain R and name CA and state 1', 'cas.append((resi, resn))', space={'cas': cas})
    L = len(seq)
    pep_ini = pep_fim = 0
    cmd.select('pep', 'm and chain P')
    cmd.select('rec', 'm and chain R')
    # catalitica: Ser195 em GDSGG, His57 em H-C
    nomes = [r[1] for r in cas]
    ser = his = None
    for i in range(2, len(cas) - 2):
        if nomes[i - 1] == 'ASP' and nomes[i] == 'SER' and nomes[i + 1] == 'GLY' and nomes[i + 2] == 'GLY' and ser is None:
            ser = cas[i][0]
        if nomes[i] in ('HSD', 'HSE', 'HSP', 'HIS') and nomes[i + 1].startswith('CYS') and i < 90 and his is None:
            his = cas[i][0]
    print(seq, 'S1 Asp', s1, 'Ser195', ser, 'His57', his, 'pep', pep_ini, pep_fim, 'estados', n)
    cmd.hide('everything')
    # receptor local: residuos a 12 A do peptideo no primeiro e no ultimo estado
    cmd.select('loc1', 'byres (rec within 12 of pep)', state=1)
    cmd.select('loc2', 'byres (rec within 12 of pep)', state=n)
    cmd.select('loc', 'loc1 or loc2')
    cmd.select('lig', 'byres (rec within 5 of pep)', state=n)
    cmd.remove('elem H')
    cmd.show('surface', 'rec')
    cmd.color('cinza', 'rec')
    cmd.set('transparency', 0.25)
    cmd.set('surface_quality', 0)
    cmd.set('two_sided_lighting', 1)
    cmd.show('sticks', 'pep')
    cmd.color(cor, 'pep and elem C')
    cmd.show('sticks', f'rec and resi {s1}')
    cmd.color('verm', f'rec and resi {s1} and elem C')
    if ser and his:
        cmd.show('sticks', f'rec and resi {ser}+{his}')
        cmd.color('amarelo', f'rec and resi {ser}+{his} and elem C')
    cmd.hide('sticks', 'elem H')
    cmd.set('stick_radius', 0.2)
    cmd.set('stick_radius', 0.28, 'pep')
    # ancora em laranja
    anc = {'NGGRPDAP': 'ARG', 'GQNDS': 'GLN', 'GGKPGEP': 'LYS', 'GGHSE': 'HSE'}[seq]
    cmd.color('laranja', f'pep and resn {anc} and elem C')
    cmd.orient('pep or rec and resi %d' % s1)
    cmd.zoom('pep or rec and resi %d' % s1, 7)
    cmd.clip('slab', 9)
    v = cmd.get_view()
    if MODO in ('ambos', 'pose'):
        cmd.frame(n)
        cmd.set('state', n)
        # contatos polares do peptideo no ultimo quadro
        cmd.distance('hb', 'pep', 'rec', 3.5, mode=2, state=n)
        cmd.hide('labels', 'hb')
        cmd.set('dash_color', 'grafite')
        cmd.hide('sticks', 'elem H')
        # residuos do receptor em contato polar
        cmd.select('hbres', 'byres (rec within 3.5 of pep)', state=n)
        cand = []
        cmd.iterate_state(n, 'hbres and name CA', 'cand.append((resi, resn))', space={'cand': cand})
        pers = {}
        for r_, rn in cand:
            c = 0
            for st in range(int(n * 0.8), n + 1):
                cmd.select('tmp', f'(rec and resi {r_} and elem N+O) within 3.5 of (pep and elem N+O)', state=st)
                if cmd.count_atoms('tmp') > 0:
                    c += 1
            pers[(r_, rn)] = c / (n - int(n * 0.8) + 1)
        rot = [k for k, v in sorted(pers.items(), key=lambda kv: -kv[1]) if v >= 0.5 and k[0] not in (str(s1), str(ser), str(his))][:5]
        cmd.show('sticks', 'rec and resi ' + '+'.join([k[0] for k in rot]))
        cmd.color('cinza', 'rec and resi ' + '+'.join([k[0] for k in rot]) + ' and elem C')
        cmd.set('stick_radius', 0.16, 'rec and resi ' + '+'.join([k[0] for k in rot]))
        cmd.hide('sticks', 'elem H')
        cmd.set('label_font_id', 7)
        cmd.set('label_size', -1.5)
        cmd.set('label_color', 'grafite')
        cmd.set('label_outline_color', 'white')
        cmd.set('label_position', (1.2, 1.2, 3.0))
        for k in rot:
            cmd.label(f'rec and resi {k[0]} and name CA', repr(nome(k[1]) + k[0]))
        cmd.label(f'rec and resi {s1} and name CA', repr('Asp189 (S1)'))
        cmd.label(f'rec and resi {ser} and name CA', repr('Ser195'))
        cmd.label(f'rec and resi {his} and name CA', repr('His57'))
        cmd.set_view(v)
        cmd.png(f'{OUT}/pose_{seq}.png', 1400, 1050, dpi=150, ray=1)
        lista = []
        json.dump({'seq': seq, 's1': s1, 'ser195': ser, 'his57': his, 'rot': [[k[0], nome(k[1]), pers[k]] for k in rot], 'polares': lista}, open(f'{OUT}/pose_{seq}.json', 'w'))
    if MODO in ('ambos', 'gif'):
        cmd.delete('hb')
        cmd.show('sticks', 'pep')
        cmd.show('sticks', f'rec and resi {s1}')
        if ser and his:
            cmd.show('sticks', f'rec and resi {ser}+{his}')
        cmd.set_view(v)
        os.makedirs(f'{OUT}/gif_{seq}', exist_ok=True)
        for i in range(1, n + 1):
            cmd.set('state', i)
            cmd.png(f'{OUT}/gif_{seq}/f{i:03d}.png', 560, 560, dpi=100, ray=1)
        print(seq, 'quadros', n)

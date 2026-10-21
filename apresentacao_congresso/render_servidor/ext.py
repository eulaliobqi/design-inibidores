import MDAnalysis as mda, os
import numpy as np
from MDAnalysis.analysis.align import rotation_matrix

runs = {'NGGRPDAP': 'md10_L/Agemmatalis__r2', 'GQNDS': 'md10_L/Onubilalis__r2',
        'GGHSE': 'md10_M/Sfrugiperda__r1', 'GGKPGEP': 'md10_M/Agemmatalis__r2'}
base = os.path.expanduser('~/design-inibidores/outputs')
out = os.path.expanduser('~/ppt_frames')
os.makedirs(out, exist_ok=True)
for seq, r in runs.items():
    d = f'{base}/{r}'
    u = mda.Universe(f'{d}/md.gro', f'{d}/md_pbc_sub.xtc')
    sel = u.select_atoms('protein')
    res = sel.residues
    L = len(seq)
    pep = res[-L:].atoms
    recp = res[:-L].atoms
    print(seq, r, len(u.trajectory), 'pep', ''.join(res[-L:].resnames), 'rec', len(res) - L)
    if not hasattr(u.atoms, 'chainIDs'):
        u.add_TopologyAttr('chainIDs', ['X'] * len(u.atoms))
    recp.chainIDs = ['R'] * len(recp)
    pep.chainIDs = ['P'] * len(pep)
    ref = recp.select_atoms('backbone')
    first = None
    step = max(1, len(u.trajectory) // 100)
    with mda.Writer(f'{out}/{seq}.pdb', sel.n_atoms, multiframe=True) as W:
        for ts in u.trajectory[::step]:
            com = ref.center_of_mass()
            if first is None:
                first = ref.positions - com
                tgt_com = com
            R, _ = rotation_matrix(ref.positions - com, first)
            u.atoms.translate(-com)
            u.atoms.rotate(R, point=(0, 0, 0))
            W.write(sel)
    print(' ok', seq)

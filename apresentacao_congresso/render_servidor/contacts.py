import MDAnalysis as mda, os, json
import numpy as np
from MDAnalysis.lib.distances import distance_array

runs = {'NGGRPDAP': ('md10_L/Agemmatalis__r2', 'md82_L/Agemmatalis__r2'),
        'GQNDS': ('md10_L/Onubilalis__r2', 'md82_L/Onubilalis__r2'),
        'GGHSE': ('md10_M/Sfrugiperda__r1', 'md82_M/Sfrugiperda__r1'),
        'GGKPGEP': ('md10_M/Agemmatalis__r2', 'md82_M/Agemmatalis__r2')}
base = os.path.expanduser('~/design-inibidores/outputs')
res_out = {}
for seq, dirs in runs.items():
    res_out[seq] = {}
    for tag, r in zip(('pH10.0', 'pH8.2'), dirs):
        d = f'{base}/{r}'
        try:
            u = mda.Universe(f'{d}/md.gro', f'{d}/md_pbc_sub.xtc')
        except Exception as e:
            print(seq, tag, 'falhou', e)
            continue
        sel = u.select_atoms('protein')
        L = len(seq)
        pep = sel.residues[-L:].atoms
        rec = sel.residues[:-L].atoms
        n = len(u.trajectory)
        frames = range(int(n * 0.8), n)          # 8-10 ns
        cont = {}
        hb = {}
        for i in frames:
            u.trajectory[i]
            dm = distance_array(pep.positions, rec.positions)
            near = np.where(dm.min(axis=0) < 4.0)[0]
            for j in set(rec.resids[near]):
                pass
            for ri in set(rec.resindices[near]):
                cont[ri] = cont.get(ri, 0) + 1
            # H-bond/salt-bridge heuristico: N/O pesado <3.5 A
            pp = pep.select_atoms('(name N* O*) and not name OW*')
            rr = rec.select_atoms('(name N* O*)')
            dd = distance_array(pp.positions, rr.positions)
            for a, b in zip(*np.where(dd < 3.5)):
                key = (int(pp.resindices[a]), pp.names[a], int(rr.resindices[b]), rr.names[b])
                hb[key] = hb.get(key, 0) + 1
        nf = len(frames)
        rr_map = {r.resindex: f'{r.resname}{r.resid}' for r in rec.residues}
        pp_map = {r.resindex: f'{r.resname}{i+1}' for i, r in enumerate(pep.residues)}
        top = sorted(((rr_map[k], round(v / nf, 2)) for k, v in cont.items() if v / nf >= 0.5), key=lambda x: -x[1])
        hbl = sorted(((pp_map[k[0]], k[1], rr_map[k[2]], k[3], round(v / nf, 2)) for k, v in hb.items() if v / nf >= 0.3),
                     key=lambda x: -x[4])[:12]
        res_out[seq][tag] = {'contatos_ge50pct': top, 'hbonds_ge30pct': hbl}
        print(seq, tag, top[:10], hbl[:6])
json.dump(res_out, open(os.path.expanduser('~/ppt_frames/contacts.json'), 'w'))

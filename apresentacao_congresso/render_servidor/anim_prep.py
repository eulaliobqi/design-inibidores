"""Prepara os dados REAIS da animacao (GGKPGEP, A. gemmatalis, len7_design_9):
- trajetoria de denoising do RFdiffusion (design_9_Xt-1_traj.pdb, 50 passos)
- esqueleto final e sequencia do ProteinMPNN
- alinhamento no receptor do quadro 1 da MD (mesmo referencial da MD e do Boltz-2)
"""
import os
import json
import numpy as np

BASE = os.path.expanduser('~/design-inibidores/outputs/b23_campaign_Agemmatalis/rfdiffusion/len_7')
OUT = os.path.expanduser('~/ppt_anim')
os.makedirs(OUT, exist_ok=True)


def parse_frames(path):
    frames, cur = [], []
    for line in open(path):
        if line.startswith('ATOM'):
            cur.append(line)
        elif line.startswith('ENDMDL'):
            frames.append(cur)
            cur = []
    if cur:
        frames.append(cur)
    return frames


def xyz(line):
    return [float(line[30:38]), float(line[38:46]), float(line[46:54])]


frames = parse_frames(f'{BASE}/traj/design_9_Xt-1_traj.pdb')
print('frames', len(frames))
B, A = [], []
for fr in frames:
    b = [(l, xyz(l)) for l in fr if l[21] == 'B']
    a = [xyz(l) for l in fr if l[21] == 'A' and l[12:16].strip() == 'CA']
    B.append(b)
    A.append(np.array(a))
print('B atomos/quadro', len(B[0]), 'receptor CA', len(A[0]))


def ca_dev(b):
    ca = np.array([c for l, c in b if l[12:16].strip() == 'CA'])
    d = np.linalg.norm(np.diff(ca, axis=0), axis=1)
    return float(np.abs(d - 3.8).mean())


dev = [ca_dev(b) for b in B]
print('desvio CA-CA primeiro/ultimo', round(dev[0], 2), round(dev[-1], 2))
ordem = list(range(len(B)))
if dev[0] < dev[-1]:
    ordem = ordem[::-1]          # ruido primeiro
print('ordem invertida:', ordem[0] != 0)
print('receptor movel entre quadros?', float(np.abs(A[0] - A[-1]).max()))

# referencial da MD (quadro 1): CA do receptor, cadeia R
import MDAnalysis as mda
md = mda.Universe(os.path.expanduser('~/ppt_frames/GGKPGEP.pdb'))
md.trajectory[0]
ids = md.atoms.chainIDs
sel = (ids == 'R') & (md.atoms.names == 'CA')
print('chains', sorted(set(ids)))
tgt = md.atoms.positions[sel].copy()
src = A[-1] if len(A[-1]) == len(tgt) else None
print('CA receptor RF/MD', len(A[-1]), len(tgt))
P, Q = A[-1], tgt
w = np.ones(len(P), bool)
for _ in range(8):   # ajuste robusto: 70% dos CA mais proximos (o receptor da MD tem trechos em outra imagem periodica)
    Pc, Qc = P[w] - P[w].mean(0), Q[w] - Q[w].mean(0)
    U, S, Vt = np.linalg.svd(Pc.T @ Qc)
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    R = Vt.T @ np.diag([1, 1, d]) @ U.T
    t = Q[w].mean(0) - R @ P[w].mean(0)
    dev_r = np.linalg.norm(P @ R.T + t - Q, axis=1)
    w = np.zeros(len(P), bool)
    w[np.argsort(dev_r)[:int(0.7 * len(P))]] = True
rmsd = float(np.sqrt((dev_r[w] ** 2).mean()))
print('RMSD alinhamento (70% nucleo) RF->MD', round(rmsd, 2))

for k, i in enumerate(ordem):
    with open(f'{OUT}/rf_{k:02d}.pdb', 'w') as f:
        for l, c in B[i]:
            c2 = R @ np.array(c) + t
            f.write(f'{l[:30]}{c2[0]:8.3f}{c2[1]:8.3f}{c2[2]:8.3f}{l[54:]}')
        f.write('END\n')
json.dump({'rmsd_receptor': rmsd, 'dev_ca_primeiro': dev[ordem[0]], 'dev_ca_ultimo': dev[ordem[-1]],
           'n_frames': len(ordem)}, open(f'{OUT}/info.json', 'w'))
print('ok')

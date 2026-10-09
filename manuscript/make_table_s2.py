"""Tabela S2: triade catalitica e bolsao S1 dos 10 receptores (numeracao do modelo; referencia = tripsina bovina).
Triade e geometria: alinhamento global a P00760 + coordenadas AlphaFold. S1: subsites_by_receptor.json (modelo 2PTC; 1SFI identico).
Saidas: manuscript/table_s2_{en,pt}.md e data-lepidoptera-panel/triad_s1_by_receptor.csv"""
import json, math, urllib.request
from pathlib import Path
from Bio import Align
ROOT = Path(__file__).resolve().parent.parent
PAN = ROOT / "data-lepidoptera-panel"
T3 = {'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E','GLY':'G','HIS':'H','ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F','PRO':'P','SER':'S','THR':'T','TRP':'W','TYR':'Y','VAL':'V'}
ORDER = [("Sfrugiperda","*S. frugiperda*"),("Slitura","*S. litura*"),("Onubilalis","*O. nubilalis*"),("Dsaccharalis","*D. saccharalis*"),
         ("Cincludens","*C. includens*"),("Hvirescens","*H. virescens*"),("Pxylostella","*P. xylostella*"),("Agemmatalis","*A. gemmatalis*"),
         ("Msexta","*M. sexta*"),("Bmori","*B. mori*")]
S1 = ["ASP189","SER190","CYS191","GLN192","GLY193","ASP194","SER195","HIS57","VAL213","SER214","TRP215","GLY216","GLY219","GLY226"]
fa = urllib.request.urlopen('https://rest.uniprot.org/uniprotkb/P00760.fasta').read().decode().split('\n')[1:]
bov = ''.join(fa); mat = bov[bov.find('IVGG'):]
anch = {'HIS57': mat.find('AAHC')+2, 'ASP102': mat.find('NDIM')+1, 'SER195': mat.find('GDSGG')+2}
al = Align.PairwiseAligner(); al.mode='global'; al.substitution_matrix=Align.substitution_matrices.load('BLOSUM62'); al.open_gap_score=-10; al.extend_gap_score=-0.5
def atoms(f):
    r = {}
    for l in open(f):
        if l.startswith('ATOM'):
            r.setdefault(int(l[22:26]), {'n':T3[l[17:20]],'a':{}})['a'][l[12:16].strip()] = (float(l[30:38]),float(l[38:46]),float(l[46:54]))
    return r
js = json.load(open(PAN/'subsites_by_receptor.json', encoding='utf-8'))['receptors']
one = lambda s: T3[s[:3]]+s[3:]
rows = {}; geo = {}
for key,_ in ORDER:
    f = next(PAN.glob(f"{key}-*.pdb")); r = atoms(f); ks = sorted(r)
    a = al.align(mat, ''.join(r[k]['n'] for k in ks))[0]; mp = {}
    for (s1,e1),(s2,e2) in zip(*a.aligned):
        for i in range(e1-s1): mp[s1+i] = ks[s2+i]
    tri = {n: mp[v] for n,v in anch.items()}
    t = js[key]['templates']
    s1 = {x['ref']: x['receptor'] for x in t['2PTC_BPTI']['subsites']['S1']}
    assert s1 == {x['ref']: x['receptor'] for x in t['1SFI_SFTI1']['subsites']['S1']}
    assert t['2PTC_BPTI']['catalytic_ser_receptor']['receptor'] == f"SER{tri['SER195']}" and s1['HIS57'] == f"HIS{tri['HIS57']}"
    rows[key] = {'HIS57': f"H{tri['HIS57']}", 'ASP102': f"D{tri['ASP102']}", 'SER195': f"S{tri['SER195']}", **{k: one(s1[k]) for k in S1}}
    H,D,S = tri['HIS57'],tri['ASP102'],tri['SER195']
    geo[key] = (math.dist(r[H]['a']['NE2'], r[S]['a']['OG']), min(math.dist(r[H]['a']['ND1'], r[D]['a'][o]) for o in ('OD1','OD2')))
    assert r[H]['n']=='H' and r[D]['n']=='D' and r[S]['n']=='S'
bovnum = {'HIS57':'H57','ASP102':'D102','SER195':'S195', **{k: one(k) for k in S1}}
lines = [("Catalytic triad","His57","HIS57"),("","Asp102","ASP102"),("","Ser195","SER195")] + [("S1 pocket" if i==0 else "", k[:1]+k[1:3].lower()+k[3:], k) for i,k in enumerate(x for x in S1 if x not in ("HIS57","SER195"))]
def fmt(v, ref): return v if v[0] == ref[0] else f"**{v}**"
def table(hdr, grp):
    out = ["| "+" | ".join(hdr)+" |", "|"+"---|"*len(hdr)]
    for g,lab,k in lines:
        if k=='HIS57' and False: pass
        if k=='SER195' and lab and g=="": pass
        cells = [g if g else "", lab, bovnum[k]] + [fmt(rows[s][k], bovnum[k]) for s,_ in ORDER]
        out.append("| "+" | ".join(cells)+" |")
    return out
def geo_rows(dec, l1, l2):
    f = lambda x: f"{x:.2f}".replace('.', dec)
    return [f"| Geometry | {l1} | – | "+" | ".join(f(geo[s][0]) for s,_ in ORDER)+" |", f"| | {l2} | – | "+" | ".join(f(geo[s][1]) for s,_ in ORDER)+" |"]
for lang,hdr,dec,l1,l2 in (("en",["Group","Position","Bovine trypsin"]+[n for _,n in ORDER],'.',"His NE2…Ser OG (Å)","His ND1…Asp102 OD (Å)"),
                           ("pt",["Grupo","Posição","Tripsina bovina"]+[n for _,n in ORDER],',',"His NE2…Ser OG (Å)","His ND1…Asp102 OD (Å)")):
    body = table(hdr, None)
    if lang=="pt":
        body = [b.replace("Catalytic triad","Tríade catalítica").replace("S1 pocket","Bolsão S1").replace("| Geometry |","| Geometria |") for b in body]
        body = [b.replace("| Catalytic triad","| Tríade catalítica") for b in body]
    else: pass
    body += geo_rows(dec,l1,l2)
    (ROOT/"manuscript"/f"table_s2_{lang}.md").write_text("\n".join(body)+"\n", encoding="utf-8")
with open(PAN/'triad_s1_by_receptor.csv','w',encoding='utf-8') as fh:
    fh.write("receptor,"+",".join(["HIS57","ASP102","SER195"]+[x for x in S1 if x not in ("HIS57","SER195")])+",NE2_OG_A,ND1_OD_A\n")
    for s,_ in ORDER: fh.write(s+","+",".join(rows[s][k] for k in ["HIS57","ASP102","SER195"]+[x for x in S1 if x not in ("HIS57","SER195")])+f",{geo[s][0]:.2f},{geo[s][1]:.2f}\n")
print(open(ROOT/"manuscript/table_s2_en.md",encoding='utf-8').read())

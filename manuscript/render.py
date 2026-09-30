"""Renderiza manuscript_src.md -> manuscript.md: resolve {key;key} (parenteticas) e {@key} (narrativas)
com refs_meta.json, gera a lista de referencias (ordem alfabetica) e confere citacoes x lista."""
import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")
src = open("manuscript_src.md", encoding="utf-8").read()
meta = json.load(open("refs_meta.json", encoding="utf-8"))
refs = json.load(open("refs_resolved.json", encoding="utf-8"))
used = []
def auth(k):
    m = meta[k]; f = m["fam"]
    if m["n"] == 1: return f[0]
    if m["n"] == 2: return f"{f[0]} and {f[1]}"
    return f"{f[0]} et al."
def paren(k):
    used.append(k); return f"{auth(k)}, {meta[k]['year']}"
def narr(k):
    used.append(k); return f"{auth(k)} ({meta[k]['year']})"
def bare(k):
    used.append(k); return f"{auth(k)}, {meta[k]['year']}"
def sub(mo):
    body = mo.group(1)
    if body.startswith("@"):
        return narr(body[1:])
    if body.startswith("#"):
        return bare(body[1:])
    keys = [x.strip() for x in body.split(";")]
    for k in keys:
        if k not in meta: raise SystemExit(f"citacao sem referencia: {k}")
    return "(" + "; ".join(paren(k) for k in keys) + ")"
out = re.sub(r"\{([@#]?[a-z0-9]+(?:;[a-z0-9 ]+)*)\}", sub, src)
left = re.findall(r"\{[^}]*\}", out)
if left: print("AVISO chaves restantes:", left[:5])
cited = sorted(set(used), key=lambda k: (meta[k]["fam"][0].lower(), meta[k]["year"]))
unused = sorted(set(meta) - set(used))
lst = "\n\n".join(refs[k] for k in cited)
out = out.replace("## Drafting notes (remove before submission)", "## References\n\n" + lst + "\n\n---\n\n## Drafting notes (remove before submission)")
open("manuscript.md", "w", encoding="utf-8").write(out)
print(f"citadas: {len(cited)} | na lista mas nao citadas: {unused}")
words = len(re.sub(r"\[\[.*?\]\]", "", src.split("## Abstract")[1].split("## References")[0]).split())
print("palavras (corpo, aprox.):", words)

"""Resolve cada DOI no Crossref e gera a lista de referências (estilo Frontiers: Sobrenome Iniciais, ...,
(ano). Título. Revista volume, páginas. doi). Confere as citações (Autor et al., ano) do manuscrito."""
import json, re, sys, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding="utf-8")
refs = json.load(open("refs_doi.json"))
BIORXIV = {"10.1101/2025.06.14.659707": ("Passaro S, Corso G, Wohlwend J, Reveiz M, Thaler S, Ram Somnath V, et al.", 2025, "Boltz-2: Towards accurate and efficient binding affinity prediction. bioRxiv [Preprint]"),
           "10.1101/2024.11.19.624167": ("Wohlwend J, Corso G, Passaro S, Getz N, Reveiz M, Leidal K, et al.", 2024, "Boltz-1: Democratizing biomolecular interaction modeling. bioRxiv [Preprint]")}
def crossref(doi):
    r = urllib.request.urlopen(urllib.request.Request("https://api.crossref.org/works/" + urllib.parse.quote(doi), headers={"User-Agent": "design-inibidores (mailto:eulalio.santos@ufv.br)"}), timeout=30)
    return json.load(r)["message"]
def initials(given):
    parts = re.split(r"[\s\-]+", given.strip())
    return "".join(p[0].upper() for p in parts if p)
out, meta = {}, {}
for key, doi in refs.items():
    if doi in BIORXIV:
        a, y, t = BIORXIV[doi]
        out[key] = f"{a} ({y}). {t}. doi: {doi}"; meta[key] = {"fam": [a.split()[0]], "n": 9, "year": y}; continue
    m = crossref(doi)
    au = m.get("author", [])
    def fmt(x):
        if 'family' not in x: return x.get('name','?')
        return f"{x['family']} {initials(x.get('given','')) if x.get('given') else ''}".strip()
    names = [fmt(x) for x in au]
    astr = ", ".join(names) if len(names) <= 6 else ", ".join(names[:6]) + ", et al."
    pr = m.get("published-print", {}).get("date-parts", [[None]])[0][0] or m.get("issued", {}).get("date-parts", [[None]])[0][0]
    title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m["title"][0])).strip().rstrip(".")
    jn = (m.get("container-title") or [""])[0].replace("&amp;", "&")
    vol, pg, art = m.get("volume", ""), m.get("page", ""), m.get("article-number", "")
    loc = f" {vol}" + (f", {pg}" if pg else (f", {art}" if art else ""))
    AUTH_FIX = {"zhang2005": ("Zhang Y, Skolnick J", ["Zhang", "Skolnick"], 2),          # PubMed PMID 15849316
                "berman2000": ("Berman HM, Westbrook J, Feng Z, Gilliland G, Bhat TN, Weissig H, et al.", ["Berman", "Westbrook"], 8)}  # PMID 10592235
    if key in AUTH_FIX: astr = AUTH_FIX[key][0]
    if key == "patarroyo2017": loc, pr = " 24, 1040-1047", 2017
    TITLE_FIX = {"almeida2021": "Small peptides inhibit gut trypsin-like proteases and impair Anticarsia gemmatalis (Lepidoptera: Noctuidae) survival and development"}
    title = TITLE_FIX.get(key, title)
    out[key] = re.sub(r"\s+", " ", f"{astr} ({pr}). {title}. {jn}{loc}. doi: {doi}")
    fam = [x.get("family", x.get("name", "?")) for x in au]
    if fam and fam[0].startswith("The UniProt"): fam = ["UniProt Consortium"]
    meta[key] = {"fam": fam[:2], "n": len(fam) if fam[0] != "UniProt Consortium" else 1, "year": pr}
    if key in AUTH_FIX: meta[key].update({"fam": AUTH_FIX[key][1], "n": AUTH_FIX[key][2]})
    if key == "patarroyo2017":   # ano/paginas conforme PubMed (PMID 28925864: Protein Pept Lett 2017;24(11):1040-1047)
        pr = 2017; meta[key]["year"] = 2017
        out_over = True
    print(f"OK {key:20s} {meta[key]['fam'][0]} ({pr}) {jn[:30]}", flush=True)
norm=lambda t: t.replace("‐","-").replace("‑","-")
out={k:norm(v) for k,v in out.items()}
json.dump(out, open("refs_resolved.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump({k: {"fam":[norm(x) for x in v["fam"]],"n":v["n"],"year":v["year"]} for k, v in meta.items()}, open("refs_meta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

import json
import urllib.request
import urllib.parse

SPECIES = [
    "Bombyx mori",
    "Manduca sexta",
    "Plutella xylostella",
    "Spodoptera litura",
    "Spodoptera frugiperda",
    "Ostrinia nubilalis",
    "Diatraea saccharalis",
    "Heliothis virescens",
    "Chrysodeixis includens",
]

for sp in SPECIES:
    query = f'trypsin AND organism_name:"{sp}"'
    params = urllib.parse.urlencode({
        "query": query,
        "format": "json",
        "fields": "accession,protein_name,organism_name,length,xref_alphafolddb",
        "size": 10,
    })
    url = f"https://rest.uniprot.org/uniprotkb/search?{params}"
    print(f"\n=== {sp} ===")
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"  ERRO: {e}")
        continue
    results = data.get("results", [])
    if not results:
        print("  (nenhum resultado)")
        continue
    for r in results:
        acc = r.get("primaryAccession")
        entry_type = r.get("entryType", "?")
        pdesc = r.get("proteinDescription", {})
        name = pdesc.get("recommendedName", {}).get("fullName", {}).get("value")
        if not name:
            subs = pdesc.get("submissionNames", [])
            name = subs[0].get("fullName", {}).get("value", "?") if subs else "?"
        length = r.get("sequence", {}).get("length", "?")
        xrefs = r.get("uniProtKBCrossReferences", [])
        has_af = any(x.get("database") == "AlphaFoldDB" for x in xrefs)
        print(f"  {acc} | {name} | len={length} | {entry_type} | AlphaFoldDB={has_af}")

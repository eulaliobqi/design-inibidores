"""Baixa estruturas reais do AlphaFold DB para tripsinas de Lepidoptera bem documentadas.

Roda no servidor. Accessions escolhidos via UniProt REST real (busca 2026-07-18),
priorizando entradas com padrao de tripsina digestiva (~250-270aa) e AlphaFoldDB=True.
"""
import urllib.request
from pathlib import Path

SPECIES = {
    "Msexta": ("P35045", "Manduca sexta", "Trypsin, alkaline A (Swiss-Prot reviewed)"),
    "Bmori": ("A0A8R2C8B0", "Bombyx mori", "trypsin (TrEMBL)"),
    "Pxylostella": ("E2IGY7", "Plutella xylostella", "trypsin (TrEMBL)"),
    "Slitura": ("B3F884", "Spodoptera litura", "trypsin (TrEMBL)"),
    "Sfrugiperda": ("A0A089QDB3", "Spodoptera frugiperda", "trypsin (TrEMBL)"),
    "Onubilalis": ("Q6R561", "Ostrinia nubilalis", "Trypsin-like proteinase T25 (TrEMBL)"),
    "Dsaccharalis": ("T1QDI0", "Diatraea saccharalis", "Trypsin 2 (TrEMBL)"),
    "Hvirescens": ("I7D523", "Heliothis virescens", "Trypsin (TrEMBL)"),
    "Cincludens": ("A0A9P0BRD5", "Chrysodeixis includens", "trypsin (TrEMBL)"),
}

OUT_DIR = Path("data-nontargets")
OUT_DIR.mkdir(exist_ok=True)

for tag, (acc, species, desc) in SPECIES.items():
    out_pdb = OUT_DIR / f"{tag}-{acc}-AlphaFold.pdb"
    if out_pdb.exists() and out_pdb.stat().st_size > 1000:
        print(f"{tag} ({acc}): ja existe, pulando")
        continue
    found = False
    for v in [4, 3, 2, 1, 5, 6]:
        url = f"https://alphafold.ebi.ac.uk/files/AF-{acc}-F1-model_v{v}.pdb"
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                content = resp.read()
            out_pdb.write_bytes(content)
            n_ca = content.decode(errors="ignore").count(" CA ")
            print(f"{tag} ({acc}, {species}): OK v{v}, {len(content)} bytes, ~{n_ca} CA atoms -> {out_pdb}")
            found = True
            break
        except Exception as e:
            continue
    if not found:
        print(f"{tag} ({acc}, {species}): FALHOU (nenhuma versao AlphaFold DB disponivel) — {desc}")

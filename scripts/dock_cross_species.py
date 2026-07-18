"""dock_cross_species.py — Docking real do TOP-10 contra tripsinas de outras espécies de
Lepidoptera bem documentadas (R3).

Diferente de SpecificityAgent (não-alvo: afinidade BAIXA é boa), aqui cada espécie listada é
OUTRA PRAGA-ALVO: afinidade ALTA (comparável ao alvo primário A. gemmatalis/ACR157) é o resultado
desejado — indicaria eficácia de amplo espectro entre espécies-praga de Lepidoptera.

Centros/sítios lidos dos binding_site.json reais gerados por StructureAgent._analyze_single
(mesmo método validado nos 4 receptores primários). Generaliza dock_harmigera.py (mantido por
compatibilidade histórica) para as demais espécies.

Uso: conda run -n protein_design_env python scripts/dock_cross_species.py
"""
import json
import re
import subprocess
from pathlib import Path

from utils import build_peptide_pdbqt

SPECIES = {
    "Agemmatalis": ("data-nontargets/Agemmatalis-A0A2U8NFD7-AlphaFold.pdb", "outputs/structure_agemmatalis/binding_site.json"),
    "Harmigera": ("data-nontargets/Harmigera-B6CME8-ESMFold.pdb", "outputs/structure_harmigera/binding_site.json"),
    "Msexta": ("data-nontargets/Msexta-P35045-AlphaFold.pdb", "outputs/structure_msexta/binding_site.json"),
    "Bmori": ("data-nontargets/Bmori-A0A8R2C8B0-AlphaFold.pdb", "outputs/structure_bmori/binding_site.json"),
    "Pxylostella": ("data-nontargets/Pxylostella-E2IGY7-AlphaFold.pdb", "outputs/structure_pxylostella/binding_site.json"),
    "Slitura": ("data-nontargets/Slitura-B3F884-AlphaFold.pdb", "outputs/structure_slitura/binding_site.json"),
    "Sfrugiperda": ("data-nontargets/Sfrugiperda-A0A089QDB3-AlphaFold.pdb", "outputs/structure_sfrugiperda/binding_site.json"),
    "Onubilalis": ("data-nontargets/Onubilalis-Q6R561-AlphaFold.pdb", "outputs/structure_onubilalis/binding_site.json"),
}

TOP10 = [
    "SRTRR", "HRPRRPR", "RLREELKKAEEWLEKRRKEE", "SEEEVLAANEAYAAAHTAYN",
    "SALASIAAHQATFLAYLESK", "MGSLTAYLEAYAAENAAALA", "RLRAIWLEAEKLLEERRKKK",
    "MGYLTAYHQALAAQNAALLA", "RVKDQWLEAEKLLEERRKKK", "SARESIKKAYKTFLERYKKL",
]

WORKDIR = Path("outputs/cross_species_docking")


def prepare_receptor(tag: str, receptor_pdb: str, out_dir: Path) -> Path:
    pdbqt = out_dir / "receptor.pdbqt"
    if pdbqt.exists() and pdbqt.stat().st_size > 5000:
        return pdbqt
    proc = subprocess.run(
        ["obabel", receptor_pdb, "-O", str(pdbqt), "-h", "-xr"],
        capture_output=True, text=True, timeout=120,
    )
    if proc.returncode != 0 or not pdbqt.exists() or pdbqt.stat().st_size < 5000:
        raise RuntimeError(f"[{tag}] obabel receptor falhou: {proc.stderr[-300:]}")
    return pdbqt


def adaptive_grid(length: int) -> list:
    needed = int(length * 3.6) + 8
    s = max(40.0, float(needed))
    return [s, s, s]


def run_vina(rec_pdbqt: Path, lig_pdbqt: Path, out_dir: Path, center: list, size: list) -> float | None:
    out_pdbqt = out_dir / "docked.pdbqt"
    cmd = [
        "vina", "--receptor", str(rec_pdbqt), "--ligand", str(lig_pdbqt),
        "--out", str(out_pdbqt),
        "--center_x", str(center[0]), "--center_y", str(center[1]), "--center_z", str(center[2]),
        "--size_x", str(size[0]), "--size_y", str(size[1]), "--size_z", str(size[2]),
        "--exhaustiveness", "8", "--num_modes", "9",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    for line in (proc.stdout + proc.stderr).splitlines():
        m = re.search(r"^\s*1\s+([-\d.]+)", line)
        if m:
            return float(m.group(1))
    return None


def main():
    WORKDIR.mkdir(parents=True, exist_ok=True)
    all_results = {}
    for tag, (receptor_pdb, site_json) in SPECIES.items():
        site_path = Path(site_json)
        if not site_path.exists():
            print(f"[{tag}] SEM binding_site.json ({site_json}) — pulando, sem inventar centro")
            continue
        site = json.loads(site_path.read_text())
        center = site["consensus_center_xyz"]

        sp_dir = WORKDIR / tag
        sp_dir.mkdir(exist_ok=True)
        existing = sp_dir / "results.json"
        if existing.exists():
            prev = json.loads(existing.read_text())
            if prev and all(v is not None for v in prev.values()):
                print(f"[{tag}] resultados ja existem ({existing}), pulando (resume-safe)")
                all_results[tag] = prev
                continue
        try:
            rec_pdbqt = prepare_receptor(tag, receptor_pdb, sp_dir)
        except RuntimeError as e:
            print(e)
            continue
        print(f"[{tag}] receptor real preparado ({rec_pdbqt.stat().st_size} bytes), centro={center}")

        results = {}
        for seq in TOP10:
            out_dir = sp_dir / seq[:15]
            out_dir.mkdir(exist_ok=True)
            lig_pdbqt = build_peptide_pdbqt(seq, center, out_dir, logger=None)
            if lig_pdbqt is None:
                results[seq] = None
                print(f"[{tag}] {seq}: falhou construção do ligante")
                continue
            aff = run_vina(rec_pdbqt, lig_pdbqt, out_dir, center, adaptive_grid(len(seq)))
            results[seq] = aff
            print(f"[{tag}] {seq} (len={len(seq)}): Vina real = {aff}")

        all_results[tag] = results
        (sp_dir / "results.json").write_text(json.dumps(results, indent=2))

    (WORKDIR / "all_cross_species_results.json").write_text(json.dumps(all_results, indent=2))
    print(f"\nSalvo: {WORKDIR / 'all_cross_species_results.json'}")


if __name__ == "__main__":
    main()

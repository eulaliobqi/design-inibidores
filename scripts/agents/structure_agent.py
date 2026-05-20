"""StructureAgent — Mapeia o sítio S1 da tripsina de Lepidoptera.

Etapas:
  1. Parseia os 4 PDBs (sem chain IDs)
  2. Identifica a tríade catalítica His-Asp-Ser por proximidade espacial
  3. Detecta o Asp específico do bolso S1 (mais próximo do centro catalítico)
  4. Executa fpocket para detecção automática de cavidades (opcional)
  5. Calcula centróide do sítio → coordenadas para docking
  6. Salva hotspots.json e binding_site.json para etapas seguintes
"""
import json
import subprocess
import numpy as np
from pathlib import Path
from itertools import combinations

from .base_agent import BaseAgent
from ..utils import load_pdb_atoms, get_residues, check_fpocket


class StructureAgent(BaseAgent):

    def run(self, pdb_files: list[str]) -> dict:
        self.logger.info(f"Analisando {len(pdb_files)} estruturas de tripsina...")
        all_sites = []

        for pdb in pdb_files:
            site = self._analyze_single(pdb)
            if site:
                all_sites.append(site)
                self.logger.info(
                    f"  {Path(pdb).name}: catalytic_center={site['center_xyz']}  "
                    f"  triad={site['triad_resseqs']}  "
                    f"  s1_asp={site['s1_asp_resseq']}"
                )

        if not all_sites:
            self.logger.error("Nenhum sítio ativo detectado. Verifique os PDBs.")
            raise RuntimeError("Structure analysis failed.")

        # Consenso: média dos centros de ligação
        centers = np.array([s["center_xyz"] for s in all_sites])
        consensus_center = centers.mean(axis=0).tolist()

        # Hotspots: resíduos funcionais conservados
        hotspots = self._consensus_hotspots(all_sites)

        result = {
            "n_structures": len(all_sites),
            "consensus_center_xyz": [round(x, 3) for x in consensus_center],
            "hotspot_residues": hotspots,
            "individual_sites": all_sites,
            "pocket_size_angstrom": self.config.get("structure", {}).get("s1_pocket_depth_cutoff", 8.0),
        }

        # Salvar
        out = self.workdir / "binding_site.json"
        out.write_text(json.dumps(result, indent=2))
        # Hotspots simplificado para RFdiffusion
        (self.workdir / "hotspots.json").write_text(
            json.dumps(hotspots, indent=2)
        )

        self.logger.info(f"Sítio consenso: {consensus_center}")
        self.logger.info(f"Hotspots identificados: {hotspots}")
        return result

    # ─── Análise individual ─────────────────────────────────────────────────

    def _analyze_single(self, pdb_path: str) -> dict | None:
        atoms = load_pdb_atoms(pdb_path)
        residues = get_residues(atoms)

        if not residues:
            return None

        # Detecta tríade catalítica: HIS + ASP + SER em ≤ 15 Å entre si
        triad = self._find_catalytic_triad(residues)
        if triad is None:
            self.logger.warning(f"  Tríade não encontrada em {Path(pdb_path).name}")
            triad = self._fallback_triad(residues)

        if triad is None:
            return None

        his_id, asp_id, ser_id = triad
        # Centro catalítico: média entre His (NE2), Asp (OD1), Ser (OG)
        center = self._triad_center(residues, his_id, asp_id, ser_id)

        # Asp do bolso S1: asp mais próximo ao centro catalítico (exceto asp da tríade)
        s1_asp = self._find_s1_asp(residues, asp_id, center)

        # Resíduos hotspot: todos na esfera de 8 Å em torno do centro
        radius = self.config.get("structure", {}).get("s1_pocket_depth_cutoff", 8.0)
        hotspot_ids = self._residues_in_sphere(residues, center, radius)

        # fpocket (se disponível)
        pockets = []
        if check_fpocket():
            pockets = self._run_fpocket(pdb_path, center)

        return {
            "pdb": str(pdb_path),
            "triad_resseqs": {"HIS": his_id, "ASP": asp_id, "SER": ser_id},
            "s1_asp_resseq": s1_asp,
            "center_xyz": [round(x, 3) for x in center],
            "hotspot_resseqs": sorted(hotspot_ids),
            "fpocket": pockets,
        }

    def _find_catalytic_triad(self, residues: dict) -> tuple | None:
        """Busca HIS-ASP-SER próximos entre si (tríade de serina-protease)."""
        his_ids = [r for r, v in residues.items() if v["resname"] == "HIS"]
        asp_ids = [r for r, v in residues.items() if v["resname"] == "ASP"]
        ser_ids = [r for r, v in residues.items() if v["resname"] == "SER"]

        best = None
        best_dist = float("inf")

        for h in his_ids:
            for d in asp_ids:
                for s in ser_ids:
                    dist_hd = self._centroid_dist(residues[h], residues[d])
                    dist_hs = self._centroid_dist(residues[h], residues[s])
                    dist_ds = self._centroid_dist(residues[d], residues[s])
                    max_d = max(dist_hd, dist_hs, dist_ds)
                    total = dist_hd + dist_hs + dist_ds
                    # Tríade catalítica: inter-resíduo tipicamente < 12 Å
                    if max_d < 15.0 and total < best_dist:
                        best_dist = total
                        best = (h, d, s)

        return best

    def _fallback_triad(self, residues: dict) -> tuple | None:
        """Fallback: usa HIS mais central, ASP e SER mais próximos."""
        his_ids = [r for r, v in residues.items() if v["resname"] == "HIS"]
        if not his_ids:
            return None
        asp_ids = [r for r, v in residues.items() if v["resname"] == "ASP"]
        ser_ids = [r for r, v in residues.items() if v["resname"] == "SER"]
        if not asp_ids or not ser_ids:
            return None

        all_centroids = np.array([residues[r]["centroid"] for r in residues])
        center = all_centroids.mean(axis=0)

        # His mais próxima do centro da proteína
        his_id = min(his_ids, key=lambda h:
                     np.linalg.norm(np.array(residues[h]["centroid"]) - center))
        hc = np.array(residues[his_id]["centroid"])

        asp_id = min(asp_ids, key=lambda d:
                     np.linalg.norm(np.array(residues[d]["centroid"]) - hc))
        ser_id = min(ser_ids, key=lambda s:
                     np.linalg.norm(np.array(residues[s]["centroid"]) - hc))
        return (his_id, asp_id, ser_id)

    def _triad_center(self, residues, his_id, asp_id, ser_id) -> list:
        coords = []
        for rid in [his_id, asp_id, ser_id]:
            coords.extend([[a["x"], a["y"], a["z"]]
                           for a in residues[rid]["atoms"]
                           if a["name"] in ("NE2", "OD1", "OD2", "OG", "CA")])
        if not coords:
            coords = [residues[r]["centroid"] for r in [his_id, asp_id, ser_id]]
        return list(np.mean(coords, axis=0))

    def _find_s1_asp(self, residues, triad_asp_id, center) -> int | None:
        asp_ids = [r for r, v in residues.items()
                   if v["resname"] == "ASP" and r != triad_asp_id]
        if not asp_ids:
            return triad_asp_id
        center_arr = np.array(center)
        return min(asp_ids, key=lambda d:
                   np.linalg.norm(np.array(residues[d]["centroid"]) - center_arr))

    def _residues_in_sphere(self, residues, center, radius) -> list:
        center_arr = np.array(center)
        return [r for r, v in residues.items()
                if np.linalg.norm(np.array(v["centroid"]) - center_arr) <= radius]

    def _centroid_dist(self, r1: dict, r2: dict) -> float:
        return float(np.linalg.norm(
            np.array(r1["centroid"]) - np.array(r2["centroid"])
        ))

    def _run_fpocket(self, pdb_path: str, center: list) -> list:
        """Executa fpocket e retorna pockets ordenados por druggability."""
        try:
            out_dir = self.workdir / f"fpocket_{Path(pdb_path).stem}"
            result = subprocess.run(
                ["fpocket", "-f", pdb_path, "-o", str(out_dir)],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode != 0:
                return []
            # Parse info file
            info_file = out_dir / f"{Path(pdb_path).stem}_info.txt"
            if not info_file.exists():
                return []
            pockets = self._parse_fpocket_info(info_file)
            return pockets[:3]  # top 3 pockets
        except Exception as e:
            self.logger.warning(f"fpocket falhou: {e}")
            return []

    def _parse_fpocket_info(self, info_file: Path) -> list:
        pockets = []
        current = {}
        with open(info_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith("Pocket"):
                    if current:
                        pockets.append(current)
                    current = {"id": line}
                elif ":" in line:
                    key, val = line.split(":", 1)
                    try:
                        current[key.strip()] = float(val.strip())
                    except ValueError:
                        current[key.strip()] = val.strip()
        if current:
            pockets.append(current)
        return sorted(pockets,
                      key=lambda p: p.get("Drug Score", 0), reverse=True)

    def _consensus_hotspots(self, all_sites: list) -> list:
        """Resíduos hotspot presentes em ≥ 50% das estruturas."""
        from collections import Counter
        all_ids = []
        for s in all_sites:
            all_ids.extend(s["hotspot_resseqs"])
        counts = Counter(all_ids)
        threshold = len(all_sites) * 0.5
        return sorted(r for r, c in counts.items() if c >= threshold)

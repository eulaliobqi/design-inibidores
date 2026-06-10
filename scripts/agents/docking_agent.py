"""DockingAgent — Valida afinidade via AutoDock Vina.

Para cada candidato top (sequências do ProteinMPNN):
  1. Constrói PDB do peptídeo
  2. Converte para PDBQT
  3. Executa Vina com grid centrado no sítio S1
  4. Retorna afinidades e poses
"""
import json
import re
import subprocess
import tempfile
from pathlib import Path

from .base_agent import BaseAgent
from ..utils import check_vina, load_pdb_atoms, write_pdb_atoms, AA_1TO3


class DockingAgent(BaseAgent):

    def run(self, receptor_pdb: str, sequences_data: dict, binding_site: dict) -> dict:
        if not check_vina():
            self._warn_missing_tool(
                "AutoDock Vina",
                "Instalar: conda install -c conda-forge vina"
            )
            results = self._heuristic_scores(sequences_data)
            # Sempre gravar em disco para que o ranking carregue corretamente
            (self.workdir / "docking_results.json").write_text(
                json.dumps(results, indent=2, default=str)
            )
            return results

        center = binding_site["consensus_center_xyz"]
        cfg = self.config.get("docking", {})
        size = [cfg.get("size_x", 25), cfg.get("size_y", 25), cfg.get("size_z", 25)]

        # Preparar receptor PDBQT (apenas uma vez)
        rec_pdbqt = self._prepare_receptor_pdbqt(receptor_pdb)

        results = {}
        candidates = self._top_candidates(sequences_data)
        self.logger.info(f"Docking Vina: {len(candidates)} candidatos...")

        for item in candidates:
            seq = item["sequence"]
            stem = f"len{item['length']}_{seq[:8]}"
            out_dir = self.workdir / stem
            out_dir.mkdir(exist_ok=True)

            lig_pdbqt = self._build_peptide_pdbqt(seq, center, out_dir)
            if lig_pdbqt is None:
                continue

            result = self._run_vina(rec_pdbqt, lig_pdbqt, center, size,
                                    cfg.get("exhaustiveness", 32), out_dir)
            result["sequence"] = seq
            result["length"] = item["length"]
            results[stem] = result

        # Salvar
        (self.workdir / "docking_results.json").write_text(
            json.dumps(results, indent=2, default=str)
        )
        self.logger.info(
            f"Docking concluído. Melhor: "
            f"{min(results.values(), key=lambda x: x.get('best_affinity_kcal', 0), default={}).get('sequence', '-')}"
        )
        return results

    def _prepare_receptor_pdbqt(self, receptor_pdb: str) -> Path:
        pdbqt = self.workdir / "receptor.pdbqt"
        if pdbqt.exists():
            return pdbqt

        # Tentar com obabel ou meeko
        if subprocess.run(["which", "obabel"], capture_output=True).returncode == 0:
            subprocess.run(
                ["obabel", receptor_pdb, "-O", str(pdbqt), "-xr"],
                capture_output=True
            )
        elif subprocess.run(["which", "prepare_receptor4.py"], capture_output=True).returncode == 0:
            subprocess.run(
                ["prepare_receptor4.py", "-r", receptor_pdb, "-o", str(pdbqt)],
                capture_output=True
            )
        else:
            # Fallback: renomear .pdb → .pdbqt (funcional para Vina moderno)
            import shutil
            shutil.copy(receptor_pdb, str(pdbqt))

        return pdbqt

    def _build_peptide_pdbqt(self, sequence: str, center: list, out_dir: Path) -> Path | None:
        pdb_path = out_dir / "peptide.pdb"
        pdbqt_path = out_dir / "peptide.pdbqt"

        # Construir peptídeo linear simples
        cx, cy, cz = center
        with open(pdb_path, "w") as f:
            for i, aa in enumerate(sequence):
                resname = AA_1TO3.get(aa, "ALA")
                f.write(
                    f"ATOM  {i+1:5d}  CA  {resname} B{i+1:4d}    "
                    f"{cx + i*3.8:8.3f}{cy:8.3f}{cz:8.3f}  1.00  0.00           C\n"
                )
            f.write("END\n")

        # Converter para PDBQT
        if subprocess.run(["which", "obabel"], capture_output=True).returncode == 0:
            proc = subprocess.run(
                ["obabel", str(pdb_path), "-O", str(pdbqt_path)],
                capture_output=True
            )
            if proc.returncode == 0 and pdbqt_path.exists():
                return pdbqt_path
        elif subprocess.run(["which", "prepare_ligand4.py"], capture_output=True).returncode == 0:
            subprocess.run(
                ["prepare_ligand4.py", "-l", str(pdb_path), "-o", str(pdbqt_path)],
                capture_output=True
            )
            if pdbqt_path.exists():
                return pdbqt_path

        # Último recurso: copiar pdb como pdbqt
        import shutil
        shutil.copy(str(pdb_path), str(pdbqt_path))
        return pdbqt_path

    def _run_vina(self, receptor_pdbqt: Path, ligand_pdbqt: Path,
                  center: list, size: list, exhaustiveness: int,
                  out_dir: Path) -> dict:
        out_pdbqt = out_dir / "docked.pdbqt"
        log_file = out_dir / "vina.log"

        cmd = [
            "vina",
            "--receptor", str(receptor_pdbqt),
            "--ligand", str(ligand_pdbqt),
            "--out", str(out_pdbqt),
            "--log", str(log_file),
            "--center_x", str(round(center[0], 3)),
            "--center_y", str(round(center[1], 3)),
            "--center_z", str(round(center[2], 3)),
            "--size_x", str(size[0]),
            "--size_y", str(size[1]),
            "--size_z", str(size[2]),
            "--exhaustiveness", str(exhaustiveness),
            "--num_modes", str(self.config.get("docking", {}).get("num_modes", 9)),
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        # Parsear log
        affinities = []
        log_text = proc.stdout + proc.stderr
        if log_file.exists():
            log_text += log_file.read_text()

        for line in log_text.splitlines():
            m = re.search(r"^\s+\d+\s+([-\d.]+)\s+", line)
            if m:
                affinities.append(float(m.group(1)))

        return {
            "best_affinity_kcal": affinities[0] if affinities else None,
            "all_affinities": affinities,
            "docked_pdbqt": str(out_pdbqt) if out_pdbqt.exists() else None,
            "vina_returncode": proc.returncode,
        }

    def _top_candidates(self, sequences_data: dict) -> list[dict]:
        # top_for_docking do config ML (padrão 200) para dataset de labels
        limit = self.config.get("ml_dataset", {}).get("top_for_docking", 200)
        candidates = []
        # Ordenar por heurística (charge + hydrophobic) para selecionar melhores
        for stem, data in sequences_data.items():
            props_list = data.get("properties", [])
            for i, seq in enumerate(data["sequences"]):
                if not seq:
                    continue
                p = props_list[i] if i < len(props_list) else {}
                score = (
                    abs(p.get("net_charge", 0)) * 1.2
                    + p.get("frac_hydrophobic", 0) * 3.0
                    + p.get("n_arg_lys", 0) * 0.5
                )
                candidates.append({
                    "sequence": seq,
                    "length": data["length"],
                    "_heuristic": score,
                })
        candidates.sort(key=lambda x: -x["_heuristic"])
        return candidates[:limit]

    def _heuristic_scores(self, sequences_data: dict) -> dict:
        """Estima afinidade heuristicamente para todo o dataset."""
        results = {}
        for stem, data in sequences_data.items():
            props_list = data.get("properties", [])
            for i, seq in enumerate(data["sequences"]):
                if not seq:
                    continue
                # Chave única por sequência completa (sem colisão)
                key = seq
                if key in results:
                    continue  # já calculado (sequência duplicada entre backbones)
                p = props_list[i] if i < len(props_list) else {}
                basic = p.get("n_arg_lys", sum(1 for aa in seq if aa in "RK"))
                frac_h = p.get("frac_hydrophobic",
                               sum(1 for aa in seq if aa in "AILMFWV") / len(seq))
                boman = p.get("boman_index", 0)
                # Heurística multi-fator: carga básica + hidrofobicidade + boman
                estimated = -(basic * 1.2 + frac_h * len(seq) * 0.5
                               + abs(boman) * 0.3 + len(seq) * 0.1)
                results[key] = {
                    "sequence": seq,
                    "length": data["length"],
                    "best_affinity_kcal": round(estimated, 2),
                    "method": "heuristic",
                }
        self.logger.info(f"Heuristic docking: {len(results)} sequências únicas pontuadas")
        return results

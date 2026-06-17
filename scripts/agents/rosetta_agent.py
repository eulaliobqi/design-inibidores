"""RosettaAgent — Refina complexos tripsina-peptídeo com FlexPepDock ou PyRosetta.

Monta o complexo (receptor + peptídeo), executa FlexPepDock para
otimização do backbone do peptídeo na interface, e extrai I_sc (interface score).
"""
import json
import os
import subprocess
from pathlib import Path

from .base_agent import BaseAgent
from ..utils import find_rosetta, load_pdb_atoms, write_pdb_atoms


class RosettaAgent(BaseAgent):

    def run(self, receptor_pdb: str, sequences_data: dict, binding_site: dict) -> dict:
        rosetta_path = find_rosetta(self.config)
        cfg = self.config.get("rosetta", {})
        nstruct = cfg.get("flexpepdock_nstruct", 10)
        center = binding_site["consensus_center_xyz"]

        results = {}
        top_complexes = self._select_top_sequences(sequences_data)

        self.logger.info(f"Refinando {len(top_complexes)} candidatos com Rosetta...")

        for item in top_complexes:
            seq = item["sequence"]
            stem = f"len{item['length']}_{seq[:8]}"
            out_dir = self.workdir / stem
            out_dir.mkdir(exist_ok=True)

            # Montar PDB do complexo
            complex_pdb = out_dir / "complex.pdb"
            self._build_complex(receptor_pdb, seq, center, complex_pdb)

            if rosetta_path == Path("pyrosetta"):
                scored = self._run_pyrosetta(complex_pdb, seq, out_dir, nstruct)
            elif rosetta_path:
                scored = self._run_flexpepdock(rosetta_path, complex_pdb, out_dir, nstruct)
            else:
                scored = self._fallback_score(seq, complex_pdb)
                if not results:
                    self._warn_missing_tool(
                        "Rosetta/PyRosetta",
                        "Instalar PyRosetta: https://www.pyrosetta.org/downloads"
                    )

            results[stem] = {
                "sequence": seq,
                "length": item["length"],
                "complex_pdb": str(complex_pdb),
                **scored,
            }

        # Ordenar por interface score
        sorted_results = dict(sorted(
            results.items(),
            key=lambda x: x[1].get("I_sc", 0)
        ))

        (self.workdir / "rosetta_scores.json").write_text(
            json.dumps(sorted_results, indent=2, default=str)
        )
        self.logger.info(f"Rosetta: {len(results)} complexos refinados.")
        return sorted_results

    def _select_top_sequences(self, sequences_data: dict) -> list[dict]:
        """Seleciona top candidatos por heurística para refinamento Rosetta."""
        limit = self.config.get("optimization", {}).get("top_k", 10)
        candidates = []

        for stem, data in sequences_data.items():
            props = data.get("properties", [])
            for i, seq in enumerate(data["sequences"]):
                if not seq:
                    continue
                p = props[i] if i < len(props) else {}
                score = (
                    p.get("n_arg_lys", 0) * 1.0
                    + p.get("frac_hydrophobic", 0) * 3.0
                    + abs(p.get("hydrophobicity_kd", 0)) * 0.5
                )
                candidates.append({
                    "sequence": seq,
                    "length": data["length"],
                    "n_arg_lys": p.get("n_arg_lys", 0),
                    "_score": score,
                })

        candidates.sort(key=lambda x: -x["_score"])
        return candidates[:limit]

    def _build_complex(self, receptor_pdb: str, sequence: str,
                        center: list, out_path: Path):
        """Constrói PDB do complexo posicionando peptídeo no sítio ativo.

        Tenta PeptideBuilder (all-atom) para scoring PyRosetta correto;
        cai para CA-only se PeptideBuilder não disponível.
        """
        rec_atoms = load_pdb_atoms(receptor_pdb)
        for a in rec_atoms:
            a["chain"] = "A"

        pep_pdb = out_path.parent / "peptide_b.pdb"
        if self._build_allatom_pdb(sequence, center, pep_pdb):
            # Combinar receptor (atoms) + peptídeo all-atom (PDB)
            pep_atoms = load_pdb_atoms(str(pep_pdb))
            for a in pep_atoms:
                a["chain"] = "B"
        else:
            pep_atoms = self._build_linear_pdb_atoms(sequence, center)

        all_atoms = rec_atoms + pep_atoms
        for i, a in enumerate(all_atoms):
            a["serial"] = i + 1
        write_pdb_atoms(all_atoms, str(out_path))

    def _build_linear_pdb_atoms(self, sequence: str, center: list) -> list[dict]:
        """Cria átomos CA para representar peptídeo linear (fallback CA-only)."""
        cx, cy, cz = center
        atoms = []
        for i, aa in enumerate(sequence):
            from ..utils import AA_1TO3
            atoms.append({
                "serial": 9000 + i,
                "name": "CA",
                "resname": AA_1TO3.get(aa, "ALA"),
                "chain": "B",
                "resseq": i + 1,
                "x": cx + i * 3.8,
                "y": cy,
                "z": cz,
            })
        return atoms

    def _build_allatom_pdb(self, sequence: str, center: list, pdb_path: Path) -> bool:
        """Gera PDB all-atom via PeptideBuilder, centralizado no sítio.

        Necessário para PyRosetta: FastRelax e InterfaceAnalyzerMover
        requerem backbone completo (N, CA, C, O) para scoring significativo.
        """
        try:
            import numpy as np
            import PeptideBuilder
            from PeptideBuilder import Geometry
            import Bio.PDB

            first_aa = sequence[0] if sequence[0] not in ("B", "X") else "A"
            try:
                geo = Geometry.geometry(first_aa)
            except Exception:
                geo = Geometry.geometry("A")
            structure = PeptideBuilder.initialize_res(geo)

            for aa in sequence[1:]:
                try:
                    g = Geometry.geometry(aa)
                except Exception:
                    g = Geometry.geometry("A")
                PeptideBuilder.add_residue(structure, g)

            target = np.array([float(v) for v in center])
            coords = np.array([a.coord for a in structure.get_atoms()])
            com = coords.mean(axis=0)
            offset = target - com
            for atom in structure.get_atoms():
                atom.coord += offset

            # Renomear para cadeia B
            for chain in structure.get_chains():
                chain.id = "B"

            io = Bio.PDB.PDBIO()
            io.set_structure(structure)
            io.save(str(pdb_path))
            return True
        except Exception as e:
            self.logger.warning(f"PeptideBuilder all-atom falhou ({sequence[:6]}): {e}")
            return False

    def _run_pyrosetta(self, complex_pdb: Path, seq: str,
                       out_dir: Path, nstruct: int) -> dict:
        try:
            from pyrosetta import pose_from_pdb, init
            from pyrosetta.rosetta.protocols.relax import FastRelax
            from pyrosetta.rosetta.core.scoring import get_score_function
            from pyrosetta.rosetta.protocols.analysis import InterfaceAnalyzerMover

            init("-mute all -ignore_unrecognized_res")
            pose = pose_from_pdb(str(complex_pdb))

            # FastRelax para minimização da interface
            sfxn = get_score_function()
            relax = FastRelax()
            relax.set_scorefxn(sfxn)
            relax.apply(pose)

            total = sfxn(pose)

            # Interface score real: ΔΔG de binding cadeia A (receptor) vs B (peptídeo)
            ia = InterfaceAnalyzerMover("A_B")
            ia.apply(pose)
            i_sc = ia.get_interface_dG()

            best_pdb = out_dir / "refined_best.pdb"
            pose.dump_pdb(str(best_pdb))

            return {
                "I_sc": round(float(i_sc), 3),
                "total_score": round(float(total), 3),
                "refined_pdb": str(best_pdb),
                "method": "pyrosetta_fastrelax_interface",
            }
        except Exception as e:
            self.logger.error(f"PyRosetta erro: {e}")
            return self._fallback_score(seq, complex_pdb)

    def _run_flexpepdock(self, rosetta_path: Path, complex_pdb: Path,
                          out_dir: Path, nstruct: int) -> dict:
        """Executa FlexPepDocking binário."""
        bin_candidates = [
            rosetta_path / "main/source/bin/FlexPepDocking.static.linuxgccrelease",
            rosetta_path / "main/source/bin/FlexPepDocking.default.linuxgccrelease",
        ]
        binary = next((b for b in bin_candidates if b.exists()), None)
        if not binary:
            return self._fallback_score(str(complex_pdb.stem), complex_pdb)

        cmd = [
            str(binary),
            "-s", str(complex_pdb),
            "-out:path:pdb", str(out_dir),
            "-peptide_loop_model",
            "-ex1", "-ex2",
            "-use_input_sc",
            f"-nstruct {nstruct}",
            "-out:prefix", "refined_",
            "-score:weights", "ref2015",
        ]
        proc = subprocess.run(
            " ".join(cmd), shell=True, capture_output=True, text=True, timeout=1800
        )
        if proc.returncode != 0:
            self.logger.error(f"FlexPepDock falhou: {proc.stderr[-300:]}")
            return self._fallback_score(str(complex_pdb.stem), complex_pdb)

        # Parse score file
        score_file = out_dir / "score.sc"
        return self._parse_score_file(score_file)

    def _parse_score_file(self, score_file: Path) -> dict:
        if not score_file.exists():
            return {"I_sc": 0.0, "total_score": 0.0}
        scores = []
        with open(score_file) as f:
            headers = None
            for line in f:
                parts = line.split()
                if "SCORE:" in line and "total_score" in line:
                    headers = parts
                elif "SCORE:" in line and headers:
                    row = dict(zip(headers, parts))
                    try:
                        scores.append({
                            "total_score": float(row.get("total_score", 0)),
                            "I_sc": float(row.get("I_sc", 0)),
                            "pdb": row.get("description", ""),
                        })
                    except ValueError:
                        pass
        if not scores:
            return {"I_sc": 0.0, "total_score": 0.0}
        best = min(scores, key=lambda x: x["I_sc"])
        return {"I_sc": best["I_sc"], "total_score": best["total_score"],
                "method": "flexpepdock"}

    def _fallback_score(self, seq: str, pdb: Path) -> dict:
        """Score heurístico baseado na composição de aminoácidos."""
        basic = sum(1 for aa in seq if aa in "RK")
        hydrophobic = sum(1 for aa in seq if aa in "AILMFWV")
        # Score estimado: mais básicos e hidrofóbicos = melhor (mais negativo)
        estimated_I_sc = -(basic * 0.8 + hydrophobic * 0.3)
        return {
            "I_sc": round(estimated_I_sc, 3),
            "total_score": round(estimated_I_sc * 2, 3),
            "method": "heuristic_fallback",
        }

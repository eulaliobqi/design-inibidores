"""DockingAgent — Valida afinidade via AutoDock Vina.

Para cada candidato top (sequências do ProteinMPNN):
  1. Constrói PDB do peptídeo
  2. Converte para PDBQT
  3. Executa Vina com grid centrado no sítio S1
  4. Retorna afinidades e poses
"""
import hashlib
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
        # Tamanho base do grid; _adaptive_grid_size() expande para peptídeos longos
        base_size = [cfg.get("size_x", 40), cfg.get("size_y", 40), cfg.get("size_z", 40)]

        # Preparar receptor PDBQT (apenas uma vez)
        rec_pdbqt = self._prepare_receptor_pdbqt(receptor_pdb)

        results = {}
        results_file = self.workdir / "docking_results.json"
        if cfg.get("forced_sequences") and results_file.exists():
            # Sequências forçadas ampliam o pool já dockado — mescla em vez de sobrescrever
            results = json.loads(results_file.read_text())
            self.logger.info(f"Mesclando com {len(results)} resultados de docking já existentes.")

        candidates = self._top_candidates(sequences_data)
        self.logger.info(f"Docking Vina: {len(candidates)} candidatos...")

        for item in candidates:
            seq = item["sequence"]
            # Pasta em disco: hash evita colisão entre variantes MPNN quase-idênticas
            # (ex.: família "GGATGAEI..." — 7 sequências distintas com o mesmo seq[:8]).
            seq_hash = hashlib.md5(seq.encode()).hexdigest()[:6]
            stem = f"len{item['length']}_{seq[:8]}_{seq_hash}"
            out_dir = self.workdir / stem
            out_dir.mkdir(exist_ok=True)

            lig_pdbqt = self._build_peptide_pdbqt(seq, center, out_dir)
            if lig_pdbqt is None:
                continue

            size = self._adaptive_grid_size(len(item["sequence"]), base_size)
            result = self._run_vina(rec_pdbqt, lig_pdbqt, center, size,
                                    cfg.get("exhaustiveness", 8), out_dir)
            result["sequence"] = seq
            result["length"] = item["length"]
            results[seq] = result

        # Salvar
        (self.workdir / "docking_results.json").write_text(
            json.dumps(results, indent=2, default=str)
        )
        valid = [v for v in results.values() if v.get("best_affinity_kcal") is not None]
        best_seq = min(valid, key=lambda x: x["best_affinity_kcal"], default={}).get("sequence", "-")
        self.logger.info(f"Docking concluído. Melhor: {best_seq} ({len(valid)}/{len(results)} poses válidas)")
        return results

    def _prepare_receptor_pdbqt(self, receptor_pdb: str) -> Path:
        pdbqt = self.workdir / "receptor.pdbqt"
        # Só reutiliza cache se gerado com obabel (> 5 kB); ignora versão mínima antiga
        if pdbqt.exists() and pdbqt.stat().st_size > 5000:
            return pdbqt

        ob = subprocess.run(["which", "obabel"], capture_output=True)
        if ob.returncode == 0:
            # -h: adicionar hidrogênios polares; -xr: receptor rígido sem torsdof
            proc = subprocess.run(
                ["obabel", receptor_pdb, "-O", str(pdbqt), "-h", "-xr"],
                capture_output=True, text=True, timeout=120
            )
            if proc.returncode == 0 and pdbqt.exists() and pdbqt.stat().st_size > 5000:
                self.logger.info(f"Receptor PDBQT gerado via obabel ({pdbqt.stat().st_size} bytes)")
                return pdbqt
            self.logger.warning(f"obabel receptor falhou: {proc.stderr[:200]}")

        if subprocess.run(["which", "prepare_receptor4.py"], capture_output=True).returncode == 0:
            proc = subprocess.run(
                ["prepare_receptor4.py", "-r", receptor_pdb, "-o", str(pdbqt)],
                capture_output=True
            )
            if proc.returncode == 0 and pdbqt.exists():
                return pdbqt

        # Fallback manual: adicionar colunas de carga e tipo AD4 ao PDB
        self.logger.warning("Receptor PDBQT: usando conversão mínima (sem H) — Vina pode falhar")
        self._pdb_to_pdbqt_minimal(receptor_pdb, str(pdbqt))
        return pdbqt

    def _pdb_to_pdbqt_minimal(self, pdb_in: str, pdbqt_out: str):
        """Converte PDB para PDBQT adicionando charge=0 e tipo AD4 baseado no elemento."""
        element_to_ad4 = {
            "C": "C", "N": "N", "O": "OA", "S": "SA",
            "H": "HD", "P": "P", "F": "F", "CL": "CL", "BR": "BR",
        }
        with open(pdb_in) as fi, open(pdbqt_out, "w") as fo:
            for line in fi:
                if line.startswith(("ATOM", "HETATM")):
                    element = line[76:78].strip().upper() if len(line) > 76 else ""
                    if not element:
                        element = line[12:16].strip().lstrip("0123456789")[0].upper()
                    atype = element_to_ad4.get(element, "C")
                    fo.write(line[:66].ljust(66) + f"    0.000 {atype}\n")
                elif line.startswith("END"):
                    fo.write(line)
                else:
                    fo.write(line)

    def _build_peptide_pdbqt(self, sequence: str, center: list, out_dir: Path) -> Path | None:
        """Constrói PDBQT rígido do peptídeo para Vina.

        Docking rígido (-xr) porque peptídeos > 8 aa têm > 32 ligações
        torsionais (phi+psi+chi), acima do limite do Vina. Para triagem
        de ML labels, docking rígido ainda dá scores relativos úteis.
        """
        pdb_path = out_dir / "peptide.pdb"
        pdbqt_path = out_dir / "peptide.pdbqt"

        # Tentar gerar estrutura all-atom via PeptideBuilder
        built = self._build_allatom_pdb(sequence, center, pdb_path)

        if built and subprocess.run(["which", "obabel"], capture_output=True).returncode == 0:
            # Sem -xr: obabel em modo ligante gera tipos AD4 corretos (N, OA, SA).
            # -xr (receptor rígido) atribui NA ao backbone N → Vina rejeita como ligante.
            # _ensure_ligand_pdbqt_format converte para formato rígido (ROOT/ENDROOT/TORSDOF 0).
            proc = subprocess.run(
                ["obabel", str(pdb_path), "-O", str(pdbqt_path), "-h"],
                capture_output=True, timeout=60
            )
            if proc.returncode == 0 and pdbqt_path.exists() and pdbqt_path.stat().st_size > 100:
                # obabel -xr em fragmento proteico gera PDBQT sem ROOT/ENDROOT/TORSDOF
                # (formato receptor, não ligante) — Vina rejeita; adicionar wrapper
                self._ensure_ligand_pdbqt_format(pdbqt_path)
                return pdbqt_path
            self.logger.warning(f"obabel peptide falhou ({sequence[:8]}): {proc.stderr[:80]}")

        # Fallback: PDBQT mínimo CA-only
        self.logger.warning(f"Peptide PDBQT fallback (CA-only): {sequence[:8]}")
        return self._write_ca_pdbqt(sequence, center, pdbqt_path)

    def _build_allatom_pdb(self, sequence: str, center: list, pdb_path: Path) -> bool:
        """Gera PDB all-atom via PeptideBuilder (Ala como fallback por resíduo)."""
        try:
            import PeptideBuilder
            from PeptideBuilder import Geometry
            import Bio.PDB
            import numpy as np

            first_aa = sequence[0] if sequence[0] != "B" else "A"
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

            # Centralizar o centro de massa do peptídeo no sítio catalítico.
            # Bug anterior: somava offset ao N-terminus (primeiro átomo) em vez
            # do COM → peptídeos longos começavam no sítio e se estendiam para fora
            # do grid box, impedindo qualquer pose válida.
            target = np.array([float(v) for v in center])
            coords = np.array([a.coord for a in structure.get_atoms()])
            com = coords.mean(axis=0)
            offset = target - com
            for atom in structure.get_atoms():
                atom.coord += offset

            io = Bio.PDB.PDBIO()
            io.set_structure(structure)
            io.save(str(pdb_path))
            return True
        except Exception as e:
            self.logger.warning(f"PeptideBuilder falhou ({sequence[:6]}): {e}")
            return False

    def _adaptive_grid_size(self, length: int, base: list) -> list:
        """Retorna grid box adaptado ao comprimento do peptídeo.

        PeptideBuilder gera geometria próxima à beta-strand estendida
        (~3.6 Å/resíduo).  Com centralização pelo COM, o peptídeo ocupa
        ±(length/2 × 3.6 Å) em cada direção → o grid precisa de pelo
        menos length × 3.6 Å no eixo principal.

        Tabela orientativa (com COM centrado no sítio):
          5 aa → ~18 Å → 25 Å cobre
          7 aa → ~25 Å → 30 Å cobre
         10 aa → ~36 Å → 40 Å cobre
         12 aa → ~43 Å → 50 Å cobre
         15 aa → ~54 Å → 60 Å cobre
         20 aa → ~72 Å → 80 Å cobre
        """
        # Estimativa conservadora: comprimento extendido ÷ 2 + margem de 4 Å
        needed = int(length * 3.6) + 8
        s = max(base[0], needed)
        return [s, s, s]

    def _ensure_ligand_pdbqt_format(self, pdbqt_path: Path):
        """Força formato ligante rígido: apenas ATOM/HETATM dentro de ROOT/ENDROOT/TORSDOF 0.

        Remove BRANCH/ENDBRANCH gerados pelo obabel em modo flexível e garante
        que não sobrem linhas ROOT duplicadas do obabel modo receptor.
        """
        content = pdbqt_path.read_text()
        atom_lines = [l for l in content.splitlines() if l.startswith(("ATOM", "HETATM"))]
        if not atom_lines:
            return
        with open(pdbqt_path, "w") as f:
            f.write("ROOT\n")
            for line in atom_lines:
                f.write(line.rstrip() + "\n")
            f.write("ENDROOT\n")
            f.write("TORSDOF 0\n")

    def _write_ca_pdbqt(self, sequence: str, center: list, pdbqt_path: Path) -> Path:
        """PDBQT CA-only como último recurso."""
        cx, cy, cz = center
        ad4 = {"R":"N","K":"N","H":"N","D":"OA","E":"OA","S":"OA","T":"OA",
               "Y":"OA","N":"NA","Q":"NA","W":"A","F":"A","P":"A"}
        with open(pdbqt_path, "w") as f:
            f.write("ROOT\n")
            for i, aa in enumerate(sequence):
                resname = AA_1TO3.get(aa, "ALA")
                atype = ad4.get(aa, "C")
                f.write(f"ATOM  {i+1:5d}  CA  {resname} B{i+1:4d}    "
                        f"{cx+i*3.8:8.3f}{cy:8.3f}{cz:8.3f}  1.00  0.00"
                        f"    0.000 {atype}\n")
            f.write("ENDROOT\nTORSDOF 0\n")
        return pdbqt_path

    def _run_vina(self, receptor_pdbqt: Path, ligand_pdbqt: Path,
                  center: list, size: list, exhaustiveness: int,
                  out_dir: Path) -> dict:
        out_pdbqt = out_dir / "docked.pdbqt"
        log_file = out_dir / "vina.log"

        # Nota: versão f458505-mod não suporta --log; stdout/stderr capturados diretamente
        cmd = [
            "vina",
            "--receptor", str(receptor_pdbqt),
            "--ligand", str(ligand_pdbqt),
            "--out", str(out_pdbqt),
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

        # Salvar log manualmente (--log não disponível nesta build do Vina)
        log_text = proc.stdout + proc.stderr
        log_file.write_text(log_text)

        # Parsear affinidades do stdout/stderr
        affinities = []
        for line in log_text.splitlines():
            m = re.search(r"^\s+\d+\s+([-\d.]+)\s+", line)
            if m:
                affinities.append(float(m.group(1)))

        if proc.returncode != 0 or not affinities:
            err = (proc.stderr or proc.stdout or "").strip()[:400]
            # WARNING nos primeiros 3 erros para diagnóstico; depois DEBUG
            level = self.logger.warning if getattr(self, "_vina_warn_count", 0) < 3 else self.logger.debug
            self._vina_warn_count = getattr(self, "_vina_warn_count", 0) + 1
            level(f"Vina rc={proc.returncode} lig={ligand_pdbqt.name}: {err}")

        return {
            "best_affinity_kcal": affinities[0] if affinities else None,
            "all_affinities": affinities,
            "docked_pdbqt": str(out_pdbqt) if out_pdbqt.exists() else None,
            "vina_returncode": proc.returncode,
        }

    def _top_candidates(self, sequences_data: dict) -> list[dict]:
        forced = self.config.get("docking", {}).get("forced_sequences")
        if forced:
            self.logger.info(f"Usando sequências forçadas para docking ({len(forced)}).")
            return [{"sequence": s, "length": len(s), "_heuristic": None} for s in forced]

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

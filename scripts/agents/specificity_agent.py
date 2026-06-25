"""
SpecificityAgent — Avalia seletividade dos candidatos contra proteases não-alvo.

Compara afinidade Vina dos top candidatos entre:
  - Alvo    : tripsina de Lepidoptera (receptor primário do pipeline)
  - Não-alvo: tripsina humana (PDB 1TRN), tripsina de Apis mellifera (AlphaFold)

Índice de Seletividade (SI):
    SI = aff_não_alvo − aff_alvo   (kcal/mol; positivo = candidato liga pior ao não-alvo = seletivo)

Critério de aprovação: SI ≥ threshold (default 2,0 kcal/mol) para TODOS os não-alvos.
"""
import json
import re
import subprocess
import urllib.request
from pathlib import Path
from typing import Optional

from .base_agent import BaseAgent
from ..utils import check_vina


# ── Proteases não-alvo com dados de referência ──────────────────────────────
NONTARGETS = {
    "human_trypsin": {
        "pdb_id":    "1TRN",
        "source":    "rcsb",
        "chain":     "A",
        "s1_residue": "ASP",
        # Coordenadas aproximadas do centro S1 em 1TRN (Asp189, numeração padrão)
        "s1_fallback_xyz": [7.5, 16.2, 24.8],
        "description": "Tripsina bovina / humana (Asp189 S1-pocket) — segurança humana",
    },
    "apis_mellifera_trypsin": {
        "uniprot_id": "Q9GYL5",
        "source":     "alphafold",
        "chain":      "A",
        "s1_residue": "ASP",
        "s1_fallback_xyz": [0.0, 0.0, 0.0],  # será calculado do PDB
        "description": "Tripsina de Apis mellifera (AlphaFold) — proteção de polinizadores",
    },
}


class SpecificityAgent(BaseAgent):

    def run(self, docking_results: dict, target_docking_results: dict) -> dict:
        """
        docking_results        : dict do DockingAgent (alvos Lepidoptera)
        target_docking_results : mesmo dict (referência de afinidade alvo)
        Retorna dict com seletividade por candidato e não-alvo.
        """
        if not check_vina():
            self.logger.warning("Vina não encontrado — especificidade calculada por heurística")
            return self._heuristic_specificity(docking_results)

        cfg    = self.config.get("specificity", {})
        thresh = cfg.get("selectivity_threshold", 2.0)
        top_n  = cfg.get("top_n_candidates", 20)

        # Top candidatos por Vina (únicos)
        top_cands = self._select_top_candidates(docking_results, top_n)
        self.logger.info(f"Especificidade: {len(top_cands)} candidatos × {len(NONTARGETS)} não-alvos")

        results: dict = {}

        for nt_key, nt_info in NONTARGETS.items():
            pdb_path = self._get_nontarget_pdb(nt_key, nt_info)
            if pdb_path is None:
                self.logger.warning(f"Não foi possível obter PDB para {nt_key} — pulando")
                continue

            rec_pdbqt = self._prepare_receptor(nt_key, pdb_path, nt_info)
            if rec_pdbqt is None:
                continue

            center = self._find_s1_center(pdb_path, nt_info)
            self.logger.info(f"[{nt_key}] S1 center: {center}")

            nontarget_affs: dict = {}
            for cand in top_cands:
                seq   = cand["sequence"]
                affnt = self._dock_peptide(seq, rec_pdbqt, center, nt_key)
                nontarget_affs[seq] = affnt

            results[nt_key] = {
                "description": nt_info["description"],
                "affinities":  nontarget_affs,
            }

        # Calcular SI e veredicto por candidato
        selectivity: dict = {}
        for cand in top_cands:
            seq      = cand["sequence"]
            aff_tgt  = cand["vina_kcal"]
            sis      = {}
            approved = True
            for nt_key, nt_data in results.items():
                aff_nt = nt_data["affinities"].get(seq)
                if aff_nt is None:
                    continue
                si = aff_nt - aff_tgt  # positivo = liga pior ao não-alvo = BOM
                sis[nt_key] = round(si, 3)
                if si < thresh:
                    approved = False
            selectivity[seq] = {
                "vina_target_kcal": aff_tgt,
                "selectivity_index": sis,
                "min_SI": round(min(sis.values()), 3) if sis else None,
                "approved": approved,
            }

        n_approved = sum(1 for v in selectivity.values() if v["approved"])
        self.logger.info(
            f"Especificidade concluída: {n_approved}/{len(selectivity)} candidatos aprovados "
            f"(SI ≥ {thresh} kcal/mol)"
        )

        output = {
            "nontarget_affinities": results,
            "selectivity":          selectivity,
            "threshold_kcal":       thresh,
            "n_approved":           n_approved,
        }
        (self.workdir / "specificity_results.json").write_text(
            json.dumps(output, indent=2, default=str)
        )
        return output

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _select_top_candidates(self, docking_results: dict, n: int) -> list:
        seen: set = set()
        cands = []
        for v in sorted(docking_results.values(),
                        key=lambda x: x.get("best_affinity_kcal", 0)):
            seq = v.get("sequence", "")
            aff = v.get("best_affinity_kcal")
            if seq and aff is not None and seq not in seen:
                seen.add(seq)
                cands.append({"sequence": seq, "vina_kcal": aff})
            if len(cands) >= n:
                break
        return cands

    def _get_nontarget_pdb(self, key: str, info: dict) -> Optional[Path]:
        out_path = self.workdir / f"{key}.pdb"
        if out_path.exists() and out_path.stat().st_size > 2000:
            return out_path

        try:
            if info["source"] == "rcsb":
                pdb_id = info["pdb_id"]
                url    = f"https://files.rcsb.org/download/{pdb_id}.pdb"
                self.logger.info(f"Baixando {pdb_id} de RCSB...")
                urllib.request.urlretrieve(url, out_path)
                return out_path

            elif info["source"] == "alphafold":
                uid = info["uniprot_id"]
                url = f"https://alphafold.ebi.ac.uk/files/AF-{uid}-F1-model_v4.pdb"
                self.logger.info(f"Baixando AF-{uid} de AlphaFold EBI...")
                urllib.request.urlretrieve(url, out_path)
                return out_path

        except Exception as e:
            self.logger.warning(f"Falha ao baixar {key}: {e}")
            return None

    def _prepare_receptor(self, key: str, pdb_path: Path, info: dict) -> Optional[Path]:
        pdbqt = self.workdir / f"{key}_receptor.pdbqt"
        if pdbqt.exists() and pdbqt.stat().st_size > 3000:
            return pdbqt

        # Limpar PDB: manter apenas ATOM da chain A, remover HETATM
        cleaned = self.workdir / f"{key}_clean.pdb"
        chain   = info.get("chain", "A")
        lines   = []
        for line in pdb_path.read_text().splitlines():
            rec = line[:6].strip()
            if rec == "ATOM":
                ch = line[21] if len(line) > 21 else " "
                if ch in (chain, " "):
                    lines.append(line)
            elif rec == "TER":
                lines.append(line)
        cleaned.write_text("\n".join(lines) + "\n")

        ob = subprocess.run(["which", "obabel"], capture_output=True)
        if ob.returncode == 0:
            r = subprocess.run(
                ["obabel", str(cleaned), "-O", str(pdbqt), "-h", "--partialcharge", "gasteiger"],
                capture_output=True, text=True
            )
            if pdbqt.exists() and pdbqt.stat().st_size > 2000:
                return pdbqt

        # Fallback mínimo — escrever PDBQT manualmente
        self.logger.warning(f"obabel falhou para {key}; usando conversão mínima")
        pdbqt_lines = []
        for line in lines:
            if line.startswith("ATOM"):
                pdbqt_lines.append(line[:66] + "  0.000  0.000          C \n")
        pdbqt.write_text("".join(pdbqt_lines))
        return pdbqt if pdbqt.exists() else None

    def _find_s1_center(self, pdb_path: Path, info: dict) -> list:
        """Localiza o Asp do bolso S1 no PDB do não-alvo e retorna XYZ."""
        target_res = info.get("s1_residue", "ASP")
        chain      = info.get("chain", "A")
        asp_coords = []

        for line in pdb_path.read_text().splitlines():
            if not line.startswith("ATOM"):
                continue
            resn = line[17:20].strip()
            ch   = line[21] if len(line) > 21 else " "
            atom = line[12:16].strip()
            if resn == target_res and ch in (chain, " ") and atom == "CA":
                try:
                    x, y, z = float(line[30:38]), float(line[38:46]), float(line[46:54])
                    asp_coords.append([x, y, z])
                except ValueError:
                    pass

        if not asp_coords:
            self.logger.warning(f"Asp não encontrado em {pdb_path.name}; usando fallback XYZ")
            return info.get("s1_fallback_xyz", [0.0, 0.0, 0.0])

        # Usar o Asp mais próximo do centro estrutural (heurística para S1)
        cx = sum(c[0] for c in asp_coords) / len(asp_coords)
        cy = sum(c[1] for c in asp_coords) / len(asp_coords)
        cz = sum(c[2] for c in asp_coords) / len(asp_coords)
        best = min(asp_coords,
                   key=lambda c: (c[0]-cx)**2 + (c[1]-cy)**2 + (c[2]-cz)**2)
        return [round(best[0], 3), round(best[1], 3), round(best[2], 3)]

    def _dock_peptide(self, seq: str, rec_pdbqt: Path, center: list, nt_key: str) -> Optional[float]:
        """Constrói peptídeo, prepara PDBQT e roda Vina contra não-alvo."""
        from ..utils import AA_1TO3
        stem   = f"{nt_key}_{seq[:8]}"
        out_dir = self.workdir / stem
        out_dir.mkdir(exist_ok=True)

        # Construir PDB linear do peptídeo
        pdb_path = out_dir / "peptide.pdb"
        self._build_linear_pdb(seq, pdb_path, AA_1TO3)

        # Converter para PDBQT
        lig_pdbqt = out_dir / "ligand.pdbqt"
        ob = subprocess.run(["which", "obabel"], capture_output=True)
        if ob.returncode == 0:
            subprocess.run(
                ["obabel", str(pdb_path), "-O", str(lig_pdbqt), "-h",
                 "--partialcharge", "gasteiger", "--gen3d"],
                capture_output=True
            )
        if not lig_pdbqt.exists() or lig_pdbqt.stat().st_size < 100:
            lig_pdbqt = self._minimal_pdbqt(seq, pdb_path, lig_pdbqt, AA_1TO3)
        if lig_pdbqt is None:
            return None

        # Vina
        out_pdbqt  = out_dir / "docked.pdbqt"
        size       = [60.0, 60.0, 60.0]  # grid generoso para não-alvos
        vina_cmd   = [
            "vina",
            "--receptor",    str(rec_pdbqt),
            "--ligand",      str(lig_pdbqt),
            "--out",         str(out_pdbqt),
            "--center_x",    str(center[0]),
            "--center_y",    str(center[1]),
            "--center_z",    str(center[2]),
            "--size_x",      str(size[0]),
            "--size_y",      str(size[1]),
            "--size_z",      str(size[2]),
            "--exhaustiveness", "4",
            "--num_modes",   "5",
        ]
        r = subprocess.run(vina_cmd, capture_output=True, text=True, timeout=300)
        aff = self._parse_vina_affinity(r.stdout + r.stderr)
        return aff

    def _parse_vina_affinity(self, output: str) -> Optional[float]:
        for line in output.splitlines():
            m = re.search(r"^\s*1\s+([-\d.]+)", line)
            if m:
                return float(m.group(1))
        return None

    def _build_linear_pdb(self, seq: str, out_path: Path, aa_map: dict):
        lines = ["REMARK LINEAR PEPTIDE"]
        atom_num = 1
        for i, aa in enumerate(seq):
            resn = aa_map.get(aa, "GLY")
            x    = float(i * 3.8)
            lines.append(
                f"ATOM  {atom_num:5d}  CA  {resn} A{i+1:4d}    "
                f"{x:8.3f}{0.0:8.3f}{0.0:8.3f}  1.00  0.00          C  "
            )
            atom_num += 1
        lines.append("END")
        out_path.write_text("\n".join(lines))

    def _minimal_pdbqt(self, seq: str, pdb_path: Path,
                       pdbqt_path: Path, aa_map: dict) -> Optional[Path]:
        lines = []
        for line in pdb_path.read_text().splitlines():
            if line.startswith("ATOM"):
                lines.append(line[:66] + "  0.000  0.000          C \n")
        pdbqt_path.write_text("".join(lines))
        return pdbqt_path if pdbqt_path.exists() else None

    def _heuristic_specificity(self, docking_results: dict) -> dict:
        """Fallback quando Vina não está disponível."""
        selectivity = {}
        for v in docking_results.values():
            seq = v.get("sequence", "")
            if not seq or seq in selectivity:
                continue
            n_basic = sum(1 for aa in seq if aa in "RK")
            # Heurística: muitos K/R = menos seletivo (liga bem a qualquer tripsina)
            si_est = max(0.0, round(1.0 - n_basic * 0.15, 2))
            selectivity[seq] = {
                "vina_target_kcal": v.get("best_affinity_kcal"),
                "selectivity_index": {"human_trypsin": si_est, "apis_mellifera": si_est},
                "min_SI": si_est,
                "approved": si_est >= 1.0,
                "note": "heurístico (Vina indisponível)",
            }
        return {"selectivity": selectivity, "mode": "heuristic"}

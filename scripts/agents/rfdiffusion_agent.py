"""RFdiffusionAgent — Gera backbones peptídicos via RFdiffusion.

Gera N backbones para cada comprimento peptídico definido em
config.rfdiffusion.contig_lengths, usando os hotspots do StructureAgent.
Se RFdiffusion não estiver instalado, gera backbones lineares simples
com PeptideBuilder como fallback para continuar o pipeline.
"""
import json
import subprocess
from pathlib import Path

from .base_agent import BaseAgent
from ..utils import find_rfdiffusion


class RFdiffusionAgent(BaseAgent):

    def run(self, target_pdb: str, binding_site: dict) -> dict:
        rfd_path = find_rfdiffusion(self.config)
        center = binding_site["consensus_center_xyz"]
        hotspots = binding_site["hotspot_residues"]

        cfg = self.config.get("rfdiffusion", {})
        lengths = cfg.get("contig_lengths", [5, 10, 15, 20])
        num_designs = cfg.get("num_designs", 50)

        results = {}

        if rfd_path:
            self.logger.info(f"RFdiffusion encontrado: {rfd_path}")
            results = self._run_rfdiffusion(rfd_path, target_pdb,
                                            hotspots, lengths, num_designs)
        else:
            self._warn_missing_tool(
                "RFdiffusion",
                "Instalar: git clone https://github.com/RosettaCommons/RFdiffusion"
            )
            self.logger.info("Usando fallback: gerando backbones lineares com PeptideBuilder...")
            results = self._fallback_backbones(lengths, center, num_designs)

        # Salvar manifesto
        manifesto = {
            "total_backbones": sum(len(v) for v in results.values()),
            "lengths": {str(k): [str(p) for p in v] for k, v in results.items()},
            "hotspots_used": hotspots,
        }
        (self.workdir / "backbones_manifesto.json").write_text(
            json.dumps(manifesto, indent=2)
        )
        self.logger.info(
            f"Backbones gerados: {manifesto['total_backbones']} "
            f"(comprimentos: {list(results.keys())})"
        )
        return results

    def _run_rfdiffusion(self, rfd_path: Path, target_pdb: str,
                         hotspots: list, lengths: list, num_designs: int) -> dict:
        cfg = self.config.get("rfdiffusion", {})
        results = {}

        # Formatar hotspots para RFdiffusion: "A5,A10,A20"
        hotspot_str = ",".join(f"A{h}" for h in hotspots[:8])

        # Localizar run_inference.py (v1: scripts/; legacy: raiz)
        inference_script = rfd_path / "scripts" / "run_inference.py"
        if not inference_script.exists():
            inference_script = rfd_path / "run_inference.py"
        self.logger.info(f"Script de inferência: {inference_script}")

        # Modelo: Complex_base_ckpt.pt (binder design) na raiz do repo clonado.
        # Necessário porque o pacote instalado via pip aponta para site-packages/models/
        # e não encontra o checkpoint. ckpt_override_path contorna isso.
        ckpt = rfd_path / "models" / "Complex_base_ckpt.pt"
        if not ckpt.exists():
            # fallback: Base_ckpt.pt (sem PPI conditioning)
            ckpt = rfd_path / "models" / "Base_ckpt.pt"
        self.logger.info(f"Checkpoint: {ckpt}")

        # target_pdb pode ser relativo; converter para absoluto para o subprocess
        target_pdb_abs = str(Path(target_pdb).resolve())

        n_res = self._count_receptor_residues(target_pdb)

        for length in lengths:
            out_dir = self.workdir / f"len_{length}"
            out_dir.mkdir(exist_ok=True)

            contig = f"A1-{n_res}/0 {length}-{length}"

            cmd = [
                "python", str(inference_script),
                f"inference.input_pdb={target_pdb_abs}",
                f"inference.ckpt_override_path={ckpt}",
                f"contigmap.contigs=[{contig}]",
                f"ppi.hotspot_res=[{hotspot_str}]",
                f"inference.num_designs={num_designs}",
                f"denoiser.noise_scale_ca={cfg.get('noise_scale_ca', 0.2)}",
                f"denoiser.noise_scale_frame={cfg.get('noise_scale_frame', 0.1)}",
                f"inference.output_prefix={out_dir.resolve()}/design",
            ]

            self.logger.info(f"RFdiffusion — comprimento {length} aa | contig={contig}")
            # cwd=rfd_path: Hydra encontra config/inference/ no repo clonado
            proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(rfd_path))
            if proc.returncode != 0:
                self.logger.error(f"RFdiffusion falhou (len={length}): {proc.stderr[-800:]}")
            else:
                results[length] = list(out_dir.glob("*.pdb"))

        return results

    def _fallback_backbones(self, lengths: list, center: list, num_designs: int) -> dict:
        """Gera backbones lineares simples com PeptideBuilder."""
        try:
            import PeptideBuilder
            import Bio.PDB
        except ImportError:
            self.logger.warning("PeptideBuilder não disponível. Gerando PDBs stub.")
            return self._stub_backbones(lengths, num_designs)

        results = {}
        for length in lengths:
            out_dir = self.workdir / f"len_{length}"
            out_dir.mkdir(exist_ok=True)
            pdbs = []
            for i in range(min(num_designs, 5)):  # fallback: 5 por comprimento
                pdb_path = out_dir / f"backbone_{i:03d}.pdb"
                self._build_linear_peptide(length, center, pdb_path)
                pdbs.append(pdb_path)
            results[length] = pdbs
        return results

    def _build_linear_peptide(self, length: int, center: list, out_path: Path):
        """Cria backbone linear de poly-Ala posicionado no sítio."""
        import PeptideBuilder
        from PeptideBuilder import Geometry
        import Bio.PDB

        geo = Geometry.geometry("A")  # Ala
        structure = PeptideBuilder.initialize_res(geo)
        for _ in range(length - 1):
            PeptideBuilder.add_residue(structure, geo)

        # Mover para o centro do sítio
        center_arr = __import__("numpy").array(center)
        for atom in structure.get_atoms():
            atom.transform(
                __import__("numpy").eye(3),
                center_arr - __import__("numpy").array([0, 0, 0])
            )

        io = Bio.PDB.PDBIO()
        io.set_structure(structure)
        io.save(str(out_path))

    def _stub_backbones(self, lengths: list, num_designs: int) -> dict:
        """Cria PDBs stub vazios para não bloquear o pipeline."""
        results = {}
        for length in lengths:
            out_dir = self.workdir / f"len_{length}"
            out_dir.mkdir(exist_ok=True)
            pdbs = []
            for i in range(min(num_designs, 3)):
                pdb_path = out_dir / f"backbone_{i:03d}.pdb"
                # PDB mínimo: poly-Ala linear
                with open(pdb_path, "w") as f:
                    for j in range(length):
                        f.write(
                            f"ATOM  {j+1:5d}  CA  ALA A{j+1:4d}    "
                            f"  0.000   {j*3.8:6.3f}   0.000  1.00  0.00           C\n"
                        )
                    f.write("END\n")
                pdbs.append(pdb_path)
            results[length] = pdbs
        return results

    def _count_receptor_residues(self, pdb_path: str) -> int:
        """Retorna o último número de resíduo (para o contig A1-N).

        Após prep_pdbs.py, PDBs têm chain A e resíduos 1-N sem offset.
        max(seqs) == N é correto; len(seqs) seria menor se houver gaps.
        """
        seqs = set()
        chain_ok = True
        with open(pdb_path) as f:
            for line in f:
                if line.startswith("ATOM"):
                    chain = line[21]
                    if chain not in (" ", "A"):
                        chain_ok = False
                    try:
                        seqs.add(int(line[22:26]))
                    except ValueError:
                        pass
        if not seqs:
            return 240
        if not chain_ok:
            self.logger.warning(
                f"PDB {pdb_path} tem chain ID inesperado — rode scripts/prep_pdbs.py primeiro"
            )
        return max(seqs)

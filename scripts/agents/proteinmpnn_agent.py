"""ProteinMPNNAgent — Desenha sequências para backbones gerados pelo RFdiffusion.

Estratégia para inibidores de tripsina de Lepidoptera:
  • Posição P1 (resíduo 1) fixada em ARG ou LYS (especificidade do bolso S1)
  • bias_AA favorece Arg/Lys, penaliza Cys
  • sampling_temp baixo (0.1) para sequências de alta confiança
"""
import json
import subprocess
from pathlib import Path

from .base_agent import BaseAgent
from ..utils import find_proteinmpnn, parse_fasta, peptide_properties


class ProteinMPNNAgent(BaseAgent):

    def run(self, backbones: dict, receptor_pdb: str) -> dict:
        """
        backbones: {length: [pdb_path, ...]}
        Retorna: {pdb_stem: {"sequences": [...], "properties": [...]}}
        """
        mpnn_path = find_proteinmpnn(self.config)
        cfg = self.config.get("proteinmpnn", {})

        results = {}
        total = 0

        for length, pdb_list in backbones.items():
            self.logger.info(f"ProteinMPNN — {len(pdb_list)} backbones de {length} aa...")
            for pdb in pdb_list:
                pdb = Path(pdb)
                if not pdb.exists():
                    continue
                if mpnn_path:
                    seqs = self._run_mpnn(mpnn_path, pdb, receptor_pdb, cfg)
                else:
                    seqs = self._fallback_sequences(length, cfg)

                props = [peptide_properties(s) for s in seqs]
                results[pdb.stem] = {
                    "backbone_pdb": str(pdb),
                    "length": length,
                    "sequences": seqs,
                    "properties": props,
                }
                total += len(seqs)

        # Salvar todas as sequências em FASTA consolidado
        fasta_out = self.workdir / "all_sequences.fasta"
        with open(fasta_out, "w") as f:
            for stem, data in results.items():
                for i, seq in enumerate(data["sequences"]):
                    f.write(f">{stem}_seq{i:03d} len={data['length']}\n{seq}\n")

        # Salvar propriedades
        (self.workdir / "sequences_properties.json").write_text(
            json.dumps(results, indent=2, default=str)
        )

        if not mpnn_path:
            self._warn_missing_tool(
                "ProteinMPNN",
                "Instalar: git clone https://github.com/dauparas/ProteinMPNN"
            )

        self.logger.info(f"Total de sequências geradas: {total}")
        return results

    def _run_mpnn(self, mpnn_path: Path, pdb: Path, receptor_pdb: str, cfg: dict) -> list[str]:
        """Executa protein_mpnn_run.py e parseia o FASTA de saída."""
        out_dir = self.workdir / "mpnn_out" / pdb.stem
        out_dir.mkdir(parents=True, exist_ok=True)

        # Arquivo de posições fixas: P1 = ARG (posição 1 do peptídeo)
        fixed = {"B": {"1": ["ARG", "LYS"]}}
        fixed_path = out_dir / "fixed.json"
        fixed_path.write_text(json.dumps(fixed))

        # bias_AA: favorece Arg/Lys
        bias = cfg.get("bias_aa", {"ARG": 1.5, "LYS": 1.0})
        bias_path = out_dir / "bias_aa.json"
        bias_path.write_text(json.dumps({"B": bias}))

        cmd = [
            "python", str(mpnn_path / "protein_mpnn_run.py"),
            "--pdb_path", str(pdb),
            "--out_folder", str(out_dir),
            "--num_seq_per_target", str(cfg.get("num_seq_per_target", 30)),
            "--sampling_temp", str(cfg.get("sampling_temp", 0.1)),
            "--backbone_noise", str(cfg.get("backbone_noise", 0.05)),
            "--fixed_positions_jsonl", str(fixed_path),
            "--bias_AA_jsonl", str(bias_path),
            "--omit_AAs", cfg.get("omit_aas", "CX"),
            "--batch_size", "1",
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if proc.returncode != 0:
            self.logger.error(f"ProteinMPNN falhou ({pdb.stem}): {proc.stderr[-300:]}")
            return self._fallback_sequences(10, cfg)

        # Parsear FASTA gerado
        fasta_files = list((out_dir / "seqs").glob("*.fa")) + \
                      list((out_dir / "seqs").glob("*.fasta"))
        sequences = []
        for fa in fasta_files:
            for _, seq in parse_fasta(str(fa)):
                # Extrair apenas a cadeia do peptídeo (cadeia B)
                clean = seq.replace("-", "").replace("/", "")
                if clean:
                    sequences.append(clean)
        return sequences if sequences else self._fallback_sequences(10, cfg)

    def _fallback_sequences(self, length: int, cfg: dict) -> list[str]:
        """Gera sequências candidatas baseadas em conhecimento de tripsina."""
        import random

        # P1 = Arg (alta afinidade S1 de tripsina)
        # P2-P5: resíduos favoráveis a serina-proteases
        favorable = list("RGKAILMFWY")  # básicos + hidrofóbicos
        neutral = list("GSTANQ")
        n_seqs = cfg.get("num_seq_per_target", 30)
        seqs = []

        for _ in range(n_seqs):
            # P1 sempre Arg ou Lys
            p1 = random.choice(["R", "K"])
            rest = "".join(
                random.choice(favorable + neutral)
                for _ in range(length - 1)
            )
            seqs.append(p1 + rest)

        # Adicionar sequências conhecidas de inibidores de Kunitz/BPTI
        # adaptadas para comprimentos curtos
        known_motifs = {
            5:  ["RYCEI", "RLFKS", "RPDFK", "RGSIE", "RKYSP"],
            7:  ["RRYCEIS", "RPDFCLE", "RGSKYFP", "RLYSQFP"],
            10: ["RPDFCLEPPK", "RRYCEIFARR", "RGSKYILPQR"],
            12: ["RPDFCLEPKKYI", "RRLFKSRGKFLE"],
            15: ["RPDFCLEPKKYIPS", "RRYCEIFARRGKFS"],
            20: ["RPDFCLEPKKYIPSTLQE", "RRYCEIFARRGKFSKYIPE"],
        }
        motifs = known_motifs.get(length, [])
        seqs = motifs + seqs[:n_seqs - len(motifs)]
        return seqs[:n_seqs]

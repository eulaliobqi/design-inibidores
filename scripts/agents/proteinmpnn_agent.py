"""ProteinMPNNAgent — Gera dataset diverso de sequências para ML/DL.

10 estratégias de geração (fallback sem ProteinMPNN instalado):
  1. random_uniform      — todos os 19 aa equiprováveis
  2. hydrophobic         — bias AILMFWV (mecanismo alostérico)
  3. charged_positive    — bias RK (inibição competitiva clássica)
  4. charged_negative    — bias DE (interações eletrostáticas alternativas)
  5. aromatic_cterminal  — corpo aleatório + C-terminal Y/W/F (subsítios primed)
  6. aromatic_nterminal  — N-terminal Y/W/F (β-hairpin mimético)
  7. amphipathic         — alternando hidrofóbico/polar (α-hélice anfipática)
  8. proline_rich        — Pro enriquecido (scaffold rígido PPII)
  9. motif_seeded        — seeds de inibidores conhecidos + mutações pontuais
  10. glycine_scan       — Gly em cada posição (mapeamento de flexibilidade)
"""
import csv
import json
import random
import subprocess
from pathlib import Path

from .base_agent import BaseAgent
from ..utils import find_proteinmpnn, parse_fasta, peptide_properties


# Inibidores canônicos de serino-proteases usados como seeds
_KNOWN_SEEDS = {
    3:  ["VLK", "VLR", "WFY", "RPD", "LLK", "IAR", "FWY", "RYL"],
    4:  ["RPDF", "WFIY", "LALA", "LLAI", "TGPK", "RRYC", "YWFY"],
    5:  ["RYCEI", "RPDFK", "LLAIY", "WFIYY", "VLIMY", "LALAK", "TGPCK", "RQFWL"],
    6:  ["RPDFCL", "WFIYGL", "LLAIGY", "RRYCEI", "KPTIYR", "VLIWYN"],
    7:  ["RRYCEIS", "RPDFKLY", "LLAIGYY", "WFIYGLY", "YQFTRKY", "KPTIYRY"],
    8:  ["RRYCEIFL", "RPDFKLYI", "WFIYGLMA", "LLAIGTVM", "KPTIYRFY"],
    9:  ["RRYCEIFAR", "RPDFCLEPP", "WFIYGLMAI", "LLAIGTVRM", "YQFTRKYWI"],
    10: ["RPDFCLEPPK", "RRYCEIFARR", "WFIYGLMAIY", "LLAIGTVRMY", "KPTIYRFYLY"],
    12: ["RPDFCLEPKKYI", "WFIYGLMAIVTY", "LLAIGTVRMSWY", "RRYCEIFARRNL"],
    15: ["RPDFCLEPKKYIPS", "WFIYGLMAIVTGKLY", "LLAIGTVRMSKAEWY"],
    20: ["RPDFCLEPKKYIPSTLQEA", "WFIYGLMAIVTGKLSEPQY", "LLAIGTVRMSKAEPQDFNVY"],
}

_ALL_AA = list("ADEFGHIKLMNPQRSTVWY")  # sem Cys
_HYDROPHOBIC = list("AILMFWV")
_POLAR = list("NQSTH")
_CHARGED_POS = list("RK")
_CHARGED_NEG = list("DE")
_AROMATIC = list("YWF")


class ProteinMPNNAgent(BaseAgent):

    def run(self, backbones: dict, receptor_pdb: str) -> dict:
        mpnn_path = find_proteinmpnn(self.config)
        cfg = self.config.get("proteinmpnn", {})
        ml_cfg = self.config.get("ml_dataset", {})

        results = {}
        all_unique: list[dict] = []
        seen_seqs: set[str] = set()

        for length, pdb_list in backbones.items():
            self.logger.info(f"ProteinMPNN — {len(pdb_list)} backbones de {length} aa...")
            for pdb in pdb_list:
                pdb = Path(pdb)
                if not pdb.exists():
                    continue
                if mpnn_path:
                    seqs = self._run_mpnn(mpnn_path, pdb, receptor_pdb, cfg)
                else:
                    seqs = self._generate_ml_dataset(int(length), cfg)

                props = [peptide_properties(s) for s in seqs]
                # Chave qualificada pelo comprimento para evitar colisão entre
                # backbones de comprimentos diferentes com mesmo stem de arquivo
                key = f"len{int(length)}_{pdb.stem}"
                results[key] = {
                    "backbone_pdb": str(pdb),
                    "length": int(length),
                    "sequences": seqs,
                    "properties": props,
                }
                seeds_for_len = set(_KNOWN_SEEDS.get(int(length), []))
                for s, p in zip(seqs, props):
                    if s not in seen_seqs:
                        seen_seqs.add(s)
                        entry = {"backbone": key, **p}
                        entry["is_known_inhibitor"] = 1 if s in seeds_for_len else 0
                        all_unique.append(entry)

        total = len(all_unique)
        self.logger.info(f"Sequências únicas geradas: {total}")

        # FASTA consolidado
        fasta_out = self.workdir / "all_sequences.fasta"
        with open(fasta_out, "w") as f:
            for stem, data in results.items():
                for i, seq in enumerate(data["sequences"]):
                    f.write(f">{stem}_seq{i:04d} len={data['length']}\n{seq}\n")

        (self.workdir / "sequences_properties.json").write_text(
            json.dumps(results, indent=2, default=str)
        )

        if ml_cfg.get("export_csv", True):
            self._export_ml_csv(all_unique, ml_cfg)

        if not mpnn_path:
            self._warn_missing_tool(
                "ProteinMPNN",
                "Instalar: git clone https://github.com/dauparas/ProteinMPNN"
            )

        return results

    # ──────────────────────────────────────────────
    # Geração principal: 10 estratégias
    # ──────────────────────────────────────────────

    def _generate_ml_dataset(self, length: int, cfg: dict) -> list[str]:
        n_total = cfg.get("num_seq_per_target", 500)
        seqs: set[str] = set()

        budget = {
            "random_uniform":     int(n_total * 0.20),
            "hydrophobic":        int(n_total * 0.10),
            "charged_positive":   int(n_total * 0.10),
            "charged_negative":   int(n_total * 0.07),
            "aromatic_cterminal": int(n_total * 0.12),
            "aromatic_nterminal": int(n_total * 0.08),
            "amphipathic":        int(n_total * 0.10),
            "proline_rich":       int(n_total * 0.07),
            "motif_seeded":       int(n_total * 0.09),
            "glycine_scan":       int(n_total * 0.07),
        }

        def ok(s):
            return len(s) == length and "C" not in s and "X" not in s

        def fill(pool_fn, n):
            attempts = 0
            while sum(1 for _ in range(1)) <= n and attempts < n * 10:
                s = pool_fn()
                if ok(s):
                    seqs.add(s)
                attempts += 1
                if len(seqs) >= n_total:
                    return

        # 1 — random uniform
        for _ in range(budget["random_uniform"] * 4):
            seqs.add("".join(random.choice(_ALL_AA) for _ in range(length)))
            if len(seqs) >= n_total:
                break

        # 2 — hydrophobic-biased (alostérico)
        pool_h = _HYDROPHOBIC * 3 + _ALL_AA
        for _ in range(budget["hydrophobic"] * 4):
            seqs.add("".join(random.choice(pool_h) for _ in range(length)))
            if len(seqs) >= n_total:
                break

        # 3 — charged positive (competitivo R/K)
        pool_pos = _CHARGED_POS * 4 + _ALL_AA
        for _ in range(budget["charged_positive"] * 4):
            seqs.add("".join(random.choice(pool_pos) for _ in range(length)))
            if len(seqs) >= n_total:
                break

        # 4 — charged negative (interações eletrostáticas)
        pool_neg = _CHARGED_NEG * 3 + _ALL_AA
        for _ in range(budget["charged_negative"] * 4):
            seqs.add("".join(random.choice(pool_neg) for _ in range(length)))
            if len(seqs) >= n_total:
                break

        # 5 — aromatic C-terminal (contatos subsítios primed)
        for _ in range(budget["aromatic_cterminal"] * 4):
            body = "".join(random.choice(_ALL_AA) for _ in range(length - 1))
            seqs.add(body + random.choice(_AROMATIC))
            if len(seqs) >= n_total:
                break

        # 6 — aromatic N-terminal (β-hairpin mimético)
        for _ in range(budget["aromatic_nterminal"] * 4):
            body = "".join(random.choice(_ALL_AA) for _ in range(length - 1))
            seqs.add(random.choice(_AROMATIC) + body)
            if len(seqs) >= n_total:
                break

        # 7 — amphipathic (α-hélice anfipática)
        if length >= 4:
            for _ in range(budget["amphipathic"] * 4):
                s = ""
                for pos in range(length):
                    if pos % 2 == 0:
                        s += random.choice(_HYDROPHOBIC)
                    else:
                        s += random.choice(_POLAR + _CHARGED_POS)
                seqs.add(s)
                if len(seqs) >= n_total:
                    break

        # 8 — proline-rich (PPII helix, scaffold rígido)
        pool_pro = ["P"] * 5 + _ALL_AA
        for _ in range(budget["proline_rich"] * 4):
            seqs.add("".join(random.choice(pool_pro) for _ in range(length)))
            if len(seqs) >= n_total:
                break

        # 9 — motif-seeded: seeds + mutações pontuais
        seeds = [s for s in _KNOWN_SEEDS.get(length, []) if ok(s)]
        for s in seeds:
            seqs.add(s)
        for _ in range(budget["motif_seeded"] * 4):
            if seeds:
                base = list(random.choice(seeds))
                n_mut = random.randint(1, max(1, length // 3))
                for _ in range(n_mut):
                    pos = random.randint(0, length - 1)
                    base[pos] = random.choice(_ALL_AA)
                s = "".join(base)
                if ok(s):
                    seqs.add(s)
            else:
                seqs.add("".join(random.choice(_ALL_AA) for _ in range(length)))
            if len(seqs) >= n_total:
                break

        # 10 — glycine scan: base aleatória + Gly em cada posição
        for _ in range(budget["glycine_scan"] * 2):
            base = "".join(random.choice(_ALL_AA) for _ in range(length))
            for pos in range(length):
                mut = list(base)
                mut[pos] = "G"
                s = "".join(mut)
                if ok(s):
                    seqs.add(s)
            if len(seqs) >= n_total:
                break

        # Completar com random se ainda faltam
        while len(seqs) < n_total:
            seqs.add("".join(random.choice(_ALL_AA) for _ in range(length)))

        result = list(seqs)[:n_total]
        # Garantir que seeds canônicos estejam incluídos
        for s in seeds:
            if s not in result:
                result = [s] + result[:n_total - 1]

        self.logger.info(
            f"  len={length}: {len(result)} seqs únicas via 10 estratégias "
            f"({len(seeds)} seeds canônicos incluídos)"
        )
        return result

    # ──────────────────────────────────────────────
    # Export ML/DL CSV
    # ──────────────────────────────────────────────

    def _export_ml_csv(self, sequences: list[dict], ml_cfg: dict):
        out_path = self.workdir.parent / "dataset" / "ml_training_dataset.csv"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if not sequences:
            return

        base_cols = [
            "sequence", "length", "backbone",
            "mw_da", "net_charge", "isoelectric_point",
            "hydrophobicity_kd", "boman_index", "instability_index", "aliphatic_index",
            "frac_aromatic", "frac_hydrophobic", "frac_charged",
            "n_arg_lys", "n_asp_glu", "n_aromatic",
            "has_aromatic_cterminal", "has_charged_nterminal", "has_pro",
        ]
        aa_cols = [f"frac_{aa}" for aa in "ADEFGHIKLMNPQRSTVWY"]
        label_cols = ["vina_affinity_kcal", "rosetta_I_sc", "is_known_inhibitor"]
        fieldnames = base_cols + aa_cols + label_cols

        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for item in sequences:
                row = {k: item.get(k, "") for k in fieldnames}
                row.setdefault("vina_affinity_kcal", "")
                row.setdefault("rosetta_I_sc", "")
                row.setdefault("is_known_inhibitor", item.get("is_known_inhibitor", 0))
                writer.writerow(row)

        self.logger.info(
            f"Dataset ML exportado → {out_path} "
            f"({len(sequences)} sequências, {len(fieldnames)} features)"
        )

    # ──────────────────────────────────────────────
    # ProteinMPNN real (quando instalado)
    # ──────────────────────────────────────────────

    def _run_mpnn(self, mpnn_path: Path, pdb: Path, receptor_pdb: str, cfg: dict) -> list[str]:
        out_dir = self.workdir / "mpnn_out" / pdb.stem
        out_dir.mkdir(parents=True, exist_ok=True)

        fasta_files = (
            list((out_dir / "seqs").glob("*.fa")) +
            list((out_dir / "seqs").glob("*.fasta"))
        )

        # Só roda ProteinMPNN se os FASTAs ainda não existem (evita re-execução demorada)
        if not fasta_files:
            cmd = [
                "python", str(mpnn_path / "protein_mpnn_run.py"),
                "--pdb_path", str(pdb),
                "--out_folder", str(out_dir),
                "--num_seq_per_target", str(cfg.get("num_seq_per_target", 500)),
                "--sampling_temp", str(cfg.get("sampling_temp", 0.1)),
                "--backbone_noise", str(cfg.get("backbone_noise", 0.05)),
                "--omit_AAs", cfg.get("omit_aas", "CX"),
                "--batch_size", "1",
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if proc.returncode != 0:
                self.logger.error(f"ProteinMPNN falhou ({pdb.stem}): {proc.stderr[-300:]}")
                return self._generate_ml_dataset(10, cfg)
            fasta_files = (
                list((out_dir / "seqs").glob("*.fa")) +
                list((out_dir / "seqs").glob("*.fasta"))
            )

        sequences = []
        for fa in fasta_files:
            for _, seq in parse_fasta(str(fa)):
                clean = seq.replace("-", "")
                # ProteinMPNN separa cadeias com "/": RECEPTOR_SEQ/BINDER_SEQ
                # Extrair apenas a cadeia binder (última parte após "/")
                parts = clean.split("/")
                binder = parts[-1] if len(parts) > 1 else parts[0]
                if binder:
                    sequences.append(binder)
        return sequences if sequences else self._generate_ml_dataset(10, cfg)

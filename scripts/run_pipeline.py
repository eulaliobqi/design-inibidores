#!/usr/bin/env python3
"""
run_pipeline.py — Orquestrador do pipeline de design de inibidores peptídicos.

Uso:
  python scripts/run_pipeline.py --config config.yaml --step all
  python scripts/run_pipeline.py --config config.yaml --step structure
  python scripts/run_pipeline.py --config config.yaml --resume --step docking

Etapas:
  structure   → mapeia sítio S1 nos 4 PDBs
  rfdiffusion → gera backbones peptídicos
  mpnn        → desenha sequências
  rosetta     → refina complexos
  docking     → valida afinidade (Vina) contra alvos Lepidoptera
  md          → estabilidade MD (GROMACS)
  ranking     → score composto + CSV
  specificity → seletividade vs não-alvos (humana + Apis mellifera) [R4]
  cleavage    → resistência proteolítica in silico (PeptideCutter rules) [R5]
  visualize   → figuras automáticas
  report      → relatório HTML/Markdown
  optimize    → redesign iterativo (requer ranking prévio)
  all         → executa tudo em sequência
"""
import argparse
import json
import sys
from pathlib import Path

import yaml

# Adiciona raiz do projeto ao path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from scripts.agents import (
    StructureAgent, RFdiffusionAgent, ProteinMPNNAgent, RosettaAgent,
    DockingAgent, MDAgent, OptimizationAgent, RankingAgent,
    VisualizationAgent, ReportAgent, SpecificityAgent,
)
from scripts.utils import tool_summary

# Checkpoint reutilizado do projeto
sys.path.insert(0, str(ROOT))
try:
    from checkpoint import CheckpointManager
except ImportError:
    class CheckpointManager:
        def __init__(self, f): self.f = Path(f); self.data = json.loads(self.f.read_text()) if self.f.exists() else {}
        def save(self, k, v): self.data[k] = v; self.f.write_text(json.dumps(self.data, indent=2, default=str))
        def load(self, k): return self.data.get(k, {})
        def is_completed(self, k): return k in self.data


STEPS = ["structure", "rfdiffusion", "mpnn", "rosetta", "docking",
         "md", "ranking", "specificity", "cleavage",
         "visualize", "report", "optimize"]


def load_config(path: str) -> dict:
    with open(path) as f:
        cfg = yaml.safe_load(f)
    # Expandir variáveis de ambiente nos caminhos
    import os
    def expand(v):
        if isinstance(v, str):
            return os.path.expandvars(os.path.expanduser(v))
        if isinstance(v, list):
            return [expand(x) for x in v]
        if isinstance(v, dict):
            return {k: expand(vv) for k, vv in v.items()}
        return v
    return expand(cfg)


def print_banner(config: dict, tools: dict):
    print("\n" + "═" * 60)
    print("  PIPELINE — Design de Inibidores de Tripsina Lepidoptera")
    print("═" * 60)
    print(f"  Projeto : {config['project']['name']}")
    print(f"  PDBs    : {len(config['data']['receptor_pdbs'])} estruturas")
    print(f"  Saída   : {config['data']['outputs_dir']}/")
    print()
    print("  Ferramentas detectadas:")
    for tool, ok in tools.items():
        status = "✓" if ok else "✗ (modo heurístico)"
        print(f"    {tool:<15} {status}")
    print("═" * 60 + "\n")


def should_run(step: str, args, ckpt: CheckpointManager) -> bool:
    if args.step not in ["all", step]:
        return False
    if args.resume and ckpt.is_completed(step):
        print(f"  [skip] {step} já concluído (checkpoint)")
        return False
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline multiagente para design de inibidores peptídicos de tripsina"
    )
    parser.add_argument("--config",  default="config.yaml",
                        help="Caminho para config.yaml")
    parser.add_argument("--step",    default="all",
                        choices=STEPS + ["all"],
                        help="Etapa a executar (default: all)")
    parser.add_argument("--resume",  action="store_true",
                        help="Retomar do último checkpoint")
    parser.add_argument("--iter",    type=int, default=1,
                        help="Iteração de otimização (para --step optimize)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostrar ferramentas detectadas sem executar")
    parser.add_argument("--md-sequences", nargs="+", metavar="SEQ",
                        help="Forçar sequências específicas no --step md (sobrescreve seleção automática)")
    parser.add_argument("--docking-sequences", nargs="+", metavar="SEQ",
                        help="Forçar sequências específicas no --step docking (sobrescreve heurística de seleção top-N)")
    args = parser.parse_args()

    # ── Carregar configuração ────────────────────────────────────────────────
    config = load_config(args.config)
    out_base = Path(config["data"]["outputs_dir"])
    out_base.mkdir(exist_ok=True)

    ckpt = CheckpointManager(out_base / "checkpoint.json")
    tools = tool_summary(config)
    print_banner(config, tools)

    if args.dry_run:
        print("  [dry-run] Saindo sem executar.")
        return

    pdbs = config["data"]["receptor_pdbs"]
    primary_pdb = pdbs[0]  # PDB primário (receptor)

    # ── STAGE 1: Análise estrutural ─────────────────────────────────────────
    if should_run("structure", args, ckpt):
        print("━" * 50)
        print("STAGE 1 — Mapeamento do Sítio S1")
        agent = StructureAgent("StructureAgent", config, out_base / "structure")
        binding_site = agent.run(pdbs)
        ckpt.save("structure", binding_site)
        print(f"  ✓ Sítio consenso: {binding_site['consensus_center_xyz']}")
    else:
        binding_site = ckpt.load("structure") or {}

    # ── STAGE 2: RFdiffusion ─────────────────────────────────────────────────
    if should_run("rfdiffusion", args, ckpt):
        print("━" * 50)
        print("STAGE 2 — Geração de Backbones (RFdiffusion)")
        agent = RFdiffusionAgent("RFdiffusionAgent", config, out_base / "rfdiffusion")
        backbones = agent.run(primary_pdb, binding_site)
        manifest = {str(k): [str(p) for p in v] for k, v in backbones.items()}
        ckpt.save("rfdiffusion", manifest)
        total = sum(len(v) for v in backbones.values())
        print(f"  ✓ {total} backbones gerados")
    else:
        manifest = ckpt.load("rfdiffusion") or {}
        backbones = {int(k): [Path(p) for p in v] for k, v in manifest.items()}

    # ── STAGE 3: ProteinMPNN ────────────────────────────────────────────────
    if should_run("mpnn", args, ckpt):
        print("━" * 50)
        print("STAGE 3 — Design de Sequências (ProteinMPNN)")
        agent = ProteinMPNNAgent("ProteinMPNNAgent", config, out_base / "proteinmpnn")
        sequences_data = agent.run(backbones, primary_pdb)
        ckpt.save("mpnn", {k: {**v, "sequences": v["sequences"][:5]}  # checkpoint compacto
                           for k, v in sequences_data.items()})
        total = sum(len(v["sequences"]) for v in sequences_data.values())
        print(f"  ✓ {total} sequências geradas")
    else:
        # Recarregar do disco
        mpnn_dir = out_base / "proteinmpnn"
        seq_file = mpnn_dir / "sequences_properties.json"
        if seq_file.exists():
            sequences_data = json.loads(seq_file.read_text())
        else:
            sequences_data = ckpt.load("mpnn") or {}

    # ── STAGE 4: Rosetta ────────────────────────────────────────────────────
    if should_run("rosetta", args, ckpt):
        print("━" * 50)
        print("STAGE 4 — Refinamento de Interface (Rosetta / PyRosetta)")
        agent = RosettaAgent("RosettaAgent", config, out_base / "rosetta")
        rosetta_results = agent.run(primary_pdb, sequences_data, binding_site)
        ckpt.save("rosetta", {k: {kk: vv for kk, vv in v.items()
                                  if kk != "refined_pdb"}
                               for k, v in rosetta_results.items()})
        print(f"  ✓ {len(rosetta_results)} complexos refinados")
    else:
        ros_file = out_base / "rosetta" / "rosetta_scores.json"
        rosetta_results = (json.loads(ros_file.read_text())
                           if ros_file.exists() else ckpt.load("rosetta") or {})

    # ── STAGE 5: Docking ────────────────────────────────────────────────────
    if should_run("docking", args, ckpt):
        print("━" * 50)
        print("STAGE 5 — Docking Molecular (AutoDock Vina)")
        if getattr(args, "docking_sequences", None):
            config.setdefault("docking", {})["forced_sequences"] = args.docking_sequences
            print(f"  → Sequências forçadas: {args.docking_sequences}")
        agent = DockingAgent("DockingAgent", config, out_base / "docking")
        docking_results = agent.run(primary_pdb, sequences_data, binding_site)
        ckpt.save("docking", docking_results)
        print(f"  ✓ {len(docking_results)} poses calculadas")
    else:
        dock_file = out_base / "docking" / "docking_results.json"
        docking_results = (json.loads(dock_file.read_text())
                           if dock_file.exists() else ckpt.load("docking") or {})

    # ── STAGE 6: MD ─────────────────────────────────────────────────────────
    if should_run("md", args, ckpt):
        print("━" * 50)
        print("STAGE 6 — Dinâmica Molecular (GROMACS)")
        if getattr(args, "md_sequences", None):
            config.setdefault("md", {})["forced_sequences"] = args.md_sequences
            print(f"  → Sequências forçadas: {args.md_sequences}")
        agent = MDAgent("MDAgent", config, out_base / "md")
        md_results = agent.run(rosetta_results, primary_pdb)
        ckpt.save("md", md_results)
        print(f"  ✓ {len(md_results)} simulações concluídas")
    else:
        md_file = out_base / "md" / "md_results.json"
        md_results = (json.loads(md_file.read_text())
                      if md_file.exists() else ckpt.load("md") or {})

    # ── STAGE 7: Ranking ────────────────────────────────────────────────────
    if should_run("ranking", args, ckpt):
        print("━" * 50)
        print("STAGE 7 — Ranking Final")
        agent = RankingAgent("RankingAgent", config, out_base / "ranking")
        ranking_df = agent.run(sequences_data, docking_results,
                               rosetta_results, md_results)
        ckpt.save("ranking", {"n_candidates": len(ranking_df)})
        if not ranking_df.empty:
            print(f"  ✓ {len(ranking_df)} candidatos rankeados")
            print(f"  🏆 Top-1: {ranking_df.iloc[0]['sequence']} "
                  f"(score={ranking_df.iloc[0]['final_score']:.3f})")
    else:
        import pandas as pd
        rank_file = out_base / "ranking" / "ranking.csv"
        ranking_df = pd.read_csv(rank_file) if rank_file.exists() else pd.DataFrame()

    # ── STAGE 8: Especificidade (R4) ───────────────────────────────────────
    if should_run("specificity", args, ckpt):
        print("━" * 50)
        print("STAGE 8 — Especificidade vs. Não-Alvos (Vina: humana + Apis)")
        if docking_results:
            agent = SpecificityAgent("SpecificityAgent", config,
                                      out_base / "specificity")
            spec_results = agent.run(docking_results, docking_results)
            n_approved = spec_results.get("n_approved", 0)
            n_total    = len(spec_results.get("selectivity", {}))
            ckpt.save("specificity", {"n_approved": n_approved, "n_total": n_total})
            print(f"  ✓ {n_approved}/{n_total} candidatos aprovados (SI ≥ "
                  f"{config.get('specificity', {}).get('selectivity_threshold', 2.0)} kcal/mol)")
        else:
            print("  ⚠ Docking não disponível — especificidade pulada")
    else:
        spec_file = out_base / "specificity" / "specificity_results.json"
        spec_results = (json.loads(spec_file.read_text())
                        if spec_file.exists() else {})

    # ── STAGE 9: Resistência proteolítica (R5) ─────────────────────────────
    if should_run("cleavage", args, ckpt):
        print("━" * 50)
        print("STAGE 9 — Resistência Proteolítica (Análise de Clivagem)")
        import subprocess as _sp
        import sys as _sys
        _r = _sp.run(
            [_sys.executable, str(ROOT / "scripts" / "analyze_cleavage.py"),
             "--top", str(config.get("ranking", {}).get("top_candidates", 20))],
            capture_output=True, text=True
        )
        cleavage_file = out_base / "cleavage_analysis.json"
        if cleavage_file.exists():
            cleavage_data = json.loads(cleavage_file.read_text())
            n_resistant = sum(1 for r in cleavage_data if r.get("verdict") == "RESISTENTE")
            n_total_cl  = len(cleavage_data)
            ckpt.save("cleavage", {"n_resistant": n_resistant, "n_total": n_total_cl})
            print(f"  ✓ {n_resistant}/{n_total_cl} candidatos resistentes ao trato intestinal")
            if _r.stdout:
                # Mostrar resumo (últimas 10 linhas)
                for line in _r.stdout.strip().splitlines()[-10:]:
                    print(f"    {line}")
        else:
            print(f"  ✗ Análise de clivagem falhou: {_r.stderr[:200]}")
    else:
        cleavage_file = out_base / "cleavage_analysis.json"
        cleavage_data = (json.loads(cleavage_file.read_text())
                         if cleavage_file.exists() else [])

    # ── STAGE 10: Visualização ──────────────────────────────────────────────
    if should_run("visualize", args, ckpt):
        print("━" * 50)
        print("STAGE 10 — Visualizações")
        agent = VisualizationAgent("VisualizationAgent", config,
                                    out_base / "visualizations")
        figures = agent.run(ranking_df, binding_site)
        ckpt.save("visualize", {"figures": list(figures.keys())})
        print(f"  ✓ {len(figures)} figuras geradas")
    else:
        figures = {}

    # ── STAGE 11: Relatório ─────────────────────────────────────────────────
    if should_run("report", args, ckpt):
        print("━" * 50)
        print("STAGE 11 — Relatório Final")
        agent = ReportAgent("ReportAgent", config, out_base / "reports")
        # Mover figuras para reports/
        import shutil
        for f_path in figures.values():
            if f_path and Path(f_path).exists():
                dest = out_base / "reports" / Path(f_path).name
                shutil.copy(f_path, dest)
        report_paths = agent.run(ranking_df, binding_site, figures, tools)
        ckpt.save("report", report_paths)
        print(f"  ✓ Relatório: {report_paths.get('html')}")
    else:
        report_paths = ckpt.load("report") or {}

    # ── STAGE 12: Otimização iterativa ──────────────────────────────────────
    if should_run("optimize", args, ckpt):
        print("━" * 50)
        print(f"STAGE 12 — Redesign Iterativo (iteração {args.iter})")
        if ranking_df.empty:
            print("  ✗ Ranking vazio — execute --step ranking primeiro")
        else:
            agent = OptimizationAgent("OptimizationAgent", config,
                                       out_base / "optimization")
            new_candidates = agent.run(ranking_df, iteration=args.iter)
            print(f"  ✓ {len(new_candidates)} novos candidatos para próxima rodada")
            print(f"  → Re-execute com --step mpnn após adicionar novos backbones")

    # ── Resumo final ────────────────────────────────────────────────────────
    print("\n" + "═" * 60)
    print("  PIPELINE CONCLUÍDO")
    if not ranking_df.empty:
        print(f"\n  Top-5 Candidatos:")
        for _, row in ranking_df.head(5).iterrows():
            print(f"    #{int(row['rank'])}  {row['sequence']:<22}  "
                  f"len={int(row['length'])}  score={row['final_score']:.3f}")
    html_path = report_paths.get("html") or out_base / "reports" / "report.html"
    print(f"\n  Relatório: {html_path}")
    print(f"  Outputs:   {out_base}/")
    print("═" * 60 + "\n")


if __name__ == "__main__":
    main()

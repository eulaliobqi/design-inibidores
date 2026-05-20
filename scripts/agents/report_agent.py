"""ReportAgent — Gera relatório científico em Markdown e HTML."""
import json
from datetime import datetime
from pathlib import Path

from .base_agent import BaseAgent

_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Design de Inibidores — Relatório Final</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; max-width: 1100px; margin: 40px auto;
          color: #1a1a2e; background: #f9f9fb; padding: 0 20px; }}
  h1 {{ color: #1a5276; border-bottom: 3px solid #2e86c1; padding-bottom: 8px; }}
  h2 {{ color: #2e86c1; margin-top: 35px; }}
  h3 {{ color: #117a65; }}
  table {{ border-collapse: collapse; width: 100%; margin: 15px 0; font-size: 13px; }}
  th {{ background: #2e86c1; color: white; padding: 8px 10px; text-align: center; }}
  td {{ padding: 6px 10px; border-bottom: 1px solid #ddd; text-align: center; }}
  tr:nth-child(even) {{ background: #eaf4fb; }}
  tr.top1 {{ background: #d4efdf !important; font-weight: bold; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 10px;
             font-size: 11px; font-weight: bold; }}
  .badge-green {{ background: #d4efdf; color: #1e8449; }}
  .badge-blue  {{ background: #d6eaf8; color: #1a5276; }}
  img {{ max-width: 100%; border: 1px solid #ddd; border-radius: 6px; margin: 10px 0; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }}
  .info-box {{ background: #eaf4fb; border-left: 4px solid #2e86c1;
               padding: 12px 16px; border-radius: 4px; margin: 10px 0; }}
  .warn-box {{ background: #fef9e7; border-left: 4px solid #f39c12;
               padding: 10px 14px; border-radius: 4px; margin: 8px 0; font-size: 13px; }}
  pre {{ background: #2c3e50; color: #ecf0f1; padding: 14px; border-radius: 6px;
         overflow-x: auto; font-size: 12px; }}
  code {{ background: #eaecee; padding: 1px 5px; border-radius: 3px; }}
</style>
</head>
<body>
{body}
</body>
</html>
"""


class ReportAgent(BaseAgent):

    def run(self, ranking_df, binding_site: dict,
            figures: dict, tool_status: dict) -> dict:
        md_path  = self.workdir / "report.md"
        html_path = self.workdir / "report.html"

        md_content  = self._build_markdown(ranking_df, binding_site,
                                           figures, tool_status)
        html_content = self._build_html(ranking_df, binding_site,
                                        figures, tool_status)

        md_path.write_text(md_content, encoding="utf-8")
        html_path.write_text(html_content, encoding="utf-8")

        self.logger.info(f"Relatório salvo: {html_path}")
        return {"markdown": str(md_path), "html": str(html_path)}

    # ─── Markdown ───────────────────────────────────────────────────────────

    def _build_markdown(self, df, binding_site, figures, tools) -> str:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        top = df.head(10) if not df.empty else df

        lines = [
            f"# Relatório — Design de Inibidores Peptídicos de Tripsina de Lepidoptera",
            f"",
            f"**Data:** {ts}  ",
            f"**Pipeline:** Multi-Agente | Python · RFdiffusion · ProteinMPNN · Rosetta · Vina · GROMACS",
            f"",
            f"---",
            f"",
            f"## 1. Alvo Molecular",
            f"",
            f"**Enzima:** Tripsina digestiva de lepidóptero-praga (serina-protease)  ",
            f"**Sítio-alvo:** Bolso S1 — especificidade por Arg/Lys em P1  ",
            f"**Estruturas template:** {binding_site.get('n_structures', 4)} PDBs (clusters HADDOCK)",
            f"",
            f"### Sítio de Ligação Mapeado",
            f"",
            f"| Parâmetro | Valor |",
            f"|---|---|",
            f"| Centro (X, Y, Z) | {binding_site.get('consensus_center_xyz', '-')} |",
            f"| Hotspot residues | {binding_site.get('hotspot_residues', [])} |",
            f"| Pocket radius | 8.0 Å |",
            f"",
            f"---",
            f"",
            f"## 2. Ferramentas Utilizadas",
            f"",
        ]

        for tool, ok in tools.items():
            status = "✓ instalado" if ok else "✗ não encontrado (heurística usada)"
            lines.append(f"- **{tool}**: {status}")

        lines += [
            f"",
            f"---",
            f"",
            f"## 3. Candidatos — Top 10",
            f"",
            f"| Rank | Sequência | Tam (aa) | Vina (kcal/mol) | Rosetta I_sc | Score |",
            f"|---|---|---|---|---|---|",
        ]

        for _, row in top.iterrows():
            vina = f"{row['vina_affinity']:.2f}" if str(row.get("vina_affinity")) != "None" and row.get("vina_affinity") is not None else "N/A"
            isc  = f"{row['rosetta_I_sc']:.2f}" if str(row.get("rosetta_I_sc")) != "None" and row.get("rosetta_I_sc") is not None else "N/A"
            lines.append(
                f"| {int(row['rank'])} | `{row['sequence']}` | {int(row['length'])} "
                f"| {vina} | {isc} | {row['final_score']:.3f} |"
            )

        lines += [
            f"",
            f"---",
            f"",
            f"## 4. Propriedades dos Top-5",
            f"",
            f"| Sequência | PM (Da) | Carga | H-fóbico (%) | #Arg+Lys |",
            f"|---|---|---|---|---|",
        ]

        from ..utils import peptide_properties
        for _, row in top.head(5).iterrows():
            p = peptide_properties(row["sequence"])
            lines.append(
                f"| `{row['sequence']}` | {p['mw_da']:.0f} | "
                f"{p['net_charge']:+.1f} | {p['frac_hydrophobic']*100:.0f}% | {p['n_arg_lys']} |"
            )

        lines += [
            f"",
            f"---",
            f"",
            f"## 5. Estratégia de Inibição",
            f"",
            f"Os candidatos selecionados foram desenhados para:",
            f"",
            f"1. **Ocupar profundamente o bolso S1** com Arg/Lys na posição P1",
            f"2. **Interagir com o Asp do sítio S1** via pontes de sal",
            f"3. **Bloquear a tríade catalítica** (His–Asp–Ser) por impedimento estérico",
            f"4. **Maximizar H-bonds** com resíduos do backbone da enzima",
            f"5. **Resistir à proteólise** (posição P1' desenhada com resíduo volumoso)",
            f"",
            f"---",
            f"",
            f"## 6. Próximos Passos",
            f"",
            f"- [ ] Síntese química dos top-3 candidatos",
            f"- [ ] Ensaios de inibição enzimática in vitro (Ki, IC50)",
            f"- [ ] Análise de estabilidade por CD e NMR",
            f"- [ ] Ensaios de bioatividade em bioensaios com lagartas-praga",
            f"- [ ] Extensão da MD para 200 ns nos 2 melhores candidatos",
        ]

        return "\n".join(lines)

    # ─── HTML ───────────────────────────────────────────────────────────────

    def _build_html(self, df, binding_site, figures, tools) -> str:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")

        tool_badges = "".join(
            f'<span class="badge badge-{"green" if ok else "blue"}">'
            f'{"✓" if ok else "✗"} {tool}</span> '
            for tool, ok in tools.items()
        )

        # Tabela top-20
        if df.empty:
            table_html = "<p>Nenhum candidato gerado.</p>"
        else:
            top = df.head(20)
            headers = ["Rank", "Sequência", "Tam", "Vina (kcal/mol)",
                       "Rosetta I_sc", "RMSD MD (nm)", "H-bonds", "#R+K", "Score"]
            ths = "".join(f"<th>{h}</th>" for h in headers)
            rows_html = ""
            for _, row in top.iterrows():
                cls = "top1" if row["rank"] == 1 else ""
                def fmt(v, dec=2):
                    return f"{v:.{dec}f}" if v is not None and str(v) != "None" else "—"
                cells = [
                    str(int(row["rank"])), f"<code>{row['sequence']}</code>",
                    str(int(row["length"])),
                    fmt(row.get("vina_affinity")),
                    fmt(row.get("rosetta_I_sc")),
                    fmt(row.get("md_rmsd_nm"), 3),
                    fmt(row.get("hbond_avg"), 1),
                    str(int(row.get("n_arg_lys", 0))),
                    fmt(row["final_score"], 3),
                ]
                rows_html += (
                    f"<tr class='{cls}'>" +
                    "".join(f"<td>{c}</td>" for c in cells) +
                    "</tr>\n"
                )
            table_html = (
                f"<table><thead><tr>{ths}</tr></thead>"
                f"<tbody>{rows_html}</tbody></table>"
            )

        # Figuras
        fig_html = '<div class="grid">'
        for name, path in figures.items():
            if path and Path(path).exists():
                rel = Path(path).name
                fig_html += f'<img src="{rel}" alt="{name}">'
        fig_html += "</div>"

        center = binding_site.get("consensus_center_xyz", ["-", "-", "-"])
        hotspots = binding_site.get("hotspot_residues", [])

        body = f"""
<h1>Design de Inibidores Peptídicos de Tripsina de Lepidoptera</h1>
<p><strong>Data:</strong> {ts} &nbsp;|&nbsp;
   <strong>Pipeline:</strong> Multi-Agente (RFdiffusion · ProteinMPNN · Rosetta · Vina · GROMACS)</p>

<div class="info-box">
  <strong>Alvo:</strong> Tripsina digestiva de lepidóptero-praga &nbsp;|&nbsp;
  <strong>Sítio:</strong> Bolso S1 (Asp específico S1) &nbsp;|&nbsp;
  <strong>Centro:</strong> {center}
</div>

<h2>Ferramentas</h2>
{tool_badges}

<h2>Sítio de Ligação Mapeado</h2>
<div class="info-box">
  <strong>Hotspots:</strong> {hotspots}<br>
  <strong>Estruturas analisadas:</strong> {binding_site.get('n_structures', 4)} PDBs
</div>

<h2>Top 20 Candidatos</h2>
{table_html}

<h2>Estratégia de Inibição</h2>
<ol>
  <li><strong>P1 = Arg/Lys</strong> — ocupa o bolso S1 com carga positiva (Asp específico S1)</li>
  <li><strong>P2-P4</strong> — resíduos hidrofóbicos para contatos com a parede do sítio</li>
  <li><strong>P1'</strong> — resíduo volumoso para impedir acesso da água</li>
  <li><strong>Comprimentos variados</strong> — 5 a 20 aa para cobertura do sítio S1 ao S5</li>
</ol>

<h2>Figuras</h2>
{fig_html}

<h2>Próximos Passos</h2>
<ul>
  <li>Síntese química e purificação dos top-3 candidatos</li>
  <li>Ensaios de inibição (Ki, IC50) com tripsina de lepidóptero</li>
  <li>Validação estrutural (CD, NMR ou cristalografia)</li>
  <li>MD 200 ns dos 2 melhores candidatos</li>
  <li>Bioensaios com lagartas (S. frugiperda, H. armigera)</li>
</ul>
"""
        return _HTML_TEMPLATE.format(body=body)

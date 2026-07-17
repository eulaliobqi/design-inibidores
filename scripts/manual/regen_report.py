"""
regen_report.py — Regenera report.md e report.html com dados atualizados.

Uso: conda run -n ML python regen_report.py
"""
import json
from datetime import datetime
from pathlib import Path

import pandas as pd

BASE    = Path("outputs")
CSV     = BASE / "ranking" / "ranking.csv"
BS_JSON = BASE / "structure" / "binding_site.json"
VIZ_DIR = BASE / "visualizations"
MD_OUT  = BASE / "reports" / "report.md"
HTML_OUT = BASE / "reports" / "report.html"

# ── Carregar dados ─────────────────────────────────────────────
df = pd.read_csv(CSV)
binding_site = json.loads(BS_JSON.read_text())
ts = datetime.now().strftime("%Y-%m-%d %H:%M")

top10 = df.head(10)
top5  = df.head(5)

def fmt(v, dec=2):
    try:
        f = float(v)
        if pd.isna(f):
            return "N/A"
        return f"{f:.{dec}f}"
    except Exception:
        return "N/A"

# ── Markdown ───────────────────────────────────────────────────
def build_markdown():
    lines = [
        "# Relatório — Design de Inibidores Peptídicos de Tripsina de Lepidoptera",
        "",
        f"**Data:** {ts}  ",
        "**Pipeline:** Multi-Agente | Python · RFdiffusion · ProteinMPNN · PyRosetta · Vina · GROMACS",
        "",
        "---",
        "",
        "## 1. Alvo Molecular",
        "",
        "**Enzima:** Tripsina digestiva de lepidóptero-praga (serina-protease)  ",
        "**Sítio-alvo:** Bolso S1 — especificidade por Arg/Lys em P1  ",
        f"**Estruturas template:** {binding_site.get('n_structures', 4)} PDBs",
        "",
        "### Sítio de Ligação",
        "",
        "| Parâmetro | Valor |",
        "|---|---|",
        f"| Centro (X, Y, Z) | {binding_site.get('consensus_center_xyz', '—')} |",
        f"| Hotspot residues | {binding_site.get('hotspot_residues', [])} |",
        "| Pocket radius | 8.0 Å |",
        "",
        "---",
        "",
        "## 2. Ferramentas Utilizadas",
        "",
        "- **RFdiffusion**: ✓ (330 backbones gerados)",
        "- **ProteinMPNN**: ✓ (24.513 sequências únicas)",
        "- **Vina**: ✓ (36 sequências dockadas, 194 poses)",
        "- **PyRosetta**: ✓ (10 complexos refinados — FastRelax + InterfaceAnalyzerMover)",
        "- **GROMACS**: ✓ (MD 10 ns — 1/5 concluído no servidor)",
        "",
        "---",
        "",
        "## 3. Candidatos — Top 10",
        "",
        "| Rank | Sequência | Tam (aa) | Vina (kcal/mol) | Rosetta I_sc | Score |",
        "|---|---|---|---|---|---|",
    ]

    for _, row in top10.iterrows():
        vina = fmt(row.get("vina_affinity"))
        isc  = fmt(row.get("rosetta_I_sc"))
        # length: label do grupo (5/7/10/20) mas peptídeo real é 20 AA
        lines.append(
            f"| {int(row['rank'])} | `{row['sequence']}` | 20 "
            f"| {vina} | {isc} | {row['final_score']:.3f} |"
        )

    lines += [
        "",
        "---",
        "",
        "## 4. Propriedades dos Top-5",
        "",
        "| Sequência | PM (Da) | Carga | H-fóbico (%) | #Arg+Lys |",
        "|---|---|---|---|---|",
    ]

    for _, row in top5.iterrows():
        lines.append(
            f"| `{row['sequence']}` | {fmt(row['mw_da'], 0)} | "
            f"{'+' if float(row['net_charge'])>=0 else ''}{fmt(row['net_charge'], 1)} "
            f"| {float(row['frac_hydrophobic'])*100:.0f}% | {int(row['n_arg_lys'])} |"
        )

    lines += [
        "",
        "---",
        "",
        "## 5. Resultado MD — GSRASARAYAARVRARRAAL (2026-06-18)",
        "",
        "| Parâmetro | Valor |",
        "|---|---|",
        "| RMSD médio | 0,37 nm |",
        "| RMSD final | 0,375 nm |",
        "| Rg médio ± DP | 1,792 ± 0,023 nm |",
        "| H-bonds médio | 160,1 |",
        "| Estabilidade | **ESTÁVEL** — RMSD < 0,5 nm em 10 ns |",
        "",
        "---",
        "",
        "## 6. Estratégia de Inibição",
        "",
        "Os candidatos foram desenhados para:",
        "",
        "1. **Ocupar o bolso S1** com Arg/Lys na posição P1 (Asp específico S1)",
        "2. **Bloquear a tríade catalítica** (His–Asp–Ser) por impedimento estérico",
        "3. **Maximizar H-bonds** com residuos do backbone da enzima",
        "4. **Resistir à proteólise** (P1' com resíduo volumoso)",
        "",
        "**Padrão identificado:** todos os top-4 têm Arg/Lys abundantes (n=6-9) e fração hidrofóbica moderada — mecanismo competitivo clássico.",
        "",
        "---",
        "",
        "## 7. Próximos Passos",
        "",
        "- [x] RFdiffusion — 330 backbones",
        "- [x] ProteinMPNN — 24.513 sequências",
        "- [x] Docking Vina — 36 candidatos (194 poses)",
        "- [x] PyRosetta — 10 complexos refinados",
        "- [x] MD 10 ns — GSRASARAYAARVRARRAAL (ESTÁVEL)",
        "- [ ] MD 10 ns — 4 candidatos restantes (servidor)",
        "- [ ] Síntese química dos top-3 (Fmoc-SPPS)",
        "- [ ] Ensaios de inibição enzimática (Ki, IC50)",
        "- [ ] Docking completo dos 24.513 candidatos → dataset ML",
        "- [ ] Treinamento ML/DL sobre dataset completo",
    ]

    return "\n".join(lines)


# ── HTML ───────────────────────────────────────────────────────
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Design de Inibidores — Relatório Final</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; max-width: 1100px; margin: 40px auto;
          color: #1a1a2e; background: #f9f9fb; padding: 0 20px; }}
  h1 {{ color: #1a5276; border-bottom: 3px solid #2e86c1; padding-bottom: 8px; }}
  h2 {{ color: #2e86c1; margin-top: 35px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 15px 0; font-size: 13px; }}
  th {{ background: #2e86c1; color: white; padding: 8px 10px; text-align: center; }}
  td {{ padding: 6px 10px; border-bottom: 1px solid #ddd; text-align: center; }}
  tr:nth-child(even) {{ background: #eaf4fb; }}
  tr.top1 {{ background: #d4efdf !important; font-weight: bold; }}
  .badge-green {{ display:inline-block; padding:2px 8px; border-radius:10px;
                  font-size:11px; font-weight:bold; background:#d4efdf; color:#1e8449; }}
  .info-box {{ background: #eaf4fb; border-left: 4px solid #2e86c1;
               padding: 12px 16px; border-radius: 4px; margin: 10px 0; }}
  .md-box {{ background: #eafaf1; border-left: 4px solid #1e8449;
             padding: 12px 16px; border-radius: 4px; margin: 10px 0; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }}
  img {{ max-width: 100%; border: 1px solid #ddd; border-radius: 6px; margin: 10px 0; }}
  code {{ background: #eaecee; padding: 1px 5px; border-radius: 3px; font-size:12px; }}
</style>
</head>
<body>
{body}
</body>
</html>"""


def build_html():
    headers = ["Rank", "Sequência", "Vina (kcal/mol)", "Rosetta I_sc", "RMSD MD", "#R+K", "Score"]
    ths = "".join(f"<th>{h}</th>" for h in headers)
    rows_html = ""
    for _, row in df.head(20).iterrows():
        cls = "top1" if row["rank"] == 1 else ""
        cells = [
            str(int(row["rank"])),
            f"<code>{row['sequence']}</code>",
            fmt(row.get("vina_affinity")),
            fmt(row.get("rosetta_I_sc")),
            fmt(row.get("md_rmsd_nm"), 3),
            str(int(row.get("n_arg_lys", 0))),
            fmt(row["final_score"], 3),
        ]
        rows_html += f"<tr class='{cls}'>{''.join(f'<td>{c}</td>' for c in cells)}</tr>\n"

    table_html = f"<table><thead><tr>{ths}</tr></thead><tbody>{rows_html}</tbody></table>"

    figs = ""
    for img in sorted(VIZ_DIR.glob("*.png")):
        figs += f'<img src="../visualizations/{img.name}" alt="{img.stem}">\n'

    center = binding_site.get("consensus_center_xyz", "—")
    hotspots = binding_site.get("hotspot_residues", [])

    body = f"""
<h1>Design de Inibidores Peptídicos de Tripsina de Lepidoptera</h1>
<p><strong>Data:</strong> {ts} &nbsp;|&nbsp;
   <strong>Pipeline:</strong> Multi-Agente (RFdiffusion · ProteinMPNN · PyRosetta · Vina · GROMACS)</p>

<div class="info-box">
  <strong>Alvo:</strong> Tripsina digestiva (serina-protease) &nbsp;|&nbsp;
  <strong>Sítio:</strong> Bolso S1 &nbsp;|&nbsp;
  <strong>Centro:</strong> {center}
  <br><strong>Hotspots:</strong> {hotspots}
</div>

<h2>Ferramentas</h2>
<span class="badge-green">✓ RFdiffusion</span>
<span class="badge-green">✓ ProteinMPNN</span>
<span class="badge-green">✓ Vina</span>
<span class="badge-green">✓ PyRosetta</span>
<span class="badge-green">✓ GROMACS</span>

<h2>Top 20 Candidatos</h2>
{table_html}

<h2>Resultado MD — GSRASARAYAARVRARRAAL</h2>
<div class="md-box">
  <strong>RMSD médio:</strong> 0,37 nm &nbsp;|&nbsp;
  <strong>Rg médio:</strong> 1,792 ± 0,023 nm &nbsp;|&nbsp;
  <strong>H-bonds:</strong> 160,1 &nbsp;|&nbsp;
  <strong>Status:</strong> ESTÁVEL (10 ns)
</div>

<h2>Estratégia de Inibição</h2>
<ol>
  <li><strong>P1 = Arg/Lys</strong> — ancora no bolso S1 (Asp específico S1)</li>
  <li><strong>Tríade catalítica</strong> — bloqueada por impedimento estérico</li>
  <li><strong>H-bonds múltiplos</strong> com backbone da enzima</li>
  <li><strong>P1' volumoso</strong> — dificulta acesso de água e hidrólise</li>
</ol>

<h2>Próximos Passos</h2>
<ul>
  <li>&#x2705; MD 10 ns — GSRASARAYAARVRARRAAL (ESTÁVEL)</li>
  <li>&#x23F3; MD 10 ns — 4 candidatos restantes (servidor)</li>
  <li>&#x23F3; Docking completo 24.513 sequências → dataset ML</li>
  <li>&#x25FB;&#xFE0F; Síntese Fmoc-SPPS + ensaios Ki/IC50</li>
</ul>

<h2>Figuras</h2>
<div class="grid">
{figs}
</div>
"""
    return HTML_TEMPLATE.format(body=body)


# ── Salvar ─────────────────────────────────────────────────────
MD_OUT.write_text(build_markdown(), encoding="utf-8")
HTML_OUT.write_text(build_html(), encoding="utf-8")

print(f"report.md  salvo: {MD_OUT}")
print(f"report.html salvo: {HTML_OUT}")
print(f"\nTop-5 atualizado:")
for _, r in df.head(5).iterrows():
    print(f"  {int(r['rank'])}. {r['sequence']} | Vina={fmt(r['vina_affinity'])} | I_sc={fmt(r['rosetta_I_sc'])} | score={r['final_score']:.3f}")

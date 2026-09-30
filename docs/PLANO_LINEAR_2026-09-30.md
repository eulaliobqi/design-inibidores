# Plano — manuscrito em forma LINEAR (decisão de 30/09/2026)

**Decisão do autor:** o manuscrito passa a tratar os peptídeos apenas na forma **linear**
(coerente com os resultados do grupo: GORE1–5, di/tripeptídeos, PEP-11). Resistência às enzimas
digestivas = **ausência de resíduos clivaveis**. O macrociclo vira (i) **braço de comparação** com os
resultados já obtidos e (ii) **sugestão de otimização** na Discussão. Nada do braço macrocíclico é
apagado.

## 1. O que muda no método (e por quê)

| Etapa | Antes (macrociclo) | Agora (linear) | Estado |
|---|---|---|---|
| Geração de backbones | RFdiffusion `cyclic=True` | **igual** — descrito como sementes estruturais sob restrição de fechamento; o peptídeo é avaliado como linear daí em diante | limitação declarada |
| Filtro de clivagem | circular + P1 geométrico isento | **linear estrito**: sem isenção de âncora; K/R C-terminal conta (carboxipeptidase B); pepsina/elastase/quimotripsina como antes | código pronto, testado (12 testes), commit d9bee41 |
| Boltz-2 | `cyclic: true` | `cyclic: false` (`score_boltz2_b23.py`, `--cyclic` reproduz o antigo) | pronto, smoke-test OK |
| MD | topologia linear com complexo de partida cíclico (incoerente) | partida = predição linear; topologia linear (coerente) | script pronto |
| Comparação | — | `compare_linear_vs_macrocycle.py` (sobreposição, Spearman cíclico×linear, top-1 nos dois braços) | pronto |

Dados já calculados (filtro linear estrito, 8 espécies, 22.066 sequências): **RESISTENTE 2.542 (11,5%)**,
MARGINAL 4.968 (22,5%), SUSCEPTIVEL 14.556 (66,0%). Por espécie RESISTENTE: Sf 227, Sl 301, On 323,
Ds 326, Ci 318, Hv 300, Px 398, Ag 349. Nos RESISTENTE: comprimento médio 6,98 aa, 96,2% ≤10 aa, 61
(2,4%) com K/R, 382 com algum sinalizador de exopeptidase terminal. Braço macrocíclico (já no
manuscrito): 1.829 RESISTENTE (8,3%).

## 2. Computação no servidor (disparo único: `screen -S linear-pipeline; bash scripts/run_linear_pipeline.sh`)

| # | Etapa | Custo estimado | Observação |
|---|---|---|---|
| 1 | Filtro linear estrito | feito | `outputs/b23_cleavage_linear_strict.json` |
| 2 | Boltz-2 linear, 2.542 candidatos | ~5–6 h (≈8 s/predição, medido em 28–30/09) | resume-safe por espécie |
| 3 | Top-1 por espécie (maior `confidence_score` entre RESISTENTE) | segundos | |
| 4 | MD 50 ns × 8 espécies | ~3 h cada (421 ns/dia medidos) ≈ 24 h | *A. gemmatalis* primeiro |
| 5 | *A. gemmatalis* réplicas 2 e 3 | ~6 h | resolve a crítica “1 réplica” só na espécie-título |
| 6 | Análise MD (S1, tríade, RMSD local com PBC) | minutos | `analyze_md_top_candidates` |
| 7 | Comparação linear × macrociclo | segundos | `outputs/linear_vs_macrocycle.json` |
| | **Total** | **≈ 36 h** | disco: +~25 GB (884 GB livres) |

Já feito hoje: os screens `b27-corrected` e `md-agem` foram **interrompidos** (MDs do braço
circular incompletas). As MDs circulares concluídas (NNGGG, GGHTGA) não voltam ao texto como MD do
macrociclo, pois a topologia nunca foi cíclica — entram apenas se o top-1 linear coincidir.

## 3. Reescrita do manuscrito (feita após os resultados, em paralelo à espera do servidor)

- **Título/Abstract/Keywords:** “macrocyclic” → “linear peptide candidates”; macrociclo = comparação/otimização.
- **Introdução:** reenquadrar no grupo (GORE1/2/3, Arg/Lys em P1, Ki 0,10–1,41 mM) e no motivo de
  buscar afinidade maior sem criar substrato (tensão P1 básico × clivagem mantida e discutida).
- **Métodos 2.4:** backbones como sementes sob fechamento; 2.6 filtro linear estrito (definição exata,
  K/R–Pro, C-terminal, pesos); 2.7 Boltz-2 linear; 2.8 MD com partida e topologia coerentes.
- **Resultados:** 3.4–3.5 com os números do filtro linear; 3.6 Boltz-2 linear; 3.7 MD; **nova 3.8**
  “Comparação com o braço macrocíclico” (sobreposição, ρ cíclico×linear, top-1).
- **Discussão:** 4.3 passa a argumentar a favor do critério (resistência por ausência de sítios) e
  contra suas consequências (peptídeos curtos, sem K/R, fora do P1 canônico); **4.5 Perspectivas:**
  macrociclização, D-aminoácidos/Nle/Orn, *capping* N/C-terminal (exopeptidases), P1 básico único.
- **Limitações:** linear fica exposto a exopeptidases do intestino (aminopeptidases/carboxipeptidases)
  — sinalizado, só parcialmente coberto pelo filtro; backbones gerados sob fechamento; ProteinMPNN sem
  receptor fixo; Boltz-2 sem validação em peptídeos de 5–8 aa; réplica única (exceto *A. gemmatalis*).
- Conferir o corpo inteiro por “macrocycl*/cyclic/head-to-tail/circular” (21 ocorrências hoje), Fig. 1
  (legenda), Fig. 3 (recalcular com o conjunto linear), tabelas 4 e 5, e a versão PT (`pt_parts`).

## 4. Literatura (cruzamento)

**Já no RAG do servidor (`eulalio-pos-doc-rag`, corpus real):** Saikhedkar 2019 (bicíclicos > lineares —
sustenta o macrociclo como otimização), Kelly 2005 (papel do *scaffold*), Laskowski 2000, Patarroyo-Vargas
2017/2020 (Arg em P1; inibição competitiva), Almeida 2021/2022, Meriño-Cabrera 2022, Schultz 2026
(degradação proteolítica de inibidores no intestino como resposta adaptativa), **Paulo 2026 (GORE3,
derivado de autólise da tripsina)** e **Severi-Castro 2026 (PEP-11)** — estes dois entram como novas
referências após verificação Crossref/PubMed.
**A verificar (nenhuma entra sem Crossref/PubMed):** peptídeos SFTI-1 acíclicos (ciclização não é essencial
para a atividade, mas estabiliza); carboxipeptidases/aminopeptidases do intestino médio de Lepidoptera;
regra tripsina K/R–Pro; mecanismo de hidrólise lenta de inibidores canônicos.

## 5. Decisões que continuam abertas (para o autor)

1. **Top-1 só por `confidence_score`** (regra do plano) ou top-3 por espécie (+16 MDs, ≈ +48 h)?
   Recomendo manter top-1 (regra declarada previamente) e ampliar só se o resultado for ambíguo.
2. **Extremidades livres:** manter carregadas (peptídeo livre em solução, como o grupo testa) ou
   acetilar/amidar (mimetiza fragmento de proteína)? Plano atual: carregadas.
3. Escopo “só computacional” na seção da revista (pendência antiga).

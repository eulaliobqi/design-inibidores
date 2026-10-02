# Rebaixamento da ocupância de S1 e controle negativo — decisões de 02/10/2026

## Decisões do usuário
1. A ocupância de S1 passa de **critério de camada** a **descrição secundária** (fica nas colunas `occ5_h2`, `anchor`,
   `anchor_same`, `s1_original`; ordena dentro da camada por último).
2. Se a isca (controle embaralhado) do candidato também permanecer em S1, usar **controle negativo**: trocar o resíduo
   da âncora por aminoácidos de química diferente e confirmar perda de afinidade.

## O que mudou (e onde)
- `manuscript/manuscript_src.md` (EN; `manuscript.md` re-renderizado): 2.9 declara a mudança como **pós-dados** (após as
  16 primeiras MDs); 3.9 ganha o parágrafo de química da âncora + [[PENDING]] do controle negativo; 3.11 redefine as camadas;
  4.4 (xi) aponta a decisão; legenda da Fig. 12; nota de rascunho 1 registra a exceção à pré-registro.
- `scripts/rank_final_candidates.py`: A = cumpre QC + delta>0 (+ anel estrito no macrociclo); B = falha um; C = falha dois ou mais;
  P = MD pendente. Ordem interna: delta, confiança E2, ocupância.
- **PT não foi sincronizado** (`manuscript_pt*.md` têm edições suas sem commit). Replicar 2.9, 3.9, 3.11, 4.4 (xi), legenda 12.

## Literatura (verificada no PubMed e Crossref)
| Achado | Fonte |
|---|---|
| Especificidade da tripsina vem do Asp na base de S1; Glu ionizado em P1 é desfavorável, e a ligação observada é da forma protonada (inibe mais em pH baixo) | Brandsdal 2006, Proteins, doi:10.1002/prot.20940 |
| Lys é o P1 cognato (melhor geometria de H-ligação, menores fatores de temperatura); Ka dos 10 variantes P1 de BPTI: 1,5×10⁴ a 1,7×10¹³ M⁻¹ | Helland 1999, J Mol Biol, doi:10.1006/jmbi.1999.2654 |
| 7 mutantes P1 (Gly, Ala, Ser, Val, Leu, Arg, Trp): 7 ordens de grandeza para tripsina; ordem Ala>Gly>Ser>Arg>Val>Leu>Trp | Grzesiak 2000, J Mol Biol, doi:10.1006/jmbi.2000.3935 |

**Inferências**
- Sua hipótese procede e **já está nos nossos dados**: nos 11 complexos de calibração a âncora era sempre Lys/Arg. Quem tem K/R
  chega em S1 se for colocado lá; a ocupância mede a colocação, não a discriminação.
- **Gly/Ala/Ser não servem de controle negativo**: ficaram entre os mais fortes dos testados (Grzesiak 2000). O contraste útil é **ácido (Asp)** e **apolar não cognato (Leu)**.
- Ressalva: dados de BPTI (andaime de 58 resíduos, alça canônica); servem para **escolher** controles, não para prever a
  afinidade de peptídeos de 5–12 resíduos.

## Desenho do controle negativo (não lançado)
- **Quando:** só para candidato cuja ocupância (2ª metade) não seja menor que a da própria isca embaralhada (`ctrl_decoy_occ5_h2`).
  Depende de E3 e dos controles `md-controls` (hoje esperando `delta_paired_{L,M}.json`).
- **O quê:** manter a pose inicial; substituir a âncora por **Asp** (ionizado em pH 10, repelido por Asp189) e por **Leu**.
  Mesmo protocolo de 10 ns (CHARMM36, pH 10).
- **Leitura:** distância âncora–Asp189 e perda da ponte salina; **não** MM-GBSA (não separou inibidor de isca na calibração, 3.3).
- **Risco declarado:** a pose inicial pode sustentar o contato por 10 ns mesmo com Asp. Se nenhuma variante sair de S1 (ou se as iscas
  embaralhadas não se separarem do candidato), o controle não informa nada e é **retirado por completo** das análises, camadas e
  figuras (decisão do usuário, 02/10). O resultado da calibração (iscas 5/5 = 1,00) é dado já obtido e permanece.
- **Custo:** ~75–105 min por MD; 2 variantes × N candidatos. Definir N depois do E3 (≈ 2,5–3,5 h por candidato).

## Pendências abertas
- Camadas finais: recalcular com `rank_final_candidates.py` quando E3 e as 48 MDs terminarem (hoje tudo provisório).
- Sincronizar PT.
- Referências novas já verificadas por mim; você conferirá todas ao fim.

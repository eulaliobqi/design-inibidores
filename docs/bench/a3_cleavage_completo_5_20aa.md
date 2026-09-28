# A3 — filtro de resistência real a protease, faixa completa 5-20aa (2026-09-28)

Reexecução de `scripts/run_cleavage_b23.py` após a campanha A4 (extensão 5-8/18-20aa)
terminar 7/7 sem erro (2026-09-24 18:29) e o P1-âncora geométrico (A2) ser recalculado
sobre o conjunto completo de 770 backbones (11 comprimentos × 10 designs × 7 espécies —
ver commit `e360fd8`). O resultado anterior (825/9.381, 8,8%) cobria só a faixa 8-16aa
(corte parcial, capturado antes da A4 terminar).

## Resultado real (19.227 sequências, 7 espécies)

| Espécie | Sequências | RESISTENTE | MARGINAL | SUSCEPTÍVEL |
|---|---|---|---|---|
| Sfrugiperda | 2.731 | 255 | 641 | 1.835 |
| Slitura | 2.706 | 321 | 614 | 1.771 |
| Onubilalis | 2.739 | 360 | 673 | 1.706 |
| Dsaccharalis | 2.807 | 366 | 685 | 1.756 |
| Cincludens | 2.778 | 333 | 657 | 1.788 |
| Hvirescens | 2.774 | 312 | 614 | 1.848 |
| Pxylostella | 2.692 | 413 | 504 | 1.775 |
| **Total** | **19.227** | **2.360 (12,3%)** | **4.388 (22,8%)** | **12.479 (64,9%)** |

**Melhora real sobre o corte parcial**: taxa de RESISTENTE sobe de 8,8% (só 8-16aa) para
12,3% (5-20aa completo) — consistente com a hipótese de que comprimentos mais curtos
(5-8aa) têm menos sítios K/R internos disponíveis para clivagem, então resistem mais por
construção. Não investigado se o ganho vem majoritariamente dos comprimentos curtos ou é
distribuído — próxima análise (convergência com Trilha B) deve segmentar por comprimento
antes de decidir o corte final.

Saída completa em `outputs/b23_cleavage_analysis.json` no servidor (não versionado, como
o resto de `outputs/`, ver `[[project_plano_v2_generativo]]`).

## Pendências que seguem abertas

Nenhum dos 2.360 candidatos RESISTENTE foi pontuado por afinidade/interação ainda — só
resistência a protease. Próximo passo real é a convergência com a Trilha B (calibração
de ranking de potência, série GORE) para então pontuar com Boltz-2 (+HADDOCK3 de
confirmação) e só depois considerar MD/MM-GBSA robusto (CHARMM36m, 3×100ns) pros
finalistas.

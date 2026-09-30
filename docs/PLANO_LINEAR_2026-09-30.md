# Plano final v3 — duas frentes (linear + macrociclo), MD de triagem de 10 ns (30/09/2026)

**Decisões do autor (30/09):** (1) manter **duas frentes** — peptídeos **lineares** e peptídeos
**macrocíclicos**; (2) usar os insights válidos do V1; (3) **MD de 10 ns** como triagem; o autor roda MD longa
nos melhores; (4) requisito duro: **o peptídeo não pode ser clivado por tripsina nem por proteases de
Lepidoptera**. Nada foi disparado; este arquivo é o plano a executar.

## 1. Requisito duro e sua base na literatura (PubMed, conferido em 30/09)

Critério de sequência (`analyze_cleavage.HARD_P1`, commit “criterio duro”): **nenhum** resíduo
K, R, F, Y, W, L, M, A ou V no interior da cadeia, exceto quando o resíduo seguinte é Pro; no linear, o
resíduo C-terminal também não pode estar nesse conjunto nem ser Ile (carboxipeptidases); no macrociclo não há
extremidades, e o resíduo do fechamento é avaliado como os demais.

| Protease do intestino médio | P1 proibido | Fonte verificada |
|---|---|---|
| Tripsina-like | K, R | Patarroyo-Vargas 2017 (corpus do grupo); Valaitis 1995 [10.1016/0965-1748(94)00033-e](https://doi.org/10.1016/0965-1748(94)00033-e) |
| Quimotripsina-like | F, Y, W, L, M | Valaitis 1999 [10.1016/s0965-1748(99)00017-x](https://doi.org/10.1016/s0965-1748(99)00017-x) (hidrolisa SAAPF/SAAPL-pNA); Yang 2012 (*D. saccharalis*) [10.1111/j.1744-7917.2012.01514.x](https://doi.org/10.1111/j.1744-7917.2012.01514.x); Zhan 2010 (*S. litura*) [10.1002/arch.20353](https://doi.org/10.1002/arch.20353) |
| Elastase-like | A, V (+L, M já incluídos) | Valaitis 1995 (elastase-2-like, substrato Suc-AAPL-pNA); Giri 2003 (*H. armigera* tem tripsina/quimotripsina/elastase-like) [10.1016/s0031-9422(03)00181-x](https://doi.org/10.1016/s0031-9422(03)00181-x) |
| Carboxipeptidases A/B, aminopeptidases | C-terminal livre (linear) | Nakonieczny 2007 [10.1016/j.crvi.2006.12.002](https://doi.org/10.1016/j.crvi.2006.12.002); Simpson 2007 [10.1111/j.1365-2583.2007.00763.x](https://doi.org/10.1111/j.1365-2583.2007.00763.x) |

Limites que o texto declara: o critério é de **motivo** (predição, não medida); a especificidade P1 de cada
enzima de cada espécie não está medida; K/R–Pro e demais exceções de Pro em P1′ são aproximações;
**aminopeptidase N** age em N-terminal livre e não se elimina por sequência (só o macrociclo ou *capping* resolve);
Ile está permitida no interior (sem evidência de P1 para essas enzimas) e há análise de sensibilidade sem Ile.

**Consequência:** o conjunto RESISTENTE cai para **527 (linear; 41–86 por espécie)** e **543 (macrociclo; 41–87)**
de 22.066 (2,4–2,5%). Composição do linear: G 49%, S 12%, P 10%, T 9%, D 6%, I 4%, N 4% (4.060 resíduos) — peptídeos ricos em Gly,
flexíveis, **sem** resíduo favorável ao S1 (K/R aparece em apenas 9 resíduos no total, todos seguidos de Pro). É o custo do critério
e entra como achado/limitação; não há garantia de que tais peptídeos se liguem.

## 2. Insights válidos do V1 (Vina, Rosetta, MD 10 ns, especificidade) e como entram

O V1 orienta o método; seus números **não** entram no manuscrito (RMSD do V1 é artefato de PBC).

| # | Insight | Uso no plano |
|---|---|---|
| I1 | Vina melhora com o comprimento (5 aa −10,3 → 15 aa −13,1); MM-GBSA idem (ρ = −0,93 com área de contato) | Boltz-2 sempre **pareado** com controle embaralhado; nenhum escore comparado entre comprimentos sem controle |
| I2 | Melhor escore ≠ complexo estável (melhor Vina marginal em MD; melhor I_sc instável) | Top-**3** por espécie (não top-1) segue para MD; critério de S1 pré-declarado |
| I3 | Vina reproduzível (DP ≤0,03) mas fora da escada de calibração; travou em ligante grande | **Vina fora da cadeia**; Boltz-2 é o único escore validado (10/10, em pares) |
| I4 | Especificidade real 0/35 aprovados (SI ≥2,0 vs tripsina humana e *Apis*); alguns SI negativo | Nenhuma afirmação de seletividade; contra-triagem **exploratória** (E5) |
| I5 | Âncora real ≠ P1 esperado (Pro, Gln, Glu, Val; muda entre réplicas; VRRPR saía do bolso com RMSD baixo) | Âncora definida empiricamente; cortes 4/5/6 Å; em 10 ns reporta-se também se a âncora muda de identidade entre metades da trajetória |
| I6 | Só VRYRR (Arg) teve salt-bridge constante a 4 Å | O requisito duro exclui esse perfil: declarar na Discussão como troca explícita (resistência × S1 canônico) |
| I7 | Réplicas revelaram o que uma corrida esconde (DP de RMSD, âncora instável) | 10 ns × 1 réplica = **triagem descritiva**; decisão de avançar usa critérios pré-registrados; o autor replica/estende os melhores |
| I8 | Convenções do grupo (`Milena-MD`: CHARMM36 feb2026, pH 8,2, KCl 0,10 M, caixa cúbica 2,0 nm; `GOREs-boltz`: QC de pose pré-registrado, 5 amostras + potentials + sementes) | QC de pose adotado; MD de triagem com o motor do `MDAgent` (idêntico nas duas frentes) e entrega dos melhores no formato do `Milena-MD` para a MD longa do autor |
| I9 | GPU a 98% por jobs do grupo | Tempos ×1,5–2 |

## 3. Metodologia final

| Etapa | Frente L (linear) | Frente M (macrociclo) | Custo* | Estado |
|---|---|---|---|---|
| E0 | filtro duro linear → 527 | filtro duro circular → 543 | feito | `outputs/b23_cleavage_{linear,circular}_hard.json` |
| E1 | Boltz-2 `cyclic:false` (1 amostra) | Boltz-2 `cyclic:true` (1 amostra; refaz 543 — 442 já existiam, serve de **teste de reprodutibilidade** do Boltz-2) | ~2,5 h | script pronto |
| E2 | top-10/espécie (80): 5 amostras × 3 sementes, `--use_potentials` | idem (80) | ~2 h | a construir |
| E3 | 3 controles embaralhados por candidato (Δ pareado) | idem | ~6 h (paralelo à MD) | a construir |
| E4 | QC de pose (clash <2,2 Å, ω trans, quiralidade L, tríade) + matriz cruzada 8×8 do top-1 | idem (+ **fechamento do anel** C–N ≈1,33 Å) | ~0,5 h | a construir |
| E5 | contra-triagem exploratória: top-3 vs receptores não-alvo do V1 (1TRN, *Apis*) e tripsina bovina | idem | ~0,5 h | a construir |
| E6 | **MD 10 ns, top-3 por espécie** (24 sim.), topologia **linear** | **MD 10 ns, top-3 por espécie** (24 sim.), topologia **cíclica** (ligação C–N explícita) | 48 × ~35 min ≈ **28 h** | linear: pronto (ajustar runner); cíclica: **a construir e validar** |
| E7 | análise: ocupância do S1 (4/5/6 Å, por metades), contato com Ser/His, RMSD local com PBC, identidade da âncora | idem + fechamento do anel e ω durante a trajetória | minutos | adaptar |
| E8 | comparação L × M: sobreposição, ρ cíclico×linear, top-3 nos dois braços, ΔS1 | | segundos | script pronto |
| E9 | **Lista de entrega ao autor** para a MD longa: candidatos que cumprem os critérios abaixo, em formato `Milena-MD` (complexo + samplesheet) | | minutos | a construir |

*GPU livre. **Total ≈ 40 h (GPU livre); contar 60–80 h com os jobs do grupo.**

**Topologia cíclica (risco técnico principal):** `pdb2gmx` não fecha o anel. Caminho preferido: `-ter` sem
terminais + `specbond.dat` com a ligação C(n)–N(1) e remoção dos H/OXT terminais, validado num peptídeo-teste (1 ns:
distância C–N, ω trans, sem explosão da dinâmica — a falha do dissulfeto de julho foi exatamente geometria de partida
incompatível); alternativa: `tleap`/`parmed` (AmberTools) com `bond`. A partida é a predição Boltz-2 **cíclica**
(anel já fechado), portanto a geometria é compatível. Se a validação falhar, a frente M fica só com E0–E5 e a MD
cíclica vai para pendência declarada.

**Critérios pré-registrados para entrar na lista de MD longa (E9):** (a) RESISTENTE pelo critério duro; (b) QC de
pose aprovado; (c) ocupância do S1 ≥70% a 5 Å na **segunda metade** dos 10 ns; (d) âncora com a mesma identidade nas
duas metades; (e) Δ pareado (E3) > 0; (f) no macrociclo, anel íntegro (C–N ≤1,5 Å e ω ≥150° em toda a trajetória).
Se nenhum candidato cumprir (c)–(d) numa espécie, a espécie é reportada como “sem candidato ancorado em 10 ns”.
Nenhum limiar é alterado depois de ver os dados (emendas ficam neste arquivo).

**Seleção:** os top-3 por espécie/frente são pela maior confiança média do Boltz-2 (E2) entre os RESISTENTE; E3 só
interpreta.

## 4. Escrita do manuscrito (em paralelo)

Título/Abstract: “linear and macrocyclic peptides” (duas frentes, comparação como resultado). Introdução: grupo (GORE),
tensão P1 básico × clivagem, e o requisito de não-clivabilidade por proteases de Lepidoptera (tabela da seção 1).
Métodos 2.6: critério duro e suas exceções; 2.7: Boltz-2 nas duas modalidades; 2.8–2.9: MD de triagem 10 ns, topologias
linear e cíclica, análise. Resultados: composição do conjunto resistente (Gly-rico), Boltz-2, QC, MD 10 ns por frente,
comparação L × M. Discussão: custo do critério duro, flexibilidade, aminopeptidases/*capping*, o que a MD de 10 ns não
permite concluir. Figuras 1 e 3 recalculadas; versão PT; referências novas conferidas (PubMed: as sete acima; RAG do
grupo: Saikhedkar 2019, Kelly 2005, Schultz 2026, Paulo 2026, Severi-Castro 2026 ainda a conferir no Crossref).

## 5. Decisões pendentes

1. **Ile** no interior: permitida (**padrão**; 527/543) ou proibida (393 linear)?
2. pH do MD de triagem: **8,2** (grupo; recomendado) ou 10,0 (texto atual do manuscrito)?
3. Extremidades do linear: **carregadas** (recomendado; como nos ensaios do grupo) ou acetil/amida?
4. Topologia cíclica: aprovar o caminho `specbond` (com fallback `tleap`)?
5. Manter E5 (contra-triagem) como exploratória? **Sim** (recomendado).
6. Disparar já a E1 das duas frentes (~2,5 h, independe do resto)? **Sim.**

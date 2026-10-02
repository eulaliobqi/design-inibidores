# Plano de análises corrigido — 01/10/2026

Substitui a parte analítica do plano v3 **sem mexer em nenhum limiar pré-registrado**. A correção foi forçada por um
resultado dos controles, não por preferência.

## 1. O que mudou e por quê

A triagem usava "ocupância de S1 ≥ 70% a 5 Å na 2ª metade, com a mesma âncora nas duas metades" como critério
central, e o ranqueamento ordenava os candidatos por essa ocupância. **Faltava a escala**: ninguém sabia quanto um
inibidor real marca na mesma análise.

Aplicando a análise idêntica aos 11 complexos da calibração (mesmo receptor de *S. frugiperda*; 6 inibidores
naturais e 5 iscas embaralhadas):

| | ocupância de S1 a 5 Å, 2ª metade | âncora |
|---|---|---|
| Inibidores reais (n = 6) | 1,00 em quatro; 0,00 (ApTI) e 0,10 (BBI) | Lys ou Arg nos seis |
| Iscas embaralhadas (n = 5) | **1,00 nas cinco** | Lys ou Arg nas cinco |

**Conclusão: no único conjunto de referência disponível, o critério não tem especificidade** — sensibilidade 4/6,
especificidade 0/5. Qualquer sequência com um resíduo básico que alcance S1 satisfaz o critério.

Ressalvas (declaradas junto com o resultado): protocolo diferente (2 ns, AMBER99SB-ILDN, outro pH) e inibidores
**proteicos** de 50–180 resíduos, cujos embaralhamentos mantêm necessariamente Arg/Lys — enquanto os candidatos
têm 5–12 resíduos e quase nenhum tem K/R. Por isso o resultado **limita a interpretação**, mas não substitui o
controle pareado por tamanho, que está em execução.

## 2. O que a MD passa a significar

| Antes (implícito) | Agora (explícito) |
|---|---|
| Passar na triagem ≈ indício de ligação | Passar na triagem = **a pose prevista não se desfez em 10 ns**. Nada além disso. |
| Ocupância alta distingue bons candidatos | Ocupância alta é **necessária, não suficiente**: uma isca a atinge. |
| MD ordena os candidatos | MD **filtra** (9 dos 12 simulados falharam, então filtra de fato) e **não ordena**. |

Isso é coerente com a decisão do autor de que as MDs servem para verificar estabilidade, e com o fato de haver uma
réplica por candidato (trajetórias únicas geram falso-positivos: Knapp, Ospina e Deane 2018,
[10.1021/acs.jctc.8b00391](https://doi.org/10.1021/acs.jctc.8b00391)).

## 3. Análises mantidas, acrescentadas e removidas

**Mantidas, sem alteração de limiar:** ocupância de S1 a 4/5/6 Å por metades; identidade da âncora nas duas
metades; contato com Ser195/His57; RMSD local do peptídeo; integridade do anel (C–N ≤ 1,5 Å e ω ≥ 150° em todos os
quadros) com a fração de quadros ≥ 150° como descrição secundária; QC de pose; Δ pareado do E3.

**Acrescentadas:**
1. **Escala de referência** (`analyze_md_controls.py`): a análise dos inibidores e iscas da calibração, relatada
   junto do critério, para o leitor ver o que ele separa e o que não separa. **Feito.**
2. **Controle negativo pareado por tamanho** (`run_md_controls.py` / `run_md_controls.sh`, `screen md-controls`):
   para os candidatos que passaram, roda 10 ns no **próprio controle embaralhado** daquele candidato, usando a
   predição que o E3 já gera — sem custo extra de Boltz-2. É o teste decisivo: se a isca do NGGRPDAP também ficar
   em S1, a ocupância não sustenta afirmação de ligação para ele. **Na fila, espera o E3.**
3. **Tamanho de efeito do Δ (E3)**: relatar Δ dividido pela dispersão, já que o desvio-padrão interno de um
   candidato no E2 é ≈ 0,02 e um Δ de +0,005 é ruído. O critério pré-registrado "Δ > 0" **continua** como está.
4. **Identidade candidato × isca** no E3, por candidato (medida: média 0,35 L / 0,29 M; 5 candidatos ≥ 60%;
   6 com só 2 controles distintos), para que o leitor saiba onde o controle é fraco.

**Removidas / rebaixadas:**
5. **A ocupância deixa de ser o critério de ordenação.** No ranqueamento, as camadas A/B/C/P continuam (são
   filtros declarados), mas a leitura passa a ser "sobreviveu aos filtros disponíveis", e a coluna do **controle
   da própria isca** entra como evidência decisiva quando existir.
6. **Nenhuma afirmação de ligação ou de potência** a partir de MD de 10 ns, em nenhuma seção.

**Não serão feitas** (decisão do autor, prazo curto): réplicas; MM-GBSA nesta rodada (a calibração já mostrou
4/10); contra-triagem de seletividade (E5 não construída) — e, portanto, nenhuma afirmação de seletividade.

## 4. Ordem de execução
1. Pipeline termina o E6 → E7 → **E3** → matriz 8 × 8 → E8/E9. *(em curso; 40–56 h + 15–20 h)*
2. `screen md-controls` dispara assim que o E3 grava `delta_paired_{L,M}.json`: 5 controles de 10 ns
   (3 na frente L, 2 na M), priorizando os candidatos que passaram. *(na fila; 6–9 h)*
3. Ranqueamento final com a coluna de controle; figuras; texto.

**Campanha de pH: cancelada neste artigo** (01/10) — 72 simulações e 4–5 dias não cabem no prazo, e ela é um
refinamento de método, não o resultado central. Fica para o artigo seguinte, com os scripts prontos. Com isso, os
controles pareados deixam de competir por GPU e são a única etapa além do pipeline.

## 5. Efeito sobre o que já está escrito
- Seção 3.9: ganhou o parágrafo da escala de referência (EN e PT).
- Seção 4.4: ganhou as limitações (ix) a (xiv) — especificidade do critério, âncora post hoc, confundimento da pose
  inicial, fraqueza dos controles em sequências ricas em Gly, ausência de limiar no Δ, e os dois desvios de
  protocolo medidos.
- Seção 3.12 e Resumo: a entrega continua sendo uma **lista priorizada para teste experimental**; falta ajustar a
  frase final quando os controles pareados voltarem.

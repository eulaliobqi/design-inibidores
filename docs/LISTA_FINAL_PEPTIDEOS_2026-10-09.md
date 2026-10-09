# Lista final de peptídeos recomendados — 09/10/2026

Responde a três perguntas: (1) quais peptídeos recomendar e por quê, mostrando o conjunto de filtros que cada um passou; (2) qual é o embasamento científico de que não serão clivados — a regra de ouro: *peptídeo digerido vira aminoácido e deixa de ser inibidor*; (3) se a metodologia do projeto atende ao objetivo.

Todos os números vêm de `data-e2-results/` e foram conferidos nesta data.

---

## 1. A regra de decisão (e por que não é o ranking agregado)

O ranking agregado da Figura 6B **não pode** ser usado para escolher a lista final. Medi a correlação entre o posto agregado e a ocupância média de S1 nos dois pH:

| frente | n | ρ de Spearman (posto agregado × ocupância de S1) | P |
|---|---|---|---|
| linear | 23 | −0,04 | 0,84 |
| macrociclo | 10 | −0,18 | 0,62 |

Ou seja: **zero**. O caso extremo prova o ponto nos dois sentidos — SGSTDIE é o 1.º colocado agregado da frente M e tem ocupância 0,06 (pH 10) e 0,00 (pH 8,2); GQNDS linear é o **23.º de 23** da frente L e tem ocupância 1,00 em pH 10. Isso é esperado, não é um defeito do cálculo: três das seis etapas do agregado são MM-GBSA e PRODIGY, e a calibração já havia mostrado que esses dois escores medem tamanho de interface (ρ = −0,93 e −0,79 com o número de contatos) e separam inibidor de isca em apenas 4/10 e 2/10 dos pares.

Então a lista final é construída pelo **único observável que sobreviveu ao piso de ruído medido**: manter a âncora em S1 em execuções independentes. A cascata de filtros é esta:

| # | filtro | o que testa | sobrevivem |
|---|---|---|---|
| F1 | regra dura de não clivabilidade | nenhum P1 de tripsina/quimotripsina/elastase (exceção K/R–Pro) | 527 L + 543 M de 22.066 |
| F2 | QC de pose do Boltz-2 | geometria do complexo inicial válida | 48 de 48 |
| F3 | Δ pareado > 0 (E3) | não pontua abaixo dos próprios controles embaralhados | 45 de 48 |
| F4 | ocupância de S1 ≥ 0,70 em pH 10,0 | âncora fica no bolso S1 | **5** |
| F5 | ocupância de S1 ≥ 0,70 em pH 8,2 (pH do ensaio) | idem, no pH em que o Ki é medido | **6** |
| F4∧F5 | nos **dois** pH | não é artefato de uma condição | **2** |
| F6 | repetição com outra semente mantém ≥ 0,70 | acima do piso de ruído (3 de 16 pares viram a ocupância em > 0,5) | **2** |
| F7 | P1 canônico (K/R na S1) | mecanismo dos inibidores canônicos | 2 dos 2 |
| F8 | K/R seguido de Pro | única configuração que satisfaz F1 e F7 ao mesmo tempo | 2 dos 2 |
| F9 | rota exopeptidásica fechada (sem extremidades livres) | imunidade estrutural a amino/carboxipeptidases | **1** |
| F11 | ligação cindível K/R–Pro sem conformação quase de ataque | a Ser195 não se posiciona para atacar o sítio | 2 dos 2 |

A cascata F1→F6 converge para **exatamente dois peptídeos**, e eles são os mesmos dois que carregam o mecanismo canônico. Não houve ajuste do critério para chegar a esse número.

---

## 2. Lista recomendada

### Nível 1 — sintetizar e ensaiar (2 peptídeos)

#### 1.º — **GGKPGEP** · macrociclo cabeça-cauda · *A. gemmatalis* · 7 resíduos · âncora Lys3

Conjunto de características que o colocam em primeiro:

| filtro | resultado |
|---|---|
| F1 não clivável (regra dura) | passa; único resíduo básico é Lys3, protegido por Pro4 |
| F2 QC de pose | passa |
| F3 Δ pareado (E3) | +0,020 (positivo) |
| F4 ocupância S1 pH 10,0 | **1,00** e **1,00** (duas execuções) |
| F5 ocupância S1 pH 8,2 | **1,00** e **1,00** (duas execuções) |
| F6 reprodutibilidade | **4 de 4 execuções com 1,00** — o único assim em 48 |
| F7 P1 canônico | **Lys** na S1 |
| F8 K/R–Pro | **Lys3–Pro4** |
| F9 exopeptidases | **fechada por construção** — macrociclo, sem N nem C livre |
| F10 anel íntegro | C–N ≤ 1,46 Å sempre; ω ≥ 150° em 99,6% dos quadros (mínimo 144,5° em pH 10; 156,7° em pH 8,2) |
| F11 geometria de ataque | **nenhuma conformação quase de ataque** na Lys3–Pro4 em nenhuma das 4 execuções; Ser195 Oγ–C mediana 5,3–5,4 Å (pH 10) e **6,7–7,6 Å (pH 8,2)** |
| — distância final âncora–Asp189 | **2,71 Å — a menor das 48** |
| — MM-GBSA | −35,4 (pH 10) / −27,7 (pH 8,2) kcal/mol |

#### 2.º — **NGGRPDAP** · linear · *A. gemmatalis* · 8 resíduos · âncora Arg4

| filtro | resultado |
|---|---|
| F1 não clivável (regra dura) | passa; único básico é Arg4, protegido por Pro5 |
| F2 QC de pose | passa |
| F3 Δ pareado (E3) | +0,030 |
| F4 ocupância S1 pH 10,0 | **1,00** e **1,00** |
| F5 ocupância S1 pH 8,2 | **0,98** e **1,00** |
| F6 reprodutibilidade | **4 de 4 execuções ≥ 0,98** |
| F7 P1 canônico | **Arg** na S1 |
| F8 K/R–Pro | **Arg4–Pro5** |
| F9 exopeptidases | **ABERTA** — N-terminal e C-terminal livres (ver §3) |
| F11 geometria de ataque | sem conformação quase de ataque na Arg4–Pro5 (mediana 4,7–5,5 Å; mínimo 4,2 Å); **1 execução de 4 com 1,6% de quadros quase de ataque na ligação Gly3–Arg4**, que não é sítio de tripsina |
| — ranking agregado | **1.º da frente linear** (posto médio 6,7 de 23) |
| — MM-GBSA pH 8,2 | **−53,25 kcal/mol — o mais favorável das 48** |

**Por que GGKPGEP passou NGGRPDAP.** Os dois empatam em tudo que diz respeito à ligação. O desempate é o filtro F9, que é exatamente a regra de ouro: o macrociclo não tem extremidades livres e, por construção, não é substrato de aminopeptidases nem de carboxipeptidases; o linear é. Some-se que a ligação cindível de GGKPGEP fica ~2 Å mais longe da Ser195 que a de NGGRPDAP no pH do ensaio (6,7–7,6 Å contra 4,7–5,5 Å). Pelo critério de não ser digerido, o macrociclo é a aposta melhor.

### Nível 2 — uma réplica antes de decidir (2 peptídeos, ~6 MDs)

- **PISQIDSGSR** (macrociclo, *C. includens*, 10 res., âncora Arg10). O terceiro e último candidato com K/R. Ocupância 1,00 em pH 8,2 e 0,33 em pH 10, **sem execução repetida**; MM-GBSA −65,0 em pH 10, o mais favorável das 48. A ligação Arg10–Pro1 fica a 9,2–9,5 Å da Ser195, a mais distante dos três. Merece 2 repetições por pH antes de qualquer síntese.
- **GGHSE** (macrociclo, *S. frugiperda*, 5 res., âncora His3). Melhor candidato **sem** resíduo básico: 0,99 e 1,00 em pH 10 (reproduziu), 0,00 e 0,88 em pH 8,2 (não reproduziu). É o teste da pergunta mais interessante do conjunto — se a His substitui K/R na S1 —, porque a His é o único resíduo quase básico que a regra de não clivabilidade permite.

### Não recomendados (e uma correção ao manuscrito)

- **GQNDS linear** está hoje na Tabela 4 e **deve sair da lista de recomendados**: é o 23.º de 23 no agregado da frente linear, tem o **pior MM-GBSA das 48 em pH 8,2 (−1,98 kcal/mol)**, perdeu S1 em pH 8,2 (0,04; a repetição deu 0,72) e sua âncora é Gln, que não é P1 canônico. Vale manter no texto como caso ilustrativo de que a ocupância em um pH não se sustenta, não como recomendação.
- **SGSTDIE** é 1.º no agregado e tem ocupância 0,00–0,06. É a melhor ilustração de que o agregado não mede engajamento de S1.
- **Atenção editorial:** GQNDS aparece nas duas frentes. A Figura 6B lista "GQNDS (M)" no posto 2 (ocupância 0,00 nos dois pH) e a Tabela 4 lista "GQNDS linear" (ocupância 1,00 em pH 10). São moléculas diferentes e o leitor vai confundir. Sugiro renomear para GQNDS-L e GQNDS-M no texto e nas figuras.

---

## 3. A regra de ouro: há base para afirmar que não serão clivados?

**Resposta direta: não, ainda não.** O que existe hoje é uma regra de motivo e uma geometria de MD sem linha de base. Nenhuma medida de proteólise foi feita. Abaixo, o que a literatura sustenta rota por rota.

### Rota 1 — endopeptidases (tripsina, quimotripsina, elastase): coberta, mas não garantida

A regra dura remove todos os P1 dessas três classes. A exceção K/R–Pro é o ponto frágil e a literatura é explícita: a tripsina **corta** antes de prolina, em frequência baixa mas documentada em grandes conjuntos de espectros de peptídeos (Rodriguez et al. 2008), e a prolina torna a hidrólise **mais lenta, não ausente** (Pan et al. 2014). Portanto K/R–Pro é barreira estatística, não absoluta.

O que nossas MDs acrescentam: em 4 execuções de cada um, a ligação cindível **nunca** atingiu conformação quase de ataque, e a Ser195 Oγ ficou a 4,2–7,6 Å do carbono da carbonila. É sustentação real, mas fraca por dois motivos: os limiares não foram calibrados contra um substrato conhecido, e 10 ns não amostram um evento catalítico.

### Rota 2 — exopeptidases: **descoberta para o peptídeo linear**. É aqui que o argumento quebra

O intestino médio de lepidópteros tem **aminopeptidases e carboxipeptidases abundantes**, além das endopeptidases (Srinivasan et al. 2006; Ajamhassani et al. 2012 mediram as duas atividades em intestino de lepidóptero; Valaitis 1995, Valaitis et al. 1999 e Nakonieczny et al. 2007 já estão citados no manuscrito). A aminopeptidase N é uma das proteínas mais abundantes da membrana em escova do intestino médio de lepidópteros — é justamente por isso que ela é o receptor mais estudado das toxinas Cry de *B. thuringiensis* (Pigott e Ellar 2007).

A aminopeptidase remove resíduos **sequencialmente a partir de um N-terminal livre**, e sua especificidade é ampla. Isso significa que:

> **Um peptídeo linear com N-terminal livre é substrato de aminopeptidase independentemente da sua sequência interna.** A regra dura do projeto avaliou apenas o resíduo C-terminal (carboxipeptidase) e **não trata a aminopeptidase** — o próprio manuscrito admite isso na Seção 2.4 e em 4.3.

Consequência prática: **NGGRPDAP, como peptídeo linear livre, tem expectativa de ser degradado a partir do N-terminal no intestino**, e o N-terminal Asn-Gly-Gly não oferece nenhuma proteção. Nenhum dos filtros atuais vê esse risco.

A ciclização cabeça-cauda fecha essa rota **por construção**, não por predição: sem α-amino e sem α-carboxila livres, não há substrato para amino nem para carboxipeptidase. É o argumento estrutural mais forte disponível, e é por isso que GGKPGEP passou à frente. Experimentalmente, a ciclização de esqueleto aumenta a estabilidade proteolítica de peptídeos curtos (Gunasekera et al. 2020, com dímeros cíclicos de KR-12).

### Rota 3 — o paradoxo do inibidor canônico: o problema mais profundo

Esta é a objeção que um revisor competente vai levantar, e ela é mecanística, não de detalhe.

Inibidores de mecanismo canônico (Laskowski) **ligam-se na orientação de substrato e são hidrolisados** na ligação do sítio reativo — só que devagar, e a forma clivada se religa, estabelecendo um equilíbrio (Song e Markley 2003 mediram a constante de hidrólise; Karna et al. 2015 mostraram a tripsina clivando **e refazendo** a ligação Lys–Ser de análogos de SFTI-1). Ser substrato, portanto, não é o mesmo que ser digerido.

O que converte um substrato em inibidor é o **arcabouço**: ele mantém a alça reativa na conformação canônica, melhora a ligação em cerca de seis ordens de grandeza e protege contra a proteólise (Kelly, Laskowski e Qasim 2005). E o determinante direto da velocidade de hidrólise é a **mobilidade**: em simulações QM/MM de SFTI-1 e análogos, a taxa de hidrólise cresce com a mobilidade do inibidor, enquanto o esqueleto cíclico e as pontes de hidrogênio intramoleculares a reduzem (Wei et al. 2019).

Aplicando ao nosso conjunto: os candidatos têm 5–8 resíduos, **nenhuma cisteína, nenhum dissulfeto, e 49% de glicina** — o resíduo mais flexível. Falta exatamente o arcabouço que faz um inibidor canônico não ser consumido. Por esse mecanismo, a expectativa teórica é que se comportem mais como substratos do que como inibidores. É a crítica mais séria ao desenho atual, e vale com mais força para a frente linear.

**Contraponto real, a favor:** tripeptídeos derivados de alças de inibidores Pin-II inibiram proteases de *H. armigera* e os autores relatam **retenção prolongada e alta estabilidade no intestino do inseto** (Saikhedkar et al. 2018); peptídeos bicíclicos das mesmas alças foram dez vezes mais potentes que os lineares (Saikhedkar et al. 2019). Ou seja: peptídeos curtos **podem** persistir no intestino de lepidóptero. Isso não transfere automaticamente para nossas sequências, mas mostra que a hipótese não está morta — está por medir.

### O que decide a questão (e o grupo já sabe fazer)

Um **ensaio de estabilidade**, que é barato e definitivo:

1. Incubar cada peptídeo com (a) tripsinas purificadas de *A. gemmatalis* e (b) extrato bruto de intestino médio, em pH 8,2 e pH 10,0, 30 °C.
2. Amostrar em 0, 15, 30, 60, 120 e 240 min; quantificar o peptídeo íntegro por RP-HPLC ou LC-MS; ajustar a meia-vida.
3. Controles: **positivo de resistência** — SFTI-1 ou um peptídeo cíclico rico em dissulfeto (os ICK de aranha resistem a tripsina, quimotripsina, elastase e pepsina, Kikuchi et al. 2015); **negativo** — o mesmo peptídeo com um K ou R interno desprotegido.
4. O grupo já executou um desenho equivalente: o "ensaio de persistência da inibição" de de Almeida Barros et al. (2022b).

A comparação **GGKPGEP (cíclico) × NGGRPDAP (linear)** nesse ensaio é, por si só, um resultado publicável: mede diretamente quanto a ciclização cabeça-cauda protege contra o intestino de uma praga real.

### Enquanto o ensaio não existe, o que se pode afirmar no artigo

Pode-se afirmar: *as sequências não contêm P1 de tripsina, quimotripsina ou elastase desprotegido; o único resíduo básico é seguido de prolina; e, nas simulações, a ligação cindível não assumiu geometria de ataque.*

**Não** se pode afirmar: que resistem à proteólise, que não são digeridos, ou que o critério de não clivabilidade foi verificado. O manuscrito hoje está correto nesse ponto — convém não afrouxar.

---

## 4. A metodologia atende ao objetivo?

Objetivo: peptídeos curtos *de novo* que **inibam** tripsinas digestivas de lagartas-praga da soja, **resistam** às proteases do intestino e sejam **específicos** para as pragas-alvo (prioridade permanente do projeto).

**Atende bem:** definição do alvo e transferência de subsítios (TM 0,946–0,957, todos os subsítios transferidos, Asp189 confirmado por estrutura e por sequência); não clivabilidade como restrição binária de desenho (contribuição genuína); e a calibração honesta da escada de escores, com o resultado negativo reportado — é o ponto metodológico mais forte do trabalho.

**Não atende, em ordem de gravidade:**

**(1) Especificidade está ausente do pipeline.** É a prioridade permanente do projeto e não existe nenhuma contrasseleção. A matriz cruzada 8 × 8 contém **só as 8 pragas-alvo** — conferi: nenhuma protease não alvo foi pontuada em etapa alguma. Como a S1 (Asp189) é conservada entre tripsinas, um peptídeo ancorado ali não tem razão para poupar tripsina humana, bovina ou de polinizadores. Fases anteriores do projeto já deram 0/21–23 aprovados em especificidade real.
→ **Sugestão:** transformar a contrasseleção em portão, não em checagem post hoc. Incluir tripsina humana (PRSS1, P07477), tripsina bovina e ao menos uma protease de inseto benéfico em **todas** as etapas, e definir o índice de seletividade como o Δ pareado contra o não alvo no protocolo idêntico. É a correção mais barata com o maior efeito sobre a aplicabilidade.

**(2) Os dois objetivos foram postos em oposição na geração, em vez de satisfeitos juntos.** A regra proíbe K/R e só os tolera antes de Pro; o resultado foram 9 resíduos básicos em 4.060 (0,22%) e 3 finalistas de 48 com K/R — e esses 3 são exatamente os que engajam a S1. O espaço de busca foi quase esvaziado do motivo que liga.
→ **Sugestão:** inverter a restrição — **exigir** P1 = Lys/Arg e P1' = Pro por construção (fixando essas duas posições no ProteinMPNN e nos hotspots do RFdiffusion) e deixar o desenho otimizar o resto. A busca passa a ocorrer inteiramente dentro da região onde os dois objetivos valem.

**(3) Falta controle positivo na escala certa.** A calibração usa BPTI, SFTI-1, SKTI, BBI e EcTI (14–176 resíduos, inibidores nM–pM), mas o comparador real é um tripeptídeo de 0,1–1,8 mM (GORE1/2, GORE3–5, tripeptídeos Pin-II). A escada nunca foi testada contra um **peptídeo milimolar**.
→ **Sugestão (maior retorno por esforço):** passar GORE2 — e idealmente GORE5 e SKTI — pela escada inteira: Boltz-2 E2/E3, MD de 10 ns nos dois pH, MM-GBSA e PRODIGY. Custo ~6 MDs. Ganho: todo candidato passa a ter escala ("pontua acima/abaixo de um inibidor milimolar conhecido no protocolo idêntico"), que é precisamente o que o artigo hoje não consegue dizer, e responde à pergunta que o revisor fará — *isto é melhor do que o que vocês já publicaram?*

**(4) O ranking agregado não mede o que se usa dele.** ρ ≈ 0 com a ocupância de S1 (§1).
→ **Sugestão:** tirar o agregado do caminho de seleção (mantê-lo como figura descritiva) ou reconstruí-lo só com as etapas de discriminação demonstrada (Δ pareado e ocupância reproduzida). Do jeito que está, o "posto 1" da Figura 6B é um passivo.

**(5) Um portão binário sobre um observável contínuo e ruidoso descartou o melhor candidato.** O critério estrito do anel (ω ≥ 150° em **todos** os quadros) excluiu 12 de 24 macrociclos cujo ω esteve ≥ 150° em 91,8–99,8% dos quadros — **incluindo GGKPGEP**, o único com ocupância 1,00 nas quatro execuções, reprovado por 0,4% dos quadros. Por isso ele nem aparece na Figura 6B.
→ **Sugestão:** trocar por um critério de fração declarado de antemão (ω ≥ 150° em ≥ 99% dos quadros) e reportar a fração; ou tratar a integridade do anel como descritor, como já se fez com a ocupância.

**(6) Resistência proteolítica nunca é medida, só afirmada por regra.** A geometria de ataque (08/10) é a ideia certa, mas sem linha de base.
→ **Sugestão:** rodar a mesma análise em SFTI-1 com tripsina bovina (1SFI) e num peptídeo controle clivável. Dois números transformam "1 de 20 execuções teve quadro quase de ataque" em algo interpretável. E acrescentar a rota exopeptidásica à regra: um peptídeo linear só é "resistente" se o N-terminal estiver bloqueado (Pro na posição 2, acetilação, ou D-aminoácido na posição 1).

**(7) 10 ns × 1 execução é triagem, não seleção.** As repetições viraram a ocupância em > 0,5 em 3 de 16 pares.
→ **Sugestão:** só para os 2–4 recomendados, n = 3 × 100 ns em pH 8,2; o protocolo já está validado em `eulalio-pos-doc`.

**Prioridade, se o tempo for curto:** (3) controle positivo GORE2 → (1) contrasseleção → (7) réplicas da lista curta. Os dois primeiros tornam a lista defensável; o terceiro a torna publicável como recomendação.

---

## 5. Correção química que resolveria a rota 2 sem redesenhar nada

Se os autores quiserem manter **NGGRPDAP** na lista apesar da rota exopeptidásica aberta, há três correções padrão e baratas, aplicáveis na síntese:

1. **N-acetilação + C-amidação** — remove as cargas terminais que amino e carboxipeptidases reconhecem; é a modificação mais comum e não muda a sequência.
2. **D-aminoácido na posição 1** (ou na última) — exopeptidases não processam resíduos D.
3. **Ciclização cabeça-cauda** — é o que GGKPGEP já é.

Qualquer uma delas deveria entrar no desenho **antes** da síntese, e a versão modificada precisa ser re-simulada, porque acetilação e amidação alteram as cargas terminais que hoje estão no modelo.

---

## Referências novas usadas aqui (DOI conferido no Crossref em 09/10/2026)

| chave | referência | para quê |
|---|---|---|
| Srinivasan et al. 2006 | Cell Mol Biol Lett 11. doi: 10.2478/s11658-006-0012-8 | diversidade de serina proteases digestivas de lepidópteros |
| Ajamhassani et al. 2012 | J Plant Prot Res 52. doi: 10.2478/v10045-012-0061-0 | mediu aminopeptidase **e** carboxipeptidase em intestino de lepidóptero |
| Pigott e Ellar 2007 | Microbiol Mol Biol Rev 71. doi: 10.1128/mmbr.00034-06 | abundância da aminopeptidase N na membrana em escova |
| Gunasekera et al. 2020 | Front Microbiol 11. doi: 10.3389/fmicb.2020.00168 | ciclização de esqueleto aumenta estabilidade proteolítica (experimental) |
| Kikuchi et al. 2015 | Int J Pept 2015. doi: 10.1155/2015/537508 | controle positivo de resistência: ICK resistem a tripsina, quimotripsina, elastase e pepsina |

Já estavam na lista do manuscrito e sustentam o §3: Rodriguez et al. 2008, Pan et al. 2014 (K/R–Pro não é barreira absoluta); Song e Markley 2003, Karna et al. 2015 (inibidor canônico é clivado e religado, em equilíbrio); Kelly, Laskowski e Qasim 2005 (papel do arcabouço, ~6 ordens de grandeza); Wei et al. 2019 (mobilidade ↔ taxa de hidrólise); Saikhedkar et al. 2018, 2019 (tripeptídeos e bicíclicos de alça Pin-II no intestino de *H. armigera*); de Almeida Barros et al. 2022b (ensaio de persistência da inibição); Valaitis 1995, Valaitis et al. 1999, Nakonieczny et al. 2007 (exopeptidases do intestino médio).

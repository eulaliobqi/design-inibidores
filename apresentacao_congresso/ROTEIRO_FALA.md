# Roteiro de fala — 10 minutos

Arquivo: `Apresentacao_congresso_10min.pptx` (15 slides). As mesmas notas estão no painel de anotações de cada slide no PowerPoint.

**Orçamento: 600 s.** O roteiro abaixo soma 590 s de fala e deixa 10 s de folga. Se o relógio apertar, **corte o slide 3 e depois o 10** — nenhum dos dois quebra o arco.

| # | s | acum. | O que dizer |
|---|---|---|---|
| 1 | 15 | 0:15 | "Vou contar como saímos de uma enzima do intestino de uma lagarta até peptídeos candidatos ordenados — e, principalmente, o que cada número desse caminho sustenta e o que não sustenta." |
| 2 | 40 | 0:55 | **E.** O Brasil colheu 180,4 milhões de toneladas de soja, a maior safra da série da Conab, e metade da soja do mundo sai da América do Sul. A lagarta-da-soja está entre os principais desfolhadores das Américas; em alta infestação a desfolha pode ser total. *Não citar número de perda: a literatura consultada não dá um valor único para esta espécie.* |
| 3 | 35 | 1:30 | **E.** O controle se apoia em inseticida e em soja Bt. O inseticida afeta não alvo e seleciona resistência; o Bt é de alta dose para esta espécie, mas depende de refúgio e de plano de manejo. *Dizer explicitamente: não estou afirmando que a lagarta já é resistente ao Cry1Ac — estou dizendo que as duas táticas carregam custo de manejo.* Inibidores de protease são a terceira via. |
| 4 | 45 | 2:15 | **E.** A digestão da lagarta roda num intestino com pH perto de 10, o maior pH luminal conhecido em um sistema biológico, e depende de tripsinas. Para leigos: a tripsina corta a proteína sempre depois de uma **lisina** ou de uma **arginina**, porque o bolso S1 tem um aspartato negativo no fundo que atrai essas duas cadeias laterais positivas. **Guardem esse fato.** |
| 5 | 35 | 2:50 | **MAS.** Inibidores naturais de protease funcionam, mas são proteínas de 14 a 176 resíduos. Os peptídeos curtos já medidos contra essas tripsinas chegam só a potência milimolar — o GORE2, 0,10 mM. Isso é fraco, e é onde cabe um desenho melhor. |
| 6 | 45 | 3:35 | **MAS — o nó.** Para inibir, o peptídeo precisa de lisina ou arginina no bolso S1. Mas lisina e arginina são exatamente onde a tripsina corta. Resistir à digestão e ancorar no alvo puxam em sentidos opostos — e um peptídeo clivado no intestino nunca chega ao alvo. **Pausa aqui.** |
| 7 | 55 | 4:30 | **PORTANTO — a virada e a mensagem da palestra.** Montamos uma plataforma de seis etapas: alvo, calibração, geração, critério duro, simulação, classificação. Uma linha por etapa. Frisar duas coisas: a mesma plataforma roda para as oito espécies ao mesmo tempo, e **cada etapa é calibrada antes de ser usada**. |
| 8 | 45 | 5:15 | **Etapa 2.** O Boltz-2 é uma rede neural que prediz o complexo e devolve uma confiança — não uma afinidade. Antes de confiar nela, comparamos seis inibidores reais com iscas embaralhadas: o inibidor real ganhou em 10 de 10 pares. Mas as faixas absolutas se sobrepõem — uma isca embaralhada chegou a 0,944. Por isso, daqui em diante, cada candidato é comparado com controles pareados contra o mesmo receptor, e nunca lemos "confiança 0,9" como "liga". |
| 9 | 45 | 6:00 | **Etapas 3 e 4.** O RFdiffusion desenhou 880 esqueletos, o ProteinMPNN escreveu as sequências — 22.066 — e o critério duro removeu todas que têm um resíduo que as proteases do intestino cortam. Sobram 527 lineares e 543 cíclicas. **O número que fica: 97,6% do que a IA desenhou cai por uma regra biológica, não por um escore.** |
| 10 | 35 | 6:35 | O preço do filtro: sobram peptídeos de 7,7 resíduos em média, com 49,4% de glicina. É consequência direta do nó do slide 6 — proibir os resíduos que a enzima corta é proibir justamente os que ancoram melhor. |
| 11 | 45 | 7:20 | **Etapa 5.** 48 complexos, 10 ns, dois pH. O resultado mais importante é sobre a própria plataforma: quem fica no bolso é quem **já começou dentro dele** — 5 de 9 que partiram a até 4 Å contra 0 de 39 mais distantes. A simulação de 10 ns verifica se uma pose sobrevive; ela não dá tempo de o peptídeo achar o bolso. Por isso a ocupância deixou de ser critério e virou descrição. |
| 12 | 40 | 8:00 | O intestino é alcalino, mas o ensaio enzimático roda em pH 8,2, então o candidato precisa funcionar na faixa inteira. Entre os dois pH não há diferença em nenhum teste pareado. E tem um ponto delicado: repetir a **mesma** simulação no **mesmo** pH já muda a ocupância em mais de 0,5 em 3 de 16 pares. Logo, nenhuma mudança entre pH pode ser lida como efeito do pH. Só NGGRPDAP e GGKPGEP repetem. |
| 13 | 45 | 8:45 | **Etapa 6.** Quatro peptídeos sobreviveram a todos os filtros. Destaque para os dois de *A. gemmatalis*: NGGRPDAP, linear, com arginina em S1 seguida de prolina; e GGKPGEP, cíclico, com lisina e a menor distância final ao Asp189, 2,71 Å. |
| 14 | 40 | 9:25 | E o nó do slide 6 tem saída, geométrica. Um controle embaralhado com a mesma composição do NGGRPDAP ocupa S1 igual, e difere só no resíduo seguinte: glicina em vez de prolina. Nele, a serina catalítica fica em geometria de ataque em 8% dos quadros. Nas nove execuções com prolina depois da lisina ou da arginina: zero. *Ressalva: clivagem antes de prolina é mais lenta, não ausente; e o critério aqui é geométrico, não cinético.* |
| 15 | 40 | 10:05 | **Take-home.** A plataforma existe, roda e é transferível para outro alvo: ela entrega um caminho reprodutível da enzima ao candidato ordenado, com a não clivabilidade como exigência explícita e cada escore calibrado antes de ser usado. O que ela ainda não diz: tudo é computacional, sem ensaio e sem contrasseleção. O próximo passo é enzimático. Fechar em: *"um candidato só interessa se o Ki medido nas mesmas condições ficar abaixo da faixa milimolar do GORE2, ou se ele persistir mais tempo no extrato de intestino."* Obrigado. |

---

## Frases que não podem sair diferente

Estas são as ressalvas que o manuscrito faz e que o resumo oral precisa manter.

- "Confiança do Boltz-2 **não é afinidade**." Serve para comparar um candidato com o seu controle pareado, no mesmo receptor.
- "MM-GBSA e PRODIGY **ordenam** candidatos do mesmo receptor e do mesmo protocolo; não estimam afinidade."
- "A ocupância de S1 em 10 ns **acompanha a pose inicial**; por si só não indica ligação."
- "**Todos** os resultados são computacionais. Seletividade e atividade não foram testadas."
- "Lisina ou arginina seguida de prolina é uma **barreira estatística**, não uma proteção absoluta."
- "A aminopeptidase N continua sendo um furo no peptídeo linear: ela processa qualquer N-terminal livre."

## Perguntas prováveis e a resposta curta

| Pergunta | Resposta |
|---|---|
| "Vocês testaram?" | Não. Nada aqui é experimental. O teste decisivo é inibição e estabilidade em extrato de intestino de *A. gemmatalis*, com o GORE2 como controle positivo. |
| "E a seletividade? Isso não mata abelha e gente?" | A seletividade **não foi tratada**. S1 é conservado entre tripsinas, e um peptídeo ancorado ali não pode ser presumido como poupando proteases não alvo. É a primeira coisa a entrar como objetivo de otimização na próxima versão. |
| "Por que só 10 ns e uma réplica?" | Porque é triagem, não medida — e nós mostramos que isso não basta: repetir no mesmo pH mudou a ocupância em mais de 0,5 em 3 de 16 pares. A lista curta precisa de réplicas e de centenas de nanossegundos. |
| "Por que tanta glicina?" | É a consequência direta da regra: ao proibir os nove resíduos que as proteases do intestino assumem em P1, sobram resíduos pequenos. Isso troca um risco por outro, e o enriquecimento é consequência da regra, não evidência de estabilidade. |
| "Por que não usar cisteína e fechar como os inibidores naturais?" | O desenho foi feito sem cisteína; o fechamento cabeça-cauda é a única restrição mantida, e só na frente M. Rigidez por dissulfeto não é garantia: um Bowman–Birk com sete dissulfetos inibiu as enzimas de *A. gemmatalis* **menos** que o inibidor de Kunitz da soja. |
| "A IA não inventou esses peptídeos do nada?" | O RFdiffusion e o ProteinMPNN propõem; quem elimina é a regra biológica e a física. Dos 22.066 propostos, 97,6% caem na regra de clivagem, e a calibração diz explicitamente que os escores de rede neural só sustentam comparação pareada. |

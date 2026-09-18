# B1.1 — Curadoria de tripsinas digestivas de Lepidoptera

**Data:** 2026-09-18 | **Fonte:** UniProt REST API (reviewed/Swiss-Prot), busca PubMed via MCP

## ACHADO PRINCIPAL — cobertura curada do UniProt é quase inexistente para as pragas-alvo

Rodei `scripts/search_uniprot_trypsins.py` (busca ampla, já existente do V1) nas 9 espécies do
plano e, em seguida, duas buscas mais estritas:

1. `organism_name:"<espécie>" AND reviewed:true` + campo `cc_tissue_specificity` (produção,
   um-off, não commitada como script — comando ad hoc documentado abaixo).
2. `keyword:KW-0224` (Digestion) — filtro de anotação funcional curada do UniProt.

**Resultado real:** das 9 espécies do plano, **só *Manduca sexta* tem tripsinas digestivas
reviewed com evidência de tecido explícita**:

| Accession | Nome | len | Tissue specificity (UniProt, curado) | AlphaFoldDB |
|---|---|---|---|---|
| P35045 | Trypsin, alkaline A | 256 | **Midgut** | sim |
| P35046 | Trypsin, alkaline B | 256 | **Midgut** | sim |
| P35047 | Trypsin, alkaline C | 256 | **Midgut** | sim |

*Bombyx mori* tem 10 entradas reviewed, mas nenhuma é tripsina digestiva com evidência de
midgut — são inibidores (glândula da seda), proteases de hemolinfa/hemócitos, ou proteases
reprodutivas. As tripsinas digestivas reais de *B. mori* aparentemente só existem como TrEMBL
não-curado (`A0A8R2AJH1` etc., sem `cc_tissue_specificity`).

**As outras 7 espécies do plano — incluindo o alvo principal *Spodoptera frugiperda* — têm ZERO
entradas reviewed para trypsin, e ZERO resultado para `keyword:KW-0224`.** Tudo que existe é
TrEMBL automático (`A0A9R0...` etc.), sem anotação funcional/tecidual curada. Isso não significa
que a evidência experimental não exista na literatura — significa que ela **não está no UniProt
de forma consultável por API**, e exige mineração de artigo por artigo (extrair sequência/
accession do texto e casar com a entrada de banco).

## Referência "Brito et al. 2013" (S. frugiperda, tripsinas insensíveis) — NÃO localizada

A memória do projeto cita "tripsinas insensíveis a inibidor descritas em *S. frugiperda* (Brito
et al. 2013)" como algo a anotar explicitamente no painel. Tentei localizar via PubMed
(`mcp__plugin_bio-research_pubmed__search_articles`) com várias combinações de termos
(`Brito Spodoptera frugiperda trypsin inhibitor insensitive`, `Brito ... proteinase inhibitor
adaptation`, etc.) — **nenhum resultado retornou um artigo de primeiro-autor Brito sobre esse
tema**. Não encontrei o artigo com os termos tentados nesta sessão.

**Não vou tratar essa citação como confirmada.** Fica marcada como *referência não verificada* —
precisa ou (a) o usuário confirmar a citação completa (journal/ano exato/DOI), ou (b) uma busca
mais ampla (Google Scholar, Web of Science) fora do escopo do MCP PubMed disponível aqui.

## Implicação prática para o plano

B1.1 como descrito no `PLANO_V2_GENERATIVO.md` (≥6 espécies com evidência de expressão em
midgut) **não é alcançável só com consultas de banco** — é um trabalho de mineração de
literatura por espécie, artigo por artigo, que não cabe em um bloco só. Isso também bloqueia
B1.3/B1.4/B1.5 e a parte "alvo Lepidoptera" de B0.5 na forma como o DAG do plano exige
(B0.5 precisa de B1.3).

**Estado real agora:** só *Manduca sexta* (P35045/P35046/P35047) tem evidência curada
verificável de expressão em midgut, entre as espécies do plano.

## Decisão pendente do usuário

Como só uma espécie (*M. sexta*) tem evidência forte e verificável sem mineração de literatura
extensa, e o resto exigiria sessões dedicadas de leitura de artigo por espécie, preciso de
direção sobre como sequenciar daqui — ver pergunta feita ao usuário na sessão de 2026-09-18.

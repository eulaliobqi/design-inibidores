# Confirmação real de especificidade tripsina (Asp189) — resolve a ambiguidade "Chymotrypsin" do UniProt

**Data:** 2026-09-18 | **Pedido do usuário:** garantir que o painel Lepidoptera são todas tripsinas
de verdade, não quimotripsinas, antes de prosseguir para B0.5.

## Método (verificado contra referências reais, não assumido)

O determinante clássico de especificidade em serino-proteases tipo-quimotripsina é o resíduo na
posição 189 (numeração clássica de quimotripsina): **Asp189 → especificidade tripsina** (liga
Lys/Arg do substrato), **Ser189 → especificidade quimotripsina** (bolso hidrofóbico p/
aromáticos). Isso é bioquímica de livro-texto (Perona & Craik), mas em vez de assumir a
numeração clássica direto nas sequências precursoras (que incluem peptídeo sinal/propeptídeo, e
por isso não batem com a numeração madura sem verificação), **verifiquei o offset real** contra
as duas referências bovinas clássicas via UniProt REST:

- **Tripsina bovina P00760**: sítio catalítico real (`Active site`, UniProt) em Ser200 (numeração
  do precursor). Resíduo em `200 − 6 = 194` = **D** (Asp) — confirmado.
- **Quimotripsina A bovina P00766**: sítio catalítico real em Ser195 (precursor). Resíduo em
  `195 − 6 = 189` = **S** (Ser) — confirmado.

Ou seja, **o resíduo de especificidade fica a exatos 6 resíduos N-terminal do Ser catalítico**,
verificado independentemente nas duas proteínas de referência (não é suposição). Apliquei o
mesmo offset a cada candidato do painel, localizando o Ser catalítico real via busca direta do
motivo conservado `G[DN]SGG[PT]` na sequência (não via `structure_agent.py` — ver achado abaixo).

## Resultado real: todas as 9 sequências têm Asp na posição de especificidade

| Espécie | Accession | Ser catalítico (posição real na sequência) | Resíduo de especificidade (Ser−6) | Contexto |
|---|---|---|---|---|
| *M. sexta* | P35045 | 213 | **D** | `DVGGRDQCQGD` |
| *S. frugiperda* | A0A089QDB3 | 220 | **D** | `DVGGKDACQGD` |
| *S. litura* | B3F884 | 211 | **D** | `PTGGRDQCQGD` |
| *O. nubilalis* | Q6R561 | 213 | **D** | `DVGGRDQCQGD` |
| *D. saccharalis* | T1QDI0 | 213 | **D** | `DVGGRDQCQGD` |
| *H. virescens* | I7D523 | 219 | **D** | `DVGGKDACQGD` |
| *C. includens* | A0A9P0BRD5 | 212 | **D** | `DVGGRDQCQGD` |
| *P. xylostella* | E2IGY7 | 211 | **D** | `DVGGKDACQGD` |
| *B. mori* | A0A8R2C8B0 | 212 | **D** | `DVGGRDSCTGD` |

**Todas têm Asp.** Contexto local (`C.QGD` imediatamente antes do motivo catalítico) bate com o
padrão conservado das duas referências bovinas (`...C-QGD-SGGP...`), confirmando que o
alinhamento/registro está correto, não é coincidência de posição. **Conclusão: o nome
"Chymotrypsin" que o UniProt atribui automaticamente a quase todas essas entradas é um artefato
de anotação automática (TrEMBL/UniRule), não reflete a especificidade real de substrato.** Isso
confirma a suspeita já registrada em `b11_b13_heuristica_modelada.md`.

## ACHADO NOVO — `structure_agent.py` erra o Ser catalítico em mais espécies que só H. virescens

Comparando o Ser catalítico real (achado por busca de sequência, motivo `GDSGGP`) com o que
`structure_agent._find_catalytic_triad` reportou na rodada de V1 (2026-07-18):

| Espécie | Ser real (sequência) | Ser reportado por structure_agent (PDB) | Diferença |
|---|---|---|---|
| Msexta | 213 | 228 | +15 |
| Slitura | 211 | 226 | +15 |
| Onubilalis | 213 | 228 | +15 |
| Dsaccharalis | 213 | 228 | +15 |
| Cincludens | 212 | 227 | +15 |
| Pxylostella | 211 | 226 | +15 |
| Bmori | 212 | 227 | +15 |
| Sfrugiperda | 220 | 236 | +16 |
| Hvirescens | 219 | FALHOU (bug já conhecido) | — |

**O critério "HIS-ASP-SER a ≤15 Å" do `structure_agent.py` é frouxo demais** — pega uma serina
errada (deslocada ~15 posições) na maioria das espécies, não só em H. virescens. Isso não muda a
conclusão de especificidade (baseada em busca direta de sequência, método independente), mas
**invalida a geometria de tríade/bolso S1 reportada em `outputs/structure_multi/summary.json`
para uso em B1.4 (mapeamento fino de subsítios)** — precisa de correção no código antes de
confiar nessa geometria para qualquer coisa além de "existe uma tríade real por perto".

## Decisão

**Go confirmado para B0.5**: todas as 8 espécies do painel primário + a referência *M. sexta* são
tripsinas reais por especificidade de substrato (Asp189-equivalente confirmado), apesar do nome
"Chymotrypsin" automático do UniProt. Nenhuma quimotripsina real entrou no painel.

**Pendência registrada para antes de B1.4**: corrigir `_find_catalytic_triad`/`_find_s1_asp` em
`scripts/agents/structure_agent.py` (critério de distância atual não é confiável) — não bloqueia
B0.5, que usa Boltz-2/MD/scoring, não a geometria específica de bolso S1 do structure_agent.

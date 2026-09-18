# B1.1 (revisado) + B1.3 parcial — painel de Lepidoptera por heurística de homologia + modelo

**Data:** 2026-09-18 | **Decisão do usuário:** adotar heurística — aceitar tripsinas modeladas
(AlphaFold/SwissModel/difusão) mesmo sem confirmação experimental de expressão em midgut,
já que o UniProt não tem cobertura curada para a maioria das pragas-alvo (ver
`b11_curadoria_lepidoptera.md`).

## O que já existia (V1, 2026-07-18) e foi reaproveitado

`scripts/fetch_lepidoptera_af.py` e `scripts/map_lepidoptera_sites.py` já tinham feito quase
todo o trabalho: 10 estruturas AlphaFoldDB reais baixadas em `~/design-inibidores/data-nontargets/`
no servidor, com detecção de tríade catalítica real via `StructureAgent._analyze_single` (mesmo
método usado nos 4 receptores primários). Não precisei rebaixar nada — só reverificar.

## Reverificação real feita nesta sessão

1. **Sequências reconfirmadas via UniProt REST** (`.fasta`) para as 10 accessions do V1 + as 3
   tripsinas alcalinas reviewed de *M. sexta* (P35045/46/47).
2. **Achado de nomenclatura:** o nome automático ATUAL no UniProt para quase todas as entradas do
   painel é **"Chymotrypsin"**, não "trypsin" — mudou desde a busca de V1 em 2026-07-18 (a
   reanotação automática do UniProt não é estática). Isso é uma ambiguidade conhecida em
   serino-proteases digestivas de inseto (alta similaridade entre famílias trypsin-like e
   chymotrypsin-like). Não usei o campo "nome" como critério — usei evidência estrutural.
3. **Identidade de sequência real** (Biopython `PairwiseAligner`, BLOSUM62, alinhamento global)
   contra a referência confirmada *M. sexta* P35046: variou de **44,8% (Plutella) a 71,0%
   (Chrysodeixis)** — consistente com divergência real entre gêneros de Lepidoptera na família
   quimotripsina-símile, não ruído (aleatório seria ~15-25%).
4. **pLDDT real** extraído da coluna B-factor dos PDBs (é onde AlphaFold grava pLDDT): todas as
   10 estruturas têm pLDDT médio 88,9-92,2 — boa confiança, sem outlier de qualidade.
5. **Achado real sobre o bug conhecido de *H. virescens*** (já registrado em memória de projeto
   anterior): a detecção automática de tríade falhou de novo (`HIS=112,ASP=111,SER=106`,
   geometricamente implausível). Mas busquei o motivo catalítico canônico `G[DN]SGG[PT]`
   **diretamente na sequência** e ele está lá, na posição 217, exatamente como esperado — a
   estrutura e a proteína são reais, o bug é só no script de detecção automática do
   `structure_agent.py` para esse accession específico. **Não excluí H. virescens do painel**,
   mas marquei que o QC estrutural completo (Asp do bolso S1) precisa ser refeito com o bug
   corrigido antes de B1.4/B1.5.
6. **Achado sobre *S. frugiperda*** (alvo principal do projeto): geometria da tríade também é
   atípica (`SER=236, s1_asp=219` vs. `~112-116` nas outras espécies) — não é uma falha total
   (HIS/ASP batem com o padrão conservado), mas fica marcado para revisão manual antes de B1.4.

## Decisão de reclassificação: *Bombyx mori* sai do painel de alvos

*B. mori* é inseto domesticado de valor econômico (seda), não praga agrícola. Por
[[feedback_prioridade_especificidade]] — nunca tratar especificidade como checagem pós-hoc —
movi *B. mori* para o papel de espécie a proteger na contrasseleção (B1.2, categoria análoga a
polinizadores), não alvo primário de design. Isso é uma decisão de escopo, documentada em
`data-lepidoptera-panel/panel_v2.json`.

## Painel final desta sessão

Arquivo: `data-lepidoptera-panel/panel_v2.json` (metadados + proveniência; os PDBs em si
continuam só no servidor, `~/design-inibidores/data-nontargets/`, não commitados por serem
arquivo de estrutura grande e reproduzível a partir do accession).

| Espécie | Accession | %id vs. M. sexta | pLDDT | QC tríade | Papel |
|---|---|---|---|---|---|
| *M. sexta* | P35045 | 96,1% (paralogo) | 92,2 | OK | referência verificada (midgut confirmado) |
| *S. frugiperda* | A0A089QDB3 | 50,6% | 89,8 | OK, geometria atípica (revisar) | **alvo primário, prioridade máxima** |
| *S. litura* | B3F884 | 67,3% | 90,1 | OK | alvo primário |
| *O. nubilalis* | Q6R561 | 66,7% | 89,7 | OK | alvo primário |
| *D. saccharalis* | T1QDI0 | 65,5% | 91,0 | OK | alvo primário |
| *C. includens* | A0A9P0BRD5 | 71,0% | 90,4 | OK | alvo primário |
| *H. virescens* | I7D523 | 48,8% | 89,9 | falhou (bug conhecido; motivo catalítico confirmado manual) | alvo primário, com ressalva |
| *P. xylostella* | E2IGY7 | 44,8% | 90,6 | OK | alvo primário, confiança menor |
| *B. mori* | A0A8R2C8B0 | 68,7% | 88,9 | OK | **reclassificado → painel negativo B1.2** |

**Go decidido:** 7 espécies-alvo primárias entram no painel de B1.4/B1.5/B2 com heurística
declarada (não confirmação experimental). *B. mori* migra para B1.2. *H. virescens* e
*S. frugiperda* têm ressalva de geometria/QC a resolver antes de confiar no mapeamento fino de
subsítios (B1.4).

## Pendências reais deixadas para depois (não bloqueiam seguir para B0.5 parcial)

- Corrigir o bug de detecção de tríade do `structure_agent.py` para *H. virescens* (e reavaliar
  *S. frugiperda*) antes de B1.4 (mapeamento de subsítios).
- B1.2 (painel negativo completo: mamíferos, polinizadores, inimigos naturais, ambientais) ainda
  não foi montado — só *B. mori* foi realocado para lá.

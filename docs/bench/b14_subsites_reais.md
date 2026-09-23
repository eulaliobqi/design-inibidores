# B1.4 — Mapeamento real dos subsítios S1-S4/S1'-S3' + exossítio (2026-09-23)

**Substitui a heurística "204/218" e a tríade catalítica de `structure_agent.py`**
(`_find_catalytic_triad`, offset sistemático de +15/+16 resíduos confirmado em 8/9 espécies —
ver `b1x_confirmacao_especificidade_tripsina.md`). Script: `scripts/map_subsites_b14.py`.
Roda no servidor, env `structure` (foldseek + biopython).

## Método

1. **Definição real dos subsítios** — dois complexos cristalográficos de referência baixados do
   RCSB: `2PTC` (tripsina bovina β, cadeia E, complexada com BPTI, cadeia I) e `1SFI` (tripsina
   bovina, cadeia A, complexada com SFTI-1, cadeia I). Para cada complexo:
   - **P1 do inibidor achado por geometria real**, não citado de literatura sem checagem: é o
     resíduo do inibidor cujo carbono carbonila fica mais próximo do OG de alguma Ser da própria
     cadeia de tripsina (geometria de ataque nucleofílico real). Resultado: **BPTI P1=Lys15**,
     **SFTI-1 P1=Lys5** — ambos batem com a literatura clássica, mas aqui foram *computados*, não
     assumidos.
   - A partir do P1, os 7 resíduos do inibidor em torno da ligação cindível (P4...P3',
     nomenclatura Schechter-Berger) são identificados por posição na cadeia.
   - Para cada Pn, os resíduos de tripsina com algum átomo a ≤4,5 Å definem o subsítio Sn real
     (contato físico, não posição heurística). Resíduos de tripsina em contato com o resto do
     inibidor (fora de P4...P3') definem o **exossítio**.
   - **Validação de sanidade automática**: em ambos os complexos, a Ser catalítica encontrada é
     **Ser195** (numeração bovina clássica) e o S1 real inclui `Asp189, Asp194, Gly216, Gly226,
     Ser190, Ser214, Trp215, Val213, His57...` — bolso de especificidade canônico da tripsina,
     batendo com décadas de literatura estrutural, mas obtido aqui por geometria pura.

2. **Transferência para os 9 receptores do painel** (`data-lepidoptera-panel/*.pdb`) via
   **equivalência estrutural real**: `foldseek easy-search --alignment-type 1` (TMalign) entre
   cada receptor (query) e a cadeia de tripsina extraída de cada template (target). A
   correspondência resíduo-a-resíduo vem do alinhamento estrutural real (`qaln`/`taln` +
   `qstart`/`tstart`), não de um offset de sequência assumido — cada resíduo do subsítio de
   referência é transferido individualmente, e um resíduo que caia num gap do alinhamento fica
   marcado como `sem_correspondencia_estrutural` em vez de silenciosamente herdar um número
   errado.

## Resultado — 18/18 combinações espécie×template aprovadas (GO)

| Métrica | Faixa observada (9 espécies × 2 templates) |
|---|---|
| TMscore (TMalign) | 0,946 – 0,957 |
| RMSD da superposição | 1,18 – 1,41 Å |
| Resíduos de subsítio transferidos | 100% (48/48 contra 2PTC, 49/49 contra 1SFI, em todas as espécies) |

Nenhum receptor foi excluído — todas as 9 estruturas (7 alvos + M. sexta + B. mori) superpõem
com altíssima confiança estrutural sobre os dois templates cristalográficos reais.

## Validação cruzada independente — 100% de concordância com o achado de B1.1x

O resíduo Asp189-equivalente (posição de especificidade tripsina/quimotripsina) já havia sido
determinado por um método **totalmente independente** (offset de sequência a partir do Ser
catalítico, verificado manualmente contra tripsina/quimotripsina bovinas reais —
`b1x_confirmacao_especificidade_tripsina.md`). O método estrutural (B1.4) reproduziu **exatamente
os mesmos números** para as 9 espécies:

| Espécie | Ser catalítica (B1.4, estrutural) | Asp189-eq. (B1.4, estrutural) | Asp189-eq. (B1.1x, sequência) |
|---|---|---|---|
| S. frugiperda | Ser220 | Asp214 | Asp214 ✅ |
| S. litura | Ser211 | Asp205 | Asp205 ✅ |
| O. nubilalis | Ser213 | Asp207 | Asp207 ✅ |
| D. saccharalis | Ser213 | Asp207 | Asp207 ✅ |
| C. includens | Ser212 | Asp206 | Asp206 ✅ |
| H. virescens | Ser219 | Asp213 | Asp213 ✅ |
| P. xylostella | Ser211 | Asp205 | Asp205 ✅ |
| M. sexta | Ser213 | Asp207 | Asp207 ✅ |
| B. mori | Ser212 | Asp206 | Asp206 ✅ |

Concordância de 9/9. Isso não é redundante: o método estrutural entrega, além dessa confirmação,
a definição **completa** de S1-S4/S1'-S3' e exossítio por espécie — algo que o método de sequência
nunca produziu, e que `structure_agent.py` produzia errado (offset sistemático).

## Saída

- `outputs/sites/subsites_by_receptor.json` (não versionado, padrão do repo)
- `data-lepidoptera-panel/subsites_by_receptor.json` (versionado — cópia dos mesmos dados),
  com `ref_definitions` (subsítios reais dos 2 templates) e `receptors` (transferência por
  espécie × template, com status, TMscore, RMSD e a lista completa de resíduos de subsítio
  transferidos, incluindo os não-transferidos quando existirem).

## Pendência / próximo passo

**B1.4 concluído.** Desbloqueia **B1.5** (determinantes de seletividade): cruzar esta geometria
real com o comportamento do painel negativo (B1.2, ainda não montado) para ranquear diferenças
exploráveis entre alvo e antialvo. Nenhum receptor foi excluído do painel nesta etapa.

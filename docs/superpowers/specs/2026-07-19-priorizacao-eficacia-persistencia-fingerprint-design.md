# Design — Reprioridade 2026-07-19: eficácia ampla, persistência competitiva, subsítios S2'/S3', assinatura de interação

## Contexto

Após concluir as réplicas reais de MD (n=3) para o TOP-13 (Seção 3.11f/artigo_resultados.md,
2026-07-19), o usuário redefiniu as prioridades imediatas do projeto `design-inibidores`,
deixando R4 (especificidade humano/*Apis*), R6 (adjuvantes) e R7 (via de aplicação) — do checklist
[[project_requisitos_biologicos]] — para depois. As 4 prioridades atuais:

1. **Eficácia ampla contra lagartas em geral** — expandir cobertura taxonômica (R3), fechando o
   trio pendente do requisito original.
2. **Candidato altamente competitivo e estável** — não apenas RMSD baixo do complexo, mas
   evidência de que o peptídeo não é deslocado do sítio de competição ao longo da trajetória.
3. **Mecanismos de inibição alternativos via subsítios S2'/S3' canônicos** (nomenclatura
   Schechter-Berger — distinto do sítio alostérico S'2 de Oliveira et al. 1993 mapeado no projeto
   irmão `analise-alosterica`, que não é o escopo aqui).
4. **Assinatura digital de interação** — critérios documentados que caracterizem um inibidor
   competitivo real, derivados dos dados já reais do projeto.

Todas as 4 frentes reusam infraestrutura/dado já validado do pipeline — nenhuma frente exige
nova ferramenta ou dependência nova.

## Dados de partida (já existentes, verificados nesta sessão)

- **Trajetórias completas** (`.xtc`/`.tpr`, minim/NVT/NPT/produção) preservadas no servidor para
  rep1 de 12/13 candidatos do TOP-13 (falta só `SARESIKKAYKTFLERYKKL`) em
  `outputs/md/{seq}/` ou `outputs/md/forced_NN/`, e rep2+rep3 de todos os 13 em
  `outputs/md_replicates/{seq}/rep{2,3}/` — confirmado por listagem direta no servidor.
- **`binding_site.json`** por receptor (`outputs/structure*/`) já contém tríade catalítica
  (His/Asp/Ser), Asp do bolso S1, e lista de ~16 resíduos hotspot dentro de 8 Å do centro do
  sítio — gerado por `StructureAgent._analyze_single`, mesmo método já usado em todas as 9
  espécies cross-species existentes (8 já dockadas + o alvo primário).
- **`scripts/dock_cross_species.py`**: pipeline de docking cross-species já validado,
  resume-safe por espécie (evita recomputar o que já rodou).
- **Ferramentas instaladas no servidor** relevantes: `MDAnalysis`, `mdtraj`, `plip 3.0.0`,
  `AutoDock Vina`, `GROMACS gmx_mpi` (ver `artigo_metodologia.md` Seção 2.10) — nenhuma
  ferramenta nova precisa ser instalada.

## Frente 1 — Expansão taxonômica (R3, trio pendente)

**Escopo aprovado pelo usuário**: 3 novas espécies (*Diatraea saccharalis*, *Heliothis
virescens*, *Chrysodeixis includens*) × TOP-13 completo (Tabela 9n/artigo).

**Fluxo:**
1. Buscar accession UniProt real de tripsina digestiva (~250-270aa, prioridade
   `AlphaFoldDB: True`) para cada espécie via `scripts/search_uniprot_trypsins.py` (mesmo padrão
   já usado nas 6 espécies anteriores — REST API real, sem inventar accession).
2. Baixar estrutura via AlphaFold DB (`scripts/fetch_lepidoptera_af.py`); se ausente, fallback
   ESMFold via API pública (mesmo padrão já usado para *H. armigera* B6CME8/B6CME7).
3. Mapear tríade catalítica + hotspot via `StructureAgent._analyze_single` (reuso, sem lógica
   nova) → `binding_site.json` por espécie.
4. Dockar os 13 candidatos via `dock_cross_species.py` (extensão da lista de espécies já
   suportada pelo script, resume-safe).

**Saída:** matriz 13×3 nova (Vina real), no mesmo formato da matriz 13×8 já existente na memória
do projeto (`project_design_inibidores.md`, seção "Cross-species CONCLUÍDO"). Consolidar depois
numa matriz 13×11 única.

**Erro esperado a tratar:** espécie sem entrada AlphaFold (já ocorreu 2x com *H. armigera*) →
fallback ESMFold; se ambos falharem, registrar espécie como "sem estrutura real disponível", não
fabricar dado.

## Frente 2 — Persistência competitiva real

**Métrica primária: ocupância de contato P1↔Asp-S1.** Para cada candidato × réplica (rep1+rep2+
rep3, 10 ns cada), calcular a distância entre o átomo funcional do resíduo P1 básico do peptídeo
(Nη/Nζ de Arg/Lys) e o carboxilato do Asp do bolso S1 (`binding_site.json`), usando os frames
nativos já salvos no `.xtc` comprimido (`nstxout-compressed = 2500` passos × 2 fs = 1 frame a
cada 5 ps, confirmado em `md_agent.py`; 2000 frames por réplica de 10 ns) — sem necessidade de
reamostragem. Classificar cada frame como "ocupando S1" se distância <4 Å (cutoff padrão de
salt-bridge/H-bond na literatura de MD). Reportar **% de ocupância por réplica** e média±DP em
n=3.

**Métrica secundária: RMSD local do peptídeo pós-superposição no bolso S1** (não no complexo
inteiro) — usa só os Cα dos resíduos hotspot do S1 como referência de alinhamento, isolando
"peptídeo balançou dentro da caixa" de "peptídeo saiu da fenda de ligação". Calculado com
`MDAnalysis.analysis.rms` sobre a mesma seleção de átomos usada na ocupância.

**Escopo de candidatos:** TOP-13 completo (mesmas trajetórias da Frente 3, dado já existe).

**Caso degenerado a tratar:** candidato sem trajetória bruta preservada
(`SARESIKKAYKTFLERYKKL`) — reportar como "sem dado real disponível para persistência", não
fabricar.

## Frente 3 — Subsítios S2'/S3' canônicos

**Definição operacional (geométrica+sequencial, sem homologia — decisão do usuário):** dos
resíduos já presentes no hotspot 8 Å de cada receptor (`binding_site.json`), os que estão na
vizinhança sequencial da Ser catalítica (aproximadamente Ser+1 a Ser+15) **e não pertencem ao
bolso S1** (Asp S1 + vizinhança imediata) são candidatos a revestir S2'/S3'. Essa faixa aproxima
a região onde a literatura de serino-proteases (tripsina/quimotripsina) situa os subsítios
"prime" — não é homologia estrutural a uma referência externa, é geometria+posição sequencial
sobre a própria estrutura já mapeada de cada receptor.

**Fluxo:** rodar PLIP (`plip 3.0.0`, já instalado) sobre múltiplos frames das trajetórias
existentes do TOP-13 (não só o frame final, como nas Seções 3.10b/3.11e anteriores) e contar
contatos reais com os resíduos S2'/S3' assim definidos, ao longo do tempo — mesma trajetória
reusada da Frente 2 (nenhuma simulação nova).

**Saída:** por candidato, fração de frames com contato real em S2'/S3' (H-bond, hidrofóbico, ou
salt-bridge PLIP), separado por réplica.

**Risco a documentar explicitamente:** a definição "Ser+1 a Ser+15" é uma heurística, não uma
verdade estrutural validada externamente — deve ser marcada no artigo como aproximação, igual ao
tratamento dado ao mapeamento fraco de S'2 no projeto irmão (RMSD de ajuste 5-6,5 Å, também
reportado com ressalva).

## Frente 4 — Assinatura digital de interação

**Formato:** tabela de critérios documentada em `artigo_resultados.md` (nova subseção), não
script novo. Deriva diretamente das saídas das Frentes 2 e 3 (sem MD/docking adicional) para os
4 candidatos reprodutivelmente estáveis (SRTRR, VRYRR, VRRPR, HRPRRPR) + o caso não-canônico
`SEEEVLAANEAYAAAHTAYN` (mecanismo via Tyr, já documentado na Seção 3.10b).

**Conteúdo esperado da tabela:** por candidato — % ocupância P1↔Asp-S1 (Frente 2), RMSD local do
bolso (Frente 2), contato real com tríade catalítica (já existente, Tabela 9m), contato real com
S2'/S3' (Frente 3) — permitindo visualizar quais contatos são comuns aos candidatos genuinamente
competitivos vs. aos marginais/alta-variância, sem inferir regra além do que os números mostrarem.

## Ordem de execução recomendada

1. Frentes 2+3 primeiro — reusam trajetórias já existentes no servidor, nenhum custo de
   simulação/docking novo, resultado mais rápido.
2. Frente 4 — síntese direta das saídas de 2+3, sem novo cálculo.
3. Frente 1 por último — única frente que precisa de estrutura nova (busca UniProt + AlphaFold/
   ESMFold) e docking novo (13×3 = 39 novos dockings), maior custo/tempo.

## Testes / verificação

- Cada frente produz dado real verificável (nenhum valor inferido) — mesma disciplina do resto
  do projeto ([[feedback_no_fabricated_data]]).
- Frente 1: confirmar contagem de átomos Cα da estrutura baixada bate com o comprimento real da
  sequência UniProt (mesma verificação de integridade já usada nas 8 espécies anteriores).
- Frentes 2/3: validar manualmente 1 candidato conhecido (ex. `SRTRR`, já confirmado estável e
  com contato real com tríade catalítica) antes de rodar os 13, conferindo que a métrica de
  ocupância bate com a expectativa qualitativa já documentada.
- Atualizar `artigo_resultados.md`/`artigo_metodologia.md` e a memória do projeto ao final de
  cada frente concluída (padrão já estabelecido, [[feedback_real_data_and_memory_hygiene]]).

## Fora de escopo (explicitamente adiado pelo usuário)

- R4 — especificidade real vs. tripsina humana/*Apis mellifera*.
- R6 — moléculas adjuvantes (Bt, lectinas, nanoencapsulação).
- R7 — via de aplicação (spray/transgenia, codon optimization, formulação).
- Sítio alostérico S'2 (Oliveira et al. 1993) do projeto irmão `analise-alosterica` — permanece
  como projeto separado, não integrado a esta spec.
- Desenho de peptídeos novos direcionados a S2'/S3' como estratégia primária (a Frente 3 é
  observacional sobre candidatos já existentes, não gera candidatos novos).

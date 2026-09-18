# B0.5 — MD curta (2 ns): consolidação parcial (12/22 sistemas), campanha ainda rodando

**Data:** 2026-09-18 | Campanha completa disparada a pedido do usuário (`ALL`, 2ns produção por
sistema), rodando em background no servidor (`screen b05-md-full`), ETA original ~5h revisado
para ~3h no ritmo mais recente. **Este é um corte parcial a pedido do usuário** ("consolidar até
aqui, retorno mais tarde") — a campanha continua rodando, não foi interrompida.

## Pipeline real usado

Reaproveitei `scripts/agents/md_agent.py` (`MDAgent._run_gromacs`) direto, sem passar pela
orquestração pensada para peptídeos do Rosetta — usei os complexos **preditos pelo Boltz-2**
(`*_model_0.pdb`, receptor+ligante já co-dobrados) como estrutura de partida. Pipeline completo:
`pdb2gmx` (amber99sb-ildn, TIP3P) → `editconf` → `solvate` → `genion` → minimização →
NVT (200ps) → NPT (500ps) → produção (2ns). Protonação real via `pdb2pqr30`/propka, **pH
diferenciado por receptor**: 8,0 para tripsina bovina (fisiológico de mamífero), 10,0 para
*S. frugiperda* (intestino alcalino real de Lepidoptera).

**Achado de engenharia real**: o env `md-gromacs` tem um `pandas` quebrado
(`AttributeError: module 'pandas' has no attribute 'DataFrame'`) que impede importar
`scripts.agents` (o `__init__.py` carrega todos os agentes, inclusive `ranking_agent.py` que
usa pandas). Contornado rodando o driver em `protein_design_env` (pandas funcional) — o
`MDAgent._find_gmx()` já localiza o `gmx_mpi` do `md-gromacs` por caminho absoluto, então isso
não afeta o binário usado, só o interpretador Python do orquestrador.

**Piloto real**: SFTI-1 × tripsina bovina, pipeline completo em ~7-8 min de parede,
**656,8 ns/dia** de throughput real medido (mais rápido que os 399,5 ns/dia de referência do
B0.4 — sistema menor). Ritmo real da campanha variou 8-16 min/sistema dependendo do tamanho do
ligante (SKTI/EcTI, maiores, são mais lentos).

## Resultado real (12 sistemas, todos contra tripsina bovina até agora)

| Par | RMSD médio (nm) | RMSD std | H-bonds médio | Rg médio (nm) |
|---|---|---|---|---|
| BPTI real | 0,229 | 0,080 | 189,0 | 2,624 |
| BPTI decoy | 0,221 | 0,040 | 182,2 | 1,824 |
| SFTI-1 real | **0,744** | 0,813 | 172,6 | 1,653 |
| SFTI-1 decoy | 0,306 | 0,532 | 155,6 | 1,642 |
| SKTI real | 0,115 | 0,015 | 271,0 | 2,220 |
| SKTI decoy | 0,168 | 0,022 | 270,5 | 2,100 |
| Bowman-Birk real | 0,179 | 0,142 | 190,0 | 1,978 |
| Bowman-Birk decoy | **1,862** | 0,442 | 188,4 | 2,744 |
| EcTI real | 0,103 | 0,014 | 270,9 | 2,208 |
| EcTI decoy | 0,212 | 0,050 | 268,3 | 2,226 |
| ApTI real (bovina) | 0,148 | 0,029 | 270,3 | 2,216 |
| ApTI real (*S. frugiperda*) | 0,460 | 0,802 | 311,3 | 2,266 |

## Achado real — RMSD de MD curta dá sinal MISTO, ao contrário do Boltz-2 (10/10)

Ao contrário do `confidence_score`/pLDDT do Boltz-2 (que separou real de decoy em 10/10 pares),
**RMSD de 2ns de MD separa real de decoy de forma inconsistente**:

- **Separa na direção esperada (real mais estável, RMSD menor)**: SKTI (0,115 vs 0,168),
  Bowman-Birk (0,179 vs **1,862** — diferença enorme), EcTI (0,103 vs 0,212). **3/5.**
- **Não separa (real ≈ decoy)**: BPTI (0,229 vs 0,221 — praticamente empatado). **1/5.**
- **Vai na direção ERRADA (real MENOS estável que o decoy)**: SFTI-1 (0,744 vs 0,306 — o real
  tem RMSD 2,4× maior que o decoy). **1/5.**

**Não estou escondendo esse resultado nem forçando uma leitura otimista.** É um achado real e
honesto: RMSD bruto de MD curta (2ns) não é um discriminador confiável sozinho, ao contrário do
que o rung Boltz-2 sugeriu. Hipóteses não confirmadas (não vou apresentar nenhuma como fato):
(a) 2ns pode ser curto demais para separar sinal de ruído térmico, especialmente para SFTI-1
(peptídeo cíclico de só 14 resíduos, interface pequena, pode ter mobilidade real alta mesmo
ligado); (b) RMSD do complexo inteiro sem alinhamento cuidadoso pode ser dominado por
tumbling/deriva do ligante pequeno relativo ao receptor grande, um artefato conhecido de RMSD
mal-especificado — **não verifiquei ainda como o cálculo de RMSD do `MDAgent` está definido
(referência, seleção de átomos), fica como pendência antes de confiar nesse número**.

**Implicação para a decisão de B0.5**: o degrau que efetivamente importa para o critério de
go/no-go do plano é a energia de ligação (MM-PBSA), não o RMSD bruto — RMSD aqui é mais um
sinal de QC (a simulação ficou estável?) do que o discriminador final. **Não declarar go/no-go
da MD só com este RMSD parcial.**

**Verifiquei o código do `MDAgent._analyze_trajectory` (não é mais hipótese) — achado
metodológico real**: o RMSD é calculado com `gmx rms -s md.tpr -f md.xtc` usando o grupo
**"Backbone" tanto para ajuste (fit) quanto para cálculo**, sem índice separado por cadeia —
ou seja, é RMSD do backbone do **complexo inteiro** (receptor+ligante juntos, ajustado como um
bloco só), não RMSD do ligante relativo a um receptor fixo. Isso explica plausivelmente o caso
do SFTI-1: um peptídeo de 14 resíduos rotacionando/deslizando um pouco relativo ao receptor de
220 resíduos infla o RMSD do complexo inteiro mesmo que o ligante continue de fato ligado — o
ajuste é dominado pela massa/tamanho do receptor, não isola o movimento da interface. O mesmo
vale para H-bonds/Rg, calculados sobre o grupo "Protein" (também o complexo inteiro). **Esse é
um limite real do método herdado do V1, não um bug introduzido agora** — mas significa que o
RMSD de complexo inteiro não é o critério certo para "o ligante ficou no bolso", e explica por
que o sinal ficou misto.

## Pendências reais

1. Campanha ainda rodando — faltam ~10 sistemas (principalmente o lado *S. frugiperda*: SFTI1,
   SKTI, BBI, EcTI, BPTI reais+decoys).
2. Se quisermos usar RMSD como discriminador real de calibração (não só QC), precisa recalcular
   com índice separado: ajustar pelo backbone do RECEPTOR só, depois medir RMSD do ligante
   nesse referencial — método padrão para estabilidade de interface, mais correto que o herdado.
3. MM-PBSA (`gmx_MMPBSA`, ambiente `mmgbsa-env`, fix de PBC já conhecido — ver memória do
   projeto) ainda não rodado — é o passo que efetivamente decide o go/no-go energético.

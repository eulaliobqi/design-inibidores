# B0.5 — incidente de memória real no Vina + preparo do painel de calibração

**Data:** 2026-09-18 | **Servidor:** eulalio@200.235.143.10, 188 GB RAM

## Preparo real feito (bom, reaproveitável)

Baixei estruturas experimentais reais (RCSB) dos 5 controles positivos que têm PDB:

| Controle | Accession | PDB | Ligante extraído | len |
|---|---|---|---|---|
| BPTI | P00974 | 1BPI (isolado) | cadeia A | 58 |
| SFTI-1 | Q4GWU5 | **1SFI (complexo real com tripsina bovina!)** | cadeia I | 14 |
| SKTI | P01070 | 1AVU (isolado) | cadeia A | 172 |
| Bowman-Birk | P01055 | 1BBI (isolado) | cadeia A | 71 |
| EcTI | P86451 | 4J2K (2 cópias cristalográficas — usei só cadeia A) | cadeia A | 168 |

**Achado sortudo:** 1SFI é o complexo real SFTI-1↔tripsina bovina — dá receptor real (tripsina
bovina, cadeia A) E o centro real do sítio ativo (centroide do ligante na pose experimental
verdadeira), sem precisar de nenhuma heurística de geometria.

ApTI (P09941/P09942, Adenanthera pavonina) não tem PDB — fica para ser modelado via Boltz-2/
AlphaFold antes de entrar no painel (heurística já aprovada pelo usuário).

Gerei 5 decoys reais por embaralhamento de sequência (mesma composição de aminoácidos, ordem
aleatória — destrói a geometria funcional do loop, mantém a composição, método padrão de
controle negativo em calibração de docking).

## INCIDENTE REAL — Vina consumiu 97 GB de RAM em um servidor de 188 GB

Ao rodar Vina com BPTI (58 resíduos) como ligante rígido (todo o domínio, sem torções, técnica
já usada no `docking_agent.py` para peptídeos desenhados) contra tripsina bovina, o processo
Vina cresceu para **97 GB de RSS** (sistema foi a 152/188 GB usados, só 1,1 GB livre — perto
real de OOM). **Matei o processo imediatamente** por segurança (`kill -9`), memória caiu de volta
para ~58 GB em uso, sistema estável.

**Diagnóstico:** testei separadamente com SFTI-1 (14 resíduos, grid box menor 24×24×24 Å) e
rodou normal, rápido, sem uso anômalo de memória, resultado plausível. A diferença real parece
ser o tamanho do ligante combinado com o grid box maior (a heurística de grid = bounding-box do
ligante + 10 Å de padding gerou uma caixa de ~37×40×48 Å para o BPTI, ~5× o volume da caixa de
teste do SFTI-1). Este build específico de Vina (`f458505-mod`) provavelmente não escala bem
quando o "ligante" é uma proteína dobrada inteira (~1000 átomos após adicionar H) em vez de uma
molécula pequena ou peptídeo curto (uso pretendido do Vina/AutoDock em geral).

**Causa raiz provável:** estou usando a ferramenta errada. Vina foi desenhado para
moléculas pequenas / peptídeos curtos (o próprio `docking_agent.py` já documenta o limite de
"peptídeos > 8 aa têm > 32 ligações torsionais" e usa modo rígido só para peptídeos desenhados
relativamente curtos). Os controles positivos de B0.5 são mini-proteínas dobradas inteiras
(58-172 resíduos) — isso é **docking proteína-proteína**, não docking de peptídeo/molécula
pequena. O `haddock3` já está instalado no servidor (ver auditoria de stack) e é a ferramenta
correta para isso, não Vina.

## Decisão — parei antes de tentar de novo

Não tentei rodar os outros 4 controles (SKTI, Bowman-Birk, EcTI, mais os 5 decoys) contra os 2
receptores porque repetir a mesma abordagem arriscaria outro evento de memória em um servidor
compartilhado. **Preciso de decisão do usuário** sobre:

1. Trocar para HADDOCK3 (já instalado) para o rung de pré-triagem rígida do painel de
   calibração, em vez de Vina — mais apropriado para proteína-proteína, mais lento por rodada
   mas seguro.
2. Ou manter Vina mas com salvaguardas reais: `ulimit -v` (limite duro de memória virtual por
   processo) antes de cada chamada + grid box bem menor (ex.: 24-28 Å fixo, focado só na
   vizinhança imediata do sítio catalítico, aceitando que isso restringe a busca a poses
   próximas do sítio em vez de exploração global) + monitorar memória em tempo real.
3. Reportar isso como achado de robustez de ferramenta (Vina não é confiável para ligantes
   >100 resíduos neste build) e pular Vina para os controles maiores, indo direto para Boltz-2
   (co-dobramento, que já lida nativamente com proteínas inteiras) como primeiro rung real da
   calibração desses controles.

**Boltz-2 (a parte de GPU que o usuário pediu para tocar) ainda não foi rodado nesta sessão** —
parei para resolver isso antes, já que envolve o mesmo tipo de ligante (proteínas inteiras) e eu
queria confirmar que não vou repetir um problema de recurso, desta vez na GPU.

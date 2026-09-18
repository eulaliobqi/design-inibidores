# B0.4 — Benchmark de throughput real (com receptor/sistema real do projeto)

**Data:** 2026-09-17/18 | **Servidor:** eulalio@200.235.143.10, RTX 5070 Ti 16 GB (sm_120), 32 cores

## ACHADO MAIS IMPORTANTE — a GPU é compartilhada com um serviço do próprio usuário

Durante os testes, `nvidia-smi` mostrou **11,6 GB / 16,3 GB ocupados e 98% de utilização
contínua** por um processo do próprio usuário: `ollama-bin/lib/ollama/llama-server` (qwen2.5:3b,
conforme `CLAUDE.md` global), rodando desde as 09:33 do dia, não relacionado a esta sessão.

**Isso não foi interrompido** — é serviço próprio do usuário, fora do escopo desta sessão decidir
parar. Mas isso muda o dimensionamento real de qualquer campanha GPU-intensiva:

- **VRAM real disponível para o pipeline, no pior caso**: ~4,7 GB (16,3 − 11,6), não 16 GB.
- **GROMACS mdrun mediu 58,8 ns/dia AGORA** (sistema real, `forced_00/md.tpr`, mesmo protocolo de
  produção) **vs. 399,5 ns/dia registrado no log de uma corrida real anterior (17/07/2026, sem
  Ollama ativo)** — **queda de 6,8×** por contenção de GPU.
- **Boltz-2 deu OOM** mesmo com `--max_parallel_samples 1` (uma amostra por vez) para o complexo
  receptor (231 aa) + peptídeo (5 aa) — não coube nos ~4,7 GB livres.

**Implicação prática para o PLANO_V2**: campanhas de MD/co-dobramento em produção precisam ou (a)
rodar em horários/janelas em que o Ollama do usuário não está ativo, ou (b) o usuário decidir
liberar a GPU deliberadamente para uma campanha longa, ou (c) assumir throughput ~5-7× menor que
o "pico" da placa em todo o dimensionamento de B2–B4. **Perguntar ao usuário antes da próxima
campanha longa** (B2.7 loop de contrasseleção, B3.5 produção de MD) qual das três opções vale.

## RFdiffusion — geração condicionada a receptor real (caso de uso de produção, B2.3)

Receptor: `data-trypsin/ACR157-A.pdb` (231 aa), hotspots reais de
`outputs/structure/binding_site.json` (15 resíduos), `Complex_base_ckpt.pt`, peptídeo-alvo 12 aa,
`diffuser.T=50` (padrão), 3 designs.

| Métrica | Valor real |
|---|---|
| Tempo/design (produção, receptor real) | **~100 s** (1,66–1,68 min) |
| Tempo/design (peptídeo isolado, teste trivial B0.2) | ~13 s |
| Razão | ~7,5× mais lento com receptor de 231 aa condicionado |
| Throughput contínuo estimado | ~36 designs/hora, ~860/dia |

O contig de produção (`A1-231/0 12-12`) é muito mais caro que o teste isolado do B0.2 — o
dimensionamento de B2.2/B2.3 deve usar este número (100 s/design), não o do B0.2.

## Vina — pré-filtro em CPU (B3.1)

8 dockings concorrentes (4 cores cada, 32 cores total), `exhaustiveness=8`, grid 40 Å — mesmos
parâmetros de produção (`config.yaml`).

| Métrica | Valor real |
|---|---|
| Tempo total (8 jobs paralelos) | 146 s |
| Throughput amortizado | ~18,25 s/pose |
| Estimado contínuo | ~197 poses/hora, ~4.700/dia (32 cores, CPU, independente da GPU) |

Nota: usei um ligante PDBQT pré-existente só para medir tempo de execução — os valores de
afinidade retornados (~10⁶ kcal/mol) são artefato de choque estérico entre um PDBQT pré-posicionado
e o grid, **não são dado científico**, apenas confirmam que o Vina rodou a busca completa
(`exhaustiveness=8`) até o fim. Não usar esses números para nada além de timing.

## GROMACS — MD de produção

Sistema real reaproveitado: `outputs/md/forced_00/md.tpr` (complexo solvatado real, protocolo
`amber99sb-ildn`/TIP3P validado em produção), 5000 passos (`mpirun -np 1 gmx_mpi mdrun -nb gpu
-pme gpu`).

| Condição | ns/dia |
|---|---|
| **Agora, com Ollama a 98% GPU** | **58,8** |
| Histórico real (17/07/2026, GPU livre) | 399,5 |

Ver achado principal acima — a diferença é contenção de GPU, não regressão de hardware/software.

## Boltz-2 — co-dobramento (B3.2)

Receptor real (231 aa) + peptídeo teste (SRTRR, 5 aa), `--use_msa_server` (servidor MSA público,
funcionou: MSA real obtida em ~50 s).

| Tentativa | Resultado |
|---|---|
| `--diffusion_samples 5` (padrão, paralelo) | **OOM** (497 MB necessários, só 268 MB livres) |
| `--diffusion_samples 5 --max_parallel_samples 1` (sequencial) | **OOM** mesmo assim |

**Não foi possível medir tempo real de inferência do Boltz-2 nesta sessão** — a contenção de GPU
pelo Ollama impediu até uma única amostra de rodar. Precisa ser re-medido em uma janela sem
contenção (ver achado principal). O download de MSA real (~50 s, servidor público) é válido e
pode ser usado para dimensionamento de rede independentemente da GPU.

## Dimensionamento provisório do funil (B2.6→B3.x), sujeito a revisão pós-Boltz-2 real

Com os números que temos (RFdiffusion 100 s/design, Vina 18 s/pose amortizado, GROMACS
58,8-399,5 ns/dia dependendo de contenção):

- Gerar ~200-300 backbones/candidatos por trilha em ~8h de GPU (RFdiffusion) é realista.
- Pré-filtro Vina de milhares de sequências em CPU não é o gargalo.
- MD de produção (n=3 réplicas por candidato, mesmo a 58,8 ns/dia) ainda permite ~1,7 ns/dia por
  réplica rodando 3 em paralelo — para os ~10 finalistas do funil (B0 §4), isso é administrável em
  dias, não semanas, **desde que a contenção de GPU seja resolvida ou contornada** (ver achado
  principal).

## Próximo bloco

B0.5 — calibração da escada de scoring com controles reais (BPTI, SFTI-1, SKTI, ApTI + decoys).
Antes de rodar em produção, decidir com o usuário a questão da contenção de GPU (Ollama).

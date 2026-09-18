# B0.2 — RFdiffusion em sm_120 (Blackwell) — resultado real

**Data:** 2026-09-17 | **Servidor:** eulalio@200.235.143.10, RTX 5070 Ti 16 GB (sm_120)
**Env:** `protein_design_env` (torch 2.12.0.dev+cu128, dgl 2.4.0+cu124, se3_transformer, pyrosetta)

## Veredicto

**Go.** RFdiffusion roda em sm_120 sem erro de CUDA/dgl. Nenhum fallback CPU foi necessário.
O plano B declarado no PLANO_V2 (hallucination/MPNN sobre backbones conhecidos) **não é
necessário**.

## Checkpoints

`~/RFdiffusion/models/` tinha apenas `Complex_base_ckpt.pt` (483.619.179 bytes). Baixados agora
via `scripts/download_models.sh` (URLs oficiais IPD):

| Checkpoint | Tamanho | MD5 | Uso |
|---|---|---|---|
| `Base_ckpt.pt` | 483.616.107 B | `4aa4a27ba280d23541e01860c106c7cc` | design incondicional/monômero, base p/ macrociclo |
| `ActiveSite_ckpt.pt` | 483.616.107 B | `0d9f82af03c73011c6fec060bac5b731` | condicionamento a sítio catalítico (relevante p/ B2.3) |
| `Complex_base_ckpt.pt` | 483.619.179 B | (já existia) | binder design PPI — usado pelo `RFdiffusionAgent` do V1 |

Tamanhos de `Base_ckpt.pt` e `ActiveSite_ckpt.pt` coincidem (mesma arquitetura); MD5 confirma que
são arquivos distintos, não uma cópia acidental.

Checkpoints **não baixados** (fora do escopo imediato, ver `download_models.sh`):
`Complex_Fold_base_ckpt.pt`, `InpaintSeq_ckpt.pt`, `InpaintSeq_Fold_ckpt.pt`,
`Base_epoch8_ckpt.pt`. Baixar sob demanda se um bloco futuro precisar de fold-conditioning ou
inpainting de sequência.

## Bug de path encontrado e como foi tratado

RFdiffusion é instalado via `pip` em `site-packages/rfdiffusion/`. Quando nenhum
`inference.ckpt_override_path` nem `inference.model_directory_path` é passado, o código resolve
o diretório de modelos como `{SCRIPT_DIR}/../../models`, onde `SCRIPT_DIR` é
`site-packages/rfdiffusion/inference/` — ou seja, resolve para `site-packages/models/`
(**não** `site-packages/rfdiffusion/models/`, como o nome sugeriria). Isso causa
`FileNotFoundError` em qualquer chamada "nua" a `run_inference.py`.

**Achado importante:** o `RFdiffusionAgent` do pipeline V1 (`scripts/agents/rfdiffusion_agent.py`)
**já contorna esse bug** passando `inference.ckpt_override_path=<repo>/models/Complex_base_ckpt.pt`
explicitamente — nenhum fix é necessário no código do pipeline. Para os testes ad-hoc deste bloco,
usei `inference.model_directory_path=/home/eulalio/RFdiffusion/models` (equivalente).
Para o `input_pdb` default (`examples/input_pdbs/1qys.pdb`) vale o mesmo problema de path relativo
— sempre passar caminho absoluto.

**Regra para blocos futuros:** qualquer chamada nova a `run_inference.py` fora do
`RFdiffusionAgent` precisa de `inference.ckpt_override_path=<abs>` OU
`inference.model_directory_path=<abs>` explícito — nunca confiar no default.

## Timing real (peptídeo isolado, sem receptor — pior caso é maior com receptor condicionado)

| Design | Resíduos | T (timesteps) | Tempo total (carga+inferência) | Inferência pura |
|---|---|---|---|---|
| Incondicional linear | 10 aa | 50 | 14 s | ~6,6 s (50 steps × ~130 ms) |
| Cíclico (`inference.cyclic=True`) | 12 aa | 50 | 13 s | ~6,3 s |
| Incondicional linear | 15 aa | 50 | — | ~0,15 min (idêntico à faixa acima) |

Carregamento do checkpoint (torch.load, 483 MB): dominante nos primeiros ~7-8 s; overhead fixo
por processo, não por design — rodar `num_designs` > 1 no mesmo processo amortiza esse custo.

**VRAM:** ~1,0 GB / 16,3 GB durante um design de peptídeo isolado (15 aa) — folga grande. Uso real
para geração condicionada a receptor (~230 aa, caso de produção do B2.3) ainda não medido; a medir
no B0.4 junto com Boltz-2/GROMACS.

## Modo macrocíclico — validado geometricamente

`inference.cyclic=True inference.cyc_chains='a'` (scripts nativos `design_cyclic_oligos.sh` são
simetria C_n entre cadeias, **não** o que precisamos; os relevantes para a Trilha A/B do plano são
`design_macrocyclic_binder.sh` e `design_macrocyclic_monomer.sh`).

Testado com peptídeo de 12 aa: distância N(res1)–C(resN) = **1,241 Å**, compatível com ligação
peptídica real (~1,33 Å esperado, dentro do ruído de backbone bruto pré-relaxamento) — confirma
que a ciclização cabeça-cauda é geometricamente real, não apenas uma flag ignorada pelo modelo.

**Implicação para o plano:** a Trilha A (macrociclo RFdiffusion nativo) está desbloqueada sem
depender de RFpeptides externo. RFpeptides pode ainda valer a pena para peptídeos com topologia
mais complexa (bicíclicos, múltiplos loops), mas o macrociclo simples já funciona nesta stack.

## Próximos passos (fora do escopo deste bloco)

- B0.3: consertar `ligandmpnn_env` (cu121→cu128) e decidir sobre `BindCraft` (env sem jax).
- B0.4: benchmark de throughput com receptor real (~230 aa) condicionado — Boltz-2, GROMACS,
  Vina — para dimensionar o tamanho de campanha de cada fase.
- B0.5: calibração da escada de scoring com controles reais (BPTI, SFTI-1, SKTI, ApTI).

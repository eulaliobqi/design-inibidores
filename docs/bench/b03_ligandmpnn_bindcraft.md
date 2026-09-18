# B0.3 — LigandMPNN e BindCraft: reconstrução e decisão

**Data:** 2026-09-17/18 | **Servidor:** eulalio@200.235.143.10, RTX 5070 Ti 16 GB (sm_120)

## LigandMPNN — Go, reconstruído do zero

O env `ligandmpnn_env` tinha as dependências (torch 2.2.1+cu121, biopython, ProDy) mas **o
repositório LigandMPNN nunca tinha sido clonado** — não era só uma questão de versão de CUDA.

Ações:
1. `torch` atualizado para `2.11.0+cu128` via `pip install --upgrade torch --index-url
   https://download.pytorch.org/whl/cu128` → `arch` confirma `sm_120` presente.
2. Clonado `https://github.com/dauparas/LigandMPNN` em `~/LigandMPNN`.
3. Baixado o checkpoint default `ligandmpnn_v_32_010_25.pt` (10,5 MB).

**Bug real encontrado e sua causa**: os PDBs deste projeto (`data-trypsin/*.pdb`, produzidos por
`prep_pdbs.py`/AlphaFold) têm `occupancy=0.00` em **todos** os átomos. O parser do LigandMPNN
filtra por padrão `atoms.select("occupancy > 0")` antes de selecionar `"protein"` — com occupancy
zerada, a seleção fica vazia (`None`) e `.select("protein")` quebra com `AttributeError`. Fix:
sempre passar `--parse_atoms_with_zero_occupancy 1` para qualquer PDB deste projeto (não é bug do
LigandMPNN, é uma característica real dos nossos PDBs — vale para qualquer ferramenta baseada em
ProDy/parsing de occupancy que passe a ser usada no pipeline).

**Smoke test real**: rodou com sucesso em `ACR157-A.pdb` (231 aa), gerou sequência redesenhada
completa (`seq_rec=0.3593`, `overall_confidence=0.5397`). VRAM: ~774 MB de 16,3 GB. Confirma que
LigandMPNN está pronto para uso no B2.5 (design de sequência) como complemento ao ProteinMPNN,
especialmente quando houver contexto de ligante/heteroátomo real.

## BindCraft — parcialmente reconstruído, Go condicional

Havia uma tentativa anterior (`~/tool_smoketests/bindcraft_install*.log`) que falhou com
`Out of memory allocating 18446744071562067968*4 bytes!` — **não é falta de memória real** (o
servidor tinha 180 GB livres no momento do teste); é um crash conhecido do solver `libmamba`
(overflow inteiro) ao resolver o conjunto de pacotes fixados pelo instalador oficial
(`jax>=0.4,<=0.6.0`, `jaxlib>=0.4,<=0.6.0=*cuda*` via conda).

**Rota alternativa usada** (mais robusta, evita o solver problemático):
1. Dependências não-jax instaladas via `mamba install` isolado (pandas, biopython, pdbfixer,
   scipy, ffmpeg, py3dmol, dm-tree, etc.) — sucesso, sem OOM, confirmando que o crash era
   específico à combinação com jax/jaxlib fixados, não memória real.
2. `jax[cuda12]` + `dm-haiku` + `flax<0.10.0` + `optax` + `chex` instalados via **pip** em vez de
   conda — wheels mais recentes com melhor suporte a arquiteturas novas.
3. `ColabDesign` instalado via `pip install git+...--no-deps` (dependência do BindCraft para
   hallucination via AF2).
4. Pesos do AlphaFold2 (`alphafold_params_2022-12-06.tar`, ~5,3 GB extraído) baixados e
   extraídos em `~/tools/BindCraft/params/` — ausentes antes, agora completos (confirmado
   `params_model_5_ptm.npz` presente, arquivo que o instalador oficial usa como critério de
   sucesso).

**Resultado real**: `jax 0.6.2` detecta a GPU (`CudaDevice(id=0)`) e executa uma multiplicação de
matriz real em sm_120 sem erro. `colabdesign` importa. Pesos presentes.

**Risco real não resolvido, documentado e não testado a fundo**: a instalação pip do jax trouxe
`numpy 2.2.6`, que **diverge do pin oficial do BindCraft** (`numpy<2.0.0` no
`install_bindcraft.sh`). Código legado (partes do ColabDesign/pdbfixer) pode ter API quebrada em
NumPy 2.x (ex. `np.float_`, `np.unicode_` removidos). **Não testei uma corrida completa de
hallucination end-to-end** (exigiria um alvo real + `settings.json` + tempo de GPU sob a
contenção real do servidor, ver B0.4) — isso fica para quando/se a Trilha C for de fato acionada.

**Decisão**: **não descartar formalmente**, mas manter como "consertado até o smoke test, não
validado em produção" — condizente com o status de Trilha C (opcional, menor prioridade que
Trilha B/SFTI-1 e Trilha A/macrociclo, ambas já com go real). Se o numpy 2.x quebrar algo na
primeira corrida real de B2.4, a correção é fixar `numpy<2.0.0` de volta e testar se `jax 0.6.2`
tolera (provavelmente sim — jax não tem hard-pin em numpy 1.x).

## Resumo para PLANO_V2

Ambos os itens do B0.3 saem do estado "quebrado" documentado em B0.1/B0.2:

| Ferramenta | Antes | Depois |
|---|---|---|
| LigandMPNN | env vazio, repo nunca clonado | funcional, sm_120, smoke test real com receptor do projeto |
| BindCraft | env sem jax | jax+colabdesign+pesos AF2 funcionais; numpy 2.x é risco conhecido não testado em produção |

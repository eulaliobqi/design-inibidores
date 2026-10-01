# Estado consolidado — 30/09/2026 (noite)

Complementa `PLANO_LINEAR_2026-09-30.md` (plano v3). Nada aqui altera limiares pré-registrados.

## 1. O que está decidido
- **Título oficial (EN):** *From Natural Protease Inhibitors to De Novo Peptide Inhibitors Targeting Digestive Trypsins of Lepidopteran Pests*. Título curto: *De novo peptide inhibitors of pest trypsins*.
- **Duas frentes:** L (peptídeo linear) e M (macrociclo cabeça-cauda), as mesmas 22.066 sequências; o critério duro de não clivabilidade define 527 (L) e 543 (M) candidatos.
- **MD de triagem:** 10 ns, pH 10,0 (intestino médio de Lepidoptera), **CHARMM36 (fev/2026, o mesmo `.ff` do grupo) + TIP3P** (decisão do autor, 30/09 noite; substitui AMBER99SB-ILDN/tleap): KCl 0,10 M, caixa dodecaédrica 1,2 nm, vdW force-switch 1,0–1,2 nm sem DispCorr. Macrociclo: o `pdb2gmx` do GROMACS 2025.4 fecha o anel sozinho; `build_system_charmm.py` confere o anel e aborta se aberto (ver §7).
- **Estrutura inicial da MD:** a amostra de maior confiança **que passa no QC de pose** (limiares inalterados); se nenhuma passa, a de maior confiança, marcada `pdb_qc_pass: false`.
- **Foco:** geração; sem HADDOCK3 de confirmação; nenhuma afirmação de seletividade (E5 não construída).

## 2. Resultados até aqui (todos conferidos nos arquivos de saída)
| Item | Resultado |
|---|---|
| Subsítios | TM-score 0,946–0,957 (20 pares) |
| Calibração | Boltz-2 10/10; RMSD do ligante 9/10; MM-GBSA 4/10, ρ = −0,93 com o tamanho da interface |
| Triagem por motivos | 1.829 sequências; conf. Boltz-2 média 0,862 (isca de SFTI-1 embaralhada chega a 0,944) |
| Critério duro | L 527, M 543; Gly 49,4% dos 4.060 resíduos; 9 K/R, todos antes de Pro; 393 L sem Ile; só 3 dos 8 melhores da 1ª rodada sobrevivem |
| E1 | 1.070/1.070 predições; conf. média L 0,874, M 0,862 |
| Reprodutibilidade do Boltz-2 | mesma entrada, n = 442: ρ = 0,57, \|Δ\| 0,028; linear × cíclico, n = 527: ρ = 0,50, \|Δ\| 0,033 |
| QC de pose (E1, amostra única, linear) | 96/527 (18%) passam; 427 com contato < 2,2 Å |

## 3. Em execução no servidor (`eulalio@200.235.143.10`, `~/design-inibidores`)
- `screen two-fronts` → `scripts/run_two_fronts_pipeline.sh`, saída em `outputs/e1_fix_pipeline.log`.
- Ordem: E2 (L, M) → `pick-qc` → E2b/E4 → E6 MD 10 ns → E7 → E3 controles → matriz 8 × 8 → E8/E9.
- Estado às 20:42: E2-L semente 1 completa (80/80), semente 2 em 35/80, semente 3 e frente M ainda não iniciadas.
- Proteções: `bzfill` (repete até 3× enquanto faltarem predições), `timeout 50m` por lote, pré-processamento com 1 thread.
- Se precisar parar/relançar: **sempre por arquivo de script** (não `pkill -f` na linha do ssh; `screen -X quit` não mata os filhos) — ver memória `feedback_ssh_servidor_cuidados`.

## 4. Incidentes (corrigidos)
1. Pré-processamento do Boltz travou sem erro (E1: 56 min; E2: 20 min; GPU a 0%) → 1 thread + timeout 50 min.
2. Predição pulada por erro intermitente (`'PosixPath' object has no attribute 'islower'`; Boltz sai com código 0) → `bzfill`.
3. Teste de quiralidade do QC de pose estava invertido → corrigido (validado nos 236 CA L do receptor).
4. Duas instâncias do pipeline por um relançamento mal feito → paradas com precisão; uma instância.

## 5. Manuscritos
- EN (submissão): `manuscript/manuscript_src.md` → `python manuscript/render.py` → `manuscript.md`.
- PT (leitura pelo grupo): `manuscript/pt_parts/` → `python manuscript/build_docx_pt.py` → `Manuscrito_PT_leitura.docx` (9 figuras + 2 suplementares inline com legenda, painel de conformidade e estado dos cálculos).
- Figuras: `manuscript/figures/make_figures_v3.py DATA OUT en|pt` (PNG + TIFF + PDF, 300 dpi); cópia PT em `figures_ready_2026-09-30/`.
- Métricas Frontiers in Natural Products: verificadas na página oficial (Original Research ≤ 12.000 palavras; 5–8 palavras-chave; figuras 300 dpi; autor-ano com seis primeiros autores; IA generativa declarada). **Não especificados nas páginas:** limite do resumo (350 é convenção), título, nº de figuras/tabelas.
- Resumo EN: 337 palavras + 9 do trecho pendente = 346/350; **ao trocar o pendente pelos resultados de E2–E7 será preciso cortar outras frases**.

## 6. Pendências
- Preencher 3.8 (E2–E4), 3.9 (MD), 3.10 (L × M), Resumo e 4.1 com resultados; gerar as figuras de ocupância de S1, integridade do anel e comparação L × M.
- Autores: lista, afiliações, contribuições, financiamento, conflito de interesses, declaração de IA (rascunho no texto), DOI de arquivamento do código.
- Conferir no texto completo as citações de Valaitis 1995/1999, Yang 2012, Zhan 2010 e Severiche-Castro 2026 (verificadas só por título/metadados).
- Decisão dos autores: extremidades do peptídeo linear em pH 10 (NH₃⁺/COO⁻ como limitação ou Ac/NHMe).
- Risco de escopo: título destaca inibidores naturais, mas o trabalho é de desenho *de novo* e só computacional; a revista pode exigir validação experimental.

## 7. Troca do campo de força: AMBER99SB-ILDN -> CHARMM36 (30/09 noite)
- **Código:** `scripts/build_system_charmm.py` (novo), `scripts/agents/md_agent.py` (mdp por campo de força + ramo CHARMM), `config.yaml` (`md.forcefield`, `forcefield_dir`, `cation`, `salt_m`). `build_system_tleap.py` fica só como histórico.
- **Armadilhas resolvidas:** (a) o item 0 do menu de terminal do `pdb2gmx` é um patch específico do resíduo (ex.: `MET1`) e quebra; a escolha é por nome (`NH3+`, `PRO-NH2+`, `COO-`) via pty (com pipe o `gmx_mpi` não imprime o menu e trava para sempre); (b) PROPKA em pH 10 devolve CYM/LYN, mapeados para CYM/LSN; (c) o macrociclo fechado não gera menu de terminal para a cadeia B; (d) o anel fechado pelo `pdb2gmx` traz CMAP em todos os resíduos (5 em 5), conferido no itp.
- **Teste de fumaça** (`~/scratch_charmm_test` no servidor, fora do pipeline; sequência GDGDG, C–N 1,30 Å): linear e cíclico montam; o cíclico passou minimização, NVT 200 ps e NPT 500 ps. Produção curta: ver nota no fim.
- **Manuscrito:** Seção de MD reescrita para CHARMM36 (EN + PT; refs `huang2013` e `wacha2023` conferidas no Crossref; `lindorff2010` removida). A **Figura S2 (teste AMBER) foi retirada** e virou `[[PENDING]]`: refazer com CHARMM36.
- **Histórico não alterado:** a calibração B0.5 / MM-GBSA citada no manuscrito foi feita antes, com AMBER (gmx_MMPBSA/AmberTools).
- **Servidor:** o checkout em `~/design-inibidores` ainda NÃO recebeu estes arquivos (pipeline em curso). `run_two_fronts_pipeline.sh` ainda cita tleap em comentário; não foi editado de propósito (script em execução).
- **Teste de fumaça fim a fim concluído (cíclico GDGDG, 1163 s):** minimização, NVT, NPT e produção de 20 ps rodaram e a análise devolveu números. Achado: o RMSD global do `_analyze_trajectory` usava o `md.tpr` como referência e dava 1,62 nm já no quadro 0 (receptor partido pela caixa no `.gro` do NPT); contra o quadro 0 corrigido por PBC dá 0,12 nm em 20 ps. **Corrigido** (`md_ref0.gro`). Rg global 2,0 nm segue sem explicação verificada (receptor do modelo pode ser alongado); só métrica de QC, a estabilidade vem de `analyze_md_top_candidates.py`.

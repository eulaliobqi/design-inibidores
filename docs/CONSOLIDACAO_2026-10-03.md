# Consolidação — 03/10/2026 (noite, MDs de 10 ns concluídas: 48/48)

Base: `outputs/md10_L` (24/24) e `outputs/md10_M` (24/24), zero erros; ranking em `outputs/ranking_final_0310_1944` (servidor, `--lang pt`).
Cópias versionadas: `docs/dados/md10_resumo_48.csv` (uma linha por MD, extraída dos `analysis_summary.json`) e `docs/dados/ranking_final.*` (+ fig12).
Todos os números vêm dessas tabelas; nada foi estimado. Script de encadeamento: `scripts/pos_md_M.sh` (log `outputs/pos_md_M.log`, terminou 19h44).

## 1. Andamento
- **E6/E7 (MD de 10 ns, CHARMM36, pH 10): concluído, 48/48.** L 24, M 24.
- **E3 (controles embaralhados) em curso**: `run_two_fronts_pipeline.sh` começou as predições Boltz-2 (`boltz_yaml_E3_L/Dsaccharalis`, ~20h45). Previsto 1.413 predições, 15–20 h. `delta_paired_{L,M}.json` ainda não existe.
- `md-controls` vivo, só com a linha de espera no log; dispara quando os dois `delta_paired` existirem.
- A GPU continua dividida com os jobs do grupo (`dn2954-gore12t-*` e `md-gore3-rep1-redo`).

## 2. O que as 48 MDs mostram
Distância âncora–Asp S1 (Å), mediana: **L** início 5,72 → fim 6,77; **M** início 5,07 → fim 6,11.

| | L (24) | M (24) |
|---|---|---|
| âncora ≤ 4 Å no último quadro | 2 | 2 |
| âncora ≤ 5,5 Å no último quadro | 7 | 6 |
| âncora > 10 Å (saiu do bolso) | 6 | 4 |
| partiu a ≤ 3,5 Å | 2 | 5 |
| ocupância de S1 (5 Å, 2ª metade) ≥ 0,70 | 2 | 3 |
| âncora igual nas duas metades | 21 | 24 |
| MDs com salto de imagem > 30 Å (≥ 1 quadro) | 6 | 5 |
| contato Ser195 ≥ 0,9 / His57 ≥ 0,9 / ambos | 14 / 11 / 7 | 17 / 11 / 10 |
| RMSD local, últimos 20% (nm): mediana (mín–máx) | 0,56 (0,21–2,64) | 0,30 (0,16–1,69) |

Leituras:
- **A posição inicial prediz a final**: correlação d_ini × d_fim = 0,77 (n = 48) e d_ini × ocupância 2ª metade = −0,46. Confirma a decisão de 02/10 de tratar a ocupância como descritiva (não discrimina candidatos; segue a pose do Boltz-2). Comprimento do peptídeo quase não explica a distância final (r = 0,16).
- **Os melhores em âncora** (d_fim): GGKPGEP (M, 2,71), NGGRPDAP (L, 2,74), GGHSE (M, 3,07), GQNDS (L, 3,77). Todos partiram a ≤ 4,0 Å. Nenhum chegou lá vindo de longe.
- **Por espécie** (mediana de d_fim, 6 MDs cada): Onubilalis 5,5; Agemmatalis 5,8; Sfrugiperda 5,9; Cincludens 6,4; Dsaccharalis 6,9; Pxylostella 7,3; Hvirescens 7,5; Slitura 7,8. Diferenças pequenas com n = 6; não interpretar como ranking de espécies.
- **Contato com a tríade** é frequente (M: 10/24 com Ser195 e His57 ≥ 0,9), mas contato a 4,5 Å não é ligação produtiva.
- **Lacuna do RMSD resolvida (corrige o §2 da versão de 12h57):** `peptide_rmsd_local_nm_last10ns` está vazia nas 48 porque o analisador grava `..._mean` e `..._final20pct` (a chave antiga só valia para as corridas de 50 ns, vide comentário em `analyze_md_top_candidates.py:173`). **O RMSD local, com a correção de PBC, existe nas 48.** A decisão (2) pendente (recalcular RMSD) deixa de ser necessária; basta o texto citar "últimos 20%" e não "últimos 10 ns".
- O ranking lê só `analysis_summary.json` (verificado em `rank_final_candidates.py:63`); o arquivo `analysis_summary_prefix_glup_bug.json` não entra.

## 3. Anel do macrociclo (frente M)
Critério pré-registrado: C–N ≤ 1,5 Å e ω ≥ 150° em **todos** os quadros. **11/24 cumprem, 13 falham** (todos os 13 em B).
- **C–N máx. ≤ 1,5 Å em 24/24** (1,42–1,46 Å): nenhum anel abriu.
- Falham só pelo ω: mínimo entre 137,2° e 149,9°. Em 12 dos 13, ≥ 97,8% dos quadros têm ω ≥ 150°; **PHGEA** é o pior (91,8%; ω mín. 137,2°).
- Quatro falham por menos de 3° do limiar (GGSQSS 149,0; GIGSG 149,2; DGING 149,9; GGSDHT 147,7).
- O limiar é pré-registrado e **não foi alterado**. A leitura honesta: a falha é de desvio transitório de planaridade da amida, não de anel aberto. Isso vai como descrição secundária (`ring_omega_frac_ge150`), como já previa o plano.

## 4. Ranqueamento final provisório (camadas A/B/C/P)
| Frente | A | B | C | P |
|---|---|---|---|---|
| L | 24 | 0 | 0 | 0 |
| M | 11 | 13 | 0 | 0 |

- **Todos `provisório`**: a coluna Δ (E3) está vazia. L tem 24/24 em A porque o único filtro ativo é o QC de pose (todos passam). **A lista não discrimina nada; "sobreviveu aos filtros disponíveis", não "deve inibir".**
- M em A com âncora no bolso: GGHSE (S. frugiperda). Os demais têm ocupância ≈ 0.
- **Nenhuma afirmação de seletividade é possível** (especificidade real 0/35 aprovados, E5 exploratória não construída).
- A ocupância de S1 não define camada (decisão de 02/10).

## 5. O que dá para escrever agora, e o que não
- **Dá**: Métodos 2.x (CHARMM36, 10 ns, critérios, correção de PBC); Resultados de estabilidade das 48 MDs (§2, §3); Resultado negativo honesto: a ocupância acompanha a pose inicial (r = 0,77).
- **Não dá até o E3 e as iscas**: 3.9, 3.10, 3.11, Resumo, 4.1 (qualquer frase de "candidatos recomendados"); figura final da lista de entrega (E9).

## 6. Próximas etapas (ordem de dependência)
1. **Aguardar o E3** (~15–20 h desde 20h45 de 03/10; previsão de fim: 04/10, tarde/noite, com a GPU dividida). Monitorar `boltz_yaml_E3_*`, `delta_paired_*.json`.
2. Pipeline fecha sozinho: matriz 8×8, E8 (L × M), E9 (lista de entrega).
3. `md-controls` dispara sozinho (5 controles de 10 ns; ~2,5–3,5 h por candidato). Escolha final de candidatos para as iscas já está em `run_md_controls.sh` (L: Agemmatalis r2, r3, Sfrugiperda r1; M: Agemmatalis r2, r1). Revisar a lista antes do disparo **se** o E3 mudar o top.
4. Rodar `rank_final_candidates.py` de novo com Δ e `ctrl_decoy_occ5_h2`; só aqui as camadas passam a discriminar.
5. Regra do controle negativo (02/10): se a isca também ficar em S1, usar controle Asp/Leu (não Gly/Ala); controle sem diferença é retirado por completo.
6. Fechar o manuscrito: `[[PENDING]]` de 3.9, 3.10, 3.11, Resumo, 4.1; referências e autores só no fim; sincronizar EN/PT.

## 7. Decisões abertas para o usuário
- (1) Lançar `md-controls` **sem esperar o E3**? O script bloqueia no `delta_paired`. Sem o E3 não há como saber qual candidato é o top real; a lista de candidatos está fixa em `run_md_controls.sh`. Risco de gastar GPU em candidatos que o E3 depois derruba.
- ~~(2) Recalcular RMSD local com PBC~~ — **resolvido**, já existe (§2).

## 8. Retomada
```bash
ssh eulalio@200.235.143.10      # timeout: VPN -> openvpn-gui.exe --connect vpn-UFV-config.ovpn
cd ~/design-inibidores
ls data-b23-scoring/results/delta_paired_*.json
tail -3 outputs/md_controls.log; screen -ls | grep -E 'two-fronts|md-controls'
ps -eo pid,etime,cmd | grep "boltz predict" | grep -v grep | cut -c1-140
```

## 9. Fechamento do dia (03/10, ~22h30)
**Feito hoje**
- Manuscrito EN e PT atualizados com as 48 MDs (Resumo, 2.8, 3.8, 3.9, 3.10, 3.11, 4.1, 4.4 xi, legendas das Figs 11, 12 e S2); commit `fbc014e`. Números conferidos contra `docs/dados/md10_resumo_48.csv`; janelas inicial (4%) e final (20%) como na Seção 2.9; correlação reportada como Spearman (ρ = 0,63) com Pearson (0,77) ao lado; sem valores de P.
- Figuras 11 (painel D dividido em linhas L e M), 12 e S2 regeneradas a partir de `data-e2-results/` (sincronizado do servidor) e `scripts/rank_final_candidates.py` (reproduz 24 A | 11 A + 13 B do servidor).
- Correção do §2: "âncora ≤ 4 Å no último quadro" é, no analisador, a média da janela final (últimos 20%); o texto usa "janela final".
- Revisão de literatura 2025–2026 (OpenAlex, Crossref, PubMed, Europe PMC). Verificados no Crossref, **ainda não inseridos** no manuscrito: Junker e Schoeder 2026 (10.1371/journal.pone.0355549), Fonteyne 2026 (10.1039/d6dd00242k), Masters 2025 (10.1038/s41467-025-63947-5), Wan 2026 (10.1021/acs.jctc.6c01334), Rettie 2025 AfCycDesign (10.1038/s41467-025-59940-7), HighFold4 (10.1093/bib/bbag505), Schultz 2026 (10.1002/arch.70145), Dunbrack 2025 ipSAE (10.1101/2025.02.10.637595, preprint).

**Estado ao fechar**
- E3 em curso (4 `boltz predict` ativos, `delta_paired_{L,M}.json` ainda não existe); GPU a 100%, dividida com jobs `gore`. `two-fronts` e `md-controls` vivos.
- Resumo EN com 455 palavras: conferir o limite da revista.
- `[[PENDING]]` que restam: 3.8 (E3 e matriz 8×8), 3.9 (controle negativo), 3.11 (camadas finais), 4.1 (E3), seções administrativas.

**Para amanhã (ordem)**
1. Conferir E3: `ls data-b23-scoring/results/delta_paired_*.json`; `screen -ls`.
2. Decidir se as frases de literatura (4.2, 4.4, Introdução) entram, e inserir as 8 referências em `refs_meta.json` e `refs_resolved.json`.
3. Após o E3: revisar a lista do `run_md_controls.sh` (inclui NGGRPDAP e GGKPGEP, não GQNDS), recalcular camadas, fechar 3.8–3.11 e 4.1.
4. Decisão aberta do usuário: lançar `md-controls` sem esperar o E3.

### 9.1 Contagem do E3 (03/10, ~22h45)
- **243 de 1.413 predições prontas (17%)**, contadas pelos `confidence_*_model_0.json` em `outputs/b23_boltz2_E3_*`. Total esperado = 471 YAMLs (234 L + 237 M) × 3 sementes.
- Linear, semente 1: 234/234 (completo). Linear, semente 2, *S. frugiperda*: 9/30 em andamento. Resto da linear (sementes 2 e 3) e toda a frente M: 0.
- Ritmo ~120 predições/h desde ~20h45 → faltam ~1.170, estimativa grosseira de 8–12 h (fim provável na manhã de 04/10; cíclicos e a GPU dividida com os jobs `gore` podem alongar).
- Após as predições o pipeline calcula `delta_paired`, matriz 8×8, E8 e E9; só então o `md-controls` dispara.
- Comando de contagem: `find outputs/b23_boltz2_E3_* -path "*predictions*" -name "confidence_*_model_0.json" | wc -l`.

## 10. Retomada de 04/10 (manhã)
**Diagnóstico.** O pipeline `two-fronts`/`e1-fix` morreu às 04:09 de 04/10 no E4m da frente L: `pose_qc.py matrix-prepare` rodou sob `boltz2-env`, que não tem MDAnalysis (`ModuleNotFoundError`). Antes disso o E3 da L havia terminado (702 predições, `delta_paired_L.json`); a frente M nem começou (`set -e` abortou o script). GPU ociosa de ~04:10 a 08:47.

**Ação.** `scripts/run_resume_e3m_e4m.sh` (novo, resume-safe) em `screen resume-e3m`, log `outputs/resume_e3m.log`: E3 da M (3 sementes × 8 espécies, ~711 predições) → `collect` + `delta` → E4m de L e M com `pose_qc` em `protein_design_env` (MDAnalysis 2.9.0) e `boltz predict` em `boltz2-env` → E8/E9. Iniciado 08:47; às 09:01 o lote 1 da M estava em 18/30, GPU a 100% (11,7/16,3 GiB, só o nosso processo). Estimativa de fim do E3 da M: 6–8 h. `md-controls` espera `delta_paired_L` **e** `delta_paired_M` e dispara sozinho depois; a decisão aberta de ontem fica resolvida como "esperar o E3".
- Não rodar `git pull` no servidor com o job vivo: o `run_resume_e3m_e4m.sh` existe lá como arquivo não rastreado e o pull o sobrescreveria (o bash lê o script de forma incremental).

**Resultado do E3, frente L** (`data-e2-results/delta_paired_L.json`, 80 candidatos do E2):
- 78 com controles (S. litura e O. nubilalis perderam os 3 controles de um candidato cada, 27/30); Δ>0 em 63/78 (81%), mediana 0,013, IQR 0,003–0,030, faixa −0,033 a 0,069; por espécie de 5/10 (S. litura) a 10/10 (A. gemmatalis).
- 24 finais L: Δ>0 em 23/24, mediana 0,030 (faixa −0,0001 a 0,069); única exceção HGGGGSG (P. xylostella, Δ = −0,0001).
- Camadas recalculadas (`rank_final_candidates.py`): **L = 23 A + 1 B**, M = 11 A + 13 B (M ainda provisória). `docs/dados/ranking_final.*` e Figura 12 regeneradas.
- Leitura: Δ é da ordem do desvio entre as 15 predições de um candidato (0,019); os finais foram escolhidos por E2 alto, o que infla Δ (0,030 contra 0,013 no conjunto de 80); cada Δ usa 3 controles. Camada A da L exclui só 1 de 24 e não discrimina.

**Manuscrito (EN + PT, re-renderizado).** Seção 3.8: parágrafo novo "Paired controls, linear front (E3)"; 3.11: 23 A + 1 B; Resumo e 4.1 atualizados; `[[PENDING]]` mantidos só para a frente M, a matriz 8×8 (E4), o controle negativo, as camadas finais e as seções administrativas. Resumo EN agora com 482 palavras (era 455): **conferir o limite da revista e cortar**.

**Para quando o job acabar:** (1) `delta_paired_M.json` → rodar `rank_final_candidates.py` e fechar 3.8/3.11/4.1/Resumo; (2) matriz 8×8 → 3.8; (3) `md-controls` dispara: revisar a lista antes (NGGRPDAP, GGKPGEP, não GQNDS); (4) inserir as 8 referências verificadas em 03/10 se as frases entrarem.

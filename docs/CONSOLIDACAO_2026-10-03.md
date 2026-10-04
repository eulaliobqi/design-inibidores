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

**Manuscrito (EN + PT, re-renderizado).** Seção 3.8: parágrafo novo "Paired controls, linear front (E3)"; 3.11: 23 A + 1 B; Resumo e 4.1 atualizados; `[[PENDING]]` mantidos só para a frente M, a matriz 8×8 (E4), o controle negativo, as camadas finais e as seções administrativas. Resumo EN reescrito e cortado de 455 para 382 palavras (contagem do build): ainda ~30 acima de 350, **conferir o limite da revista**.

**Para quando o job acabar:** (1) `delta_paired_M.json` → rodar `rank_final_candidates.py` e fechar 3.8/3.11/4.1/Resumo; (2) matriz 8×8 → 3.8; (3) `md-controls` dispara: revisar a lista antes (NGGRPDAP, GGKPGEP, não GQNDS); (4) inserir as 8 referências verificadas em 03/10 se as frases entrarem.

### 10.1 Revisão completa do manuscrito (04/10, tarde)
- **Referências (72/72):** todos os DOIs resolvem no Crossref; autor, título e ano conferem. 14 divergências são só de formato (ano online × impresso em almeida2021, silvajunior2020, patarroyo2017, varadi2024, uniprot2025, vankempen2024, hou2011; hífen em sobrenomes; autor coletivo em berman2000/zhang2005/uniprot2025). **Não verificado:** se cada frase citada é sustentada pelo texto do artigo; para Valaitis 1995/1999, Yang 2012 e Zhan 2010 só título e metadados foram vistos (nota 3 do manuscrito).
- **Números conferidos contra os dados/aritmética:** soma das Tabelas 3 e 4 (22.066; 1.829; 4.987; 15.250), percentuais das Seções 3.5–3.7, contagens da Tabela 3, "63/78" e "23/24" do E3 linear, identidade candidato × controle (0,35 L / 0,29 M; 5 com ≥60%; 6 com 2 controles distintos, **só nos 48 finais** — texto corrigido).
- **Correções:** (a) os dois candidatos sem controle são poliglicina (GGGGGGG, GGGGGG): todo embaralhamento reproduz a sequência (antes o texto dizia "predições não obtidas"); na M falta o GGGGGGGGGGGGGG pelo mesmo motivo — mencionar ao fechar a 3.8; (b) numeração das limitações em 4.4 estava duplicada ((ix)–(x) repetidos), agora (i)–(xvi); (c) nota de rascunho 1 atualizada.
- **Escrita mais objetiva:** Resumo reescrito (EN e PT); Seção 4.1 e 4.3 reescritas com cortes (~15%). Seções 2 e 3 não foram reescritas; a 3.9 (a mais longa) é candidata a corte numa próxima passada.

## 11. Fechamento do E3-M e entrega (04/10, noite)
**Pipeline `two-fronts` concluído** (`screen resume-e3m`, log `outputs/resume_e3m.log`, terminou com `TWO_FRONTS_ALL_DONE` às 17:47:48):
- E3 da M concluído às 17:22 (`delta_paired_M.json`; 3 sementes × 8 espécies; *S. litura* ficou em 27/30 por semente, como na L). O E3 acabou antes da estimativa de 6–8 h.
- E4m (matriz cruzada 8×8, top-1): L às 17:22, M às 17:34. E8/E9 (comparação e lista de entrega) às 17:47.
- Lista de entrega para MD longa: `outputs/delivery_md_long/` no servidor; cópia em `docs/dados/delivery_md_long_report_2026-10-04.md`. **3 entregues, de 48:**
  - L: `Onubilalis__r2` GQNDS (conf 0,909; Δ 0,013; ocup. 1,0) e `Agemmatalis__r2` NGGRPDAP (0,937; Δ 0,030; ocup. 1,0).
  - M: `Sfrugiperda__r1` GGHSE (0,908; Δ 0,015; ocup. 0,988; anel estrito).
- Critério de entrega (colunas do relatório): QC, MD 10 ns passando, ocupância 5 Å na 2ª metade, âncora igual, Δ>0 (e anel, na M). Os 3 entregues têm ocupância ≥0,988; os Δ são pequenos (0,013–0,030, mesma ordem do desvio entre predições, ver §10).
- Δ ≤ 0 em 3 casos: HGGGGSG (L, *P. xylostella*, −0,0001), GPDGGTG (M, *S. frugiperda*, −0,002), GGHGGG (M, *P. xylostella*, −0,009).
- **Atenção, GGKPGEP (M, *A. gemmatalis*):** ocupância 1,0 e Δ 0,020, mas anel=False, logo **não** entregue. Era um dos nomes da lista prevista em §10 (NGGRPDAP, GGKPGEP, não GQNDS); a lista real difere (entrou GQNDS, saiu GGKPGEP, entrou GGHSE).

**`md-controls`** (`screen md-controls`, log `outputs/md_controls.log`) disparou às 17:25 ao existirem os dois deltas. Primeiro controle: `Agemmatalis__r2__ctrl_d1` (NGGRPDAP embaralhado → PGRGDANP, linear, 1 × 10 ns, CHARMM36 `charmm36-feb2026_cgenff-5.0`); em MD de produção desde 17:41 (gmx_mpi, GPU, 16 threads). **Sem resultado de controle ainda** às 19:01; não sei quantos controles o script roda no total.

**Pendências:**
1. Rodar `rank_final_candidates.py` com `delta_paired_M.json` e fechar 3.8/3.11/4.1/Resumo (camadas M finais; hoje 11 A / 13 B provisório); `[[PENDING]]` da M e da matriz 8×8 (E4).
2. Ler a matriz 8×8 (E4m L/M) e escrever na 3.8.
3. Quando os controles `md-controls` terminarem: comparar com o candidato; regra do projeto, controle sem diferença é retirado por completo.
4. Decidir se GGKPGEP (anel=False) entra por outra via; mencionar poliglicina sem controle (GGGGGGG, GGGGGG, GGGGGGGGGGGGGG) ao fechar a 3.8.
5. Inserir as 8 referências verificadas em 03/10 se as frases entrarem; conferir limite de palavras do Resumo EN (382 contra 350).
6. **Não** rodar `git pull` no servidor com `md-controls` vivo (ver §10).

### 11.1 Manuscrito atualizado com E3-M, camadas M e matriz 8×8 (04/10, noite)
- **Dados trazidos do servidor** para `data-e2-results/`: `delta_paired_M.json`, `matrix_L.json`, `matrix_M.json`, `b23_boltz2_E3_M_scores.json`. Ranking recalculado: `outputs/ranking_final_0410/` (cópia em `docs/dados/ranking_final.*`; Fig. 12 regenerada em `manuscript/figures/`).
- **E3 macrocíclico:** 79/80 com controles (falta GGGGGGGGGGGGGG, *S. litura*); Δ>0 em 60/79 (76%), mediana 0,014, IQR 0,001–0,024, faixa −0,027 a 0,061; finais 22/24 (mediana 0,023); exceções GGHGGG (−0,009) e GPDGGTG (−0,002). Duas frentes juntas: 123/157 (78%).
- **Camadas finais:** L 23 A + 1 B + 0 C; M **10 A + 13 B + 1 C** (antes 11/13/0): GGHGGG foi de A para B (só Δ) e GPDGGTG de B para C (Δ e anel).
- **Matriz 8×8 (1 amostra, parâmetros padrão):** 63/64 (L) e 62/64 (M) predições; 3 falharam no pré-processamento (Slitura×Pxylostella na L; Hvirescens×Pxylostella e Hvirescens×Agemmatalis na M, erro `'tuple' object has no attribute 'islower'`) e não foram repetidas. Diagonal 0,928 (L) e 0,910 (M) contra 0,903 e 0,882 fora da diagonal (~0,025, ruído); receptor próprio é o melhor em 4/8 (L) e 3/8 (M); receptor de *S. litura* tem a menor confiança nas duas frentes. Conclusão escrita: sem preferência espécie-específica, e sem ser teste de seletividade.
- **Correção de erro anterior:** a frente linear tem 5/9 (e não 5/10) em *S. litura* (9 candidatos com controle).
- **Manuscrito:** `manuscript_src.md` (EN) e `pt_parts/p*.md` (PT; `manuscript_pt_src.md` é gerado por `build_docx_pt.py` e sobrescrito) editados em Resumo, 3.8, 3.11, 4.1, legenda da Fig. 12 e nota 1; `render.py` e `build_docx_pt.py` rodados. `[[PENDING]]` restantes: controle negativo (3.9), controles embaralhados em MD e pH (3.11), seções administrativas. **Resumo EN: 390 palavras (limite Frontiers 350).**
- **`md-controls` às 20:53:** 2 controles concluídos (Agemmatalis__r2__ctrl_d1 RMSD 0,45 nm; Agemmatalis__r3__ctrl_d1 0,71 nm; ocupância ainda não analisada), o 3º (Sfrugiperda__r1__ctrl_d2) em MD de produção desde 20:39.

# Consolidação — correções do manuscrito (sessão de 09–11/10/2026)

Estado: manuscrito EN (`manuscript_src.md` → `manuscript.md`, `Manuscript_EN.docx`) e PT (`pt_parts/p1–p5.md` → `manuscript_pt.md`, `Manuscrito_PT_leitura.docx`) sincronizados. Nenhuma simulação nova; só texto, tabelas e figuras. Commits locais `4c05d68` … `2417dd8` (9 à frente de `origin/main`, **sem push e sem `git pull` no servidor**).

## O que mudou

1. **Motivo dos dois pH (2.6 e 3.7, EN/PT).** O intestino médio das lagartas não tem pH único (Dow 1992: fortemente alcalino; *H. virescens* 9,56–10,0, Karumbaiah 2007); pH 8,2 também é o dos ensaios GORE (Schultz 2026). Critério de leitura da 3.7: um candidato que mantém S1 nos dois pH é mais viável. **Falta** uma referência verificada com o pH do intestino médio das outras espécies-alvo (nenhum valor foi inventado; item marcado na lista de pendências do `manuscript_src.md`).
2. **Receptores = tripsinas.** Nove das dez entradas do UniProt têm o nome automático "Chymotrypsin"; por decisão do usuário o texto não menciona mais essa anotação nem o quimotripsinogênio A (commit `aa08173`). A evidência de classe é o Asp189, mais a tríade His57/Asp102/Ser195 e o bolsão S1, conferidos em cada modelo por alinhamento com a tripsina bovina P00760 e por geometria (His NE2–Ser OG 2,92–3,13 Å; His ND1–Asp102 OD 2,70–2,75 Å): **Tabela S2** (EN/PT), `data-lepidoptera-panel/triad_s1_by_receptor.csv`, `manuscript/make_table_s2.py`. Conservados nos 10: Asp189, Cys191, Gly193, Asp194, Gly216, Gly226; variam Ser190 (Ala/Gln), Val213, Trp215 (Phe em 3), Gly219. "Quimotripsina-like" permanece só como classe de protease do intestino no critério de clivagem.
3. **Calibração (3.2, Tabela 2, Figura 2).** Fica só o que o inibidor real superou: confiança Boltz-2, ipTM e pLDDT do complexo (10/10) e RMSD do ligante (9/10; exceção *S. frugiperda*–EcTI). MM-GBSA (4/10) e PRODIGY (2/10) e as correlações com o tamanho da interface saíram do corpo; resumo, 2.2, introdução, 4.1, 4.2 e conclusão ajustados. **Decisão de relato:** ambos seguem ordenando candidatos (2.8), e uma frase em 2.8 diz que nenhum foi calibrado como discriminador e que não são lidos como afinidades. Dados originais em `data-calibration-b05/` e `data-e2-results/prodigy_calib.json`.
4. **Figuras.** Apagadas as saídas cruas antigas (`Figure*` na raiz de `manuscript/figures/`) e `_retiradas/`; ficam `final/` (EN), `pt/` (PT), geradores e `_src/`. Para refazer `final/`: `collect_final.py --run`. `make_figures_final.py` estava com erro de sintaxe (quebra de linha em string na Figura 6); corrigido. Só a Figura 2 foi regenerada (2×2).
5. **Word.** `Manuscript_EN.docx` novo (`build_docx_en.py` + `docx_post.py`; 19 figuras inline, 6 tabelas, sem notas de rascunho). O `.docx` PT passou a incluir as Tabelas S1–S2 (o build descartava tudo após as legendas). Se o Word estiver com o arquivo aberto, o script grava `*_novo.docx`: fechar o Word e rodar de novo.

## Verificado e descartado
- Legenda da Tabela 1: identidade contra *M. sexta* P35046 (tripsina B) está correta; a linha da tabela é P35045 (tripsina A). Não há erro.

## Pendências
- Referência do pH do intestino médio das outras espécies (item 1).
- `build_docx_pt.py` insere figuras só até S10 (a S11 existe e entra no EN).
- Tabela S2 tem 13 colunas; conferir no Word se cabe na página.
- Figuras 1, 5, 6 e 7 não foram regeneradas após a correção do script.
- Os Métodos não justificam pesos (1,0/0,6/0,3) nem cortes (0,3/0,5) da triagem por escore de motivos.
- Autores, afiliações, contribuições, financiamento, IA generativa, DOI do código (já pendentes).
- Push dos 9 commits e `git pull` no servidor.

## Como regenerar
`cd manuscript && python render.py && python build_docx_en.py && python build_docx_pt.py` (PT se monta de `pt_parts/`; editar `manuscript_pt_src.md` é inútil, é sobrescrito).

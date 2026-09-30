# Revisão completa pré-manuscrito — 2026-09-30

Escopo: código, pipeline e números do projeto V2 (`docs/PLANO_V2_GENERATIVO.md`) que entram no
manuscrito. Método: cada número foi **recalculado a partir dos arquivos de dados reais**
(não copiado de documentos); código lido linha a linha nos módulos que geram números reportados.
Regra do manuscrito: só entra o que segue o plano e está correto; V1 (Vina/Rosetta/ranking
composto/ML), a calibração contra a série GORE, a confirmação HADDOCK3 de candidatos, a tentativa de
dissulfeto e o incidente do Vina **não entram**.

## A. Erros que alteravam resultados (corrigidos)

| # | Achado | Evidência | Correção | Efeito |
|---|---|---|---|---|
| A1 | **Filtro de clivagem ignorava a ligação de fechamento do macrociclo** (`seq[:-1]`): K/R (ou F/Y/W/A/G/S/V) na última posição não contava, embora o resíduo n se ligue ao 1. | leitura de `analyze_cleavage.py`; 137/2.360 pontuados tinham K/R na última posição | modo `circular` em `find_cleavage_sites`/`analyze_sequence`; sem P1 geométrico não presume âncora; `run_cleavage_b23.py` usa circular por padrão (`--linear-rule` reproduz o antigo). Semântica legada da pepsina preservada (teste de regressão: linear == original em 3.000 sequências × 7 regras) | RESISTENTE: 2.360 → **1.548** nas 7 espécies (0 fora do conjunto antigo). **5 dos 7 candidatos que foram para MD deixaram de ser RESISTENTE** (só *C. includens* NNGGG e *P. xylostella* GGHTGA permanecem) → MD refeita para os novos top-1 |
| A2 | **RMSD de MD calculado no `md.xtc` bruto** (sem PBC): a cadeia do peptídeo cai noutra imagem periódica. | *C. includens*: distância bruta entre centros de massa 10,8–94,8 Å (mediana 44,7; caixa 116 Å) com peptídeo em contato 100% dos quadros; `rmsd.xvg` média 1,67 nm | `MDAgent._analyze_trajectory` passa por `trjconv -pbc mol -center` (pipe de shell); RMSD/H-bond/Rg agora em `md_pbc.xtc`; análise de interface desempacota o peptídeo por imagem mínima | **Todos os `rmsd_avg_nm`/`rmsd_std_nm` anteriores são inválidos** (inclui o "5/10" da calibração B0.5) |
| A3 | Calibração B0.5, degrau MD: “RMSD 5/10 ≈ acaso” era o artefato A2 | `recompute_b05_md_metrics.py` (22 sistemas, `md_pbc.xtc`, RMSD do ligante após superposição no receptor, desempacotado) | recomputado | **RMSD do ligante: real < decoy em 9/10 pares** (antes 5/10). Contato (nº de resíduos do receptor a <4,5 Å): real > decoy em apenas 2/10 |
| A4 | RMSD local do peptídeo (minha análise de 30/09) sem desempacotamento | *D. saccharalis*: 3/501 quadros com salto de imagem (~97 Å) | `unwrap_peptide` (imagem mínima relativa ao Asp-S1) | *D. saccharalis* RMSD local médio 0,169 → **0,106 nm**; demais inalterados; ocupâncias do S1 não dependem disso (imagem mínima) |

## B. Descrições incorretas ou incompletas nos documentos (corrigidas no manuscrito)

| # | Achado | Fato verificado |
|---|---|---|
| B1 | “Macrociclos confirmados por N–C 1,2–1,4 Å” | Nos 880 backbones (8 espécies × 110): N–C = **0,76–1,40 Å**, nenhum >2 Å. É fechamento dentro da tolerância do modelo, não validação de geometria de ligação peptídica (backbones sem relaxamento all-atom) |
| B2 | “Hotspots = S1+S2 de B1.4” | O RFdiffusion recebeu só `hotspots[:8]` (8 menores números dos 15 de S1+S2): His57-, Leu99-, Asp189-, Ser190-, Cys191-, Gln192-, Gly193-, Asp194-equivalentes (confirmado nos `.trb`). Ser195-eq., Val213/Ser214/Trp215/Gly216/Gly219/Gly226-eq. **não** foram hotspot. O `backbones_manifesto.json` registra a lista completa de 15 (enganoso) |
| B3 | “ProteinMPNN com receptor fixo” | `designed_chains=['A','B']`, `fixed_chains=[]`: receptor **redesenhado junto** (recuperação de sequência nativa ~40%); pesos `v_48_020` (não *soluble*); seed aleatória; `omit_AAs=CX`; T=0,1; ruído de backbone 0,05; só a cadeia B foi retida. Restrições duras do plano B2.5 (zero K/R interno exceto P1) **não** foram implementadas — o corte é pós-hoc (filtro de clivagem) |
| B4 | Painel: identidades de sequência | Recalculadas (BLOSUM62, gap −11/−1, global, sobre o menor comprimento) contra *M. sexta* P35046: 44,3% (*P. xylostella*) – 71,0% (*C. includens*); diferem ≤0,9 pp dos valores dos docs antigos. pLDDT médio 88,9–92,2 confere |
| B5 | “TM-score 0,946–0,957” (B1.4) | É o `alntmscore` do Foldseek (normalizado pelo comprimento do alinhamento), não normalizado pelo comprimento da proteína |
| B6 | Painel B1.4: “18/18 GO” | Com *A. gemmatalis*: **20/20** (10 receptores × 2 templates), RMSD 1,18–1,41 Å, 48/48 e 49/49 resíduos transferidos |
| B7 | Boltz-2: “ipTM limítrofe em 1/10” | ipTM real > decoy em 10/10; menor margem 0,005 (SKTI × *S. frugiperda*: 0,711 vs 0,706). `confidence_score = 0,8·pLDDT + 0,2·ipTM` (erro máx. 8e-8 nos 2.360) |
| B8 | MM-GBSA “4/10” | Confirmado (4/10). **Post hoc**: ΔG correlaciona com a área de contato (ρ de Spearman = −0,93, n = 22, p = 7e-10) — explica por que decoys colapsados “vencem” |
| B9 | Referências | “Boaventura et al. 2023” é **Fonseca et al. 2023** (J Econ Entomol, DOI 10.1093/jee/toad188). “Brito et al. 2013” (tripsinas insensíveis, *S. frugiperda*) **não existe** (PMID apontava outro artigo) — fora. DOIs de Luckett 1999 e Terra & Ferreira 1994 estavam errados (apontavam para artigos de outros temas); corrigidos via Crossref. “Leite et al. 2024” não verificada — fora. Toda referência do manuscrito passou por Crossref/PubMed |

## C. Limitações que precisam constar (não são erros, mas mudam a interpretação)

1. **Rótulo RESISTENTE é heurístico**: 7 regras de motivo (tripsina, quimotripsina alta/baixa, elastase, LysC, ArgC, pepsina), pesos 1,0/0,6/0,3, corte de score <0,3; 1–2 sítios mudam a classe (ex.: GIFDDIG: 0 sítios de tripsina, score 0,34 → MARGINAL). Regras de elastase (após A/G/S/V) e pepsina são cruas; pepsina não é protease de intestino de lagarta. Não é medida de resistência.
2. **O filtro seleciona peptídeos curtos sem K/R**: no conjunto RESISTENTE (n = 1.829, 8 espécies) comprimento médio 7,05 aa, 95,6% ≤ 10 aa, só 4,3% com algum K/R, 1,3% com P1 geométrico em K/R. Isso é o oposto do P1 básico do mecanismo canônico (S1 Asp189).
3. **Boltz-2 e peptídeos curtos**: na calibração, o decoy embaralhado de SFTI-1 (14 aa) teve confidence 0,944 e os reais foram 0,850–0,986; candidatos de 5–8 aa com 0,93–0,95 estão na faixa de um decoy. A calibração (10/10) é **pareada** e feita com proteínas/domínios de 14–176 aa; não valida o ranking absoluto de peptídeos de 5–8 aa. Decoys embaralhados também diferem por enovelamento, não só por ligação.
4. **MD**: 1 réplica × 50 ns por candidato; AMBER99SB-ILDN/TIP3P (campo legado; o plano previa ff19SB/OPC ou CHARMM36m); peptídeo tratado como **linear** (sem fechar o anel na topologia); pH 10,0 via PROPKA. Sinal qualitativo apenas.
5. **Especificidade (B1.2/B1.5/B2.7)** não foi avaliada nesta fase (decisão de escopo, 23/09). Nenhuma afirmação de seletividade é possível; o S1 é conservado.
6. **Painel**: estruturas AlphaFold (não experimentais); anotação UniProt automática “Chymotrypsin”; especificidade tripsina inferida por Asp189-equivalente (10/10 com Asp). Só *M. sexta* tem evidência curada de intestino médio.
7. **Cobertura de experimento**: nenhum ensaio in vitro/in vivo. Todos os resultados são computacionais.

## D. Verificações que confirmaram os números

- Boltz-2 nos 2.360: média 0,8601, mediana 0,8655, mín. 0,6951, máx. 0,9561; 435 (18,4%) ≥ 0,9; 2.121 (89,9%) ≥ 0,8; nenhum < 0,5 ✔.
- Calibração Boltz-2: confidence, pLDDT e ipTM real > decoy em 10/10 ✔ (Δ confidence 0,042–0,274).
- MM-GBSA: 4/10 ✔ (22/22 `status: real`).
- B1.4: 20/20 GO; TM 0,946–0,957; RMSD 1,18–1,41 Å; 48/48 e 49/49 ✔. Asp189-eq. por offset de sequência (Ser−6; calibrado em P00760 → Asp194 e P00766 → Ser189) e por Foldseek coincidem nas 10 estruturas ✔; numeração do JSON = numeração do PDB ✔.
- Campanha: 110 backbones/espécie × 8; comprimento da cadeia B = comprimento pedido em 880/880; 22.066 sequências únicas, 0 divergências de comprimento ✔ (`scripts/audit_campaign.py`).

## E. Pendências de computação (servidor)

`screen b27-corrected` (`scripts/run_b27_corrected_pipeline.sh`): Boltz-2 de *A. gemmatalis* (283 yaml) →
top-1 por espécie (RESISTENTE circular) → MD 50 ns → análise. Só depois disso os resultados de MD e de
*A. gemmatalis* podem entrar no manuscrito.

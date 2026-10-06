# Auditoria metodológica, de código e de resultados — 05/10/2026

Escopo pedido: revisar toda a sequência metodológica e o código e conferir se os resultados estão corretos e justificados pela discussão.
Complementa `docs/AUDITORIA_2026-10-01.md` (V1–V5, F1–F6, W1–W6). Tudo abaixo foi **medido ou lido**; o que não foi verificado está na Seção 5.

## 1. Números do manuscrito (Seções 3.1–3.8 e Tabelas 1, 2, 4)

`scripts/audit_numbers.py` recalcula a partir dos arquivos de dados do repositório e compara com o texto: **187 verificações, 0 falhas** (saída em `docs/dados/audit_numbers_2026-10-05.json`). Cobre: calibração (Boltz-2, RMSD, MM-GBSA, PRODIGY, correlações), painel (TM-score, RMSD, transferência, comprimento, pLDDT, Ser e Asp189 de cada receptor), E2/E3 (médias, ρ, DP, Δ positivos, medianas), QC de pose, matriz cruzada, as 48 MDs (distâncias, ocupância, âncora, RMSD, anel, contagens de 0,70, 9/5/39/0, ρ), PRODIGY nas poses, Tabela 4, tiers.

Recálculos feitos fora desse script (dados no servidor):

| Afirmação | Recalculado | Resultado |
|---|---|---|
| 22.066 sequências; **527 lineares e 543 cíclicas**; 41–86 e 41–87 por espécie | `scripts/audit_hard_criterion.py` sobre as 8 campanhas | confere |
| 16 só-cíclicas (14 terminam em resíduo proibido seguido de Pro inicial; 2 em Ile) | idem | confere |
| comprimento médio 7,7; 430 com ≤ 8; Gly 49,4%, Ser 11,7%, Pro 9,8%, Thr 9,0%, Asp 5,8%; 9 K/R (6 Arg–Pro, 3 Lys–Pro); 393 sem Ile no interior | idem | confere |
| rodada 1: 1.829 RESISTENTE, confiança 0,862 (0,695–0,953), 345 ≥ 0,90, 1.658 ≥ 0,80, ipTM 0,753, pLDDT 0,889 | junção `b23_cleavage_circular.json` × `b23_boltz2_scores.json` | confere (o arquivo de escores tem 2.643 entradas; o texto usa só as 1.829 RESISTENTE) |
| E1: médias 0,874 (L) e 0,862 (M); reprodutibilidade ρ = 0,57 (n = 442; |Δ| 0,028; 0,21–0,69 por espécie); L × M ρ = 0,50 (|Δ| 0,033; L maior em 0,013) | `E1_b23_boltz2_*.json` | confere |
| camadas: L 23 A + 1 B; M 10 A + 13 B + 1 C | `rank_final_candidates.py --layout local` | confere |
| calibração das MDs antigas: pH 8,0 (bovina) e 10,0 (*S. frugiperda*) | logs `MDAgent_*` das 22 corridas | confere |

### Erros encontrados e corrigidos
| # | Erro | Correção |
|---|---|---|
| N1 | "inibidores reais 0,850–0,986": o mínimo é **0,853** (0,850 era o limiar do texto antigo) | corrigido (EN/PT) |
| N2 | "a isca teve mais contatos (PRODIGY) em 6 dos 10 pares": são **7** (um por 0,25 contato) | corrigido (EN/PT, docs) |
| N3 | `manuscript/figures/ranking_final.{csv,json,md}` era de 03/10 (sem Δ, tiers provisórios: 24 A / 11 A + 13 B) | substituído pela saída de 04/10 (`outputs/ranking_final_0410`, com Δ; 23/1 e 10/13/1) |
| N4 | frase "os candidatos com Lys/Arg (NGGRPDAP, GGKPGEP)": são **três** (inclui PISQIDSGSR) | corrigido (EN/PT) |

## 2. Citações da discussão (conferidas contra o resumo completo das fontes)

| Afirmação do texto | Fonte | Veredito |
|---|---|---|
| Boltz-2 "tem estruturas úteis, mas saídas de afinidade não confiáveis" (versão anterior) | Wan 2026 (JCTC 22:7811): predições de afinidade com correlação fraca/moderada com ESMACS; "lacks the energetic resolution for lead identification"; múltiplas poses, não uma pose convergida | **não sustentado como escrito** ("estruturas úteis" não está no resumo) → reescrito; e deixado explícito que usamos o escore de confiança, não a saída de afinidade (a avaliação é de pequenas moléculas) |
| "benchmark de complexos peptídeo cíclico–proteína em que a confiança depende de atributos" | Li 2026 (bioRxiv): 111 complexos; escore de ranking × qualidade ρ 0,53–0,66; ~12% das poses com confiança alta e qualidade ruim; pior em dissulfeto e alvos ≤ 200 resíduos | **imprecisa** → reescrita com os números; preprint, assinalado como bioRxiv |
| peptídeos de Kunitz/Pin-II "agem em pH alcalino" (saikhedkar2018/2019, merino2020rational agrupados) | só Saikhedkar 2018 relata maior eficácia em pH alcalino; 2019: bicíclicos 10× mais potentes; Merino 2020: *S. cosmioides* | **superatribuição** → cada fonte com o seu achado |
| terra1994 junto à afirmação do pH luminal "o mais alto conhecido" | Dow 1992 sustenta; Terra 1994 é revisão geral | **superatribuição** → terra1994 citada à parte |
| comparação com estudo de peptídeo derivado de interface contra tripsinas de *S. frugiperda* (triplicata de 100 ns, MM/GBSA) | Severiche-Castro 2026 (PubMed, texto completo lido) | confere |
| PRODIGY treinado em complexos proteína–proteína | Vangone & Bonvin 2015 (título/DOI no Crossref) | confere |
| "trajetórias únicas podem dar conclusões falso-positivas" (adicionada) | Knapp, Ospina & Deane 2018 (JCTC 14:6127; Crossref) | confere |

Pendências antigas ainda abertas: as frases que citam Valaitis 1995/1999, Yang 2012 e Zhan 2010 seguem no nível do título (texto completo não lido).

## 3. Código

| Arquivo | O que foi verificado | Achado |
|---|---|---|
| `analyze_cleavage.hard_cleavage_sites` | lido; **reimplementado do zero a partir do texto dos Métodos** e rodado nas 22.066 sequências | 0 divergências; o código faz o que os Métodos dizem (Pro seguinte, C-terminal linear com Ile, fechamento do anel) |
| `analyze_md_top_candidates.py` | definição de âncora, janelas (inicial 4%, final 20%), metades, ocupância, ω do anel (diedro CAn–Cn–N1–CA1), RMSD local com correção de imagem, `passes_screen` | correto e coerente com a Seção 2.7. Notas: (a) a âncora usa a distância mínima sobre **todos os átomos pesados do resíduo**, inclusive o esqueleto — vale a descrição "resíduo mais próximo", não "cadeia lateral em S1"; (b) a metade final inclui o ponto médio (t ≥ 5 ns), sem efeito prático |
| `pose_qc.py` | limiares 2,2 Å, ω ≥ 150°, quiralidade, His57–Ser195 ≤ 3,8 Å, C–N ≤ 1,5 Å | idênticos ao texto (2.5) |
| `rescore_boltz2_topk.py` | `--use_potentials`, 5 amostras × 3 sementes; controles embaralhados com semente = hash da sequência | coerente com 2.5 |
| `md_agent.py`, `build_system_charmm.py` | histórico git | **última alteração em 01/10**, antes das 48 MDs de pH 10 e das de pH 8,2: o protocolo é o mesmo nos dois pH. N-terminal: pH 10 usou "charged" (NH3+) por padrão; pH 8,2 usa `nterm=auto`, que também dá NH3+ (pH − 7,7 < 2); `build_report.json` mostra `ph: 8.2` |
| `prodigy_scores.py` (novo) | PRODIGY insensível à protonação (mesma ΔG antes/depois do PDB2PQR); nomes AMBER → canônicos na calibração (Ile CD → CD1 etc.) | corrigido durante o desenvolvimento (primeira versão falhava no freesasa); resultado final rodou sem erro |
| `mmgbsa_md82.py` (novo) | topologia só com as duas cadeias de proteína (a original falhava: íons na topologia); quadros 251–501 a cada 2 = 126 (5,0–10,0 ns, 40 ps); bloco Delta do CSV | testado numa trajetória de pH 10 (NGGRPDAP: −45,3 kcal/mol); parser corrigido |
| `rank_energy_stages.py` (novo) | direção de cada etapa (E2, Δ ↑; RMSD, PRODIGY ↓); postos médios com empate; portões | coerente com 2.8; usa `delta_paired_*.json` quando o CSV não tem Δ |
| `compare_ph.py` (novo) | métricas pareadas, Wilcoxon, ρ, piso de ruído | ainda **não rodado em dados reais** (aguarda as MDs de pH 8,2) |

### Desvios de protocolo (declarados)
F1/F2 (barostato Parrinello–Rahman na NPT; `refcoord_scaling` ausente) — **restaurados na limitação (vi)** do manuscrito (estavam fora da versão reescrita), com a densidade medida (1022–1033 kg m⁻³; 0,2%); o mesmo código roda pH 10,0 e 8,2.

## 4. Resultados × discussão

| Resultado (seção) | Alegação da discussão | Justificada? |
|---|---|---|
| Boltz-2 separa em 10/10 pares, valores absolutos se sobrepõem (3.2) | só vale pareado; 0,9 não é evidência de ligação (4.2) | sim |
| MM-GBSA 4/10 (ρ −0,93 com contatos) e PRODIGY 2/10 (ρ −0,79) (3.2) | "ordenam por tamanho de interface; não são afinidades" (4.2) | sim, nas duas direções: a alegação é negativa e é o que os dados dão |
| Reprodutibilidade ρ 0,57; L × M ρ 0,50 (3.4) | ruído de execução limita o ranking (4.2) | sim |
| Δ positivo em 63/78 e 60/79, da ordem do ruído (3.4) | "não pontuou abaixo do controle, não que se liga" | sim |
| Ocupância depende da distância inicial: 5/9 × 0/39, ρ 0,63/−0,63, Fisher *P* = 7 × 10⁻⁵ (3.5) | MD de 10 ns "re-relata a pose do Boltz-2" (4.1, 4.4) | sim, como descrição; **limite**: uma execução por candidato, âncora definida *post hoc*, 48 simulações não independentes do desenho |
| Controles embaralhados e de troca de âncora (7 + 8) retirados (3.5) | só divulgação em 3.5 e (vii) | sim; a retirada segue a regra de 02/10 |
| PRODIGY nas poses acompanha o comprimento (ρ −0,60) (3.6) | "ordena candidatos de tamanho parecido" (3.6, 4.4 x) | sim |
| Classificação por etapa: postos variam muito entre etapas (3.6) | "triagem grosseira, não medida" | sim |
| Lista curta de 4 peptídeos (3.8) | "sobreviveram aos filtros; sem alegação de seletividade ou atividade" (4.1, 5) | sim. **Ressalva a manter visível:** a escolha dos quatro vem da ocupância (que o próprio texto diz não discriminar) e do ranking por etapa; ela não é uma conclusão de ligação |
| Critério duro deixa peptídeos curtos e ricos em Gly (3.3) | "seleciona contra o resíduo mais apto a S1; custo entrópico provável" (4.3) | o fato (composição) é medido; "provavelmente flexíveis" é **hipótese**, assinalada como tal |

Pontos em que a discussão **vai além** dos dados (mantidos como hipótese, não como resultado): custo de entropia de ligação dos peptídeos ricos em Gly; possibilidade de um macrociclo tolerar um P1 básico; nenhum deles foi testado aqui.

## 5. O que **não** foi verificado
- Identidade de sequência da Tabela 1 (precisa da P35046 e do Biopython; não recalculada aqui).
- Detalhes de MD da calibração (2 ns, AMBER99SB-ILDN): pH confirmado nos logs; nada além disso.
- Qualidade das predições do Boltz-2 em si (não há estrutura experimental destes complexos).
- As frases com Valaitis, Yang e Zhan no nível do texto completo.
- **Resultados de pH 8,2, MM-GBSA e a comparação de pH**: ainda não existem (MDs em curso); `compare_ph.py` e a seção 3.7 ficam para depois, e o resumo, 4.1, 4.4 e 5 precisarão ser reajustados.
- A versão em português foi gerada do inglês por tradução e conferida por números nos pontos tocados hoje; uma revisão linha a linha do PT não foi feita.

# B2.7 — scoring Boltz-2 dos candidatos RESISTENTE (2026-09-28)

Pontuação real com Boltz-2 (único scorer validado em B0.5, 10/10 real-vs-decoy) dos 2.360
candidatos RESISTENTE a protease da campanha B2.3 (faixa completa 5-20aa, 7 espécies), após
o usuário cortar a etapa de calibração contra a série GORE ("Trilha B" — ver
[[feedback_foco_geracao_nao_calibracao_lalay]]): o objetivo é a tecnologia generativa, não
reproduzir inibidores conhecidos.

## Pipeline

- `scripts/precompute_receptor_msa.py` — MSA real do receptor via servidor MMseqs2
  (colabfold API), uma vez por espécie. Versionado em `data-b23-scoring/msa_cache/`.
- `scripts/score_boltz2_b23.py` — gera yaml Boltz-2 (receptor com MSA custom + peptídeo
  macrocíclico `cyclic: true` em `msa: empty`, sem homólogos reais) e consolida
  `confidence_score`/`complex_plddt`/`iptm`.
- `scripts/run_boltz2_scoring_campaign.sh` — roda as 7 espécies em `screen
  b23-boltz2-scoring`.

## Bugs reais encontrados e corrigidos

1. `_manifest.json` dentro do diretório de yaml quebra o `boltz predict` (varre TODO
   arquivo do diretório, não só `.yaml`). Fix: manifest em `_manifests/` separado.
2. **Bug do próprio Boltz-2**: `--preprocessing-threads` tem default
   `multiprocessing.cpu_count()` (32 no servidor), apesar do `--help` dizer "Default is 1"
   (bug de documentação do boltz). Com 32 processos paralelos lendo o mesmo MSA custom do
   receptor, ocorre falha intermitente real em `parse_csv.py`
   (`'tuple'/'PosixPath' object has no attribute 'islower'`) que descarta candidatos
   silenciosamente (`Skipping`). Fix: `--preprocessing-threads 4` — zero falhas em todo o
   piloto e a campanha completa.

## Resultado real (2.360/2.360 pontuados, zero falhas)

| Espécie | N pontuados | confidence média | confidence máx | top candidato |
|---|---|---|---|---|
| Sfrugiperda | 255 | 0,869 | 0,956 | GIFDDIG (7aa) |
| Slitura | 321 | 0,815 | 0,903 | TGISGK (6aa) |
| Onubilalis | 360 | 0,840 | 0,930 | NNNFGS (6aa) |
| Dsaccharalis | 366 | 0,889 | 0,954 | SSNINGK (7aa) |
| Cincludens | 333 | 0,859 | 0,948 | NNGGG (5aa) |
| Hvirescens | 312 | 0,863 | 0,930 | RPLNSATG (8aa) |
| Pxylostella | 413 | 0,880 | 0,931 | GGHTGA (6aa) |
| **Total** | **2.360** | **0,860 (mediana 0,865)** | — | — |

Distribuição: 435/2.360 (18,4%) com confidence_score ≥0,9; 2.121/2.360 (89,9%) ≥0,8;
**nenhum candidato abaixo de 0,5**. Para comparação, os inibidores reais calibrados em B0.5
(SKTI/BBI/EcTI/BPTI/SFTI-1/ApTI) ficaram na faixa 0,81-0,95, e os decoys embaralhados
tipicamente bem mais baixo — os candidatos gerados aqui caem quase todos na faixa dos
inibidores reais.

**Ressalva importante, não investigada ainda**: todos os 7 melhores candidatos (um por
espécie) são curtos (5-8aa) — pode refletir capacidade real do macrociclo curto de se
encaixar bem no bolso S1, ou um viés do Boltz-2 (peptídeos mais curtos podem ser "mais
fáceis" de prever com pLDDT alto independente de especificidade real de ligação). Não
confiar nisso como conclusão definitiva sem uma segunda linha de evidência (MD real, ver
abaixo).

## Próximo passo: MD real (1 réplica, 50ns) para o melhor candidato por espécie

Reusa `MDAgent._run_gromacs` (protocolo validado em B0.5, amber99sb-ildn/tip3p, pH 10,0 —
intestino alcalino, `config.yaml`), complexo de partida = predição COMPLETA do Boltz-2 (com
side-chains reais, não o backbone-only do RFdiffusion). `scripts/run_md_top_candidates.py`
(novo), rodando em `screen md-top-candidates`.

**Limitação real conhecida e aceita para esta rodada (decisão do usuário, 2026-09-28)**:
os PDBs preditos pelo Boltz-2 não têm registro de ligação N-C do macrociclo (sem
`CONECT`), e o `MDAgent` nunca implementou fechamento de anel na topologia GROMACS —
o `pdb2gmx` trata o peptídeo como **linear** (N-terminal/C-terminal livres, NH3+/COO-),
não o macrociclo real desenhado pelo RFdiffusion. Corrigir isso exige editar a topologia
do GROMACS pra fechar o anel (trabalho de engenharia não-trivial, nunca feito neste
projeto) — usuário optou por rodar linear mesmo, com esta ressalva explícita, em vez de
arriscar uma correção não testada numa campanha overnight. **Os resultados desta MD não
testam a estabilidade real do macrociclo — servem como sinal aproximado de
estabilidade/interação do peptídeo com o receptor, não como validação final.** Fechar o
anel corretamente na topologia fica como item de trabalho real para sessão futura.

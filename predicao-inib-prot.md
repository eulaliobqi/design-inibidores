# Prompt: Desenho Racional de Inibidores Peptídicos para Tripsinas de Lepidópteros com IA Generativa

## Objetivo
Executar um pipeline computacional para:
1. Identificar e modelar estruturas 3D de tripsinas de lepidópteros (pragas agrícolas).
2. Desenhar inibidores peptídicos candidatos usando modelos de IA generativa.
3. Validar os candidatos por docking molecular e dinâmica molecular.
4. Gerar uma lista priorizada de peptídeos para síntese e ensaios posteriores.

## Contexto Biológico
- *Alvo: Tripsinas do intestino médio de lagartas (ex.: *Spodoptera frugiperda, Anticarsia gemmatalis, Plutella xylostella).
- *Sítio ativo*: Tríade catalítica (His, Asp, Ser). Bolsão S1, subsítios S2-S4 hidrofóbicos.
- *Inibidores conhecidos*: Tripeptídeos (GORE1: V-L-K; GORE2: V-L-R) e pentapeptídeos (L-A-L-A-Y, L-A-L-A-K, L-A-L-A-L-R, T-G-P-C-K, A-V-I-M-K), sequências derivadas do loop reativo SKTI e BPTI.

## Ferramentas e Bibliotecas Permitidas
- *Modelagem de proteínas*: AlphaFold 2/3 (via ColabFold ou API), MODELLER, swiss-model.
- *IA generativa para peptídeos*: PepMLM, RFdiffusion e ProteinMPNN, EvoPepFold, ou treinamento de VAE/LSTM com dados de inibidores conhecidos.
- *Docking*: AutoDock Vina, HADDOCK, LightDock, ClusPro.
- *Dinâmica molecular*: GROMACS, AMBER (MM/GBSA).
- *Linguagem*: Python 3.10+, com pandas, numpy, biopython, scikit-learn, pytorch/tensorflow (se necessário).
- *APIs* (opcionais): Acesso a PDB, Uniprot, PubChem.

## Etapas a Serem Executadas pelo Claude Code

### 1. Levantamento e Modelagem dos Alvos
- [ ] Buscar sequências de tripsinas de lepidópteros no Uniprot ou via literatura (forneça IDs se disponíveis, senão usar NCBI). já tenho algumas modeladas.
- [ ] Para cada sequência, modelar a estrutura 3D usando *AlphaFold 2* (ColabFold local ou API). Se houver estrutura no PDB (ex.: 1AVW, 1J8I), baixá-la.
- [ ] Validar modelos com *PROCHECK* (qualidade geométrica) e *VERIFY_3D*.
- [ ] Identificar sítios ativos (com auxílio do *PyMOL* ou *PLIP*) e mapear hidrofobicidade dos subsítios S2‑S4.
- *Saída*: Arquivos PDB dos alvos, arquivo CSV com resíduos do sítio e pontuação de validação.

### 2. Coleta e Preparação de Dados para IA Generativa
- [ ] Construir um conjunto de treinamento (fonte) contendo sequências de inibidores peptídicos ativos contra tripsinas de insetos (literatura e peptídeos conhecidos, ex.: TGPCK, VPSNPQR, GORE1, GORE2, GORE3, AAAPGRR).
- [ ] Adicionar sequências de loops reativos de inibidores naturais (BPTI, SKTI) e regiões pró‑sequência da própria tripsina.
- [ ] Opcional: gerar dados negativos (peptídeos aleatórios ou inativos) para aprendizado supervisionado.
- [ ] Codificar as sequências (one‑hot, embedding ESM‑2) para uso nos modelos gerativos.
- *Saída*: Arquivo .csv ou .fasta com sequências positivas e negativas, dicionário de mapeamento.

### 3. Geração de Novos Inibidores com IA Generativa
- [ ] Utilizar *PepMLM* (pré‑treinado em peptídeos de ligação a proteínas) para gerar candidatos condicionados à sequência do domínio catalítico de cada tripsina.
- [ ] Alternativa ou complemento: Implementar um VAE simples (ou LSTM) com pytorch treinado sobre os dados coletados na etapa 2. O decoder deve gerar sequências de 5‑20 aminoácidos.
- [ ] Para cada modelo gerativo, produzir pelo menos 500 candidatos por alvo enzimático.
- [ ] Aplicar filtros: comprimento (5‑20 aa), evitar cisteínas múltiplas (estabilidade), evitar pontuação de toxicidade (usar preditor básico como ToxinPred).
- *Saída*: Arquivo .txt com lista de sequências peptídicas candidatas.

### 4. Triagem Virtual (Docking) e Filtragem Inicial
- [ ] Para cada peptídeo candidato, prever estrutura 3D (usando *AlphaFold2* ou *PEP‑FOLD3*).
- [ ] Realizar docking flexível (peptídeo flexível, enzima rígida) usando *AutoDock Vina*. Utilizar grid box centrada no sítio ativo (dimensões 25x25x25 Å).
- [ ] Extrair a afinidade de ligação (kcal/mol) para cada candidato.
- [ ] Ordenar candidatos por afinidade e inspecionar interações chave (pontes de H com Ser195, His57, Asp189, interações hidrofóbicas com resíduos do subsítio S2‑S4).
- [ ] Selecionar os 30 melhores candidatos por alvo para refino.
- *Saída*: Tabela CSV com sequência, afinidade (kcal/mol), resíduos de interação, e arquivo PDB do complexo.

### 5. Refino com Dinâmica Molecular e Cálculo de Energia Livre
- [ ] Para os top‑10 candidatos de cada tripsina, executar simulações de DM (50‑100 ns) usando *GROMACS* (solvatação TIP3P, neutralização, minimização, equilibração NVT/NPT, produção).
- [ ] Calcular MM/GBSA (com *gmx_MMPBSA*) para obter afinidade livre de ligação.
- [ ] Analisar trajectórias: RMSD, RMSF, raio de giro, número de pontes de hidrogênio.
- [ ] Refinar sequências: se houver perda de interações críticas, modificar 1‑2 resíduos (mutagênese virtual) e repetir DM.
- *Saída*: Gráficos de DM, arquivos de energia livre, lista final priorizada (top‑5 por alvo).

### 6. Documentação e Próximos Passos
- [ ] Gerar um relatório final (Markdown + tabelas) com:
  - Sequências e estruturas dos alvos.
  - Metodologia detalhada de geração de peptídeos (modelo IA, hiperparâmetros).
  - Tabela dos melhores candidatos com afinidades, interações chave e estabilidade em DM.
  - Sugestões de modificações químicas (ex.: ciclização, uso de D‑aminoácidos) para aumentar estabilidade proteolítica.
- [ ] Fornecer scripts Python comentados para reprodução do pipeline (docking, DM, análise).
- [ ] Recomendar ensaios experimentais: síntese SPFS, ensaio de inibição enzimática (Ki), bioensaios com lagartas.

## Restrições e Recursos
- *Tempo estimado*: O pipeline deve ser executável em até 2 horas (utilizando docking rápido e DM curta para prototipagem). Sugerir opções de aceleração (ex.: usar estruturas pré‑modeladas, reduzir número de candidatos).
- *Acesso a GPUs*: Preferencial, mas não obrigatório (AlphaFold pode rodar em CPU com --model_preset=monomer).
- *Limpeza*: Todos os arquivos intermediários devem ser organizados em pastas (1_models/, 2_peptides/, 3_docking/, 4_MD/).

## Critérios de Sucesso do Prompt
O Claude Code terá executado corretamente se ao final for fornecido:
1. Arquivo .md com o relatório final.
2. Pelo menos 10 sequências peptídicas inéditas, diferentes dos inibidores conhecidos.
3. Evidência de docking e DM (logs, gráficos, pontuações) para os 5 melhores.
4. Scripts prontos para serem rodados novamente.

## Instrução Final
*Claude, execute todas as etapas acima de forma autônoma. Instale os pacotes necessários (usando conda/pip) quando faltarem. Documente cada passo no chat. Ao final, entregue os resultados organizados e um resumo executivo.*
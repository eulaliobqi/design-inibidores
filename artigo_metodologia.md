# Metodologia Computacional — Design Racional de Inibidores Peptídicos de Tripsinas de Lepidoptera por IA Generativa

## 2. Material e Métodos

### 2.1 Estruturas-Alvo

Foram utilizados quatro modelos estruturais tridimensionais de tripsinas digestivas de lepidópteros-praga, denominados ACR157, QCL936, XP273 e XP352, obtidos por modelagem comparativa e refinamento por docking proteína-proteína (HADDOCK). As estruturas foram validadas previamente por análise geométrica (PROCHECK) e verificação de energia (VERIFY_3D).

### 2.2 Identificação do Sítio Catalítico e Bolso S1

O sítio ativo de cada tripsina foi mapeado com base nos resíduos catalíticos identificados por inspeção estrutural e verificação de conservação de sequência:

| Modelo  | Res. 1 (nucleofílico) | Asp (tríade) | Ser/Ala (tríade) | Esp. S1    |
|---------|----------------------|--------------|------------------|------------|
| ACR157  | His69                | Asp114       | Ser211           | Asp205     |
| QCL936  | His92                | Asp142       | Ser247           | Asp241     |
| XP273   | Tyr83*               | Asp132       | Ser234           | Ile229*    |
| XP352   | His112               | Asp166       | Ala268           | Asp262     |

*XP273 apresenta variações atípicas: Tyr83 em posição equivalente à His catalítica e Ile229 no bolso S1, sugerindo especificidade diferenciada das tripsinas canônicas.

As coordenadas cartesianas do centro de cada sítio foram calculadas como a média dos centróides dos resíduos da tríade. O centro de ligação consenso entre os quatro modelos:

**Centro consenso (X, Y, Z):** 2,607 / 4,572 / −1,885 Å

Os resíduos dentro de raio de 8,0 Å do centro consenso foram definidos como *hotspots* para ancoragem dos peptídeos.

### 2.3 Geração de Backbones Peptídicos por IA Generativa (RFdiffusion)

Backbones peptídicos foram gerados pelo modelo RFdiffusion (*Watson et al., Nature, 2023*), um modelo de difusão estrutural treinado para gerar conformações proteicas de novo condicionadas a sítios de ligação. O modelo foi instalado no servidor a partir do repositório oficial (`~/RFdiffusion`) com o checkpoint `Complex_base_ckpt.pt` (462 MB).

O processo foi configurado para o receptor ACR157 (231 resíduos, cadeia A) com os seguintes parâmetros:
- `noise_scale_ca = 0.2` — ruído nas posições Cα
- `noise_scale_frame = 0.1` — ruído nos frames de orientação
- Mapa de contigs: `A1-231/0 20-20` (receptor fixo + 20 novos resíduos binder)
- Hotspot residues: resíduos dentro de 6,0 Å do centro consenso do sítio S1
- Parâmetro obrigatório: `inference.ckpt_override_path` (instalação via pip não inclui diretório `models/`)

Foram gerados **330 backbones** para o receptor ACR157 em uma única rodada de difusão. A variação de comprimento (5, 7, 10, 12, 15 e 20 aa) foi especificada como parâmetro de configuração, porém todos os 330 backbones convergiram para binders de **20 aminoácidos** na cadeia B — limitação da configuração empregada nesta rodada. Os backbones gerados apresentam diversidade conformacional real (hélices, estruturas estendidas, *hairpins*), em contraste com os scaffolds lineares poly-Ala gerados em modo *fallback*.

Os arquivos PDB de entrada (ACR157, QCL936, XP273, XP352) foram pré-processados por `scripts/prep_pdbs.py` para correção de cadeia (blank → A) e renumeração de resíduos (início em 1), requisito do parser interno do RFdiffusion.

### 2.4 Design de Sequências por ProteinMPNN

O ProteinMPNN (*Dauparas et al., Science, 2022*) foi executado no modo real (instalado em `~/ProteinMPNN`) sobre os 330 backbones gerados pelo RFdiffusion. Cada backbone recebeu **500 sequências redesenhadas** para a cadeia binder (cadeia B, 20 aa), configuradas com temperatura de amostragem `0,1`, ruído de backbone `0,05` e exclusão de Cys/X (`--omit_AAs CX`) — restrição revista na Fase 5+ (Seção 2.11): Cys foi liberada para permitir desenho de dissulfeto estabilizador. As sequências de receptor (cadeia A) foram mantidas fixas.

**Formato de saída FASTA e extração do binder:**  
O ProteinMPNN gera sequências no formato `RECEPTOR_SEQ/BINDER_SEQ` (cadeias separadas por `/`). O módulo `_run_mpnn()` extrai a cadeia binder (parte após o último `/`) via `parts = seq.split("/"); binder = parts[-1]`. A concatenação incorreta (`replace("/","")`) foi identificada como bug crítico na sessão anterior, pois produzia sequências quiméricas receptor+binder de 240+ aa como candidatos — redesigns das tripsinas de input, não inibidores. O fix (commit `e9024bc`) garante que apenas os 20 aa desenhados para a interface sejam avaliados.

**Dataset resultante:**
- 330 backbones × 500 sequências = 165.000 brutas
- Após remoção de duplicatas: **24.513 sequências únicas de binder (20 aa)**
- Todos os binders têm comprimento homogêneo de 20 aa (limitação desta rodada — ver Seção 2.3)
- Dataset exportado: `outputs/dataset/ml_training_dataset.csv` com 41 features físico-químicas

Não foram aplicadas restrições de aminoácido na posição P1, permitindo explorar mecanismos de inibição além do competitivo clássico (modulação alostérica, bloqueio estérico, inibição mista).

### 2.5 Anotação de Features Físico-Químicas para ML/DL

Cada sequência foi anotada com **41 features** calculadas analiticamente (sem dependência de ferramentas externas):

- **Massa molecular** (Da) — soma de massas residuais + H₂O
- **Carga líquida** (pH 7) — soma de contribuições ionizáveis
- **Ponto isoelétrico (pI)** — busca binária na curva de titulação (pK: Asp=3,65; Glu=4,25; His=6,00; Tyr=10,07; Lys=10,53; Arg=12,48)
- **Hidrofobicidade** (média escala Kyte-Doolittle)
- **Índice de Boman** — potencial de ligação a proteínas (*Boman, 2003*)
- **Índice alipático** — indicador de termoestabilidade (100 × [A + 2,9V + 3,9(I+L)] / n)
- **Índice de instabilidade** (aproximado)
- **Frações por classe:** aromáticos (Y/F/W/H), hidrofóbicos (A/I/L/M/F/W/V), carregados (R/K/D/E)
- **Composição por aminoácido:** fração de cada um dos 19 aminoácidos não-Cys
- **Features binárias:** presença de C-terminal aromático, N-terminal carregado, Pro

O dataset foi exportado em formato CSV (`outputs/dataset/ml_training_dataset.csv`) com colunas de label (`vina_affinity_kcal`, `rosetta_I_sc`, `final_score`) a serem preenchidas nas etapas de validação.

### 2.6 Refinamento de Interface por PyRosetta

Os complexos tripsina-peptídeo foram submetidos a refinamento energético pelo protocolo **FastRelax** e cálculo de *interface score* pelo **PyRosetta 2026.25** (*Chaudhury et al., Bioinformatics, 2010*), instalado no servidor via `pyrosetta-installer` (Python 3.10, sem licença explícita — distribuição aberta desde 2024).

**Protocolo implementado em `_run_pyrosetta()`:**
1. Leitura do complexo receptor (cadeia A) + peptídeo all-atom (cadeia B) via `pose_from_pdb()`
2. Minimização energética com `FastRelax` (campo de força REF2015, score function padrão)
3. Cálculo do *interface score* (I_sc, kcal/mol) via `InterfaceAnalyzerMover("A_B").get_interface_dG()` — ΔΔG de dissociação A|B, valores negativos indicam binding favorável

**Construção all-atom do peptídeo:** os peptídeos foram construídos com `PeptideBuilder` (geometria de ligação ECEPP/3) e o centro de massa transladado para o sítio consenso antes do refinamento — necessário pois `FastRelax` e `InterfaceAnalyzerMover` requerem backbone completo (N, Cα, C, O) para scoring significativo. CA-only (fallback anterior) gerava I_sc artificialmente próximo a zero.

O *interface score* (I_sc, REF2015) foi registrado como feature secundária no ranking composto (peso 0,25).

### 2.7 Validação por Docking Molecular

A afinidade de ligação ao sítio S1 foi estimada por docking molecular rígido com AutoDock Vina f458505-mod (*Trott & Olson, J. Comput. Chem., 2010*). A *grid box* foi centrada nas coordenadas consenso (25 × 25 × 25 Å; exaustividade = 8). O protocolo adota **docking rígido** para os peptídeos candidatos, pois sequências com comprimento ≥ 9 aa possuem mais de 32 ligações rotacionáveis (φ + ψ + cadeia lateral), excedendo o limite interno do Vina para docking flexível. A modalidade rígida (TORSDOF = 0) é adequada para a geração de *labels* de triagem em larga escala (correlação Pearson ~0,7 com docking flexível completo para top candidatos).

**Preparação dos ligantes e receptor:**
Os peptídeos binder (20 aa, extraídos da cadeia B dos outputs ProteinMPNN) foram construídos em modo *all-atom* via PeptideBuilder, com geometria de ligação ECEPP/3. O **centro de massa** (COM) de cada estrutura peptídica foi transladado para as coordenadas do sítio catalítico consenso, garantindo que o peptídeo fique centrado na *grid box* independentemente do comprimento. A conversão para formato PDBQT foi realizada com mapeamento interno de tipos atômicos AutoDock4 (`_pdb_to_pdbqt_minimal()`), com correção do tipo `"N": "N"` (nitrogênio backbone) — o mapeamento incorreto `"N": "NA"` (sódio) causava rejeição pelo Vina com erro `unknown atom type: NA`. Os blocos `ROOT/ENDROOT/TORSDOF 0` são adicionados sistematicamente (`_ensure_ligand_pdbqt_format()` reescreve o arquivo sempre). O receptor foi preparado com OpenBabel (`-h`, sem `-xr` — a flag `-xr` gera formato de receptor sem `ROOT/ENDROOT`, incompatível com uso como ligante em testes de validação).

**Grid box adaptativa:**
O tamanho da *grid box* é calculado automaticamente em função do comprimento do peptídeo (`_adaptive_grid_size()`): tamanho = max(40 Å, comprimento × 3,6 + 8) Å. Isso garante que a conformação semi-estendida gerada pelo PeptideBuilder fique inteiramente dentro do espaço de busca do Vina em todos os comprimentos avaliados (5–20 aa).

| Comprimento (aa) | Grid box (Å³) | Comprimento extendido ~(Å) |
|---|---|---|
| 5  | 26 × 26 × 26 | 18 |
| 7  | 33 × 33 × 33 | 25 |
| 10 | 44 × 44 × 44 | 36 |
| 12 | 51 × 51 × 51 | 43 |
| 15 | 62 × 62 × 62 | 54 |
| 20 | 80 × 80 × 80 | 72 |

Em modo *fallback* (Vina não disponível), scores heurísticos foram calculados como função da carga básica, hidrofobicidade e índice de Boman, constituindo labels proxy para o treinamento inicial de modelos ML/DL.

### 2.8 Dinâmica Molecular

Os 10 melhores complexos foram submetidos a DM de 10 ns em GROMACS (*Van der Spoel et al., J. Comput. Chem., 2005*), campo de força AMBER99SB-ILDN, água TIP3P, 300 K, 1 bar. O protocolo incluiu minimização de energia (50.000 passos), equilibração NVT (50 ps) e NPT (50 ps), e produção MD (passo 2 fs, PME). Instalação no servidor: `gmx_mpi` + `mpirun -np 1` (build CUDA-MPI, GPU RTX 5070 Ti).

### 2.9 Ranking Composto e Seleção de Candidatos

Um *score* composto integra as métricas por normalização min-max:

$$S_{final} = 0{,}35 \cdot S_{Vina} + 0{,}25 \cdot S_{Rosetta} + 0{,}20 \cdot S_{H\text{-}bond} + 0{,}10 \cdot S_{RMSD} + 0{,}10 \cdot S_{básicos}$$

Os scores são reescritos nas colunas de label do CSV ML após o ranking, tornando o dataset supervisionado disponível para treinamento.

### 2.10 Implementação Computacional

Pipeline implementado em Python 3.10 como sistema **multiagente** com 10 módulos especializados (BaseAgent → agentes derivados). Cada agente opera em modo *real* (ferramenta instalada) ou *fallback* heurístico (pipeline não bloqueia). Ambiente conda `protein_design_env`, executado no servidor Debian com RTX 5070 Ti 16 GB via `conda run`. Código-fonte: https://github.com/eulaliobqi/design-inibidores

**Infraestrutura:**
- Servidor: `eulalio@200.235.143.10`, Debian, 32 cores, RTX 5070 Ti 16 GB
- Notebook local: Windows 11, RTX 2050 4 GB
- Workflow git: edição local → commit → push GitHub → `git pull` no servidor → execução

**Ferramentas instaladas no servidor (atualizado 2026-06-17):**

| Ferramenta | Status | Versão/Notas |
|---|---|---|
| Python 3.10 | ✓ | conda env `protein_design_env` |
| numpy, pandas, biopython, matplotlib | ✓ | ambiente base |
| PeptideBuilder | ✓ | geração all-atom de peptídeos |
| rdkit, pdbfixer, mdtraj, MDAnalysis | ✓ | análise estrutural |
| plip 3.0.0 | ✓ | análise de interações proteína-ligante |
| OpenBabel | ✓ | conversão PDBQT (obabel) |
| AutoDock Vina f458505-mod | ✓ | docking rígido de peptídeos |
| fpocket | ✓ | análise de bolso de ligação |
| GROMACS gmx_mpi | ✓ | CUDA-MPI, build sm_120 Blackwell |
| PyTorch 2.12.0.dev+cu128 | ✓ | CUDA 12.8, RTX 5070 Ti (Blackwell) |
| ProteinMPNN | ✓ | `~/ProteinMPNN` (git clone); 24.513 binders gerados |
| RFdiffusion | ✓ | `~/RFdiffusion`; checkpoint `Complex_base_ckpt.pt` 462 MB; 330 backbones gerados |
| PyRosetta | ✓ | `pyrosetta-2026.25+release`; `pyrosetta-installer`; FastRelax + InterfaceAnalyzerMover |
| pdb2pqr / propka | ✓ (Fase 5+, 2026-07-17) | `pdb2pqr` 3.6.2 + `propka` 3.5.1, instalados via pip em `protein_design_env` |

### 2.11 Fase 5+ — Critérios de Inibidor Ideal (Revisão de Literatura) e Ajustes de Rigidez/pH

Uma revisão de literatura direcionada (2026-07-17) sobre determinantes reais de potência e
resistência em inibidores de tripsina revelou duas lacunas metodológicas nas Fases 1-5, corrigidas
nesta seção.

**Rigidez do loop reativo (mecanismo de Laskowski).** Inibidores canônicos naturais (Kunitz,
Bowman-Birk, e principalmente o SFTI-1 de girassol — peptídeo bicíclico de 14 resíduos, uma única
ponte dissulfeto, Ki = 0,5 nM contra tripsina) alcançam potência nanomolar e resistência à
hidrólise simultaneamente porque o loop reativo é conformacionalmente travado por uma rede de
pontes de hidrogênio e uma ponte dissulfeto — não porque evitam quimicamente sítios de clivagem
(*Veer et al., Angew. Chem. Int. Ed., 2021*; revisão do mecanismo em *Mastering the Canonical
Loop of Serine Protease Inhibitors*, PLOS One, 2011). O design das Fases 1-5 usava
`--omit_AAs CX` no ProteinMPNN, excluindo Cisteína de **todo** o espaço de sequências geradas —
bloqueando estruturalmente essa estratégia. A partir desta sessão, `omit_aas` foi alterado para
`"X"` (Cys liberada), e `scripts/scan_disulfide_geometry.py` foi implementado para varrer
conformações **já simuladas por MD real** (10 ns, pós-produção) em busca de pares de resíduos com
distância Cβ-Cβ compatível com dissulfeto (3,5–7,5 Å), no estilo *Disulfide-by-Design*. Aplicado ao
candidato mais estável do pipeline (RLREELKKAEEWLEKRRKEE, RMSD 0,294 nm), o scan identificou
**11 pares geometricamente compatíveis** na conformação real; o melhor (posições 4/Glu e 6/Leu,
5,42 Å) é candidato direto para uma variante E4C/L6C a ser validada em nova rodada de MD com
formação explícita da ligação dissulfeto (`pdb2gmx -ss`, produzindo o resíduo `CYX` já definido
no campo de força `amber99sb-ildn.ff`).

**Tentativa de validação (2026-07-18) — resultado negativo, causa raiz diagnosticada.** A
primeira rodada de MD da variante E4C/L6C (`RLRCECKKAEEWLEKRRKEE`) via `--md-sequences` abortou
(SIGABRT) 6 segundos após o início do equilíbrio NVT — sem produzir dado fabricado
(`md_results.json` registrou corretamente `rmsd_avg_nm: null` com a mensagem de erro real). A
causa raiz é metodológica: `_build_complex_for_md()` reconstrói o peptídeo do zero via
`PeptideBuilder` a partir da sequência, sem partir da conformação real já equilibrada de onde a
distância de 5,42 Å foi medida — a estrutura recém-construída não tem geometria compatível com
dissulfeto entre essas posições, e forçar `-ss` sobre ela gerou clash estérico severo. Validar a
hipótese corretamente exigirá mutar os resíduos *in place* na conformação real equilibrada
(extraída da trajetória, não reconstruída do zero), tarefa de implementação ainda pendente.

**pH real do intestino de Lepidoptera.** O intestino médio de larvas de Lepidoptera é fortemente
alcalino (pH 8–11 em geral; tripsina de *Manduca sexta* tem ótimo em pH 10,5, com atividade máxima
registrada em pH 11,5 em outra espécie lepidóptera — *Lazarević, Entomol. Exp. Appl., 2015*;
tripsinas bacterianas do intestino de *A. gemmatalis* ativas em pH 7,5–10 — *Pilon et al., Arch.
Insect Biochem. Physiol., 2017*). Todas as simulações de MD das Fases 1-5 usaram os estados de
protonação padrão do `pdb2gmx` (aproximadamente neutros), sem qualquer ajuste para esse ambiente
alcalino real. A partir desta sessão, `md_agent.py` executa `pdb2pqr30 --ff AMBER --ffout AMBER
--titration-state-method propka --with-ph {config md.gut_ph, padrão 10,0}` antes do `pdb2gmx`,
renomeando resíduos titculáveis para os estados de protonação corretos nesse pH
(`HID`/`HIE`/`HIP` para His, `LYN` para Lys neutra, `ASH`/`GLH` para Asp/Glu protonados) — todos
já definidos em `amber99sb-ildn.ff/aminoacids.rtp`, confirmados por inspeção direta do arquivo no
servidor. A etapa degrada graciosamente (mantém protonação padrão) se `pdb2pqr30` falhar ou não
estiver disponível, preservando a robustez do pipeline.

**Ressalva sobre o candidato resistente da Fase 5.** O melhor candidato nativamente resistente
encontrado até agora (`SEEEVLAANEAYAAAHTAYN`, Vina real −13,40 kcal/mol, 0 sítios K/R internos —
Seção 3.10b) não contém nenhum resíduo Arg ou Lys, não podendo usar o mecanismo canônico
P1-Arg/Lys↔Asp189 assumido no restante do design. Seu mecanismo de ligação real permanece
desconhecido e não deve ser priorizado para síntese antes de investigação adicional (redocking
com análise de pose, contatos reais na interface).

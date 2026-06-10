# Metodologia Computacional — Design Racional de Inibidores Peptídicos de Tripsinas de Lepidoptera por IA Generativa

## 2. Material e Métodos

### 2.1 Estruturas-Alvo

Foram utilizadas quatro modelos estruturais tridimensionais de tripsinas digestivas de lepidópteros-praga, denominados ACR157, QCL936, XP273 e XP352, obtidos por modelagem comparativa e refinamento por docking proteína-proteína (HADDOCK). As estruturas foram validadas previamente por análise geométrica (PROCHECK) e verificação de energia (VERIFY_3D).

### 2.2 Identificação do Sítio Catalítico e Bolso S1

O sítio ativo de cada tripsina foi mapeado com base nos resíduos catalíticos identificados por análise estrutural:

| Modelo  | Res. 1 (nucleofílico) | Asp (tríade) | Ser/Ala (tríade) | Asp S1 (especificidade) |
|---------|----------------------|--------------|------------------|------------------------|
| ACR157  | His69                | Asp114       | Ser211           | Asp205                 |
| QCL936  | His92                | Asp142       | Ser247           | Asp241                 |
| XP273   | Tyr83*               | Asp132       | Ser234           | Ile229*                |
| XP352   | His112               | Asp166       | Ala268           | Asp262                 |

*XP273 apresenta variação atípica: Tyr83 em posição equivalente à His catalítica e Ile229 no bolso S1, sugerindo especificidade de substrato diferenciada em relação às tripsinas canônicas.

As coordenadas cartesianas do centro de cada sítio catalítico foram calculadas como a média dos centróides dos três resíduos da tríade. O centro de ligação consenso entre os quatro modelos foi obtido por média aritmética:

**Centro consenso (X, Y, Z):** 2,607 / 4,572 / −1,885 Å

Os resíduos localizados em raio de 8,0 Å em torno do centro de cada sítio foram definidos como *hotspots* para geração de backbones peptídicos.

### 2.3 Geração de Backbones Peptídicos por IA Generativa

Backbones peptídicos foram gerados pelo modelo RFdiffusion (*Watson et al., Nature, 2023*), um modelo de difusão baseado em redes neurais treinado para gerar estruturas proteicas condicionadas a sítios de ligação definidos. Para cada comprimento peptídico (5, 7, 10, 12, 15 e 20 aminoácidos), foram gerados 50 backbones independentes ancorados aos *hotspots* do sítio S1.

O processo de difusão foi configurado com:
- `noise_scale_ca = 0.2` — ruído aplicado às posições Cα
- `noise_scale_frame = 0.1` — ruído nos frames de orientação
- Mapa de contigs: `A1-N/0 L-L`, onde N = número de resíduos do receptor e L = comprimento do peptídeo

### 2.4 Design de Sequências por ProteinMPNN

Para cada backbone gerado pelo RFdiffusion, 30 sequências peptídicas foram projetadas pelo modelo ProteinMPNN (*Dauparas et al., Science, 2022*), um modelo de linguagem de proteínas treinado para prever sequências compatíveis com um dado backbone estrutural.

As seguintes restrições foram aplicadas:
- **Posição P1 fixada** em Arg ou Lys (especificidade do bolso S1 de tripsina por resíduos básicos)
- **Temperatura de amostragem:** 0,1 (regime conservador, alta confiança)
- **Ruído de backbone:** 0,05 Å
- **Aminoácidos excluídos:** Cys (instabilidade oxidativa) e resíduos desconhecidos
- **Bias para Arg** (+1,5) e Lys (+1,0) para favorecer interação com Asp do bolso S1

### 2.5 Refinamento de Interface por Rosetta

Os complexos tripsina-peptídeo foram submetidos a refinamento energético pelo protocolo FlexPepDock do Rosetta (*Raveh et al., PLoS Comp Biol, 2011*), que otimiza simultaneamente a conformação do backbone do peptídeo e as cadeias laterais na interface. Quando disponível, o refinamento foi realizado por FastRelax via PyRosetta. O *interface score* (I_sc, REF2015) foi extraído para cada complexo refinado.

### 2.6 Validação por Docking Molecular

A afinidade de ligação de cada peptídeo candidato ao sítio S1 foi estimada por docking molecular flexível utilizando AutoDock Vina (*Trott & Olson, J. Comput. Chem., 2010*). A *grid box* foi centrada nas coordenadas consenso do sítio catalítico (dimensões: 25 × 25 × 25 Å; exaustividade = 32). A energia de ligação predita (kcal/mol) foi registrada para os nove modos de ligação gerados.

### 2.7 Dinâmica Molecular e Cálculo de Energia Livre

Os dez melhores complexos por alvo foram submetidos a simulações de dinâmica molecular (DM) de 10 ns utilizando o pacote GROMACS (*Van der Spoel et al., J. Comput. Chem., 2005*) com campo de força AMBER99SB-ILDN e modelo de água TIP3P. O protocolo incluiu:

1. **Preparação topológica** (`pdb2gmx`, campo de força AMBER99SB-ILDN)
2. **Definição da caixa** (dodecaedro, margem mínima de 1,2 nm)
3. **Solvatação** (água TIP3P) e **neutralização** (íons Na⁺/Cl⁻, 0,15 M)
4. **Minimização de energia** (steepest descent, 50.000 passos, convergência ≤ 1.000 kJ·mol⁻¹·nm⁻¹)
5. **Equilibração NVT** (50 ps, 300 K, termostato V-rescale)
6. **Equilibração NPT** (50 ps, 300 K / 1 bar, barostato Parrinello-Rahman)
7. **Produção MD** (10 ns, passo de integração 2 fs, PME para eletrostática)

As trajetórias foram analisadas quanto a: RMSD do backbone do peptídeo, número médio de pontes de hidrogênio na interface receptor-ligante e raio de giro do peptídeo.

### 2.8 Ranking e Seleção de Candidatos

Um *score* composto foi calculado para cada candidato integrando as métricas das etapas anteriores por normalização min-max:

$$S_{final} = 0{,}35 \cdot S_{Vina} + 0{,}25 \cdot S_{Rosetta} + 0{,}20 \cdot S_{H\text{-}bond} + 0{,}10 \cdot S_{RMSD} + 0{,}10 \cdot S_{básicos}$$

onde valores maiores indicam candidatos mais promissores. Os vinte melhores candidatos foram selecionados para análise detalhada e recomendação de síntese.

### 2.9 Implementação Computacional

Todo o pipeline foi implementado em Python 3.10 como um sistema multiagente com dez módulos especializados, cada um responsável por uma etapa do fluxo computacional. O código-fonte está disponível em: https://github.com/eulaliobqi/design-inibidores

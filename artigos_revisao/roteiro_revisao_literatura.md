# Roteiro de Revisão de Literatura — Design Racional de Inibidores Peptídicos de Tripsina
# 24 artigos curados | Gerado por baixar_artigos.py

## Objetivo do estudo
Desenvolver inibidores peptídicos de tripsinas digestivas de Lepidoptera-praga (S. frugiperda, A. gemmatalis)
via pipeline multiagente de IA generativa (RFdiffusion + ProteinMPNN + PyRosetta + Vina + GROMACS).

## 1. Inibidores Peptídicos de Tripsinas de Lepidoptera (11 artigos)

### Severiche-Castro2026a
**Structure-Guided Design of an Interface-Derived Inhibitor Peptide Against Spodoptera frugiperda Digestive Trypsins**
*Severiche-Castro J et al. (2026) Arch Insect Biochem Physiol 122:e70164* | DOI: 10.1002/arch.70164
**Relevância:** ALTA — design in silico de peptídeo inibidor de tripsina de S. frugiperda; usa mesmo alvo do projeto
**Resumo:** Rational computational strategy identified PEP-11 (11-mer) targeting S. frugiperda digestive trypsin. MM/GBSA showed negative binding free energy in all replicas. Docking+MD revealed stable complex via polar and hydrophobic interactions.

### Schultz2026
**Synthetic Peptide Inhibition of Trypsin-Like Proteases in Spodoptera frugiperda: Evaluating the Influence of Gut Microbiota**
*Schultz H, Paulo DGS, Meriño-Cabrera Y et al. (2026) Arch Insect Biochem Physiol 121:e70145* | DOI: 10.1002/arch.70145
**Relevância:** ALTA — GORE1/GORE2 são os peptídeos de referência do grupo UFV; comparação direta
**Resumo:** GORE1 (Ki=1.41 mM) e GORE2 (Ki=0.49 mM) — inibição competitiva de tripsina S. frugiperda. Microbiota intestinal modula desenvolvimento larval mas não altera inibição enzimática.

### Paulo2026a
**Peptidic Product Derived from Trypsin Autolysis Modulates Insect Digestive Proteases and Supports Plant Biochemical Defense**
*Paulo DGS, Schultz H, Meriño Cabrera YB et al. (2026) Pest Manag Sci 82:4632-4647* | DOI: 10.1002/ps.70579
**Relevância:** ALTA — GORE3 ocupa mesmo sítio S1 alvo do pipeline; validação in vivo incluída
**Resumo:** GORE3 — inibidor competitivo (Ki=4.0 mM) de tripsina de S. frugiperda. Docking: ocupa subsítios S1/S1'. Reduz massa larval, prolonga período larval, mortalidade até 46.66%.

### Paulo2026b
**Peptides Derived From Reactive Center Loops Inhibit Digestive Trypsin-Like Enzymes in Lepidopteran Pests**
*Paulo DGS, Schneider JR, Meriño-Cabrera Y et al. (2026) Arch Insect Biochem Physiol 121:e70123* | DOI: 10.1002/arch.70123
**Relevância:** ALTA — estratégia RCL-derived peptide análoga ao nosso pipeline IA generativa
**Resumo:** TGPCK, TGPCR, AVIMK, AVIMR (derivados de RCL de BPTI/SKTI) inibem tripsina de A. gemmatalis competitivamente. Interações pi-sigma correlacionam com maior afinidade.

### deAndrade2026
**Expression of a Recombinant Peptide with Bioinsecticidal Potential for the Control of Agricultural Pests**
*de Andrade RJ, Meriño-Cabrera Y, Castro JS et al. (2026) Int J Biol Macromol 359:151886* | DOI: 10.1016/j.ijbiomac.2026.151886
**Relevância:** ALTA — abordagem recombinante do mesmo peptídeo GORE; prova de conceito de expressão
**Resumo:** GORE1-2T quimérico expresso em E. coli BL21. Inibição competitiva Ki≈100 µM. MD mostra backbone RMSD estável, ligações H persistentes. Seletividade para serinas de Lepidoptera.

### MerinoCabrera2020
**Rational Design of Mimetic Peptides Based on the Interaction Between Inga laurina Inhibitor and Trypsins for Spodoptera cosmioides Pest Control**
*Meriño-Cabrera Y, Severiche Castro JG, Rios Diez JD et al. (2020) Insect Biochem Mol Biol 122:103390* | DOI: 10.1016/j.ibmb.2020.103390
**Relevância:** ALTA — artigo fundador do conceito de design racional de mimético de Kunitz para Spodoptera
**Resumo:** Dois peptídeos lineares derivados da interface ILTI-tripsina. Estabilidade estrutural e propensão à conformação de ligação. Atividade inibitória sobre tripsinas digestivas e efeito tóxico em S. cosmioides.

### deAlmeidaBarros2021
**Small Peptides Inhibit Gut Trypsin-Like Proteases and Impair Anticarsia gemmatalis Survival and Development**
*de Almeida Barros R, Meriño-Cabrera Y, Vital CE et al. (2021) Pest Manag Sci 77:1714-1723* | DOI: 10.1002/ps.6191
**Relevância:** ALTA — A. gemmatalis (alvo secundário do projeto); demonstra Ki sub-mM com peptídeos curtos
**Resumo:** GORE1 (Ki=0.49 mM) e GORE2 (Ki=0.10 mM) — inibição competitiva reversível. Docking confirma ligação ao sítio ativo (His57, Asp102, Ser195). Reduz sobrevivência e desenvolvimento de A. gemmatalis in vivo.

### MerinoCabrera2022a
**Arginine-Containing Dipeptides Decrease Affinity of Gut Trypsins and Compromise Soybean Pest Development**
*Meriño-Cabrera Y, Castro JS, de Almeida Barros R et al. (2022) Pestic Biochem Physiol 184:105107* | DOI: 10.1016/j.pestbp.2022.105107
**Relevância:** MUITO ALTA — justifica seleção de Arg/Lys em top candidatos (padrão observado nos 10 resultados Vina+Rosetta)
**Resumo:** Dipeptídeos contendo Arg > Lys em afinidade pelo subsítio S1 de tripsina de A. gemmatalis (guanidínio+). Inibição competitiva in vitro; redução de trypsin, sobrevivência e peso larval in vivo.

### deAlmeidaBarros2022
**Inhibition Constant and Stability of Tripeptide Inhibitors of Gut Trypsin-Like Enzyme**
*de Almeida Barros R, Meriño-Cabrera Y, Severiche Castro JG et al. (2022) Arch Insect Biochem Physiol 109:e21887* | DOI: 10.1002/arch.21887
**Relevância:** ALTA — Ki de tripeptídeos estabelece referência para comparação com candidatos do pipeline
**Resumo:** Constantes de inibição de tripeptídeos GORE vs tripsinas de lepidópteros. Estabilidade estrutural dos peptídeos no sítio ativo.

### deAlmeidaBarros2022b
**BPTI and SKTI: Differential Effects on Proteases and Larval Development of Anticarsia gemmatalis**
*de Almeida Barros R, Meriño-Cabrera Y, Castro JS et al. (2022) Pestic Biochem Physiol 187:105188* | DOI: 10.1016/j.pestbp.2022.105188
**Relevância:** ALTA — BPTI/SKTI são as seeds positivas do dataset ML; artigo explica mecanismo diferencial
**Resumo:** BPTI evita adaptação (não há overproduction de protease). SKTI é digerido e induz overproduction. BPTI reduz trypsin, sobrevivência e peso pupal. Modelo paradigmático de inibição de referência.

### PatarroyoVargas2017
**Kinetic Characterization of Anticarsia gemmatalis Digestive Serine-Proteases and Inhibitory Effect of Synthetic Peptides**
*Patarroyo-Vargas AM, Merino-Cabrera YB, Zanuncio JC et al. (2017) Protein Pept Lett 24:1040-1047* | DOI: 10.2174/0929866524666170918103146
**Relevância:** FUNDADORA — primeiro trabalho do grupo em peptídeos inibitórios de A. gemmatalis; base do pipeline
**Resumo:** Tripsina de A. gemmatalis: maior afinidade para substratos com Arg na P1. Gor3/4/5 — inibidores lineares competitivos. Gor5 (menor Ki) interage com resíduos hidrofóbicos do subsítio S2'.

## 2. Biologia das Tripsinas Digestivas de S. frugiperda (4 artigos)

### Fuzita2022
**Proteomic Approach to Identify Digestive Enzymes and Their Secretory Routes in the Midgut of Spodoptera frugiperda**
*Fuzita FJ, Palmisano G, Pimenta DC et al. (2022) Comp Biochem Physiol B 259:110670* | DOI: 10.1016/j.cbpb.2021.110670
**Relevância:** ALTA — confirma importância das tripsinas no intestino de S. frugiperda; fundamenta escolha do alvo
**Resumo:** Identificação proteômica de enzimas digestivas no intestino médio de S. frugiperda. Tripsinas como componentes majoritários do suco intestinal. Secretadas por rota microapocrína.

### Hafeez2021
**Role of Digestive Protease Enzymes in Host Plant Adaptation of Spodoptera frugiperda**
*Hafeez M, Li XW, Zhang JM et al. (2021) Insect Sci 28:1639-1655* | DOI: 10.1111/1744-7917.12906
**Relevância:** ALTA — explica plasticidade das tripsinas de S. frugiperda; fundamenta necessidade de múltiplos candidatos
**Resumo:** Perfil de atividade de proteases digestivas no intestino de S. frugiperda durante adaptação a diferentes hospedeiros. Modulação de tripsinas e quimiotripsinas em resposta a inibidores.

### Severiche-Castro2023
**Structural Analysis and Inhibition Capacity of Dioscorin Protein Yam: Molecular Docking and Dynamics**
*Severiche-Castro J, Wilches Diaz G, Combariza Montañez AF et al. (2023) Arch Insect Biochem Physiol 113:e22025* | DOI: 10.1002/arch.22025
**Relevância:** ALTA — template estrutural usado no PMID 42138598; serve de referência para comparar nossos candidatos
**Resumo:** Dioscorina se liga a tripsinas de S. frugiperda com energia de ligação -57.3 a -66.9 kcal/mol (MM/GBSA). Dois sítios reativos; interações via ligações H, hidrofóbicas e VdW. Template estrutural para design PEP-11.

### Fonseca2023
**A Soybean Trypsin Inhibitor Reduces the Resistance to Transgenic Maize in Spodoptera frugiperda**
*Fonseca SS, Santos ALZ, Pinto CPG et al. (2023) J Econ Entomol 116:2087-2094* | DOI: 10.1093/jee/toad188
**Relevância:** MÉDIA — demonstra aplicabilidade de inibidores de tripsina em contexto de praga de campo
**Resumo:** Inibidor de tripsina de soja (STI) reduz resistência de S. frugiperda ao milho Bt-transgênico. Sinergia entre inibidores endógenos de plantas e toxinas Bt para controle de praga.

## 3. Metodologia de IA Generativa Estrutural (3 artigos)

### Watson2023
**De Novo Design of Protein Structure and Function with RFdiffusion**
*Watson JL, Juergens D, Bennett NR et al. (2023) Nature 620:1089-1100* | DOI: 10.1038/s41586-023-06415-8
**Relevância:** METODOLÓGICA CRÍTICA — artigo fundador do RFdiffusion usado no pipeline (etapa 2)
**Resumo:** RFdiffusion: fine-tuning de RoseTTAFold em denoising de backbones. Gera binders de novo com alta especificidade. Confirmado por cryo-EM. Suporta design de oligômeros, proteínas de simetria, binders peptídicos.

### Dauparas2022
**Robust Deep Learning-Based Protein Sequence Design Using ProteinMPNN**
*Dauparas J, Anishchenko I, Bennett N et al. (2022) Science 378:49-56* | DOI: 10.1126/science.add2187
**Relevância:** METODOLÓGICA CRÍTICA — artigo fundador do ProteinMPNN usado no pipeline (etapa 3)
**Resumo:** ProteinMPNN: deep learning para design de sequências dado backbone. 52.4% de sequence recovery (vs 32.9% Rosetta). Validado por cristalografia, cryo-EM e estudos funcionais.

### VazquezTorres2024
**De Novo Design of High-Affinity Binders of Bioactive Helical Peptides**
*Vázquez Torres S, Leung PJY, Venkatesh P et al. (2024) Nature 626:435-442* | DOI: 10.1038/s41586-023-06953-1
**Relevância:** ALTA — exemplo de aplicação combinada RFdiffusion+ProteinMPNN para peptídeos binders (análogo ao projeto)
**Resumo:** Design de binders de alta afinidade para peptídeos helicoidais bioativos usando RFdiffusion+ProteinMPNN. Validado experimentalmente por cristalografia e ensaios de ligação.

## 4. Defesa Vegetal por Inibidores de Protease (Kunitz/Bowman-Birk) (3 artigos)

### Liu2026
**Induced Bowman-Birk Trypsin Inhibitor TaBBTI-1 in Wheat During Poor-Host Interactions with Aphids**
*Liu X, Zhang Y, Francis F et al. (2026) Int J Biol Macromol:150204* | DOI: 10.1016/j.ijbiomac.2026.150204
**Relevância:** MÉDIA — BBTIs como proteínas de referência; mecanismo análogo ao objetivo do projeto
**Resumo:** Bowman-Birk trypsin inhibitor TaBBTI-1 em trigo — induzido por herbivoría; resistência de amplo espectro a insetos. Mecanismo via inibição de serinas digestivas.

### Das2025
**Divergent Functions of Three Kunitz Trypsin Inhibitor (KTI) Proteins in Herbivore Defense in Poplar**
*Das IS, Shi Q, Dreischhoff S et al. (2025) BMC Plant Biol 25:e07955* | DOI: 10.1186/s12870-025-07955-z
**Relevância:** MÉDIA — diversidade funcional de KTIs; suporta necessidade de design específico por espécie-alvo
**Resumo:** KTIs em Populus com funções divergentes na defesa contra herbívoros Lepidoptera. Especificidade de inibição depende de diferenças no RCL e bolso S1.

### Li2025
**A Natural Variant of MYC2 in Soybean Contributes to Resistance Against the Common Cutworm**
*Li X, Hu D, Yang Z et al. (2025) Proc Natl Acad Sci USA 122:e2424956122* | DOI: 10.1073/pnas.2424956122
**Relevância:** MÉDIA — contexto de resistência de plantas a Spodoptera; justifica design de inibidores
**Resumo:** Variante natural de MYC2 em soja ativa cascade de defesa contra Spodoptera (cutworm). Inibidores de protease são componentes da resposta defensiva.

## 5. Controle Biológico e Manejo de Spodoptera (3 artigos)

### GarciaMunguia2025
**Baculovirus-Based Biocontrol: Synergistic and Antagonistic Interactions of PxGV, PxNPV, SeMNPV, SfMNPV**
*García-Munguía AM, García-Munguía CA, Guerra-Ávila PL et al. (2025) Viruses 17:1077* | DOI: 10.3390/v17081077
**Relevância:** MÉDIA — contexto de biocontrole; alternativa biológica ao controle químico (manejo integrado)
**Resumo:** Baculovírus como agentes de biocontrole de lepidópteros. SfMNPV específico para S. frugiperda. Interações sinérgicas e antagônicas com outros vírus.

### ElSaid2025
**Lethal and Sublethal Effects of Chemical and Bio-Insecticides on Spodoptera frugiperda Adults**
*El-Said NA, Alfuhaid NA, Chellappan BV et al. (2025) Front Plant Sci 16:1694032* | DOI: 10.3389/fpls.2025.1694032
**Relevância:** MÉDIA — panorama de estratégias de controle; posiciona inibidores de protease como alternativa
**Resumo:** Efeitos letais e subletais de inseticidas químicos e biológicos em S. frugiperda adultos. Bio-inseticidas reduzem fecundidade e fertilidade.

### VandenBerg2022
**A Special Collection: Spodoptera frugiperda (Fall Armyworm): Ecology and Management**
*Van den Berg J, Brewer MJ, Reisig DD et al. (2022) J Econ Entomol 116:1-5* | DOI: 10.1093/jee/toac143
**Relevância:** MÉDIA — revisão abrangente de manejo; contexto geral para justificativa do projeto
**Resumo:** Revisão compilada de ecologia e manejo de S. frugiperda (fall armyworm). Coleção especial do J Econ Entomol.

## Pontos de discussão sugeridos

### 1. Justificativa do alvo (tripsinas S. frugiperda / A. gemmatalis)
- Citar Fuzita2022 (proteômica), Hafeez2021 (adaptação), Patarroyo2017 (cinética)
- Resíduos catalíticos His/Asp/Ser; bolso S1 (Asp205 ACR157) — especificidade por Arg/Lys

### 2. Estado da arte em inibidores peptídicos (grupo Meriño-Cabrera/UFV)
- Linha: ILTI -> GORE1/2 -> GORE3 -> GORE1-2T recombinante -> PEP-11 guiado estruturalmente
- Padrão consistente: Ki sub-mM, inibição competitiva, interação com Asp189 (S1)
- Nosso pipeline avança: 24.513 candidatos por IA generativa vs. design manual

### 3. Vantagem do design por IA generativa
- Watson2023 (RFdiffusion) + Dauparas2022 (ProteinMPNN): backbones de novo condicionados ao sítio
- VazquezTorres2024: prova de conceito para peptide binders de alta afinidade
- Comparar com abordagem RCL (Paulo2026b) e mimético de Kunitz (MerinoCabrera2020)

### 4. Argumento Arg/Lys (respaldado por literatura)
- MerinoCabrera2022a: Arg >> Lys em afinidade (guanidínio²⁺ vs. amônio⁺ no S1)
- Padrão observado nos top-10 candidatos (Vina + Rosetta): todos Arg/Lys-rico, sem aromáticos
- Concordância com seleção natural de inibidores (BPTI usa Lys15/Arg17)

### 5. Validação in silico -> in vitro (plano experimental futuro)
- MD 10 ns: estabilidade do complexo (RMSD < 2 Å, H-bonds persistentes)
- Ki estimado -> síntese Fmoc-SPPS -> ensaios IC50 vs. tripsinas recombinantes
- Comparar Ki obtidos com GORE1 (1.41 mM) e GORE2 (0.49 mM) como referência
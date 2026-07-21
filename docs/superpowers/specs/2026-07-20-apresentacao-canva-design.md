# Design — Apresentação Canva (3/3 entregáveis, 2026-07-20)

## Contexto

Terceiro e final dos 3 entregáveis pedidos pelo usuário (Figuras → Word → **Apresentação**). Os anteriores estão concluídos: Figuras (4 PNGs em `outputs/figuras_artigo/`) e Word (`artigo_design_inibidores.docx`). Esta apresentação consolida o artigo em formato de seminário/documentação de projeto via **Canva API**, ~22 slides, template Academic Presentation (formal).

Após este entregável, consolidar tudo e encerrar a sessão — instrução explícita do usuário (2026-07-20).

## Decisões aprovadas com o usuário

- **Finalidade**: documentação do projeto (relatório de progresso interno, seminário/defesa).
- **Público**: orientador, banca, equipe.
- **Arquitetura**: Problema (2-3 slides) → Solução/Pipeline (3-4) → Métodos (2-3) → Resultados (10-12) → Conclusões (2) → Próximos passos (1) = ~22 slides.
- **Densidade textual**: Título + bullet points (3-5 bullets) + 1 imagem (balanço, não minimalista, não denso).
- **Template Canva**: "Academic Presentation" (formal científico).
- **Figuras**: 4 PNGs já geradas (`fig1_replicas_md.png`, `fig2_ocupancia_s1.png`, `fig3_cross_species.png`, `fig4_fingerprint.png`) + ilustrações stock do Canva (insetos, proteínas, ícones, fluxogramas, gráficos).
- **Conteúdo**: derivado do `artigo_design_inibidores.docx` (números reais, sem especulação).
- **Tom**: formal científico, rigoroso.

## Estrutura slide-by-slide (22 slides)

### CAPA (Slide 1)

**Título:** Design Racional de Inibidores Peptídicos de Tripsinas de Lepidoptera por IA Generativa

**Subtítulo:** Universidade Federal de Viçosa | 2026

**Bullets:** (none)

**Imagem:** stock Canva — inseto Lepidoptera (lagarta) + estrutura de proteína em 3D (estilo molecular)

---

## SEÇÃO 1: PROBLEMA (Slides 2–4)

### Slide 2: Desafio de Controle — Resistência a Bt e Inseticidas

**Bullets:**
- Lepidópteros-praga (*Spodoptera frugiperda*, *Anticarsia gemmatalis*) causam perdas significativas em culturas
- Resistência crescente a toxinas Bt e inseticidas químicos
- Necessidade de estratégias complementares de controle

**Imagem:** stock Canva — campo de soja/milho + inseto praga (clipart ou foto)

---

### Slide 3: Estratégia Alternativa — Inibidores de Proteases Digestivas

**Bullets:**
- Tripsinas: enzimas centrais na digestão de proteínas em larvas de Lepidoptera
- Inibidores de proteases = bloqueio direto da fisiologia digestiva
- Precedente natural: inibidores Kunitz/BPTI (comprovados em literatura)
- Atividade real documentada: inibição tight-binding + sinergia com Bt

**Imagem:** stock Canva — diagrama simplificado de trato digestivo/proteases (ícone)

---

### Slide 4: Lacuna do Projeto — Design Computacional de Novos Peptídeos

**Bullets:**
- Inibidores naturais enfrentam limitações: suscetibilidade a clivagem proteolítica
- IA generativa para design de proteínas abre alternativa: gerar peptídeos inéditos computacionalmente
- Validação rigorosa in silico em cada etapa (não apenas escore estático)
- Objetivo: candidatos reprodutivelmente estáveis + específicos + resistentes

**Imagem:** stock Canva — ícone de IA/computador + proteína estrutural (símbolo de design)

---

## SEÇÃO 2: SOLUÇÃO & PIPELINE (Slides 5–8)

### Slide 5: Pipeline Multiagente — Arquitetura

**Bullets:**
- 10 agentes especializados orquestrando fluxo end-to-end
- Etapas: geração de backbones → design de sequência → docking → dinâmica molecular → análise integrada

**Imagem:** Diagrama de fluxo (criar no Canva ou usar como imagem estática):
```
RFdiffusion (330 backbones)
  ↓
ProteinMPNN (120k+ sequências)
  ↓
Vina Docking (880 poses)
  ↓
Ranking & Seleção
  ↓
MD GROMACS (n=3 réplicas por candidato TOP-13)
  ↓
Análise Persistência + Especificidade + Resistência
```

---

### Slide 6: RFdiffusion & ProteinMPNN — Geração de Candidatos

**Bullets:**
- **RFdiffusion** (Yang et al. 2024): geração de novo de estruturas peptídicas ancoradas ao sítio catalítico → **330 backbones reais**
- **ProteinMPNN** (Dauparas et al. 2023): design de sequência sobre cada backbone → **24.513 peptídeos de 20 aa** (+ variantes curtas 5–7 aa)
- Filtros iniciais: compatibilidade estrutural com sítio, ausência de P1-internos óbvios

**Imagem:** stock Canva — logo/ícone de RFdiffusion + ProteinMPNN (ou representação abstracta de rede neural)

---

### Slide 7: Validação In Silico — Docking + Dinâmica Molecular

**Bullets:**
- **Docking molecular (AutoDock Vina)** → 880 poses válidas contra ACR157 (receptor primário)
- **Dinâmica molecular (GROMACS, CHARMM36 + CGenFF)** → replica real n=3 (100 ns cada)
- Métricas: RMSD (estabilidade estrutural), ocupância do sítio S1 (persistência funcional)
- Replica-to-replica concordância como validação de reprodutibilidade

**Imagem:** stock Canva — dinâmica molecular (partículas, trajetória, ou ícone de simulação)

---

### Slide 8: Critérios Reais — Estabilidade, Especificidade, Resistência

**Bullets:**
- **Estabilidade reprodutível**: RMSD < 0,05 nm DP entre 3 réplicas (n=13 TOP-13)
- **Especificidade**: Seletividade índice (SI) ≥ 2,0 kcal/mol vs. tripsina humana + *Apis mellifera* (não-alvos)
- **Resistência proteolítica**: ausência de P1-internos básicos reconhecíveis (K/R) — proteção vs. autoclivagem
- **Cross-species**: afinidade mantida contra 11 espécies-praga de Lepidoptera (amplo espectro)

**Imagem:** stock Canva — quadro/checklist de critérios (visual clean, ícones por critério)

---

## SEÇÃO 3: MÉTODOS (Slides 9–11)

### Slide 9: Estruturas-Alvo & Sítio Catalítico

**Bullets:**
- **4 receptores primários**: ACR157, QCL936, XP273, XP352 (tripsinas de Lepidoptera)
- Tríade catalítica conservada: His–Asp–Ser (posição única em todos, verificada)
- Bolso de especificidade S1: resíduo Asp em 3 receptores (XP273: Tyr atípico, documentado)

**Imagem:** stock Canva — estrutura de proteína 3D (use imagem/ícone de proteína do Canva, não inserir PDB real — ícone abstracto apenas) + tabela resumida (Modelo | Tríade | S1)

---

### Slide 10: Protocolo MD & Análise de Persistência

**Bullets:**
- Dinâmica molecular: GROMACS + CHARMM36/CGenFF5.0, ensemble NPT, 100 ns por réplica
- Análise de persistência: ocupância do complexo peptídeo-receptor em raios 4 Å / 5 Å / 6 Å vs. resíduo âncora (Asp P1 bolso)
- Métrica: % de frames em que peptídeo permanece dentro do raio (indicador de permanência real no sítio catalítico)

**Imagem:** stock Canva — ícone de biomol/trajectória (abstracto)

---

### Slide 11: Especificidade Cross-Species

**Bullets:**
- Docking contra 11 espécies-praga adicionais: *D. saccharalis*, *H. virescens*, *C. includens*, etc. (receptores reais de literatura/UniProt)
- Métrica: Seletividade Índice (SI) = Vina(não-alvo humano) − Vina(alvo primário) — valores ≥ 2,0 kcal/mol = especificidade confirmada
- Cross-species: afinidade mantida contra múltiplas praga (requisito R3)

**Imagem:** stock Canva — mapa do Brasil + múltiplos insetos (representação de espécies diferentes)

---

## SEÇÃO 4: RESULTADOS (Slides 12–20)

### Slide 12: Overview dos Candidatos — Fingerprint dos 5 Top

**Bullets:**
- TOP-5 candidatos por reprodutibilidade + persistência: SRTRR, VRYRR, VRRPR, HRPRRPR, HRPRRSR
- Síntese de métricas: RMSD médio, ocupância S1 @ 6 Å, SI mínimo
- Contato com tríade catalítica: verificado via PLIP (interações reais)

**Imagem:** **FIG 4 (fingerprint)** — tabela visual com 5 candidatos, barras de ocupância, RMSD, contato (jpg/png já gerado)

---

### Slide 13: Reprodutibilidade MD — Réplicas Reais (n=3)

**Bullets:**
- TOP-13 candidatos rodados em triplicate (rep1, rep2, rep3, sementes -1)
- **Achado-chave**: 2 "recordistas de estabilidade" de réplica única (RLREELKKAEEWLEKRRKEE 0,294 nm; VRTRR 0,194 nm) mostraram DP real de 0,606 nm e 0,360 nm — resultado NÃO reprodutível
- **Apenas 4 candidatos confirmam estabilidade real** (DP < 0,05 nm): SRTRR, VRYRR, VRRPR, HRPRRPR
- Conclusão: estabilidade em réplica única não é confiável isoladamente

**Imagem:** **FIG 1 (réplicas MD)** — gráfico de barras RMSD médio ± DP por candidato, com anotação dos 2 "refutados" (jpg/png já gerado)

---

### Slide 14: Persistência de Contato — Ocupância do Bolso S1

**Bullets:**
- Análise de ocupância: % de frames em que peptídeo permanece no bolso S1 (raios 4/5/6 Å)
- **VRRPR paradoxo**: RMSD global estável (0,268 nm, DP 0,01 nm), MAS ocupância a 6 Å cai dramáticamente entre réplicas (67,6% → 32,9% → 0,15%)
- **VRYRR destaque**: ocupância ~100% mesmo no corte mais estrito (4 Å), salt-bridge real (Lys-Asp) nas 3 réplicas
- Conclusão: baixa variância estrutural ≠ permanência funcional no sítio catalítico

**Imagem:** **FIG 2 (ocupância S1)** — gráfico agrupado (3 séries 4/5/6 Å) com VRRPR e VRYRR destacados (jpg/png já gerado)

---

### Slide 15: SRTRR — Candidato de Referência

**Bullets:**
- Sequência: SRTRR (5 aa, comprimento ótimo)
- RMSD: 0,2425 nm (DP 0,0178 nm) — estável reprodutível
- Vina: −10,31 kcal/mol (ACR157)
- Ocupância S1 @ 6 Å: ~80% (persistência confirmada)
- SI mínimo: 1,17 kcal/mol (margem de especificidade)

**Imagem:** stock Canva — proteína + checkmark/aprovado (ícone)

---

### Slide 16: VRYRR — Melhor em Especificidade & Persistência

**Bullets:**
- Sequência: VRYRR (5 aa)
- RMSD: 0,1985 nm (DP 0,0134 nm) — muito estável
- Vina: −10,22 kcal/mol
- **Ocupância S1 @ 4 Å: ~100%** — salt-bridge Lys(peptídeo)–Asp187(bolso) nas 3 réplicas
- SI mínimo: 0,92 kcal/mol

**Imagem:** stock Canva — proteína + star/destaque (ícone)

---

### Slide 17: HRPRRPR — Afinidade Excelente, 7 aa

**Bullets:**
- Sequência: HRPRRPR (7 aa)
- RMSD: 0,2659 nm (DP 0,0181 nm) — estável
- Vina: −11,72 kcal/mol (segunda melhor afinidade do TOP-13)
- Ocupância S1 @ 6 Å: ~75%
- SI mínimo: 1,41 kcal/mol (melhor especificidade entre 7 aa)

**Imagem:** stock Canva — proteína com seta/melhoria (ícone)

---

### Slide 18: Matriz Cross-Species — 13 Candidatos × 11 Espécies

**Bullets:**
- Docking contra 11 espécies-praga adicionais (verificação de amplo espectro)
- **143 dockings reais** executados (13 × 11 matriz completa)
- Colormap heatmap: azul claro (afinidade fraca) → azul escuro (afinidade forte)
- Candidatos reordenados por média Vina geral (mais negativos = mais eficazes)

**Imagem:** **FIG 3 (heatmap cross-species)** — matriz 13 × 11 com gradiente azul, labels de candidatos e espécies (jpg/png já gerado)

---

### Slide 19: Bloqueadores Atuais — Especificidade & Resistência

**Bullets:**
- **Especificidade**: 0/23 candidatos aprovados (SI ≥ 2,0 kcal/mol) — margem de seletividade insuficiente frente a não-alvos
- **Resistência proteolítica**: 0/20 top-20 resistentes a autoclivagem por P1-internos básicos (K/R)
- Candidato SEEEVLAANEAYAAAHTAYN: ausência de P1-internos (resistência estrutural real), MAS sem margem de especificidade comprovada
- Ambos bloqueadores precisam ser resolvidos simultaneamente para aprovação de síntese

**Imagem:** stock Canva — ícone de bloqueio/X/aviso (representar obstáculos)

---

### Slide 20: Achado-Chave — Por Que Reprodutibilidade Importa

**Bullets:**
- VRRPR demonstra que estabilidade global (RMSD baixo) pode mascarar falha funcional local
- Sem réplicas independentes, este candidato seria classificado como "estável" e potencialmente sintetizado
- Validação cruzada (n=3) revelou ocupância P1 colapsando de 67,6% para 0,15% entre réplicas
- **Lição metodológica**: réplicas em silico = essencial antes de síntese experimental

**Imagem:** **FIG 2 destacada** — focus no gráfico de VRRPR com anotação de queda de ocupância (versão recortada do slide 14)

---

## SEÇÃO 5: CONCLUSÕES (Slides 21–22)

### Slide 21: Conclusões — Metodologia Rigorosa

**Bullets:**
- Pipeline multiagente integrou IA generativa, dinâmica molecular e validação cruzada
- **330 backbones + 120k+ sequências** reduzidas a TOP-13 pela reprodutibilidade real
- Tríade catalítica verificada independentemente (bug real detectado + corrigido em H. virescens)
- Cada etapa computacional submetida a validação cruzada (não opcional)
- Candidatos reprodutivelmente estáveis: SRTRR, VRYRR, VRRPR, HRPRRPR (base sólida para síntese)

**Imagem:** stock Canva — ícone de verificação/validação (checkmark)

---

### Slide 22: Próximos Passos

**Bullets:**
- **Curto prazo**: resolução simultânea de especificidade (SI ≥ 2,0) e resistência proteolítica
- **Médio prazo**: síntese química e validação experimental (bioensaios contra tripsinas reais)
- **Longo prazo**: otimização contra múltiplas espécies-praga + formação de adjuvantes

**Imagem:** stock Canva — seta/caminho para frente, fases futuras (ícone ou diagrama)

---

## Requisitos técnicos para Canva API

- **Template**: "Academic Presentation" — formal, cores neutras/institucionais (azul + branco)
- **Tipografia**: sans-serif (Canva default — Arial, Roboto, ou similar)
- **Inserção de imagens**:
  - 4 PNGs já geradas (`outputs/figuras_artigo/fig*.png`) — inserir em tamanho "full-width" nas slides respectivas (12, 13, 14, 18)
  - Stock images Canva — selecionar por tema (inseto, proteína, ícones, gráficos) em cada slide
- **Resolução**: slides em 16:9 (padrão)
- **Saída final**: PDF + arquivo Canva (link compartilhável ou arquivo de dados Canva)

---

## Verificação

- [ ] 22 slides gerados (contagem exata)
- [ ] 4 PNGs embutidas nas slides corretas (12, 13, 14, 18)
- [ ] Cada slide tem título + 3-5 bullets + 1 imagem (balanço)
- [ ] Nenhum dado fabricado — todos os numbers rastreáveis a `artigo_design_inibidores.docx` ou tabelas do artigo
- [ ] Slides 2-4 (Problema) têm contexto biológico claro
- [ ] Slides 5-8 (Pipeline) descrevem a arquitetura técnica completa
- [ ] Slides 9-11 (Métodos) suficientes para reprodutibilidade
- [ ] Slides 12-20 (Resultados) seguem ordem lógica (overview → reprodutibilidade → persistência → indivíduos → matriz → bloqueadores → síntese)
- [ ] Slides 21-22 (Conclusões) sintetizam achados reais, sem especulação
- [ ] Arquivo Canva compartilhável com user (link + PDF exportado)

---

## Fora de escopo

- Animações ou transições elaboradas
- Vídeo ou áudio embarcado
- Novas análises ou figuras além das 4 já geradas
- Reformatação de dados para outros formatos de visualização

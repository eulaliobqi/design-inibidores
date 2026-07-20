# Design — Artigo Completo em Word (2/3 entregáveis, 2026-07-20)

## Contexto

Segundo dos 3 entregáveis pedidos pelo usuário (Figuras → **Word** → Apresentação, ordem
aprovada). O primeiro (Figuras) está concluído — `outputs/figuras_artigo/fig1-4.png`, dado real,
revisado. Este entregável consolida `artigo_metodologia.md`, `artigo_resultados.md` e
`references.md` (documentos de trabalho em Markdown, fonte de verdade do conteúdo científico) num
artigo completo em `.docx`, com Introdução e Conclusão escritas nesta etapa (não existem ainda em
lugar nenhum).

Após este entregável, o próximo passo é a Apresentação (via API do Canva). Quando os 3 estiverem
prontos, consolidar tudo e encerrar a sessão — instrução explícita do usuário.

## Decisões já confirmadas com o usuário

- **Finalidade**: relatório de progresso interno (orientador/uso próprio) — não é submissão a
  periódico específico, não precisa seguir normas rígidas de nenhum journal.
- **Formato de citação**: manter como já está em `references.md` (numerado [1]-[27], estilo
  próximo de Vancouver) — não reformatar para ABNT/APA.
- **Introdução e Conclusão**: escritas do zero nesta etapa. Toda afirmação precisa rastrear a uma
  referência real de `references.md` (Introdução) ou a um resultado já documentado em
  `artigo_resultados.md`/`artigo_metodologia.md`/memória do projeto (Conclusão) — nunca um
  achado, número ou referência nova inventada.
- **Resultados e Discussão**: mantido combinado, seção-a-seção, como já está estruturado em
  `artigo_resultados.md` — não separar em blocos distintos.
- **Figuras**: inseridas dentro das seções correspondentes do texto (não em bloco único no fim):
  - `fig1_replicas_md.png` → Seção 3.11f (Réplicas Reais de MD)
  - `fig2_ocupancia_s1.png` → Seção 3.11g (Persistência Competitiva Real)
  - `fig4_fingerprint.png` → Seção 3.11i (Assinatura Digital de Interação)
  - `fig3_cross_species.png` → Seção 3.11j (Fechamento do R3 — Matriz Cross-Species)
- **Saída**: `artigo_design_inibidores.docx`, raiz do repositório.

## Estrutura do documento

1. **Capa** — título, autor, instituição (UFV), data.
2. **Introdução** (nova) — contextualiza tripsinas de Lepidoptera como alvo de controle de
   pragas, a lacuna que o design racional de inibidores preenche, objetivos do trabalho. Fonte:
   `references.md` (as 27 refs já verificadas, priorizando as da seção "I. Alvo biológico" e
   correlatas) — nenhuma referência nova.
3. **2. Material e Métodos** — conteúdo integral de `artigo_metodologia.md` (Seções 2.1-2.12),
   convertido preservando tabelas e formatação.
4. **3. Resultados e Discussão** — conteúdo integral de `artigo_resultados.md` (Seções 3.1-3.11j
   + Conclusões Parciais já existentes na Seção 4 desse arquivo, renumerada conforme necessário),
   com as 4 figuras inseridas nos pontos indicados acima.
5. **Conclusões** (nova) — síntese dos achados reais já documentados, incluindo os fechados nesta
   sessão (n=3 completo para os 13 candidatos, tríades de D. saccharalis/C. includens
   confirmadas corretas, achados de VRRPR/VRTRR/SARESIKKAYKTFLERYKKL). Fonte: conteúdo já
   existente em `artigo_resultados.md` e na memória do projeto — síntese, não nova análise.
6. **Referências** — as 27 de `references.md`, mesmo formato numerado, sem reformatação.

## Abordagem técnica

**python-docx** (já instalado, v1.2.0), mesmo padrão já usado pelo usuário em outros projetos
(Marcela TCC, Kerson-paper). Um script Python lê os 3 arquivos Markdown fonte, converte cabeçalhos
(`##`/`###`) em estilos de título do Word, tabelas Markdown (`| ... |`) em tabelas nativas do
Word, insere as 4 figuras via `document.add_picture()` nos pontos indicados, e escreve
Introdução/Conclusões diretamente como parágrafos novos (não convertidos de Markdown, já que não
existem em Markdown ainda).

**Aplicação do humanizer**: por regra de memória do usuário (cross-project), o texto novo
(Introdução e Conclusões) passa pelo processo de humanização antes de ser considerado pronto —
não se aplica ao conteúdo já existente de Resultados/Metodologia (que já é texto científico
estabelecido, não gerado nesta etapa).

## Verificação

- Abrir o `.docx` gerado (ou extrair texto/estrutura via python-docx) e conferir: nenhuma tabela
  quebrada na conversão (contagem de linhas/colunas bate com a fonte Markdown), as 4 figuras
  aparecem nas seções corretas, a Introdução não cita nenhuma referência fora das 27 de
  `references.md`, a Conclusão não menciona nenhum número/achado que não apareça em
  `artigo_resultados.md`.
- Contagem de seções do Word conferida contra a contagem de `##`/`###` dos 2 arquivos-fonte —
  nenhuma seção pode ficar de fora silenciosamente.

## Fora de escopo

- Apresentação/Canva — spec própria, próximo entregável.
- Reformatação de citações para ABNT/APA — decisão explícita de manter o formato atual.
- Separação de Resultados e Discussão em blocos distintos — decisão explícita de manter
  combinado.
- Qualquer nova análise/figura além das 4 já geradas — este entregável é só consolidação do que
  já existe.

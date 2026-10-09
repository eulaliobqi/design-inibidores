# Risco de clivagem dos candidatos finais (08/10/2026)

## Geometria de ataque da Ser195 nas MDs existentes
`scripts/scissile_geometry.py` (saída em `data-e2-results/scissile_geometry.json`): para cada ligação peptídica, na 2ª metade de cada MD (md10, md82 e as segundas sementes), distância Ser195 OG–C da carbonila, ângulo OG···C=O, distância ao buraco do oxiânion (N de Gly193 e Ser195) e fração de quadros "quase de ataque" (NAC: d < 3,5 Å, ângulo 90–125°, d_oxi < 3,5 Å). Descritivo; sem linha de base com um substrato/inibidor conhecido.
- GGKPGEP (4 execuções): ligação K3–P4 a 5,3–5,4 Å (mediana, pH 10,0 run1/run2), mínimo 3,84–4,17 Å; nenhum quadro NAC em nenhuma execução. A carbonila mais próxima da Ser195 é a da Gly2 (ligação G2–K3), 4,8–5,3 Å.
- NGGRPDAP (4 execuções): R4–P5 a 4,7–5,0 Å (mínimo 4,2–4,4 Å), NAC 0. A ligação mais próxima é G3–R4 (3,5–4,3 Å; <4 Å em 19–88% dos quadros), com NAC 0,000–0,016; Gly em P1 não é sítio de tripsina.
- PISQIDSGSR: ligação S9-R10 e R10–P1 sem aparecer entre as duas mais próximas (≥ 6 Å); Arg não está em posição de ataque.
- GGHSE, GQNDS: nenhum quadro NAC.
- Leitura: nos 10 ns simulados a Ser195 não se aproxima da ligação K/R–Pro em orientação de ataque; o registro do peptídeo parece deslocado de um resíduo em relação ao de um substrato canônico (a carbonila mais próxima é a anterior à âncora). Não prova resistência: simulação clássica não descreve a catálise e a pose é a do Boltz-2.

## Literatura verificada (PubMed)
- Rodriguez et al. 2008, J Proteome Res 7:300 (doi 10.1021/pr0705035; PMID 18067249): 14,5 milhões de espectros mostram "surpreendente número" de clivagens antes de Pro; a regra de Keil (sem clivagem K/R–P) não é absoluta.
- Pan et al. 2014, Anal Bioanal Chem 406:6247 (doi 10.1007/s00216-014-8071-6; PMID 25134673): Arg é clivada mais rápido que Lys; sítios com vizinhos carregados (D/E/K/R) ou prolina são clivados mais devagar (não zero).
- Song & Markley 2003, Biochemistry 42:5186 (doi 10.1021/bi034041u; PMID 12731859): inibidores de mecanismo padrão ligam-se como substratos e são clivados no sítio reativo P1–P1'; K_hyd é a razão no equilíbrio entre forma intacta e modificada.
- Karna et al. 2015, ChemBioChem 16:2036 (doi 10.1002/cbic.201500296; PMID 26212347): em análogos do SFTI-1, a serino-protease catalisa a clivagem e a refusão (splicing) da ligação Lys–Ser do sítio reativo; estruturas cristalográficas com tripsina.
- Wei et al. 2019, RSC Adv 9:13776 (doi 10.1039/c9ra02114k; PMID 35519558): em QM/MM do SFTI-1 e análogos, a taxa de hidrólise correlaciona positivamente com a mobilidade do inibidor; a cadeia cíclica, o dissulfeto e ligações de hidrogênio intramoleculares reduzem a hidrólise.
- Corpus do RAG do projeto: Patarroyo-Vargas et al. 2017 (tripsina de A. gemmatalis prefere Arg em P1) e Schultz et al. 2026 (Lys e Arg diferem em flexibilidade; possível efeito sobre a resistência luminal, sem medida).

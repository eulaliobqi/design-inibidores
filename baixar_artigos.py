"""
baixar_artigos.py — Download de artigos relevantes ao projeto design-inibidores.

Categorias:
  1. Inibidores de tripsina em Lepidoptera / S. frugiperda (grupo Meriño-Cabrera)
  2. Biologia do alvo (tripsinas digestivas S. frugiperda)
  3. Metodologia computacional (RFdiffusion, ProteinMPNN, PyRosetta)
  4. Defesa vegetal (Kunitz, Bowman-Birk)
  5. Controle biológico de Spodoptera

Uso:
    pip install requests
    python baixar_artigos.py
"""
import os
import time
import json
import requests
from pathlib import Path

OUT_DIR = Path("artigos_revisao")
OUT_DIR.mkdir(exist_ok=True)
(OUT_DIR / "pdfs").mkdir(exist_ok=True)
(OUT_DIR / "abstracts").mkdir(exist_ok=True)

NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
PMC_PDF   = "https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc}/pdf/"
HEADERS   = {"User-Agent": "Mozilla/5.0 (research; eulalio.santos@ufv.br)"}

# ─── Curadoria manual: artigos selecionados ──────────────────────────────────
PAPERS = [
    # ── TIER 1: Grupo Meriño-Cabrera — inibidores peptídicos de tripsina Lepidoptera ──
    {
        "pmid": "42138598", "pmc": "PMC13178409",
        "doi": "10.1002/arch.70164",
        "year": 2026, "cat": "T1_alvo_peptideo",
        "ref": "Severiche-Castro2026a",
        "cite": "Severiche-Castro J et al. (2026) Arch Insect Biochem Physiol 122:e70164",
        "title": "Structure-Guided Design of an Interface-Derived Inhibitor Peptide Against Spodoptera frugiperda Digestive Trypsins",
        "abstract": "Rational computational strategy identified PEP-11 (11-mer) targeting S. frugiperda digestive trypsin. MM/GBSA showed negative binding free energy in all replicas. Docking+MD revealed stable complex via polar and hydrophobic interactions.",
        "relevance": "ALTA — design in silico de peptídeo inibidor de tripsina de S. frugiperda; usa mesmo alvo do projeto",
    },
    {
        "pmid": "41849700", "pmc": "PMC12999070",
        "doi": "10.1002/arch.70145",
        "year": 2026, "cat": "T1_alvo_peptideo",
        "ref": "Schultz2026",
        "cite": "Schultz H, Paulo DGS, Meriño-Cabrera Y et al. (2026) Arch Insect Biochem Physiol 121:e70145",
        "title": "Synthetic Peptide Inhibition of Trypsin-Like Proteases in Spodoptera frugiperda: Evaluating the Influence of Gut Microbiota",
        "abstract": "GORE1 (Ki=1.41 mM) e GORE2 (Ki=0.49 mM) — inibição competitiva de tripsina S. frugiperda. Microbiota intestinal modula desenvolvimento larval mas não altera inibição enzimática.",
        "relevance": "ALTA — GORE1/GORE2 são os peptídeos de referência do grupo UFV; comparação direta",
    },
    {
        "pmid": "41572648", "pmc": "PMC13071266",
        "doi": "10.1002/ps.70579",
        "year": 2026, "cat": "T1_alvo_peptideo",
        "ref": "Paulo2026a",
        "cite": "Paulo DGS, Schultz H, Meriño Cabrera YB et al. (2026) Pest Manag Sci 82:4632-4647",
        "title": "Peptidic Product Derived from Trypsin Autolysis Modulates Insect Digestive Proteases and Supports Plant Biochemical Defense",
        "abstract": "GORE3 — inibidor competitivo (Ki=4.0 mM) de tripsina de S. frugiperda. Docking: ocupa subsítios S1/S1'. Reduz massa larval, prolonga período larval, mortalidade até 46.66%.",
        "relevance": "ALTA — GORE3 ocupa mesmo sítio S1 alvo do pipeline; validação in vivo incluída",
    },
    {
        "pmid": "41510779", "pmc": "PMC12784448",
        "doi": "10.1002/arch.70123",
        "year": 2026, "cat": "T1_alvo_peptideo",
        "ref": "Paulo2026b",
        "cite": "Paulo DGS, Schneider JR, Meriño-Cabrera Y et al. (2026) Arch Insect Biochem Physiol 121:e70123",
        "title": "Peptides Derived From Reactive Center Loops Inhibit Digestive Trypsin-Like Enzymes in Lepidopteran Pests",
        "abstract": "TGPCK, TGPCR, AVIMK, AVIMR (derivados de RCL de BPTI/SKTI) inibem tripsina de A. gemmatalis competitivamente. Interações pi-sigma correlacionam com maior afinidade.",
        "relevance": "ALTA — estratégia RCL-derived peptide análoga ao nosso pipeline IA generativa",
    },
    {
        "pmid": "41956187", "pmc": None,
        "doi": "10.1016/j.ijbiomac.2026.151886",
        "year": 2026, "cat": "T1_alvo_peptideo",
        "ref": "deAndrade2026",
        "cite": "de Andrade RJ, Meriño-Cabrera Y, Castro JS et al. (2026) Int J Biol Macromol 359:151886",
        "title": "Expression of a Recombinant Peptide with Bioinsecticidal Potential for the Control of Agricultural Pests",
        "abstract": "GORE1-2T quimérico expresso em E. coli BL21. Inibição competitiva Ki≈100 µM. MD mostra backbone RMSD estável, ligações H persistentes. Seletividade para serinas de Lepidoptera.",
        "relevance": "ALTA — abordagem recombinante do mesmo peptídeo GORE; prova de conceito de expressão",
    },
    {
        "pmid": "32360954", "pmc": None,
        "doi": "10.1016/j.ibmb.2020.103390",
        "year": 2020, "cat": "T1_alvo_peptideo",
        "ref": "MerinoCabrera2020",
        "cite": "Meriño-Cabrera Y, Severiche Castro JG, Rios Diez JD et al. (2020) Insect Biochem Mol Biol 122:103390",
        "title": "Rational Design of Mimetic Peptides Based on the Interaction Between Inga laurina Inhibitor and Trypsins for Spodoptera cosmioides Pest Control",
        "abstract": "Dois peptídeos lineares derivados da interface ILTI-tripsina. Estabilidade estrutural e propensão à conformação de ligação. Atividade inibitória sobre tripsinas digestivas e efeito tóxico em S. cosmioides.",
        "relevance": "ALTA — artigo fundador do conceito de design racional de mimético de Kunitz para Spodoptera",
    },
    {
        "pmid": "33200876", "pmc": None,
        "doi": "10.1002/ps.6191",
        "year": 2021, "cat": "T1_alvo_peptideo",
        "ref": "deAlmeidaBarros2021",
        "cite": "de Almeida Barros R, Meriño-Cabrera Y, Vital CE et al. (2021) Pest Manag Sci 77:1714-1723",
        "title": "Small Peptides Inhibit Gut Trypsin-Like Proteases and Impair Anticarsia gemmatalis Survival and Development",
        "abstract": "GORE1 (Ki=0.49 mM) e GORE2 (Ki=0.10 mM) — inibição competitiva reversível. Docking confirma ligação ao sítio ativo (His57, Asp102, Ser195). Reduz sobrevivência e desenvolvimento de A. gemmatalis in vivo.",
        "relevance": "ALTA — A. gemmatalis (alvo secundário do projeto); demonstra Ki sub-mM com peptídeos curtos",
    },
    {
        "pmid": "35715046", "pmc": None,
        "doi": "10.1016/j.pestbp.2022.105107",
        "year": 2022, "cat": "T1_alvo_peptideo",
        "ref": "MerinoCabrera2022a",
        "cite": "Meriño-Cabrera Y, Castro JS, de Almeida Barros R et al. (2022) Pestic Biochem Physiol 184:105107",
        "title": "Arginine-Containing Dipeptides Decrease Affinity of Gut Trypsins and Compromise Soybean Pest Development",
        "abstract": "Dipeptídeos contendo Arg > Lys em afinidade pelo subsítio S1 de tripsina de A. gemmatalis (guanidínio+). Inibição competitiva in vitro; redução de trypsin, sobrevivência e peso larval in vivo.",
        "relevance": "MUITO ALTA — justifica seleção de Arg/Lys em top candidatos (padrão observado nos 10 resultados Vina+Rosetta)",
    },
    {
        "pmid": "35315942", "pmc": None,
        "doi": "10.1002/arch.21887",
        "year": 2022, "cat": "T1_alvo_peptideo",
        "ref": "deAlmeidaBarros2022",
        "cite": "de Almeida Barros R, Meriño-Cabrera Y, Severiche Castro JG et al. (2022) Arch Insect Biochem Physiol 109:e21887",
        "title": "Inhibition Constant and Stability of Tripeptide Inhibitors of Gut Trypsin-Like Enzyme",
        "abstract": "Constantes de inibição de tripeptídeos GORE vs tripsinas de lepidópteros. Estabilidade estrutural dos peptídeos no sítio ativo.",
        "relevance": "ALTA — Ki de tripeptídeos estabelece referência para comparação com candidatos do pipeline",
    },
    {
        "pmid": "36127063", "pmc": None,
        "doi": "10.1016/j.pestbp.2022.105188",
        "year": 2022, "cat": "T1_alvo_peptideo",
        "ref": "deAlmeidaBarros2022b",
        "cite": "de Almeida Barros R, Meriño-Cabrera Y, Castro JS et al. (2022) Pestic Biochem Physiol 187:105188",
        "title": "BPTI and SKTI: Differential Effects on Proteases and Larval Development of Anticarsia gemmatalis",
        "abstract": "BPTI evita adaptação (não há overproduction de protease). SKTI é digerido e induz overproduction. BPTI reduz trypsin, sobrevivência e peso pupal. Modelo paradigmático de inibição de referência.",
        "relevance": "ALTA — BPTI/SKTI são as seeds positivas do dataset ML; artigo explica mecanismo diferencial",
    },
    {
        "pmid": "28925864", "pmc": None,
        "doi": "10.2174/0929866524666170918103146",
        "year": 2017, "cat": "T1_alvo_peptideo",
        "ref": "PatarroyoVargas2017",
        "cite": "Patarroyo-Vargas AM, Merino-Cabrera YB, Zanuncio JC et al. (2017) Protein Pept Lett 24:1040-1047",
        "title": "Kinetic Characterization of Anticarsia gemmatalis Digestive Serine-Proteases and Inhibitory Effect of Synthetic Peptides",
        "abstract": "Tripsina de A. gemmatalis: maior afinidade para substratos com Arg na P1. Gor3/4/5 — inibidores lineares competitivos. Gor5 (menor Ki) interage com resíduos hidrofóbicos do subsítio S2'.",
        "relevance": "FUNDADORA — primeiro trabalho do grupo em peptídeos inibitórios de A. gemmatalis; base do pipeline",
    },
    # ── TIER 2: Biologia do alvo ──────────────────────────────────────────────
    {
        "pmid": "34438074", "pmc": None,
        "doi": "10.1016/j.cbpb.2021.110670",
        "year": 2022, "cat": "T2_biologia_alvo",
        "ref": "Fuzita2022",
        "cite": "Fuzita FJ, Palmisano G, Pimenta DC et al. (2022) Comp Biochem Physiol B 259:110670",
        "title": "Proteomic Approach to Identify Digestive Enzymes and Their Secretory Routes in the Midgut of Spodoptera frugiperda",
        "abstract": "Identificação proteômica de enzimas digestivas no intestino médio de S. frugiperda. Tripsinas como componentes majoritários do suco intestinal. Secretadas por rota microapocrína.",
        "relevance": "ALTA — confirma importância das tripsinas no intestino de S. frugiperda; fundamenta escolha do alvo",
    },
    {
        "pmid": "33629522", "pmc": None,
        "doi": "10.1111/1744-7917.12906",
        "year": 2021, "cat": "T2_biologia_alvo",
        "ref": "Hafeez2021",
        "cite": "Hafeez M, Li XW, Zhang JM et al. (2021) Insect Sci 28:1639-1655",
        "title": "Role of Digestive Protease Enzymes in Host Plant Adaptation of Spodoptera frugiperda",
        "abstract": "Perfil de atividade de proteases digestivas no intestino de S. frugiperda durante adaptação a diferentes hospedeiros. Modulação de tripsinas e quimiotripsinas em resposta a inibidores.",
        "relevance": "ALTA — explica plasticidade das tripsinas de S. frugiperda; fundamenta necessidade de múltiplos candidatos",
    },
    {
        "pmid": "37199037", "pmc": None,
        "doi": "10.1002/arch.22025",
        "year": 2023, "cat": "T2_biologia_alvo",
        "ref": "Severiche-Castro2023",
        "cite": "Severiche-Castro J, Wilches Diaz G, Combariza Montañez AF et al. (2023) Arch Insect Biochem Physiol 113:e22025",
        "title": "Structural Analysis and Inhibition Capacity of Dioscorin Protein Yam: Molecular Docking and Dynamics",
        "abstract": "Dioscorina se liga a tripsinas de S. frugiperda com energia de ligação -57.3 a -66.9 kcal/mol (MM/GBSA). Dois sítios reativos; interações via ligações H, hidrofóbicas e VdW. Template estrutural para design PEP-11.",
        "relevance": "ALTA — template estrutural usado no PMID 42138598; serve de referência para comparar nossos candidatos",
    },
    {
        "pmid": "37816687", "pmc": None,
        "doi": "10.1093/jee/toad188",
        "year": 2023, "cat": "T2_biologia_alvo",
        "ref": "Fonseca2023",
        "cite": "Fonseca SS, Santos ALZ, Pinto CPG et al. (2023) J Econ Entomol 116:2087-2094",
        "title": "A Soybean Trypsin Inhibitor Reduces the Resistance to Transgenic Maize in Spodoptera frugiperda",
        "abstract": "Inibidor de tripsina de soja (STI) reduz resistência de S. frugiperda ao milho Bt-transgênico. Sinergia entre inibidores endógenos de plantas e toxinas Bt para controle de praga.",
        "relevance": "MÉDIA — demonstra aplicabilidade de inibidores de tripsina em contexto de praga de campo",
    },
    # ── TIER 3: Metodologia computacional ────────────────────────────────────
    {
        "pmid": "37433327", "pmc": "PMC10468394",
        "doi": "10.1038/s41586-023-06415-8",
        "year": 2023, "cat": "T3_metodos_IA",
        "ref": "Watson2023",
        "cite": "Watson JL, Juergens D, Bennett NR et al. (2023) Nature 620:1089-1100",
        "title": "De Novo Design of Protein Structure and Function with RFdiffusion",
        "abstract": "RFdiffusion: fine-tuning de RoseTTAFold em denoising de backbones. Gera binders de novo com alta especificidade. Confirmado por cryo-EM. Suporta design de oligômeros, proteínas de simetria, binders peptídicos.",
        "relevance": "METODOLÓGICA CRÍTICA — artigo fundador do RFdiffusion usado no pipeline (etapa 2)",
    },
    {
        "pmid": "36108050", "pmc": "PMC9997061",
        "doi": "10.1126/science.add2187",
        "year": 2022, "cat": "T3_metodos_IA",
        "ref": "Dauparas2022",
        "cite": "Dauparas J, Anishchenko I, Bennett N et al. (2022) Science 378:49-56",
        "title": "Robust Deep Learning-Based Protein Sequence Design Using ProteinMPNN",
        "abstract": "ProteinMPNN: deep learning para design de sequências dado backbone. 52.4% de sequence recovery (vs 32.9% Rosetta). Validado por cristalografia, cryo-EM e estudos funcionais.",
        "relevance": "METODOLÓGICA CRÍTICA — artigo fundador do ProteinMPNN usado no pipeline (etapa 3)",
    },
    {
        "pmid": "38109936", "pmc": "PMC10849960",
        "doi": "10.1038/s41586-023-06953-1",
        "year": 2024, "cat": "T3_metodos_IA",
        "ref": "VazquezTorres2024",
        "cite": "Vázquez Torres S, Leung PJY, Venkatesh P et al. (2024) Nature 626:435-442",
        "title": "De Novo Design of High-Affinity Binders of Bioactive Helical Peptides",
        "abstract": "Design de binders de alta afinidade para peptídeos helicoidais bioativos usando RFdiffusion+ProteinMPNN. Validado experimentalmente por cristalografia e ensaios de ligação.",
        "relevance": "ALTA — exemplo de aplicação combinada RFdiffusion+ProteinMPNN para peptídeos binders (análogo ao projeto)",
    },
    # ── TIER 4: Defesa vegetal (Kunitz, Bowman-Birk) ─────────────────────────
    {
        "pmid": "41539518", "pmc": None,
        "doi": "10.1016/j.ijbiomac.2026.150204",
        "year": 2026, "cat": "T4_defesa_vegetal",
        "ref": "Liu2026",
        "cite": "Liu X, Zhang Y, Francis F et al. (2026) Int J Biol Macromol:150204",
        "title": "Induced Bowman-Birk Trypsin Inhibitor TaBBTI-1 in Wheat During Poor-Host Interactions with Aphids",
        "abstract": "Bowman-Birk trypsin inhibitor TaBBTI-1 em trigo — induzido por herbivoría; resistência de amplo espectro a insetos. Mecanismo via inibição de serinas digestivas.",
        "relevance": "MÉDIA — BBTIs como proteínas de referência; mecanismo análogo ao objetivo do projeto",
    },
    {
        "pmid": "41419797", "pmc": None,
        "doi": "10.1186/s12870-025-07955-z",
        "year": 2025, "cat": "T4_defesa_vegetal",
        "ref": "Das2025",
        "cite": "Das IS, Shi Q, Dreischhoff S et al. (2025) BMC Plant Biol 25:e07955",
        "title": "Divergent Functions of Three Kunitz Trypsin Inhibitor (KTI) Proteins in Herbivore Defense in Poplar",
        "abstract": "KTIs em Populus com funções divergentes na defesa contra herbívoros Lepidoptera. Especificidade de inibição depende de diferenças no RCL e bolso S1.",
        "relevance": "MÉDIA — diversidade funcional de KTIs; suporta necessidade de design específico por espécie-alvo",
    },
    {
        "pmid": "41452982", "pmc": None,
        "doi": "10.1073/pnas.2424956122",
        "year": 2025, "cat": "T4_defesa_vegetal",
        "ref": "Li2025",
        "cite": "Li X, Hu D, Yang Z et al. (2025) Proc Natl Acad Sci USA 122:e2424956122",
        "title": "A Natural Variant of MYC2 in Soybean Contributes to Resistance Against the Common Cutworm",
        "abstract": "Variante natural de MYC2 em soja ativa cascade de defesa contra Spodoptera (cutworm). Inibidores de protease são componentes da resposta defensiva.",
        "relevance": "MÉDIA — contexto de resistência de plantas a Spodoptera; justifica design de inibidores",
    },
    # ── TIER 5: Controle biológico de Spodoptera ─────────────────────────────
    {
        "pmid": "40872791", "pmc": None,
        "doi": "10.3390/v17081077",
        "year": 2025, "cat": "T5_biocontrole",
        "ref": "GarciaMunguia2025",
        "cite": "García-Munguía AM, García-Munguía CA, Guerra-Ávila PL et al. (2025) Viruses 17:1077",
        "title": "Baculovirus-Based Biocontrol: Synergistic and Antagonistic Interactions of PxGV, PxNPV, SeMNPV, SfMNPV",
        "abstract": "Baculovírus como agentes de biocontrole de lepidópteros. SfMNPV específico para S. frugiperda. Interações sinérgicas e antagônicas com outros vírus.",
        "relevance": "MÉDIA — contexto de biocontrole; alternativa biológica ao controle químico (manejo integrado)",
    },
    {
        "pmid": "41169723", "pmc": None,
        "doi": "10.3389/fpls.2025.1694032",
        "year": 2025, "cat": "T5_biocontrole",
        "ref": "ElSaid2025",
        "cite": "El-Said NA, Alfuhaid NA, Chellappan BV et al. (2025) Front Plant Sci 16:1694032",
        "title": "Lethal and Sublethal Effects of Chemical and Bio-Insecticides on Spodoptera frugiperda Adults",
        "abstract": "Efeitos letais e subletais de inseticidas químicos e biológicos em S. frugiperda adultos. Bio-inseticidas reduzem fecundidade e fertilidade.",
        "relevance": "MÉDIA — panorama de estratégias de controle; posiciona inibidores de protease como alternativa",
    },
    {
        "pmid": "36515103", "pmc": None,
        "doi": "10.1093/jee/toac143",
        "year": 2022, "cat": "T5_biocontrole",
        "ref": "VandenBerg2022",
        "cite": "Van den Berg J, Brewer MJ, Reisig DD et al. (2022) J Econ Entomol 116:1-5",
        "title": "A Special Collection: Spodoptera frugiperda (Fall Armyworm): Ecology and Management",
        "abstract": "Revisão compilada de ecologia e manejo de S. frugiperda (fall armyworm). Coleção especial do J Econ Entomol.",
        "relevance": "MÉDIA — revisão abrangente de manejo; contexto geral para justificativa do projeto",
    },
]

# ─── Funções ──────────────────────────────────────────────────────────────────

def download_pmc_pdf(pmc_id: str, dest: Path) -> bool:
    """Baixa PDF de um artigo no PubMed Central."""
    url = PMC_PDF.format(pmc=pmc_id)
    try:
        r = requests.get(url, headers=HEADERS, timeout=30, allow_redirects=True)
        if r.status_code == 200 and b"%PDF" in r.content[:1024]:
            dest.write_bytes(r.content)
            return True
        # Tenta URL alternativa (alguns PMC têm paths diferentes)
        r2 = requests.get(f"https://pmc.ncbi.nlm.nih.gov/articles/{pmc_id}/pdf/", headers=HEADERS, timeout=30, allow_redirects=True)
        if r2.status_code == 200 and b"%PDF" in r2.content[:1024]:
            dest.write_bytes(r2.content)
            return True
    except Exception as e:
        print(f"  [ERRO PDF] {pmc_id}: {e}")
    return False


def save_abstract(paper: dict, dest: Path):
    """Salva abstract e metadados de um paper em arquivo texto."""
    txt = f"""TÍTULO: {paper['title']}
AUTORES: {paper['cite']}
DOI: {paper['doi']}
PMID: {paper['pmid']}
PMC: {paper.get('pmc') or 'N/A'}
CATEGORIA: {paper['cat']}
RELEVÂNCIA: {paper['relevance']}

ABSTRACT:
{paper['abstract']}
"""
    dest.write_text(txt, encoding="utf-8")


def generate_bibtex(papers: list) -> str:
    """Gera arquivo BibTeX com todos os papers."""
    lines = [f"% Gerado por baixar_artigos.py — projeto design-inibidores\n% {len(papers)} artigos curados\n"]
    for p in papers:
        authors_raw = p['cite'].split('(')[0].strip()
        year = p['year']
        title = p['title']
        doi = p['doi']
        pmid = p['pmid']
        ref = p['ref']
        venue = p['cite'].split('(')[1].split(')')[1].strip() if ')' in p['cite'] else ""
        lines.append(f"""@article{{{ref},
  title   = {{{title}}},
  author  = {{{authors_raw}}},
  year    = {{{year}}},
  doi     = {{{doi}}},
  pmid    = {{{pmid}}},
  note    = {{{venue}}}
}}
""")
    return "\n".join(lines)


def generate_review_outline(papers: list) -> str:
    """Gera roteiro de revisão de literatura estruturado."""
    cats = {}
    for p in papers:
        cats.setdefault(p['cat'], []).append(p)

    cat_titles = {
        "T1_alvo_peptideo": "1. Inibidores Peptídicos de Tripsinas de Lepidoptera",
        "T2_biologia_alvo": "2. Biologia das Tripsinas Digestivas de S. frugiperda",
        "T3_metodos_IA": "3. Metodologia de IA Generativa Estrutural",
        "T4_defesa_vegetal": "4. Defesa Vegetal por Inibidores de Protease (Kunitz/Bowman-Birk)",
        "T5_biocontrole": "5. Controle Biológico e Manejo de Spodoptera",
    }

    lines = [
        "# Roteiro de Revisão de Literatura — Design Racional de Inibidores Peptídicos de Tripsina",
        f"# {len(papers)} artigos curados | Gerado por baixar_artigos.py",
        "",
        "## Objetivo do estudo",
        "Desenvolver inibidores peptídicos de tripsinas digestivas de Lepidoptera-praga (S. frugiperda, A. gemmatalis)",
        "via pipeline multiagente de IA generativa (RFdiffusion + ProteinMPNN + PyRosetta + Vina + GROMACS).",
        "",
    ]

    for cat_key, cat_title in cat_titles.items():
        ps = cats.get(cat_key, [])
        lines.append(f"## {cat_title} ({len(ps)} artigos)")
        for p in ps:
            lines.append(f"\n### {p['ref']}")
            lines.append(f"**{p['title']}**")
            lines.append(f"*{p['cite']}* | DOI: {p['doi']}")
            lines.append(f"**Relevância:** {p['relevance']}")
            lines.append(f"**Resumo:** {p['abstract']}")
        lines.append("")

    lines += [
        "## Pontos de discussão sugeridos",
        "",
        "### 1. Justificativa do alvo (tripsinas S. frugiperda / A. gemmatalis)",
        "- Citar Fuzita2022 (proteômica), Hafeez2021 (adaptação), Patarroyo2017 (cinética)",
        "- Resíduos catalíticos His/Asp/Ser; bolso S1 (Asp205 ACR157) — especificidade por Arg/Lys",
        "",
        "### 2. Estado da arte em inibidores peptídicos (grupo Meriño-Cabrera/UFV)",
        "- Linha: ILTI -> GORE1/2 -> GORE3 -> GORE1-2T recombinante -> PEP-11 guiado estruturalmente",
        "- Padrão consistente: Ki sub-mM, inibição competitiva, interação com Asp189 (S1)",
        "- Nosso pipeline avança: 24.513 candidatos por IA generativa vs. design manual",
        "",
        "### 3. Vantagem do design por IA generativa",
        "- Watson2023 (RFdiffusion) + Dauparas2022 (ProteinMPNN): backbones de novo condicionados ao sítio",
        "- VazquezTorres2024: prova de conceito para peptide binders de alta afinidade",
        "- Comparar com abordagem RCL (Paulo2026b) e mimético de Kunitz (MerinoCabrera2020)",
        "",
        "### 4. Argumento Arg/Lys (respaldado por literatura)",
        "- MerinoCabrera2022a: Arg >> Lys em afinidade (guanidínio²⁺ vs. amônio⁺ no S1)",
        "- Padrão observado nos top-10 candidatos (Vina + Rosetta): todos Arg/Lys-rico, sem aromáticos",
        "- Concordância com seleção natural de inibidores (BPTI usa Lys15/Arg17)",
        "",
        "### 5. Validação in silico -> in vitro (plano experimental futuro)",
        "- MD 10 ns: estabilidade do complexo (RMSD < 2 Å, H-bonds persistentes)",
        "- Ki estimado -> síntese Fmoc-SPPS -> ensaios IC50 vs. tripsinas recombinantes",
        "- Comparar Ki obtidos com GORE1 (1.41 mM) e GORE2 (0.49 mM) como referência",
    ]

    return "\n".join(lines)


# ─── Execução principal ───────────────────────────────────────────────────────

def main():
    print(f"\n{'='*60}")
    print(f"  baixar_artigos.py — {len(PAPERS)} artigos curados")
    print(f"  Saída: {OUT_DIR.resolve()}")
    print(f"{'='*60}\n")

    open_access = [p for p in PAPERS if p.get("pmc")]
    print(f"[INFO] {len(open_access)} artigos open-access (PMC) para download de PDF")
    print(f"[INFO] {len(PAPERS) - len(open_access)} artigos sem PMC (abstract salvo)")

    # 1. Abstracts de todos os artigos
    print("\n[1/3] Salvando abstracts...")
    for p in PAPERS:
        dest = OUT_DIR / "abstracts" / f"{p['ref']}.txt"
        save_abstract(p, dest)
        print(f"  OK {p['ref']}.txt")

    # 2. PDFs dos artigos open-access
    print("\n[2/3] Baixando PDFs do PubMed Central...")
    pdf_ok, pdf_fail = [], []
    for p in open_access:
        pmc = p["pmc"]
        dest = OUT_DIR / "pdfs" / f"{p['ref']}.pdf"
        if dest.exists() and dest.stat().st_size > 10_000:
            print(f"  [cache] {p['ref']}.pdf  ({dest.stat().st_size//1024} KB)")
            pdf_ok.append(p['ref'])
            continue
        print(f"  -> {p['ref']} ({pmc})...", end=" ", flush=True)
        ok = download_pmc_pdf(pmc, dest)
        if ok:
            print(f"OK  {dest.stat().st_size//1024} KB")
            pdf_ok.append(p['ref'])
        else:
            print(f"FAIL  (sem PDF direto — acesse: https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc}/)")
            pdf_fail.append(p['ref'])
        time.sleep(0.4)

    # 3. Gerar BibTeX e roteiro de revisão
    print("\n[3/3] Gerando BibTeX e roteiro de revisão...")
    bib = generate_bibtex(PAPERS)
    (OUT_DIR / "referencias.bib").write_text(bib, encoding="utf-8")
    print(f"  OK  referencias.bib  ({len(PAPERS)} entradas)")

    review = generate_review_outline(PAPERS)
    (OUT_DIR / "roteiro_revisao_literatura.md").write_text(review, encoding="utf-8")
    print(f"  OK  roteiro_revisao_literatura.md")

    # 4. Índice JSON
    index = [{"ref": p["ref"], "pmid": p["pmid"], "pmc": p.get("pmc"), "year": p["year"],
               "cat": p["cat"], "doi": p["doi"], "pdf": (OUT_DIR/"pdfs"/f"{p['ref']}.pdf").exists(),
               "title": p["title"][:80]} for p in PAPERS]
    (OUT_DIR / "index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  OK  index.json")

    # Resumo final
    print(f"\n{'='*60}")
    print(f"  CONCLUÍDO")
    print(f"  PDFs baixados:     {len(pdf_ok)}/{len(open_access)}")
    if pdf_fail:
        print(f"  PDFs não-diretos:  {', '.join(pdf_fail)}")
        print(f"    -> acesse manualmente via PMC ou institucional")
    print(f"  Abstracts:         {len(PAPERS)}")
    print(f"  BibTeX:            {OUT_DIR}/referencias.bib")
    print(f"  Roteiro revisão:   {OUT_DIR}/roteiro_revisao_literatura.md")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

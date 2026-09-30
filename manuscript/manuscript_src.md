# Computational design and triage of macrocyclic peptide candidates targeting digestive trypsins of lepidopteran soybean pests

**Running title:** Macrocyclic peptides against lepidopteran trypsins

**Authors:** [AUTHOR LIST TO BE COMPLETED]  
**Affiliations:** [TO BE COMPLETED]  
**Correspondence:** [TO BE COMPLETED]

**Article type:** Original Research — section *Informatics and Computational Methods*  
**Keywords:** protease inhibitor, digestive trypsin, Lepidoptera, *Anticarsia gemmatalis*, macrocyclic peptide, RFdiffusion, Boltz-2, molecular dynamics

---

## Abstract

[[ABSTRACT — TO BE FINALIZED AFTER THE PENDING SIMULATIONS; see the drafting notes at the end of this file]]

---

## 1 Introduction

Lepidopteran larvae are among the main biotic factors limiting soybean productivity in South America, and the velvetbean caterpillar *Anticarsia gemmatalis* is one of the defoliating species of this group {carpane2022;almeida2021}. In lepidopteran larvae, protein digestion takes place in a midgut lumen that is strongly alkaline; lepidopteran midguts generate the highest luminal pH known in a biological system {dow1992}. Trypsin-like enzymes are the main proteases of the *A. gemmatalis* midgut {almeida2021}, and serine proteases are the main protease class expressed in fifth-instar larvae {silvajunior2020}, and a proteomic survey of the larval intestine found 54 expressed protease antigens, indicating multiple isoforms {silvajunior2021}. General reviews of insect digestion describe the compartmentalization and properties of these enzymes {terra1994}.

Plants defend themselves against herbivores with proteinaceous protease inhibitors, many of them accumulated in seeds, and such inhibitors have been examined as leads for pest control. Examples that are relevant to trypsins of *A. gemmatalis* include the inhibitor from *Adenanthera pavonina* seeds (ApTI), which is a noncompetitive tight-binding inhibitor of larval trypsins {merino2020apti}, and the bovine pancreatic and soybean Kunitz inhibitors, which reduced larval survival with distinct effects on the insect proteolytic response {almeida2022bpti}. At the small end of the size range, the 14-residue cyclic peptide SFTI-1 from sunflower seeds inhibits trypsin with a K~i~ of 100 pM, and its potency has been attributed to the rigidity conferred by cyclization and a single disulfide bond {luckett1999}. A recurrent limitation is insect adaptation: larvae compensate by inducing protease activity that is insensitive to the inhibitor {jongsma1995;jongsma1997}, by regulating the expression of multiple digestive proteases {kuwar2015;lomate2018}, and, in some species, through gene-family expansion that may explain differences in sensitivity to soybean inhibitors between *Spodoptera frugiperda* and *Diatraea saccharalis* {souza2016}.

Short synthetic peptides that mimic the reactive-center loop of these inhibitors have therefore attracted interest, because they are cheaper to produce than proteins. Linear peptides derived from the interface of a Kunitz inhibitor–trypsin complex inhibited digestive trypsins of *Spodoptera cosmioides* and were toxic to the larvae {merino2020rational}. Tripeptides derived from Pin-II inhibitors inhibited *Helicoverpa armigera* midgut proteases, with enhanced efficacy at alkaline gut pH {saikhedkar2018}, and bicyclic peptides built from the same loops were ten-fold more potent than their linear counterparts {saikhedkar2019}. In *A. gemmatalis*, the designed tripeptides GORE1 and GORE2 are reversible competitive inhibitors with K~i~ values of 0.49 and 0.10 mM, respectively, and impair larval survival and development {almeida2021}; their complexes were examined by molecular dynamics {almeida2022tri}, and arginine-containing dipeptides, predicted *in silico* to bind the S1 subsite of *A. gemmatalis* trypsins more strongly than lysine-containing peptides, were competitive inhibitors *in vitro* {merino2022}. Peptides inspired by the reactive-center loops of BPTI and soybean Kunitz inhibitor were competitive inhibitors of *A. gemmatalis* trypsin-like proteases {paulo2026}, and GORE1 and GORE2 also inhibited trypsin-like proteases of *S. frugiperda* {schultz2026}. The GORE tripeptides have K~i~ values of 0.10–1.41 mM against trypsin-like proteases of *A. gemmatalis* and *S. frugiperda* {almeida2021;schultz2026}, which leaves room for higher-affinity and more stable designs.

Canonical ("standard mechanism") inhibitors bind through an exposed loop of conserved conformation whose P1 residue inserts into the S1 pocket {laskowski1980;laskowski2000}; the remainder of the molecule, the scaffold, improves binding by about six orders of magnitude and protects the inhibitor from proteolysis {kelly2005}. For trypsin-like enzymes the S1 pocket is defined by an aspartate at the position numbered 189 in chymotrypsin, which favors lysine and arginine at P1 {perona1995;hedstrom2002}; the trypsin-like enzymes of *A. gemmatalis* likewise show higher affinity for substrates with arginine at P1 {patarroyo2017}. This raises a design tension that is central to the present study: the basic P1 residues that best engage S1 are themselves cleavage sites for the target enzyme.

Deep-learning methods now allow peptides and other binders to be generated *de novo*. RFdiffusion generates backbones conditioned on a target {watson2023}, ProteinMPNN assigns sequences to backbones {dauparas2022}, head-to-tail macrocycles can be designed with these tools {rettie2025}, and co-folding models such as Boltz-1 and Boltz-2 predict biomolecular complexes {wohlwend2024;passaro2025}. Whether the confidence scores of such models rank short peptide candidates against insect proteases in a meaningful way has not been established, and end-point free-energy methods are known to be sensitive to sampling and to system type {hou2011;genheden2015;xu2025}. A design campaign against insect proteases therefore needs an explicit calibration of the scoring steps it relies on.

Here we report a computational pipeline that (i) defines the catalytic subsites of digestive trypsins from eight lepidopteran pests by structural transfer from crystal complexes, (ii) calibrates a scoring ladder against six natural inhibitors and shuffled decoys, (iii) generates head-to-tail macrocyclic peptides of 5–20 residues with RFdiffusion and ProteinMPNN, (iv) screens them for protease-cleavage motifs, and (v) triages the survivors by Boltz-2 co-folding and molecular dynamics. An overview is given in Figure 1. The work is entirely computational. It does not evaluate selectivity against non-target proteases, which is a separate module of our project, and no result reported here should be read as evidence of inhibitory activity or selectivity.

---

## 2 Materials and methods

### 2.1 Target panel and receptor structures

The panel comprises digestive trypsin-like serine proteases of eight lepidopteran pests (*Spodoptera frugiperda*, *S. litura*, *Ostrinia nubilalis*, *Diatraea saccharalis*, *Chrysodeixis includens*, *Heliothis virescens*, *Plutella xylostella* and *Anticarsia gemmatalis*), *Manduca sexta* as the reference species with curated midgut evidence, and *Bombyx mori*, which was retained in the panel but not used as a design target. Only *M. sexta* (UniProt P35045–P35047) has reviewed entries annotated with midgut expression; for the other species the entries are unreviewed and were selected by homology, so the panel rests on sequence and structural evidence rather than on documented midgut expression. Structures are AlphaFold monomer v2.0 models {jumper2021} retrieved from the AlphaFold Protein Structure Database {varadi2024} (accessions in Table 1). Sequence identity to *M. sexta* alkaline trypsin B (P35046) was computed with Biopython {cock2009} (global alignment, BLOSUM62, gap open −11, gap extension −1; identical positions divided by the length of the shorter sequence), and per-model confidence is the mean pLDDT of the Cα atoms, read from the B-factor column.

Because UniProt names most of these entries "Chymotrypsin" (automatic annotation), trypsin-type specificity was checked from the sequence. The specificity residue was located six residues N-terminal to the catalytic serine, an offset calibrated on two reference proteins from UniProt {uniprot2025}: bovine trypsin (P00760; catalytic Ser200, Asp at position 194 of the precursor) and bovine chymotrypsinogen A (P00766; Ser195, Ser at position 189). The catalytic serine of each panel sequence was found from the conserved motif G[DN]SGG[PT].

### 2.2 Definition and transfer of catalytic subsites

Subsites were defined from two crystal complexes of bovine trypsin obtained from the Protein Data Bank {berman2000}: trypsin–BPTI (2PTC, trypsin chain E) and trypsin–SFTI-1 (1SFI, trypsin chain A; the structure reported by {luckett1999}). For each complex, the inhibitor residue whose carbonyl carbon lies closest to the Oγ of a serine of the trypsin chain was taken as P1 (2.68 Å for 2PTC and 2.83 Å for 1SFI; a distance above 4.5 Å would have failed the quality control). The seven inhibitor residues P4–P3′ (Schechter–Berger nomenclature {schechter1967}) define S4–S3′, and a trypsin residue was assigned to a subsite when any of its atoms lay within 4.5 Å of the corresponding inhibitor residue; trypsin residues within 4.5 Å of any other inhibitor residue were assigned to an exosite. Each trypsin chain was then structurally aligned with each panel receptor using Foldseek {vankempen2024} in TM-align mode (`--alignment-type 1`, exhaustive search), which implements the TM-align algorithm {zhang2005}, and reference residues were transferred through the residue-to-residue correspondence of the alignment. A receptor–template pair was accepted when the alignment TM-score (Foldseek `alntmscore`, normalized by alignment length) was ≥0.5 and the RMSD ≤3.0 Å.

### 2.3 Calibration of the scoring ladder

Six natural inhibitors of known sequence served as positive controls. Mature sequences were taken from the PDB entries {berman2000} of bovine pancreatic trypsin inhibitor (BPTI; UniProt P00974; 1BPI {parkin1996}; 58 residues), SFTI-1 (Q4GWU5; 1SFI {luckett1999}; 14 residues, modeled as the linear sequence), soybean Kunitz trypsin inhibitor (SKTI; P01070; 1AVU {song1998}; 172 residues), the Bowman–Birk inhibitor (BBI; P01055; 1BBI {werner1992}; 71 residues) and the *Enterolobium contortisiliquum* inhibitor (EcTI; P86451; 4J2K, chain A {zhou2013}; 168 residues); ApTI (P09941 and P09942; 176 residues in three chains) has no experimental structure and was taken from UniProt. For the first five, a decoy with the same amino-acid composition and a shuffled sequence (`random.seed(42)`) was generated. Each control and decoy was modeled with two receptors: bovine β-trypsin (the trypsin chain of 1SFI) and the *S. frugiperda* model A0A089QDB3, giving 22 systems in total (ApTI had no decoy).

The ladder had three rungs. (i) Co-folding with Boltz-2 {passaro2025} (checkpoint `boltz2_conf`, MSA from the public ColabFold server {mirdita2022}, one diffusion sample, three recycling steps) with the Boltz-2 `confidence_score`, complex pLDDT and ipTM as metrics. (ii) A 2-ns molecular dynamics (MD) simulation started from each predicted complex (protocol in Section 2.8; pH 8.0 for bovine trypsin and 10.0 for *S. frugiperda*). The MD metric was the RMSD of the ligand backbone after superposition on the receptor Cα atoms, with the ligand made whole and translated to the periodic image nearest the receptor in every frame (necessary because the ligand and the receptor are separate molecules that can be written to different periodic images), averaged over the last third of the trajectory; the number of receptor residues with a heavy atom within 4.5 Å of the ligand was also recorded. The expected direction (real inhibitor with lower ligand RMSD and larger contact than its decoy) was fixed in the analysis script before it was run. (iii) End-point MM-GBSA on the same trajectories with gmx_MMPBSA {valdes2021} (AmberTools 24.8; generalized Born model `igb=5`, 0.150 M salt; 45 frames from the last third of each trajectory, one trajectory per complex, no entropy term). A method was said to separate real from decoy in a pair when the real inhibitor had the more favorable value. Because each decoy is shared by the two receptors, the ten pairs are not independent.

### 2.4 Generation of macrocyclic backbones

Backbones were generated with RFdiffusion {watson2023} (package 1.1.0, `Complex_base_ckpt`, 50 diffusion steps, `denoiser.noise_scale_ca=0.2`, `noise_scale_frame=0.1`, random seeds) in head-to-tail cyclic mode (`inference.cyclic=True`, `cyc_chains=a`), with the receptor chain fixed (contig `A1–N/0 L–L` for a receptor of N residues and a peptide of L residues). For each of the eight targets, ten backbones were generated for each of 11 lengths (5, 6, 7, 8, 10, 12, 14, 16, 18, 19 and 20 residues), i.e. 110 per species and 880 in total. Hotspot residues came from the S1 and S2 subsites transferred from the trypsin–SFTI-1 template (15 residues per receptor); the RFdiffusion interface accepted only the first eight of these in ascending residue number, so the hotspots effectively used were the equivalents of His57, Leu99, Asp189, Ser190, Cys191, Gln192, Gly193 and Asp194 (bovine numbering). The equivalents of the catalytic Ser195 and of the S1 wall residues 213–216, 219 and 226 were not used as hotspots. Ring closure was checked as the distance between the N atom of the first residue and the C atom of the last residue of the peptide chain.

### 2.5 Sequence design

Sequences were assigned to each backbone with ProteinMPNN {dauparas2022} (commit 8907e66, weights `v_48_020`, sampling temperature 0.1, backbone noise 0.05, cysteine and unknown residues excluded, 30 sequences per backbone, random seeds). The program was run with its default chain settings, in which all chains are designed (`designed_chains=['A','B']`); the receptor sequence was therefore redesigned together with the peptide and was not held fixed, and only the peptide chain was retained. Identical sequences were merged within each species, and a merged sequence was kept with the first backbone that generated it. No amino-acid restrictions were imposed at design time; proteolytic liability was handled by the post hoc screen below.

### 2.6 Cleavage-motif screen

Each sequence was scanned with seven simplified P1-motif rules, defined with reference to the enzyme specificities compiled in PeptideCutter {gasteiger2005} but simplified and not benchmarked against it: trypsin (after K/R, not before P), chymotrypsin at high (F/Y/W) and low (F/Y/W/M/L) specificity, an elastase-like rule (after A/G/S/V, not before P), Lys-C, Arg-C and a pepsin-like rule; the last is not a lepidopteran gut protease and nevertheless contributes to the score with the weight of a priority-2 enzyme. Because the candidates are head-to-tail macrocycles, the peptide bond between the last and the first residue was evaluated like any other (a "circular" scan). The residue of the peptide whose Cα atom lay closest to the Cα of the catalytic serine in the RFdiffusion backbone was taken as a geometric proxy for P1; if that residue was a trypsin site, it was exempted from the count of internal trypsin sites, otherwise every trypsin site counted as internal. A susceptibility score was computed as the weighted number of sites (weights 1.0, 0.6 and 0.3 for protease priorities 1, 2 and 3; for trypsin only internal sites were counted, for the other rules all sites), divided by 10 and capped at 1. A sequence was labelled RESISTENTE (resistant-like) with no internal trypsin site and a score below 0.3, MARGINAL with at most one internal site and a score below 0.5, and SUSCEPTIVEL otherwise. These labels are motif-based predictions and do not measure proteolysis. They are also sensitive to a single site: for example, GIFDDIG has no trypsin site but a score of 0.34 and is labelled MARGINAL.

### 2.7 Boltz-2 co-folding of candidates

Candidates labelled RESISTENTE were co-folded with each receptor using Boltz-2 {passaro2025} (Boltz 2.2.1) with the receptor sequence and a receptor MSA computed once per species against the public ColabFold server {mirdita2022}, and the peptide declared cyclic (`cyclic: true`) with no MSA. One prediction was made per candidate with default settings (`--preprocessing-threads 4`). We report the Boltz-2 `confidence_score`, which we verified to equal 0.8·pLDDT + 0.2·ipTM for all predictions (largest absolute deviation 8 × 10^−8^), complex pLDDT and ipTM. Boltz-2 affinity outputs were not used.

### 2.8 Molecular dynamics of top candidates

For each species, the RESISTENTE candidate with the highest `confidence_score` was simulated. Starting from the Boltz-2 complex, protonation at pH 10.0 (an alkaline value within the range generated by lepidopteran midguts {dow1992}) was assigned with PROPKA 3 {olsson2011} through PDB2PQR 3.6.2 {dolinsky2007}. Simulations used GROMACS 2025.4 {abraham2015} with the AMBER99SB-ILDN force field {lindorff2010} and TIP3P water {jorgensen1983}, a dodecahedral box with 1.2 nm between solute and box edge, neutralizing NaCl at 0.15 M, steepest-descent minimization (50,000 steps at most), 200 ps of NVT and 500 ps of NPT equilibration with position restraints on protein heavy atoms (GROMACS default force constant, 1,000 kJ mol^−1^ nm^−2^), and a 50-ns production run at 300 K and 1 bar. The temperature was controlled with the velocity-rescaling thermostat {bussi2007} (τ = 0.1 ps, separate coupling of protein and non-protein), pressure with the Parrinello–Rahman barostat {parrinello1981} (τ = 2 ps), electrostatics with particle-mesh Ewald {essmann1995} and a 1.0-nm cutoff for both Coulomb and van der Waals interactions, with bonds to hydrogen constrained (LINCS) and a 2-fs time step; coordinates were written every 5 ps. Initial velocities were generated with a random seed. Each candidate was simulated once. The peptide was built as a linear chain with charged termini: the head-to-tail bond of the macrocycle was not imposed in the topology.

### 2.9 Trajectory analysis

Trajectories were made whole and centered on the protein (`gmx trjconv -pbc mol -center`) and subsampled to 100-ps intervals (501 frames). This step is required because the peptide is a separate molecule: in the uncorrected trajectory of one of the systems the distance between the centers of mass of receptor and peptide reached 94.8 Å (median 44.7 Å, box edge 116 Å) although the peptide remained in contact with the receptor in every frame. Analyses used MDAnalysis {michaud2011;gowers2016} 2.9.0. The S1 aspartate was the equivalent of Asp189 from Section 2.2 (its residue name was checked in every system). In each frame, the distance from every peptide residue to the carboxylate oxygens of that aspartate was taken as the minimum heavy-atom distance with the minimum-image convention. The peptide residue with the smallest mean distance was defined as the anchor, without assuming which residue it would be. S1 occupancy is the fraction of frames with anchor–Asp189 distance below 4, 5 or 6 Å, reported for the whole trajectory and separately for each half. We also report the fraction of frames in which any peptide heavy atom was within 4.5 Å of the Oγ of the catalytic serine or of the Nε2 of the catalytic histidine, the fraction of frames with any peptide–receptor contact within 4.5 Å, and the RMSD of the peptide Cα atoms after superposition on the receptor Cα atoms (reference: first production frame), computed after making the peptide whole and translating it to the periodic image nearest the S1 aspartate. Following the criterion declared in our project plan, an occupancy of at least 70% at 5 Å is used as the descriptive threshold for "S1-anchored"; because each candidate was simulated once, no statistical inference is made.

### 2.10 Software, hardware and data availability

Calculations ran on one NVIDIA GeForce RTX 5070 Ti (16 GB) under Linux with 32 CPU cores (Python 3.10/3.11; PyTorch 2.12/2.13 with CUDA 12.8/13.0). Code, configuration, the transferred subsite table, calibration data, candidate lists and per-candidate scores are available in the project repository (https://github.com/eulaliobqi/design-inibidores) [repository visibility and archival DOI to be confirmed before submission]. Trajectories are not deposited because of size and are available on request.

---

## 3 Results

### 3.1 The receptor panel: eight targets and two reference species

All ten sequences carry the catalytic motif G[DN]SGG[PT] and have an aspartate at the specificity position, six residues before the catalytic serine (Table 1), which is the residue found for bovine trypsin (Asp194 of the precursor) and not for chymotrypsinogen A (Ser189). Identity to *M. sexta* trypsin B ranged from 44.3% (*P. xylostella*) to 71.0% (*C. includens*) among the pest species, against 96.1% for the *M. sexta* paralog P35045, and the mean pLDDT of the models was 88.9–92.2. The panel is therefore trypsin-type despite the automatic "Chymotrypsin" annotation, but it has not been validated by expression data for the pest species (Section 2.1).

**Table 1.** Receptor panel (AlphaFold models). Identity: to *M. sexta* P35046 (Section 2.1). Numbers of the catalytic serine and of the Asp189-equivalent refer to the residue numbering of the model.

| Species | UniProt | Length | Identity (%) | Mean pLDDT | Ser (cat.) | Asp189-eq. | Role |
|---|---|---|---|---|---|---|---|
| *Spodoptera frugiperda* | A0A089QDB3 | 266 | 50.4 | 89.8 | 220 | 214 | target |
| *Spodoptera litura* | B3F884 | 254 | 67.3 | 90.1 | 211 | 205 | target |
| *Ostrinia nubilalis* | Q6R561 | 256 | 66.4 | 89.7 | 213 | 207 | target |
| *Diatraea saccharalis* | T1QDI0 | 257 | 65.2 | 91.0 | 213 | 207 | target |
| *Chrysodeixis includens* | A0A9P0BRD5 | 255 | 71.0 | 90.4 | 212 | 206 | target |
| *Heliothis virescens* | I7D523 | 263 | 48.4 | 89.9 | 219 | 213 | target |
| *Plutella xylostella* | E2IGY7 | 255 | 44.3 | 90.6 | 211 | 205 | target |
| *Anticarsia gemmatalis* | A0A2U8NFD7 | 260 | 63.3 | 90.9 | 217 | 211 | target |
| *Manduca sexta* | P35045 | 256 | 96.1 | 92.2 | 213 | 207 | reference (curated midgut) |
| *Bombyx mori* | A0A8R2C8B0 | 255 | 67.8 | 88.9 | 212 | 206 | not used as target |

### 3.2 Subsite transfer succeeded for all receptor–template pairs

P1 was Lys15 in BPTI and Lys5 in SFTI-1, obtained from geometry (Section 2.2). In both complexes the S1 contact set had 14 trypsin residues, including Asp189, Ser190, Cys191, Gln192, Gly193, Asp194, His57, Ser195, Val213, Ser214, Trp215, Gly216, Gly219 and Gly226 (Table 2). All 20 receptor–template pairs (10 receptors × 2 templates) were accepted, with alignment TM-score 0.946–0.957 and RMSD 1.18–1.41 Å, and all subsite residues could be transferred (48/48 for 2PTC and 49/49 for 1SFI, exosite included). The Asp189-equivalent obtained from the structural alignment coincided with the one obtained independently from the sequence offset in all ten receptors, and residue numbering of the transferred table matched the numbering of the models.

**Table 2.** Reference subsites (residues of bovine trypsin within 4.5 Å of the inhibitor residue at each position).

| Subsite | BPTI residue | Trypsin contacts (2PTC) | SFTI-1 residue | Trypsin contacts (1SFI) |
|---|---|---|---|---|
| S4 | Gly12 | Gln192 | Arg2 | Asn97, Gln175, Gly216, Ser217, Trp215 |
| S3 | Pro13 | Gln192, Gly216, Trp215 | Cys3 | Gln192, Gly216, Trp215 |
| S2 | Cys14 | Gln192, His57, Leu99, Ser195, Ser214, Trp215 | Thr4 | Gln192, His57, Leu99, Ser195, Ser214, Trp215 |
| S1 | Lys15 | Asp189, Asp194, Cys191, Gln192, Gly193, Gly216, Gly219, Gly226, His57, Ser190, Ser195, Ser214, Trp215, Val213 | Lys5 | same 14 residues |
| S1′ | Ala16 | Cys42, Gln192, Gly193, His57, Phe41, Ser195 | Ser6 | same 6 residues |
| S2′ | Arg17 | Gln192, Gly193, His40, Phe41, Tyr151, Tyr39 | Ile7 | same 6 residues |
| S3′ | Ile18 | His57, Phe41, Tyr39 | Pro8 | none |

### 3.3 Calibration: Boltz-2 and ligand RMSD separate inhibitors from decoys, MM-GBSA does not

Boltz-2 gave a higher confidence for the real inhibitor than for its shuffled decoy in 10 of 10 pairs (differences of 0.042–0.274; median 0.190), and the same held for complex pLDDT (10/10; 0.026–0.312) and for ipTM (10/10; 0.005–0.399, the smallest margin being that of SKTI with *S. frugiperda*, 0.711 against 0.706). Absolute values overlapped, however: real inhibitors scored 0.850–0.986 and decoys 0.628–0.944, and the shuffled SFTI-1 decoy (14 residues) reached 0.944 with bovine trypsin (Table 3). Discrimination therefore holds within a pair but not as an absolute threshold (Figure 2A).

The ligand RMSD after superposition on the receptor (2 ns, last third) was lower for the real inhibitor than for its decoy in 9 of 10 pairs (Figure 2B); the exception was *S. frugiperda*–EcTI (0.366 versus 0.347 nm). The number of receptor residues in contact with the ligand was larger for the real inhibitor in only 2 of 10 pairs.

MM-GBSA favored the real inhibitor in only 4 of 10 pairs; in the other six the decoy was more favorable, by up to 144.8 kcal mol^−1^ (Table 3). Across the 22 systems, ΔG correlated with the number of receptor residues in contact with the ligand (Spearman ρ = −0.93, *P* = 7 × 10^−10^; a post hoc analysis), whereas it did not correlate with ligand length (ρ = −0.27, *P* = 0.23). In this single-trajectory 2-ns setting, MM-GBSA behaved as a measure of interface size (Figure 2C, D) and was not used for decisions. In one system (*S. frugiperda*–BPTI) the ligand was found in a different periodic image of the receptor in at least one frame of the trajectory used for MM-GBSA, which is a further reason not to interpret the absolute values.

**Table 3.** Calibration pairs (real inhibitor / shuffled decoy). Conf.: Boltz-2 confidence score. RMSD: ligand RMSD after receptor superposition (nm, last third of 2 ns). Contact: mean number of receptor residues within 4.5 Å of the ligand. ΔG: MM-GBSA (kcal mol^−1^). Bold marks a pair in which the decoy scored better than the real inhibitor.

| Receptor | Inhibitor | Conf. | RMSD (nm) | Contact | ΔG (kcal mol^−1^) |
|---|---|---|---|---|---|
| bovine | SFTI-1 | 0.986 / 0.944 | 0.084 / 0.206 | 25.1 / 23.5 | -70.2 / -64.8 |
| bovine | BBI | 0.931 / 0.794 | 0.372 / 0.452 | **22.1 / 28.1** | **-66.1 / -68.5** |
| bovine | BPTI | 0.962 / 0.796 | 0.380 / 0.643 | **24.4 / 25.6** | -68.8 / -52.5 |
| bovine | EcTI | 0.934 / 0.687 | 0.181 / 0.537 | **31.3 / 31.4** | **-72.7 / -79.0** |
| bovine | SKTI | 0.954 / 0.680 | 0.275 / 0.364 | **29.6 / 36.3** | **-77.4 / -103.0** |
| *S. frugiperda* | SFTI-1 | 0.933 / 0.869 | 0.129 / 0.274 | 35.8 / 31.0 | -86.0 / -84.0 |
| *S. frugiperda* | BBI | 0.862 / 0.650 | 0.349 / 1.167 | **37.3 / 68.7** | **-88.6 / -151.2** |
| *S. frugiperda* | BPTI | 0.877 / 0.755 | 0.317 / 0.342 | **40.7 / 52.2** | **-112.7 / -131.6** |
| *S. frugiperda* | EcTI | 0.868 / 0.637 | **0.366 / 0.347** | **38.0 / 66.9** | **-78.9 / -223.7** |
| *S. frugiperda* | SKTI | 0.853 / 0.628 | 0.200 / 0.466 | **50.7 / 54.4** | -129.2 / -128.6 |

### 3.4 The generation campaign

Generation produced 110 macrocyclic backbones per species (10 per length, 11 lengths), 880 in total. In all of them the chain of the peptide had the requested length, and the N–C closure distance was 0.76–1.40 Å (none above 2 Å). These values indicate that the closure constraint was met within the tolerance of the backbone model; the backbones were not relaxed at all-atom level, and bond geometry was not validated. ProteinMPNN yielded 22,066 unique sequences (2,692–2,839 per species, Table 4), all with the length of their backbone. The hotspot residues effectively passed to RFdiffusion were those listed in Section 2.4 and can be read from the `.trb` file of every backbone.

### 3.5 The motif screen selects short peptides without basic residues

With the circular scan, 1,829 of 22,066 sequences (8.3%) were labelled RESISTENTE, 4,987 (22.6%) MARGINAL and 15,250 (69.1%) SUSCEPTIVEL (Table 4 and Figure 3). The screen mainly removed long sequences: the RESISTENTE set had a mean length of 7.05 residues and 95.6% of its members had 10 residues or fewer, against a mean of 15.74 residues and 12.7% for the SUSCEPTIVEL set (Figure 3A). Only 4.3% of the RESISTENTE sequences contained any lysine or arginine, against 85% of the SUSCEPTIVEL ones, and in only 1.3% did the geometric P1 proxy fall on a lysine or arginine. Glycine (19.5%), threonine (14.1%), proline (13.3%), serine (9.8%) and aspartate (9.3%) were the most frequent residues of the RESISTENTE set, and arginine and lysine together accounted for 0.7%.

**Table 4.** Campaign summary per target.

| Species | Backbones | Unique sequences | RESISTENTE | MARGINAL | SUSCEPTIVEL | Top candidate (Boltz-2 confidence) |
|---|---|---|---|---|---|---|
| *S. frugiperda* | 110 | 2,731 | 147 | 621 | 1,963 | [[PENDING]] |
| *S. litura* | 110 | 2,706 | 205 | 607 | 1,894 | [[PENDING]] |
| *O. nubilalis* | 110 | 2,739 | 238 | 667 | 1,834 | [[PENDING]] |
| *D. saccharalis* | 110 | 2,807 | 247 | 638 | 1,922 | [[PENDING]] |
| *C. includens* | 110 | 2,778 | 235 | 640 | 1,903 | [[PENDING]] |
| *H. virescens* | 110 | 2,774 | 189 | 614 | 1,971 | [[PENDING]] |
| *P. xylostella* | 110 | 2,692 | 287 | 539 | 1,866 | [[PENDING]] |
| *A. gemmatalis* | 110 | 2,839 | 281 | 661 | 1,897 | [[PENDING]] |
| Total | 880 | 22,066 | 1,829 | 4,987 | 15,250 | |

### 3.6 Boltz-2 confidence of the RESISTENTE candidates

[[PENDING: Boltz-2 statistics for the eight species. Provisional values for the seven species already scored (n = 1,548): mean confidence 0.859, median 0.864, range 0.695–0.953; 262 (16.9%) with confidence ≥0.9 and 1,382 (89.3%) ≥0.8; mean confidence per length 0.86 for 5–10 residues and 0.83 for 12 residues; Spearman correlation between length and confidence ρ = −0.08. The values will be recomputed with the eighth species and with the final candidate set.]]

### 3.7 Molecular dynamics of the top candidates

[[PENDING: 50-ns simulations of the top-ranked RESISTENTE candidate of each of the eight species (selection rule in Section 2.8), with the analysis of Section 2.9: anchor residue, S1 occupancy at 4, 5 and 6 Å (overall and by halves), contact with the catalytic serine and histidine, and local peptide RMSD.]]

---

## 4 Discussion

[[DISCUSSION — DRAFTING NOTES ONLY, TO BE WRITTEN AFTER SECTIONS 3.6–3.7 ARE COMPLETE; see the end of this file]]

---

## Figure legends

**Figure 1.** Overview of the pipeline and of the number of items at each step. Blue: definition of targets and subsites; orange: calibration of the scoring ladder; green: generation and triage of candidates. Selectivity against non-target proteases, enzymatic activity and closure of the macrocycle in the MD topology were not addressed.

**Figure 2.** Calibration of the scoring ladder with six natural inhibitors and shuffled decoys (22 systems; Bt: bovine trypsin, Sf: *S. frugiperda*). (A–C) Real inhibitor (filled) and shuffled decoy (open) for (A) Boltz-2 confidence, (B) RMSD of the ligand backbone after superposition on the receptor (2 ns, last third) and (C) MM-GBSA ΔG; a connector is red when the decoy scored better than the real inhibitor (in C, higher scores are less favorable). The number of pairs (out of 10) in which the real inhibitor scored better is given in each panel title. (D) MM-GBSA ΔG against the mean number of receptor residues within 4.5 Å of the ligand for the 22 systems (post hoc analysis).

**Figure 3.** Properties of the 22,066 designed sequences by class of the cleavage-motif screen. (A) Length distribution within each class. (B) Percentage of sequences containing lysine or arginine, and of sequences in which the residue closest to the catalytic serine in the design backbone (geometric P1 proxy) is lysine or arginine. (C) Amino-acid composition of the resistant-like and susceptible classes.

---

## Drafting notes (remove before submission)

1. **Abstract, Sections 3.6–3.7 and Discussion depend on pending computations** (Boltz-2 of the *A. gemmatalis* candidates, selection of the top candidate per species under the corrected screen, eight 50-ns simulations).
2. **Points the Discussion must make (each supported by data above):**
   - Calibration: Boltz-2 discriminates within pairs but not by absolute value; short-peptide decoys reach 0.94; the metric was calibrated on 14–176-residue ligands and not on 5–8-residue macrocycles.
   - Methodological lesson: RMSD computed without periodic-boundary correction gave a false "chance-level" result; the corrected ligand RMSD separated 9/10 pairs. MM-GBSA tracked interface size (ρ = −0.93).
   - The cleavage screen selects short, basic-free peptides, i.e. it works against the canonical P1 Lys/Arg–Asp189 interaction; tension between proteolytic resistance and S1 engagement (Introduction).
   - Limitations: computational only; no selectivity analysis; single 50-ns replicate, legacy force field, linear topology of the peptide, pH 10 protonation; ProteinMPNN with the receptor not fixed; hotspot list truncated to eight residues; AlphaFold models without expression evidence for pest species; motif-based (not measured) resistance label; Boltz-2 not validated for short cyclic peptides.
   - Outlook: fix the receptor in ProteinMPNN and impose the basic-P1 exception at design time; close the ring in the topology; replicate simulations; counter-selection panel; enzymatic assays with *A. gemmatalis* midgut extracts.
3. Author list, affiliations, funding, conflict-of-interest, author-contribution, ethics (not applicable) and the generative-AI-use statement required by the journal are still to be completed by the authors.

# From Natural Protease Inhibitors to De Novo Candidate Peptides Targeting Digestive Trypsins of Lepidopteran Pests

**Running title:** De novo candidate peptides against pest trypsins

**Authors:** [AUTHOR LIST TO BE COMPLETED]  
**Affiliations:** [TO BE COMPLETED]  
**Correspondence:** [TO BE COMPLETED]

**Article type:** Original Research — section *Informatics and Computational Methods*  
**Keywords:** natural protease inhibitors, de novo peptide design, digestive trypsin, Lepidoptera, *Anticarsia gemmatalis*, proteolytic resistance, molecular dynamics, binding free energy

---

## Abstract

**Background:** Plant protease inhibitors can impair lepidopteran pests, but they are large, and peptides derived from their reactive loops inhibit digestive trypsins only at sub-millimolar to millimolar concentrations. Whether natural inhibitors can guide *de novo* design of short peptides that the larval gut will not degrade, and whether deep-learning and free-energy scores can rank them, is unknown. **Methods:** For eight soybean lepidopteran pests, including *Anticarsia gemmatalis*, catalytic subsites from natural-inhibitor crystal complexes were transferred to AlphaFold models, and a scoring ladder (Boltz-2, molecular dynamics, MM-GBSA, PRODIGY) was calibrated with six inhibitors and shuffled decoys. We designed 22,066 sequences on macrocyclic backbones (RFdiffusion, ProteinMPNN), kept those without a P1 residue of midgut trypsin-, chymotrypsin- or elastase-like proteases, co-folded them with Boltz-2, and simulated the top three per species for 10 ns, linear and macrocyclic. **Results:** Boltz-2 scored the inhibitor above its decoy in 10 of 10 pairs; MM-GBSA did so in 4 of 10 and PRODIGY in 2 of 10, and both tracked interface size (ρ = −0.93 and −0.79). The criterion kept 527 linear and 543 cyclic sequences, 49% glycine. Repeated Boltz-2 runs correlated at 0.57 (n = 442), close to the 0.50 between the linear and cyclic forms of one sequence. In 48 simulations at pH 10.0 (one run each) the median anchor–Asp189 distance rose from 5.7 to 6.8 Å (linear) and from 5.1 to 6.1 Å (macrocyclic); four anchors ended within 4 Å, all having started within 4.0 Å. The same 48 complexes at pH 8.2 did not differ from pH 10.0 in any paired metric (final distance *P* = 0.16, occupancy *P* = 0.88). The paired Boltz-2 difference against shuffled controls was positive for 63 of 78 linear and 60 of 79 macrocyclic candidates, within prediction noise. **Conclusions:** Natural inhibitors served as templates and calibration standards, but Boltz-2 confidence supports only pairwise comparisons, MM-GBSA and PRODIGY order candidates by interface size, and 10-ns S1 occupancy follows the starting pose. Requiring non-cleavability selects short, glycine-rich peptides, which makes the trade-off between resistance and S1 engagement explicit. All results are computational; selectivity and activity were not tested.

---

## 1 Introduction

Lepidopteran larvae limit soybean productivity in South America, and the velvetbean caterpillar *Anticarsia gemmatalis* is one of the defoliators (Carpane et al., 2022; de Almeida Barros et al., 2021). Protein digestion takes place in a strongly alkaline midgut, the highest luminal pH known in a biological system (Dow, 1992); insect digestion is reviewed in Terra and Ferreira, 1994. Trypsin-like serine proteases are the main digestive enzymes of *A. gemmatalis* larvae (de Almeida Barros et al., 2021; da Silva Júnior et al., 2020), expressed as multiple isoforms (Silva-Júnior et al., 2021).

Plant protease inhibitors are examined as leads for pest control: the seed inhibitor ApTI is a tight-binding inhibitor of *A. gemmatalis* trypsins (Meriño-Cabrera et al., 2020a), and BPTI and the soybean Kunitz inhibitor reduced larval survival (de Almeida Barros et al., 2022a). Larvae adapt, however, by inducing insensitive proteases, regulating several digestive enzymes and, in some species, expanding gene families (Jongsma et al., 1995; Jongsma and Bolter, 1997; Kuwar et al., 2015; Lomate et al., 2018; Souza et al., 2016); in *A. gemmatalis*, the soybean Kunitz inhibitor induced serine proteases, whereas the tripeptide GORE-2 repressed digestive protease transcripts (Júnior et al., 2026). Short peptides that mimic the reactive-center loop are cheaper to produce than proteins: linear peptides from a Kunitz inhibitor–trypsin interface inhibited *S. cosmioides* trypsins (Meriño-Cabrera et al., 2020b), tripeptides inhibited *Helicoverpa armigera* proteases with higher efficacy at alkaline gut pH (Saikhedkar et al., 2018), and bicyclic peptides from the same loops were ten-fold more potent than linear ones (Saikhedkar et al., 2019). In *A. gemmatalis*, the tripeptides GORE1 and GORE2 are reversible competitive inhibitors (K~i~ 0.49 and 0.10 mM) that impair larval survival (de Almeida Barros et al., 2021), and their complexes have been examined by molecular dynamics (de Almeida Barros et al., 2022b). Peptides inspired by the loops of BPTI and the soybean Kunitz inhibitor (Paulo et al., 2026) and peptides from the trypsinogen pro-region (Mariano et al., 2026) were designed against *A. gemmatalis* trypsin-like proteases, and a structure-guided peptide against *Spodoptera frugiperda* trypsins has been proposed (Severiche-Castro et al., 2026). Their millimolar potency leaves room for designs with higher affinity and stability (de Almeida Barros et al., 2021; Schultz et al., 2026).

Canonical inhibitors insert the P1 residue of an exposed loop into the S1 pocket (Laskowski and Kato, 1980; Laskowski and Qasim, 2000). In trypsin-like enzymes S1 is defined by Asp189 and favors lysine and arginine (Perona and Craik, 1995; Hedstrom, 2002; Patarroyo-Vargas et al., 2017), which are also the cleavage sites of the target enzyme. A peptide cleaved in the gut cannot reach its target, so proteolytic stability is a requirement: the midgut also holds chymotrypsin-like and elastase-like endopeptidases and exopeptidases (Valaitis, 1995; Valaitis et al., 1999; Yang et al., 2013; Zhan et al., 2011; Nakonieczny et al., 2007). A sequence without the P1 residues of these enzymes and, as a head-to-tail macrocycle, without free termini should in principle resist them.

Deep-learning tools now generate peptide backbones and sequences *de novo* (Watson et al., 2023; Dauparas et al., 2022; Rettie et al., 2025) and co-fold complexes (Wohlwend et al., 2024; Passaro et al., 2025), but their affinity outputs correlate only weakly to moderately with physics-based free energies (Wan et al., 2026), their confidence ranks cyclic-peptide poses only moderately (Li et al., 2026), and end-point free-energy scores depend on sampling and system type (Hou et al., 2011; Genheden and Ryde, 2015; Xu et al., 2025). A design campaign against insect proteases therefore needs an explicit calibration of each score it uses.

Here we ask how far natural inhibitors can be carried into *de novo* candidate peptides directed at lepidopteran digestive trypsins. Natural inhibitors supply the structural templates, the calibration standards and the P1–S1 logic; *de novo* design is asked to supply small size and the absence of cleavage motifs. We (i) define the catalytic subsites of eight pest trypsins by structural transfer, (ii) calibrate a scoring ladder (Boltz-2, molecular dynamics, MM-GBSA, PRODIGY) against six natural inhibitors and shuffled decoys, (iii) generate head-to-tail macrocyclic backbones with RFdiffusion and ProteinMPNN, (iv) apply a hard non-cleavability criterion, (v) co-fold the survivors and simulate them as linear peptides and as macrocycles, and (vi) rank them by stage with a free-energy filter (Figure 1). The work is entirely computational: it includes no assay and no test of selectivity against non-target proteases.

---

## 2 Materials and methods

### 2.1 Receptors and catalytic subsites

Digestive trypsin-like proteases of eight pest species (*S. frugiperda*, *S. litura*, *Ostrinia nubilalis*, *Diatraea saccharalis*, *Chrysodeixis includens*, *Heliothis virescens*, *Plutella xylostella*, *A. gemmatalis*) and the references *Manduca sexta* and *Bombyx mori* were modeled with AlphaFold v2 structures (Jumper et al., 2021; Varadi et al., 2024) (Table 1). Only the *M. sexta* entries are reviewed with midgut evidence; for the other species the entries were selected by homology. Sequence identity to *M. sexta* trypsin B (P35046) used a global BLOSUM62 alignment (Cock et al., 2009). The specificity residue was located six residues before the catalytic serine (motif G[DN]SGG[PT]), an offset calibrated on bovine trypsin and chymotrypsinogen A (UniProt Consortium, 2025).

Subsites S4–S3′ (Schechter and Berger, 1967) were defined from two crystal complexes of bovine trypsin (Berman et al., 2000), 2PTC (BPTI) and 1SFI (SFTI-1; Luckett et al., 1999). P1 was the inhibitor residue whose carbonyl carbon lies closest to the Oγ of the catalytic serine, and a trypsin residue was assigned to a subsite when any of its atoms was within 4.5 Å of the corresponding inhibitor residue. Each trypsin chain was aligned to each receptor with Foldseek in TM-align mode (van Kempen et al., 2024; Zhang and Skolnick, 2005), residues were transferred through the alignment, and a receptor–template pair was accepted with a TM-score of at least 0.5 and an RMSD of at most 3.0 Å.

### 2.2 Calibration of the scoring ladder

Six natural inhibitors served as positive controls: BPTI (1BPI; Parkin et al., 1996), SFTI-1 (1SFI, linear), soybean Kunitz inhibitor (SKTI, 1AVU; Song and Suh, 1998), Bowman–Birk inhibitor (BBI, 1BBI; Werner and Wemmer, 1992), the *Enterolobium contortisiliquum* inhibitor (EcTI, 4J2K; Zhou et al., 2013) and ApTI (UniProt; no structure). A shuffled decoy of the same composition was generated for each except ApTI. Each ligand was modeled with bovine β-trypsin and with the *S. frugiperda* model A0A089QDB3 (22 systems). Four scores were compared: (i) Boltz-2 confidence (Passaro et al., 2025) (ColabFold MSA (Mirdita et al., 2022); one sample); (ii) the RMSD of the ligand backbone after receptor superposition in a 2-ns simulation (Section 2.6; last third; pH 8.0 for bovine trypsin and 10.0 for the *S. frugiperda* model); (iii) MM-GBSA with gmx_MMPBSA (Valdés-Tresanco et al., 2021) (igb = 5, 0.150 M salt, 45 frames from the last third, no entropy term); (iv) PRODIGY (Vangone and Bonvin, 2015) on four frames of the last third. A score separated a pair when the real inhibitor had the better value, with the direction fixed beforehand. The ten pairs are not independent, because each decoy is used with two receptors.

### 2.3 Backbone generation and sequence design

Head-to-tail cyclic backbones were generated with RFdiffusion 1.1.0 (Watson et al., 2023) (`Complex_base_ckpt`, 50 steps, `noise_scale_ca` 0.2, `noise_scale_frame` 0.1, cyclic mode, receptor fixed): ten backbones for each of 11 lengths (5, 6, 7, 8, 10, 12, 14, 16, 18, 19, 20 residues) and each of the eight targets (880 backbones). Hotspots were the S1 and S2 residues transferred from 1SFI; only the first eight in residue number reached RFdiffusion (equivalents of His57, Leu99, Asp189, Ser190, Cys191, Gln192, Gly193 and Asp194). ProteinMPNN (Dauparas et al., 2022) (`v_48_020`, T = 0.1, backbone noise 0.05, no cysteine, 30 sequences per backbone) was run with default chain settings, so the receptor was also redesigned and only the peptide was kept. Identical sequences were merged within each species.

### 2.4 Non-cleavability screens

*Motif-score screen (first round).* Each sequence was scanned circularly with seven simplified P1-motif rules based on PeptideCutter (Gasteiger et al., 2005) (trypsin, chymotrypsin at two specificities, an elastase-like rule, Lys-C, Arg-C and a pepsin-like rule). A weighted count of sites (weights 1.0, 0.6, 0.3 for enzyme priorities 1–3; only internal sites for trypsin; divided by 10 and capped at 1) gave a score. A sequence was labelled *resistant-like* with no internal trypsin site and a score below 0.3, *marginal* with at most one internal site and a score below 0.5, and *susceptible* otherwise. The labels are motif-based predictions and do not measure proteolysis.

*Hard criterion.* A sequence was kept only if no residue was K or R (trypsin-like), F, Y, W, L or M (chymotrypsin-like), or A or V (elastase-like), unless the next residue was proline. In the linear peptide the C-terminal residue was also evaluated (it must not belong to this set or be isoleucine, because of carboxypeptidases); in the macrocycle the closing bond was evaluated like any other. Isoleucine was allowed in the interior. The rule was applied to the same sequences for the linear (front L) and cyclic (front M) interpretation. It rests on reported midgut specificities (Valaitis, 1995; Valaitis et al., 1999; Yang et al., 2013; Zhan et al., 2011; Nakonieczny et al., 2007); the K/R–Pro exception is an approximation, and aminopeptidase N, which needs a free N-terminus, is not excluded for linear peptides.

### 2.5 Co-folding, re-scoring and pose quality

Candidates were co-folded with Boltz-2 2.2.1 (Passaro et al., 2025) (receptor MSA from ColabFold (Mirdita et al., 2022); peptide without MSA, `cyclic: true` for macrocycles). We report the `confidence_score` (verified equal to 0.8·pLDDT + 0.2·ipTM), pLDDT and ipTM; affinity outputs were not used. *E1:* the 527 linear and 543 cyclic candidates of the hard criterion, one prediction each. *E2:* the ten best candidates per species and front were re-predicted with five diffusion samples, three recycling steps, inference-time potentials and three seeds (15 predictions); the score is the mean and the best sample is the starting structure. *E3:* three shuffled controls per E2 candidate were predicted with the same protocol, and Δ = score of the candidate − mean score of its controls. *E4:* pose quality control, with thresholds fixed beforehand: no peptide–receptor heavy-atom pair closer than 2.2 Å; |ω| ≥ 150° (Pro cis accepted); L chirality; His57 Nε2–Ser195 Oγ ≤ 3.8 Å; for macrocycles, closing C–N ≤ 1.5 Å and closing ω ≥ 150°. The best candidate of each species was also co-folded with the seven other receptors (8 × 8 cross matrix). The three candidates per species and front with the highest mean E2 confidence among distinct sequences (24 linear, 24 cyclic) went to simulation; Δ was not used for selection.

### 2.6 Molecular dynamics

Each of the 48 complexes was simulated for 10 ns at pH 10.0 (screening pH, chosen for the larval midgut: *H. virescens* gut extracts at pH 9.56–10.0 (Karumbaiah et al., 2007); (Dow, 1992)) and at pH 8.2, the pH of the enzymatic assays with the GORE peptides (0.1 M Tris-HCl, 20 mM CaCl~2~ (Schultz et al., 2026)), so that the simulated conditions match those under which a Ki would be measured. Protonation was assigned with PROPKA 3 (Olsson et al., 2011) through PDB2PQR (Dolinsky et al., 2007). Systems were built with GROMACS 2025.4 (Abraham et al., 2015), the CHARMM36 force field (Huang and MacKerell, 2013) (port made with charmm2gmx (Wacha and Lemkul, 2023)) and TIP3P water Jorgensen et al., 1983 in a dodecahedral box (1.2-nm buffer, 0.10 M KCl). The linear peptide carries NH~3~^+^ and COO^−^ termini at both pH; the macrocycle has no termini, and pdb2gmx forms the head-to-tail bond from the Boltz-2 geometry (the assembly script stops if the closing bond or CMAP term is missing). After minimization, 200 ps NVT and 500 ps NPT with position restraints (1,000 kJ mol^−1^ nm^−2^), production ran for 10 ns at 300 K and 1 bar (velocity-rescaling thermostat Bussi et al., 2007; Parrinello–Rahman barostat Parrinello and Rahman, 1981; PME Essmann et al., 1995; 1.2-nm cutoffs, force-switched van der Waals; LINCS; 2-fs step). Each system was run once per pH with a random seed; four candidates per front (NGGRPDAP, GQNDS, PTTTQT and GSNIN linear; GGHSE, GGKPGEP, IYPETG and SGSTDIE cyclic) were run again at each pH with another seed to estimate run-to-run variation.

### 2.7 Trajectory analysis

Trajectories were made whole and centered (`gmx trjconv -pbc mol -center`), because receptor and peptide are separate molecules that can be written to different periodic images; analyses used MDAnalysis 2.9.0 (Michaud-Agrawal et al., 2011; Gowers et al., 2016). In each frame, the distance from each peptide residue to the carboxylate oxygens of the Asp189 equivalent was the minimum heavy-atom distance, and the residue with the smallest mean distance was the anchor (defined post hoc, without assuming which residue). S1 occupancy is the fraction of frames with anchor–Asp189 distance below 5 Å (4 and 6 Å also computed), for the whole trajectory and each half. The anchor–Asp189 distance and the peptide Cα RMSD after receptor superposition are reported for an initial (first 0.4 ns) and a final window (last 2 ns). We also report the fraction of frames with any peptide atom within 4.5 Å of the catalytic Ser Oγ or His Nε2 or of the receptor and, for macrocycles, the closing C–N distance and ω in every frame. The screen declared beforehand required second-half occupancy ≥ 70%, the same anchor in both halves and, for macrocycles, an intact ring (C–N ≤ 1.5 Å, ω ≥ 150° in every frame). On 2 October 2026, after the first 16 simulations, occupancy was demoted from a gate to a description (Section 3.5), a change of the declared procedure made after seeing data. With one run per candidate no statistical inference is made.

*Attack geometry.* In the second half of each run, for every peptide bond (the closing bond included; the C-terminal carboxylate excluded) we measured the Ser195 Oγ–carbonyl C distance, the Oγ···C=O angle and the carbonyl O distance to the backbone N of Gly193 and Ser195 (oxyanion hole). A near-attack conformation required < 3.5 Å, 90–125° and < 3.5 Å; the thresholds were chosen for this analysis and not calibrated against a known substrate (`scripts/scissile_geometry.py`).

### 2.8 Energy filter, ranking and pH comparison

MM-GBSA used gmx_MMPBSA (Valdés-Tresanco et al., 2021) (MMPBSA.py (Miller et al., 2012); generalized Born igb = 5 (Onufriev et al., 2004); 0.150 M salt; single trajectory; no entropy) on the second half of each trajectory (126 frames; receptor chain A, peptide chain B), with a standard error over five blocks of frames. PRODIGY (Vangone and Bonvin, 2015), a contact-based predictor with no explicit protonation, was applied to the initial pose (protonated at pH 8.2) and to 30 frames of the second half. Both scores grow with interface size, so each is also given per residue. Each stage ranks the candidates within a front (1 = best; ties receive the mean rank): Boltz-2 E2 confidence, paired Δ (E3), final peptide RMSD at pH 8.2, PRODIGY on the pose, and PRODIGY and MM-GBSA on the trajectory at pH 8.2; the aggregate is the mean rank over the stages. The ranking covers candidates that passed the pose quality control, had Δ > 0 and, for macrocycles, met the strict ring criterion; S1 occupancy does not enter (Section 3.5). The pH 8.2 and pH 10.0 simulations are paired (same pose and protocol; they differ in side-chain protonation, counter-ions and seed) and compared by the paired difference of each metric (Wilcoxon signed-rank test), the rank correlation between pH and the agreement of categorical outcomes, read against the difference between runs of the same pH.

### 2.9 Software and data

Calculations ran on one NVIDIA RTX 5070 Ti (16 GB) with 32 CPU cores (Python 3.10/3.11; PyTorch 2.12/2.13, CUDA 12.8/13.0). Code, configuration, subsite table, calibration data, candidate lists and scores are available in the project repository (https://github.com/eulaliobqi/design-inibidores) [repository visibility and archival DOI to be confirmed]. Trajectories are available on request.

---

## 3 Results

### 3.1 Receptor panel and subsite transfer

All ten sequences carry the catalytic motif G[DN]SGG[PT] and an aspartate at the specificity position, the residue found for bovine trypsin and not for chymotrypsinogen A (Table 1). Identity to *M. sexta* trypsin B ranged from 44.3% (*P. xylostella*) to 71.0% (*C. includens*) among the pests; mean pLDDT was 89.7–91.0 for the eight pest models and 88.9–92.2 across the ten. The panel is therefore trypsin-type despite the automatic "Chymotrypsin" annotation, but expression of these enzymes in the pest midguts is not documented (Section 2.1). P1 was Lys15 in BPTI and Lys5 in SFTI-1; in both complexes the S1 contact set had 14 trypsin residues, including Asp189, Ser190, Cys191, Gln192, Gly193, Asp194, His57, Ser195, Val213, Ser214, Trp215, Gly216, Gly219 and Gly226 (Table S1). All 20 receptor–template pairs were accepted (TM-score 0.946–0.957; RMSD 1.18–1.41 Å), all subsite residues were transferred (48 of 48 for 2PTC and 49 of 49 for 1SFI, exosite included), and the Asp189 equivalent found by structure matched the one found from sequence in all ten receptors.

**Table 1.** Receptor panel (AlphaFold models). Identity: to *M. sexta* P35046. Numbers of the catalytic serine and of the Asp189 equivalent refer to the numbering of the model.

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

### 3.2 Calibration of the scoring ladder

Boltz-2 gave a higher confidence for the real inhibitor than for its decoy in 10 of 10 pairs (differences 0.042–0.274; median 0.190), as did complex pLDDT (10/10) and ipTM (10/10; the smallest margin was SKTI with *S. frugiperda*, 0.711 against 0.706). Absolute values overlapped (real inhibitors 0.853–0.986, decoys 0.628–0.944; the shuffled SFTI-1 decoy reached 0.944 with bovine trypsin), so the discrimination holds within a pair and not as an absolute threshold (Figure 2A, Table 2). The ligand RMSD was lower for the real inhibitor in 9 of 10 pairs (the exception was *S. frugiperda*–EcTI, 0.366 against 0.347 nm; Figure 2B).

MM-GBSA favored the real inhibitor in 4 of 10 pairs and PRODIGY in 2 of 10 (Figure 2C, D; Table 2). Across the 22 systems, the MM-GBSA ΔG correlated with the number of receptor residues in contact with the ligand (Spearman ρ = −0.93, *P* = 7 × 10^−10^; post hoc) and not with ligand length (ρ = −0.27, *P* = 0.23), and the PRODIGY ΔG correlated with its number of intermolecular contacts (ρ = −0.79, n = 22); the decoy had more contacts than its inhibitor in 7 of the 10 pairs (in one of them by 0.25 contacts) (Figure 2E, F). In this setting both scores therefore behave as measures of interface size and are used below to order candidates against the same receptor, not as affinities. In one system (*S. frugiperda*–BPTI) the ligand was found in another periodic image in at least one frame of the trajectory used for MM-GBSA, a further reason not to read absolute values.

**Table 2.** Calibration pairs (real inhibitor / shuffled decoy). Conf.: Boltz-2 confidence. RMSD: ligand RMSD after receptor superposition (nm, last third of 2 ns). Contact: mean number of receptor residues within 4.5 Å of the ligand. ΔG: MM-GBSA and PRODIGY (kcal mol^−1^). Bold marks a pair in which the decoy scored better than the real inhibitor.

| Receptor | Inhibitor | Conf. | RMSD (nm) | Contact | ΔG MM-GBSA | ΔG PRODIGY |
|---|---|---|---|---|---|---|
| bovine | SFTI-1 | 0.986 / 0.944 | 0.084 / 0.206 | 25.1 / 23.5 | -70.2 / -64.8 | -11.8 / -10.8 |
| bovine | BBI | 0.931 / 0.794 | 0.372 / 0.452 | **22.1 / 28.1** | **-66.1 / -68.5** | **-13.5 / -13.8** |
| bovine | BPTI | 0.962 / 0.796 | 0.380 / 0.643 | **24.4 / 25.6** | -68.8 / -52.5 | **-12.2 / -12.9** |
| bovine | EcTI | 0.934 / 0.687 | 0.181 / 0.537 | **31.3 / 31.4** | **-72.7 / -79.0** | **-12.9 / -13.6** |
| bovine | SKTI | 0.954 / 0.680 | 0.275 / 0.364 | **29.6 / 36.3** | **-77.4 / -103.0** | **-13.2 / -14.8** |
| *S. frugiperda* | SFTI-1 | 0.933 / 0.869 | 0.129 / 0.274 | 35.8 / 31.0 | -86.0 / -84.0 | -10.8 / -10.1 |
| *S. frugiperda* | BBI | 0.862 / 0.650 | 0.349 / 1.167 | **37.3 / 68.7** | **-88.6 / -151.2** | **-15.2 / -20.9** |
| *S. frugiperda* | BPTI | 0.877 / 0.755 | 0.317 / 0.342 | **40.7 / 52.2** | **-112.7 / -131.6** | **-14.1 / -16.1** |
| *S. frugiperda* | EcTI | 0.868 / 0.637 | **0.366 / 0.347** | **38.0 / 66.9** | **-78.9 / -223.7** | **-11.6 / -22.2** |
| *S. frugiperda* | SKTI | 0.853 / 0.628 | 0.200 / 0.466 | **50.7 / 54.4** | -129.2 / -128.6 | **-16.4 / -18.1** |

### 3.3 Generation and the hard non-cleavability criterion

Generation produced 880 backbones (110 per species) with the requested length and an N–C closure distance of 0.76–1.40 Å (not relaxed at all-atom level), and ProteinMPNN yielded 22,066 unique sequences (2,692–2,839 per species; Table 3). The motif-score screen kept 1,829 (8.3%) as resistant-like, 4,987 (22.6%) as marginal and 15,250 (69.1%) as susceptible; it mainly removed long sequences (mean length 7.05 residues and 95.6% with 10 residues or fewer in the resistant-like set against 15.74 and 12.7% in the susceptible set), and only 4.3% of the resistant-like sequences contained lysine or arginine (Figure S2). The 1,829 resistant-like sequences were co-folded with Boltz-2 in a first round (mean confidence 0.862, range 0.695–0.953; Figure S8), values that overlap those of the natural inhibitors and decoys of the calibration.

**Table 3.** Campaign summary per target.

| Species | Backbones | Unique sequences | Resistant-like | Marginal | Susceptible |
|---|---|---|---|---|---|
| *S. frugiperda* | 110 | 2,731 | 147 | 621 | 1,963 |
| *S. litura* | 110 | 2,706 | 205 | 607 | 1,894 |
| *O. nubilalis* | 110 | 2,739 | 238 | 667 | 1,834 |
| *D. saccharalis* | 110 | 2,807 | 247 | 638 | 1,922 |
| *C. includens* | 110 | 2,778 | 235 | 640 | 1,903 |
| *H. virescens* | 110 | 2,774 | 189 | 614 | 1,971 |
| *P. xylostella* | 110 | 2,692 | 287 | 539 | 1,866 |
| *A. gemmatalis* | 110 | 2,839 | 281 | 661 | 1,897 |
| Total | 880 | 22,066 | 1,829 | 4,987 | 15,250 |

The hard criterion (Figure S1) left 527 sequences (2.4%) for the linear peptide and 543 (2.5%) for the macrocycle, 41–86 and 41–87 per species (Figure 3). All 527 linear sequences are in the cyclic set; of the 16 cyclic-only sequences, 14 end in a forbidden residue followed across the closure by a proline that is also the first residue, and two end in isoleucine. The hard set and the motif-score set do not nest (396 of the 543 cyclic candidates, 73%, were also resistant-like). The hard set is short and glycine-rich (Figure S3): mean length 7.7 residues, 430 of 527 linear sequences (81.6%) with 8 residues or fewer, and glycine 49.4% of the 4,060 residues, followed by serine (11.7%), proline (9.8%), threonine (9.0%) and aspartate (5.8%). Lysine or arginine accounted for nine residues (0.22%), each followed by proline (six Arg–Pro, three Lys–Pro). Forbidding isoleucine in the interior as well leaves 393 linear sequences.

### 3.4 Co-folding with Boltz-2: reproducibility, paired controls and pose quality

All 527 linear and 543 cyclic candidates were predicted (E1; mean confidence 0.874 and 0.862). Predicting 442 cyclic candidates a second time with identical input gave a rank correlation of only 0.57 between runs (mean absolute difference 0.028; 0.21–0.69 by species), and the linear and cyclic predictions of the same sequence (n = 527) correlated at 0.50 (Figure 4). The agreement between the two modalities is therefore close to the agreement between two runs of the same modality, and a single prediction cannot separate an effect of modality from sampling noise. In E2, the ten best candidates per species and front were re-predicted (15 predictions each): mean confidence fell from 0.922 to 0.900 (linear) and from 0.911 to 0.888 (cyclic), the regression expected for a top-ranked set; the standard deviation among the 15 predictions of one candidate averaged 0.019 and 0.022, of the order of the spread among the ten candidates of a species, so the order within a top ten is not resolved (Figure S4). Every candidate had at least one sample that passed the pose quality control, and the 48 selected candidates all passed it, with the catalytic triad intact (His57–Ser195 distance 2.4–3.4 Å) and no peptide–receptor heavy-atom pair closer than 2.4 Å (Figure S5). The minimum distance to the Asp189 carboxylate in the starting structure was 5 Å or less in 9 of 24 linear and 18 of 24 cyclic structures. Only three of the 48 contain lysine or arginine (linear NGGRPDAP; cyclic PISQIDSGSR and GGKPGEP).

The paired difference Δ against three shuffled controls (E3) was positive in 63 of 78 linear candidates (81%; median 0.013, interquartile range 0.003–0.030) and in 60 of 79 cyclic ones (76%; median 0.014; the other two linear and one cyclic candidate of the 80 per front are poly-glycine and cannot be shuffled); among the 48 final candidates it was positive in 23 of 24 linear and 22 of 24 cyclic. The differences are of the order of the standard deviation among the 15 predictions of a candidate (0.02), each Δ rests on three controls, and the shuffled controls of glycine-rich sequences are similar to the candidate (mean identity 0.35 linear, 0.29 cyclic); a positive Δ therefore means that the candidate did not score below its controls, and not that it binds; that poly-glycine sequences, which have no shuffled control, were among the ten best by first-pass (E1) confidence in both fronts points the same way, since a score that rewards a homopolymer is not reporting specific recognition. The cross matrix (best candidate of each species against its own and the seven other receptors) showed no species-specific preference: the own receptor gave the highest confidence in 4 of 8 (linear) and 3 of 8 (cyclic) species, and the receptor explained more variation than the peptide (the *S. litura* model gave the lowest mean confidence in both fronts). Because Boltz-2 confidence is not affinity (Section 3.2), this is neither a demonstration nor a refutation of selectivity.

### 3.5 Ten-nanosecond simulations at pH 10.0

All 48 simulations (one run each) finished and were analysed with the procedure of Section 2.7 (Figure 5). The median anchor–Asp189 distance rose from 5.72 Å in the initial window to 6.77 Å in the final window for the linear candidates, and from 5.07 to 6.11 Å for the cyclic ones. In the final window the anchor was within 4 Å of Asp189 in 2 of 24 linear and 2 of 24 cyclic simulations, and farther than 10 Å in 6 and 4. Second-half occupancy at 5 Å reached at least 0.70 in 5 of 48: NGGRPDAP (Arg anchor, 1.00) and GQNDS (Gln, 1.00) in the linear front, and GGKPGEP (Lys, 1.00), GGHSE (His, 0.99) and GGGGH (His, 0.82) in the cyclic front. The anchor was the same in both halves in 21 of 24 linear and 24 of 24 cyclic simulations. The peptide kept some receptor contact within 4.5 Å in at least 0.82 (linear) and 0.97 (cyclic) of the frames, so leaving S1 did not mean dissociation; contact with the catalytic serine and histidine was present when the anchor was far from S1 and does not discriminate. The final-window peptide RMSD had a median of 0.56 nm (0.21–2.64) in the linear and 0.30 nm (0.16–1.69) in the cyclic front. In all 24 cyclic simulations the ring stayed closed (C–N at most 1.462 Å); 11 met the strict criterion, and the other 13 fell below the ω limit (minimum 137.2–149.9°) in at least one frame, in 12 of them in fewer than 2.2% of the frames (Figure S6).

*The starting pose decides the outcome.* A second-half occupancy of at least 0.70 occurred in 5 of the 9 simulations whose peptide started within 4.0 Å of the Asp189 carboxylate and in none of the 39 that started farther (Fisher exact test, *P* = 7 × 10^−5; descriptive, because each candidate was run once and the anchor is defined post hoc). The initial and final distances correlated (Spearman ρ = 0.63) and the initial distance was inversely related to occupancy (ρ = −0.63); the anchor identity did not separate the five (Arg, Gln, Lys and two His; three of them carry no basic residue). The 10-ns screen therefore re-reports the pose proposed by Boltz-2: it measures whether a pose already in S1 survives, and a peptide placed 5 Å away is not given time to find the pocket. For this reason occupancy was demoted from a criterion to a description (Section 2.7).

*Reference scale.* The identical analysis of the calibration complexes (*S. frugiperda* receptor; 2 ns; another force field and pH) gave an occupancy of 1.00 in the second half for all five shuffled decoys and for four of six inhibitors; in all eleven systems the anchor was a lysine or an arginine, which reach S1 whenever they are placed there (Brandsdal et al., 2006; Helland et al., 1999). Occupancy therefore measures placement and not the discrimination between a binder and a decoy. Shuffled controls of the candidates (seven) and variants with the anchor replaced by Asp or Leu (eight) were also simulated at the same protocol; they are not used, because their starting distance to Asp189 explained the outcome (controls that started within 2.74 Å all reached 1.00; the variants started 1.0–4.8 Å farther than their parents), so they cannot separate sequence from pose. Under the rule fixed before the runs, a control that does not separate is removed from the analyses and tiers; the analyses are in the repository.

### 3.6 Energy filter and ranking by stage

PRODIGY on the initial poses of the 48 candidates (protonated at pH 8.2) gave ΔG between −12.2 and −7.1 kcal mol^−1^ (median −9.6) and followed the size of the peptide (Spearman ρ with the number of residues −0.60; with the number of contacts −0.62; Figure 6A). The lowest values belong to the longest macrocycles (QSPDFPNPPNNH −12.2 and QAPDFPTGPNQS −12.1, both *S. litura*), and NGGRPDAP has the lowest value of the linear front (−11.1); GQNDS, GGHSE and GGKPGEP score −9.0, −8.8 and −9.7 (per residue: −1.80, −1.76 and −1.39 against −1.39 for NGGRPDAP). Given the calibration (Section 3.2), these values order candidates of similar size and are not affinities.

Ranking by stage among the 33 candidates that passed the gates (23 linear, 10 cyclic) with the six stages (Boltz-2 E2, Δ, final peptide RMSD, PRODIGY on the pose, PRODIGY on trajectory frames and MM-GBSA, the last three from the simulation at pH 8.2) placed NGGRPDAP (mean rank 6.7), GSNIN (7.0), PTTTQT (7.4), SGPIG (7.8) and TDETG (8.2) first in the linear front, and SGSTDIE (3.2), GQNDS (4.1), IYPETG (4.5), GGHSE (4.9) and GGSTDID (5.2) first in the cyclic front (Figure 6B). The ranks of one candidate vary widely among stages (for example NGGRPDAP is tied for 2nd by E2 and 13th by Δ), so the aggregate ranking is a coarse screen and not a measurement.

MM-GBSA and PRODIGY were also computed on the second half of the 48 simulations at pH 10.0 (Figure S10). MM-GBSA ΔG had a median of −24.8 kcal mol^−1^ (−65.0 to −4.1; standard error between blocks of frames, median 0.9), correlated weakly with peptide length (ρ = −0.29, *P* = 0.05) and with the final anchor–Asp189 distance (ρ = 0.37, *P* = 0.01), and was more favourable for the three peptides with a lysine or arginine (median −45.3 against −23.2 for the other 45; Mann–Whitney *P* = 0.014), as expected for a score that includes the electrostatic attraction to the Asp189 carboxylate. The most favourable values were those of PISQIDSGSR (−65.0), QAPDFPTGPNNS (−56.5), QSPDFPNGPGQS (−54.5), GENGGPG (−47.3) and NGGRPDAP (−45.3). PRODIGY on 30 frames of the same half gave a median of −8.2 kcal mol^−1^ (−11.4 to −6.5; ρ with length −0.37, with MM-GBSA 0.61). Given the calibration (Section 3.2), these values order candidates and are not affinities.

MM-GBSA and PRODIGY were computed in the same way on the second half of the 48 simulations at pH 8.2 (`outputs/ranking_energy_final_all.*`). MM-GBSA ΔG had a median of −26.7 kcal mol^−1^ (−53.3 to −2.0; standard error between blocks of frames, median 0.9) and PRODIGY on 30 frames a median of −8.4 kcal mol^−1^ (−11.9 to −6.7). The most favourable MM-GBSA values were those of NGGRPDAP (−53.3), QAPDFPTGPNNS (−51.4), GSNIN (−48.2), PISQIDSGSR (−42.5) and GTPESNES (−42.2). The comparison with pH 10.0 is in Section 3.7.

### 3.7 pH 8.2 versus pH 10.0

All 48 simulations at pH 8.2 (24 linear, 24 macrocyclic) finished and are paired in Figure 7 with the same candidates at pH 10.0 (same initial pose; only the protonation state assigned by PROPKA, which differed in a median of one residue per system, and the number of counter-ions change). The final anchor–Asp189 distance had a median of 6.40 Å at pH 8.2 against 6.62 Å at pH 10.0 (Wilcoxon *P* = 0.16), second-half occupancy 0.01 against 0.00 (*P* = 0.88) and the final peptide RMSD 0.43 against 0.40 nm (*P* = 0.63). The anchor was within 4 Å of Asp189 in the final window in 4 simulations at each pH, and farther than 10 Å in 5 at pH 8.2 and 10 at pH 10.0. An occupancy of at least 0.70 occurred in six simulations at pH 8.2 (NGGRPDAP, GGKPGEP, the macrocycles PISQIDSGSR, GGHGGG and GGSDHT, and GENGGPG) and in five at pH 10.0 (NGGRPDAP, GGKPGEP, linear GQNDS, GGHSE and GGGGH); only NGGRPDAP and GGKPGEP reached it at both, four reached it at pH 8.2 alone and three at pH 10.0 alone, and 39 of the 48 pairs at neither. The occupancy differed by more than 0.5 between pH in nine pairs, in both directions. The outcome at one pH predicted the other moderately for the final distance (Spearman ρ = 0.51, *P* < 0.001) and for occupancy (ρ = 0.44, *P* = 0.002). Linear GQNDS occupied S1 only in the first half at pH 8.2 (0.97, then 0.04), GGHSE left it (final distance 8.61 Å, occupancy 0.00; minimum |ω| 149.5° against 153.7° at pH 10.0) and GGGGH did too (0.07 against 0.82; started at 4.11 Å against 2.93 Å), whereas GGHGGG (0.91 against 0.00), GGSDHT (1.00 against 0.00), GENGGPG (0.85 against 0.41) and PISQIDSGSR were closer to S1 at pH 8.2. PISQIDSGSR, an Arg-anchored macrocycle, kept the Arg in S1 at pH 8.2 (occupancy 1.00, final distance 2.80 Å, started at 3.21 Å) and lost it at pH 10.0 (0.33; 5.21 Å; started at 3.97 Å). NGGRPDAP and GGKPGEP, the two peptides whose anchor is a basic residue followed by proline (Arg and Lys), kept S1 at both pH: occupancy 0.98 and 1.00 and final distance 2.84 and 2.74 Å for NGGRPDAP; occupancy 1.00 at both pH and 2.71 Å for GGKPGEP, whose ring met the strict criterion at pH 8.2 (minimum |ω| 156.7° against 144.5° at pH 10.0). *The starting pose decided here too:* five of the nine simulations at pH 8.2 whose peptide started within 4.0 Å of Asp189 reached an occupancy of at least 0.70, and one of the 39 that started farther (GENGGPG, 4.57 Å; Fisher exact test, *P* = 4 × 10^−4^; Spearman ρ between initial distance and occupancy −0.60), as at pH 10.0. The energy scores agreed between pH: MM-GBSA ρ = 0.50 (*P* < 0.001; median −26.7 at pH 8.2 against −24.8 kcal mol^−1^ at pH 10.0, *P* = 0.80) and PRODIGY on the frames ρ = 0.60 (*P* < 0.001; −8.38 against −8.21 kcal mol^−1^, *P* = 0.18). At pH 8.2 the MM-GBSA ΔG was more favourable for the three peptides with a lysine or arginine anchor (NGGRPDAP, GGKPGEP and PISQIDSGSR; median −42.5 against −25.9 kcal mol^−1^ for the other 45; Mann–Whitney *P* = 0.041), the same direction as at pH 10.0, and was weakly related to the final distance (ρ = 0.29, *P* = 0.044). Each candidate was run once per pH with a different seed. To estimate the run-to-run floor, eight shortlisted candidates (four per front: GSNIN, GQNDS, PTTTQT and NGGRPDAP; GGHSE, IYPETG, SGSTDIE and GGKPGEP) were run a second time at each pH with another seed (16 pairs, 8 at each pH). They are not a random sample. The median absolute difference between the two runs at the same pH was 0.31 Å (pH 10.0) and 1.37 Å (pH 8.2) for the final anchor–Asp189 distance, 0.03 (pH 10.0) and 0.05 (pH 8.2) for the second-half occupancy and 0.11 nm at both pH for the peptide RMSD, against 1.36 Å, 0.04 and 0.18 nm between pH for the 48 pairs; the run-to-run difference is therefore of the same size as the difference between pH. The medians hide the cases that matter, because most occupancies are near zero: in three of the 16 pairs the occupancy changed by more than 0.5 between runs at the same pH (GQNDS at pH 8.2, 0.04 and 0.73; GGHSE at pH 8.2, 0.00 and 0.88; IYPETG at pH 8.2, 0.57 and 0.00), and two of them crossed the 0.70 limit. The loss of S1 by GGHSE at pH 8.2 and the first-half-only occupancy of GQNDS are thus not reproduced, and no change between pH can be read as an effect of pH. Only NGGRPDAP (0.98 and 1.00 at pH 8.2; 1.00 and 1.00 at pH 10.0) and GGKPGEP (1.00 in both runs at both pH) repeated their occupancy. The changes of occupancy between pH went in both directions, no difference between pH exceeds what repeats at the same pH produce, and the pH comparison reports no difference that passes a paired test.

### 3.8 Candidate peptides

Four peptides stand out by the criteria declared beforehand and by the stages above (Table 4, Figure 8). GGHSE (*S. frugiperda*, cyclic) is the only simulation at pH 10.0 that combined an occupancy of at least 0.70 with the strict ring criterion; at pH 8.2 it left S1 in one run and kept it in the repeat (occupancy 0.00 and 0.88; Section 3.7). GQNDS (*O. nubilalis*, linear) reached an occupancy of 1.00 with a Gln anchor at pH 10.0, but at pH 8.2 occupied S1 only in the first half of one run and 0.73 of the second half of its repeat. NGGRPDAP (*A. gemmatalis*, linear) holds an Arg in S1 followed by proline, the canonical mechanism, and has the lowest PRODIGY ΔG of the linear front; with GGKPGEP, it is one of the two of the four whose S1 occupancy was found at both pH (one run each), and it had the most favourable MM-GBSA of the 48 simulations at pH 8.2 (−53.3 kcal mol^−1^) and the fifth at pH 10.0 (−45.3). GGKPGEP (*A. gemmatalis*, cyclic) has the closest final anchor–Asp189 distance (2.71 Å) and a Lys followed by proline, but at pH 10.0 falls below the ω limit of the strict ring criterion (minimum 144.5° against 150°; 156.7° at pH 8.2, where it also kept S1). All four started with the anchor within 4.0 Å of Asp189 (Section 3.5), and neither the Boltz-2 starting pose nor the 10-ns simulation separates them from a shuffled sequence; they are candidates that survived the filters available, and none carries a claim of selectivity or activity. The 48 candidates were also classified in tiers A–C with the criteria declared before the simulations (23 A and 1 B linear; 10 A, 13 B and 1 C cyclic; Figure S7); tier A excludes few candidates and does not discriminate among the rest.

Lysine or arginine followed by proline is only a statistical barrier for trypsin: cleavage before proline is observed in large peptide-spectrum datasets (Rodriguez et al., 2008) and is slower, not absent, next to proline or charged residues (Pan et al., 2014). Inhibitors that bind as substrates are also cleaved at the reactive site to an extent set by the equilibrium between the intact and the cleaved form (Song and Markley, 2003), and trypsin can both cleave and re-form the Lys–Ser reactive-site bond of SFTI-1 analogues (Karna et al., 2015). The simulations therefore cannot show that a peptide resists proteolysis, but they can show whether the catalytic serine is placed to attack the K/R–Pro bond. In the 20 runs of the five peptides analysed (GGKPGEP, NGGRPDAP, PISQIDSGSR, GGHSE and GQNDS, with their repeats at both pH), a near-attack conformation of any bond was found in a single run (1.6% of the frames of the second half, for the Gly3–Arg4 bond of NGGRPDAP). The median Ser195 Oγ–carbon distance of the K/R–Pro bond was 5.3–5.4 Å (minimum 3.8–4.2 Å) for GGKPGEP at pH 10.0 and 6.7–7.6 Å at pH 8.2, 4.7–5.0 Å (minimum 4.2–4.4 Å) for NGGRPDAP at pH 10.0 and 4.7–5.5 Å at pH 8.2, and 9.2–9.5 Å for the Arg10–Pro1 bond of PISQIDSGSR. In most runs the carbonyl closest to the serine was the one preceding the anchor (Gly2–Lys3 in GGKPGEP, Gly3–Arg4 in NGGRPDAP, within 4 Å in 19–88% of the frames of NGGRPDAP and in at most 23% of those of GGKPGEP), a glycine–basic bond that is not a trypsin site, which suggests that the register of the peptide is shifted by one residue relative to a canonical substrate. Peptides this short and rich in glycine are probably mobile, and in QM/MM simulations of SFTI-1 and its analogues the hydrolysis rate rose with the mobility of the inhibitor, whereas the cyclic backbone and intramolecular hydrogen bonds lowered it (Wei et al., 2019). This is a property of 10-ns classical simulations that start from a predicted pose; it does not measure catalysis and it has no baseline from a known substrate, so it does not establish resistance, and a stability assay with trypsin and a larval midgut extract is the test that would.

**Table 4.** Shortlisted candidates. Initial and final: anchor–Asp189 distance in the initial and final windows of the 10-ns simulation at pH 10.0. Occ.: second-half occupancy at 5 Å (descriptive). ΔG PRODIGY: initial pose; in parentheses, per residue. MM-GBSA: second half of the 10-ns simulation at pH 10.0 and at pH 8.2 (one run each). The occupancy and ring columns refer to pH 10.0.

| Peptide | Front | Species | Length | E2 conf. | Δ (E3) | Anchor | Initial (Å) | Final (Å) | Occ. | Ring | ΔG PRODIGY (kcal mol^−1^) | MM-GBSA pH 10.0 / 8.2 (kcal mol^−1^) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NGGRPDAP | linear | *A. gemmatalis* | 8 | 0.937 | 0.030 | Arg | 2.78 | 2.74 | 1.00 | – | −11.1 (−1.39) | −45.3 / −53.3 |
| GQNDS | linear | *O. nubilalis* | 5 | 0.909 | 0.013 | Gln | 4.00 | 3.77 | 1.00 | – | −9.0 (−1.80) | −18.2 / −2.0 |
| GGHSE | cyclic | *S. frugiperda* | 5 | 0.908 | 0.015 | His | 2.86 | 3.07 | 0.99 | strict | −8.8 (−1.76) | −26.5 / −23.9 |
| GGKPGEP | cyclic | *A. gemmatalis* | 7 | 0.923 | 0.020 | Lys | 2.71 | 2.71 | 1.00 | not strict | −9.7 (−1.39) | −35.4 / −27.7 |

---

## 4 Discussion

### 4.1 Principal findings

We assembled and calibrated a pipeline from eight lepidopteran digestive trypsins to ranked candidate peptides, with non-cleavability by midgut proteases as an explicit binary requirement. The structural part was robust: subsites from two crystal complexes transferred to all ten receptors, and the Asp189 equivalent found by structure matched the one found from sequence. The scoring ladder was weaker: Boltz-2 separated real inhibitors from decoys within pairs, but MM-GBSA and PRODIGY did not and tracked interface size. Requiring non-cleavability left 527 linear and 543 cyclic sequences, short and almost half glycine. Ten-nanosecond simulations showed that S1 occupancy follows the Boltz-2 starting pose, so the simulations verify the stability of a pose and are not evidence of binding; the same 48 simulations at pH 8.2 gave no difference from pH 10.0 that passed a paired test, and only two peptides (NGGRPDAP, GGKPGEP) kept S1 at both pH. No result bears on inhibitory activity or on selectivity.

Natural inhibitors supplied the subsites (2PTC, 1SFI), the calibration standards and the S1-anchoring logic. They did not supply their defining feature: the designed peptides contain no cysteine, so the disulfide-stabilized loops of BPTI, SKTI and SFTI-1 (Luckett et al., 1999; Kelly et al., 2005) are not reproduced, and the head-to-tail ring is the only constraint retained, in one of the two fronts. Rigidity is not simply an advantage against adapted lepidopteran trypsins: a Bowman–Birk inhibitor with seven disulfide bonds inhibited *A. gemmatalis* trypsin-like enzymes less than the soybean Kunitz inhibitor (Patarroyo-Vargas et al., 2020).

### 4.2 What the scoring ladder supports

Boltz-2 preferred the real inhibitor in every pair, but the absolute scores overlapped, and a shuffled 14-residue decoy scored 0.944. The candidates are 5–8 residues long and mostly scored between 0.80 and 0.95, so the calibration supports comparing a candidate with a matched control and not reading 0.9 as evidence of binding. This agrees with an evaluation of Boltz-2 on two small-molecule data sets, which found only weak to moderate correlations of its affinity predictions with physics-based free energies and concluded that it lacks the energetic resolution for lead identification (Wan et al., 2026), and with a benchmark of 111 cyclic peptide–protein complexes, in which model confidence correlated only moderately with pose quality (Spearman 0.53–0.66) and about 12% of poses had high confidence despite poor quality (Li et al., 2026). We used the confidence score and not the Boltz-2 affinity output, so the first result is a caution and not a test of our use. The run-to-run rank correlation of 0.57 for identical input adds a limit: differences of a few hundredths in confidence should not be interpreted, and the agreement between linear and cyclic forms (ρ = 0.50) cannot be read as a modality effect until it is compared with that ceiling. The decoys are shuffled sequences of folded proteins, so they differ from the inhibitors in folding as well as in binding, the calibration ligands have 14–176 residues against 5–8 for the candidates, and the pairs are not independent.

MM-GBSA from a single 2-ns trajectory without entropy favored the real inhibitor in 4 of 10 pairs, and PRODIGY, trained on protein–protein complexes (Vangone and Bonvin, 2015), in 2 of 10; both are close to measures of the number of contacts, consistent with the sensitivity of end-point methods to sampling and system type (Hou et al., 2011; Genheden and Ryde, 2015; Xu et al., 2025). They are therefore used to order peptides of the same receptor and protocol, with a per-residue value, and not to estimate affinity. For comparison, a single-receptor study of an interface-derived peptide against *S. frugiperda* trypsins used triplicate 100-ns simulations and MM/GBSA (Severiche-Castro et al., 2026); our screen is a single 10-ns run per candidate and cannot establish stability.

A methodological point deserves emphasis: separate receptor and ligand molecules can be written to different periodic images of the box. In one of our systems the receptor–peptide center-of-mass distance reached 94.8 Å in a 116-Å box while the molecules were in contact in every frame. Any RMSD or contact analysis of protein–peptide simulations that does not correct for this reports displacement of the image as instability.

### 4.3 Resistance to proteolysis and S1 engagement pull in opposite directions

The screen selects peptides that are short (mean 7.7 residues) and almost free of basic residues. In canonical inhibitors the P1 residue inserts into S1 (Laskowski and Kato, 1980; Laskowski and Qasim, 2000), and trypsin-like enzymes, including those of *A. gemmatalis*, prefer arginine or lysine there (Patarroyo-Vargas et al., 2017; Meriño-Cabrera et al., 2022); the hard criterion therefore selects against the residue best suited to engage Asp189. By forbidding every residue that a trypsin-, chymotrypsin- or elastase-like enzyme can take at P1, it leaves peptides that are almost half glycine and contain only nine basic residues, each protected by a following proline, an exception taken from general enzyme specificity and approximate for each species. Such sequences are probably flexible, which may cost binding entropy, and they lack the side chains that define the S1 interaction of canonical inhibitors. The canonical alternative is rigidity, which improves binding by about six orders of magnitude and protects against proteolysis (Kelly et al., 2005); a macrocycle might tolerate one basic P1 that a linear motif rule flags. The three candidates that carry a Lys or Arg (NGGRPDAP, PISQIDSGSR, GGKPGEP) are the ones in which this can be examined, and the present screen cannot tell whether their conformation keeps that residue protected (Section 3.8 reports the attack geometry in the simulations). Cyclization removes the exposed termini but not the interior sites (the macrocycle gained only 16 sequences over the linear set), and aminopeptidase N, which needs a free N-terminus, is not addressed for linear peptides. The motif rules are coarse (a weighted count of sites; the elastase-like rule flags four common residues), and "resistant-like" is a prediction of low motif burden, not a measurement of stability in the midgut.

*Relation to earlier peptide work.* The candidates are of the same size class as the tripeptides GORE1 and GORE2 and the Pin-II loop tripeptides, whose potency is millimolar (de Almeida Barros et al., 2021; Saikhedkar et al., 2018), as is that of the trypsinogen pro-region peptides (Ki 0.78–1.80 mM against *A. gemmatalis* enzymes (Mariano et al., 2026)), and shorter than the 11-residue interface peptide proposed for *S. frugiperda* (Severiche-Castro et al., 2026). What this work adds is an explicit, rule-based non-cleavability requirement and a calibrated scoring ladder; it adds no evidence of higher affinity. Because Ki values have been measured for GORE2 and for loop- and pro-region-derived peptides (de Almeida Barros et al., 2021; Paulo et al., 2026; Mariano et al., 2026), GORE2 is the natural positive control: a candidate is of interest only if its Ki, measured under the same conditions, falls below the millimolar range of these peptides or if it persists longer in a midgut extract.

### 4.4 Limitations

(i) All results are computational; no inhibition or stability assay was performed. (ii) Selectivity was not addressed: S1 is conserved among trypsins, and a peptide anchored there cannot be assumed to spare non-target proteases. (iii) The receptors are AlphaFold models, and midgut expression is not documented for the pest species. (iv) ProteinMPNN redesigned the receptor along with the peptide, only eight of the 15 hotspot residues reached RFdiffusion, and the sequences were designed on cyclic backbones, so the linear front evaluates the same sequences without redesign. (v) The non-cleavability criterion is a motif-level prediction; the K/R–Pro exception is an approximation and aminopeptidase N is not excluded for linear peptides. (vi) Each simulation is a single 10-ns run with one force field, and single trajectories can yield false-positive conclusions (Knapp et al., 2018); the linear peptide carries NH~3~^+^/COO^−^ termini at both pH; ten nanoseconds only screen, and repeating eight candidates at the same pH changed the second-half occupancy by more than 0.5 in three of 16 pairs, so one run does not settle whether a peptide holds S1. The NPT equilibration used the Parrinello–Rahman barostat, where a relaxation barostat is standard, and `refcoord_scaling` was not set with position restraints under pressure coupling; both deviations were kept so that all simulations share one protocol (pH 10.0 and 8.2 used the same code), and in three systems the density stayed at 1022–1033 kg m^−3^ with a root-mean-square fluctuation of 0.2% and negligible drift. (vii) The S1 occupancy criterion has no demonstrated specificity: every decoy of the calibration satisfied it, and the shuffled-sequence and anchor-swap controls did not separate sequence from starting pose (Section 3.5); the anchor is defined post hoc as the residue with the smallest mean distance. (viii) A single Boltz-2 prediction is a noisy ranker (ρ = 0.57 for identical input), and the shuffled controls of E3 are weak for glycine-rich sequences. (ix) The calibration systems were simulated for 2 ns from one predicted structure each, with ligands much larger than the candidates. (x) MM-GBSA and PRODIGY did not separate inhibitors from decoys, so the energy ranking is a coarse screen.

### 4.5 Outlook

The most direct improvements are to fix the receptor sequence during design and allow exactly one basic P1 followed by proline at design time; to design linear backbones directly and to cap the termini of linear peptides; to run replicate simulations of the shortlisted peptides, extended to hundreds of nanoseconds; and to add a counter-selection against non-target proteases so that selectivity becomes an objective. The decisive test is enzymatic: inhibition assays with midgut extracts of *A. gemmatalis* and non-target trypsins, and a stability assay of the candidates in the same extracts.

---

## 5 Conclusion

Natural inhibitors served as templates and calibration standards for a pipeline that takes eight lepidopteran digestive trypsins to a ranked set of short, non-cleavable peptides. Boltz-2 supports pairwise comparisons; MM-GBSA and PRODIGY order candidates by interface size; and 10-ns S1 occupancy follows the starting pose, so it does not by itself indicate binding; the occupancy of nine candidates differed by more than 0.5 between pH 8.2 and pH 10.0, in either direction without a net shift, and repeats at the same pH differed by more than 0.5 in three of 16 pairs. The four shortlisted peptides (NGGRPDAP, GQNDS, GGHSE, GGKPGEP) survived the filters available and carry no claim of selectivity or activity. The decisive tests are enzymatic.

## Data availability statement

Code, configuration files, candidate lists and per-candidate scores are available in the project repository (https://github.com/eulaliobqi/design-inibidores). [[PENDING: confirm repository visibility and archival DOI (for example Zenodo) before submission.]]

## Ethics statement

Not applicable. This is a computational study; it involved no animals, human participants or personal data.

## Author contributions

[[PENDING: to be completed by the authors (CRediT roles).]]

## Funding

[[PENDING: to be completed by the authors.]]

## Acknowledgments

[[PENDING: to be completed by the authors.]]

## Conflict of interest

[[PENDING: to be completed by the authors. Frontiers wording used in two of the three example articles: "The author(s) declared that this work was conducted in the absence of any commercial or financial relationships that could be construed as a potential conflict of interest."]]

## Generative AI statement

[[PENDING, authors to confirm the wording, in the form used by Frontiers in Natural Products: "The author(s) declared that generative AI was used in the creation of this manuscript. During the preparation of this manuscript, the authors used Claude (Anthropic) to write analysis scripts, generate figures, and draft and translate text. The authors verified all numerical results against the output files, verified every reference against Crossref or PubMed, and take full responsibility for the content."]]

## Supplementary material

Figures S1–S10 and Table S1 (legends and table below) are supplied as Supplementary Material.

---

## Figure legends

**Figure 1.** Study design. Eight receptors with transferred subsites and a calibrated scoring ladder precede the generation of 880 backbones and 22,066 sequences; the hard non-cleavability criterion splits them into front L (linear, 527) and front M (macrocycle, 543); Boltz-2 co-folding, re-scoring, paired controls and pose quality control (E1–E4) yield 48 candidates (three per species and front), which are simulated for 10 ns at pH 10.0 and at pH 8.2, with 16 repeated runs, and then analysed and ranked by stage. No enzymatic assay and no counter-selection against non-target proteases was performed.

**Figure 2.** Calibration of the scoring ladder with six natural inhibitors and shuffled decoys (22 systems; Bt: bovine trypsin, Sf: *S. frugiperda*). (A–D) Real inhibitor (filled) and shuffled decoy (open) for (A) Boltz-2 confidence, (B) ligand backbone RMSD after receptor superposition (2 ns, last third), (C) MM-GBSA ΔG and (D) PRODIGY ΔG; a connector is red when the decoy scored better, and the number of pairs (out of 10) in which the inhibitor scored better is given in each panel. (E) MM-GBSA ΔG against the number of receptor residues within 4.5 Å of the ligand (circles: bovine trypsin; squares: *S. frugiperda*; filled: inhibitor; open: decoy). (F) PRODIGY ΔG against its number of intermolecular contacts. ρ: Spearman correlation (post hoc).

**Figure 3.** Candidates surviving each screen. Left: sequences per species labelled resistant-like by the first-round motif score (circular rule) and by the hard criterion for the linear (front L) and cyclic (front M) interpretation; right: totals out of 22,066 sequences.

**Figure 4.** Reproducibility of Boltz-2 confidence in the two-front screen. (A) The same 442 cyclic candidates predicted in the first round and again in the two-front screen with identical input. (B) The same 527 sequences predicted as cyclic and as linear peptides. The dotted line is identity; ρ is the Spearman correlation and |Δ| the mean absolute difference.

**Figure 5.** Ten-nanosecond screening simulations at pH 10.0 (CHARMM36, 300 K, one run each; all 48 finished). (A) Distance from the anchor residue to the Asp189 carboxylate and (B) local peptide RMSD (Cα, receptor-aligned) for the three *A. gemmatalis* candidates of each front (solid, dashed and dotted: candidates 1, 2 and 3). (C) S1 occupancy at 5 Å in the first and second halves for all 48 simulations (circle: passes the screen as originally declared; cross: does not; the dashed line is the 70% level, now descriptive). (D) Per simulation, linear (top) and macrocyclic (bottom): second-half occupancy, contact with the catalytic serine and any receptor contact; ✗ marks macrocycles that failed the strict ring criterion and ✓ those that met it.

**Figure 6.** Energy filter and ranking by stage. (A) PRODIGY ΔG of the initial pose of the 48 candidates against peptide length (ρ: Spearman). (B) Rank of each candidate within its front at each stage and the aggregate (mean rank) for the ten best candidates of each front among those that passed the gates; stages shown: Boltz-2 E2 confidence, paired Δ (E3), final peptide RMSD, PRODIGY on the pose, PRODIGY on trajectory frames and MM-GBSA (the last three stages from the 10-ns simulation at pH 8.2). The number printed in a cell is the raw rank (1 = best); the colour is that rank relative to the number of candidates ranked in the same front (23 linear, 10 macrocyclic), because a given rank does not mean the same in pools of different size.

**Figure 7.** Comparison of the 48 simulations at pH 8.2 and pH 10.0 (one run per pH with different seeds). (A, B) Paired final anchor–Asp189 distance and second-half S1 occupancy at 5 Å (dotted lines: 4 Å and 0.70; Wilcoxon signed-rank test). (C–E) pH 8.2 against pH 10.0 for the final distance, MM-GBSA ΔG and PRODIGY ΔG on trajectory frames (dotted line: identity; ρ: Spearman correlation). Blue: linear; teal: macrocycle; highlighted: NGGRPDAP, GGKPGEP, GQNDS and GGHSE.

**Figure 8.** Starting poses (Boltz-2) of the four shortlisted peptides in the active site. Peptide in cyan with the anchor residue (the one closest to the Asp189 carboxylate) in magenta; Asp189 in orange; His57 and Ser195 in green; the dotted line is the anchor–Asp189 distance; receptor shown as cartoon within 12 Å of the peptide. (A) NGGRPDAP (linear, *A. gemmatalis*). (B) GQNDS (linear, *O. nubilalis*). (C) GGHSE (cyclic, *S. frugiperda*). (D) GGKPGEP (cyclic, *A. gemmatalis*).

**Figure S1.** Residues forbidden at P1 by class of midgut protease in the hard criterion. A residue is tolerated when the next residue is proline; isoleucine is forbidden only at the free C-terminus of the linear peptide.

**Figure S2.** Properties of the 22,066 designed sequences by class of the motif-score screen. (A) Length distribution. (B) Percentage of sequences with lysine or arginine, and with lysine or arginine at the geometric P1 proxy. (C) Amino-acid composition of the resistant-like and susceptible classes.

**Figure S3.** Composition of the resistant-like set under the hard criterion: amino-acid composition (all sequences and the 527 linear sequences) and length distribution.

**Figure S4.** Re-scoring of the ten best candidates per species and front (E2). (A) Mean E2 confidence against the E1 confidence. (B) E2 confidence per candidate by species. (C) Fraction of the 15 samples that pass the pose quality control.

**Figure S5.** The 48 final candidates. (A) E2 confidence. (B) Minimum distance between the peptide and the Asp189 carboxylate in the starting structure (dashed: 5 Å).

**Figure S6.** Ring integrity in the cyclic simulations of *A. gemmatalis* (10 ns, pH 10.0): closing C–N distance, absolute closing ω angle over time and distribution of ω. Dashed lines: the limits declared beforehand (C–N ≤ 1.5 Å, ω ≥ 150°).

**Figure S7.** Evidence matrix and tiers (A, B, C) of the 48 final candidates, ordered within a tier by paired difference, Boltz-2 confidence and S1 occupancy (the occupancy does not define the tier).

**Figure S8.** Boltz-2 co-folding of the 1,829 macrocycles of the first round: ipTM and complex pLDDT per species and mean ipTM by length.

**Figure S9.** Motif-score screen by species under the linear-strict and the circular rule.

**Figure S10.** MM-GBSA and PRODIGY on the trajectories of the 48 simulations at pH 10.0 (second half; ΔG without entropy). (A) MM-GBSA ΔG against peptide length. (B) MM-GBSA ΔG against the final anchor–Asp189 distance. (C) PRODIGY ΔG on 30 frames against MM-GBSA ΔG. ρ: Spearman correlation.

**Table S1.** Reference subsites (residues of bovine trypsin within 4.5 Å of the inhibitor residue at each position).

| Subsite | BPTI residue | Trypsin contacts (2PTC) | SFTI-1 residue | Trypsin contacts (1SFI) |
|---|---|---|---|---|
| S4 | Gly12 | Gln192 | Arg2 | Asn97, Gln175, Gly216, Ser217, Trp215 |
| S3 | Pro13 | Gln192, Gly216, Trp215 | Cys3 | Gln192, Gly216, Trp215 |
| S2 | Cys14 | Gln192, His57, Leu99, Ser195, Ser214, Trp215 | Thr4 | Gln192, His57, Leu99, Ser195, Ser214, Trp215 |
| S1 | Lys15 | Asp189, Asp194, Cys191, Gln192, Gly193, Gly216, Gly219, Gly226, His57, Ser190, Ser195, Ser214, Trp215, Val213 | Lys5 | same 14 residues |
| S1′ | Ala16 | Cys42, Gln192, Gly193, His57, Phe41, Ser195 | Ser6 | same 6 residues |
| S2′ | Arg17 | Gln192, Gly193, His40, Phe41, Tyr151, Tyr39 | Ile7 | same 6 residues |
| S3′ | Ile18 | His57, Phe41, Tyr39 | Pro8 | none |

---

## References

Abraham MJ, Murtola T, Schulz R, Páll S, Smith JC, Hess B, et al. (2015). GROMACS: High performance molecular simulations through multi-level parallelism from laptops to supercomputers. SoftwareX 1-2, 19-25. doi: 10.1016/j.softx.2015.06.001

Berman HM, Westbrook J, Feng Z, Gilliland G, Bhat TN, Weissig H, et al. (2000). The Protein Data Bank. Nucleic Acids Research 28, 235-242. doi: 10.1093/nar/28.1.235

Brandsdal BO, Smalås AO, Åqvist J (2006). Free energy calculations show that acidic P1 variants undergo large pKa shifts upon binding to trypsin. Proteins: Structure, Function, and Bioinformatics 64, 740-748. doi: 10.1002/prot.20940

Bussi G, Donadio D, Parrinello M (2007). Canonical sampling through velocity rescaling. The Journal of Chemical Physics 126, 014101. doi: 10.1063/1.2408420

Carpane PD, Llebaria M, Nascimento AF, Vivan L (2022). Feeding injury of major lepidopteran soybean pests in South America. PLOS ONE 17, e0271084. doi: 10.1371/journal.pone.0271084

Cock PJA, Antao T, Chang JT, Chapman BA, Cox CJ, Dalke A, et al. (2009). Biopython: freely available Python tools for computational molecular biology and bioinformatics. Bioinformatics 25, 1422-1423. doi: 10.1093/bioinformatics/btp163

da Silva Júnior NR, Vital CE, de Almeida Barros R, Faustino VA, Monteiro LP, Barros E, et al. (2020). Intestinal proteolytic profile changes during larval development of Anticarsia gemmatalis caterpillars. Archives of Insect Biochemistry and Physiology 103, e21631. doi: 10.1002/arch.21631

Dauparas J, Anishchenko I, Bennett N, Bai H, Ragotte RJ, Milles LF, et al. (2022). Robust deep learning–based protein sequence design using ProteinMPNN. Science 378, 49-56. doi: 10.1126/science.add2187

de Almeida Barros R, Meriño-Cabrera Y, Vital CE, da Silva Júnior NR, de Oliveira CN, Lessa Barbosa S, et al. (2021). Small peptides inhibit gut trypsin-like proteases and impair Anticarsia gemmatalis (Lepidoptera: Noctuidae) survival and development. Pest Management Science 77, 1714-1723. doi: 10.1002/ps.6191

de Almeida Barros R, Meriño-Cabrera Y, Castro JS, da Silva Junior NR, de Oliveira JVA, Schultz H, et al. (2022a). Bovine pancreatic trypsin inhibitor and soybean Kunitz trypsin inhibitor: Differential effects on proteases and larval development of the soybean pest Anticarsia gemmatalis (Lepidoptera: Noctuidae). Pesticide Biochemistry and Physiology 187, 105188. doi: 10.1016/j.pestbp.2022.105188

de Almeida Barros R, Meriño-Cabrera Y, Severiche Castro JG, Rodrigues da Silva Júnior N, Schultz H, de Andrade RJ, et al. (2022b). Inhibition constant and stability of tripeptide inhibitors of gut trypsin-like enzyme of the soybean pest Anticarsia gemmatalis. Archives of Insect Biochemistry and Physiology 110, e21887. doi: 10.1002/arch.21887

Dolinsky TJ, Czodrowski P, Li H, Nielsen JE, Jensen JH, Klebe G, et al. (2007). PDB2PQR: expanding and upgrading automated preparation of biomolecular structures for molecular simulations. Nucleic Acids Research 35, W522-W525. doi: 10.1093/nar/gkm276

Dow JAT (1992). pH gradients in lepidopteran midgut. Journal of Experimental Biology 172, 355-375. doi: 10.1242/jeb.172.1.355

Essmann U, Perera L, Berkowitz ML, Darden T, Lee H, Pedersen LG (1995). A smooth particle mesh Ewald method. The Journal of Chemical Physics 103, 8577-8593. doi: 10.1063/1.470117

Gasteiger E, Hoogland C, Gattiker A, Duvaud S, Wilkins MR, Appel RD, et al. (2005). Protein Identification and Analysis Tools on the ExPASy Server. The Proteomics Protocols Handbook , 571-607. doi: 10.1385/1-59259-890-0:571

Genheden S, Ryde U (2015). The MM/PBSA and MM/GBSA methods to estimate ligand-binding affinities. Expert Opinion on Drug Discovery 10, 449-461. doi: 10.1517/17460441.2015.1032936

Gowers R, Linke M, Barnoud J, Reddy T, Melo M, Seyler S, et al. (2016). MDAnalysis: A Python Package for the Rapid Analysis of Molecular Dynamics Simulations. Proceedings of the Python in Science Conference , 98-105. doi: 10.25080/majora-629e541a-00e

Hedstrom L (2002). Serine Protease Mechanism and Specificity. Chemical Reviews 102, 4501-4524. doi: 10.1021/cr000033x

Helland R, Otlewski J, Sundheim O, Dadlez M, Smalås AO (1999). The crystal structures of the complexes between bovine β-trypsin and ten P1 variants of BPTI. Journal of Molecular Biology 287, 923-942. doi: 10.1006/jmbi.1999.2654

Hou T, Wang J, Li Y, Wang W (2011). Assessing the Performance of the MM/PBSA and MM/GBSA Methods. 1. The Accuracy of Binding Free Energy Calculations Based on Molecular Dynamics Simulations. Journal of Chemical Information and Modeling 51, 69-82. doi: 10.1021/ci100275a

Huang J, MacKerell AD (2013). CHARMM36 all-atom additive protein force field: Validation based on comparison to NMR data. Journal of Computational Chemistry 34, 2135-2145. doi: 10.1002/jcc.23354

Jongsma MA, Bakker PL, Peters J, Bosch D, Stiekema WJ (1995). Adaptation of Spodoptera exigua larvae to plant proteinase inhibitors by induction of gut proteinase activity insensitive to inhibition. Proceedings of the National Academy of Sciences 92, 8041-8045. doi: 10.1073/pnas.92.17.8041

Jongsma MA, Bolter C (1997). The adaptation of insects to plant protease inhibitors. Journal of Insect Physiology 43, 885-895. doi: 10.1016/s0022-1910(97)00040-1

Jorgensen WL, Chandrasekhar J, Madura JD, Impey RW, Klein ML (1983). Comparison of simple potential functions for simulating liquid water. The Journal of Chemical Physics 79, 926-935. doi: 10.1063/1.445869

Jumper J, Evans R, Pritzel A, Green T, Figurnov M, Ronneberger O, et al. (2021). Highly accurate protein structure prediction with AlphaFold. Nature 596, 583-589. doi: 10.1038/s41586-021-03819-2

Júnior NRDS, Santos EGDD, Paulo DGS, Meriño-Cabrera Y, Pinto IDPA, Summy MJ, et al. (2026). Integrated Transcriptomic and Physiological Analyses Reveal Disruption of Digestive Homeostasis Induced by Protease Inhibitors in Anticarsia gemmatalis Caterpillars. Archives of Insect Biochemistry and Physiology 123, e70223. doi: 10.1002/arch.70223

Karna N, Łęgowska A, Malicki S, Dębowski D, Golik P, Gitlin A, et al. (2015). Investigation of Serine-Proteinase-Catalyzed Peptide Splicing in Analogues of Sunflower Trypsin Inhibitor 1 (SFTI-1). ChemBioChem 16, 2036-2045. doi: 10.1002/cbic.201500296

Karumbaiah L, Oppert B, Jurat-Fuentes JL, Adang MJ (2007). Analysis of midgut proteinases from Bacillus thuringiensis-susceptible and -resistant Heliothis virescens (Lepidoptera: Noctuidae). Comparative Biochemistry and Physiology Part B: Biochemistry and Molecular Biology 146, 139-146. doi: 10.1016/j.cbpb.2006.10.104

Kelly C, Laskowski Jr. M, Qasim M (2005). The Role of Scaffolding in Standard Mechanism Serine Proteinase Inhibitors. Protein & Peptide Letters 12, 465-471. doi: 10.2174/0929866054395383

Knapp B, Ospina L, Deane CM (2018). Avoiding false positive conclusions in molecular simulation: the importance of replicas. Journal of Chemical Theory and Computation 14, 6127-6138. doi: 10.1021/acs.jctc.8b00391

Kuwar SS, Pauchet Y, Vogel H, Heckel DG (2015). Adaptive regulation of digestive serine proteases in the larval midgut of Helicoverpa armigera in response to a plant protease inhibitor. Insect Biochemistry and Molecular Biology 59, 18-29. doi: 10.1016/j.ibmb.2015.01.016

Laskowski M, Kato I (1980). Protein Inhibitors of Proteinases. Annual Review of Biochemistry 49, 593-626. doi: 10.1146/annurev.bi.49.070180.003113

Laskowski M, Qasim M (2000). What can the structures of enzyme-inhibitor complexes tell us about the structures of enzyme substrate complexes?. Biochimica et Biophysica Acta (BBA) - Protein Structure and Molecular Enzymology 1477, 324-337. doi: 10.1016/s0167-4838(99)00284-8

Li Z, Yuan Y, Hu K, Pan P, He F (2026). Benchmarking confidence estimation and rescoring for cyclic peptide–protein complex predictions. bioRxiv. doi: 10.64898/2026.08.20.746104

Lomate PR, Dewangan V, Mahajan NS, Kumar Y, Kulkarni A, Wang L, et al. (2018). Integrated Transcriptomic and Proteomic Analyses Suggest the Participation of Endogenous Protease Inhibitors in the Regulation of Protease Gene Expression in Helicoverpa armigera. Molecular & Cellular Proteomics 17, 1324-1336. doi: 10.1074/mcp.ra117.000533

Luckett S, Garcia R, Barker J, Konarev A, Shewry P, Clarke A, et al. (1999). High-resolution structure of a potent, cyclic proteinase inhibitor from sunflower seeds. Journal of Molecular Biology 290, 525-533. doi: 10.1006/jmbi.1999.2891

Mariano GA, de Oliveira JVA, Andrade RJD, Paulo DGS, Cabrera YBM, Santos EGDD, et al. (2026). Trypsinogen Pro-Region as a Molecular Scaffold for the Design of Competitive Peptide Inhibitors of Trypsin-Like Proteases. Archives of Insect Biochemistry and Physiology 123, e70224. doi: 10.1002/arch.70224

Meriño-Cabrera Y, de Oliveira Mendes TA, Castro JGS, Barbosa SL, Macedo MLR, de Almeida Oliveira MG (2020a). Noncompetitive tight-binding inhibition of Anticarsia gemmatalis trypsins by Adenanthera pavonina protease inhibitor affects larvae survival. Archives of Insect Biochemistry and Physiology 104, e21687. doi: 10.1002/arch.21687

Meriño-Cabrera Y, Severiche Castro JG, Rios Diez JD, Rodrigues Macedo ML, de Oliveira Mendes TA, Goreti de Almeida Oliveira M (2020b). Rational design of mimetic peptides based on the interaction between Inga laurina inhibitor and trypsins for Spodoptera cosmioides pest control. Insect Biochemistry and Molecular Biology 122, 103390. doi: 10.1016/j.ibmb.2020.103390

Meriño-Cabrera Y, Castro JS, de Almeida Barros R, da Silva Junior NR, de Oliveira Ramos H, de Almeida Oliveira MG (2022). Arginine-containing dipeptides decrease affinity of gut trypsins and compromise soybean pest development. Pesticide Biochemistry and Physiology 184, 105107. doi: 10.1016/j.pestbp.2022.105107

Michaud-Agrawal N, Denning EJ, Woolf TB, Beckstein O (2011). MDAnalysis: A toolkit for the analysis of molecular dynamics simulations. Journal of Computational Chemistry 32, 2319-2327. doi: 10.1002/jcc.21787

Miller BR, McGee TD, Swails JM, Homeyer N, Gohlke H, Roitberg AE (2012). MMPBSA.py: An Efficient Program for End-State Free Energy Calculations. Journal of Chemical Theory and Computation 8, 3314-3321. doi: 10.1021/ct300418h

Mirdita M, Schütze K, Moriwaki Y, Heo L, Ovchinnikov S, Steinegger M (2022). ColabFold: making protein folding accessible to all. Nature Methods 19, 679-682. doi: 10.1038/s41592-022-01488-1

Nakonieczny M, Michalczyk K, Kędziorski A (2007). Midgut protease activities in monophagous larvae of Apollo butterfly, Parnassius apollo ssp. frankenbergeri. Comptes Rendus. Biologies 330, 126-134. doi: 10.1016/j.crvi.2006.12.002

Olsson MHM, Søndergaard CR, Rostkowski M, Jensen JH (2011). PROPKA3: Consistent Treatment of Internal and Surface Residues in Empirical p K a Predictions. Journal of Chemical Theory and Computation 7, 525-537. doi: 10.1021/ct100578z

Onufriev A, Bashford D, Case DA (2004). Exploring protein native states and large‐scale conformational changes with a modified generalized born model. Proteins: Structure, Function, and Bioinformatics 55, 383-394. doi: 10.1002/prot.20033

Pan Y, Cheng K, Mao J, Liu F, Liu J, Ye M, et al. (2014). Quantitative proteomics reveals the kinetics of trypsin-catalyzed protein digestion. Analytical and Bioanalytical Chemistry 406, 6247-6256. doi: 10.1007/s00216-014-8071-6

Parkin S, Rupp B, Hope H (1996). Structure of bovine pancreatic trypsin inhibitor at 125 K definition of carboxyl-terminal residues Gly57 and Ala58. Acta Crystallographica Section D Biological Crystallography 52, 18-29. doi: 10.1107/S0907444995008675

Parrinello M, Rahman A (1981). Polymorphic transitions in single crystals: A new molecular dynamics method. Journal of Applied Physics 52, 7182-7190. doi: 10.1063/1.328693

Passaro S, Corso G, Wohlwend J, Reveiz M, Thaler S, Ram Somnath V, et al. (2025). Boltz-2: Towards accurate and efficient binding affinity prediction. bioRxiv [Preprint]. doi: 10.1101/2025.06.14.659707

Patarroyo-Vargas AM, Merino-Cabrera YB, Zanuncio JC, Rocha F, Campos WG, de Almeida Oliveira MG (2017). Kinetic Characterization of Anticarsia gemmatalis Digestive Serine- Proteases and the Inhibitory Effect of Synthetic Peptides. Protein & Peptide Letters 24, 1040-1047. doi: 10.2174/0929866524666170918103146

Patarroyo-Vargas AM, Cordeiro G, Silva CRD, Silva CRD, Mendonça EG, Visôtto LE, et al. (2020). Inhibition kinetics of digestive proteases for Anticarsia gemmatalis. Anais da Academia Brasileira de Ciências 92, e20180477. doi: 10.1590/0001-3765202020180477

Paulo DGS, Schneider JR, Meriño-Cabrera Y, Wurlitzer WB, de Andrade RJ, Santos ILB, et al. (2026). Peptides Derived From Reactive Center Loops Inhibit Digestive Trypsin-Like Enzymes in Lepidopteran Pests. Archives of Insect Biochemistry and Physiology 121, e70123. doi: 10.1002/arch.70123

Perona JJ, Craik CS (1995). Structural basis of substrate specificity in the serine proteases. Protein Science 4, 337-360. doi: 10.1002/pro.5560040301

Rettie SA, Juergens D, Adebomi V, Bueso YF, Zhao Q, Leveille AN, et al. (2025). Accurate de novo design of high-affinity protein-binding macrocycles using deep learning. Nature Chemical Biology 21, 1948-1956. doi: 10.1038/s41589-025-01929-w

Rodriguez J, Gupta N, Smith RD, Pevzner PA (2008). Does Trypsin Cut Before Proline? Journal of Proteome Research 7, 300-305. doi: 10.1021/pr0705035

Saikhedkar NS, Joshi RS, Bhoite AS, Mohandasan R, Yadav AK, Fernandes M, et al. (2018). Tripeptides derived from reactive centre loop of potato type II protease inhibitors preferentially inhibit midgut proteases of Helicoverpa armigera. Insect Biochemistry and Molecular Biology 95, 17-25. doi: 10.1016/j.ibmb.2018.02.001

Saikhedkar NS, Joshi RS, Yadav AK, Seal S, Fernandes M, Giri AP (2019). Phyto-inspired cyclic peptides derived from plant Pin-II type protease inhibitor reactive center loops for crop protection from insect pests. Biochimica et Biophysica Acta (BBA) - General Subjects 1863, 1254-1262. doi: 10.1016/j.bbagen.2019.05.003

Schechter I, Berger A (1967). On the size of the active site in proteases. I. Papain. Biochemical and Biophysical Research Communications 27, 157-162. doi: 10.1016/S0006-291X(67)80055-X

Schultz H, Paulo DGS, Meriño-Cabrera Y, de Andrade RJ, Santos ILB, Rodrigues MCNG, et al. (2026). Synthetic Peptide Inhibition of Trypsin-Like Proteases in Spodoptera frugiperda (Lepidoptera: Noctuidae): Evaluating the Influence of Gut Microbiota. Archives of Insect Biochemistry and Physiology 121, e70145. doi: 10.1002/arch.70145

Severiche-Castro J, Valerio MF, Oliveira MGdA (2026). Structure-Guided Design of an Interface-Derived Inhibitor Peptide Against Spodoptera frugiperda Digestive Trypsins. Archives of Insect Biochemistry and Physiology 122, e70164. doi: 10.1002/arch.70164

Silva-Júnior NR, Cabrera YM, Barbosa SL, Barros RDA, Barros E, Vital CE, et al. (2021). Intestinal proteases profiling from Anticarsia gemmatalis and their binding to inhibitors. Archives of Insect Biochemistry and Physiology 107, e21792. doi: 10.1002/arch.21792

Song HK, Suh SW (1998). Kunitz-type soybean trypsin inhibitor revisited: refined structure of its complex with porcine trypsin reveals an insight into the interaction between a homologous inhibitor from Erythrina caffra and tissue-type plasminogen activator. Journal of Molecular Biology 275, 347-363. doi: 10.1006/jmbi.1997.1469

Song J, Markley JL (2003). Protein Inhibitors of Serine Proteinases: Role of Backbone Structure and Dynamics in Controlling the Hydrolysis Constant. Biochemistry 42, 5186-5194. doi: 10.1021/bi034041u

Souza TP, Dias RO, Castelhano EC, Brandão MM, Moura DS, Silva-Filho MC (2016). Comparative analysis of expression profiling of the trypsin and chymotrypsin genes from Lepidoptera species with different levels of sensitivity to soybean peptidase inhibitors. Comparative Biochemistry and Physiology Part B: Biochemistry and Molecular Biology 196-197, 67-73. doi: 10.1016/j.cbpb.2016.02.007

Terra WR, Ferreira C (1994). Insect digestive enzymes: properties, compartmentalization and function. Comparative Biochemistry and Physiology Part B: Comparative Biochemistry 109, 1-62. doi: 10.1016/0305-0491(94)90141-4

The UniProt Consortium, Bateman A, Martin MJ, Orchard S, Magrane M, Adesina A, et al. (2025). UniProt: the Universal Protein Knowledgebase in 2025. Nucleic Acids Research 53, D609-D617. doi: 10.1093/nar/gkae1010

Valaitis AP (1995). Gypsy moth midgut proteinases: Purification and characterization of luminal trypsin, elastase and the brush border membrane leucine aminopeptidase. Insect Biochemistry and Molecular Biology 25, 139-149. doi: 10.1016/0965-1748(94)00033-e

Valaitis AP, Augustin S, Clancy KM (1999). Purification and characterization of the western spruce budworm larval midgut proteinases and comparison of gut activities of laboratory-reared and field-collected insects. Insect Biochemistry and Molecular Biology 29, 405-415. doi: 10.1016/s0965-1748(99)00017-x

Valdés-Tresanco MS, Valdés-Tresanco ME, Valiente PA, Moreno E (2021). gmx_MMPBSA: A New Tool to Perform End-State Free Energy Calculations with GROMACS. Journal of Chemical Theory and Computation 17, 6281-6291. doi: 10.1021/acs.jctc.1c00645

van Kempen M, Kim SS, Tumescheit C, Mirdita M, Lee J, Gilchrist CLM, et al. (2024). Fast and accurate protein structure search with Foldseek. Nature Biotechnology 42, 243-246. doi: 10.1038/s41587-023-01773-0

Vangone A, Bonvin AMJJ (2015). Contacts-based prediction of binding affinity in protein–protein complexes. eLife 4, e07454. doi: 10.7554/eLife.07454

Varadi M, Bertoni D, Magana P, Paramval U, Pidruchna I, Radhakrishnan M, et al. (2024). AlphaFold Protein Structure Database in 2024: providing structure coverage for over 214 million protein sequences. Nucleic Acids Research 52, D368-D375. doi: 10.1093/nar/gkad1011

Wacha AF, Lemkul JA (2023). charmm2gmx: An Automated Method to Port the CHARMM Additive Force Field to GROMACS. Journal of Chemical Information and Modeling 63, 4246-4252. doi: 10.1021/acs.jcim.3c00860

Wan S, Zhang X, Xue X, Coveney PV (2026). Reliability of AI methods in drug discovery: evaluation of Boltz-2 for structure and binding affinity prediction. Journal of Chemical Theory and Computation 22, 7811-7824. doi: 10.1021/acs.jctc.6c01334

Watson JL, Juergens D, Bennett NR, Trippe BL, Yim J, Eisenach HE, et al. (2023). De novo design of protein structure and function with RFdiffusion. Nature 620, 1089-1100. doi: 10.1038/s41586-023-06415-8

Wei W, Ma J, Xie D, Zhou Y (2019). Linking inhibitor motions to proteolytic stability of sunflower trypsin inhibitor-1. RSC Advances 9, 13776-13786. doi: 10.1039/c9ra02114k

Werner MH, Wemmer DE (1992). Three-dimensional structure of soybean trypsin/chymotrypsin Bowman-Birk inhibitor in solution. Biochemistry 31, 999-1010. doi: 10.1021/bi00119a008

Wohlwend J, Corso G, Passaro S, Getz N, Reveiz M, Leidal K, et al. (2024). Boltz-1: Democratizing biomolecular interaction modeling. bioRxiv [Preprint]. doi: 10.1101/2024.11.19.624167

Xu X, Zhou F, Zheng L, Wang S, Peng X, Li D (2025). Sampling Challenges of MM/PBSA Binding Energy Calculations. The Journal of Physical Chemistry B 129, 11666-11678. doi: 10.1021/acs.jpcb.5c04908

Yang Y, Zhu YC, Ottea J, Husseneder C, Leonard BR, Abel C, et al. (2013). Characterization and transcriptional analyses of cDNAs encoding three trypsin- and chymotrypsin-like proteinases in Cry1Ab-susceptible and Cry1Ab-resistant strains of sugarcane borer, Diatraea saccharalis. Insect Science 20, 485-496. doi: 10.1111/j.1744-7917.2012.01514.x

Zhan Q, Zheng S, Feng Q, Liu L (2011). A midgut-specific chymotrypsin cDNA (Slctlp1) from Spodoptera litura: cloning, characterization, localization and expression analysis. Archives of Insect Biochemistry and Physiology 76, 130-143. doi: 10.1002/arch.20353

Zhang Y, Skolnick J (2005). TM-align: a protein structure alignment algorithm based on the TM-score. Nucleic Acids Research 33, 2302-2309. doi: 10.1093/nar/gki524

Zhou D, Lobo YA, Batista IFC, Marques-Porto R, Gustchina A, Oliva MLV, et al. (2013). Crystal Structures of a Plant Trypsin Inhibitor from Enterolobium contortisiliquum (EcTI) and of Its Complex with Bovine Trypsin. PLoS ONE 8, e62252. doi: 10.1371/journal.pone.0062252

---

## Drafting notes (remove before submission)

1. **Rewritten on 5 October 2026** for objective methods and fewer analyses (the earlier version is in `docs/dados/manuscript_src_before_rewrite_2026-10-05.md`). Cuts: the linear × macrocycle section (three paired sequences, no inference), the first-round Boltz-2 section (now Figure S8), the tier narrative (now one sentence and Figure S7), the species comparison of the simulations, the detailed ring and limitation lists. Section numbers and figures were renumbered (figure files with final names are in `manuscript/figures/final/`).
2. **Pending (marked [[PENDING]]):** (a) the reason for pH 8.2 (the midgut of the larvae is at pH 9–10); (b) the second runs: all 16 analysed on 8 October 2026 and written into 3.7, 4.4(vi) and 5; (c) the list of recommended peptides and further cuts. On 8 October 2026 the 48 simulations at pH 8.2, their MM-GBSA/PRODIGY and the six-stage ranking were integrated (3.6, 3.7, Table 4, Figures 6 and 7, abstract, 2.8, 4.1, 4.4, 5; files in `data-e2-results/`).
3. **Controls retired (decision of the author, 5 October 2026):** seven shuffled-sequence and eight anchor-swap simulations were done and removed from the analyses, tiers and figures under the rule of 2 October; one paragraph in 3.5 and limitation (vii) disclose that they were run and why they are not used (delete only if the authors accept omitting runs that were done). Data in `data-e2-results/`; figures in `manuscript/figures/_retiradas/`.
4. **Thresholds** are pre-registered in `docs/PLANO_LINEAR_2026-09-30.md`; none may change after the data are seen. One exception, declared in 2.7: occupancy was demoted to a description on 2 October 2026 after the first 16 simulations had been analysed.
5. **Format check** against the three *Frontiers in Natural Products* articles in `manuscript/exemplos-papers/`: the examples merge results and discussion and end with a short Conclusion; this manuscript keeps them apart and has a Conclusion (accepted by the journal); the Generative AI statement, Supplementary material and Ethics sections were added; the reference style (Surname, I., ... (year)) is restyled by the journal production. Main text length is reported by `build_docx_pt.py` (limit 12,000 words).
6. **Figures suggested by the literature** (computational peptide-design and MD papers, including the closest precedent, a triplicate 100-ns study of an interface-derived peptide against *S. frugiperda* trypsins (Severiche-Castro et al., 2026)): workflow; calibration pairs; funnel; structural panel of the best poses (Figure 8); RMSD/RMSF/Rg/SASA and intermolecular hydrogen bonds over time with mean ± SD of replicates; per-residue MM-GBSA decomposition; interaction diagram (2D); ranking heatmap by stage (Figure 6B). Time series of peptide–receptor hydrogen bonds, Rg/SASA and per-residue decomposition can be added when the pH 8.2 trajectories are analysed.
7. References added on 5 October 2026 (Crossref-checked): vangone2015, valdes2021, onufriev2004, miller2012, wan2026 and li2026 (bioRxiv preprint). `grzesiak2000` and `brandsdal2006`/`helland1999` were checked on 2 October (PubMed, Crossref); the citing sentences of valaitis1995/1999, yang2012 and zhan2010 stay at the level of the titles until the full texts are read.

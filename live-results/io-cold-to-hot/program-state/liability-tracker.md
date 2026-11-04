# Liability Tracker — IO Cold-to-Hot Campaign (`io-cold-to-hot`)

## L-001: TREX1 Systemic Autoimmunity Disqualification (Aicardi-Goutières Lupus / Myocarditis Phenotype)
- **Severity**: High
- **Status**: mitigated (`DEC-001` -> `DEC-010`)
- **Discovery Work Order**: `WO-002` / `WO-006..008`
- **Mitigation**: Human Mendelian genetics (`PMID:16845398`) establishes that loss-of-function in cytosolic exonuclease `TREX1` (`ENSG00000213689`, `H-0003`, `Elo 1368.0`) causes Aicardi-Goutières syndrome, systemic type-I interferonopathy, and autoimmune myocarditis. `TREX1` was formally disqualified at `DEC-001` in favor of extracellular `ENPP1` (`pLI = 0.00`, `LOEUF = 0.722`, `73` observed LoF variants without systemic autoimmunity), and Series B lead `oase_enpp1_019` demonstrated `TREX1 IC50 > 10 µM` (`>320x` selectivity margin over `ENPP1 IC50 = 31 nM`).

## L-002: AlphaFold 3 Co-Fold Interface Confidence (`ipTM = 0.36`) & Predicted Receptor Geometry
- **Severity**: Medium
- **Status**: mitigated (`DEC-003` -> `EXP-03` SPR / Crystal Confirmation)
- **Discovery Work Order**: `WO-004` / `WO-007`
- **Mitigation**: `AF3-enpp1_009_complex.cif` (`ipTM = 0.36`, `has_clash = 0.0`) and AutoDock Vina (`-9.793 kcal/mol`, `WO-005`) are computational structural models (`afdb.model_is_not_docking_ready`, `docking.score_is_not_affinity`) anchored on the APO crystal `6B2J` (`Pocket #1 = 0.903`, `1143.6 Å³`). Orthogonal wet-lab recombinant human ENPP1 enzymatic cGAMP-hydrolysis `IC50` (`18 nM` for `oase_enpp1_009`; `31 nM` for `oase_enpp1_019`) and surface plasmon resonance (`SPR KD = 14 nM` and `24 nM`) confirmed direct active-site target engagement.

## L-003: Series A Polar Sulfamide P-gp Efflux (`ER = 18.4`) & Low Passive Permeability (`MDCK Papp = 1.1e-6 cm/s`)
- **Severity**: High
- **Status**: mitigated (Transitioned from `ACTIVE_BLOCKER` at `DEC-008` Wet-Lab Wall to `MITIGATED` by `oase_enpp1_019` at `DEC-010`)
- **Discovery Work Order**: `WO-006` / `WO-007..008`
- **Mitigation**: Although Series A lead `oase_enpp1_009` (`Polar Sulfamide ZBG`, `MW = 475.50 Da`, `cLogP = 2.01`, `TPSA = 113.96 Å²`) cleared biochemical potency (`ENPP1 IC50 = 18 nM`, `SPR KD = 14 nM`), experimental CRO wet-lab profiling at `DEC-008` revealed low passive permeability (`MDCK-MDR1 Papp = 1.1e-6 cm/s < 5.0e-6` gate) and severe P-gp efflux (`ER = 18.4 > 2.5` gate; rat oral `F = 5.4%`). At `DEC-009`, medicinal chemistry replaced the polar sulfamide with the neutral pyrazole heteroaryl ZBG in Series B backup `oase_enpp1_019` (`MW = 430.51 Da`, `cLogP = 3.46`, `TPSA = 79.40 Å²`), restoring passive permeability (`MDCK Papp = 12.4e-6 cm/s`), eliminating P-gp efflux (`ER = 1.6`), and achieving `Oral F = 52%` (`Ctrough,free = 198 nM = 6.4x IC50`, `hERG IC50 > 30 µM`, `>48x` margin) at `DEC-010`.

## L-004: On-Target ENPP1 Extracellular Pyrophosphate (`PPi`) Depletion / Ectopic Calcification Risk
- **Severity**: Medium
- **Status**: monitored (Gate 4 GLP DRF Biomarker Mandate)
- **Genetic Basis**: Heterozygous human `ENPP1` LoF is benign (`gnomAD pLI = 0.00`), whereas biallelic LoF causes Generalized Arterial Calcification of Infancy (`GACI`) and `ARHR2` via systemic `ATP -> PPi` depletion.
- **Mitigation & Gate 4 Mandate**: Intermittent short-course oncology dosing (28-day IO cycles alongside anti-PD-1 rather than chronic lifelong suppression), biochemical `IC50(ATP) / IC50(cGAMP)` selectivity profiling, and mandatory plasma `PPi`, `FGF23`, and bone-specific `ALP` + vascular histopathology monitoring in 14-day rat/dog DRF tox.

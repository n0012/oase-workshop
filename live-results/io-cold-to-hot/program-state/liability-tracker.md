# Liability Tracker — IO Cold-to-Hot Campaign (`io-cold-to-hot`)

## L-001: TREX1 Systemic Autoimmunity Disqualification (Aicardi-Goutières Lupus / Myocarditis Phenotype)
- **Severity**: High
- **Status**: mitigated
- **Discovery Work Order**: `WO-002`
- **Mitigation**: Human Mendelian genetics (`PMID:16845398`) establishes that loss-of-function in cytosolic exonuclease `TREX1` (`ENSG00000213689`, `H-0003`, `Elo 1368.0`) causes Aicardi-Goutières syndrome, systemic type-I interferonopathy, and autoimmune myocarditis. `TREX1` was formally disqualified at `DEC-001` in favor of extracellular `ENPP1` (`pLI = 2.7418338646034427e-13`, `LOEUF = 0.7220920420139987`, `73` observed LoF variants without systemic autoimmunity).

## L-002: AlphaFold 3 Co-Fold Interface Confidence (`ipTM = 0.36`) & Predicted Receptor Geometry
- **Severity**: Medium
- **Status**: open
- **Discovery Work Order**: `WO-004`
- **Mitigation**: `AF3-enpp1_009_complex.cif` (`ipTM = 0.36`, `has_clash = 0.0`) and AutoDock Vina (`-9.793 kcal/mol`, `WO-005`) are computational structural models (`afdb.model_is_not_docking_ready`, `docking.score_is_not_affinity`). Orthogonal wet-lab recombinant human ENPP1 enzymatic cGAMP-hydrolysis $\text{IC}_{50}$ (`EXP-01`) and SPR $K_d$ confirmation are gated at the Wet-Lab Wall (`DEC-003`).

## L-003: Aqueous Solubility & Polar Sulfonylurea Permeability Balance (`LogS = -4.083`)
- **Severity**: Low
- **Status**: mitigated
- **Discovery Work Order**: `WO-006`
- **Mitigation**: Sulfonylurea linker optimization (`enpp1_hit_001` $\rightarrow$ `oase_enpp1_009`) lowered `cLogP` from `3.65` to `2.01` and improved predicted aqueous solubility to `LogS = -4.083` while keeping zero hERG pharmacophore features matched (`0` CYP isoforms flagged).

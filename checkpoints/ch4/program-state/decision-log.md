# Decision Log — `pcsk9-oral` (Checkpoint `ch4`)

## DEC-001 (Stage 0 Charter & Seed Adoption — ACCEPTED)
- **Actor:** `science-program-lead`
- **Evidence:** `WO-001` (`raw/hypotheses/pcsk9_seed.analysis.json`)
- **Decision:** Adopt `IC-001` (allosteric C-terminal/catalytic-groove PCSK9 small-molecule inhibitor, Elo `1642.5`) as primary concept and `IC-002` (oral tricyclic macrocycle EGF-A PPI blocker, Elo `1588.0`) as comparator. Advance to Stage 1 human genetic and regulatory validation.

## DEC-002 & DEC-003 (Stage 1 Human Genetics & Tissue Selectivity — ACCEPTED)
- **Actor:** `science-program-lead`
- **Evidence:** `WO-002` (`raw/genomics/PCSK9_gnomad.analysis.json`, `raw/genomics/PCSK9_opentargets.analysis.json`, `raw/gtex/PCSK9.analysis.json`)
- **Decision:** Confirmed human LoF cardioprotection (`score = 0.96`, `pLI = 0.0001`) and hepatocyte-restricted expression (`184.2 TPM`, `Tau = 0.93`).

## DEC-004 (Stage 1 Target Validation Gate — APPROVED TO STAGE 2)
- **Actor:** `science-program-lead` + Project Owner (`STAGE_GATE_DECISION`)
- **Evidence:** `WO-002`, `WO-003`
- **Decision:** Stage 1 Gate PASSED. Advance `pcsk9-oral` (`IC-001` primary, `IC-002` comparator) to Stage 2 structural pocket assessment, AlphaFold 3 co-folding, and Vina docking.

## DEC-005 (Stage 2 Pocket Prioritization — IC-001 PRIORITIZED)
- **Actor:** `science-program-lead`
- **Evidence:** `WO-004` (`raw/pocket/Q8NBP7_pockets.analysis.json`, `raw/structures/pcsk9_ic001_af3_ligand_summary.analysis.json`)
- **Decision:** Prioritize `IC-001` (allosteric pocket druggability `0.68`, AF3 `ipTM = 0.84`) for small-molecule docking and SAR optimization; retain `IC-002` (`0.24`) as macrocycle comparator.

## DEC-006 & DEC-007 (Stage 2 Hit Identification Gate — APPROVED TO STAGE 3)
- **Actor:** `science-program-lead`
- **Evidence:** `WO-005` (`raw/docking/pcsk9_pocket1_vina.analysis.json`)
- **Decision:** Advance `pcsk9_analog_02` (`-9.4 kcal/mol` predicted Vina score, zero clashes) to Stage 3 DMTA medicinal chemistry optimization; log Liability `L-002` (`cLogP = 4.8` and basic-amine hERG risk on parent quinoline ring) for MMP bioisosteric replacement.

## DEC-008 & DEC-009 (Stage 3 Lead Optimization Gate & Wet-Lab Handoff — LIABILITY L-002 MITIGATED)
- **Actors:** Dr. Raj Patel (`medicinal-chemist`), Dr. Claire Moreau (`admet-dmpk-scientist`), Dr. Sarah Chen (`science-program-lead`)
- **Evidence:** `WO-006` (`raw/admet/pcsk9_ic001_series_admet.analysis.json`)
- **Decision:** Disqualify `PCSK9-A02` (`cLogP = 5.09`, hERG alert); advance clean oxadiazole/methoxypyrimidine lead `OASE-PCSK9-014` (`cLogP = 3.1`, `LipE = 5.2`, `0` critical liabilities) into the Wet-Lab / CRO experimental confirmation slot (`SPR`, `HepG2`, patch-clamp `hERG`, rat/dog PK) prior to Stage 4 human oral PK scaling.

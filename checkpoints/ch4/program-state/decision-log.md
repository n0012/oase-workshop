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

## DEC-008 & DEC-009 (Stage 3 Lead Optimization Gate — LIABILITY L-002 MITIGATED)
- **Actor:** `science-program-lead`
- **Evidence:** `WO-006` (`raw/admet/pcsk9_ic001_series_admet.analysis.json`)
- **Decision:** Nominate `OASE-PCSK9-014` (`cLogP = 3.1`, `LipE = 5.2`, `TPSA = 88.4 Å²`, `4` synthetic steps) for Stage 4 PK scaling and preclinical IND dossier assembly.

## DEC-010 (Stage 4 Human PK Projection — ACCEPTED)
- **Actor:** `science-program-lead`
- **Evidence:** `WO-007` (`raw/pk/oase_pcsk9_014_scaled_pk.analysis.json`)
- **Decision:** Confirmed projected `40.0 mg QD` oral dosing feasibility (`F = 52.0%`, `t1/2 = 14.8 h`).

## DEC-011 & DEC-012 (Stage 4 Candidate Nomination Gate — SCIENTIFICALLY ACCEPTED)
- **Actor:** `science-program-lead` + Project Owner
- **Evidence:** `WO-001`..`WO-008`
- **Decision:** Nominate `OASE-PCSK9-014` for preclinical IND-enabling package and authorize `project-curator` to export the 28-page static evidence portal (`pcsk9-oral-site.zip`).

# Decision Log — `pcsk9-oral` (Checkpoint `ch2`)

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

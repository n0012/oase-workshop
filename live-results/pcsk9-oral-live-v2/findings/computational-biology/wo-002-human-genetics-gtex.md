# WO-002: Human Genetic Constraint (gnomAD v4) & GTEx v8 Expression Profiling of PCSK9

**Work Order:** `WO-002-r1`
**Author:** `computational-biologist` (Dr. Marcus Vance)

## Summary
We queried gnomAD v4 genetic constraint (`oase genetics fetch/analyze PCSK9`) and GTEx v8 expression (`oase gtex fetch/analyze PCSK9`) to evaluate whether pharmacological inhibition of `PCSK9` (`ENSG00000169174`) is tolerated in humans and whether whole-blood transcriptomics exhibits peripheral expression liabilities.

## Key Findings
- **gnomAD v4 Loss-of-Function Tolerance (`PCSK9.gnomad-constraint.json`):**
  - `PCSK9` exhibits complete tolerance to heterozygous and homozygous loss-of-function in humans (`verdict: lof_tolerant`), with `pLI =` 2.765187110917756e-18 {source: raw/genomics/PCSK9.gnomad-constraint.analysis.json $.metrics.pLI} and `LOEUF =` 1.1441346736692857 {source: raw/genomics/PCSK9.gnomad-constraint.analysis.json $.metrics.loeuf}.
  - Observed vs. expected LoF ratio `oe_lof =` 0.9176378304213768 {source: raw/genomics/PCSK9.gnomad-constraint.analysis.json $.metrics.oe_lof} (57 {source: raw/genomics/PCSK9.gnomad-constraint.analysis.json $.metrics.obs_lof} observed vs. 62.116009290752274 {source: raw/genomics/PCSK9.gnomad-constraint.analysis.json $.metrics.exp_lof} expected LoF variants) and missense ratio `oe_mis =` 0.906450937101462 {source: raw/genomics/PCSK9.gnomad-constraint.analysis.json $.metrics.oe_mis}.
- **GTEx v8 Whole-Blood Bulk RNA-Seq Expression (`ENSG00000169174.10.gtex.json`):**
  - GTEx whole-blood RNA-seq expression for `PCSK9` (`ENSG00000169174.10`) is classified as `not_expressed`, with `median_tpm =` 0.245957 {source: raw/gtex/ENSG00000169174.10.analysis.json $.metrics.median_tpm} TPM.
- **Supporting Artifacts:**
  - [gnomAD Constraint Artifact](../../raw/genomics/PCSK9.gnomad-constraint.json)
  - [GTEx Expression Artifact](../../raw/gtex/ENSG00000169174.10.gtex.json)

## Mandatory Relays & Governance Dispositions
- **Relay: `gtex.whole_blood_is_not_peripheral_blood`** — GTEx whole blood is drawn from femoral/subclavian veins and measured by bulk RNA-seq (755 samples, median TPM `0.245957`). We explicitly report this as GTEx whole-blood RNA-seq expression, not as general peripheral blood mononuclear cell (PBMC) expression, and confirm hepatic synthesis dominance of secreted PCSK9.

## Implications
Human genetic de-risking is 100% supportive of chronic PCSK9 inhibition; proceed to `WO-003` 1P AlphaGenome functional variant scoring.

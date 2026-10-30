# WO-002: Human Genetic Constraint (`ENPP1` vs `TREX1` gnomAD v4) & GTEx v8 Expression Triage

**Work Order:** `WO-002-r1`
**Author:** `computational-biologist` (Dr. Marcus Vance)

## Summary
We queried gnomAD v4 genetic constraint (`oase genetics fetch/analyze`) for `ENPP1` (`ENSG00000197594`) and `TREX1` (`ENSG00000213689`), alongside GTEx v8 whole-blood RNA-seq expression (`oase gtex fetch/analyze ENPP1`), to evaluate systemic human target safety and formally adjudicate the `TREX1` autoimmunity liability (`L-001`).

## Key Findings
- **ENPP1 Human Loss-of-Function Tolerance (`ENPP1.gnomad-constraint.json`):**
  - `ENPP1` (`ENSG00000197594`) is tolerant to heterozygous loss-of-function in general human populations (`verdict: lof_tolerant`), with `pLI =` 2.7418338646034427e-13 {source: raw/genomics/ENPP1.gnomad-constraint.analysis.json $.metrics.pLI}, `LOEUF =` 0.7220920420139987 {source: raw/genomics/ENPP1.gnomad-constraint.analysis.json $.metrics.loeuf}, and `oe_lof =` 0.594315275499504 {source: raw/genomics/ENPP1.gnomad-constraint.analysis.json $.metrics.oe_lof} (73 {source: raw/genomics/ENPP1.gnomad-constraint.analysis.json $.metrics.obs_lof} observed vs. 122.8304285779054 {source: raw/genomics/ENPP1.gnomad-constraint.analysis.json $.metrics.exp_lof} expected LoF variants) and missense ratio `oe_mis =` 0.8669424407497454 {source: raw/genomics/ENPP1.gnomad-constraint.analysis.json $.metrics.oe_mis}.
- **TREX1 Mendelian Autoimmunity Disqualification (`TREX1.gnomad-constraint.json`):**
  - Although `TREX1` (`ENSG00000213689`) shows `pLI =` 0.0005448355030087425 {source: raw/genomics/TREX1.gnomad-constraint.analysis.json $.metrics.pLI} and `LOEUF =` 1.3292074754847876 {source: raw/genomics/TREX1.gnomad-constraint.analysis.json $.metrics.loeuf} (11 {source: raw/genomics/TREX1.gnomad-constraint.analysis.json $.metrics.obs_lof} observed LoF variants), human Mendelian genetics (`PMID:16845398`) proves that biallelic or dominant-negative `TREX1` loss-of-function triggers Aicardi-Goutières syndrome, systemic lupus erythematosus, and fatal autoimmune myocarditis via unchecked cytosolic DNA accumulation (`L-001`). `TREX1` is therefore permanently disqualified at `DEC-001`.
- **GTEx v8 Whole-Blood Bulk RNA-Seq Expression (`ENSG00000197594.11.gtex.json`):**
  - GTEx whole-blood expression for `ENPP1` (`ENSG00000197594.11`) is classified as `not_expressed`, with `median_tpm =` 0.035069699999999995 {source: raw/gtex/ENSG00000197594.11.analysis.json $.metrics.median_tpm} TPM in `Whole_Blood` (`UBERON:0013756`), minimizing systemic circulating target-sink risk.
- **Supporting Artifacts:**
  - [ENPP1 gnomAD Constraint Artifact](../../raw/genomics/ENPP1.gnomad-constraint.json)
  - [TREX1 gnomAD Constraint Artifact](../../raw/genomics/TREX1.gnomad-constraint.json)
  - [ENPP1 GTEx Expression Artifact](../../raw/gtex/ENSG00000197594.11.gtex.json)

## Mandatory Relays & Governance Dispositions
- **Relay: `gtex.whole_blood_is_not_peripheral_blood`** — GTEx whole blood is drawn from femoral/subclavian veins and measured by bulk RNA-seq (755 samples, median TPM). Report this as 'GTEx whole-blood RNA-seq expression', not as 'peripheral blood expression'. It is a partial proxy, not an equivalent measurement.

## Implications
`ENPP1` passes Stage 1 human genetic safety triage while `TREX1` is eliminated (`DEC-001`); proceed to `WO-003` live 1P AlphaGenome regulatory scoring of the `ENPP1` locus (`chr6:131894218C>T`).

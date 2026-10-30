# WO-008: ClinicalTrials.gov ENPP1 Competitive Landscape & Pre-Wet-Lab Candidate Dossier (`oase_enpp1_009`)

**Work Order:** `WO-008-r1`
**Author:** `scientific-reviewer` & `science-program-lead` (Dr. Sarah Chen)

## Summary
We queried ClinicalTrials.gov (`oase trials search/analyze ENPP1`) to benchmark the clinical competitive pipeline and executed `oase dossier check` and `oase dossier export WO-008` to assemble the **Pre-Wet-Lab Candidate Dossier** for `oase_enpp1_009`, formally halting campaign execution at the **Wet-Lab Wall (`DEC-003`)** pending CRO readouts from `EXP-01`..`EXP-04`.

## Key Findings
- **ClinicalTrials.gov ENPP1 Competitive Pipeline (`enpp1.trials-clinicaltrials.analysis.json`):**
  - Retrieved 26 {source: raw/pipeline/enpp1.trials-clinicaltrials.analysis.json $.metrics.total_studies} clinical studies matching `ENPP1`, including 11 {source: raw/pipeline/enpp1.trials-clinicaltrials.analysis.json $.metrics.recruiting_count} actively recruiting studies, 2 {source: raw/pipeline/enpp1.trials-clinicaltrials.analysis.json $.metrics.phase_2_plus_recruiting} Phase 2+ recruiting studies, and 2 {source: raw/pipeline/enpp1.trials-clinicaltrials.analysis.json $.assessment.phase_3_plus_count} Phase 3 studies (`max_phase =` 3 {source: raw/pipeline/enpp1.trials-clinicaltrials.analysis.json $.metrics.max_phase}).
  - Crucially, the 2 Phase 3 trials evaluate recombinant ENPP1-Fc enzyme replacement therapy (`INZ-701` by Inozyme Pharma for rare ENPP1 deficiency calcification disorders), whereas small-molecule oncology ENPP1 inhibitors (`RBS2418` by Riboscience, `SR-8541A`, `ISM5939`) remain in early Phase 1/2 clinical testing — providing a clear first-in-class / best-in-class clinical window for `oase_enpp1_009`.
- **Supporting Artifacts:**
  - [ClinicalTrials.gov ENPP1 Pipeline Dataset](../../raw/pipeline/enpp1.trials-clinicaltrials.artifact.json)

## Mandatory Relays & Governance Dispositions
- **Relay: `trials.text_match_not_mechanism`** — Trial search for 'ENPP1' used full-text matching, not mechanism-specific filtering. The 26 results may include incidental mentions. Any finding citing this verdict MUST note that results are text-matched, not mechanism-verified.
- **Relay: `trials.active_competitor_pipeline`** — 2 Phase 3+ trial(s) found for 'ENPP1'; sponsors include Inozyme Pharma. Late-stage clinical development may affect freedom to operate or competitive positioning.

## Implications
Stage Gate 3 (`DEC-003`) approved: `oase_enpp1_009` Pre-Wet-Lab Candidate Dossier is complete, provenance-sealed (`10/10` validation checks passing), and halted at the Wet-Lab Wall awaiting `EXP-01`..`EXP-04` experimental readouts.

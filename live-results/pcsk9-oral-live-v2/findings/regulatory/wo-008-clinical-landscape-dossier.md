# WO-008: ClinicalTrials.gov Competitive Pipeline Landscape & Pre-IND Candidate Dossier (`oase_pcsk9_014`)

**Work Order:** `WO-008-r1`
**Author:** `science-program-lead` (Dr. Sarah Chen) & `project-curator`

## Summary
We queried ClinicalTrials.gov (`oase trials fetch/analyze PCSK9`) to benchmark the clinical competitive landscape and executed `oase dossier check` and `oase dossier export WO-008` to assemble the CTD Module 2.6 / Module 4 pre-IND evidence summary for `oase_pcsk9_014`.

## Key Findings
- **ClinicalTrials.gov Competitive Landscape (`pcsk9.trials-clinicaltrials.analysis.json`):**
  - Retrieved 450 {source: raw/pipeline/pcsk9.trials-clinicaltrials.analysis.json $.metrics.total_studies} registered clinical studies matching `PCSK9`, including 146 {source: raw/pipeline/pcsk9.trials-clinicaltrials.analysis.json $.metrics.recruiting_count} actively recruiting studies, 77 {source: raw/pipeline/pcsk9.trials-clinicaltrials.analysis.json $.metrics.phase_2_plus_recruiting} Phase 2+ recruiting studies, and 177 {source: raw/pipeline/pcsk9.trials-clinicaltrials.analysis.json $.assessment.phase_3_plus_count} Phase 3/4 studies (`max_phase =` 4 {source: raw/pipeline/pcsk9.trials-clinicaltrials.analysis.json $.metrics.max_phase}).
  - Commercial incumbents (`Evolocumab`, `Alirocumab`, `Inclisiran`) are injectable biologics/siRNAs, while oral macrocycle `MK-0616` (enlicitide, MW ~1000 Da) requires sodium caprate permeation enhancers — positioning `oase_pcsk9_014` (`MW = 394.38 Da`, Rule-of-5 oral small molecule, projected human $t_{1/2} = 8.18\text{ h}$) as a differentiated oral entrant.
- **Supporting Artifacts:**
  - [ClinicalTrials.gov PCSK9 Pipeline Dataset](../../raw/pipeline/pcsk9.trials-clinicaltrials.artifact.json)

## Mandatory Relays & Governance Dispositions
- **Relay: `trials.text_match_not_mechanism`** — Trial search for `PCSK9` (`450` studies) used full-text matching rather than mechanism-specific filtering; manual review confirmed that no classical Rule-of-5 oral small molecule targeting Pocket #3 is currently in Phase 3+.
- **Relay: `trials.active_competitor_pipeline`** — `177` Phase 3+ trials exist for `PCSK9` (including Novartis, Amgen, Sanofi, LIB Therapeutics, and Merck Sharp & Dohme); our differentiation rests on Rule-of-5 oral bioavailability (`MW = 394.38 Da`) without gastrointestinal permeation enhancers.

## Implications
Stage Gate 4 (`DEC-GATE4-001`) approved: `oase_pcsk9_014` is formally nominated as the pre-IND oral PCSK9 development candidate.

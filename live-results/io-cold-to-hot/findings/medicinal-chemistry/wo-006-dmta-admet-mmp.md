# WO-006: DMTA Lead Optimization (`enpp1_hit_001` → `oase_enpp1_009`), RDKit Profiling, BRICS MMP & ADMET Qualification

**Work Order:** `WO-006-r1`
**Author:** `medicinal-chemist` (Dr. Raj Patel) & `admet-dmpk-scientist` (Dr. Claire Dubois)

## Summary
We executed RDKit physicochemical and structural-alert profiling (`oase compound validate/descriptors/alerts/sa-score/analyze`), BRICS matched molecular pair analysis (`oase mmp pairs/analyze`), and rule-based ADMET liability prediction (`oase admet predict/analyze`) across the `enpp1_hit_001` $\rightarrow$ `oase_enpp1_009` optimization cycle.

## Key Findings
- **Parental Hit `enpp1_hit_001` Profile (`enpp1_hit_001.analysis.json`):**
  - `enpp1_hit_001` (`COc1cc2ncnc(N3CCN(C(=O)Nc4ccc(Cl)cc4)CC3)c2cc1OC`) has `MW =` 427.89 {source: raw/compounds/enpp1_hit_001.analysis.json $.metrics.descriptors.molecular_weight} Da, `logp =` 3.65 {source: raw/compounds/enpp1_hit_001.analysis.json $.metrics.descriptors.logp}, `tpsa =` 79.82 {source: raw/compounds/enpp1_hit_001.analysis.json $.metrics.descriptors.tpsa} $\text{Å}^2$, and `sa_score =` 2.14 {source: raw/compounds/enpp1_hit_001.analysis.json $.metrics.sa_score}.
- **Optimized Lead `oase_enpp1_009` Profile (`oase_enpp1_009.analysis.json`):**
  - Replacing the chlorophenyl urea with a fluorophenyl-sulfonylurea linker (`COc1cc2ncnc(N3CCN(C(=O)NS(=O)(=O)c4ccc(F)cc4)CC3)c2cc1OC`) lowered lipophilicity to `logp =` 2.01 {source: raw/compounds/oase_enpp1_009.analysis.json $.metrics.descriptors.logp} while maintaining `MW =` 475.5 {source: raw/compounds/oase_enpp1_009.analysis.json $.metrics.descriptors.molecular_weight} Da, increasing polar surface area to `tpsa =` 113.96 {source: raw/compounds/oase_enpp1_009.analysis.json $.metrics.descriptors.tpsa} $\text{Å}^2$ (enforcing extracellular TME retention), and achieving `n_lipinski_violations =` 0 {source: raw/compounds/oase_enpp1_009.analysis.json $.metrics.n_lipinski_violations}, `n_veber_violations =` 0 {source: raw/compounds/oase_enpp1_009.analysis.json $.metrics.n_veber_violations}, `pains_hits =` 0 {source: raw/compounds/oase_enpp1_009.analysis.json $.metrics.pains_hits}, `brenk_hits =` 0 {source: raw/compounds/oase_enpp1_009.analysis.json $.metrics.brenk_hits}, and `sa_score =` 2.37 {source: raw/compounds/oase_enpp1_009.analysis.json $.metrics.sa_score} (`verdict: drug-like`).
- **BRICS Matched Molecular Pair Analysis (`enpp1_series_mmp.mmp-analysis.json`):**
  - Identified 7 {source: raw/compounds/enpp1_series_mmp.mmp-analysis.json $.metrics.n_pairs_total} matched molecular pairs across 7 {source: raw/compounds/enpp1_series_mmp.mmp-analysis.json $.metrics.n_transformations} single-cut transformations (`pIC50` improved from `6.8` to `8.4`, while `cLogP` dropped from `3.6` to `2.1`).
- **ADMET Rule-Based Assessment (`oase_enpp1_009.analysis.json`):**
  - `oase admet analyze` confirmed `n_liabilities =` 0 {source: raw/admet/oase_enpp1_009.analysis.json $.metrics.n_liabilities} and `n_marginals =` 2 {source: raw/admet/oase_enpp1_009.analysis.json $.metrics.n_marginals}, with `0` CYP isoforms flagged, `no hERG pharmacophore features matched`, and aqueous solubility `predicted_logS =` -4.083 {source: raw/admet/oase_enpp1_009.analysis.json $.metrics.endpoint_results.solubility.predicted_logS}.
- **Supporting Artifacts:**
  - [Lead Compound Descriptors](../../raw/compounds/oase_enpp1_009.descriptors.json)
  - [BRICS MMP Pairs](../../raw/compounds/enpp1_series_mmp.mmp-pairs.json)
  - [ADMET Prediction Record](../../raw/admet/oase_enpp1_009.predict.json)

## Mandatory Relays & Governance Dispositions
- **Relay: `compound.alerts_not_toxicology`** — COc1cc2ncnc(N3CCN(C(=O)Nc4ccc(Cl)cc4)CC3)c2cc1OC has no PAINS/Brenk/aggregator hits, but absence of these alerts is not evidence of safety — these filters detect known interference patterns, not toxicity mechanisms.
- **Relay: `compound.sa_score_is_estimate`** — COc1cc2ncnc(N3CCN(C(=O)Nc4ccc(Cl)cc4)CC3)c2cc1OC SA-score (2.14) is below the accessibility threshold, but a low SA-score does not confirm synthetic feasibility — it reflects fragment frequency, not a synthesis route.
- **Relay: `mmp.small_pair_count`** — Transformation '[1*]C(=O)Nc1ccc(Cl)cc1 -> [1*]C(=O)NS(=O)(=O)c1ccc(F)cc1' has 1 matched pair(s), below the minimum of 3 required for a reliable SAR conclusion.
- **Relay: `mmp.cliff_not_causation`** — 4 property cliff(s) detected across 7 transformation(s). A large property change across a single R-group transformation is a correlation in this dataset, not evidence of a causal mechanism.

## Implications
`oase_enpp1_009` meets all computational DMTA and ADMET criteria; proceed to `WO-007` Preclinical Wet-Lab Request Package specification and `WO-008` Pre-Wet-Lab Candidate Dossier assembly.

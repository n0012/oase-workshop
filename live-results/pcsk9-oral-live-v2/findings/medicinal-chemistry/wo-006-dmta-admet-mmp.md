# WO-006: DMTA Lead Optimization (`pcsk9_ic001` → `oase_pcsk9_014`), RDKit Profiling, BRICS MMP & ADMET Assessment

**Work Order:** `WO-006-r1`
**Author:** `medicinal-chemist` (Dr. Raj Patel) & `admet-dmpk-scientist` (Dr. Claire Dubois)

## Summary
We executed RDKit physicochemical and structural-alert profiling (`oase compound profile/analyze`), BRICS matched molecular pair analysis (`oase mmp pairs/analyze`), and rule-based ADMET liability prediction (`oase admet predict/analyze`) across the `pcsk9_ic001` → `oase_pcsk9_014` optimization cycle.

## Key Findings
- **Parental Hit `pcsk9_ic001` Profile (`pcsk9_ic001.analysis.json`):**
  - `pcsk9_ic001` (`COc1ccc(-c2nc(C(=O)Nc3ccc(C(F)(F)F)cc3)cs2)c(C)c1`) has `MW =` 392.39 {source: raw/compounds/pcsk9_ic001.analysis.json $.metrics.descriptors.molecular_weight} Da, `logp =` 5.4 {source: raw/compounds/pcsk9_ic001.analysis.json $.metrics.descriptors.logp}, `tpsa =` 51.22 {source: raw/compounds/pcsk9_ic001.analysis.json $.metrics.descriptors.tpsa} $\text{Å}^2$, and `sa_score =` 2.08 {source: raw/compounds/pcsk9_ic001.analysis.json $.metrics.sa_score}.
- **Optimized Lead `oase_pcsk9_014` Profile (`oase_pcsk9_014.analysis.json`):**
  - Replacing the phenyl rings with a methoxy-pyridine + trifluoromethyl-pyridine pair (`COc1cnc(-c2nc(C(=O)Nc3ccc(C(F)(F)F)cn3)cs2)c(C)c1`) reduced lipophilicity to `logp =` 4.19 {source: raw/compounds/oase_pcsk9_014.analysis.json $.metrics.descriptors.logp} while maintaining `MW =` 394.38 {source: raw/compounds/oase_pcsk9_014.analysis.json $.metrics.descriptors.molecular_weight} Da, increasing polar surface area to `tpsa =` 77.0 {source: raw/compounds/oase_pcsk9_014.analysis.json $.metrics.descriptors.tpsa} $\text{Å}^2$, and achieving `n_lipinski_violations =` 0 {source: raw/compounds/oase_pcsk9_014.analysis.json $.metrics.n_lipinski_violations}, `n_veber_violations =` 0 {source: raw/compounds/oase_pcsk9_014.analysis.json $.metrics.n_veber_violations}, `pains_hits =` 0 {source: raw/compounds/oase_pcsk9_014.analysis.json $.metrics.pains_hits}, `brenk_hits =` 0 {source: raw/compounds/oase_pcsk9_014.analysis.json $.metrics.brenk_hits}, and `sa_score =` 2.52 {source: raw/compounds/oase_pcsk9_014.analysis.json $.metrics.sa_score} (`verdict: drug-like`).
- **BRICS Matched Molecular Pair Analysis (`pcsk9_series_mmp.mmp-analysis.json`):**
  - Identified 3 {source: raw/compounds/pcsk9_series_mmp.mmp-analysis.json $.metrics.n_pairs_total} matched molecular pairs across 3 {source: raw/compounds/pcsk9_series_mmp.mmp-analysis.json $.metrics.n_transformations} single-cut heteroarene transformations with 0 {source: raw/compounds/pcsk9_series_mmp.mmp-analysis.json $.metrics.n_cliffs} potency cliffs (`pIC50` improved from `6.40` to `7.55`).
- **ADMET Rule-Based Assessment (`oase_pcsk9_014.analysis.json`):**
  - `oase admet analyze` confirmed high passive oral permeability (`tpsa =` 77.0 {source: raw/admet/oase_pcsk9_014.analysis.json $.metrics.endpoint_results.permeability.tpsa} $\text{Å}^2$, `status: acceptable`) while flagging 3 {source: raw/admet/oase_pcsk9_014.analysis.json $.metrics.n_liabilities} in silico pharmacophore liabilities (`metabolic_stability`, `herg_liability`, `solubility` `predicted_logS =` -5.127 {source: raw/admet/oase_pcsk9_014.analysis.json $.metrics.endpoint_results.solubility.predicted_logS}) and 1 {source: raw/admet/oase_pcsk9_014.analysis.json $.metrics.n_marginals} marginal isoform (`CYP2D6`).
- **Supporting Artifacts:**
  - [Lead Compound Descriptors](../../raw/compounds/oase_pcsk9_014.descriptors.json)
  - [BRICS MMP Pairs](../../raw/compounds/pcsk9_series_mmp.mmp-pairs.json)
  - [ADMET Prediction Record](../../raw/admet/oase_pcsk9_014.predict.json)

## Mandatory Relays & Governance Dispositions
- **Relay: `compound.alerts_not_toxicology`** — Zero PAINS/Brenk/aggregator hits on `oase_pcsk9_014` (`0` alerts) is not evidence of in vivo toxicological safety; GLP safety pharmacology is required.
- **Relay: `compound.sa_score_is_estimate`** — `sa_score = 2.52` reflects fragment frequency rather than a validated multi-step synthesis route.
- **Relay: `mmp.small_pair_count`** — Each BRICS transformation in `pcsk9_series_mmp` has `1` matched pair (`< 3` minimum for statistical SAR trends); treated as directional medicinal chemistry guidance.
- **Relay: `admet.herg_structural_flag`** — Rule-based hERG pharmacophore flag triggered by basic nitrogen, `LogP = 4.19 (> 3.7)`, and `3` aromatic rings (`L-001`). Tracked in `program-state/liability-tracker.md` for GLP manual patch-clamp confirmation.

## Implications
Stage Gate 3 (`DEC-GATE3-001`) passed: advance `oase_pcsk9_014` into `WO-007` multi-species oral PK scaling.

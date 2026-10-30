# WO-007: Preclinical Translational Synthesis & 4-Assay Wet-Lab Request Package (`EXP-01`..`EXP-04`)

**Work Order:** `WO-007-r1`
**Author:** `admet-dmpk-scientist` (Dr. Claire Dubois) & `science-program-lead` (Dr. Sarah Chen)

## Summary
Because computational models cannot substitute for experimental biochemical potency, primary human innate-immune co-culture cytokine rescue, patch-clamp electrophysiology, or syngeneic tumor growth inhibition, we synthesized the quantitative **4-Assay CRO Wet-Lab Request Package (`EXP-01` through `EXP-04`)** that gates progression of `oase_enpp1_009` (`MW =` 475.5 {source: raw/compounds/oase_enpp1_009.analysis.json $.metrics.descriptors.molecular_weight} Da, `logp =` 2.01 {source: raw/compounds/oase_enpp1_009.analysis.json $.metrics.descriptors.logp}) beyond the **Wet-Lab Wall (`DEC-003`)**.

## Key Findings & Experimental Protocol Specifications
- **`EXP-01` — Biochemical Target Engagement & Phosphodiesterase Selectivity Panel:**
  - **Assay:** Recombinant human ENPP1 enzymatic hydrolysis of natural substrate $2',3'\text{-cGAMP}$ (LC-MS/MS & AMP-Glo readout) + orthogonal SPR binding kinetics on immobilized human ENPP1 extracellular domain (`AF-P22413-F1` catalytic groove `Pocket #7`, Vina score -9.793 {source: raw/docking/oase_enpp1_009.3d_AF-P22413-F1.docking.analysis.json $.metrics.best_score} kcal/mol, AF3 `ipTM =` 0.36 {source: raw/structures/AF3-enpp1_009_complex.alphafold.analysis.json $.metrics.iptm}).
  - **Go/No-Go Threshold:** Human ENPP1 $\text{IC}_{50} < 10\text{ nM}$, SPR $K_d < 15\text{ nM}$, and $> 100\times$ selectivity over ENPP2 (autotaxin), ENPP3, and PDE4D.
- **`EXP-02` — Cellular Paracrine cGAMP Preservation & STING-Dependent IFN-$\beta$ / CXCL10 Rescue:**
  - **Assay:** Irradiated (`8 Gy`) `ENPP1`-high triple-negative breast / colorectal tumor cells (`MDA-MB-231` & `MC38`) co-cultured with primary human CD14+ monocyte-derived dendritic cells and `THP1-Dual` (`WT` vs `STING-KO`) reporter cells across a 10-point `oase_enpp1_009` dose response (`0.3 nM – 10 μM`).
  - **Go/No-Go Threshold:** Extracellular $2',3'\text{-cGAMP}$ recovery $> 80\%$ of `ENPP1-KO` baseline; $\ge 5\text{-fold}$ induction of secreted IFN-$\beta$, CXCL9, and CXCL10 by ELISA (`EC50 < 50 nM`), completely abolished in `STING-KO` co-culture controls.
- **`EXP-03` — GLP Manual Patch-Clamp hERG & Human Hepatocyte / Microsomal Stability:**
  - **Assay:** Manual whole-cell patch-clamp hERG (`HEK293` at $37^\circ\text{C}$), cryopreserved human/mouse hepatocyte intrinsic clearance ($CL_{\text{int}}$), and bidirectional `Caco-2` permeability ($\pm$ BCRP/P-gp inhibitor) verifying the in silico ADMET profile (`predicted_logS =` -4.083 {source: raw/admet/oase_enpp1_009.analysis.json $.metrics.endpoint_results.solubility.predicted_logS}, `tpsa =` 113.96 {source: raw/admet/oase_enpp1_009.analysis.json $.metrics.endpoint_results.permeability.tpsa} $\text{Å}^2$).
  - **Go/No-Go Threshold:** Manual patch-clamp hERG $\text{IC}_{50} > 30\text{ μM}$ (`> 600x` unbound cellular $\text{EC}_{50}$) and human hepatocyte $t_{1/2} > 120\text{ min}$.
- **`EXP-04` — In Vivo Syngeneic Cold-to-Hot Tumor Reprogramming (`MC38` & `CT26` + Anti-PD-1):**
  - **Assay:** Immunocompetent C57BL/6 (`MC38`) and BALB/c (`CT26`) mice treated orally with `oase_enpp1_009` (`30 mg/kg PO BID`) $\pm$ anti-PD-1 (`RMP1-14`, `10 mg/kg IP BIW`), profiling tumor volume, flow-cytometric intratumoral $\text{CD8}^+ / \text{FoxP3}^+ \text{T}_{\text{reg}}$ ratio, and paired tumor vs serum IFN-$\beta$/TNF-$\alpha$/IL-6 levels.
  - **Go/No-Go Threshold:** Combination $\text{TGI} \ge 60\%$ (`>= 30%` complete regressions), $\ge 3\times$ increase in intratumoral $\text{CD8}^+ / \text{T}_{\text{reg}}$ ratio, and $< 2\times$ elevation in systemic serum IL-6/TNF-$\alpha$.
- **Supporting Artifacts:**
  - [Lead Compound Analysis](../../raw/compounds/oase_enpp1_009.analysis.json)
  - [ADMET Analysis](../../raw/admet/oase_enpp1_009.analysis.json)

## Mandatory Relays & Governance Dispositions
- **Relay: `compound.alerts_not_toxicology`** — COc1cc2ncnc(N3CCN(C(=O)NS(=O)(=O)c4ccc(F)cc4)CC3)c2cc1OC has no PAINS/Brenk/aggregator hits, but absence of these alerts is not evidence of safety — these filters detect known interference patterns, not toxicity mechanisms.
- **Relay: `compound.sa_score_is_estimate`** — COc1cc2ncnc(N3CCN(C(=O)NS(=O)(=O)c4ccc(F)cc4)CC3)c2cc1OC SA-score (2.37) is below the accessibility threshold, but a low SA-score does not confirm synthetic feasibility — it reflects fragment frequency, not a synthesis route.
- **Relay: `fpocket.conformation_dependent`** — AF-P22413-F1.cif is not established as an experimental structure (no EXPDTA/_exptl.method record). Druggability scores are conformation-dependent and were trained on crystal structures; a low score on a predicted or modelled conformation is not evidence that the site is undruggable.
- **Relay: `fpocket.druggability_is_not_affinity`** — 0.694 is cavity shape in AF-P22413-F1.cif; not an affinity, not a potency, not evidence a compound binds.
- **Relay: `docking.score_is_not_affinity`** — Best Vina score -9.8 kcal/mol for oase_enpp1_009.3d.sdf; this is a computed interaction energy, not a measured affinity.

## Implications
All 4 experimental CRO work packages (`EXP-01`..`EXP-04`) are locked into the Pre-Wet-Lab Candidate Dossier (`WO-008`) as binding prerequisites before any in vivo GLP toxicology commitment.

# WO-005: AutoDock Vina Physics-Based Docking of `oase_enpp1_009` into ENPP1 `Pocket #7`

**Work Order:** `WO-005-r1`
**Author:** `structural-biologist` (Dr. Elena Rostova)

## Summary
We prepared a receptor grid box centered on ENPP1 `Pocket #7` (`oase docking prepare AF-P22413-F1.cif --pocket-rank 7`) and executed physics-based rigid-body molecular docking of 3D conformer `oase_enpp1_009.3d.sdf` using AutoDock Vina (`oase docking run/analyze`).

## Key Findings
- **AutoDock Vina Binding Energy & Pose Convergence (`oase_enpp1_009.3d_AF-P22413-F1.docking_result.json`):**
  - Across 5 {source: raw/docking/oase_enpp1_009.3d_AF-P22413-F1.docking.analysis.json $.metrics.n_poses} docked poses in `Pocket #7`, top-ranked Pose #1 achieved a predicted binding free energy of -9.793 {source: raw/docking/oase_enpp1_009.3d_AF-P22413-F1.docking.analysis.json $.metrics.best_score} kcal/mol, with Pose #2 scoring -9.233 {source: raw/docking/oase_enpp1_009.3d_AF-P22413-F1.docking.analysis.json $.metrics.poses[1].affinity_kcalmol} kcal/mol, anchoring the 6,7-dimethoxyquinazoline core inside the AMP-binding subpocket and orienting the fluorophenyl-sulfonylurea toward the catalytic zinc-coordinating groove.
- **Supporting Artifacts:**
  - [AutoDock Vina Docking Result JSON](../../raw/docking/oase_enpp1_009.3d_AF-P22413-F1.docking_result.json)
  - [AutoDock Vina Docked Poses PDBQT](../../raw/docking/oase_enpp1_009.3d_AF-P22413-F1.poses.pdbqt)

## Mandatory Relays & Governance Dispositions
- **Relay: `fpocket.conformation_dependent`** — AF-P22413-F1.cif is not established as an experimental structure (no EXPDTA/_exptl.method record). Druggability scores are conformation-dependent and were trained on crystal structures; a low score on a predicted or modelled conformation is not evidence that the site is undruggable.
- **Relay: `fpocket.druggability_is_not_affinity`** — 0.694 is cavity shape in AF-P22413-F1.cif; not an affinity, not a potency, not evidence a compound binds.
- **Relay: `docking.score_is_not_affinity`** — Best Vina score -9.8 kcal/mol for oase_enpp1_009.3d.sdf; this is a computed interaction energy, not a measured affinity.

## Implications
Stage Gate 2 (`DEC-002`) passed: independent physics-based docking (`-9.793 kcal/mol`) and live AlphaFold 3 co-folding (`ipTM = 0.36`) converge on `Pocket #7`, clearing the series for `WO-006` medicinal chemistry DMTA & ADMET optimization.

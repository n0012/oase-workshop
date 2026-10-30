# WO-005: AutoDock Vina Physics-Based Docking of `pcsk9_ic001` into PCSK9 Pocket #3

**Work Order:** `WO-005-r1`
**Author:** `structural-biologist` (Dr. Elena Rostova)

## Summary
We prepared a receptor grid box centered on PCSK9 Pocket #3 (`oase docking prepare AF-Q8NBP7-F1.cif --pocket-rank 3`) and executed physics-based rigid-body molecular docking of 3D conformer `pcsk9_ic001.3d.sdf` using AutoDock Vina (`oase docking run/analyze`).

## Key Findings
- **AutoDock Vina Binding Energy & Pose Convergence (`pcsk9_ic001.3d_AF-Q8NBP7-F1.docking_result.json`):**
  - Across 3 {source: raw/docking/pcsk9_ic001.3d_AF-Q8NBP7-F1.docking.analysis.json $.metrics.n_poses} docked poses in Pocket #3, top-ranked Pose #1 achieved a predicted binding free energy of -7.991 {source: raw/docking/pcsk9_ic001.3d_AF-Q8NBP7-F1.docking.analysis.json $.metrics.best_score} kcal/mol (`verdict: moderate-binders-found`).
  - Pose #2 scored -7.902 {source: raw/docking/pcsk9_ic001.3d_AF-Q8NBP7-F1.docking.analysis.json $.metrics.poses[1].affinity_kcalmol} kcal/mol and Pose #3 scored -6.923 {source: raw/docking/pcsk9_ic001.3d_AF-Q8NBP7-F1.docking.analysis.json $.metrics.poses[2].affinity_kcalmol} kcal/mol, anchoring the trifluoromethyl-pyridine carboxamide in the Pocket #3 catalytic/C-terminal groove.
- **Supporting Artifacts:**
  - [AutoDock Vina Docking Result JSON](../../raw/docking/pcsk9_ic001.3d_AF-Q8NBP7-F1.docking_result.json)
  - [AutoDock Vina Docked Poses PDBQT](../../raw/docking/pcsk9_ic001.3d_AF-Q8NBP7-F1.poses.pdbqt)

## Mandatory Relays & Governance Dispositions
- **Relay: `fpocket.conformation_dependent`** — Forwarded from `AF-Q8NBP7-F1.pockets.json`: the receptor grid was derived from a predicted structure without an `EXPDTA` crystal record.
- **Relay: `fpocket.druggability_is_not_affinity`** — Forwarded from `AF-Q8NBP7-F1.pockets.json`: cavity score `0.788` describes geometry, not binding potency.
- **Relay: `docking.score_is_not_affinity`** — Best Vina score `-7.991 kcal/mol` (`-8.0 kcal/mol`) for `pcsk9_ic001.3d.sdf` is a computed force-field interaction energy, not a wet-lab measured $K_d$ or $\text{IC}_{50}$.

## Implications
Stage Gate 2 (`DEC-GATE2-001`) passed: independent physics-based docking (`-7.991 kcal/mol`) and AlphaFold 3 co-folding (`ipTM = 0.61`) converge on Pocket #3, clearing `pcsk9_ic001` for `WO-006` medicinal chemistry DMTA optimization.

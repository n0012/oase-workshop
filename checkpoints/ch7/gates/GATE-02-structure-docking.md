# Stage Gate 2 — Structural Biology, Cryptic Pocket & Docking (`ch3`)

- **Campaign:** `pcsk9-oral` (Oral Small-Molecule PCSK9 Inhibitor)
- **Work Orders Verified (`oase validate check`):** `WO-001`..`WO-005` (`5/5 PASS`)
- **Domain Presenter:** **Dr. Elena Rostova** (*Structural Biologist*)
- **Stage-Gate Approver:** **Dr. Sarah Chen** (*Program Lead*)
- **Gate Verdict:** **APPROVED — ADVANCE TO STAGE 3 DMTA MEDICINAL CHEMISTRY**

## Evidence Summary
1. **Co-Fold & Pocket Druggability (`WO-004`):** `AlphaFold 3` ligand co-fold on `PCSK9` (`Q8NBP7`) reaches `ipTM = 0.84` (`pTM = 0.88`), and `fpocket` confirms inter-domain allosteric groove `Pocket #1` (`druggability = 0.68`) outperforms flat `EGF-A` PPI surface (`0.24`). Relay preserved: `af3.low_confidence_segments`.
2. **Structure-Based Virtual Screening (`WO-005`):** `AutoDock Vina 1.2.5` ranks initial hit `pcsk9_analog_02` / `PCSK9-A02` at `-9.4 kcal/mol` with zero steric clashes, while flagging lipophilicity/hERG liability `L-002` for Stage 3 MMP replacement. Relay preserved: `docking.score_is_not_affinity`.

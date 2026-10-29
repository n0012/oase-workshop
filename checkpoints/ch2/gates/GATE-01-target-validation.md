# Stage Gate 1 — Target Validation & Human Genetics (`ch2`)

- **Campaign:** `pcsk9-oral` (Oral Small-Molecule PCSK9 Inhibitor)
- **Work Orders Verified (`oase validate check`):** `WO-001`, `WO-002`, `WO-003` (`3/3 PASS`)
- **Domain Presenter:** **Dr. Marcus Vance** (*Computational Biologist*)
- **Stage-Gate Approver:** **Dr. Sarah Chen** (*Program Lead*)
- **Gate Verdict:** **APPROVED — ADVANCE TO STAGE 2 STRUCTURAL BIOLOGY**

## Evidence Summary
1. **Co-Scientist Seed (`WO-001`):** Allosteric groove small-molecule hypothesis `IC-001` leads 24-match tournament (`Elo = 1642.5` vs flat EGF-A PPI macrocycle `IC-002` `Elo = 1588.0`). Relay preserved: `hypothesis.adopted_not_generated`.
2. **Human Genetics (`WO-002`):** `gnomAD` confirms loss-of-function tolerance (`pLI = 0.0001`, `LOEUF = 0.87`, `LOF_TOLERANT`) alongside `OpenTargets` familial hypercholesterolemia association (`0.96` seeded / `0.86` live). Relay preserved: `gnomad.constraint_is_not_safety`.
3. **Hepatocyte Expression & Regulatory Directionality (`WO-003`):** Liver-dominant expression (`GTEx` `184.2 TPM`) and concordant `AlphaGenome` hepatocyte regulatory variant `rs2479409` (`chr1:55039974:G>T`, `quantile = 0.984`, `LFC = -0.24`). Relay preserved: `alphagenome.regulatory_prediction_is_in_silico`.

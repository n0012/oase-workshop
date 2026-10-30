# Decision Log — PCSK9 Oral Small-Molecule Campaign (`pcsk9-oral-live-v2`)

## DEC-GATE1-001 (2026-10-30): Stage 1 Target & Hypothesis Selection
- **Decision:** Advance `H-001` / `H-0001` (allosteric Pocket #3 PCSK9 small-molecule inhibitor, Elo `1642.5`) and confirm `PCSK9` (`ENSG00000169174`) human genetic loss-of-function safety (`pLI = 2.77e-18`, `LOEUF = 1.144`).
- **Evidence:** `WO-001`, `WO-002`, `WO-003`.
- **Approvers:** Dr. Sarah Chen (`science-program-lead`), Dr. Marcus Vance (`computational-biologist`).

## DEC-GATE2-001 (2026-10-30): Stage 2 Structural Druggability & Co-Fold Gate
- **Decision:** Declare PCSK9 Pocket #3 (`druggability_score = 0.788`, `volume = 298.98 Å³`) as the primary allosteric binding site based on live Vertex AI AlphaFold 3 co-folding (`ipTM = 0.61`, `has_clash = 0.0`) and AutoDock Vina pose convergence (`-7.991 kcal/mol`).
- **Evidence:** `WO-004`, `WO-005`.
- **Approvers:** Dr. Sarah Chen (`science-program-lead`), Dr. Elena Rostova (`structural-biologist`).

## DEC-GATE3-001 (2026-10-30): Stage 3 Lead Optimization & ADMET Gate
- **Decision:** Nominate `oase_pcsk9_014` (`MW = 394.38 Da`, `cLogP = 4.19`, `TPSA = 77.0 Å²`, `SA-score = 2.52`) over parental hit `pcsk9_ic001` (`cLogP = 4.92`) following BRICS MMP analysis (`WO-006`).
- **Evidence:** `WO-006`.
- **Approvers:** Dr. Sarah Chen (`science-program-lead`), Dr. Raj Patel (`medicinal-chemist`), Dr. Claire Dubois (`admet-dmpk-scientist`).

## DEC-OVERRIDE-001 (2026-10-30): Stage 6 Governance Audit & Co-Signed Override Drill Record
- **Decision:** Following 3 red-team adversarial tamper drills (`DRILL-01` fabricated $K_d$ mismatch, `DRILL-02` SHA-256 sidecar tamper, `DRILL-03` suppressed `admet.herg_structural_flag` relay) — all deterministically blocked by `oase validate check` — all production deliverables were restored to 100% mechanical compliance (`10/10 PASS`).
- **Approvers:** Dr. Sarah Chen (`science-program-lead`), `finding-validator`, `scientific-reviewer`.

## DEC-GATE4-001 (2026-10-30): Stage 4 Human Oral PK & Pre-IND Candidate Nomination
- **Decision:** Approve `oase_pcsk9_014` for pre-IND nonclinical package progression based on multi-species oral NCA (`Rat` $t_{1/2} = 4.80\text{ h}$, `Dog` $t_{1/2} = 6.81\text{ h}$), human allometric scaling ($t_{1/2} = 8.18\text{ h}$ supporting once-daily oral dosing), and CTD Module 2.6/4 dossier export (`WO-007`, `WO-008`).
- **Evidence:** `WO-007`, `WO-008`.
- **Approvers:** Full 5-scientist human governance board + 10-agent OASE swarm.

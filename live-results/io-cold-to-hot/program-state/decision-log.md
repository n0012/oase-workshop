# Decision Log — IO Cold-to-Hot Tumor Reprogramming Campaign (`io-cold-to-hot`)

## DEC-001 (2026-10-30): Stage 1 Target Selection (`ENPP1` Selected; `TREX1` Disqualified)
- **Decision:** Advance `H-0001` (extracellular **ENPP1** catalytic pocket blockade preserving tumor-derived $2',3'\text{-cGAMP}$, Co-Scientist & Hypex Elo `1658.4`) as primary target, retain `PTPN2` (`Elo 1554.5`) as intracellular backup, and permanently disqualify `TREX1` (`Elo 1368.0`) due to human Mendelian Aicardi-Goutières syndrome autoimmunity risk (`L-001`, `PMID:16845398`).
- **Evidence:** `WO-001`, `WO-002`, `WO-003`.
- **Approvers:** Dr. Sarah Chen (`science-program-lead`), Dr. Marcus Vance (`computational-biologist`).

## DEC-002 (2026-10-30): Stage 2 Structural Druggability & Starting Matter Declaration
- **Decision:** Declare ENPP1 catalytic groove `Pocket #7` (`druggability_score = 0.694`, `volume = 535.366 Å³`) as the primary binding pocket based on live Vertex AI AlphaFold 3 co-folding (`AF3-enpp1_009_complex.cif`, `ipTM = 0.36`, `has_clash = 0.0`) and AutoDock Vina pose convergence (`-9.793 kcal/mol`), and advance the 6,7-dimethoxyquinazoline sulfonylurea series into DMTA optimization (`WO-006`).
- **Evidence:** `WO-004`, `WO-005`.
- **Approvers:** Dr. Sarah Chen (`science-program-lead`), Dr. Elena Rostova (`structural-biologist`).

## DEC-OVERRIDE-001 (2026-10-30): Stage 3 Governance Audit & Adversarial Tamper Drill Verification
- **Decision:** Executed 3 red-team adversarial tamper drills (`DRILL-01` fabricated Vina affinity mismatch, `DRILL-02` SHA-256 sidecar tamper on docked poses, `DRILL-03` suppressed mandatory relay in `WO-006`) — all 3 deterministically blocked by `oase validate check` (`exit 1`) and restored to 100% mechanical compliance (`10/10 PASS`).
- **Approvers:** Dr. Sarah Chen (`science-program-lead`), `finding-validator`, `scientific-reviewer`.

## DEC-003 (2026-10-30): Stage 3 Candidate Nomination & Wet-Lab Wall Gate (`HALTED FOR WET-LAB VALIDATION`)
- **Decision:** Nominate **`oase_enpp1_009`** (`MW = 475.5 Da`, `cLogP = 2.01`, `TPSA = 113.96 Å²`, `SA-score = 2.37`) into the Pre-Wet-Lab Candidate Dossier (`WO-008`) and **HALT computational progression at the Wet-Lab Wall** pending return of the 4 experimental CRO assays (`EXP-01` human ENPP1 cGAMP hydrolysis $\text{IC}_{50} < 10\text{ nM}$, `EXP-02` THP-1/tumor co-culture IFN-$\beta$ & CXCL10 ELISA, `EXP-03` manual patch-clamp hERG $\text{IC}_{50} > 30\text{ μM}$, and `EXP-04` syngeneic `MC38`/`CT26` + anti-PD-1 tumor growth inhibition).
- **Evidence:** `WO-006`, `WO-007`, `WO-008`.
- **Approvers:** Full 5-scientist human governance board + 10-agent OASE swarm.

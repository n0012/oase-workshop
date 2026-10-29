# Step 6 — Adversarial Governance Tamper Drills & Co-Signed Override Audit (`ch6`)

- **Campaign:** `pcsk9-oral` (`WO-001`..`WO-008` baseline intact)
- **Audit Lead:** **Dr. Sarah Chen** (*Program Lead*) & **Dr. Raj Patel** (*Medicinal Chemist*)
- **Validator Engine:** `oase validate check` (10 deterministic checks, ±1% JSONPath numeric tolerance, SHA-256 sidecar verification)

## 1. Three Deterministic Tamper Drills — ALL BLOCKED (`exit code != 0`)
| Drill ID | Simulated Failure Mode | Target Artifact | Triggered Gate | Result |
| :--- | :--- | :--- | :--- | :--- |
| **`DRILL-01`** | Unrecorded byte edit to raw docking pose file | `raw/docking/pcsk9_pocket1_vina.sdf` | `provenance_valid` (SHA-256 mismatch) | **BLOCKED** |
| **`DRILL-02`** | Hallucinated potency inflation (`-9.4` -> `-11.2 kcal/mol`) | `findings/computational-chemistry/WO-005.md` | `source_tags_resolve` (>1% JSONPath drift) | **BLOCKED** |
| **`DRILL-03`** | Omitted mandatory domain caveat (`af3.low_confidence_segments`) | `findings/structural-biology/WO-004.md` | `relay_coverage` (missing relay tag) | **BLOCKED** |

## 2. Co-Signed Human Governance Exception (`OVERRIDE-001`)
- **Requestor:** **Dr. Raj Patel** (*Medicinal Chemist*)
- **Co-Signer:** **Dr. Sarah Chen** (*Program Lead*)
- **Scope:** Retain des-CF3 backup scaffold `PCSK9-A02-desCF3` (`cLogP = 3.95`, borderline lipophilicity warning) strictly as a **secondary wet-lab backup series** pending experimental patch-clamp `hERG` counter-screening, while keeping `OASE-PCSK9-014` as the sole primary candidate.
- **Audit Trail:** Permanently recorded in `.oase/control/decisions/DEC-OVERRIDE-001.json` and `.oase/control/events.ndjson`.

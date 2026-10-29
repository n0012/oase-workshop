#!/usr/bin/env python3
"""Deterministic builder for the 8 cumulative campaign checkpoints (`ch0`..`ch7`).

Sculpts the stage-gated checkpoint directories under `checkpoints/` so every
chapter reset (`POST /api/state/chapters/{id}/reset`) restores the exact
cumulative work orders, gate sign-offs, tamper drill records, and executive
portfolio handoff artifacts for that chapter.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

STEP_01_BRIEF_MD = """# Step 1 — Pre-Mission Brief, Co-Scientist Prompt & Wingman Roster (`ch1`)

- **Campaign:** `pcsk9-oral` (Oral Small-Molecule PCSK9 Inhibitor in ASCVD)
- **Work Order Verified (`oase validate check`):** `WO-001` (`PASS`, `scientifically_accepted`)
- **Full Pod Outset Signatories:** **Dr. Sarah Chen** (`GOLD-1`), **Dr. Marcus Vance** (`GOLD-2`), **Dr. Elena Rostova** (`GOLD-3`), **Dr. Raj Patel** (`GOLD-4`), **Dr. Claire Moreau** (`GOLD-5`)

## 1. Co-Authored Co-Scientist Input Prompt & Target Product Profile (TPP)
| Prompt Clause | Functional Author | Locked Threshold / Kill Criterion in `.oase/thresholds.yaml` |
| :--- | :--- | :--- |
| **Clause 1 — Human Genetics & Liver Selectivity** | Dr. Marcus Vance (*Comp Bio*) | Require human LoF cardioprotection (`PCSK9 R46L` / `gnomAD pLI < 0.90`), `GTEx >= 100 TPM` liver expression, and 1P `AlphaGenome` `1 Mb` regulatory polarity |
| **Clause 2 — Allosteric Groove & `FP-001` Kill Switch** | Dr. Elena Rostova (*Structural Bio*) | Require 1P `AlphaFold 3` co-fold `ipTM >= 0.70` and `fpocket` druggability `>= 0.50` (`KILL` small molecule if `< 0.30`); retain macrocycle comparator `FP-002` |
| **Clause 3 — Unenhanced Oral Ro5 & Cardiac `hERG` Gate** | Dr. Raj Patel (*Med Chem*) & Dr. Claire Moreau (*DMPK*) | Require `cLogP <= 3.5`, `MW <= 500 Da`, `0` critical Aronov `hERG` / PAINS alerts, no dietary permeation enhancers, and a mandatory CRO wet-lab pause prior to human PK |

## 2. 24-Match Co-Scientist Tournament Outcome & Dynamic Subway Map Routing (`WO-001`)
- **Primary Green Line (`IC-001`, `1642.5 Elo`, `10W-2L`):** Cryptic inter-domain groove small molecule (`+54.5 Elo` over `#2`) advances into Stage 1 Genetics & `AlphaGenome`, carrying mandatory relay `hypothesis.adopted_not_generated`.
- **Parked Amber Backup Line (`IC-002`, `1588.0 Elo`, `8W-4L`):** Oral tricyclic macrocycle parked on standby in case `FP-001` pocket collapse fires at Gate 2 or `hERG`/PK blocks the small molecule at Gates 3–4.

## 3. Assigned Doctor <-> AI Wingman Mission Pairings
| Mission Leg | Human Lead (Doctor) | Paired AI Counterpart(s) in Scion Grove | Assigned Work Orders & Stage Gates |
| :--- | :--- | :--- | :--- |
| **Mission Command & Governance** | Dr. Sarah Chen (`GOLD-1`) | `Grove-1` (`@science-program-lead`) · `Aegis-6` (`@finding-validator`) · `@scientific-reviewer` | `WO-001` audit, Stage Gates `1–4` co-signatures, Step 6 red-team tamper drills, Step 7 closeout |
| **Stage 1 — Genetics & `AlphaGenome`** | Dr. Marcus Vance (`GOLD-2`) | `Helix-2` (`@computational-biologist`) | `WO-002`–`WO-003` (`gnomAD`, `OpenTargets`, `GTEx`, 1P `AlphaGenome`) -> **Gate 1** |
| **Stage 2 — `AlphaFold 3` & Docking** | Dr. Elena Rostova (`GOLD-3`) | `Fold-3` (`@structural-biologist`) · `@computational-chemist` | `WO-004`–`WO-005` (1P `AlphaFold 3` co-fold, `fpocket`, `AutoDock Vina`) -> **Gate 2** |
| **Stage 3 — Med Chem DMTA** | Dr. Raj Patel (`GOLD-4`) | `Spark-4` (`@medicinal-chemist`) | `WO-006` (`RDKit`, `BRICS` oxadiazole reroute `PCSK9-A02 -> OASE-PCSK9-014`, `ASKCOS`) -> **Gate 3** |
| **Stage 3–4 — `ADMET`, CRO & `PK`** | Dr. Claire Moreau (`GOLD-5`) | `Shield-5` (`@admet-dmpk-scientist`) · `@project-curator` | `WO-006`–`WO-008` (Aronov `hERG` takedown, `⏸` CRO wet-lab bridge, `40 mg QD` human PK, IND dossier) -> **Gate 4** |
"""

GATE_01_MD = """# Stage Gate 1 — Target Validation & Human Genetics (`ch2`)

- **Campaign:** `pcsk9-oral` (Oral Small-Molecule PCSK9 Inhibitor)
- **Work Orders Verified (`oase validate check`):** `WO-001`, `WO-002`, `WO-003` (`3/3 PASS`)
- **Domain Presenter:** **Dr. Marcus Vance** (*Computational Biologist*)
- **Stage-Gate Approver:** **Dr. Sarah Chen** (*Program Lead*)
- **Gate Verdict:** **APPROVED — ADVANCE TO STAGE 2 STRUCTURAL BIOLOGY**

## Evidence Summary
1. **Co-Scientist Seed (`WO-001`):** Allosteric groove small-molecule hypothesis `IC-001` leads 24-match tournament (`Elo = 1642.5` vs flat EGF-A PPI macrocycle `IC-002` `Elo = 1588.0`). Relay preserved: `hypothesis.adopted_not_generated`.
2. **Human Genetics (`WO-002`):** `gnomAD` confirms loss-of-function tolerance (`pLI = 0.0001`, `LOEUF = 0.87`, `LOF_TOLERANT`) alongside `OpenTargets` familial hypercholesterolemia association (`0.96` seeded / `0.86` live). Relay preserved: `gnomad.constraint_is_not_safety`.
3. **Hepatocyte Expression & Regulatory Directionality (`WO-003`):** Liver-dominant expression (`GTEx` `184.2 TPM`) and concordant `AlphaGenome` hepatocyte regulatory variant `rs2479409` (`chr1:55039974:G>T`, `quantile = 0.984`, `LFC = -0.24`). Relay preserved: `alphagenome.regulatory_prediction_is_in_silico`.
"""

GATE_02_MD = """# Stage Gate 2 — Structural Biology, Cryptic Pocket & Docking (`ch3`)

- **Campaign:** `pcsk9-oral` (Oral Small-Molecule PCSK9 Inhibitor)
- **Work Orders Verified (`oase validate check`):** `WO-001`..`WO-005` (`5/5 PASS`)
- **Domain Presenter:** **Dr. Elena Rostova** (*Structural Biologist*)
- **Stage-Gate Approver:** **Dr. Sarah Chen** (*Program Lead*)
- **Gate Verdict:** **APPROVED — ADVANCE TO STAGE 3 DMTA MEDICINAL CHEMISTRY**

## Evidence Summary
1. **Co-Fold & Pocket Druggability (`WO-004`):** `AlphaFold 3` ligand co-fold on `PCSK9` (`Q8NBP7`) reaches `ipTM = 0.84` (`pTM = 0.88`), and `fpocket` confirms inter-domain allosteric groove `Pocket #1` (`druggability = 0.68`) outperforms flat `EGF-A` PPI surface (`0.24`). Relay preserved: `af3.low_confidence_segments`.
2. **Structure-Based Virtual Screening (`WO-005`):** `AutoDock Vina 1.2.5` ranks initial hit `pcsk9_analog_02` / `PCSK9-A02` at `-9.4 kcal/mol` with zero steric clashes, while flagging lipophilicity/hERG liability `L-002` for Stage 3 MMP replacement. Relay preserved: `docking.score_is_not_affinity`.
"""

GATE_03_MD = """# Stage Gate 3 & Future-State Wet-Lab / CRO Handoff Slot (`ch4`)

- **Campaign:** `pcsk9-oral` (Oral Small-Molecule PCSK9 Inhibitor)
- **Work Orders Verified (`oase validate check`):** `WO-001`..`WO-006` (`6/6 PASS`)
- **Domain Co-Presenters:** **Dr. Raj Patel** (*Medicinal Chemist*) & **Dr. Claire Moreau** (*DMPK & Safety Lead*)
- **Stage-Gate Approver:** **Dr. Sarah Chen** (*Program Lead*)
- **Gate Verdict:** **PCSK9-A02 DISQUALIFIED (hERG ALERT) · OASE-PCSK9-014 (PCSK9-A03) NOMINATED FOR WET-LAB ASSAY HANDOFF**

## 1. In Silico DMTA & Safety Gate (`WO-006`)
- **Disqualified Hit (`PCSK9-A02`):** Despite leading Vina docking (`-9.4 kcal/mol`), the CF3-thiazole hit fails `admet-endpoints@1.0` with `cLogP = 5.09` and 3 critical alerts including the Aronov 2005 `herg_liability` pharmacophore flag.
- **Selected Lead (`OASE-PCSK9-014` / `PCSK9-A03`):** Matched molecular pair bioisosteric replacement (`CF3-thiazole` -> polar `F,CN-oxadiazole` / `2-methoxypyrimidine` series) lowers `cLogP` to `3.01`–`3.1`, raises `LipE` to `5.2`, eliminates all critical alerts (`0` flags), and preserves groove complementarity. Relay preserved: `admet.herg_structural_flag`.

## 2. Explicit Wet-Lab / CRO Experimental Handoff Slot (Future-State Integration Point)
> **Architectural Note:** In a live pharmaceutical R&D deployment, `OASE` pauses campaign progression here and dispatches structured Wet-Lab Work Orders (`LIMS` / `Benchling` / CRO synthesis + assay queue) before unlocking Stage 4 human clinical PK projection:
> - **Synthesis & Orthogonal Binding (`CRO-SYN-014`):** 50 mg resynthesis of `OASE-PCSK9-014` + surface plasmon resonance (`SPR Kd`) and `HepG2` LDL-uptake EC50 confirmation.
> - **Experimental Safety Counter-Screen (`CRO-SAFE-014`):** Manual automated patch-clamp `hERG IC50` (`target > 30 uM`) confirming resolution of the structural alert.
> - **In Vivo Preclinical PK (`CRO-PK-014`):** Male Sprague-Dawley rat & beagle dog IV/PO crossover PK (`CL`, `Vdss`, `%F`) feeding Stage 4 human allometric scaling (`WO-007`).
"""

GATE_04_MD = """# Stage Gate 4 — Translational Human Oral PK & Preclinical Candidate Nomination (`ch5`)

- **Campaign:** `pcsk9-oral` (Oral Small-Molecule PCSK9 Inhibitor)
- **Work Orders Verified (`oase validate check`):** `WO-001`..`WO-008` (`8/8 PASS`)
- **Domain Presenter:** **Dr. Claire Moreau** (*DMPK & Safety Lead*)
- **Stage-Gate Approver:** **Dr. Sarah Chen** (*Program Lead*)
- **Gate Verdict:** **APPROVED — PRECLINICAL DEVELOPMENT CANDIDATE `OASE-PCSK9-014` NOMINATED (`40 mg QD` ORAL)**

## Evidence Summary
1. **Human Oral PK Scaling (`WO-007`):** 1-compartment oral PK projection confirms `F = 52.0%` oral bioavailability, `t1/2 = 14.8 h` effective half-life, and `88%` trough target coverage at a convenient **`40.0 mg QD`** human oral regimen. Relay preserved: `pk.allometry_uncertainty`.
2. **Candidate Nomination Dossier (`WO-008`):** Full 30-page static Evidence Portal compiled and mechanically audited across all 10 `oase validate check` governance rules (`0` unresolved citations, `100%` SHA-256 provenance integrity, `36/36` versioned threshold schemas attributed).
"""

EXEC_SUMMARY_MD = """# Preclinical Candidate Nomination Summary — `OASE-PCSK9-014`

- **Target:** Human `PCSK9` (`UniProt Q8NBP7`) Inter-Domain Allosteric Groove (`Pocket #1`)
- **Nominated Candidate:** `OASE-PCSK9-014` (`PCSK9-A03` Polar Oxadiazole / Methoxypyrimidine Lead)
- **Projected Human Regimen:** **`40.0 mg QD` Oral Tablet** (`F = 52.0%`, `t1/2 = 14.8 h`)
- **Governance Status:** `8 / 8` Work Orders (`WO-001`..`WO-008`) Mechanically Verified via `oase validate check`
- **Discovery Pod Sign-Off:** Dr. Sarah Chen (*Program Lead*), Dr. Marcus Vance (*Comp Bio*), Dr. Elena Rostova (*Struct Bio*), Dr. Raj Patel (*Med Chem*), Dr. Claire Moreau (*DMPK & Safety*)
"""

STEP_06_AUDIT_MD = """# Step 6 — Adversarial Governance Tamper Drills & Co-Signed Override Audit (`ch6`)

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
- **Scope:** Retain backup scaffold `PCSK9-B07` (`PCSK9-A02-desCF3`, `cLogP = 3.95`, borderline lipophilicity warning) strictly as a **secondary wet-lab backup series** pending experimental patch-clamp `hERG` counter-screening, while keeping `OASE-PCSK9-014` as the sole primary candidate.
- **Audit Trail:** Permanently recorded in `.oase/control/decisions/DEC-OVERRIDE-001.json` and `.oase/control/events.ndjson`.
"""

STEP_07_CLOSEOUT_MD = """# Step 7 — Post-Mission Debrief, Subway Map Recap & Portfolio Sign-Off (`ch7`)

- **Campaign:** `pcsk9-oral` (`WO-001`..`WO-008` verified, `GATE-01`..`GATE-04` signed, `STEP-06` audit complete)
- **Full Pod Debrief Signatories:** **Dr. Sarah Chen** (`GOLD-1`), **Dr. Marcus Vance** (`GOLD-2`), **Dr. Elena Rostova** (`GOLD-3`), **Dr. Raj Patel** (`GOLD-4`), **Dr. Claire Moreau** (`GOLD-5`) + **`Grove-1`** (`@science-program-lead`)
- **Nominated Clinical Candidate:** **`OASE-PCSK9-014`** (`40.0 mg QD` conventional oral tablet, `F = 52.0%`, `t1/2 = 14.8 h`, `0` hERG/PAINS alerts)

## 1. Pair-by-Pair Post-Mission Debrief Against the Step 1 Pre-Mission Brief
| Doctor <-> AI Wingman Pair | Mission Leg (`Work Orders`) | What the Pair Proved & Dynamic Subway Map Action | Status |
| :--- | :--- | :--- | :--- |
| **Sarah (`GOLD-1`) + `Grove-1` / `Aegis-6`** | Stage 0 & Governance (`WO-001`, `STEP-06`, `STEP-07`) | Co-authored Co-Scientist prompt; ranked `IC-001` (`1642.5 Elo`) #1; blocked `3 / 3` tamper drills; logged `1` co-signed override (`DEC-OVERRIDE-001`) | **CO-SIGNED** |
| **Marcus (`GOLD-2`) + `Helix-2`** | Stage 1 Genetics & 1P `AlphaGenome` (`WO-002..003`) | Confirmed human LoF tolerance (`pLI = 0.0001`), liver enrichment (`184.2 TPM`), and `AlphaGenome` hepatocyte score (`0.984`) before chemistry spend | **GATE 1 PASS** |
| **Elena (`GOLD-3`) + `Fold-3`** | Stage 2 1P `AlphaFold 3` & Docking (`WO-004..005`) | Validated cryptic Pocket #1 (`ipTM = 0.84`, `fpocket = 0.68`) and terminated flat `EGF-A` spur (`0.24`); flagged `L-002` lipophilicity risk | **GATE 2 PASS** |
| **Raj (`GOLD-4`) + `Spark-4`** | Stage 3 Med-Chem DMTA Reroute (`WO-006`) | Caught `PCSK9-A02` Aronov `hERG` red signal (`cLogP = 5.09`), rerouted via `BRICS` loop to `OASE-PCSK9-014` (`cLogP = 3.01`, `0` alerts), parked backup `PCSK9-B07` | **GATE 3 PASS** |
| **Claire (`GOLD-5`) + `Shield-5`** | `⏸` CRO Wet-Lab Gate & Oral PK (`WO-006..008`) | Paused campaign for experimental SPR, patch-clamp `hERG > 30 uM`, and rat (`54%`) / dog (`61%`) PK -> locked **`40.0 mg QD`** unenhanced human tablet | **GATE 4 APPROVED** |

## 2. Portfolio Handoff Deliverable
- 30-page static HTML Evidence Portal (`_site/index.html` + `_site/chapters.html`) and `executive/PORTFOLIO-HANDOFF.md` verified with `0` ungrounded claims (`28/28` JSONPath citations within `±1%`, `36/36` thresholds attributed).
"""

PORTFOLIO_HANDOFF_MD = """# Executive Portfolio Handoff Package — `OASE-PCSK9-014` (`ch7`)

- **Program:** Oral Small-Molecule PCSK9 Allosteric PPI Inhibitor (`pcsk9-oral`)
- **Primary Candidate:** `OASE-PCSK9-014` (`40.0 mg` once-daily oral tablet)
- **Secondary Exploratory Backup:** `PCSK9-B07` (`PCSK9-A02-desCF3`, governed under co-signed `DEC-OVERRIDE-001`)
- **Provenance & Validation:** `8 / 8` Work Orders (`WO-001`..`WO-008`), `28 / 28` JSONPath scalar citations (`<= 1%` tolerance), `36 / 36` organization thresholds resolved, `3 / 3` tamper drills blocked
- **Published Evidence Portal:** 30 provenance-linked HTML pages ready for portfolio committee review and GLP toxicology initiation
"""


def build_all_checkpoints(cp: Path) -> None:
    src_full = cp / "_tmp_full_stage4"
    if src_full.exists():
        shutil.rmtree(src_full)

    base_full_dir = cp / "ch5" if (cp / "ch5" / "findings" / "regulatory" / "WO-008.md").exists() else cp / "ch4"
    shutil.copytree(base_full_dir, src_full)

    (cp / "ch1" / "gates").mkdir(parents=True, exist_ok=True)
    (cp / "ch1" / "gates" / "STEP-01-pre-mission-brief.md").write_text(STEP_01_BRIEF_MD)

    (cp / "ch2" / "gates").mkdir(parents=True, exist_ok=True)
    (cp / "ch2" / "gates" / "STEP-01-pre-mission-brief.md").write_text(STEP_01_BRIEF_MD)
    (cp / "ch2" / "gates" / "GATE-01-target-validation.md").write_text(GATE_01_MD)

    (cp / "ch3" / "gates").mkdir(parents=True, exist_ok=True)
    (cp / "ch3" / "gates" / "STEP-01-pre-mission-brief.md").write_text(STEP_01_BRIEF_MD)
    (cp / "ch3" / "gates" / "GATE-01-target-validation.md").write_text(GATE_01_MD)
    (cp / "ch3" / "gates" / "GATE-02-structure-docking.md").write_text(GATE_02_MD)

    if (cp / "ch4").exists():
        shutil.rmtree(cp / "ch4")
    shutil.copytree(src_full, cp / "ch4")
    for rel in [
        "findings/admet-dmpk",
        "findings/regulatory",
        "raw/pk",
        "raw/pipeline",
        ".oase/control/work-orders/WO-007.json",
        ".oase/control/work-orders/WO-008.json",
        ".oase/control/validations/VAL-WO-007.json",
        ".oase/control/validations/VAL-WO-008.json",
    ]:
        p = cp / "ch4" / rel
        if p.is_dir():
            shutil.rmtree(p)
        elif p.exists():
            p.unlink()

    ev_path = cp / "ch4" / ".oase" / "control" / "events.ndjson"
    ev_lines = [
        ln for ln in ev_path.read_text().splitlines()
        if ln.strip() and '"WO-007"' not in ln and '"WO-008"' not in ln
    ]
    ev_path.write_text("\n".join(ev_lines) + "\n")

    (cp / "ch4" / "gates").mkdir(parents=True, exist_ok=True)
    (cp / "ch4" / "gates" / "STEP-01-pre-mission-brief.md").write_text(STEP_01_BRIEF_MD)
    (cp / "ch4" / "gates" / "GATE-01-target-validation.md").write_text(GATE_01_MD)
    (cp / "ch4" / "gates" / "GATE-02-structure-docking.md").write_text(GATE_02_MD)
    (cp / "ch4" / "gates" / "GATE-03-wetlab-handoff.md").write_text(GATE_03_MD)

    if (cp / "ch5").exists():
        shutil.rmtree(cp / "ch5")
    shutil.copytree(src_full, cp / "ch5")
    for md_file in (cp / "ch5" / "program-state").glob("*.md"):
        md_file.write_text(md_file.read_text().replace("(Checkpoint `ch4`)", "(Checkpoint `ch5`)"))
    (cp / "ch5" / "gates").mkdir(parents=True, exist_ok=True)
    (cp / "ch5" / "gates" / "STEP-01-pre-mission-brief.md").write_text(STEP_01_BRIEF_MD)
    (cp / "ch5" / "gates" / "GATE-01-target-validation.md").write_text(GATE_01_MD)
    (cp / "ch5" / "gates" / "GATE-02-structure-docking.md").write_text(GATE_02_MD)
    (cp / "ch5" / "gates" / "GATE-03-wetlab-handoff.md").write_text(GATE_03_MD)
    (cp / "ch5" / "gates" / "GATE-04-candidate-nomination.md").write_text(GATE_04_MD)
    (cp / "ch5" / "executive").mkdir(parents=True, exist_ok=True)
    (cp / "ch5" / "executive" / "CANDIDATE-SUMMARY.md").write_text(EXEC_SUMMARY_MD)

    if (cp / "ch6").exists():
        shutil.rmtree(cp / "ch6")
    shutil.copytree(cp / "ch5", cp / "ch6")
    for md_file in (cp / "ch6" / "program-state").glob("*.md"):
        md_file.write_text(md_file.read_text().replace("(Checkpoint `ch5`)", "(Checkpoint `ch6`)"))

    drills = [
        (
            "DRILL-01-provenance-tamper.json",
            {
                "drill_id": "DRILL-01",
                "work_order": "WO-005",
                "mutation": "Appended unrecorded trailing whitespace byte to raw/docking/pcsk9_pocket1_vina.sdf without regenerating Phase-1 sidecar",
                "command": "oase validate check --dry-run WO-005",
                "exit_code": 1,
                "failed_check": "provenance_valid",
                "verdict": "BLOCKED",
                "message": "SHA-256 digest mismatch between raw/docking/pcsk9_pocket1_vina.sdf on disk and pcsk9_pocket1_vina.meta.json",
            },
        ),
        (
            "DRILL-02-jsonpath-inflation.json",
            {
                "drill_id": "DRILL-02",
                "work_order": "WO-005",
                "mutation": "Inflated cited Vina binding score in findings/computational-chemistry/WO-005.md from -9.4 to -11.2 kcal/mol",
                "command": "oase validate check --dry-run WO-005",
                "exit_code": 1,
                "failed_check": "source_tags_resolve",
                "verdict": "BLOCKED",
                "message": "Numeric citation -11.2 exceeds +/-1.0% relative tolerance against raw/docking/pcsk9_pocket1_vina.analysis.json (-9.4)",
            },
        ),
        (
            "DRILL-03-missing-caveat-relay.json",
            {
                "drill_id": "DRILL-03",
                "work_order": "WO-004",
                "mutation": "Deleted mandatory epistemic caveat relay **Relay: `af3.low_confidence_segments`** from findings/structural-biology/WO-004.md",
                "command": "oase validate check --dry-run WO-004",
                "exit_code": 1,
                "failed_check": "relay_coverage",
                "verdict": "BLOCKED",
                "message": "Required caveat relay 'af3.low_confidence_segments' from pcsk9_ic001_af3_ligand_summary.analysis.json missing in synthesis markdown",
            },
        ),
    ]
    for fname, payload in drills:
        (cp / "ch6" / "gates" / fname).write_text(json.dumps(payload, indent=2) + "\n")

    override_payload = {
        "override_id": "OVERRIDE-001",
        "decision_id": "DEC-OVERRIDE-001",
        "timestamp": "2026-10-28T23:55:00Z",
        "work_order": "WO-006",
        "command": "oase workorder override WO-006 --series PCSK9-B07 --reason 'Exploratory backup scaffold retained for manual patch-clamp hERG counter-screen only'",
        "requested_by": {"name": "Dr. Raj Patel", "role": "Medicinal Chemist", "account_slug": "oase-raj"},
        "co_signed_by": {"name": "Dr. Sarah Chen", "role": "Program Lead", "account_slug": "oase-sarah"},
        "primary_candidate_unchanged": "OASE-PCSK9-014",
        "override_scope": "secondary_exploratory_backup_only",
        "rationale": "Retains backup analog PCSK9-B07 (PCSK9-A02-desCF3, cLogP = 3.95) in secondary CRO patch-clamp counter-screen queue to preserve scaffold diversity while OASE-PCSK9-014 advances as sole primary candidate.",
        "audit_status": "CO_SIGNED_AND_LOGGED",
    }
    (cp / "ch6" / "gates" / "OVERRIDE-001-backup-series.json").write_text(json.dumps(override_payload, indent=2) + "\n")
    (cp / "ch6" / "gates" / "STEP-06-governance-audit.md").write_text(STEP_06_AUDIT_MD)
    (cp / "ch6" / ".oase" / "control" / "decisions" / "DEC-OVERRIDE-001.json").write_text(
        json.dumps(override_payload, indent=2) + "\n"
    )

    if (cp / "ch7").exists():
        shutil.rmtree(cp / "ch7")
    shutil.copytree(cp / "ch6", cp / "ch7")
    for md_file in (cp / "ch7" / "program-state").glob("*.md"):
        md_file.write_text(md_file.read_text().replace("(Checkpoint `ch6`)", "(Checkpoint `ch7`)"))
    (cp / "ch7" / "gates" / "STEP-07-portfolio-closeout.md").write_text(STEP_07_CLOSEOUT_MD)
    (cp / "ch7" / "executive" / "PORTFOLIO-HANDOFF.md").write_text(PORTFOLIO_HANDOFF_MD)

    shutil.rmtree(src_full)
    print(f"[ok] Built all 8 checkpoints in {cp}: ch0, ch1, ch2, ch3, ch4, ch5, ch6, ch7")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--checkpoints-dir",
        type=Path,
        default=REPO_ROOT / "checkpoints",
        help="Path to checkpoints/ directory (default: <repo>/checkpoints).",
    )
    args = parser.parse_args()
    build_all_checkpoints(args.checkpoints_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Provision and seed the 8-Checkpoint OASE Team Discovery Pilot on Scion Hub.

Creates 8 parallel Scion Hub projects (ch0..ch7), binds the 5 dedicated
workshop scientist accounts (zero admin@ presence), shares the prebuilt OASE
v0.3.0 scientific toolchain, initializes Git checkpoint tags (ch0..ch7) in
each Grove workspace, publishes chapter-scoped artifacts, and launches live
specialist agent containers ready for multi-human Webchat collaboration.

Usage:
  python3 scripts/seed-pilot-chapters.py \
    --gcp-project "$GCP_PROJECT_ID" \
    --workshop-domain "$WORKSHOP_DOMAIN"
"""

from __future__ import annotations

import argparse
import base64
import datetime
import hashlib
import hmac
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

ROLE_PROJECT_OWNER = "a2855400-38a5-4b2d-9f02-3c505aec71ed"
ROLE_PROJECT_ADMIN = "277a804d-cad4-4065-97d4-1b64a9942b74"
ROLE_SUPER_ADMIN = "e0596b8d-df67-4913-a4c4-c61899a14798"

PERSONAS = [
    ("sarah", "Dr. Sarah Chen (Program Lead)", "admin", ROLE_PROJECT_OWNER),
    ("marcus", "Dr. Marcus Vance (Comp Bio)", "member", ROLE_PROJECT_ADMIN),
    ("elena", "Dr. Elena Rostova (Structural Bio)", "member", ROLE_PROJECT_ADMIN),
    ("raj", "Dr. Raj Patel (Med Chem)", "member", ROLE_PROJECT_ADMIN),
    ("claire", "Dr. Claire Moreau (DMPK & Safety)", "member", ROLE_PROJECT_ADMIN),
]

ALL_11_GROVE_AGENTS = [
    ("science-program-lead", "science-program-lead", "Program Lead & Multi-Stage Grove Coordinator"),
    ("computational-biologist", "computational-biologist", "Human Genetics, OpenTargets, GTEx & AlphaGenome"),
    ("structural-biologist", "structural-biologist", "AlphaFold 3 Co-Folding & fpocket Druggability"),
    ("computational-chemist", "computational-chemist", "3-Phase AutoDock Vina Pose & Contact Scoring"),
    ("medicinal-chemist", "medicinal-chemist", "Matched Molecular Pair SAR & Retrosynthesis"),
    ("admet-dmpk-scientist", "admet-dmpk-scientist", "ADMET Liability Gate, Wet-Lab PK Bridge & Human QD Dose"),
    ("scientific-reviewer", "scientific-reviewer", "Independent Two-Phase Scientific Peer Reviewer"),
    ("finding-validator", "finding-validator", "Deterministic CLI Provenance & Threshold Validator"),
    ("project-curator", "project-curator", "Stage-Gate Dossier & Evidence Portal Publisher"),
    ("controller", "research-operations-controller", "Work Order State Machine & Queue Controller"),
    ("hypex-supervisor", "hypex-supervisor", "Co-Scientist Pairwise Elo Tournament Supervisor"),
]

CHAPTER_SPECS = [
    {
        "chapter": "ch0",
        "slug": "00-pcsk9-initial-seed",
        "name": "00-pcsk9-initial-seed",
        "description": "Initial Seed (t=0) — Pre-Campaign Seed Staged (0 Work Orders closed; ready for live Step 1 kickoff)",
        "lead_human": "sarah",
        "live_agents": ["science-program-lead", "computational-biologist"],
        "artifact_keys": [],
        "topic_slug": "step-0-campaign-charter",
        "topic_agent": "science-program-lead",
        "seed_messages": [
            (
                "human:sarah",
                "**[Campaign Charter Staged — `t=0` Initial Seed (`pcsk9-oral`)]**\n"
                "Team: `seed/pcsk9-oral/campaign-seed.json` and `CHECKSUMS.json` are staged in `/workspace` (`0` Work Orders closed).\n"
                "- **Target**: Human **PCSK9** (`ENSG00000169174` / `Q8NBP7`) oral small-molecule PPI inhibitor (`<= 100 mg QD`, clean cardiac hERG safety).\n"
                "- `@science-program-lead` and `@computational-biologist` are online and standing by to launch **Step 1 (`WO-001` Co-Scientist Elo Tournament Validation)**.",
                [],
                True,
            ),
        ],
    },
    {
        "chapter": "ch1",
        "slug": "01-pcsk9-coscientist",
        "name": "01-pcsk9-coscientist",
        "description": "Step 1 — Pre-Mission Brief, Co-Scientist Prompt & Wingman Roster (WO-001: IC-001 Elo 1642.5)",
        "lead_human": "sarah",
        "live_agents": ["science-program-lead", "computational-biologist"],
        "artifact_keys": ["wo-001-finding", "pcsk9-evidence-portal"],
        "topic_slug": "step-1-coscientist-elo-ranking",
        "topic_agent": "computational-biologist",
        "seed_messages": [
            (
                "human:sarah",
                "**[Step 1 Pre-Mission Brief — Co-Scientist Prompt & Wingman Roster (`WO-001`)]**\n"
                "`@science-program-lead` `@computational-biologist` — All 5 scientists have co-authored our Co-Scientist Research Brief & TPP in `gates/STEP-01-pre-mission-brief.md` (LoF + `AlphaGenome` liver selectivity, `AlphaFold 3` + `FP-001` pocket kill rule, unenhanced Rule-of-5 + `0` hERG alerts). Verify our 24-match Stage 0 tournament (`IC-001` vs `IC-002`) and 5 Doctor-to-AI Wingman pairings.",
                ["wo-001-finding"],
                False,
            ),
            (
                "agent:science-program-lead",
                "**[Pre-Mission Brief Locked & `WO-001` Verified — `IC-001` Ranked #1 (`Elo = 1642.5`)]**\n"
                "Verified `gates/STEP-01-pre-mission-brief.md`, `.oase/thresholds.yaml` (`36/36` schemas), and all 24 Co-Scientist matches:\n"
                "- **Primary Green Line (`IC-001`)**: Cryptic EGF-A Groove Small Molecule (`Asp374`/`Phe379`/`Ser381`) — **`Elo = 1642.5`** (`+54.5 Elo`)\n"
                "- **Amber Backup Line (`IC-002`)**: Oral Tricyclic Macrocycle — **`Elo = 1588.0`** (parked behind CRO wet-lab gate)\n"
                "- **5 Doctor <-> AI Wingman Pairs Locked**: `Sarah + Grove-1`, `Marcus + Helix-2`, `Elena + Fold-3`, `Raj + Spark-4`, `Claire + Shield-5` (plus `Aegis-6` audit).",
                ["wo-001-finding", "pcsk9-evidence-portal"],
                True,
            ),
        ],
    },
    {
        "chapter": "ch2",
        "slug": "02-pcsk9-genetics-gate1",
        "name": "02-pcsk9-genetics-gate1",
        "description": "Step 2 + Gate 1 — Human LoF Genetics, GTEx Liver Selectivity (184.2 TPM) & AlphaGenome (WO-001..003)",
        "lead_human": "marcus",
        "live_agents": ["science-program-lead", "computational-biologist"],
        "artifact_keys": ["wo-001-finding", "wo-002-finding", "wo-003-finding", "decision-log", "pcsk9-evidence-portal"],
        "topic_slug": "step-2-genetics-alphagenome-gate1",
        "topic_agent": "computational-biologist",
        "seed_messages": [
            (
                "human:marcus",
                "**[Chapter 2 Review — Human Genetics, GTEx & AlphaGenome (`WO-002`, `WO-003`)]**\n"
                "`@computational-biologist` — Before `Dr. Sarah Chen` and I co-sign **Stage Gate 1 (Target Validation)**, summarize the human LoF protective odds ratio, hepatic expression selectivity, and AlphaGenome regulatory variant score.",
                ["wo-002-finding", "wo-003-finding"],
                False,
            ),
            (
                "agent:computational-biologist",
                "**[Stage Gate 1 Evidence Package Ready — `WO-002` & `WO-003` Accepted]**\n"
                "1. **Human LoF Cardioprotection (`WO-002`)**: OpenTargets (`0.89`) + gnomAD v4 confirm `R46L` (`rs11591147`, `OR = 0.40`), `Y142X` & `C679X` (`-40%` LDL-C, `-88%` CHD risk) with healthy homozygotes.\n"
                "2. **Hepatic Selectivity (`WO-002`)**: GTEx v8 liver expression = **`184.2 TPM`** (`>74%` liver-restricted vs `<5 TPM` extrahepatic).\n"
                "3. **AlphaGenome 1 Mb Scoring (`WO-003`)**: Regulatory variant `rs2479409` hepatocyte quantile = **`0.984`** (`PASS`).\n"
                "- **Gate 1 Status**: Recorded in `gates/GATE-01-target-validation.md` (`ADVANCE` to Step 3 Structural Biology).",
                ["wo-002-finding", "wo-003-finding", "decision-log"],
                True,
            ),
        ],
    },
    {
        "chapter": "ch3",
        "slug": "03-pcsk9-structure-gate2",
        "name": "03-pcsk9-structure-gate2",
        "description": "Step 3 + Gate 2 — AlphaFold 3 Co-Fold (ipTM 0.84), fpocket Groove (0.68) & Vina (-9.4 kcal/mol) (WO-001..005)",
        "lead_human": "elena",
        "live_agents": ["science-program-lead", "structural-biologist"],
        "artifact_keys": [
            "wo-001-finding",
            "wo-002-finding",
            "wo-003-finding",
            "wo-004-finding",
            "wo-005-finding",
            "decision-log",
            "pcsk9-evidence-portal",
        ],
        "topic_slug": "step-3-af3-pockets-vina-gate2",
        "topic_agent": "structural-biologist",
        "seed_messages": [
            (
                "human:elena",
                "**[Chapter 3 Structural Audit — AlphaFold 3, `fpocket` & AutoDock Vina (`WO-004`, `WO-005`)]**\n"
                "`@structural-biologist` — Let's verify the Pocket #1 druggability contrast against the flat EGF-A surface and confirm orthogonal Vina redocking agreement before signing **Stage Gate 2**.",
                ["wo-004-finding", "wo-005-finding"],
                False,
            ),
            (
                "agent:structural-biologist",
                "**[Stage Gate 2 Structural Package Verified — `WO-004` & `WO-005` Accepted]**\n"
                "- **AlphaFold 3 Co-Fold (`WO-004`)**: `ipTM = 0.84`, pocket `pLDDT = 91.4`, interface PAE `3.1 A`.\n"
                "- **Cryptic Groove Druggability (`fpocket`)**: **Pocket #1 = `0.68`** (cryptic catalytic/EGF-A groove) vs **`0.24`** on the flat exposed surface.\n"
                "- **3-Phase AutoDock Vina (`WO-005`)**: **`dG = -9.4 kcal/mol`**, key `Asp374`/`Phe379`/`Ser381` contact distance = **`2.34 A`** (`PASS <= 3.5 A`).\n"
                "- **Gate 2 Status**: Signed in `gates/GATE-02-structure-docking.md` (`ADVANCE` `IC-001` scaffold to Step 4 MedChem & ADMET).",
                ["wo-004-finding", "wo-005-finding", "pcsk9-evidence-portal"],
                True,
            ),
        ],
    },
    {
        "chapter": "ch4",
        "slug": "04-pcsk9-admet-wetlab-gate3",
        "name": "04-pcsk9-admet-wetlab-gate3",
        "description": "Step 4 + Gate 3 + Wet-Lab Handoff Slot — PCSK9-A02 Disqualified on hERG; OASE-PCSK9-014 Queued for CRO Assays (WO-001..006)",
        "lead_human": "raj",
        "live_agents": ["science-program-lead", "medicinal-chemist", "admet-dmpk-scientist"],
        "artifact_keys": [
            "wo-001-finding",
            "wo-002-finding",
            "wo-003-finding",
            "wo-004-finding",
            "wo-005-finding",
            "wo-006-finding",
            "liability-tracker",
            "active-series",
            "decision-log",
            "pcsk9-evidence-portal",
        ],
        "topic_slug": "step-4-herg-gate3-wetlab-handoff",
        "topic_agent": "medicinal-chemist",
        "seed_messages": [
            (
                "human:claire",
                "**[Chapter 4 Safety Gate — Aronov hERG Disqualification & Wet-Lab Handoff (`WO-006`)]**\n"
                "`@admet-dmpk-scientist` `@medicinal-chemist` — `PCSK9-A02` (`cLogP = 5.09`, basic amine) triggered our cardiac hERG gate. Confirm its formal disqualification and verify that polar analog **`OASE-PCSK9-014` (`PCSK9-A03`)** is staged at the **Future-State Wet-Lab / CRO Assay Handoff** prior to Step 5 oral PK.",
                ["liability-tracker", "wo-006-finding"],
                False,
            ),
            (
                "agent:medicinal-chemist",
                "**[Stage Gate 3 + Explicit Wet-Lab Handoff Staged — `WO-006` Accepted]**\n"
                "- **Disqualified**: `PCSK9-A02` (`cLogP = 5.09`, predicted `hERG IC50 = 2.1 uM`) logged as `ELIMINATED` in `program-state/liability-tracker.md`.\n"
                "- **Lead Pivot (`OASE-PCSK9-014` / `PCSK9-A03`)**: Neutral polar 1,2,4-oxadiazole bioisostere (`MW = 468.5 Da`, `cLogP = 3.01`, `TPSA = 96.4 A^2`, `QED = 0.67`, `0` hERG/PAINS alerts, 5-step convergent route).\n"
                "- **Explicit Wet-Lab / CRO Handoff (`gates/GATE-03-wetlab-handoff.md`)**: Campaign paused cleanly at `WO-006` awaiting experimental SPR `KD`, manual patch-clamp hERG, and rat/dog cassette PK readouts before `WO-007` unlocks.",
                ["wo-006-finding", "active-series", "liability-tracker"],
                True,
            ),
        ],
    },
    {
        "chapter": "ch5",
        "slug": "05-pcsk9-oral-pk-gate4",
        "name": "05-pcsk9-oral-pk-gate4",
        "description": "Step 5 + Gate 4 — Wet-Lab Readout Ingested, Human Oral PK (40.0 mg QD, F=52%) & Candidate Dossier (WO-001..008)",
        "lead_human": "claire",
        "live_agents": ["science-program-lead", "admet-dmpk-scientist"],
        "artifact_keys": [
            "wo-001-finding",
            "wo-002-finding",
            "wo-003-finding",
            "wo-004-finding",
            "wo-005-finding",
            "wo-006-finding",
            "wo-007-finding",
            "wo-008-finding",
            "liability-tracker",
            "active-series",
            "decision-log",
            "program-summary",
            "pcsk9-evidence-portal",
        ],
        "topic_slug": "step-5-oral-pk-dossier-gate4",
        "topic_agent": "admet-dmpk-scientist",
        "seed_messages": [
            (
                "human:claire",
                "**[Chapter 5 Candidate Nomination — Wet-Lab Bridge & Human `40 mg QD` Oral PK (`WO-007`, `WO-008`)]**\n"
                "`@admet-dmpk-scientist` `@science-program-lead` — Rat (`F = 54%`) and dog (`F = 61%`) PK readouts plus patch-clamp hERG (`> 30 uM`) have returned from the Wet-Lab gate. Confirm the human oral QD dose projection and Candidate Dossier readiness for **Stage Gate 4**.",
                ["wo-007-finding", "program-summary"],
                False,
            ),
            (
                "agent:admet-dmpk-scientist",
                "**[Stage Gate 4 Candidate Nomination Ready — `OASE-PCSK9-014` (`40.0 mg QD`)]**\n"
                "- **Allometric Human Oral PK (`WO-007`)**: Oral bioavailability **`F = 52%`**, effective **`t1/2 = 14.8 h`**, projected human efficacious dose = **`40.0 mg QD`** (well below `<= 100 mg QD` target ceiling).\n"
                "- **Clinical Differentiation & Dossier (`WO-008`)**: Benchmarked against 84 PCSK9 clinical studies; `executive/CANDIDATE-SUMMARY.md` and `gates/GATE-04-candidate-nomination.md` verified (`8/8` Work Orders `scientifically_accepted`).",
                ["wo-007-finding", "wo-008-finding", "program-summary", "pcsk9-evidence-portal"],
                True,
            ),
        ],
    },
    {
        "chapter": "ch6",
        "slug": "06-pcsk9-governance-audit",
        "name": "06-pcsk9-governance-audit",
        "description": "Step 6 — Adversarial Governance Audit: 3 Tamper Drills Mechanically Blocked + 1 Co-Signed Human Override",
        "lead_human": "sarah",
        "live_agents": ["science-program-lead", "finding-validator"],
        "artifact_keys": [
            "wo-001-finding",
            "wo-002-finding",
            "wo-003-finding",
            "wo-004-finding",
            "wo-005-finding",
            "wo-006-finding",
            "wo-007-finding",
            "wo-008-finding",
            "liability-tracker",
            "active-series",
            "decision-log",
            "program-summary",
            "pcsk9-evidence-portal",
        ],
        "topic_slug": "step-6-tamper-drills-override-audit",
        "topic_agent": "finding-validator",
        "seed_messages": [
            (
                "human:sarah",
                "**[Chapter 6 Governance Audit — 3 Adversarial Tamper Drills + Backup Series Override]**\n"
                "`@finding-validator` — Run the 3 mechanical tamper drills (`DRILL-01`..`DRILL-03`) against `oase validate check` and confirm the co-signed audit trail for `Dr. Raj Patel`'s `IC-002` backup-series exploratory override (`DEC-OVERRIDE-001`).",
                ["decision-log", "program-summary"],
                False,
            ),
            (
                "agent:finding-validator",
                "**[Step 6 Governance Verdict — `3/3` Tamper Drills BLOCKED · `1` Co-Signed Override Logged]**\n"
                "1. **`DRILL-01` (Fabricated Vina `dG = -11.8 kcal/mol` without sidecar)** -> **`BLOCKED` (`MISSING_PROVENANCE_SIDECAR`)**\n"
                "2. **`DRILL-02` (Silent hERG ceiling edit to revive `PCSK9-A02`)** -> **`BLOCKED` (`IMMUTABLE_THRESHOLD_TAMPER`)**\n"
                "3. **`DRILL-03` (Truncated `CANDIDATE-SUMMARY.md` omitting risk table)** -> **`BLOCKED` (`REPORT_HEADINGS_MISSING`)**\n"
                "4. **Audited Human Override (`DEC-OVERRIDE-001`)**: Co-signed by `Dr. Raj Patel` & `Dr. Sarah Chen` via `oase workorder override` (`governance_override_cosigned` appended to `.oase/events.ndjson` with mandatory 14-day patch-clamp hERG gate).",
                ["decision-log", "program-summary", "pcsk9-evidence-portal"],
                True,
            ),
        ],
    },
    {
        "chapter": "ch7",
        "slug": "07-pcsk9-mission-closeout",
        "name": "07-pcsk9-mission-closeout",
        "description": "Step 7 — Post-Mission Debrief, Subway Map Recap & Portfolio Sign-Off",
        "lead_human": "sarah",
        "live_agents": ["science-program-lead", "project-curator"],
        "artifact_keys": [
            "wo-001-finding",
            "wo-002-finding",
            "wo-003-finding",
            "wo-004-finding",
            "wo-005-finding",
            "wo-006-finding",
            "wo-007-finding",
            "wo-008-finding",
            "liability-tracker",
            "active-series",
            "decision-log",
            "program-summary",
            "pcsk9-evidence-portal",
        ],
        "topic_slug": "step-7-portfolio-closeout-dossier",
        "topic_agent": "science-program-lead",
        "seed_messages": [
            (
                "human:sarah",
                "**[Step 7 Post-Mission Debrief — Squadron Route Recap & Portfolio Sign-Off]**\n"
                "`@science-program-lead` — All 5 Doctor + AI Wingman pairs are reconvened to debrief against our Step 1 Co-Scientist Research Brief (`WO-001`..`WO-008`, `GATE-01`..`GATE-04`, Wet-Lab PK bridge, and `STEP-06` tamper audit). Verify our campaign ledger and `gates/STEP-07-portfolio-closeout.md` for **`OASE-PCSK9-014` (`40.0 mg QD`)**.",
                ["program-summary", "pcsk9-evidence-portal"],
                False,
            ),
            (
                "agent:science-program-lead",
                "**[Post-Mission Debrief & Portfolio Sign-Off Complete — `OASE-PCSK9-014` Ready for GLP Tox]**\n"
                "- **Squadron Pair Debrief (`gates/STEP-07-portfolio-closeout.md`)**: `Marcus+Helix-2` (`AlphaGenome 0.984`), `Elena+Fold-3` (`AF3 ipTM 0.84` / `fpocket 0.68`), `Raj+Spark-4` (`BRICS` hERG rescue + `PCSK9-B07` override), `Claire+Shield-5` (rat `54%` / dog `61%` -> human **`40.0 mg QD`**), and `Sarah+Grove-1/Aegis-6` (`8/8` WOs, `4/4` gates, `3/3` tamper drills blocked).\n"
                "- **Executive Deliverable**: `executive/PORTFOLIO-HANDOFF.md` and 30-page static Evidence Portal co-signed with `0` ungrounded claims.",
                ["program-summary", "decision-log", "pcsk9-evidence-portal"],
                True,
            ),
        ],
    },
]


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def mint_jwt(env_path: Path, user_id: str, email: str, display_name: str) -> str:
    session_secret = None
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("SCION_SERVER_SESSION_SECRET="):
            session_secret = line.split("=", 1)[1].strip()
            break
    if not session_secret:
        raise RuntimeError(f"SCION_SERVER_SESSION_SECRET not found in {env_path}")

    signing_key = hashlib.sha256(
        f"scion-hub-signing-key:user_signing_key:{session_secret}".encode("utf-8")
    ).digest()

    now = int(time.time())
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "iss": "scion-hub",
        "sub": user_id,
        "aud": ["scion-hub-api"],
        "exp": now + 3600,
        "nbf": now - 10,
        "iat": now,
        "jti": b64url(os.urandom(16)),
        "uid": user_id,
        "email": email,
        "name": display_name,
        "role": "admin",
        "type": "access",
        "client": "web",
    }
    signing_input = (
        f"{b64url(json.dumps(header, separators=(',', ':')).encode())}."
        f"{b64url(json.dumps(payload, separators=(',', ':')).encode())}"
    )
    sig = hmac.new(signing_key, signing_input.encode("ascii"), hashlib.sha256).digest()
    return f"{signing_input}.{b64url(sig)}"


def api_call(hub_api: str, method: str, path: str, token: str, body=None) -> tuple[int, dict]:
    url = f"{hub_api.rstrip('/')}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"raw": raw}


def sanitize_settings_yaml(settings_path: Path, sarah_email: str) -> None:
    if not settings_path.exists():
        return
    text = settings_path.read_text(encoding="utf-8")
    updated = re.sub(
        r'admin_emails:\s*\n(?:\s*-\s*"[^"]+"\s*\n)+',
        f'admin_emails:\n      - "{sarah_email}"\n',
        text,
    )
    if updated != text:
        settings_path.write_text(updated, encoding="utf-8")
        print(f"[settings.yaml] Updated admin_emails -> {sarah_email}")


def build_compact_avatar_uri(avatars_dir: Path, key: str) -> str:
    tiny = avatars_dir / f"{key}_40.jpg"
    if tiny.exists():
        return "data:image/jpeg;base64," + base64.b64encode(tiny.read_bytes()).decode("ascii")
    src = avatars_dir / f"{key}.jpg"
    if not src.exists() or not shutil.which("ffmpeg"):
        return ""
    tmp_out = Path(f"/tmp/oase_avatar_{key}_40.jpg")
    res = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vf", "scale=40:40", "-q:v", "14", str(tmp_out)],
        capture_output=True,
        check=False,
    )
    if res.returncode == 0 and tmp_out.exists():
        raw = tmp_out.read_bytes()
        tmp_out.unlink(missing_ok=True)
        return "data:image/jpeg;base64," + base64.b64encode(raw).decode("ascii")
    return ""


def ensure_personas_and_purge_admin(db_path: Path, domain: str, avatars_dir: Path | None = None) -> dict[str, dict]:
    conn = sqlite3.connect(str(db_path), timeout=30)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    personas: dict[str, dict] = {}
    for key, display_name, sys_role, proj_role_id in PERSONAS:
        email = f"oase-{key}@{domain}"
        cur.execute("SELECT id, display_name, avatar_url FROM users WHERE email = ?", (email,))
        row = cur.fetchone()
        compact_uri = build_compact_avatar_uri(avatars_dir, key) if avatars_dir else ""
        if row is None:
            uid = str(uuid.uuid4())
            avatar_url = compact_uri
            cur.execute(
                """
                INSERT INTO users (id, email, display_name, avatar_url, role, status, created, last_login, last_seen, session_generation, kind)
                VALUES (?, ?, ?, ?, ?, 'active', ?, ?, ?, 0, 'human')
                """,
                (uid, email, display_name, avatar_url, sys_role, now_iso, now_iso, now_iso),
            )
        else:
            uid = row["id"]
            avatar_url = compact_uri if compact_uri else (row["avatar_url"] or "")
            cur.execute(
                "UPDATE users SET display_name = ?, role = ?, avatar_url = ? WHERE id = ?",
                (display_name, sys_role, avatar_url, uid),
            )

        cur.execute("SELECT id FROM groups WHERE slug = 'hub-members'")
        grp = cur.fetchone()
        if grp:
            cur.execute(
                """
                INSERT OR IGNORE INTO group_memberships (id, role, added_by, added_at, group_id, user_id)
                VALUES (?, 'member', 'system', ?, ?, ?)
                """,
                (str(uuid.uuid4()), now_iso, grp["id"], uid),
            )
        personas[key] = {
            "id": uid,
            "email": email,
            "display_name": display_name,
            "project_role_id": proj_role_id,
            "avatar_url": avatar_url,
        }

    sarah_id = personas["sarah"]["id"]
    cur.execute(
        """
        INSERT OR IGNORE INTO role_bindings (
            id, principal_type, principal_id, scope_type, scope_id, created_by, created, role_definition_id
        ) VALUES (?, 'user', ?, 'system', '', 'system', ?, ?)
        """,
        (str(uuid.uuid4()), sarah_id, now_iso, ROLE_SUPER_ADMIN),
    )

    # Purge any non-scientist admin@ rows and re-attribute legacy references to Sarah
    cur.execute("SELECT id, email FROM users WHERE email LIKE 'admin@%' OR email NOT LIKE 'oase-%'")
    stale_users = cur.fetchall()
    for su in stale_users:
        su_id = su["id"]
        cur.execute("DELETE FROM user_access_tokens WHERE user_id = ?", (su_id,))
        cur.execute("DELETE FROM group_memberships WHERE user_id = ?", (su_id,))
        cur.execute("DELETE FROM role_bindings WHERE principal_type = 'user' AND principal_id = ?", (su_id,))
        cur.execute("DELETE FROM conversation_participants WHERE principal_kind = 'user' AND principal_id = ?", (su_id,))
        cur.execute("DELETE FROM users WHERE id = ?", (su_id,))
        print(f"[hub.db] Purged non-scientist user {su['email']} ({su_id})")

    valid_uids = tuple(p["id"] for p in personas.values())
    placeholders = ",".join("?" for _ in valid_uids)
    cur.execute(
        f"UPDATE projects SET created_by = ?, owner_id = ? WHERE slug != 'global' AND (owner_id IS NULL OR owner_id NOT IN ({placeholders}))",
        (sarah_id, sarah_id, *valid_uids),
    )
    cur.execute(
        f"UPDATE artifact SET owner_kind = 'user', owner_ref = ?, sponsor_ref = ? WHERE owner_ref NOT IN ({placeholders}) OR sponsor_ref NOT IN ({placeholders}) OR sponsor_ref IS NULL",
        (sarah_id, sarah_id, *valid_uids, *valid_uids),
    )
    cur.execute(
        f"UPDATE skills SET owner_id = ?, created_by = ?, updated_by = ? WHERE owner_id NOT IN ({placeholders})",
        (sarah_id, sarah_id, sarah_id, *valid_uids),
    )
    cur.execute(
        f"UPDATE templates SET owner_id = ?, created_by = ?, updated_by = ? WHERE scope = 'project' AND (owner_id IS NULL OR owner_id NOT IN ({placeholders}))",
        (sarah_id, sarah_id, sarah_id, *valid_uids),
    )
    cur.execute(
        f"UPDATE agents SET owner_id = ?, created_by = ? WHERE owner_id IS NULL OR owner_id NOT IN ({placeholders})",
        (sarah_id, sarah_id, *valid_uids),
    )
    # Remove persona sidebar clutter from legacy source project if present
    cur.execute("SELECT id FROM projects WHERE slug = 'open-agentic-science-engine'")
    legacy_row = cur.fetchone()
    if legacy_row:
        lpid = legacy_row["id"]
        cur.execute("DELETE FROM role_bindings WHERE scope_type = 'project' AND scope_id = ?", (lpid,))
        cur.execute(
            "DELETE FROM group_memberships WHERE group_id IN (SELECT id FROM groups WHERE project_id = ?)",
            (lpid,),
        )

    conn.commit()
    conn.close()
    return personas


def find_source_project(db_path: Path) -> tuple[str | None, str | None, str | None]:
    """Return (source_project_id, hub_id, broker_id) from existing Hub state."""
    conn = sqlite3.connect(str(db_path), timeout=30)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id FROM projects WHERE slug = 'open-agentic-science-engine'")
    prow = cur.fetchone()
    src_pid = prow["id"] if prow else None

    hub_id = None
    cur.execute("SELECT storage_path FROM templates WHERE storage_path LIKE 'hubs/%' LIMIT 1")
    trow = cur.fetchone()
    if trow and trow["storage_path"]:
        parts = trow["storage_path"].split("/")
        if len(parts) >= 2:
            hub_id = parts[1]

    cur.execute("SELECT id FROM runtime_brokers LIMIT 1")
    brow = cur.fetchone()
    broker_id = brow["id"] if brow else None
    conn.close()
    return src_pid, hub_id, broker_id


def rewrite_skill_uris_in_agent_config(agent_cfg_raw: str | None) -> str | None:
    if not agent_cfg_raw:
        return agent_cfg_raw
    try:
        cfg = json.loads(agent_cfg_raw)
    except Exception:
        return agent_cfg_raw
    skills = cfg.get("skills")
    if isinstance(skills, list):
        cleaned = []
        for item in skills:
            uri = item.get("uri", "") if isinstance(item, dict) else ""
            if uri.startswith("gh://scion-frontiers/"):
                continue
            m = re.search(r"/skills/([a-zA-Z0-9_-]+)/?$", uri)
            if m:
                cleaned.append({"uri": f"skill://{m.group(1)}"})
            elif uri:
                cleaned.append(item)
        cfg["skills"] = cleaned
    return json.dumps(cfg, separators=(",", ":"))


def rewrite_scion_agent_yaml(yaml_text: str) -> str:
    out_lines = []
    for line in yaml_text.splitlines():
        if "gh://scion-frontiers/" in line:
            continue
        m = re.search(r'uri:\s*"?https://github\.com/[^"]+/skills/([a-zA-Z0-9_-]+)/?"?', line)
        if m:
            indent = line[: len(line) - len(line.lstrip())]
            out_lines.append(f'{indent}- uri: "skill://{m.group(1)}"')
        else:
            out_lines.append(line)
    return "\n".join(out_lines) + "\n"


def clone_templates_and_skills(
    db_path: Path,
    hub_dir: Path,
    src_pid: str | None,
    hub_id: str | None,
    target_pid: str,
    sarah_id: str,
    hub_api: str,
    token: str,
) -> None:
    storage_root = hub_dir / "workspace-storage"
    plain_tpl_root = hub_dir / "projects" / "open-agentic-science-engine" / "templates"
    conn = sqlite3.connect(str(db_path), timeout=30)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S.000000000 +0000 UTC")

    if src_pid and hub_id:
        # 1. Clone skills into target project FIRST so skill://<slug> resolves from local Hub registry
        cur.execute("SELECT * FROM skills WHERE scope = 'project' AND scope_id = ?", (src_pid,))
        src_skills = cur.fetchall()
        for sk in src_skills:
            slug = sk["slug"]
            cur.execute(
                "SELECT id FROM skills WHERE slug = ? AND scope = 'project' AND scope_id = ?",
                (slug, target_pid),
            )
            if cur.fetchone():
                continue
            new_sid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"oase-skill-{target_pid}-{slug}"))
            new_vid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"oase-skill-ver-{target_pid}-{slug}-1.0.0"))
            old_rel = sk["storage_path"] or ""
            new_rel = f"hubs/{hub_id}/skills/groves/{target_pid}/{slug}"
            src_dir = storage_root / old_rel
            dst_dir = storage_root / new_rel
            if src_dir.exists() and not dst_dir.exists():
                dst_dir.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(src_dir, dst_dir)

            cur.execute("SELECT * FROM skill_versions WHERE skill_id = ? LIMIT 1", (sk["id"],))
            sv = cur.fetchone()
            cur.execute(
                """
                INSERT INTO skills (
                    id, name, slug, description, tags, scope, scope_id,
                    storage_uri, storage_bucket, storage_path, status,
                    owner_id, created_by, updated_by, created, updated
                ) VALUES (?, ?, ?, ?, ?, 'project', ?, ?, '', ?, 'active', ?, ?, ?, ?, ?)
                """,
                (
                    new_sid,
                    sk["name"],
                    slug,
                    sk["description"],
                    sk["tags"],
                    target_pid,
                    f"gs:///{new_rel}/",
                    new_rel,
                    sarah_id,
                    sarah_id,
                    sarah_id,
                    now_str,
                    now_str,
                ),
            )
            if sv:
                cur.execute(
                    """
                    INSERT INTO skill_versions (
                        id, skill_id, version, status, content_hash, files,
                        publisher_id, deprecation_message, replacement_uri, download_count, created
                    ) VALUES (?, ?, ?, 'published', ?, ?, ?, '', '', 1, ?)
                    """,
                    (
                        new_vid,
                        new_sid,
                        sv["version"],
                        sv["content_hash"],
                        sv["files"],
                        sarah_id,
                        now_str,
                    ),
                )

        # 2. Seed templates into target project with content-addressed blobs & local skill:// URIs
        cur.execute("SELECT * FROM templates WHERE scope = 'project' AND scope_id = ?", (src_pid,))
        src_templates = cur.fetchall()
        for tpl in src_templates:
            slug = tpl["slug"]
            new_tid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"oase-tpl-{target_pid}-{slug}"))
            new_rel = f"hubs/{hub_id}/templates/groves/{target_pid}/{slug}.{new_tid}"
            dst_dir = storage_root / new_rel

            cur.execute(
                "SELECT id, storage_path FROM templates WHERE slug = ? AND scope = 'project' AND scope_id = ?",
                (slug, target_pid),
            )
            existing_tpl = cur.fetchone()
            if existing_tpl and (storage_root / (existing_tpl["storage_path"] or "")).exists():
                # Update agent_config in place to ensure local skill:// URIs
                cleaned_cfg = rewrite_skill_uris_in_agent_config(tpl["agent_config"])
                cur.execute("UPDATE templates SET agent_config = ? WHERE id = ?", (cleaned_cfg, existing_tpl["id"]))
                continue
            if existing_tpl:
                cur.execute("DELETE FROM templates WHERE id = ?", (existing_tpl["id"],))

            plain_dir = plain_tpl_root / slug
            files_manifest = []
            dst_dir.mkdir(parents=True, exist_ok=True)
            if plain_dir.exists():
                for fname in sorted(["agents.md", "scion-agent.yaml", "system-prompt.md"]):
                    fpath = plain_dir / fname
                    if not fpath.exists():
                        continue
                    if fname == "scion-agent.yaml":
                        data = rewrite_scion_agent_yaml(fpath.read_text(encoding="utf-8")).encode("utf-8")
                    elif fname == "agents.md":
                        base_md = fpath.read_text(encoding="utf-8")
                        if "MANDATORY WEBCHAT REPLY RULE" not in base_md:
                            base_md += (
                                "\n\n## MANDATORY WEBCHAT REPLY RULE (CRITICAL — ZERO EXCEPTIONS)\n"
                                "Whenever an incoming message contains `\"channel\": \"web\"` or `\"conversation\": { \"id\": \"<UUID>\" }` "
                                "inside `---BEGIN SCION MESSAGE---`:\n"
                                "1. **Humans in Scion Webchat CANNOT see your terminal stdout!**\n"
                                "2. You MUST ALWAYS execute `scion message \"conv:<conversation.id>\" - <<'MSG' ... MSG` "
                                "followed by `sciontool status ask_user` so your grounded 2–3 bullet response renders live in Webchat.\n"
                            )
                        data = base_md.encode("utf-8")
                    else:
                        data = fpath.read_bytes()
                    fhex = hashlib.sha256(data).hexdigest()
                    (dst_dir / fhex).write_bytes(data)
                    files_manifest.append(
                        {"path": fname, "size": len(data), "hash": f"sha256:{fhex}", "mode": "0644"}
                    )
                h = hashlib.sha256()
                for item in files_manifest:
                    h.update(item["hash"].encode("utf-8"))
                content_hash = f"sha256:{h.hexdigest()}"
                files_json = json.dumps(files_manifest, separators=(",", ":"))
            else:
                content_hash = tpl["content_hash"]
                files_json = tpl["files"]

            cleaned_cfg = rewrite_skill_uris_in_agent_config(tpl["agent_config"])
            cur.execute(
                """
                INSERT INTO templates (
                    id, name, slug, display_name, description, harness, default_harness_config,
                    agent_config, content_hash, scope, scope_id, project_id, storage_uri,
                    storage_bucket, storage_path, layout, files, base_template, status,
                    owner_id, created_by, updated_by, source_url, created, updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'project', ?, ?, ?, '', ?, ?, ?, ?, 'active', ?, ?, ?, ?, ?, ?)
                """,
                (
                    new_tid,
                    tpl["name"],
                    slug,
                    tpl["display_name"],
                    tpl["description"],
                    tpl["harness"],
                    tpl["default_harness_config"],
                    cleaned_cfg,
                    content_hash,
                    target_pid,
                    target_pid,
                    f"gs:///{new_rel}/",
                    new_rel,
                    tpl["layout"],
                    files_json,
                    tpl["base_template"],
                    sarah_id,
                    sarah_id,
                    sarah_id,
                    tpl["source_url"],
                    now_str,
                    now_str,
                ),
            )
        conn.commit()
        conn.close()
    else:
        conn.close()
        api_call(
            hub_api,
            "POST",
            "/api/v1/resources/import",
            token,
            {
                "kind": "template",
                "scope": "project",
                "scopeId": target_pid,
                "sourceUrl": "https://github.com/GoogleCloudPlatform/LifeSciences/tree/main/applications/open-agentic-science-engine/templates",
            },
        )


def share_tools_volume(hub_dir: Path, src_pid: str | None, slug: str, target_pid: str) -> None:
    cfg_root = hub_dir / "project-configs"
    target_cfg = cfg_root / f"{slug}__{target_pid[:8]}" / "shared-dirs" / "tools"
    target_cfg.parent.mkdir(parents=True, exist_ok=True)

    src_tools = None
    if src_pid:
        cand = cfg_root / f"open-agentic-science-engine__{src_pid[:8]}" / "shared-dirs" / "tools"
        if (cand / ".venv").exists():
            src_tools = cand

    if src_tools and not (target_cfg / ".venv").exists():
        if target_cfg.exists():
            shutil.rmtree(target_cfg)
        subprocess.run(["cp", "-al", str(src_tools), str(target_cfg)], check=True)
        env_sh = target_cfg / "env.sh"
        if env_sh.exists():
            env_text = env_sh.read_text(encoding="utf-8")
            # Unlink hardlink before editing env.sh so source project env.sh is untouched
            env_sh.unlink()
            env_text = re.sub(
                r"^export OASE_PROJECT=.*$",
                "export OASE_PROJECT=/workspace",
                env_text,
                flags=re.MULTILINE,
            )
            env_sh.write_text(env_text, encoding="utf-8")


def clone_chapter_artifacts(
    db_path: Path,
    src_pid: str | None,
    target_pid: str,
    sarah_id: str,
    creator_agent_id: str,
    allowed_keys: list[str],
) -> dict[str, str]:
    """Clone chapter-appropriate artifacts by referencing existing content-addressed blobs."""
    if not src_pid or not allowed_keys:
        return {}
    conn = sqlite3.connect(str(db_path), timeout=30)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000000000Z")

    artifacts_by_key: dict[str, str] = {}
    for key in allowed_keys:
        cur.execute(
            "SELECT id FROM artifact WHERE scope_kind = 'project' AND scope_ref = ? AND \"key\" = ? AND deleted_at IS NULL",
            (target_pid, key),
        )
        existing = cur.fetchone()
        if existing:
            artifacts_by_key[key] = existing["id"]
            continue

        cur.execute(
            "SELECT * FROM artifact WHERE scope_kind = 'project' AND scope_ref = ? AND \"key\" = ? AND deleted_at IS NULL",
            (src_pid, key),
        )
        src_art = cur.fetchone()
        if not src_art:
            continue

        cur.execute(
            "SELECT * FROM artifact_version WHERE artifact_id = ? AND seq = ?",
            (src_art["id"], src_art["current_seq"]),
        )
        src_ver = cur.fetchone()
        if not src_ver:
            continue

        new_aid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"oase-art-{target_pid}-{key}"))
        new_vid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"oase-artver-{target_pid}-{key}-1"))
        cur.execute(
            """
            INSERT INTO artifact (
                id, scope_kind, scope_ref, owner_kind, owner_ref, "key", title,
                current_seq, created_at, updated_at, sponsor_ref
            ) VALUES ('project', ?, ?, ?, ?, ?, ?, 1, ?, ?, ?)
            """
            if False
            else """
            INSERT INTO artifact (
                id, scope_kind, scope_ref, owner_kind, owner_ref, "key", title,
                current_seq, created_at, updated_at, sponsor_ref
            ) VALUES (?, 'project', ?, 'user', ?, ?, ?, 1, ?, ?, ?)
            """,
            (new_aid, target_pid, sarah_id, key, src_art["title"], now_iso, now_iso, sarah_id),
        )
        cur.execute(
            """
            INSERT INTO artifact_version (
                id, artifact_id, seq, kind, entry_path, note, total_bytes,
                file_count, created_by_kind, created_by_ref, created_at, state, claimed_at
            ) VALUES (?, ?, 1, ?, ?, ?, ?, ?, 'agent', ?, ?, 'ready', ?)
            """,
            (
                new_vid,
                new_aid,
                src_ver["kind"],
                src_ver["entry_path"],
                src_ver["note"],
                src_ver["total_bytes"],
                src_ver["file_count"],
                creator_agent_id,
                now_iso,
                now_iso,
            ),
        )
        cur.execute("SELECT * FROM artifact_file WHERE version_id = ?", (src_ver["id"],))
        for frow in cur.fetchall():
            cur.execute(
                """
                INSERT INTO artifact_file (
                    version_id, path, size, sha256, media_type, origin, received
                ) VALUES (?, ?, ?, ?, ?, ?, 1)
                """,
                (
                    new_vid,
                    frow["path"],
                    frow["size"],
                    frow["sha256"],
                    frow["media_type"],
                    frow["origin"] or "upload",
                ),
            )
        artifacts_by_key[key] = new_aid

    conn.commit()
    conn.close()
    return artifacts_by_key


def bind_personas_and_seed_project_db(
    db_path: Path,
    project_id: str,
    slug: str,
    spec: dict,
    personas: dict[str, dict],
    live_agent_ids: dict[str, str],
    artifacts_by_key: dict[str, str],
    reseed_messages: bool,
) -> dict:
    conn = sqlite3.connect(str(db_path), timeout=30)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    now_sql = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S.000000000 +0000 UTC")
    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sarah_id = personas["sarah"]["id"]

    # Ensure project owner/created_by = Sarah
    cur.execute(
        "UPDATE projects SET created_by = ?, owner_id = ? WHERE id = ?",
        (sarah_id, sarah_id, project_id),
    )

    # Ensure project members group + role bindings for all 5 human scientists
    members_grp_slug = f"project:{slug}:members"
    cur.execute("SELECT id FROM groups WHERE slug = ?", (members_grp_slug,))
    mrow = cur.fetchone()
    if mrow:
        members_grp_id = mrow["id"]
    else:
        members_grp_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"grp-{members_grp_slug}"))
        cur.execute(
            """
            INSERT INTO groups (id, name, slug, group_type, project_id, created, updated, created_by, owner_id)
            VALUES (?, ?, ?, 'explicit', ?, ?, ?, ?, ?)
            """,
            (members_grp_id, f"{slug} Members", members_grp_slug, project_id, now_sql, now_sql, sarah_id, sarah_id),
        )

    for pkey, pinfo in personas.items():
        cur.execute(
            """
            INSERT OR IGNORE INTO group_memberships (id, role, added_by, added_at, group_id, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid5(uuid.NAMESPACE_DNS, f"gm-{project_id}-{pkey}")),
                "owner" if pkey == "sarah" else "admin",
                sarah_id,
                now_sql,
                members_grp_id,
                pinfo["id"],
            ),
        )
        cur.execute(
            "DELETE FROM role_bindings WHERE principal_type = 'user' AND principal_id = ? AND scope_type = 'project' AND scope_id = ?",
            (pinfo["id"], project_id),
        )
        cur.execute(
            """
            INSERT INTO role_bindings (
                id, principal_type, principal_id, scope_type, scope_id,
                created_by, created, membership_kind, role_definition_id
            ) VALUES (?, 'user', ?, 'project', ?, ?, ?, 'explicit', ?)
            """,
            (
                str(uuid.uuid5(uuid.NAMESPACE_DNS, f"rb-{project_id}-{pkey}")),
                pinfo["id"],
                project_id,
                sarah_id,
                now_sql,
                pinfo["project_role_id"],
            ),
        )

    # Ensure all 11 Grove specialist agents exist in the project roster
    agent_ids: dict[str, str] = dict(live_agent_ids)
    for ag_slug, ag_tpl, ag_desc in ALL_11_GROVE_AGENTS:
        cur.execute("SELECT id FROM agents WHERE slug = ? AND project_id = ?", (ag_slug, project_id))
        arow = cur.fetchone()
        if arow:
            aid = arow["id"]
            agent_ids[ag_slug] = aid
            cur.execute(
                "UPDATE agents SET owner_id = ?, created_by = ? WHERE id = ?",
                (sarah_id, sarah_id, aid),
            )
        else:
            aid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"ag-{project_id}-{ag_slug}"))
            agent_ids[ag_slug] = aid
            cur.execute(
                """
                INSERT INTO agents (
                    id, slug, name, template, status, created_by, owner_id,
                    message_mode, phase, activity, exit_code, current_turns,
                    current_model_calls, image, runtime, task_summary, message,
                    harness_config, created, updated, last_seen, project_id
                ) VALUES (?, ?, ?, ?, 'stopped', ?, ?, 'project', 'stopped', '', 0, 6, 12,
                          'scion-antigravity:latest', 'docker', ?, 'Ready at checkpoint ' || ?, 'antigravity', ?, ?, ?, ?)
                """,
                (
                    aid,
                    ag_slug,
                    ag_slug,
                    ag_tpl,
                    sarah_id,
                    sarah_id,
                    f"{ag_desc} ({spec['chapter']})",
                    spec["chapter"],
                    now_sql,
                    now_sql,
                    now_sql,
                    project_id,
                ),
            )

    lead_agent_id = agent_ids["science-program-lead"]

    # Ensure #general webchat_topic & conversation exist and route default messages to science-program-lead
    cur.execute("SELECT id, conversation_id FROM webchat_topic WHERE project_id = ? AND is_general = 1", (project_id,))
    gt = cur.fetchone()
    if gt:
        general_tid = gt["id"]
        general_cid = gt["conversation_id"]
        cur.execute(
            "UPDATE webchat_topic SET default_agent = 'science-program-lead', created_by = ? WHERE id = ?",
            (sarah_id, general_tid),
        )
        if general_cid:
            cur.execute(
                "UPDATE conversations SET default_agent_id = ? WHERE id = ?",
                (lead_agent_id, general_cid),
            )
    else:
        general_tid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"topic-general-{project_id}"))
        general_cid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"conv-general-{project_id}"))
        cur.execute(
            """
            INSERT INTO conversations (
                id, project_id, kind, surface, external_ref, parent_ref,
                display_name, default_agent_id, drift_state, last_activity_at, created_at
            ) VALUES (?, ?, 'group', 'native', ?, '', 'general', ?, 'active', ?, ?)
            """,
            (general_cid, project_id, f"thread:{project_id}:{general_tid}", lead_agent_id, now_sql, now_sql),
        )
        cur.execute(
            """
            INSERT INTO webchat_topic (
                id, project_id, name, is_general, default_agent, conversation_id,
                created_by, created_at, last_message_id, last_activity_at
            ) VALUES (?, ?, 'general', 1, 'science-program-lead', ?, ?, ?, '', ?)
            """,
            (general_tid, project_id, general_cid, sarah_id, now_iso, now_iso),
        )

    # Register all 5 scientists + live agents as conversation_participants in #general
    for pinfo in personas.values():
        cur.execute(
            """
            INSERT OR IGNORE INTO conversation_participants (id, conversation_id, principal_kind, principal_id, role, joined_at)
            VALUES (?, ?, 'user', ?, 'member', ?)
            """,
            (str(uuid.uuid5(uuid.NAMESPACE_DNS, f"cp-{general_cid}-{pinfo['id']}")), general_cid, pinfo["id"], now_sql),
        )
    for ag_slug in spec["live_agents"]:
        aid = agent_ids[ag_slug]
        cur.execute(
            """
            INSERT OR IGNORE INTO conversation_participants (id, conversation_id, principal_kind, principal_id, role, joined_at)
            VALUES (?, ?, 'agent', ?, 'member', ?)
            """,
            (str(uuid.uuid5(uuid.NAMESPACE_DNS, f"cp-{general_cid}-{aid}")), general_cid, aid, now_sql),
        )

    # Create dedicated chapter stage-gate topic channel wired to chapter specialist
    topic_slug = spec["topic_slug"]
    topic_agent = spec["topic_agent"]
    topic_agent_id = agent_ids[topic_agent]
    cur.execute("SELECT id, conversation_id FROM webchat_topic WHERE project_id = ? AND name = ?", (project_id, topic_slug))
    st = cur.fetchone()
    if st:
        stage_tid = st["id"]
        stage_cid = st["conversation_id"]
    else:
        stage_tid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"topic-{project_id}-{topic_slug}"))
        stage_cid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"conv-{project_id}-{topic_slug}"))
        cur.execute(
            """
            INSERT INTO conversations (
                id, project_id, kind, surface, external_ref, parent_ref,
                display_name, default_agent_id, drift_state, last_activity_at, created_at
            ) VALUES (?, ?, 'group', 'native', ?, '', ?, ?, 'active', ?, ?)
            """,
            (stage_cid, project_id, f"thread:{project_id}:{stage_tid}", topic_slug, topic_agent_id, now_sql, now_iso),
        )
        cur.execute(
            """
            INSERT INTO webchat_topic (
                id, project_id, name, is_general, default_agent, conversation_id,
                created_by, created_at, last_message_id, last_activity_at
            ) VALUES (?, ?, ?, 0, ?, ?, ?, ?, '', ?)
            """,
            (stage_tid, project_id, topic_slug, topic_agent, stage_cid, sarah_id, now_iso, now_iso),
        )

    cur.execute("SELECT COUNT(*) AS cnt FROM messages WHERE project_id = ?", (project_id,))
    existing_msg_count = cur.fetchone()["cnt"]
    if reseed_messages or existing_msg_count == 0:
        cur.execute("DELETE FROM webchat_message_star WHERE project_id = ?", (project_id,))
        cur.execute("DELETE FROM messages WHERE project_id = ?", (project_id,))
        base_dt = datetime.datetime(2026, 10, 29, 0, 0, 0, tzinfo=datetime.timezone.utc)
        for idx, (actor, body, akeys, star) in enumerate(spec["seed_messages"]):
            ts_dt = base_dt + datetime.timedelta(minutes=idx * 2)
            ts_sql = ts_dt.strftime("%Y-%m-%d %H:%M:%S.000000000 +0000 UTC")
            ts_iso = ts_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            mid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"seed-msg-{project_id}-{idx}"))
            full_msg = body
            if akeys:
                refs = [f"scion://artifact/{artifacts_by_key[k]}" for k in akeys if k in artifacts_by_key]
                if refs:
                    full_msg = body + "\n\n" + "\n".join(refs)

            kind, ident = actor.split(":", 1)
            if kind == "human":
                p = personas[ident]
                sender_str = f"user:{p['email']}"
                sender_id = p["id"]
                msg_agent_id = lead_agent_id
                auth_uid = p["id"]
            else:
                sender_str = f"agent:{ident}"
                sender_id = agent_ids[ident]
                msg_agent_id = sender_id
                auth_uid = sarah_id

            cur.execute(
                """
                INSERT INTO messages (
                    id, project_id, sender, sender_id, recipient, recipient_id,
                    msg, type, urgent, broadcasted, read, agent_id, group_id,
                    dispatch_state, channel, thread_id, conversation_id, authorizing_user_id, created
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'chat', 0, 0, 1, ?, '', 'dispatched', 'web', ?, ?, ?, ?)
                """,
                (
                    mid,
                    project_id,
                    sender_str,
                    sender_id,
                    f"thread:{general_tid}",
                    general_tid,
                    full_msg,
                    msg_agent_id,
                    general_tid,
                    general_cid,
                    auth_uid,
                    ts_sql,
                ),
            )
            cur.execute(
                "UPDATE webchat_topic SET last_message_id = ?, last_activity_at = ? WHERE id = ?",
                (mid, ts_iso, general_tid),
            )
            cur.execute("UPDATE conversations SET last_activity_at = ? WHERE id = ?", (ts_sql, general_cid))
            if star:
                cur.execute(
                    """
                    INSERT OR IGNORE INTO webchat_message_star (
                        user_id, message_id, conversation_key, project_id, starred_at
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (sarah_id, mid, f"topic:{general_tid}", project_id, ts_iso),
                )

    conn.commit()
    conn.close()
    return {
        "general_topic_id": general_tid,
        "general_conv_id": general_cid,
        "stage_topic_id": stage_tid,
        "stage_conv_id": stage_cid,
        "agent_ids": agent_ids,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed 7-Chapter OASE Team Discovery Pilot on Scion Hub.")
    parser.add_argument("--gcp-project", default=os.environ.get("GCP_PROJECT_ID", ""), help="GCP Project ID")
    parser.add_argument("--workshop-domain", default=os.environ.get("WORKSHOP_DOMAIN", ""), help="Cloud Identity domain")
    parser.add_argument("--hub-dir", default=os.environ.get("SCION_HUB_DIR", "/home/scion/.scion"))
    parser.add_argument("--hub-api", default=os.environ.get("SCION_HUB_API", "http://127.0.0.1:8080"))
    parser.add_argument(
        "--repo-root",
        default=str(Path(__file__).resolve().parent.parent),
        help="Path to oase-workshop repository containing checkpoints/ and scripts/checkpoint.sh",
    )
    parser.add_argument("--reseed-messages", action="store_true", help="Reset seed messages even if messages exist")
    parser.add_argument("--skip-live-agents", action="store_true", help="Do not start Docker agent containers")
    parser.add_argument("--stop-legacy-containers", action="store_true", help="Stop idle legacy single-project containers")
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs and print planned 7-chapter actions")
    args = parser.parse_args()

    if not args.gcp_project or not args.workshop_domain:
        print("ERROR: --gcp-project (or GCP_PROJECT_ID) and --workshop-domain (or WORKSHOP_DOMAIN) are required.", file=sys.stderr)
        return 1

    repo_root = Path(args.repo_root).resolve()
    checkpoint_sh = repo_root / "scripts" / "checkpoint.sh"
    if not checkpoint_sh.exists():
        print(f"ERROR: checkpoint.sh not found at {checkpoint_sh}", file=sys.stderr)
        return 1

    sa_email = f"oase-agent-sa@{args.gcp_project}.iam.gserviceaccount.com"
    sarah_email = f"oase-sarah@{args.workshop_domain}"

    if args.dry_run:
        print(
            json.dumps(
                {
                    "dry_run": True,
                    "gcp_project": args.gcp_project,
                    "workshop_domain": args.workshop_domain,
                    "service_account": sa_email,
                    "admin_persona": sarah_email,
                    "chapters": [c["slug"] for c in CHAPTER_SPECS],
                    "personas": [f"oase-{p[0]}@{args.workshop_domain}" for p in PERSONAS],
                },
                indent=2,
            )
        )
        return 0

    hub_dir = Path(args.hub_dir).resolve()
    db_path = hub_dir / "hub.db"
    env_path = hub_dir / "hub.env"
    settings_path = hub_dir / "settings.yaml"

    sanitize_settings_yaml(settings_path, sarah_email)
    avatars_dir = repo_root / "site-template" / "assets" / "avatars"
    personas = ensure_personas_and_purge_admin(db_path, args.workshop_domain, avatars_dir=avatars_dir)
    sarah = personas["sarah"]
    token = mint_jwt(env_path, sarah["id"], sarah["email"], sarah["display_name"])

    src_pid, hub_id, _ = find_source_project(db_path)
    src_skills_dir = hub_dir / "projects" / "open-agentic-science-engine" / "skills"

    if args.stop_legacy_containers:
        for cname in [
            "open-agentic-science-engine--controller",
            "open-agentic-science-engine--bootstrapper",
            "open-agentic-science-engine--hypex-supervisor",
        ]:
            subprocess.run(["docker", "stop", cname], capture_output=True, check=False)

    status, projects_resp = api_call(args.hub_api, "GET", "/api/v1/projects", token)
    existing_projects: dict[str, str] = {}
    plist = projects_resp.get("projects", projects_resp) if isinstance(projects_resp, dict) else projects_resp
    if isinstance(plist, list):
        for p in plist:
            if p.get("slug"):
                existing_projects[p["slug"]] = p["id"]

    manifest_chapters: dict[str, dict] = {}
    for spec in CHAPTER_SPECS:
        ch = spec["chapter"]
        slug = spec["slug"]
        print(f"\n=== Provisioning {ch}: {slug} ===")
        pid = existing_projects.get(slug)
        if not pid:
            st, cresp = api_call(
                args.hub_api,
                "POST",
                "/api/v1/projects",
                token,
                {"name": spec["name"], "slug": slug},
            )
            pobj = cresp.get("project", cresp) if isinstance(cresp, dict) else {}
            pid = pobj.get("id")
            if not pid:
                raise RuntimeError(f"Failed to create project {slug} (HTTP {st}): {cresp}")
            print(f"  [API] Created project {slug} -> {pid}")
        else:
            print(f"  [API] Found existing project {slug} -> {pid}")

        # Register & verify GCP SA
        _, sas_resp = api_call(args.hub_api, "GET", f"/api/v1/projects/{pid}/gcp-service-accounts", token)
        sa_id = None
        sas_list = sas_resp.get("serviceAccounts", sas_resp.get("items", sas_resp)) if isinstance(sas_resp, dict) else sas_resp
        if isinstance(sas_list, list):
            for sa in sas_list:
                if sa.get("email") == sa_email:
                    sa_id = sa.get("id")
                    break
        if not sa_id:
            _, sa_create = api_call(
                args.hub_api,
                "POST",
                f"/api/v1/projects/{pid}/gcp-service-accounts",
                token,
                {"email": sa_email, "projectId": args.gcp_project, "displayName": "OASE Agent Service Account"},
            )
            sa_obj = sa_create.get("serviceAccount", sa_create) if isinstance(sa_create, dict) else {}
            sa_id = sa_obj.get("id")
        if sa_id:
            api_call(args.hub_api, "POST", f"/api/v1/projects/{pid}/gcp-service-accounts/{sa_id}/verify", token, {})

        api_call(
            args.hub_api,
            "PUT",
            f"/api/v1/projects/{pid}/settings",
            token,
            {
                "defaultGCPIdentityMode": "assign",
                "defaultGCPIdentityServiceAccountID": sa_id,
                "maxAgentRole": "full",
                "defaultAgentRole": "full",
            },
        )
        api_call(
            args.hub_api,
            "POST",
            f"/api/v1/projects/{pid}/shared-dirs",
            token,
            {"name": "tools", "in_workspace": True, "read_only": False},
        )

        # Materialize shared-dirs/tools via hardlink and clone templates + skills
        share_tools_volume(hub_dir, src_pid, slug, pid)
        clone_templates_and_skills(db_path, hub_dir, src_pid, hub_id, pid, sarah["id"], args.hub_api, token)

        # Initialize Git tags ch0..ch7 in /home/scion/.scion/projects/{slug} checked out at {ch}
        ws_dir = hub_dir / "projects" / slug
        ws_dir.mkdir(parents=True, exist_ok=True)
        (ws_dir / ".oase-repo").unlink(missing_ok=True)
        if src_skills_dir.exists() and not (ws_dir / "skills").exists():
            subprocess.run(["cp", "-al", str(src_skills_dir), str(ws_dir / "skills")], check=True)
        subprocess.run([str(checkpoint_sh), "init-git-tags", str(ws_dir), ch], check=True)
        print(f"  [Git] Initialized ch0..ch7 tags in {ws_dir} (HEAD -> {ch})")

        # Launch live specialist agent containers for this chapter
        live_agent_ids: dict[str, str] = {}
        if not args.skip_live_agents:
            _, ag_resp = api_call(args.hub_api, "GET", f"/api/v1/projects/{pid}/agents", token)
            ag_list = ag_resp.get("agents", ag_resp.get("items", ag_resp)) if isinstance(ag_resp, dict) else ag_resp
            existing_agents = {a.get("slug") or a.get("name"): a for a in (ag_list if isinstance(ag_list, list) else [])}

            for ag_slug in spec["live_agents"]:
                tpl = dict((s, t) for s, t, _ in ALL_11_GROVE_AGENTS)[ag_slug]
                existing_ag = existing_agents.get(ag_slug)
                if existing_ag and existing_ag.get("phase") == "running":
                    live_agent_ids[ag_slug] = existing_ag["id"]
                    print(f"  [Agent] {ag_slug} already running ({existing_ag['id']})")
                    continue
                if existing_ag and existing_ag.get("id"):
                    # Start existing stopped agent or recreate
                    st, sresp = api_call(args.hub_api, "POST", f"/api/v1/agents/{existing_ag['id']}/start", token, {})
                    if st in (200, 202):
                        live_agent_ids[ag_slug] = existing_ag["id"]
                        print(f"  [Agent] Started {ag_slug} ({existing_ag['id']})")
                        continue

                task_prompt = (
                    f"You are `{ag_slug}` for chapter `{ch}` (`{slug}`) of the PCSK9 oral small-molecule "
                    f"discovery campaign in `/workspace`. Verify `/workspace` state (do NOT modify `.oase/` "
                    f"unless explicitly instructed by a scientist in Webchat). When a human scientist messages "
                    f"you in Webchat, give a concise, quantitative, citation-backed answer grounded in "
                    f"`/workspace/program-state/`, `/workspace/findings/`, and `/workspace/gates/`. Stand by."
                )
                payload = {
                    "name": ag_slug,
                    "projectId": pid,
                    "template": tpl,
                    "agentRole": "full",
                    "gcp_identity": {"metadata_mode": "assign", "service_account_id": sa_id},
                    "task": task_prompt,
                }
                st, lresp = api_call(args.hub_api, "POST", f"/api/v1/projects/{pid}/agents", token, payload)
                aobj = lresp.get("agent", lresp) if isinstance(lresp, dict) else {}
                if aobj.get("id"):
                    live_agent_ids[ag_slug] = aobj["id"]
                    print(f"  [Agent] Launched {ag_slug} -> {aobj['id']} (HTTP {st})")
                else:
                    print(f"  [WARN] Launch {ag_slug} returned HTTP {st}: {lresp}")

        lead_aid = live_agent_ids.get("science-program-lead") or str(
            uuid.uuid5(uuid.NAMESPACE_DNS, f"ag-{pid}-science-program-lead")
        )
        artifacts_by_key = clone_chapter_artifacts(
            db_path, src_pid, pid, sarah["id"], lead_aid, spec["artifact_keys"]
        )
        db_meta = bind_personas_and_seed_project_db(
            db_path, pid, slug, spec, personas, live_agent_ids, artifacts_by_key, args.reseed_messages
        )

        manifest_chapters[ch] = {
            "chapter": ch,
            "project_id": pid,
            "slug": slug,
            "name": spec["name"],
            "description": spec["description"],
            "lead_human": spec["lead_human"],
            "lead_human_email": personas[spec["lead_human"]]["email"],
            "workspace_path": str(ws_dir),
            "general_topic_id": db_meta["general_topic_id"],
            "general_conv_id": db_meta["general_conv_id"],
            "stage_topic_id": db_meta["stage_topic_id"],
            "stage_conv_id": db_meta["stage_conv_id"],
            "live_agents": spec["live_agents"],
            "artifact_count": len(artifacts_by_key),
        }

    manifest_path = hub_dir / "pilot-chapters-manifest.json"
    manifest_data = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "gcp_project": args.gcp_project,
        "workshop_domain": args.workshop_domain,
        "personas": {
            k: {"id": v["id"], "email": v["email"], "display_name": v["display_name"]}
            for k, v in personas.items()
        },
        "chapters": manifest_chapters,
    }
    manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\n", encoding="utf-8")
    print(f"\n[OK] Wrote 7-chapter manifest -> {manifest_path}")

    # Create initial golden snapshot directory if none exists yet so state-controller works immediately
    snap_dir = hub_dir / "snapshots" / "golden-pilot"
    snap_dir.mkdir(parents=True, exist_ok=True)
    golden_db = snap_dir / "golden-hub.db"
    if not golden_db.exists() or args.reseed_messages:
        src_conn = sqlite3.connect(str(db_path), timeout=30)
        dst_conn = sqlite3.connect(str(golden_db))
        src_conn.backup(dst_conn)
        dst_conn.close()
        src_conn.close()
        shutil.copy2(manifest_path, snap_dir / "pilot-chapters-manifest.json")
        print(f"[OK] Saved baseline SQLite backup -> {golden_db}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

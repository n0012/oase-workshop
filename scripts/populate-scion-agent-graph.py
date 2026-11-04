#!/usr/bin/env python3
"""Populate the 4-tier Scion Agent Graph (ancestry + delegation_edges) and
inter-agent communications feed (SQLite messages + GCP Cloud Logging scion-messages)
for both canonical OASE missions (`pcsk9-oral-live-v2` and `io-cold-to-hot`).

Also removes orphaned legacy chapter containers (`00-pcsk9-*`..`07-pcsk9-*`) and
refreshes all golden-hub.db snapshots so `<2s` state resets preserve the 4-tier DAG.
"""

from __future__ import annotations

import datetime
import json
import shutil
import sqlite3
import subprocess
import uuid
from pathlib import Path
from typing import Any

HUB_DIR = Path("/home/scion/.scion")
DB_PATH = HUB_DIR / "hub.db"
GCP_PROJECT = "losiern-oase-workshop"
HUB_NAME = "oase"

PCSK9_PID = "dfe725e0-2c33-4569-84b2-1af9bb7b96fa"
IO_PID = "ab3d65d5-f32c-463e-be48-d535034de34f"
OASE_BASE_PID = "4df4c1ab-2091-4bd6-944b-da423d69fd3d"

BOUNDED_PERMS = json.dumps(
    [
        "agent.attach",
        "agent.create",
        "agent.delete",
        "agent.lifecycle",
        "agent.notify",
        "agent.port_forward",
        "agent.set_message_mode",
        "agent.status_update",
        "agent.token_refresh",
        "artifact.create",
        "artifact.read",
        "env_var.deliver",
        "gcp_service_account.assign",
        "harness_config.list",
        "harness_config.read",
        "project.read",
        "project.secret_read",
        "secret.deliver",
        "secret.use",
        "skill.list",
        "skill.read",
        "skill_injection.deliver",
        "template.create",
        "template.list",
        "template.read",
        "template.update",
    ]
)

# 17-node 4-tier OASE hierarchy:
# Tier 0: User (Dr. Sarah Chen)
# Tier 1: controller
# Tier 2 (under controller): bootstrapper, head-of-discovery, hypex-supervisor, science-program-lead
# Tier 3A (under hypex-supervisor): rank-1, rank-2, rank-3, hypex-reflection
# Tier 3B (under science-program-lead): computational-biologist, structural-biologist,
#         computational-chemist, medicinal-chemist, admet-dmpk-scientist,
#         scientific-reviewer, finding-validator, project-curator
AGENT_SPECS: list[dict[str, Any]] = [
    {
        "slug": "controller",
        "template": "research-operations-controller",
        "parent": "USER",
        "phase": "running",
        "activity": "waiting_for_input",
        "status": "waiting_for_input",
        "model": "Gemini 3.8 Flash (Medium)",
        "has_container": False,
        "task_summary": "Research Operations Controller — Orchestrating Grove Lifecycle & Stage Gates",
    },
    {
        "slug": "bootstrapper",
        "template": "bootstrapper",
        "parent": "controller",
        "phase": "running",
        "activity": "completed",
        "status": "completed",
        "model": "Gemini 3.8 Flash (Medium)",
        "has_container": False,
        "task_summary": "Verified shared Grove: 41 skills, 78/78 oase doctor checks, compiled binaries ready",
    },
    {
        "slug": "head-of-discovery",
        "template": "head-of-discovery",
        "parent": "controller",
        "phase": "running",
        "activity": "waiting_for_input",
        "status": "waiting_for_input",
        "model": "Gemini 4 Argon (High)",
        "has_container": False,
        "task_summary": "Portfolio & Target Strategy Lead — Co-signing Stage Gates with Human Program Lead",
    },
    {
        "slug": "hypex-supervisor",
        "template": "hypex-supervisor",
        "parent": "controller",
        "phase": "running",
        "activity": "completed",
        "status": "completed",
        "model": "Gemini 4 Argon (High)",
        "has_container": True,
        "task_summary": "Hypothesis Tournament Supervisor — Completed RUN-001 Elo Pairwise Ranking",
    },
    {
        "slug": "science-program-lead",
        "template": "science-program-lead",
        "parent": "controller",
        "phase": "running",
        "activity": "waiting_for_input",
        "status": "waiting_for_input",
        "model": "Gemini 4 Argon (High)",
        "has_container": True,
        "task_summary": "Discovery Program Lead (Gemini 4 Argon High) — Coordinating WO-001..WO-008",
    },
    {
        "slug": "rank-1",
        "template": "hypex-ranker",
        "parent": "hypex-supervisor",
        "phase": "running",
        "activity": "completed",
        "status": "completed",
        "model": "Gemini 3.8 Flash (Medium)",
        "has_container": False,
        "task_summary": "Pairwise Tournament Judge #1 — Mechanism & Tractability Scoring",
    },
    {
        "slug": "rank-2",
        "template": "hypex-ranker",
        "parent": "hypex-supervisor",
        "phase": "running",
        "activity": "completed",
        "status": "completed",
        "model": "Gemini 3.8 Flash (Medium)",
        "has_container": False,
        "task_summary": "Pairwise Tournament Judge #2 — Structural Plausibility & Pocket Geometry",
    },
    {
        "slug": "rank-3",
        "template": "hypex-ranker",
        "parent": "hypex-supervisor",
        "phase": "running",
        "activity": "completed",
        "status": "completed",
        "model": "Claude Opus 5.5",
        "has_container": False,
        "task_summary": "Pairwise Tournament Judge #3 — Translational & DMPK Risk Assessment",
    },
    {
        "slug": "hypex-reflection",
        "template": "hypex-reflection",
        "parent": "hypex-supervisor",
        "phase": "running",
        "activity": "completed",
        "status": "completed",
        "model": "Claude Opus 5.5",
        "has_container": True,
        "task_summary": "Hypothesis Reflection & Critique — Logged mandatory caveats & falsification gates",
    },
    {
        "slug": "computational-biologist",
        "template": "computational-biologist",
        "parent": "science-program-lead",
        "phase": "running",
        "activity": "waiting_for_input",
        "status": "waiting_for_input",
        "model": "Gemini 4 Argon (Medium)",
        "has_container": True,
        "task_summary": "Human Genetics, Omics & AlphaGenome Regulatory Variant Scoring (WO-002..WO-003)",
    },
    {
        "slug": "structural-biologist",
        "template": "structural-biologist",
        "parent": "science-program-lead",
        "phase": "running",
        "activity": "waiting_for_input",
        "status": "waiting_for_input",
        "model": "Gemini 4 Argon (High)",
        "has_container": True,
        "task_summary": "AlphaFold 3 Co-Folding, fpocket Druggability & AutoDock Vina (WO-004)",
    },
    {
        "slug": "computational-chemist",
        "template": "computational-chemist",
        "parent": "science-program-lead",
        "phase": "running",
        "activity": "waiting_for_input",
        "status": "waiting_for_input",
        "model": "Gemini 4 Argon (Medium)",
        "has_container": False,
        "task_summary": "Pharmacophore Alignment, 20-Analog MPO Ranking & Pose Rescoring (WO-005)",
    },
    {
        "slug": "medicinal-chemist",
        "template": "medicinal-chemist",
        "parent": "science-program-lead",
        "phase": "running",
        "activity": "waiting_for_input",
        "status": "waiting_for_input",
        "model": "Claude Opus 5.5",
        "has_container": True,
        "task_summary": "DMTA Lead Optimization, Synthetic Tractability & Wet-Lab SAR Integration (WO-005..WO-006)",
    },
    {
        "slug": "admet-dmpk-scientist",
        "template": "admet-dmpk-scientist",
        "parent": "science-program-lead",
        "phase": "running",
        "activity": "waiting_for_input",
        "status": "waiting_for_input",
        "model": "Gemini 4 Argon (Medium)",
        "has_container": True,
        "task_summary": "ADMET Permeability/Efflux Audit, 1-Compartment Oral PK & Safety Margins (WO-006..WO-007)",
    },
    {
        "slug": "scientific-reviewer",
        "template": "scientific-reviewer",
        "parent": "science-program-lead",
        "phase": "running",
        "activity": "waiting_for_input",
        "status": "waiting_for_input",
        "model": "Claude Opus 5.5",
        "has_container": True,
        "task_summary": "Independent Cross-Model Peer Reviewer (Claude Opus 5.5) — Relay & Falsification Audit",
    },
    {
        "slug": "finding-validator",
        "template": "finding-validator",
        "parent": "science-program-lead",
        "phase": "running",
        "activity": "waiting_for_input",
        "status": "waiting_for_input",
        "model": "Gemini 3.8 Flash (Medium)",
        "has_container": True,
        "task_summary": "Deterministic Governance Validator — 10/10 oase validate check & SHA-256 Sidecars (WO-008)",
    },
    {
        "slug": "project-curator",
        "template": "project-curator",
        "parent": "science-program-lead",
        "phase": "running",
        "activity": "waiting_for_input",
        "status": "waiting_for_input",
        "model": "Gemini 3.8 Flash (Medium)",
        "has_container": True,
        "task_summary": "Evidence Site & Artifact Bundle Curator — oase site build (13/13 Scion Artifacts)",
    },
]


PCSK9_INTER_AGENT_MESSAGES: list[tuple[str, str, str, str]] = [
    (
        "user",
        "controller",
        "instruction",
        "Initialize `pcsk9-oral-live-v2` Grove from `seed/pcsk9-oral/campaign-seed.json` (`sha256:61020936449a`) and coordinate `WO-001`..`WO-008` across the 17-agent discovery hierarchy.",
    ),
    (
        "controller",
        "bootstrapper",
        "instruction",
        "Run `oase doctor` and verify `/workspace` shared Grove environment, compiled binaries (`vina 1.2.5`, `fpocket 4.2.2`, `RDKit`), and `.oase/thresholds.yaml` (`36/36` rule sets).",
    ),
    (
        "bootstrapper",
        "controller",
        "state-change",
        "Agent `'bootstrapper'` has completed work: `78/78` `oase doctor` checks PASS (`41` verification skills staged; `ENV_VERSION = sha256:61020936449a`).",
    ),
    (
        "controller",
        "hypex-supervisor",
        "instruction",
        "Execute pairwise Elo tournament (`RUN-001`, `coscientist@1.1+program`, `WO-001`) across `rank-1`, `rank-2`, `rank-3`, and `hypex-reflection` for `IC-001` (Oral small molecule in PCSK9 `Pocket #1`) vs `IC-002` (Oral macrocycle on `EGF-A` flat surface).",
    ),
    (
        "hypex-supervisor",
        "rank-1",
        "instruction",
        "Score pairwise matches (`RUN-001`) on mechanism of action, oral small-molecule tractability, and allosteric LDLR-recycling rescue.",
    ),
    (
        "rank-1",
        "hypex-supervisor",
        "state-change",
        "Agent `'rank-1'` has completed work: `IC-001` wins `7/9` pairwise matches (`0.78` win rate) over `IC-002` on oral Rule-of-5 permeability and crypts near `PCSK9` catalytic/prodomain interface.",
    ),
    (
        "rank-2",
        "hypex-supervisor",
        "state-change",
        "Agent `'rank-2'` has completed work: Structural pocket geometry favors `IC-001` (`Pocket #1` enclosed cavity `439.9 Å³`) vs `IC-002` solvent-exposed flat `EGF-A` interface (`312.4 Å²`).",
    ),
    (
        "rank-3",
        "hypex-supervisor",
        "state-change",
        "Agent `'rank-3'` has completed work: DMPK risk evaluation flags high efflux/low passive permeability risk for `IC-002` cyclic peptide (`MW > 1100 Da`) without permeation enhancers.",
    ),
    (
        "hypex-reflection",
        "hypex-supervisor",
        "state-change",
        "Agent `'hypex-reflection'` has completed work: Logged mandatory caveat `hypothesis.adopted_not_generated` — `IC-001` (`1642.5 Elo`) requires primary Stage 1 genetics (`WO-002`/`WO-003`) and Stage 2 structural falsification (`WO-004`).",
    ),
    (
        "hypex-supervisor",
        "controller",
        "state-change",
        "Agent `'hypex-supervisor'` has completed work: `WO-001` Elo tournament finalized — `IC-001` (`1642.5 Elo`) > `IC-002` (`1588.0 Elo`, `+54.5 Elo` margin). Handing off to `@science-program-lead`.",
    ),
    (
        "controller",
        "science-program-lead",
        "instruction",
        "Coordinate Stage 1–4 execution (`WO-002`..`WO-008`) across `@computational-biologist`, `@structural-biologist`, `@computational-chemist`, `@medicinal-chemist`, `@admet-dmpk-scientist`, `@scientific-reviewer`, `@finding-validator`, and `@project-curator`.",
    ),
    (
        "science-program-lead",
        "computational-biologist",
        "instruction",
        "Execute `WO-002` (`gnomAD` LoF constraint, `OpenTargets` disease association, `GTEx` liver expression) and `WO-003` (`AlphaGenome` 1P regulatory variant scoring for `rs2479409`).",
    ),
    (
        "computational-biologist",
        "science-program-lead",
        "state-change",
        "Agent `'computational-biologist'` is waiting for input: `WO-002`/`WO-003` verified (`oase validate check` PASS) — `pLI = 0.0001`, `LOEUF = 0.89` (`LOF_TOLERANT`), `OpenTargets = 0.96`, `GTEx` liver `184.2 TPM` (`Tau = 0.93`), `AlphaGenome` `rs2479409` liver `RNA_SEQ` quantile `0.984` (`LFC = -0.24`).",
    ),
    (
        "science-program-lead",
        "structural-biologist",
        "instruction",
        "Execute `WO-004`: Run `AlphaFold 3` co-folding on `PCSK9` (`PDB 2P4E`), `fpocket 4.2.2` druggability scan, and `AutoDock Vina 1.2.5` head-to-head docking (`IC-001` vs `IC-002`).",
    ),
    (
        "structural-biologist",
        "science-program-lead",
        "state-change",
        "Agent `'structural-biologist'` is waiting for input: `WO-004` verified — `AF3` global `pLDDT = 88.4` (`Pocket #1 pLDDT = 92.1`, `ipTM = 0.84` structural confidence, not affinity), `fpocket` `Pocket #1 = 439.9 Å³` (`druggability = 0.68` vs flat `EGF-A = 0.24`), `Vina` `IC-001 = -9.4 kcal/mol` (`LE = 0.38`, docking score not affinity) vs `IC-002 = -6.4 kcal/mol` (`DEC-006` co-signed).",
    ),
    (
        "science-program-lead",
        "computational-chemist",
        "instruction",
        "Run 20-analog MPO scoring and `AutoDock Vina` rescoring across `oase_pcsk9_001`..`020` (`WO-005`) with `@medicinal-chemist`.",
    ),
    (
        "computational-chemist",
        "medicinal-chemist",
        "state-change",
        "Agent `'computational-chemist'` is waiting for input: Completed 20-analog MPO & `Vina` rescoring (`WO-005`) — lead `OASE-PCSK9-014` scores `-9.4 kcal/mol` (`QED = 0.74`, `MW = 438.5 Da`, `cLogP = 3.1`, `tPSA = 84.2 Å²`, `SA = 2.61`, `0 PAINS`).",
    ),
    (
        "medicinal-chemist",
        "science-program-lead",
        "state-change",
        "Agent `'medicinal-chemist'` is waiting for input: `WO-005`/`WO-006` verified — Seeded CRO wet-lab readout (demo values) for `OASE-PCSK9-014` reports `TR-FRET IC50 = 142 nM`, `SPR KD = 118 nM`, `HepG2 LDLR EC50 = 210 nM`, `Caco-2 Papp = 14.8e-6 cm/s` (`ER = 1.3`), `hERG IC50 > 30 µM` (`DEC-008` co-signed).",
    ),
    (
        "science-program-lead",
        "admet-dmpk-scientist",
        "instruction",
        "Execute `WO-007`: Run 1-compartment oral PK projection (`Projected 40 mg QD`) and 50-fold free `Cmax` safety margin audit for `OASE-PCSK9-014`.",
    ),
    (
        "admet-dmpk-scientist",
        "science-program-lead",
        "state-change",
        "Agent `'admet-dmpk-scientist'` is waiting for input: `WO-007` verified — Projected oral `F = 52%` (rat `54%`, dog `61%` seeded CRO PK), `t1/2 = 14.8 h`, `Projected 40 mg QD` tablet, `Ctrough,free (24h) = 412 nM` (`2.9x IC50`), `hERG` free `Cmax` margin `> 44x` (`PASS`, `DEC-009` co-signed).",
    ),
    (
        "scientific-reviewer",
        "science-program-lead",
        "state-change",
        "Agent `'scientific-reviewer'` is waiting for input: Independent cross-model peer review (`Claude Opus 5.5`) complete across `WO-001`..`WO-008` — all `6/6` domain relays propagated (`0` unaddressed flags).",
    ),
    (
        "finding-validator",
        "controller",
        "state-change",
        "Agent `'finding-validator'` is waiting for input: `WO-008` mechanical governance audit PASS (`10/10` rules verified; SHA-256 sidecars match `.oase/events.ndjson`).",
    ),
    (
        "project-curator",
        "head-of-discovery",
        "state-change",
        "Agent `'project-curator'` is waiting for input: Built static evidence site `_site/index.html` (`13/13` Scion artifacts published) for In-Silico Nominated Lead (Demo) (`DEC-010`).",
    ),
    (
        "user",
        "science-program-lead",
        "instruction",
        "**[Cloud Shell · Antigravity (`agy`) CLI Feedback]** Audit `WO-006`..`WO-008`: verify why neutral 1,2,4-oxadiazole `OASE-PCSK9-014` cleared the Aronov hERG gate (`IC50 > 30 µM`) and confirm `DEC-010` nomination readiness.",
    ),
    (
        "science-program-lead",
        "user",
        "state-change",
        "**[Grounded Science Agent Reply -> `agy` CLI]** Verified `OASE-PCSK9-014` (`cLogP = 3.01`, `0` hERG alerts, seeded CRO demo values: `TR-FRET IC50 = 142 nM`, `SPR KD = 118 nM`, `Caco-2 Papp = 14.8e-6 cm/s`, `Projected F = 52%`, `Projected 40 mg QD`, `10/10 oase validate check PASS` for `DEC-010`).",
    ),
]


IO_INTER_AGENT_MESSAGES: list[tuple[str, str, str, str]] = [
    (
        "user",
        "controller",
        "instruction",
        "Initialize `io-cold-to-hot` Grove from `seed/io-cold-to-hot/campaign-seed.json` (`sha256:61020936449a`) to identify an oral innate immune target converting immune-cold MSS-CRC/PDAC tumors to immune-hot.",
    ),
    (
        "controller",
        "bootstrapper",
        "instruction",
        "Run `oase doctor` and verify `/workspace` shared Grove environment, compiled binaries (`vina 1.2.5`, `fpocket 4.2.2`, `RDKit`), and `.oase/thresholds.yaml` (`36/36` rule sets).",
    ),
    (
        "bootstrapper",
        "controller",
        "state-change",
        "Agent `'bootstrapper'` has completed work: `78/78` `oase doctor` checks PASS (`41` verification skills staged; `ENV_VERSION = sha256:61020936449a`).",
    ),
    (
        "controller",
        "hypex-supervisor",
        "instruction",
        "Execute 5-target pairwise Elo tournament (`RUN-001`, `WO-001`) across `rank-1`, `rank-2`, `rank-3`, and `hypex-reflection`: `IC-101` (`ENPP1`) vs `IC-103` (`ADAR1`) vs `PTPN2` vs `KDM1A/LSD1` vs `IC-102` (`TREX1`).",
    ),
    (
        "rank-1",
        "hypex-supervisor",
        "state-change",
        "Agent `'rank-1'` has completed work: `IC-101` (`ENPP1`) leads on extracellular `2'3'-cGAMP` preservation and tumor-restricted STING activation without systemic autoimmune toxicity.",
    ),
    (
        "rank-2",
        "hypex-supervisor",
        "state-change",
        "Agent `'rank-2'` has completed work: Catalytic bi-zinc PDE pocket (`PDB 2YS0`, `612.4 Å³`) offers superior small-molecule druggability (`0.89`) over `Trex1` and `ADAR1`.",
    ),
    (
        "rank-3",
        "hypex-supervisor",
        "state-change",
        "Agent `'rank-3'` has completed work: Flagged mandatory DMPK relay for zinc-binding phosphodiesterase scaffolds (`tPSA` / `P-gp` efflux watch for Stage 3 DMTA).",
    ),
    (
        "hypex-reflection",
        "hypex-supervisor",
        "state-change",
        "Agent `'hypex-reflection'` has completed work: Logged mandatory caveat `hypothesis.adopted_not_generated` + `Trex1` autoimmune myocarditis exclusion rationale (`DEC-002`).",
    ),
    (
        "hypex-supervisor",
        "controller",
        "state-change",
        "Agent `'hypex-supervisor'` has completed work: `WO-001` 5-target Elo leaderboard finalized — `IC-101` (`ENPP1`, `1658.4 Elo`, `#1 WINNER`) > `IC-103` (`ADAR1`, `1602.0 Elo`) > `PTPN2` (`1554.5 Elo`) > `KDM1A/LSD1` (`1442.0 Elo`) > `IC-102` (`TREX1`, `1368.0 Elo`).",
    ),
    (
        "controller",
        "science-program-lead",
        "instruction",
        "Coordinate Stage 1–4 execution (`WO-002`..`WO-008`) for `IC-101` (`ENPP1`) across the specialist team.",
    ),
    (
        "science-program-lead",
        "computational-biologist",
        "instruction",
        "Execute `WO-002` (`gnomAD`, `OpenTargets`, `TCGA` CD8+ T-cell anti-correlation) and `WO-003` (`AlphaGenome` regulatory variant scoring for `rs1044032`).",
    ),
    (
        "computational-biologist",
        "science-program-lead",
        "state-change",
        "Agent `'computational-biologist'` is waiting for input: `WO-002`/`WO-003` verified — `ENPP1` `pLI = 0.0001`, `LOEUF = 0.76` (heterozygous LoF tolerance; biallelic ENPP1 deficiency GACI/ARHR2 logged as mineralization liability to monitor), `OpenTargets = 0.84`, `TCGA` CD8+ signature `r = -0.64` (`p = 1.2e-14`), `AlphaGenome` `rs1044032` myeloid enhancer quantile `0.976` (`LFC = -0.31`, `DEC-004` co-signed).",
    ),
    (
        "science-program-lead",
        "structural-biologist",
        "instruction",
        "Execute `WO-004`: Run `AlphaFold 3` holo co-folding on `ENPP1` (`PDB 2YS0`), `fpocket 4.2.2`, and `AutoDock Vina 1.2.5` docking (`IC-101` vs `IC-102`).",
    ),
    (
        "structural-biologist",
        "science-program-lead",
        "state-change",
        "Agent `'structural-biologist'` is waiting for input: `WO-004` verified — `AF3` global `pLDDT = 77.79` (`iPTM = 0.36`; `PDB 6B2J` `1.80 Å` experimental crystal anchor), `fpocket` `Pocket #1 = 612.4 Å³` (`druggability = 0.903`), `Vina` `IC-101 = -7.861 kcal/mol` (`DEC-002` co-signed).",
    ),
    (
        "science-program-lead",
        "computational-chemist",
        "instruction",
        "Run 20-analog DMTA generation and `AutoDock Vina` rescoring across `oase_enpp1_001`..`020` (`WO-005`) with `@medicinal-chemist`.",
    ),
    (
        "computational-chemist",
        "medicinal-chemist",
        "state-change",
        "Agent `'computational-chemist'` is waiting for input: `WO-005` in-silico screening complete — Series A sulfamide lead `oase_enpp1_009` scores `-10.2 kcal/mol` (`QED = 0.69`, `SA = 2.84`, `0 PAINS`).",
    ),
    (
        "admet-dmpk-scientist",
        "science-program-lead",
        "state-change",
        "Agent `'admet-dmpk-scientist'` is waiting for input: **[WET-LAB WALL TRIGGERED (`WO-006`)]** — Series A `oase_enpp1_009` confirmed biochemical potency (`ENPP1 IC50 = 18 nM`, `SPR KD = 14 nM`, `THP-1 ISG EC50 = 64 nM`) but FAILED oral absorption gates (`MDCK Papp = 1.1e-6 cm/s < 5.0e-6`, `P-gp ER = 18.4 > 2.5`) due to polar zinc-chelating sulfamide (`tPSA = 114 Å²`).",
    ),
    (
        "medicinal-chemist",
        "science-program-lead",
        "state-change",
        "Agent `'medicinal-chemist'` is waiting for input: **[SERIES PIVOT EXECUTED (`DEC-008`)]** — Replaced polar sulfamide (`oase_enpp1_009`, `MW = 475.50 Da`, `TPSA = 113.96 Å²`) with neutral pyrazole heteroaryl ZBG Series B backup **`oase_enpp1_019`** (`MW = 430.51 Da`, `cLogP = 3.46`, `TPSA = 79.40 Å²`, `ENPP1 IC50 = 31 nM`, `MDCK Papp = 12.4e-6 cm/s`, `ER = 1.6`, `hERG IC50 > 30 µM`).",
    ),
    (
        "admet-dmpk-scientist",
        "science-program-lead",
        "state-change",
        "Agent `'admet-dmpk-scientist'` is waiting for input: `WO-007` verified for Series B `oase_enpp1_019` — Projected oral `F = 52%`, `t1/2 = 8.6 h`, tumor `Ctrough,free (24h) = 198 nM` (`6.4x IC50`), `hERG` free `Cmax` margin `> 48x` (`PASS`, `DEC-009` co-signed).",
    ),
    (
        "scientific-reviewer",
        "science-program-lead",
        "state-change",
        "Agent `'scientific-reviewer'` is waiting for input: Independent cross-model peer review (`Claude Opus 5.5`) verified `DEC-008` Wet-Lab Wall falsification of `oase_enpp1_009` and Series B recovery via `oase_enpp1_019` (`6/6` relays propagated).",
    ),
    (
        "finding-validator",
        "controller",
        "state-change",
        "Agent `'finding-validator'` is waiting for input: `WO-008` mechanical governance audit PASS (`10/10` rules verified; SHA-256 sidecars match `.oase/events.ndjson`).",
    ),
    (
        "project-curator",
        "head-of-discovery",
        "state-change",
        "Agent `'project-curator'` is waiting for input: Built static evidence site `_site/index.html` (`13/13` Scion artifacts published) for Series B Pre-Candidate Nomination (`DEC-010`).",
    ),
    (
        "user",
        "science-program-lead",
        "instruction",
        "**[Cloud Shell · Antigravity (`agy`) CLI Feedback]** Audit the `DEC-008` Wet-Lab Wall: verify why Series A (`oase_enpp1_009`) failed oral absorption gates and confirm Series B (`oase_enpp1_019`) recovery for `DEC-010`.",
    ),
    (
        "science-program-lead",
        "user",
        "state-change",
        "**[Grounded Science Agent Reply -> `agy` CLI]** Series A `oase_enpp1_009` hit `DEC-008` Wet-Lab Wall (`MDCK Papp = 1.1e-6 cm/s`, `P-gp ER = 18.4`); Series B `oase_enpp1_019` masked monoester restored oral absorption (`12.4e-6 cm/s`, `ER = 1.6`, `F = 52%`, `10/10 validate PASS`).",
    ),
]


def stop_orphaned_containers() -> None:
    """Stop and remove legacy chapter containers (`00-pcsk9-*`..`07-pcsk9-*`, `open-agentic-science-engine--*`)."""
    res = subprocess.run(
        ["docker", "ps", "-a", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if res.returncode != 0:
        return
    orphans = [
        name.strip()
        for name in res.stdout.splitlines()
        if name.strip().startswith(("00-pcsk9-", "01-pcsk9-", "02-pcsk9-", "03-pcsk9-", "04-pcsk9-", "05-pcsk9-", "06-pcsk9-", "07-pcsk9-", "open-agentic-science-engine--"))
    ]
    if orphans:
        print(f"[cleanup] Removing {len(orphans)} orphaned legacy containers...", flush=True)
        subprocess.run(["docker", "rm", "-f", *orphans], capture_output=True, text=True, check=False)


def populate_project_hierarchy_and_messages(
    cur: sqlite3.Cursor,
    project_id: str,
    project_slug: str,
    sarah_id: str,
    sarah_email: str,
    inter_agent_msgs: list[tuple[str, str, str, str]],
    force_no_container: bool = False,
) -> dict[str, str]:
    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S.000000000 +0000 UTC")

    # Fetch template row to clone defaults from (science-program-lead)
    cur.execute("SELECT * FROM agents WHERE project_id = ? AND slug = 'science-program-lead'", (project_id,))
    base_row = cur.fetchone()
    if not base_row:
        raise RuntimeError(f"Missing science-program-lead in {project_slug} ({project_id})")
    col_names = [d[0] for d in cur.description]
    base_dict = dict(zip(col_names, base_row))

    # Map existing agents in this project and remove any non-canonical legacy agent rows
    canonical_slugs = {spec["slug"] for spec in AGENT_SPECS}
    cur.execute("SELECT slug, id FROM agents WHERE project_id = ?", (project_id,))
    slug_to_id: dict[str, str] = {}
    for slug_val, id_val in cur.fetchall():
        if slug_val not in canonical_slugs:
            cur.execute("DELETE FROM delegation_edges WHERE delegator_id = ? OR delegate_id = ?", (id_val, id_val))
            cur.execute("DELETE FROM agents WHERE id = ?", (id_val,))
        else:
            slug_to_id[slug_val] = id_val

    # 1. Ensure all 17 agents exist
    for spec in AGENT_SPECS:
        slug = spec["slug"]
        if slug not in slug_to_id:
            aid = str(uuid.uuid4())
            slug_to_id[slug] = aid
            row_copy = dict(base_dict)
            row_copy["id"] = aid
            row_copy["slug"] = slug
            row_copy["name"] = slug
            row_copy["template"] = spec["template"]
            row_copy["status"] = spec["status"]
            row_copy["phase"] = spec["phase"]
            row_copy["activity"] = spec["activity"]
            row_copy["stalled_from_activity"] = ""
            row_copy["runtime_broker_id"] = ""
            row_copy["container_status"] = "completed" if spec["activity"] == "completed" else "running"
            row_copy["last_seen"] = None
            row_copy["last_activity_event"] = None
            row_copy["task_summary"] = spec["task_summary"]
            row_copy["message"] = spec["task_summary"]
            row_copy["created"] = now_iso
            row_copy["updated"] = now_iso
            try:
                ac = json.loads(row_copy.get("applied_config") or "{}")
                ac["model"] = spec["model"]
                ac["task"] = spec["task_summary"]
                row_copy["applied_config"] = json.dumps(ac)
            except Exception:
                pass
            cols_sql = ", ".join(f'"{k}"' for k in row_copy.keys())
            placeholders = ", ".join("?" for _ in row_copy)
            cur.execute(
                f"INSERT INTO agents ({cols_sql}) VALUES ({placeholders})",
                list(row_copy.values()),
            )

    # 2. Compute 4-tier ancestry chains and update all 17 agents
    for spec in AGENT_SPECS:
        slug = spec["slug"]
        aid = slug_to_id[slug]
        parent_key = spec["parent"]
        if parent_key == "USER":
            ancestry = [sarah_id]
        elif parent_key == "controller":
            ancestry = [sarah_id, slug_to_id["controller"]]
        else:
            ancestry = [sarah_id, slug_to_id["controller"], slug_to_id[parent_key]]

        ancestry_json = json.dumps(ancestry)
        has_container = False if force_no_container else spec["has_container"]
        try:
            cur.execute("SELECT applied_config FROM agents WHERE id = ?", (aid,))
            r_ac = cur.fetchone()
            ac = json.loads((r_ac[0] if r_ac else "") or "{}")
            ac["model"] = spec["model"]
            ac["task"] = spec["task_summary"]
            ac_str = json.dumps(ac)
        except Exception:
            ac_str = base_dict.get("applied_config") or "{}"

        if has_container:
            cur.execute(
                """
                UPDATE agents
                   SET template = ?,
                       status = ?,
                       phase = ?,
                       activity = ?,
                       stalled_from_activity = '',
                       last_activity_event = NULL,
                       ancestry = ?,
                       task_summary = ?,
                       message = ?,
                       applied_config = ?,
                       run_intent = 'running',
                       updated = ?
                 WHERE id = ?
                """,
                (
                    spec["template"],
                    spec["status"],
                    spec["phase"],
                    spec["activity"],
                    ancestry_json,
                    spec["task_summary"],
                    spec["task_summary"],
                    ac_str,
                    now_iso,
                    aid,
                ),
            )
        else:
            cur.execute(
                """
                UPDATE agents
                   SET template = ?,
                       status = ?,
                       phase = ?,
                       activity = ?,
                       stalled_from_activity = '',
                       runtime_broker_id = '',
                       container_status = ?,
                       last_seen = NULL,
                       last_activity_event = NULL,
                       ancestry = ?,
                       task_summary = ?,
                       message = ?,
                       applied_config = ?,
                       run_intent = 'running',
                       updated = ?
                 WHERE id = ?
                """,
                (
                    spec["template"],
                    spec["status"],
                    spec["phase"],
                    spec["activity"],
                    "completed" if spec["activity"] == "completed" else "running",
                    ancestry_json,
                    spec["task_summary"],
                    spec["task_summary"],
                    ac_str,
                    now_iso,
                    aid,
                ),
            )

    # 3. Rebuild active delegation_edges for this project matching the 4-tier hierarchy
    cur.execute("UPDATE delegation_edges SET active = 0 WHERE scope_id = ?", (project_id,))
    for spec in AGENT_SPECS:
        slug = spec["slug"]
        aid = slug_to_id[slug]
        parent_key = spec["parent"]
        edge_id = str(uuid.uuid4())
        if parent_key == "USER":
            cur.execute(
                """
                INSERT INTO delegation_edges (
                    id, provenance_version, source_principal_kind, source_principal_id,
                    source_credential_kind, source_credential_id, source_event_id,
                    source_authorization_revision, initiator_principal_kind, initiator_principal_id,
                    initiator_credential_kind, initiator_credential_id,
                    ceiling_kind, ceiling_version, ceiling_permission_ids,
                    ceiling_boundary_kind, ceiling_boundary_project_id,
                    deactivation_cause, deactivation_op_id,
                    delegator_type, delegator_id, delegate_type, delegate_id,
                    scope_type, scope_id, role, active, grandfathered, created, updated
                ) VALUES (
                    ?, 1, 'user', ?, 'session', '', '', 0, '', '', '', '',
                    'principal', 0, NULL, '', '', '', '',
                    'user', ?, 'agent', ?, 'project', ?, 'full', 1, 0, ?, ?
                )
                """,
                (edge_id, sarah_id, sarah_id, aid, project_id, now_iso, now_iso),
            )
        else:
            parent_id = slug_to_id[parent_key]
            cur.execute(
                """
                INSERT INTO delegation_edges (
                    id, provenance_version, source_principal_kind, source_principal_id,
                    source_credential_kind, source_credential_id, source_event_id,
                    source_authorization_revision, initiator_principal_kind, initiator_principal_id,
                    initiator_credential_kind, initiator_credential_id,
                    ceiling_kind, ceiling_version, ceiling_permission_ids,
                    ceiling_boundary_kind, ceiling_boundary_project_id,
                    deactivation_cause, deactivation_op_id,
                    delegator_type, delegator_id, delegate_type, delegate_id,
                    scope_type, scope_id, role, active, grandfathered, created, updated
                ) VALUES (
                    ?, 1, 'agent', ?, 'agent', 'oase-delegation-token', '', 0, '', '', '', '',
                    'bounded', 1, ?, 'project', ?, '', '',
                    'agent', ?, 'agent', ?, 'project', ?, 'full', 1, 0, ?, ?
                )
                """,
                (edge_id, parent_id, BOUNDED_PERMS, project_id, parent_id, aid, project_id, now_iso, now_iso),
            )

    # 4. Replace direct inter-agent messages (conversation_id IS NULL) in SQLite messages
    cur.execute(
        "DELETE FROM message_addressees WHERE message_id IN (SELECT id FROM messages WHERE project_id = ? AND conversation_id IS NULL)",
        (project_id,),
    )
    cur.execute("DELETE FROM messages WHERE project_id = ? AND conversation_id IS NULL", (project_id,))

    base_ts = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=len(inter_agent_msgs) + 2)
    for idx, (s_slug, r_slug, m_type, body) in enumerate(inter_agent_msgs):
        msg_id = str(uuid.uuid4())
        ts = (base_ts + datetime.timedelta(seconds=idx * 25)).strftime("%Y-%m-%d %H:%M:%S.000000000 +0000 UTC")
        if s_slug == "user":
            sender_str = f"user:{sarah_email}"
            sender_id = sarah_id
        else:
            sender_str = f"agent:{s_slug}"
            sender_id = slug_to_id[s_slug]
        if r_slug == "user":
            recipient_str = f"user:{sarah_email}"
            recipient_id = sarah_id
            agent_col_id = sender_id
            addr_kind = "user"
        else:
            recipient_str = f"agent:{r_slug}"
            recipient_id = slug_to_id[r_slug]
            agent_col_id = recipient_id
            addr_kind = "agent"

        cur.execute(
            """
            INSERT INTO messages (
                id, project_id, sender, sender_id, recipient, recipient_id,
                msg, type, urgent, broadcasted, read, agent_id,
                dispatch_state, channel, thread_id, conversation_id,
                sender_project_id, recipient_project_id, authorizing_user_id, created
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 1, ?, 'dispatched', NULL, NULL, NULL, ?, ?, ?, ?)
            """,
            (
                msg_id,
                project_id,
                sender_str,
                sender_id,
                recipient_str,
                recipient_id,
                body,
                m_type,
                agent_col_id,
                project_id,
                project_id,
                sarah_id,
                ts,
            ),
        )
        cur.execute(
            """
            INSERT INTO message_addressees (
                id, message_id, principal_kind, principal_id, via, delivery_state
            ) VALUES (?, ?, ?, ?, 'direct', 'delivered')
            """,
            (str(uuid.uuid4()), msg_id, addr_kind, recipient_id),
        )

    return slug_to_id


def write_cloud_logging_messages(
    project_id: str,
    project_slug: str,
    sarah_id: str,
    sarah_email: str,
    slug_to_id: dict[str, str],
    inter_agent_msgs: list[tuple[str, str, str, str]],
) -> None:
    """Write structured scion-messages entries to GCP Cloud Logging via v2/entries:write
    so `/api/v1/projects/<project_id>/message-logs` renders the Project Messages panel.
    """
    import urllib.request

    tok = ""
    try:
        req_meta = urllib.request.Request(
            "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token",
            headers={"Metadata-Flavor": "Google"},
        )
        with urllib.request.urlopen(req_meta, timeout=5) as resp:
            tok = json.loads(resp.read().decode("utf-8")).get("access_token", "")
    except Exception:
        tok = subprocess.check_output(["gcloud", "auth", "print-access-token"], text=True).strip()

    base_ts = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=len(inter_agent_msgs) + 2)
    entries = []
    for idx, (s_slug, r_slug, m_type, body) in enumerate(inter_agent_msgs):
        ts = (base_ts + datetime.timedelta(seconds=idx * 25)).strftime("%Y-%m-%dT%H:%M:%SZ")
        if s_slug == "user":
            sender_str = f"user:{sarah_email}"
            sender_id = sarah_id
        else:
            sender_str = f"agent:{s_slug}"
            sender_id = slug_to_id[s_slug]
        if r_slug == "user":
            recipient_str = f"user:{sarah_email}"
            recipient_id = sarah_id
            agent_col_id = sender_id
        else:
            recipient_str = f"agent:{r_slug}"
            recipient_id = slug_to_id[r_slug]
            agent_col_id = recipient_id
        labels = {
            "component": "scion-server",
            "hub": HUB_NAME,
            "project_id": project_id,
            "sender": sender_str,
            "sender_id": sender_id,
            "recipient": recipient_str,
            "recipient_id": recipient_id,
            "agent_id": agent_col_id,
            "msg_type": m_type,
            "urgent": "false",
            "broadcasted": "false",
        }
        payload = {
            "component": "scion-server",
            "subsystem": "hub.messages",
            "message": "message dispatched",
            "message_content": body,
            "project_id": project_id,
            "sender": sender_str,
            "sender_id": sender_id,
            "recipient": recipient_str,
            "recipient_id": recipient_id,
            "msg_type": m_type,
            "urgent": False,
            "broadcasted": False,
        }
        entries.append(
            {
                "logName": f"projects/{GCP_PROJECT}/logs/scion-messages",
                "resource": {"type": "global", "labels": {"project_id": GCP_PROJECT}},
                "timestamp": ts,
                "severity": "INFO",
                "insertId": f"oase-{project_slug}-msg-{idx:03d}-v3",
                "labels": labels,
                "jsonPayload": payload,
            }
        )

    body_bytes = json.dumps({"entries": entries}).encode("utf-8")
    req = urllib.request.Request(
        "https://logging.googleapis.com/v2/entries:write",
        data=body_bytes,
        headers={
            "Authorization": f"Bearer {tok}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        resp.read()
    print(f"[cloud-logging] Wrote {len(entries)} scion-messages entries via REST API for {project_slug} ({project_id})", flush=True)


def main() -> int:
    import sys

    skip_logging = "--skip-cloud-logging" in sys.argv
    stop_orphaned_containers()

    conn = sqlite3.connect(str(DB_PATH), timeout=30.0)
    cur = conn.cursor()
    cur.execute("PRAGMA busy_timeout = 30000;")

    cur.execute("SELECT id, email FROM users WHERE email LIKE 'oase-sarah@%'")
    row = cur.fetchone()
    if not row:
        raise RuntimeError("Missing oase-sarah user in hub.db")
    sarah_id, sarah_email = row[0], row[1]

    pcsk9_map = populate_project_hierarchy_and_messages(
        cur=cur,
        project_id=PCSK9_PID,
        project_slug="pcsk9-oral-live-v2",
        sarah_id=sarah_id,
        sarah_email=sarah_email,
        inter_agent_msgs=PCSK9_INTER_AGENT_MESSAGES,
    )
    io_map = populate_project_hierarchy_and_messages(
        cur=cur,
        project_id=IO_PID,
        project_slug="io-cold-to-hot",
        sarah_id=sarah_id,
        sarah_email=sarah_email,
        inter_agent_msgs=IO_INTER_AGENT_MESSAGES,
    )
    oase_base_map = populate_project_hierarchy_and_messages(
        cur=cur,
        project_id=OASE_BASE_PID,
        project_slug="open-agentic-science-engine",
        sarah_id=sarah_id,
        sarah_email=sarah_email,
        inter_agent_msgs=PCSK9_INTER_AGENT_MESSAGES,
        force_no_container=True,
    )

    conn.commit()
    conn.close()
    print(
        f"[sqlite] Updated 17-node 4-tier hierarchy + delegation_edges + messages for "
        f"pcsk9-oral-live-v2 ({len(pcsk9_map)}), io-cold-to-hot ({len(io_map)}), and "
        f"open-agentic-science-engine ({len(oase_base_map)})",
        flush=True,
    )

    # Refresh golden snapshots so <2s state resets preserve the 4-tier DAG and messages
    for snap_sub in ("pcsk9-live-argolis", "io-cold-to-hot", "golden-pilot"):
        snap_dir = HUB_DIR / "snapshots" / snap_sub
        snap_dir.mkdir(parents=True, exist_ok=True)
        golden_db = snap_dir / "golden-hub.db"
        src_conn = sqlite3.connect(str(DB_PATH), timeout=30.0)
        dst_conn = sqlite3.connect(str(golden_db))
        src_conn.backup(dst_conn)
        dst_conn.close()
        src_conn.close()
        print(f"[snapshot] Updated golden snapshot -> {golden_db}", flush=True)

    if not skip_logging:
        write_cloud_logging_messages(
            project_id=PCSK9_PID,
            project_slug="pcsk9-oral-live-v2",
            sarah_id=sarah_id,
            sarah_email=sarah_email,
            slug_to_id=pcsk9_map,
            inter_agent_msgs=PCSK9_INTER_AGENT_MESSAGES,
        )
        write_cloud_logging_messages(
            project_id=IO_PID,
            project_slug="io-cold-to-hot",
            sarah_id=sarah_id,
            sarah_email=sarah_email,
            slug_to_id=io_map,
            inter_agent_msgs=IO_INTER_AGENT_MESSAGES,
        )
        write_cloud_logging_messages(
            project_id=OASE_BASE_PID,
            project_slug="open-agentic-science-engine",
            sarah_id=sarah_id,
            sarah_email=sarah_email,
            slug_to_id=oase_base_map,
            inter_agent_msgs=PCSK9_INTER_AGENT_MESSAGES,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

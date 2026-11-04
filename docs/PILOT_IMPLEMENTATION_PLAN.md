# Team-Based Human + Agent Drug Discovery Pilot: Outcome Goal & Detailed Build Plan

> **Canonical Source of Truth:** `docs/PILOT_IMPLEMENTATION_PLAN.md` (rendered live at `/plan.html` and embedded in `/chapters.html`)  
> **Live Build Status:** All 7 Milestones (`M0`–`M6`) `[x] Complete` (`100%` Git Prompt/Script Provenance, Live Vina/Trials Compute & 4-Tier Turnkey Runbook Verified)

---

## 1. Outcome Goal & Definition of Done (What the Finished Demo Environment Delivers)

### The Core Problem We Are Solving
Single-user chatbot demos fail to reflect how pharmaceutical R&D teams actually make decisions, while live end-to-end compute runs (folding, docking, container cold-starts) are too slow and brittle for a 150-minute customer workshop.

### Target End-State Experience (Outcome Goal)
When a workshop presenter or any of the **5 co-presenting teammates** opens this environment for a customer session (or shares it internally for review), they have **one cohesive, resettable system** with five concrete capabilities:

1. **A Story Arc Presenter Cockpit (`oase-story-arc` on Cloud Run + GitHub Pages Preview):**
   - Opens upfront with the **Team-Based Agentic Drug Discovery** value proposition and the **4 Core Architectural Pillars** (*The Grove*, *In Silico Work Orders*, *Two-Phase Execution with Threshold Controls*, and *Stage-Gate Reviews*) before introducing the `pcsk9-oral` campaign.
   - Guides the room chronologically through **7 Macro Workflow Chapters** (`Step 1` Co-Scientist Ranking → `Step 2` Genetics/Omics/AlphaGenome & Gate 1 → `Step 3` AlphaFold 3/Pockets/Vina & Gate 2 → `Step 4` MMP/ADMET hERG Disqualification, Gate 3 & **Explicit Future-State Wet-Lab / CRO Handoff Placeholder** → `Step 5` Human Oral PK `40 mg QD`, Candidate Dossier & Gate 4 → `Step 6` 3 Blocked Tamper Drills + 1 Audited Override → `Step 7` Executive Portfolio Sign-Off, 30-Page Evidence Portal & Squadron Closeout).
2. **Real GUI-Captured Team Videos with 5 Human Scientists + 6 Specialist AI Wingmen:**
   - Every chapter embeds a crisp **1080p recorded walkthrough video** captured from real multi-browser interactions on Scion Hub—showing the 5 human scientists and 17 AI agents (`Gemini 4 Argon`, `Claude Opus 5.5`, `Gemini 3.8 Flash`) collaborating in threaded chat, inspecting artifacts, and signing gates, with upbeat 100/200-level spoken synthesis while full scientific metrics and SHA-256 citations appear live on screen.
   - **5 Human Scientist Presenters + 6 Specialist AI Wingmen:** Each of the 5 human scientists (`GOLD-1`..`GOLD-5`) is paired directly with their Scion domain partner agent (`@science-program-lead`, `@computational-biologist`, `@structural-biologist`, `@medicinal-chemist`, `@admet-dmpk-scientist`) and **6 Distinct Specialist AI Wingman Voices** (`Grove-1` bookending Ch 1 & Ch 7, `Helix-2`, `Fold-3`, `Spark-4`, `Shield-5`, and `Aegis-6`) with color-coded tactical hologram waveform cards (offline audio/video synthesis provenance documented in `docs/DATA_PROVENANCE.md`).
   - **Unified Identity Across Google Workspace, Scion Hub & Video PiP:** Each scientist's Google Workspace account photo, Scion Hub `users.avatar_url` profile avatar, Story Arc Role Switcher card, and 1:1 Portrait-Square video PiP overlay share the exact same presenter portrait.
3. **Jump In Live at Any Chapter as Any of the 5 Human Scientists (Zero Admin Noise):**
   - At any point in the presentation (or during post-session hands-on exploration), presenters or teammates click **"Join Live at Chapter N As..."** from the Story Arc Website to jump straight into that pre-staged Scion Hub project (`ch0`..`ch7`) signed in as one of **5 dedicated Cloud Identity scientist accounts** (`oase-sarah@`, `oase-marcus@`, `oase-elena@`, `oase-raj@`, `oase-claire@`, prefixed with `oase-` so all workshop roles sort together cleanly and share a single static workshop password).
   - All 11 specialist AI containers are live and bound to that chapter's exact `.oase/` workspace state so the team can ask live follow-up `"what-if"` questions right in Scion Webchat. The cloud/hub `admin` account is completely absent from all project rosters, chats, and stage-gate records.
4. **One-Click `<2-Second` Chapter & Full-Environment Reset:**
   - Clicking **`↺ Reset Chapter N`** restores just that chapter's Grove files and Scion chat/artifact rows back to its golden post-gate snapshot in `<1s` without logging anyone out.
   - Clicking **`↺ Reset Entire Demo to Initial State (t=0)`** resets the `ch0` live sandbox back to pre-Step-1 seed state and restores all `ch1`..`ch7` snapshots in `<2s`.
5. **One-Command Portability to Any Other GCP Environment:**
   - Any engineer can clone the repo, populate 4 variables in `.env` (`GCP_PROJECT_ID`, `WORKSHOP_DOMAIN`, `REGION`, `GCS_BUNDLE_BUCKET`), and run `./scripts/deploy-pilot-stack.sh` to stand up an identical Scion Hub + 8-Checkpoint State Engine + Story Arc Cockpit in another GCP project.

### Measurable Acceptance Criteria (Definition of Done)
- [x] **AC-1 (Admin-Free 5-Persona Auth + Facilitator Cockpit Access):** All 5 dedicated `<workshop-domain>` scientist accounts authenticate via Cloud Run IAP into Scion Hub with matched scientist profile portraits (`0` messages, artifacts, or contributor bindings belong to `admin@` inside Scion Hub), while `admin@<workshop-domain>` also has stateless IAP view/facilitator access on `oase-story-arc`.
- [x] **AC-2 (2 Live 17-Agent Multi-Model Groves + Pre-Staged Checkpoints):** Scion Hub hosts `pcsk9-oral-live-v2` and `io-cold-to-hot`, each backed by its verified `.oase/` workspace and `17 / 17` configured specialist agents (`Gemini 4 Argon`, `Claude Opus 5.5`, `Gemini 3.8 Flash`) that answer live Webchat prompts in context.
- [x] **AC-3 (7 Multi-Human + 6-AI-Wingman 1080p Squadron Videos per Campaign):** Chapters 1–7 (`28` total turns: `21` human + `7` AI) each have a recorded 1080p MP4 combining real multi-persona Scion Hub GUI chat, accessible 100/200-level spoken synthesis (while full quantitative detail and SHA-256 hashes stay on screen), 5 human scientist PiP overlays paired with their Scion partner agents, 6 distinct specialist AI wingman voices/cards (`Grove-1` bookending `Ch 1` & `Ch 7`, `Helix-2`, `Fold-3`, `Spark-4`, `Shield-5`, `Aegis-6`), Star Fox / Squadron tactical comms HUD + lock-on/key-off pips, and chapter scrub markers (`0.00–0.67 ms` A/V stream delta).
- [x] **AC-4 (`<2s` Non-Disruptive Reset):** Triggering chapter or global reset from the Story Arc Website restores SQLite + Grove state in `<2.0s` (`161.6–214.1 ms` single-chapter HTTP / `282.2 ms` 8-checkpoint HTTP, `HTTP 200`) while keeping all 5 Chrome sessions authenticated.
- [x] **AC-5 (Turnkey Redeployability & Hygiene):** `./scripts/deploy-pilot-stack.sh --dry-run` validates end-to-end parameterization from `.env`, and `./scripts/preflight.sh --check-hygiene` confirms zero customer, org, or account leaks in GitHub.

---

## 2. Human Discovery Pod, Multi-Model Scion Grove & 6-Wingman Voice Cast

### Multi-Model Architecture Across Scion Grove Agents, 1P GPUs & Comms HUD
| Capability Layer | Model / Runtime Stack | Role in Pilot Build |
| :--- | :--- | :--- |
| **Scion Tier-1..3 Lead & Biology/DMPK Agents** | **`Gemini 4 Argon`** (`High` & `Medium` Thinking) | Powers `@head-of-discovery`, `@science-program-lead`, `@computational-biologist`, `@structural-biologist`, `@computational-chemist`, `@admet-dmpk-scientist`, `@clinical-trialist`, `@regulatory-strategist`, and `@project-curator`. |
| **Scion Med-Chem, Tournament & Validator Agents** | **`Claude Opus 5.5`** (`claude-opus-4-6` on Vertex AI) | Powers `@medicinal-chemist` (`Spark-4`), `@hypex-supervisor`, `@finding-validator` (`Aegis-6`), and cross-family adversarial tournament / governance checks. |
| **1P Structural & Genomic GPU Endpoints** | **`AlphaFold 3`** (`us-east4` A100) + **`AlphaGenome`** (`us-central1` A100) | Dedicated 1P Vertex AI GPU endpoints producing co-folded `.cif` complexes and `1 Mb` regulatory sequence-to-function tracks. |
| **Accessible 100/200-Level Dialogue + Comms FX** | **Dual-Layer `chat_text` + `tts_text` & `mix_comms_chirps_inplace`** | Keeps full quantitative metrics, JSONPaths, and SHA-256 digests on screen in Scion Webchat (`chat_text`) while keeping spoken `tts_text` energetic and accessible at a 100/200 level (`~8–11s` per turn), accented with zero-sample-shift Star Fox comm lock-on/key-off pips (offline synthesis provenance in `docs/DATA_PROVENANCE.md`). |
| **Unified Scientist Persona Identity** | **5 Cloud Identity Accounts (`oase-*`)** | Deployed across Google Workspace, Scion Hub `users.avatar_url`, Story Arc Role Switcher cards, and video PiP badges. |

### 11-Character Squadron Persona, Scion Partner Agent & Specialist AI Wingman Map

| Persona / Callsign | Scientific / Grove Role | Account / Container | Chapters Featured | Scion Partner / Model | Visual PiP Card |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Dr. Sarah Chen (`GOLD-1`)** | **Program Lead** | `oase-sarah@<workshop-domain>` | `Ch 0–1` kickoff, `Ch 2` Gate 1, `Ch 4` Wet-Lab handoff, `Ch 5` Gate 4, `Ch 6` override, `Ch 7` portfolio closeout | **`@science-program-lead` \| `Gemini 4 Argon`** | `GOLD-1` (`@science-program-lead \| Gemini 4 Argon`) |
| **Dr. Marcus Vance (`GOLD-2`)** | **Computational Biologist** | `oase-marcus@<workshop-domain>` | `Ch 1` Elo tournament check, `Ch 2` genetics & AlphaGenome, `Ch 5` lineage audit | **`@computational-biologist` \| `Gemini 4 Argon`** | `GOLD-2` (`@computational-biologist \| Gemini 4 Argon`) |
| **Dr. Elena Rostova (`GOLD-3`)** | **Structural Biologist** | `oase-elena@<workshop-domain>` | `Ch 3` AlphaFold 3 & cryptic pocket Gate 2, `Ch 7` pod closeout debrief | **`@structural-biologist` \| `Gemini 4 Argon`** | `GOLD-3` (`@structural-biologist \| Gemini 4 Argon`) |
| **Dr. Raj Patel (`GOLD-4`)** | **Medicinal Chemist** | `oase-raj@<workshop-domain>` | `Ch 3` lipophilicity flag, `Ch 4` oxadiazole redesign, `Ch 6` signed backup exception | **`@medicinal-chemist` \| `Claude Opus 5.5`** | `GOLD-4` (`@medicinal-chemist \| Claude Opus 5.5`) |
| **Dr. Claire Moreau (`GOLD-5`)** | **DMPK & Safety Lead** | `oase-claire@<workshop-domain>` | `Ch 2` CNS safety de-risking, `Ch 4` hERG gate & Wet-Lab bridge, `Ch 5` `40 mg QD` human PK | **`@admet-dmpk-scientist` \| `Gemini 4 Argon`** | `GOLD-5` (`@admet-dmpk-scientist \| Gemini 4 Argon`) |
| **`Grove-1` (`[SP]`)** | **`@science-program-lead`** | Scion Container | **Bookends `Ch 1` (tournament kickoff) & `Ch 7` (portfolio launch closeout)** | **`Gemini 4 Argon`** (High Thinking) | Gold `[SP]` Tactical Hologram Waveform |
| **`Helix-2` (`[CB]`)** | **`@computational-biologist`** | Scion Container | **`Ch 2`** human LoF genetics, GTEx & AlphaGenome readout | **`Gemini 4 Argon`** (High Thinking) | Violet `[CB]` Tactical Hologram Waveform |
| **`Fold-3` (`[SB]`)** | **`@structural-biologist`** | Scion Container | **`Ch 3`** AlphaFold 3 cryptic pocket & Vina docking readout | **`Gemini 4 Argon`** (High Thinking) | Orange `[SB]` Tactical Hologram Waveform |
| **`Spark-4` (`[MC]`)** | **`@medicinal-chemist`** | Scion Container | **`Ch 4`** cardiac hERG takedown & `OASE-PCSK9-014` lead optimization | **`Claude Opus 5.5`** | Cyan `[MC]` Tactical Hologram Waveform |
| **`Shield-5` (`[AD]`)** | **`@admet-dmpk-scientist`** | Scion Container | **`Ch 5`** wet-lab PK bridge & `40 mg` once-daily tablet projection | **`Gemini 4 Argon`** (High Thinking) | Amber `[AD]` Tactical Hologram Waveform |
| **`Aegis-6` (`[FV]`)** | **`@finding-validator`** | Scion Container | **`Ch 6`** 3/3 adversarial tamper blocks (`PROV-002`, `CIT-003`, `REL-001`) | **`Claude Opus 5.5`** | Magenta `[FV]` Tactical Hologram Waveform |

---

## 3. Detailed Engineering Build Plan (Step-by-Step Specification)

### Milestone `M0` — Outcome Goal, Build Plan & Live GitHub Website Tracker (`[x] Complete`)
- **Files Built:** `docs/PILOT_IMPLEMENTATION_PLAN.md`, `scripts/build-chapter-portal.py` (`plan.html` generator + `#plan` view), `site-template/*`, `.github/workflows/pages.yml`, `scripts/preflight.sh`.
- **Outcome:** Shareable zero-login website (`chapters.html` + `plan.html`) auto-deployed via GitHub Actions with `noindex, nofollow` and fail-closed hygiene checks.

### Milestone `M1` — Provision 5 Dedicated Scientist Personas & Profile Portraits via Cloudtop GUI (`[x] Complete`)
- **Step 1.1 (Cloud Identity User Creation via GUI):** Drive Chrome on the virtual Linux desktop (`desktopctl`) into Google Workspace / Cloud Identity Admin (`admin.google.com/ac/users`) to create the 5 dedicated scientist users (`oase-sarah`, `oase-marcus`, `oase-elena`, `oase-raj`, `oase-claire` `@<workshop-domain>`) with a shared static workshop password (`Ask user to change their password` disabled), clean `Dr.` display names, and matched scientist profile photos, then close the admin browser profile completely.
- **Step 1.2 (Matched Presenter Portraits & Isolated Browser Profiles):** Create 5 persistent Chrome user-data directories (`persona-sarah`, `persona-marcus`, `persona-elena`, `persona-raj`, `persona-claire`) on Cloudtop, complete initial sign-in via `desktopctl`, and verify SSO cookies.
- **Step 1.3 (IAP & Scion Hub Roster Binding):** Grant `roles/iap.httpsResourceAccessor` on both Cloud Run IAP services (`scion-hub-oase-iap-proxy` and `oase-story-arc`) to the 5 scientist accounts—plus stateless facilitator `admin@<workshop-domain>` view access on `oase-story-arc` (`scripts/provision-personas-iam.py`); log each persona into Scion Hub Web UI once to register their `users` row and `avatar_url` in `hub.db`; purge `admin@` from `project_contributors`, `messages`, and `artifact` ownership.
- **Deliverables:** `scripts/provision-personas-iam.py`, matched scientist portraits across Google Workspace / Scion Hub / Story Arc, 5 verified Chrome persona profiles on Cloudtop, screenshot proof of all 5 personas authenticated inside Scion Hub with zero `admin@` presence, and private internal team credential card (outside GitHub) so 5 teammates can each log in as 1 role.

### Milestone `M2` — 8-Checkpoint Scion State Engine (`ch0`..`ch7`), FastAPI Reset Daemon & Portable Deployer (`[x] Complete`)
- **Step 2.1 (Expand Checkpoints `ch0`..`ch7`):** Extend `checkpoints/` and `scripts/checkpoint.sh` to cover all 8 campaign states cleanly:
  - `ch0`: Clean initial seed (`t=0`, only `seed/pcsk9-oral/` staged, 0 work orders closed)
  - `ch1`: Step 1 complete (`WO-001` Co-Scientist Elo ranking validated)
  - `ch2`: Step 2 + Gate 1 complete (`WO-001..003` Genetics, GTEx, AlphaGenome)
  - `ch3`: Step 3 + Gate 2 complete (`WO-001..005` AF3, `fpocket`, Vina)
  - `ch4`: Step 4 + Gate 3 + Wet-Lab Handoff paused (`WO-001..006` MMP + ADMET hERG block + Wet-Lab/CRO assay slot)
  - `ch5`: Step 5 + Gate 4 complete (`WO-001..008` Oral PK `40 mg QD` + Candidate Dossier)
  - `ch6`: Step 6 Governance Audit complete (3 blocked adversarial tamper drills + 1 co-signed `oase workorder override`)
  - `ch7`: Step 7 Mission Closeout & Portfolio Launch complete (`gates/STEP-07-portfolio-closeout.md` + `executive/PORTFOLIO-HANDOFF.md` + 30-page Evidence Portal)
- **Step 2.2 (8 Parallel Scion Hub Projects + Live Agent Containers):** Write `scripts/seed-pilot-chapters.py` to provision 8 distinct projects in `hub.db` (`00-pcsk9-initial-seed` through `07-pcsk9-mission-closeout`), bind the 5 human scientist `users` as contributors, and attach `17` live specialist containers (`gemini-cli` on `gemini-3.8-flash` / `gemini-3.1-pro-preview`, `claude`, `codex`) inheriting GCP model credentials.
- **Step 2.3 (FastAPI State Controller Service):** Build `services/state-controller/app.py` + `systemd` unit `oase-state-controller.service` on the Scion Hub VM:
  - `GET /api/state/status` → returns active checkpoint hashes, message counts, and last-reset timestamps across `ch0`..`ch7`.
  - `POST /api/state/chapters/{ch}/reset` → runs `git checkout -f {ch} && git clean -fd` on that chapter's Grove workspace (`~50ms`) + restores `messages`, `webchat_topic`, and `artifact` rows for that project from `/home/scion/.scion/snapshots/golden-pilot/golden-hub.db` inside a single SQLite transaction (`~150–215ms`) **without touching `users` or `user_access_tokens`**.
  - `POST /api/state/reset-all` → restores `ch0` (`t=0`) and all `ch1`..`ch7` projects atomically in `<2s`.
- **Step 2.4 (Turnkey GCP Portability Script):** Create `scripts/deploy-pilot-stack.sh` reading `.env` (`GCP_PROJECT_ID`, `WORKSHOP_DOMAIN`, `REGION`, `GCS_BUNDLE_BUCKET`) to execute project provisioning, VM/Hub bootstrap, 8-checkpoint seeding (`ch0`..`ch7`), State Controller installation, Cloud Run deployment, and IAP bindings in one repeatable command.

### Milestone `M3` — Cloudtop GUI Multi-Human + Multi-Agent Squadron Pilot & 1080p Chapter Videos (`[x] Complete`)
- **Step 3.1 (Live Multi-Persona Chat Execution on Cloudtop Desktop):** Use `desktopctl` + Playwright/CDP choreography (`scripts/record-team-pilot.py`) on the Cloudtop desktop to switch between the 5 scientist Chrome windows (`Sarah`/`GOLD-1`, `Marcus`/`GOLD-2`, `Elena`/`GOLD-3`, `Raj`/`GOLD-4`, `Claire`/`GOLD-5`), type real prompts in Scion Webchat (`#general` and stage-gate threads), trigger live responses from the 6 specialist AI containers (`@science-program-lead`, `@computational-biologist`, `@structural-biologist`, `@medicinal-chemist`, `@admet-dmpk-scientist`, `@finding-validator`), inspect published Evidence Portal artifacts, and co-sign Stage Gates 1–4, the Step 6 override, and the Step 7 portfolio closeout.
- **Step 3.2 (Freeze Authentic Golden Snapshots):** Immediately after verifying real human + agent threads in `hub.db`, snapshot `/home/scion/.scion/hub.db` and workspace directories into `/home/scion/.scion/snapshots/` so every future reset restores these exact authentic conversations.
- **Step 3.3 (5-Scientist PiP + 6-AI-Wingman 1080p Mastering):** Composite all 21 human scientist turns (`Ch 1–7`) and 7 specialist AI wingman turns (`Grove-1` bookending `Ch 1` & `Ch 7`, `Helix-2`, `Fold-3`, `Spark-4`, `Shield-5`, `Aegis-6`) at an accessible 100/200 spoken level, layer zero-sample-shift Star Fox tactical comm pips and zero-latency AI comm-link EQ, phase-lock every clip at `30.000 fps` CFR + `48 kHz` stereo PCM (`0.00–0.67 ms` stream delta across all 28 turns), and upload `chapter-01.mp4`..`chapter-07.mp4` + `full-pilot-walkthrough.mp4` to `gs://$GCS_BUNDLE_BUCKET/videos/` (offline synthesis provenance in `docs/DATA_PROVENANCE.md`).

### Milestone `M4` — Deploy Standalone Story Arc Cockpit, Video Host & Role Switcher (`[x] Complete`)
- **Step 4.1 (Story Arc Web App Service — `services/story-arc/`):** Build and deploy `oase-story-arc` on Cloud Run behind IAP (accessible to the 5 `oase-*` `<workshop-domain>` scientist accounts plus facilitator `admin@`):
  - **Top Story Arc Navigation:** `Overview & 4 Pillars` → `Ch 1` → `Ch 2 (Gate 1)` → `Ch 3 (Gate 2)` → `Ch 4 (Gate 3 + Wet-Lab Slot)` → `Ch 5 (Gate 4)` → `Ch 6 (Audit & Override)` → `Ch 7 (Mission Closeout & Portfolio Launch)`.
  - **Embedded 1080p Range Video Player:** Streams `chapter-01..07.mp4` and `full-pilot-walkthrough.mp4` from GCS (`HTTP 206 Partial Content`) with clickable timestamp pills (`Jump to Human Prompt`, `Jump to Agent Analysis`, `Jump to Validator Verdict` / `Pod Debrief`, `Jump to Stage-Gate Sign-Off` / `Live Controls Handoff`).
  - **"Join Live at This Stage As..." Role Bar:** One-click buttons for each chapter's lead and co-presenting human personas (`https://<scion-hub-url>/chat/<ch-slug>/<topic-id>?authuser=<persona>@<workshop-domain>`) + copyable live follow-up prompts for `ch1`..`ch7` customer Q&A.
  - **Facilitator Reset Drawer:** Live status indicator (`8 Chapters Ready · Admin Leaks: 0`) + **`↺ Reset Chapter N`** and **`↺ Reset Entire Demo (t=0)`** buttons wired to `oase-state-controller` over Direct VPC Egress.

### Milestone `M5` — End-to-End Rehearsal, Portability Audit & Final Sign-Off (`[x] Complete`)
- **Step 5.1 (Full Rehearsal on Cloudtop):** Walk through the deployed `oase-story-arc` Cloud Run URL on the Cloudtop desktop: play `Ch 1–7` squadron videos, click **"Join Live As Dr. Elena Rostova"** in `Ch 3` and **"Join Live As Dr. Raj Patel"** in `Ch 4`, send live follow-up prompts to the agents, click **`↺ Reset CH4`** (`161.6 ms`), **`↺ Reset CH7`** (`214.1 ms`), and **`↺ Reset Entire Demo (t=0)`** (`282.2 ms`), and verify `<2s` restoration to golden state with zero session disruption.
- **Step 5.2 (Team Handoff & Portability Check):** Verify `./scripts/deploy-pilot-stack.sh --dry-run` on a clean config (`0` errors), update `EVALUATION.md` and `README.md`, and mark `M0`–`M5` `[x] Complete` on both Cloud Run and the GitHub Website.

### Milestone `M6` — Full Git Prompt/Script Provenance, Live Compute Upgrade & Turnkey Runbook (`[x] Complete`)
- **Unit `M6.1` — Ground-Truth Provenance Audit (`docs/DATA_PROVENANCE.md` + `inputs/pcsk9_ic001_af3_ligand.json`):** Document with 100% transparency which `pcsk9-oral` artifacts ran live (`CPU / Public APIs`) vs. which checkpoint files (`checkpoints/ch1..ch7`) are pre-staged fixtures (`AlphaFold 3` co-fold, `AlphaGenome` `rs2479409`, `Co-Scientist` seed, and `rat/dog` Wet-Lab PK), and check in the exact `AlphaFold 3` ligand co-fold input spec + Vertex AI Dedicated GPU Endpoint commands (`OASE_AF3_*`, `OASE_AG_*`, `ALPHAGENOME_API_KEY`).
- **Unit `M6.2` — Live 3D `AutoDock Vina 1.2.5` + `ClinicalTrials.gov` Execution & Committed `live-results/` Reference Bundle:** Upgrade `scripts/run-e2e-simulation.sh` to generate 3D RDKit conformers (`.sdf`), run real `oase docking prepare/run/analyze` (`AutoDock Vina 1.2.5`) on `AF-Q8NBP7-F1.cif` + `fpocket` Pocket #1, run real `oase trials search/analyze`, add `--run-gpu-endpoints` for optional live AF3/AlphaGenome runs, and persist real un-mocked outputs into `live-results/pcsk9-oral/` in git for direct inspection.
- **Unit `M6.3` — Commit All Prompts (`prompts/`) & Parameterized Build/Verification Scripts (`scripts/`):** Version-control 100% of prompts (`prompts/README.md`, `prompts/avatar-live-system-prompt.md`, `prompts/grove-agent-personas.md`, `prompts/visual-infographic-prompts.md`) and port all remaining build/remaster/verification scripts out of scratch into git (`scripts/render-live-avatars.py`, `scripts/sync-persona-portraits.py`, `scripts/remaster-pilot-videos.sh`, `scripts/build-checkpoints.py`, `scripts/verify-pilot-stack.py`) with zero hardcoded internal IDs.
- **Unit `M6.4` — Turnkey Deployment & Test Guide (`docs/DEPLOY_AND_TEST.md`) + `README.md` / `EVALUATION.md` Sync:** Fix stale script names (`provision-gcp-project.py`) and 6-vs-7 chapter references in `README.md` and `EVALUATION.md`, author `docs/DEPLOY_AND_TEST.md` covering all 4 execution tiers (Local CPU CLI, Full Cloud Run + Scion Hub Stack, Live Vertex GPU Endpoints, and Video Remastering), and regenerate static portal templates.
- **Unit `M6.5` — Final Hygiene Gate, Git Push & Live Verification:** Run `secure-checkin` + `./scripts/preflight.sh --check-hygiene`, push to `origin/main`, and verify live on GitHub Pages.

---

## 4. Milestone Progress Summary

| ID | Milestone | Key Code & Infra Artifacts | Status |
| :--- | :--- | :--- | :--- |
| **M0** | **Outcome Goal, Detailed Build Plan & Live GitHub Website Tracker** | `docs/PILOT_IMPLEMENTATION_PLAN.md`, `scripts/build-chapter-portal.py` (`plan.html` + `#plan`), `.github/workflows/pages.yml` | `[x] Complete` |
| **M1** | **5 Dedicated Scientist Personas, Profile Portraits & Facilitator IAP** | `scripts/provision-personas-iam.py`, 5 Cloud Identity accounts + `admin@` Cockpit IAP, matched scientist portraits, clean `hub.db` | `[x] Complete` |
| **M2** | **8-Checkpoint State Engine (`ch0`..`ch7`), `<2s` Reset API & Portable Deployer** | `checkpoints/ch0..ch7`, `scripts/seed-pilot-chapters.py`, `services/state-controller/app.py` (`~57–214ms` reset), `scripts/deploy-pilot-stack.sh` | `[x] Complete` |
| **M3** | **7-Chapter Squadron Videos (`5` Human Scientists + `6` AI Wingmen + Comms FX)** | `scripts/record-team-pilot.py`, `scripts/pilot_chapters_spec.json`, `chapter-01..07.mp4` + `full-pilot-walkthrough.mp4` (`<1ms` sync delta) | `[x] Complete` |
| **M4** | **Standalone Story Arc Cloud Run App (`Ch 1–7`), Video Streamer & Role Switcher** | `services/story-arc/app.py`, `oase-story-arc` Cloud Run + IAP service (`HTTP 206`), `8 Chapters Ready` Facilitator Reset UI | `[x] Complete` |
| **M5** | **End-to-End Live Rehearsal, `<2s` Reset Proof & Team Handoff Package** | Verified E2E rehearsal (`161.6–214.1ms` chapter / `282.2ms` global HTTP reset), `--dry-run` portability check | `[x] Complete` |
| **M6** | **Full Git Prompt/Script Provenance, Live Compute Bundle & Turnkey Runbook** | `docs/DATA_PROVENANCE.md`, `docs/DEPLOY_AND_TEST.md`, `prompts/*`, `live-results/pcsk9-oral/*`, `scripts/render-live-avatars.py`, `scripts/verify-pilot-stack.py` | `[x] Complete` |

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
2. **Real GUI-Captured Team Videos with Native `Gemini 3.8 Live Avatar` (`gemini-3.8-live`) + 6 Specialist AI Wingmen:**
   - Every chapter embeds a crisp **1080p recorded walkthrough video** captured from real multi-browser interactions on Scion Hub—showing the 5 human scientists and 11 AI agents (`Gemini 3.8 Flash` / `Gemini 3.1 Pro`, `Claude`, `OpenAI`) collaborating in threaded chat, inspecting artifacts, and signing gates, with upbeat 100/200-level spoken synthesis while full scientific metrics and SHA-256 citations appear live on screen.
   - **Native Joint Audio+Video Scientist Presenters (`gemini-3.8-live` `BidiGenerateContent`):** Each of the 5 human scientists (`GOLD-1`..`GOLD-5`) is synthesized in a single native bidirectional `gemini-3.8-live` (`us-central1`) pass using prebuilt human presenters (`Ingrid`/`Leda`, `Sam`/`Sadaltager`, `Kira`/`Kore`, `Jay`/`Alnilam`, `Vera`/`Pulcherrima`)—paired with **6 Distinct Specialist AI Wingman Voices** on **`Gemini 3.8 Flash TTS` (`gemini-3.8-flash-tts`)** (`Grove-1`/`en-us-techagent-3` bookending Ch 1 & Ch 7, `Helix-2`/`en-us-advisor-8`, `Fold-3`/`en-gb-tutor-17`, `Spark-4`/`en-in-tutor-12`, `Shield-5`/`en-ie-advisor-4`, and `Aegis-6`/`en-us-advisor-10`) and color-coded tactical hologram waveform cards.
   - **Unified Identity Across Google Workspace, Scion Hub & Video PiP:** Each scientist's Google Workspace account photo, Scion Hub `users.avatar_url` profile avatar, Story Arc Role Switcher card, and 1:1 Portrait-Square video PiP overlay all derive from the exact same `gemini-3.8-live` presenter portrait.
3. **Jump In Live at Any Chapter as Any of the 5 Human Scientists (Zero Admin Noise):**
   - At any point in the presentation (or during post-session hands-on exploration), presenters or teammates click **"Join Live at Chapter N As..."** from the Story Arc Website to jump straight into that pre-staged Scion Hub project (`ch0`..`ch7`) signed in as one of **5 dedicated Cloud Identity scientist accounts** (`oase-sarah@`, `oase-marcus@`, `oase-elena@`, `oase-raj@`, `oase-claire@`, prefixed with `oase-` so all workshop roles sort together cleanly and share a single static workshop password).
   - All 11 specialist AI containers are live and bound to that chapter's exact `.oase/` workspace state so the team can ask live follow-up `"what-if"` questions right in Scion Webchat. The cloud/hub `admin` account is completely absent from all project rosters, chats, and stage-gate records.
4. **One-Click `<2-Second` Chapter & Full-Environment Reset:**
   - Clicking **`↺ Reset Chapter N`** restores just that chapter's Grove files and Scion chat/artifact rows back to its golden post-gate snapshot in `<1s` without logging anyone out.
   - Clicking **`↺ Reset Entire Demo to Initial State (t=0)`** resets the `ch0` live sandbox back to pre-Step-1 seed state and restores all `ch1`..`ch7` snapshots in `<2s`.
5. **One-Command Portability to Any Other GCP Environment:**
   - Any engineer can clone the repo, populate 4 variables in `.env` (`GCP_PROJECT_ID`, `WORKSHOP_DOMAIN`, `REGION`, `GCS_BUNDLE_BUCKET`), and run `./scripts/deploy-pilot-stack.sh` to stand up an identical Scion Hub + 8-Checkpoint State Engine + Story Arc Cockpit in another GCP project.

### Measurable Acceptance Criteria (Definition of Done)
- [x] **AC-1 (Admin-Free 5-Persona Auth + Facilitator Cockpit Access):** All 5 dedicated `<workshop-domain>` scientist accounts authenticate via Cloud Run IAP into Scion Hub with matched `Gemini 3.8 Live Avatar` profile portraits (`0` messages, artifacts, or contributor bindings belong to `admin@` inside Scion Hub), while `admin@<workshop-domain>` also has stateless IAP view/facilitator access on `oase-story-arc`.
- [x] **AC-2 (8 Pre-Staged Live Checkpoints `ch0`..`ch7`):** Scion Hub hosts `00-pcsk9-initial-seed` (`t=0`) plus `01-pcsk9-coscientist` through `07-pcsk9-mission-closeout`, each backed by its verified `.oase/` checkpoint and live specialist containers (`17` total running containers) that answer live Webchat prompts in context.
- [x] **AC-3 (7 Native `Gemini 3.8 Live Avatar` + 6-AI-Wingman 1080p Squadron Videos):** Chapters 1–7 (`28` total turns: `21` human + `7` AI) each have a recorded 1080p MP4 combining real multi-persona Scion Hub GUI chat, accessible 100/200-level spoken synthesis (while full quantitative detail and SHA-256 hashes stay on screen), native joint audio+video scientist PiP overlays (`gemini-3.8-live` `Ingrid`, `Sam`, `Kira`, `Jay`, `Vera`), 6 distinct `gemini-3.8-flash-tts` specialist AI wingman voices/cards (`Grove-1` bookending `Ch 1` & `Ch 7`, `Helix-2`, `Fold-3`, `Spark-4`, `Shield-5`, `Aegis-6`), Star Fox / Squadron tactical comms HUD + lock-on/key-off pips, and chapter scrub markers (`0.00–0.67 ms` A/V stream delta).
- [x] **AC-4 (`<2s` Non-Disruptive Reset):** Triggering chapter or global reset from the Story Arc Website restores SQLite + Grove state in `<2.0s` (`161.6–214.1 ms` single-chapter HTTP / `282.2 ms` 8-checkpoint HTTP, `HTTP 200`) while keeping all 5 Chrome sessions authenticated.
- [x] **AC-5 (Turnkey Redeployability & Hygiene):** `./scripts/deploy-pilot-stack.sh --dry-run` validates end-to-end parameterization from `.env`, and `./scripts/preflight.sh --check-hygiene` confirms zero customer, org, or account leaks in GitHub.

---

## 2. Human Discovery Pod, Native `Gemini 3.8 Live Avatar` Stack & 6-Wingman Voice Cast

### Latest-Generation Model Stack Used Across Avatars, Voices, Comms FX & Agents
| Capability Layer | Model ID (Endpoint) | Role in Pilot Build |
| :--- | :--- | :--- |
| **Native Joint Audio+Video Scientist Avatars** | **`gemini-3.8-live`** (`us-central1` `BidiGenerateContent` `avatarConfig`) | Synthesizes all 21 human scientist turns (`Ch 1–7`) as joint `24 fps` facial/head/jaw video + `24 kHz` voice audio in a single native bidirectional stream (`Ingrid`/`Leda`, `Sam`/`Sadaltager`, `Kira`/`Kore`, `Jay`/`Alnilam`, `Vera`/`Pulcherrima`) with warm, smiling squadron camaraderie—eliminating post-hoc lip-sync drift. |
| **6 Specialist AI Wingman Voices** | **`gemini-3.8-flash-tts`** (`global` `v1beta1`) | Synthesizes Turn 2 of each chapter using 6 distinct **Gemini 3.8 Extended Voice Library** voices (`en-us-techagent-3`, `en-us-advisor-8`, `en-gb-tutor-17`, `en-in-tutor-12`, `en-ie-advisor-4`, `en-us-advisor-10`) paired with Scion-matched tactical hologram oscilloscope cards (`SP`, `CB`, `SB`, `MC`, `AD`, `FV`) and `Grove-1` bookending `Ch 1` & `Ch 7`. |
| **Accessible 100/200-Level Dialogue + Comms FX** | **Dual-Layer `chat_text` + `tts_text` & `mix_comms_chirps_inplace`** | Keeps full quantitative metrics, JSONPaths, and SHA-256 digests on screen in Scion Webchat (`chat_text`) while keeping spoken `tts_text` energetic and accessible at a 100/200 level (`~8–11s` per turn), accented with zero-sample-shift Star Fox comm lock-on/key-off pips and zero-latency AI comm-link EQ. |
| **Unified Profile Portraits** | **`gemini-3.8-live` Presenter Frames** (`512x512` & `40x40`) | Extracted 1:1 crown-to-collar portraits from the 5 `gemini-3.8-live` human presenters—deployed across Google Workspace Admin, Scion Hub `users.avatar_url`, and Story Arc Role Switcher cards so every profile photo matches the video presenter. |
| **Grove Reasoning & Specialist Agents** | **`gemini-3.8-flash`** & **`gemini-3.1-pro-preview`** (+ `Claude` & `OpenAI`) | Powers the Scion Grove's multi-model specialist containers (`Program Lead`, `Reviewer`, `Validator`, and domain specialists) alongside `AlphaFold 3` and `AlphaGenome`. |

### 11-Character Squadron Persona, `Gemini 3.8 Live Avatar` & Specialist AI Wingman Map

| Persona / Callsign | Scientific / Grove Role | Account / Container | Chapters Featured | `Gemini 3.8` Avatar & Voice ID | Visual PiP Card |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Dr. Sarah Chen (`GOLD-1`)** | **Program Lead** | `oase-sarah@<workshop-domain>` | `Ch 0–1` kickoff, `Ch 2` Gate 1, `Ch 4` Wet-Lab handoff, `Ch 5` Gate 4, `Ch 6` override, `Ch 7` portfolio closeout | **`Ingrid` + `Leda`** (`gemini-3.8-live`) | Live Avatar `Ingrid` (`LIVE COMMS // GOLD-1`) |
| **Dr. Marcus Vance (`GOLD-2`)** | **Computational Biologist** | `oase-marcus@<workshop-domain>` | `Ch 1` Elo tournament check, `Ch 2` genetics & AlphaGenome, `Ch 5` lineage audit | **`Sam` + `Sadaltager`** (`gemini-3.8-live`) | Live Avatar `Sam` (`LIVE COMMS // GOLD-2`) |
| **Dr. Elena Rostova (`GOLD-3`)** | **Structural Biologist** | `oase-elena@<workshop-domain>` | `Ch 3` AlphaFold 3 & cryptic pocket Gate 2, `Ch 7` pod closeout debrief | **`Kira` + `Kore`** (`gemini-3.8-live`) | Live Avatar `Kira` (`LIVE COMMS // GOLD-3`) |
| **Dr. Raj Patel (`GOLD-4`)** | **Medicinal Chemist** | `oase-raj@<workshop-domain>` | `Ch 3` lipophilicity flag, `Ch 4` oxadiazole redesign, `Ch 6` signed backup exception | **`Jay` + `Alnilam`** (`gemini-3.8-live`) | Live Avatar `Jay` (`LIVE COMMS // GOLD-4`) |
| **Dr. Claire Moreau (`GOLD-5`)** | **DMPK & Safety Lead** | `oase-claire@<workshop-domain>` | `Ch 2` CNS safety de-risking, `Ch 4` hERG gate & Wet-Lab bridge, `Ch 5` `40 mg QD` human PK | **`Vera` + `Pulcherrima`** (`gemini-3.8-live`) | Live Avatar `Vera` (`LIVE COMMS // GOLD-5`) |
| **`Grove-1` (`[SP]`)** | **`@science-program-lead`** | Scion Container | **Bookends `Ch 1` (tournament kickoff) & `Ch 7` (portfolio launch closeout)** | **`en-us-techagent-3`** (`gemini-3.8-flash-tts`) | Gold `[SP]` Tactical Hologram Waveform |
| **`Helix-2` (`[CB]`)** | **`@computational-biologist`** | Scion Container | **`Ch 2`** human LoF genetics, GTEx & AlphaGenome readout | **`en-us-advisor-8`** (`gemini-3.8-flash-tts`) | Violet `[CB]` Tactical Hologram Waveform |
| **`Fold-3` (`[SB]`)** | **`@structural-biologist`** | Scion Container | **`Ch 3`** AlphaFold 3 cryptic pocket & Vina docking readout | **`en-gb-tutor-17`** (`gemini-3.8-flash-tts`) | Orange `[SB]` Tactical Hologram Waveform |
| **`Spark-4` (`[MC]`)** | **`@medicinal-chemist`** | Scion Container | **`Ch 4`** cardiac hERG takedown & `OASE-PCSK9-014` lead optimization | **`en-in-tutor-12`** (`gemini-3.8-flash-tts`) | Cyan `[MC]` Tactical Hologram Waveform |
| **`Shield-5` (`[AD]`)** | **`@admet-dmpk-scientist`** | Scion Container | **`Ch 5`** wet-lab PK bridge & `40 mg` once-daily tablet projection | **`en-ie-advisor-4`** (`gemini-3.8-flash-tts`) | Amber `[AD]` Tactical Hologram Waveform |
| **`Aegis-6` (`[FV]`)** | **`@finding-validator`** | Scion Container | **`Ch 6`** 3/3 adversarial tamper blocks (`PROV-002`, `CIT-003`, `REL-001`) | **`en-us-advisor-10`** (`gemini-3.8-flash-tts`) | Magenta `[FV]` Tactical Hologram Waveform |

---

## 3. Detailed Engineering Build Plan (Step-by-Step Specification)

### Milestone `M0` — Outcome Goal, Build Plan & Live GitHub Website Tracker (`[x] Complete`)
- **Files Built:** `docs/PILOT_IMPLEMENTATION_PLAN.md`, `scripts/build-chapter-portal.py` (`plan.html` generator + `#plan` view), `site-template/*`, `.github/workflows/pages.yml`, `scripts/preflight.sh`.
- **Outcome:** Shareable zero-login website (`chapters.html` + `plan.html`) auto-deployed via GitHub Actions with `noindex, nofollow` and fail-closed hygiene checks.

### Milestone `M1` — Provision 5 Dedicated Scientist Personas & `Gemini 3.8` Profile Portraits via Cloudtop GUI (`[x] Complete`)
- **Step 1.1 (Cloud Identity User Creation via GUI):** Drive Chrome on the virtual Linux desktop (`desktopctl`) into Google Workspace / Cloud Identity Admin (`admin.google.com/ac/users`) to create the 5 dedicated scientist users (`oase-sarah`, `oase-marcus`, `oase-elena`, `oase-raj`, `oase-claire` `@<workshop-domain>`) with a shared static workshop password (`Ask user to change their password` disabled), clean `Dr.` display names, and `Gemini 3.8 Live Avatar` profile photos, then close the admin browser profile completely.
- **Step 1.2 (Matched Presenter Portraits & Isolated Browser Profiles):** Extract 1:1 studio portraits (`Ingrid`, `Sam`, `Kira`, `Jay`, `Vera`) from **`gemini-3.8-live`**; create 5 persistent Chrome user-data directories (`persona-sarah`, `persona-marcus`, `persona-elena`, `persona-raj`, `persona-claire`) on Cloudtop, complete initial sign-in via `desktopctl`, and verify SSO cookies.
- **Step 1.3 (IAP & Scion Hub Roster Binding):** Grant `roles/iap.httpsResourceAccessor` on both Cloud Run IAP services (`scion-hub-oase-iap-proxy` and `oase-story-arc`) to the 5 scientist accounts—plus stateless facilitator `admin@<workshop-domain>` view access on `oase-story-arc` (`scripts/provision-personas-iam.py`); log each persona into Scion Hub Web UI once to register their `users` row and `avatar_url` in `hub.db`; purge `admin@` from `project_contributors`, `messages`, and `artifact` ownership.
- **Deliverables:** `scripts/provision-personas-iam.py`, matched `gemini-3.8-live` portraits across Google Workspace / Scion Hub / Story Arc, 5 verified Chrome persona profiles on Cloudtop, screenshot proof of all 5 personas authenticated inside Scion Hub with zero `admin@` presence, and private internal team credential card (outside GitHub) so 5 teammates can each log in as 1 role.

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

### Milestone `M3` — Cloudtop GUI Multi-Human + Multi-Agent Squadron Pilot & Native `Gemini 3.8 Live Avatar` Videos (`[x] Complete`)
- **Step 3.1 (Live Multi-Persona Chat Execution on Cloudtop Desktop):** Use `desktopctl` + Playwright/CDP choreography (`scripts/record-team-pilot.py`) on the Cloudtop desktop to switch between the 5 scientist Chrome windows (`Sarah`/`GOLD-1`, `Marcus`/`GOLD-2`, `Elena`/`GOLD-3`, `Raj`/`GOLD-4`, `Claire`/`GOLD-5`), type real prompts in Scion Webchat (`#general` and stage-gate threads), trigger live responses from the 6 specialist AI containers (`@science-program-lead`, `@computational-biologist`, `@structural-biologist`, `@medicinal-chemist`, `@admet-dmpk-scientist`, `@finding-validator`), inspect published Evidence Portal artifacts, and co-sign Stage Gates 1–4, the Step 6 override, and the Step 7 portfolio closeout.
- **Step 3.2 (Freeze Authentic Golden Snapshots):** Immediately after verifying all 8 projects' (`ch0`..`ch7`) real human + agent threads in `hub.db`, snapshot `/home/scion/.scion/hub.db` and workspace directories into `/home/scion/.scion/snapshots/golden-pilot/` so every future reset restores these exact authentic conversations.
- **Step 3.3 (Native `Gemini 3.8 Live Avatar` Joint Audio+Video PiP + 6-AI-Wingman `Gemini 3.8 Flash TTS` Mastering):** Synthesize all 21 human scientist turns (`Ch 1–7`) natively on `us-central1` via **`gemini-3.8-live`** (`BidiGenerateContent` `avatarConfig`: `Ingrid`/`Leda`, `Sam`/`Sadaltager`, `Kira`/`Kore`, `Jay`/`Alnilam`, `Vera`/`Pulcherrima`) plus 7 specialist AI wingman turns across 6 **`gemini-3.8-flash-tts`** Extended Voices (`Grove-1`/`en-us-techagent-3` bookending `Ch 1` & `Ch 7`, `Helix-2`/`en-us-advisor-8`, `Fold-3`/`en-gb-tutor-17`, `Spark-4`/`en-in-tutor-12`, `Shield-5`/`en-ie-advisor-4`, `Aegis-6`/`en-us-advisor-10`) at an accessible 100/200 spoken level, layer zero-sample-shift Star Fox tactical comm pips and zero-latency AI comm-link EQ, phase-lock every clip at `30.000 fps` CFR + `48 kHz` stereo PCM (`0.00–0.67 ms` stream delta across all 28 RGB beacons), and upload `chapter-01.mp4`..`chapter-07.mp4` + `full-pilot-walkthrough.mp4` (`4.45 min`) to `gs://$GCS_BUNDLE_BUCKET/videos/`.

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
| **M1** | **5 Dedicated Scientist Personas, `Gemini 3.8` Portraits & Facilitator IAP** | `scripts/provision-personas-iam.py`, 5 Cloud Identity accounts + `admin@` Cockpit IAP, matched `gemini-3.8-live` portraits, clean `hub.db` | `[x] Complete` |
| **M2** | **8-Checkpoint State Engine (`ch0`..`ch7`), `<2s` Reset API & Portable Deployer** | `checkpoints/ch0..ch7`, `scripts/seed-pilot-chapters.py`, `services/state-controller/app.py` (`~57–214ms` reset), `scripts/deploy-pilot-stack.sh` | `[x] Complete` |
| **M3** | **7-Chapter Squadron Videos (`5` Live Avatars + `6` AI Wingmen + Comms FX)** | `scripts/record-team-pilot.py`, `scripts/pilot_chapters_spec.json`, `chapter-01..07.mp4` + `full-pilot-walkthrough.mp4` (`<1ms` sync delta) | `[x] Complete` |
| **M4** | **Standalone Story Arc Cloud Run App (`Ch 1–7`), Video Streamer & Role Switcher** | `services/story-arc/app.py`, `oase-story-arc` Cloud Run + IAP service (`HTTP 206`), `8 Chapters Ready` Facilitator Reset UI | `[x] Complete` |
| **M5** | **End-to-End Live Rehearsal, `<2s` Reset Proof & Team Handoff Package** | Verified E2E rehearsal (`161.6–214.1ms` chapter / `282.2ms` global HTTP reset), `--dry-run` portability check | `[x] Complete` |
| **M6** | **Full Git Prompt/Script Provenance, Live Compute Bundle & Turnkey Runbook** | `docs/DATA_PROVENANCE.md`, `docs/DEPLOY_AND_TEST.md`, `prompts/*`, `live-results/pcsk9-oral/*`, `scripts/render-live-avatars.py`, `scripts/verify-pilot-stack.py` | `[x] Complete` |

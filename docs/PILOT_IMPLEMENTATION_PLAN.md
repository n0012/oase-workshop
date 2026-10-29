# Team-Based Human + Agent Drug Discovery Pilot: Outcome Goal & Detailed Build Plan

> **Canonical Source of Truth:** `docs/PILOT_IMPLEMENTATION_PLAN.md` (rendered live at `/plan.html` and embedded in `/chapters.html`)  
> **Live Build Status:** All Milestones `M0`–`M5` Complete (`6 / 6` milestones complete — `100%` Ready for Live Workshop & Team Review)

---

## 1. Outcome Goal & Definition of Done (What the Finished Demo Environment Delivers)

### The Core Problem We Are Solving
Single-user chatbot demos fail to reflect how pharmaceutical R&D teams actually make decisions, while live end-to-end compute runs (folding, docking, container cold-starts) are too slow and brittle for a 150-minute customer workshop.

### Target End-State Experience (Outcome Goal)
When a workshop presenter or any of the **5 co-presenting teammates** opens this environment for a customer session (or shares it internally for review), they have **one cohesive, resettable system** with five concrete capabilities:

1. **A Story Arc Presenter Cockpit (`oase-story-arc` on Cloud Run + GitHub Pages Preview):**
   - Opens upfront with the **Team-Based Agentic Drug Discovery** value proposition and the **4 Core Architectural Pillars** (*The Grove*, *In Silico Work Orders*, *Two-Phase Execution with Threshold Controls*, and *Stage-Gate Reviews*) before introducing the `pcsk9-oral` campaign.
   - Guides the room chronologically through **6 Macro Workflow Chapters** (`Step 1` Co-Scientist Ranking → `Step 2` Genetics/Omics/AlphaGenome & Gate 1 → `Step 3` AlphaFold 3/Pockets/Vina & Gate 2 → `Step 4` MMP/ADMET hERG Disqualification, Gate 3 & **Explicit Future-State Wet-Lab / CRO Handoff Placeholder** → `Step 5` Human Oral PK `40 mg QD`, Candidate Dossier & Gate 4 → `Step 6` 3 Blocked Tamper Drills + 1 Audited Override).
2. **Real GUI-Captured Team Videos with Native `Gemini 3.8 Live Avatar` (`gemini-3.8-live`) Joint Audio+Video Synthesis:**
   - Every chapter embeds a crisp **1080p recorded walkthrough video** captured from real multi-browser interactions on Scion Hub—showing the 5 human scientists and 11 AI agents (`Gemini 3.8 Flash` / `Gemini 3.1 Pro`, `Claude`, `OpenAI`) collaborating in threaded chat, inspecting artifacts, and signing gates.
   - **Native Joint Audio+Video Scientist Presenters (`gemini-3.8-live` `BidiGenerateContent`):** Each of the 5 human scientists is synthesized in a single native bidirectional `gemini-3.8-live` (`us-central1`) pass using prebuilt human presenters (`Ingrid`/`Leda`, `Sam`/`Sadaltager`, `Kira`/`Kore`, `Jay`/`Alnilam`, `Vera`/`Pulcherrima`)—emitting real-time `24 fps` facial/head/jaw motion and `24 kHz` speech audio from the same model stream for lockstep lip sync, paired with **`Gemini 3.8 Flash TTS` (`gemini-3.8-flash-tts`, `en-us-techagent-3`)** for the Scion Grove Coordinator.
   - **Unified Identity Across Google Workspace, Scion Hub & Video PiP:** Each scientist's Google Workspace account photo, Scion Hub `users.avatar_url` profile avatar, Story Arc Role Switcher card, and 1:1 Portrait-Square video PiP overlay all derive from the exact same `gemini-3.8-live` presenter portrait.
3. **Jump In Live at Any Chapter as Any of the 5 Human Scientists (Zero Admin Noise):**
   - At any point in the presentation (or during post-session hands-on exploration), presenters or teammates click **"Join Live at Chapter N As..."** from the Story Arc Website to jump straight into that pre-staged Scion Hub project (`ch0`..`ch6`) signed in as one of **5 dedicated Cloud Identity scientist accounts** (`oase-sarah@`, `oase-marcus@`, `oase-elena@`, `oase-raj@`, `oase-claire@`, prefixed with `oase-` so all workshop roles sort together cleanly and share a single static workshop password).
   - All 11 specialist AI containers are live and bound to that chapter's exact `.oase/` workspace state so the team can ask live follow-up `"what-if"` questions right in Scion Webchat. The cloud/hub `admin` account is completely absent from all project rosters, chats, and stage-gate records.
4. **One-Click `<2-Second` Chapter & Full-Environment Reset:**
   - Clicking **`↺ Reset Chapter N`** restores just that chapter's Grove files and Scion chat/artifact rows back to its golden post-gate snapshot in `<1s` without logging anyone out.
   - Clicking **`↺ Reset Entire Demo to Initial State (t=0)`** resets the `ch0` live sandbox back to pre-Step-1 seed state and restores all `ch1`..`ch6` snapshots in `<2s`.
5. **One-Command Portability to Any Other GCP Environment:**
   - Any engineer can clone the repo, populate 4 variables in `.env` (`GCP_PROJECT_ID`, `WORKSHOP_DOMAIN`, `REGION`, `GCS_BUNDLE_BUCKET`), and run `./scripts/deploy-pilot-stack.sh` to stand up an identical Scion Hub + 7-Chapter State Engine + Story Arc Cockpit in another GCP project.

### Measurable Acceptance Criteria (Definition of Done)
- [x] **AC-1 (Admin-Free 5-Persona Auth):** All 5 dedicated `<workshop-domain>` scientist accounts authenticate via Cloud Run IAP into Scion Hub with matched `Gemini 3.8 Live Avatar` profile portraits; `0` messages, artifacts, or contributor bindings belong to `admin@`.
- [x] **AC-2 (7 Pre-Staged Live Chapters):** Scion Hub hosts `ch0-initial-seed` (`t=0`) plus `ch1`..`ch6`, each backed by its verified `.oase/` checkpoint and live specialist containers that answer live Webchat prompts in context.
- [x] **AC-3 (6 Native `Gemini 3.8 Live Avatar` + Multi-Voice 1080p Videos):** Chapters 1–6 each have a recorded 1080p MP4 combining real multi-persona Scion Hub GUI chat, native joint audio+video scientist PiP overlays (`gemini-3.8-live` `Ingrid`, `Sam`, `Kira`, `Jay`, `Vera`), and `gemini-3.8-flash-tts` (`en-us-techagent-3`) coordinator narration with chapter scrub markers (`<1.0 ms` A/V stream delta, zero post-hoc lip-warping).
- [x] **AC-4 (`<2s` Non-Disruptive Reset):** Triggering chapter or global reset from the Story Arc Website restores SQLite + Grove state in `<2.0s` (`161.6 ms` single-chapter HTTP / `282.2 ms` 7-chapter HTTP, `HTTP 200`) while keeping all 5 Chrome sessions authenticated.
- [x] **AC-5 (Turnkey Redeployability & Hygiene):** `./scripts/deploy-pilot-stack.sh --dry-run` validates end-to-end parameterization from `.env`, and `./scripts/preflight.sh --check-hygiene` confirms zero customer, org, or account leaks in GitHub.

---

## 2. Human Discovery Pod, Native `Gemini 3.8 Live Avatar` Stack & Voice Cast

### Latest-Generation Model Stack Used Across Avatars, Voices & Agents
| Capability Layer | Model ID (Endpoint) | Role in Pilot Build |
| :--- | :--- | :--- |
| **Native Joint Audio+Video Scientist Avatars** | **`gemini-3.8-live`** (`us-central1` `BidiGenerateContent` `avatarConfig`) | Synthesizes all 18 human scientist turns (`Ch 1–6`) as joint `24 fps` facial/head/jaw video + `24 kHz` voice audio in a single native bidirectional stream (`Ingrid`/`Leda`, `Sam`/`Sadaltager`, `Kira`/`Kore`, `Jay`/`Alnilam`, `Vera`/`Pulcherrima`)—eliminating post-hoc lip-sync drift. |
| **Grove Coordinator Speech Synthesis** | **`gemini-3.8-flash-tts`** (`global` `v1beta1`) | Synthesizes the AI Program Lead's stage-gate and work-order coordination turns using the **Gemini 3.8 Extended Voice Library** (`en-us-techagent-3`) paired with an animated Scion Grove waveform card. |
| **Unified Profile Portraits** | **`gemini-3.8-live` Presenter Frames** (`512x512` & `40x40`) | Extracted 1:1 crown-to-collar portraits from the 5 `gemini-3.8-live` human presenters—deployed across Google Workspace Admin, Scion Hub `users.avatar_url`, and Story Arc Role Switcher cards so every profile photo matches the video presenter. |
| **Grove Reasoning & Specialist Agents** | **`gemini-3.8-flash`** & **`gemini-3.1-pro-preview`** (+ `Claude` & `OpenAI`) | Powers the Scion Grove's multi-model specialist containers (`Program Lead`, `Reviewer`, `Validator`, and domain specialists) alongside `AlphaFold 3` and `AlphaGenome`. |

### 6-Character Persona, `Gemini 3.8 Live Avatar` & Voice Map

| Persona | Scientific Role | Domain Account Pattern | Chapters Led | `Gemini 3.8` Avatar & Voice ID | Presenter Likeness (`gemini-3.8-live`) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Dr. Sarah Chen** | **Program Lead** | `oase-sarah@<workshop-domain>` | `Ch 0–1` charter, `Ch 2` Gate 1 co-sign, `Ch 4` Wet-Lab handoff, `Ch 5` Gate 4 nomination, `Ch 6` audited override | **`Ingrid` + `Leda`** (`gemini-3.8-live`) | Prebuilt human presenter `Ingrid` (1:1 studio headshot + native talking-head PiP) |
| **Dr. Marcus Vance** | **Computational Biologist** | `oase-marcus@<workshop-domain>` | `Ch 1` Co-Scientist Elo audit (`1642.5`), `Ch 2` OpenTargets / GWAS / GTEx / AlphaGenome validation | **`Sam` + `Sadaltager`** (`gemini-3.8-live`) | Prebuilt human presenter `Sam` (1:1 studio headshot + native talking-head PiP) |
| **Dr. Elena Rostova** | **Structural Biologist** | `oase-elena@<workshop-domain>` | `Ch 3` AlphaFold 3 (`ipTM = 0.84`), `fpocket` groove selection (`Pocket #1`), AutoDock Vina (`-9.4 kcal/mol`) | **`Kira` + `Kore`** (`gemini-3.8-live`) | Prebuilt human presenter `Kira` (1:1 studio headshot + native talking-head PiP) |
| **Dr. Raj Patel** | **Medicinal Chemist** | `oase-raj@<workshop-domain>` | `Ch 4` MMP optimization (`PCSK9-A02` `cLogP = 5.09` dropped → polar `PCSK9-A03` / `OASE-PCSK9-014` `cLogP = 3.01`), `Ch 6` override request | **`Jay` + `Alnilam`** (`gemini-3.8-live`) | Prebuilt human presenter `Jay` (1:1 studio headshot + native talking-head PiP) |
| **Dr. Claire Moreau** | **DMPK & Safety Lead** | `oase-claire@<workshop-domain>` | `Ch 4` Aronov 2005 hERG alert gate & Wet-Lab rat/dog PK bridge, `Ch 5` `40 mg QD` human oral PK projection | **`Vera` + `Pulcherrima`** (`gemini-3.8-live`) | Prebuilt human presenter `Vera` (1:1 studio headshot + native talking-head PiP) |
| **AI Program Lead** | **Grove Coordinator** | Scion Container (`gemini-cli`) | Dispatches `WO-001`..`WO-008`, synthesizes `Reviewer` + `Validator` (`oase validate check`) checks | **`en-us-techagent-3`** (`gemini-3.8-flash-tts`) | Clean animated Scion Grove Coordinator waveform badge |

---

## 3. Detailed Engineering Build Plan (Step-by-Step Specification)

### Milestone `M0` — Outcome Goal, Build Plan & Live GitHub Website Tracker (`[x] Complete`)
- **Files Built:** `docs/PILOT_IMPLEMENTATION_PLAN.md`, `scripts/build-chapter-portal.py` (`plan.html` generator + `#plan` view), `site-template/*`, `.github/workflows/pages.yml`, `scripts/preflight.sh`.
- **Outcome:** Shareable zero-login website (`chapters.html` + `plan.html`) auto-deployed via GitHub Actions with `noindex, nofollow` and fail-closed hygiene checks.

### Milestone `M1` — Provision 5 Dedicated Scientist Personas & `Gemini 3.8` Profile Portraits via Cloudtop GUI (`[x] Complete`)
- **Step 1.1 (Cloud Identity User Creation via GUI):** Drive Chrome on the virtual Linux desktop (`desktopctl`) into Google Workspace / Cloud Identity Admin (`admin.google.com/ac/users`) to create the 5 dedicated scientist users (`oase-sarah`, `oase-marcus`, `oase-elena`, `oase-raj`, `oase-claire` `@<workshop-domain>`) with a shared static workshop password (`Ask user to change their password` disabled), clean `Dr.` display names, and `Gemini 3.8 Live Avatar` profile photos, then close the admin browser profile completely.
- **Step 1.2 (Matched Presenter Portraits & Isolated Browser Profiles):** Extract 1:1 studio portraits (`Ingrid`, `Sam`, `Kira`, `Jay`, `Vera`) from **`gemini-3.8-live`**; create 5 persistent Chrome user-data directories (`persona-sarah`, `persona-marcus`, `persona-elena`, `persona-raj`, `persona-claire`) on Cloudtop, complete initial sign-in via `desktopctl`, and verify SSO cookies.
- **Step 1.3 (IAP & Scion Hub Roster Binding):** Grant `roles/iap.httpsResourceAccessor` on the Cloud Run IAP service to the 5 scientist accounts (`scripts/provision-personas-iam.py`); log each persona into Scion Hub Web UI once to register their `users` row and `avatar_url` in `hub.db`; purge `admin@` from `project_contributors`, `messages`, and `artifact` ownership.
- **Deliverables:** `scripts/provision-personas-iam.py`, matched `gemini-3.8-live` portraits across Google Workspace / Scion Hub / Story Arc, 5 verified Chrome persona profiles on Cloudtop, screenshot proof of all 5 personas authenticated inside Scion Hub with zero `admin@` presence, and private internal team credential card (outside GitHub) so 5 teammates can each log in as 1 role.

### Milestone `M2` — 7-Chapter Scion State Engine, FastAPI Reset Daemon & Portable Deployer (`[x] Complete`)
- **Step 2.1 (Expand Checkpoints `ch0`..`ch6`):** Extend `checkpoints/` and `scripts/checkpoint.sh` from `ch0..ch4` to cover all 7 states cleanly:
  - `ch0`: Clean initial seed (`t=0`, only `seed/pcsk9-oral/` staged, 0 work orders closed)
  - `ch1`: Step 1 complete (`WO-001` Co-Scientist Elo ranking validated)
  - `ch2`: Step 2 + Gate 1 complete (`WO-001..003` Genetics, GTEx, AlphaGenome)
  - `ch3`: Step 3 + Gate 2 complete (`WO-001..005` AF3, `fpocket`, Vina)
  - `ch4`: Step 4 + Gate 3 + Wet-Lab Handoff paused (`WO-001..006` MMP + ADMET hERG block + Wet-Lab/CRO assay slot)
  - `ch5`: Step 5 + Gate 4 complete (`WO-001..008` Oral PK `40 mg QD` + Candidate Dossier)
  - `ch6`: Step 6 Governance Audit complete (3 blocked adversarial tamper drills + 1 co-signed `oase workorder override`)
- **Step 2.2 (7 Parallel Scion Hub Projects + Live Agent Containers):** Write `scripts/seed-pilot-chapters.py` to provision 7 distinct projects in `hub.db` (`00-pcsk9-initial-seed` through `06-pcsk9-governance-audit`), bind the 5 human scientist `users` as contributors, and attach live specialist containers (`gemini-cli` on `gemini-3.8-flash` / `gemini-3.1-pro-preview`, `claude`, `codex`) inheriting GCP model credentials.
- **Step 2.3 (FastAPI State Controller Service):** Build `services/state-controller/app.py` + `systemd` unit `oase-state-controller.service` on the Scion Hub VM:
  - `GET /api/state/status` → returns active checkpoint hashes, message counts, and last-reset timestamps per chapter.
  - `POST /api/state/chapters/{ch}/reset` → runs `git checkout -f {ch} && git clean -fd` on that chapter's Grove workspace (`~50ms`) + restores `messages`, `webchat_topic`, and `artifact` rows for that project from `/home/scion/.scion/snapshots/golden-pilot/golden-hub.db` inside a single SQLite transaction (`~200ms`) **without touching `users` or `user_access_tokens`**.
  - `POST /api/state/reset-all` → restores `ch0` (`t=0`) and all `ch1`..`ch6` projects atomically in `<2s`.
- **Step 2.4 (Turnkey GCP Portability Script):** Create `scripts/deploy-pilot-stack.sh` reading `.env` (`GCP_PROJECT_ID`, `WORKSHOP_DOMAIN`, `REGION`, `GCS_BUNDLE_BUCKET`) to execute project provisioning, VM/Hub bootstrap, 7-chapter seeding, State Controller installation, and Cloud Run deployment in one repeatable command.

### Milestone `M3` — Cloudtop GUI Multi-Human + Multi-Agent Pilot & Native `Gemini 3.8 Live Avatar` Videos (`[x] Complete`)
- **Step 3.1 (Live Multi-Persona Chat Execution on Cloudtop Desktop):** Use `desktopctl` + Playwright/CDP choreography (`scripts/record-team-pilot.py`) on the Cloudtop desktop to switch between the 5 scientist Chrome windows (`Sarah`, `Marcus`, `Elena`, `Raj`, `Claire`), type real prompts in Scion Webchat (`#general` and stage-gate threads), trigger live responses from the AI Program Lead, Domain Specialists, Reviewer, and Validator, inspect published Evidence Portal artifacts, and co-sign Stage Gates 1–4 + the Step 6 override.
- **Step 3.2 (Freeze Authentic Golden Snapshots):** Immediately after verifying all 6 chapters' real human + agent threads in `hub.db`, snapshot `/home/scion/.scion/hub.db` and workspace directories into `/home/scion/.scion/snapshots/golden-pilot/` so every future reset restores these exact authentic conversations.
- **Step 3.3 (Native `Gemini 3.8 Live Avatar` Joint Audio+Video PiP + `Gemini 3.8 Flash TTS` Mastering):** Synthesize all 18 human scientist turns (`Ch 1–6`) natively on `us-central1` via **`gemini-3.8-live`** (`BidiGenerateContent` `avatarConfig`: `Ingrid`/`Leda`, `Sam`/`Sadaltager`, `Kira`/`Kore`, `Jay`/`Alnilam`, `Vera`/`Pulcherrima`) plus **`gemini-3.8-flash-tts`** (`en-us-techagent-3`) for the Scion Grove Coordinator, phase-lock every clip at `30.000 fps` CFR + `48 kHz` stereo PCM with zero-latency scalar gain, align UI-to-speech via RGB turn-state beacons (`<1.0 ms` stream delta), and upload `chapter-01.mp4`..`chapter-06.mp4` + `full-pilot-walkthrough.mp4` to `gs://$GCS_BUNDLE_BUCKET/videos/`.

### Milestone `M4` — Deploy Standalone Story Arc Cockpit, Video Host & Role Switcher (`[x] Complete`)
- **Step 4.1 (Story Arc Web App Service — `services/story-arc/`):** Build and deploy `oase-story-arc` on Cloud Run behind IAP (accessible to the 5 `<workshop-domain>` accounts):
  - **Top Story Arc Navigation:** `Overview & 4 Pillars` → `Ch 1` → `Ch 2 (Gate 1)` → `Ch 3 (Gate 2)` → `Ch 4 (Gate 3 + Wet-Lab Slot)` → `Ch 5 (Gate 4)` → `Ch 6 (Audit & Override)`.
  - **Embedded 1080p Range Video Player:** Streams the chapter MP4 from GCS (`HTTP 206 Partial Content`) with clickable timestamp pills (`Jump to Human Prompt`, `Jump to Agent Analysis`, `Jump to Validator Verdict`, `Jump to Stage-Gate Sign-Off`).
  - **"Join Live at This Stage As..." Role Bar:** One-click buttons for each chapter's lead and co-presenting human personas (`https://<scion-hub-url>/chat/<ch-slug>/<topic-id>?authuser=<persona>@<workshop-domain>`) + copyable live follow-up prompts for customer Q&A.
  - **Facilitator Reset Drawer:** Live status indicator + **`↺ Reset Chapter N`** and **`↺ Reset Entire Demo (t=0)`** buttons wired to `oase-state-controller` over Direct VPC Egress.

### Milestone `M5` — End-to-End Rehearsal, Portability Audit & Final Sign-Off (`[x] Complete`)
- **Step 5.1 (Full Rehearsal on Cloudtop):** Walk through the deployed `oase-story-arc` Cloud Run URL on the Cloudtop desktop: play multi-voice + avatar chapter videos, click **"Join Live As Dr. Elena Rostova"** in `Ch 3` and **"Join Live As Dr. Raj Patel"** in `Ch 4`, send live follow-up prompts to the agents, click **`↺ Reset CH4`** (`161.6 ms` HTTP) and **`↺ Reset Entire Demo (t=0)`** (`282.2 ms` HTTP), and verify `<2s` restoration to golden state with zero session disruption.
- **Step 5.2 (Team Handoff & Portability Check):** Verify `./scripts/deploy-pilot-stack.sh --dry-run` on a clean config (`0` errors), update `EVALUATION.md`, and mark `M0`–`M5` `[x] Complete` (`6 / 6` = `100%`) on both Cloud Run and the GitHub Website.

---

## 4. Milestone Progress Summary

| ID | Milestone | Key Code & Infra Artifacts | Status |
| :--- | :--- | :--- | :--- |
| **M0** | **Outcome Goal, Detailed Build Plan & Live GitHub Website Tracker** | `docs/PILOT_IMPLEMENTATION_PLAN.md`, `scripts/build-chapter-portal.py` (`plan.html` + `#plan`), `.github/workflows/pages.yml` | `[x] Complete` |
| **M1** | **5 Dedicated Scientist Personas & `Gemini 3.8` Portraits (Cloudtop GUI)** | `scripts/provision-personas-iam.py`, 5 Cloud Identity accounts, matched `gemini-3.8-live` portraits, 5 Chrome profiles, clean `hub.db` | `[x] Complete` |
| **M2** | **7-Chapter State Engine (`ch0`..`ch6`), `<2s` Reset API & Portable Deployer** | `checkpoints/ch0..ch6`, `scripts/seed-pilot-chapters.py`, `services/state-controller/app.py` (`51ms` chapter / `159ms` full reset), `scripts/deploy-pilot-stack.sh` | `[x] Complete` |
| **M3** | **GUI Multi-Human Pilot & Native `Gemini 3.8 Live Avatar` 1080p Videos** | `scripts/record-team-pilot.py`, `/home/scion/.scion/snapshots/golden-pilot/`, `chapter-01..06.mp4` + `full-pilot-walkthrough.mp4` (`<1ms` sync delta) | `[x] Complete` |
| **M4** | **Standalone Story Arc Cloud Run App, Video Streamer & Role Switcher** | `services/story-arc/app.py`, `oase-story-arc` Cloud Run + IAP service (`HTTP 206`), Facilitator Reset UI | `[x] Complete` |
| **M5** | **End-to-End Live Rehearsal, `<2s` Reset Proof & Team Handoff Package** | Verified E2E rehearsal (`161.6ms` chapter / `282.2ms` global HTTP reset), `--dry-run` portability check, `6 / 6` milestones complete | `[x] Complete` |

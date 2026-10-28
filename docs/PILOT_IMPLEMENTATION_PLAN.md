# Team-Based Human + Agent Drug Discovery Pilot: Vision, Architecture & Build Tracker

> **Live Build Status:** Milestone `M0` Complete (`1 / 6` milestones complete)  
> **Target Experience:** A turnkey, repeatable **5-Human Discovery Pod + 11-Agent Multi-Model Grove** demo & workshop environment on Google Cloud—combining a **Story Arc Presenter Cockpit**, **Multi-Voice Gemini TTS Chapter Videos**, **Live Role-Based Scion Hub Logins**, and **Sub-2-Second Environment Reset**.

---

## 1. Executive Vision & Goal (Why We Are Building This)

Traditional AI biology demos fail in executive and scientific workshops for two opposite reasons:
- **Single-user chatbot demos** look like toy Q&A sessions—they miss how real pharmaceutical R&D pods actually work (cross-functional human specialists debating trade-offs, enforcing assay thresholds, pausing for wet-lab validation, and signing formal stage gates).
- **End-to-end live compute runs** are brittle in a 150-minute customer session—waiting on live folding, docking, or container cold-starts risks timeouts and leaves no room for interactive customer exploration.

### What This Demo Environment Delivers
1. **A High-Level Story Arc Cockpit (`chapters.html`) Driving 6 Chronological Chapters:**
   - Opens with **Team-Based Agentic Drug Discovery** and the **4 Core Architectural Pillars** (*The Grove*, *In Silico Work Orders*, *Two-Phase Execution with Threshold Controls*, and *Stage-Gate Reviews*) before diving into the `pcsk9-oral` campaign.
   - Walks chronologically through **6 Macro Workflow Chapters**—including an explicit **Future-State Wet-Lab / CRO Handoff** placeholder between *in silico* ADMET triage and human oral PK nomination.
2. **Real GUI-Captured Human + Agent Team Collaboration (with Distinct Gemini TTS Character Voices):**
   - Rather than synthetic mockups or a single narrator, each chapter features recorded real browser interactions on Scion Hub between **5 named human scientists** and **11 specialized AI agents** (`Gemini`, `Claude`, `OpenAI`), voiced by a **6-voice Vertex Gemini TTS cast** (`gemini-2.5-flash-tts`) so every scientist has a distinct, natural voice synced to their on-screen messages.
3. **Jump In Live at Any Stage as Any Scientist Role:**
   - Presenters and workshop colleagues can click straight from any chapter in the Story Arc Website into that exact stage of Scion Hub (`ch0`..`ch6`), logged in as one of the **5 dedicated human scientist accounts** (e.g., *Structural Biologist* at Gate 2 or *Medicinal Chemist* / *DMPK Lead* at Gate 3) to ask live follow-up questions to the running AI agents—with **zero admin account noise** in the workspace.
4. **Instant `<2s` Reset & Turnkey Multi-Project Portability:**
   - After live Q&A or post-session hands-on exploration, a single click (`↺ Reset Chapter` or `↺ Reset Entire Demo to Initial State`) restores the Grove files and Scion Hub threads in under 2 seconds without logging anyone out.
   - The entire stack is parameterized via `.env` and packaged into a repeatable deployment script (`./scripts/deploy-pilot-stack.sh`) so any presenter can stand up an identical instance in **any GCP project and Cloud Identity domain**.

---

## 2. How Workshop Team Members Share, Collaborate & Present

| Mode | Who Uses It | How Access Works | Friction |
| :--- | :--- | :--- | :--- |
| **1. Story Arc & Build Tracker Website** | Presenters, solution architects, reviewers | Open the hosted static Story Arc & Plan URL (`chapters.html` / `plan.html`) to review the narrative, 4 pillars, 30-page Evidence Portal, recorded videos, and live milestone status. | **Zero login** (direct link) |
| **2. Interactive 5-Role Live Pod** | Up to 5 workshop facilitators (or post-session participants) | Each facilitator opens an Incognito window or dedicated Chrome profile and signs in with one of the **5 dedicated `<workshop-domain>` scientist accounts** (`sarah.chen@`, `marcus.vance@`, `elena.rostova@`, `raj.patel@`, `claire.moreau@`). | **1 sign-in per role** (IAP SSO) |
| **3. Redeploy to Another GCP Environment** | Field engineers spinning up a dedicated sandbox | Copy `.env.example` → `.env` (`GCP_PROJECT_ID`, `WORKSHOP_DOMAIN`, `REGION`), run `./scripts/deploy-pilot-stack.sh`, and seed all 7 chapter snapshots + Cloud Run services automatically. | **Single CLI command** |

---

## 3. Human Discovery Pod & Vertex Gemini TTS Voice Cast

 Infrastructure admin accounts are strictly excluded from Scion project rosters, chat channels, and stage-gate signatures. All human turns on screen and in chapter audio are performed by these 5 dedicated personas (paired with the AI Program Lead voice):

| Persona | Role | Domain Account Pattern | Owned Chapters & Decisions | Gemini TTS Voice (`gemini-2.5-flash-tts`) |
| :--- | :--- | :--- | :--- | :--- |
| **Dr. Sarah Chen** | **Program Lead** | `sarah.chen@<workshop-domain>` | Campaign charter (`Ch 0–1`), Gate 1 co-sign (`Ch 2`), Wet-Lab / CRO handoff (`Ch 4`), Gate 4 nomination (`Ch 5`), and audited override (`Ch 6`). | **`Kore`** — Decisive, clear R&D program director |
| **Dr. Marcus Vance** | **Computational Biologist** | `marcus.vance@<workshop-domain>` | Co-Scientist Elo tournament audit (`Ch 1`) and OpenTargets / GWAS / GTEx / AlphaGenome target validation (`Ch 2`). | **`Charon`** — Analytical, grounded human genetics lead |
| **Dr. Elena Rostova** | **Structural Biologist** | `elena.rostova@<workshop-domain>` | AlphaFold 3 co-fold (`ipTM = 0.84`), `fpocket` druggable groove selection (`Pocket #1`), and Vina pose verification (`Ch 3`). | **`Aoede`** — Articulate, precise structural biophysicist |
| **Dr. Raj Patel** | **Medicinal Chemist** | `raj.patel@<workshop-domain>` | Matched molecular pair (`oase mmp`) optimization—dropping lipophilic `PCSK9-A02` (`cLogP = 5.09`) for polar `PCSK9-A03` / `OASE-PCSK9-014` (`Ch 4`, `Ch 6`). | **`Orus`** — Pragmatic, energetic med-chem lead |
| **Dr. Claire Moreau** | **DMPK & Safety Lead** | `claire.moreau@<workshop-domain>` | Aronov 2005 hERG alert enforcement (`Ch 4`), Wet-Lab rat/dog PK bridge, and `40 mg QD` human oral dose projection (`Ch 5`). | **`Leda`** — Measured, safety-first translational DMPK lead |
| **AI Program Lead** | **Grove Coordinator** | Container (`gemini-cli`) | Dispatches `WO-001`..`WO-008`, aggregates `Reviewer` + `Validator` (`oase validate check`) verdicts, and drafts gate summaries. | **`Zephyr`** — Calm, studio-clear AI coordinator |

*(Phonetic rules enforced across all TTS prompts: first mention `"O-A-S-E"` then `"the Science Engine"`, `"Ee-low"`, `"Nomad"`, `"AD-met"`, `"hurg"`.)*

---

## 4. Incremental Implementation Milestones

| ID | Milestone | Key Deliverables | Verification Gate | Status |
| :--- | :--- | :--- | :--- | :--- |
| **M0** | **Vision, Technical Plan & Live GitHub Website Tracker** | `docs/PILOT_IMPLEMENTATION_PLAN.md`, `plan.html` live build tracker in `scripts/build-chapter-portal.py`, static `site-template/` pages, and automated GitHub Pages workflow (`.github/workflows/pages.yml`) with fail-closed hygiene checks. | `preflight.sh --check-hygiene` passes (`0` leaks); GitHub Pages serves `chapters.html`, `index.html`, and `plan.html` (`HTTP 200`). | `[x] Complete` |
| **M1** | **5 Dedicated Scientist Personas & Admin-Free Roster** | Provision 5 dedicated Cloud Identity accounts (`sarah.chen`, `marcus.vance`, `elena.rostova`, `raj.patel`, `claire.moreau`) via Cloudtop GUI browser automation; bind IAP access; set up 5 isolated Chrome profiles; remove admin identity from Scion project rosters & chat. | All 5 Chrome persona profiles sign in cleanly through IAP into Scion Hub Web UI; admin principal absent from project contributors and chat threads. | `[ ] Next Up` |
| **M2** | **7-Chapter State Engine, Reset Daemon & Portable Deployer** | Provision `ch0-initial-seed` (`t=0`) + `ch1`..`ch6` Scion projects & Git-tagged Grove workspaces; deploy FastAPI `oase-state-controller` (`POST /api/chapters/{ch}/reset`, `POST /api/reset-all`); start live specialist AI containers; codify `./scripts/deploy-pilot-stack.sh` for turnkey GCP portability. | `POST /api/chapters/ch4/reset` restores Grove files + SQLite messages/artifacts in `<2.0s` while keeping all 5 browser sessions signed in. | `[ ] Pending` |
| **M3** | **GUI Multi-Human + Multi-Agent Pilot & Multi-Voice Gemini TTS Videos** | Drive the 5 scientist Chrome windows on the virtual desktop across Steps 1–6 (Co-Scientist → Genetics/Omics/AlphaGenome → AF3/fpocket/Vina → MMP/ADMET & Wet-Lab Handoff → Oral PK/Dossier → 3 Tamper Blocks + 1 Audited Override); synthesize 6-voice Gemini TTS dialogue (`Kore`, `Charon`, `Aoede`, `Orus`, `Leda`, `Zephyr`); record 1080p chapter MP4s; freeze golden snapshots. | Authentic multi-human + multi-agent threads saved in `/home/scion/.scion/snapshots/golden-pilot/`; 6 multi-voice MP4 chapter videos verified. | `[ ] Pending` |
| **M4** | **Standalone Story Arc Web App, Video Host & Role Switcher** | Deploy standalone Story Arc Cloud Run service (`oase-story-arc`) behind IAP with HTML5 Range video player, chapter jump markers, **"Join Live As..."** `?authuser=` persona cards + starter prompts, Team Onboarding Guide, and Facilitator Reset Drawer. | Clicking any persona button opens the target Scion chapter chat as that scientist; video scrubbing and in-UI Reset buttons pass live smoke tests. | `[ ] Pending` |
| **M5** | **End-to-End Rehearsal, Portability Check & Sign-Off** | Full 6-chapter rehearsal from Story Arc Website → multi-persona live agent Q&A mid-campaign → single-chapter reset → full `t=0` reset; verify clean redeployability runbook for team handoff; mark all milestones complete on GitHub Website. | All 6 chapters, 5 personas, 6 Gemini TTS voices, live agent replies, and `<2s` resets verified end-to-end. | `[ ] Pending` |

---

## 5. Chapter-to-Persona & Stage-Gate Architecture

| Chapter | Campaign Phase & Work Orders | Lead Human Persona(s) | Active AI Specialist Agents | Gate / Checkpoint |
| :--- | :--- | :--- | :--- | :--- |
| **Ch 0** | **Initial Seed (`t=0` Clean Sandbox)** | Dr. Sarah Chen | `ai-program-lead`, `validator` | `ch0` (Pre-Step 1 initial state) |
| **Ch 1** | **Step 1 — Co-Scientist Tournament Ingestion (`WO-001`)** | Dr. Sarah Chen, Dr. Marcus Vance | `ai-program-lead`, `genetics-specialist`, `validator` | `ch1` (`IC-001` Elo `1642.5` ingested) |
| **Ch 2** | **Step 2 — Genetics, Hepatocyte Omics & AlphaGenome (`WO-002`–`WO-003`)** | Dr. Marcus Vance, Dr. Sarah Chen | `genetics-specialist`, `omics-specialist`, `reviewer`, `validator` | **Gate 1** (`ch2` — Target Validated) |
| **Ch 3** | **Step 3 — AlphaFold 3, Pocket Druggability & Vina Docking (`WO-004`–`WO-005`)** | Dr. Elena Rostova | `structural-biologist`, `cheminformatics-specialist`, `reviewer`, `validator` | **Gate 2** (`ch3` — Groove Hit Confirmed) |
| **Ch 4** | **Step 4 — MMP Lead Opt, ADMET hERG Gate & Wet-Lab Handoff (`WO-006`)** | Dr. Raj Patel, Dr. Claire Moreau, Dr. Sarah Chen | `medicinal-chemist`, `admet-specialist`, `reviewer`, `validator` | **Gate 3 + Lab Gate** (`ch4` — Polar Lead Advanced; Wet-Lab Slot) |
| **Ch 5** | **Step 5 — Translational Oral PK (`40 mg QD`) & Dossier (`WO-007`–`WO-008`)** | Dr. Claire Moreau, Dr. Sarah Chen | `pk-specialist`, `dossier-writer`, `reviewer`, `validator` | **Gate 4** (`ch5` — Preclinical Candidate Nominated) |
| **Ch 6** | **Step 6 — Adversarial Tamper Tests & Audited Override** | Dr. Sarah Chen, Dr. Raj Patel | `validator`, `reviewer`, `ai-program-lead` | `ch6` (3 Tamper Drills Blocked + 1 Co-Signed Override) |

---

## 6. State Transition, Reset & Redeployment Stack

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Story Arc Cockpit Web App (Cloud Run behind IAP — <workshop-domain> users)   │
│  • Vision Overview + 4 Core Pillars + Chapters 1..6 + Wet-Lab Handoff Slot   │
│  • Multi-Voice Gemini TTS 1080p Chapter Videos (GCS HTTP Range Streaming)    │
│  • "Join Live As..." Role Cards (?authuser=<role>@<workshop-domain>)         │
│  • Facilitator Reset Bar: [↺ Reset Chapter N]  [↺ Reset All to t=0]          │
└───────────────────┬───────────────────────────────────────┬──────────────────┘
                    │ Deep Link (0 ms)                      │ POST /api/reset/*
                    ▼                                       ▼
┌─────────────────────────────────────────┐   ┌────────────────────────────────┐
│ Scion Hub Web UI (Cloud Run IAP Proxy)  │   │ FastAPI State Controller       │
│  • ch0-initial-seed (live t=0 sandbox)  │◄──┤ (systemd on Scion Hub VM)      │
│  • ch1..ch6 Pre-Staged Chapter Projects │   │ 1. git checkout -f chN (~50ms) │
│  • 5 Human Personas (Zero admin chat)   │   │ 2. Scoped SQLite restore       │
│  • 11 Multi-Model AI Agent Containers   │   │    preserving users/sessions   │
└─────────────────────────────────────────┘   └────────────────────────────────┘
```

### Portability & Public Hygiene Guarantees
- **Portable `.env`-Driven Deployment:** Every script reads `GCP_PROJECT_ID`, `WORKSHOP_DOMAIN`, `REGION`, and `GCS_BUNDLE_BUCKET` from `.env` (never hardcoded), allowing one-command redeployment to any clean GCP project.
- **Zero Account / Customer Leakage:** Tracked repository files contain zero internal org IDs, project IDs, domain names, or customer names. Every commit and GitHub Pages build runs `./scripts/preflight.sh --check-hygiene` and sets `noindex, nofollow` meta tags on hosted preview pages.

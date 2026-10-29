# GCP-OASE Workshop: Oral PCSK9 Small-Molecule Discovery on Google Cloud

> ### 🎯 Team-Based Human + Agent Pilot: Outcome Goal, Vision & Live Build Plan
> - **2.5-Hour (150m) Guided Workshop & Lab Playbook:** [**`docs/LAB_GUIDE_150M.md`**](docs/LAB_GUIDE_150M.md) *(3 "What If" Opening Provocations → 5 Pod Seats → Red-Team Tamper Lab)*
> - **Outcome Goal & Detailed Engineering Build Plan (Markdown):** [**`docs/PILOT_IMPLEMENTATION_PLAN.md`**](docs/PILOT_IMPLEMENTATION_PLAN.md)
> - **Turnkey 4-Tier Deploy & Test Runbook:** [**`docs/DEPLOY_AND_TEST.md`**](docs/DEPLOY_AND_TEST.md)
> - **Live vs. Seeded Data Provenance & Real Outputs:** [**`docs/DATA_PROVENANCE.md`**](docs/DATA_PROVENANCE.md) · [**`live-results/pcsk9-oral/`**](live-results/pcsk9-oral/) · [**`prompts/`**](prompts/)
> - **Live Web Build Tracker & Outcome Goal (`plan.html`):** [**https://n0012.github.io/oase-workshop/plan.html**](https://n0012.github.io/oase-workshop/plan.html)
> - **Interactive Story Arc, 2.5-Hr Lab Guide & 30-Page Evidence Portal (`chapters.html`):** [**https://n0012.github.io/oase-workshop/chapters.html**](https://n0012.github.io/oase-workshop/chapters.html)

Hands-on engineering workshop for the **Open Agentic Science Engine (`oase v0.3.0`)** running inside **Google Cloud Scion (`v0.1.50`)** multi-agent Groves.

Participants take a single drug discovery campaign (**`pcsk9-oral`** — oral small-molecule inhibitors of the PCSK9–LDLR protein-protein interaction) through all four preclinical stages:

1. **Stage 0–1 Target Validation & Omics (`WO-001`–`WO-003`):** Co-Scientist Elo tournament ranking (`IC-001` Elo `1642.5`), `gnomAD` loss-of-function constraint (`LOF_TOLERANT`), `OpenTargets` genetic association (`0.86` live / `0.96` seeded FH), `GTEx`/`HPA` hepatocyte expression (`184.2 TPM` / `47.5 nTPM`), and `AlphaGenome` `rs2479409` regulatory polarity (`0.984`).
2. **Stage 2 Structure & Docking (`WO-004`–`WO-005`):** AlphaFold monomer (`AF-Q8NBP7-F1`, `pLDDT = 85.19`) and seeded AlphaFold 3 co-fold (`ipTM = 0.84`), `fpocket` druggability (`0.788` live apo / `0.68` `Pocket #1` groove vs `0.24` flat `EGF-A` surface), and `AutoDock Vina 1.2.5` pose scoring (`-9.4 kcal/mol`).
3. **Stage 3 DMTA Lead Optimization (`WO-006`):** RDKit property profiling (`oase compound`) and rule-based ADMET gating (`oase admet` / `admet-endpoints@1.0`) — disqualifying the lipophilic top docker `PCSK9-A02` (`cLogP = 5.09`, 3 liabilities including the Aronov 2005 `herg_liability` pharmacophore alert) in favor of the polar F,CN-oxadiazole `PCSK9-A03` / `OASE-PCSK9-014` (`cLogP = 3.01`, `MW = 338.3 Da`, `TPSA = 101.0 Å²`, `0` critical liabilities).
4. **Stage 4 Translational PK & Dossier (`WO-007`–`WO-008`):** 1-compartment oral PK simulation (`F = 52%`, `t1/2 = 14.8 h`, `40 mg QD` human oral dose) and candidate dossier synthesis (`findings/regulatory/WO-008.md` + 30-page static Evidence Portal `_site/index.html` and interactive replay `_site/chapters.html`).

Every finding written by an agent is verified by `oase validate check` against 10 deterministic checks across four core governance gates before work-order closure:
- **Gate 1 (SHA-256 Provenance — `provenance_valid`):** Every file in `raw/` must have a matching `<artifact>.meta.json` sidecar whose `sha256` digest matches the file on disk.
- **Gate 2 (JSONPath Citation Verification — `source_tags_resolve`):** Every scalar numerical claim in `findings/**/*.md` must carry an inline `{source: raw/<class>/<stem>.analysis.json $.metrics.<key>}` citation (outside code backticks) that resolves within **±1% relative tolerance** of the Phase-2 analysis JSON.
- **Gate 3 (Mandatory Epistemic Caveat Relays — `relay_coverage`):** Every domain caveat emitted in `.analysis.json` (`hypothesis.adopted_not_generated`, `gnomad.constraint_is_not_safety`, `alphagenome.regulatory_prediction_is_in_silico`, `af3.low_confidence_segments`, `docking.score_is_not_affinity`, `admet.herg_structural_flag`, `pk.allometry_uncertainty`) must appear verbatim as `**Relay: \`<code>\`**` in the synthesis markdown.
- **Gate 4 (Versioned Threshold Attribution — `analysis_citations`):** Every `.analysis.json` record must attribute its verdict to a fully resolved, version-locked threshold schema (`36/36` schemas resolved in `.oase/thresholds.yaml`).

---

## Quickstart (Interactive Checkpoints & Turnkey Pilot Stack)

```bash
# 1. Configure your environment
cp .env.example .env

# 2. Verify CLI prerequisites and repository hygiene
./scripts/preflight.sh --check-hygiene

# 3. Inspect or load a verified campaign checkpoint (ch0..ch7)
./scripts/checkpoint.sh list
./scripts/checkpoint.sh jump ch2

# 4. (Optional) Validate or deploy the 5-Persona + 8-Checkpoint Live Pilot Stack
./scripts/deploy-pilot-stack.sh --dry-run
```

---

## Reproduce End-to-End (Automated Provisioning, Bootstrap & 7-Chapter Simulation)

See [**`docs/DEPLOY_AND_TEST.md`**](docs/DEPLOY_AND_TEST.md) for the complete 4-tier deployment and verification guide, and [**`docs/DATA_PROVENANCE.md`**](docs/DATA_PROVENANCE.md) for the artifact-by-artifact breakdown of live CPU/API outputs ([`live-results/pcsk9-oral/`](live-results/pcsk9-oral/)) vs. seeded GPU/wet-lab fixtures (`AlphaFold 3`, `AlphaGenome`, rodent/dog PK).

To provision a net-new Google Cloud project, compile the 7 scientific binaries (`vina`, `fpocket`, `rate4site`, `muscle`, `hypex`, `elo`, `prox`) + Python 3.11 environment, and execute the full 7-chapter simulation (11 live CLI tools including 3D `AutoDock Vina 1.2.5` + `WO-001`..`WO-008` validation + 4 adversarial tamper drills + 32-page Evidence Portal):

```bash
# 1. (Optional) Provision an isolated Google Cloud GCP project + scion-default-agent SA
python3 scripts/provision-gcp-project.py \
  --project-id my-oase-workshop \
  --org-id 123456789012

# 2. Bootstrap OASE v0.3.0 tools home (Python 3.11 venv + 7 binaries + offline KaTeX)
OASE_TOOLS_HOME=/tmp/scion-volumes/tools ./scripts/bootstrap-oase-env.sh

# 3. Run the complete 7-chapter end-to-end simulation + live Vina docking + 4 tamper drills + portal build
#    (Add --run-gpu-endpoints when OASE_AF3_* and OASE_AG_* / ALPHAGENOME_API_KEY are configured)
OASE_TOOLS_HOME=/tmp/scion-volumes/tools ./scripts/run-e2e-simulation.sh /tmp/sim-pcsk9-oral

# 4. Serve the 32-page Evidence Portal & Interactive Chapter Replay locally
python3 -m http.server 8765 --bind 127.0.0.1 --directory /tmp/sim-pcsk9-oral/_site
# Open http://127.0.0.1:8765/chapters.html and http://127.0.0.1:8765/index.html

# 5. (Optional) Synthesize Gemini 3.8 Live Avatars + AI Wingmen & remaster all 7 Squadron 1080p videos
./scripts/remaster-pilot-videos.sh
```

---

## 150-Minute Workshop Curriculum (Modules `00`–`05` ↔ Pilot Chapters `1`–`7`)

| Curriculum Module | Story Arc Chapter | Time | Stage & Work Orders | Checkpoint |
| :--- | :--- | :--- | :--- | :--- |
| **[00 — Prerequisites & Setup](docs/00-prerequisites.md)** | Prep / Sandbox (`t=0`) | T-15m | CLI preflight, Google Cloud project & Scion Hub auth, and surface selection | `ch0` |
| **[01 — Tour the Grove](docs/01-tour-the-grove.md)** | **Chapter 1** (`#ch1`) | 0:00–0:20 | Stage 0 (`WO-001`): `oase doctor`, Co-Scientist tournament ingest/analyze (`IC-001` Elo `1642.5` vs `IC-002` `1588.0`), `Grove-1` kickoff & `hypothesis.adopted_not_generated` relay | `ch1` |
| **[02 — Target Validation: Genetics & Omics](docs/02-target-validation-genetics-omics.md)** | **Chapter 2** (`#ch2`) | 0:20–0:45 | Stage 1 (`WO-002`, `WO-003`): `gnomAD` (`LOF_TOLERANT`), `OpenTargets` (`0.86` live / `0.96` seeded), `GTEx`/`HPA` (`184.2 TPM` / `47.5 nTPM`), `AlphaGenome` (`0.984`) & Gate 1 | `ch2` |
| **[03 — Structural Biology & Docking](docs/03-structure-docking-af3.md)** | **Chapter 3** (`#ch3`) | 0:45–1:15 | Stage 2 (`WO-004`, `WO-005`): AFDB `Q8NBP7` (`pLDDT = 85.19`), seeded AF3 co-fold (`ipTM = 0.84`), `fpocket` (`0.788` live / `0.68` groove vs `0.24` surface), AutoDock Vina (`-9.4 kcal/mol`) & Gate 2 | `ch3` |
| **[04 — DMTA, PK & Dossier Portal](docs/04-dmta-pk-dossier-portal.md)** | **Chapters 4–7** (`#ch4`–`#ch7`) | 1:15–1:55 | Stages 3–4 (`WO-006`..`WO-008`): ADMET hERG disqualification + Wet-Lab handoff (`ch4`), oral PK `40 mg QD` + Gate 4 (`ch5`), 3 blocked tamper drills + signed override (`ch6`), and `Grove-1` portfolio closeout + 30-page portal (`ch7`) | `ch4`..`ch7` |
| **[05 — Build & Register Custom Tools](docs/05-extend-custom-tools.md)** | Extension | 1:55–2:30 | Write a two-phase tool adapter (`raw/` + `.meta.json` + `.analysis.json`) and verify it with `oase validate check` | — |

### Reference Guides & Live Web Portal
- **[Story Arc & Campaign Replay Website](https://n0012.github.io/oase-workshop/chapters.html)** | **[30-Page Evidence Portal](https://n0012.github.io/oase-workshop/index.html)** | **[Pilot Vision & Live Build Tracker](https://n0012.github.io/oase-workshop/plan.html)**
- **[Multi-Persona Pilot Plan & Architecture (`docs/PILOT_IMPLEMENTATION_PLAN.md`)](docs/PILOT_IMPLEMENTATION_PLAN.md):** Goal, 7-chapter Squadron walkthrough with 5 native `Gemini 3.8 Live Avatar` human scientist presenters (`GOLD-1..5`), 6 specialist AI wingmen on `Gemini 3.8 Flash TTS` (`Grove-1`..`Aegis-6`), Star Fox tactical comms HUD, `<2s` chapter reset architecture, and portable GCP deployment tracker.
- **[Surface Connectivity Reference](docs/surface-connectivity-reference.md):** Connecting Gemini Enterprise (GA), Antigravity IDE (AGY), Gemini CLI, and Scion Web Console (`scion.hlscde.dev`) to the same OASE workspace.
- **[Facilitator Runbook](docs/06-facilitator-guide.md):** Hub seeding (`./scripts/seed-hub.sh` / `./scripts/deploy-pilot-stack.sh`), Story Arc Cockpit pacing, and `<2s` live demo recovery.
- **[Troubleshooting & Validator Reference](docs/07-troubleshooting.md):** Exact remediation steps for `PROV-001`..`002`, `CIT-001`..`003`, `REL-001`, and `THR-001`.
- **[Technical Article](ARTICLE.md), [Design PRFAQ](PRFAQ.md) & [Field Evaluation Scorecard](EVALUATION.md):** Background narrative, Working-Backwards rationale, and our 5 field engineering discoveries from deploying OASE v0.3.0 in Google Cloud.

---

## Repository Layout

```text
oase-workshop/
├── README.md                                 # Quickstart, e2e reproduction commands, and curriculum map
├── ARTICLE.md                                # Technical overview, architecture, and 5 field discoveries
├── PRFAQ.md                                  # Working-Backwards design document
├── EVALUATION.md                             # Reflective comparison of PRFAQ/Article vs. deployed reality
├── .env.example                              # Generic environment template
├── docs/                                     # Modules 00–07, PILOT_IMPLEMENTATION_PLAN.md, DEPLOY_AND_TEST.md, DATA_PROVENANCE.md
├── inputs/
│   └── pcsk9_ic001_af3_ligand.json           # Canonical AlphaFold 3 PCSK9 (Q8NBP7) + OASE-PCSK9-014 co-fold input
├── live-results/
│   └── pcsk9-oral/                           # Real un-mocked Phase-1/Phase-2 outputs (gnomAD, OpenTargets, GTEx, HPA, fpocket, Vina, ADMET)
├── prompts/                                  # Complete prompt registry (Gemini 3.8 Live Avatar, 11 Grove agents, 28 turns, visuals)
├── services/
│   ├── state-controller/                     # FastAPI <2s Git + SQLite snapshot reset daemon (:8780)
│   └── story-arc/                            # Cloud Run IAP Presenter Cockpit, HTTP 206 video streamer & role switcher
├── scripts/
│   ├── deploy-pilot-stack.sh                 # Turnkey 4-var .env deployer (8-checkpoint Hub + Cockpit + IAP)
│   ├── verify-pilot-stack.py                 # Playwright E2E verifier for HTTP 206 streaming, 8 checkpoints & <2s reset
│   ├── render-live-avatars.py                # Native gemini-3.8-live (BidiGenerateContent) + gemini-3.8-flash-tts synthesizer
│   ├── sync-persona-portraits.py             # Crops 512px/40px presenter portraits & syncs Scion Hub SQLite avatars
│   ├── remaster-pilot-videos.sh              # End-to-end 7-chapter live Scion capture, HUD mastering & GCS upload pipeline
│   ├── build-checkpoints.py                  # Deterministic builder for cumulative checkpoints ch0..ch7
│   ├── provision-personas-iam.py             # Binds 5 oase-* scientist accounts + facilitator admin@ on Cloud Run IAP
│   ├── seed-pilot-chapters.py                # Provisions ch0..ch7 Scion Hub projects & live specialist containers
│   ├── record-team-pilot.py                  # Records & masters 7 Squadron 1080p chapters (Gemini 3.8 Live + TTS)
│   ├── pilot_chapters_spec.json              # 7-chapter, 28-turn Squadron script, voices, callsigns & HUD spec
│   ├── provision-gcp-project.py              # Repeatable Google Cloud GCP project & SA provisioner
│   ├── bootstrap-oase-env.sh                 # Builds Python 3.11 venv + 7 scientific binaries + offline KaTeX
│   ├── run-e2e-simulation.sh                 # Runs 11 live CLI tools (incl. Vina & Trials), 8 WO checks, 4 tamper drills & portal build
│   ├── build-chapter-portal.py               # Generates chapters.html + plan.html & links all 30 portal pages
│   ├── record-demo-video.py                  # Standalone Cloud TTS SSML + Playwright 1080p portal video recorder
│   ├── preflight.sh                          # Checks tools, auth, and repo hygiene (--check-hygiene)
│   ├── seed-hub.sh                           # Provisions the pcsk9-oral seed on a Scion Hub
│   ├── checkpoint.sh                         # Restores verified campaign states (ch0..ch7)
│   ├── reset-workshop.sh                     # Resets local workspace to ch0
│   └── render-customer-overlay.sh            # Generates gitignored customer-specific workshop bundles
├── overlays/
│   ├── README.md                             # Customer overlay guide
│   └── customer-overlay.env.example          # Template for customer-specific parameters
└── checkpoints/
    ├── ch0/                                  # Clean pre-campaign seed (t=0, campaign-seed.json, 0 WOs closed)
    ├── ch1/                                  # Step 1: WO-001 Co-Scientist Elo ranking validated
    ├── ch2/                                  # Step 2 + Gate 1: WO-001..003 Genetics, GTEx & AlphaGenome validated
    ├── ch3/                                  # Step 3 + Gate 2: WO-001..005 AF3, fpocket & Vina validated
    ├── ch4/                                  # Step 4 + Gate 3 + Wet-Lab Handoff: WO-001..006 ADMET hERG gate
    ├── ch5/                                  # Step 5 + Gate 4: WO-001..008 Oral PK (40 mg QD) & Candidate Dossier
    ├── ch6/                                  # Step 6: 3 blocked tamper drills + 1 co-signed override (DEC-OVERRIDE-001)
    └── ch7/                                  # Step 7: Executive portfolio sign-off, 30-page portal & GLP tox handoff
```

Each checkpoint directory (`checkpoints/ch1`..`ch7`) is a complete, schema-valid OASE workspace containing `.oase/thresholds.yaml` (all 36 threshold schemas resolved), `.oase/control/work-orders/WO-*.json`, `raw/<class>/*` artifacts, `<artifact>.meta.json` SHA-256 sidecars, `<stem>.analysis.json` metric records, `findings/**/*.md` synthesis reports, and `VAL-WO-*.json` validation receipts.

---

## Customer-Specific Overlays

This repository is intentionally generic. To generate a customer-tailored workshop bundle (custom internal portal URL, GCP project ID, target antigen, or therapeutic program name) without committing customer identifiers to git:

```bash
cp overlays/customer-overlay.env.example overlays/acme-bio.local.env
./scripts/render-customer-overlay.sh overlays/acme-bio.local.env
```

Rendered bundles are written to `overlays/customers/<slug>/` (gitignored) and automatically checked by `./scripts/preflight.sh --check-hygiene`.

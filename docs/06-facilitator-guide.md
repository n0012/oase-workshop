# Module 06 — Facilitator Run-of-Show & Talk-Track Guide

> **Event:** GCP-OASE Hands-On Engineering & Pre-Clinical Discovery Workshop  
> **Duration:** 150 Minutes (2.5 Hours)  
> **Target Audience:** Biopharma Discovery Scientists, Computational Biologists, and AI Platform Engineering Pods  
> **Instructors:** OASE Architecture & Field Engineering Team

---

## 1. Pre-Session Checklist (T-24h and T-30m)

Run the pre-flight and hub-seeding suite before participants join:

```bash
source /workspace/workshop/.env

# 1. Run preflight verification (Vertex ADC, AF3, AlphaGenome, BigQuery, KaTeX, binaries)
/workspace/workshop/scripts/preflight.sh

# 2. Verify all 3 Scion groves exist and stage0-1-walkthrough is set to ch0-bootstrap
/workspace/workshop/scripts/checkpoint.sh status

# 3. Verify 3-second emergency reset snapshot is warm
ls -lh /home/scion/.scion/snapshots/golden-hub.db
```

---

## 2. The Latency Matrix: What Runs Live vs. What Uses Time-Machine Checkpoints

Never make 10+ workshop participants sit silently for 30 minutes watching a terminal spinner. Use this exact rule of thumb: **anything `<15 seconds` runs live; anything `>2 minutes` is launched live for 60 seconds so they see the real Vertex/Scion mechanics, then fast-forwarded via `checkpoint.sh` (`<2 seconds`).**

| Operation | Real Wall-Clock Latency | Workshop Execution Mode | Command / Checkpoint |
|---|---|---|---|
| `oase doctor` / `oase tools list` / `oase relays` | `1–2 sec` | **100% Live** | `oase doctor` |
| `scion start controller ...` (Bootstrap + start `science-program-lead`) | `45–60 sec` | **100% Live** in `live-sandbox` | `scion start controller ...` |
| `oase pubmed-bq search` (BigQuery literature triage) | `2–4 sec` | **100% Live** | `oase pubmed-bq search "hepatic fibrosis MMP13"` |
| `Hypex` 14-concept, 103-match ELO tournament (`WO-001`) | `25–45 min` | **Launch Live (`60s`) → Jump to `ch1` (`<2s`)** | `checkpoint.sh goto ch1` |
| `oase alphagenome score-variant` (Vertex AI Dedicated Endpoint) | `4–6 sec` | **100% Live** | `oase alphagenome score-variant --chrom chr11 ...` |
| `oase alphafold fetch` + `oase pocket run` (`fpocket`) | `6–8 sec` | **100% Live** | `oase alphafold fetch P45452 && oase pocket run ...` |
| `oase alphafold predict` (Vertex AI AF3 Co-Folding) | `5–10 min` | **Generate JSON Live → Jump to `ch3` (`<2s`)** | `oase alphafold predict --template ligand` → `checkpoint.sh goto ch3` |
| `oase compound profile` + `oase admet predict` (`RDKit`) | `2–3 sec` | **100% Live** | `oase compound profile "<SMILES>" --name EED226` |
| `oase validate check` (381 SHA-256 sidecars, 67 JSONPaths) | `2–3 sec` | **100% Live** on `ch4` | `oase validate check --dry-run WO-005` |
| `oase site build` (28-page static HTML portal + 14 viewers) | `2–3 sec` | **100% Live** on `ch4` | `oase site build` |
| `pytest tests/test_h5ad.py` (49 unit tests for custom tool) | `2–3 sec` | **100% Live** | `pytest /workspace/tests/test_h5ad.py -v` |

---

## 3. Minute-by-Minute Run of Show & Instructor Talk Track

### Block 1 (`10:00 – 10:20 AM PT` · 20m): Welcome, Framing & Module 01 (`Tour the Grove`)
- **Lead:** Nick Losier & David Henderson
- **Talk Track (The 3 Sentences That Frame the Day):**
  1. *"Static bioinformatics DAGs like Nextflow break the moment biology surprises you; single-player chatbots hallucinate IC50s and drown you in unverified prose."*
  2. *"GCP-OASE is built for **Team-Based Science**: 5+ human scientists sharing a Scion workspace to co-steer 13 specialized T-shaped agent roles that route Work Orders dynamically like a subway navigator."*
  3. *"You don't give up OpenAI or Claude—we use model diversity across **Gemini 4, Claude, and OpenAI** as a scientific control so no model grades its own homework, while running Google Cloud's exclusive **AlphaFold 3**, **AlphaGenome**, and **BigQuery** underneath."*
- **Live Action:** Have every participant log into Scion Web UI, inspect `templates/structural-biologist/scion-agent.yaml`, and run `oase doctor`, `oase tools list`, and `oase relays`.

---

### Block 2 (`10:20 – 10:50 AM PT` · 30m): Module 02 (`Launch a Live Team Campaign`)
- **Lead:** David Henderson
- **Talk Track:**
  - Emphasize that starting an OASE campaign is **one command** (`scion start controller ...`). The controller runs `oase doctor --json`, syncs templates, initializes `.oase/`, and briefs `science-program-lead`.
  - Have participants post a live mid-flight steering constraint in the `science-program-lead` thread (e.g., requiring MMP1/MMP14 musculoskeletal selectivity checks) so they experience multi-human co-steering firsthand.
- **Time-Machine Transition (`10:40 AM`):**
  - Run `/workspace/workshop/scripts/checkpoint.sh goto ch1` in `stage0-1-walkthrough`.
  - Show `DEC-008` (catching an empty context snapshot) and `DEC-002` (refusing to treat uncalibrated `Hypex` ELO point gaps as probabilities).

---

### Block 3 (`10:50 – 11:30 AM PT` · 40m): Module 03 (`Evidence, Viewers & Refusals`)
- **Lead:** David Henderson & Nick Losier
- **Live GCP AI Consumption Moments:**
  1. **Vertex AI AlphaGenome (`10:52 AM`):** Everyone runs `oase alphagenome score-variant --chrom chr11 --pos 102943000 --ref C --alt T --output-type RNA_SEQ --output-type ATAC --scorer geneMask` and `oase alphagenome analyze raw/genomics/chr11-102943000-C-T.scores.json`. Open the `.meta.json` sidecar and `.analysis.json` to show the Phase 1 / Phase 2 split.
  2. **Vertex AI AlphaFold 3 & `fpocket` (`11:02 AM`):** Run `oase alphafold fetch P45452`, `oase alphafold analyze P45452`, `oase pocket run raw/structures/AF-P45452-F1.cif`, and `oase alphafold predict --template ligand`. Point out the automatic `afdb.confidence_is_not_accuracy` and `afdb.model_is_not_docking_ready` relays.
  3. **10-Check Mechanical Validator & 28-Page Portal (`11:12 AM`):** Jump to `ch4` (`checkpoint.sh goto ch4`), run `oase validate check --dry-run WO-005` and `oase site build`, and walk through the 14 interactive viewers in `_site/index.html`.
  4. **The Refusal Track Record (`11:20 AM`):** Open `negative-gate-audit` (`Pilot-9b`) and show **`DEC-145` (0 of 8 Hidradenitis Suppurativa concepts advanced)** plus the 4 preclinical traps caught in `Pilot-6` (`LAIR1` KO mouse refutation `DEC-006`, mutant `A549` control cell line catch `DEC-009`, `1,000x` VHL warhead halt `DEC-032`, and `EED226-CRBN` **AlphaFold 3 co-folding** `ipTM 0.88` confirmation `DEC-034`).

---

### Block 4 (`11:30 AM – 12:00 PM PT` · 30m): Module 04 (`Make It Yours & Wet-Lab / CRO Handoffs`)
- **Lead:** Nick Losier
- **Talk Track:**
  - Address the #1 practical workflow question from pharma discovery teams: *"We don't run Stage 0 to Stage 4 non-stop on a computer; we stop to run wet-lab CRISPR or CRO assays at WuXi/Charles River."*
  - Have participants edit `.oase/thresholds.yaml` and re-run `oase compound analyze --name EED226 --overwrite` in `<0.2s` offline (`threshold_sources: "program_override"`).
  - Run `oase assay ingest`, `oase selectivity compare`, and `oase pk scale` to demonstrate how wet-lab CRO data re-enters the `.oase/` directory weeks later—and highlight **Standing Rule #2 (`tool-design-guidance.md` §1.1): a prediction never overrides a measurement; when they disagree, the disagreement is the finding.**

---

### Block 5 (`12:00 – 12:30 PM PT` · 30m): Module 05 (`Extend Custom Tools: oase h5ad`) & Next Steps
- **Lead:** Roland & David Henderson
- **Talk Track:**
  - Walk through how `pilot-10` hit a healthy bulk liver GTEx null (`<0.5 TPM`) for `MMP13`, discovered that `oase` lacked a raw single-cell `.h5ad` slicer, opened `OQ-017`, and had `pilot-10-h5ad-builder` build `oase h5ad` (`_h5ad_io.py`, `h5ad.py`, `test_h5ad.py`).
  - Run `pytest /workspace/tests/test_h5ad.py -v` (`49/49` passing) and highlight the three scientific guardrails: `measured` vs. `searched_absent` (`NA`, never `0`), `ACTB` positive control enforcement, and refusing to guess cell-type labels when `"stellate"` is absent from DISCO's vocabulary.
  - Review **Patterns A–D** for onboarding internal R&D containers and close with the **30/60/90-day GCP Sandbox rollout plan**.

---

## 4. Emergency Time-Machine & Reset Commands

If any grove gets into an unexpected state during the live session:

```bash
# Jump stage0-1-walkthrough to any checkpoint in <2 seconds:
/workspace/workshop/scripts/checkpoint.sh goto ch0   # Bootstrap
/workspace/workshop/scripts/checkpoint.sh goto ch1   # Stage 0 Hypex Tournament (103 matches)
/workspace/workshop/scripts/checkpoint.sh goto ch2   # Stage 1 Omics & oase h5ad
/workspace/workshop/scripts/checkpoint.sh goto ch3   # Stage 1 Structure, AF3 & Chemistry
/workspace/workshop/scripts/checkpoint.sh goto ch4   # Validated & 28-Page Site Built

# Full 3-second workshop reset (restores golden-hub.db + resets Git tags without dropping OAuth):
/workspace/workshop/scripts/reset-workshop.sh
```

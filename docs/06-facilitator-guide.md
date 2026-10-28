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

# 1. Run preflight verification (GCP ADC, AF3, AlphaGenome, BigQuery, KaTeX, binaries)
/workspace/workshop/scripts/preflight.sh

# 2. Verify all Scion groves exist and stage0-1-walkthrough is set to ch0-bootstrap
/workspace/workshop/scripts/checkpoint.sh status

# 3. Verify 3-second emergency reset snapshot is warm
ls -lh /home/scion/.scion/snapshots/golden-hub.db
```

---

## 2. The Latency Matrix: What Runs Live vs. What Uses Time-Machine Checkpoints

Never make 10+ workshop participants sit silently for 30 minutes watching a terminal spinner. Use this exact rule of thumb: **anything `<15 seconds` runs live; anything `>2 minutes` is launched live for 60 seconds so they see the real GCP/Scion mechanics, then fast-forwarded via `checkpoint.sh` (`<2 seconds`).**

| Operation | Real Wall-Clock Latency | Workshop Execution Mode | Command / Checkpoint |
|---|---|---|---|
| `oase doctor` / `oase tools list` / `oase relays` | `1–2 sec` | **100% Live** | `oase doctor` |
| `create_project` + `bootstrap_campaign` (A2UI Card) / `scion start controller` | `45–60 sec` | **100% Live** in `live-sandbox` | `bootstrap_campaign` / `scion start controller ...` |
| `oase pubmed-bq search` (BigQuery literature triage) | `2–4 sec` | **100% Live** | `oase pubmed-bq search "hepatic fibrosis MMP13"` |
| `Hypex` 14-concept, 103-match ELO tournament (`WO-001`) | `25–45 min` (`~8m` in `sciarchitect` mode) | **Launch Live (`60s`) → Jump to `ch1` (`<2s`)** | `checkpoint.sh goto ch1` |
| `oase alphagenome score-variant` (Dedicated GCP GPU Endpoint) | `4–6 sec` | **100% Live** (Phase 1) + `<1s` Offline (Phase 2) | `oase alphagenome score-variant --chrom chr11 ...` |
| `oase alphafold fetch` + `oase pocket run` (`fpocket`) | `6–8 sec` | **100% Live** | `oase alphafold fetch P45452 && oase pocket run ...` |
| `oase alphafold predict` (Dedicated GCP AF3 GPU Co-Folding) | `5–10 min` | **Generate JSON / Submit 1 Live → Jump to `ch3` (`<2s`)** | `oase alphafold predict --template ligand` → `checkpoint.sh goto ch3` |
| `oase compound profile` + `oase admet predict` (`RDKit`) | `2–3 sec` | **100% Live** | `oase compound profile "<SMILES>" --name EED226` |
| `oase validate check` (Validation 1: 381 SHA-256 sidecars, 67 JSONPaths) | `2–3 sec` | **100% Live** on `ch4` | `oase validate check --dry-run WO-005` |
| `oase site build` & `oase site export` (28-page static HTML portal + 14 viewers) | `2–3 sec` | **100% Live** on `ch4` | `oase site build && oase site export` |
| `pytest tests/test_h5ad.py` (49 unit tests for custom tool) | `2–3 sec` | **100% Live** | `pytest /workspace/tests/test_h5ad.py -v` |

---

## 3. Minute-by-Minute Run of Show & Instructor Talk Track

### Block 1 (`10:00 – 10:20 AM PT` · 20m): Welcome, Framing & Module 01 (`Tour the Grove`)
- **Lead:** Nick Losier, Preston Holmes & David Henderson
- **Talk Track (The 3 Sentences That Frame the Day):**
  1. *"Static bioinformatics DAGs like Nextflow break the moment biology surprises you; single-player chatbots hallucinate IC50s and drown you in unverified prose."*
  2. *"GCP-OASE is built for **Team-Based Science**: the Project Owner initiates a shared workspace from Gemini Agent (`create_project` + `bootstrap_campaign` A2UI card) and assigns R&D team members (`project-member`) to co-steer a 4-tier / 22-template AI research team across a 9-state work-order lifecycle."*
  3. *"You don't give up OpenAI or Claude—we use portable model size aliases (`small..extra-large`) across **Gemini 4, Claude, and OpenAI on GCP** as a scientific control so no model grades its own homework, while running Google Cloud's exclusive **AlphaFold 3**, **AlphaGenome**, and **BigQuery** underneath."*
- **Live Action:** Have every participant log into Scion Web UI, inspect the 4-tier template roster (`templates/structural-biologist/scion-agent.yaml`), and run `oase doctor`, `oase tools list`, and `oase relays`.

---

### Block 2 (`10:20 – 10:50 AM PT` · 30m): Module 02 (`Launch a Live Team Campaign`)
- **Lead:** Preston Holmes & David Henderson
- **Talk Track:**
  - Show the **Project Owner GA ↔ OASE Initiation Contract**: `create_project` (4-step atomic setup + `OASE_TEMPLATES_MISSING` guard) and `bootstrap_campaign` (interactive **A2UI Project & Campaign Initiation Card** + controller-only launch with `CONTROLLER_TEMPLATE_MISMATCH` guard).
  - Have participants bind their sessions (`SESSION_PROJECT_LOCKED`), read live `DEC-###` logs over Hub WebDAV (`decision_log`), escalate a domain constraint via `request_work_order` / `send_message`, and watch `[OASE_INBOUND_MESSAGE]` alerts arrive verbatim.
- **Time-Machine Transition (`10:40 AM`):**
  - Run `/workspace/workshop/scripts/checkpoint.sh goto ch1` in `stage0-1-walkthrough`.
  - Show `DEC-008` (catching an empty context snapshot) and `DEC-002` (refusing to treat uncalibrated `Hypex` ELO point gaps as probabilities).

---

### Block 3 (`10:50 – 11:30 AM PT` · 40m): Module 03 (`Evidence, Viewers & Refusals`)
- **Lead:** David Henderson & Nick Losier
- **Live GCP AI Consumption Moments:**
  1. **AlphaGenome on GCP (`10:52 AM`):** Run `oase alphagenome score-variant --chrom chr11 --pos 102943000 --ref C --alt T --output-type RNA_SEQ --output-type ATAC --scorer geneMask` and `oase alphagenome analyze raw/genomics/chr11-102943000-C-T.scores.json`. Open the `.meta.json` sidecar and `.analysis.json` to show the Phase 1 / Phase 2 split.
  2. **AlphaFold 3 on GCP & `fpocket` (`11:02 AM`):** Run `oase alphafold fetch P45452`, `oase alphafold analyze P45452`, `oase pocket run raw/structures/AF-P45452-F1.cif`, and `oase alphafold predict --template ligand`. Point out the automatic `afdb.confidence_is_not_accuracy` and `afdb.model_is_not_docking_ready` relays.
  3. **Dual Validation (`Validation 1` + `Validation 2`) & 28-Page Portal (`11:12 AM`):** Jump to `ch4` (`checkpoint.sh goto ch4` and `checkpoint.sh diff ch3 ch4` showing `DEC-031`..`DEC-034`), run `oase validate check --dry-run WO-005` and `oase site build && oase site export`, and walk through the 14 interactive viewers in `_site/index.html`.
  4. **The Refusal Track Record (`11:20 AM`):** Open `negative-gate-audit` (`Pilot-9b`) and show **`DEC-145` (0 of 8 Hidradenitis Suppurativa concepts advanced)**, citation forensics catching padded seed PMIDs, the sealed gate log in `Pilot-9c` (`DEC-248: "The seal caught the lead"`), and the 4 preclinical traps caught in `Pilot-6`.

---

### Block 4 (`11:30 AM – 12:00 PM PT` · 30m): Module 04 (`Fast-Progressing Stage 0→4 Campaigns & Wet-Lab / CRO Handoffs`)
- **Lead:** Nick Losier & David Henderson
- **Talk Track:**
  - Walk through the **Fast-Progressing Stage 0 → 4 Small-Molecule Campaign Options** (`Oral Allosteric PCSK9` in ASCVD, `MTA-Cooperative PRMT5` in MTAP-Deleted Tumors, and `Oral NLRP3` in Cardiometabolic Inflammation) that run end-to-end in ~45 minutes live (`seed_mode=sciarchitect`).
  - Have participants edit `.oase/thresholds.yaml` and re-run `oase compound analyze --name EED226 --overwrite` in `<0.2s` offline (`threshold_sources: "program_override"`).
  - Run `oase assay ingest`, `oase selectivity compare`, and `oase pk scale` to demonstrate how wet-lab CRO data re-enters the `.oase/` directory weeks later—and highlight **Standing Rule #2 (`tool-design-guidance.md` §1.1): a prediction never overrides a measurement; when they disagree, the disagreement is the finding.**

---

### Block 5 (`12:00 – 12:30 PM PT` · 30m): Module 05 (`Extend Custom Tools: oase h5ad`) & Next Steps
- **Lead:** Roland Miezianko, David Henderson & Nick Losier
- **Talk Track:**
  - Walk through how `pilot-10` hit a healthy bulk liver GTEx null (`<0.5 TPM`) for `MMP13`, discovered the `disco.py` key-mapping defect, opened `OQ-017`, and had `pilot-10-h5ad-builder` build `oase h5ad` (`_h5ad_io.py`, `h5ad.py`, `test_h5ad.py`).
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

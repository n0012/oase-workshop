# Multi-Pass Adversarial Evaluation Log (`oase-workshop`)

**Date:** 2026-10-27  
**Scope:** Working Backwards PRFAQ (`PRFAQ.md` / `.beagle/concepts/oase-workshop/prfaq.md`), Concept Brief (`brief.md`), `README.md`, `ARTICLE.md`, `.env.example`, and `docs/00`–`07`.  
**Reference Codebase:** `oase v0.3.0` (`707e461`) + `feat/h5ad-reanalyse` (`8a64d02` / `029b0f2`).

---

## Pass 1: Customer Adoption & Skeptic Narrative Audit
**Evaluator Persona:** Skeptical Biopharma Principal Scientist & Multi-Cloud AI Platform Architect

### Audit Questions & Findings
1. **Does the narrative answer *why* a biopharma R&D team would adopt OASE when they already use OpenAI, Claude, and AWS/Nextflow?**
   - *Initial Gap:* Early framing risked sounding like "switch everything to Gemini and replace Nextflow."
   - *Remediation Applied:* Explicitly positioned Scion's **Template vs. Harness decoupling** (`defaultHarnessConfig` + portable size aliases `small | medium | large | extra-large`) as a **scientific control** (`PRFAQ.md` Q1, `README.md` Step 1, `docs/01-tour-the-grove.md` §3). Teams keep OpenAI and Claude for cross-family adversarial review (`scientific-reviewer`, `finding-validator`) and `Hypex` ELO tournament debates so no single model family grades its own homework—while using Google Cloud (GCP) for exclusive first-party scientific foundation models (`AlphaFold 3`, `AlphaGenome`, `Gemini 4`, `BigQuery`).
2. **Does "Team-Based Science" have concrete operational teeth, or is it a buzzword?**
   - *Remediation Applied:* Grounded Team-Based Science in the **Project Owner GA ↔ OASE Surface Contract** (`create_project` 4-step atomic setup + `bootstrap_campaign` A2UI Initiation Card + 15 `scion` MCP tools), **4-Tier / 22-Template Architecture**, **9-State Work-Order Lifecycle**, **Single-Writer State Contract** (`science-program-lead` sole writer of `program-state/`), **Subway-Map Dynamic Routing**, and **19 registered mandatory relay codes** (`oase relays`).
3. **Does it address real pharma wet-lab and CRO workflows (WuXi, Charles River) plus fast Stage 0→4 small-molecule progression?**
   - *Remediation Applied:* Added dedicated FAQ Q5 (`PRFAQ.md`) and full hands-on exercises (`docs/04-make-it-yours.md` §1 & §3) covering both the **Fast-Progressing Stage 0 → 4 Small-Molecule Campaign Candidates** (`Oral Allosteric PCSK9`, `MTA-Cooperative PRMT5`, `Oral NLRP3` via `seed_mode=sciarchitect`) and configurable **Stage 1 / Stage 2 Stopping Gates** with experimental data re-ingestion (`oase assay ingest`, `oase selectivity compare`, `oase pk ingest/nca/scale`) and **Standing Rule #2 (`tool-design-guidance.md` §1.1): a model prediction never overrides a primary measurement.**
4. **Weasel-Word & Legacy-Name Gate:**
   - Executed regex scan across all generated files for banned `prfaq-beagle` terms (*significantly, revolutionary, seamless, leverage, robust, cutting-edge, best-in-class, enterprise-grade*) and legacy internal code names.
   - **Result:** `0` occurrences in prose (`PASS`).

---

## Pass 2: Technical Ground-Truth Audit Against `oase v0.3.0` (`707e461`) & `feat/h5ad-reanalyse` (`8a64d02`)
**Evaluator Persona:** OASE Core Maintainer & CLI Contract Auditor

### Discrepancies Caught & Remediated
Every CLI invocation in `PRFAQ.md`, `README.md`, `ARTICLE.md`, `.env.example`, and `docs/00`–`07` was cross-checked against `.venv/bin/oase <cmd> --help` and `tools/oase/commands/*.py`:

| Item Audited | Initial Draft Assumption | Actual `oase v0.3.0` (`707e461`) Implementation | Status |
|---|---|---|---|
| **1. `oase alphagenome score-variant` chromosome flag & artifact directory** | Used `--chr` and `raw/variants/` | Uses `--chrom` (e.g., `--chrom chr11 --pos 102943000 --ref C --alt T --output-type RNA_SEQ --output-type ATAC --scorer geneMask`) and writes to `raw/genomics/` (`ARTIFACT_CLASS = "genomics"`). | **FIXED** across `PRFAQ.md`, `README.md`, `docs/03`, `docs/06` |
| **2. `oase alphagenome analyze` argument** | Passed bare stem `chr11-102943000-C-T` | Expects `ARTIFACT` path (`raw/genomics/chr11-102943000-C-T.scores.json`). | **FIXED** in `README.md`, `docs/03`, `docs/06` |
| **3. `oase alphafold predict` flags & env vars** | Assumed `--smiles` CLI flag and `OASE_AF3_ENDPOINT_ID` | Uses `--template [default\|complex\|ligand]` to emit JSON template and `--input <file.json>` to submit; reads `OASE_AF3_PROJECT`, `OASE_AF3_REGION`, `OASE_AF3_ENDPOINT_NAME`, and `OASE_AF3_LOCK` (`~/.cache/oase/af3.lock`). | **FIXED** in `.env.example`, `PRFAQ.md`, `docs/00`, `docs/03`, `docs/07` |
| **4. `oase alphagenome` GCP DNS env vars** | Assumed `OASE_AG_ENDPOINT_URL` | Reads `OASE_AG_PROJECT`, `OASE_AG_REGION`, `OASE_AG_ENDPOINT_ID`, and `OASE_AG_ENDPOINT_DNS` (`<id>.<region>-<project_number>.prediction.vertexai.goog`). | **FIXED** in `.env.example`, `PRFAQ.md`, `docs/00`, `docs/07` |
| **5. `oase pocket analyze` argument** | Passed UniProt ID `P45452` | Expects `PATH` to the pockets record (`raw/structures/AF-P45452-F1.pockets.json`). | **FIXED** in `README.md`, `docs/03` |
| **6. `oase compound profile` / `analyze` & `oase admet predict` / `analyze`** | Used `--smiles ... --id EED226` and `EED226.analysis.json` | `SMILES` is a positional argument and the alias flag is `--name EED226` (which normalizes to lowercase filename slug `raw/compounds/eed226.analysis.json`); re-running `analyze` after changing `.oase/thresholds.yaml` requires `--overwrite` (otherwise exits with code `9` to prevent silent tampering). | **FIXED** in `docs/04`, `docs/06` |
| **7. `oase assay`, `oase selectivity`, `oase pk` arguments** | Used `--input` option | All take positional file paths (`oase assay ingest raw/assays/cro-batch-01.json`, `oase pk nca ... --blq-method exclude`). | **FIXED** in `README.md`, `docs/04` |
| **8. `oase validate check` & Dual Validation (`Validation 1` + `Validation 2`)** | Ran `oase validate check WO-005` directly | Documented Dual Validation (`Validation 1` by `finding-validator` + `Validation 2` by `science-program-lead` before `project-curator` runs `oase site build`), and used `--dry-run` so participants can run all 10 mechanical checks advisory-style against `ch4`. | **FIXED** in `README.md`, `docs/01`, `docs/03`, `docs/06` |
| **9. `oase h5ad` branch provenance** | Assumed in `main` (`707e461`) | Built in `pilot-10` on branch `feat/h5ad-reanalyse` (`8a64d02` / `029b0f2`, `49/49` tests passing) and requires `h5py` in `/scion-volumes/tools/.venv`. | **DOCUMENTED** in `PRFAQ.md` Stage 4 Q1, `docs/05`, `docs/07` |

---

## Pass 3: GCP Architecture & 150-Minute Workshop Execution Audit
**Evaluator Persona:** Google Cloud Life Sciences Solutions Architect & Field Workshop Lead

### Audit Checklist
1. **Are Google Cloud AI models and services structurally embedded in every workshop module?**
   - **Module 00:** Configures `Gemini 4`, `Claude`, `OpenAI` harnesses on GCP, Dedicated GCP `AlphaFold 3` GPU Endpoint, Dedicated GCP `AlphaGenome` GPU Endpoint, `BigQuery` (`OASE_PUBMED_BQ_DATASET`), and the 15-tool `scion` MCP surface connection.
   - **Module 01:** Demonstrates the 4-tier / 22-template roster, portable model size aliases (`small..extra-large`), and GCE Workload Identity ADC verification via `oase doctor`.
   - **Module 02:** Launches live `Gemini 4` + `Claude` agents (`create_project` + `bootstrap_campaign` A2UI card / `scion start controller`) and `oase pubmed-bq search` on BigQuery.
   - **Module 03:** Runs live `oase alphagenome score-variant` (Dedicated GCP GPU Endpoint) and `oase alphafold predict --template ligand` (Dedicated GCP GPU Endpoint), plus audits `DEC-034` (`EED226-CRBN` **AlphaFold 3 co-folding on GCP** at `ipTM 0.88`).
   - **Module 04:** Details the 3 Fast-Progressing Stage 0 → 4 Small-Molecule Campaign Candidates (`Oral PCSK9`, `MTA-Cooperative PRMT5`, `Oral NLRP3`).
   - **Module 05:** Includes **Pattern D** for wrapping additional GPU foundation models on Dedicated GCP GPU Endpoints / Cloud Run into `oase`.
2. **Can every live exercise in the 150-minute agenda complete within its time block without awkward dead air?**
   - Verified in `docs/06-facilitator-guide.md` §2: all live CLI exercises complete in `1–8 seconds` (or `45–60 seconds` for `bootstrap_campaign` / `scion start controller`), while the `25–45 min` `Hypex` tournament and `5–10 min` `AlphaFold 3` co-folding run are bridged via `<2 second` Git-tagged checkpoints (`checkpoint.sh goto ch1`..`ch4`).

### Overall Evaluation Result: **3/3 PASS (Ready for Technical Script Implementation)**

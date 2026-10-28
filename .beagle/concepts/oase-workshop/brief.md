# Concept Brief: GCP-OASE Hands-On Workshop & Biopharma R&D Sandbox (`oase-workshop`)

**Status**: PASSED Working Backwards PRFAQ Gate  
**Date**: 2026-10-27  
**Format**: 150-Minute Hands-On Engineering & Discovery Workshop  
**Target Repository**: `~/dev/github/n0012/oase-workshop` (staging for `/usr/local/google/home/losiern/dev/gob/lifesciences-oss-apps/applications/open-agentic-science-engine/workshop/`)

---

## 1. Executive Summary
We are delivering a 150-minute hands-on workshop and self-contained GitHub kit (`oase-workshop`) that enables biopharma platform engineers and computational/discovery scientists to adopt **GCP-OASE (Open Agentic Science Engine)** on Google Cloud.

Instead of pitching an isolated AI chatbot or a rigid bioinformatics pipeline, the workshop proves four concrete propositions live:
1. **Team-Based Science ("Google Docs for Cross-Functional R&D Teams"):** Five or more human scientists collaborate in a shared Scion grove alongside 13 specialized T-shaped agent roles (22 templates) that dynamically route Work Orders like a subway navigator (`Stage 0 → Stages 1–4`), pausing at configurable stopping gates to hand off to wet-lab or CRO partners (WuXi, Charles River) and re-ingesting assay CSVs later (`oase assay`, `oase selectivity`, `oase pk`, `oase tox`).
2. **Multi-Model Harnesses as a Scientific Control (`Gemini 4` + `Claude` + `OpenAI` + Open-Weight):** Biopharma teams keep their existing OpenAI and Claude investments while running **Gemini 4** on Vertex AI for long-context orchestration, **Claude** on Vertex AI Partner Models for independent `Scientific Reviewer` verification, and multi-model panels across `Hypex` ELO tournaments so no single model ever grades its own homework.
3. **First-Party GCP Scientific AI + 62 Deterministic Open-Source CLI Tools:** Agents execute Google Cloud's exclusive **AlphaFold 3** (`oase alphafold predict` for monomers, `--template complex` PPIs, and `--template ligand` SMILES co-folding), **AlphaGenome** (`oase alphagenome score-variant` and `predict-interval` across 11 regulatory modalities), and **BigQuery** (`oase pubmed-bq search`) alongside 62 deterministic open-source CLI tool groups—enforced by a **Two-Phase Zero-Fabrication Split** (51/51 `analyze` commands offline-latched) and **10-Check Mechanical Validation (`oase validate check`)**.
4. **3-Step Custom Container Onboarding (`Tool → Skill → Template`):** Demonstrated live via `oase h5ad` (`_h5ad_io.py`, `h5ad.py`, `test_h5ad.py` — 49/49 unit tests passing), which was built during `pilot-10` to slice cirrhotic liver `.h5`/`.h5ad` single-cell matrices and overturn a misleading healthy-liver bulk GTEx null.

---

## 2. Target Architecture & Deliverable Layout

```text
oase-workshop/
├── README.md                        # Medium-style narrative + "Start Here" table + GCP AI & 62-Tool Stack
├── ARTICLE.md                       # Standalone Medium blog post with 5 editorial diagrams
├── PRFAQ.md                         # Working Backwards PRFAQ for the OASE Workshop & Sandbox Adoption
├── .env.example                     # PROJECT_ID, REGION, HUB_NAME, OASE_AF3_*, OASE_AG_*, model harness config
├── assets/                          # 5 editorial diagrams (oase_post_thumbnail, challenges, benefits, data_arch, complete_picture)
├── .beagle/concepts/oase-workshop/
│   ├── prfaq.md                     # Full 5-stage PRFAQ with Ignition/PR/Customer FAQ/Internal FAQ/Verdict
│   ├── brief.md                     # Passed Concept Brief handoff
│   └── eval-log.md                  # Multi-pass adversarial evaluation & refinement log
└── docs/
    ├── 00-prerequisites.md          # GCP APIs, IAM, Vertex Gemini 4 / AF3 / AlphaGenome / Claude & BigQuery setup
    ├── 01-tour-the-grove.md         # Scion UI tour, 22 T-shaped templates, multi-model harnesses, `oase doctor`
    ├── 02-launch-campaign.md        # Live team-science exercise: 5+ humans in shared threads -> controller -> lead -> WO-001
    ├── 03-evidence-and-refusals.md  # Play-forward: AlphaGenome, AF3, docking, 10-check validate, negative gate (pilot-9b/10/6)
    ├── 04-make-it-yours.md          # Menu of public targets/indications + wet-lab/CRO stopping states & assay re-ingestion
    ├── 05-extend-custom-tools.md    # 3-Step Container Contract (Tool -> Skill -> Template) + `oase h5ad` (49/49 tests) + Patterns A-D
    ├── 06-facilitator-guide.md      # 150-min run of show, exact talk track, latency table, time-machine commands
    └── 07-troubleshooting.md        # Real failure modes & remedies (AF3 single-flight 429s, KaTeX path, disco.py, h5py, etc.)
```

---

## 3. Hard Constraints & Quality Bar
- **Zero Legacy Naming:** Use **GCP-OASE (Open Agentic Science Engine)** and **Scion** everywhere.
- **100% Ground-Truth CLI Accuracy:** Every `oase` command, flag, file path, and template name must match `oase v0.3.0` (`707e461` + `feat/h5ad-reanalyse` `8a64d02`).
- **Zero Weasel Words:** Ban *significantly, revolutionary, seamless, leverage, robust, cutting-edge, best-in-class, enterprise-grade*.
- **Sub-2-Second Time-Machine Fallback:** Every multi-minute computation in the 150-minute schedule must have a corresponding pre-seeded checkpoint (`ch0`–`ch4`) in `stage0-1-walkthrough` (`pilot-10`) and `negative-gate-audit` (`pilot-9b`).

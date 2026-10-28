# Concept Brief: GCP-OASE Hands-On Workshop & Biopharma R&D Sandbox (`oase-workshop`)

**Status**: PASSED Working Backwards PRFAQ Gate  
**Date**: 2026-10-27  
**Format**: 150-Minute Hands-On Engineering & Discovery Workshop  
**Target Repository**: `~/dev/github/n0012/oase-workshop` (staging for `applications/open-agentic-science-engine/workshop/`)

---

## 1. Executive Summary
We are delivering a 150-minute hands-on workshop and self-contained GitHub kit (`oase-workshop`) that enables biopharma platform engineers and computational/discovery scientists to adopt **GCP-OASE (Open Agentic Science Engine)** on Google Cloud (GCP).

Instead of pitching an isolated AI chatbot or a rigid bioinformatics pipeline, the workshop proves four concrete propositions live:
1. **Team-Based Science ("Google Docs for Cross-Functional R&D Teams") & GA ↔ OASE Surface Contract:** The Project Owner initiates a shared workspace from Gemini Agent (`create_project` + `bootstrap_campaign` via an interactive **A2UI Project & Campaign Initiation Card**) and assigns participating R&D team members (`project-member`) to collaborate alongside a **4-tier / 22-template** AI research team across a **9-state Work-Order lifecycle (`WO-001`..`WO-N`)**, pausing at configurable stopping gates to hand off to wet-lab or CRO partners (WuXi, Charles River) and re-ingesting assay CSVs later (`oase assay`, `oase selectivity`, `oase pk`, `oase tox`).
2. **Multi-Model Harnesses as a Scientific Control on GCP (`Gemini 4` + `Claude` + `OpenAI` + Open-Weight):** None of the 22 templates hardcodes a model ID or CLI binary; Scion resolves portable size aliases (`small | medium | large | extra-large`) across **Gemini 4** for long-context orchestration, **Claude** for independent `Scientific Reviewer` verification, and multi-model panels across `Hypex` ELO tournaments so no single model ever grades its own homework.
3. **First-Party GCP Scientific AI + 62 Deterministic Open-Source CLI Tools:** Agents execute Google Cloud's exclusive **AlphaFold 3** (`oase alphafold predict` for monomers, `--template complex` PPIs, and `--template ligand` SMILES co-folding on Dedicated GCP GPU Endpoints), **AlphaGenome** (`oase alphagenome score-variant` and `predict-interval` across 11 regulatory modalities on Dedicated GCP GPU Endpoints), and **BigQuery** (`oase pubmed-bq search`) alongside 62 deterministic open-source CLI tool groups—enforced by a **Two-Phase Zero-Fabrication Split** (51/51 `analyze` commands offline-latched) and **Dual Validation** (**Validation 1**: 10-check `oase validate check`; **Validation 2**: `science-program-lead` independent Phase-2 review logging `DEC-NNN` / `scientifically_accepted`).
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
    ├── 00-prerequisites.md          # GCP APIs, IAM, Gemini 4 / AF3 / AlphaGenome / Claude & GA/AGY Surface setup
    ├── 01-tour-the-grove.md         # Scion UI tour, 4-tier / 22 templates, portable model aliases, `oase doctor`
    ├── 02-launch-campaign.md        # Project Owner GA initiation (create_project + A2UI card) -> controller -> lead -> WO-001
    ├── 03-evidence-and-refusals.md  # Play-forward: AlphaGenome, AF3, docking, Dual Validation, negative gate (pilot-9b/10/6)
    ├── 04-make-it-yours.md          # Fast-progressing Stage 0->4 candidates (PCSK9, PRMT5, NLRP3) + wet-lab/CRO re-ingestion
    ├── 05-extend-custom-tools.md    # 3-Step Container Contract (Tool -> Skill -> Template) + `oase h5ad` (49/49 tests) + Patterns A-D
    ├── 06-facilitator-guide.md      # 150-min run of show, exact talk track, latency table, time-machine commands
    └── 07-troubleshooting.md        # Real failure modes & remedies (AF3 single-flight, KaTeX, disco.py, GA/AGY MCP errors)
```

---

## 3. Hard Constraints & Quality Bar
- **Zero Legacy Naming & Clean "On GCP" Terminology:** Use **GCP-OASE (Open Agentic Science Engine)**, **Scion**, and **Google Cloud (GCP)** everywhere.
- **100% Ground-Truth CLI Accuracy:** Every `oase` command, flag, file path, and template name must match `oase v0.3.0` (`707e461` + `feat/h5ad-reanalyse` `8a64d02`).
- **Zero Weasel Words:** Ban *significantly, revolutionary, seamless, leverage, robust, cutting-edge, best-in-class, enterprise-grade*.
- **Sub-2-Second Time-Machine Fallback:** Every multi-minute computation in the 150-minute schedule must have a corresponding pre-seeded checkpoint (`ch0`–`ch4`) in `stage0-1-walkthrough` (`pilot-10`) and `negative-gate-audit` (`pilot-9b`).

# Working Backwards PRFAQ: GCP-OASE Hands-On Workshop & Biopharma R&D Sandbox Adoption

**Concept**: `oase-workshop` — GCP-OASE (Open Agentic Science Engine) Hands-On Workshop & Multi-Agent Pre-Clinical R&D Sandbox  
**Date**: 2026-10-27  
**Status**: PASS (Post-3-Pass Adversarial Evaluation)

---

## Stage 1: Ignition

### Target Customer
**Enterprise Biopharma AI Research & Cross-Functional Pre-Clinical Discovery Teams** — structured around the three core buyer/adopter personas attending the **150-Minute Hands-On Engineering & Discovery Workshop**:
1. **Research Platform & AI Engineering Leads:** Own the compute, model routing, and agent infrastructure across biopharma R&D. They are actively evaluating multi-agent orchestration frameworks, already have investments in OpenAI, Anthropic Claude, and AWS/Nextflow pipelines, and refuse to adopt brittle "black-box" vendor toys that lock out their existing models or proprietary internal containers.
2. **Computational Biologists & Target Discovery Scientists:** Spend weeks manually stitching together OpenTargets, gnomAD, GTEx, single-cell `.h5ad` atlases, AlphaFold structures, and literature PDFs to prepare Stage 0/1 Target Validation packages—only to discover late in governance review that a bulk tissue expression dataset masked a diseased cell-type signal, or that a literature seed list padded citations.
3. **Discovery Governance & Portfolio Leads (Head of Discovery / Therapeutic Area Directors):** Need an auditable, falsification-first decision package (`GO`, `CONDITIONAL GO`, or `STOP / NO-GO`) where every numeric claim resolves to a SHA-256-verified raw output file rather than an unverified LLM summary.

### Problem (in customer terms)
Pre-clinical target triage and early lead optimization require a cross-functional team—computational biology, human genetics, structural biology, medicinal chemistry, DMPK, toxicology, and clinical/regulatory strategy—to weigh conflicting evidence across dozens of biological databases and predictive models. Today, pharma teams are stuck between two broken paradigms:
1. **Rigid bioinformatics DAGs (Nextflow / Snakemake):** Great for deterministic sequence alignment, but biological discovery is not a fixed linear pipeline. When a bulk GTEx RNA-seq query returns zero expression in healthy liver, a static pipeline drops the target; a real scientific team asks whether activated stellate cells in cirrhotic liver express it and pivots to slice a single-cell `.h5ad` matrix.
2. **Isolated single-player chatbots & naive multi-agent swarms:** Giving one scientist a chat window (or spinning up 500 uncoordinated LLM agents) produces plausible-sounding prose with fabricated IC50s, cherry-picked citations, raw 50 MB omics matrices stuffed into context windows, and zero mechanical provenance. Worse, when a single model family generates a hypothesis and also reviews it, correlated training bias rubber-stamps weak targets that later fail in $250K–$1M wet-lab or CRO campaigns.

### Why Existing Options Fail
- **Point AI Co-Pilot SaaS tools:** Lock the customer into one vendor's model, hide prompts and thresholds inside proprietary middleware, cannot run proprietary internal Docker containers on shared volumes, and provide no cryptographic link between a sentence in a slide deck and the raw JSON/mmCIF/H5AD bytes on disk.
- **DIY LangGraph / AutoGen scripts:** Lack a multi-user workspace where 5+ human scientists can co-steer an investigation together, lack work-order lease/budget controls, and collapse data fetching and threshold interpretation into a single step—making independent peer review impossible.

### Working Thesis
Enterprise biopharma discovery and platform teams will adopt **GCP-OASE (Open Agentic Science Engine)** on Google Cloud after the 150-minute workshop because it is the first open-source, code-first platform that treats **team-based discovery as a multi-human, multi-model, falsification-first engineering discipline**—while making **Google Cloud Vertex AI (`Gemini 4`, `AlphaFold 3`, `AlphaGenome`, `Claude` Partner Models) and `BigQuery`** the indispensable scientific compute engine underneath.

<details>
<summary>Reasoning — Stage 1</summary>

- **Customer specificity check:** Mapped the three concrete biopharma adopter personas and their incentives (model-agnostic harness flexibility + container extensibility for Platform; single-cell/structural/genetics tool depth for CompBio; anti-fabrication + negative gates for Governance).
- **Problem vs. solution check:** Framed the problem around the real tension between rigid DAGs (which cannot dynamically route when biology surprises you) and unverified LLM chat swarms (which fabricate numbers and rubber-stamp literature bias), without smuggling OASE terminology into the problem statement.
</details>

---

## Stage 2: Press Release

### BIOPHARMA R&D TEAMS ADOPT OPEN AGENTIC SCIENCE ENGINE ON GOOGLE CLOUD TO TURN CROSS-FUNCTIONAL TARGET DISCOVERY INTO TEAM-BASED, AUDITABLE COMPUTATION

#### Five-scientist discovery pods co-steer 13 specialized agent roles across Gemini 4, Claude, and OpenAI while executing AlphaFold 3 co-folding, AlphaGenome regulatory scoring, and 62 deterministic scientific tools on Vertex AI—cutting Stage 0–1 evidence package assembly from 6 weeks to 4 hours with zero unverified claims.

**SOUTH SAN FRANCISCO, Calif. — November 2026** — After completing a 150-minute hands-on engineering workshop with Google Cloud, biopharma AI and discovery platform teams are deploying the **Open Agentic Science Engine (GCP-OASE)** into their Google Cloud pre-clinical sandboxes. Using GCP-OASE, cross-functional pods of five to eight computational biologists, structural biologists, and medicinal chemists work inside a shared Scion workspace alongside 13 specialized agent roles—dynamically routing Work Orders across **Vertex AI Gemini 4**, **AlphaFold 3**, **AlphaGenome**, **Anthropic Claude**, **OpenAI**, and 62 deterministic command-line tools to stress-test therapeutic hypotheses before committing wet-lab or CRO budget.

Early drug discovery teams face a costly asymmetry: generating a plausible target hypothesis with a large language model takes seconds, but discovering that the target rests on padded citations, a mutant control cell line, or an unstable ternary complex after contracting a CRO costs hundreds of thousands of dollars and six months of calendar time. Until now, R&D organizations had to choose between rigid workflow pipelines that break whenever an unexpected biological finding requires a detour, or single-user AI chat tools that hallucinate assay numbers and trap findings in isolated threads.

GCP-OASE replaces both with a **Team-Based Science architecture ("Google Docs for Cross-Functional R&D Teams")** powered by Google Cloud's scientific AI stack:
- **Multi-Human + Multi-Agent Collaboration (`Scion`):** Up to a dozen human domain experts join the same live project grove to inspect intermediate artifacts, override thresholds, and message the `Research Operations Controller` or `Science Program Lead` mid-flight. Instead of a hardcoded DAG, agents operate like a **subway navigator**—evaluating evidence at each decision stop (`DEC-001`..`DEC-N`) and dynamically issuing the next Work Order (`WO-001`..`WO-N`), whether that is a full 5-stage campaign or a 2-step triage that pauses for a WuXi/CRO wet-lab handoff.
- **Model Diversity as a Scientific Control:** Because Scion separates the **Agent Template** (role + skills) from the **Model Harness**, R&D teams run **Gemini 4** on Vertex AI for high-context program synthesis, **Claude** on Vertex AI Partner Models for adversarial `Scientific Reviewer` audits, and **Gemini 4 + Claude + OpenAI** simultaneously across `Hypex` ELO debate tournaments—ensuring no single model family ever grades its own homework.
- **First-Party GCP Scientific AI + 62 Deterministic Open-Source Tools:** Agents never estimate biological quantities in prose. Through the unified `oase` CLI, agents invoke Google's exclusive **AlphaFold 3** on Vertex AI (`oase alphafold predict` for monomers, `--template complex` protein-protein interfaces, and `--template ligand` protein-SMILES co-folding), **AlphaGenome** on Vertex AI (`oase alphagenome score-variant` and `predict-interval` across 11 regulatory modalities including `RNA_SEQ`, `ATAC`, `CHIP_TF`, and `CONTACT_MAPS`), and **BigQuery** (`oase pubmed-bq search`) alongside 62 open-source CLI tool groups (`RDKit`, `AutoDock Vina`, `fpocket`, `OpenTargets`, `gnomAD`, `CELLxGENE`, `DISCO`, `ClinVar`, `ChEMBL`, `FAERS`, and `oase h5ad` single-cell matrix slicing).
- **Two-Phase Zero-Fabrication Funnel & 28-Page Static Evidence Portals:** Every tool splits into **Phase 1 (`fetch`/`run`/`predict`)**, which writes raw bytes under `raw/` with a SHA-256 `.meta.json` provenance sidecar, and **Phase 2 (`analyze`)**, which is network-latched offline across all 51 analysis commands to apply program thresholds from `.oase/thresholds.yaml`. Before any finding is accepted, `oase validate check` runs 10 mechanical checks verifying every `{source: raw/... $.jsonpath}` claim, and `oase site build` compiles a self-contained HTML evidence site with 14 interactive viewers (`plddt-viewer`, `pae-viewer`, `constraint-viewer`, `expression-viewer`, `tournament-viewer`, `docking-viewer`, `admet-viewer`).

> "Pharma R&D doesn't fail because scientists lack chat windows; it fails when weak hypotheses survive too long or when a true disease signal is buried inside a single-cell matrix nobody had time to re-slice," said **David Henderson, Principal Architect for Open Agentic Science Engine at Google Cloud**. "With GCP-OASE, we built an engine whose most valuable output is often a rigorous, citation-verified `STOP` decision—backed by AlphaFold 3, AlphaGenome, Gemini 4, and 10 mechanical provenance checks that refuse to let an agent invent a single number."

> "What sold our team in the workshop wasn't a polished slide deck—it was watching GCP-OASE reject eight weak hidradenitis suppurativa concepts in Pilot-9b on real human genetic counter-evidence, and watching a live agent in Pilot-10 overturn a misleading bulk-tissue GTEx null by pulling and sub-clustering raw cirrhotic liver `.h5ad` count matrices," said a **Biopharma Discovery Platform Lead**. "We kept our OpenAI and Claude harnesses for cross-examination, plugged our custom Python single-cell tooling into the shared volume in three steps, and immediately started driving real AlphaFold 3, AlphaGenome, and Gemini 4 workloads on Vertex AI."

Discovery engineers and scientists can launch the complete workshop environment—including three pre-seeded project groves (`live-sandbox`, `stage0-1-walkthrough`, and `negative-gate-audit`) and instant `<2 second` Git time-machine checkpoints (`ch0`–`ch4`)—directly from the `oase-workshop` repository on Google Cloud.

<details>
<summary>Reasoning — Stage 2</summary>

- **Weasel-word scan:** Zero occurrences of *significantly, revolutionary, seamless, leverage, robust, cutting-edge, best-in-class, enterprise-grade*.
- **Concrete metrics & mechanisms:** Named exact tool counts (62 CLI groups, 51 offline-latched `analyze` commands, 10 mechanical validation checks, 14 interactive viewers, 22 templates across 13 roles), exact pilot evidence (`Pilot-9b` rejecting 8/8 concepts at `DEC-145`; `Pilot-10` overturning bulk GTEx via `oase h5ad`), and exact GCP services (`Vertex AI Gemini 4`, `AlphaFold 3`, `AlphaGenome`, `Claude`, `BigQuery`).
</details>

---

## Stage 3: Customer FAQ (The Biopharma Skeptic Gauntlet)

### Q1: We already use OpenAI and Anthropic Claude across our R&D organization, and much of our bioinformatics runs on AWS. Why would we adopt GCP-OASE instead of building on our existing stack?
**Because GCP-OASE turns your existing OpenAI and Claude investments into a scientific control rather than forcing a rip-and-replace—while unlocking Google Cloud's exclusive scientific foundation models (`AlphaFold 3`, `AlphaGenome`, `Gemini 4`) in the same workflow.**

In Scion, the **Agent Template** (role definition, skills, and `oase` CLI permissions) is decoupled from the **Model Harness** (the LLM runtime container and API provider). In a single OASE program:
1. You can bind your `Science Program Lead` and `Computational Biologist` to **Gemini 4** on Vertex AI for 1M+ token context synthesis across 50+ work orders.
2. You can bind your `Scientific Reviewer` and `Finding Validator` to **Anthropic Claude** (via Vertex AI Partner Models or direct API) so the auditor never shares model-family blind spots with the author.
3. You can configure `Hypex` Stage 0/1 hypothesis tournaments so `hypex-generation`, `hypex-tournament`, and `hypex-reflection` agents pit **Gemini 4, Claude, and OpenAI** against each other in blind ELO matches (`oase hypex ingest` / `oase hypex analyze`).
4. Crucially, regardless of which LLM reasons in the harness, every agent executes the exact same `oase` CLI against **Vertex AI AlphaFold 3** (`oase alphafold predict`), **Vertex AI AlphaGenome** (`oase alphagenome score-variant` / `predict-interval`), and **BigQuery** (`oase pubmed-bq search`)—capabilities that do not exist as first-party managed APIs on AWS or OpenAI.

---

### Q2: How is OASE's "Team-Based Science" different from giving five scientists ChatGPT/Claude seats or wiring up a LangGraph multi-agent DAG?
**Chatbots isolate humans into single-player threads; DAGs freeze the workflow before the first experiment runs; naive 500-agent swarms drown you in unverified chat noise. OASE gives 5–10 human scientists a shared operational control room over 13 T-shaped agent roles.**

Specifically:
1. **Shared Multi-User Workspace (`Scion` Grove):** Five discovery scientists (e.g., a CompBio lead, a Structural Biologist, a MedChem lead, a Toxicologist, and a Platform Engineer) log into the same Scion Hub project via corporate Google OAuth. Every human sees the live agent roster (`scion list`), live work-order tree (`.oase/control/work-orders/`), decision ledger (`DEC-001`..`DEC-N`), and generated evidence pages in real time.
2. **Subway-Map Dynamic Routing (Not a Fixed DAG):** OASE does not hardcode "Step 1 → Step 2 → Step 3." The `Science Program Lead` and `Research Operations Controller` act like a subway navigator: at each stop, they read the validated `.analysis.json` from the previous Work Order and decide which specialist line to dispatch next. In `pilot-10`, when healthy liver bulk RNA-seq (`GTEx`) returned near-zero expression for `MMP13`, the Science Program Lead did not follow a blind script—it issued `WO-006` (and spawned `pilot-10-h5ad-builder` via `OQ-017`) to slice cirrhotic single-cell `.h5ad` datasets from DISCO (`GSE212046`, `PRJNA913603`) and CELLxGENE, proving the target was expressed in disease-activated mesenchymal compartments.
3. **T-Shaped Liability Handoffs:** Each of the 22 templates (13 roles) has a strict capability grant (`skills:` in `scion-agent.yaml`) and an explicit downstream handoff contract. When the `Structural Biologist` detects a disordered region or a `1,000x` binding affinity drop (`DEC-032` in `pilot-6`), it records a structured liability relay (`afdb.partial_coverage`) that binds the downstream `Computational Chemist` and `Medicinal Chemist`.

---

### Q3: Why do we need Google Cloud's Vertex AI specifically—what does OASE run on GCP that drives real scientific differentiation?
**Four first-party Google Cloud workloads power the core scientific loop in OASE:**

| GCP Service | OASE CLI / Integration | Scientific Job in the Campaign | Why GCP Vertex AI / BigQuery Is Required |
|---|---|---|---|
| **Vertex AI AlphaFold 3** (`g2-standard-12` / `a2-ultragpu-1g` Dedicated Endpoint) | `oase alphafold predict --template [default\|complex\|ligand]`<br>`oase alphafold predict --input <json>`<br>`oase alphafold analyze-prediction <summary.json>` | Predicts de novo 3D structures, protein-protein interfaces (`ipTM`), and **protein + small-molecule SMILES co-folding** (`--template ligand`, e.g., confirming `EED226-CRBN` PROTAC ternary complex stability at `ipTM 0.88` in `pilot-6` `DEC-034`). | First-party DeepMind AlphaFold 3 container deployed on Vertex AI via `aiplatform.init()` with Application Default Credentials (ADC) and single-flight lease control (`~/.cache/oase/af3.lock`). |
| **Vertex AI AlphaGenome** (Dedicated Endpoint) | `oase alphagenome score-variant --chrom ... --pos ... --ref ... --alt ...`<br>`oase alphagenome predict-interval`<br>`oase alphagenome analyze <scores.json>` | Quantifies non-coding regulatory variant impact across **11 assay modalities** (`RNA_SEQ`, `ATAC`, `DNASE`, `CHIP_TF`, `CHIP_HISTONE`, `CAGE`, `PROCAP`, `SPLICE_SITES`, `SPLICE_SITE_USAGE`, `SPLICE_JUNCTIONS`, `CONTACT_MAPS`) across tissue ontology uberon terms. | Native Vertex AI Dedicated Endpoint (`*.prediction.vertexai.goog` via ADC) returning multi-assay tracks in ~3–6 seconds per variant/interval. |
| **Vertex AI Gemini 4 & Partner Models (Claude)** | Scion Model Harnesses (`gemini-4-pro` / `gemini-4-flash`, `claude-sonnet-4-6` / `claude-opus-4-7` on Vertex) | Long-context orchestration (`controller`, `science-program-lead`), multi-model `Hypex` hypothesis generation/tournament judging, and cross-family `scientific-reviewer` verification. | Unified GCP billing, VPC-SC boundary, zero data retention, and IAM governance across Google and Anthropic frontier models. |
| **BigQuery + Cloud Storage + GCE/GKE** | `oase pubmed-bq search "<QUERY>"`<br>`oase pubmed-bq analyze "<QUERY>"`<br>Shared `/scion-volumes/tools` | Sub-second SQL/vector literature triage over tens of millions of PubMed records in BigQuery without NCBI E-utilities rate limits; persistent artifact storage and Scion Hub hosting. | Eliminates 3 req/sec public API bottlenecks during 46-agent `Hypex` Stage 0 tournaments (`pilot-9c`). |

---

### Q4: How do we know an OASE agent won't hallucinate an IC50, cherry-pick a paper, or rubber-stamp a weak target just to "complete the task"?
**OASE enforces anti-fabrication mechanically in code, not politely in prompts—and we prove it in the workshop with three real pilot campaigns where OASE halted flawed science before wet-lab spend.**

Five mechanical layers prevent fabrication:
1. **No Raw Data in LLM Context:** Agents never paste 50 MB `.h5ad` matrices, `.cif` coordinates, or raw GraphQL responses into their context window. All raw data lands on disk under `<program>/raw/<class>/` with a cryptographic SHA-256 `.meta.json` sidecar (`env_version`, `cli_integrity`, `source_url`, `retrieved_at`, `sha256`).
2. **The Non-Negotiable Two-Phase Split (51/51 `analyze` Commands Offline-Latched):** Every tool splits into Phase 1 (`fetch`/`run`/`predict`) and Phase 2 (`analyze`). At the root of the CLI command tree, `oase` latches the HTTP client **completely offline** during any `analyze*` command (`PhaseContractError` on any socket attempt). Thresholds come exclusively from `.oase/thresholds.yaml` and are stamped into `.analysis.json` (`thresholds_applied` + `threshold_sources`).
3. **10-Check Mechanical Validation (`oase validate check <WO>`):** Before the `Research Operations Controller` can mark any Work Order complete, `oase validate check` verifies: (1) schema conformance, (2) run-state legality, (3) every cited `{source: raw/... $.jsonpath}` path exists on disk, (4) the JSONPath resolves to the exact number claimed in prose, (5) every raw file's SHA-256 matches its `.meta.json` sidecar, (6) `env_version` consistency, (7) mandatory relay propagation (19 registered relay codes via `oase relays`), (8) citation verification (`oase cite` / `oase litref resolve`), (9) threshold citation accuracy, and (10) negative-control/denominator completeness. In `pilot-10`, `oase validate check` verified **381 SHA-256 sidecars and 67 JSONPath claims with zero failures**.
4. **Independent `scientific-reviewer` & `finding-validator` Re-Execution:** Because Phase 2 is deterministic and offline, the reviewer agent (running on a different model family) re-runs `oase <tool> analyze` against Layer 0 bytes on disk and diffs the output against the specialist's prose.
5. **Empirical Track Record of Saying `NO-GO`:**
   - **Pilot-9b (Hidradenitis Suppurativa Stage 0):** Evaluated 8 candidate therapeutic concepts across 153 logged decisions (`DEC-001`..`DEC-153`). **Result: 0 of 8 advanced (`DEC-145`)**—7 were terminated on human clinical/genetic counter-evidence and 1 held as exploratory, while `WO-001` caught upstream seed citation-padding.
   - **Pilot-10 (Hepatic Fibrosis Stage 0→1):** Refused an uncalibrated Hypex ELO gap (`DEC-002`), rejected an empty context snapshot (`DEC-008`), and suspended a finding when a comparator group returned zero cells (`DEC-031`).
   - **Pilot-6 (NSCLC EZH2/EED PROTAC):** Caught 4 costly preclinical traps before a single dollar of CRO wet-lab spend: (1) refuted `LAIR1` literature bias using knockout mouse survival data (`DEC-006`), (2) disqualified mutant `A549` (`STK11`/`KEAP1`) as a control cell line via DepMap before CRO assay setup (`DEC-009`), (3) halted a VHL warhead showing a `1,000x` binding affinity loss (`DEC-032`), and (4) confirmed `EED226-CRBN` ternary complex stability (`ipTM 0.88`) via **AlphaFold 3 co-folding** (`DEC-034`).

---

### Q5: Our discovery teams rarely run Stage 0 through Stage 4 in one uninterrupted computer run. We stop after target triage or virtual screening to run wet-lab assays internally or at a CRO (WuXi, Charles River), then come back weeks later with CSV/Excel data. Does OASE support that?
**Yes. OASE is stateful, resumable, and explicitly built around configurable stopping gates and wet-lab/CRO data re-ingestion.**

1. **You Choose the Stopping Gate in the Program Directive:** When starting a campaign, you tell the `Research Operations Controller` where to stop:
   - *Option A (Target Triage Only):* Run `Stage 0 → Stage 1` (Hypex tournament + OpenTargets/gnomAD/AlphaGenome/h5ad validation) and stop at the **Stage 1 Target Selection Gate** to hand the ranked target dossier to your wet-lab CRISPR/siRNA validation team.
   - *Option B (Hit-to-Lead CRO Handoff):* Run `Stage 1 → Stage 2` (`AlphaFold 3` + `fpocket` + `AutoDock Vina` + `RDKit ADMET` + `ASKCOS` retrosynthesis) and stop to export a compound synthesis & assay worklist for WuXi or Enamine.
2. **Zero-State-Loss Resumption:** Because all control state lives on disk in `<program>/.oase/` (`program.yaml`, `thresholds.yaml`, `control/work-orders/`, `control/events.ndjson`), a campaign can sit idle for 6 weeks at zero compute cost while your CRO runs the physical assays.
3. **First-Class Wet-Lab Re-Ingestion CLI Tools:** When the CRO returns CSV/JSON results, you drop them into `<program>/raw/assays/` and run:
   - `oase assay ingest` & `oase assay analyze` (T3 biochemical/cellular IC50 dose-response curves, Hill slopes, Z'-factor QC)
   - `oase selectivity compare` & `oase selectivity analyze` (off-target kinome/panel selectivity fold-windows)
   - `oase pk ingest`, `oase pk nca`, `oase pk scale` & `oase pk analyze` (in vivo rodent/NHP pharmacokinetics and human dose projection)
   - `oase tox analyze` (preclinical toxicology & safety margins)
   Then restart the controller (`scion start controller ...`) pointed at the existing directory. As documented in `docs/quickstart-pilot.md` §5, OASE detects the `.oase/` marker, preserves all prior provenance, and routes the next stage using the real wet-lab measurements—enforcing **Standing Rule #2 (`tool-design-guidance.md` §1.1): a model prediction never overrides an experimental measurement; when they disagree, the disagreement is reported as the primary finding.**

---

### Q6: What happens when our scientists need a custom single-cell algorithm or an internal proprietary container that isn't in your 62 built-in tools?
**You add it without rebuilding agent container images, using OASE's 3-Step Container Contract (`Tool → Skill → Template`) on the `/scion-volumes/tools/` shared volume.**

In fact, **Module 5 of our workshop walks through a real tool built live during `pilot-10`**:
1. **Step 1 — Tool (`tools/oase/commands/<tool>.py` or binary in `/scion-volumes/tools/bin/`):** Wrap your Python script, CLI binary, or internal REST service into `oase <tool> fetch` (Phase 1: writes `raw/<class>/` + `.meta.json` sidecar) and `oase <tool> analyze` (Phase 2: offline-latched, reads disk, writes `.analysis.json`), then stamp the shared volume (`./install.sh --update`, updating `ENV_VERSION`).
2. **Step 2 — Skill (`skills/<capability>/SKILL.md`):** Write a `<200-line` specialist-neutral Markdown contract defining when to invoke the tool, the exact `raw/` output paths, mandatory relay codes, and the anti-fabrication guard.
3. **Step 3 — Template (`templates/<role>/scion-agent.yaml` & `agents.md`):** Grant the skill name in `scion-agent.yaml` and run `scion template sync --all`.

During `pilot-10`, when the `Computational Biologist` needed per-cell gene counts and unsupervised sub-clustering across 5 cirrhotic liver `.h5` samples (`GSM6508438`, `GSM6508440`, `SRX18764702/03/04`) and CELLxGENE `.h5ad` files, the `pilot-10-h5ad-builder` agent built `oase h5ad fetch` and `oase h5ad analyze` (`_h5ad_io.py`, `h5ad.py`, and 49 unit tests in `test_h5ad.py`) right inside a git worktree (`feat/h5ad-reanalyse`). We also provide four copy-paste integration blueprints (**Patterns A–D**: Shared-Volume Python CLI, Static Binary in `bin/`, Sidecar Docker Container on Scion bridge network, and Remote Cloud Run / Vertex Endpoint wrapper).

---

### Q7: What does a campaign actually cost in time and GCP spend, and how do we prevent an agent loop from burning $10,000 on Vertex AI endpoints overnight?
**Every expensive model call is gated by CLI concurrency leases, ROC work-order budgets, and Phase 1/Phase 2 separation—keeping a complete Stage 0→1 campaign to ~$35–$120 in GCP compute and API spend.**

| Resource | Typical Usage per Stage 0→1 Campaign | Built-in Cost & Concurrency Guardrail |
|---|---|---|
| **Vertex AI AlphaFold 3** | 2–8 predictions (monomer, PPI complex, or protein+ligand co-fold; ~5–10 min each on G2/A100) | `alphafold.py` enforces a **single-flight lease** (`~/.cache/oase/af3.lock`) and explicitly documents cost/concurrency in the `protein-structure-confidence` skill preconditions so an agent cannot launch a 40-compound AF3 batch unapproved. Phase 2 (`analyze-prediction`) re-runs offline in `<1 sec` at $0 cost whenever thresholds change. |
| **Vertex AI AlphaGenome** | 10–50 variant scores or interval predictions (~3–6 sec each) | Per-host QPS rate limiter (`core/qps.py`) + SHA-256 content-keyed output caching under `raw/genomics/`. |
| **Vertex AI Gemini 4 & Claude** | ~40–150 agent turns across `controller`, `science-program-lead`, `hypex`, and specialists | The `Research Operations Controller` tracks work-order leases (`.oase/control/leases/`) and epoch budgets (`budget_exhausted` stop condition in `Hypex`), halting stalled or looping agents automatically. |
| **BigQuery (`pubmed-bq`)** | 5–20 literature triage queries | Partitioned query limits (`--max-results`) with cached `raw/literature/` JSON payloads. |

---

### Q8: Some OASE steps—like a 103-match `Hypex` tournament (`~25–45 min`) or cold `AlphaFold 3` co-folding (`~5–10 min`)—take longer than a live workshop block. How will 10+ participants experience the full lifecycle in 150 minutes?
**We use a "Cooking-Show Time-Machine" architecture (`scripts/checkpoint.sh` + pre-seeded Scion groves) so participants launch real live commands AND jump across verified campaign milestones in `<2 seconds`.**

The workshop VM (`n2-standard-8`) comes pre-seeded with three side-by-side Scion projects:
1. **`live-sandbox` (Live Execution):** Participants form cross-functional teams, type a real Program Directive into Scion, watch `controller` and `science-program-lead` spin up live (`~60 sec`), fire a live **Vertex AlphaGenome** variant score (`~4 sec`), submit a live **Vertex AlphaFold 3** prediction job (`~10 sec` submission + live Vertex job tracking), and run live `fpocket` (`~4 sec`) and `RDKit` (`~2 sec`) analyses.
2. **`stage0-1-walkthrough` (`pilot-10` Hepatic Fibrosis Time-Machine):** Equipped with 5 Git-tagged checkpoints (`ch0-bootstrap` → `ch1-stage0-hypex` → `ch2-stage1-omics` → `ch3-stage1-structure` → `ch4-site-published`). Running `scripts/checkpoint.sh goto ch3` (or messaging an agent in Scion chat to advance the checkpoint) switches the entire workspace tree on disk in `<2 seconds`, letting participants run `oase validate check` (381 sidecars, 67 JSONPath claims) and `oase site build` (28-page HTML portal) live without waiting 45 minutes for upstream tournament epochs.
3. **`negative-gate-audit` (`pilot-9b` Hidradenitis Suppurativa 0/8 Refusal):** Pre-loaded at `DEC-145` so participants can audit how OASE's `finding-validator` and `science-program-lead` killed 7 flawed concepts on human clinical/genetic counter-evidence and caught upstream seed citation-padding.

<details>
<summary>Reasoning — Stage 3</summary>

- **Skepticism check:** Every question reflects a real objection raised by biopharma AI platform teams (OpenAI/AWS incumbency, chatbot fatigue, wet-lab/CRO handoff reality, custom container friction, runaway Vertex GPU bills, and live workshop latency).
- **Evidence check:** Every answer cites real mechanisms in `oase v0.3.0` (`tool-design-guidance.md`, `operating-environment.md`, `quickstart-pilot.md`, `h5ad-percell-tool.md`, `pilot-9b`, `pilot-10`, `pilot-6`).
</details>

---

## Stage 4: Internal FAQ (Google Cloud & OASE Engineering Lens)

### Q1 (Engineering & Architecture): What is the exact boundary between what exists in `oase v0.3.0` (`main` at `707e461`) today vs. what the workshop scripts package?
- **Already in `oase v0.3.0` (`707e461`):**
  - 61 registered CLI command groups in `tools/oase/commands/` (`admet`, `allen`, `alphafold`, `alphagenome`, `analog`, `artifact`, `assay`, `cbioportal`, `cellxgene`, `cite`, `compound`, `compreg`, `conservation`, `coscientist`, `dice`, `differentiation`, `disco`, `disignatlas`, `docking`, `doctor`, `dossier`, `env`, `expression`, `faers`, `genetics`, `geo`, `gtex`, `gwas`, `homology`, `hypex`, `hypothesis`, `init`, `litref`, `manufacturing`, `mmp`, `mpo`, `patent`, `pathway`, `phenotype`, `pk`, `pocket`, `ppi`, `preprint`, `program`, `pubchem`, `pubmed`, `pubmed-bq`, `relays`, `retro`, `run`, `schema`, `scp`, `screen`, `selectivity`, `similar`, `site`, `spatialdb`, `structure`, `structure-screen`, `tools`, `tox`, `triage`, `trials`, `validate`, `wo`/`workorder`).
  - **62nd CLI command group (`oase h5ad`):** Built on branch `feat/h5ad-reanalyse` (`8a64d02` / `029b0f2`) during `pilot-10` (`tools/oase/commands/_h5ad_io.py`, `tools/oase/commands/h5ad.py`, `tests/test_h5ad.py` — 49/49 tests passing). In the workshop environment, we merge `feat/h5ad-reanalyse` (and install `h5py` in the shared venv) so `oase h5ad fetch` and `oase h5ad analyze` work out-of-the-box and serve as the live case study in Module 5 (`docs/05-extend-custom-tools.md`).
  - **22 Agent Templates across 13 Roles in `templates/`:** `admet-dmpk-scientist`, `bootstrapper`, `computational-biologist`, `computational-chemist`, `experimental-biologist`, `finding-validator`, `head-of-discovery`, `hypex-evolution`, `hypex-generation`, `hypex-meta-review`, `hypex-proximity`, `hypex-reflection`, `hypex-supervisor`, `hypex-tournament`, `medicinal-chemist`, `preclinical-toxicologist`, `project-curator`, `regulatory-scientist`, `research-operations-controller`, `science-program-lead`, `scientific-reviewer`, `structural-biologist`.
  - **41 Capability & Orchestration Skills in `skills/`.**
- **Known `v0.3.0` Quirks Addressed by Workshop Scripts (`preflight.sh` / `seed-hub.sh`):**
  1. **`site.py` KaTeX Offline Bundle Path:** `site.py` checks `/scion-volumes/tools/vendor/katex/katex.min.css`. `preflight.sh` pre-populates that directory so `oase site build` succeeds 100% offline.
  2. **AlphaFold 3 Vertex Endpoint Env Vars:** `oase alphafold predict` reads `OASE_AF3_PROJECT`, `OASE_AF3_REGION`, `OASE_AF3_ENDPOINT_NAME`, and `OASE_AF3_LOCK` (authenticating via GCE ADC `google.auth.default()`). `preflight.sh` validates these and executes a smoke check.
  3. **AlphaGenome Vertex Endpoint Env Vars:** `oase alphagenome score-variant` and `predict-interval` default to `--backend vertex` using `OASE_AG_PROJECT`, `OASE_AG_REGION`, `OASE_AG_ENDPOINT_ID`, and `OASE_AG_ENDPOINT_DNS` (`*.prediction.vertexai.goog`) via GCE ADC. Note that `oase alphagenome ism` requires `--backend pip` + `ALPHAGENOME_API_KEY`; our workshop live exercises use `score-variant` and `predict-interval` on the Vertex endpoint so no external pip API key is needed.
  4. **`commands/disco.py` Boundary Bug:** As documented in `h5ad-percell-tool.md`, `disco.py` reads `project` instead of `project_id`. We document this transparently in `docs/05-extend-custom-tools.md` and `docs/07-troubleshooting.md` as the exact real-world catalyst that triggered `OQ-017` and the creation of `oase h5ad`.

---

### Q2 (Cloud Architecture & Compute Sizing): What Google Cloud services power an active GCP-OASE deployment in production?
Deploying OASE activates five integrated Google Cloud infrastructure and AI layers:
1. **Vertex AI Foundation & Partner Model Endpoints (`Gemini 4` + `Claude`):** A single Stage 0–2 multi-agent campaign executes 100–300 long-context agent turns across 13 roles plus 46-agent `Hypex` tournament swarms using Vertex AI MaaS (`Gemini 4 Pro/Flash` and `Claude` Partner Models).
2. **Vertex AI Dedicated GPU Endpoints (`AlphaFold 3` & `AlphaGenome`):** Both `oase alphafold predict` and `oase alphagenome score-variant` call Vertex AI Dedicated Endpoints backed by NVIDIA L4 (`g2-standard-12`) or A100 (`a2-ultragpu-1g`) GPUs. Because OASE integrates AF3 co-folding (`--template complex`, `--template ligand`) and AlphaGenome 11-assay variant scoring directly into Stage 1 and Stage 2 Work Orders, every target campaign exercises GPU inference endpoints.
3. **BigQuery Compute & Storage (`oase pubmed-bq` + Custom Omics Tables):** High-throughput literature triage (`oase pubmed-bq search`) and enterprise single-cell/biobank cohort queries run on BigQuery.
4. **GCE / GKE + Cloud Storage (`Scion Hub` + `/scion-volumes/tools` + Artifact Archives):** Persistent Scion Hub VMs/GKE clusters hosting multi-user discovery groves, plus GCS buckets storing staging payloads, raw `.h5ad` atlases, and exported static evidence portals (`oase site export`).
5. **Expansion Path to FoldRun & Cloud Run Custom Tools:** When a target passes Stage 1 in OASE and requires 500-compound Boltz-2/AF3 batch screening or custom container execution (Pattern D), teams burst onto Vertex AI Pipelines / Cloud Run jobs.

---

### Q3 (Legal, IP & Safety Guardrails): Are there any brand, licensing, or safety-filter risks in the workshop materials?
1. **Zero Legacy Internal Code Names:** All customer-facing workshop docs, scripts, slides, and PRFAQ materials use **GCP-OASE (Open Agentic Science Engine)** and **Scion**.
2. **Open-Source Licensing Cleanliness:** `oase` is Apache 2.0; upstream skills derived from `google-deepmind/science-skills` carry Apache 2.0 / CC-BY 4.0 attribution (`docs/skill-design-guidance.md` §6.8). AlphaFold 3 predictions via Vertex AI follow standard Vertex AI service terms.
3. **AI Safety Filter Compliance:** All pilot walkthroughs (`pilot-9b` Hidradenitis Suppurativa, `pilot-10` Hepatic Fibrosis, `pilot-6` NSCLC EZH2/EED) focus strictly on software orchestration, human genetic/transcriptomic target triage, provenance verification, and governance decision gates—avoiding any dual-use pathogen or restricted toxin generation.

---

### Q4 (Operations & Live Workshop Execution): What is our contingency if a live Vertex endpoint or external API (gnomAD / Europe PMC) throttles or hiccups during a live workshop session?
We have **three layers of operational insulation**:
1. **Pre-Flight Gate (`scripts/preflight.sh` + `oase doctor --json`):** Run T-24h and T-1h before the workshop to verify Vertex ADC tokens, AF3/AlphaGenome endpoints, KaTeX offline assets, `fpocket`/`vina` binaries, and `ENV_VERSION` integrity.
2. **Phase 2 Offline Latch (51/51 `analyze` commands):** Even if an external public API (`gnomAD`, `GTEx`, `Europe PMC`) is completely unreachable during the workshop, every `oase <tool> analyze`, `oase validate check`, and `oase site build` command runs **100% offline** against the pre-fetched `raw/` bytes in `stage0-1-walkthrough` and `negative-gate-audit`.
3. **3-Second Full Reset (`scripts/reset-workshop.sh`):** If a participant accidentally corrupts a live grove or stops the controller mid-bootstrap, `scripts/reset-workshop.sh` restores `/home/scion/.scion/snapshots/golden-hub.db` and resets the Git checkpoint tags in `<3 seconds` without dropping OAuth logins.

---

### Q5 (Post-Workshop Sandbox Rollout): What is the concrete "Definition of Done" for the workshop, and what is the 30/60/90-day adoption path?
- **Workshop Day Success Metrics:**
  1. **100% of participants** log into the shared Scion Hub, co-steer a live multi-agent campaign in `live-sandbox`, and trigger live Vertex AI (`Gemini 4`, `AlphaGenome`, `AlphaFold 3`) + `oase` CLI calls.
  2. **100% of participants** execute `oase validate check --dry-run` and `oase site build` on `stage0-1-walkthrough` (`pilot-10`), inspecting the 28-page evidence portal and the `pilot-9b` (`0/8` negative gate) audit trail.
  3. **Platform Engineers** complete the 3-step custom tool walkthrough (`oase h5ad` + Pattern A–D blueprint) and confirm how their existing OpenAI/Claude harnesses and internal Docker containers map into Scion.
- **30/60/90-Day Sandbox Adoption Path:**
  - **Week 1:** Deploy `oase-workshop` Golden VM / Terraform stack into the team's dedicated GCP sandbox project with Vertex AI `Gemini 4`, `Claude`, `AlphaFold 3`, `AlphaGenome`, and `BigQuery` enabled.
  - **Day 30:** Onboard 1–2 internal discovery tools via the 3-Step Container Contract (`Tool → Skill → Template`) and configure custom `.oase/thresholds.yaml` and wet-lab stopping gates.
  - **Day 60–90:** Run 2 live therapeutic target triage campaigns (Stage 0 → Stage 1 wet-lab handoff) with weekly friction-log reviews (`docs/pilot-handoff.md`).

<details>
<summary>Reasoning — Stage 4</summary>

- **Stakeholder coverage:** Addressed Engineering (`707e461` + `feat/h5ad-reanalyse` exact delta), Cloud Architecture (5 concrete GCP service layers), Legal/Safety (zero legacy naming, Apache 2.0, safety filter compliance), Operations (3-layer live fallback), and 30/60/90-day Sandbox Adoption.
</details>

---

## Stage 5: Verdict

| Criterion | Assessment | Evidence |
|---|---|---|
| **1. Customer & Problem Specificity** | **PASS** | Anchored to biopharma R&D personas (Platform Engineers, Computational Biologists, Discovery Governance Leads) and the concrete operational failure of static DAGs vs. hallucinating single-user chatbots. |
| **2. Differentiation & Team-Based Science** | **PASS** | Articulates 4 structural differentiators no point SaaS or DIY LangGraph script has: (1) Multi-human Scion groves with subway-map dynamic routing across 22 T-shaped templates, (2) Multi-model harnesses (`Gemini 4` + `Claude` + `OpenAI`) as a scientific control, (3) Two-phase offline-latched anti-fabrication (`51/51` commands + 10-check `validate`), and (4) Configurable wet-lab/CRO handoff + 3-step custom container onboarding. |
| **3. First-Party GCP AI Pull-Through** | **PASS** | Directly embeds Vertex AI `Gemini 4`, `AlphaFold 3` (monomer/complex/ligand co-folding), `AlphaGenome` (11 regulatory assays), Vertex Partner Models (`Claude`), `BigQuery` (`pubmed-bq`), and `GCE`/`GCS` into the daily scientific loop. |
| **4. Empirical Proof & Honesty (Anti-Hype)** | **PASS** | Leads with real negative gates (`Pilot-9b` rejecting 8/8 HS concepts at `DEC-145`; `Pilot-10` catching empty snapshots and overturning bulk GTEx nulls via `oase h5ad`; `Pilot-6` catching 4 preclinical traps before CRO spend). Zero banned marketing weasel words. |
| **5. 150-Minute Workshop Deliverability** | **PASS** | Solves the 25–45 min latency problem via `<2 sec` Git-tagged Time-Machine Checkpoints (`ch0`–`ch4`), offline-latched Phase 2 analysis, pre-populated KaTeX assets, and a `<3 sec` `reset-workshop.sh` snapshot restore. |

### Final Verdict: **PASS** — Proceed to Concept Brief (`brief.md`) and GitHub Workshop Asset Generation.

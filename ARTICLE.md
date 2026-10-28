# Introducing GCP-OASE: From Isolated Chatbots to Team-Based Agentic Pre-Clinical R&D on Google Cloud

[Agentic AI in life sciences](https://cloud.google.com/life-sciences) is transforming how pre-clinical discovery teams evaluate therapeutic targets and design molecules. By connecting foundation models and computational biology tools across the drug discovery funnel, AI agents can now assist with everything from **human genetic target validation** that links population loss-of-function variants to disease, to **single-cell transcriptomics** that isolates disease-specific cell states, to **3D protein-ligand co-folding** and **multi-parameter lead optimization (DMTA)** that de-risk candidates before wet-lab synthesis.

Yet building production-ready agentic science that a pharma governance board can actually trust remains challenging. We built **GCP-OASE (Open Agentic Science Engine)** on **Google Cloud Vertex AI** and **Scion** to change that—an open, code-first platform designed to replace isolated single-player chatbots and brittle bioinformatics scripts with **team-based, multi-model, provenance-locked discovery**.

![GCP-OASE Intro](assets/oase_post_thumbnail.jpg)

---

## Quick Navigation — 150-Minute Hands-On Workshop Kit

| Role | Start Here | Deep-Dive Modules |
|---|---|---|
| **Computational Biologist / Discovery Scientist** | [01 — Tour the Grove](docs/01-tour-the-grove.md) | [02 — Launch a Team Campaign](docs/02-launch-campaign.md) · [03 — Evidence, Viewers & Refusals](docs/03-evidence-and-refusals.md) · [04 — Make It Yours & Wet-Lab Handoffs](docs/04-make-it-yours.md) |
| **AI Platform / Bioinformatics Engineer** | [00 — GCP & Vertex Prerequisites](docs/00-prerequisites.md) | [01 — Tour the Grove](docs/01-tour-the-grove.md) · [05 — Extend Custom Tools (`oase h5ad`)](docs/05-extend-custom-tools.md) · [07 — Troubleshooting](docs/07-troubleshooting.md) |
| **Discovery Governance / R&D Leader** | [Working Backwards PRFAQ](PRFAQ.md) | [03 — Evidence & Refusals (`Pilot-9b`, `Pilot-10`, `Pilot-6`)](docs/03-evidence-and-refusals.md) · [3-Pass Evaluation Log](.beagle/concepts/oase-workshop/eval-log.md) |
| **Workshop Facilitator / Instructor** | [06 — Facilitator Run-of-Show Guide](docs/06-facilitator-guide.md) | [00 — GCP & Vertex Prerequisites](docs/00-prerequisites.md) · [07 — Troubleshooting](docs/07-troubleshooting.md) |

---

## Why Agentic Drug Discovery Is Harder Than It Looks

The concept is simple: give AI agents access to biological databases and structure predictors to accelerate target triage and hit-to-lead. The implementation? That's where things get complicated.

![Agentic Drug Discovery Challenges](assets/oase_challenges.jpg)

**The rigid workflow problem.** Traditional bioinformatics pipelines (Nextflow, Snakemake) and static LangGraph DAGs assume Step B always follows Step A. That works for read alignment, but biological discovery is full of surprises. When a bulk liver RNA-seq query in GTEx returns near-zero expression for a fibrosis target, a fixed pipeline drops the gene. A real discovery team asks whether activated stellate cells in *cirrhotic* liver express it—and pivots mid-flight to slice a single-cell `.h5ad` matrix. Nor do real programs march from Stage 0 to Stage 4 non-stop on a computer; teams pause after target validation or virtual screening to run wet-lab assays internally or at a CRO (WuXi, Charles River), then return weeks later with experimental CSVs.

**The chatbot fabrication trap.** Many agent prototypes stuff 50 MB omics tables, PDB coordinates, or PubMed abstracts directly into an LLM context window and ask the model to summarize the numbers in prose. When a tool fails to install or a query returns an empty set, an unguarded LLM invents a plausible IC50, pads citations, or mistakes a missing gene column (`NA`) for zero expression (`0`). Worse, if fetching data and judging thresholds happen in the same step, there is no raw artifact on disk for an independent reviewer to audit.

**The single-model echo chamber.** Most enterprise AI tools lock your entire workflow into a single model vendor. When the same model family generates a therapeutic hypothesis, interprets the literature, and conducts the scientific review, correlated training bias takes over—the model agrees with its own blind spots and rubber-stamps weak targets that later fail in $250,000–$1,000,000 wet-lab campaigns.

**The fragmented scientific tool stack.** A single target validation and lead-optimization campaign requires calling first-party foundation models (**AlphaFold 3** for protein-ligand co-folding, **AlphaGenome** for non-coding regulatory variant scoring, **Gemini 4** for long-context synthesis), 60+ open-source scientific libraries (`RDKit`, `AutoDock Vina`, `fpocket`, `gnomAD`, `OpenTargets`, `CELLxGENE`, `h5py`), **BigQuery** for literature mining, and your organization's proprietary internal Docker containers. Wiring credentials, rate limits, file schemas, and provenance across all of those takes months of infrastructure work before a scientist can ask a single question.

---

## How GCP-OASE Solves These Problems

**GCP-OASE (Open Agentic Science Engine)** on Google Cloud directly addresses each of these challenges:

![GCP-OASE Benefits](assets/oase_benefits.jpg)

| Challenge | GCP-OASE Solution |
|---|---|
| **The rigid workflow problem** | **Team-Based Science & Subway-Map Routing (`Scion`)**: 5–10 human scientists share a live workspace ("Google Docs for R&D pods") to co-steer 22 T-shaped agent templates across 13 roles. Like a subway navigator, agents evaluate validated evidence at each stop (`DEC-001`..`DEC-N`) and dynamically route the next Work Order—or pause at configurable **Wet-Lab / CRO Stopping Gates** (`oase assay`, `oase selectivity`, `oase pk`). |
| **The chatbot fabrication trap** | **Two-Phase Zero-Fabrication Funnel & 10-Check Validator**: Raw matrices never enter LLM context. **Phase 1 (`fetch`/`run`/`predict`)** writes raw bytes to `raw/` with a SHA-256 `.meta.json` sidecar. **Phase 2 (`analyze`)** is network-latched offline across all 51 analysis commands to apply `.oase/thresholds.yaml`. Before any finding closes, `oase validate check` enforces 10 mechanical checks verifying every `{source: raw/... $.jsonpath}` claim. |
| **The single-model echo chamber** | **Model Diversity as a Scientific Control**: Scion decouples the **Agent Template** from the **Model Harness**. Run **Vertex AI Gemini 4** for 1M+ token orchestration, **Anthropic Claude** (on Vertex AI Partner Models) for adversarial `Scientific Reviewer` audits, and **Gemini 4 + Claude + OpenAI** in blind `Hypex` ELO debate tournaments so no single model ever grades its own homework. |
| **The fragmented scientific tool stack** | **First-Party GCP Scientific AI + 62 CLI Tools + 3-Step Extensibility**: One unified `oase` CLI calls **Vertex AI AlphaFold 3** (monomer, PPI complex, and SMILES ligand co-folding), **Vertex AI AlphaGenome** (11 regulatory assays), and **BigQuery** (`pubmed-bq`) alongside 62 open-source CLI tool groups—plus a **3-Step Container Contract (`Tool → Skill → Template`)** to plug in custom internal tools without rebuilding agent images. |

In the rest of this post, we'll walk through the [official GCP-OASE Hands-On Workshop](docs/01-tour-the-grove.md), which runs a cross-functional discovery campaign for **Hepatic Fibrosis (`Pilot-10`)** and audits real preclinical trap catches across **Hidradenitis Suppurativa (`Pilot-9b`)** and **NSCLC Degraders (`Pilot-6`)**.

---

## The Scenario: Hepatic Fibrosis Target Validation & The Bulk-Tissue Trap

Imagine your cross-functional discovery pod is investigating extracellular matrix remodeling targets—such as **MMP13**—for severe hepatic fibrosis (cirrhosis / MASH F3–F4). With a traditional static pipeline or a single-shot AI chatbot, the system queries healthy bulk liver RNA-seq in GTEx, sees `<0.5 TPM` median expression, and kills the target—completely missing the biological reality that scar-associated hepatic stellate and mesenchymal cells only expand inside *diseased cirrhotic tissue*. Or worse, the chatbot trusts a high volume of review papers, overlooks a mutated control cell line, and sends a flawed assay protocol to your CRO.

Now imagine a different experience. Five scientists from your team—a computational biologist, a human geneticist, a structural biologist, a medicinal chemist, and a discovery governance lead—join the same live **Scion** grove. When bulk GTEx returns near-zero expression in healthy liver, the `Science Program Lead` doesn't blindly drop the target or invent a number. Instead, it logs Open Question `OQ-017`, dispatches a specialist to pull and sub-cluster raw cirrhotic human liver `.h5ad` count matrices (`GSE212046`, `PRJNA913603`), and proves the target is expressed in disease-activated fibroblasts—while **Vertex AI AlphaGenome** scores non-coding regulatory variants and **Vertex AI AlphaFold 3** co-folds the protein-ligand complex.

### The Pre-Clinical R&D Challenges We'll Solve

Real discovery programs don't fail on textbook happy paths; they fail on subtle biological and data traps. Here are four real traps GCP-OASE caught across our benchmark pilot campaigns:

| Scenario / Pilot Campaign | What Naive AI / Static Pipelines Do | What GCP-OASE Actually Did |
|---|---|---|
| **Healthy Bulk Tissue Masks Disease Signal** (`Pilot-10` Hepatic Fibrosis, `WO-006`) | Sees `<0.5 TPM` in healthy GTEx bulk liver and drops `MMP13`—or hallucinates cell-type expression from abstract text. | Opened `OQ-017`, built and ran `oase h5ad` across 5 cirrhotic human liver single-cell samples (`DISCO` & `CELLxGENE`), distinguished provider-filtered genes (`searched_absent` = `NA`) from zero counts (`0`), and overturned the bulk GTEx null. |
| **Padded Citations & Weak Stage 0 Seeds** (`Pilot-9b` Hidradenitis Suppurativa, `DEC-145`) | Rubber-stamps the "top 3" candidate targets from an initial literature seed list so the pipeline has something to advance. | Audited 8 candidate HS concepts across 153 logged decisions (`DEC-001`..`DEC-153`), caught upstream seed citation-padding via `oase litref resolve`, and **advanced 0 of 8 (`DEC-145`)** on human genetic/clinical counter-evidence. |
| **Literature Bias & Mutant CRO Control Cells** (`Pilot-6` NSCLC PROTAC, `DEC-006` & `DEC-009`) | Trusts high publication count on `LAIR1` and approves standard `A549` cells as a wild-type CRO control line. | Refuted `LAIR1` using knockout mouse survival data (`DEC-006`), queried `cBioPortal`/DepMap to flag that `A549` carries confounding `STK11`/`KEAP1` mutations (`DEC-009`), and substituted a clean control line *before* CRO spend. |
| **Unverified Degrader Ternary Complex** (`Pilot-6` NSCLC PROTAC, `DEC-032` & `DEC-034`) | Pushes a weak VHL warhead into synthesis without checking 3D ternary complex geometry. | Halted the VHL series after flagging a `1,000x` binding affinity loss (`DEC-032`) and ran **Vertex AI AlphaFold 3 co-folding** (`DEC-034`) to confirm `EED226-CRBN` ternary complex stability (`ipTM 0.88`). |

GCP-OASE handles all four scenarios with a single, provenance-locked architecture. The rest of this guide walks through how each piece fits together.

---

## GCP-OASE Data and Control Architecture

Before diving into commands, let's understand how GCP-OASE organizes your discovery program. The architecture centers on four key concepts: **Scion Groves**, **Work Orders (`WO`)**, **Two-Phase Artifacts (`Layer 0` & `Layer 1`)**, and the **3-Step Capability Contract (`Tool → Skill → Template`)**.

![GCP-OASE Data and Control Architecture](assets/oase_data_arch.jpg)

A **Scion Grove** is a shared multi-human, multi-agent project workspace backed by an on-disk `.oase/` control plane (`program.yaml`, `thresholds.yaml`, `control/work-orders/`, `control/events.ndjson`). **Work Orders (`WO-001`..`WO-N`)** are bounded scientific tasks dispatched dynamically by the `Science Program Lead` and `Research Operations Controller`—never a hardcoded DAG. **Two-Phase Artifacts** separate raw data acquisition (**Layer 0** under `raw/<class>/`, stamped with SHA-256 `.meta.json` sidecars and offline-latched `.analysis.json` verdicts) from specialist prose interpretations (**Layer 1** under `findings/`). Finally, the **3-Step Capability Contract** decouples deterministic CLI code (`tools/oase/commands/`) from specialist-neutral routing rules (`skills/`) and role permissions (`templates/`).

---

## Running a Team-Based Discovery Campaign: Step by Step

Now let's run a working discovery workflow. We'll bootstrap a multi-agent grove in one command, score regulatory variants and co-fold complexes on **Vertex AI**, slice single-cell `.h5ad` matrices offline, enforce the 10-check mechanical validator, and re-ingest wet-lab CRO data—all in five steps.

### Step 1: Launch a Multi-Human, Multi-Model Grove in One Command

Starting an OASE program from a clean environment requires **one command**. You pass your scientific directive (target scope, indication, modality, and stopping gate) to the `Research Operations Controller`:

```bash
scion start controller --type research-operations-controller \
  "Program directive: Conduct Stage 0 portfolio triage and Stage 1 target validation for extracellular matrix remodeling and stellate-cell activation targets in Hepatic Fibrosis (cirrhosis / MASH F3-F4). Modality: small molecule. Stopping gate: pause after Stage 1 Target Validation Gate to export a wet-lab CRISPR/primary-stellate assay handoff package. Program directory: /workspace/live-sandbox"
```

This single command triggers the automated ROC bootstrap sequence (`docs/quickstart-pilot.md` §3): the controller verifies `/scion-volumes/tools/env.sh`, runs `oase doctor --json`, syncs all 22 agent templates (`scion template sync --all`), initializes `/workspace/live-sandbox/.oase/`, and starts the `Science Program Lead`.

Within 60 seconds, your pod can inspect the live agent roster and message agents directly in shared Scion threads:

```text
$ scion list
AGENT                           STATUS     ROLE                             HARNESS
controller                      running    research-operations-controller   vertex/gemini-4-pro
science-program-lead            running    science-program-lead             vertex/gemini-4-pro
wo001-r3-hypex-supervisor       running    hypex-supervisor                 vertex/gemini-4-pro
wo001-gen-1                     running    hypex-generation                 vertex/gemini-4-pro
wo001-rank-1                    running    hypex-tournament                 vertex/claude-sonnet-4-6
wo001-exam-1                    running    hypex-reflection                 openai/gpt-4.1
```

#### Why Model Diversity Matters as a Scientific Control

Notice the `HARNESS` column in the output above: `gemini-4-pro`, `claude-sonnet-4-6` (on Vertex AI Partner Models), and `openai/gpt-4.1` are running side by side in the same grove. This isn't arbitrary—it's an epistemic control that turns your existing multi-vendor LLM investments into a falsification mechanism.

When a single model generates a hypothesis and also evaluates it, self-preference bias inflates confidence scores by 15–30%. Because Scion decouples the **Agent Template** (`templates/<role>/scion-agent.yaml`) from the **Model Harness**, OASE assigns **Vertex AI Gemini 4** to long-context orchestration (`science-program-lead`), **Anthropic Claude** on Vertex AI to adversarial peer review (`scientific-reviewer`, `finding-validator`), and a heterogeneous panel (**Gemini 4 + Claude + OpenAI**) to blind pairwise debates in `Hypex` ELO tournaments (`oase hypex ingest` / `oase hypex analyze`). No single model family ever grades its own homework.

---

### Step 2: Score Regulatory Variants & Co-Fold Complexes on Vertex AI (`AlphaGenome` & `AlphaFold 3`)

While any LLM can reason inside a Scion harness, **Google Cloud Vertex AI** is where agents execute first-party biological foundation models—**AlphaGenome** and **AlphaFold 3**—through the exact same `oase` CLI contract as open-source tools.

Here is how the `Computational Biologist` and `Structural Biologist` invoke **Vertex AI AlphaGenome** (across 11 regulatory modalities) and **Vertex AI AlphaFold 3** (for monomer, protein-protein `--template complex`, or protein-ligand `--template ligand` co-folding):

```bash
source /scion-volumes/tools/env.sh
export OASE_PROJECT=/workspace/live-sandbox

# 1. Phase 1 (Online — Vertex AI AlphaGenome Dedicated Endpoint via GCE ADC):
#    Score a regulatory variant across RNA_SEQ and ATAC tracks (~4 seconds)
oase alphagenome score-variant \
  --chrom chr11 \
  --pos 102943000 \
  --ref C \
  --alt T \
  --output-type RNA_SEQ \
  --output-type ATAC \
  --scorer geneMask

# 2. Phase 2 (100% Offline-Latched — <1 second):
#    Apply .oase/thresholds.yaml to emit the structured verdict & mandatory relays
oase alphagenome analyze raw/genomics/chr11-102943000-C-T.scores.json

# 3. Fetch canonical 3D structure (cross-checked against UniProt length) & run fpocket
oase alphafold fetch P45452
oase alphafold analyze P45452
oase pocket run raw/structures/AF-P45452-F1.cif
oase pocket analyze raw/structures/AF-P45452-F1.pockets.json

# 4. Generate a Vertex AI AlphaFold 3 protein + SMILES ligand co-folding payload
oase alphafold predict --template ligand > raw/structures/af3-eed226-crbn.input.json
```

Running `oase alphafold predict --template ligand` emits the canonical AlphaFold 3 co-folding schema, ready for single-flight submission (`oase alphafold predict --input ...`) to your Vertex AI AlphaFold 3 Dedicated Endpoint:

```json
{
  "dialect": "alphafold3",
  "version": 1,
  "name": "my_docking",
  "modelSeeds": [42],
  "sequences": [
    {"protein": {"id": "A", "sequence": "REPLACE_WITH_SEQUENCE"}},
    {"ligand": {"id": "B", "smiles": "REPLACE_WITH_SMILES"}}
  ]
}
```

#### Why the Two-Phase Split (`fetch` vs. `analyze`) Is Non-Negotiable

Notice that every tool above runs in two distinct commands: Phase 1 (`score-variant`, `fetch`, `run`, `predict`) and Phase 2 (`analyze`). At the root of the CLI command tree, `oase` **latches the HTTP client completely offline** during all 51 `analyze*` subcommands—raising `PhaseContractError` if any code attempts a network call (`docs/tool-design-guidance.md` §3).

This two-phase split buys your team three concrete guarantees:
1. **Zero-Cost Threshold Tuning:** Cold AlphaFold 3 co-folding takes 5–10 minutes on GPU; a `Hypex` tournament takes 30 minutes. Because Phase 2 reads stored `raw/` bytes offline, changing a cutoff in `.oase/thresholds.yaml` and re-running `oase <tool> analyze --overwrite` takes **`<0.2 seconds` at `$0` compute cost**.
2. **Mechanical Peer Review:** The `Scientific Reviewer` (running on Claude) re-runs `analyze` against Layer 0 bytes on disk and diffs the output against the specialist's prose.
3. **Mandatory Liability Relays:** Phase 2 stamps registered relay codes (19 codes inspectable via `oase relays`, such as `afdb.confidence_is_not_accuracy` and `afdb.model_is_not_docking_ready`) into `.analysis.json`. If a specialist omits a relay code in its report, `oase validate check` blocks the work order.

---

### Step 3: Pivot Mid-Flight When Biology Surprises You (`oase h5ad` Single-Cell Slicing)

Now the Moment of Truth from **`Pilot-10` (Hepatic Fibrosis)**. When healthy bulk liver RNA-seq from GTEx (`oase gtex fetch`) returned `<0.5 TPM` for `MMP13`, our discovery pod needed to check whether activated mesenchymal/stellate cells in **human cirrhotic liver** express the gene.

Using `oase h5ad` (built during `Pilot-10` under `OQ-017` and verified by 49 unit tests in `tests/test_h5ad.py`), the `Computational Biologist` downloads raw `.h5`/`.h5ad` count matrices from `DISCO` (`GSE212046`, `PRJNA913603`) and `CELLxGENE` in Phase 1, then runs offline per-cell counting and unsupervised sub-clustering (`log1p CP10K → HVG → PCA → seeded k-means++`) in Phase 2:

```bash
# Phase 1: Download verbatim 10x H5 / H5AD matrices + per-cell label TSVs into raw/single-cell/
oase h5ad fetch GSM6508438 GSM6508440 --source disco

# Phase 2 (100% Offline): Extract per-cell counts for MMP13, MMP1, MMP8 with ACTB positive control
oase h5ad analyze GSM6508438 GSM6508440 \
  --source disco \
  --gene MMP13 --gene MMP1 --gene MMP8 \
  --select-label "CFD+MGP+ fibroblast" \
  --control ACTB
```

Here is what `oase h5ad` discovered on those real cirrhotic liver samples (`h5ad-percell-tool.md`):

```text
Sample       DISCO Project  SHA-256 (prefix)  Distinct Mesenchymal / Fibroblast Labels Present (Verbatim)
=================================================================================================================
GSM6508438   GSE212046      a0142e480a46...    Hepatocyte (4455), T cell (1338), CFD+MGP+ fibroblast (646), LYVE1 macrophage (445)
GSM6508440   GSE212046      216f4ac73d47...   Hepatocyte (2965), T cell (2580), CFD+MGP+ fibroblast (1148), CCL19+APOE+ fibroblast (239)
SRX18764703  PRJNA913603    30f04e491140...   GZMK CD8 T cell (1188), LYVE1 macrophage (301), Mesenchymal stromal cell (221)

Gene Parse Status Check (CELLxGENE d7476ae2-e320-4703-8304-da5c42627e71, 12,621 features):
  ACTB (Positive Control) : measured         (non-zero counts verified)
  MMP14 / MMP2 / MMP9     : measured         (present in provider feature list)
  MMP13 / MMP1 / MMP8     : searched_absent  (provider-filtered -> written as 'NA', never '0'!)
```

Two design rules in `oase h5ad` prevented a major scientific error here:
1. **Zero Label Guessing:** None of the 5 cirrhotic liver samples in DISCO contained a label literally named `"stellate"`; the atlas annotated that compartment as `"CFD+MGP+ fibroblast"` and `"Mesenchymal stromal cell"`. When an agent passes `--select-label "Activated stellate cell"`, `oase h5ad` refuses (`exit 2`) and lists the exact labels present rather than guessing.
2. **Absence vs. Failure (`NA` vs. `0`):** In the CELLxGENE dataset, `MMP13` was filtered out of the provider's 12,621-gene feature list. A naive script reports `0` expression; `oase h5ad` stamps `parse_status: searched_absent` and writes `NA`.

---

### Step 4: Enforce the 10-Check Mechanical Gate & Pause for Wet-Lab / CRO Handoff

Before any Work Order can be accepted into a campaign's decision ledger, the `Research Operations Controller` runs `oase validate check`. In the workshop, you can jump straight to **Checkpoint 4 (`ch4-site-published`)** in `<2 seconds` and run the validator yourself:

```bash
cd /workspace/stage0-1-walkthrough
/workspace/workshop/scripts/checkpoint.sh goto ch4

# Run all 10 mechanical validation checks against Work Order WO-005
oase --project /workspace/stage0-1-walkthrough validate check --dry-run WO-005
```

Across `Pilot-10`, `oase validate check` verified **381 SHA-256 `.meta.json` sidecars and 67 inline `{source: raw/... $.jsonpath}` numerical claims** with zero mismatches.

And when your campaign reaches its configured **Stage 1 or Stage 2 Stopping Gate**, OASE pauses at **zero compute cost** while your wet-lab or CRO partner (WuXi, Charles River) runs the physical assays. When the experimental CSVs/JSONs return weeks later, you drop them into `raw/` and re-ingest them directly:

```bash
# Re-ingest physical CRO IC50 assay, off-target selectivity panel, and rodent PK data:
oase assay ingest raw/assays/cro-batch-01.json
oase assay analyze raw/assays/cro-batch-01.assay.json

oase selectivity compare raw/assays/selectivity-panel-01.json
oase selectivity analyze raw/assays/selectivity-panel-01.selectivity.json

oase pk ingest raw/assays/rat-pk-01.json
oase pk nca raw/pk/rat-pk-01.pk-study.json --blq-method exclude
oase pk scale raw/pk/rat-pk-01.pk-nca.json
oase pk analyze raw/pk/rat-pk-01.pk-scaling.json
```

By standing rule (`docs/tool-design-guidance.md` §1.1), **a model prediction never overrides a primary measurement**—when an `AutoDock Vina` or `RDKit ADMET` prediction disagrees with your CRO `oase assay` readout, OASE flags the disagreement itself as the primary finding for the next DMTA cycle.

---

### Step 5: Compile the 28-Page Evidence Portal & Extend with Custom Containers in 3 Steps

Once Work Orders pass validation, `oase site build` compiles the entire campaign into a self-contained static HTML evidence portal—complete with **14 interactive scientific viewers** (`plddt-viewer`, `pae-viewer`, `constraint-viewer`, `expression-viewer`, `tournament-viewer`, `docking-viewer`, `admet-viewer`, `mpo-viewer`, `selectivity-viewer`, `pk-viewer`, `trials-viewer`, `faers-viewer`, `pathway-viewer`, and `dossier-viewer`):

```bash
# Validate all internal links/citations and build the 28-page static HTML portal (<3 seconds, 100% offline)
oase --project /workspace/stage0-1-walkthrough site validate
oase --project /workspace/stage0-1-walkthrough site build
```

And whenever your platform engineering team wants to plug an internal Python package, static C++ binary, sidecar Docker container, or custom Vertex AI / Cloud Run model endpoint into GCP-OASE, you never rebuild monolithic agent images. You follow the **3-Step Container Contract (`Tool → Skill → Template`)** detailed in [Module 05](docs/05-extend-custom-tools.md):
1. **Tool (`tools/oase/commands/<name>.py`):** Implement Phase 1 (`fetch`/`run`) + Phase 2 (`analyze`, automatically offline-latched) and run `./install.sh --update` to stamp `/scion-volumes/tools/ENV_VERSION`.
2. **Skill (`skills/<capability>/SKILL.md`):** Write a `<200-line` specialist-neutral Markdown routing contract with an explicit invocation table and anti-fabrication guard.
3. **Template (`templates/<role>/scion-agent.yaml`):** Add the skill to the role's `skills:` grant and run `scion template sync --all`.

---

## The Complete Picture

In just five steps—which you can run hands-on in our **150-minute workshop** using `<2 second` Git time-machine checkpoints (`ch0`–`ch4`)—we went from a single-line therapeutic directive to a multi-model tournament, live **Vertex AI AlphaGenome** & **AlphaFold 3** predictions, cirrhotic single-cell `.h5ad` slicing, wet-lab CRO re-ingestion, and a 28-page SHA-256-verified evidence portal:

![The Complete Picture](assets/oase_complete_picture.jpg)

GCP-OASE eliminates the false choice between rigid bioinformatics pipelines that break when biology surprises you and isolated chatbots that hallucinate numbers you can't defend in governance review. Your discovery pods focus on the science; the platform handles multi-model routing, Vertex AI foundation model execution, and mechanical provenance.

### Try It Yourself

Ready to run your own team-based discovery campaign on Google Cloud? Start here:

- **Hands-On Lab Walkthrough:** Start with [Module 00 — Prerequisites](docs/00-prerequisites.md) and [Module 01 — Tour the Grove](docs/01-tour-the-grove.md) to launch `live-sandbox`, `stage0-1-walkthrough` (`Pilot-10`), and `negative-gate-audit` (`Pilot-9b`).
- **Why Enterprise Biopharma Teams Adopt OASE:** Read the [Working Backwards PRFAQ](PRFAQ.md) and [3-Pass Evaluation Log](.beagle/concepts/oase-workshop/eval-log.md).
- **Extend OASE with Your Internal Containers:** Jump to [Module 05 — Extend Custom Tools (`oase h5ad` + Patterns A–D)](docs/05-extend-custom-tools.md).
- **Facilitator Guide (`150-Min Run of Show`):** See [Module 06 — Facilitator Guide](docs/06-facilitator-guide.md).

---

Agentic drug discovery used to mean choosing between static DAGs that can't pivot on a biological surprise and single-player chat windows that invent assay numbers. GCP-OASE replaces both with team-based, multi-model, provenance-locked computation on Google Cloud Vertex AI.

The gap between *"we tried an AI co-pilot"* and *"our discovery pods trust it to gate wet-lab spend"* just got a lot smaller.

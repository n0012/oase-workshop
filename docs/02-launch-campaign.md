# Module 02 — Launch a Live Team Campaign: Subway-Map Routing & `Hypex` Tournaments

> **Duration:** 30 Minutes (`0:20 – 0:50`)  
> **Hands-On Goal:** Form a 5-scientist discovery pod in **`live-sandbox`**, launch a live Stage 0→1 campaign with one command, co-steer the `Research Operations Controller` and `Science Program Lead` in shared Scion threads, and use the `<2s` Time-Machine (`ch1-stage0-hypex`) to inspect a completed 103-match `Hypex` ELO tournament.

---

## 1. The One-Command Program Launch (`docs/quickstart-pilot.md` §2)

In GCP-OASE, starting a multi-agent discovery program from a blank environment requires **one user action**. The `Research Operations Controller` (`controller`) automates the entire bootstrap sequence:
1. Verifies `/scion-volumes/tools/env.sh` and runs `oase doctor --json`.
2. Syncs all 22 agent templates to the Scion Hub (`scion template sync --all`).
3. Initializes the program directory (`oase init <dir>`), creating `.oase/thresholds.yaml`, `.oase/program.yaml`, and `.oase/control/` (`work-orders/`, `contexts/`, `runs/`, `validations/`, `leases/`, `events.ndjson`).
4. Writes the program brief (including capability checks and stopping gates) and starts the `Science Program Lead` (`science-program-lead`).

### Live Exercise 2.1: Start Your Pod's Controller in `live-sandbox`

In the `live-sandbox` terminal (or via the Scion Web UI **Start Agent** button), launch the controller with a Stage 0→1 target triage directive for **Hepatic Fibrosis**:

```bash
scion start controller --type research-operations-controller \
  "Program directive: Conduct Stage 0 portfolio triage and Stage 1 target validation for extracellular matrix remodeling and stellate-cell activation targets in Hepatic Fibrosis (cirrhosis / NASH F3-F4). Modality: small molecule or catalytic inhibitor. Stopping gate: pause after Stage 1 Target Validation Gate to export a wet-lab CRISPR/primary-stellate assay handoff package. Program directory: /workspace/live-sandbox"
```

Watch the bootstrap sequence unfold in real time (`~60 seconds`):

```bash
# 1. Watch controller and science-program-lead come online
scion list

# 2. Stream the controller's live bootstrap log
scion output controller

# 3. Inspect the initialized .oase/ control plane
ls -la /workspace/live-sandbox/.oase/
cat /workspace/live-sandbox/.oase/program.yaml
```

---

## 2. Team-Based Science in Action: Co-Steering in Shared Scion Threads

Unlike a static Nextflow pipeline or a single-user chatbot, **every human in your pod can interact with the running agents in the Scion Web UI**:

1. **Human #1 (CompBio / Genetics Lead):** Open the `science-program-lead` thread in the Scion Web UI. Watch as it frames the Stage 0 portfolio triage charter and dispatches **`WO-001`** to `hypex-supervisor` (and `oase pubmed-bq search` on BigQuery for rapid literature seeding).
2. **Human #2 (MedChem / Structural Lead):** Message `science-program-lead` directly in the shared chat thread:
   ```text
   @science-program-lead For any metalloproteinase candidate (e.g., MMP family) that emerges from Stage 0, require an explicit selectivity check against broad-spectrum musculoskeletal MMP liabilities (MMP1/MMP14) in Stage 1 before advancing.
   ```
3. **Human #3 (Discovery Governance Lead):** Inspect `.oase/control/work-orders/` and `.oase/thresholds.yaml` to see how your pod's mid-flight constraint is recorded in the control ledger and propagated into the next Work Order's context snapshot!

---

## 3. How `Hypex` Multi-Model Tournaments Prevent Single-Model Bias

When `science-program-lead` issues `WO-001` for Stage 0 hypothesis generation and ranking, it does not ask a single LLM *"Give me 10 targets for hepatic fibrosis."* Instead, it spawns the **7-role `Hypex` tournament subsystem**:

| Template Role | What It Does in the Tournament | Multi-Model Harness Assignment |
|---|---|---|
| `hypex-supervisor` | Orchestrates tournament epochs, enforces match budgets (`budget_exhausted`), and runs `oase hypex ingest` & `oase hypex analyze`. | **Vertex AI Gemini 4 Pro** |
| `hypex-generation` | Generates mechanistic therapeutic hypotheses grounded in `oase pubmed-bq` (BigQuery), `OpenTargets`, and `GWAS` evidence. | **Gemini 4 Pro** + **Claude** + **OpenAI** (parallel generation pods) |
| `hypex-proximity` | Clusters generated hypotheses to deduplicate redundant mechanisms before pairing. | **Vertex AI Gemini 4 Flash** |
| `hypex-tournament` | Runs blind head-to-head pairwise debates scored via ELO ratings across mechanism plausibility, human genetic support, and tractability. | Cross-family judges (**Claude** judging **Gemini** outputs and vice versa) |
| `hypex-reflection` | Conducts deep second-pass examination of top-ranked hypotheses for fatal flaws, missing comparators, or literature bias. | **Anthropic Claude** on Vertex AI |
| `hypex-evolution` | Refines surviving hypotheses to address tractable critiques discovered during reflection. | **Vertex AI Gemini 4 Pro** |
| `hypex-meta-review` | Synthesizes the tournament ledger into an auditable Stage 0 ranking memo for `finding-validator`. | **Vertex AI Gemini 4 Pro** |

---

## 4. Cooking-Show Time-Machine: Jump to `ch1-stage0-hypex` (`<2 Seconds`)

A full 14-concept, 103-match `Hypex` tournament across multiple epochs takes `~25–45 minutes` of wall-clock compute. While your `live-sandbox` agents continue executing their initial queries in the background, let's switch to the **`stage0-1-walkthrough` (`pilot-10`)** grove and jump straight to **Checkpoint 1 (`ch1-stage0-hypex`)**:

```bash
cd /workspace/stage0-1-walkthrough

# Jump to Checkpoint 1: Stage 0 Hypex Tournament Complete (<2 seconds)
/workspace/workshop/scripts/checkpoint.sh goto ch1
```

Now inspect the real Layer 0 and Layer 2 artifacts produced by `wo001-r3-hypex-supervisor` in `pilot-10`:

```bash
source /scion-volumes/tools/env.sh

# 1. Re-run Phase 2 offline analysis on the stored Hypex tournament run
oase --project /workspace/stage0-1-walkthrough hypex analyze \
  raw/hypotheses/WO-001-r3.hypex.json --overwrite

# 2. Inspect how the Science Program Lead handled an uncalibrated ELO gap (DEC-002)
grep -A 15 "DEC-002" /workspace/stage0-1-walkthrough/decisions/*.md 2>/dev/null || \
  ls -la /workspace/stage0-1-walkthrough/.oase/control/work-orders/
```

### Key Takeaway from Checkpoint 1 (`DEC-002` & `DEC-008`)
Notice what happened in `pilot-10` during Stage 0:
- In **`DEC-008`**, the controller caught an empty context snapshot on an early work-order revision and refused to proceed until the context was populated.
- In **`DEC-002`**, when `wo001-r3-hypex-supervisor` ranked 14 hepatic fibrosis concepts across **103 ELO matches**, the `Science Program Lead` refused to treat raw ELO point gaps as calibrated probabilities—requiring every surviving Stage 0 concept (`MMP13`, `LOXL2`, `TGFB1` axis, etc.) to pass primary human genetic, single-cell transcriptomic, and 3D structural falsification in Stage 1.

---

**Next Step:** Proceed to [Module 03 — Evidence, Viewers & Refusals](03-evidence-and-refusals.md).

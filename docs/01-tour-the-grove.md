# Module 01 — 4-Tier Architecture, Multi-Model Harnesses & Stage 0 Initiation (`ch1`)

> **Duration:** 20 Minutes (`0:15 – 0:35`)  
> **Hands-On Goal:** Inspect the **4-Tier / 22-Template Agent Architecture**, the **Single-Writer State Contract**, and portable model size aliases (`small | medium | large | extra-large`) on GCP; initiate the **`pcsk9-oral`** campaign via `bootstrap_campaign` (`A2UI_INPUT_REQUIRED`); run Stage 0 seed ingestion (`oase coscientist ingest/analyze`); and inspect `DEC-001` (`IC-001` vs. `IC-002`).

---

## 1. The 4-Tier Agent Roster (22 Templates) & Single-Writer State Contract

List the 22 agent templates registered in the Scion project:

```bash
ls -1 /workspace/templates/
```

| Agent Tier | Templates (22 Total) | Authority, Write Scope & Validation Role |
|---|---|---|
| **1. Authority & Governance Tier (2 Templates)** | `science-program-lead`, `head-of-discovery` (`<slug>-head-of-discovery`) | `science-program-lead` is the **sole writer** of Layer 2 `program-state/` (`active-series.md`, `decision-log.md`, `liability-tracker.md`, `open-questions.md`), owns work-order decomposition, executes **Validation 2** (independent Phase-2 reanalysis and scientific review of every `validation_passed` work order before logging `DEC-NNN` / `scientifically_accepted`), and prepares Stage Gate packages (`Stage 0 → Stages 1–4`). `<slug>-head-of-discovery` provides portfolio challenge and stage-gate governance alongside the human Project Owner. |
| **2. Operations, Validation & Curation Tier (4 Templates)** | `research-operations-controller`, `bootstrapper`, `finding-validator`, `project-curator` | `research-operations-controller` (`controller`) is the sole agent started by `GA`/`AGY` at campaign launch; it spawns `bootstrapper` (`oase init` + `oase doctor`), starts `science-program-lead` and `<slug>-head-of-discovery`, manages the **9-state work-order state machine** (`drafted → dispatched → in_progress → submitted → validating → validation_passed → under_scientific_review → scientifically_accepted → closed` in `.oase/control/events.ndjson`), dispatches `finding-validator` for **Validation 1** (the 10-check `oase validate check`), and wakes `project-curator` (`oase site build`). |
| **3. Domain Specialists & Independent Review Tier (9 Templates)** | `computational-biologist`, `structural-biologist`, `computational-chemist`, `medicinal-chemist`, `experimental-biologist`, `admet-dmpk-scientist`, `preclinical-toxicologist`, `regulatory-scientist`, `scientific-reviewer` | 8 ephemeral domain specialists (writing **only** to `findings/<domain>/` and `raw/`) plus 1 independent `scientific-reviewer`. |
| **4. HypEx Stage 0 Tournament Tier (7 Templates)** | `hypex-supervisor`, `hypex-generation`, `hypex-reflection`, `hypex-tournament`, `hypex-evolution`, `hypex-proximity`, `hypex-meta-review` | Multi-epoch ELO hypothesis generation, clustering, blind pairwise debate, reflection, evolution, and meta-review. All OASE agents operate on a push-only message bus (`sciontool status blocked` until woken by `---BEGIN SCION MESSAGE---`). |

### Multi-Model Harnesses as a Scientific Control on GCP
None of the 22 templates hardcodes a model string or CLI binary. Scion maps portable size aliases (`small`, `medium`, `large`, `extra-large`) to your configured harnesses on GCP:
- **Orchestration & Synthesis (`Gemini 4 Pro / Flash` — `gemini-cli` / `large` & `extra-large`):** Bound to `controller`, `science-program-lead`, and domain specialists.
- **Independent Peer Review (`Anthropic Claude` — `claude` / `large`):** Bound to `scientific-reviewer`, `finding-validator`, and `head-of-discovery` so a distinct model family audits specialist outputs.
- **Hypothesis Debate Tournaments (`Gemini 4` + `Claude` + `OpenAI` in `Hypex`):** Competing hypotheses are debated across heterogeneous model harnesses in blind pairwise matches.

---

## 2. Exercise 1.1 — Campaign Initiation & The A2UI Gate (`bootstrap_campaign`)

If the Project Owner asks `GA` or `AGY` to launch a campaign without specifying all required charter parameters, `bootstrap_campaign` halts before making any Hub mutation and returns `status: "A2UI_INPUT_REQUIRED"` to render the **A2UI Project & Campaign Initiation Card**. Once confirmed:

```json
{
  "ServerName": "scion",
  "ToolName": "bootstrap_campaign",
  "Arguments": {
    "project_id": "<oral-pcsk9-ascvd-uuid>",
    "program_slug": "pcsk9-oral",
    "program_directive": "Discover and optimize an oral QD allosteric small-molecule or macrocyclic peptidomimetic inhibitor of human PCSK9 (Q8NBP7) for ASCVD that disrupts LDLR degradation with hepatic selectivity, clean hERG/CYP safety, and competitive differentiation vs. injectable anti-PCSK9 mAbs (evolocumab/Repatha) and oral macrocycles (MK-0616/enlicitide).",
    "sponsor_gate_policy": "manual",
    "seed_mode": "sciarchitect",
    "stage_entry_point": "stage0_verification",
    "seed_bundle_dir": "/workspace/workshop/checkpoints/ch0/seed/pcsk9-oral"
  }
}
```

**What `bootstrap_campaign` Enforces:**
1. **Pre-Init Single-Writer Rule:** Does **not** create `/workspace/pcsk9-oral/` prior to `controller` startup (because `oase init /workspace/pcsk9-oral` requires the target directory to be non-existent or empty).
2. **Seed Staging to `/workspace/.seed/pcsk9-oral/`:** Uploads the 7-part seed bundle (`campaign-seed.json` with `oase.campaign-seed.v2` schema, `coscientist-export.json`, etc.) over WebDAV, verifies each file by read-back `GET` SHA-256 (`SEED_UPLOAD_CHECKSUM_MISMATCH` guard), and writes `CHECKSUMS.json` last.
3. **Controller-Only Launch:** Starts only `controller` (`--type research-operations-controller`, without `--role baseline`) and verifies `controller.template == "research-operations-controller"` (`CONTROLLER_TEMPLATE_MISMATCH` guard).

---

## 3. Exercise 1.2 — Stage 0 Seed Ingestion (`oase coscientist`) & Reading `DEC-001`

Inside the container, after `bootstrapper` runs `oase doctor` and `oase init /workspace/pcsk9-oral`, `science-program-lead` and `computational-biologist` (`WO-001`) ingest and analyze the tournament export:

```bash
# Phase 1: Ingest the staged SciArchitect tournament export into Layer 0 (raw/hypotheses/)
oase --project /workspace/pcsk9-oral coscientist ingest \
  /workspace/.seed/pcsk9-oral/coscientist-export.json \
  --top 10

# Phase 2 (100% offline): Apply threshold set coscientist@1.0 (elo_decisive_gap=50.0, min_win_rate=0.60)
oase --project /workspace/pcsk9-oral coscientist analyze \
  raw/hypotheses/pcsk9-oral-seed.json \
  --elo-decisive-gap 50.0 \
  --min-win-rate 0.60

# Inspect Rank 1 (IC-001) and verified literature references:
oase --project /workspace/pcsk9-oral coscientist show raw/hypotheses/pcsk9-oral-seed.json --rank 1
oase --project /workspace/pcsk9-oral coscientist references raw/hypotheses/pcsk9-oral-seed.json --gene PCSK9
```

> **Why `oase coscientist ingest` Instead of `oase hypothesis adopt`:** Always use `oase coscientist ingest <export_file>` for tournament seed bundles so all ranked hypotheses, Elo ratings, match ledgers, falsifiable predictions, and citations are preserved in Layer 0 (`oase hypothesis adopt` is a 2-field CLI `--title`, `--mechanism` for single ad-hoc sentences).

From `GA` or `AGY`, any team member can read `DEC-001` and `program-state/active-series.md` over WebDAV in ~1.5s without waking an agent container:

```json
{
  "ServerName": "scion",
  "ToolName": "decision_log",
  "Arguments": {
    "project_id": "<oral-pcsk9-ascvd-uuid>",
    "program_slug": "pcsk9-oral",
    "limit": 5
  }
}
```

### Checkpoint `ch1` Verification
Materialize or inspect the pre-computed `ch1` state (`checkpoints/ch1/`):
```bash
./scripts/checkpoint.sh goto ch1
cat checkpoints/ch1/findings/computational-biology/WO-001.md
cat checkpoints/ch1/program-state/decision-log.md
```
- **`IC-001` (Primary Series):** Oral allosteric small-molecule inhibitor binding the C-terminal / catalytic-domain groove of PCSK9 (`Q8NBP7`, `Elo = 1642.5`).
- **`IC-002` (Backup Comparator):** Oral tricyclic macrocycle occluding the flat PCSK9–LDLR EGF-A interface (`Elo = 1588.0`).
- *(Real-Run Note from `Pilot-10` `DEC-002` & `DEC-008`: When `seed_mode="hypex"` runs a native in-container tournament and `elo_decisive_gap` is unset, `science-program-lead` reports `no-clear-leader` rather than inventing an arbitrary ELO cutoff in prose.)*

---

**Next Step:** Proceed to [Module 02 — Stage 1 Target Validation: Human Genetics, AlphaGenome on GCP & Single-Cell Slicing (`ch2`)](02-target-validation-genetics-omics.md).

# Module 01 — Tour the Grove: 4-Tier Architecture, Multi-Model Harnesses & `oase doctor`

> **Duration:** 20 Minutes (`0:00 – 0:20`)  
> **Hands-On Goal:** Log into the shared **Scion Hub**, explore the pre-seeded discovery groves, inspect the **4-Tier / 22-Template Agent Architecture** and **Single-Writer State Contract**, see how portable model size aliases (`small | medium | large | extra-large`) bind to **multi-model harnesses on GCP (`Gemini 4`, `Claude`, `OpenAI`)**, and run `oase doctor` and `oase tools`.

---

## 1. Why "Team-Based Science" Beats Single-Player Chatbots

When you open the Scion Web UI (or connect your **Gemini Agent / Antigravity** session via `SESSION_PROJECT_LOCKED`), you are not entering a private chatbot thread. You are entering a **multi-human, multi-agent discovery grove**—analogous to Google Docs for a cross-functional R&D program team.

In your browser, inspect the pre-seeded workshop projects:

| Scion Project Grove | Purpose in Today's Workshop | Pre-Loaded State |
|---|---|---|
| **`live-sandbox`** | **Live Multi-Human + Multi-Agent Execution:** Where the Project Owner initiates a campaign (`create_project` + `bootstrap_campaign` / `scion start controller`), assigns `project-member` teammates, and triggers live GCP `AlphaGenome` & `AlphaFold 3` calls. | Clean `oase init` root ready for your directive. |
| **`stage0-1-walkthrough`** | **Time-Machine Campaign (`pilot-10` Hepatic Fibrosis):** Full Stage 0→1 campaign with 5 Git-tagged checkpoints (`ch0`–`ch4`), 381 SHA-256 sidecars, 67 verified JSONPath claims, `oase h5ad` single-cell slicing, real `scientifically_accepted` Validation 2 records, and a 28-page HTML evidence portal. | Checked out at `ch0-bootstrap` (jump to any stage in `<2s` via `checkpoint.sh`). |
| **`negative-gate-audit`** | **Falsification Case Study (`pilot-9b` Hidradenitis Suppurativa):** Complete 153-decision Stage 0 audit where **0 of 8 candidate concepts advanced (`DEC-145`)** due to human clinical/genetic counter-evidence and upstream citation-padding detection. | Checked out at `DEC-145` (Stage 0 Gate Closed). |

---

## 2. Inspecting the 4-Tier Agent Architecture (22 Scion Templates) & Single-Writer State Contract

Open a terminal inside the workspace and list the 22 agent templates synced to the Scion Hub:

```bash
ls -1 /workspace/templates/
```

```text
admet-dmpk-scientist
bootstrapper
computational-biologist
computational-chemist
experimental-biologist
finding-validator
head-of-discovery
hypex-evolution
hypex-generation
hypex-meta-review
hypex-proximity
hypex-reflection
hypex-supervisor
hypex-tournament
medicinal-chemist
preclinical-toxicologist
project-curator
regulatory-scientist
research-operations-controller
science-program-lead
scientific-reviewer
structural-biologist
```

### The 4 Agent Tiers & Strict Separation of Powers

| Agent Tier | Templates (22 Total) | Authority, Write Scope & Validation Role |
|---|---|---|
| **1. Authority & Governance Tier (2 Templates)** | `science-program-lead`, `head-of-discovery` (`<slug>-head-of-discovery`) | `science-program-lead` is the **sole writer** of Layer 2 `program-state/` (`active-series.md`, `decision-log.md`, `liability-tracker.md`, `open-questions.md`), owns work-order decomposition, executes **Validation 2** (independent Phase-2 reanalysis and scientific review of every `validation_passed` work order before logging `DEC-NNN` / `scientifically_accepted`), and prepares Stage Gate packages (`Stage 0 → Stages 1–4`). `<slug>-head-of-discovery` provides executive portfolio challenge and stage-gate governance alongside the human Project Owner. |
| **2. Operations, Validation & Curation Tier (4 Templates)** | `research-operations-controller`, `bootstrapper`, `finding-validator`, `project-curator` | `research-operations-controller` (`controller`) is the sole agent started by GA at campaign launch; it spawns `bootstrapper` (`oase init` + `oase doctor`), starts `science-program-lead` and `<slug>-head-of-discovery`, manages specialist container lifecycles and the **9-state work-order state machine** (`drafted → dispatched → in_progress → submitted → validating → validation_passed → under_scientific_review → scientifically_accepted → closed` in `.oase/control/events.ndjson`), dispatches `finding-validator` for **Validation 1** (the 10-check mechanical validator `oase validate check`), and wakes `project-curator` to compile the static HTML portal (`oase site build`)—without authority to alter a scientific question or accept an interpretation. |
| **3. Domain Specialists & Independent Review Tier (9 Templates)** | `computational-biologist`, `structural-biologist`, `computational-chemist`, `medicinal-chemist`, `experimental-biologist`, `admet-dmpk-scientist`, `preclinical-toxicologist`, `regulatory-scientist`, `scientific-reviewer` | 8 ephemeral domain specialists (each writing **only** to `findings/<domain>/` and `raw/`) plus 1 independent `scientific-reviewer` (`review-rubric` auditor). |
| **4. HypEx Stage 0 Tournament Tier (7 Templates)** | `hypex-supervisor`, `hypex-generation`, `hypex-reflection`, `hypex-tournament`, `hypex-evolution`, `hypex-proximity`, `hypex-meta-review` | Multi-epoch ELO hypothesis generation, clustering, blind pairwise debate, reflection, evolution, and meta-review. All OASE agents operate on a **push-only message bus** (`sciontool status blocked` until woken by an inbound `---BEGIN SCION MESSAGE---` envelope) and never poll in loops. |

### How OASE Separates Capability Layers (`docs/tool-design-guidance.md` §1)

| Layer | What It Owns | Where It Lives |
|---|---|---|
| **1. Environment** | Python venv (`RDKit`, `h5py`, `biopython`), binaries (`vina`, `fpocket`), `ENV_VERSION` hash | `/scion-volumes/tools/` |
| **2. CLI (`oase`)** | Deterministic execution, QPS rate limits, AF3 locks, Phase 1 `.meta.json` sidecars, Phase 2 offline `.analysis.json`, 10-check validation, static site build | `/workspace/tools/oase/` (62 command groups) |
| **3. Skill** | Specialist-neutral capability routing, invocation tables, mandatory relay codes, anti-fabrication guard (zero hardcoded thresholds) | `/workspace/skills/<capability>/SKILL.md` (41 skills) |
| **4. Template** | The role's capability grant (`skills:` list in `scion-agent.yaml`), portable model size alias, and **T-shaped liability handoffs** (`agents.md`) | `/workspace/templates/<role>/` (22 templates) |

Let's inspect the `structural-biologist` template to see how a T-shaped role is defined:

```bash
cat /workspace/templates/structural-biologist/scion-agent.yaml
```

---

## 3. Multi-Model Harnesses & Portable Size Aliases on GCP

None of the 22 OASE templates hardcodes a model ID or CLI binary. Scion decouples each agent's role definition (`scion-agent.yaml`) from its underlying LLM harness (`defaultHarnessConfig: gemini-cli, claude, antigravity, codex`) and resolves portable model size aliases (`defaultModel: small, medium, large, extra-large`) at spawn time:

```bash
# Inspect active agents and their bound model harnesses
scion list
```

In our workshop configuration on GCP:
- **Orchestration & Long-Context Synthesis (`Gemini 4 Pro / Flash` on GCP — `gemini-cli` / `large` & `extra-large`):** Bound to `research-operations-controller`, `science-program-lead`, and domain specialists that synthesize across dozens of work orders and hundreds of JSON sidecars.
- **Adversarial Peer Review (`Anthropic Claude` on GCP — `claude` / `large`):** Bound to `scientific-reviewer`, `finding-validator`, and `head-of-discovery`. When `scientific-reviewer` re-runs `oase <tool> analyze` offline and audits a specialist's prose, a completely independent model family performs the critique.
- **Multi-Model Hypothesis Tournaments (`Gemini 4` + `Claude` + `OpenAI` in `Hypex`):** Across the 7 `hypex-*` templates, competing hypotheses are generated and debated across heterogeneous model harnesses in blind ELO matches so no single model ever grades its own homework.

---

## 4. Hands-On Exercise: Run `oase doctor`, `oase tools`, and `oase relays`

Activate the shared tools environment and run the three core introspection commands:

```bash
source /scion-volumes/tools/env.sh

# 1. Check environment health, binaries, ADC credentials, and ENV_VERSION consistency
oase --project /workspace/live-sandbox doctor

# 2. Browse the 62 deterministic CLI tool groups organized by scientific capability
oase tools list

# 3. Inspect the 19 registered mandatory relay codes that specialists cannot suppress
oase relays
```

### What Just Happened?
- **`oase doctor`** verified that `fpocket` and `vina` are executable, `RDKit` and `h5py` import cleanly, all 51 of 51 Phase-2 commands are latched offline, Google Cloud ADC resolves via the GCE metadata server for **AlphaFold 3** and **AlphaGenome** on GCP, and all artifact sidecars in the project share a single `env_version` stamp.
- **`oase relays`** printed the 19 registered warning codes (such as `afdb.partial_coverage`, `afdb.confidence_is_not_accuracy`, `afdb.model_is_not_docking_ready`, `gnomad.constraint_is_not_safety`, `fpocket.druggability_is_not_affinity`). Whenever a tool emits one of these codes into `.analysis.json`, `oase validate check` mechanically refuses any specialist finding that fails to propagate that relay code into its Layer 1 conclusion!

---

**Next Step:** Proceed to [Module 02 — Launch a Live Team Campaign](02-launch-campaign.md).

# Module 01 — Tour the Grove: Team-Based Science, Multi-Model Harnesses & `oase doctor`

> **Duration:** 20 Minutes (`0:00 – 0:20`)  
> **Hands-On Goal:** Log into the shared **Scion Hub**, explore the three pre-seeded discovery groves, inspect how **22 T-shaped agent templates (13 roles)** bind to **multi-model harnesses (`Gemini 4`, `Claude`, `OpenAI`)**, and run `oase doctor` and `oase tools`.

---

## 1. Why "Team-Based Science" Beats Single-Player Chatbots

When you open the Scion Web UI and log in with your corporate Google OAuth identity, you are not entering a private chatbot thread. You are entering a **multi-human, multi-agent discovery grove**—analogous to Google Docs for a cross-functional R&D program team.

In your browser, inspect the three pre-seeded workshop projects:

| Scion Project Grove | Purpose in Today's Workshop | Pre-Loaded State |
|---|---|---|
| **`live-sandbox`** | **Live Multi-Human + Multi-Agent Execution:** Where your 5-person pod will issue a live Program Directive, co-steer agents, and run live Vertex AI `AlphaGenome` & `AlphaFold 3` calls. | Clean `oase init` root ready for your directive. |
| **`stage0-1-walkthrough`** | **Time-Machine Campaign (`pilot-10` Hepatic Fibrosis):** Full Stage 0→1 campaign with 5 Git-tagged checkpoints (`ch0`–`ch4`), 381 SHA-256 sidecars, 67 verified JSONPath claims, `oase h5ad` single-cell slicing, and a 28-page HTML evidence portal. | Checked out at `ch0-bootstrap` (jump to any stage in `<2s` via `checkpoint.sh`). |
| **`negative-gate-audit`** | **Falsification Case Study (`pilot-9b` Hidradenitis Suppurativa):** Complete 153-decision Stage 0 audit where **0 of 8 candidate concepts advanced (`DEC-145`)** due to human clinical/genetic counter-evidence and upstream citation-padding detection. | Checked out at `DEC-145` (Stage 0 Gate Closed). |

---

## 2. Inspecting the 22 T-Shaped Agent Templates (13 Roles)

Open a terminal inside the workspace and list the agent templates synced to the Scion Hub:

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

### How OASE Separates the Four Tiers (`docs/tool-design-guidance.md` §1)

| Tier | What It Owns | Where It Lives |
|---|---|---|
| **1. Environment** | Python venv (`RDKit`, `h5py`, `biopython`), binaries (`vina`, `fpocket`), `ENV_VERSION` hash | `/scion-volumes/tools/` |
| **2. CLI (`oase`)** | Deterministic execution, QPS rate limits, AF3 locks, Phase 1 `.meta.json` sidecars, Phase 2 offline `.analysis.json`, 10-check validation, static site build | `/workspace/tools/oase/` (62 command groups) |
| **3. Skill** | Specialist-neutral capability routing, invocation tables, mandatory relay codes, anti-fabrication guard (zero hardcoded thresholds) | `/workspace/skills/<capability>/SKILL.md` (41 skills) |
| **4. Template** | The role's capability grant (`skills:` list in `scion-agent.yaml`), role-specific questions, and **T-shaped liability handoffs** (`agents.md`) | `/workspace/templates/<role>/` (22 templates) |

Let's inspect the `structural-biologist` template to see how a T-shaped role is defined:

```bash
cat /workspace/templates/structural-biologist/scion-agent.yaml
```

Notice two critical architectural properties:
1. **Explicit Capability Grant (`skills:`):** The `structural-biologist` only receives the skills relevant to structural confidence, pocket druggability, homology search, and complex prediction. It cannot invent toxicology thresholds or modify control-plane state.
2. **T-Shaped Liability Handoffs (`agents.md`):** While its deep vertical bar is 3D structure (`AlphaFold 3`, `AFDB`, `RCSB PDB`, `fpocket`), its horizontal bar requires it to emit structured warnings (relays like `afdb.partial_coverage` or `afdb.model_is_not_docking_ready`) that bind downstream `computational-chemist` and `medicinal-chemist` agents.

---

## 3. Multi-Model Harnesses: Turning Model Diversity into a Scientific Control

A major risk in agentic science is **correlated model bias**: if the same LLM family generates a hypothesis, interprets the literature, and conducts the peer review, it will systematically agree with its own blind spots.

Scion solves this by decoupling the **Agent Template** from the **Model Harness**:

```bash
# Inspect active agents and their bound model harnesses
scion list
```

In our workshop configuration:
- **Orchestration & Long-Context Synthesis (`Gemini 4 Pro / Flash` on Vertex AI):** Bound to `research-operations-controller`, `science-program-lead`, and domain specialists that synthesize across dozens of work orders and hundreds of JSON sidecars.
- **Adversarial Peer Review (`Anthropic Claude` on Vertex AI Partner Models):** Bound to `scientific-reviewer` and `finding-validator`. When `scientific-reviewer` re-runs `oase <tool> analyze` offline and audits a specialist's prose, a completely independent model family performs the critique.
- **Multi-Model Hypothesis Tournaments (`Gemini 4` + `Claude` + `OpenAI` in `Hypex`):** Across the 7 `hypex-*` templates (`hypex-supervisor`, `hypex-generation`, `hypex-tournament`, `hypex-reflection`, `hypex-evolution`, `hypex-proximity`, `hypex-meta-review`), competing hypotheses are generated and debated across heterogeneous model harnesses in blind ELO matches.

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
- **`oase doctor`** verified that `fpocket` and `vina` are executable, `RDKit` and `h5py` import cleanly, Google Cloud ADC resolves via the GCE metadata server for **Vertex AI AlphaFold 3** and **AlphaGenome**, and all artifact sidecars in the project share a single `env_version` stamp.
- **`oase relays`** printed the 19 registered warning codes (such as `afdb.partial_coverage`, `afdb.confidence_is_not_accuracy`, `afdb.model_is_not_docking_ready`, `gnomad.constraint_is_not_safety`, `fpocket.druggability_is_not_affinity`). Whenever a tool emits one of these codes into `.analysis.json`, `oase validate check` mechanically refuses any specialist finding that fails to propagate that relay code into its Layer 1 conclusion!

---

**Next Step:** Proceed to [Module 02 — Launch a Live Team Campaign](02-launch-campaign.md).

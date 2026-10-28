# Module 02 — Launch a Live Team Campaign: Project Owner GA Initiation, Subway-Map Routing & `Hypex` Tournaments

> **Duration:** 30 Minutes (`0:20 – 0:50`)  
> **Hands-On Goal:** Initiate a shared discovery project as the **Project Owner** via the **Gemini Agent (`GA`) ↔ OASE Surface Contract** (`create_project` + `bootstrap_campaign` A2UI Initiation Card) or one CLI command in **`live-sandbox`**, assign `project-member` teammates, co-steer via WebDAV reads + bounded push messages, and use the `<2s` Time-Machine (`ch1-stage0-hypex`) to inspect a completed 103-match `Hypex` ELO tournament.

---

## 1. The Agreed Gemini Agent (`GA`) ↔ OASE Project Initiation Contract

In production and during the workshop, scientists do not hand-craft container state or manually edit control files on the VM. Gemini Agent (`GA` / Antigravity) and OASE (on Scion Hub) operate under a fail-closed **Surface Initiation & Management Contract** (`scion` MCP / `pharma-cli dde`):

### Phase A: Project Owner 4-Step Atomic Project Provisioning (`create_project`)
The **Project Owner** initiates project creation and assigns participating R&D team members (`members` → `role: "project-member"`):

```json
{
  "ServerName": "scion",
  "ToolName": "create_project",
  "Arguments": {
    "name": "Translational R&D — Oral PCSK9 ASCVD",
    "slug": "oral-pcsk9-ascvd",
    "service_account_email": "scion-default-agent@<YOUR_GCP_PROJECT_ID>.iam.gserviceaccount.com",
    "harness_config": "gemini-cli",
    "default_model": "large",
    "members": [
      "scientist1@example-biopharma.com",
      "scientist2@example-biopharma.com",
      "lead@example-biopharma.com"
    ]
  }
}
```

`create_project` automatically executes four fail-closed steps:
1. **Create Scion Project:** Calls `POST /api/v1/projects` (`{name, slug, labels}`).
2. **Register & Verify GCP Service Account, Harness Aliases & Team Members:** Registers the project's GCP Service Account (`verified == true`), sets `defaultGCPIdentityMode: "assign"`, `defaultHarnessConfig`, and `defaultModel` (`small | medium | large | extra-large`), and assigns each email in `members` (`role: "project-member"`).
3. **Provision Shared `tools` Volume:** Calls `POST /api/v1/projects/{id}/shared-dirs` (`{"name": "tools", "readOnly": false, "inWorkspace": false}`) so `/scion-volumes/tools/env.sh` is mounted into every agent container.
4. **Import & Verify Project-Scoped OASE Templates (`OASE_TEMPLATES_MISSING` Guard):** Calls `POST /api/v1/projects/{id}/import-templates` and verifies by name that all 6 critical governance/orchestration templates (`research-operations-controller`, `science-program-lead`, `bootstrapper`, `head-of-discovery`, `finding-validator`, `hypex-supervisor`) exist—preventing any agent from silently falling back to `template: default`.

### Phase B: Controller-Only Campaign Launch & A2UI Initiation Card (`bootstrap_campaign`)
When the Project Owner launches a campaign from GA, if any required charter parameter is unset (`program_slug`, `program_directive`, `sponsor_gate_policy` [`manual | pre-authorized | budget-gated`], `seed_mode` [`hypex | sciarchitect | bring_your_own`], `stage_entry_point` [`stage0_hypex | stage0_verification | stage1_direct`]), GA renders an interactive **A2UI Project & Campaign Initiation Card (`A2UI_INPUT_REQUIRED`)**. Once confirmed:
- Stages any seed bundle to `/workspace/.seed/<slug>/` over Hub WebDAV (`MKCOL` + `PUT` + read-back `GET` SHA-256 verification, writing `CHECKSUMS.json` last).
- Starts **only `controller`** (`--type research-operations-controller`, without `--role baseline`) and verifies post-start that `controller` bound to `template == "research-operations-controller"` (`CONTROLLER_TEMPLATE_MISMATCH` guard).
- `controller` then spawns `bootstrapper` (`oase init` + `oase doctor`), starts `science-program-lead` (which writes `DEC-001` and `WO-001`), and starts `<slug>-head-of-discovery`.

### Live Exercise 2.1: Start Your Pod's Controller in `live-sandbox`
You can launch via the A2UI card in GA (`bootstrap_campaign`) or run the equivalent one-line command in `live-sandbox`:

```bash
scion start controller --type research-operations-controller \
  "Program directive: Conduct Stage 0 portfolio triage and Stage 1 target validation for extracellular matrix remodeling and stellate-cell activation targets in Hepatic Fibrosis (cirrhosis / MASH F3-F4). Modality: small molecule or catalytic inhibitor. Stopping gate: pause after Stage 1 Target Validation Gate to export a wet-lab CRISPR/primary-stellate assay handoff package. Program directory: /workspace/live-sandbox"
```

Watch the bootstrap sequence unfold in real time (`~60 seconds`):

```bash
# 1. Watch controller, science-program-lead, and head-of-discovery come online
scion list

# 2. Stream the controller's live bootstrap log
scion output controller

# 3. Inspect the initialized .oase/ control plane and project lock
ls -la /workspace/live-sandbox/.oase/
cat /workspace/live-sandbox/.oase/program.yaml
```

---

## 2. Team-Based Science in Action: Direct WebDAV Reads & Bounded Push Writes

Assigned team members bind their own GA/AGY sessions to the shared project (`SESSION_PROJECT_LOCKED`, enforcing `ONE_PROGRAM_PER_PROJECT` via `.oase-project-lock.json`) or join the shared Scion project threads (`operations`, `science-lead`):

| Team Action | MCP Tool / CLI Command | Contract & Performance |
|---|---|---|
| **Inspect Latest Decisions (`DEC-###`)** | `call_mcp_tool("scion", "decision_log", {"project_id": "<id>", "program_slug": "<slug>", "limit": 10})` or `pharma-cli dde decision-log` | Reads `program-state/decision-log.md` over Hub WebDAV with ETag caching (~1.5s). |
| **Read Workspace Files (`L0–L4`)** | `call_mcp_tool("scion", "dav_read", {"project_id": "<id>", "path": "<slug>/program-state/active-series.md"})` | Uses local ETag / SHA-256 cache (`304 Not Modified`). Files `> 20 KB` return a `LARGE_FILE_SUMMARY`. |
| **Read Accepted Findings** | `call_mcp_tool("scion", "dde_finding", {"project_id": "<id>", "program_slug": "<slug>", "work_order_id": "WO-004"})` | Verifies the run passed Validation 1 + Validation 2 (`scientifically_accepted`) before returning the finding. |
| **Escalate Decision-Grade Question ("Gray Zone" Rule)** | `call_mcp_tool("scion", "request_work_order", {"project_id": "<id>", "program_slug": "<slug>", "question": "...", "target_role": "structural-biologist"})` | Fast 2–30s exploratory checks run in GA; any finding cited in a `DEC-*` or stage gate escalates via a `< 10 KB` `WORK_ORDER_REQUEST` push message to `science-program-lead`. |
| **Issue Constraint or Gate Verdict** | `call_mcp_tool("scion", "send_message", {"project_id": "<id>", "agent": "science-program-lead", "message": "..."})` | Pushes a `---BEGIN SCION MESSAGE---` envelope (`< 10 KB`). When OASE agents reply (`agent:* -> user:*`), the `[OASE_INBOUND_MESSAGE]` watchdog wakes the user's session and relays the message verbatim. |

Try messaging `science-program-lead` directly from your pod thread:
```text
@science-program-lead For any metalloproteinase candidate (e.g., MMP family) that emerges from Stage 0, require an explicit selectivity check against broad-spectrum musculoskeletal MMP liabilities (MMP1/MMP14) in Stage 1 before advancing.
```

---

## 3. How `Hypex` Multi-Model Tournaments Prevent Single-Model Bias

When `science-program-lead` issues `WO-001` for Stage 0 hypothesis generation and ranking, it spawns the **7-template `Hypex` tournament tier**:

| Template Role | What It Does in the Tournament | Multi-Model Harness Assignment on GCP |
|---|---|---|
| `hypex-supervisor` | Orchestrates tournament epochs, enforces match budgets (`budget_exhausted`), and runs `oase hypex ingest` & `oase hypex analyze`. | **Gemini 4 Pro on GCP** (`gemini-cli` / `large`) |
| `hypex-generation` | Generates mechanistic therapeutic hypotheses grounded in `oase pubmed-bq` (BigQuery), `OpenTargets`, and `GWAS` evidence. | **Gemini 4 Pro** + **Claude** + **OpenAI** (parallel generation pods) |
| `hypex-proximity` | Clusters generated hypotheses to deduplicate redundant mechanisms before pairing. | **Gemini 4 Flash on GCP** (`gemini-cli` / `medium`) |
| `hypex-tournament` | Runs blind head-to-head pairwise debates scored via ELO ratings across mechanism plausibility, human genetic support, and tractability. | Cross-family judges (**Claude** judging **Gemini** outputs and vice versa) |
| `hypex-reflection` | Conducts deep second-pass examination of top-ranked hypotheses for fatal flaws, missing comparators, or literature bias. | **Anthropic Claude on GCP** (`claude` / `large`) |
| `hypex-evolution` | Refines surviving hypotheses to address tractable critiques discovered during reflection. | **Gemini 4 Pro on GCP** (`gemini-cli` / `large`) |
| `hypex-meta-review` | Synthesizes the tournament ledger into an auditable Stage 0 ranking memo for `finding-validator`. | **Gemini 4 Pro on GCP** (`gemini-cli` / `large`) |

---

## 4. Cooking-Show Time-Machine: Jump to `ch1-stage0-hypex` (`<2 Seconds`)

A full 14-concept, 103-match `Hypex` tournament across multiple epochs takes `~25–45 minutes` of wall-clock compute (or `~8 minutes` when initiated with `seed_mode=sciarchitect` at `stage0_verification`). While your `live-sandbox` agents continue executing their initial queries in the background, switch to the **`stage0-1-walkthrough` (`pilot-10`)** grove and jump straight to **Checkpoint 1 (`ch1-stage0-hypex`)**:

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
- In **`DEC-008`**, `controller` rejected `WO-001` rev 1 and rev 2 at intake because the context snapshot was empty, refusing to dispatch until `WO-001` rev 3 supplied a bounded, checksummed context snapshot.
- In **`DEC-002`**, when `oase doctor` flagged `thresholds hypex@1.0 (elo_decisive_gap unset)`, the `Science Program Lead` refused to invent an arbitrary ELO cutoff in prose and ruled that the tournament must report `no-clear-leader` until calibrated—requiring every surviving Stage 0 concept to pass primary human genetic, single-cell transcriptomic, and 3D structural falsification in Stage 1.

---

**Next Step:** Proceed to [Module 03 — Evidence, Viewers & Refusals](03-evidence-and-refusals.md).

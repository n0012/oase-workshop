# Module 08 — Surface-to-OASE Connectivity & Formal Initiation Contract (`GA` & `AGY` ↔ `OASE`)

> **Purpose:** Authoritative architectural and operational reference for connecting **Gemini Agent (`GA`)**, **Antigravity (`AGY`)**, and **Jetski** to the **Open Agentic Science Engine (`OASE v0.3.0`)** on **Scion Hub**, initiating projects and campaigns as the **Project Owner**, assigning R&D team members, staging zero-truncation seed packages, and collaborating live across surfaces.

---

## 1. Architecture Overview: Surface-to-OASE Connectivity Stack

**Gemini Agent (`GA`)** and **Antigravity / Jetski (`AGY`)** serve as the human-facing interactive scientific surfaces (for sub-minute exploratory queries, charter configuration, hypothesis tournament seeding, and stage-gate governance), while **OASE on Scion Hub** executes long-running, multi-agent, provenance-locked campaign work orders (`WO-001`..`WO-N`).

| Surface / Component | Config & Skill Root | MCP Registration Path | How It Connects to OASE on Scion Hub |
|---|---|---|---|
| **Gemini Agent (`gemini_agent` / Coworkagent)** | `~/cowork_workspace/skills/` (physical copies with normalized lowercase kebab-case `SKILL.md` frontmatter) | `~/cowork_workspace/.cowork/mcp_servers.json` (`"servers"` list) → `~/cowork_workspace/.cowork/bin/scion_mcp_server` (`0755`) | Runs `scion_mcp_server` on the host outside `nsjail` via `WorkspaceMcpRegistry` so `scion` reaches Scion Hub. Includes `gemini-agent-guard` (`~/.config/gemini-agent-guard/`) with automatic inbound OASE message polling (`[OASE_INBOUND_MESSAGE]`). |
| **Antigravity (`antigravity` IDE)** | `~/.gemini/antigravity/skills/` & `~/.gemini/antigravity/agents/` (or `$PHARMA_ANTIGRAVITY_HOME`) | `~/.gemini/antigravity/mcp_config.json` (`"mcpServers"` map) → `python3 <repo>/tools/scion_mcp_server.py` | Connects directly via the `scion` stdio MCP server and `pharma-cli dde` CLI using proxy or direct HTTPS (`SCION_DIRECT_HTTPS=1`). |
| **Jetski (`jetski` IDE)** | `~/.gemini/config/skills/`, `~/.gemini/config/agents/`, & `~/.gemini/config/plugins/` | `~/.gemini/config/mcp_config.json` + lazy tool schemas in `~/.gemini/jetski/mcp/scion/*.json` | Connects via the `scion` MCP server (with 15 lazily-loaded tool schemas synced via `refresh_jetski_mcp_schemas`) and `pharma-cli dde`. |

### The 15 `scion` MCP Tools Shared Identically Across `GA` and `AGY`
1. **Hub & Roster Inspection (4 tools):** `hub_status`, `list_projects`, `list_agents`, `agent_logs`
2. **Direct WebDAV Read & ETag Caching (4 tools):** `decision_log` (parses latest `DEC-###` entries in ~1.5s), `dav_read` (with ETag / `If-None-Match` SHA-256 cache under `~/.cache/pharma_skills/oase_dav` and `LARGE_FILE_SUMMARY` for files `> 20 KB`), `dav_list`, `dde_finding` (reads `scientifically_accepted` work orders)
3. **A2A Push Messaging & Inbound Watchdog (3 tools):** `send_message` (`< 10 KB` bounded envelope), `list_conversations`, `get_messages`
4. **Audited Work-Order Escalation (1 tool):** `request_work_order` (formats a structured `WORK_ORDER_REQUEST` to `science-program-lead`)
5. **Project Owner Provisioning & Campaign Initiation (3 tools):** `create_project` (4-step atomic setup + team member assignment), `bootstrap_campaign` (`A2UI_INPUT_REQUIRED` initiation gate + WebDAV seed staging + controller-only launch), `start_agent`

---

## 2. Step 1: Configure Scion Hub Endpoints & Authentication (Zero Hardcoding)

Neither `GA` nor `AGY` ever hardcodes a Scion Hub URL, GCP project ID, or Service Account in source code. Both surfaces resolve endpoints through `scicore.platform_config` in strict priority order:
1. Environment variables, or
2. `~/.config/pharma_skills/config.toml` (override path via `$PHARMA_SKILLS_CONFIG`).

### 2.1 Create `~/.config/pharma_skills/config.toml`
```toml
[oase]
# Scion Hub HTTPS endpoint (no trailing slash, no query/credentials)
hub_url = "https://<your-scion-hub-host>"

# Default GCP project and agent Service Account used when provisioning projects
default_gcp_project = "<YOUR_GCP_PROJECT_ID>"
default_service_account_email = "scion-default-agent@<YOUR_GCP_PROJECT_ID>.iam.gserviceaccount.com"

# Optional: byte threshold for inline WebDAV reads before returning LARGE_FILE_SUMMARY (default: 20480)
dav_inline_max_bytes = 20480

[cost_gates]
# Cost gates are off by default (LOGGED_NOT_GATED); set true only if enforcing per-run budget ceilings
enabled = false
```

### 2.2 Environment Variable Overrides (Optional)
```bash
export SCION_HUB_URL="https://<your-scion-hub-host>"
export SCION_GCP_PROJECT_ID="<YOUR_GCP_PROJECT_ID>"
export SCION_SERVICE_ACCOUNT_EMAIL="scion-default-agent@<YOUR_GCP_PROJECT_ID>.iam.gserviceaccount.com"

# Optional session defaults when working inside a single project/program:
export OASE_PROJECT="<project-uuid-or-slug>"
export OASE_PROGRAM_SLUG="<program-slug>"

# Set SCION_DIRECT_HTTPS=1 on VPCs that connect directly over HTTPS without a corporate proxy:
export SCION_DIRECT_HTTPS=1
```

### 2.3 Authenticate `scion` CLI & Verify User Identity
Project creation and project-admin operations (`create_project`, registering GCP Service Accounts, updating project settings, assigning team members) require the **Project Owner's `UserIdentity` token** (`~/.scion/credentials.json` or `SCION_BEARER_TOKEN`), because in-container `AgentIdentity` tokens are rejected with `403 Forbidden` on project-admin endpoints:

```bash
# Authenticate to the Scion Hub (writes ~/.scion/credentials.json)
scion --hub "$SCION_HUB_URL" auth login

# Verify Hub connectivity and token validity
scion --hub "$SCION_HUB_URL" hub status
```

---

## 3. Step 2: Install & Sync Skills, Agents, and the `scion` MCP Server Into `GA` & `AGY`

Run the unified surface installer to register the `scion` MCP server, skills (`dde`, `sciarchitect`, domain skills), and guard hooks across all interactive surfaces:

```bash
python3 scripts/surface_install.py \
  --surface gemini_agent \
  --surface antigravity \
  --surface jetski
```

### 3.1 What This Configures in Gemini Agent (`GA`)
- Copies all skills into `~/cowork_workspace/skills/` with normalized single-word kebab-case `SKILL.md` frontmatter.
- Installs an executable launcher at `~/cowork_workspace/.cowork/bin/scion_mcp_server` (`chmod 0755`) and registers it in `~/cowork_workspace/.cowork/mcp_servers.json` under `"servers"`.
- Installs the **`gemini-agent-guard` plugin + inbound OASE watchdog**:
  - On every tool invocation (throttled to 1 Hub poll per 5s via `fcntl.flock` on `~/.config/pharma_skills/oase_sessions/inbound_cursor_<project_id>.json`), the guard polls inbound `agent:* -> user:*` messages for the bound project.
  - When an OASE agent (`science-program-lead`, `controller`, `<slug>-head-of-discovery`) sends a message or stage-gate alert, the watchdog injects `[OASE_INBOUND_MESSAGE ...]` into the `GA` turn and enforces immediate, verbatim relay to the scientist.
  - **Running Inside an Active `GA` Session:** Inside `GA`, `~/.gemini` and `.cowork` are mounted read-only by default. If `surface_install.py` exits with code `3` (`ESCALATION_REQUIRED`), re-run the command with `permissions="require_escalated"`.

### 3.2 What This Configures in Antigravity (`AGY`) & Jetski
- **Antigravity (`~/.gemini/antigravity/`):** Symlinks skills into `skills/`, specialist subagents into `agents/`, and upserts `"mcpServers": {"scion": ...}` into `~/.gemini/antigravity/mcp_config.json`.
- **Jetski (`~/.gemini/config/` & `~/.gemini/jetski/`):** Symlinks skills into `~/.gemini/config/skills/` and specialist subagents into `~/.gemini/config/agents/`, upserts `"mcpServers": {"scion": ...}` into `~/.gemini/config/mcp_config.json`, and executes `refresh_jetski_mcp_schemas()`, writing all 15 lazy tool schemas (`hub_status.json`, `create_project.json`, `bootstrap_campaign.json`, `decision_log.json`, `dav_read.json`, `request_work_order.json`, `send_message.json`, etc.) to `~/.gemini/jetski/mcp/scion/`.

---

## 4. Step 3: How a Project & Campaign Are Initiated Through `GA` or `AGY` — The Formal Initiation Contract

Neither `GA` nor `AGY` ever hand-crafts `/workspace/<program-slug>/` files, manually spawns specialist containers at launch, or guesses missing charter settings. Project and campaign initiation across both `GA` and `AGY` is governed by a strict, fail-closed **3-Level Initiation Contract**:

### 4.1 The Three Initiation Levels & Workspace Lock Invariants

| Initiation Level | Who Initiates | MCP Tool / CLI Command | Cardinality & Lock Invariants Enforced |
|---|---|---|---|
| **Level 1: Scion Project Provisioning** | **Project Owner** (`UserIdentity` token required) | `scion:create_project` (or `bootstrap_campaign` with `create_project=true`) / `pharma-cli dde create-project` | Executes 4-step atomic project creation, GCP SA verification (`verified == true`), harness/model alias setup, team member assignment (`role: "project-member"`), `tools` shared volume setup, and 22-template import (`OASE_TEMPLATES_MISSING` guard). |
| **Level 2: OASE Campaign Bootstrap** | **Project Owner** | `scion:bootstrap_campaign` / `pharma-cli dde bootstrap-campaign` | Enforces **1-Project-Per-Session** (`SESSION_PROJECT_LOCKED` at `~/.config/pharma_skills/oase_sessions/session_<sid>.json`), **1-Program-Per-Project** (`ONE_PROGRAM_PER_PROJECT` at `/workspace/.oase-project-lock.json` + `.oase/control/lock.json`), **Pre-Init Single-Writer** (`GA`/`AGY` never creates `/workspace/<slug>/` prior to `oase init`), and **Controller-Only Launch** (`CONTROLLER_TEMPLATE_MISMATCH` guard). |
| **Level 3: Audited Work Order / Gate Action** | **Project Owner** or **Assigned Team Member** | `scion:request_work_order` / `scion:send_message` | Sends a bounded (`< 10 KB`) `WORK_ORDER_REQUEST` or `STAGE_GATE_DECISION` push message to `science-program-lead`. |

> [!IMPORTANT]
> **Critical Pre-Initialization Invariant:** `GA` and `AGY` **never** create `/workspace/<program-slug>/` or write `decision-log.md` / `events.ndjson` over WebDAV prior to starting `controller`. Inside the container, `bootstrapper` runs `oase init /workspace/<program-slug>`, which requires `/workspace/<program-slug>/` to be non-existent or empty at initialization time; any pre-initiation seed package is staged strictly under `/workspace/.seed/<program-slug>/`.

---

### 4.2 Level 1 Contract: Project Owner Project Creation & Team Assignment (`create_project`)

The **Project Owner** initiates project creation from `GA` or `AGY` and assigns participating team members (`members`).

#### MCP Tool Call (`create_project`)
```json
{
  "ServerName": "scion",
  "ToolName": "create_project",
  "Arguments": {
    "name": "Translational R&D — Oral PCSK9 ASCVD",
    "slug": "oral-pcsk9-ascvd",
    "service_account_email": "scion-default-agent@<YOUR_GCP_PROJECT_ID>.iam.gserviceaccount.com",
    "gcp_project_id": "<YOUR_GCP_PROJECT_ID>",
    "harness_config": "gemini-cli",
    "default_model": "large",
    "members": [
      "compbio-lead@example-biopharma.com",
      "medchem-lead@example-biopharma.com",
      "dmpk-lead@example-biopharma.com"
    ],
    "labels": {
      "workshop": "oase-translational-rd",
      "therapeutic_area": "cardiovascular"
    }
  }
}
```

#### CLI Equivalent
```bash
pharma-cli dde create-project \
  --name "Translational R&D — Oral PCSK9 ASCVD" \
  --slug "oral-pcsk9-ascvd" \
  --service-account "scion-default-agent@<YOUR_GCP_PROJECT_ID>.iam.gserviceaccount.com" \
  --gcp-project-id "<YOUR_GCP_PROJECT_ID>" \
  --harness-config "gemini-cli" \
  --default-model "large" \
  --member "compbio-lead@example-biopharma.com" \
  --member "medchem-lead@example-biopharma.com" \
  --member "dmpk-lead@example-biopharma.com"
```

#### The 4-Step Atomic REST API Contract Executed by `create_project`
1. **Step 1 — Create Project (`POST /api/v1/projects`):**
   - Payload: `{"name": "<name>", "slug": "<slug>", "labels": {"<k>": "<v>"}}`.
   - Contract rules: `labels` must be a JSON object (`map[string]string`), never a list; `workspaceMode` is omitted unless `gitRemote` is explicitly set (sending `workspaceMode: "local"` without `gitRemote` triggers HTTP 400).
2. **Step 2 — Register & Verify GCP Service Account, Update Settings & Assign Team Members:**
   - Registers SA via `POST /api/v1/projects/{id}/gcp-service-accounts` (`{"email": "<sa_email>", "projectId": "<gcp_project_id>", "name": "default-agent"}`); if `409 Conflict` (already registered), resolves via `GET /api/v1/projects/{id}/gcp-service-accounts` and triggers `POST /api/v1/projects/{id}/gcp-service-accounts/{saId}/verify`. Fails closed (`GCP_SA_NOT_VERIFIED`) if `verified != true`.
   - Reads existing settings via `GET /api/v1/projects/{id}/settings` (never `PUT`s an empty dict if `GET` fails, to avoid wiping bucket/env) and merges via `PUT /api/v1/projects/{id}/settings`:
     - `defaultGCPIdentityMode`: `"assign"`
     - `defaultGCPIdentityServiceAccountID`: `"<sa.id>"`
     - `defaultHarnessConfig`: `"gemini-cli"` | `"claude"` | `"antigravity"` | `"codex"`
     - `defaultModel`: `"small"` | `"medium"` | `"large"` | `"extra-large"` (portable size aliases resolved by the harness; raw model strings are rejected).
   - Assigns each team member in `members` via `POST /api/v1/projects/{id}/members` with `{"email": "<member_email>", "role": "project-member"}`.
3. **Step 3 — Provision Shared `tools` Volume (`POST /api/v1/projects/{id}/shared-dirs`):**
   - Payload: `{"name": "tools", "readOnly": false, "inWorkspace": false}` so `/scion-volumes/tools/env.sh` is mounted into every agent container.
4. **Step 4 — Import & Verify OASE Templates (`POST /api/v1/projects/{id}/import-templates`):**
   - Payload: `{"path": "applications/open-agentic-science-engine/templates"}`.
   - Lists registered project templates and verifies by exact name (never by count alone) that all **6 critical templates** (`research-operations-controller`, `science-program-lead`, `bootstrapper`, `head-of-discovery`, `finding-validator`, `hypex-supervisor`) exist. If any is missing, fails closed with `OASE_TEMPLATES_MISSING`.

---

### 4.3 Level 2 Contract: Campaign Initiation & The A2UI Initiation Gate (`bootstrap_campaign`)

#### Required Campaign Initiation Parameters

| Parameter | Required / Conditional | Allowed Values & Contract |
|---|---|---|
| `project_id` (or `create_project=true` + `project_name` / `project_slug`) | **Required** | Existing Scion Project UUID/slug. `bootstrap_campaign` never implicitly creates a new project unless `create_project=true` is explicitly passed by the Project Owner. |
| `program_slug` | **Required** | Lowercase kebab-case slug (`^[a-z0-9]+(-[a-z0-9]+)*$`, e.g. `"pcsk9-oral"`). Maps to `/workspace/<program_slug>/`. |
| `program_directive` | **Required** | Clear scientific charter objective passed to `controller` and `science-program-lead` (target/indication, modality scope, TPP goals, and key falsification questions). |
| `sponsor_gate_policy` | **Required** | `"manual"` (human Project Owner approves every Stage Gate Stage 0 → 4), `"pre-authorized"` (autonomous progression across pre-approved gates), or `"budget-gated"` (auto-progresses within budget ceiling). |
| `seed_mode` | **Required** | `"hypex"` (Mode 1: native in-container OASE evolutionary tournament), `"sciarchitect"` (Mode 2: `oase.campaign-seed.v2` package from `GA`/`AGY`), or `"bring_your_own"` (Mode 3: customer/scientist hypotheses). |
| `stage_entry_point` | **Required** | `"stage0_hypex"` (required for `seed_mode="hypex"`), `"stage0_verification"` (recommended default for `sciarchitect` and `bring_your_own`), or `"stage1_direct"` (requires explicit sponsor pre-authorization). |
| `service_account_email` | **Required when `create_project=true`** | Verified GCP Service Account email (defaults to `[oase] default_service_account_email` in `config.toml` if configured). |
| `seed_bundle_dir` or `seed_payload` | **Required when `seed_mode` is `"sciarchitect"` or `"bring_your_own"`** | Local directory containing the 7-part seed bundle (`seed_bundle_dir`) or validated `oase.campaign-seed.v2` / `dde.campaign-seed.v1` JSON object (`seed_payload`). |
| `members` | Optional (Project Owner) | List of team member emails assigned `role: "project-member"` on the project. |

#### Interactive A2UI Initiation Gate (`A2UI_INPUT_REQUIRED`)
If the Project Owner asks `GA` or `AGY` to initiate a campaign and any required parameter above is unset, `bootstrap_campaign` **never guesses defaults**. Instead, it halts before making any Hub mutation and returns an `A2UI_INPUT_REQUIRED` response containing an interactive **A2UI Project & Campaign Initiation Card**:

```json
{
  "status": "A2UI_INPUT_REQUIRED",
  "missing_fields": [
    "program_slug",
    "program_directive",
    "sponsor_gate_policy",
    "seed_mode",
    "stage_entry_point"
  ],
  "message": "Interactive confirmation required before provisioning or launching an OASE campaign. Present the A2UI card fields to the scientist.",
  "a2ui_card": {
    "card_type": "oase_campaign_initiation",
    "title": "OASE Project & Campaign Initiation",
    "fields": [
      {"name": "project_name", "label": "Scion Project Name", "required": true},
      {"name": "project_slug", "label": "Project Slug (kebab-case)", "required": true},
      {"name": "program_slug", "label": "Program Directory Slug (/workspace/<slug>/)", "required": true},
      {"name": "program_directive", "label": "Scientific Program Directive & Charter", "required": true},
      {"name": "sponsor_gate_policy", "options": ["manual", "pre-authorized", "budget-gated"], "required": true},
      {"name": "seed_mode", "options": ["hypex", "sciarchitect", "bring_your_own"], "required": true},
      {"name": "stage_entry_point", "options": ["stage0_hypex", "stage0_verification", "stage1_direct"], "required": true},
      {"name": "service_account_email", "label": "GCP Service Account Email (for GCP AI Endpoints)", "required": true},
      {"name": "harness_config", "options": ["gemini-cli", "claude", "antigravity", "codex"], "default": "gemini-cli"},
      {"name": "default_model", "options": ["small", "medium", "large", "extra-large"], "default": "large"},
      {"name": "members", "label": "Project Team Members (comma-separated emails)", "required": false}
    ]
  }
}
```

#### The Three Negotiated Seed Modes

| Seed Mode (`seed_mode`) | Allowed `stage_entry_point` | Pre-Init WebDAV Seed Artifact (`/workspace/.seed/<slug>/`) | How OASE (`science-program-lead`) Ingests & Starts the Campaign |
|---|---|---|---|
| **Mode 1: `hypex` (Native OASE Tournament)** | `stage0_hypex` | None required | `science-program-lead` logs `DEC-001` and dispatches `WO-001` (`role: hypex-supervisor`) to run an in-container evolutionary hypothesis tournament (`10–15` hypotheses across `hypex-generation`, `hypex-reflection`, `hypex-tournament`, `hypex-evolution`, `hypex-proximity`, `hypex-meta-review` with Elo ranking and `>= 3` PubMed citations per hypothesis), then promotes top winners to `IC-001..IC-N`. |
| **Mode 2: `sciarchitect` (`GA`/`AGY` Tournament Seed Package)** | `stage0_verification` (recommended) or `stage1_direct` | Full **7-Part Zero-Truncation Seed Package** at `/workspace/.seed/<slug>/` anchored by `campaign-seed.json` (`schema: "oase.campaign-seed.v2"`), `coscientist-export.json`, and `CHECKSUMS.json` | `science-program-lead` verifies `CHECKSUMS.json` and `provenance.checksum`, runs `oase coscientist ingest /workspace/.seed/<slug>/coscientist-export.json` + `oase coscientist analyze`, adopts `IC-001..IC-N` (`>= 2` ranked hypotheses), and dispatches `WO-001` (`computational-biologist` / literature verification in `stage0_verification`, or Stage 1 target validation in `stage1_direct`). |
| **Mode 3: `bring_your_own` (Customer / Team Seed)** | `stage0_verification` (default) or `stage1_direct` | `/workspace/.seed/<slug>/campaign-seed.json` (`>= 1` hypothesis with `mechanism_of_action.target_gene`, `>= 1` falsifiable prediction, and `concept_mapping` `IC-001+`) + `CHECKSUMS.json` | `science-program-lead` verifies `CHECKSUMS.json` and `provenance.checksum`, maps customer hypotheses to `IC-001..IC-N`, logs `DEC-001`, and dispatches `WO-001` (`stage0_verification` verification pass or `stage1_direct` Stage 1 execution). |

---

### 4.4 The Seed Handoff Contract (`oase.campaign-seed.v2`) & 7-Part Zero-Truncation `/workspace/.seed/<slug>/` Package

When `seed_mode` is `"sciarchitect"` or `"bring_your_own"`, `GA` or `AGY` stages the seed package over Scion Hub WebDAV (`/api/v1/projects/{projectId}/dav/.seed/<program_slug>/`) **before** starting `controller`.

#### WebDAV Upload & Verification Protocol
1. **Directory Creation (`MKCOL`):** Recursively issues `MKCOL /api/v1/projects/{id}/dav/.seed/<slug>[/<subdir>]`, accepting only HTTP `{201, 405}`.
2. **File Upload (`PUT`):** Uploads each file via `PUT` (accepting only HTTP `{201, 204}`), with large JSON/Markdown files sharded at `<= 1.8 MB` per file to stay well under proxy `~4–6 MB` WebDAV request body ceilings.
3. **Read-Back Integrity Check (`GET`):** Immediately reads back every uploaded file via `GET` and verifies that both byte length and SHA-256 digest match the local source bytes (`SEED_UPLOAD_CHECKSUM_MISMATCH` guard).
4. **Final Manifest Commit (`CHECKSUMS.json` Written LAST):** Only after all package files pass read-back verification does `GA`/`AGY` write `/workspace/.seed/<slug>/CHECKSUMS.json` (containing bare 64-character lowercase hex SHA-256 digests and byte sizes for every file) and read-back verify `CHECKSUMS.json` itself.

#### The 7-Part Zero-Truncation Seed Package Structure (`/workspace/.seed/<slug>/`)

| Part | Staged Files under `/workspace/.seed/<slug>/` | Contract & Scientific Purpose |
|---|---|---|
| **1. Every Idea in Complete Form (Zero Truncation)** | `campaign-seed.json`, `coscientist-export.json`, `ideas/all-ranked-ideas-complete.json`, `ideas/candidate-population-100.json`, `exclusions/rejected-hypotheses-complete.json` | Preserves 100% of tournament hypotheses, rationales, mechanisms, falsification tests, and excluded ideas without field truncation. `coscientist-export.json` feeds `oase coscientist ingest` so OASE never drops fields via the 2-field `oase hypothesis adopt` CLI. |
| **2. All Citations & Claim Provenance** | `citations/references-and-lookup-map.json`, `citations/corpus-references.json`, `citations/claim-ledger-complete.json`, `citations/claim-map.json` | Full PubMed/DOI/ChEMBL/UniProt registry metadata and claim tags (`established`, `retrieved`, `asserted`). Quarantines user `--seed-pmids` inside `corpus-references.json` (`source: "user_seed_pmid_unverified_relevance"`) so they never pollute per-hypothesis `cited_pmids`. |
| **3. Summary & Recommendations** | `summary/report.md`, `tournament/recommendation.md`, `summary/recommendations-and-pareto.json` | Human-readable tournament synthesis, Pareto frontier ranking, and recommended primary (`IC-001`) + backup (`IC-002+`) candidate concepts. |
| **4. Novelty & Scientific Veracity Assessments** | `verification/novelty-and-veracity-assessments.json`, `verification/clinical-development-screen.json`, `verification/entity-support.json`, `verification/data-connectors-audit.json`, `ATTESTATION.json` | Full `verification_gate.verdict` (including objections and `measured_scores`), ClinicalTrials.gov screen, HGNC/UniProt/OpenTargets entity grounding, and `ATTESTATION.json` declaring scope vs. `not_attested` (so OASE runs independent Phase-1/Phase-2 verification). |
| **5. Tournament Data (Debates & Bracket)** | `tournament/match-ledger-index.json`, `tournament/debate-logs-part-01.json..part-NN.json`, `tournament/debates-part-01.md..part-NN.md`, `tournament/evolution-and-bracket-summary.json` | Complete head-to-head debate transcripts, Elo rating trajectories, and evolutionary lineage sharded at `<= 1.8 MB` per file. |
| **6. Submitted Summary & Hardened Prompt** | `submission/submitted-summary-and-hardened-prompt.json`, `submission/model-calls-part-01.json..part-NN.json` | Exact user args, domain profile, hardened tournament prompt, `tool_plan`, and raw model call audit trail. |
| **7. Cryptographic Integrity Manifest** | `CHECKSUMS.json` (**written last**) | Maps every relative path in `/workspace/.seed/<slug>/` to `{"sha256": "<64-char-lowercase-hex>", "bytes": <int>}`. Verified by `science-program-lead` before `DEC-001`. |

#### Canonical `campaign-seed.json` (`oase.campaign-seed.v2`) Structure
```json
{
  "schema": "oase.campaign-seed.v2",
  "version": 1,
  "seed_mode": "sciarchitect",
  "source_run_id": "daedalis-20261028-pcsk9-oral",
  "created_at": "2026-10-28T00:15:00Z",
  "program_context": {
    "program_slug": "pcsk9-oral",
    "program_directive": "Evaluate oral allosteric PCSK9 inhibitors in ASCVD using human genetics, AlphaGenome regulatory variant scoring on GCP, AlphaFold 3 pocket modeling on GCP, and oral macrocycle/small-molecule SAR.",
    "target_indication": "Atherosclerotic Cardiovascular Disease (ASCVD) / Hypercholesterolemia",
    "sponsor_gate_policy": "manual",
    "stage_entry_point": "stage0_verification"
  },
  "ranked_hypotheses": [
    {
      "hypothesis_id": "H-001",
      "rank": 1,
      "elo_rating": 1642.5,
      "title": "Allosteric C-terminal/catalytic-groove PCSK9 small-molecule inhibition disrupting LDLR EGF-A binding",
      "statement": "Small-molecule engagement of the inter-domain allosteric groove between the PCSK9 catalytic and C-terminal Cys-His-rich domains allosterically destabilizes the LDLR EGF-A interface.",
      "mechanism_of_action": {
        "target_gene": "PCSK9",
        "uniprot_id": "Q8NBP7",
        "modality": "small_molecule_allosteric_inhibitor",
        "biological_rationale": "Avoids the flat EGF-A PPI surface while preserving oral Rule-of-5 hepatocyte permeability."
      },
      "falsifiable_predictions": [
        {
          "prediction_id": "FP-001",
          "test_description": "fpocket & AlphaFold 3 co-folding of PCSK9 (PDB 2P4E / Q8NBP7) identifies a cryptic allosteric pocket with druggability score >= 0.50 and ligand ipTM >= 0.70.",
          "kill_criterion": "Druggability score < 0.30 or steric clash across all low-energy conformers."
        }
      ],
      "cited_pmids": ["12730697", "16554528", "37196161"]
    },
    {
      "hypothesis_id": "H-002",
      "rank": 2,
      "elo_rating": 1588.0,
      "title": "Oral tricyclic macrocycle PCSK9-LDLR PPI blockade benchmarked against MK-0616 (enlicitide)",
      "statement": "Oral tricyclic peptidomimetic macrocycle directly occluding the PCSK9 EGF-A binding patch.",
      "mechanism_of_action": {
        "target_gene": "PCSK9",
        "uniprot_id": "Q8NBP7",
        "modality": "oral_macrocycle_ppi_inhibitor",
        "biological_rationale": "Direct orthosteric competition with LDLR EGF-A domain."
      },
      "falsifiable_predictions": [
        {
          "prediction_id": "FP-002",
          "test_description": "Interface contact mapping on EGF-A binding surface confirms salt-bridge and hydrophobic hot-spot coverage with projected human oral bioavailability.",
          "kill_criterion": "Loss of EGF-A hot-spot engagement or unbound hepatic clearance incompatible with QD oral dosing."
        }
      ],
      "cited_pmids": ["17460039", "36884306", "37874921"]
    }
  ],
  "concept_mapping": [
    {
      "concept_id": "IC-001",
      "hypothesis_id": "H-001",
      "target_gene": "PCSK9",
      "modality": "small_molecule_allosteric_inhibitor",
      "role": "primary",
      "status": "active"
    },
    {
      "concept_id": "IC-002",
      "hypothesis_id": "H-002",
      "target_gene": "PCSK9",
      "modality": "oral_macrocycle_ppi_inhibitor",
      "role": "backup",
      "status": "active"
    }
  ],
  "recommendation": {
    "primary_concept_id": "IC-001",
    "backup_concept_ids": ["IC-002"],
    "stage0_verification_focus": [
      "Verify human LoF cardioprotection (gnomAD, OpenTargets, ClinVar) and rs11591147 (R46L) + liver eQTL/sQTL regulatory architecture via AlphaGenome on GCP.",
      "Compare cryptic small-molecule pocket druggability (IC-001) head-to-head against the flat EGF-A macrocycle interface (IC-002)."
    ]
  },
  "rejected_hypotheses": [],
  "corpus_references": [],
  "provenance": {
    "generator": "sciarchitect",
    "checksum_algorithm": "sha256-rfc8785-jcs",
    "checksum": "sha256:<64-char-rfc8785-jcs-digest>"
  }
}
```

> **Canonical Checksum Rule (`provenance.checksum`):** Computed as `"sha256:" + sha256(json.dumps(payload_without_checksum, sort_keys=True, separators=(",", ":"), ensure_ascii=False))` with both `provenance.checksum` and `provenance.checksum_algorithm` omitted from the hashed copy.

---

### 4.5 Canonical `controller` Startup Directive Grammar & 7-Step Autonomous Bootstrap

#### Controller-Only Launch Rule
`GA` and `AGY` start **only one agent** at campaign initiation: `controller` (`--type research-operations-controller`, **without** `--role baseline` so `controller` retains `project:agent:create` permission to spawn `bootstrapper`, `science-program-lead`, `<slug>-head-of-discovery`, `finding-validator`, `project-curator`, and domain specialists). Immediately after `POST /api/v1/projects/{id}/agents`, `bootstrap_campaign` queries `GET /api/v1/projects/{id}/agents` and verifies `controller.template == "research-operations-controller"`. If `controller` silently fell back to `template: "default"`, `bootstrap_campaign` deletes the mis-templated container and fails closed with `CONTROLLER_TEMPLATE_MISMATCH`.

#### Exact `controller` Startup Directive Grammar
- **Mode 1 (`seed_mode = "hypex"`):**
  ```text
  Program directive: <program_directive>. Program directory: /workspace/<program_slug>/. Sponsor gate policy: <manual|pre-authorized|budget-gated>. Seed mode: hypex. Stage entry point: stage0_hypex.
  ```
- **Mode 2 (`seed_mode = "sciarchitect"`) & Mode 3 (`seed_mode = "bring_your_own"`):**
  ```text
  Program directive: <program_directive>. Program directory: /workspace/<program_slug>/. Sponsor gate policy: <manual|pre-authorized|budget-gated>. Seed mode: <sciarchitect|bring_your_own>. Seed artifact: /workspace/.seed/<program_slug>/campaign-seed.json. Stage entry point: <stage0_verification|stage1_direct>.
  ```

#### The 7-Step Autonomous Execution Sequence Inside OASE After `controller` Starts
1. **Step 1 — Spawn `bootstrapper`:** `controller` parses the startup directive and spawns `bootstrapper` (`scion start bootstrapper ... --type bootstrapper`).
2. **Step 2 — Environment Verification (`oase doctor`):** `bootstrapper` executes `oase doctor`, verifying all 62 CLI tool groups, compiled binaries (`fpocket`, `vina`, `meeko`, `hypex`, `elo`, `prox`), `51/51` Phase-2 offline latch rules, and GCP credentials (`AlphaFold 3`, `AlphaGenome`, `Gemini 4`). Requires verdict `PROCEED`.
3. **Step 3 — Workspace Initialization (`oase init`):** `bootstrapper` executes `oase init /workspace/<program_slug>`, creating the 5-layer directory hierarchy (`raw/`, `findings/`, `program-state/`, `gates/`, `executive/`, and `.oase/control/{work-orders,runs,events.ndjson,lock.json}`) and emitting `PROGRAM_INITIALIZED` in `events.ndjson`.
4. **Step 4 — Seed Handoff Verification:** If `seed_mode` is `sciarchitect` or `bring_your_own`, `controller` verifies `/workspace/.seed/<program_slug>/campaign-seed.json` (and `CHECKSUMS.json`) exists on disk and passes its path to `science-program-lead`.
5. **Step 5 — Spawn Governance Tier:** `controller` starts `science-program-lead` (`--type science-program-lead`) and `<program_slug>-head-of-discovery` (`--type head-of-discovery`).
6. **Step 6 — Seed Ingestion, `DEC-001` & `WO-001` Authoring:** `science-program-lead` verifies `CHECKSUMS.json` and `provenance.checksum`, ingests the seed (`oase coscientist ingest` + `campaign-seed.json` for Mode 2/3), writes `DEC-001` in `program-state/decision-log.md` and `program-state/active-series.md`, and drafts `WO-001` (`hypex-supervisor` for Mode 1 `stage0_hypex`, or `computational-biologist` / literature & genetics verification for Mode 2/3 `stage0_verification`).
7. **Step 7 — Autonomous Specialist Dispatch & Dual Validation Loop:** `controller` dispatches `WO-001..WO-N` to ephemeral domain specialists (Phase 1 raw capture with `.meta.json` SHA-256 sidecars → Phase 2 offline analysis), runs **Validation 1** (`finding-validator` executing `oase validate check`), routes passing runs to `science-program-lead` for **Validation 2** (independent Phase-2 reanalysis and `DEC-###` logging), wakes `project-curator` to rebuild `_site/index.html` (`oase site build`), and notifies the human Project Owner via `scion message` (`[OASE_INBOUND_MESSAGE]`) when a Stage Gate is reached.

---

**Next Step:** Proceed to [Module 09 — End-to-End Stage 0→4 Training Curriculum (`pcsk9-oral`)](09-end-to-end-pcsk9-curriculum.md).

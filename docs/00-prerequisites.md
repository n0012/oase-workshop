# Module 00 — GCP & Surface Prerequisites (Connecting GA & AGY to OASE)

> **Audience:** AI Platform Engineers, Cloud Architects, and Workshop Facilitators  
> **Goal:** Provision or verify a Google Cloud (GCP) environment capable of running a multi-user **Scion Hub** and the **GCP-OASE (`oase v0.3.0`)** tool suite with **Gemini 4**, **Claude**, **OpenAI**, **AlphaFold 3**, **AlphaGenome**, and **BigQuery**—and connect interactive agent surfaces (**Gemini Agent / Antigravity / Jetski**) via the **`scion` MCP server (15 tools)** and `pharma-cli dde`.

---

## 1. Architecture & Access Overview

GCP-OASE runs inside a **Scion Hub** VM (`n2-standard-8`, Ubuntu 22.04/24.04 LTS, 250 GB SSD) or GKE cluster where agent containers mount a shared read-only tools volume (`/scion-volumes/tools/`).

As documented in `docs/operating-environment.md`, OASE authenticates to Google Cloud services primarily via **Application Default Credentials (`google.auth.default()`)** resolved from the GCE VM's Workload Identity / service account metadata server—meaning **no static service account JSON key files need to be copied into agent containers**.

| Dependency | Auth Mechanism | Environment Variables | OASE Command(s) |
|---|---|---|---|
| **Frontier LLM Harnesses on GCP (`Gemini 4`, `Claude`, `OpenAI`)** | GCE Metadata ADC (`roles/aiplatform.user`) / Scion Harness Config (`small\|medium\|large\|extra-large`) | `PROJECT_ID`, `REGION` | Scion Agent Harnesses (`controller`, `science-program-lead`, `head-of-discovery`, `scientific-reviewer`, `hypex-*`, specialists) |
| **Dedicated GCP AlphaFold 3 GPU Endpoint** | GCE Metadata ADC (`aiplatform.init()`) | `OASE_AF3_PROJECT`, `OASE_AF3_REGION`, `OASE_AF3_ENDPOINT_NAME`, `OASE_AF3_LOCK` | `oase alphafold predict --input <json>` |
| **Dedicated GCP AlphaGenome GPU Endpoint** | GCE Metadata ADC (`_access_token()`) | `OASE_AG_PROJECT`, `OASE_AG_REGION`, `OASE_AG_ENDPOINT_ID`, `OASE_AG_ENDPOINT_DNS` | `oase alphagenome score-variant`, `oase alphagenome predict-interval` (`--backend vertex`) |
| **BigQuery PubMed Corpus** | GCE Metadata ADC (`roles/bigquery.jobUser`) | `OASE_PUBMED_BQ_DATASET` | `oase pubmed-bq search`, `oase pubmed-bq analyze` |
| **Public Scientific Databases** (`AFDB`, `UniProt`, `gnomAD`, `GTEx`, `HPA`, `CELLxGENE`, `DISCO`, `Europe PMC`, `ClinicalTrials.gov`) | Unauthenticated HTTPS (governed by `oase/core/qps.py` rate limiters) | `OASE_PACE_DIR` | All other `oase <tool> fetch` / `search` commands |

---

## 2. Required GCP APIs & IAM Roles

Run the following commands in your target GCP project (or verify via `scripts/preflight.sh`):

```bash
source .env

# 1. Enable required Google Cloud APIs
gcloud services enable \
  aiplatform.googleapis.com \
  bigquery.googleapis.com \
  compute.googleapis.com \
  storage.googleapis.com \
  artifactregistry.googleapis.com \
  iam.googleapis.com \
  --project="${PROJECT_ID}"

# 2. Verify Gemini 4 and Anthropic Claude models are enabled in your GCP project
```

The GCE VM service account (or developer ADC identity) requires:
- `roles/aiplatform.user` — Invoke Gemini 4, Claude, Dedicated GCP AlphaFold 3 GPU Endpoint, and Dedicated GCP AlphaGenome GPU Endpoint.
- `roles/bigquery.jobUser` + `roles/bigquery.dataViewer` — Execute `oase pubmed-bq search` queries.
- `roles/storage.objectUser` — Read/write staging payloads and exported site archives.

---

## 3. Verifying Dedicated GCP AlphaFold 3 & AlphaGenome GPU Endpoints

Dedicated GCP GPU endpoints (`AlphaFold 3` on `g2-standard-12` / `a2-ultragpu-1g` and `AlphaGenome`) use dedicated prediction DNS hostnames (`*.prediction.vertexai.goog`).

```bash
# Verify AlphaFold 3 Dedicated GCP Endpoint is deployed and visible
gcloud ai endpoints list \
  --project="${OASE_AF3_PROJECT}" \
  --region="${OASE_AF3_REGION}" \
  --filter="displayName:\"${OASE_AF3_ENDPOINT_NAME}\""

# Verify AlphaGenome Dedicated GCP Endpoint is deployed and visible
gcloud ai endpoints describe "${OASE_AG_ENDPOINT_ID}" \
  --project="${OASE_AG_PROJECT}" \
  --region="${OASE_AG_REGION}" \
  --format="value(dedicatedEndpointDns)"
```

> [!IMPORTANT]
> **Single-Flight Serialization on AlphaFold 3:** `oase alphafold predict` acquires an exclusive file lock (`OASE_AF3_LOCK`, default `~/.cache/oase/af3.lock`) before calling the GCP endpoint so concurrent agents on the same host queue cleanly rather than colliding with `already working on a prediction`.

---

## 4. Connecting Interactive Surfaces (`Gemini Agent` & `Antigravity` / `Jetski`) to OASE

Human scientists interact with OASE through their interactive surface (**Gemini Agent (`GA`)**, **Antigravity (`AGY`)**, or **Jetski**) connected to Scion Hub via the **`scion` MCP server (15 tools)** and `pharma-cli dde`.

| Surface / Component | Config & Skill Root | MCP Registration Path | How It Connects to OASE on Scion Hub |
|---|---|---|---|
| **Gemini Agent (`gemini_agent`)** | `~/cowork_workspace/skills/` (physical copies with normalized lowercase kebab-case `SKILL.md` frontmatter) | `~/cowork_workspace/.cowork/mcp_servers.json` (`"servers"` list) → `~/cowork_workspace/.cowork/bin/scion_mcp_server` (`0755`) | Runs `scion_mcp_server` on the host outside `nsjail` via `WorkspaceMcpRegistry`. Includes `gemini-agent-guard` (`~/.config/gemini-agent-guard/`) with automatic inbound OASE message polling (`[OASE_INBOUND_MESSAGE]`). |
| **Antigravity (`antigravity`)** | `~/.gemini/antigravity/skills/` & `~/.gemini/antigravity/agents/` | `~/.gemini/antigravity/mcp_config.json` (`"mcpServers"` map) → `python3 <repo>/tools/scion_mcp_server.py` | Connects via the `scion` stdio MCP server and `pharma-cli dde` CLI (`SCION_DIRECT_HTTPS=1` on external VPCs). |
| **Jetski (`jetski`)** | `~/.gemini/config/skills/`, `~/.gemini/config/agents/`, & `~/.gemini/config/plugins/` | `~/.gemini/config/mcp_config.json` + lazy tool schemas in `~/.gemini/jetski/mcp/scion/*.json` | Connects via the `scion` MCP server (with 15 lazily-loaded tool schemas synced via `refresh_jetski_mcp_schemas`) and `pharma-cli dde`. |

### The 15 `scion` MCP Tools Shared Across Surfaces
1. **Hub & Roster Inspection (4 tools):** `hub_status`, `list_projects`, `list_agents`, `agent_logs`
2. **Direct WebDAV Read & ETag Caching (4 tools):** `decision_log` (parses latest `DEC-###` entries in ~1.5s), `dav_read` (with ETag / `If-None-Match` SHA-256 cache under `~/.cache/pharma_skills/oase_dav` and `LARGE_FILE_SUMMARY` for files `> 20 KB`), `dav_list`, `dde_finding` (reads `scientifically_accepted` work orders)
3. **A2A Push Messaging & Inbound Watchdog (3 tools):** `send_message` (`< 10 KB` bounded envelope), `list_conversations`, `get_messages`
4. **Audited Work-Order Escalation (1 tool):** `request_work_order` (formats a structured `WORK_ORDER_REQUEST` to `science-program-lead`)
5. **Project Owner Provisioning & Campaign Launch (3 tools):** `create_project` (4-step atomic setup + team member assignment + `OASE_TEMPLATES_MISSING` guard), `bootstrap_campaign` (`A2UI_INPUT_REQUIRED` initiation card + WebDAV seed staging + controller-only launch with `CONTROLLER_TEMPLATE_MISMATCH` guard), `start_agent`

### Configure `~/.config/pharma_skills/config.toml` (Zero Hardcoding)
```toml
[oase]
hub_url = "https://<your-scion-hub-host>"
default_gcp_project = "<YOUR_GCP_PROJECT_ID>"
default_service_account_email = "scion-default-agent@<YOUR_GCP_PROJECT_ID>.iam.gserviceaccount.com"
dav_inline_max_bytes = 20480

[cost_gates]
enabled = false
```

```bash
# Authenticate to the Scion Hub (writes ~/.scion/credentials.json) and sync surfaces
scion --hub "$SCION_HUB_URL" auth login
scion --hub "$SCION_HUB_URL" hub status

python3 scripts/surface_install.py \
  --surface gemini_agent \
  --surface antigravity \
  --surface jetski
```

---

## 5. Provisioning the Shared Tools Volume (`/scion-volumes/tools/`)

In OASE, specialist agents are **strictly read-only at runtime** (`docs/tool-design-guidance.md` §2 Rule 1: no `pip install`, no `uv add`, no `apt` inside specialist containers). All Python packages (`RDKit`, `biopython`, `scipy`, `h5py`, `meeko`) and compiled static binaries (`fpocket`, `vina`) are installed once into `/scion-volumes/tools/` and stamped with a cryptographic `ENV_VERSION`:

```bash
# 1. Install or update the shared OASE tools environment
cd /workspace/tools && ./install.sh

# 2. Activate the shared environment (adds .venv/bin and bin/ to PATH)
source /scion-volumes/tools/env.sh

# 3. Verify environment stamp and provenance
oase env
```

### Offline KaTeX Assets for `oase site build`
Because `oase site build` compiles self-contained 28-page evidence portals completely offline, it checks for KaTeX assets under `/scion-volumes/tools/vendor/katex/katex.min.css` (and `/scion-volumes/tools/npm/node_modules/katex/dist`). Verify they are present:

```bash
ls -lh /scion-volumes/tools/vendor/katex/katex.min.css
```

---

## 6. Running the Workshop Pre-Flight Check

Before starting Module 01, run `oase doctor` against the `live-sandbox` project:

```bash
source /scion-volumes/tools/env.sh
OASE_PROJECT=/workspace/live-sandbox oase doctor
```

Expected verdict: **`PROCEED`** (zero `"fail"` checks; `"warn"` items such as an unset `ALPHAGENOME_API_KEY` when using the GCP endpoint backend are informational and non-blocking).

---

**Next Step:** Proceed to [Module 01 — Tour the Grove](01-tour-the-grove.md).

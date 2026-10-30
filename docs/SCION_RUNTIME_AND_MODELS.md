# Scion Multi-Model Runtime, Toolchain & Endpoint Configuration Runbook

This runbook documents the complete, repeatable procedure to configure a Scion Hub VM (`scion-hub-oase`) for multi-model live OASE execution using **Gemini 4 Argon**, **Anthropic Claude Opus 5.5**, and **Gemini 3.8 Flash**, together with a portable shared `oase v0.3.0` scientific toolchain and dedicated Vertex AI GPU endpoints (`AlphaGenome` and `AlphaFold 3`).

All steps are automated by two idempotent repository scripts:
- [`scripts/enable-vertex-models.py`](../scripts/enable-vertex-models.py) — Enables Vertex AI partner model data sharing (`:setPublisherModelConfig`), configures `constraints/vertexai.allowedPartnerModelFeatures`, and surfaces the one-time Model Garden subscription links.
- [`scripts/reconcile-scion-runtime.py`](../scripts/reconcile-scion-runtime.py) — Builds the multi-model Scion container images (`scion-claude:latest` alongside `scion-antigravity:latest`), repairs shared `oase v0.3.0` `.venv` portability without altering `ENV_VERSION`, injects dedicated endpoint environment variables into `hub.db`, configures the 20 specialist agent templates, and provisions the isolated `pcsk9-oral-live-v2` live execution grove.

---

## 1. Multi-Model Roster & Scion Harness Mapping

Scion routes each specialist agent template to a container harness (`antigravity` or `claude`) and a model tier (`extra-large`, `large`, `medium`, `small`) defined in `/home/scion/.scion/harness-configs/<harness>/config.yaml`:

| Harness | Container Image | CLI Version Requirement | Tier Alias | Resolved Vertex AI Model ID | Assigned OASE Specialist Templates |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`antigravity`** | `scion-antigravity:latest` | `agy` (Antigravity CLI) | `extra-large` | **`gemini-4-argon-high`** (`Gemini 4 Argon (High)`) | `science-program-lead`, `head-of-discovery`, `structural-biologist`, `hypex-supervisor`, `hypex-generation`, `hypex-tournament`, `hypex-meta-review` |
| **`claude`** | `scion-claude:latest` | `@anthropic-ai/claude-code >= 2.1.280` | `large` | **`claude-opus-5-5`** (`Claude Opus 5.5`) | `scientific-reviewer`, `medicinal-chemist`, `hypex-reflection` |
| **`antigravity`** | `scion-antigravity:latest` | `agy` (Antigravity CLI) | `large` | **`gemini-4-argon-medium`** (`Gemini 4 Argon (Medium)`) | `admet-dmpk-scientist`, `computational-chemist`, `computational-biologist`, `experimental-biologist`, `preclinical-toxicologist`, `regulatory-scientist`, `hypex-evolution` |
| **`antigravity`** | `scion-antigravity:latest` | `agy` (Antigravity CLI) | `medium` | **`gemini-3.8-flash-medium`** (`Gemini 3.8 Flash (Medium)`) | `finding-validator`, `project-curator`, `research-operations-controller`, `hypex-proximity`, `bootstrapper` |

> **Why Cross-Family Peer Review (`Gemini 4 Argon` + `Claude Opus 5.5`) Matters**: Routing `scientific-reviewer`, `medicinal-chemist`, and `hypex-reflection` to **Anthropic Claude Opus 5.5** while `science-program-lead`, `structural-biologist`, and `hypex-generation` run on **Gemini 4 Argon (High)** eliminates single-model self-confirmation bias during Two-Phase Peer Review (`oase review record`) and Co-Scientist tournament reflection.

### Specialist Persona Prompts (`system-prompt.md` + `agents.md`) & Template Hydration

Every specialist template in `/home/scion/.scion/projects/open-agentic-science-engine/templates/<slug>/` carries three synchronized artifacts:
1. **`system-prompt.md` (`900 B – 3,700 B`)**: Role identity, decision authority boundaries, and the **Operational & Epistemic Invariants**:
   - **Provenance & Evidence Discipline:** Every numerical or factual claim in a Layer 1 finding, review, or decision must carry a machine-verifiable `[src:<run_id>:<json_pointer>]` or `[src:lit:<id>]` provenance tag backed by a stored Layer 0 artifact and `.provenance.json` sidecar.
   - **Shared OASE Toolchain:** Automatic activation of `/workspace/.scion-volumes/tools/env.sh` before running `oase` or `prox`.
   - **Scion Webchat Reply Contract:** Mandatory `scion message "conv:<conversation.id>"` + `sciontool status ask_user` response whenever `"channel": "web"` is present.
2. **`agents.md` (`2.5 KB – 67.8 KB`)**: Full specialist operational runbook (`science-program-lead`: `67.8 KB`; `research-operations-controller`: `33.6 KB`; `scientific-reviewer`: `31.1 KB`; `hypex-reflection`: `16.3 KB`; `hypex-meta-review`: `13.2 KB`; domain specialists: `7.8 KB – 10.4 KB`).
3. **`scion-agent.yaml`**: Binds the template's domain skills (`skill://<slug>`) from the 43 project-scoped OASE skills.

`hydrate_and_repair_templates()` in `scripts/reconcile-scion-runtime.py` ensures that for all 220 template rows across all groves (`open-agentic-science-engine`, `00..07`, and `pcsk9-oral-live-v2`):
- Content-addressed blobs are written to `/home/scion/.scion/workspace-storage/<storage_path>.blobs/<sha256_hex>` (`layout = 'blobs'`),
- Unpacked template directories (`agents.md`, `scion-agent.yaml`, `system-prompt.md`) are populated in `/home/scion/.scion/cache/templates/<content_hash>/` and registered in `/home/scion/.scion/cache/templates/index.json`, and
- Every provisioned agent home (`home/.scion/harness/inputs/{instructions.md,system-prompt.md}`, `.gemini/GEMINI.md`, and `.claude/{CLAUDE.md,system-prompt.md}`) is hydrated so neither `Gemini 4 Argon` nor `Claude Opus 5.5` ever falls back to `templates/default` (`# Placeholder`).

---

## 2. Step-by-Step Repeatable Enablement

### Step 2.1 — Enable Vertex AI Partner Models (`Claude Opus 5.5`)

 Enabling Anthropic Claude models (`claude-opus-5-5`, `claude-sonnet-5-5`, `claude-haiku-5-5`, `claude-haiku-4-5`) on a Google Cloud project requires three layers:

1. **One-Time Model Garden Partner Subscription (Console EULA)**:
   - In the Google Cloud Console, open the Model Garden questionnaire for **Claude Opus 5.5** (`publishers/anthropic/models/claude-opus-5-5`, partner service `anthropic-914.cloudpartnerservices.goog`) and click **Enable / Agree**.
   - Run `python3 scripts/enable-vertex-models.py --project "$GCP_PROJECT_ID"` to print the exact pre-populated `model_garden_enable_urls` for your project.
2. **Per-Location Data Sharing (`:setPublisherModelConfig`)**:
   - Vertex AI requires opting into Anthropic partner data sharing **per model and per location** (`global`, `us`, `us-east5`, `us-central1`):
     ```bash
     POST https://aiplatform.googleapis.com/v1beta1/projects/${GCP_PROJECT_ID}/locations/global/publishers/anthropic/models/claude-opus-5-5:setPublisherModelConfig
     {"publisherModelConfig": {"dataSharingEnabledProvider": "anthropic"}}
     ```
   - **Important Endpoint Host Rule**:
     - `global` uses `https://aiplatform.googleapis.com`
     - Multi-region `us` uses `https://aiplatform.us.rep.googleapis.com` (not `us-aiplatform.googleapis.com`)
     - Regional endpoints use `https://<region>-aiplatform.googleapis.com`
   - **Important mTLS Token Rule**:
     - Public `aiplatform.googleapis.com` rejects context-aware mTLS client-certificate tokens (`401 ACCESS_TOKEN_TYPE_UNSUPPORTED`). Always mint tokens with `CLOUDSDK_CONTEXT_AWARE_USE_CLIENT_CERTIFICATE=false` (handled automatically by `scripts/enable-vertex-models.py`).
3. **Partner Model Features Organization Policy**:
   - Enables `orgpolicy.googleapis.com` and sets `constraints/vertexai.allowedPartnerModelFeatures` to allow `publishers/anthropic`:
     ```bash
     python3 scripts/enable-vertex-models.py --project "$GCP_PROJECT_ID"
     ```

### Step 2.2 — Build `scion-claude:latest` & Configure Haiku Sub-Call Pinning

Scion's `claude` harness (`harness-configs/claude/provision.py`) enforces `OPUS_5_5_MIN_CLAUDE_VERSION = (2, 1, 280)` and launches containers from `scion-claude:latest`.

1. **Build `scion-claude:latest` from `scion-base:latest`**:
   - `scripts/reconcile-scion-runtime.py` writes `/home/scion/.scion/harness-configs/claude/Dockerfile` and builds `scion-claude:latest` + `localhost/scion/scion-claude:latest` with `@anthropic-ai/claude-code@latest` (`>= 2.1.312`).
2. **Pin Background Fast/Haiku Calls to `claude-opus-5-5`**:
   - By default, Claude Code makes background fast calls using `ANTHROPIC_DEFAULT_HAIKU_MODEL` (`claude-haiku-4-5`). If only `claude-opus-5-5` has had its Model Garden EULA enabled in the project, background Haiku calls would return `404`.
   - `scripts/reconcile-scion-runtime.py` sets both `ANTHROPIC_DEFAULT_HAIKU_MODEL: "claude-opus-5-5"` and `ANTHROPIC_SMALL_FAST_MODEL: "claude-opus-5-5"` in `/home/scion/.scion/harness-configs/claude/config.yaml` so every Claude Code call routes cleanly through the enabled `claude-opus-5-5` endpoint.

---

## 3. Shared `oase v0.3.0` Volume Portability (Zero `ENV_VERSION` Drift)

When Scion provisions chapter or live execution groves, it bind-mounts each grove's `shared-dirs/tools` directory into `/workspace/.scion-volumes/tools` inside the agent container. Three host-path traps in a default `pip install -e` virtual environment must be normalized so `oase` runs inside every container without altering the pinned `ENV_VERSION` hash (`sha256:2987d3053f138de06c119fb09bd1eed054f75c013cfc25c8b294d1dee2acac5b`):

1. **Replace Host-Only Editable `.pth` Finder with Materialized Package Directory**:
   - An editable install (`__editable__.oase-0.3.0.pth` + `__editable___oase_0_3_0_finder.py`) points to the host path `/home/scion/.scion/projects/open-agentic-science-engine/tools/oase`, which does not exist inside chapter containers.
   - `repair_shared_oase_volumes()` removes the `.pth` finder and copies the `oase/` package directory directly into `shared-dirs/tools/.venv/lib/python3.13/site-packages/oase` while leaving `oase-0.3.0.dist-info/` and `env-manifest.txt` untouched (`importlib.metadata.version("oase") == "0.3.0"` and `ENV_VERSION` hash remain 100% identical).
2. **Dynamic `VIRTUAL_ENV` Resolution in `.venv/bin/activate`**:
   - Default `activate` scripts hardcode `export VIRTUAL_ENV=/scion-volumes/tools/.venv`. When mounted at `/workspace/.scion-volumes/tools`, sourcing `activate` prepends `/scion-volumes/tools/.venv/bin` instead of `/workspace/.scion-volumes/tools/.venv/bin`.
   - `repair_shared_oase_volumes()` rewrites `VIRTUAL_ENV` in `.venv/bin/activate` to resolve dynamically:
     ```bash
     export VIRTUAL_ENV="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
     ```
3. **Portable Entry-Point Shebangs**:
   - Rewrites `#!/scion-volumes/tools/.venv/bin/python*` across `.venv/bin/*` entry-point scripts (`oase`, `pytest`, `rdkit`, etc.) to `#!/usr/bin/env python3`.
4. **Symlink `/scion-volumes/tools -> /workspace/.scion-volumes/tools` for Hashed Wrapper Binaries (`prox`)**:
   - `tools/bin/prox` is hashed directly in `env-manifest.txt` (`sha256:7e32badc...`) and invokes `/scion-volumes/tools/.venv/bin/python`. Modifying `tools/bin/prox` would change `ENV_VERSION`. Creating the symlink `/scion-volumes/tools -> /workspace/.scion-volumes/tools` inside each container allows `prox` (and `hypothesis strategy: hypex`) to pass `oase doctor` with zero bytes changed in `tools/bin/prox`.
5. **Campaign Program Root vs. Source Repo Sentinel (`.oase-repo`)**:
   - `oase` uses `.oase-repo` to detect its own source code repository and refuses to use a directory containing `.oase-repo` as a campaign `OASE_PROJECT` root. `repair_shared_oase_volumes()` removes any accidental `.oase-repo` sentinel from campaign workspaces (`00..07` and `pcsk9-oral-live-v2`) while preserving it in `open-agentic-science-engine`.

---

## 4. Dedicated Vertex AI GPU Endpoint Discovery & Hub Env Injection

Both **AlphaGenome** and **AlphaFold 3** run on **Dedicated Vertex AI Endpoints** (`dedicatedEndpointEnabled: true`), which require sending prediction traffic to their dedicated DNS hostnames (`*.prediction.vertexai.goog`) rather than standard shared regional endpoints.

### Discovering Endpoint IDs and Dedicated DNS Hostnames

> **Important**: A Dedicated Vertex AI Endpoint DNS hostname embeds the **Model Garden tenant project number**, not your consumer project number. Always query `dedicatedEndpointDns` directly from `gcloud ai endpoints list`:

```bash
# 1. AlphaGenome Dedicated Endpoint (us-central1)
gcloud ai endpoints list \
  --project="$GCP_PROJECT_ID" \
  --region=us-central1 \
  --format="table(name.basename(),displayName,dedicatedEndpointDns)"

# 2. AlphaFold 3 Dedicated Endpoint (us-east4)
gcloud ai endpoints list \
  --project="$GCP_PROJECT_ID" \
  --region=us-east4 \
  --format="table(name.basename(),displayName,dedicatedEndpointDns)"
```

### Hub-Scoped Environment Variables (`hub.db` -> `env_vars`)

`scripts/reconcile-scion-runtime.py` upserts all 10 variables at `scope='hub'` with `injection_mode='always'` so every container across `antigravity` and `claude` receives them automatically at PID 1 (`sciontool init`):

| Variable | Description |
| :--- | :--- |
| `OASE_PROJECT` | Default OASE campaign program root inside agent containers (`/workspace`) |
| `OASE_TOOLS_HOME` | Shared OASE v0.3.0 toolchain volume path inside agent containers (`/workspace/.scion-volumes/tools`) |
| `OASE_AG_PROJECT` | Consumer GCP project ID hosting the AlphaGenome endpoint |
| `OASE_AG_REGION` | Region for AlphaGenome (`us-central1`) |
| `OASE_AG_ENDPOINT_ID` | Vertex AI Endpoint ID (`mg-endpoint-...`) |
| `OASE_AG_ENDPOINT_DNS` | Dedicated prediction DNS (`mg-endpoint-....us-central1-....prediction.vertexai.goog`) |
| `OASE_AF3_PROJECT` | Consumer GCP project ID hosting the AlphaFold 3 endpoint |
| `OASE_AF3_REGION` | Region for AlphaFold 3 (`us-east4`) |
| `OASE_AF3_ENDPOINT_NAME` | Endpoint display name (`AlphaFold 3 Dedicated Endpoint`) |
| `CLOUD_ML_REGION` | Vertex AI region for Anthropic Claude partner models (`global`) |

---

## 5. Running the Full Reconciler & Verifying `pcsk9-oral-live-v2`

Run `scripts/reconcile-scion-runtime.py` on `scion-hub-oase` to apply all container, toolchain, environment variable, template model routing, and live `v2` grove configurations in one pass:

```bash
gcloud compute scp scripts/reconcile-scion-runtime.py \
  scion-hub-oase:/tmp/reconcile-scion-runtime.py \
  --project="$GCP_PROJECT_ID" --zone=us-central1-c

gcloud compute ssh scion-hub-oase \
  --project="$GCP_PROJECT_ID" --zone=us-central1-c \
  --command="sudo python3 /tmp/reconcile-scion-runtime.py \
    --gcp-project '$GCP_PROJECT_ID' \
    --ag-region us-central1 \
    --ag-endpoint-id '$OASE_AG_ENDPOINT_ID' \
    --ag-endpoint-dns '$OASE_AG_ENDPOINT_DNS' \
    --af3-region us-east4 \
    --af3-endpoint-name 'AlphaFold 3 Dedicated Endpoint' \
    --claude-vertex-region global \
    --enable-claude \
    --provision-live-grove pcsk9-oral-live-v2"
```

### Verification Checklist

1. **`oase doctor --json` inside both `antigravity` (`Gemini 4 Argon`) and `claude` (`Claude Opus 5.5`) containers**:
   - Returns `"verdict": "PROCEED"`, `"failures": []` (`0` failures across all `17` checks), and `"env_version": "sha256:2987d3053f138de06c119fb09bd1eed054f75c013cfc25c8b294d1dee2acac5b"`.
2. **Live Model Inference Verification**:
   - `pcsk9-oral-live-v2--science-program-lead` runs `scion-antigravity:latest` with `SCION_MODEL=extra-large` -> **`Gemini 4 Argon (High)`** (`gemini-4-argon-high`).
   - `pcsk9-oral-live-v2--scientific-reviewer` runs `scion-claude:latest` with `SCION_MODEL=large` -> **`Claude Opus 5.5`** (`claude-opus-5-5`).
   - `pcsk9-oral-live-v2--controller` runs `scion-antigravity:latest` with `SCION_MODEL=medium` -> **`Gemini 3.8 Flash (Medium)`** (`gemini-3.8-flash-medium`).
3. **Zero Mutation of Reference Groves (`00..07`)**:
   - All 8 reference pilot chapters (`00-pcsk9-initial-seed` through `07-pcsk9-mission-closeout`) remain untouched and selectable in the Story Arc Presenter Cockpit.

---

## 6. Argolis First-Try Execution Hardening (Lessons from `venter-scion`)

Cross-referencing the original `venter-scion` pilot handoff (`docs/pilot-handoff.md`, `docs/quickstart-pilot.md`, and `docs/alphafold-complex-prediction.md`) surfaced six operational safeguards now enforced by [`scripts/reconcile-scion-runtime.py`](../scripts/reconcile-scion-runtime.py):

1. **Container PID 1 `OASE_PROJECT` & `OASE_TOOLS_HOME` Injection:**
   - Because Scion launches `claude` and `agy` via `tmux new-session ... sh -c` (non-interactive shell before `.bashrc` runs), `OASE_PROJECT=/workspace` and `OASE_TOOLS_HOME=/workspace/.scion-volumes/tools` are injected directly via Hub `env_vars` (`injection_mode='always'`) so every agent sees `OASE_PROJECT=/workspace` immediately on startup.
2. **Pre-Booted `controller` (`research-operations-controller`) Alongside `science-program-lead` and `scientific-reviewer`:**
   - `science-program-lead` never executes CLI tools or spawns specialist containers directly; it dispatches approved work orders to `controller` (`research-operations-controller`), which spawns specialist workers (`computational-biologist`, `structural-biologist`, `computational-chemist`, `medicinal-chemist`, `admet-dmpk-scientist`, `finding-validator`, `hypex-supervisor`) via `scion start`. Pre-booting `controller` in `pcsk9-oral-live-v2` ensures work orders execute immediately.
3. **`#general` Webchat Default Agent Routing (`default_agent = 'science-program-lead'`):**
   - `webchat_topic` and `conversations` in `pcsk9-oral-live-v2` bind `default_agent = 'science-program-lead'` and register all 5 scientist accounts plus the 3 live orchestrator agents in `conversation_participants` so any un-tagged message in `#general` routes automatically to `science-program-lead`.
4. **`web-builder` Template Alias to `project-curator`:**
   - `templates/research-operations-controller/agents.md` dispatches portal builds via `scion start <program>-web-builder --type web-builder`. Registering `web-builder` as a project template alias for `project-curator` prevents a missing-template error during stage-gate portal publication.
5. **Complete `agent-role-full` Permissions (`role_definitions`):**
   - Ensures `agent-role-full` grants `"agent.list"`, `"agent.read"`, `"agent.update"`, `"agent.message"`, `"project.chat_post"`, `"inbox.read"`, and `"inbox.write"` so agents spawned dynamically by `controller` or `hypex-supervisor` can message peers and post to Webchat without `403` errors.
6. **Single-Flight AlphaFold 3 & Heredoc Messaging Discipline:**
   - **AlphaFold 3 (`oase alphafold predict`)** runs on a single-replica Dedicated Vertex AI Endpoint (`--deadline 1800`, retrying `504` every `60s` on cold start and `429` every `15–25s` when busy). Always schedule AF3 work orders sequentially rather than fanning out across parallel containers.
   - **Backtick Command-Substitution Guard (`scion message`)**: Never pass double-quoted strings containing backticks to `scion message`; always use single-quoted heredocs (`scion message "conv:<id>" - <<'MSG' ... MSG`).

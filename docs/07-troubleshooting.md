# Module 07 — Field-Tested Troubleshooting & Remedies

> **Audience:** AI Platform Engineers, Developers, and Workshop Facilitators  
> **Purpose:** Exact diagnostics and one-command remedies for every real failure mode observed across `oase v0.3.0` (`707e461`), the `GA/AGY ↔ OASE` surface contract (`scion` MCP), Scion Hub, and Dedicated GCP GPU Endpoints.

---

## 1. Quick Diagnostic Matrix (`oase` CLI & GCP Endpoints)

Always start by running `oase doctor --json` inside the target project directory:

```bash
source /scion-volumes/tools/env.sh
oase --project /workspace/live-sandbox doctor --json | jq .
```

| Symptom / Error Message | Root Cause | Exact Remedy |
|---|---|---|
| `EndpointUnavailable: timed out waiting for the AF3 lock file` | `oase alphafold predict` serializes single-flight calls via `~/.cache/oase/af3.lock` (`OASE_AF3_LOCK`). Another prediction is running (or a killed process left a lock). | Check `ps aux \| grep "oase alphafold predict"`. Wait for completion, pass `--deadline 3600`, or jump to `ch3` via `checkpoint.sh goto ch3`. |
| `404 Not Found` when calling `oase alphagenome score-variant` | Calling the regional API host (`us-central1-aiplatform.googleapis.com`) instead of the Dedicated GCP Endpoint DNS (`*.prediction.vertexai.goog`). | Ensure `OASE_AG_ENDPOINT_DNS` is set to `<ENDPOINT_ID>.<REGION>-<PROJECT_NUMBER>.prediction.vertexai.goog` (see `.env.example`). |
| `CredentialError: checked the ALPHAGENOME_API_KEY environment variable` | Running `oase alphagenome ism` or passing `--backend pip` without an API key (`ism` is pip-backend-only). | Use `oase alphagenome score-variant` or `predict-interval` with `--backend vertex` (default GCP endpoint backend, uses GCE ADC), or export `ALPHAGENOME_API_KEY`. |
| `oase site build` fails looking for `katex.min.css` | `site.py` requires offline KaTeX assets under `${OASE_TOOLS_HOME}/vendor/katex/katex.min.css` (and `/scion-volumes/tools/npm/node_modules/katex/dist`). | Run `/workspace/workshop/scripts/preflight.sh` (which populates both offline KaTeX paths). |
| `PhaseContractError` during an `analyze` command | A custom or modified `analyze*` command attempted to make an outbound HTTP request. Phase 2 is strictly offline-latched at the root CLI tree. | Move all network/API lookups into Phase 1 (`fetch`/`run`/`predict`) and read from `raw/` in Phase 2 (`docs/tool-design-guidance.md` §3). |
| `oase h5ad` exits with code `8` (`h5py is not installed`) | `h5py` was not installed into the shared `/scion-volumes/tools/.venv`. | Run `/scion-volumes/tools/.venv/bin/pip install h5py` via `cd /workspace/tools && ./install.sh --update` (never inside a specialist container). |
| `oase h5ad analyze` exits with code `2` on `--select-label "Activated stellate cell"` | By design! `oase h5ad` matches atlas labels verbatim and never guesses. DISCO's 5 cirrhosis samples use `"CFD+MGP+ fibroblast"`, `"CCL19+APOE+ fibroblast"`, `"Mesenchymal stromal cell"`, `"Pericyte"`. | Inspect the exact label vocabulary printed in the error message and pass `--select-label "CFD+MGP+ fibroblast"`. |
| `oase doctor` reports an **`env_version` partition warning** (`HOUSEKEEPING`) | `/scion-volumes/tools/` was updated mid-program, so earlier `.meta.json` sidecars carry a different `env_version` hash than newer ones. | Phase 2 `.analysis.json` files can be regenerated offline (`oase <tool> analyze <id>`); Phase 1 payloads must be re-fetched if strict single-environment comparability (`oase doctor --strict`) is required. |
| `oase disco search` returns empty `project` and `cell_type_annotation` fields | Known upstream boundary defect in `commands/disco.py`: `_extract_sample_record` reads `project` instead of `project_id` from the DISCO v3 API. | Use `oase h5ad fetch <SAMPLE_ID> --source disco`, which queries `toolkit/getSampleMetadata` (`project_id`) and `toolkit/getCellTypeSample` directly. |
| `UsageError: geneMask does not accept OUTPUT_TYPE_CONTACT_MAPS` | `alphagenome.py` pre-validates `scorer` × `output-type` pairings locally because the GCP endpoint returns an opaque `502` on unsupported combinations. | Pair `--scorer geneMask` with `RNA_SEQ`, `ATAC`, `CAGE`, `DNASE`, `CHIP_HISTONE`, `CHIP_TF`, or `PROCAP`; use contact/splice scorers for `CONTACT_MAPS` / `SPLICE_*`. |

---

## 2. Surface-to-OASE (`GA` & `AGY` / `scion` MCP) Troubleshooting Matrix

| Error Code / Symptom | Root Cause | Exact Remedy |
|---|---|---|
| `OaseHubNotConfigured` | Neither `SCION_HUB_URL` nor `~/.config/pharma_skills/config.toml` (`[oase] hub_url`) is set. | Add `[oase]\nhub_url = "https://..."` to `~/.config/pharma_skills/config.toml` or export `SCION_HUB_URL`. |
| `GCP_SA_NOT_VERIFIED` | Project GCP Service Account failed verification on `POST /api/v1/projects/{id}/gcp-service-accounts/{saId}/verify`. | Verify the SA exists in the target GCP project and has IAM permissions, then re-run `create_project`. |
| `OASE_TEMPLATES_MISSING` | Project was created via raw `scion project create` without importing the 22 OASE templates. | Run `create_project` (or `POST /api/v1/projects/{id}/import-templates`) and verify all 6 critical templates exist before starting `controller`. |
| `CONTROLLER_TEMPLATE_MISMATCH` | `controller` started before template import completed and silently fell back to `template: default`. | `bootstrap_campaign` automatically deletes the mis-templated agent and fails closed; re-run after template import passes. |
| `SEED_UPLOAD_CHECKSUM_MISMATCH` | WebDAV `PUT` was truncated (e.g., unsharded file `> 4 MB` hit proxy limit) or corrupted in transit. | Keep seed shards `<= 1.8 MB` and re-run `bootstrap_campaign` so read-back `GET` SHA-256 verification and `CHECKSUMS.json` succeed. |
| `SESSION_PROJECT_LOCKED` | Current GA/AGY session is already bound to a different Scion project (1-project-per-session rule). | Start a new GA/AGY chat session for the second project, or pass `switch_project=true` if intentionally rebinding. |
| `ONE_PROGRAM_PER_PROJECT` | Target Scion project already has `.oase-project-lock.json` bound to a different `program_slug`. | Create a new Scion project (`create_project`) for the new scientific program (1-program-per-project invariant). |
| `ESCALATION_REQUIRED` (`Exit 3`) | `surface_install.py` was invoked inside GA's read-only `nsjail` sandbox. | Re-run `python3 scripts/surface_install.py` from GA with `permissions="require_escalated"` or from a host terminal. |

---

## 3. The 6 Golden Rules & Quick Command Cross-Reference

### The 6 Golden Rules of `GA`/`AGY` ↔ OASE Operation
1. **Project Owner Initiates & Assigns (`create_project` + `bootstrap_campaign`):** Always initiate new projects and campaigns from `GA` or `AGY` via `create_project` / `bootstrap_campaign` (never bare `scion project create`) so GCP SA verification, `tools` volume mounting, team `members` assignment, and 6-template verification happen atomically.
2. **Respect the Latency & Provenance Boundary ("Gray Zone" Rule):**
   - Need a 5-second answer for interactive discussion? Run it on the `GA` / `AGY` surface.
   - Will the number or conclusion be cited in a `DEC-###` decision or Stage Gate? Escalate it via `request_work_order` so OASE executes Phase 1 (`.meta.json` SHA-256 sidecar) + Phase 2 (100% offline `.analysis.json`) + Dual Validation (`Validation 1` + `Validation 2`).
3. **Read Direct via WebDAV (`decision_log`, `dav_read`), Write Only via Bounded Push Messages (`< 10 KB`):** Never write or edit files under `/workspace/<program-slug>/` directly from `GA`/`AGY`. Use `decision_log` (~1.5s) and `dav_read` (with ETag cache) for reads, and `request_work_order` / `send_message` (`< 10 KB`) for writes.
4. **One Project Per Session (`SESSION_PROJECT_LOCKED`) & One Program Per Project (`ONE_PROGRAM_PER_PROJECT`):** Start a new `GA`/`AGY` chat session when switching to a different Scion project, and create a new Scion project for each distinct drug discovery program.
5. **Never Use `oase hypothesis adopt` for SciArchitect Bundles:** Always stage the 7-part seed bundle to `/workspace/.seed/<slug>/` (`CHECKSUMS.json` last) and ingest via `oase coscientist ingest <export_file>` so zero fields, citations, or debate logs are lost.
6. **Always Verify `oase validate check --preflight` Before Submitting a Work Order:** Checks SHA-256 sidecars, JSON schemas, threshold citations, mandatory `[relay:<code>]` tags, and `{source: raw/...}` JSONPath numerical claims in seconds.

### Quick Command Cross-Reference (`scion` MCP vs. `pharma-cli dde` vs. Container `oase` CLI)

| Task | From `GA` / `AGY` (`scion` MCP Tool) | From Workstation CLI (`pharma-cli dde`) | Inside OASE Agent Container (`oase` CLI) |
|---|---|---|---|
| **Create Project & Assign Team** | `scion:create_project` | `pharma-cli dde create-project --name ... --member ...` | *(Forbidden: requires `UserIdentity` token)* |
| **Launch Campaign + Seed** | `scion:bootstrap_campaign` | `pharma-cli dde bootstrap-campaign ...` | `oase doctor` → `oase init /workspace/<slug>` |
| **Read Latest Decisions (`DEC-###`)** | `scion:decision_log` (`limit: 10`) | `pharma-cli dde decision-log --limit 10` | Read `program-state/decision-log.md` |
| **Read Workspace File (`L0–L4`)** | `scion:dav_read` (`path`, `head_lines`/`section`) | `pharma-cli dde dav-read <path>` | Read `/workspace/<slug>/<path>` |
| **Request New Work Order (`WO-*`)** | `scion:request_work_order` | `pharma-cli dde request-work-order ...` | `oase workorder create --from wo.json --commit` |
| **Validate Work Order (10 Checks)** | Read via `scion:dde_finding` | `pharma-cli dde finding --wo WO-004` | `oase validate check WO-004` |
| **Build & Export 28-Page Portal** | Request `project-curator` via `send_message` | Download `_site/<slug>-site.zip` via WebDAV | `oase site build && oase site validate && oase site export` |

---

## 4. Debugging Scion Agent Containers

### Checking Agent Status and Recent Logs
```bash
# List all running, blocked, or completed agents in the active grove
scion list

# Inspect the last 100 lines of output from an agent
scion output controller
scion output science-program-lead
```

### If `controller` Stops During Bootstrap
As documented in `docs/quickstart-pilot.md` §6, `controller` executes five sequential bootstrap steps and halts immediately if any check fails:
1. `cd /workspace/tools && ./install.sh --update`
2. `source /scion-volumes/tools/env.sh && oase doctor --json`
3. `scion template sync --all`
4. `oase init <program-directory>`
5. `scion start science-program-lead ...`

Run `scion output controller` to see which of the 5 steps halted, fix the underlying prerequisite, and restart `controller`.

---

## 4. Recovering a Corrupted Workshop Grove (`<3 Seconds`)

If a participant accidentally deletes files under `.oase/control/` or corrupts a work order in `live-sandbox` or `stage0-1-walkthrough`:

```bash
# Option A: Reset only the stage0-1-walkthrough workspace to a clean checkpoint (<2s)
/workspace/workshop/scripts/checkpoint.sh goto ch4

# Option B: Full Workshop Hub & Grove Reset (<3s)
/workspace/workshop/scripts/reset-workshop.sh
```

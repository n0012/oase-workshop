# Module 07 — Troubleshooting & Validator Reference

> **Audience:** AI Platform Engineers, Developers, and Workshop Facilitators  
> **Purpose:** Exact diagnostics and one-command remedies for `oase v0.3.0` (`707e461`), `oase validate check` rejection codes, the `GA/AGY ↔ OASE` surface contract (`scion` MCP), and Dedicated GCP GPU Endpoints.

---

## 1. `oase validate check` Rejection Reference

Every Work Order (`WO-001`..`WO-008`) must pass `oase validate check <WO-ID>` before advancing to `scientifically_accepted`. Use this table to diagnose and fix validation failures:

| Code / Sub-Check | Gate | Trigger Condition | Exact Remedy |
| :--- | :--- | :--- | :--- |
| **`PROV-001`** (`MISSING_SIDECAR`) | Gate 1: Provenance | A file in `raw/<class>/` is missing its `<artifact>.meta.json` sidecar. | Re-run Phase 1 (`oase <tool> fetch/run`) or generate the sidecar via `oase_ provenance.write_meta(...)`. |
| **`PROV-002`** (`CHECKSUM_MISMATCH`) | Gate 1: Provenance | The 64-char SHA-256 hex digest in `<artifact>.meta.json` does not match the raw file bytes on disk. | Restore the unmodified raw artifact or re-run Phase 1; never hand-edit files in `raw/`. |
| **`CIT-001`** (`UNCITED_CLAIM`) | Gate 2: Citations | A numerical claim in `findings/**/*.md` has no `{source: <path> <jsonpath>}` tag (or the tag was accidentally wrapped in inline backticks `` `...` ``, which `_strip_code_spans` ignores). | Place `{source: raw/<class>/<stem>.analysis.json $.metrics.<key>}` directly after the number in plain text (space-separated, never inside backticks). |
| **`CIT-002`** (`LOCATOR_NOT_FOUND`) | Gate 2: Citations | The referenced file path or `$.metrics.<key>` JSONPath does not exist in `.analysis.json`. | Check the keys in `raw/<class>/<stem>.analysis.json` with `jq .metrics` and update the JSONPath locator. |
| **`CIT-003`** (`VALUE_MISMATCH`) | Gate 2: Citations | The number written in prose differs from the JSON value at `$.metrics.<key>` by more than `±1%` relative tolerance (`0.01`). | Update the prose number to match the exact value in `.analysis.json` (and put at most one `$` JSONPath locator per bullet line so `oase site build` does not treat paired `$` signs as inline KaTeX math). |
| **`REL-001`** (`MISSING_MANDATORY_RELAY`) | Gate 3: Relays | A relay code listed in the Work Order's `mandatory_relays` is missing from `findings/<domain>/WO-*.md` (or formatted as `[relay:code]` instead of standard format). | Include the verbatim header `**Relay: \`<code>\`**` followed by the explanation in the synthesis markdown. |
| **`THR-001`** (`THRESHOLD_VIOLATION`) | Gate 4: Governance | A candidate fails a Tier-1 threshold in `.oase/thresholds.yaml` without an explicit `STAGE_GATE_WAIVER` logged in `events.ndjson`. | Disqualify the failing candidate (e.g., `PCSK9-A02` on hERG `< 10.0 uM`) or record a signed sponsor waiver. |

---

## 2. CLI & GCP Endpoint Diagnostics (`oase doctor`)

Start by running `oase doctor --json` inside the target workspace directory:

```bash
source /scion-volumes/tools/env.sh
oase --project /workspace/stage0-1-walkthrough doctor --json | jq .
```

| Symptom / Error Message | Root Cause | Exact Remedy |
| :--- | :--- | :--- |
| `EndpointUnavailable: timed out waiting for the AF3 lock file` | `oase alphafold predict` serializes single-flight calls via `~/.cache/oase/af3.lock` (`OASE_AF3_LOCK`). Another prediction is running or a killed process left a lock. | Check `ps aux \| grep "oase alphafold predict"`. Wait for completion, pass `--deadline 3600`, or jump to `ch3` via `./scripts/checkpoint.sh jump ch3`. |
| `404 Not Found` when calling `oase alphagenome score-variant` | Calling the regional API host (`us-central1-aiplatform.googleapis.com`) instead of the Dedicated GCP Endpoint DNS (`*.prediction.vertexai.goog`). | Ensure `OASE_AG_ENDPOINT_DNS` is set to `<ENDPOINT_ID>.<REGION>-<PROJECT_NUMBER>.prediction.vertexai.goog` (see `.env.example`). |
| `CredentialError: checked the ALPHAGENOME_API_KEY environment variable` | Running `oase alphagenome ism` or passing `--backend pip` without an API key (`ism` is pip-backend-only). | Use `oase alphagenome score-variant` or `predict-interval` with `--backend vertex` (default GCP endpoint backend, uses GCE ADC), or export `ALPHAGENOME_API_KEY`. |
| `oase site build` fails looking for `katex.min.css` | `site.py` requires offline KaTeX assets under `${OASE_TOOLS_HOME}/vendor/katex/katex.min.css` (and `/scion-volumes/tools/npm/node_modules/katex/dist`). | Run `./scripts/preflight.sh` (which populates both offline KaTeX paths). |
| `PhaseContractError` during an `analyze` command | A custom or modified `analyze*` command attempted an outbound network socket connection. Phase 2 is strictly offline-latched at the root CLI tree. | Move all network/API lookups into Phase 1 (`fetch`/`run`/`predict`) and read from `raw/` in Phase 2 (`docs/tool-design-guidance.md` §3). |
| `oase h5ad` exits with code `8` (`h5py is not installed`) | `h5py` was not installed into the shared `/scion-volumes/tools/.venv`. | Run `/scion-volumes/tools/.venv/bin/pip install h5py` via `cd /workspace/tools && ./install.sh --update`. |
| `oase h5ad analyze` exits with code `2` on `--select-label "Activated stellate cell"` | By design: `oase h5ad` matches atlas labels verbatim and never guesses. DISCO's 5 cirrhosis samples use `"CFD+MGP+ fibroblast"`, `"CCL19+APOE+ fibroblast"`, `"Mesenchymal stromal cell"`, `"Pericyte"`. | Inspect the exact label vocabulary printed in the error message and pass `--select-label "CFD+MGP+ fibroblast"`. |
| `oase doctor` reports an **`env_version` partition warning** (`HOUSEKEEPING`) | `/scion-volumes/tools/` was updated mid-program, so earlier `.meta.json` sidecars carry a different `env_version` hash than newer ones. | Phase 2 `.analysis.json` files can be regenerated offline (`oase <tool> analyze <id>`); Phase 1 payloads must be re-fetched if strict single-environment comparability (`oase doctor --strict`) is required. |

---

## 3. Surface-to-OASE (`GA` & `AGY` / `scion` MCP) Troubleshooting Matrix

| Error Code / Symptom | Root Cause | Exact Remedy |
| :--- | :--- | :--- |
| `OaseHubNotConfigured` | Neither `SCION_HUB_URL` nor `~/.config/pharma_skills/config.toml` (`[oase] hub_url`) is set. | Add `[oase]\nhub_url = "https://..."` to `~/.config/pharma_skills/config.toml` or export `SCION_HUB_URL`. |
| `GCP_SA_NOT_VERIFIED` | Project GCP Service Account failed verification on `POST /api/v1/projects/{id}/gcp-service-accounts/{saId}/verify`. | Verify the SA exists in the target GCP project and has IAM permissions, then re-run `create_project`. |
| `OASE_TEMPLATES_MISSING` | Project was created via raw `scion project create` without importing the 22 OASE templates. | Run `create_project` (or `POST /api/v1/projects/{id}/import-templates`) and verify all 6 critical templates exist before starting `controller`. |
| `CONTROLLER_TEMPLATE_MISMATCH` | `controller` started before template import completed and silently fell back to `template: default`. | `bootstrap_campaign` automatically deletes the mis-templated agent and fails closed; re-run after template import passes. |
| `SEED_UPLOAD_CHECKSUM_MISMATCH` | WebDAV `PUT` was truncated (e.g., unsharded file `> 4 MB` hit proxy limit) or corrupted in transit. | Keep seed shards `<= 1.8 MB` and re-run `bootstrap_campaign` so read-back `GET` SHA-256 verification and `CHECKSUMS.json` succeed. |
| `SESSION_PROJECT_LOCKED` | Current GA/AGY session is already bound to a different Scion project (1-project-per-session rule). | Start a new GA/AGY chat session for the second project, or pass `switch_project=true` if intentionally rebinding. |
| `ONE_PROGRAM_PER_PROJECT` | Target Scion project already has `.oase-project-lock.json` bound to a different `program_slug`. | Create a new Scion project (`create_project`) for the new scientific program (1-program-per-project invariant). |
| `ESCALATION_REQUIRED` (`Exit 3`) | `surface_install.py` was invoked inside GA's read-only `nsjail` sandbox. | Re-run `python3 scripts/surface_install.py` from GA with `permissions="require_escalated"` or from a host terminal. |

---

## 4. Operational Rules & Command Cross-Reference

### Six Operational Rules for `GA`/`AGY` ↔ OASE
1. **Project Owner Initiates & Assigns (`create_project` + `bootstrap_campaign`):** Initiate new projects and campaigns via `create_project` / `bootstrap_campaign` (never bare `scion project create`) so GCP SA verification, `tools` volume mounting, team `members` assignment, and 6-template verification happen atomically.
2. **Respect the Latency & Provenance Boundary:**
   - Sub-minute exploratory question? Run it on the `GA` / `AGY` surface.
   - Decision-grade claim cited in a `DEC-###` entry or Stage Gate? Dispatch it via `request_work_order` so OASE executes Phase 1 (`.meta.json` SHA-256 sidecar) + Phase 2 (offline `.analysis.json`) + `oase validate check`.
3. **Read Direct via WebDAV (`decision_log`, `dav_read`), Write Only via Push Messages (`< 10 KB`):** Never write or edit files under `/workspace/<program-slug>/` directly from `GA`/`AGY`. Use `decision_log` and `dav_read` for reads, and `request_work_order` / `send_message` (`< 10 KB`) for writes.
4. **One Project Per Session (`SESSION_PROJECT_LOCKED`) & One Program Per Project (`ONE_PROGRAM_PER_PROJECT`):** Start a new `GA`/`AGY` session when switching projects, and create a new Scion project for each distinct drug discovery program.
5. **Use `oase coscientist ingest` for Seed Packages:** Stage the 7-part seed bundle to `/workspace/.seed/<slug>/` (`CHECKSUMS.json` last) and ingest via `oase coscientist ingest <export_file>` so all fields, citations, and debate logs are preserved.
6. **Verify `oase validate check --preflight` Before Submitting a Work Order:** Checks SHA-256 sidecars, JSON schemas, threshold citations, mandatory `**Relay: \`<code>\`**` headers, and `{source: raw/<class>/<stem>.analysis.json $.metrics.<key>}` JSONPath claims in seconds.

### Command Cross-Reference (`scion` MCP vs. `pharma-cli dde` vs. Container `oase` CLI)

| Task | From `GA` / `AGY` (`scion` MCP Tool) | From Workstation CLI (`pharma-cli dde`) | Inside OASE Agent Container (`oase` CLI) |
| :--- | :--- | :--- | :--- |
| **Create Project & Assign Team** | `scion:create_project` | `pharma-cli dde create-project --name ... --member ...` | *(Requires `UserIdentity` token)* |
| **Launch Campaign + Seed** | `scion:bootstrap_campaign` | `pharma-cli dde bootstrap-campaign ...` | `oase doctor` → `oase init /workspace/<slug>` |
| **Read Latest Decisions (`DEC-###`)** | `scion:decision_log` (`limit: 10`) | `pharma-cli dde decision-log --limit 10` | Read `program-state/decision-log.md` |
| **Read Workspace File (`L0–L4`)** | `scion:dav_read` (`path`, `head_lines`/`section`) | `pharma-cli dde dav-read <path>` | Read `/workspace/<slug>/<path>` |
| **Request New Work Order (`WO-*`)** | `scion:request_work_order` | `pharma-cli dde request-work-order ...` | `oase workorder create --from wo.json --commit` |
| **Validate Work Order** | Read via `scion:dde_finding` | `pharma-cli dde finding --wo WO-004` | `oase validate check WO-004` |
| **Build & Export Portal** | Request `project-curator` via `send_message` | Download `_site/<slug>-site.zip` via WebDAV | `oase site build && oase site validate && oase site export` |

---

## 5. Recovering a Corrupted Workspace (`<3 Seconds`)

If a participant accidentally deletes files under `.oase/control/` or corrupts a work order:

```bash
# Option A: Restore any clean checkpoint (<2s)
./scripts/checkpoint.sh jump ch4

# Option B: Full Workshop Hub & Workspace Reset (<3s)
./scripts/reset-workshop.sh
```

# Module 00 — GCP Prerequisites, Surface Connectivity & Project Provisioning (`ch0`)

> **Duration:** 15 Minutes (`0:00 – 0:15`)  
> **Audience:** Discovery Scientists, Computational Biologists, and Platform Engineers  
> **Goal:** Verify GCP endpoints and shared tool binaries (`oase doctor`), connect interactive surfaces (**Gemini Agent (`GA`)**, **Antigravity (`AGY`)**, or **Jetski**) via the **`scion` MCP server (15 tools)**, and provision the shared workshop project (`create_project`) with assigned R&D team roles (`project-member`).

---

## 1. How R&D Team Roles Map to OASE Agent Templates

OASE is designed for multi-user, multi-agent team science. Each workshop participant operates their domain surface alongside OASE's 22 container templates:

| Workshop Participant Role | Surface & Viewers Used | Counterpart OASE Agent Templates | Workshop Responsibilities |
|---|---|---|---|
| **1. Project Owner / Program Lead** | `GA` or `AGY` (`UserIdentity` token) | `research-operations-controller` (`controller`), `science-program-lead`, `<slug>-head-of-discovery`, `bootstrapper` | Runs `create_project`, assigns team members (`role: "project-member"`), confirms the `A2UI_INPUT_REQUIRED` campaign initiation card (`bootstrap_campaign`), reviews `DEC-###` entries, and issues `STAGE_GATE_DECISION` verdicts. |
| **2. Target & Computational Biologist** | `GA` / `AGY` + `constraint-viewer.html`, `expression-viewer.html` | `computational-biologist`, `hypex-supervisor`, `scientific-reviewer` | Audits Stage 0 seed ingestion (`oase coscientist`), escalates Stage 1 work orders (`WO-002`, `WO-003`) via `request_work_order`, and inspects `oase genetics` (gnomAD), `oase gwas` (OpenTargets/ClinVar), `oase gtex`, `oase h5ad`, and **AlphaGenome on GCP** (`oase alphagenome`). |
| **3. Structural Biologist & Computational Chemist** | `GA` / `AGY` + `plddt-viewer.html`, `pae-viewer.html`, `pockets-viewer.html`, `docking-viewer.html` | `structural-biologist`, `computational-chemist` | Commissions and audits Stage 2 work orders (`WO-004`, `WO-005`): `oase alphafold fetch/analyze`, live **AlphaFold 3 on GCP** ligand co-folding (`oase alphafold predict --template ligand`), `fpocket` (`oase pocket`), and 3-phase AutoDock Vina + Meeko docking (`oase docking`). |
| **4. Medicinal Chemist** | `GA` / `AGY` + `brics-viewer.html`, `admet-viewer.html`, `sdf-viewer.html` | `medicinal-chemist` | Injects medicinal chemistry constraints (`MW <= 500`, `cLogP <= 3.5`, `TPSA 75–110 Å²`, `0` alerts, `<= 5` steps) via `request_work_order` (`WO-006`) and audits `oase mmp` (BRICS), `oase admet` (`OASE-PCSK9-014`), and `oase retro` (ASKCOS). |
| **5. DMPK, Safety & Regulatory Lead** | `GA` / `AGY` + `_site/index.html` (28-page portal) | `admet-dmpk-scientist`, `preclinical-toxicologist`, `regulatory-scientist`, `finding-validator`, `project-curator` | Audits Stage 4 work orders (`WO-007`, `WO-008`): `oase pk` (`ingest → nca → scale → analyze` for 70 kg human QD oral dosing), `oase trials`, `oase faers`, `oase dossier export`, and `oase site build && oase site export`. |

---

## 2. GCP Runtime & Shared Volume Prerequisites

OASE runs inside a **Scion Hub** VM (`n2-standard-8`, Ubuntu 22.04/24.04 LTS, 250 GB SSD) or GKE cluster where agent containers mount a shared read-only tools volume (`/scion-volumes/tools/`). Authentication to Google Cloud services uses **Application Default Credentials (`google.auth.default()`)** from the GCE metadata server—no service account JSON key files are copied into containers.

| Dependency | Auth Mechanism | Environment Variables | OASE Command(s) |
|---|---|---|---|
| **Frontier LLM Harnesses on GCP (`Gemini 4`, `Claude`, `OpenAI`)** | GCE Metadata ADC (`roles/aiplatform.user`) / Scion Harness Config (`small\|medium\|large\|extra-large`) | `PROJECT_ID`, `REGION` | Scion Agent Harnesses (`controller`, `science-program-lead`, `head-of-discovery`, `scientific-reviewer`, `hypex-*`, specialists) |
| **Dedicated GCP AlphaFold 3 GPU Endpoint** | GCE Metadata ADC (`aiplatform.init()`) | `OASE_AF3_PROJECT`, `OASE_AF3_REGION`, `OASE_AF3_ENDPOINT_NAME`, `OASE_AF3_LOCK` | `oase alphafold predict --input <json>` |
| **Dedicated GCP AlphaGenome GPU Endpoint** | GCE Metadata ADC (`_access_token()`) | `OASE_AG_PROJECT`, `OASE_AG_REGION`, `OASE_AG_ENDPOINT_ID`, `OASE_AG_ENDPOINT_DNS` | `oase alphagenome score-variant`, `oase alphagenome predict-interval` (`--backend vertex`) |
| **BigQuery PubMed Corpus** | GCE Metadata ADC (`roles/bigquery.jobUser`) | `OASE_PUBMED_BQ_DATASET` | `oase pubmed-bq search`, `oase pubmed-bq analyze` |
| **Public Scientific Databases** (`AFDB`, `UniProt`, `gnomAD`, `GTEx`, `HPA`, `CELLxGENE`, `DISCO`, `Europe PMC`, `ClinicalTrials.gov`) | Unauthenticated HTTPS (governed by `oase/core/qps.py` rate limiters) | `OASE_PACE_DIR` | All other `oase <tool> fetch` / `search` commands |

---

## 3. Exercise 0.1 — Verify Surface Connectivity & Environment Health

From a terminal on your workstation (or inside `GA`/`AGY`), verify Hub connectivity and the OASE tool environment:

```bash
# 1. Verify Scion Hub connectivity via the scion MCP server:
python3 tools/scion_mcp_server.py --cli hub_status --args '{}'

# 2. Inside the OASE container / sandbox VM, verify all 62 CLI tool groups and 51/51 Phase-2 offline latches:
source /scion-volumes/tools/env.sh
oase doctor --json
```

**What to Check in `oase doctor --json`:**
- `"verdict": "PROCEED"` (zero `"fail"` items).
- `"phase_two_offline_latch": "51/51 verified"` (confirms every Phase-2 `analyze` command is wrapped by `enforce_phase_two`).
- Compiled binaries on `/scion-volumes/tools`: `fpocket`, `vina`, `mk_prepare_receptor.py`, `mk_prepare_ligand.py`, `hypex`, `elo`, `prox`, and offline KaTeX (`vendor/katex/katex.min.css`).

---

## 4. Exercise 0.2 — Project Owner Creates the Project & Assigns the Team (`create_project`)

The **Project Owner** initiates project creation from Gemini Agent (`GA`) or Antigravity / Jetski (`AGY`) using their `UserIdentity` token (`scion auth login`). Do not use bare `scion project create` alone, as it leaves `sharedDirs: null` and imports `0` project-scoped templates. (For full REST API details, see [Surface Connectivity Reference](surface-connectivity-reference.md).)

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
      "franchise": "cardiometabolic-ascvd"
    }
  }
}
```

**What `create_project` Verifies Atomically:**
1. Creates the Scion project (`POST /api/v1/projects`).
2. Registers and verifies the GCP Service Account (`verified == true`), sets `defaultGCPIdentityMode: "assign"`, `defaultHarnessConfig`, and `defaultModel` (`small | medium | large | extra-large`), and assigns each email in `members` (`role: "project-member"`).
3. Mounts the shared `tools` volume (`readOnly: false, inWorkspace: false`).
4. Imports the 22 OASE templates and verifies all 6 critical templates by exact name (`research-operations-controller`, `science-program-lead`, `bootstrapper`, `head-of-discovery`, `finding-validator`, `hypex-supervisor`), failing closed with `OASE_TEMPLATES_MISSING` if any is absent.

Each assigned scientist then lists projects (`scion:list_projects`) and binds their session (`SESSION_PROJECT_LOCKED`) by calling `decision_log` or `dav_list` with `"project_id": "<oral-pcsk9-ascvd-uuid>"`.

---

**Next Step:** Proceed to [Module 01 — 4-Tier Architecture, Multi-Model Harnesses & Stage 0 Initiation (`ch1`)](01-tour-the-grove.md).

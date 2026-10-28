# Module 00 — GCP & Vertex AI Prerequisites

> **Audience:** AI Platform Engineers, Cloud Architects, and Workshop Facilitators  
> **Goal:** Provision or verify a Google Cloud environment capable of running a multi-user **Scion Hub** and the **GCP-OASE (`oase v0.3.0`)** tool suite with **Vertex AI Gemini 4**, **Claude Partner Models**, **AlphaFold 3**, **AlphaGenome**, and **BigQuery**.

---

## 1. Architecture & Access Overview

GCP-OASE runs inside a **Scion Hub** VM (`n2-standard-8`, Ubuntu 22.04/24.04 LTS, 250 GB SSD) or GKE cluster where agent containers mount a shared read-only tools volume (`/scion-volumes/tools/`).

As documented in `docs/operating-environment.md`, OASE authenticates to Google Cloud services primarily via **Application Default Credentials (`google.auth.default()`)** resolved from the GCE VM's Workload Identity / service account metadata server—meaning **no static service account JSON key files need to be copied into agent containers**.

| Dependency | Auth Mechanism | Environment Variables | OASE Command(s) |
|---|---|---|---|
| **Vertex AI Gemini 4 & Claude Partner Models** | GCE Metadata ADC (`roles/aiplatform.user`) | `PROJECT_ID`, `REGION` | Scion Agent Harnesses (`controller`, `science-program-lead`, `scientific-reviewer`, `hypex-*`, specialists) |
| **Vertex AI AlphaFold 3 Dedicated Endpoint** | GCE Metadata ADC (`aiplatform.init()`) | `OASE_AF3_PROJECT`, `OASE_AF3_REGION`, `OASE_AF3_ENDPOINT_NAME` | `oase alphafold predict --input <json>` |
| **Vertex AI AlphaGenome Dedicated Endpoint** | GCE Metadata ADC (`_access_token()`) | `OASE_AG_PROJECT`, `OASE_AG_REGION`, `OASE_AG_ENDPOINT_ID`, `OASE_AG_ENDPOINT_DNS` | `oase alphagenome score-variant`, `oase alphagenome predict-interval` (`--backend vertex`) |
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

# 2. Verify Vertex AI Claude Partner Models & Gemini 4 are enabled in Model Garden
# (For Claude on Vertex AI, ensure data sharing is accepted per location and
#  constraints/vertexai.allowedPartnerModelFeatures permits your target models.)
```

The GCE VM service account (or developer ADC identity) requires:
- `roles/aiplatform.user` — Invoke Gemini 4, Claude Partner Models, AlphaFold 3 Dedicated Endpoint, and AlphaGenome Dedicated Endpoint.
- `roles/bigquery.jobUser` + `roles/bigquery.dataViewer` — Execute `oase pubmed-bq search` queries.
- `roles/storage.objectUser` — Read/write staging payloads and exported site archives.

---

## 3. Verifying Vertex AI AlphaFold 3 & AlphaGenome Endpoints

Dedicated Vertex AI endpoints (`AlphaFold 3` on `g2-standard-12` / `a2-ultragpu-1g` and `AlphaGenome`) use dedicated prediction DNS hostnames (`*.prediction.vertexai.goog`) rather than the regional `us-central1-aiplatform.googleapis.com` host.

```bash
# Verify AlphaFold 3 Dedicated Endpoint is deployed and visible
gcloud ai endpoints list \
  --project="${OASE_AF3_PROJECT}" \
  --region="${OASE_AF3_REGION}" \
  --filter="displayName:\"${OASE_AF3_ENDPOINT_NAME}\""

# Verify AlphaGenome Dedicated Endpoint is deployed and visible
gcloud ai endpoints describe "${OASE_AG_ENDPOINT_ID}" \
  --project="${OASE_AG_PROJECT}" \
  --region="${OASE_AG_REGION}" \
  --format="value(dedicatedEndpointDns)"
```

> [!IMPORTANT]
> **Single-Flight Serialization on AlphaFold 3:** `oase alphafold predict` acquires an exclusive file lock (`OASE_AF3_LOCK`, default `~/.cache/oase/af3.lock`) before calling the Vertex endpoint so concurrent agents on the same host queue cleanly rather than colliding with `already working on a prediction`.

---

## 4. Provisioning the Shared Tools Volume (`/scion-volumes/tools/`)

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
Because `oase site build` compiles self-contained 28-page evidence portals completely offline, it checks for KaTeX assets at `/scion-volumes/tools/vendor/katex/katex.min.css`. Verify they are present:

```bash
ls -lh /scion-volumes/tools/vendor/katex/katex.min.css
```

---

## 5. Running the Workshop Pre-Flight Check

Before starting Module 01, run `oase doctor` against the `live-sandbox` project:

```bash
source /scion-volumes/tools/env.sh
OASE_PROJECT=/workspace/live-sandbox oase doctor
```

Expected verdict: **`PROCEED`** (zero `"fail"` checks; `"warn"` items such as an unset `ALPHAGENOME_API_KEY` when using the Vertex backend are informational and non-blocking).

---

**Next Step:** Proceed to [Module 01 — Tour the Grove](01-tour-the-grove.md).

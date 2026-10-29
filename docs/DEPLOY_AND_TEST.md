# Turnkey Deployment, Execution & Verification Guide (`DEPLOY_AND_TEST.md`)

This runbook documents every step required to deploy, execute, and verify the **`pcsk9-oral`** GCP-OASE 7-Chapter Pilot across **four clear execution tiers**—from a 60-second local CPU/API run on any Linux workstation up to the full Cloud Run + Scion Hub stack, live Vertex AI GPU endpoints (`AlphaFold 3` & `AlphaGenome`), and full `Gemini 3.8 Live Avatar` video remastering.

> **Looking for what ran live vs. what was pre-staged in checkpoints?** See [**`docs/DATA_PROVENANCE.md`**](DATA_PROVENANCE.md) and inspect the committed un-mocked outputs directly in [**`live-results/pcsk9-oral/`**](../live-results/pcsk9-oral/).

---

## Tier 1 — Local CPU & Public API End-to-End Test (~60s, Zero Cloud Infra Required)

Runs all **11 live CPU/API `oase v0.3.0` tools** (`doctor`, `coscientist`, `genetics` / `gnomAD`, `gwas` / `OpenTargets`, `gtex`, `expression` / `HPA`, `alphafold fetch` / `AFDB`, `pocket` / `fpocket 4.2.2`, `docking` / `AutoDock Vina 1.2.5`, `compound` / `RDKit`, `admet`, and `trials` / `ClinicalTrials.gov v2`), verifies all 8 campaign work orders (`WO-001`..`WO-008`), runs 4 adversarial tamper drills, and compiles the 32-page Evidence Portal (`_site/`).

### Prerequisites
- Linux `x86_64` with `python3` (`3.11+`), `gcc`/`g++`, `make`, `curl`, `git`, and [`uv`](https://docs.astral.sh/uv/)
- Outbound HTTPS access to `gnomad.broadinstitute.org`, `api.platform.opentargets.org`, `gtexportal.org`, `proteinatlas.org`, `alphafold.ebi.ac.uk`, and `clinicaltrials.gov`

### Step-by-Step Commands
```bash
# 1. Verify repository hygiene and local prerequisites
./scripts/preflight.sh --check-hygiene

# 2. Compile the 7 scientific C/C++/Go binaries (vina, fpocket, rate4site, muscle, hypex, elo, prox)
#    + Python 3.11 .venv + offline KaTeX 0.16.21 (~3 min cold, ~7s cached)
OASE_TOOLS_HOME=/tmp/scion-volumes/tools ./scripts/bootstrap-oase-env.sh

# 3. Execute the full 7-chapter simulation + live AutoDock Vina 3D docking + 4 tamper drills + portal build
OASE_TOOLS_HOME=/tmp/scion-volumes/tools ./scripts/run-e2e-simulation.sh /tmp/sim-pcsk9-oral

# 4. Serve and inspect the compiled 32-page Evidence Portal & Interactive Story Arc locally
python3 -m http.server 8765 --bind 127.0.0.1 --directory /tmp/sim-pcsk9-oral/_site
# Open http://127.0.0.1:8765/chapters.html and http://127.0.0.1:8765/index.html
```

### Expected Verification Output (`exit=0`)
- **`live-runs/raw/`:** `21` Phase-1 `.meta.json` SHA-256 sidecars and `14` Phase-2 `.analysis.json` records verified (`PCSK9-A03` / `OASE-PCSK9-014` scores **`-9.6 kcal/mol`** `strong-binders-found` in `AutoDock Vina 1.2.5` with `0` critical ADMET alerts, while `PCSK9-A02` fails on 3 liabilities including `herg_liability`).
- **Mechanical Governance (`WO-001`..`WO-008`):** `8 / 8 [PASS]` across all 10 `oase validate check` gates.
- **Adversarial Negative Drills (`DRILL-01`..`DRILL-04`):** `4 / 4 [PASS - CAUGHT]` (`provenance_valid`, `source_tags_resolve`, `relay_coverage`, `analysis_citations`).
- **Static Portal (`_site/`):** `30` OASE evidence pages + `chapters.html` + `plan.html` + `pcsk9-oral-site.zip`.

---

## Tier 2 — Full GCP Cloud Pilot Stack (Scion Hub VM + 5 Personas + Cloud Run Story Arc Cockpit)

Deploys the live interactive team environment: 8 parallel Scion Hub projects (`ch0`..`ch7`), 17 running multi-model agent containers, `<250 ms` FastAPI state reset daemon (`:8780`), and the IAP-protected `oase-story-arc` Cloud Run Presenter Cockpit.

### Prerequisites
1. **Google Cloud Organization & Cloud Identity Domain (`WORKSHOP_DOMAIN`):**
   Create 5 dedicated workshop scientist accounts in Google Admin Console (`admin.google.com/ac/users`) with `Ask user to change password` disabled:
   - `oase-sarah@<WORKSHOP_DOMAIN>` (*Dr. Sarah Chen — Program Lead*)
   - `oase-marcus@<WORKSHOP_DOMAIN>` (*Dr. Marcus Vance — Computational Biologist*)
   - `oase-elena@<WORKSHOP_DOMAIN>` (*Dr. Elena Rostova — Structural Biologist*)
   - `oase-raj@<WORKSHOP_DOMAIN>` (*Dr. Raj Patel — Medicinal Chemist*)
   - `oase-claire@<WORKSHOP_DOMAIN>` (*Dr. Claire Moreau — DMPK & Safety Lead*)
2. **Scion Hub GCE VM (`scion-hub-oase`):**
   A Linux GCE VM in `ZONE` (`us-central1-c`) running **Google Cloud Scion (`v0.1.50+`)** under user `scion` (`/home/scion/.scion/hub.db`) fronted by a Cloud Run IAP proxy (`scion-hub-oase-iap-proxy`).

### Step-by-Step Deployment Commands
```bash
# 1. Provision or reconcile the isolated GCP project + least-privilege agent service account
python3 scripts/provision-gcp-project.py \
  --project-id <YOUR_GCP_PROJECT_ID> \
  --org-id <YOUR_GCP_ORG_ID>

# 2. Configure .env with your 4 core deployment variables
cp .env.example .env
# Edit .env:
#   GCP_PROJECT_ID="<YOUR_GCP_PROJECT_ID>"
#   WORKSHOP_DOMAIN="<YOUR_CLOUD_IDENTITY_DOMAIN>"
#   REGION="us-central1"
#   GCS_BUNDLE_BUCKET="<YOUR_GCP_PROJECT_ID>-bundles"
#   SCION_HUB_URL="https://<YOUR_SCION_IAP_CLOUD_RUN_URL>"

# 3. Validate configuration & repo hygiene in dry-run mode (<2s)
./scripts/deploy-pilot-stack.sh --dry-run

# 4. Deploy the complete 8-checkpoint stack (GCS bucket, VPC firewall, ch0..ch7 Hub projects,
#    systemd oase-state-controller :8780, Cloud Run oase-story-arc, and 5-persona IAP bindings)
./scripts/deploy-pilot-stack.sh

# 5. (Optional) Sync matched 512px & compact 40px Gemini 3.8 portraits into Scion Hub SQLite
python3 scripts/sync-persona-portraits.py --update-hub-db

# 6. Run automated Playwright E2E verification against the deployed Cloud Run Cockpit
python3 scripts/verify-pilot-stack.py \
  --cockpit-url "https://<YOUR_STORY_ARC_CLOUD_RUN_URL>" \
  --profile-dir /path/to/authenticated-chrome-profile
```

---

## Tier 3 — Live Vertex AI GPU Compute (`AlphaFold 3` Co-Folding & `AlphaGenome` Variant Scoring)

In the standard 150-minute workshop (`Tier 1` & `Tier 2`), `WO-004` (`AlphaFold 3` co-fold) and `WO-003` (`AlphaGenome` `rs2479409` 1 Mb regulatory variant scoring) use pre-staged checkpoint fixtures so attendees do not wait on GPU provisioning or 15-minute folding jobs. To execute **both models live on dedicated GPUs**:

### 1. Deploy Vertex AI Model Garden Dedicated Endpoints
1. In **Google Cloud Console → Vertex AI → Model Garden**, deploy:
   - **AlphaFold 3** onto an `a2-ultragpu-1g` (`A100 80GB`) or `a3-highgpu-1g` (`H100 80GB`) Dedicated Endpoint in `us-central1`.
   - **AlphaGenome** onto a Dedicated Endpoint in `us-central1` (or obtain an `ALPHAGENOME_API_KEY` for `--backend pip`).
2. Export the endpoint variables in `.env`:
   ```bash
   export OASE_AF3_PROJECT="<YOUR_GCP_PROJECT_ID>"
   export OASE_AF3_REGION="us-central1"
   export OASE_AF3_ENDPOINT_NAME="<YOUR_AF3_ENDPOINT_RESOURCE_NAME>"

   # Option A: Vertex AI Dedicated Endpoint
   export OASE_AG_PROJECT="<YOUR_GCP_PROJECT_ID>"
   export OASE_AG_REGION="us-central1"
   export OASE_AG_ENDPOINT_ID="<YOUR_ALPHAGENOME_ENDPOINT_ID>"
   export OASE_AG_ENDPOINT_DNS="<ENDPOINT_ID>.us-central1-<PROJECT_NUMBER>.prediction.vertexai.goog"

   # Option B: AlphaGenome API Key backend
   # export ALPHAGENOME_API_KEY="<YOUR_API_KEY>"
   ```

### 2. Run the Full Simulation with `--run-gpu-endpoints`
```bash
OASE_TOOLS_HOME=/tmp/scion-volumes/tools \
  ./scripts/run-e2e-simulation.sh /tmp/sim-pcsk9-oral-gpu --run-gpu-endpoints
```
This executes:
- `oase alphagenome score-variant --chrom chr1 --pos 55039974 --ref G --alt T --window 1048576 --output-type RNA_SEQ --output-type ATAC --output-type CAGE --scorer geneMask --strand +` + `oase alphagenome analyze`
- `oase alphafold predict --input inputs/pcsk9_ic001_af3_ligand.json` (canonical 692-aa `PCSK9` `Q8NBP7` + `OASE-PCSK9-014` SMILES) + `oase alphafold analyze-prediction`

---

## Tier 4 — Re-Synthesizing `Gemini 3.8 Live Avatars` & Remastering All 7 Squadron Videos

To regenerate all 21 native `gemini-3.8-live` (`BidiGenerateContent`) human scientist video clips, all 7 `gemini-3.8-flash-tts` specialist AI wingman voiceovers, and re-record/master `chapter-01..07.mp4` + `full-pilot-walkthrough.mp4` against live Scion Hub browser sessions:

```bash
# 1. Ensure 5 Chrome persona profiles (persona-sarah .. persona-claire) are signed into Scion Hub IAP
#    under CHROME_PROFILES_DIR (default: /tmp/oase-chrome-profiles)

# 2. Run the end-to-end avatar synthesis + live Scion capture + ffmpeg HUD mastering + GCS upload pipeline
./scripts/remaster-pilot-videos.sh

# Or re-master from cached avatar clips without re-calling Vertex Live API:
./scripts/remaster-pilot-videos.sh --skip-avatar-synthesis

# 3. Rebuild static site templates (chapters.html + plan.html) with updated video durations/manifests
python3 scripts/build-chapter-portal.py
```

All prompts used during synthesis and Grove agent execution are version-controlled in [**`prompts/`**](../prompts/).

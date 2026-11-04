# Data & Compute Provenance Audit: What Ran Live vs. What Was Seeded (`pcsk9-oral`)

This document provides an explicit, artifact-by-artifact accounting of **what executed live against real APIs, compiled binaries, and GCP model endpoints** versus **what was pre-staged as deterministic JSON fixtures** across `checkpoints/ch0..ch7` and `live-results/pcsk9-oral/`.

---

## 1. Executive Summary (Direct Answer)

1. **Did `AlphaFold 3` (`oase alphafold predict`) and `AlphaGenome` (`oase alphagenome score-variant`) run live on the sandbox GCP project?**
   - **No.** In `checkpoints/ch2..ch7`, the `AlphaFold 3` ligand co-fold summary (`raw/structures/pcsk9_ic001_af3_ligand_summary.json`, `ipTM = 0.84`) and the `AlphaGenome` variant score (`raw/genomics/chr1_55039974_G_T.json`, `rs2479409` liver quantile `0.984`) are **pre-staged reference fixtures** stamped with valid `.meta.json` SHA-256 sidecars and `.analysis.json` threshold evaluations.
   - **Why:** `oase alphafold predict` and `oase alphagenome score-variant --backend vertex` call **Vertex AI Model Garden Dedicated GPU Endpoints** (`A100`/`H100` single-flight endpoints configured via `OASE_AF3_*` and `OASE_AG_*`), which are not provisioned by default on a lightweight CPU-only workshop sandbox project. Section 3 below provides the exact commands and checked-in input file ([`inputs/pcsk9_ic001_af3_ligand.json`](../inputs/pcsk9_ic001_af3_ligand.json)) to execute both jobs live whenever dedicated GPU endpoints (or `ALPHAGENOME_API_KEY`) are enabled.
2. **Which scientific tools and cloud components DID run 100% live (and where can you inspect their real outputs)?**
   - **11 Real `oase v0.3.0` Phase-1 + Phase-2 CLI Tool Runs** execute live in [`scripts/run-e2e-simulation.sh`](../scripts/run-e2e-simulation.sh), and their real, un-edited outputs are committed in **[`live-results/pcsk9-oral/`](../live-results/pcsk9-oral/)** for direct inspection:
     - **Public Human Genetics & Multi-Omics APIs:** `gnomAD v4` GraphQL (`oase genetics`), `OpenTargets v4` GraphQL (`oase gwas`), `GTEx v8` REST (`oase gtex`), `Human Protein Atlas` (`oase expression`), `AlphaFold Protein Structure Database` (`oase alphafold fetch Q8NBP7` — full `612 KB` mmCIF + `1.13 MB` PAE matrix), and `ClinicalTrials.gov v2` (`oase trials`).
     - **Compiled Local C/C++ & Cheminformatics Binaries:** `fpocket 4.2.2` (`oase pocket` — 48 real 3D cavities detected on `AF-Q8NBP7-F1.cif`), `Meeko` + `AutoDock Vina 1.2.5` (`oase docking prepare` + `oase docking run` — real 3D `.poses.pdbqt` docking of `PCSK9-A02` and `PCSK9-A03` into Pocket #1), `RDKit` (`oase compound` descriptors, Lipinski/PAINS/Brenk alerts, SA score), and `oase admet` (Aronov 2005 `hERG` SMARTS rule disqualifying `PCSK9-A02` at `cLogP = 5.09` while clearing `PCSK9-A03` at `cLogP = 3.01`).
     - **Mechanical Governance & Portal Compiler:** `oase doctor` (`7/7` compiled binaries, `36/36` threshold schemas), `oase validate check` (`8/8` Work Orders `PASS` + `4/4` negative tamper drills caught with `exit=1`), and `oase site build` (`30` static HTML pages + `chapters.html` + `plan.html`).
   - **Live Cloud Infrastructure, Multi-Model Agents & `Gemini 3.8` Synthesis:**
     - **Scion Hub (`v0.1.50`) on GCE + Cloud Run IAP:** 8 real Scion Hub projects (`00-pcsk9-initial-seed`..`07-pcsk9-mission-closeout`), 5 real Cloud Identity scientist accounts (`oase-sarah`..`oase-claire`), `17` running Docker agent containers (`Gemini`, `Claude`, `OpenAI`), and `<250 ms` FastAPI Git+SQLite resets.
     - **Native `Gemini 3.8` Audio/Video Synthesis:** All 21 scientist video PiP turns rendered live via `gemini-3.8-live` (`us-central1` `BidiGenerateContent`) and all 7 specialist AI wingman turns rendered live via `gemini-3.8-flash-tts`.

---

## 2. Artifact-by-Artifact Provenance Matrix (`WO-001` .. `WO-008`)

| Stage / Work Order | Domain / Tool | `checkpoints/ch1..ch7` File (Fast Workshop Snapshot) | Real Live Execution in `live-results/pcsk9-oral/` (`run-e2e-simulation.sh`) | Provenance Classification |
| :--- | :--- | :--- | :--- | :--- |
| **`WO-001`**<br>Stage 0 Seed | `oase coscientist` | `checkpoints/ch0/seed/pcsk9-oral/coscientist-export.json` (`IC-001` Elo `1642.5` vs `IC-002` `1588.0`) | `oase coscientist ingest` + `analyze` runs live on the seed (`clear-leader`, `+54` Elo margin) | **Seeded Upstream Export + Live OASE Ingest/Analyze** (represents external Co-Scientist Mode 1 handoff) |
| **`WO-002`**<br>Stage 1 Genetics | `oase genetics`<br>(`gnomAD`) | Compact fixture `PCSK9_gnomad.json` (`pLI = 0.0001`, `LOEUF = 0.89`, `LOF_TOLERANT`) | **100% Live API:** `PCSK9.gnomad-constraint.json` (`pLI = 2.77e-18`, `LOEUF = 1.144`, `LOF_TOLERANT`) | **Live Executed** (public `gnomAD` GraphQL API) |
| **`WO-002`**<br>Stage 1 GWAS | `oase gwas`<br>(`OpenTargets`) | Compact fixture `PCSK9_opentargets.json` (FH score `0.96`) | **100% Live API:** `pcsk9.gwas-opentargets.analysis.json` (`ASSOCIATIONS_FOUND`, overall `0.86`, clinical `0.97`) | **Live Executed** (public `OpenTargets v4` GraphQL API) |
| **`WO-002`**<br>Stage 1 Expression | `oase gtex` &<br>`oase expression` | Compact fixture `gtex/PCSK9.json` (`184.2 TPM`, `tau = 0.93`) | **100% Live API:** `ENSG00000169174.10.gtex.json` & HPA `ENSG00000169174.hpa.json` (liver `47.5 nTPM` across 50 tissues) | **Live Executed** (`GTEx` & `Human Protein Atlas` APIs) |
| **`WO-003`**<br>Stage 1 Variant | `oase alphagenome`<br>(`rs2479409`) | Seeded fixture `chr1_55039974_G_T.json` (hepatocyte quantile `0.984`, `LFC = -0.24`) | Optional `--run-gpu-endpoints` (`oase alphagenome score-variant`) | **Seeded Fixture by Default** (requires Vertex AlphaGenome GPU endpoint or `ALPHAGENOME_API_KEY`; see §3) |
| **`WO-004`**<br>Stage 2 Structure | `oase alphafold` | `fetch` monomer (`AF-Q8NBP7-F1`) + **seeded AF3 co-fold fixture** `pcsk9_ic001_af3_ligand_summary.json` (`ipTM = 0.84`) | **100% Live AFDB Monomer:** `AF-Q8NBP7-F1.cif` (`612 KB`, `pLDDT = 85.19`) + optional `--run-gpu-endpoints` for AF3 co-fold | **Monomer Live Executed · Ligand Co-Fold Seeded by Default** (AF3 co-fold requires Vertex Dedicated GPU endpoint; see §3) |
| **`WO-004`**<br>Stage 2 Pockets | `oase pocket`<br>(`fpocket 4.2.2`) | Compact fixture `Q8NBP7_pockets.json` (`Pocket #1` groove `0.68` vs flat `EGF-A` `0.24`) | **100% Live C Binary:** `AF-Q8NBP7-F1.pockets.json` (`48` real 3D pockets on `Q8NBP7`, top druggability `0.788`) | **Live Executed** (compiled static `fpocket 4.2.2`) |
| **`WO-005`**<br>Stage 2 Docking | `oase docking`<br>(`Vina 1.2.5`) | Compact summary fixture `pcsk9_pocket1_vina.json` (`-9.4 kcal/mol` series table) | **100% Live 3D Docking:** `oase docking prepare` (`Meeko` PDBQT + gridbox) + `oase docking run` (`AutoDock Vina 1.2.5` 9 poses/ligand in `live-results/pcsk9-oral/docking/`: **`PCSK9-A03` `-9.6 kcal/mol` `strong-binders-found`** vs `PCSK9-A02` `-8.2 kcal/mol`) | **Live Executed in `live-results/`** (checkpoints keep compact summary fixture for fast git checkout) |
| **`WO-006`**<br>Stage 3 ADMET | `oase compound` &<br>`oase admet` | Series summary `pcsk9_ic001_series_admet.json` (`PCSK9-A02` disqualified; `OASE-PCSK9-014` clean) | **100% Live RDKit + SMARTS:** `pcsk9-a02.analysis.json` (`cLogP = 5.09`, `3` liabilities incl. `herg_liability`) vs `pcsk9-a03.analysis.json` (`cLogP = 3.01`, `0` liabilities) | **Live Executed** (`RDKit` + `admet-endpoints@1.0`) |
| **`WO-007`**<br>Stage 4 Human PK | `oase pk` | Seeded Wet-Lab bridge fixture `oase_pcsk9_014_scaled_pk.json` (`F = 52%`, `t1/2 = 14.8 h`, `40 mg QD`) | Validated via `oase validate check WO-007` | **Seeded Wet-Lab / CRO Bridge Fixture by Design** (in vivo Sprague-Dawley rat & Beagle dog PK cannot be computed *in silico* without wet-lab assay data) |
| **`WO-008`**<br>Stage 4 Dossier | `oase trials` &<br>`oase site build` | Compact fixture `pcsk9_hypercholesterolemia_trials.json` + 30-page `_site/` | **100% Live API & Compiler:** `oase trials search "PCSK9 hypercholesterolemia"` (`ClinicalTrials.gov v2`) + `oase site build` | **Live Executed** (`ClinicalTrials.gov` API v2 + static site compiler) |

> **Why `checkpoints/ch1..ch7` and `live-results/pcsk9-oral/` both exist:**  
> Notice that some quantitative numbers differ slightly between the **pre-staged workshop checkpoints** (e.g., `fpocket` Pocket #1 `0.68` on the co-folded groove vs. `0.788` on the live apo `AF-Q8NBP7-F1.cif` monomer; `gnomAD` `LOEUF = 0.89` in the frozen v4.0 snapshot vs. `1.144` from the live API). Keeping `checkpoints/ch0..ch7` frozen guarantees deterministic `<250 ms` workshop resets and 100% reproducible stage-gate citations even offline, while `live-results/pcsk9-oral/` proves the real compiled C/Python binaries and live APIs execute cleanly end-to-end.

---

## 3. Running Live `AlphaFold 3` & `AlphaGenome` Jobs on GCP GPUs

When you want to replace the two GPU-dependent fixtures (`WO-003` `AlphaGenome` and `WO-004` `AlphaFold 3` co-fold) with **real live GPU predictions** in your Google Cloud project:

### Prerequisites (Vertex AI Model Garden Dedicated Endpoints)
1. **AlphaFold 3 Dedicated Endpoint (`A100 80GB` or `H100 80GB`):**
   Deploy **AlphaFold 3** from **Vertex AI Model Garden** into your project (default display name: `"AlphaFold 3 Dedicated Endpoint"`). Ensure the caller (`gcloud` user or `oase-agent-sa@<project>.iam.gserviceaccount.com`) has `roles/aiplatform.user`.
2. **AlphaGenome Endpoint (Vertex Dedicated Endpoint OR GDM Science API Key):**
   - **Option A (`--backend vertex` — VPC-native, no API key):** Deploy **AlphaGenome** from Vertex AI Model Garden onto a dedicated endpoint (`mg-endpoint-...`) and note its endpoint ID and project number.
   - **Option B (`--backend pip` — zero GPU provisioning):** Export `ALPHAGENOME_API_KEY="<your-key>"` (`gdmscience.googleapis.com` with `alphagenome>=0.6.1` installed in `OASE_TOOLS_HOME/.venv`).

### Execute Both Live GPU Jobs
```bash
# 1. Load the compiled OASE v0.3.0 toolchain
source "${OASE_TOOLS_HOME:-/tmp/scion-volumes/tools}/env.sh"
export OASE_PROJECT="/tmp/sim-pcsk9-oral/live-runs"

# 2. Configure your GCP GPU endpoint variables
export OASE_AF3_PROJECT="<your-gcp-project-id>"
export OASE_AF3_REGION="us-central1"
export OASE_AF3_ENDPOINT_NAME="AlphaFold 3 Dedicated Endpoint"

export OASE_AG_PROJECT="<your-gcp-project-id>"
export OASE_AG_REGION="us-central1"
export OASE_AG_ENDPOINT_ID="mg-endpoint-<your-endpoint-uuid>"
export OASE_AG_ENDPOINT_DNS="${OASE_AG_ENDPOINT_ID}.${OASE_AG_REGION}-<your-project-number>.prediction.vertexai.goog"

# 3A. Run LIVE AlphaFold 3 protein-ligand co-folding (PCSK9 Q8NBP7 + OASE-PCSK9-014 SMILES)
export OASE_WORK_ORDER="WO-004"
oase alphafold predict \
  --input "$(pwd)/inputs/pcsk9_ic001_af3_ligand.json" \
  --deadline 1800
oase alphafold analyze-prediction \
  raw/structures/pcsk9_q8nbp7_oase_pcsk9_014_cofold.summary.json

# 3B. Run LIVE AlphaGenome 1 Mb regulatory variant scoring (rs2479409: chr1:55039974:G>T)
export OASE_WORK_ORDER="WO-003"
oase alphagenome score-variant \
  --chrom chr1 \
  --pos 55039974 \
  --ref G \
  --alt T \
  --strand "-" \
  --organism HOMO_SAPIENS \
  --window 1048576 \
  --output-type RNA_SEQ \
  --output-type DNASE \
  --output-type CAGE \
  --scorer geneMask \
  --backend vertex
oase alphagenome analyze \
  raw/genomics/chr1_55039974_G_T.scores.json
```

Or run the entire CPU + GPU suite in one command via:
```bash
./scripts/run-e2e-simulation.sh /tmp/sim-pcsk9-oral --run-gpu-endpoints
```

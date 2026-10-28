# Module 09 — End-to-End Stage 0→4 Operational Training Curriculum (`pcsk9-oral` Use Case)

> **Purpose:** Practical, module-by-module operational training guide for translational R&D scientists, computational biologists, structural biologists, medicinal chemists, DMPK/safety leads, and Project Owners. This curriculum trains participants on operating **OASE (`v0.3.0`)** from **Gemini Agent (`GA`)**, **Antigravity / Jetski (`AGY`)**, the **Scion Hub UI**, and the **`oase` CLI** across **Stages 0 → 4** using our primary fast-progressing benchmark campaign: **Oral Allosteric PCSK9 Small-Molecule / Macrocyclic Peptidomimetic Inhibitor in ASCVD (`pcsk9-oral`)**—benchmarking directly against subcutaneous anti-PCSK9 mAbs (`evolocumab / Repatha`) and oral cyclic peptides (`MK-0616 / enlicitide`), with parallel command callouts for **MTA-Cooperative PRMT5 in MTAP-Deleted Solid Tumors (`prmt5-mtap`)** and **Oral NLRP3 in Cardiometabolic Inflammation (`nlrp3-oral`)**.

---

## 0. Curriculum Overview, Team Roles & 150-Minute Workshop Map

### 0.1 How Roles Map Across the R&D Team & OASE Agents

OASE is built for **multi-human + multi-agent team science**. During the training, each participant practices operating their surface role alongside OASE's 22 container templates:

| Human Workshop Role | Surface Used (`GA` / `AGY` / Scion UI) | Counterpart OASE Agent Templates | What You Do in This Training |
|---|---|---|---|
| **1. Project Owner / Program Lead** | Gemini Agent (`GA`) or Antigravity (`AGY`) with `UserIdentity` token | `research-operations-controller` (`controller`), `science-program-lead`, `<slug>-head-of-discovery`, `bootstrapper` | Runs `create_project` (4-step atomic setup), assigns R&D team members (`role: "project-member"`), completes the interactive **A2UI Project & Campaign Initiation Card** (`bootstrap_campaign`), reviews `DEC-###` logs, and issues `STAGE_GATE_DECISION` verdicts across Stages 0 → 4. |
| **2. Target & Computational Biologist** | `GA` / `AGY` (`scion` MCP) + `constraint-viewer.html` & `expression-viewer.html` | `computational-biologist`, `hypex-supervisor`, `scientific-reviewer` | Audits Stage 0 seed ingestion (`oase coscientist`), runs fast exploratory queries in `GA`/`AGY`, escalates Stage 1 work orders (`WO-002`, `WO-003`) via `request_work_order`, and inspects `oase genetics` (gnomAD), `oase gwas` (OpenTargets, ClinVar), `oase gtex`, and live **AlphaGenome on GCP** (`oase alphagenome score-variant` + `analyze`). |
| **3. Structural Biologist & Computational Chemist** | `GA` / `AGY` + `plddt-viewer.html`, `pae-viewer.html`, `pockets-viewer.html`, `docking-viewer.html` | `structural-biologist`, `computational-chemist` | Commissions and audits Stage 2 work orders (`WO-004`, `WO-005`): `oase alphafold fetch/analyze` (`Q8NBP7`), live **AlphaFold 3 on GCP** ligand co-folding (`oase alphafold predict --template ligand` + `analyze-prediction`), `fpocket` (`oase pocket run/analyze`), and 3-phase AutoDock Vina + Meeko docking (`oase docking prepare/run/analyze/contacts`). |
| **4. Medicinal Chemist** | `GA` / `AGY` + `brics-viewer.html`, `admet-viewer.html`, `sdf-viewer.html` | `medicinal-chemist` | Injects live medicinal chemistry design constraints (`MW <= 500`, `cLogP <= 3.5`, `TPSA 75–110 Å²`, zero structural alerts, `<= 5` synthetic steps) via `request_work_order` (`WO-006`) and audits `oase mmp` (BRICS matched molecular pairs), `oase admet` (RDKit + ChEMBL structural alerts + Tox21), and `oase retro` (ASKCOS retrosynthesis). |
| **5. DMPK, Safety & Regulatory Lead** | `GA` / `AGY` + `_site/index.html` 28-page portal | `admet-dmpk-scientist`, `preclinical-toxicologist`, `regulatory-scientist`, `finding-validator`, `project-curator` | Audits Stage 4 work orders (`WO-007`, `WO-008`): `oase pk` (`ingest → nca → scale → analyze` for 70 kg human QD oral projection), `oase trials` (ClinicalTrials.gov differentiation vs. `evolocumab`/`inclisiran`/`MK-0616`), `oase faers` (FDA adverse events), `oase dossier export`, and `oase site build && oase site export`. |

### 0.2 End-to-End 8-Module Training Map (150 Minutes)

| Module | Time | Campaign Stage & Focus (`pcsk9-oral`) | Primary Tools & Commands Exercised | Work Orders / Decisions / Instant Checkpoint |
|---|---|---|---|---|
| **Module 0** | `0:00–0:15` (15m) | Pre-Flight, Project Owner Provisioning & Team Onboarding | `scion auth login`, `oase doctor`, `scion:create_project` (`members` assignment, SA verification, `tools` shared volume, 22-template import) | Project `oral-pcsk9-ascvd` created & locked (`ch0`) |
| **Module 1** | `0:15–0:35` (20m) | Campaign Initiation, A2UI Gate & Stage 0 Seed Verification | `scion:bootstrap_campaign` (`A2UI_INPUT_REQUIRED` card, 7-part `/workspace/.seed/pcsk9-oral/` staging, `CHECKSUMS.json`), `oase coscientist ingest/analyze/show`, `scion:decision_log` | `DEC-001`, `WO-001` (`IC-001` Allosteric SM vs. `IC-002` Oral Macrocycle) · **Checkpoint `ch1`** |
| **Module 2** | `0:35–1:00` (25m) | Stage 1: Human Genetics, Multi-Tissue Safety & AlphaGenome Regulatory Polarity | `scion:request_work_order`, `oase genetics fetch/analyze`, `oase gwas search/analyze`, `oase gtex fetch/analyze`, `oase alphagenome score-variant/analyze`, `oase validate check` | `WO-002`, `WO-003`, `DEC-002..004`, Stage 1 Gate · **Checkpoint `ch2`** |
| **Module 3** | `1:00–1:25` (25m) | Stage 2: 3D Structure, Live AlphaFold 3 Ligand Co-Folding, `fpocket` & AutoDock Vina | `oase alphafold fetch/analyze`, `oase alphafold predict --template ligand`, `oase alphafold analyze-prediction`, `oase pocket run/analyze`, `oase docking prepare/run/analyze/contacts` | `WO-004`, `WO-005`, `DEC-005..007`, Stage 2 Gate · **Checkpoint `ch3`** |
| **Module 4** | `1:25–1:50` (25m) | Stage 3: DMTA Lead Optimization, BRICS MMP, ADMET & ASKCOS Retrosynthesis | `scion:request_work_order`, `oase mmp fragment/pairs/analyze`, `oase admet predict-batch/analyze`, `oase retro search/analyze` | `WO-006`, `DEC-008..009`, `liability-tracker.md`, Stage 3 Gate |
| **Module 5** | `1:50–2:10` (20m) | Stage 4: Oral PK Allometric Scaling, Clinical Differentiation, IND Dossier & Portal Export | `oase pk ingest/nca/scale/analyze`, `oase trials search/analyze`, `oase faers search/analyze`, `oase dossier check/export`, `oase site build/validate/export` | `WO-007`, `WO-008`, `DEC-010..012`, `pcsk9-oral-site.zip` (28-page portal) · **Checkpoint `ch4`** |
| **Module 6** | `2:10–2:20` (10m) | Forensic Epistemic Governance Drills (Catching Overclaims & Missing Relays) | `oase validate check --preflight`, `[relay:<code>]` verification, `{source: raw/...}` JSONPath audit, `oase h5ad searched_absent`, `oase workorder override` | Hands-on failure/remediation drills |
| **Module 7** | `2:20–2:30` (10m) | Operational Best-Practices Cheat Sheet & Cross-Reference | 6 Golden Rules of `GA`/`AGY` ↔ OASE operation, latency routing heuristic, and 3-column CLI cross-reference | Production readiness sign-off |

---

## Module 0 (15 Min): Pre-Flight Verification, Project Owner Provisioning & Team Onboarding

### Learning Objectives
1. Verify that your `GA` or `AGY` surface is connected to Scion Hub with a valid `UserIdentity` token.
2. Execute Level 1 Project Provisioning (`create_project`) as the **Project Owner**, assigning participating R&D team members (`role: "project-member"`).
3. Verify that the project has a verified GCP Service Account, the `/scion-volumes/tools` shared directory, and all 6 critical OASE agent templates before any agent container starts.

### Exercise 0.1 — Verify Surface Connectivity & Environment Health
From a terminal on your workstation (or inside `GA`/`AGY`), verify Hub connectivity and the OASE tool environment:

```bash
# 1. Verify Scion Hub connectivity via the scion MCP server:
python3 tools/scion_mcp_server.py --cli hub_status --args '{}'

# 2. Inside the OASE container / sandbox VM, verify all 62 CLI tool groups and 51/51 Phase-2 offline latches:
oase doctor --json
```

**What to Look For in `oase doctor --json`:**
- `"verdict": "PROCEED"` (if `"BLOCKED"`, inspect the `failures` array for missing binaries or unconfigured GCP endpoints).
- `"phase_two_offline_latch": "51/51 verified"` (confirms every Phase-2 `analyze` command is wrapped by `enforce_phase_two`).
- Compiled binaries present on `/scion-volumes/tools`: `fpocket`, `vina`, `mk_prepare_receptor.py`, `mk_prepare_ligand.py`, `hypex`, `elo`, `prox`, and KaTeX (`node_modules/katex/dist`).

### Exercise 0.2 — Project Owner Creates the Project & Assigns the R&D Team (`create_project`)
The **Project Owner** initiates project creation from Gemini Agent (`GA`) or Antigravity / Jetski (`AGY`). Never use raw `scion project create` alone, because raw project creation leaves `sharedDirs: null` and `0` project-scoped templates.

**Prompt to `GA` or `AGY` (Project Owner):**
> *"Create a new OASE Scion project named `Translational R&D — Oral PCSK9 ASCVD` with slug `oral-pcsk9-ascvd`, using harness `gemini-cli` and model size `large`, and assign `compbio-lead@example-biopharma.com`, `medchem-lead@example-biopharma.com`, and `dmpk-lead@example-biopharma.com` as project members."*

**Underlying MCP Tool Invocation (`scion:create_project`):**
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

**Expected Output & Verification Check:** Confirm that the returned JSON shows all 4 atomic steps succeeded:
- `"project_id"`: UUID of the newly created Scion project.
- `"service_account_verified": true` and `"defaultGCPIdentityMode": "assign"`.
- `"shared_dirs"`: includes `"tools"` (`readOnly: false, inWorkspace: false`).
- `"critical_templates_verified"`: `["bootstrapper", "finding-validator", "head-of-discovery", "hypex-supervisor", "research-operations-controller", "science-program-lead"]`.
- `"members_assigned"`: `["compbio-lead@example-biopharma.com", "medchem-lead@example-biopharma.com", "dmpk-lead@example-biopharma.com"]` with `role: "project-member"`.

### Exercise 0.3 — Team Members Join & Bind Their `GA` / `AGY` Sessions
Each assigned scientist opens their own `GA` or `AGY` session and binds to the shared project:
```json
{
  "ServerName": "scion",
  "ToolName": "list_projects",
  "Arguments": {}
}
```
Once a team member invokes any project-scoped tool (`decision_log`, `dav_list`, `list_agents`) with `"project_id": "<oral-pcsk9-ascvd-uuid>"`, their chat session is automatically locked to that project (`SESSION_PROJECT_LOCKED` at `~/.config/pharma_skills/oase_sessions/session_<sid>.json`), preventing accidental cross-project writes.

---

## Module 1 (20 Min): Campaign Initiation, The A2UI Gate & Stage 0 Hypothesis Seed Verification

### Learning Objectives
1. Initiate the `pcsk9-oral` campaign from `GA` or `AGY` using `bootstrap_campaign` and the interactive **A2UI Project & Campaign Initiation Card**.
2. Understand how `seed_mode: "sciarchitect"` stages the **7-Part Zero-Truncation Seed Package** (`/workspace/.seed/pcsk9-oral/`) over WebDAV (`CHECKSUMS.json` written last) before starting `controller`.
3. Inspect how `science-program-lead` ingests the seed via `oase coscientist ingest` + `analyze`, logs `DEC-001`, and dispatches `WO-001` (`stage0_verification`).

### Exercise 1.1 — Triggering & Submitting the A2UI Campaign Initiation Card
If the Project Owner asks `GA` or `AGY` to *"Start the oral PCSK9 campaign in project `oral-pcsk9-ascvd`"* without specifying all charter fields, `bootstrap_campaign` halts and returns `status: "A2UI_INPUT_REQUIRED"` to render the **A2UI Project & Campaign Initiation Card**.

**Complete `bootstrap_campaign` Call After A2UI Card Confirmation:**
```json
{
  "ServerName": "scion",
  "ToolName": "bootstrap_campaign",
  "Arguments": {
    "project_id": "<oral-pcsk9-ascvd-uuid>",
    "program_slug": "pcsk9-oral",
    "program_directive": "Discover and optimize an oral QD allosteric small-molecule or macrocyclic peptidomimetic inhibitor of human PCSK9 (Q8NBP7) for ASCVD that disrupts LDLR degradation with hepatic selectivity, clean hERG/CYP safety, and competitive differentiation vs. injectable anti-PCSK9 mAbs (evolocumab/Repatha) and oral macrocycles (MK-0616/enlicitide).",
    "sponsor_gate_policy": "manual",
    "seed_mode": "sciarchitect",
    "stage_entry_point": "stage0_verification",
    "seed_bundle_dir": "/workspace/workshop/checkpoints/ch0/seed/pcsk9-oral"
  }
}
```

**What Happens Automatically Under the Contract:**
1. **Pre-Init Single-Writer Rule:** `GA`/`AGY` does **not** create `/workspace/pcsk9-oral/` (because `oase init /workspace/pcsk9-oral` requires the directory to be non-existent or empty).
2. **7-Part Seed Staging to `/workspace/.seed/pcsk9-oral/`:** Stages `campaign-seed.json` (`schema: "oase.campaign-seed.v2"`), `coscientist-export.json`, `ideas/`, `citations/`, `summary/`, `verification/`, `tournament/`, `submission/`, verifies every file by read-back `GET` SHA-256, and writes `CHECKSUMS.json` last.
3. **Controller-Only Startup:** Starts **only** `controller` (`--type research-operations-controller`, without `--role baseline`) with the canonical startup directive:
   ```text
   Program directive: Discover and optimize an oral QD allosteric small-molecule or macrocyclic peptidomimetic inhibitor of human PCSK9 (Q8NBP7) for ASCVD... Program directory: /workspace/pcsk9-oral/. Sponsor gate policy: manual. Seed mode: sciarchitect. Seed artifact: /workspace/.seed/pcsk9-oral/campaign-seed.json. Stage entry point: stage0_verification.
   ```
4. **Post-Start Template Check:** Verifies `controller.template == "research-operations-controller"` (`CONTROLLER_TEMPLATE_MISMATCH` guard).

### Exercise 1.2 — What OASE Executes in Stage 0 (`oase init` & `oase coscientist`)
Once `controller` starts, it spawns `bootstrapper` (`oase doctor` → `oase init /workspace/pcsk9-oral`) and wakes `science-program-lead`. Inside the container, `science-program-lead` executes the two-phase Co-Scientist seed ingestion and analysis tools:

```bash
# Phase 1: Ingest the staged SciArchitect tournament export into Layer 0 (raw/coscientist/)
# Writes raw/coscientist/pcsk9-oral-seed.json + .meta.json SHA-256 sidecar
oase --project /workspace/pcsk9-oral coscientist ingest \
  /workspace/.seed/pcsk9-oral/coscientist-export.json \
  --top 10

# Phase 2 (100% offline latch): Apply threshold set coscientist@1.0 (elo_decisive_gap=50.0, min_win_rate=0.60)
# Writes raw/coscientist/pcsk9-oral-seed.analysis.json with mandatory relays
oase --project /workspace/pcsk9-oral coscientist analyze \
  raw/coscientist/pcsk9-oral-seed.json \
  --elo-decisive-gap 50.0 \
  --min-win-rate 0.60

# Inspect the top-ranked hypothesis (Rank 1 -> IC-001) and its verified references:
oase --project /workspace/pcsk9-oral coscientist show \
  raw/coscientist/pcsk9-oral-seed.json --rank 1

oase --project /workspace/pcsk9-oral coscientist references \
  raw/coscientist/pcsk9-oral-seed.json --gene PCSK9
```

> [!TIP]
> **Key Operational Detail (`oase coscientist ingest` vs. `oase hypothesis adopt`):** Always use `oase coscientist ingest <export_file>` for Mode 2 (`sciarchitect`) seeds. It preserves all ranked hypotheses, Elo ratings, match ledgers, falsifiable predictions, and claim citations in Layer 0 (`raw/coscientist/`), whereas `oase hypothesis adopt` is a 2-field manual CLI (`--title`, `--mechanism`) intended only for ad-hoc single sentences.

### Exercise 1.3 — Reading `DEC-001` & Active Concepts from `GA` or `AGY` in ~1.5 Seconds
From `GA` or `AGY`, any team member can read the structured decision log and active candidate concepts (`IC-001` and `IC-002`) directly over WebDAV without waking an agent container:

```json
{
  "ServerName": "scion",
  "ToolName": "decision_log",
  "Arguments": {
    "project_id": "<oral-pcsk9-ascvd-uuid>",
    "program_slug": "pcsk9-oral",
    "limit": 5
  }
}
```

And inspect `program-state/active-series.md` via `dav_read`:
```json
{
  "ServerName": "scion",
  "ToolName": "dav_read",
  "Arguments": {
    "project_id": "<oral-pcsk9-ascvd-uuid>",
    "path": "pcsk9-oral/program-state/active-series.md"
  }
}
```

**What You Will See in `active-series.md` & `DEC-001`:**
- **`IC-001` (Primary Concept):** Oral allosteric small-molecule inhibitor binding the C-terminal Cys-His-rich / catalytic-domain groove of PCSK9 (`Q8NBP7`) to allosterically destabilize LDLR EGF-A domain engagement (`Elo = 1642.5`).
- **`IC-002` (Backup Concept):** Oral tricyclic macrocyclic peptidomimetic directly occluding the flat PCSK9–LDLR EGF-A protein-protein interface, benchmarked against clinical comparator `MK-0616 / enlicitide` (`Elo = 1588.0`).

*(Workshop Checkpoint Shortcut: To jump directly to the end of Stage 0 at any time, run `./scripts/checkpoint.sh goto ch1`.)*

---

## Module 2 (25 Min): Stage 1 — Human Genetics, Multi-Tissue Safety & Live AlphaGenome Regulatory Scoring (`WO-002` & `WO-003`)

### Learning Objectives
1. Apply the **Exploratory vs. Decision-Grade Task Division Rule ("Gray Zone" Escalation)**: run fast interactive checks in `GA`/`AGY`, then escalate decision-relevant questions via `request_work_order`.
2. Operate OASE's Stage 1 genetics and regulatory genomics CLI tools (`oase genetics`, `oase gwas`, `oase gtex`, and `oase alphagenome score-variant / analyze`) across Phase 1 (`fetch`/`score-variant`) and Phase 2 (`analyze`).
3. Audit Validation 1 (`oase validate check`) and Validation 2 (`science-program-lead` Phase-2 review) and issue the Stage 1 Gate Verdict.

### Exercise 2.1 — Escalating a Decision-Grade Question from `GA`/`AGY` (`request_work_order`)
Suppose the Target Biologist wants to test whether hepatocyte-specific non-coding regulatory variants at the `PCSK9` locus (`chr1:55039974:G>T` / `rs2479409`) and the comparator `1p13.3 SORT1` locus (`chr1:109274968:G>T` / `rs12740374`) confirm liver-specific transcriptional directionality without extra-hepatic toxicity risk.

Because this finding will be cited in the Stage 1 Target Validation Gate (`DEC-004`), the scientist escalates it from `GA`/`AGY` to `science-program-lead` via `request_work_order`:

```json
{
  "ServerName": "scion",
  "ToolName": "request_work_order",
  "Arguments": {
    "project_id": "<oral-pcsk9-ascvd-uuid>",
    "program_slug": "pcsk9-oral",
    "target_role": "computational-biologist",
    "title": "Stage 1 Human Genetic Constraint, GTEx Tissue Selectivity & AlphaGenome Regulatory Variant Scoring for PCSK9",
    "question": "1. Quantify human loss-of-function constraint (gnomAD pLI/LOEUF) and protective ASCVD coding/non-coding associations (OpenTargets, ClinVar R46L rs11591147, Y142X) for PCSK9. 2. Quantify multi-tissue RNA expression across 54 GTEx tissues to verify hepatocyte restriction. 3. Score PCSK9 regulatory variant chr1:55039974:G>T (rs2479409) and positive comparator chr1:109274968:G>T (rs12740374, SORT1 1p13.3) using AlphaGenome on GCP across RNA_SEQ, DNASE, and CAGE in human liver."
  }
}
```

### Exercise 2.2 — Exact Phase-1 & Phase-2 `oase` Commands Executed by `computational-biologist` (`WO-002` & `WO-003`)

#### Step A: Human Loss-of-Function Constraint (`oase genetics`)
```bash
# Phase 1: Fetch gnomAD constraint metrics for PCSK9 into raw/genetics/PCSK9.json (+ .meta.json)
oase --project /workspace/pcsk9-oral genetics fetch PCSK9

# Phase 2 (offline): Apply genetics@1.0 thresholds (pLI=0.90, LOEUF=0.35)
# Writes raw/genetics/PCSK9.analysis.json
oase --project /workspace/pcsk9-oral genetics analyze PCSK9 --pli 0.90 --loeuf 0.35
```
- **Key Output Fields (`raw/genetics/PCSK9.analysis.json`):** `pLI = 0.0001`, `loeuf = 0.89` (`verdict: "loss-of-function-tolerant"`). Confirms that complete human `PCSK9` loss of function is viable and non-essential, de-risking on-target safety.

#### Step B: Human Genetic Association & Protective LoF Alleles (`oase gwas`)
```bash
# Phase 1: Query OpenTargets Platform, GWAS Catalog v2, and ClinVar for PCSK9
oase --project /workspace/pcsk9-oral gwas search PCSK9 --source opentargets
oase --project /workspace/pcsk9-oral gwas search PCSK9 --source clinvar

# Phase 2 (offline): Filter and score associations against gwas@1.0 threshold (0.70)
oase --project /workspace/pcsk9-oral gwas analyze PCSK9 \
  --source opentargets \
  --threshold 0.70 \
  --disease-filter "hypercholesterolemia"
```
- **Key Output Fields (`raw/gwas/PCSK9_opentargets.analysis.json`):** Overall association score `> 0.95` for hypercholesterolemia / ASCVD; protective human LoF variants `rs11591147` (`p.Arg46Leu / R46L`) and `p.Tyr142Ter` (`Y142X`) confer lifelong LDL-C reduction and `~50–88%` lower coronary heart disease risk without adverse liver or neurocognitive phenotypes.

#### Step C: Multi-Organ Expression Selectivity (`oase gtex`)
```bash
# Phase 1: Fetch median TPM across all 54 non-diseased GTEx v8 tissues
oase --project /workspace/pcsk9-oral gtex fetch PCSK9

# Phase 2 (offline): Compute tissue specificity index (Tau) and top-tissue rank
oase --project /workspace/pcsk9-oral gtex analyze PCSK9
```
- **Key Output Fields (`raw/gtex/PCSK9.analysis.json`):** `Liver` (`UBERON:0002107`) is rank `#1` (`median TPM > 180`), with high tissue specificity (`Tau > 0.92`) and minimal expression in heart, skeletal muscle, kidney, or brain.

#### Step D: Live AlphaGenome 1 Mb Sequence-to-Function Regulatory Scoring on GCP (`oase alphagenome`)
```bash
# Phase 1: Score PCSK9 5' regulatory variant chr1:55039974:G>T (rs2479409, GRCh38) on Dedicated GCP AlphaGenome Endpoint
oase --project /workspace/pcsk9-oral alphagenome score-variant \
  --chrom chr1 \
  --pos 55039974 \
  --ref G \
  --alt T \
  --window 1048576 \
  --output-type RNA_SEQ \
  --output-type DNASE \
  --output-type CAGE \
  --organism HOMO_SAPIENS \
  --deadline 600

# Phase 2 (offline): Apply alphagenome@1.0 thresholds (quantile_significance=0.95, raw_score_moderate=0.10)
oase --project /workspace/pcsk9-oral alphagenome analyze \
  raw/alphagenome/chr1_55039974_G_T.json \
  --quantile-significance 0.95 \
  --raw-score-moderate 0.10
```

> [!IMPORTANT]
> **Operational Guardrail Taught in Module 2 (`alphagenome.high_quantile_low_raw` Relay):** If a variant has a high percentile/quantile score (`>= 0.95`) but a tiny absolute raw log-fold-change (`< 0.10`), `oase alphagenome analyze` automatically emits the mandatory relay `alphagenome.high_quantile_low_raw` in `.analysis.json`. The specialist **must** include `[relay:alphagenome.high_quantile_low_raw]` in `findings/computational-biology/WO-003.md` so the team never mistakes background noise for a large regulatory effect.
>
> *(Parallel Track Callout: For Candidate 2 — `PRMT5` in `MTAP`-deleted solid tumors — this same step runs `oase cbioportal` on `9p21 CDKN2A/MTAP` co-deletion and `oase alphagenome score-variant` at the `9p21` regulatory locus.)*

### Exercise 2.3 — Running the 10-Check Mechanical Validator (`oase validate check`) & Stage 1 Gate Approval
Before `WO-002` and `WO-003` can be reviewed by `science-program-lead`, `finding-validator` runs Validation 1:

```bash
# Run preflight check during authoring, or full check upon submission:
oase --project /workspace/pcsk9-oral validate check WO-003 --preflight
oase --project /workspace/pcsk9-oral validate check WO-003
```

Once Validation 1 (`validation_passed`) and Validation 2 (`science-program-lead` logs `DEC-004` and transitions `WO-003` to `scientifically_accepted`) complete, `science-program-lead` messages the Project Owner (`[OASE_INBOUND_MESSAGE]`). The Project Owner approves the Stage 1 → Stage 2 Gate from `GA`/`AGY`:

```json
{
  "ServerName": "scion",
  "ToolName": "send_message",
  "Arguments": {
    "project_id": "<oral-pcsk9-ascvd-uuid>",
    "agent": "science-program-lead",
    "message": "STAGE_GATE_DECISION: Stage 1 Target Validation APPROVED for pcsk9-oral (IC-001 primary allosteric small molecule, IC-002 backup oral macrocycle). Proceed to Stage 2 3D structural pocket assessment, AlphaFold 3 ligand co-folding on GCP, and Vina virtual screening."
  }
}
```

---

## Module 3 (25 Min): Stage 2 — 3D Structure Assessment, Live AlphaFold 3 Co-Folding on GCP, `fpocket` & AutoDock Vina (`WO-004` & `WO-005`)

### Learning Objectives
1. Fetch and audit canonical protein structures (`oase alphafold fetch` + `analyze`), including UniProt canonical length cross-checks and 2D PAE domain segmentation.
2. Run live **AlphaFold 3 protein-ligand co-folding on GCP** (`oase alphafold predict --template ligand` + `analyze-prediction` + `analyze-plddt`).
3. Identify and score druggable cavities (`oase pocket run` + `analyze`) and execute 3-phase AutoDock Vina + Meeko molecular docking (`oase docking prepare → run → analyze → contacts`).

### Exercise 3.1 — Structural Biologist Work Order (`WO-004`): AFDB, AlphaFold 3 Co-Folding & `fpocket`

#### Step A: Fetch & Analyze `PCSK9` (`Q8NBP7`) Structure and PAE Domains
```bash
# Phase 1: Download AlphaFold DB v4 mmCIF + PAE matrix + API record for human PCSK9 (Q8NBP7, 692 aa)
# Cross-checks modelled length against UniProt canonical length
oase --project /workspace/pcsk9-oral alphafold fetch Q8NBP7

# Phase 2 (offline): Compute pLDDT confidence bands and 2D PAE rigid domain blocks
oase --project /workspace/pcsk9-oral alphafold analyze Q8NBP7 \
  --plddt-confident 0.70 \
  --plddt-moderate 0.50 \
  --pae-domain-cutoff 5.0
```
- **Key Output (`raw/alphafold/Q8NBP7.analysis.json`):** Identifies the disordered N-terminal signal/propeptide segment (`aa 1–60`, `pLDDT < 50`) vs. the rigid, well-folded prodomain + subtilisin-like catalytic domain (`aa 61–454`, `pLDDT > 88`) and C-terminal Cys-His-rich domain (`aa 455–692`), and verifies the inter-domain groove adjacent to the LDLR EGF-A binding surface (`PDB: 2P4E / 3P5B`).

#### Step B: Live AlphaFold 3 Protein + SMILES Co-Folding on GCP (`oase alphafold predict`)
```bash
# Phase 1: Co-fold PCSK9 catalytic/C-terminal domain with candidate allosteric ligand SMILES on Dedicated GCP AF3 Endpoint
oase --project /workspace/pcsk9-oral alphafold predict \
  --input raw/structures/pcsk9_ic001_af3_ligand.json \
  --template ligand \
  --deadline 1800

# Phase 2 (offline): Evaluate AF3 summary confidences (ipTM, pTM, ranking_score, fraction_disordered, has_clash)
oase --project /workspace/pcsk9-oral alphafold analyze-prediction \
  raw/alphafold/pcsk9_ic001_af3_ligand/summary_confidences.json

# Phase 2 (offline): Extract per-atom B_iso_or_equiv pLDDT distribution from the AF3 mmCIF
oase --project /workspace/pcsk9-oral alphafold analyze-plddt \
  raw/alphafold/pcsk9_ic001_af3_ligand/model.cif
```
- **Operational Input Rules for `oase alphafold predict`:**
  - Use `--template monomer` for single chains, `--template complex` for multi-chain PPIs (e.g., `PCSK9` + `LDLR EGF-A`), and `--template ligand` for protein + small-molecule SMILES or CCD codes.
  - Always run **both** `analyze-prediction` (which checks `summary_confidences.json` for `iptm >= 0.70`, `ptm`, `ranking_score`, and `has_clash == 0.0`) and `analyze-plddt` (which inspects per-atom `B_iso_or_equiv` values in the output `.cif`).

#### Step C: Cavity Detection & Druggability Scoring (`oase pocket`)
```bash
# Phase 1: Run compiled fpocket 4.2.2 on PCSK9 structure (stripping short co-crystallized peptides by default)
oase --project /workspace/pcsk9-oral pocket run \
  raw/alphafold/Q8NBP7.cif \
  --strip-peptides

# Phase 2 (offline): Apply pocket@1.0 druggability threshold (0.50) and highlight pockets near the allosteric groove
oase --project /workspace/pcsk9-oral pocket analyze \
  raw/pocket/Q8NBP7_pockets.json \
  --druggable 0.50 \
  --near "A:153,A:194,A:238,A:374,A:378"
```
- **Why `--strip-peptides` Matters:** If you pass an experimental complex (such as `PDB: 2P4E`, which contains the bound `LDLR EGF-A` peptide chain), `--strip-peptides` removes bound peptide chains smaller than `--peptide-threshold` before running `fpocket` so the binding pocket is not occluded by the co-crystallized peptide.
- **Outcome (`DEC-005`):** `IC-001`'s cryptic inter-domain allosteric pocket scores **`druggability = 0.68`** (volume `740 Å³`, enclosed hydrophobic/polar cleft suitable for a Rule-of-5 oral small molecule), whereas the flat outer EGF-A surface targeted by `IC-002` scores **`druggability = 0.24`** (requiring a larger macrocyclic scaffold). `science-program-lead` prioritizes `IC-001` as the primary small-molecule series while retaining `IC-002` as the macrocycle comparator.

### Exercise 3.2 — Computational Chemist Work Order (`WO-005`): 3-Phase AutoDock Vina + Pose Contacts
OASE splits molecular docking into three phases (`prepare → run → analyze`) so that the prepared receptor `.pdbqt` and 3D grid box are citable Layer 0 artifacts reused identically across all analog series:

```bash
# Phase 1a (Prepare): Convert receptor to PDBQT via Meeko (mk_prepare_receptor.py) and compute grid box
# from fpocket Pocket #1 centroid (+10 Å padding)
oase --project /workspace/pcsk9-oral docking prepare \
  raw/alphafold/Q8NBP7.cif \
  raw/pocket/Q8NBP7_pockets.json \
  --pocket-rank 1 \
  --protein-only

# Phase 1b (Run): Execute AutoDock Vina 1.2.5 across 5 curated ChEMBL PCSK9 allosteric analogs (< 90 seconds on CPU)
oase --project /workspace/pcsk9-oral docking run \
  raw/docking/Q8NBP7_receptor.pdbqt \
  raw/docking/Q8NBP7_pocket1_gridbox.json \
  raw/compounds/pcsk9_analog_01.sdf \
  raw/compounds/pcsk9_analog_02.sdf \
  raw/compounds/pcsk9_analog_03.sdf \
  raw/compounds/pcsk9_analog_04.sdf \
  raw/compounds/pcsk9_analog_05.sdf \
  --exhaustiveness 8 \
  --n-poses 9

# Phase 2a (Offline Analyze): Rank ligands against docking-scores@1.0 thresholds and flag steric clashes
oase --project /workspace/pcsk9-oral docking analyze \
  raw/docking/runs/pcsk9_analog_01.dock.json \
  raw/docking/runs/pcsk9_analog_02.dock.json \
  raw/docking/runs/pcsk9_analog_03.dock.json \
  raw/docking/runs/pcsk9_analog_04.dock.json \
  raw/docking/runs/pcsk9_analog_05.dock.json

# Phase 2b (Offline Contacts): Compute < 4.0 Å atomic receptor-ligand interactions and check for < 2.0 Å steric clashes
oase --project /workspace/pcsk9-oral docking contacts \
  raw/docking/runs/pcsk9_analog_02_poses.pdbqt \
  raw/docking/Q8NBP7_receptor.pdbqt \
  --cutoff 4.0 \
  --min-distance 2.0
```

### Exercise 3.3 — Inspecting Interactive 3D Structure & Docking Viewers
In the Scion Hub proxy or exported `_site/` portal, open:
- **`plddt-viewer.html` & `pae-viewer.html`:** Verify the pLDDT spectrum and off-diagonal PAE blocks for `Q8NBP7` and the AF3 co-folded complex.
- **`pockets-viewer.html`:** Inspect Pocket #1 (`druggability = 0.68`) vs. the surface EGF-A patch.
- **`docking-viewer.html`, `docking-scores-viewer.html` & `contacts-viewer.html`:** Compare the top docked hit (`pcsk9_analog_02`, `ΔG = -9.4 kcal/mol`, zero steric clashes `< 2.0 Å`, key hydrogen bonds to `Arg194` and `Asp238`) across all 5 analogs.

*(Workshop Checkpoint Shortcut: Run `./scripts/checkpoint.sh goto ch3` to load the completed Stage 2 state.)*

---

## Module 4 (25 Min): Stage 3 — DMTA Lead Optimization, BRICS Matched Molecular Pairs, ADMET & ASKCOS Retrosynthesis (`WO-006`)

### Learning Objectives
1. Inject a real-time medicinal chemistry constraint from `GA`/`AGY` into the active campaign (`request_work_order`).
2. Operate `oase mmp` (RDKit BRICS fragmentation & matched molecular pair transforms), `oase admet` (physicochemical descriptors, LipE, ChEMBL structural alerts, and Tox21), and `oase retro` (ASKCOS retrosynthetic route scoring).
3. Track resolved vs. open chemical liabilities in `program-state/liability-tracker.md`.

### Exercise 4.1 — Injecting a Live Medicinal Chemistry Constraint from `GA`/`AGY`
Suppose `pcsk9_analog_02` has strong docking affinity (`-9.4 kcal/mol`) but carries a high lipophilicity (`cLogP = 4.8`) and a potential CYP3A4 / hERG liability. The Medicinal Chemist sends a work-order request from `GA`/`AGY`:

```json
{
  "ServerName": "scion",
  "ToolName": "request_work_order",
  "Arguments": {
    "project_id": "<oral-pcsk9-ascvd-uuid>",
    "program_slug": "pcsk9-oral",
    "target_role": "medicinal-chemist",
    "title": "Stage 3 DMTA SAR Optimization of PCSK9 Allosteric Lead Series (IC-001)",
    "question": "Generate and evaluate matched molecular pair (MMP) analogs of pcsk9_analog_02 that reduce cLogP <= 3.5, maintain MW <= 500 and TPSA between 75 and 110 A^2 for oral hepatocyte uptake, eliminate ChEMBL/Tox21 structural alerts and hERG liability, and confirm a convergent ASKCOS retrosynthetic route in <= 5 steps."
  }
}
```

### Exercise 4.2 — Exact Phase-1 & Phase-2 DMTA Commands Executed by `medicinal-chemist` (`WO-006`)

#### Step A: BRICS Fragmentation & Matched Molecular Pair (MMP) SAR Analysis (`oase mmp`)
```bash
# Phase 1a: Fragment parent hit SMILES via RDKit BRICS bonds
oase --project /workspace/pcsk9-oral mmp fragment \
  "Cc1ccc(C(=O)Nc2ccc(CN3CCN(c4ccnc5ccccc45)CC3)cc2)cc1F"

# Phase 1b: Enumerate matched molecular pairs across the PCSK9 analog series (.smi file)
oase --project /workspace/pcsk9-oral mmp pairs \
  raw/compounds/pcsk9_ic001_series.smi

# Phase 2 (offline): Analyze property deltas (ΔpIC50, ΔcLogP, ΔLipE, ΔTPSA) across MMP transforms
oase --project /workspace/pcsk9-oral mmp analyze \
  raw/mmp/pcsk9_ic001_series.mmp.json
```

#### Step B: Batch ADMET, ChEMBL Structural Alerts & Tox21 Profiling (`oase admet`)
```bash
# Phase 1: Compute RDKit descriptors, ChEMBL structural alerts (chembl_alerts.py), and Tox21 endpoints
oase --project /workspace/pcsk9-oral admet predict-batch \
  raw/compounds/pcsk9_ic001_series.smi

# Phase 2 (offline): Apply admet@1.0 oral drug-likeness thresholds and emit mandatory safety relays
oase --project /workspace/pcsk9-oral admet analyze \
  raw/admet/pcsk9_ic001_series.admet.json
```
- **Key Output (`raw/admet/pcsk9_ic001_series.admet.analysis.json`):** Replacing the quinoline ring with a 2-methoxypyrimidine bioisostere (**`OASE-PCSK9-014`**) lowers `cLogP` from **`4.8 → 3.1`**, increases `LipE` from **`3.4 → 5.2`**, keeps `MW = 462.5 Da` and `TPSA = 88.4 Å²`, clears all ChEMBL/PAINS structural alerts (`0` alerts), and mitigates basic-amine hERG risk (`pKa` attenuated from `8.9 → 7.1`).

#### Step C: Retrosynthetic Tractability Assessment (`oase retro`)
```bash
# Phase 1: Query ASKCOS / retrosynthetic route tree for lead candidate OASE-PCSK9-014
oase --project /workspace/pcsk9-oral retro search \
  "COc1ncc(N2CCN(Cc3ccc(NC(=O)c4ccc(C)c(F)c4)cc3)CC2)cn1" \
  --max-results 5

# Phase 2 (offline): Score step count, starting-material availability, and route plausibility (threshold 0.60)
oase --project /workspace/pcsk9-oral retro analyze \
  "COc1ncc(N2CCN(Cc3ccc(NC(=O)c4ccc(C)c(F)c4)cc3)CC2)cn1" \
  --threshold 0.60
```
- **Key Output (`raw/retro/...analysis.json`):** Convergent **4-step synthesis** from commercially available building blocks (Buchwald-Hartwig / SNAr piperazine coupling + reductive amination + amide coupling, plausibility score `0.87`).

### Exercise 4.3 — Auditing `brics-viewer.html`, `admet-viewer.html` & `liability-tracker.md`
From `GA`/`AGY`, read `program-state/liability-tracker.md` via `dav_read` to verify how `science-program-lead` records the mitigation of `L-002` (lipophilicity/hERG liability on initial hit `pcsk9_analog_02` mitigated in `OASE-PCSK9-014`, `DEC-009`).

---

## Module 5 (20 Min): Stage 4 — Oral PK Scaling, Clinical Differentiation vs. Evolocumab/MK-0616, IND Dossier & 28-Page Portal Export (`WO-007` & `WO-008`)

### Learning Objectives
1. Execute OASE's 4-step pharmacokinetic scaling pipeline (`oase pk ingest → nca → scale → analyze`) to project human oral QD dosing.
2. Benchmark clinical trial landscapes (`oase trials`) and post-marketing FDA adverse event profiles (`oase faers`) against subcutaneous anti-PCSK9 mAbs (`evolocumab / Repatha`) and oral comparator `MK-0616 / enlicitide`.
3. Compile the regulatory preclinical dossier (`oase dossier check / export`) and export the standalone **28-page HTML campaign portal** (`oase site build && oase site export`).

### Exercise 5.1 — DMPK & Clinical Differentiation Commands (`WO-007` & `WO-008`)

#### Step A: Preclinical NCA & Allometric Human Oral PK Projection (`oase pk`)
```bash
# Phase 1a: Ingest rat and dog IV/PO time-concentration study data into Layer 0 (raw/pk/)
oase --project /workspace/pcsk9-oral pk ingest \
  raw/pk/oase_pcsk9_014_rat_iv_po.json
oase --project /workspace/pcsk9-oral pk ingest \
  raw/pk/oase_pcsk9_014_dog_iv_po.json

# Phase 1b: Run Non-Compartmental Analysis (NCA: AUC0-inf, Cmax, T1/2, CL, Vss, F%)
oase --project /workspace/pcsk9-oral pk nca \
  raw/pk/oase_pcsk9_014_rat_iv_po.pk.json --blq-method loq-half
oase --project /workspace/pcsk9-oral pk nca \
  raw/pk/oase_pcsk9_014_dog_iv_po.pk.json --blq-method loq-half

# Phase 1c: Allometric scaling to 70 kg human targeting unbound hepatic IC90 trough coverage
oase --project /workspace/pcsk9-oral pk scale \
  raw/pk/oase_pcsk9_014_rat_iv_po.nca.json \
  raw/pk/oase_pcsk9_014_dog_iv_po.nca.json \
  --human-bw 70.0 \
  --target-auc 12.5 \
  --target-cmax 2.0

# Phase 2 (offline): Apply pk@1.0 thresholds (oral bioavailability F >= 30%, QD dosing feasibility)
oase --project /workspace/pcsk9-oral pk analyze \
  raw/pk/oase_pcsk9_014_scaled.pk.json
```

#### Step B: Clinical Trial Landscape & FDA FAERS Safety Benchmarking (`oase trials` & `oase faers`)
```bash
# Phase 1 & Phase 2: ClinicalTrials.gov competitive landscape for PCSK9 in hypercholesterolemia / ASCVD
oase --project /workspace/pcsk9-oral trials search "PCSK9 hypercholesterolemia" --by condition
oase --project /workspace/pcsk9-oral trials analyze "PCSK9 hypercholesterolemia"

# Phase 1 & Phase 2: OpenFDA FAERS post-marketing safety baseline for evolocumab (Repatha)
oase --project /workspace/pcsk9-oral faers search "evolocumab" --max-results 100
oase --project /workspace/pcsk9-oral faers analyze "evolocumab"
```
- **Differentiation Summary Logged in `DEC-011`:** Compares **`OASE-PCSK9-014`** (oral Rule-of-5 allosteric small molecule, projected **40 mg QD oral tablet** without food or permeation-enhancer restrictions) against **`evolocumab / Repatha`** (subcutaneous Q2W/QM mAb injection) and **`MK-0616 / enlicitide`** (cyclic peptide requiring sodium caprate permeation enhancer and fasting administration).

#### Step C: Preclinical IND Dossier Compilation (`oase dossier`)
```bash
# Verify that all Stage 0 -> 4 gate artifacts, liability records, and accepted findings are present:
oase --project /workspace/pcsk9-oral dossier check

# Export the eCTD-structured candidate nomination dossier for WO-008:
oase --project /workspace/pcsk9-oral dossier export WO-008 --format markdown
```

### Exercise 5.2 — Building & Exporting the Self-Contained 28-Page HTML Campaign Portal (`oase site`)
Once `science-program-lead` logs `DEC-012` (`scientifically_accepted`), `project-curator` compiles the entire 5-layer workspace (`L4 Executive → L3 Gates → L2 Program State → L1 Findings → L0 Raw Data` + all 14 interactive HTML viewers) into a portable static site:

```bash
# 1. Production Governance Path (all WOs have passed Validation 1 + Validation 2):
oase --project /workspace/pcsk9-oral site build
oase --project /workspace/pcsk9-oral site validate
oase --project /workspace/pcsk9-oral site export --output /workspace/pcsk9-oral/pcsk9-oral-site.zip

# 2. Workshop Sandbox Preview Shortcut (ONLY when previewing unreviewed sandbox WOs in live-sandbox):
# Note: accept-all transitions ready_for_validation WOs with --decision bulk-accepted for sandbox previewing
oase --project /workspace/pcsk9-oral workorder accept-all && \
  oase --project /workspace/pcsk9-oral site build && \
  oase --project /workspace/pcsk9-oral site export --output /workspace/pcsk9-oral/pcsk9-oral-site.zip
```
Attendees download `pcsk9-oral-site.zip`, unzip it locally, and open `_site/index.html` in any browser (zero server required).

---

## Module 6 (10 Min): Forensic Epistemic Governance Drills — How OASE Catches Overclaims & Missing Relays

In this module, participants intentionally trigger and fix **4 real scientific and mechanical validation failures** so they understand how OASE's guardrails protect R&D teams from hallucinated or overstated findings:

### Drill 1 — Missing Mandatory Relay Code (`check_mandatory_relays`)
- **Scenario:** `oase docking analyze` records a `docking.steric_clash_warning` relay in `raw/docking/runs/pcsk9_analog_05.dock.analysis.json` because an atom sits `1.72 Å` from `His226`, but the specialist writes `findings/computational-chemistry/WO-005.md` without disclosing the clash.
- **What Happens:** `oase validate check WO-005` fails closed on Check #6 (`check_mandatory_relays`), listing the un-relayed code `docking.steric_clash_warning`.
- **How to Fix:** Include the verbatim relay tag `[relay:docking.steric_clash_warning]` in `findings/computational-chemistry/WO-005.md` explaining why `pcsk9_analog_05` was deprioritized due to the `1.72 Å` `His226` clash, then re-run `oase validate check WO-005`.

### Drill 2 — Uncited or Out-of-Tolerance Numerical Claims (`check_finding_source_tags`)
- **Scenario:** A finding states *"PCSK9 Pocket 1 has a druggability score of 0.85 `{source: raw/pocket/Q8NBP7_pockets.analysis.json#$.pockets[0].druggability_score}`"*, when the actual JSON value on disk is `0.68`.
- **What Happens:** `oase validate check WO-004` parses the JSONPath expression `#$.pockets[0].druggability_score`, compares `0.85` against `0.68`, and rejects the work order for numerical mismatch.
- **How to Fix:** Update the prose to cite the exact measured value `0.68` from the Phase-2 `.analysis.json` artifact.

### Drill 3 — Single-Cell `searched_absent` (`NA`) vs. Measured Zero (`0.0`) (`oase h5ad`)
- **Scenario:** On a provider-filtered `.h5ad` single-cell matrix (e.g., `12,621` genes retained), a target gene is absent from `var_names`.
- **What Happens:** `oase h5ad` refuses to report `mean_expression: 0.0` (which would falsely claim biological absence) and instead emits `parse_status: "searched_absent"` (`value: null`) alongside positive control `ACTB` (`ENSG00000075624`, `parse_status: "measured"`).
- **Operational Rule:** Always check `parse_status` in `raw/h5ad/*.analysis.json` (or `raw/single-cell/*.analysis.json`); treat `searched_absent` as *"unmeasured in this filtered matrix"*, never as zero expression.

### Drill 4 — Accepting Valid Data While Overriding Agent Interpretation (`DIRECTION_OVERRIDE`)
- **Scenario:** A specialist work order (`WO-006`) passes all 10 mechanical checks (Validation 1), so its Layer 0 / Phase-2 data is 100% valid, but the specialist over-interprets a marginal `0.2 kcal/mol` docking difference.
- **How the Project Owner & `science-program-lead` Handle It:** Instead of discarding valid raw data, `science-program-lead` logs **`DATA ACCEPTED / INTERPRETATION OVERRIDDEN`** in `DEC-009` (`events.ndjson: direction_override` / `oase workorder override WO-006 --actor science-program-lead --reason "..." --evidence raw/docking/...`), keeping the Layer 0 data in the workspace while recording the corrected scientific conclusion in Layer 2.

---

## Module 7 (10 Min): Operational Best-Practices Cheat Sheet & Cross-Reference

### 7.1 The 6 Golden Rules for R&D Teams Using OASE
1. **Project Owner Initiates & Assigns (`create_project` + `bootstrap_campaign`):** Always initiate new projects and campaigns from `GA` or `AGY` via `create_project` / `bootstrap_campaign` (never bare `scion project create`) so GCP SA verification, `tools` volume mounting, team `members` assignment, and 6-template verification happen atomically.
2. **Respect the Latency & Provenance Boundary ("Gray Zone" Rule):**
   - Need a 5-second answer for interactive discussion? Run it on the `GA` / `AGY` surface.
   - Will the number or conclusion be cited in a `DEC-###` decision or Stage Gate? Escalate it via `request_work_order` so OASE executes Phase 1 (`.meta.json` SHA-256 sidecar) + Phase 2 (100% offline `.analysis.json`) + Dual Validation (`Validation 1` + `Validation 2`).
3. **Read Direct via WebDAV (`decision_log`, `dav_read`), Write Only via Bounded Push Messages (`< 10 KB`):** Never write or edit files under `/workspace/<program-slug>/` directly from `GA`/`AGY`. Use `decision_log` (~1.5s) and `dav_read` (with ETag cache) for reads, and `request_work_order` / `send_message` (`< 10 KB`) for writes.
4. **One Project Per Session (`SESSION_PROJECT_LOCKED`) & One Program Per Project (`ONE_PROGRAM_PER_PROJECT`):** Start a new `GA`/`AGY` chat session when switching to a different Scion project, and create a new Scion project for each distinct drug discovery program.
5. **Never Use `oase hypothesis adopt` for SciArchitect Bundles:** Always stage the 7-part seed bundle to `/workspace/.seed/<slug>/` (`CHECKSUMS.json` last) and ingest via `oase coscientist ingest <export_file>` so zero fields, citations, or debate logs are lost.
6. **Always Verify `oase validate check --preflight` Before Submitting a Work Order:** Checks SHA-256 sidecars, JSON schemas, threshold citations, mandatory `[relay:<code>]` tags, and `{source: raw/...}` JSONPath numerical claims in seconds.

### 7.2 Quick Command Cross-Reference (Surface MCP vs. `pharma-cli dde` vs. Container `oase` CLI)

| Task | From `GA` / `AGY` (`scion` MCP Tool) | From Workstation CLI (`pharma-cli dde`) | Inside OASE Agent Container (`oase` CLI) |
|---|---|---|---|
| **Create Project & Assign Team** | `scion:create_project` | `pharma-cli dde create-project --name ... --member ...` | *(Forbidden: requires `UserIdentity` token)* |
| **Launch Campaign + Seed** | `scion:bootstrap_campaign` | `pharma-cli dde bootstrap-campaign ...` | `oase doctor` → `oase init /workspace/<slug>` |
| **Read Latest Decisions (`DEC-###`)** | `scion:decision_log` (`limit: 10`) | `pharma-cli dde decision-log --limit 10` | Read `program-state/decision-log.md` |
| **Read Workspace File (`L0–L4`)** | `scion:dav_read` (`path`, `head_lines`/`section`) | `pharma-cli dde dav-read <path>` | Read `/workspace/<slug>/<path>` |
| **Request New Work Order (`WO-*`)** | `scion:request_work_order` | `pharma-cli dde request-work-order ...` | `oase workorder create --from wo.json --commit` |
| **Validate Work Order (10 Checks)** | Read via `scion:dde_finding` | `pharma-cli dde finding --wo WO-004` | `oase validate check WO-004` |
| **Build & Export 28-Page Portal** | Request `project-curator` via `send_message` | Download `_site/<slug>-site.zip` via WebDAV | `oase site build && oase site validate && oase site export` |

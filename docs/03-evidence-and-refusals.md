# Module 03 — Evidence, Viewers & Refusals: Vertex AI `AlphaGenome`, `AlphaFold 3`, 10-Check Validation & Negative Gates

> **Duration:** 40 Minutes (`0:50 – 1:30`)  
> **Hands-On Goal:** Execute live **Vertex AI AlphaGenome**, **Vertex AI AlphaFold 3**, **`fpocket`**, and **`RDKit`** calls; step through `ch2`→`ch4` in `stage0-1-walkthrough`; run `oase validate check` (381 sidecars, 67 JSONPath claims) and `oase site build` (28-page portal with 14 interactive viewers); and audit how OASE refused 8/8 flawed concepts in `Pilot-9b` and caught 4 costly CRO traps in `Pilot-6`.

---

## 1. Live Exercise 3.1: Score a Regulatory Variant with Vertex AI `AlphaGenome` (`~5 sec`)

In Stage 1 (`target-genetic-evidence`), the `Computational Biologist` combines population constraint (`oase genetics fetch` on gnomAD) and GWAS associations (`oase gwas`) with **Vertex AI AlphaGenome** to test whether disease-associated non-coding variants actually perturb transcription or chromatin accessibility in the relevant tissue.

Run a live **Phase 1 (`score-variant`)** + **Phase 2 (`analyze`)** sequence against our Vertex AI AlphaGenome Dedicated Endpoint:

```bash
source /scion-volumes/tools/env.sh
export OASE_PROJECT=/workspace/live-sandbox

# Phase 1 (Online — Vertex AI Dedicated Endpoint via GCE ADC, ~4-6 seconds):
# Score a variant across RNA_SEQ and ATAC modalities using the geneMask scorer
oase alphagenome score-variant \
  --chrom chr11 \
  --pos 102943000 \
  --ref C \
  --alt T \
  --output-type RNA_SEQ \
  --output-type ATAC \
  --scorer geneMask

# Phase 2 (100% Offline-Latched — <1 second):
# Apply .oase/thresholds.yaml to emit the structured .analysis.json verdict
oase alphagenome analyze raw/genomics/chr11-102943000-C-T.scores.json
```

Inspect the three files written under `/workspace/live-sandbox/raw/genomics/`:
1. `chr11-102943000-C-T.scores.json` (and `.response.ndjson`) — Raw Layer 0 bytes.
2. `chr11-102943000-C-T.meta.json` — Cryptographic SHA-256 provenance sidecar recording the Vertex endpoint URL, `env_version`, and ADC credential source.
3. `chr11-102943000-C-T.analysis.json` — Structured verdict, `thresholds_applied`, and mandatory relay codes (such as `alphagenome.band_modality_mismatch` when extrapolating RNA-seq magnitude bands to ATAC).

---

## 2. Live Exercise 3.2: 3D Structure Confidence, `fpocket` Druggability & Vertex AI `AlphaFold 3` Co-Folding

Next, step into the shoes of the `Structural Biologist` and `Computational Chemist`:

### Step A: Fetch & Analyze Monomer Confidence + Druggable Pockets (`~8 sec`)

```bash
# 1. Fetch canonical structure & PAE matrix for Human MMP13 (UniProt P45452)
#    Automatically cross-checks canonical length against UniProt REST API!
oase alphafold fetch P45452
oase alphafold analyze P45452

# 2. Run fpocket druggability detection on the structure (<4 seconds)
oase pocket run raw/structures/AF-P45452-F1.cif
oase pocket analyze raw/structures/AF-P45452-F1.pockets.json
```

Inspect `raw/structures/AF-P45452-F1.analysis.json` to see the automatic mandatory relays emitted by OASE (`afdb.confidence_is_not_accuracy` and `afdb.model_is_not_docking_ready`).

### Step B: Generate & Submit a Vertex AI `AlphaFold 3` Co-Folding Payload

When a program needs de novo complex prediction—such as a protein-protein interface (`--template complex`) or a **protein + small-molecule SMILES co-fold (`--template ligand`)**—OASE calls the **Vertex AI AlphaFold 3 Dedicated Endpoint**:

```bash
# 1. Generate a canonical AlphaFold 3 protein-ligand co-folding input template
oase alphafold predict --template ligand > /tmp/af3_ligand_demo.json
cat /tmp/af3_ligand_demo.json

# 2. (Optional Live Submission) Submit to the Vertex AI AlphaFold 3 endpoint
#    Note: Cold-start or full diffusion takes ~5-10 min and is serialized via ~/.cache/oase/af3.lock.
#    For instant inspection, jump to ch3 in stage0-1-walkthrough below!
```

### Step C: Fast-Forward Through `ch2-stage1-omics` and `ch3-stage1-structure` (`<2 sec`)

Let's use our Time-Machine in `stage0-1-walkthrough` (`pilot-10`) to inspect the completed Stage 1 omics (`ch2`) and structural/chemistry (`ch3`) artifacts:

```bash
cd /workspace/stage0-1-walkthrough

# Jump to Checkpoint 2: Stage 1 Omics (GTEx bulk null vs. cirrhotic single-cell oase h5ad)
/workspace/workshop/scripts/checkpoint.sh goto ch2

# Jump to Checkpoint 3: Stage 1 Structure, Pocket & Chemistry Complete
/workspace/workshop/scripts/checkpoint.sh goto ch3
```

---

## 3. Live Exercise 3.3: Run the 10-Check Mechanical Validator & Build the 28-Page Evidence Portal (`ch4`)

Now advance to **Checkpoint 4 (`ch4-site-published`)** and run the exact mechanical validation and site-compilation commands that the `Research Operations Controller` executes before publishing any campaign:

```bash
cd /workspace/stage0-1-walkthrough
/workspace/workshop/scripts/checkpoint.sh goto ch4

source /scion-volumes/tools/env.sh

# 1. Run all 10 mechanical validation checks (advisory preflight mode) on Work Order WO-005
oase --project /workspace/stage0-1-walkthrough validate check --dry-run WO-005

# 2. Validate cross-links and provenance across the entire campaign
oase --project /workspace/stage0-1-walkthrough site validate

# 3. Compile the self-contained 28-page static HTML evidence portal (<3 seconds, 100% offline)
oase --project /workspace/stage0-1-walkthrough site build
```

Open the generated `_site/index.html` in your browser (via the Scion file browser or preview server). Across `pilot-10`, `oase validate check` verified **381 SHA-256 `.meta.json` sidecars and 67 `{source: raw/... $.jsonpath}` inline numerical claims** with zero errors, and `oase site build` rendered **14 interactive scientific viewers**:
- `plddt-viewer` & `pae-viewer` (per-residue confidence & domain error heatmaps)
- `constraint-viewer` (gnomAD `pLI` / `LOEUF` intolerance distributions)
- `expression-viewer` (GTEx / HPA / single-cell cluster expression charts)
- `tournament-viewer` (`Hypex` 103-match ELO network & debate brackets)
- `docking-viewer`, `admet-viewer`, `mpo-viewer`, `selectivity-viewer`, `pk-viewer`, `trials-viewer`, `faers-viewer`, `pathway-viewer`, and `dossier-viewer`.

---

## 4. Auditing the Refusal Track Record: How OASE Saves Wet-Lab & CRO Dollars

A platform that says `GO` to every target is a liability. Let's inspect three real campaigns where GCP-OASE's falsification gates halted flawed hypotheses *before* wet-lab spend:

### Case Study 1: `negative-gate-audit` (`Pilot-9b` — Hidradenitis Suppurativa Stage 0)
Switch to `/workspace/negative-gate-audit` in Scion:

```bash
cd /workspace/negative-gate-audit
ls -la decisions/
```

- **What entered:** 8 therapeutic target concepts for Hidradenitis Suppurativa (HS) across 153 logged decisions (`DEC-001`..`DEC-153`).
- **What OASE caught:**
  1. In **`WO-001`**, `oase litref resolve` and `oase cite` caught upstream seed citation-padding (references cited in the initial seed brief that did not support the claimed HS mechanism).
  2. Across Stage 0 validation, 7 of the 8 concepts failed primary human genetic or clinical trial counter-evidence checks, and 1 was held as exploratory.
- **Final Decision (`DEC-145`):** **0 of 8 concepts advanced past Stage 0.** Instead of rubber-stamping the "least bad" target, `science-program-lead` closed the gate with a full counterfactual audit trail explaining what human evidence would be required to reopen each hypothesis.

### Case Study 2: `Pilot-6` (NSCLC EZH2/EED PROTAC Campaign)
Across a 5-stage oncology degrader campaign, OASE caught **four expensive preclinical traps** before a single dollar of CRO spend:

| Decision ID | Preclinical Trap | How OASE Caught It | Wet-Lab / CRO Cost Avoided |
|---|---|---|---|
| **`DEC-006`** | **Literature Bias (`LAIR1`):** High paper volume suggested `LAIR1` as a primary NSCLC target. | `Computational Biologist` cross-checked knockout mouse survival phenotypes (`oase phenotype`) and primary patient survival cohorts, refuting the literature consensus and pivoting to `EZH2`/`EED`. | Avoided a 6-month dead-end target validation campaign. |
| **`DEC-009`** | **Mutant Control Cell Line (`A549`):** Standard CRO protocol proposed `A549` cells as the wild-type control. | Agent queried DepMap / cancer genomics (`oase cbioportal`) and flagged that `A549` carries `STK11`/`KEAP1` mutations that confound the pathway readout—substituting a clean wild-type line before ordering the CRO assay. | Saved `$50K–$150K` in invalidated CRO cell-panel screening. |
| **`DEC-032`** | **Weak VHL Warhead (`1,000x` Kd Loss):** Early linker-warhead series showed poor potency. | `Medicinal Chemist` + `Computational Chemist` flagged a `1,000x` binding affinity drop on the VHL warhead arm and halted synthesis of that series. | Saved weeks of custom PROTAC synthesis at a chemistry CRO. |
| **`DEC-034`** | **Ternary Complex Uncertainty (`EED226-CRBN`):** Needed proof that the redesigned CRBN-recruiting degrader forms a stable ternary complex without steric clash. | `Structural Biologist` ran **Vertex AI AlphaFold 3 co-folding** (`oase alphafold predict`), confirming `EED226-CRBN` ternary complex stability at **`ipTM 0.88`** before committing to synthesis. | De-risked custom ternary degrader synthesis with high-confidence 3D geometry. |

---

**Next Step:** Proceed to [Module 04 — Make It Yours & Wet-Lab Handoffs](04-make-it-yours.md).

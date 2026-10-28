# Module 02 — Stage 1 Target Validation: Human Genetics, AlphaGenome on GCP & Single-Cell Slicing (`ch2`)

> **Duration:** 25 Minutes (`0:35 – 1:00`)  
> **Hands-On Goal:** Escalate a decision-grade Stage 1 work order (`request_work_order`), execute Phase-1 (`fetch`/`score-variant`) and Phase-2 (`analyze`) commands across `oase genetics`, `oase gwas`, `oase gtex`, and **AlphaGenome on GCP** (`WO-002` & `WO-003`), run `oase validate check`, approve the Stage 1 Gate (`DEC-004`), and audit two real Stage 0/1 case studies (`Pilot-10` cirrhotic `.h5ad` slicing and `Pilot-9b` `DEC-145`).

---

## 1. Exercise 2.1 — Escalating a Decision-Grade Question from `GA`/`AGY` (`request_work_order`)

Fast exploratory queries (`2–30s`) can run directly on the `GA`/`AGY` surface, but any finding that will be cited in a `DEC-###` entry or Stage Gate must be escalated via `request_work_order` so OASE executes Phase 1 (`.meta.json` SHA-256 sidecar) + Phase 2 (offline `.analysis.json`) + Dual Validation:

```json
{
  "ServerName": "scion",
  "ToolName": "request_work_order",
  "Arguments": {
    "project_id": "<oral-pcsk9-ascvd-uuid>",
    "program_slug": "pcsk9-oral",
    "target_role": "computational-biologist",
    "title": "Stage 1 Human Genetic Constraint, GTEx Tissue Selectivity & AlphaGenome Regulatory Variant Scoring for PCSK9",
    "question": "1. Quantify human loss-of-function constraint (gnomAD pLI/LOEUF) and protective ASCVD associations (OpenTargets, ClinVar R46L rs11591147, Y142X) for PCSK9. 2. Quantify multi-tissue RNA expression across 54 GTEx tissues to verify hepatocyte restriction. 3. Score PCSK9 regulatory variant chr1:55039974:G>T (rs2479409) using AlphaGenome on GCP across RNA_SEQ, DNASE, and CAGE in human liver."
  }
}
```

---

## 2. Exercise 2.2 — Phase-1 & Phase-2 Stage 1 Commands (`WO-002` & `WO-003`)

### Step A: Human Loss-of-Function Constraint (`oase genetics`)
```bash
# Phase 1: Fetch gnomAD constraint metrics for PCSK9 into raw/genomics/ (+ .meta.json)
oase --project /workspace/pcsk9-oral genetics fetch PCSK9

# Phase 2 (offline): Apply genetics@1.0 thresholds (pLI=0.90, LOEUF=0.35)
oase --project /workspace/pcsk9-oral genetics analyze PCSK9 --pli 0.90 --loeuf 0.35
```
- **Output (`raw/genomics/PCSK9_gnomad.analysis.json`):** `pLI = 0.0001`, `loeuf = 0.89` (`loss-of-function-tolerant`), confirming complete human `PCSK9` loss of function is viable and non-essential. Emits mandatory relay **`**Relay: \`gnomad.constraint_is_not_safety\`**`**.

### Step B: Human Genetic Association & Protective LoF Alleles (`oase gwas`)
```bash
# Phase 1: Query OpenTargets Platform and ClinVar for PCSK9
oase --project /workspace/pcsk9-oral gwas search PCSK9 --source opentargets
oase --project /workspace/pcsk9-oral gwas search PCSK9 --source clinvar

# Phase 2 (offline): Filter and score associations against gwas@1.0 threshold (0.70)
oase --project /workspace/pcsk9-oral gwas analyze PCSK9 \
  --source opentargets \
  --threshold 0.70 \
  --disease-filter "hypercholesterolemia"
```
- **Output (`raw/genomics/PCSK9_opentargets.analysis.json`):** Overall association score `0.96` for hypercholesterolemia / ASCVD; protective human LoF variants `rs11591147` (`R46L`) and `Y142X` confer lifelong LDL-C lowering and `68.0%` coronary heart disease risk reduction without adverse hepatic or neurocognitive phenotypes.

### Step C: Multi-Organ Expression Selectivity (`oase gtex`)
```bash
# Phase 1 & Phase 2 (offline): Fetch and analyze median TPM across 54 GTEx v8 tissues
oase --project /workspace/pcsk9-oral gtex fetch PCSK9
oase --project /workspace/pcsk9-oral gtex analyze PCSK9
```
- **Output (`raw/gtex/PCSK9.analysis.json`):** `Liver` is rank `#1` (`184.2 TPM`) with tissue specificity index `Tau = 0.93`.

### Step D: Live AlphaGenome 1 Mb Regulatory Variant Scoring on GCP (`oase alphagenome`)
```bash
# Phase 1 (Dedicated GCP AlphaGenome Endpoint via GCE ADC):
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
  raw/genomics/chr1_55039974_G_T.json \
  --quantile-significance 0.95 \
  --raw-score-moderate 0.10
```
- **Output (`raw/genomics/chr1_55039974_G_T.analysis.json`):** Liver `RNA_SEQ` quantile `0.984`, raw log-fold-change `-0.24`, and `DNASE` quantile `0.962`.
- *(Parallel Track Callout: For `prmt5-mtap` in MTAP-deleted solid tumors, this step runs `oase cbioportal` on `9p21 CDKN2A/MTAP` homozygous co-deletion and `oase alphagenome score-variant` at the `9p21` regulatory locus.)*

---

## 3. Exercise 2.3 — Mechanical Validation (`oase validate check`) & Stage 1 Gate Approval (`DEC-004`)

```bash
# Run preflight check during authoring, or full check upon submission:
oase --project /workspace/pcsk9-oral validate check WO-003 --preflight
oase --project /workspace/pcsk9-oral validate check WO-003

# Or inspect the pre-computed ch2 artifacts directly:
./scripts/checkpoint.sh goto ch2
cat checkpoints/ch2/findings/computational-biology/WO-002.md
cat checkpoints/ch2/findings/computational-biology/WO-003.md
```

Once Validation 1 (`validation_passed`) and Validation 2 (`DEC-004` / `scientifically_accepted`) complete, the Project Owner approves the Stage 1 → Stage 2 Gate via `scion:send_message`:

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

## 4. Real-Run Case Studies: When Stage 0/1 Biology Surprises You

### Case Study A (`Pilot-10` Hepatic Fibrosis): Slicing Cirrhotic Single-Cell `.h5ad` Matrices When Bulk GTEx Is Null
In `Pilot-10` (Hepatic Fibrosis), bulk healthy liver RNA-seq from GTEx (`oase gtex fetch`) returned `<0.5 TPM` for extracellular matrix remodeling target `MMP13`, because activated stellate/mesenchymal cells only expand inside **cirrhotic** liver. Instead of dropping the target on a healthy-tissue null, `science-program-lead` opened `OQ-017` and ran `oase h5ad` across 5 cirrhotic human liver single-cell samples (`GSE212046`, `PRJNA913603`):

```bash
# Phase 1: Download verbatim 10x H5 / H5AD matrices + per-cell label TSVs into raw/single-cell/
oase h5ad fetch GSM6508438 GSM6508440 --source disco

# Phase 2 (offline): Extract per-cell counts with ACTB positive control
oase h5ad analyze GSM6508438 GSM6508440 \
  --source disco \
  --gene MMP13 --gene MMP1 --gene MMP8 \
  --select-label "CFD+MGP+ fibroblast" \
  --control ACTB
```
- **Zero Label Guessing:** None of the 5 DISCO cirrhosis samples contained a label literally named `"stellate"` (the atlas uses `"CFD+MGP+ fibroblast"`, `"CCL19+APOE+ fibroblast"`, `"Mesenchymal stromal cell"`). Passing `--select-label "Activated stellate cell"` exits with code `2` and prints the exact vocabulary present rather than guessing.
- **`searched_absent` (`NA`) vs. Measured Zero (`0`):** On a provider-filtered `12,621`-gene CELLxGENE matrix where `MMP13` was omitted from `var_names`, `oase h5ad` stamps `parse_status: "searched_absent"` (`value: null` / `NA`) alongside positive control `ACTB` (`parse_status: "measured"`), preventing an unmeasured gene from being falsely reported as `0.0` expression.

### Case Study B (`Pilot-9b` Hidradenitis Suppurativa `DEC-145` & `Pilot-9c` `DEC-248`): Terminating 8 of 8 Flawed Targets
In `Pilot-9b` (`/workspace/negative-gate-audit`), 8 therapeutic target concepts (`IC-001`..`IC-008`) entered Stage 0 evaluation across 153 logged decisions (`DEC-001`..`DEC-153`):
1. **Citation Forensics (`findings/reviews/seed-citation-attestation-audit.md`):** An independent audit verified every PMID via `oase litref resolve` and proved that the upstream generator had attached a shared block of generic background PMIDs to every target to pass a `len(verified_pmids) >= 3` check.
2. **Human Genetic & Clinical Counter-Evidence:** 7 of the 8 concepts failed primary human genetic or Phase 2b clinical trial counter-evidence checks, and 1 (`IC-006`) was parked—resulting in **`DEC-145`: 0 of 8 concepts advanced past Stage 0**.
3. **Post-Seal Enforcement (`Pilot-9c` `DEC-248`):** When `science-program-lead` attempted to append `DEC-247` after `DEC-246` sealed `decision-log.md` read-only, the tool refused the write (`DEC-248: "The seal caught the lead"`), forcing post-gate notes into `decision-log-POST-SEAL-ADDENDUM.md`.

---

**Next Step:** Proceed to [Module 03 — Stage 2 Structure, AlphaFold 3 Co-Folding on GCP, `fpocket` & AutoDock Vina (`ch3`)](03-structure-docking-af3.md).

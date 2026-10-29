# Upstream AI Co-Scientist Research Brief & Downstream Campaign Cascade (`pcsk9-oral`)

> **Canonical Seed Files:** [`checkpoints/ch0/seed/pcsk9-oral/campaign-seed.json`](../checkpoints/ch0/seed/pcsk9-oral/campaign-seed.json) · [`checkpoints/ch0/seed/pcsk9-oral/coscientist-export.json`](../checkpoints/ch0/seed/pcsk9-oral/coscientist-export.json)  
> **Session ID:** `daedalis-20261028-pcsk9-oral` (`oase coscientist ingest` → `WO-001`)

In Initiation Mode 1, **how the human discovery lead defines the upstream AI Co-Scientist research goal, modality preferences, and falsifiable kill criteria determines the shape of the entire downstream Grove**—which parallel modality tracks open, which cutoffs are locked in `.oase/thresholds.yaml`, and where the campaign switches tracks if biological or chemical measurements surprise the team.

---

## 1. The Structured Research Brief (Input Prompt & Constraints)

```yaml
title: "Oral Small-Molecule & Macrocycle PCSK9 Inhibitors in ASCVD"

research_goal: >
  Evaluate oral allosteric small-molecule and tricyclic macrocycle PCSK9 inhibitors
  disrupting LDLR EGF-A binding in Atherosclerotic Cardiovascular Disease (ASCVD) /
  Hypercholesterolemia as a room-temperature, once-daily alternative to injectable
  monoclonal antibodies.

program_directive: >
  Evaluate oral allosteric PCSK9 inhibitors in ASCVD using human genetics,
  AlphaGenome regulatory variant scoring on GCP, AlphaFold 3 pocket modeling on GCP,
  and oral macrocycle/small-molecule SAR.

hard_preferences:
  - "Prioritize classical oral bioavailability (Rule-of-5 hepatocyte permeability without dietary permeation enhancers)"
  - "Enforce human loss-of-function genetic validation (PCSK9 R46L / germline LoF cardioprotection) and hepatic tissue selectivity"

pre_registered_falsifiable_predictions:
  FP-001 (Allosteric Small Molecule — Concept IC-001):
    test: "fpocket & AlphaFold 3 co-folding of PCSK9 (Q8NBP7) identifies a cryptic inter-domain pocket with druggability >= 0.50 and ligand ipTM >= 0.70."
    kill_criterion: "Druggability score < 0.30 or steric clash across all low-energy conformers."
  FP-002 (Orthosteric Tricyclic Macrocycle — Concept IC-002):
    test: "Interface contact mapping on the EGF-A patch confirms hot-spot coverage benchmarked against clinical macrocycle MK-0616."
    kill_criterion: "Loss of EGF-A hot-spot engagement or unbound hepatic clearance / permeation-enhancer dependence incompatible with unenhanced QD oral dosing."

sponsor_gate_policy: "manual" # Requires explicit human Program Lead co-sign at Gate 1, Wet-Lab Handoff, and Gate 4
```

---

## 2. How Each Clause of the Input Prompt Cascades Downstream

| Input Prompt Clause | Immediate Stage 0 (`WO-001`) Effect | Downstream `.oase/thresholds.yaml` & Subway Track Effect |
| :--- | :--- | :--- |
| **"Prioritize classical oral bioavailability without permeation enhancers"** | Ranks allosteric small molecule **`IC-001` (`1642.5 Elo`, `10W-2L`)** `#1` (`+54.5 Elo`) while retaining tricyclic macrocycle **`IC-002` (`1588.0 Elo`, `8W-4L`)** on a parallel **Backup Line** instead of discarding it. | Locks `max_clogp: 3.5` and `max_mw: 500` in Stage 3—which **disqualifies top docker `PCSK9-A02` (`cLogP = 5.09`, Aronov `hERG`)**, triggers the **`BRICS` polar oxadiazole reroute (`OASE-PCSK9-014`)**, and requires an **audited human override (`DEC-OVERRIDE-001`)** to advance macrocycle backup `PCSK9-B07` (`MW > 500 Da`) in Step 6. |
| **"Enforce human LoF genetic validation & hepatocyte selectivity"** | Requires Stage 1 verification before any 3D GPU co-folding spend is authorized. | Spawns `WO-002` (`gnomAD pLI < 0.90`, `OpenTargets >= 0.70`, `GTEx >= 100 TPM`) and `WO-003` (`AlphaGenome` `rs2479409 >= 0.95`). If bulk `GTEx` returned `<5 TPM`, `@science-program-lead` routes a **single-cell `oase h5ad` detour** rather than dropping the target. |
| **Pre-registered `FP-001` (`druggability >= 0.50`, `ipTM >= 0.70`, kill `< 0.30`)** | Converts prose hypotheses into machine-checkable Stage 2 Structural Biology contracts (`WO-004` & `WO-005`). | In Step 3, flat `EGF-A` scores `0.24` (terminating the orthosteric Rule-of-5 spur) while cryptic `Pocket #1` scores `0.68` (`0.788` live apo), keeping `Line A` (`IC-001`) open. Had `Pocket #1` scored `<0.30`, `Line A` would terminate at Gate 2 and transfer the campaign onto **Backup Line `IC-002`**. |
| **`sponsor_gate_policy: "manual"` + Adopted Seed Provenance** | Stamps `raw/hypotheses/` with SHA-256 receipt and attaches mandatory caveat `hypothesis.adopted_not_generated`. | Forces every upstream Co-Scientist literature claim to be independently re-verified by deterministic Phase-1/Phase-2 tools before **Gate 1** can be co-signed. |

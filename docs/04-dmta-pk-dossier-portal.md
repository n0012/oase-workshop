# Module 04 — Stages 3 & 4 DMTA Lead Optimization, Oral PK Scaling, Wet-Lab Re-Ingestion & Portal Export (`ch4`)

> **Duration:** 35 Minutes (`1:25 – 2:00`)  
> **Hands-On Goal:** Inject medicinal chemistry constraints (`WO-006`: `oase mmp`, `oase admet`, `oase retro`) to optimize `pcsk9_analog_02` into **`OASE-PCSK9-014`**; re-analyze Layer 0 artifacts offline under modified `.oase/thresholds.yaml` cutoffs (`<0.2s`, `$0` cost); re-ingest wet-lab / CRO assay data (`oase assay`, `oase selectivity`, `oase pk`); compile the Stage 4 IND dossier and 28-page static HTML portal (`WO-007` & `WO-008`, `ch4`); and run 4 validation & override exercises.

---

## 1. Exercise 4.1 — Stage 3 DMTA Lead Optimization (`WO-006`: `oase mmp`, `oase admet`, `oase retro`)

`pcsk9_analog_02` has strong predicted docking energy (`-9.4 kcal/mol`) but carries Liability `L-002` (`cLogP = 4.8` and basic-amine hERG risk on its quinoline ring). The Medicinal Chemist dispatches `WO-006` via `scion:request_work_order`:

```bash
# 1. BRICS Fragmentation & Matched Molecular Pair (MMP) SAR Analysis (oase mmp)
oase --project /workspace/pcsk9-oral mmp fragment \
  "Cc1ccc(C(=O)Nc2ccc(CN3CCN(c4ccnc5ccccc45)CC3)cc2)cc1F"
oase --project /workspace/pcsk9-oral mmp pairs raw/compounds/pcsk9_ic001_series.smi
oase --project /workspace/pcsk9-oral mmp analyze raw/mmp/pcsk9_ic001_series.mmp.json

# 2. Batch ADMET, ChEMBL Structural Alerts & Tox21 Profiling (oase admet)
oase --project /workspace/pcsk9-oral admet predict-batch raw/compounds/pcsk9_ic001_series.smi
oase --project /workspace/pcsk9-oral admet analyze raw/admet/pcsk9_ic001_series.admet.json

# 3. ASKCOS Retrosynthetic Tractability Assessment (oase retro)
oase --project /workspace/pcsk9-oral retro search \
  "COc1ncc(N2CCN(Cc3ccc(NC(=O)c4ccc(C)c(F)c4)cc3)CC2)cn1" --max-results 5
oase --project /workspace/pcsk9-oral retro analyze \
  "COc1ncc(N2CCN(Cc3ccc(NC(=O)c4ccc(C)c(F)c4)cc3)CC2)cn1" --threshold 0.60
```

- **Outcome (`DEC-008` & `DEC-009`, Liability `L-002` Mitigated):** Replacing the quinoline ring with a 2-methoxypyrimidine bioisostere (**`OASE-PCSK9-014`**) lowers `cLogP` from `4.8 → 3.1`, raises `LipE` from `3.4 → 5.2`, maintains `MW = 462.5 Da` and `TPSA = 88.4 Å²`, clears all ChEMBL/PAINS structural alerts (`0` alerts), and achieves a convergent **4-step synthesis** from commercial building blocks (plausibility `0.87`).

---

## 2. Exercise 4.2 — Offline Threshold Tuning (`--overwrite`) & Wet-Lab / CRO Assay Re-Ingestion

### Offline Phase-2 Re-Analysis (`<0.2s`, `$0` Compute Cost)
Because all 51 `oase <tool> analyze*` commands are network-latched offline and read from `raw/`, you can tighten or relax cutoffs in `.oase/thresholds.yaml` and re-compute verdicts without re-running GCP GPU endpoints. Without `--overwrite`, OASE refuses a conflicting analysis overwrite with exit code `9` to prevent silent tampering:

```bash
# Edit .oase/thresholds.yaml (e.g. tighten max_clogp to 3.0) and re-run Phase 2 offline:
oase --project /workspace/pcsk9-oral admet analyze \
  raw/admet/pcsk9_ic001_series.admet.json --overwrite
```
In the updated `.analysis.json`, `threshold_sources` flips from `"default"` to `"program_override"`.

### Configurable Stopping Gates & Wet-Lab / CRO Data Re-Ingestion
Programs can pause after Stage 1 (target validation) or Stage 2 (virtual screening) at zero compute cost while internal bench scientists or CROs (WuXi AppTec, Charles River, Eurofins) run physical assays, then re-ingest the returned CSV/JSON files directly into `raw/`:

```bash
# 1. Ingest and analyze biochemical/cellular IC50 assay results (oase.assay.v1)
oase --project /workspace/pcsk9-oral assay ingest raw/assays/cro-batch-01.json
oase --project /workspace/pcsk9-oral assay analyze raw/assays/cro-batch-01.assay.json

# 2. Compute off-target selectivity fold-margins against safety panels (oase.selectivity-panel.v1)
oase --project /workspace/pcsk9-oral selectivity compare raw/assays/selectivity-panel-01.json
oase --project /workspace/pcsk9-oral selectivity analyze raw/assays/selectivity-panel-01.selectivity.json
```
> **Standing Rule (`docs/tool-design-guidance.md` §1.1):** Measurements always outrank predictions. When an `AutoDock Vina` or `RDKit ADMET` prediction disagrees with a re-ingested experimental `oase assay` measurement, OASE surfaces the disagreement itself as the finding for the next DMTA cycle.

---

## 3. Exercise 4.3 — Stage 4 Oral PK Scaling, Clinical Differentiation, IND Dossier & 28-Page Portal (`WO-007` & `WO-008`, `ch4`)

```bash
# 1. 4-Step Rat/Dog IV/PO NCA & 70 kg Human Allometric Oral PK Projection (WO-007)
oase --project /workspace/pcsk9-oral pk ingest raw/pk/oase_pcsk9_014_rat_iv_po.json
oase --project /workspace/pcsk9-oral pk ingest raw/pk/oase_pcsk9_014_dog_iv_po.json
oase --project /workspace/pcsk9-oral pk nca raw/pk/oase_pcsk9_014_rat_iv_po.pk.json --blq-method loq-half
oase --project /workspace/pcsk9-oral pk nca raw/pk/oase_pcsk9_014_dog_iv_po.pk.json --blq-method loq-half
oase --project /workspace/pcsk9-oral pk scale \
  raw/pk/oase_pcsk9_014_rat_iv_po.nca.json \
  raw/pk/oase_pcsk9_014_dog_iv_po.nca.json \
  --human-bw 70.0 --target-auc 12.5 --target-cmax 2.0
oase --project /workspace/pcsk9-oral pk analyze raw/pk/oase_pcsk9_014_scaled_pk.json

# 2. Clinical Trial Landscape & OpenFDA FAERS Safety Benchmarking vs. Evolocumab & MK-0616 (WO-008)
oase --project /workspace/pcsk9-oral trials search "PCSK9 hypercholesterolemia" --by condition
oase --project /workspace/pcsk9-oral trials analyze "PCSK9 hypercholesterolemia"
oase --project /workspace/pcsk9-oral faers search "evolocumab" --max-results 100
oase --project /workspace/pcsk9-oral faers analyze "evolocumab"

# 3. Preclinical IND Dossier & 28-Page Static HTML Evidence Portal Export
oase --project /workspace/pcsk9-oral dossier check
oase --project /workspace/pcsk9-oral dossier export WO-008 --format markdown
oase --project /workspace/pcsk9-oral site build
oase --project /workspace/pcsk9-oral site validate
oase --project /workspace/pcsk9-oral site export --output /workspace/pcsk9-oral/pcsk9-oral-site.zip
```

Inspect the completed Stage 4 checkpoint (`checkpoints/ch4/`):
```bash
./scripts/checkpoint.sh goto ch4
cat checkpoints/ch4/program-state/decision-log.md
cat checkpoints/ch4/program-state/liability-tracker.md
```

---

## 4. Exercise 4.4 — Four Validation & Override Exercises (`oase validate check`)

In `checkpoints/ch4/`, test how `oase validate check` catches mechanical and epistemic errors:

1. **Missing Mandatory Relay (`relay_coverage`):**
   - *Test:* Remove `**Relay: \`docking.score_is_not_affinity\`**` from `findings/computational-chemistry/WO-005.md`.
   - *Result:* `oase validate check WO-005` fails on `relay_coverage` (`COMPLETENESS`), listing `docking.score_is_not_affinity` as unaddressed.
2. **Out-of-Tolerance JSONPath Numerical Claim (`source_tags_resolve`):**
   - *Test:* In `findings/structural-biology/WO-004.md`, change `0.68 {source: raw/pocket/Q8NBP7_pockets.analysis.json $.metrics.pocket1_druggability}` to `0.85`.
   - *Result:* `oase validate check WO-004` parses `$.metrics.pocket1_druggability`, compares `0.85` against `0.68` (`> ±1%` tolerance), and rejects the work order.
3. **Single-Cell `searched_absent` (`NA`) vs. Measured Zero (`0.0`) (`oase h5ad`):**
   - *Rule:* When a gene is absent from a provider-filtered `.h5ad` feature list, `oase h5ad` emits `parse_status: "searched_absent"` (`value: null`) alongside positive control `ACTB` (`parse_status: "measured"`). Never report `searched_absent` as zero expression.
4. **Accepting Valid Layer 0 Data While Overriding Specialist Interpretation (`oase workorder override`):**
   - *Scenario:* `WO-006` passes all 10 mechanical checks (Validation 1), so its Layer 0 data is valid, but a specialist over-interprets a marginal `0.2 kcal/mol` docking difference.
   - *Remedy:* Run `oase workorder override WO-006 --actor science-program-lead --reason "..." --evidence raw/docking/...` to log `DATA ACCEPTED / INTERPRETATION OVERRIDDEN` in `DEC-009` (`events.ndjson: direction_override`), preserving the valid Layer 0 data while recording the corrected scientific conclusion in Layer 2.

---

**Next Step:** Proceed to [Module 05 — Extending OASE with Custom Tools (`Tool → Skill → Template`)](05-extend-custom-tools.md).

# Module 03 — Stage 2 Structure, AlphaFold 3 Co-Folding on GCP, `fpocket` & AutoDock Vina (`ch3`)

> **Duration:** 25 Minutes (`1:00 – 1:25`)  
> **Hands-On Goal:** Fetch and audit canonical protein structures (`oase alphafold fetch/analyze`), run **AlphaFold 3 protein-ligand co-folding on GCP** (`oase alphafold predict --template ligand` + `analyze-prediction` + `analyze-plddt`), score cavities with `fpocket` (`oase pocket run --strip-peptides` + `analyze`), execute 3-phase AutoDock Vina + Meeko docking (`oase docking prepare → run → analyze → contacts`), and inspect the 3D viewers (`ch3`).

---

## 1. Exercise 3.1 — Structural Biologist Work Order (`WO-004`): AFDB, AlphaFold 3 Co-Folding & `fpocket`

### Step A: Fetch & Analyze `PCSK9` (`Q8NBP7`) Structure and PAE Domains
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
- **Output (`raw/structures/Q8NBP7.analysis.json`):** Separates the disordered N-terminal signal/propeptide (`aa 1–60`, `pLDDT < 50`) from the well-folded prodomain + catalytic domain (`aa 61–454`, `pLDDT > 88`) and C-terminal Cys-His-rich domain (`aa 455–692`), and emits mandatory relays `afdb.confidence_is_not_accuracy` and `afdb.model_is_not_docking_ready`.

### Step B: Live AlphaFold 3 Protein + SMILES Co-Folding on GCP (`oase alphafold predict`)
```bash
# Phase 1 (Dedicated GCP AlphaFold 3 GPU Endpoint, serialized via ~/.cache/oase/af3.lock):
oase --project /workspace/pcsk9-oral alphafold predict \
  --input raw/structures/pcsk9_ic001_af3_ligand.json \
  --template ligand \
  --deadline 1800

# Phase 2a (offline): Evaluate AF3 summary confidences (ipTM, pTM, ranking_score, has_clash)
oase --project /workspace/pcsk9-oral alphafold analyze-prediction \
  raw/structures/pcsk9_ic001_af3_ligand/summary_confidences.json

# Phase 2b (offline): Extract per-atom B_iso_or_equiv pLDDT distribution from the AF3 mmCIF
oase --project /workspace/pcsk9-oral alphafold analyze-plddt \
  raw/structures/pcsk9_ic001_af3_ligand/model.cif
```
- **Input Template Rules:** Use `--template monomer` for single chains, `--template complex` for multi-chain PPIs, and `--template ligand` for protein + small-molecule SMILES or CCD codes.
- **Output (`WO-004`):** Ligand `ipTM = 0.84`, overall `pTM = 0.88`, `has_clash = 0.0`.
- *(Real-Run Note from `Pilot-6` NSCLC PROTAC `DEC-032` & `DEC-034`: When early linker-warhead series showed a `1,000x` binding affinity loss on the VHL arm (`DEC-032`), `structural-biologist` ran `oase alphafold predict` on GCP (`DEC-034`) to confirm `EED226-CRBN` ternary complex stability at `ipTM = 0.88` before committing to custom CRO synthesis.)*

### Step C: Cavity Detection & Druggability Scoring (`oase pocket`)
```bash
# Phase 1: Run compiled fpocket 4.2.2 on PCSK9 structure (stripping short co-crystallized peptides)
oase --project /workspace/pcsk9-oral pocket run \
  raw/structures/Q8NBP7.cif \
  --strip-peptides

# Phase 2 (offline): Apply pocket@1.0 druggability threshold (0.50) near the inter-domain groove
oase --project /workspace/pcsk9-oral pocket analyze \
  raw/pocket/Q8NBP7_pockets.json \
  --druggable 0.50 \
  --near "A:153,A:194,A:238,A:374,A:378"
```
- **Why `--strip-peptides` Is Required on Co-Crystal Complexes:** On experimental complexes such as `PDB: 2P4E` (which includes the bound `LDLR EGF-A` peptide chain), `--strip-peptides` removes bound peptide chains smaller than `--peptide-threshold` prior to running `fpocket` so the cavity is not occluded by the co-crystallized peptide.
- **Outcome (`DEC-005`):** Pocket #1 (`IC-001` inter-domain allosteric groove) scores **`druggability = 0.68`** (volume `740.0 Å³`), whereas the flat outer EGF-A surface targeted by `IC-002` scores **`druggability = 0.24`**. `science-program-lead` prioritizes `IC-001` as the primary small-molecule series and retains `IC-002` as the macrocycle comparator.

---

## 2. Exercise 3.2 — Computational Chemist Work Order (`WO-005`): 3-Phase AutoDock Vina + Pose Contacts

OASE separates molecular docking into `prepare → run → analyze` so the prepared receptor `.pdbqt` and 3D grid box are citable Layer 0 artifacts reused identically across all analog series:

```bash
# Phase 1a (Prepare): Convert receptor to PDBQT via Meeko and compute grid box from Pocket #1 centroid (+10 Å padding)
oase --project /workspace/pcsk9-oral docking prepare \
  raw/structures/Q8NBP7.cif \
  raw/pocket/Q8NBP7_pockets.json \
  --pocket-rank 1 \
  --protein-only

# Phase 1b (Run): Execute AutoDock Vina 1.2.5 across 5 curated ChEMBL PCSK9 allosteric analogs (< 90s on CPU)
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

# Phase 2a (Offline Analyze): Rank ligands against docking@1.0 thresholds
oase --project /workspace/pcsk9-oral docking analyze \
  raw/docking/runs/pcsk9_analog_01.dock.json \
  raw/docking/runs/pcsk9_analog_02.dock.json \
  raw/docking/runs/pcsk9_analog_03.dock.json \
  raw/docking/runs/pcsk9_analog_04.dock.json \
  raw/docking/runs/pcsk9_analog_05.dock.json

# Phase 2b (Offline Contacts): Compute < 4.0 Å receptor-ligand interactions and flag < 2.0 Å steric clashes
oase --project /workspace/pcsk9-oral docking contacts \
  raw/docking/runs/pcsk9_analog_02_poses.pdbqt \
  raw/docking/Q8NBP7_receptor.pdbqt \
  --cutoff 4.0 \
  --min-distance 2.0
```

### Checkpoint `ch3` Verification
```bash
./scripts/checkpoint.sh goto ch3
cat checkpoints/ch3/findings/structural-biology/WO-004.md
cat checkpoints/ch3/findings/computational-chemistry/WO-005.md
```
- **Top Hit (`pcsk9_analog_02`):** Predicted Vina binding energy `-9.4 kcal/mol`, minimum interatomic distance `2.34 Å` (zero clashes `< 2.0 Å`), geometric proximity to `Arg194` and `Asp238`. Propagates **`**Relay: \`docking.score_is_not_affinity\`**`** and **`**Relay: \`docking.contact_is_not_binding_event\`**`**.
- **Excluded Hit (`pcsk9_analog_05`):** Deprioritized due to a `1.72 Å` steric clash with `His226`.

---

**Next Step:** Proceed to [Module 04 — Stages 3 & 4 DMTA Lead Optimization, Oral PK Scaling, Wet-Lab Re-Ingestion & 28-Page Portal (`ch4`)](04-dmta-pk-dossier-portal.md).

# Un-Mocked Live `oase v0.3.0` Outputs — `pcsk9-oral`

This directory contains **58 real Phase-1 and Phase-2 outputs** produced directly by [`scripts/run-e2e-simulation.sh`](../../scripts/run-e2e-simulation.sh) against live public scientific APIs (`gnomAD`, `OpenTargets`, `GTEx`, `Human Protein Atlas`, `AlphaFold DB`) and compiled local C/C++/Python tools (`fpocket 4.2.2`, `Meeko 0.8.0`, `AutoDock Vina 1.2.5`, `RDKit`).

> For the complete Live-vs-Seeded table (including why `AlphaFold 3` co-folding, `AlphaGenome` `rs2479409` scoring, and rodent/dog Wet-Lab PK use pre-staged checkpoint fixtures by default and how to run `AF3` + `AlphaGenome` live on Vertex AI GPUs), see [**`docs/DATA_PROVENANCE.md`**](../../docs/DATA_PROVENANCE.md).

## Key Inspectable Highlights in This Directory

| Subdirectory | Tool Executed Live | Key Un-Mocked Output & Measured Verdict |
| :--- | :--- | :--- |
| [`hypotheses/`](hypotheses/) | `oase coscientist ingest` & `analyze` | `clear-leader`: Allosteric groove `IC-001` (`Elo = 1642.5`, `+54.5` gap over macrocycle `IC-002` `1588.0`). |
| [`genomics/`](genomics/) | `oase genetics` (`gnomAD`) & `oase gwas` (`OpenTargets`) | `PCSK9` `lof_tolerant` (`pLI = 2.77e-18`, `LOEUF = 1.144`); `25` significant disease associations led by Familial Hypercholesterolemia (`overall = 0.86`, `clinical = 0.97`). |
| [`gtex/`](gtex/) & [`expression/`](expression/) | `oase gtex` & `oase expression` (`HPA`) | `Tissue enriched` in **liver** (`47.5 nTPM`, highest of 50 human tissues) with negligible whole-blood expression (`0.25 TPM`, `not_expressed`). |
| [`structures/`](structures/) | `oase alphafold` (`AFDB`) & `oase pocket` (`fpocket 4.2.2`) | `AF-Q8NBP7-F1` monomer `confident` (ordered domain `58–542`); `druggable-pocket-present` (`0.788` top druggability across `48` detected cavities). |
| [`docking/`](docking/) | `oase docking prepare/run/analyze` (`Meeko 0.8.0` + `AutoDock Vina 1.2.5`) | Real 3D rigid-receptor Vina docking into `AF-Q8NBP7-F1` Pocket #1 (`exhaustiveness = 8`, `9` poses): **`PCSK9-A03` (`OASE-PCSK9-014` polar oxadiazole lead) scores `-9.6 kcal/mol` (`strong-binders-found`)**, outperforming `PCSK9-A02` (`-8.2 kcal/mol`, `moderate-binders-found`). Includes full 3D docked `.poses.pdbqt` coordinates. |
| [`compounds/`](compounds/) & [`admet/`](admet/) | `oase compound` & `oase admet` (`RDKit`) | **`PCSK9-A02`** (`cLogP = 5.09`, `TPSA = 51.2 Å²`, `LogS = -5.613`) flagged with **`liabilities-identified`** (`3` alerts including Aronov `herg_liability`); **`PCSK9-A03`** (`cLogP = 3.01`, `TPSA = 101.0 Å²`, `SA = 2.23`) eliminates `herg_liability` (`0` critical alerts). |

## Large Raw Files Omitted from Git (`> 250 KB`)

Seven large raw outputs (`AF-Q8NBP7-F1.cif` `612 KB`, `AF-Q8NBP7-F1.pae.json` `1.13 MB`, `AF-Q8NBP7-F1.receptor.pdbqt` `510 KB`, and the `ClinicalTrials.gov v2` raw payload `26.6 MB` + summaries) are indexed with their exact `sha256` digests in [`MANIFEST.json`](MANIFEST.json) and regenerated automatically by:

```bash
OASE_TOOLS_HOME=/tmp/scion-volumes/tools ./scripts/run-e2e-simulation.sh /tmp/sim-pcsk9-oral
```

# Step 1 — Pre-Mission Brief, Co-Scientist Prompt & Wingman Roster (`ch1`)

- **Campaign:** `pcsk9-oral` (Oral Small-Molecule PCSK9 Inhibitor in ASCVD)
- **Work Order Verified (`oase validate check`):** `WO-001` (`PASS`, `scientifically_accepted`)
- **Full Pod Outset Signatories:** **Dr. Sarah Chen** (`GOLD-1`), **Dr. Marcus Vance** (`GOLD-2`), **Dr. Elena Rostova** (`GOLD-3`), **Dr. Raj Patel** (`GOLD-4`), **Dr. Claire Moreau** (`GOLD-5`)

## 1. Co-Authored Co-Scientist Input Prompt & Target Product Profile (TPP)
| Prompt Clause | Functional Author | Locked Threshold / Kill Criterion in `.oase/thresholds.yaml` |
| :--- | :--- | :--- |
| **Clause 1 — Human Genetics & Liver Selectivity** | Dr. Marcus Vance (*Comp Bio*) | Require human LoF cardioprotection (`PCSK9 R46L` / `gnomAD pLI < 0.90`), `GTEx >= 100 TPM` liver expression, and 1P `AlphaGenome` `1 Mb` regulatory polarity |
| **Clause 2 — Allosteric Groove & `FP-001` Kill Switch** | Dr. Elena Rostova (*Structural Bio*) | Require 1P `AlphaFold 3` co-fold `ipTM >= 0.70` and `fpocket` druggability `>= 0.50` (`KILL` small molecule if `< 0.30`); retain macrocycle comparator `FP-002` |
| **Clause 3 — Unenhanced Oral Ro5 & Cardiac `hERG` Gate** | Dr. Raj Patel (*Med Chem*) & Dr. Claire Moreau (*DMPK*) | Require `cLogP <= 3.5`, `MW <= 500 Da`, `0` critical Aronov `hERG` / PAINS alerts, no dietary permeation enhancers, and a mandatory CRO wet-lab pause prior to human PK |

## 2. 24-Match Co-Scientist Tournament Outcome & Dynamic Subway Map Routing (`WO-001`)
- **Primary Green Line (`IC-001`, `1642.5 Elo`, `10W-2L`):** Cryptic inter-domain groove small molecule (`+54.5 Elo` over `#2`) advances into Stage 1 Genetics & `AlphaGenome`, carrying mandatory relay `hypothesis.adopted_not_generated`.
- **Parked Amber Backup Line (`IC-002`, `1588.0 Elo`, `8W-4L`):** Oral tricyclic macrocycle parked on standby in case `FP-001` pocket collapse fires at Gate 2 or `hERG`/PK blocks the small molecule at Gates 3–4.

## 3. Assigned Doctor <-> AI Wingman Mission Pairings
| Mission Leg | Human Lead (Doctor) | Paired AI Counterpart(s) in Scion Grove | Assigned Work Orders & Stage Gates |
| :--- | :--- | :--- | :--- |
| **Mission Command & Governance** | Dr. Sarah Chen (`GOLD-1`) | `Grove-1` (`@science-program-lead`) · `Aegis-6` (`@finding-validator`) · `@scientific-reviewer` | `WO-001` audit, Stage Gates `1–4` co-signatures, Step 6 red-team tamper drills, Step 7 closeout |
| **Stage 1 — Genetics & `AlphaGenome`** | Dr. Marcus Vance (`GOLD-2`) | `Helix-2` (`@computational-biologist`) | `WO-002`–`WO-003` (`gnomAD`, `OpenTargets`, `GTEx`, 1P `AlphaGenome`) -> **Gate 1** |
| **Stage 2 — `AlphaFold 3` & Docking** | Dr. Elena Rostova (`GOLD-3`) | `Fold-3` (`@structural-biologist`) · `@computational-chemist` | `WO-004`–`WO-005` (1P `AlphaFold 3` co-fold, `fpocket`, `AutoDock Vina`) -> **Gate 2** |
| **Stage 3 — Med Chem DMTA** | Dr. Raj Patel (`GOLD-4`) | `Spark-4` (`@medicinal-chemist`) | `WO-006` (`RDKit`, `BRICS` oxadiazole reroute `PCSK9-A02 -> OASE-PCSK9-014`, `ASKCOS`) -> **Gate 3** |
| **Stage 3–4 — `ADMET`, CRO & `PK`** | Dr. Claire Moreau (`GOLD-5`) | `Shield-5` (`@admet-dmpk-scientist`) · `@project-curator` | `WO-006`–`WO-008` (Aronov `hERG` takedown, `⏸` CRO wet-lab bridge, `40 mg QD` human PK, IND dossier) -> **Gate 4** |

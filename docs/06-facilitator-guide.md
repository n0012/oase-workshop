# Module 06 — Facilitator Runbook & Pacing Guide

> **Event:** GCP-OASE Hands-On Engineering & Pre-Clinical Discovery Workshop (`pcsk9-oral`)  
> **Duration:** 150 Minutes (2.5 Hours)  
> **Target Audience:** Biopharma Discovery Scientists, Computational Biologists, and AI Platform Engineers  
> **Guided Lab Playbook (Start Here for Live Sessions):** [**`docs/LAB_GUIDE_150M.md`**](LAB_GUIDE_150M.md) *(3 "What If" Opening Questions → "Well, We Built It" Pivot → 5 Pod Seats → 6 Hands-On Blocks)*

---

## 0. Opening the Conversation: The Three "What If" Questions (`0:00–0:15`)

Open the workshop with three provocative questions before touching a slide deck or terminal:

1. **Multiplayer Science Surface:** *"What if we had an agentic AI surface all of our scientists could use together at the same time?"*
2. **Frontier Model Optionality:** *"What if we had optionality in the frontier models we use—not locking our science into one vendor or one model's blind spots?"*
3. **Audit-Ready Stage-Gate Governance:** *"What if every AI-assisted claim, threshold check, and stage-gate decision was cryptographically verified against raw data—so a portfolio review committee could audit and trust the dossier?"*

Then open [**`chapters.html`**](https://n0012.github.io/oase-workshop/chapters.html) (or your live Cloud Run Story Arc Cockpit) with the pivot: ***"Well — we built it."*** See [**`docs/LAB_GUIDE_150M.md`**](LAB_GUIDE_150M.md) for the complete facilitator and participant lab playbook, copyable `@mention` prompts, and red-team tamper exercises.

---

## 1. Pre-Session Checklist (T-24h and T-30m)

Run the preflight and hub-seeding scripts before participants join:

```bash
# 1. Load environment variables
source .env

# 2. Run preflight verification (CLI tools, GCP ADC, KaTeX offline bundle, hygiene gate)
./scripts/preflight.sh
./scripts/preflight.sh --check-hygiene

# 3. Seed or reconcile the 8 Scion Hub checkpoints (ch0..ch7) + Story Arc Cockpit
./scripts/deploy-pilot-stack.sh --dry-run
./scripts/checkpoint.sh list
```

---

## 2. Live Execution vs. Checkpoint Pacing Matrix (`ch0`..`ch7`)

To keep a 150-minute workshop moving without waiting on 30-minute cold tournament or GPU runs:
- **Story Arc Presenter Cockpit (`oase-story-arc`):** Stream the 7 recorded 1080p Squadron chapters (`Ch 1`–`Ch 7`, ~36–43s each, accessible 100/200-level spoken synthesis + 6 specialist AI wingmen), then click **"Join Live at This Stage As..."** (`oase-sarah`..`oase-claire`) to drop straight into that chapter's live Scion Webchat thread. Facilitators signed in as `admin@<workshop-domain>` also have view/reset access on the Cockpit without adding `admin@` rows to Scion Hub.
- **Sub-15-second commands** run 100% live (`oase doctor`, `oase validate check`, Phase-2 `analyze`, `pytest`).
- **Multi-minute jobs** (`Hypex` tournament, cold `AlphaFold 3` co-folding, wet-lab CRO assays) are advanced via `./scripts/checkpoint.sh jump <ch1..ch7>` or the Cockpit's **`↺ Reset CHN (<2s)`** button.

| Operation | Real Wall-Clock Latency | Workshop Execution Mode | Command / Checkpoint |
| :--- | :--- | :--- | :--- |
| `oase doctor` / `oase tools list` / `oase relays` | `1–2 sec` | **100% Live** | `oase doctor` (`ch0`) |
| `create_project` + `bootstrap_campaign` (`pcsk9-oral` seed) | `45–60 sec` | **100% Live** | `./scripts/checkpoint.sh jump ch1` |
| `oase genetics fetch/analyze` + `oase gtex fetch/analyze` (`WO-002..003`) | `4–8 sec` | **100% Live** | `./scripts/checkpoint.sh jump ch2` |
| `oase alphafold predict` + `fpocket` + `AutoDock Vina` (`WO-004..005`) | `5–10 min` (AF3) / `6 sec` (Vina) | **Submit AF3 & Run Phase-2 Live → Jump to `ch3`** | `./scripts/checkpoint.sh jump ch3` |
| `oase admet` hERG gate + Wet-Lab CRO assay handoff (`WO-006`) | `3–5 sec` | **100% Live → Pause at Wet-Lab Slot** | `./scripts/checkpoint.sh jump ch4` |
| `oase pk` (`40 mg QD`) + `oase dossier` (`WO-007..008`, Gate 4) | `3–5 sec` | **100% Live** | `./scripts/checkpoint.sh jump ch5` |
| `oase validate check` (3 tamper blocks + `oase workorder override`) | `1–2 sec` | **100% Live** on `ch6` | `./scripts/checkpoint.sh jump ch6` |
| Portfolio closeout (`Grove-1` bookend + 30-page Evidence Portal) | `1–2 sec` | **100% Live** on `ch7` | `./scripts/checkpoint.sh jump ch7` |
| `pytest tests/test_h5ad.py` (49 unit tests for custom tool) | `2–3 sec` | **100% Live** | `pytest /workspace/tests/test_h5ad.py -v` |

---

## 3. Minute-by-Minute Run of Show

### Block 0 (`T-15m – 0:00`): [Module 00 — Prerequisites & Setup](00-prerequisites.md)
- Confirm every attendee has selected one of the four supported surfaces (Cloud Shell, Gemini CLI, Antigravity IDE, or Scion Web Console) and passes `./scripts/preflight.sh`.

### Block 1 (`0:00 – 0:20` · 20m): [Module 01 — Tour the Grove](01-tour-the-grove.md) (`ch0 → ch1`)
- **Key Points:**
  1. Static bioinformatics DAGs break when biology requires an unplanned detour; isolated single-player chatbots fabricate numbers when tools fail.
  2. GCP-OASE runs a 4-tier Scion Grove (`director`, `chemist`, `biologist`, `computationalist`) over a shared filesystem with deterministic two-phase tool execution.
  3. Portable model aliases (`small..extra-large`) allow **Gemini 4, Anthropic Claude, and OpenAI** to run side by side on GCP so the reviewer never shares model-family blind spots with the author.
- **Hands-On:** Inspect `.oase/control/work-orders/WO-001.json`, `raw/hypotheses/pcsk9_seed.meta.json`, and `findings/hypotheses/WO-001.md` at `ch1`.

### Block 2 (`0:20 – 0:45` · 25m): [Module 02 — Target Validation: Genetics & Omics](02-target-validation-genetics-omics.md) (`ch1 → ch2`)
- **Hands-On:**
  - Execute `WO-002` (`gnomAD` `LOF_TOLERANT` with live `pLI = 2.77e-18` / `LOEUF = 1.144` and seeded `pLI = 0.0001` / `LOEUF = 0.89`; `OpenTargets` FH score `0.86` live / `0.96` seeded; `GTEx`/`HPA` hepatocyte enrichment at `47.5 nTPM` live / `184.2 TPM` seeded with `tau = 0.93`) and `WO-003` (seeded `AlphaGenome` `rs2479409` liver RNA-seq quantile `0.984`).
  - Inspect how `.oase/thresholds.yaml` (`36/36` resolved threshold schemas, including the 13 sets that default to `UNRESOLVED` in `oase 0.3.0`) gates Stage 1 progression offline in `<0.2 seconds`.

### Block 3 (`0:45 – 1:15` · 30m): [Module 03 — Structural Biology & Docking](03-structure-docking-af3.md) (`ch2 → ch3`)
- **Hands-On:**
  - Inspect `WO-004` (live `AF-Q8NBP7-F1` monomer global `pLDDT = 85.19` across ordered domain `58–542`, seeded `AlphaFold 3` co-fold `ipTM = 0.84` / `pTM = 0.88`, and `fpocket 4.2.2` scoring `0.788` live across 48 pockets on `Q8NBP7` vs. seeded `Pocket #1` groove `0.68` and flat `EGF-A` surface `0.24`).
  - Inspect `WO-005` (seeded `AutoDock Vina 1.2.5` docking across the `IC-001` series at `-9.4 kcal/mol`, `2.34 Å` to `Arg194/Asp238/Phe379`).
  - Point out the mandatory scientific caveats (`**Relay: \`af3.low_confidence_segments\`**` and `**Relay: \`docking.score_is_not_affinity\`**`) enforced by `oase validate check`.

### Block 4 (`1:15 – 1:55` · 40m): [Module 04 — DMTA, PK & Dossier Portal](04-dmta-pk-dossier-portal.md) (`ch3 → ch4`)
- **Hands-On:**
  - Walk through the **Multi-Parameter Disqualification Moment (`WO-006`)**: `PCSK9-A02` (`COc1ccc(-c2nc(C(=O)Nc3ccc(C(F)(F)F)cc3)cs2)cc1`, RDKit `MW = 378.4 Da`, `TPSA = 51.2 Å²`, `cLogP = 5.09`, `LogS = -5.613`) triggers **3 critical rule-based ADMET liabilities** in `oase admet` (`metabolic_stability`, Aronov 2005 `herg_liability`, and `solubility`) along with mandatory relay `admet.herg_structural_flag`. Replacing the lipophilic CF3-thiazole with a polar F,CN-oxadiazole yields `PCSK9-A03` / `OASE-PCSK9-014` (`MW = 338.3 Da`, `TPSA = 101.0 Å²`, `cLogP = 3.01`, `LogS = -4.25`), which clears all 3 liabilities (`0` critical liabilities).
  - Review `WO-007` (seeded rodent-to-human PK fixture: `F = 52%`, `t1/2 = 14.8 h`, `40 mg QD` oral human dose) and `WO-008` (`findings/regulatory/WO-008.md` and 31-page `_site/index.html` + `_site/chapters.html`).
  - Run the **4 Epistemic Governance Drills** (`./scripts/run-e2e-simulation.sh` Chapter 5C: corrupted SHA-256 sidecar `PROV-002`, inflated prose claim `CIT-003`, deleted caveat relay `REL-001`, and stripped `threshold_set` attribution `THR-001`) so participants watch `oase validate check` reject each violation deterministically (`exit=1`).

### Block 5 (`1:55 – 2:30` · 35m): [Module 05 — Build & Register Custom Tools](05-extend-custom-tools.md)
- **Hands-On:**
  - Walk through the `oase h5ad` case study (`49/49` unit tests in `tests/test_h5ad.py`), demonstrating how OASE distinguishes `measured` vs. `searched_absent` (`NA` vs `0`) and refuses to guess cell-type labels.
  - Review **Patterns A–D** for onboarding internal Python libraries, static binaries, sidecar containers, and GCP GPU endpoints.

---

## 4. Recovery & `<2s` Non-Disruptive Reset Commands

During live sessions on the Story Arc Presenter Cockpit (`oase-story-arc`), open **`⚙ Facilitator Reset Drawer`** in the top control bar to reset any single chapter (`↺ Reset CH1`..`↺ Reset CH7`) or click **`↺ Reset Entire Demo (t=0)`** to restore all 8 Scion Hub checkpoints (`ch0`..`ch7`) in `<2 seconds` without logging out any of the 5 scientist Chrome sessions.

For local CLI workspaces:

```bash
# Restore any individual checkpoint in <2 seconds:
./scripts/checkpoint.sh jump ch1   # Step 1: Co-Scientist Seed Ingested (WO-001)
./scripts/checkpoint.sh jump ch2   # Step 2 + Gate 1: Genetics & Omics (WO-001..003)
./scripts/checkpoint.sh jump ch3   # Step 3 + Gate 2: AF3, fpocket & Vina (WO-001..005)
./scripts/checkpoint.sh jump ch4   # Step 4 + Gate 3 + Wet-Lab Handoff (WO-001..006)
./scripts/checkpoint.sh jump ch5   # Step 5 + Gate 4: Oral PK 40 mg QD & Dossier (WO-001..008)
./scripts/checkpoint.sh jump ch6   # Step 6: 3 Blocked Tamper Drills + Signed Override
./scripts/checkpoint.sh jump ch7   # Step 7: Portfolio Closeout & 30-Page Evidence Portal

# Full workshop reset back to ch0 (t=0):
./scripts/reset-workshop.sh
```

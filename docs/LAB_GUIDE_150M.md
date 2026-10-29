# 2.5-Hour (150-Minute) Guided Workshop & Hands-On Lab Instructions

> **Session Format:** Interactive Executive Provocation + Multi-Scientist Hands-On Lab (`pcsk9-oral`)  
> **Duration:** 150 Minutes (`2.5 Hours`)  
> **Participants:** 5–25 Discovery Scientists, Computational Biologists, Medicinal Chemists, DMPK Leads, and AI Platform Engineers  
> **Core Outcome:** Give discovery and platform leaders a firsthand **"lightbulb moment"**—experiencing multiplayer human + AI collaboration, multi-model optionality without vendor lock-in, and cryptographic scientific governance—so they leave ready to deploy GCP-OASE in their own Google Cloud environment.

---

## 1. Opening Provocation: Start With Three "What If" Questions (`0:00–0:10`)

Before showing architecture diagrams or terminal commands, open the conversation with **three "What If" questions** (one slide or talking point each) and let the room debate where current tools fall short:

| # | Opening "What If" Question | Why It Matters in Biopharma R&D | What GCP-OASE Demonstrates Live |
| :--- | :--- | :--- | :--- |
| **1** | **"What if we had an agentic AI surface all of our scientists could use together at the same time?"** | Single-player chat tabs isolate computational biology, structural biology, med chem, and DMPK in separate silos with copy-pasted summaries. | **Shared Scion Grove:** 5 human scientists (`Program Lead`, `Comp Bio`, `Structural Bio`, `Med Chem`, `DMPK`) work simultaneously in one shared workspace alongside 11 specialist agents. |
| **2** | **"What if we had optionality in the frontier models we use—not locking our science into one vendor or one model's blind spots?"** | Locking an R&D pipeline to one model family creates vendor lock-in and correlated "echo chamber" bias when the same model generates and reviews its own hypotheses. | **Multi-Model Squadron on Google Cloud:** **Gemini**, **Anthropic Claude**, and **OpenAI** run side-by-side via portable model tiers so no model family ever peer-reviews its own work. |
| **3** | **"What if every AI-assisted claim, threshold check, and stage-gate decision was cryptographically verified against raw data—so a portfolio review committee could audit and trust the dossier?"** | Chatbots hallucinate binding numbers, drop negative caveats, or silently confuse missing data (`NA`) with zero expression (`0`), making unverified prose unusable at formal stage gates. | **Two-Phase Tool Execution & 10-Check Validator:** Deterministic CLI tools lock `raw/` outputs with SHA-256 receipts, offline Phase-2 rules grade program cutoffs, and `oase validate check` blocks any unverified number (`±1%`) or missing caveat. |

### The Facilitator Pivot (`0:10–0:15`): *"Well — We Built It."*

After discussing the three "What Ifs", open [**`chapters.html`**](https://n0012.github.io/oase-workshop/chapters.html) (or your live Cloud Run **Story Arc Presenter Cockpit**) and say:

> ***"Well — we built it. Over the next two hours, we're going to sit in the five scientist seats of an oral PCSK9 small-molecule discovery pod, run this multi-model agent team through four preclinical stage gates and a wet-lab handoff, try to sneak fabricated data past the validator, and look at what it takes to stand this up in your own environment."***

---

## 2. Assigning the 5 Discovery Pod Seats

Divide attendees into **5 functional roles** (individuals or small 2–4 person breakout pods). On the live Story Arc Cockpit, each pod clicks **"Join Live at This Stage As..."** to enter Scion Webchat under its dedicated identity, or uses its local CLI / IDE terminal:

| Pod Seat | Persona Identity | Login Handle | Primary Stages Led | Paired AI Specialist Wingmen |
| :--- | :--- | :--- | :--- | :--- |
| **Seat 1 (`GOLD-1`)** | **Dr. Sarah Chen** — *Program Lead* | `oase-sarah` | **Step 1** (Kickoff), **Gate 1 & Gate 4** Co-Sign, **Step 7** (Portfolio Handoff) | `@science-program-lead` (`Grove-1`) · `@project-curator` |
| **Seat 2 (`GOLD-2`)** | **Dr. Marcus Vance** — *Computational Biologist* | `oase-marcus` | **Step 1** (`WO-001` Elo) & **Step 2** (`WO-002..003` Genetics, GTEx, AlphaGenome) | `@computational-biologist` (`Helix-2`) |
| **Seat 3 (`GOLD-3`)** | **Dr. Elena Rostova** — *Structural Biologist* | `oase-elena` | **Step 3** (`WO-004..005` AF3, `fpocket`, Vina) & **Step 6** (Governance Audit) | `@structural-biologist` (`Fold-3`) · `@computational-chemist` · `@finding-validator` (`Aegis-6`) |
| **Seat 4 (`GOLD-4`)** | **Dr. Raj Patel** — *Medicinal Chemist* | `oase-raj` | **Step 4** (`WO-006` RDKit, ADMET hERG Takedown, BRICS MMP & Synthesis Handoff) | `@medicinal-chemist` (`Spark-4`) |
| **Seat 5 (`GOLD-5`)** | **Dr. Claire Moreau** — *DMPK & Safety Lead* | `oase-claire` | **⏸ Lab Gate** & **Step 5** (`WO-007..008` Oral PK `40 mg QD` & Candidate Dossier) | `@admet-dmpk-scientist` (`Shield-5`) · `@toxicology-scientist` · `@regulatory-scientist` |

> **Facilitator Pacing Tip:** Let your lead scientific facilitator pace the discussion organically. Each chapter's recorded video is only **36–43 seconds** long—use the video to set context quickly, then spend 15–20 minutes per block in live Q&A, `@mention` prompts, artifact inspection, and scientific debate.

---

## 3. Minute-by-Minute 2.5-Hour (`150m`) Guided Lab Agenda

| Time | Duration | Lab Block | Chapters / Checkpoints | Hands-On Activity & Key Takeaway |
| :--- | :--- | :--- | :--- | :--- |
| **`0:00–0:15`** | `15 min` | **Block 0 — Three "What Ifs" → *"Well, We Built It"*** | `Overview` · `4 Core Pillars` (`ch0`) | Open with the 3 "What If" provocations, pivot to `chapters.html`, tour the 5 artifact layers, and assign the 5 Discovery Pod seats. |
| **`0:15–0:40`** | `25 min` | **Block 1 — Multiplayer Grove & Target Validation** | `Step 1` & `Step 2` (`ch1 → ch2`) | Watch `Step 1–2` clips, join simultaneously as `Sarah` + `Marcus`, query `gnomAD` / `GTEx` / `AlphaGenome`, inspect `.oase/thresholds.yaml`, and co-sign **Gate 1**. |
| **`0:40–1:10`** | `30 min` | **Block 2 — 3D Co-Folding, Cryptic Pockets & Docking** | `Step 3` (`ch2 → ch3`) | Watch `Step 3`, join as `Elena` + `Raj`, compare `Pocket #1` (`0.68` co-fold / `0.788` live apo) vs flat `EGF-A` (`0.24`), inspect `AutoDock Vina` poses (`-9.4 kcal/mol`), and sign **Gate 2** with liability `L-002`. |
| **`1:10–1:45`** | `35 min` | **Block 3 — ADMET Takedown, Wet-Lab Gate & Oral PK** *(incl. 5m break)* | `Step 4` & `Step 5` (`ch3 → ch5`) | Disqualify `PCSK9-A02` (`cLogP = 5.09`, Aronov `herg_liability`), nominate `OASE-PCSK9-014` (`cLogP = 3.01`, `0` alerts), walk through the **⏸ Wet-Lab CRO Stopping Gate**, verify `40 mg QD` oral PK, and co-sign **Gate 4**. |
| **`1:45–2:10`** | `25 min` | **Block 4 — Red-Team the Validator (Break the Science)** | `Step 6` (`ch6`) | **Hands-on tamper challenge:** alter a raw file (`PROV-002`), inflate a binding score (`CIT-003`), strip a caveat (`REL-001`), watch `oase validate check` block all three, log an audited human override, and test `<2s` **`↺ Reset CH6`**. |
| **`2:10–2:30`** | `20 min` | **Block 5 — Portfolio Readout, Custom Tools & Own-GCP Pilot** | `Step 7` (`ch7`) | Watch `Grove-1` closeout, tour the 30-page Evidence Portal, inspect the 2-phase custom tool wrapper (`oase h5ad`), and scope a 2-week pilot in the team's own GCP environment. |

---

## 4. Step-by-Step Hands-On Facilitator & Participant Instructions

### Block 0 (`0:00–0:15` · 15 min) — The Three "What Ifs" & Environment Check

1. **Facilitator (`0:00–0:08`):** Present the **Three "What If" Questions** above. Ask the group:
   - *"Where do AI prototypes break today when a discovery team tries to bring an AI-generated target or hit series to a real stage-gate review?"*
2. **Live Reveal (`0:08–0:12`):** Open `chapters.html` (`Overview & Challenges` → `4 Core Pillars`). Point out:
   - **Separation of Powers across 5 Artifact Layers:** `raw/` (SHA-256 tool outputs) → `findings/` (cited specialist Markdown) → `program-state/` (AI Program Lead decisions & liability tracker) → Stage-Gate Co-Signs → `_site/` (30-page static Evidence Portal).
3. **Seat Check (`0:12–0:15`):** Have participants open the **Story Arc Cockpit** (or local terminal) and run a 2-second environment check:
   ```bash
   ./scripts/checkpoint.sh list
   ./scripts/checkpoint.sh jump ch1
   ```

---

### Block 1 (`0:15–0:40` · 25 min) — Multiplayer Grove Kickoff & Human Genetic Target Validation (`Steps 1–2` · `WO-001..003`)

**Objective:** Experience **What If #1 (Multiplayer Surface)** and **What If #2 (Multi-Model Optionality)** firsthand while taking `pcsk9-oral` through **Gate 1 (Target Validation)**.

1. **Watch Context (`3 min`):** Review the high-level **Subway Navigator** framing in `Overview` (`#why`), then play the **Step 1** (`WO-001` Co-Scientist Elo Tournament) and **Step 2** (`WO-002..003` Human Genetics & Omics) Squadron clips in `chapters.html` (`#ch1` and `#ch2`), inspecting the **Upstream Co-Scientist Research Brief** ([`prompts/coscientist-research-brief.md`](../prompts/coscientist-research-brief.md))—pointing out how the initial prompt's unenhanced oral Rule-of-5 preference and `FP-001` kill criteria open both primary hypothesis `IC-001` and backup macrocycle `IC-002` while locking `.oase/thresholds.yaml`.
2. **Multiplayer Scion & Dynamic Subway Routing Exercise (`10 min`):**
   - **Seat 1 (`oase-sarah`)** and **Seat 2 (`oase-marcus`)** both click **"Join Live at This Stage"** on `Step 2` so the room sees multiple scientists typing in the same shared Grove conversation simultaneously.
   - Paste or adapt these live `@mention` prompts in Scion Webchat (including a live **Subway Track-Switch Drill** showing how OASE dynamically routes to single-cell `.h5ad` if bulk RNA-seq comes back low):
     ```text
     @computational-biologist Why did allosteric small-molecule hypothesis IC-001 (1642.5 Elo) outperform cyclic peptide IC-002 (1588.0 Elo) in WO-001, and what caveat must travel forward?
     ```
     ```text
     @computational-biologist Compare PCSK9 hepatocyte expression in GTEx against extrahepatic CNS tissues in WO-002, and explain how gnomAD LoF tolerance supports chronic inhibition safety.
     ```
     ```text
     @science-program-lead SUBWAY ROUTING DRILL: Suppose bulk GTEx liver expression had returned 0.4 TPM instead of 184.2 TPM. Show the exact oase h5ad single-cell Work Order you would dispatch rather than dropping the target.
     ```
3. **CLI / Artifact Verification (`8 min`):** Inspect the Phase-1 + Phase-2 artifacts and run live target-validation grading:
   ```bash
   ./scripts/checkpoint.sh jump ch2
   cat checkpoints/ch2/findings/computational-biology/WO-002.md
   # Optional live run inside OASE tools environment:
   oase genetics fetch PCSK9 && oase genetics analyze PCSK9
   oase gtex fetch PCSK9 && oase gtex analyze PCSK9
   oase validate check WO-002
   ```
4. **Gate 1 Discussion (`4 min`):** Highlight `.oase/thresholds.yaml`—36 versioned schemas where organizational cutoffs are fixed *before* Phase 2 runs offline, preventing an LLM from moving goalposts mid-analysis. Co-sign **Gate 1**.

---

### Block 2 (`0:40–1:10` · 30 min) — 3D Structural Co-Folding, Cryptic Pockets & Docking (`Step 3` · `WO-004..005`)

**Objective:** Show how GPU structure prediction (`AlphaFold 3`) pairs with deterministic physics/geometry tools (`fpocket`, `AutoDock Vina`) without letting chatbots overclaim binding affinity.

1. **Watch Context (`2 min`):** Open `#ch3` (`Step 3: AF3, Pockets & Gate 2`) and play the 40-second Squadron walkthrough.
2. **Multiplayer Structural Triage (`12 min`):**
   - **Seat 3 (`oase-elena`)** and **Seat 4 (`oase-raj`)** join `#ch3` live and interrogate the structural specialists:
     ```text
     @structural-biologist Compare cryptic Pocket #1 druggability (0.68 in co-fold / 0.788 apo) against the flat EGF-A PPI interface (0.24) in WO-004. Which residues anchor the groove?
     ```
     ```text
     @science-program-lead PCSK9-A02 achieved the strongest Vina pose score (-9.4 kcal/mol), yet you logged liability L-002 at Gate 2. What chemical risk are we carrying into Step 4?
     ```
3. **Inspect Live vs. Seeded Compute Receipts (`10 min`):**
   - Compare the canonical **AlphaFold 3** protein+ligand input ([`inputs/pcsk9_ic001_af3_ligand.json`](../inputs/pcsk9_ic001_af3_ligand.json)) and real **`AutoDock Vina 1.2.5`** 3D docking outputs ([`live-results/pcsk9-oral/raw/docking/`](../live-results/pcsk9-oral/raw/docking/)):
     ```bash
     ./scripts/checkpoint.sh jump ch3
     cat live-results/pcsk9-oral/raw/pocket/Q8NBP7_pockets.analysis.json
     cat live-results/pcsk9-oral/raw/docking/PCSK9-A03_vina.analysis.json
     ```
4. **Gate 2 Takeaway (`6 min`):** Point out `**Relay: docking.score_is_not_affinity**` in `WO-005.md`. OASE advances the scaffold on geometry while mechanically forcing the caveat—and `L-002` lipophilicity risk—into Stage 3.

---

### Block 3 (`1:10–1:45` · 35 min) — Multiparameter ADMET Takedown, Wet-Lab Stopping Gate & Oral PK (`Steps 4–5` · `WO-006..008`)

*(Take a 5-minute break from `1:10–1:15`.)*

**Objective:** Demonstrate multiparameter DMTA trade-offs (disqualifying the highest-scoring docker on cardiac safety) and show how GCP-OASE pauses cleanly on disk across multi-week wet-lab / CRO studies.

1. **Watch Context (`3 min`):** Play the **Step 4** (`#ch4`) and **Step 5** (`#ch5`) Squadron clips.
2. **Hands-On Med-Chem Disqualification (`12 min`):**
   - **Seat 4 (`oase-raj`)** leads `Step 4`. Inspect why `PCSK9-A02` (`-9.4 kcal/mol`, `cLogP = 5.09`, `TPSA = 51.2 Å²`) is disqualified by `oase admet` (`metabolic_stability`, Aronov `herg_liability`, `solubility`), whereas polar oxadiazole `OASE-PCSK9-014` (`PCSK9-A03`, `cLogP = 3.01`, `TPSA = 101.0 Å²`, `-9.6 kcal/mol` live Vina) clears every rule with **zero critical alerts**:
     ```bash
     cat live-results/pcsk9-oral/raw/admet/PCSK9-A02_admet.analysis.json
     cat live-results/pcsk9-oral/raw/admet/PCSK9-A03_admet.analysis.json
     ```
   - Ask in Scion Webchat:
     ```text
     @medicinal-chemist Walk through the exact RDKit descriptors (cLogP, TPSA, basic amine count) that triggered the Aronov hERG alert on PCSK9-A02 and how OASE-PCSK9-014 resolved L-002.
     ```
3. **The ⏸ Wet-Lab Stopping Gate & Step 5 Oral PK (`15 min`):**
   - **Seat 5 (`oase-claire`)** leads the transition across the **Wet-Lab / CRO Handoff**:
     - Show how **Gate 3** generates a concrete CRO package (`4`-step convergent synthesis `CRO-SYN-014`, `SPR` `KD`, manual patch-clamp `hERG IC50`, and rat/dog IV+PO PK) and **hibernates on disk with zero idle compute burn**.
     - Inspect the returned PK projection in `ch5` (`54%` rat `F`, `61%` dog `F` → projected human `F = 52%`, `t1/2 = 14.8 h`, **`40 mg QD` oral tablet**) alongside live ClinicalTrials.gov competitive context (`100` PCSK9 trials, `0` approved oral small molecules in [`live-results/pcsk9-oral/raw/trials/`](../live-results/pcsk9-oral/raw/trials/)).
   - Co-sign **Gate 4 (Candidate Nomination)**.

---

### Block 4 (`1:45–2:10` · 25 min) — Red-Team the Validator: Break the Science & Test Overrides (`Step 6`)

**Objective:** Deliver the **What If #3 (Audit-Ready Governance)** lightbulb moment by letting participants actively tamper with data and findings—and watching `oase validate check` catch every violation in `<1 second`.

1. **Watch Context (`2 min`):** Play the **Step 6** (`#ch6`) clip featuring `Aegis-6` (`@finding-validator`).
2. **Hands-On Red-Team Challenge (`15 min`):** Challenge attendees to sneak an unverified edit past `oase validate check` in a scratch copy (or on `#ch6`):
   ```bash
   cp -r checkpoints/ch5 /tmp/redteam-lab && cd /tmp/redteam-lab

   # Baseline: confirm WO-005 passes all 10 checks (exit=0)
   oase validate check WO-005

   # Drill 1 (PROV-002 — Raw Data Tampering): alter one byte in a raw docking JSON
   sed -i 's/-9.4/-9.9/' raw/docking/pcsk9_pocket1_vina.json
   oase validate check WO-005   # -> BLOCKED (exit=1): SHA-256 mismatch against .meta.json!
   cp "$OLDPWD/checkpoints/ch5/raw/docking/pcsk9_pocket1_vina.json" raw/docking/pcsk9_pocket1_vina.json

   # Drill 2 (CIT-003 — Hallucinated Prose Metric): inflate -9.4 to -11.2 kcal/mol in Markdown
   sed -i 's/-9.4/-11.2/' findings/computational-chemistry/WO-005.md
   oase validate check WO-005   # -> BLOCKED (exit=1): exceeds ±1% tolerance of $.metrics!
   cp "$OLDPWD/checkpoints/ch5/findings/computational-chemistry/WO-005.md" findings/computational-chemistry/WO-005.md

   # Drill 3 (REL-001 — Stripped Caveat): delete a required scientific limitation relay
   sed -i '/docking.score_is_not_affinity/d' findings/computational-chemistry/WO-005.md
   oase validate check WO-005   # -> BLOCKED (exit=1): mandatory relay missing!
   ```
3. **Audited Human Override & `<2s` Reset (`8 min`):**
   - Ask: *"What happens when an experienced medicinal chemist intentionally wants to advance a beyond-Rule-of-5 macrocycle that fails a default threshold?"*
   - Inspect `DEC-OVERRIDE-001` in `checkpoints/ch6/program-state/decision-log.md` (`oase workorder override`), showing how OASE **permits human scientific judgment** while permanently recording the signer, timestamp, and rationale in the audit trail.
   - Click **`↺ Reset CH6 (<2s)`** in the Story Arc Facilitator Drawer to demonstrate instant, non-disruptive state recovery.

---

### Block 5 (`2:10–2:30` · 20 min) — Portfolio Closeout, Custom Internal Tools & Deploying in Your Own Environment (`Step 7`)

**Objective:** Connect the workshop experience directly to the organization's internal tools, assays, and Google Cloud environment.

1. **Campaign Route Recap & 30-Page Evidence Portal (`5 min`):**
   - Watch **Step 7** (`#ch7`, `Grove-1` closeout), walk through the **Interactive Campaign Route Recap Map** (`#recap-subway-section`, clicking Stations `S0`–`S5` to review how the campaign dynamically switched tracks around flat `EGF-A` and the `PCSK9-A02` `hERG` trap), and click **`Portal Home (30 Pages)`** (`index.html`) + **`WO-008 Candidate Dossier`** to show the self-contained executive deliverable a portfolio committee receives—every claim clickable down to its Layer-0 JSON receipt.
2. **Wrapping Internal Tools & Assays (`7 min`):**
   - Open [Module 05 — Build & Register Custom Tools](05-extend-custom-tools.md) (`oase h5ad` adapter + `49` unit tests). Highlight how any internal Python library, container, or LIMS/CRO reader plugs into OASE in ~100 lines by emitting `raw/<class>/<id>.json` + `.meta.json` (Phase 1) and `.analysis.json` (Phase 2).
3. **Actionable Next-Step Closeout — Standing Up a Pilot in Your GCP Environment (`8 min`):**
   - Walk through the 4-tier runbook in [**`docs/DEPLOY_AND_TEST.md`**](DEPLOY_AND_TEST.md):
     ```bash
     # 1. Provision isolated GCP project + least-privilege service account
     python3 scripts/provision-gcp-project.py --project-id <your-pilot-project> --org-id <your-org-id>

     # 2. Bootstrap OASE v0.3.0 scientific toolchain + run full verification suite
     OASE_TOOLS_HOME=/scion-volumes/tools ./scripts/bootstrap-oase-env.sh
     OASE_TOOLS_HOME=/scion-volumes/tools ./scripts/run-e2e-simulation.sh /tmp/sim-pcsk9-oral

     # 3. Deploy the multi-user Scion Hub + 5-seat Story Arc Cockpit behind Cloud Run IAP
     ./scripts/deploy-pilot-stack.sh
     ```
   - **Closeout Alignment Questions for the Room:**
     1. *Which **internal therapeutic target or hit series** would make the sharpest 2-week validation pilot?*
     2. *Which **1–2 internal data sources or assays** (e.g., internal scRNA-seq `.h5ad` atlas, proprietary docking/FEP pipeline, or CRO PK sheet) should we wrap first?*
     3. *Who are the **5 pod counterparts** (Program Lead, Comp Bio, Structural Bio, Med Chem, DMPK + Platform Engineer) to seat in the pilot Grove?*

# GCP-OASE Workshop: Oral PCSK9 Small-Molecule Discovery on Google Cloud

Hands-on engineering workshop for the **Open Agentic Science Engine (`oase v0.3.0`)** running inside **Google Cloud Scion (`v0.1.50`)** multi-agent Groves.

Participants take a single drug discovery campaign (**`pcsk9-oral`** — oral small-molecule inhibitors of the PCSK9–LDLR protein-protein interaction) through all four preclinical stages:

1. **Stage 0–1 Target Validation & Omics (`WO-001`–`WO-003`):** Co-Scientist Elo tournament ranking (`IC-001` Elo `1642.5`), `gnomAD` loss-of-function constraint (`LOF_TOLERANT`), `OpenTargets` genetic association (`0.86` live / `0.96` seeded FH), `GTEx`/`HPA` hepatocyte expression (`184.2 TPM` / `47.5 nTPM`), and `AlphaGenome` `rs2479409` regulatory polarity (`0.984`).
2. **Stage 2 Structure & Docking (`WO-004`–`WO-005`):** AlphaFold monomer (`AF-Q8NBP7-F1`, `pLDDT = 85.19`) and seeded AlphaFold 3 co-fold (`ipTM = 0.84`), `fpocket` druggability (`0.788` live apo / `0.68` `Pocket #1` groove vs `0.24` flat `EGF-A` surface), and `AutoDock Vina 1.2.5` pose scoring (`-9.4 kcal/mol`).
3. **Stage 3 DMTA Lead Optimization (`WO-006`):** RDKit property profiling (`oase compound`) and rule-based ADMET gating (`oase admet` / `admet-endpoints@1.0`) — disqualifying the lipophilic top docker `PCSK9-A02` (`cLogP = 5.09`, 3 liabilities including the Aronov 2005 `herg_liability` pharmacophore alert) in favor of the polar F,CN-oxadiazole `PCSK9-A03` / `OASE-PCSK9-014` (`cLogP = 3.01`, `MW = 338.3 Da`, `TPSA = 101.0 Å²`, `0` critical liabilities).
4. **Stage 4 Translational PK & Dossier (`WO-007`–`WO-008`):** 1-compartment oral PK simulation (`F = 52%`, `t1/2 = 14.8 h`, `40 mg QD` human oral dose) and candidate dossier synthesis (`findings/regulatory/WO-008.md` + 30-page static Evidence Portal `_site/index.html` and interactive replay `_site/chapters.html`).

Every finding written by an agent is verified by `oase validate check` against 10 deterministic checks across four core governance gates before work-order closure:
- **Gate 1 (SHA-256 Provenance — `provenance_valid`):** Every file in `raw/` must have a matching `<artifact>.meta.json` sidecar whose `sha256` digest matches the file on disk.
- **Gate 2 (JSONPath Citation Verification — `source_tags_resolve`):** Every scalar numerical claim in `findings/**/*.md` must carry an inline `{source: raw/<class>/<stem>.analysis.json $.metrics.<key>}` citation (outside code backticks) that resolves within **±1% relative tolerance** of the Phase-2 analysis JSON.
- **Gate 3 (Mandatory Epistemic Caveat Relays — `relay_coverage`):** Every domain caveat emitted in `.analysis.json` (`hypothesis.adopted_not_generated`, `gnomad.constraint_is_not_safety`, `alphagenome.regulatory_prediction_is_in_silico`, `af3.low_confidence_segments`, `docking.score_is_not_affinity`, `admet.herg_structural_flag`, `pk.allometry_uncertainty`) must appear verbatim as `**Relay: \`<code>\`**` in the synthesis markdown.
- **Gate 4 (Versioned Threshold Attribution — `analysis_citations`):** Every `.analysis.json` record must attribute its verdict to a fully resolved, version-locked threshold schema (`36/36` schemas resolved in `.oase/thresholds.yaml`).

---

## Quickstart (Interactive Checkpoints)

```bash
# 1. Configure your environment
cp .env.example .env

# 2. Verify CLI prerequisites and repository hygiene
./scripts/preflight.sh --check-hygiene

# 3. Inspect or load a verified campaign checkpoint (ch0..ch4)
./scripts/checkpoint.sh list
./scripts/checkpoint.sh jump ch2
```

---

## Reproduce End-to-End (Automated Provisioning, Bootstrap & 6-Chapter Simulation)

To provision a net-new Argolis GCP project, compile the 7 scientific binaries (`vina`, `fpocket`, `rate4site`, `muscle`, `hypex`, `elo`, `prox`) + Python 3.11 environment, and execute the full 6-chapter simulation (`live-runs/` + `WO-001`..`WO-008` validation + 4 adversarial tamper drills + 31-page Evidence Portal):

```bash
# 1. (Optional) Provision an isolated Argolis GCP project + scion-default-agent SA
python3 scripts/provision-argolis-project.py \
  --project-id my-oase-workshop \
  --org-id 123456789012

# 2. Bootstrap OASE v0.3.0 tools home (Python 3.11 venv + 7 binaries + offline KaTeX)
OASE_TOOLS_HOME=/tmp/scion-volumes/tools ./scripts/bootstrap-oase-env.sh

# 3. Run the complete 6-chapter end-to-end simulation + 4 negative drills + portal build
OASE_TOOLS_HOME=/tmp/scion-volumes/tools ./scripts/run-e2e-simulation.sh /tmp/sim-pcsk9-oral

# 4. Serve the 31-page Evidence Portal & Interactive Chapter Replay locally
python3 -m http.server 8765 --bind 127.0.0.1 --directory /tmp/sim-pcsk9-oral/_site
# Open http://127.0.0.1:8765/chapters.html and http://127.0.0.1:8765/index.html
```

---

## 150-Minute Workshop Curriculum (Modules `00`–`05` ↔ Simulation Chapters `1`–`6`)

| Curriculum Module | Simulation Chapter | Time | Stage & Work Orders | Checkpoint |
| :--- | :--- | :--- | :--- | :--- |
| **[00 — Prerequisites & Setup](docs/00-prerequisites.md)** | Prep | T-15m | CLI preflight, Argolis project & Scion Hub auth, and surface selection | `ch0` |
| **[01 — Tour the Grove](docs/01-tour-the-grove.md)** | **Chapter 1** (`#ch1`) | 0:00–0:20 | Stage 0 (`WO-001`): `oase doctor`, Co-Scientist tournament ingest/analyze (`IC-001` Elo `1642.5` vs `IC-002` `1588.0`), and `hypothesis.adopted_not_generated` relay | `ch1` |
| **[02 — Target Validation: Genetics & Omics](docs/02-target-validation-genetics-omics.md)** | **Chapter 2** (`#ch2`) | 0:20–0:45 | Stage 1 (`WO-002`, `WO-003`): `gnomAD` (`LOF_TOLERANT`), `OpenTargets` (`0.86` live / `0.96` seeded), `GTEx`/`HPA` (`184.2 TPM` / `47.5 nTPM`), and `AlphaGenome` (`0.984`) | `ch2` |
| **[03 — Structural Biology & Docking](docs/03-structure-docking-af3.md)** | **Chapter 3** (`#ch3`) | 0:45–1:15 | Stage 2 (`WO-004`, `WO-005`): AFDB `Q8NBP7` (`pLDDT = 85.19`), seeded AF3 co-fold (`ipTM = 0.84`), `fpocket` (`0.788` live / `0.68` groove vs `0.24` surface), and AutoDock Vina (`-9.4 kcal/mol`) | `ch3` |
| **[04 — DMTA, PK & Dossier Portal](docs/04-dmta-pk-dossier-portal.md)** | **Chapters 4–6** (`#ch4`–`#ch6`) | 1:15–1:55 | Stages 3–4 (`WO-006`..`WO-008`): ADMET hERG disqualification of `PCSK9-A02` (`cLogP = 5.09`, 3 liabilities) vs `PCSK9-A03` (`cLogP = 3.01`, 0 liabilities), oral PK (`40 mg QD`), 4 adversarial tamper drills, and `_site/` portal build | `ch4` |
| **[05 — Build & Register Custom Tools](docs/05-extend-custom-tools.md)** | Extension | 1:55–2:30 | Write a two-phase tool adapter (`raw/` + `.meta.json` + `.analysis.json`) and verify it with `oase validate check` | — |

### Reference Guides
- **[Surface Connectivity Reference](docs/surface-connectivity-reference.md):** Connecting Gemini Enterprise (GA), Antigravity IDE (AGY), Gemini CLI, and Scion Web Console (`scion.hlscde.dev`) to the same OASE workspace.
- **[Facilitator Runbook](docs/06-facilitator-guide.md):** Hub seeding (`./scripts/seed-hub.sh`), pacing, and live demo recovery.
- **[Troubleshooting & Validator Reference](docs/07-troubleshooting.md):** Exact remediation steps for `PROV-001`..`002`, `CIT-001`..`003`, `REL-001`, and `THR-001`.
- **[Technical Article](ARTICLE.md) & [Design PRFAQ](PRFAQ.md):** Background narrative, Working-Backwards rationale, and our 5 field engineering discoveries from deploying OASE v0.3.0 in Argolis.

---

## Repository Layout

```text
oase-workshop/
├── README.md                                 # Quickstart, e2e reproduction commands, and curriculum map
├── ARTICLE.md                                # Technical overview, architecture, and 5 field discoveries
├── PRFAQ.md                                  # Working-Backwards design document
├── .env.example                              # Generic environment template
├── docs/                                     # Step-by-step workshop modules (00–07 + connectivity reference)
├── scripts/
│   ├── provision-argolis-project.py          # Repeatable Argolis GCP project & SA provisioner
│   ├── bootstrap-oase-env.sh                 # Builds Python 3.11 venv + 7 scientific binaries + offline KaTeX
│   ├── run-e2e-simulation.sh                 # Runs Chapters 1–6, 8 WO validations, 4 negative drills & portal build
│   ├── build-chapter-portal.py               # Generates _site/chapters.html replay & links all 30 portal pages
│   ├── preflight.sh                          # Checks tools, auth, and repo hygiene (--check-hygiene)
│   ├── seed-hub.sh                           # Provisions the 7-part pcsk9-oral seed on a Scion Hub
│   ├── checkpoint.sh                         # Restores verified campaign states (ch0..ch4)
│   ├── reset-workshop.sh                     # Resets local workspace to ch0
│   └── render-customer-overlay.sh            # Generates gitignored customer-specific workshop bundles
├── overlays/
│   ├── README.md                             # Customer overlay guide
│   └── customer-overlay.env.example          # Template for customer-specific parameters
└── checkpoints/
    ├── ch0/                                  # Clean pre-campaign seed (campaign-seed.json, coscientist-export.json)
    ├── ch1/                                  # WO-001 completed (Co-Scientist seed ingested & validated)
    ├── ch2/                                  # Stage 1 completed (WO-001..003: Genetics, GTEx & AlphaGenome validated)
    ├── ch3/                                  # Stage 2 completed (WO-001..005: AF3, fpocket & Vina validated)
    └── ch4/                                  # Stages 3–4 completed (WO-001..008: ADMET, PK & Dossier validated)
```

Each checkpoint directory (`checkpoints/ch1`..`ch4`) is a complete, schema-valid OASE workspace containing `.oase/thresholds.yaml` (all 36 threshold schemas resolved), `.oase/control/work-orders/WO-*.json`, `raw/<class>/*` artifacts, `<artifact>.meta.json` SHA-256 sidecars, `<stem>.analysis.json` metric records, `findings/**/*.md` synthesis reports, and `VAL-WO-*.json` validation receipts.

---

## Customer-Specific Overlays

This repository is intentionally generic. To generate a customer-tailored workshop bundle (custom internal portal URL, GCP project ID, target antigen, or therapeutic program name) without committing customer identifiers to git:

```bash
cp overlays/customer-overlay.env.example overlays/acme-bio.local.env
./scripts/render-customer-overlay.sh overlays/acme-bio.local.env
```

Rendered bundles are written to `overlays/customers/<slug>/` (gitignored) and automatically checked by `./scripts/preflight.sh --check-hygiene`.

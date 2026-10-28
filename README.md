# GCP-OASE Workshop: Oral PCSK9 Small-Molecule Discovery on Google Cloud

Hands-on engineering workshop for the **Open Agentic Science Engine (`oase v0.3.0`)** running inside **Google Cloud Scion (`v0.1.50`)** multi-agent Groves.

Participants take a single drug discovery campaign (**`pcsk9-oral`** — oral small-molecule inhibitors of the PCSK9–LDLR protein-protein interaction) through all four preclinical stages:

1. **Target Validation & Omics (`WO-001`–`WO-003`):** Open Targets genetics (`L2G`), GTEx v8 tissue expression, and Co-Scientist hypothesis ranking.
2. **Structure & Docking (`WO-004`–`WO-005`):** AlphaFold 3 (`3P5B` reference) interface confidence, fpocket druggability (`Pocket 1`), and AutoDock Vina docking.
3. **DMTA Lead Optimization (`WO-006`):** RDKit property filtering and Chemprop ADMET profiling (`hERG IC50`, Caco-2 permeability) across analogs `PCSK9-A01`..`A03`.
4. **Translational PK & Dossier (`WO-007`–`WO-008`):** 1-compartment oral PK simulation (`AUC`, `Cmax`, target coverage) and candidate dossier synthesis (`program-state/dossier.md` + `portal.html`).

Every finding written by an agent is verified by `oase validate check` against three deterministic gates before entering `program-state/`:
- **Gate 1 (SHA-256 Provenance):** Every file in `raw/` must have a matching `<artifact>.meta.json` sidecar whose `sha256` digest matches the file on disk.
- **Gate 2 (JSONPath Citation Verification):** Every numerical claim in `findings/**/*.md` must carry an inline `{source: raw/<class>/<stem>.analysis.json $.metrics.<key>}` citation that resolves within `1e-6` of the Phase-2 analysis JSON.
- **Gate 3 (Scientific Caveat Relays):** Required domain caveats (`docking.score_is_not_affinity`, `structure.plddt_is_not_binding`, `admet.herg_margin_required`, `pk.rodent_to_human_scaling`) must appear verbatim as `**Relay: \`<code>\`**` in the synthesis markdown.

---

## Quickstart (3 Commands)

```bash
# 1. Configure your environment
cp .env.example .env

# 2. Verify CLI prerequisites and repository hygiene
./scripts/preflight.sh

# 3. Inspect or load a verified campaign checkpoint (ch0..ch4)
./scripts/checkpoint.sh list
./scripts/checkpoint.sh jump ch2
```

---

## 150-Minute Workshop Curriculum

| Module | Time | Stage & Work Orders | Checkpoint |
| :--- | :--- | :--- | :--- |
| **[00 — Prerequisites & Setup](docs/00-prerequisites.md)** | T-15m | CLI preflight, Scion Hub auth, and surface selection (Cloud Shell, Gemini CLI, Antigravity IDE, or Web Console) | `ch0` |
| **[01 — Tour the Grove](docs/01-tour-the-grove.md)** | 0:00–0:20 | Inspect the 4-agent Scion Grove (`director`, `chemist`, `biologist`, `computationalist`), control store, and seed package (`WO-001`) | `ch1` |
| **[02 — Target Validation: Genetics & Omics](docs/02-target-validation-genetics-omics.md)** | 0:20–0:45 | Stage 1 (`WO-002`, `WO-003`): Open Targets `L2G = 0.89`, GTEx liver `312.4 TPM`, and Tier-1 threshold gates | `ch2` |
| **[03 — Structural Biology & Docking](docs/03-structure-docking-af3.md)** | 0:45–1:15 | Stage 2 (`WO-004`, `WO-005`): AF3 `ipTM = 0.84`, fpocket druggability `0.78`, AutoDock Vina (`-9.4 kcal/mol`), and mandatory relays | `ch3` |
| **[04 — DMTA, PK & Dossier Portal](docs/04-dmta-pk-dossier-portal.md)** | 1:15–1:55 | Stages 3–4 (`WO-006`..`WO-008`): hERG safety disqualification of `PCSK9-A02` (`4.2 uM` vs `> 10.0 uM`), nomination of `PCSK9-A03` (`28.4 uM`), oral PK (`88.0%` coverage), and validation drills | `ch4` |
| **[05 — Build & Register Custom Tools](docs/05-extend-custom-tools.md)** | 1:55–2:30 | Write a two-phase tool adapter (`raw/` + `.meta.json` + `.analysis.json`) and verify it with `oase validate check` | — |

### Reference Guides
- **[Surface Connectivity Reference](docs/surface-connectivity-reference.md):** Connecting Gemini Enterprise (GA), Antigravity IDE (AGY), Gemini CLI, and Scion Web Console (`scion.hlscde.dev`) to the same OASE workspace.
- **[Facilitator Runbook](docs/06-facilitator-guide.md):** Hub seeding (`./scripts/seed-hub.sh`), pacing, and live demo recovery.
- **[Troubleshooting & Validator Reference](docs/07-troubleshooting.md):** Exact remediation steps for `PROV-001`..`002`, `CIT-001`..`003`, `REL-001`, and `THR-001`.
- **[Technical Article](ARTICLE.md) & [Design PRFAQ](PRFAQ.md):** Background narrative and architectural rationale.

---

## Repository Layout

```text
oase-workshop/
├── README.md                                 # Quickstart, curriculum table, and repo map
├── ARTICLE.md                                # Technical overview and architecture narrative
├── PRFAQ.md                                  # Working-Backwards design document
├── .env.example                              # Generic environment template
├── docs/                                     # Step-by-step workshop modules (00–07 + connectivity reference)
├── scripts/
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
    ├── ch2/                                  # Stage 1 completed (WO-001..003: Genetics & GTEx validated)
    ├── ch3/                                  # Stage 2 completed (WO-001..005: AF3, fpocket & Vina validated)
    └── ch4/                                  # Stages 3–4 completed (WO-001..008: ADMET, PK & Dossier validated)
```

Each checkpoint directory (`checkpoints/ch1`..`ch4`) is a complete, schema-valid OASE workspace containing `.oase/control/work-orders/WO-*.json`, `raw/<class>/*` artifacts, `<artifact>.meta.json` SHA-256 sidecars, `<stem>.analysis.json` metric records, `findings/**/*.md` synthesis reports, and `VAL-WO-*.json` validation receipts.

---

## Customer-Specific Overlays

This repository is intentionally generic. To generate a customer-tailored workshop bundle (custom internal portal URL, GCP project ID, target antigen, or therapeutic program name) without committing customer identifiers to git:

```bash
cp overlays/customer-overlay.env.example overlays/acme-bio.local.env
./scripts/render-customer-overlay.sh overlays/acme-bio.local.env
```

Rendered bundles are written to `overlays/customers/<slug>/` (gitignored) and automatically checked by `./scripts/preflight.sh --check-hygiene`.

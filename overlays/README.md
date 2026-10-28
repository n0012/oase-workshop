# Customer-Specific Workshop Overlays (`overlays/`)

The public `oase-workshop` repository is **100% generic and customer-agnostic** so it can be shared openly on GitHub (`Translational R&D`, `oral-pcsk9-ascvd`, compound series `OASE-PCSK9-014`, `@example-biopharma.com`, `<YOUR_GCP_PROJECT_ID>`).

When delivering a dedicated hands-on workshop for a specific biopharma customer or internal R&D franchise, use the **Customer Overlay Generator** (`scripts/render-customer-overlay.sh`) to produce a tailored local bundle under `overlays/customers/<customer-slug>/`—which is strictly excluded by `.gitignore` so customer names, stakeholder emails, and internal GCP project IDs are never committed to the public repository.

---

## 1. Quick Start: Render a Customer-Specific Workshop Bundle (`<1 Second`)

```bash
# 1. Copy the example overlay configuration to a gitignored .local.env file:
cp overlays/customer-overlay.env.example overlays/acme-bio.local.env

# 2. Edit overlays/acme-bio.local.env with the customer's org name, project slug,
#    compound prefix, participating scientist emails, and GCP project ID.

# 3. Render the tailored customer bundle into overlays/customers/<slug>/:
./scripts/render-customer-overlay.sh overlays/acme-bio.local.env
```

---

## 2. What `render-customer-overlay.sh` Customizes Automatically

| Generic Public Default | Overlay Variable | Example Customer Value | Where It Is Substituted |
|---|---|---|---|
| `Translational R&D` | `WORKSHOP_ORG_NAME` | `Acme Bio R&D` | `README.md`, `ARTICLE.md`, `PRFAQ.md`, `docs/*.md` |
| `Translational R&D — Oral PCSK9 ASCVD` | `WORKSHOP_PROJECT_NAME` | `Acme Bio — Oral PCSK9 ASCVD` | `docs/01-tour-the-grove.md`, `docs/surface-connectivity-reference.md` |
| `oral-pcsk9-ascvd` | `WORKSHOP_PROJECT_SLUG` | `acme-pcsk9-ascvd` | `create_project` & `bootstrap_campaign` MCP payloads |
| `OASE-PCSK9-` / `oase_pcsk9_` | `WORKSHOP_COMPOUND_PREFIX` | `ACME-PCSK9-` / `acme_pcsk9_` | Stage 3 DMTA (`OASE-PCSK9-014`) & Stage 4 PK (`oase_pcsk9_014_*`) |
| `compbio-lead@example-biopharma.com`, `medchem-lead@example-biopharma.com`, `dmpk-lead@example-biopharma.com` | `WORKSHOP_MEMBER_1`, `WORKSHOP_MEMBER_2`, `WORKSHOP_MEMBER_3` | Real customer participant emails | `create_project` `members` array & CLI flags |
| `<YOUR_GCP_PROJECT_ID>` | `WORKSHOP_GCP_PROJECT_ID` | Customer / workshop GCP project ID | `.env`, `config.toml`, `create_project` payloads |
| `https://<your-scion-hub-host>` | `WORKSHOP_SCION_HUB_URL` | Live workshop Scion Hub URL | `.env`, `config.toml` |

---

## 3. Public Repo Hygiene Gate

All files under `overlays/customers/` and `overlays/*.local.env` are ignored by `.gitignore`. Before pushing any change to the public repository, verify zero customer identifiers exist in tracked files:

```bash
./scripts/preflight.sh --check-hygiene
```

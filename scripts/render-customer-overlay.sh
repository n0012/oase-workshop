#!/usr/bin/env bash
# ==============================================================================
# render-customer-overlay.sh — Generate a gitignored customer-specific workshop
# bundle from the generic public oase-workshop repository.
#
# Usage:
#   ./scripts/render-customer-overlay.sh overlays/<customer>.local.env
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <path-to-overlay.env>" >&2
  echo "Example: cp overlays/customer-overlay.env.example overlays/customer.local.env && $0 overlays/customer.local.env" >&2
  exit 1
fi

OVERLAY_ENV="$1"
if [[ ! -f "${OVERLAY_ENV}" ]]; then
  echo "ERROR: Overlay file not found: ${OVERLAY_ENV}" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "${OVERLAY_ENV}"

: "${WORKSHOP_CUSTOMER_SLUG:?Missing WORKSHOP_CUSTOMER_SLUG in ${OVERLAY_ENV}}"
: "${WORKSHOP_ORG_NAME:?Missing WORKSHOP_ORG_NAME in ${OVERLAY_ENV}}"
: "${WORKSHOP_PROJECT_NAME:?Missing WORKSHOP_PROJECT_NAME in ${OVERLAY_ENV}}"
: "${WORKSHOP_PROJECT_SLUG:?Missing WORKSHOP_PROJECT_SLUG in ${OVERLAY_ENV}}"
: "${WORKSHOP_COMPOUND_UPPER:=OASE}"
: "${WORKSHOP_COMPOUND_LOWER:=oase}"
: "${WORKSHOP_MEMBER_1:=compbio-lead@example-biopharma.com}"
: "${WORKSHOP_MEMBER_2:=medchem-lead@example-biopharma.com}"
: "${WORKSHOP_MEMBER_3:=dmpk-lead@example-biopharma.com}"
: "${WORKSHOP_SCION_HUB_URL:=https://<your-scion-hub-host>}"
: "${WORKSHOP_GCP_PROJECT_ID:=<YOUR_GCP_PROJECT_ID>}"
: "${WORKSHOP_SERVICE_ACCOUNT_EMAIL:=scion-default-agent@${WORKSHOP_GCP_PROJECT_ID}.iam.gserviceaccount.com}"

OUT_DIR="${REPO_ROOT}/overlays/customers/${WORKSHOP_CUSTOMER_SLUG}"
rm -rf "${OUT_DIR}"
mkdir -p "${OUT_DIR}/docs" "${OUT_DIR}/checkpoints"

cp -R "${REPO_ROOT}/README.md" "${REPO_ROOT}/ARTICLE.md" "${REPO_ROOT}/PRFAQ.md" "${REPO_ROOT}/.env.example" "${OUT_DIR}/"
cp -R "${REPO_ROOT}/docs/." "${OUT_DIR}/docs/"
if [[ -d "${REPO_ROOT}/checkpoints" ]]; then
  cp -R "${REPO_ROOT}/checkpoints/." "${OUT_DIR}/checkpoints/"
fi

# Apply deterministic substitutions across all markdown & JSON files in OUT_DIR
python3 - "${OUT_DIR}" \
  "${WORKSHOP_ORG_NAME}" \
  "${WORKSHOP_PROJECT_NAME}" \
  "${WORKSHOP_PROJECT_SLUG}" \
  "${WORKSHOP_COMPOUND_UPPER}" \
  "${WORKSHOP_COMPOUND_LOWER}" \
  "${WORKSHOP_MEMBER_1}" \
  "${WORKSHOP_MEMBER_2}" \
  "${WORKSHOP_MEMBER_3}" \
  "${WORKSHOP_SCION_HUB_URL}" \
  "${WORKSHOP_GCP_PROJECT_ID}" \
  "${WORKSHOP_SERVICE_ACCOUNT_EMAIL}" << 'PYEOF'
import os, sys

(
    out_dir,
    org_name,
    proj_name,
    proj_slug,
    comp_upper,
    comp_lower,
    m1,
    m2,
    m3,
    hub_url,
    gcp_proj,
    sa_email,
) = sys.argv[1:]

replacements = [
    ("Translational R&D — Oral PCSK9 ASCVD", proj_name),
    ("Translational R&D", org_name),
    ("oral-pcsk9-ascvd", proj_slug),
    ("OASE-PCSK9-", f"{comp_upper}-PCSK9-"),
    ("oase_pcsk9_", f"{comp_lower}_pcsk9_"),
    ("compbio-lead@example-biopharma.com", m1),
    ("medchem-lead@example-biopharma.com", m2),
    ("dmpk-lead@example-biopharma.com", m3),
    ("scientist1@example-biopharma.com", m1),
    ("scientist2@example-biopharma.com", m2),
    ("lead@example-biopharma.com", m3),
    ("https://<your-scion-hub-host>", hub_url),
    ("scion-default-agent@<YOUR_GCP_PROJECT_ID>.iam.gserviceaccount.com", sa_email),
    ("<YOUR_GCP_PROJECT_ID>", gcp_proj),
]

for root, _, files in os.walk(out_dir):
    for fn in files:
        if fn.endswith((".md", ".json", ".env", ".example", ".yaml", ".toml")):
            p = os.path.join(root, fn)
            with open(p, "r", encoding="utf-8") as f:
                txt = f.read()
            for old, new in replacements:
                txt = txt.replace(old, new)
            with open(p, "w", encoding="utf-8") as f:
                f.write(txt)
PYEOF

echo "[OK] Rendered customized workshop overlay for '${WORKSHOP_ORG_NAME}' at:"
echo "     ${OUT_DIR}"
echo "     (Note: overlays/customers/ is gitignored and never pushed to public GitHub)"

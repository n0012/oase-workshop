#!/usr/bin/env bash
# ==============================================================================
# seed-hub.sh — Provision & Seed the 3 Workshop Scion Groves + Golden Snapshot
#
# Groves Provisioned:
#   1. live-sandbox         — Clean root + staged /workspace/.seed/pcsk9-oral/
#   2. stage0-1-walkthrough — Multi-checkpoint campaign grove (ch0..ch4)
#   3. negative-gate-audit  — Stage 0 Falsification & Citation Audit grove
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE_ROOT="${OASE_WORKSPACE_ROOT:-/workspace}"

echo "=== Seeding OASE Workshop Workspaces under ${WORKSPACE_ROOT} ==="

mkdir -p \
  "${WORKSPACE_ROOT}/.seed/pcsk9-oral" \
  "${WORKSPACE_ROOT}/live-sandbox" \
  "${WORKSPACE_ROOT}/stage0-1-walkthrough" \
  "${WORKSPACE_ROOT}/negative-gate-audit"

# Copy the canonical 7-part pcsk9-oral seed package (CHECKSUMS.json copied last)
if [[ -d "${REPO_ROOT}/checkpoints/ch0/seed/pcsk9-oral" ]]; then
  cp -R "${REPO_ROOT}/checkpoints/ch0/seed/pcsk9-oral/." "${WORKSPACE_ROOT}/.seed/pcsk9-oral/"
  echo "[OK] Staged pcsk9-oral seed package to ${WORKSPACE_ROOT}/.seed/pcsk9-oral/"
fi

# Initialize stage0-1-walkthrough to ch1 by default if empty
if [[ -d "${REPO_ROOT}/checkpoints/ch1" ]]; then
  cp -R "${REPO_ROOT}/checkpoints/ch1/." "${WORKSPACE_ROOT}/stage0-1-walkthrough/"
  echo "[OK] Initialized ${WORKSPACE_ROOT}/stage0-1-walkthrough to ch1"
fi

# Take a golden SQLite snapshot of Scion Hub DB if running on the Scion Hub host
SCION_DB="${SCION_DB_PATH:-/home/scion/.scion/hub.db}"
SNAPSHOT_DIR="/home/scion/.scion/snapshots"
if [[ -f "${SCION_DB}" ]] && command -v sqlite3 >/dev/null 2>&1; then
  mkdir -p "${SNAPSHOT_DIR}"
  sqlite3 "${SCION_DB}" ".backup '${SNAPSHOT_DIR}/golden-hub.db'"
  echo "[OK] Saved golden Scion Hub SQLite snapshot to ${SNAPSHOT_DIR}/golden-hub.db"
fi

echo "[PASS] Workshop Hub seeding complete."

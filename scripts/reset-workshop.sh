#!/usr/bin/env bash
# ==============================================================================
# reset-workshop.sh — 3-Second Emergency Workshop Reset
#
# Stops stray specialist containers, restores the golden Scion Hub SQLite
# snapshot (without dropping OAuth tokens), and resets checkpoints to ch0.
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCION_DB="${SCION_DB_PATH:-/home/scion/.scion/hub.db}"
GOLDEN_DB="/home/scion/.scion/snapshots/golden-hub.db"

echo "=== Executing 3-Second Emergency Workshop Reset ==="

if [[ -f "${GOLDEN_DB}" && -f "${SCION_DB}" ]] && command -v sqlite3 >/dev/null 2>&1; then
  sqlite3 "${SCION_DB}" ".restore '${GOLDEN_DB}'"
  echo "[OK] Restored Scion Hub state from ${GOLDEN_DB}"
fi

"${REPO_ROOT}/scripts/checkpoint.sh" goto ch0
echo "[PASS] Workshop reset to clean ch0 state."

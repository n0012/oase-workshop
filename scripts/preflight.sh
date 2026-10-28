#!/usr/bin/env bash
# ==============================================================================
# preflight.sh — GCP-OASE Hands-On Workshop Pre-Flight & Public Hygiene Verifier
#
# Modes:
#   ./scripts/preflight.sh                 # Full environment & endpoint pre-flight
#   ./scripts/preflight.sh --check-hygiene # Verify public repo has zero customer/internal leaks
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ "${1:-}" == "--check-hygiene" ]]; then
  echo "=== Running Public Repository Hygiene Gate ==="
  cd "${REPO_ROOT}"
  FORBIDDEN_REGEX="Amgen|ARIA|Lili Peng|Mickey Makhija|Andres Plata|@amgen\.com|Thousand Oaks|pharma-oss-factory|826100493373|5713950e|\bRVP\b|\bVenter\b|Argolis|argolis"
  if git grep -n -I -E "${FORBIDDEN_REGEX}" -- . ":(exclude)scripts/preflight.sh" ; then
    echo "[FAIL] Customer-specific or internal identifiers detected in tracked files!" >&2
    exit 1
  fi
  echo "[PASS] Zero customer-specific or internal identifiers found in tracked files."
  exit 0
fi

echo "=== GCP-OASE Workshop Environment Pre-Flight Check ==="

# 1. Load .env if present
if [[ -f "${REPO_ROOT}/.env" ]]; then
  # shellcheck disable=SC1091
  source "${REPO_ROOT}/.env"
  echo "[OK] Loaded ${REPO_ROOT}/.env"
else
  echo "[WARN] No .env found at ${REPO_ROOT}/.env (copy .env.example to .env for live GCP checks)"
fi

# 2. Check Shared Tools Volume (/scion-volumes/tools/env.sh)
OASE_TOOLS_HOME="${OASE_TOOLS_HOME:-/scion-volumes/tools}"
if [[ -f "${OASE_TOOLS_HOME}/env.sh" ]]; then
  # shellcheck disable=SC1090
  source "${OASE_TOOLS_HOME}/env.sh"
  echo "[OK] Sourced ${OASE_TOOLS_HOME}/env.sh"
else
  echo "[INFO] ${OASE_TOOLS_HOME}/env.sh not mounted on this host (skipping container-local binary checks)"
fi

# 3. Check Offline KaTeX Assets (required by oase site build)
if [[ -d "${OASE_TOOLS_HOME}" ]]; then
  KATEX_VENDOR="${OASE_TOOLS_HOME}/vendor/katex/katex.min.css"
  KATEX_NPM="${OASE_TOOLS_HOME}/npm/node_modules/katex/dist/katex.min.css"
  if [[ ! -f "${KATEX_VENDOR}" && -f "${KATEX_NPM}" ]]; then
    mkdir -p "$(dirname "${KATEX_VENDOR}")"
    cp -R "${OASE_TOOLS_HOME}/npm/node_modules/katex/dist/." "$(dirname "${KATEX_VENDOR}")/"
    echo "[OK] Synced offline KaTeX assets to ${KATEX_VENDOR}"
  elif [[ -f "${KATEX_VENDOR}" ]]; then
    echo "[OK] Offline KaTeX assets verified at ${KATEX_VENDOR}"
  fi
fi

# 4. Run oase doctor if oase is on PATH
if command -v oase >/dev/null 2>&1; then
  echo "=== Running oase doctor --json ==="
  oase doctor --json
else
  echo "[INFO] 'oase' CLI not on host PATH (run inside OASE container or Scion Hub VM)"
fi

# 5. Verify Scion Hub connectivity if SCION_HUB_URL is configured
if [[ -n "${SCION_HUB_URL:-}" ]] && command -v scion >/dev/null 2>&1; then
  echo "=== Checking Scion Hub Status (${SCION_HUB_URL}) ==="
  scion --hub "${SCION_HUB_URL}" hub status || echo "[WARN] Run 'scion --hub ${SCION_HUB_URL} auth login' to authenticate."
fi

echo "[PASS] Workshop pre-flight complete."

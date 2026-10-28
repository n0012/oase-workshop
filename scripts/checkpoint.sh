#!/usr/bin/env bash
# ==============================================================================
# checkpoint.sh — Campaign State Manager for GCP-OASE Workshops (ch0..ch4)
#
# Usage:
#   ./scripts/checkpoint.sh status
#   ./scripts/checkpoint.sh list
#   ./scripts/checkpoint.sh jump <ch0|ch1|ch2|ch3|ch4> [target-workspace-dir]
#   ./scripts/checkpoint.sh goto <ch0|ch1|ch2|ch3|ch4> [target-workspace-dir]
#   ./scripts/checkpoint.sh diff <chA> <chB> [target-workspace-dir]
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ACTION="${1:-status}"
TARGET_CP="${2:-}"
DEFAULT_WS="/workspace/stage0-1-walkthrough"
if [[ ! -d "/workspace" && ! -w "/" ]]; then
  DEFAULT_WS="${TMPDIR:-/tmp}/oase-workshop-workspace"
fi
WORKSPACE_DIR="${3:-${OASE_WALKTHROUGH_DIR:-${DEFAULT_WS}}}"

declare -A CP_DESC=(
  ["ch0"]="Stage 0 Pre-Campaign Seed Staged (seed/pcsk9-oral/ with campaign-seed.json & CHECKSUMS.json)"
  ["ch1"]="Stage 0 Complete — Co-Scientist Seed Ingested & Validated (WO-001)"
  ["ch2"]="Stage 1 Complete — Open Targets Genetics (L2G 0.89) & GTEx Liver Expression (312.4 TPM) Validated (WO-001..003)"
  ["ch3"]="Stage 2 Complete — AlphaFold 3 (ipTM 0.84), fpocket (0.78) & AutoDock Vina (-9.4 kcal/mol) Validated (WO-001..005)"
  ["ch4"]="Stages 3–4 Complete — Chemprop ADMET (PCSK9-A03 Nominated), Oral PK (88% Coverage) & Dossier Portal (WO-001..008)"
)

case "${ACTION}" in
  list|status)
    echo "=== GCP-OASE Workshop Campaign Checkpoints ==="
    for cp in ch0 ch1 ch2 ch3 ch4; do
      echo "  ${cp} : ${CP_DESC[$cp]}"
    done
    if [[ -d "${WORKSPACE_DIR}/.git" ]]; then
      echo ""
      echo "Active workspace (${WORKSPACE_DIR}) HEAD:"
      git -C "${WORKSPACE_DIR}" status -sb
    elif [[ -d "${WORKSPACE_DIR}" ]]; then
      echo ""
      echo "Active workspace directory: ${WORKSPACE_DIR}"
    fi
    ;;

  jump|goto)
    if [[ -z "${TARGET_CP}" || -z "${CP_DESC[${TARGET_CP}]:-}" ]]; then
      echo "ERROR: Specify a valid checkpoint: ch0, ch1, ch2, ch3, or ch4" >&2
      exit 1
    fi
    echo "=== Restoring ${TARGET_CP}: ${CP_DESC[${TARGET_CP}]} ==="
    if [[ -d "${WORKSPACE_DIR}/.git" ]] && git -C "${WORKSPACE_DIR}" rev-parse "${TARGET_CP}" >/dev/null 2>&1; then
      git -C "${WORKSPACE_DIR}" checkout -f "${TARGET_CP}"
      git -C "${WORKSPACE_DIR}" clean -fd
      echo "[OK] Checked out Git tag '${TARGET_CP}' in ${WORKSPACE_DIR}"
    elif [[ -d "${REPO_ROOT}/checkpoints/${TARGET_CP}" ]]; then
      mkdir -p "${WORKSPACE_DIR}"
      rm -rf "${WORKSPACE_DIR}/.oase" "${WORKSPACE_DIR}/raw" "${WORKSPACE_DIR}/findings" "${WORKSPACE_DIR}/program-state" "${WORKSPACE_DIR}/seed"
      cp -R "${REPO_ROOT}/checkpoints/${TARGET_CP}/." "${WORKSPACE_DIR}/"
      echo "[OK] Restored checkpoint '${TARGET_CP}' into ${WORKSPACE_DIR}"
    else
      echo "ERROR: Checkpoint directory '${REPO_ROOT}/checkpoints/${TARGET_CP}' not found." >&2
      exit 1
    fi
    ;;

  diff)
    CP_A="${2:-ch3}"
    CP_B="${3:-ch4}"
    WS="${4:-${WORKSPACE_DIR}}"
    if [[ -d "${WS}/.git" ]]; then
      git -C "${WS}" diff --stat "${CP_A}" "${CP_B}"
      git -C "${WS}" diff "${CP_A}" "${CP_B}" -- program-state/ 2>/dev/null || true
    else
      diff -ru "${REPO_ROOT}/checkpoints/${CP_A}" "${REPO_ROOT}/checkpoints/${CP_B}" || true
    fi
    ;;

  *)
    echo "Usage: $0 {status|list|jump <ch0..ch4>|goto <ch0..ch4>|diff <chA> <chB>}" >&2
    exit 1
    ;;
esac

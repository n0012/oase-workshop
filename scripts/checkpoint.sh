#!/usr/bin/env bash
# ==============================================================================
# checkpoint.sh — Instant (<2s) Cooking-Show Time-Machine for OASE Workshops
#
# Usage:
#   ./scripts/checkpoint.sh status
#   ./scripts/checkpoint.sh list
#   ./scripts/checkpoint.sh goto <ch0|ch1|ch2|ch3|ch4> [target-workspace-dir]
#   ./scripts/checkpoint.sh diff <chA> <chB> [target-workspace-dir]
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ACTION="${1:-status}"
TARGET_CP="${2:-}"
WORKSPACE_DIR="${3:-${OASE_WALKTHROUGH_DIR:-/workspace/stage0-1-walkthrough}}"

declare -A CP_DESC=(
  ["ch0"]="Stage 0 Bootstrap & 7-Part Seed Package Staged (/workspace/.seed/pcsk9-oral/)"
  ["ch1"]="Stage 0 Complete — Seed Ingested (oase coscientist), DEC-001 & WO-001 (IC-001 vs IC-002)"
  ["ch2"]="Stage 1 Complete — Human Genetics (gnomAD, OpenTargets), GTEx & Live AlphaGenome (WO-002..003, DEC-004)"
  ["ch3"]="Stage 2 Complete — AFDB Q8NBP7, Live AlphaFold 3 Co-Folding, fpocket (0.68) & Vina Docking (WO-004..005, DEC-007)"
  ["ch4"]="Stages 3–4 Complete — DMTA (OASE-PCSK9-014), Oral PK Scaling, IND Dossier & 28-Page HTML Portal (WO-006..008, DEC-012)"
)

case "${ACTION}" in
  list|status)
    echo "=== OASE Workshop Time-Machine Checkpoints ==="
    for cp in ch0 ch1 ch2 ch3 ch4; do
      echo "  ${cp} : ${CP_DESC[$cp]}"
    done
    if [[ -d "${WORKSPACE_DIR}/.git" ]]; then
      echo ""
      echo "Active workspace (${WORKSPACE_DIR}) HEAD:"
      git -C "${WORKSPACE_DIR}" status -sb
    fi
    ;;

  goto)
    if [[ -z "${TARGET_CP}" || -z "${CP_DESC[${TARGET_CP}]:-}" ]]; then
      echo "ERROR: Specify a valid checkpoint: ch0, ch1, ch2, ch3, or ch4" >&2
      exit 1
    fi
    echo "=== Jumping to ${TARGET_CP}: ${CP_DESC[${TARGET_CP}]} ==="
    if [[ -d "${WORKSPACE_DIR}/.git" ]] && git -C "${WORKSPACE_DIR}" rev-parse "${TARGET_CP}" >/dev/null 2>&1; then
      git -C "${WORKSPACE_DIR}" checkout -f "${TARGET_CP}"
      git -C "${WORKSPACE_DIR}" clean -fd
      echo "[OK] Checked out Git tag '${TARGET_CP}' in ${WORKSPACE_DIR}"
    elif [[ -d "${REPO_ROOT}/checkpoints/${TARGET_CP}" ]]; then
      mkdir -p "${WORKSPACE_DIR}"
      cp -R "${REPO_ROOT}/checkpoints/${TARGET_CP}/." "${WORKSPACE_DIR}/"
      echo "[OK] Materialized checkpoint fixture '${TARGET_CP}' into ${WORKSPACE_DIR}"
    else
      echo "[INFO] Checkpoint '${TARGET_CP}' verified (run inside Scion Hub VM to materialize into ${WORKSPACE_DIR})."
    fi
    ;;

  diff)
    CP_A="${2:-ch3}"
    CP_B="${3:-ch4}"
    WS="${4:-${WORKSPACE_DIR}}"
    if [[ -d "${WS}/.git" ]]; then
      git -C "${WS}" diff --stat "${CP_A}" "${CP_B}"
      git -C "${WS}" diff "${CP_A}" "${CP_B}" -- program-state/ decisions/ 2>/dev/null || true
    else
      diff -ru "${REPO_ROOT}/checkpoints/${CP_A}" "${REPO_ROOT}/checkpoints/${CP_B}" || true
    fi
    ;;

  *)
    echo "Usage: $0 {status|list|goto <ch0..ch4>|diff <chA> <chB>}" >&2
    exit 1
    ;;
esac

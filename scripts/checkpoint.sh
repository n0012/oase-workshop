#!/usr/bin/env bash
# ==============================================================================
# checkpoint.sh — Campaign State Manager for GCP-OASE Workshops (ch0..ch7)
#
# Usage:
#   ./scripts/checkpoint.sh status
#   ./scripts/checkpoint.sh list
#   ./scripts/checkpoint.sh jump <ch0|ch1|ch2|ch3|ch4|ch5|ch6|ch7> [target-workspace-dir]
#   ./scripts/checkpoint.sh goto <ch0|ch1|ch2|ch3|ch4|ch5|ch6|ch7> [target-workspace-dir]
#   ./scripts/checkpoint.sh init-git-tags <target-workspace-dir>
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

ALL_CPS=(ch0 ch1 ch2 ch3 ch4 ch5 ch6 ch7)

declare -A CP_DESC=(
  ["ch0"]="Initial Seed (t=0) — Pre-Campaign Seed Staged (seed/pcsk9-oral/ with campaign-seed.json & CHECKSUMS.json, 0 WOs closed)"
  ["ch1"]="Step 1 Complete — Co-Scientist Tournament Seed Ingested & Validated (WO-001, IC-001 Elo 1642.5)"
  ["ch2"]="Step 2 + Gate 1 Complete — Human Genetics (gnomAD, OpenTargets), GTEx Liver (184.2 TPM) & AlphaGenome (WO-001..003)"
  ["ch3"]="Step 3 + Gate 2 Complete — AlphaFold 3 (ipTM 0.84), fpocket Groove (0.68) & AutoDock Vina (-9.4 kcal/mol) (WO-001..005)"
  ["ch4"]="Step 4 + Gate 3 + Wet-Lab Handoff Slot — ADMET Disqualifies PCSK9-A02 (hERG); OASE-PCSK9-014 Queued for Wet-Lab Assays (WO-001..006)"
  ["ch5"]="Step 5 + Gate 4 Complete — Human Oral PK (40.0 mg QD, F=52%, t1/2=14.8 h) & Candidate Nomination Dossier (WO-001..008)"
  ["ch6"]="Step 6 Governance Audit Complete — 3 Blocked Adversarial Tamper Drills + 1 Co-Signed Human Override (DEC-OVERRIDE-001)"
  ["ch7"]="Step 7 Mission Closeout & Portfolio Sign-Off — Executive Dossier, 30-Page Evidence Portal & GLP Tox Handoff"
)

sync_cp_into_dir() {
  local cp="$1"
  local dest="$2"
  mkdir -p "${dest}"
  rm -rf "${dest}/.oase" "${dest}/raw" "${dest}/findings" "${dest}/program-state" "${dest}/seed" "${dest}/gates" "${dest}/executive"
  cp -R "${REPO_ROOT}/checkpoints/${cp}/." "${dest}/"
}

case "${ACTION}" in
  list|status)
    echo "=== GCP-OASE Workshop Campaign Checkpoints (ch0..ch7) ==="
    for cp in "${ALL_CPS[@]}"; do
      echo "  ${cp} : ${CP_DESC[$cp]}"
    done
    if [[ -d "${WORKSPACE_DIR}/.git" ]]; then
      echo ""
      echo "Active workspace (${WORKSPACE_DIR}) HEAD:"
      git -C "${WORKSPACE_DIR}" status -sb
      git -C "${WORKSPACE_DIR}" describe --tags --exact-match 2>/dev/null || true
    elif [[ -d "${WORKSPACE_DIR}" ]]; then
      echo ""
      echo "Active workspace directory: ${WORKSPACE_DIR}"
    fi
    ;;

  jump|goto)
    if [[ -z "${TARGET_CP}" || -z "${CP_DESC[${TARGET_CP}]:-}" ]]; then
      echo "ERROR: Specify a valid checkpoint: ch0, ch1, ch2, ch3, ch4, ch5, ch6, or ch7" >&2
      exit 1
    fi
    echo "=== Restoring ${TARGET_CP}: ${CP_DESC[${TARGET_CP}]} ==="
    if [[ -d "${WORKSPACE_DIR}/.git" ]] && git -C "${WORKSPACE_DIR}" rev-parse "${TARGET_CP}" >/dev/null 2>&1; then
      git -C "${WORKSPACE_DIR}" checkout -f "${TARGET_CP}"
      git -C "${WORKSPACE_DIR}" clean -fd -e .scion -e .scion-volumes -e .agents -e skills -e templates
      echo "[OK] Checked out Git tag '${TARGET_CP}' in ${WORKSPACE_DIR}"
    elif [[ -d "${REPO_ROOT}/checkpoints/${TARGET_CP}" ]]; then
      sync_cp_into_dir "${TARGET_CP}" "${WORKSPACE_DIR}"
      echo "[OK] Restored checkpoint '${TARGET_CP}' into ${WORKSPACE_DIR}"
    else
      echo "ERROR: Checkpoint directory '${REPO_ROOT}/checkpoints/${TARGET_CP}' not found." >&2
      exit 1
    fi
    ;;

  init-git-tags)
    TARGET_WS="${2:-${WORKSPACE_DIR}}"
    FINAL_CP="${3:-ch0}"
    mkdir -p "${TARGET_WS}"
    if [[ ! -d "${TARGET_WS}/.git" ]]; then
      git -C "${TARGET_WS}" init -q -b main
    fi
    git -C "${TARGET_WS}" config user.name "OASE Checkpoint Engine"
    git -C "${TARGET_WS}" config user.email "oase-checkpoint@example.invalid"
    cat > "${TARGET_WS}/.gitignore" <<'GITIGNORE'
.scion/
.scion-volumes/
.agents/
skills/
templates/
__pycache__/
*.pyc
GITIGNORE
    for cp in "${ALL_CPS[@]}"; do
      sync_cp_into_dir "${cp}" "${TARGET_WS}"
      git -C "${TARGET_WS}" add -A
      git -C "${TARGET_WS}" commit -q --allow-empty -m "Checkpoint ${cp}: ${CP_DESC[$cp]}"
      git -C "${TARGET_WS}" tag -f "${cp}"
    done
    git -C "${TARGET_WS}" checkout -q -f "${FINAL_CP}"
    git -C "${TARGET_WS}" clean -fd -q -e .scion -e .scion-volumes -e .agents -e skills -e templates
    echo "[OK] Initialized Git tags ch0..ch7 in ${TARGET_WS} (active tag: ${FINAL_CP})"
    ;;

  diff)
    CP_A="${2:-ch4}"
    CP_B="${3:-ch5}"
    WS="${4:-${WORKSPACE_DIR}}"
    if [[ -d "${WS}/.git" ]] && git -C "${WS}" rev-parse "${CP_A}" >/dev/null 2>&1; then
      git -C "${WS}" diff --stat "${CP_A}" "${CP_B}"
      git -C "${WS}" diff "${CP_A}" "${CP_B}" -- program-state/ gates/ 2>/dev/null || true
    else
      diff -ru "${REPO_ROOT}/checkpoints/${CP_A}" "${REPO_ROOT}/checkpoints/${CP_B}" || true
    fi
    ;;

  *)
    echo "Usage: $0 {status|list|jump <ch0..ch7>|goto <ch0..ch7>|init-git-tags <dir> [active-cp]|diff <chA> <chB>}" >&2
    exit 1
    ;;
esac

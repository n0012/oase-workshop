#!/usr/bin/env bash
# ==============================================================================
# OASE Workshop — Google Cloud Shell + Antigravity (agy) Setup for Dr. Sarah Chen
# Run inside Google Cloud Shell (signed in as oase-sarah@losiern-1.altostrat.com):
#   bash scripts/setup-sarah-cloudshell.sh
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export GCP_PROJECT_ID="${GCP_PROJECT_ID:-losiern-oase-workshop}"
export OASE_GCP_PROJECT="${GCP_PROJECT_ID}"
export OASE_GCP_ZONE="${OASE_GCP_ZONE:-us-central1-c}"
export OASE_GCE_INSTANCE="${OASE_GCE_INSTANCE:-scion-hub-oase}"

gcloud config set project "${GCP_PROJECT_ID}" >/dev/null 2>&1 || true

mkdir -p ~/.gemini/skills ~/.claude/skills "${REPO_ROOT}/.agent/skills"
ln -sfn "${REPO_ROOT}/.agent/skills/scion-oase-bridge" ~/.gemini/skills/scion-oase-bridge
ln -sfn "${REPO_ROOT}/.agent/skills/scion-oase-bridge" ~/.claude/skills/scion-oase-bridge

echo "=============================================================================="
echo " ✓ Google Cloud Shell + Antigravity (AGY) <-> Scion Hub Bridge Ready"
echo "   Persona : oase-sarah@losiern-1.altostrat.com (Dr. Sarah Chen, Program Lead)"
echo "   Project : ${GCP_PROJECT_ID} (${OASE_GCP_ZONE} / ${OASE_GCE_INSTANCE})"
echo "   Skill   : scion-oase-bridge (.agent/skills/scion-oase-bridge/SKILL.md)"
echo "=============================================================================="
echo ""
echo "Prompt 1 — Initiate / Bootstrap a New Campaign from Antigravity (agy):"
echo "  agy -p \"Use scion-oase-bridge to bootstrap the io-cold-to-hot campaign from seed/io-cold-to-hot/campaign-seed.json, verify oase doctor (78/78 checks), and list the 17-agent 4-tier discovery team.\""
echo ""
echo "Prompt 2 — Analyze a Completed Program Run & Audit the DEC-008 Wet-Lab Wall:"
echo "  agy -p \"Use scion-oase-bridge to analyze io-cold-to-hot across WO-001..WO-008: read decision-log.md and reports/wet-lab-wall-readiness.md, and message @science-program-lead to explain why Series A (oase_enpp1_009) hit the DEC-008 Wet-Lab Wall and how Series B (oase_enpp1_019) recovered oral absorption.\""
echo "=============================================================================="

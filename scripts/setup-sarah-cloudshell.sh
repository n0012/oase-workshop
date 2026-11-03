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

mkdir -p ~/.gemini/skills ~/.gemini/antigravity/skills ~/.claude/skills "${REPO_ROOT}/.agent/skills"
ln -sfn "${REPO_ROOT}/.agent/skills/scion-oase-bridge" ~/.gemini/skills/scion-oase-bridge
ln -sfn "${REPO_ROOT}/.agent/skills/scion-oase-bridge" ~/.gemini/antigravity/skills/scion-oase-bridge
ln -sfn "${REPO_ROOT}/.agent/skills/scion-oase-bridge" ~/.claude/skills/scion-oase-bridge

# Register the scion MCP server in ~/.gemini/antigravity/mcp_config.json and ~/.gemini/settings.json
python3 - "${REPO_ROOT}/scripts/scion_mcp_server.py" "${GCP_PROJECT_ID}" "${OASE_GCP_ZONE}" "${OASE_GCE_INSTANCE}" <<'PY'
import json
import sys
from pathlib import Path

server_py, proj, zone, inst = sys.argv[1:5]
mcp_entry = {
    "command": "python3",
    "args": [server_py],
    "env": {
        "OASE_GCP_PROJECT": proj,
        "OASE_GCP_ZONE": zone,
        "OASE_GCE_INSTANCE": inst,
    },
}

for cfg_path in [
    Path.home() / ".gemini" / "antigravity" / "mcp_config.json",
    Path.home() / ".gemini" / "config" / "mcp_config.json",
]:
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        data = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else {}
    except Exception:
        data = {}
    if not isinstance(data, dict):
        data = {}
    servers = data.setdefault("mcpServers", {})
    servers["scion"] = mcp_entry
    cfg_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
PY

echo "=============================================================================="
echo " ✓ Google Cloud Shell + Antigravity (agy CLI) <-> Scion Hub Bridge Ready"
echo "   Persona    : oase-sarah@losiern-1.altostrat.com (Dr. Sarah Chen, Program Lead)"
echo "   Project    : ${GCP_PROJECT_ID} (${OASE_GCP_ZONE} / ${OASE_GCE_INSTANCE})"
echo "   Skill      : scion-oase-bridge (.agent/skills/scion-oase-bridge/SKILL.md)"
echo "   MCP Server : scion (${REPO_ROOT}/scripts/scion_mcp_server.py)"
echo "=============================================================================="
echo ""
echo "Workflow 1 — Initiate a New Science Agent Campaign (CLI Feedback -> Scion Reacts):"
echo "  agy -p \"Use scion-oase-bridge to bootstrap the io-cold-to-hot campaign from seed/io-cold-to-hot/campaign-seed.json, verify oase doctor (78/78 checks), list the 17-agent 4-tier discovery team, and show @controller and @science-program-lead's live kickoff feedback.\""
echo ""
echo "Workflow 2 — Analyze a Completed Program Run & Send Live Feedback to Scion:"
echo "  agy -p \"Use scion-oase-bridge to analyze io-cold-to-hot across WO-001..WO-008: read decision-log.md and reports/wet-lab-wall-readiness.md, and message @science-program-lead to explain why Series A (oase_enpp1_009) hit the DEC-008 Wet-Lab Wall and how Series B (oase_enpp1_019) recovered oral absorption.\""
echo ""
echo "Direct MCP CLI Equivalents (without agy wrapper):"
echo "  python3 scripts/scion_mcp_server.py --cli hub_status"
echo "  python3 scripts/scion_mcp_server.py --cli bootstrap_campaign --project io-cold-to-hot"
echo "  python3 scripts/scion_mcp_server.py --cli list_agents --project io-cold-to-hot"
echo "  python3 scripts/scion_mcp_server.py --cli dav_read --project io-cold-to-hot --path reports/wet-lab-wall-readiness.md"
echo "  python3 scripts/scion_mcp_server.py --cli send_message --project io-cold-to-hot --agent science-program-lead --message \"Audit DEC-008 Wet-Lab Wall\""
echo "  python3 scripts/scion_mcp_server.py --cli get_messages --project io-cold-to-hot --limit 10"
echo "=============================================================================="

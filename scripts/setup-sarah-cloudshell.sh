#!/usr/bin/env bash
# ==============================================================================
# OASE Workshop — Google Cloud Shell + Antigravity (agy) Setup for Workshop Pods
# Run inside Google Cloud Shell (signed in as oase-sarah..oase-claire@losiern-1.altostrat.com):
#   bash scripts/setup-sarah-cloudshell.sh
# ==============================================================================
set -euo pipefail

SCRIPT_SRC="${BASH_SOURCE[0]:-}"
if [[ -n "${SCRIPT_SRC}" && -f "$(dirname "${SCRIPT_SRC}")/scion_mcp_server.py" ]]; then
  REPO_ROOT="$(cd "$(dirname "${SCRIPT_SRC}")/.." && pwd)"
elif [[ -f "$PWD/scripts/scion_mcp_server.py" ]]; then
  REPO_ROOT="$PWD"
else
  REPO_ROOT="$HOME/oase-workshop"
  if [[ ! -d "${REPO_ROOT}/.git" ]]; then
    echo "Cloning https://github.com/n0012/oase-workshop.git into ${REPO_ROOT} ..."
    git clone https://github.com/n0012/oase-workshop.git "${REPO_ROOT}"
  else
    git -C "${REPO_ROOT}" pull --ff-only || true
  fi
fi

export GCP_PROJECT_ID="${GCP_PROJECT_ID:-losiern-oase-workshop}"
export OASE_GCP_PROJECT="${GCP_PROJECT_ID}"
export OASE_GCP_ZONE="${OASE_GCP_ZONE:-us-central1-c}"
export OASE_GCE_INSTANCE="${OASE_GCE_INSTANCE:-scion-hub-oase}"

mkdir -p "$HOME/.local/bin"
export PATH="$HOME/.local/bin:$PATH"
if [[ -f "$HOME/.bashrc" ]] && ! grep -q 'HOME/.local/bin' "$HOME/.bashrc" 2>/dev/null; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
fi

gcloud config set project "${GCP_PROJECT_ID}" >/dev/null 2>&1 || true

mkdir -p ~/.gemini/skills ~/.gemini/antigravity/skills ~/.gemini/antigravity-cli/skills ~/.claude/skills "${REPO_ROOT}/.agent/skills"
ln -sfn "${REPO_ROOT}/.agent/skills/scion-oase-bridge" ~/.gemini/skills/scion-oase-bridge
ln -sfn "${REPO_ROOT}/.agent/skills/scion-oase-bridge" ~/.gemini/antigravity/skills/scion-oase-bridge
ln -sfn "${REPO_ROOT}/.agent/skills/scion-oase-bridge" ~/.gemini/antigravity-cli/skills/scion-oase-bridge
ln -sfn "${REPO_ROOT}/.agent/skills/scion-oase-bridge" ~/.claude/skills/scion-oase-bridge

# Register the scion MCP server across Antigravity CLI and Cloud Shell Gemini CLI configs
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
    Path.home() / ".gemini" / "settings.json",
    Path.home() / ".gemini" / "antigravity" / "mcp_config.json",
    Path.home() / ".gemini" / "antigravity-cli" / "mcp_config.json",
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

# Ensure headless `agy -p "..."` auto-approves MCP, file reads, and shell commands
agy_settings_path = Path.home() / ".gemini" / "antigravity-cli" / "settings.json"
agy_settings_path.parent.mkdir(parents=True, exist_ok=True)
try:
    agy_settings = json.loads(agy_settings_path.read_text(encoding="utf-8")) if agy_settings_path.exists() else {}
except Exception:
    agy_settings = {}
if not isinstance(agy_settings, dict):
    agy_settings = {}
agy_settings.setdefault("gcp", {"project": proj, "location": "global"})
agy_settings["toolPermission"] = "always-proceed"
perms = agy_settings.setdefault("permissions", {})
allow_list = perms.setdefault("allow", [])
for rule in ("mcp(*)", "read_file(*)", "run_command(*)"):
    if rule not in allow_list:
        allow_list.append(rule)
agy_settings_path.write_text(json.dumps(agy_settings, indent=2) + "\n", encoding="utf-8")
PY

# In Google Cloud Shell, `gemini` CLI is pre-installed while `agy` may not be pre-installed.
# Provide a seamless `~/.local/bin/agy` shim delegating to `gemini` with the registered `scion` MCP server.
if ! command -v agy >/dev/null 2>&1; then
  cat > "$HOME/.local/bin/agy" <<'SHIM'
#!/usr/bin/env bash
set -euo pipefail
ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)
      shift
      if [[ $# -gt 0 ]]; then
        case "$1" in
          gemini-4-*|gemini-3.*|gemini-4-argon-*|gemini-2.0-*) ARGS+=("--model" "$1") ;;
          *) ARGS+=("--model" "gemini-4-argon") ;;
        esac
        shift
      fi
      ;;
    *)
      ARGS+=("$1")
      shift
      ;;
  esac
done
if command -v gemini >/dev/null 2>&1; then
  exec gemini "${ARGS[@]}"
fi
echo "Error: Neither agy nor gemini CLI found in PATH. Run direct MCP CLI instead:" >&2
echo "  python3 ~/oase-workshop/scripts/scion_mcp_server.py --cli hub_status" >&2
exit 1
SHIM
  chmod +x "$HOME/.local/bin/agy"
fi

# Start persistent background IAP TCP tunnel to scion-hub-oase:8780 on 127.0.0.1:18780
if ! curl -fsS --max-time 2 http://127.0.0.1:18780/api/scion/hub-status >/dev/null 2>&1; then
  echo "Starting background IAP tunnel to ${OASE_GCE_INSTANCE}:8780 on 127.0.0.1:18780 ..."
  nohup gcloud compute start-iap-tunnel "${OASE_GCE_INSTANCE}" 8780 \
    --local-host-port=127.0.0.1:18780 \
    --project="${GCP_PROJECT_ID}" \
    --zone="${OASE_GCP_ZONE}" \
    --quiet >/tmp/scion-iap-tunnel.log 2>&1 &
  for _ in {1..15}; do
    if curl -fsS --max-time 1 http://127.0.0.1:18780/api/scion/hub-status >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done
fi

ACTIVE_PERSONA="$(gcloud config get-value account 2>/dev/null || echo 'oase-sarah@losiern-1.altostrat.com')"
echo "=============================================================================="
echo " ✓ Google Cloud Shell + Antigravity (agy CLI) <-> Scion Hub Bridge Ready"
echo "   Persona    : ${ACTIVE_PERSONA}"
echo "   Project    : ${GCP_PROJECT_ID} (${OASE_GCP_ZONE} / ${OASE_GCE_INSTANCE})"
echo "   Skill      : scion-oase-bridge (.agent/skills/scion-oase-bridge/SKILL.md)"
echo "   MCP Server : scion (${REPO_ROOT}/scripts/scion_mcp_server.py)"
echo "=============================================================================="
python3 "${REPO_ROOT}/scripts/scion_mcp_server.py" --cli hub_status || true
echo ""
echo "Workflow 1 — Initiate / Verify a Science Agent Campaign (CLI Feedback -> Scion Reacts):"
echo "  agy -p \"Use scion-oase-bridge to bootstrap the io-cold-to-hot campaign, verify oase doctor (78/78 checks), list the 17-agent 4-tier discovery team, and show @controller and @science-program-lead's live kickoff feedback.\""
echo ""
echo "Workflow 2 — Analyze a Completed Program Run & Send Live Feedback to Scion:"
echo "  agy -p \"Use scion-oase-bridge to analyze io-cold-to-hot across WO-001..WO-008: read program-state/decision-log.md and executive/CANDIDATE-SUMMARY.md, and message @science-program-lead to explain why Series A (oase_enpp1_009) hit the DEC-008 Wet-Lab Wall and how Series B (oase_enpp1_019) recovered oral absorption.\""
echo ""
echo "Direct MCP CLI Equivalents (instant zero-LLM execution):"
echo "  python3 ${REPO_ROOT}/scripts/scion_mcp_server.py --cli hub_status"
echo "  python3 ${REPO_ROOT}/scripts/scion_mcp_server.py --cli list_agents --project io-cold-to-hot"
echo "  python3 ${REPO_ROOT}/scripts/scion_mcp_server.py --cli dav_read --project io-cold-to-hot --path program-state/decision-log.md"
echo "  python3 ${REPO_ROOT}/scripts/scion_mcp_server.py --cli dav_read --project io-cold-to-hot --path executive/CANDIDATE-SUMMARY.md"
echo "  python3 ${REPO_ROOT}/scripts/scion_mcp_server.py --cli send_message --project io-cold-to-hot --agent science-program-lead --message \"Audit DEC-008 Wet-Lab Wall\""
echo "  python3 ${REPO_ROOT}/scripts/scion_mcp_server.py --cli get_messages --project io-cold-to-hot --limit 10"
echo "=============================================================================="

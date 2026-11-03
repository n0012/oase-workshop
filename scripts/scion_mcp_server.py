#!/usr/bin/env python3
"""Host-side Scion / OASE MCP Server (`scion_mcp_server.py`) for Antigravity (`agy`) & Gemini CLI.

Connects to the Argolis `scion-hub-oase` instance (`losiern-oase-workshop`, `us-central1-c`)
either over a local IAP tunnel (`http://127.0.0.1:18780` / `http://127.0.0.1:8780`) or
automatically via `gcloud compute ssh` using the non-interactive service account
`claude-vertex@losiern-vibe.iam.gserviceaccount.com` (zero corporate `UberProxy` or
`gcert` dependencies).

Supports two modes:
  1. Standard MCP JSON-RPC 2.0 over `stdio` (default when launched by Antigravity / Gemini CLI).
  2. Direct `--cli` mode for shell or agent tool invocations:
       python3 scripts/scion_mcp_server.py --cli hub_status
       python3 scripts/scion_mcp_server.py --cli list_projects
       python3 scripts/scion_mcp_server.py --cli list_agents --project io-cold-to-hot
       python3 scripts/scion_mcp_server.py --cli dav_list --project io-cold-to-hot --path reports
       python3 scripts/scion_mcp_server.py --cli dav_read --project io-cold-to-hot --path reports/wet-lab-wall-readiness.md
       python3 scripts/scion_mcp_server.py --cli get_messages --project io-cold-to-hot --agent science-program-lead
       python3 scripts/scion_mcp_server.py --cli send_message --project io-cold-to-hot --agent science-program-lead --message "..."
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

GCP_PROJECT = os.environ.get("OASE_GCP_PROJECT", "losiern-oase-workshop")
GCP_ZONE = os.environ.get("OASE_GCP_ZONE", "us-central1-c")
GCE_INSTANCE = os.environ.get("OASE_GCE_INSTANCE", "scion-hub-oase")
SA_ACCOUNT = os.environ.get("OASE_GCLOUD_ACCOUNT", "").strip()
DEFAULT_LAB_SA = "claude-vertex@losiern-vibe.iam.gserviceaccount.com"
LOCAL_CONTROLLER_URLS = (
    os.environ.get("OASE_STATE_CONTROLLER_URL", "").strip(),
    "http://127.0.0.1:18780",
    "http://127.0.0.1:8780",
)


def _has_gcloud_account(acct: str) -> bool:
    """Return True if `acct` is present in the local gcloud credential store."""
    if not acct:
        return False
    creds_db = os.path.expanduser("~/.config/gcloud/credentials.db")
    try:
        if os.path.exists(creds_db):
            with open(creds_db, "rb") as fh:
                return acct.encode("utf-8") in fh.read()
    except Exception:
        pass
    return False


def _call_bridge(method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Call `/api/scion/...` over local tunnel if active, else via `gcloud compute ssh`."""
    body_bytes = json.dumps(payload).encode("utf-8") if payload is not None else None
    http_timeout = 18.0 if method.upper() == "POST" else 3.0
    for base_url in LOCAL_CONTROLLER_URLS:
        if not base_url:
            continue
        url = f"{base_url.rstrip('/')}{path}"
        req = urllib.request.Request(
            url,
            data=body_bytes,
            method=method,
            headers={"Content-Type": "application/json"} if body_bytes else {},
        )
        try:
            with urllib.request.urlopen(req, timeout=http_timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception:
            continue

    # Fallback: execute curl directly on scion-hub-oase over IAP using active gcloud identity (or lab SA if available)
    remote_url = f"http://127.0.0.1:8780{path}"
    if method.upper() == "GET":
        remote_cmd = f"curl -sS {shlex.quote(remote_url)}"
    else:
        json_str = json.dumps(payload or {})
        remote_cmd = (
            f"curl -sS -X {shlex.quote(method.upper())} "
            f"-H 'Content-Type: application/json' "
            f"-d {shlex.quote(json_str)} "
            f"{shlex.quote(remote_url)}"
        )

    env = dict(os.environ)
    if SA_ACCOUNT:
        env["CLOUDSDK_CORE_ACCOUNT"] = SA_ACCOUNT
    elif "CLOUDSDK_CORE_ACCOUNT" not in env and _has_gcloud_account(DEFAULT_LAB_SA):
        env["CLOUDSDK_CORE_ACCOUNT"] = DEFAULT_LAB_SA

    proc = subprocess.run(
        [
            "gcloud",
            "compute",
            "ssh",
            GCE_INSTANCE,
            "--quiet",
            "--ssh-flag=-n",
            f"--project={GCP_PROJECT}",
            f"--zone={GCP_ZONE}",
            f"--command={remote_cmd}",
        ],
        env=env,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        check=False,
        timeout=55,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"SSH bridge error ({proc.returncode}): {proc.stderr or proc.stdout}")
    stdout = (proc.stdout or "").strip()
    idx = stdout.find("{")
    if idx > 0:
        stdout = stdout[idx:]
    return json.loads(stdout)


TOOLS_SCHEMA: list[dict[str, Any]] = [
    {
        "name": "hub_status",
        "description": "Verify Scion Hub connectivity, authenticated persona (Dr. Sarah Chen), and active OASE discovery projects in Argolis.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "list_projects",
        "description": "List all Scion Hub OASE discovery projects (`pcsk9-oral-live-v2`, `io-cold-to-hot`, `open-agentic-science-engine`) with agent and message counts.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "list_agents",
        "description": "List the 17-agent 4-tier discovery hierarchy (`controller`, `hypex-supervisor`, `science-program-lead`, and 12 specialists) for a Scion project.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {
                    "type": "string",
                    "description": "Project slug or UUID (e.g. `io-cold-to-hot`, `pcsk9-oral-live-v2`, `open-agentic-science-engine`).",
                }
            },
            "required": ["project"],
        },
    },
    {
        "name": "dav_list",
        "description": "List workspace files and directories in a Scion Grove (`reports/`, `.oase/workorders/`, `gates/`, etc.).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project slug or UUID."},
                "path": {"type": "string", "description": "Relative directory path inside workspace (default `.`)."},
            },
            "required": ["project"],
        },
    },
    {
        "name": "dav_read",
        "description": "Read a live Markdown, YAML, or JSON artifact from a Scion Grove (`decision-log.md`, `reports/wet-lab-wall-readiness.md`, `.oase/workorders/WO-004.md`, etc.).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project slug or UUID."},
                "path": {"type": "string", "description": "Relative file path inside workspace."},
            },
            "required": ["project", "path"],
        },
    },
    {
        "name": "get_messages",
        "description": "Retrieve recent inter-agent and user-to-agent messages from Scion Hub (`messages` table / Project Messages feed).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project slug or UUID."},
                "agent": {"type": "string", "description": "Optional agent slug filter (e.g. `science-program-lead`)."},
                "limit": {"type": "integer", "description": "Max messages to return (default 25)."},
            },
            "required": ["project"],
        },
    },
    {
        "name": "bootstrap_campaign",
        "description": "Initialize or re-verify an OASE discovery campaign Grove (`io-cold-to-hot`, `pcsk9-oral-live-v2`, `open-agentic-science-engine`) from its campaign seed, checking `oase doctor` (78/78), 41 skills, and the 17-agent 4-tier hierarchy.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project slug or UUID (default `io-cold-to-hot`)."},
            },
            "required": ["project"],
        },
    },
    {
        "name": "send_message",
        "description": "Dispatch a live instruction to a Scion agent (`@science-program-lead`, `@controller`, `@structural-biologist`, `@admet-dmpk-scientist`, etc.), logging both the instruction and the grounded reply to the Scion Web UI and Cloud Logging.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project slug or UUID (`io-cold-to-hot`, `pcsk9-oral-live-v2`, `open-agentic-science-engine`)."},
                "agent": {"type": "string", "description": "Target agent slug (default `science-program-lead`)."},
                "message": {"type": "string", "description": "Instruction or scientific question to send."},
            },
            "required": ["project", "message"],
        },
    },
]


def execute_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    if name in ("hub_status", "scion_hub_status"):
        return _call_bridge("GET", "/api/scion/hub-status")
    if name in ("list_projects", "scion_list_projects"):
        return _call_bridge("GET", "/api/scion/projects")
    if name in ("list_agents", "scion_list_agents"):
        proj = urllib.parse.quote(str(args.get("project", "io-cold-to-hot")))
        return _call_bridge("GET", f"/api/scion/projects/{proj}/agents")
    if name in ("dav_list", "scion_dav_list", "dav_read", "scion_dav_read"):
        proj = urllib.parse.quote(str(args.get("project", "io-cold-to-hot")))
        rel = urllib.parse.quote(str(args.get("path", "")))
        return _call_bridge("GET", f"/api/scion/projects/{proj}/dav?path={rel}")
    if name in ("get_messages", "scion_get_messages"):
        proj = urllib.parse.quote(str(args.get("project", "io-cold-to-hot")))
        qs: dict[str, Any] = {"limit": int(args.get("limit", 25))}
        if args.get("agent"):
            qs["agent"] = str(args["agent"])
        return _call_bridge("GET", f"/api/scion/projects/{proj}/messages?{urllib.parse.urlencode(qs)}")
    if name in ("bootstrap_campaign", "scion_bootstrap_campaign"):
        proj = urllib.parse.quote(str(args.get("project", "io-cold-to-hot")))
        return _call_bridge("POST", f"/api/scion/projects/{proj}/bootstrap", {})
    if name in ("send_message", "scion_send_message"):
        proj = urllib.parse.quote(str(args.get("project", "io-cold-to-hot")))
        return _call_bridge(
            "POST",
            f"/api/scion/projects/{proj}/message",
            {
                "agent": str(args.get("agent", "science-program-lead")),
                "message": str(args.get("message", "")),
                "type": str(args.get("type", "instruction")),
                "auto_reply": bool(args.get("auto_reply", True)),
            },
        )
    raise ValueError(f"Unknown tool: {name}")


def run_mcp_stdio() -> int:
    """Standard JSON-RPC 2.0 stdio loop for MCP clients (Antigravity / Gemini CLI)."""
    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            continue
        req_id = req.get("id")
        method = req.get("method", "")
        params = req.get("params") or {}

        if method == "initialize":
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "scion-oase-mcp", "version": "1.0.0"},
                },
            }
        elif method == "notifications/initialized":
            continue
        elif method == "tools/list":
            resp = {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS_SCHEMA}}
        elif method == "tools/call":
            t_name = params.get("name", "")
            t_args = params.get("arguments") or {}
            try:
                out = execute_tool(t_name, t_args)
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(out, indent=2)}],
                        "isError": False,
                    },
                }
            except Exception as exc:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": f"Error: {exc}"}],
                        "isError": True,
                    },
                }
        else:
            if req_id is None:
                continue
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }
        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()
    return 0


def main() -> int:
    if "--cli" not in sys.argv:
        return run_mcp_stdio()

    parser = argparse.ArgumentParser(description="Scion OASE MCP Bridge CLI")
    parser.add_argument("--cli", required=True, help="Tool name (hub_status, list_projects, list_agents, dav_list, dav_read, get_messages, send_message)")
    parser.add_argument("--project", default="io-cold-to-hot", help="Project slug or UUID")
    parser.add_argument("--agent", default="science-program-lead", help="Agent slug")
    parser.add_argument("--path", default="", help="Relative workspace path for dav_list / dav_read")
    parser.add_argument("--message", default="", help="Message body for send_message")
    parser.add_argument("--limit", type=int, default=25, help="Max messages for get_messages")
    args = parser.parse_args()

    res = execute_tool(
        args.cli,
        {
            "project": args.project,
            "agent": args.agent,
            "path": args.path,
            "message": args.message,
            "limit": args.limit,
        },
    )
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

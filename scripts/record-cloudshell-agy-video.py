#!/usr/bin/env python3
"""Render the 1080p Google Cloud Shell + Antigravity (`agy`) <-> Scion Engine Walkthrough Video
(`cloudshell-agy-scion.mp4`) as Dr. Sarah Chen (`oase-sarah@losiern-1.altostrat.com`).

Demonstrates both core workflows requested for the workshop:
  1. Initiating / Bootstrapping a new OASE discovery campaign from Google Cloud Shell (`agy`)
     using the 41 OASE skills + `scion-oase-bridge` MCP server (`scion:bootstrap_campaign`,
     `scion:list_agents`, `scion:send_message`) and watching the 4-tier 17-agent graph light up in Scion.
  2. Analyzing a completed program run (`WO-001`..`WO-008`) from Google Cloud Shell (`agy`)
     (`scion:dav_read`, `scion:send_message`), auditing the `DEC-008` Wet-Lab Wall pivot from
     Series A (`oase_enpp1_009`) to Series B (`oase_enpp1_019`), and verifying the live message
     inside Scion Hub Project Messages.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
WORK_DIR = Path("/tmp/oase-cloudshell-agy-video")
OUT_MP4 = WORK_DIR / "cloudshell-agy-scion.mp4"

FPS = 30
AUDIO_SR = 48000
BREATH_GAP_S = 0.65


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


VOICES: dict[str, dict[str, Any]] = {
    "sarah": {
        "display_name": "Dr. Sarah Chen",
        "role": "Program Lead · Google Cloud Shell (agy)",
        "avatar_name": "Ingrid",
        "voice_id": "Leda",
        "callsign": "SARAH-LEAD",
        "accent_hex": "0x10b981",
        "pip_line3": "@science-program-lead | Gemini 4 Argon",
        "accent_label": "Partner: @science-program-lead · Gemini 4 Argon (High)",
        "model_label": "Gemini 4 Argon (High)",
        "is_agent": False,
    },
    "science-program-lead": {
        "display_name": "@science-program-lead",
        "role": "Discovery Program Lead · Scion Hub",
        "voice_id": "Charon",
        "callsign": "GROVE-1",
        "badge_code": "SPL",
        "model_label": "Gemini 4 Argon (High)",
        "accent_hex": "0x38bdf8",
        "wave_colors": "0x38bdf8|0x818cf8",
        "is_agent": True,
    },
    "admet-dmpk-scientist": {
        "display_name": "@admet-dmpk-scientist",
        "role": "ADMET & DMPK Specialist · Scion Hub",
        "voice_id": "Aoede",
        "callsign": "SHIELD-5",
        "badge_code": "DMPK",
        "model_label": "Gemini 4 Argon (Medium)",
        "accent_hex": "0xf59e0b",
        "wave_colors": "0xf59e0b|0x34d399",
        "is_agent": True,
    },
}

TURNS: list[dict[str, Any]] = [
    {
        "turn_id": "cs2_t1",
        "turn_num": 1,
        "speaker": "sarah",
        "scrub_key": "bootstrap",
        "scrub_label": "1. Cloud Shell (agy CLI): Initiate Campaign & Live CLI Feedback",
        "tts_text": (
            "From Google Cloud Shell as Doctor Sarah Chen, I run the Antigravity CLI with our forty-one "
            "Open Agentic Science Engine skills and Scion MCP bridge. I bootstrap the Cold-to-Hot Immuno-Oncology "
            "campaign in Scion. Then I dispatch the five-target tournament across E-N-P-P-one, ay-dar-one, "
            "P-T-P-N-two, K-D-M-one-A, and T-rex-one."
        ),
    },
    {
        "turn_id": "cs2_t2",
        "turn_num": 2,
        "speaker": "science-program-lead",
        "scrub_key": "graph",
        "scrub_label": "2. Scion Reacting: 4-Tier 17-Agent Graph Dispatches WO-001",
        "tts_text": (
            "Grove-One online! Seventy-eight of seventy-eight Science Agent doctor checks pass. "
            "Scion is reacting to your Cloud Shell directive—the four-tier seventeen-agent graph is active, "
            "HypEx Supervisor is running the five-target Elo tournament, and all twelve Tier-Three specialists are coordinated."
        ),
    },
    {
        "turn_id": "cs2_t3",
        "turn_num": 3,
        "speaker": "sarah",
        "scrub_key": "analyze",
        "scrub_label": "3. Cloud Shell (agy CLI): Program Run Audit & Series B Feedback",
        "tts_text": (
            "Back in the Antigravity CLI, I audit the completed Science Agent run by reading the decision log "
            "and candidate summary. I compare Series A polar sulfamide against Series B's neutral pyrazole "
            "heteroaryl zinc-binding group after the Decision Eight Wet-Lab Wall."
        ),
    },
    {
        "turn_id": "cs2_t4",
        "turn_num": 4,
        "speaker": "admet-dmpk-scientist",
        "scrub_key": "verify",
        "scrub_label": "4. Scion Reacting: Live Project Messages & Series B Pivot",
        "tts_text": (
            "Shield-Five confirming in Scion! Your Antigravity CLI feedback is logged in Scion Project Messages—Series A "
            "failed MDCK permeability and P-gp efflux gates at Decision Eight, and the Science Agent team pivoted to "
            "Series B lead E-N-P-P-one nineteen with fifty-two percent oral bioavailability."
        ),
    },
]


def _build_scene_html(turn_idx: int) -> str:
    """Build 1920x1080 HTML scene for each of the 4 turns.
    Right-column cards end above y=680 so the 296x360 PiP card at (1608, 700) never obscures any UI card.
    """
    progress_pct = int(((turn_idx + 1) / 4.0) * 100)
    turn = TURNS[turn_idx]
    vmeta = VOICES[turn["speaker"]]
    dot_hex = "#" + vmeta["accent_hex"].removeprefix("0x")

    hud_bar = f"""
    <div style="position:fixed;top:0;left:0;right:0;height:42px;background:rgba(2,6,23,0.96);border-bottom:1px solid #1e293b;display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:99999;font-family:'Inter',system-ui,sans-serif;">
      <div style="position:absolute;top:0;left:0;height:3px;width:{progress_pct}%;background:linear-gradient(90deg,#2563eb,#10b981);"></div>
      <div style="display:flex;align-items:center;gap:12px;">
        <span style="background:rgba(16,185,129,0.18);color:#34d399;border:1px solid rgba(16,185,129,0.45);padding:3px 10px;border-radius:999px;font-size:11px;font-weight:700;letter-spacing:0.04em;">☁ GOOGLE CLOUD SHELL + ANTIGRAVITY (AGY) ↔ SCION ENGINE</span>
        <span style="color:#f8fafc;font-weight:700;font-size:13.5px;">{turn['scrub_label']}</span>
      </div>
      <div style="display:flex;align-items:center;gap:10px;font-size:12px;color:#cbd5e1;">
        <span style="width:9px;height:9px;border-radius:50%;background:{dot_hex};box-shadow:0 0 8px {dot_hex};display:inline-block;"></span>
        <strong style="color:#fff;">{vmeta['display_name']}</strong>
        <span style="color:#94a3b8;">({vmeta['role']})</span>
      </div>
    </div>
    """

    gcp_topbar = """
    <div style="margin-top:42px;height:44px;background:#1a202c;border-bottom:1px solid #2d3748;display:flex;align-items:center;justify-content:space-between;padding:0 20px;color:#e2e8f0;font-family:'Inter',system-ui,sans-serif;font-size:12.5px;">
      <div style="display:flex;align-items:center;gap:14px;">
        <span style="font-weight:800;color:#60a5fa;font-size:14px;letter-spacing:0.01em;">Google Cloud</span>
        <span style="background:#2d3748;border:1px solid #4a5568;padding:3px 10px;border-radius:5px;font-family:monospace;font-size:12px;color:#f8fafc;">Project: <strong>losiern-oase-workshop</strong> (us-central1-c)</span>
        <span style="background:rgba(56,189,248,0.14);border:1px solid rgba(56,189,248,0.35);color:#7dd3fc;padding:3px 10px;border-radius:5px;font-family:monospace;font-size:11.5px;">Cloud Shell · Antigravity CLI (agy v1.4) + scion-oase-mcp</span>
      </div>
      <div style="display:flex;align-items:center;gap:10px;">
        <span style="background:rgba(16,185,129,0.16);border:1px solid rgba(16,185,129,0.4);color:#6ee7b7;padding:3px 10px;border-radius:999px;font-family:monospace;font-size:11.5px;">● oase-sarah@losiern-1.altostrat.com (Dr. Sarah Chen · Program Lead)</span>
      </div>
    </div>
    """

    if turn_idx == 0:
        body = f"""
        {hud_bar}
        {gcp_topbar}
        <div style="display:grid;grid-template-columns:1240px 632px;gap:16px;padding:16px;height:994px;box-sizing:border-box;background:#020617;font-family:'Inter',system-ui,sans-serif;">
          <!-- Left: Google Cloud Shell Terminal running one-shot agy CLI with live Scion Agent Feedback -->
          <div style="background:#090d16;border:1px solid #1e293b;border-radius:10px;display:flex;flex-direction:column;overflow:hidden;box-shadow:0 12px 32px rgba(0,0,0,0.45);">
            <div style="height:36px;background:#0f172a;border-bottom:1px solid #1e293b;display:flex;align-items:center;justify-content:space-between;padding:0 14px;font-size:12px;color:#94a3b8;font-family:monospace;">
              <div><span style="color:#10b981;font-weight:700;">●</span> Google Cloud Shell Terminal — <code>oase-sarah@cloudshell:~/oase-workshop (losiern-oase-workshop)</code></div>
              <div style="color:#38bdf8;">MCP: <code>scion-oase-mcp</code> (CONNECTED) · 41 Science Agent Skills</div>
            </div>
            <div style="padding:16px 20px;font-family:'JetBrains Mono',ui-monospace,monospace;font-size:12.6px;line-height:1.52;color:#e2e8f0;flex:1;">
              <div><span style="color:#34d399;">oase-sarah@cloudshell</span>:<span style="color:#60a5fa;">~/oase-workshop</span> <span style="color:#fbbf24;">(losiern-oase-workshop)</span>$ <span style="color:#fff;font-weight:700;">agy -p "Use scion-oase-bridge to bootstrap io-cold-to-hot from seed/io-cold-to-hot/campaign-seed.json, verify oase doctor (78/78 PASS), and dispatch WO-001 to @controller."</span></div>
              <div style="margin-top:8px;padding:8px 12px;background:rgba(37,99,235,0.12);border-left:3px solid #38bdf8;border-radius:4px;color:#bae6fd;font-size:12px;">
                <strong>Antigravity CLI (agy · Gemini 4 Argon) · Open Agentic Science Engine (Science Agent)</strong><br>
                ✓ Loaded <strong>41 domain verification skills</strong> + <strong>pharma_skills (Stages 1–4)</strong> + <strong>scion-oase-bridge</strong><br>
                ✓ Authenticated to Scion Hub (<code>scion-hub-oase</code>) as <code>oase-sarah@losiern-1.altostrat.com</code> (Dr. Sarah Chen)
              </div>
              <div style="margin-top:10px;padding:10px 14px;background:#0f172a;border:1px solid #1e293b;border-radius:6px;font-size:11.9px;">
                <div style="color:#38bdf8;font-weight:700;">⚡ Tool Call 1/3: <code>scion:bootstrap_campaign(project="io-cold-to-hot")</code></div>
                <div style="color:#a7f3d0;margin-top:2px;">  ✓ Seed: <code>seed/io-cold-to-hot/campaign-seed.json</code> (<code>ENV_VERSION = sha256:61020936449a</code>) · <code>oase doctor</code>: <strong>78/78 PASS</strong></div>
                <div style="color:#38bdf8;font-weight:700;margin-top:6px;">⚡ Tool Call 2/3: <code>scion:list_agents(project="io-cold-to-hot")</code></div>
                <div style="color:#a7f3d0;margin-top:2px;">  ✓ Verified <strong>17/17 running Science Agent nodes</strong> across 4 tiers (<code>17</code> active delegation edges · <code>0</code> stalled)</div>
                <div style="color:#38bdf8;font-weight:700;margin-top:6px;">⚡ Tool Call 3/3: <code>scion:send_message(project="io-cold-to-hot", agent="controller", type="instruction")</code></div>
                <div style="color:#a7f3d0;margin-top:2px;">  ✓ Dispatched directive <code>9e81c402</code> -&gt; <code>@controller</code> &amp; received live Scion callback in <code>agy</code> CLI</div>
              </div>
              <div style="margin-top:10px;padding:11px 14px;background:rgba(16,185,129,0.11);border:1px solid rgba(16,185,129,0.42);border-radius:6px;">
                <div style="color:#34d399;font-weight:700;margin-bottom:5px;">● Live Scion Feedback in agy CLI — @controller &amp; @hypex-supervisor (WO-001 5-Target Tournament)</div>
                <div style="font-size:12px;color:#e2e8f0;line-height:1.52;">
                  <code>[agent:controller -&gt; user:oase-sarah]</code> Shared Grove verified via <code>@bootstrapper</code> (<code>78/78 PASS</code>, <code>36/36</code> thresholds staged).<br>
                  <code>[agent:hypex-supervisor -&gt; agent:controller]</code> Completed <code>WO-001</code> 5-target Co-Scientist Elo tournament across <code>rank-1..3</code> &amp; <code>hypex-reflection</code>:<br>
                  &nbsp;&nbsp;1. <strong>ENPP1 (1658.4 Elo, Rank #1 WINNER)</strong> — extracellular cGAMP hydrolase · <code>gnomAD pLI = 0.00</code><br>
                  &nbsp;&nbsp;2. <strong>ADAR1 (1602.0 Elo, Rank #2)</strong> · 3. <strong>PTPN2 (1554.5 Elo, Rank #3)</strong> · 4. <strong>KDM1A/LSD1 (1442.0 Elo, Rank #4)</strong> · 5. <strong>TREX1 (1368.0 Elo, Rank #5 — L-001 lupus/AGS counter-screen)</strong><br>
                  <code>[agent:science-program-lead -&gt; user:oase-sarah]</code> 12 Tier-3 specialists coordinated for Stage Gate 1 (<code>DEC-002</code>) target lock.
                </div>
              </div>
            </div>
          </div>
          <!-- Right: Step 1 -> Step 2 Flow Callout (top 575px so bottom-right PiP at y=700 never overlaps) -->
          <div style="display:flex;flex-direction:column;gap:12px;max-height:575px;">
            <div style="background:#0f172a;border:1px solid #38bdf8;border-radius:10px;padding:15px;color:#f8fafc;">
              <div style="font-size:12px;font-weight:800;color:#38bdf8;text-transform:uppercase;letter-spacing:0.05em;">Step 1: One-Shot Antigravity (agy) CLI Dispatch</div>
              <div style="font-size:12.3px;color:#cbd5e1;margin-top:8px;line-height:1.52;">
                1. <strong>One-Shot CLI Command:</strong> Dr. Sarah Chen runs <code>agy -p "..."</code> as <code>oase-sarah@losiern-1.altostrat.com</code>.<br>
                2. <strong>Deterministic MCP Execution:</strong> <code>agy</code> invokes <code>scion:bootstrap_campaign</code>, <code>scion:list_agents</code>, and <code>scion:send_message</code>.<br>
                3. <strong>5-Target Tournament Feedback:</strong> <code>ENPP1 (1658.4)</code> &gt; <code>ADAR1 (1602.0)</code> &gt; <code>PTPN2 (1554.5)</code> &gt; <code>KDM1A/LSD1 (1442.0)</code> &gt; <code>TREX1 (1368.0)</code>.
              </div>
            </div>
            <div style="background:#0f172a;border:1px solid #334155;border-radius:10px;padding:15px;color:#f8fafc;">
              <div style="font-size:12px;font-weight:800;color:#34d399;text-transform:uppercase;letter-spacing:0.05em;">Live CLI Session Telemetry</div>
              <div style="margin-top:8px;font-family:'JetBrains Mono',monospace;font-size:11.6px;color:#e2e8f0;line-height:1.58;">
                • <strong>Identity:</strong> <code>oase-sarah@losiern-1.altostrat.com</code><br>
                • <strong>GCP Project:</strong> <code>losiern-oase-workshop</code><br>
                • <strong>Scion Hub VM:</strong> <code>scion-hub-oase (us-central1-c)</code><br>
                • <strong>Active Grove:</strong> <code>io-cold-to-hot (ab3d65d5...)</code><br>
                • <strong>Doctor Gate:</strong> <code>78/78 PASS (sha256:61020936449a)</code><br>
                • <strong>Next Scene:</strong> Watch Scion's 4-Tier 17-Agent Graph react &rarr;
              </div>
            </div>
          </div>
        </div>
        """
    elif turn_idx == 1:
        body = f"""
        {hud_bar}
        {gcp_topbar}
        <div style="display:grid;grid-template-columns:1240px 632px;gap:16px;padding:16px;height:994px;box-sizing:border-box;background:#020617;font-family:'Inter',system-ui,sans-serif;">
          <!-- Left 1240px: Full Unclipped 4-Tier 17-Agent Scion DAG with all 12 Tier-3 Specialist Nodes Visible -->
          <div style="background:#090d16;border:1px solid #1e293b;border-radius:10px;display:flex;flex-direction:column;overflow:hidden;box-shadow:0 12px 32px rgba(0,0,0,0.45);">
            <div style="height:38px;background:#0f172a;border-bottom:1px solid #1e293b;display:flex;align-items:center;justify-content:space-between;padding:0 16px;font-size:12px;font-family:monospace;">
              <div style="color:#f8fafc;font-weight:700;"><span style="color:#10b981;">●</span> Scion Hub — <code>io-cold-to-hot</code> (<code>/projects/ab3d65d5-13bd-4271-a8d7-fd3c8593d37c</code>) · 4-Tier 17-Agent Graph</div>
              <div style="display:flex;gap:10px;align-items:center;">
                <span style="background:rgba(16,185,129,0.18);color:#34d399;border:1px solid rgba(16,185,129,0.45);padding:2px 9px;border-radius:999px;font-size:11px;font-weight:700;">17 / 17 RUNNING · 0 STALLED</span>
                <span style="background:rgba(56,189,248,0.18);color:#7dd3fc;border:1px solid rgba(56,189,248,0.45);padding:2px 9px;border-radius:999px;font-size:11px;font-weight:700;">WO-001..WO-008 ACTIVE</span>
              </div>
            </div>
            <div style="padding:18px 20px;display:flex;flex-direction:column;gap:14px;flex:1;justify-content:space-between;background:radial-gradient(circle at 50% 20%, rgba(30,41,59,0.45), #090d16 75%);">
              <!-- Tier 0: Human Lead -->
              <div style="display:flex;flex-direction:column;align-items:center;gap:4px;">
                <div style="font-size:10.5px;font-weight:800;color:#34d399;letter-spacing:0.08em;text-transform:uppercase;">Tier 0 · Human Program Lead (Google Cloud Shell agy CLI)</div>
                <div style="background:rgba(16,185,129,0.14);border:1.5px solid #10b981;border-radius:8px;padding:7px 20px;color:#f8fafc;font-family:monospace;font-size:12px;box-shadow:0 4px 14px rgba(16,185,129,0.2);">
                  <strong style="color:#6ee7b7;">user:oase-sarah@losiern-1.altostrat.com</strong> · Dr. Sarah Chen (VP Discovery) — <code>directive 9e81c402 -&gt; @controller</code>
                </div>
                <div style="color:#38bdf8;font-size:13px;line-height:1;">▼</div>
              </div>
              <!-- Tier 1: Orchestrator (1 Agent) -->
              <div style="display:flex;flex-direction:column;align-items:center;gap:4px;">
                <div style="font-size:10.5px;font-weight:800;color:#38bdf8;letter-spacing:0.08em;text-transform:uppercase;">Tier 1 · Autonomous Campaign Orchestrator (Node 1 / 17)</div>
                <div style="background:rgba(56,189,248,0.14);border:1.5px solid #38bdf8;border-radius:8px;padding:7px 22px;color:#f8fafc;font-family:monospace;font-size:12px;">
                  <span style="color:#10b981;">●</span> <strong style="color:#7dd3fc;">@controller</strong> (Research Operations Controller · <code>Gemini 3.8 Flash</code>) — <code>RUNNING · Dispatches WO-001..WO-008</code>
                </div>
                <div style="color:#38bdf8;font-size:13px;line-height:1;">▼ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ▼ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ▼ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ▼</div>
              </div>
              <!-- Tier 2: 4 Stage Leads (Nodes 2..5 / 17) -->
              <div>
                <div style="text-align:center;font-size:10.5px;font-weight:800;color:#a78bfa;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:6px;">Tier 2 · Stage-Gate &amp; Tournament Supervisors (Nodes 2–5 / 17)</div>
                <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;">
                  <div style="background:#0f172a;border:1.5px solid #8b5cf6;border-radius:8px;padding:8px 10px;font-family:monospace;font-size:11.3px;color:#e2e8f0;">
                    <div style="color:#c4b5fd;font-weight:700;"><span style="color:#10b981;">●</span> @bootstrapper</div>
                    <div style="color:#94a3b8;font-size:10.5px;margin-top:2px;">Gemini 3.8 Flash · Seed &amp; Doctor</div>
                    <div style="color:#34d399;font-size:10.5px;margin-top:2px;">78/78 Checks PASS</div>
                  </div>
                  <div style="background:#0f172a;border:1.5px solid #8b5cf6;border-radius:8px;padding:8px 10px;font-family:monospace;font-size:11.3px;color:#e2e8f0;">
                    <div style="color:#c4b5fd;font-weight:700;"><span style="color:#10b981;">●</span> @head-of-discovery</div>
                    <div style="color:#94a3b8;font-size:10.5px;margin-top:2px;">Gemini 4 Argon (High) · Portfolio</div>
                    <div style="color:#34d399;font-size:10.5px;margin-top:2px;">Stage Gates 1–4 Active</div>
                  </div>
                  <div style="background:#0f172a;border:1.5px solid #8b5cf6;border-radius:8px;padding:8px 10px;font-family:monospace;font-size:11.3px;color:#e2e8f0;">
                    <div style="color:#c4b5fd;font-weight:700;"><span style="color:#10b981;">●</span> @hypex-supervisor</div>
                    <div style="color:#94a3b8;font-size:10.5px;margin-top:2px;">Gemini 4 Argon (High) · Co-Scientist</div>
                    <div style="color:#34d399;font-size:10.5px;margin-top:2px;">5-Target Elo Tournament</div>
                  </div>
                  <div style="background:#0f172a;border:1.5px solid #38bdf8;border-radius:8px;padding:8px 10px;font-family:monospace;font-size:11.3px;color:#e2e8f0;">
                    <div style="color:#7dd3fc;font-weight:700;"><span style="color:#10b981;">●</span> @science-program-lead</div>
                    <div style="color:#94a3b8;font-size:10.5px;margin-top:2px;">Gemini 4 Argon (High) · Lead</div>
                    <div style="color:#34d399;font-size:10.5px;margin-top:2px;">DEC-001..DEC-010 Chair</div>
                  </div>
                </div>
                <div style="text-align:center;color:#8b5cf6;font-size:13px;line-height:1;margin-top:5px;">▼ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ▼ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ▼ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ▼</div>
              </div>
              <!-- Tier 3A: 4 Co-Scientist Tournament Nodes (Nodes 6..9 / 17) -->
              <div>
                <div style="font-size:10.5px;font-weight:800;color:#fbbf24;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:6px;">Tier 3A · Co-Scientist Hypothesis &amp; Elo Tournament Pod (Nodes 6–9 / 17)</div>
                <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;">
                  <div style="background:#0f172a;border:1px solid #f59e0b;border-radius:7px;padding:7px 10px;font-family:monospace;font-size:11px;color:#e2e8f0;">
                    <div style="color:#fde68a;font-weight:700;"><span style="color:#10b981;">●</span> @rank-1 (Winner)</div>
                    <div style="color:#34d399;margin-top:2px;">ENPP1 · 1658.4 Elo (#1)</div>
                  </div>
                  <div style="background:#0f172a;border:1px solid #f59e0b;border-radius:7px;padding:7px 10px;font-family:monospace;font-size:11px;color:#e2e8f0;">
                    <div style="color:#fde68a;font-weight:700;"><span style="color:#10b981;">●</span> @rank-2</div>
                    <div style="color:#cbd5e1;margin-top:2px;">ADAR1 · 1602.0 Elo (#2)</div>
                  </div>
                  <div style="background:#0f172a;border:1px solid #f59e0b;border-radius:7px;padding:7px 10px;font-family:monospace;font-size:11px;color:#e2e8f0;">
                    <div style="color:#fde68a;font-weight:700;"><span style="color:#10b981;">●</span> @rank-3</div>
                    <div style="color:#cbd5e1;margin-top:2px;">PTPN2 · 1554.5 Elo (#3)</div>
                  </div>
                  <div style="background:#0f172a;border:1px solid #f59e0b;border-radius:7px;padding:7px 10px;font-family:monospace;font-size:11px;color:#e2e8f0;">
                    <div style="color:#fde68a;font-weight:700;"><span style="color:#10b981;">●</span> @hypex-reflection</div>
                    <div style="color:#cbd5e1;margin-top:2px;">KDM1A 1442 · TREX1 1368</div>
                  </div>
                </div>
              </div>
              <!-- Tier 3B: 8 Domain Specialist Nodes (Nodes 10..17 / 17) — Fully Unclipped Above Bottom Edge -->
              <div>
                <div style="font-size:10.5px;font-weight:800;color:#34d399;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:6px;">Tier 3B · 8 Domain Verification Specialists (Nodes 10–17 / 17 · All 12 Tier-3 Specialists Active)</div>
                <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;">
                  <div style="background:#0f172a;border:1px solid #10b981;border-radius:7px;padding:8px 10px;font-family:monospace;font-size:11px;color:#e2e8f0;">
                    <div style="color:#6ee7b7;font-weight:700;"><span style="color:#10b981;">●</span> @computational-biologist</div>
                    <div style="color:#94a3b8;font-size:10.3px;margin-top:2px;">Gemini 4 Argon (Med) + AlphaGenome</div>
                    <div style="color:#cbd5e1;font-size:10.3px;margin-top:2px;">pLI=0.00 · rs1044032=0.976</div>
                  </div>
                  <div style="background:#0f172a;border:1px solid #10b981;border-radius:7px;padding:8px 10px;font-family:monospace;font-size:11px;color:#e2e8f0;">
                    <div style="color:#6ee7b7;font-weight:700;"><span style="color:#10b981;">●</span> @structural-biologist</div>
                    <div style="color:#94a3b8;font-size:10.3px;margin-top:2px;">Gemini 4 Argon (High) + AlphaFold 3</div>
                    <div style="color:#cbd5e1;font-size:10.3px;margin-top:2px;">AF3 ipTM=0.36 · 6B2J Anchor</div>
                  </div>
                  <div style="background:#0f172a;border:1px solid #10b981;border-radius:7px;padding:8px 10px;font-family:monospace;font-size:11px;color:#e2e8f0;">
                    <div style="color:#6ee7b7;font-weight:700;"><span style="color:#10b981;">●</span> @computational-chemist</div>
                    <div style="color:#94a3b8;font-size:10.3px;margin-top:2px;">Gemini 4 Argon (Med) · fpocket/Vina</div>
                    <div style="color:#cbd5e1;font-size:10.3px;margin-top:2px;">Pocket #1=0.903 · -7.861 kcal</div>
                  </div>
                  <div style="background:#0f172a;border:1px solid #10b981;border-radius:7px;padding:8px 10px;font-family:monospace;font-size:11px;color:#e2e8f0;">
                    <div style="color:#6ee7b7;font-weight:700;"><span style="color:#10b981;">●</span> @medicinal-chemist</div>
                    <div style="color:#94a3b8;font-size:10.3px;margin-top:2px;">Claude Opus 5.5 · RDKit BRICS</div>
                    <div style="color:#cbd5e1;font-size:10.3px;margin-top:2px;">Series A 009 -&gt; Series B 019</div>
                  </div>
                  <div style="background:#0f172a;border:1px solid #10b981;border-radius:7px;padding:8px 10px;font-family:monospace;font-size:11px;color:#e2e8f0;">
                    <div style="color:#6ee7b7;font-weight:700;"><span style="color:#10b981;">●</span> @admet-dmpk-scientist</div>
                    <div style="color:#94a3b8;font-size:10.3px;margin-top:2px;">Gemini 4 Argon (Med) · PK/DMPK</div>
                    <div style="color:#cbd5e1;font-size:10.3px;margin-top:2px;">Papp=12.4e-6 · ER=1.6 · F=52%</div>
                  </div>
                  <div style="background:#0f172a;border:1px solid #10b981;border-radius:7px;padding:8px 10px;font-family:monospace;font-size:11px;color:#e2e8f0;">
                    <div style="color:#6ee7b7;font-weight:700;"><span style="color:#10b981;">●</span> @toxicology-scientist</div>
                    <div style="color:#94a3b8;font-size:10.3px;margin-top:2px;">Gemini 4 Argon (Med) · Safety</div>
                    <div style="color:#cbd5e1;font-size:10.3px;margin-top:2px;">TREX1 &gt;320x (L-001) · hERG &gt;48x</div>
                  </div>
                  <div style="background:#0f172a;border:1px solid #10b981;border-radius:7px;padding:8px 10px;font-family:monospace;font-size:11px;color:#e2e8f0;">
                    <div style="color:#6ee7b7;font-weight:700;"><span style="color:#10b981;">●</span> @scientific-reviewer</div>
                    <div style="color:#94a3b8;font-size:10.3px;margin-top:2px;">Claude Opus 5.5 · Peer Review</div>
                    <div style="color:#cbd5e1;font-size:10.3px;margin-top:2px;">Independent Cross-Family Gate</div>
                  </div>
                  <div style="background:#0f172a;border:1px solid #10b981;border-radius:7px;padding:8px 10px;font-family:monospace;font-size:11px;color:#e2e8f0;">
                    <div style="color:#6ee7b7;font-weight:700;"><span style="color:#10b981;">●</span> @finding-validator</div>
                    <div style="color:#94a3b8;font-size:10.3px;margin-top:2px;">Gemini 3.8 Flash · SHA-256</div>
                    <div style="color:#cbd5e1;font-size:10.3px;margin-top:2px;">10/10 Relays · 3/3 Drills</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <!-- Right 632px: SCION 4-TIER 17-AGENT GRAPH Status Card (top 575px so PiP at y=700 never overlaps) -->
          <div style="display:flex;flex-direction:column;gap:12px;max-height:575px;">
            <div style="background:#0f172a;border:1px solid #38bdf8;border-radius:10px;padding:15px;color:#f8fafc;">
              <div style="font-size:11.8px;font-weight:800;color:#34d399;letter-spacing:0.05em;text-transform:uppercase;">⚡ SCION 4-TIER 17-AGENT GRAPH (IO-COLD-TO-HOT)</div>
              <div style="font-size:12.2px;color:#e2e8f0;margin-top:8px;line-height:1.52;">
                • <strong>Tier 0 (Human Lead):</strong> <code>oase-sarah@losiern-1.altostrat.com</code> (Dr. Sarah Chen · Cloud Shell <code>agy</code>)<br>
                • <strong>Tier 1 (Orchestrator):</strong> <code>controller</code> receives <code>WO-001</code> from <code>agy</code> CLI<br>
                • <strong>Tier 2 (4 Stage Leads):</strong> <code>bootstrapper</code> · <code>head-of-discovery</code> · <code>hypex-supervisor</code> · <code>science-program-lead</code><br>
                • <strong>Tier 3 (12 Specialists):</strong> <code>rank-1..3</code> + <code>hypex-reflection</code> + 8 Domain Specialists
              </div>
            </div>
            <div style="background:#0f172a;border:1px solid #334155;border-radius:10px;padding:15px;color:#f8fafc;">
              <div style="font-size:11.8px;font-weight:800;color:#fbbf24;letter-spacing:0.05em;text-transform:uppercase;">WO-001 5-Target Co-Scientist Elo Tournament</div>
              <div style="margin-top:8px;font-family:'JetBrains Mono',monospace;font-size:11.5px;color:#e2e8f0;line-height:1.58;">
                1. <strong style="color:#34d399;">ENPP1: 1658.4 Elo (WINNER)</strong> · Extracellular cGAMP<br>
                2. <strong>ADAR1: 1602.0 Elo</strong> · RNA editing lethality<br>
                3. <strong>PTPN2: 1554.5 Elo</strong> · Phosphatase selectivity<br>
                4. <strong>KDM1A/LSD1: 1442.0 Elo</strong> · Epigenetic hematotox<br>
                5. <strong style="color:#fca5a5;">TREX1: 1368.0 Elo</strong> · L-001 lupus/AGS counter-screen<br>
                <span style="color:#7dd3fc;">ENPP1 1658.4 &gt; ADAR1 1602.0 &gt; PTPN2 1554.5 &gt; KDM1A 1442.0 &gt; TREX1 1368.0</span>
              </div>
            </div>
          </div>
        </div>
        """
    elif turn_idx == 2:
        body = f"""
        {hud_bar}
        {gcp_topbar}
        <div style="display:grid;grid-template-columns:1240px 632px;gap:16px;padding:16px;height:994px;box-sizing:border-box;background:#020617;font-family:'Inter',system-ui,sans-serif;">
          <!-- Left: Google Cloud Shell Terminal analyzing program run & receiving feedback in agy CLI -->
          <div style="background:#090d16;border:1px solid #1e293b;border-radius:10px;display:flex;flex-direction:column;overflow:hidden;box-shadow:0 12px 32px rgba(0,0,0,0.45);">
            <div style="height:36px;background:#0f172a;border-bottom:1px solid #1e293b;display:flex;align-items:center;justify-content:space-between;padding:0 14px;font-size:12px;color:#94a3b8;font-family:monospace;">
              <div><span style="color:#10b981;font-weight:700;">●</span> Google Cloud Shell Terminal — <code>oase-sarah@cloudshell:~/oase-workshop (losiern-oase-workshop)</code></div>
              <div style="color:#38bdf8;">Mode: Science Agent Run Analysis &amp; Wet-Lab Wall Feedback</div>
            </div>
            <div style="padding:16px 20px;font-family:'JetBrains Mono',ui-monospace,monospace;font-size:12.4px;line-height:1.48;color:#e2e8f0;flex:1;">
              <div><span style="color:#34d399;">oase-sarah@cloudshell</span>:<span style="color:#60a5fa;">~/oase-workshop</span> <span style="color:#fbbf24;">(losiern-oase-workshop)</span>$ <span style="color:#fff;font-weight:700;">agy -p "Use scion-oase-bridge to inspect io-cold-to-hot: read program-state/decision-log.md and executive/CANDIDATE-SUMMARY.md, compare Series A (oase_enpp1_009) vs Series B (oase_enpp1_019), and message @science-program-lead."</span></div>
              <div style="margin-top:9px;padding:9px 13px;background:#0f172a;border:1px solid #1e293b;border-radius:6px;font-size:11.7px;">
                <div style="color:#38bdf8;font-weight:700;">⚡ Tool Call 1/3: <code>scion:dav_read(project="io-cold-to-hot", path="program-state/decision-log.md")</code></div>
                <div style="color:#a7f3d0;">  ✓ Read 10 co-signed Stage Gate decisions (<code>DEC-001</code>..<code>DEC-010</code> · <code>sha256:61020936449a</code>)</div>
                <div style="color:#38bdf8;font-weight:700;margin-top:4px;">⚡ Tool Call 2/3: <code>scion:dav_read(project="io-cold-to-hot", path="executive/CANDIDATE-SUMMARY.md")</code></div>
                <div style="color:#a7f3d0;">  ✓ Extracted Series A (<code>oase_enpp1_009</code>) Wet-Lab Wall receipts &amp; Series B (<code>oase_enpp1_019</code>) recovery dossier</div>
                <div style="color:#38bdf8;font-weight:700;margin-top:4px;">⚡ Tool Call 3/3: <code>scion:send_message(project="io-cold-to-hot", agent="science-program-lead")</code></div>
                <div style="color:#a7f3d0;">  ✓ Sent feedback <code>f541212d</code> &amp; received grounded reply <code>ae096d6e</code> from <code>@science-program-lead</code> in <code>agy</code> CLI</div>
              </div>
              <!-- Live Agent Reply + Audit Table inside agy CLI -->
              <div style="margin-top:10px;padding:11px 14px;background:rgba(16,185,129,0.10);border:1px solid rgba(16,185,129,0.4);border-radius:6px;">
                <div style="color:#34d399;font-weight:700;font-size:12.1px;margin-bottom:6px;">● Live @science-program-lead Feedback in agy CLI — DEC-008 Wet-Lab Wall &amp; Series B Recovery</div>
                <table style="width:100%;border-collapse:collapse;font-size:11.4px;color:#e2e8f0;">
                  <thead>
                    <tr style="border-bottom:1px solid #334155;color:#93c5fd;text-align:left;">
                      <th style="padding:4px 8px;">Assay / Gate Metric</th>
                      <th style="padding:4px 8px;">Threshold</th>
                      <th style="padding:4px 8px;">Series A: oase_enpp1_009</th>
                      <th style="padding:4px 8px;">Series B: oase_enpp1_019</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr style="border-bottom:1px solid #1e293b;">
                      <td style="padding:4px 8px;">Zinc-Binding Scaffold</td>
                      <td style="padding:4px 8px;">tPSA &lt; 95 Å²</td>
                      <td style="padding:4px 8px;color:#fca5a5;">Polar Sulfamide ZBG (MW = 475.50 Da, TPSA = 113.96 Å²)</td>
                      <td style="padding:4px 8px;color:#6ee7b7;">Neutral Pyrazole Heteroaryl ZBG (MW = 430.51 Da, cLogP = 3.46, TPSA = 79.40 Å²)</td>
                    </tr>
                    <tr style="border-bottom:1px solid #1e293b;">
                      <td style="padding:4px 8px;">ENPP1 IC50 / SPR KD</td>
                      <td style="padding:4px 8px;">&lt; 100 nM</td>
                      <td style="padding:4px 8px;color:#6ee7b7;">18 nM / 14 nM (PASS)</td>
                      <td style="padding:4px 8px;color:#6ee7b7;">ENPP1 IC50 = 31 nM / SPR KD = 24 nM (PASS)</td>
                    </tr>
                    <tr style="border-bottom:1px solid #1e293b;">
                      <td style="padding:4px 8px;">MDCK-MDR1 Papp (A-&gt;B)</td>
                      <td style="padding:4px 8px;">&gt;= 5.0e-6 cm/s</td>
                      <td style="padding:4px 8px;color:#f87171;font-weight:700;">MDCK Papp = 1.1e-6 cm/s (FAIL — WALL)</td>
                      <td style="padding:4px 8px;color:#34d399;font-weight:700;">MDCK Papp = 12.4e-6 cm/s (PASS)</td>
                    </tr>
                    <tr style="border-bottom:1px solid #1e293b;">
                      <td style="padding:4px 8px;">P-gp Efflux Ratio (ER)</td>
                      <td style="padding:4px 8px;">&lt; 2.5</td>
                      <td style="padding:4px 8px;color:#f87171;font-weight:700;">P-gp ER = 18.4 (FAIL — WALL)</td>
                      <td style="padding:4px 8px;color:#34d399;font-weight:700;">P-gp ER = 1.6 (PASS)</td>
                    </tr>
                    <tr>
                      <td style="padding:4px 8px;">Oral F% / Selectivity</td>
                      <td style="padding:4px 8px;">F &gt;= 30%, &gt;30x</td>
                      <td style="padding:4px 8px;color:#94a3b8;">Halted at DEC-008</td>
                      <td style="padding:4px 8px;color:#34d399;font-weight:700;">F = 52% · hERG &gt; 48x · TREX1 &gt; 320x (L-001) · DEC-010</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          <!-- Right: Stage Gate Progression Summary (top 575px so PiP at y=700 never overlaps) -->
          <div style="background:#0f172a;border:1px solid #334155;border-radius:10px;padding:15px;color:#f8fafc;display:flex;flex-direction:column;gap:9px;max-height:575px;">
            <div style="font-size:11.8px;font-weight:800;color:#38bdf8;text-transform:uppercase;letter-spacing:0.05em;">Science Agent Stage-Gate Audit (WO-001 .. WO-008)</div>
            <div style="padding:8px 11px;background:#1e293b;border-left:3px solid #10b981;border-radius:4px;font-size:11.5px;line-height:1.42;">
              <strong>WO-001 (5-Target Elo Tournament):</strong><br>
              5-target Elo tournament (<code>ENPP1 1658.4</code> vs <code>ADAR1 1602.0</code>; <code>TREX1 L-001</code> lupus/AGS counter-screen).
            </div>
            <div style="padding:8px 11px;background:#1e293b;border-left:3px solid #10b981;border-radius:4px;font-size:11.5px;line-height:1.42;">
              <strong>WO-002..004 (Genetics, AlphaGenome &amp; AF3/Crystal):</strong><br>
              <code>gnomAD pLI = 0.00</code> · <code>TCGA r = -0.64</code> · <code>AlphaGenome rs1044032 = 0.976</code> · <code>AF3 ipTM = 0.36 (APO 6B2J anchor)</code> · <code>fpocket Pocket #1 = 0.903 (1143.6 Å³)</code> · <code>Vina = -7.861 kcal/mol</code>.
            </div>
            <div style="padding:8px 11px;background:rgba(245,158,11,0.14);border-left:3px solid #f59e0b;border-radius:4px;font-size:11.5px;line-height:1.42;">
              <strong>WO-006 / DEC-008 (The Wet-Lab Wall):</strong><br>
              Series A <code>oase_enpp1_009</code> (<code>MW = 475.50 Da, TPSA = 113.96 Å²</code>) blocked by <code>MDCK Papp = 1.1e-6</code> &amp; <code>P-gp ER = 18.4</code>.
            </div>
            <div style="padding:8px 11px;background:rgba(16,185,129,0.14);border-left:3px solid #10b981;border-radius:4px;font-size:11.5px;line-height:1.42;">
              <strong>WO-007..008 / DEC-010 (Series B Nomination):</strong><br>
              <code>oase_enpp1_019</code> neutral pyrazole heteroaryl ZBG (<code>TPSA = 79.40 Å²</code>, <code>12.4e-6 cm/s</code>, <code>ER = 1.6</code>, <code>F = 52%</code>, <code>TREX1 &gt; 320x</code>).
            </div>
          </div>
        </div>
        """
    else:
        body = f"""
        {hud_bar}
        {gcp_topbar}
        <div style="display:grid;grid-template-columns:1240px 632px;gap:16px;padding:16px;height:994px;box-sizing:border-box;background:#020617;font-family:'Inter',system-ui,sans-serif;">
          <!-- Left 1240px: Full-Width Unclipped Scion Hub Project Messages View (word-wrap: break-word, zero truncation) -->
          <div style="background:#090d16;border:1px solid #1e293b;border-radius:10px;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 12px 32px rgba(0,0,0,0.45);">
            <div style="height:38px;background:#0f172a;border-bottom:1px solid #1e293b;display:flex;align-items:center;justify-content:space-between;padding:0 16px;font-size:12px;font-weight:700;color:#93c5fd;font-family:monospace;">
              <span>⚡ Scion Hub Reacting — Project Messages &amp; Audit Trail (io-cold-to-hot · /projects/ab3d65d5-13bd-4271-a8d7-fd3c8593d37c)</span>
              <span style="color:#34d399;">● Cloud Logging scion-messages Synced (6/6 Relays)</span>
            </div>
            <div style="padding:14px 18px;display:flex;flex-direction:column;gap:10px;flex:1;font-family:'JetBrains Mono',monospace;font-size:11.6px;line-height:1.48;word-wrap:break-word;overflow-wrap:break-word;">
              <!-- Message 1: Sarah CLI Directive -->
              <div style="background:#0f172a;border:1px solid #334155;border-left:4px solid #10b981;border-radius:6px;padding:10px 14px;">
                <div style="display:flex;justify-content:space-between;color:#94a3b8;font-size:11px;margin-bottom:4px;">
                  <span><strong style="color:#6ee7b7;">user:oase-sarah@losiern-1.altostrat.com</strong> &rarr; <strong style="color:#7dd3fc;">agent:science-program-lead</strong></span>
                  <span>msg_id: <code>f541212d</code> · type: <code>instruction</code> · source: <code>agy-cli-mcp</code></span>
                </div>
                <div style="color:#f8fafc;">
                  **[CLOUD SHELL (AGY CLI) AUDIT DIRECTIVE]** — Inspect <code>program-state/decision-log.md</code> and <code>executive/CANDIDATE-SUMMARY.md</code>: verify the <code>DEC-008</code> Wet-Lab Wall halt of Series A (<code>oase_enpp1_009</code>) and confirm Series B (<code>oase_enpp1_019</code>) gate closure at <code>DEC-010</code>.
                </div>
              </div>
              <!-- Message 2: ADMET DMPK Scientist Wet-Lab Wall -->
              <div style="background:#0f172a;border:1px solid #334155;border-left:4px solid #f59e0b;border-radius:6px;padding:10px 14px;">
                <div style="display:flex;justify-content:space-between;color:#94a3b8;font-size:11px;margin-bottom:4px;">
                  <span><strong style="color:#fbbf24;">agent:admet-dmpk-scientist</strong> &rarr; <strong style="color:#7dd3fc;">agent:science-program-lead</strong></span>
                  <span>msg_id: <code>81b40e19</code> · type: <code>state-change</code> · model: <code>Gemini 4 Argon (Medium)</code></span>
                </div>
                <div style="color:#f8fafc;">
                  **[WET-LAB WALL TRIGGERED ('DEC-008' · HALT SERIES A)]** — Experimental CRO wet-lab panel falsified Series A lead <code>oase_enpp1_009</code> (polar sulfamide ZBG, <code>MW = 475.50 Da</code>, <code>TPSA = 113.96 Å²</code>): <code>ENPP1 IC50 = 18 nM</code> / <code>SPR KD = 14 nM</code> passed, but <code>MDCK-MDR1 Papp = 1.1e-6 cm/s</code> (&lt; <code>5.0e-6</code> gate) and <code>P-gp ER = 18.4</code> (&gt; <code>2.5</code> gate) blocked oral progression.
                </div>
              </div>
              <!-- Message 3: Medicinal Chemist Series Pivot -->
              <div style="background:#0f172a;border:1px solid #334155;border-left:4px solid #38bdf8;border-radius:6px;padding:10px 14px;">
                <div style="display:flex;justify-content:space-between;color:#94a3b8;font-size:11px;margin-bottom:4px;">
                  <span><strong style="color:#7dd3fc;">agent:medicinal-chemist</strong> &rarr; <strong style="color:#7dd3fc;">agent:science-program-lead</strong></span>
                  <span>msg_id: <code>c492a710</code> · type: <code>instruction-reply</code> · model: <code>Claude Opus 5.5</code></span>
                </div>
                <div style="color:#f8fafc;">
                  **[SERIES PIVOT EXECUTED ('DEC-008 -&gt; DEC-009')]** — Replaced polar sulfamide (<code>oase_enpp1_009</code>, <code>TPSA = 113.96 Å²</code>) with neutral pyrazole heteroaryl ZBG (<code>oase_enpp1_019</code>, <code>MW = 430.51 Da</code>, <code>cLogP = 3.46</code>, <code>TPSA = 79.40 Å²</code>, <code>ENPP1 IC50 = 31 nM</code>, <code>MDCK Papp = 12.4e-6 cm/s</code>, <code>ER = 1.6</code>, <code>hERG IC50 &gt; 30 µM</code>).
                </div>
              </div>
              <!-- Message 4: Scientific Reviewer Cross-Model Peer Review -->
              <div style="background:#0f172a;border:1px solid #334155;border-left:4px solid #a78bfa;border-radius:6px;padding:10px 14px;">
                <div style="display:flex;justify-content:space-between;color:#94a3b8;font-size:11px;margin-bottom:4px;">
                  <span><strong style="color:#c4b5fd;">agent:scientific-reviewer</strong> &rarr; <strong style="color:#7dd3fc;">agent:science-program-lead</strong></span>
                  <span>msg_id: <code>d903e512</code> · type: <code>peer-review</code> · model: <code>Claude Opus 5.5</code></span>
                </div>
                <div style="color:#f8fafc;">
                  Independent cross-model peer review ('Claude Opus 5.5') verified DEC-008 Wet-Lab Wall falsification and DEC-010 Series B gate closure (6/6 relays propagated).
                </div>
              </div>
              <!-- Message 5: Science Program Lead Grounded Reply to Sarah -->
              <div style="background:rgba(16,185,129,0.10);border:1px solid rgba(16,185,129,0.45);border-left:4px solid #10b981;border-radius:6px;padding:10px 14px;">
                <div style="display:flex;justify-content:space-between;color:#94a3b8;font-size:11px;margin-bottom:4px;">
                  <span><strong style="color:#7dd3fc;">agent:science-program-lead</strong> &rarr; <strong style="color:#6ee7b7;">user:oase-sarah@losiern-1.altostrat.com</strong></span>
                  <span>msg_id: <code>ae096d6e</code> · type: <code>gate-signoff</code> · model: <code>Gemini 4 Argon (High)</code></span>
                </div>
                <div style="color:#f8fafc;">
                  **[DEC-010 PRECLINICAL CANDIDATE NOMINATED]** — <code>oase_enpp1_019</code> locked (<code>Oral F = 52%</code>, <code>Ctrough,free = 6.4x IC50</code>, <code>TREX1 IC50 &gt; 10 µM [&gt;320x L-001 PASS]</code>, <code>hERG &gt; 48x</code>, <code>10/10 oase validate PASS</code>).
                </div>
              </div>
            </div>
          </div>
          <!-- Right 632px: Live Message Exchange Receipt (top 575px so PiP at y=700 never overlaps) -->
          <div style="background:#090d16;border:1px solid #1e293b;border-radius:10px;padding:16px;color:#e2e8f0;font-family:'JetBrains Mono',monospace;font-size:11.8px;line-height:1.5;display:flex;flex-direction:column;gap:10px;max-height:575px;">
            <div style="font-family:'Inter',sans-serif;font-size:12.5px;font-weight:800;color:#34d399;text-transform:uppercase;letter-spacing:0.04em;">
              ✓ Scion Hub Reacting to Antigravity (agy) CLI Feedback
            </div>
            <div style="padding:11px;background:#0f172a;border-left:3px solid #38bdf8;border-radius:6px;">
              <div style="color:#93c5fd;font-weight:700;">[1. SENT FROM CLOUD SHELL (AGY CLI)]</div>
              <div style="color:#cbd5e1;margin-top:4px;">
                <strong>Sender:</strong> <code>user:oase-sarah@losiern-1.altostrat.com</code><br>
                <strong>Recipient:</strong> <code>agent:science-program-lead</code><br>
                <strong>Paths Read:</strong> <code>program-state/decision-log.md</code> &amp; <code>executive/CANDIDATE-SUMMARY.md</code>
              </div>
            </div>
            <div style="padding:11px;background:rgba(16,185,129,0.10);border-left:3px solid #10b981;border-radius:6px;">
              <div style="color:#6ee7b7;font-weight:700;">[2. SCION REACTION &amp; SERIES B PIVOT CONFIRMED]</div>
              <div style="color:#e2e8f0;margin-top:4px;">
                1. Series A <code>oase_enpp1_009</code> (<code>MW = 475.50 Da, TPSA = 113.96 Å²</code>) halted at <code>DEC-008</code> (<code>Papp = 1.1e-6</code>, <code>ER = 18.4</code>).<br>
                2. Series B <code>oase_enpp1_019</code> neutral pyrazole heteroaryl ZBG (<code>MW = 430.51 Da, cLogP = 3.46, TPSA = 79.40 Å²</code>) nominated at <code>DEC-010</code> (<code>Papp = 12.4e-6</code>, <code>ER = 1.6</code>, <code>F = 52%</code>, <code>Claude Opus 5.5</code> peer review PASS).
              </div>
            </div>
          </div>
        </div>
        """

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ width: 1920px; height: 1080px; overflow: hidden; background: #020617; }}
</style>
</head>
<body>
{body}
</body>
</html>"""


def main() -> int:
    os.environ["CLOUDSDK_CORE_ACCOUNT"] = "claude-vertex@losiern-vibe.iam.gserviceaccount.com"
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    audio_dir = WORK_DIR / "audio"
    live_dir = WORK_DIR / "talking-heads" / "live_turns"
    seg_dir = WORK_DIR / "segments"
    audio_dir.mkdir(parents=True, exist_ok=True)
    live_dir.mkdir(parents=True, exist_ok=True)
    seg_dir.mkdir(parents=True, exist_ok=True)

    rla = _load_module("render_live_avatars", REPO_ROOT / "scripts" / "render-live-avatars.py")
    rtp = _load_module("record_team_pilot", REPO_ROOT / "scripts" / "record-team-pilot.py")

    gcp_project = "losiern-oase-workshop"
    # 1. Synthesize or reuse cached 4 turns (2 Sarah Gemini 3.8 Live Avatar turns + 2 AI wingman turns)
    turn_meta: dict[str, dict[str, Any]] = {}
    for t in TURNS:
        tid = t["turn_id"]
        sp = t["speaker"]
        vmeta = VOICES[sp]
        cached_wav = audio_dir / f"{tid}.wav"
        cached_mp4 = live_dir / f"{tid}_live30.mp4"
        if cached_wav.exists() and cached_wav.stat().st_size > 10000 and (vmeta["is_agent"] or cached_mp4.exists()):
            dur = float(rtp.ffprobe_duration(cached_wav))
            turn_meta[tid] = {
                "turn_id": tid,
                "wav": str(cached_wav),
                "duration_s": round(dur, 4),
                "slot_frames": int(round((dur + BREATH_GAP_S) * FPS)),
            }
            continue
        tok = rla.gcloud_access_token(None)
        if vmeta["is_agent"]:
            job = {
                "turn_id": tid,
                "chapter": "cs",
                "speaker": sp,
                "voice_id": vmeta["voice_id"],
                "tts_text": rla.normalize_biopharma_tts_text(t["tts_text"]),
            }
            turn_meta[tid] = rla.render_single_agent_turn(job, audio_dir, WORK_DIR / "work", gcp_project, tok)
        else:
            job = {
                "turn_id": tid,
                "chapter": "cs",
                "speaker": sp,
                "avatar_name": vmeta["avatar_name"],
                "voice_id": vmeta["voice_id"],
                "tts_text": rla.normalize_biopharma_tts_text(t["tts_text"]),
            }
            turn_meta[tid] = rla.render_single_human_turn(
                job, live_dir, audio_dir, WORK_DIR / "work", gcp_project, "us-central1", None
            )

    # 2. Render the 4 1920x1080 scene PNGs via headless Chrome
    scene_pngs: list[Path] = []
    for idx in range(4):
        html_path = WORK_DIR / f"scene_{idx + 1}.html"
        png_path = WORK_DIR / f"scene_{idx + 1}.png"
        html_path.write_text(_build_scene_html(idx), encoding="utf-8")
        subprocess.run(
            [
                "/usr/bin/google-chrome",
                "--headless",
                "--no-sandbox",
                "--disable-gpu",
                "--hide-scrollbars",
                "--window-size=1920,1080",
                f"--screenshot={png_path.resolve()}",
                f"file://{html_path.resolve()}",
            ],
            check=True,
            capture_output=True,
        )
        scene_pngs.append(png_path)

    # 3. Build per-turn 48kHz stereo WAVs + PiP overlays + 1080p video segments
    vseg_files: list[Path] = []
    aseg_files: list[Path] = []
    scrub_markers: list[dict[str, Any]] = []
    cursor_frames = 0

    for idx, t in enumerate(TURNS):
        tid = t["turn_id"]
        sp = t["speaker"]
        vmeta = VOICES[sp]
        tinfo = turn_meta[tid]
        slot_frames = int(tinfo["slot_frames"])
        slot_dur_s = slot_frames / float(FPS)
        src_wav = Path(tinfo["wav"])

        wav_48k = seg_dir / f"{tid}_48k.wav"
        rtp.build_exact_48k_stereo_wav(src_wav, slot_frames, wav_48k, is_agent=bool(vmeta["is_agent"]))
        aseg_files.append(wav_48k)

        pip_mp4 = seg_dir / f"{tid}_pip.mp4"
        rtp.build_pip_overlay_clip(
            tid=tid,
            speaker=sp,
            vmeta=vmeta,
            wav_48k_path=wav_48k,
            slot_frames=slot_frames,
            talking_heads_dir=WORK_DIR / "talking-heads",
            out_pip_mp4=pip_mp4,
        )

        vseg_mp4 = seg_dir / f"{tid}_vseg.mp4"
        fc = f"[0:v]fps={FPS},scale=1920:1080[base];[base][1:v]overlay=1608:700[vout]"
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-loop",
                "1",
                "-i",
                str(scene_pngs[idx]),
                "-i",
                str(pip_mp4),
                "-filter_complex",
                fc,
                "-map",
                "[vout]",
                "-frames:v",
                str(slot_frames),
                "-r",
                str(FPS),
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-crf",
                "19",
                "-pix_fmt",
                "yuv420p",
                "-an",
                str(vseg_mp4),
            ],
            check=True,
            capture_output=True,
        )
        vseg_files.append(vseg_mp4)

        cursor_s = cursor_frames / float(FPS)
        total_sec = int(round(cursor_s))
        mm = total_sec // 60
        ss = total_sec % 60
        scrub_markers.append(
            {
                "key": t["scrub_key"],
                "label": t["scrub_label"],
                "time_s": round(cursor_s, 2),
                "timecode": f"{mm}:{ss:02d}",
                "speaker": vmeta["display_name"],
                "role": vmeta["role"],
                "voice_id": vmeta["voice_id"],
            }
        )
        cursor_frames += slot_frames
        print(f"[SEG] {tid}: {slot_frames} frames ({slot_dur_s:.2f}s) rendered", flush=True)

    vconcat_txt = seg_dir / "vconcat.txt"
    vconcat_txt.write_text("\n".join(f"file '{p.resolve()}'" for p in vseg_files) + "\n", encoding="utf-8")
    master_wav = seg_dir / "master_48k.wav"
    rtp.concatenate_wavs_sample_exact(aseg_files, master_wav)

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(vconcat_txt),
            "-i",
            str(master_wav),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "20",
            "-r",
            str(FPS),
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            str(AUDIO_SR),
            "-ac",
            "2",
            "-movflags",
            "+faststart",
            "-shortest",
            str(OUT_MP4),
        ],
        check=True,
        capture_output=True,
    )
    dur_s = round(rtp.ffprobe_duration(OUT_MP4), 2)
    meta_out = {
        "video_filename": "cloudshell-agy-scion.mp4",
        "title": "Google Cloud Shell + Antigravity (AGY) ↔ Scion Engine Live Walkthrough (Dr. Sarah Chen)",
        "duration_s": dur_s,
        "resolution": "1920x1080",
        "markers": scrub_markers,
    }
    (WORK_DIR / "cloudshell-agy-meta.json").write_text(json.dumps(meta_out, indent=2), encoding="utf-8")
    print(f"[SUCCESS] Mastered {OUT_MP4} ({dur_s}s, {OUT_MP4.stat().st_size / (1024 * 1024):.2f} MB)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

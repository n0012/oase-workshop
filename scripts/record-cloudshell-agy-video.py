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

import base64
import importlib.util
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
BRAIN_DIR = Path("/usr/local/google/home/losiern/.gemini/jetski/brain/1895894a-be26-469d-b98d-f3cd550d7ac5")
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
        "turn_id": "cs_t1",
        "turn_num": 1,
        "speaker": "sarah",
        "scrub_key": "bootstrap",
        "scrub_label": "1. Cloud Shell (agy): Initiate New Campaign",
        "tts_text": (
            "From Google Cloud Shell as Doctor Sarah Chen, I launch Antigravity with our forty-one OASE skills "
            "and Scion MCP bridge to initialize the Cold-to-Hot Immuno-Oncology campaign and dispatch Work Order One."
        ),
    },
    {
        "turn_id": "cs_t2",
        "turn_num": 2,
        "speaker": "science-program-lead",
        "scrub_key": "graph",
        "scrub_label": "2. Scion Hub: 4-Tier 17-Agent Graph Live",
        "tts_text": (
            "Grove-One online! Seventy-eight of seventy-eight OASE doctor checks pass. "
            "The four-tier Scion agent graph is active—HypEx Supervisor is running the three-target Elo tournament "
            "while I coordinate all eight domain specialists."
        ),
    },
    {
        "turn_id": "cs_t3",
        "turn_num": 3,
        "speaker": "sarah",
        "scrub_key": "analyze",
        "scrub_label": "3. Cloud Shell (agy): Analyze Run & Wet-Lab Wall",
        "tts_text": (
            "We can also use Antigravity in Cloud Shell to analyze a completed program run—reading the decision log "
            "and messaging Science Program Lead to audit why Series A hit the Decision Eight Wet-Lab Wall."
        ),
    },
    {
        "turn_id": "cs_t4",
        "turn_num": 4,
        "speaker": "admet-dmpk-scientist",
        "scrub_key": "verify",
        "scrub_label": "4. Scion Project Messages: Series B Pivot Verified",
        "tts_text": (
            "Shield-Five confirming in Scion! Series A failed MDCK permeability and P-gp efflux gates at Decision Eight, "
            "triggering the Series B pivot to OASE-ENPP1-019 with fifty-two percent oral bioavailability."
        ),
    },
]


def _img_data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def _build_scene_html(turn_idx: int, graph_uri: str, msgs_uri: str) -> str:
    """Build 1920x1080 HTML scene for each of the 4 turns."""
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
        <div style="display:grid;grid-template-columns:1160px 712px;gap:16px;padding:16px;height:962px;box-sizing:border-box;background:#020617;font-family:'Inter',system-ui,sans-serif;">
          <!-- Left: Google Cloud Shell Terminal running agy -->
          <div style="background:#090d16;border:1px solid #1e293b;border-radius:10px;display:flex;flex-direction:column;overflow:hidden;box-shadow:0 12px 32px rgba(0,0,0,0.45);">
            <div style="height:36px;background:#0f172a;border-bottom:1px solid #1e293b;display:flex;align-items:center;justify-content:space-between;padding:0 14px;font-size:12px;color:#94a3b8;font-family:monospace;">
              <div><span style="color:#10b981;font-weight:700;">●</span> Cloud Shell Terminal — <code>oase-sarah@cloudshell:~/oase-workshop (losiern-oase-workshop)</code></div>
              <div style="color:#38bdf8;">MCP: <code>scion-oase-mcp</code> (CONNECTED) · 41 OASE Skills Loaded</div>
            </div>
            <div style="padding:18px 20px;font-family:'JetBrains Mono',ui-monospace,monospace;font-size:13.2px;line-height:1.58;color:#e2e8f0;flex:1;">
              <div><span style="color:#34d399;">oase-sarah@cloudshell</span>:<span style="color:#60a5fa;">~/oase-workshop</span> <span style="color:#fbbf24;">(losiern-oase-workshop)</span>$ <span style="color:#fff;font-weight:700;">agy --model gemini-4-argon</span></div>
              <div style="margin-top:8px;padding:10px 14px;background:rgba(37,99,235,0.12);border-left:3px solid #38bdf8;border-radius:4px;color:#bae6fd;font-size:12.4px;">
                <strong>Antigravity (agy) · Vertex AI (losiern-oase-workshop)</strong><br>
                ✓ Loaded <strong>41 OASE domain verification skills</strong> + <strong>pharma_skills (Stages 1–4)</strong> + <strong>scion-oase-bridge</strong><br>
                ✓ Connected to Scion Hub MCP (<code>scion-hub-oase</code> · authenticated as <code>oase-sarah@losiern-1.altostrat.com</code>)
              </div>
              <div style="margin-top:14px;color:#f8fafc;">
                <span style="color:#10b981;font-weight:700;">sarah &gt;</span> Initialize a new Cold-to-Hot Immuno-Oncology campaign (<code>io-cold-to-hot</code>) on Scion Hub from <code>seed/io-cold-to-hot/campaign-seed.json</code>, verify <code>oase doctor</code> (78/78 checks), and dispatch <code>WO-001</code> (3-target Co-Scientist Elo tournament: <code>ENPP1</code> vs <code>Trex1</code> vs <code>ADAR1</code>) to <code>@controller</code>.
              </div>
              <div style="margin-top:12px;padding:10px 14px;background:#0f172a;border:1px solid #1e293b;border-radius:6px;font-size:12.3px;">
                <div style="color:#38bdf8;font-weight:700;">⚡ Tool Call 1/3: <code>scion:bootstrap_campaign(project="io-cold-to-hot")</code></div>
                <div style="color:#a7f3d0;margin-top:4px;">  ✓ Seed: <code>seed/io-cold-to-hot/campaign-seed.json</code> (<code>ENV_VERSION = sha256:61020936449a</code>)</div>
                <div style="color:#a7f3d0;">  ✓ <code>oase doctor</code>: <strong>78/78 PASS</strong> · Binaries: <code>AutoDock Vina 1.2.5</code>, <code>fpocket 4.2.2</code>, <code>RDKit</code>, <code>AlphaFold 3</code>, <code>AlphaGenome</code></div>
                <div style="color:#a7f3d0;">  ✓ Governance Thresholds: <strong>36/36 rules staged</strong> in <code>.oase/thresholds.yaml</code></div>
                <div style="color:#38bdf8;font-weight:700;margin-top:8px;">⚡ Tool Call 2/3: <code>scion:list_agents(project="io-cold-to-hot")</code></div>
                <div style="color:#a7f3d0;margin-top:4px;">  ✓ Verified <strong>17/17 running agents</strong> across 4 tiers (<code>17</code> active delegation edges · <code>0</code> stopped/stalled)</div>
                <div style="color:#38bdf8;font-weight:700;margin-top:8px;">⚡ Tool Call 3/3: <code>scion:send_message(project="io-cold-to-hot", agent="controller", type="instruction")</code></div>
                <div style="color:#a7f3d0;margin-top:4px;">  ✓ Dispatched <code>WO-001</code> (<code>RUN-001</code> Pairwise Elo Tournament) -&gt; <code>@controller</code> -&gt; <code>@hypex-supervisor</code></div>
              </div>
              <div style="margin-top:12px;padding:12px 14px;background:rgba(16,185,129,0.10);border:1px solid rgba(16,185,129,0.35);border-radius:6px;">
                <div style="color:#34d399;font-weight:700;margin-bottom:4px;">● Antigravity Response — Campaign Initialized &amp; Running in Scion</div>
                <div style="font-size:12.3px;color:#e2e8f0;">
                  <code>io-cold-to-hot</code> (<code>ab3d65d5-f32c-463e-be48-d535034de34f</code>) is live on Scion Hub. <code>@controller</code> has verified the shared Grove via <code>@bootstrapper</code> and delegated <code>WO-001</code> across <code>@hypex-supervisor</code> (<code>rank-1..3</code>, <code>hypex-reflection</code>) and <code>@science-program-lead</code>.
                </div>
              </div>
            </div>
          </div>
          <!-- Right: Live Scion Hub Preview + Skill Stack -->
          <div style="display:flex;flex-direction:column;gap:14px;">
            <div style="background:#0f172a;border:1px solid #334155;border-radius:10px;padding:14px 16px;color:#f8fafc;">
              <div style="font-size:12px;font-weight:700;color:#38bdf8;text-transform:uppercase;letter-spacing:0.05em;">Why Antigravity (AGY) in Cloud Shell + Scion Hub</div>
              <div style="font-size:12.5px;color:#cbd5e1;margin-top:6px;line-height:1.5;">
                • <strong>100% Argolis / Customer-Native:</strong> Runs as <code>oase-sarah@losiern-1.altostrat.com</code> inside <code>losiern-oase-workshop</code> with zero corporate proxy dependencies.<br>
                • <strong>41 OASE Skills + Pharma Stage Skills:</strong> Every prompt in <code>agy</code> invokes deterministic Scion MCP tools (<code>bootstrap_campaign</code>, <code>list_agents</code>, <code>dav_read</code>, <code>send_message</code>).<br>
                • <strong>Live Bidirectional Sync:</strong> Instructions sent from Cloud Shell immediately log into Scion's SQLite DB &amp; Cloud Logging.
              </div>
            </div>
            <div style="background:#0f172a;border:1px solid #334155;border-radius:10px;overflow:hidden;flex:1;display:flex;flex-direction:column;">
              <div style="padding:8px 14px;background:#1e293b;font-size:11.5px;font-weight:700;color:#93c5fd;font-family:monospace;">
                Live Scion Hub 4-Tier Agent Graph · /projects/ab3d65d5.../agents?view=graph
              </div>
              <div style="flex:1;background:#f8fafc;display:flex;align-items:center;justify-content:center;overflow:hidden;">
                <img src="{graph_uri}" style="width:100%;height:100%;object-fit:cover;object-position:top center;">
              </div>
            </div>
          </div>
        </div>
        """
    elif turn_idx == 1:
        body = f"""
        {hud_bar}
        <div style="margin-top:42px;height:1038px;background:#0f172a;position:relative;overflow:hidden;font-family:'Inter',system-ui,sans-serif;">
          <img src="{graph_uri}" style="width:1920px;height:1038px;object-fit:contain;background:#f8fafc;">
          <div style="position:absolute;top:18px;left:24px;width:540px;background:rgba(15,23,42,0.94);border:1px solid #38bdf8;border-radius:10px;padding:14px 18px;color:#f8fafc;box-shadow:0 12px 28px rgba(0,0,0,0.45);">
            <div style="font-size:11.5px;font-weight:800;color:#38bdf8;letter-spacing:0.05em;text-transform:uppercase;">Live Scion 4-Tier 17-Agent Discovery Hierarchy (io-cold-to-hot)</div>
            <div style="font-size:12.5px;color:#e2e8f0;margin-top:6px;line-height:1.5;">
              • <strong>Tier 0 (Human Lead):</strong> <code>oase-sarah@losiern-1.altostrat.com</code> (Dr. Sarah Chen)<br>
              • <strong>Tier 1 (Orchestrator):</strong> <code>controller</code> (Research Operations Controller)<br>
              • <strong>Tier 2 (Stage Leads):</strong> <code>bootstrapper</code> · <code>head-of-discovery</code> · <code>hypex-supervisor</code> · <code>science-program-lead</code><br>
              • <strong>Tier 3 (12 Specialists):</strong> <code>rank-1..3</code> + <code>hypex-reflection</code> (Elo Tournament: <code>ENPP1 1658.0</code> &gt; <code>Trex1 1604.0</code> &gt; <code>ADAR1 1561.0</code>) + 8 Domain Specialists (<code>WO-002..WO-008</code>)
            </div>
          </div>
        </div>
        """
    elif turn_idx == 2:
        body = f"""
        {hud_bar}
        {gcp_topbar}
        <div style="display:grid;grid-template-columns:1220px 652px;gap:16px;padding:16px;height:962px;box-sizing:border-box;background:#020617;font-family:'Inter',system-ui,sans-serif;">
          <!-- Left: Google Cloud Shell Terminal analyzing program run -->
          <div style="background:#090d16;border:1px solid #1e293b;border-radius:10px;display:flex;flex-direction:column;overflow:hidden;box-shadow:0 12px 32px rgba(0,0,0,0.45);">
            <div style="height:36px;background:#0f172a;border-bottom:1px solid #1e293b;display:flex;align-items:center;justify-content:space-between;padding:0 14px;font-size:12px;color:#94a3b8;font-family:monospace;">
              <div><span style="color:#10b981;font-weight:700;">●</span> Cloud Shell Terminal — <code>oase-sarah@cloudshell:~/oase-workshop (losiern-oase-workshop)</code></div>
              <div style="color:#38bdf8;">Mode: Program Run Analysis &amp; Wet-Lab Wall Audit</div>
            </div>
            <div style="padding:18px 20px;font-family:'JetBrains Mono',ui-monospace,monospace;font-size:13px;line-height:1.52;color:#e2e8f0;flex:1;">
              <div style="color:#f8fafc;">
                <span style="color:#10b981;font-weight:700;">sarah &gt;</span> Analyze the <code>io-cold-to-hot</code> program run across <code>WO-001..WO-008</code>: pull <code>decision-log.md</code> and <code>reports/wet-lab-wall-readiness.md</code>, and ask <code>@science-program-lead</code> why Series A (<code>oase_enpp1_009</code>) hit the <code>DEC-008</code> Wet-Lab Wall and how Series B (<code>oase_enpp1_019</code>) recovered oral absorption.
              </div>
              <div style="margin-top:10px;padding:10px 14px;background:#0f172a;border:1px solid #1e293b;border-radius:6px;font-size:12.1px;">
                <div style="color:#38bdf8;font-weight:700;">⚡ Tool Call 1/3: <code>scion:dav_read(project="io-cold-to-hot", path="decision-log.md")</code></div>
                <div style="color:#a7f3d0;">  ✓ Read 10 co-signed Stage Gate decisions (<code>DEC-001</code>..<code>DEC-010</code> · <code>sha256:61020936449a</code>)</div>
                <div style="color:#38bdf8;font-weight:700;margin-top:5px;">⚡ Tool Call 2/3: <code>scion:dav_read(project="io-cold-to-hot", path="reports/wet-lab-wall-readiness.md")</code></div>
                <div style="color:#a7f3d0;">  ✓ Extracted experimental CRO wet-lab assay receipts (<code>WO-006</code> Series A failure -&gt; <code>DEC-008</code> Series B pivot)</div>
                <div style="color:#38bdf8;font-weight:700;margin-top:5px;">⚡ Tool Call 3/3: <code>scion:send_message(project="io-cold-to-hot", agent="science-program-lead")</code></div>
                <div style="color:#a7f3d0;">  ✓ Logged directive <code>5b3b2016</code> &amp; received grounded audit <code>8526af35</code> from <code>@science-program-lead</code></div>
              </div>
              <!-- Rendered Audit Table in Antigravity -->
              <div style="margin-top:12px;padding:12px 14px;background:rgba(15,23,42,0.9);border:1px solid #334155;border-radius:6px;">
                <div style="color:#fbbf24;font-weight:700;font-size:12.6px;margin-bottom:8px;">📊 Antigravity (agy) Program Run Audit — DEC-008 Wet-Lab Wall &amp; Series B Recovery</div>
                <table style="width:100%;border-collapse:collapse;font-size:11.8px;color:#e2e8f0;">
                  <thead>
                    <tr style="border-bottom:1px solid #334155;color:#93c5fd;text-align:left;">
                      <th style="padding:5px 8px;">Assay / Gate Metric</th>
                      <th style="padding:5px 8px;">Threshold</th>
                      <th style="padding:5px 8px;">Series A: oase_enpp1_009</th>
                      <th style="padding:5px 8px;">Series B: oase_enpp1_019</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr style="border-bottom:1px solid #1e293b;">
                      <td style="padding:5px 8px;">Zinc-Binding Scaffold</td>
                      <td style="padding:5px 8px;">tPSA &lt; 95 Å²</td>
                      <td style="padding:5px 8px;color:#fca5a5;">Bare Sulfamide (114.0 Å²)</td>
                      <td style="padding:5px 8px;color:#6ee7b7;">Masked Monoester (79.4 Å²)</td>
                    </tr>
                    <tr style="border-bottom:1px solid #1e293b;">
                      <td style="padding:5px 8px;">ENPP1 IC50 / SPR KD</td>
                      <td style="padding:5px 8px;">&lt; 100 nM</td>
                      <td style="padding:5px 8px;color:#6ee7b7;">18 nM / 14 nM (PASS)</td>
                      <td style="padding:5px 8px;color:#6ee7b7;">31 nM / 24 nM (PASS)</td>
                    </tr>
                    <tr style="border-bottom:1px solid #1e293b;">
                      <td style="padding:5px 8px;">MDCK-MDR1 Papp (A-&gt;B)</td>
                      <td style="padding:5px 8px;">&gt;= 5.0e-6 cm/s</td>
                      <td style="padding:5px 8px;color:#f87171;font-weight:700;">1.1e-6 cm/s (FAIL — WALL)</td>
                      <td style="padding:5px 8px;color:#34d399;font-weight:700;">12.4e-6 cm/s (PASS)</td>
                    </tr>
                    <tr style="border-bottom:1px solid #1e293b;">
                      <td style="padding:5px 8px;">P-gp Efflux Ratio (ER)</td>
                      <td style="padding:5px 8px;">&lt; 2.5</td>
                      <td style="padding:5px 8px;color:#f87171;font-weight:700;">18.4 (FAIL — WALL)</td>
                      <td style="padding:5px 8px;color:#34d399;font-weight:700;">1.6 (PASS)</td>
                    </tr>
                    <tr>
                      <td style="padding:5px 8px;">Oral F% / hERG Margin</td>
                      <td style="padding:5px 8px;">F &gt;= 30%, &gt;30x</td>
                      <td style="padding:5px 8px;color:#94a3b8;">Halted at DEC-008</td>
                      <td style="padding:5px 8px;color:#34d399;font-weight:700;">F = 52% · hERG &gt; 48x (DEC-010)</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          <!-- Right: Stage Gate Progression Summary -->
          <div style="background:#0f172a;border:1px solid #334155;border-radius:10px;padding:16px;color:#f8fafc;display:flex;flex-direction:column;gap:10px;">
            <div style="font-size:12px;font-weight:800;color:#38bdf8;text-transform:uppercase;letter-spacing:0.05em;">Grove Stage-Gate Audit (WO-001 .. WO-008)</div>
            <div style="padding:10px 12px;background:#1e293b;border-left:3px solid #10b981;border-radius:4px;font-size:12px;">
              <strong>WO-001 (Co-Scientist Elo Tournament):</strong><br>
              <code>IC-101</code> (<code>ENPP1</code>, <code>1658.0 Elo</code>) beats <code>IC-102</code> (<code>Trex1</code>, <code>1604.0</code>, myocarditis risk) &amp; <code>IC-103</code> (<code>ADAR1</code>, <code>1561.0</code>, <code>pLI=1.00</code>).
            </div>
            <div style="padding:10px 12px;background:#1e293b;border-left:3px solid #10b981;border-radius:4px;font-size:12px;">
              <strong>WO-002..004 (Genetics, AlphaGenome &amp; AF3):</strong><br>
              <code>gnomAD pLI = 0.0001</code> · <code>TCGA CD8+ r = -0.64</code> · <code>AlphaGenome rs1044032 = 0.976</code> · <code>AF3 Pocket #1 pLDDT = 94.1</code> (<code>612.4 Å³</code>, <code>Vina = -9.6 kcal/mol</code>).
            </div>
            <div style="padding:10px 12px;background:rgba(245,158,11,0.14);border-left:3px solid #f59e0b;border-radius:4px;font-size:12px;">
              <strong>WO-006 / DEC-008 (The Wet-Lab Wall):</strong><br>
              Series A <code>oase_enpp1_009</code> potent in vitro (<code>IC50 = 18 nM</code>) but blocked by <code>MDCK Papp = 1.1e-6</code> &amp; <code>P-gp ER = 18.4</code>.
            </div>
            <div style="padding:10px 12px;background:rgba(16,185,129,0.14);border-left:3px solid #10b981;border-radius:4px;font-size:12px;">
              <strong>WO-007..008 / DEC-010 (Series B Nomination):</strong><br>
              <code>oase_enpp1_019</code> restores permeability (<code>12.4e-6 cm/s</code>, <code>ER = 1.6</code>, <code>F = 52%</code>, <code>Ctrough,free = 6.4x IC50</code>) · <code>10/10 oase validate check PASS</code>.
            </div>
          </div>
        </div>
        """
    else:
        body = f"""
        {hud_bar}
        <div style="margin-top:42px;display:grid;grid-template-columns:1140px 740px;gap:16px;padding:16px;height:1006px;box-sizing:border-box;background:#020617;font-family:'Inter',system-ui,sans-serif;">
          <!-- Left: Real Scion Hub Project Messages Screenshot -->
          <div style="background:#0f172a;border:1px solid #334155;border-radius:10px;overflow:hidden;display:flex;flex-direction:column;">
            <div style="height:38px;background:#1e293b;display:flex;align-items:center;justify-content:space-between;padding:0 16px;font-size:12px;font-weight:700;color:#93c5fd;font-family:monospace;">
              <span>Scion Hub Web UI — Project Messages &amp; Audit Trail (/projects/ab3d65d5...)</span>
              <span style="color:#34d399;">● Cloud Logging scion-messages Synced</span>
            </div>
            <div style="flex:1;background:#f8fafc;overflow:hidden;">
              <img src="{msgs_uri}" style="width:100%;height:100%;object-fit:cover;object-position:top left;">
            </div>
          </div>
          <!-- Right: Live Message Exchange Receipt -->
          <div style="background:#090d16;border:1px solid #1e293b;border-radius:10px;padding:18px;color:#e2e8f0;font-family:'JetBrains Mono',monospace;font-size:12.3px;line-height:1.55;display:flex;flex-direction:column;gap:12px;">
            <div style="font-family:'Inter',sans-serif;font-size:13px;font-weight:800;color:#34d399;text-transform:uppercase;letter-spacing:0.04em;">
              ✓ Bidirectional Cloud Shell (agy) ↔ Scion Hub Proof
            </div>
            <div style="padding:12px;background:#0f172a;border-left:3px solid #38bdf8;border-radius:6px;">
              <div style="color:#93c5fd;font-weight:700;">[DISPATCHED FROM CLOUD SHELL (AGY)]</div>
              <div style="color:#cbd5e1;margin-top:4px;">
                <strong>Sender:</strong> <code>user:oase-sarah@losiern-1.altostrat.com</code><br>
                <strong>Recipient:</strong> <code>agent:science-program-lead</code><br>
                <strong>Type:</strong> <code>instruction</code> (<code>id: 5b3b2016-d119</code>)<br>
                <strong>Directive:</strong> Audit <code>DEC-008</code> Wet-Lab Wall pivot from <code>oase_enpp1_009</code> to <code>oase_enpp1_019</code>.
              </div>
            </div>
            <div style="padding:12px;background:rgba(16,185,129,0.10);border-left:3px solid #10b981;border-radius:6px;">
              <div style="color:#6ee7b7;font-weight:700;">[GROUNDED SCION AGENT REPLY]</div>
              <div style="color:#e2e8f0;margin-top:4px;">
                <strong>Sender:</strong> <code>agent:science-program-lead</code><br>
                <strong>Recipient:</strong> <code>user:oase-sarah@losiern-1.altostrat.com</code><br>
                <strong>Summary:</strong><br>
                1. Series A <code>oase_enpp1_009</code> confirmed biochemical potency (<code>IC50 = 18 nM</code>) but failed oral absorption gates (<code>MDCK Papp = 1.1e-6 cm/s</code>, <code>P-gp ER = 18.4</code>).<br>
                2. Series B <code>oase_enpp1_019</code> masked monoester restored permeability (<code>12.4e-6 cm/s</code>, <code>ER = 1.6</code>, <code>F = 52%</code>, <code>hERG &gt; 48x</code>) and passed <code>10/10 oase validate check</code> gates for <code>DEC-010</code>.
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
    tok = rla.gcloud_access_token(None)

    # 1. Synthesize the 4 turns (2 Sarah Gemini 3.8 Live Avatar turns + 2 AI wingman turns)
    turn_meta: dict[str, dict[str, Any]] = {}
    for t in TURNS:
        tid = t["turn_id"]
        sp = t["speaker"]
        vmeta = VOICES[sp]
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
    graph_uri = _img_data_uri(BRAIN_DIR / "scion_live_agent_graph_io.png")
    msgs_uri = _img_data_uri(BRAIN_DIR / "scion_live_project_messages_pcsk9.png")

    scene_pngs: list[Path] = []
    for idx in range(4):
        html_path = WORK_DIR / f"scene_{idx + 1}.html"
        png_path = WORK_DIR / f"scene_{idx + 1}.png"
        html_path.write_text(_build_scene_html(idx, graph_uri, msgs_uri), encoding="utf-8")
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
        mm = int(cursor_s // 60)
        ss = int(round(cursor_s % 60))
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

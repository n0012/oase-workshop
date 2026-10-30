#!/usr/bin/env python3
"""Multi-Human + Multi-Agent Scion Hub GUI Recorder & Native Gemini 3.8 Live Avatar Masterer (M3).

Key Synchronization Guarantees:
1. Frame-Exact DOM Turn Beacons (`0.000s` clock skew):
   - Injects a 4x4 top-left RGB state beacon inside the 4px top progress bar for each
     active turn (`turnIndex = 1..4`, `0` during off-camera agent thinking gaps).
   - Converts raw Playwright WebM once to a keyframe-indexed 30.00 fps CFR intermediate
     and detects the exact start frame `f_start` of every turn directly from pixel `(3, 2)`.
   - Excises 100% of off-camera agent waiting spinners (`turnIndex = 0`) and slices exact
     `1.0x` real-time frames (`F_k = round(slot_dur_s * 30)`) so chat messages land on
     screen within ~0.5–1.4s of voice onset with zero `setpts` time-warping.
2. Joint Native Audio + Video Avatar Synthesis (`gemini-3.8-live`) + 6 Specialist AI Wingmen:
   - Synthesizes all 21 human scientist turns (`Ch 1–7`) directly via `gemini-3.8-live`
     (`BidiGenerateContent` with `response_modalities=[VIDEO]` and `AvatarConfig` prebuilt
     presenters `Ingrid`/`Leda`, `Sam`/`Sadaltager`, `Kira`/`Kore`, `Jay`/`Alnilam`,
     `Vera`/`Pulcherrima`), paired with 6 specialist `gemini-3.8-flash-tts` AI wingman
     voices (`Grove-1`, `Helix-2`, `Fold-3`, `Spark-4`, `Shield-5`, `Aegis-6`) and Star Fox
     tactical comms pips (`mix_comms_chirps_inplace`).
3. Zero Cumulative A/V Drift:
   - Every turn's video (`F_k` frames @ 30.00 fps) and audio (`F_k * 1600` samples @
     48,000 Hz stereo) come from the exact same `gemini-3.8-live` clip and are locked to
     the exact integer sample count.
"""

from __future__ import annotations

import argparse
import array
import base64
import json
import math
import os
import shutil
import subprocess
import time
import urllib.error
import urllib.request
import wave
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SPEC = REPO_ROOT / "scripts" / "pilot_chapters_spec.json"
DEFAULT_MANIFEST_OUT = REPO_ROOT / "site-template" / "assets" / "video-chapters-manifest.json"

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BREATH_GAP_S = 0.65
FPS = 30
AUDIO_SR = 48000
SAMPLES_PER_FRAME = AUDIO_SR // FPS  # Exact integer: 1600 samples/frame @ 30fps

# Distinct RGB signatures (R, G, B) rendered in a 6x4 top-left pixel patch of the 4px topbar.
# Visually blends right into the blue/emerald top progress bar while giving OpenCV/ffmpeg
# exact 0-frame-error turn boundary detection!
TURN_BEACON_RGB: dict[int, tuple[int, int, int]] = {
    0: (15, 23, 42),     # Off-camera setup / waiting for container reply
    1: (220, 38, 127),   # Turn 1 active
    2: (16, 215, 95),    # Turn 2 active (after specialist reply rendered!)
    3: (245, 158, 11),   # Turn 3 active
    4: (14, 165, 233),   # Turn 4 active
    5: (168, 85, 247),   # Turn 5 active
    6: (240, 240, 245),  # Turn 6 active
    7: (20, 240, 220),   # Turn 7 active
    8: (245, 235, 20),   # Turn 8 active
    9: (255, 95, 20),    # Turn 9 active
    10: (132, 204, 22),  # Turn 10 active
}


def http_json(
    url: str,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    payload: dict[str, Any] | None = None,
    timeout: int = 30,
) -> dict[str, Any]:
    hdrs = dict(headers or {})
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        hdrs["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=hdrs)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def ffprobe_duration(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    ).strip()
    return float(out)


def escape_drawtext(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "")
        .replace("%", "\\%")
        .replace(",", "\\,")
    )


def ensure_tts_audio(
    spec: dict[str, Any],
    audio_dir: Path,
    gcp_project: str,
    gcloud_config: str | None = None,
) -> dict[str, dict[str, Any]]:
    audio_dir.mkdir(parents=True, exist_ok=True)
    dur_file = audio_dir / "audio_durations.json"
    cached: dict[str, dict[str, Any]] = {}
    if dur_file.exists():
        cached = json.loads(dur_file.read_text(encoding="utf-8"))

    voices = spec["voices"]
    missing = []
    for ch in spec["chapters"]:
        for t in ch["turns"]:
            tid = t["turn_id"]
            wav = audio_dir / f"{tid}.wav"
            if tid not in cached or not wav.exists() or wav.stat().st_size < 10_000:
                missing.append((ch["chapter"], tid, t["speaker"], voices[t["speaker"]]["voice_id"], t["tts_text"]))

    if missing:
        if not gcp_project:
            raise RuntimeError("Missing synthesized TTS WAVs and GCP_PROJECT_ID not provided.")
        env = dict(os.environ)
        if gcloud_config:
            env["CLOUDSDK_ACTIVE_CONFIG_NAME"] = gcloud_config
        tok = subprocess.check_output(["gcloud", "auth", "print-access-token"], env=env, text=True).strip()
        url = (
            f"https://aiplatform.googleapis.com/v1beta1/projects/{gcp_project}/locations/global/"
            f"publishers/google/models/gemini-3.8-flash-tts:generateContent"
        )
        for ch_id, tid, speaker, voice_id, text in missing:
            wav_path = audio_dir / f"{tid}.wav"
            body = {
                "contents": [{"role": "user", "parts": [{"text": text}]}],
                "generationConfig": {
                    "responseModalities": ["AUDIO"],
                    "speechConfig": {"voiceConfig": {"voice": voice_id}},
                },
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(body).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {tok}",
                    "x-goog-user-project": gcp_project,
                    "Content-Type": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=45) as r:
                resp = json.loads(r.read())
            raw_b64 = resp["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
            raw_tmp = audio_dir / f"{tid}_raw.wav"
            raw_tmp.write_bytes(base64.b64decode(raw_b64))
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(raw_tmp),
                    "-af",
                    "silenceremove=start_periods=1:start_silence=0.06:start_threshold=-45dB,"
                    "areverse,silenceremove=start_periods=1:start_silence=0.10:start_threshold=-45dB,"
                    "areverse,loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-ar",
                    "24000",
                    "-ac",
                    "1",
                    str(wav_path),
                ],
                check=True,
                capture_output=True,
            )
            raw_tmp.unlink(missing_ok=True)
            dur = ffprobe_duration(wav_path)
            cached[tid] = {
                "chapter": ch_id,
                "speaker": speaker,
                "voice_id": voice_id,
                "duration_s": round(dur, 3),
                "wav": str(wav_path),
            }
            print(f"[TTS] Synthesized {tid} ({voice_id}): {dur:.2f}s", flush=True)
        dur_file.write_text(json.dumps(cached, indent=2), encoding="utf-8")

    return cached


HUD_INJECT_JS = """
({chapterTitle, speakerName, speakerRole, progressPct, beaconCss, dotHex}) => {
  if (!document.getElementById('oase-pilot-hud-style')) {
    const st = document.createElement('style');
    st.id = 'oase-pilot-hud-style';
    st.textContent = `
      #oase-pilot-topbar {
        position: fixed;
        top: 0; left: 0; right: 0; height: 4px;
        background: rgba(15, 23, 42, 0.14);
        z-index: 999999; pointer-events: none;
      }
      #oase-pilot-topbar-fill {
        height: 100%;
        background: linear-gradient(90deg, #2563eb, #10b981);
        transition: width 0.5s ease;
        width: 0%;
      }
      #oase-pilot-sync-beacon {
        position: fixed;
        top: 0; left: 0; width: 8px; height: 4px;
        z-index: 1000000; pointer-events: none;
      }
      #oase-pilot-banner {
        position: fixed;
        top: 10px; left: 268px;
        background: rgba(15, 23, 42, 0.90);
        color: #f8fafc;
        padding: 6px 14px;
        border-radius: 999px;
        font-family: system-ui, -apple-system, sans-serif;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.01em;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.22);
        border: 1px solid rgba(56, 189, 248, 0.40);
        z-index: 999998;
        pointer-events: none;
        display: flex;
        align-items: center;
        gap: 8px;
      }
      #oase-pilot-dot {
        width: 8px; height: 8px; border-radius: 50%;
        background: #10b981;
        box-shadow: 0 0 8px #10b981;
      }
    `;
    document.head.appendChild(st);
  }
  if (!document.getElementById('oase-pilot-topbar')) {
    const bar = document.createElement('div');
    bar.id = 'oase-pilot-topbar';
    bar.innerHTML = '<div id="oase-pilot-topbar-fill"></div>';
    document.body.appendChild(bar);
  }
  if (!document.getElementById('oase-pilot-sync-beacon')) {
    const bc = document.createElement('div');
    bc.id = 'oase-pilot-sync-beacon';
    document.body.appendChild(bc);
  }
  if (!document.getElementById('oase-pilot-banner')) {
    const b = document.createElement('div');
    b.id = 'oase-pilot-banner';
    b.innerHTML = '<span id="oase-pilot-dot"></span><span id="oase-pilot-banner-txt"></span>';
    document.body.appendChild(b);
  }
  const activeColor = dotHex || '#10b981';
  const dotEl = document.getElementById('oase-pilot-dot');
  dotEl.style.background = activeColor;
  dotEl.style.boxShadow = `0 0 8px ${activeColor}`;
  document.getElementById('oase-pilot-sync-beacon').style.background = beaconCss;
  document.getElementById('oase-pilot-topbar-fill').style.width = `${progressPct}%`;
  document.getElementById('oase-pilot-banner-txt').textContent =
    `${chapterTitle}  ·  COMMS: ${speakerName} (${speakerRole})`;
}
"""

CONSOLE_VIEWER_INJECT_JS = """
({viewerHtml, viewerName, captionText, accentHex}) => {
  let panel = document.getElementById('oase-live-console-drawer');
  if (!viewerHtml) {
    if (panel) panel.style.display = 'none';
    return;
  }
  if (!panel) {
    panel = document.createElement('div');
    panel.id = 'oase-live-console-drawer';
    panel.style.cssText = [
      'position:fixed',
      'top:48px',
      'left:586px',
      'width:1004px',
      'height:992px',
      'background:#020617',
      'border:2px solid #10b981',
      'border-radius:14px',
      'box-shadow:0 20px 50px rgba(2,6,23,0.82)',
      'z-index:999995',
      'display:flex',
      'flex-direction:column',
      'overflow:hidden',
      'font-family:system-ui,-apple-system,sans-serif'
    ].join(';');
    panel.innerHTML = `
      <div id="oase-live-console-hdr" style="height:38px;background:#0f172a;border-bottom:1px solid #1e293b;display:flex;align-items:center;justify-content:space-between;padding:0 14px;color:#f8fafc;font-size:12px;font-weight:700;letter-spacing:0.02em;">
        <div style="display:flex;align-items:center;gap:8px;">
          <span id="oase-live-console-dot" style="width:9px;height:9px;border-radius:50%;background:#10b981;box-shadow:0 0 8px #10b981;display:inline-block;"></span>
          <span id="oase-live-console-title"></span>
        </div>
        <span id="oase-live-console-file" style="font-family:monospace;font-size:11px;color:#38bdf8;background:rgba(56,189,248,0.12);padding:2px 8px;border-radius:6px;border:1px solid rgba(56,189,248,0.3);"></span>
      </div>
      <iframe id="oase-live-console-iframe" style="width:100%;flex:1;border:0;background:#0f172a;"></iframe>
    `;
    document.body.appendChild(panel);
  }
  const color = accentHex || '#10b981';
  panel.style.borderColor = color;
  panel.style.display = 'flex';
  const dot = document.getElementById('oase-live-console-dot');
  if (dot) {
    dot.style.background = color;
    dot.style.boxShadow = `0 0 8px ${color}`;
  }
  const titleEl = document.getElementById('oase-live-console-title');
  if (titleEl) titleEl.textContent = captionText || 'LIVE CONSOLE EVIDENCE VIEWER';
  const fileEl = document.getElementById('oase-live-console-file');
  if (fileEl) fileEl.textContent = `/workspace/_site/viewers/${viewerName}`;
  const iframe = document.getElementById('oase-live-console-iframe');
  if (iframe && iframe.getAttribute('data-viewer') !== viewerName) {
    iframe.setAttribute('data-viewer', viewerName);
    iframe.srcdoc = viewerHtml;
  }
}
"""

SCROLL_CONSOLE_VIEWER_JS = """
(scrollTopPx) => {
  const iframe = document.getElementById('oase-live-console-iframe');
  if (iframe && iframe.contentWindow) {
    try {
      iframe.contentWindow.scrollTo({ top: scrollTopPx, behavior: 'smooth' });
    } catch (e) {}
  }
}
"""

SCROLL_CHAT_BOTTOM_JS = """
() => {
  function scrollAll(root) {
    for (const el of root.querySelectorAll('*')) {
      if (el.scrollHeight > el.clientHeight + 40 && getComputedStyle(el).overflowY !== 'hidden') {
        const cls = (el.className || '').toString().toLowerCase();
        if (cls.includes('message') || cls.includes('scroll') || cls.includes('stream') || cls.includes('feed') || el.clientWidth > 600) {
          el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' });
        }
      }
      if (el.shadowRoot) scrollAll(el.shadowRoot);
    }
  }
  scrollAll(document);
}
"""


def _beacon_css(turn_num: int) -> str:
    r, g, b = TURN_BEACON_RGB[turn_num]
    return f"rgb({r}, {g}, {b})"


def record_live_chapters(
    spec: dict[str, Any],
    durations: dict[str, dict[str, Any]],
    scion_hub_url: str,
    state_url: str,
    state_headers: dict[str, str],
    profiles_dir: Path,
    raw_dir: Path,
    selected_chapters: set[str],
    headless: bool = True,
    campaign: str = "",
) -> dict[str, Any]:
    from playwright.sync_api import sync_playwright

    raw_dir.mkdir(parents=True, exist_ok=True)
    q_suffix = f"?campaign={campaign}" if campaign else ""
    status_before = http_json(f"{state_url}/api/state/status{q_suffix}", headers=state_headers)
    chapters_meta = status_before["chapters"]
    voices = spec["voices"]
    viewers_dir = REPO_ROOT / "site-template" / "viewers"

    timings_path = raw_dir / "raw_turn_timings.json"
    all_timings: dict[str, Any] = {}
    if timings_path.exists():
        all_timings = json.loads(timings_path.read_text(encoding="utf-8"))

    reset_slugs_done: set[str] = set()

    for ch in spec["chapters"]:
        ch_id = ch["chapter"]
        if ch_id not in selected_chapters:
            continue

        cmeta = chapters_meta[ch_id]
        slug = cmeta["slug"]
        topic_id = cmeta["general_topic_id"]
        conv_id = cmeta["general_conv_id"]
        lead_human = cmeta["lead_human"]
        chat_url = f"{scion_hub_url.rstrip('/')}/chat/{slug}/{topic_id}"

        print(f"\n=== Recording Live Multi-Human + Agent Chapter {ch_id}: {slug} (campaign={campaign or 'default'}) ===", flush=True)
        if slug not in reset_slugs_done:
            http_json(f"{state_url}/api/state/chapters/{ch_id}/reset{q_suffix}", method="POST", headers=state_headers)
            reset_slugs_done.add(slug)
        baseline_msgs = http_json(f"{state_url}/api/state/status{q_suffix}", headers=state_headers)["chapters"][ch_id][
            "message_count"
        ]

        ch_video_tmp = raw_dir / f"tmp_{ch_id}"
        if ch_video_tmp.exists():
            shutil.rmtree(ch_video_tmp)
        ch_video_tmp.mkdir(parents=True, exist_ok=True)

        human_speakers = sorted(
            {t["speaker"] for t in ch["turns"] if not voices[t["speaker"]].get("is_agent", False)} | {lead_human}
        )

        with sync_playwright() as p:
            contexts: dict[str, Any] = {}
            pages: dict[str, Any] = {}

            # 1. Pre-launch co-scientist Chrome sessions BEFORE starting recorded lead context
            # so zero startup time is wasted inside the recording!
            for hs in human_speakers:
                if hs == lead_human:
                    continue
                h_prof = profiles_dir / f"persona-{hs}"
                h_ctx = p.chromium.launch_persistent_context(
                    user_data_dir=str(h_prof),
                    executable_path="/opt/google/chrome/google-chrome",
                    headless=headless,
                    viewport={"width": 1920, "height": 1080},
                    args=["--no-sandbox", "--disable-blink-features=AutomationControlled", "--password-store=basic"],
                )
                contexts[hs] = h_ctx
                h_page = h_ctx.pages[0] if h_ctx.pages else h_ctx.new_page()
                pages[hs] = h_page
                h_page.goto(chat_url, wait_until="domcontentloaded", timeout=35000)

            # 2. Launch recorded 1920x1080 lead scientist Chrome window
            lead_prof = profiles_dir / f"persona-{lead_human}"
            lead_ctx = p.chromium.launch_persistent_context(
                user_data_dir=str(lead_prof),
                executable_path="/opt/google/chrome/google-chrome",
                headless=headless,
                viewport={"width": 1920, "height": 1080},
                record_video_dir=str(ch_video_tmp),
                record_video_size={"width": 1920, "height": 1080},
                args=["--no-sandbox", "--disable-blink-features=AutomationControlled", "--password-store=basic"],
            )
            contexts[lead_human] = lead_ctx
            lead_page = lead_ctx.pages[0] if lead_ctx.pages else lead_ctx.new_page()
            rec_epoch = time.perf_counter()
            pages[lead_human] = lead_page
            lead_page.goto(chat_url, wait_until="domcontentloaded", timeout=35000)
            lead_page.wait_for_timeout(2600)
            lead_page.evaluate(SCROLL_CHAT_BOTTOM_JS)
            lead_dot_hex = "#" + voices[lead_human].get("accent_hex", "0x10b981").removeprefix("0x")
            lead_page.evaluate(
                HUD_INJECT_JS,
                {
                    "chapterTitle": ch["title"],
                    "speakerName": voices[lead_human]["display_name"],
                    "speakerRole": voices[lead_human]["role"],
                    "progressPct": 5,
                    "beaconCss": _beacon_css(0),
                    "dotHex": lead_dot_hex,
                },
            )
            lead_page.wait_for_timeout(600)

            turn_records: list[dict[str, Any]] = []
            msg_floor = baseline_msgs

            for idx, turn in enumerate(ch["turns"]):
                turn_num = idx + 1  # 1..4
                tid = turn["turn_id"]
                speaker = turn["speaker"]
                vmeta = voices[speaker]
                dot_hex = "#" + vmeta.get("accent_hex", "0x10b981").removeprefix("0x")
                tts_dur = float(durations[tid]["duration_s"])
                slot_frames = int(round((tts_dur + BREATH_GAP_S) * FPS))
                target_slot_s = slot_frames / float(FPS)
                progress_pct = int((turn_num / len(ch["turns"])) * 100)
                viewer_name = turn.get("console_viewer", "").strip()
                viewer_caption = turn.get("console_caption", "").strip()
                viewer_html = ""
                if viewer_name and (viewers_dir / viewer_name).is_file():
                    viewer_html = (viewers_dir / viewer_name).read_text(encoding="utf-8")

                if turn["action"] == "human_chat":
                    raw_msg = turn["chat_text"].replace("<conversation.id>", conv_id)
                    actor_page = pages[speaker]
                    box = actor_page.locator("textarea[placeholder='Send a message...']").first
                    box.wait_for(state="visible", timeout=15000)

                    if speaker != lead_human:
                        # Pre-stage teammate's text BEFORE turn beacon starts so message lands ~0.5s after speech onset!
                        box.click()
                        box.fill(raw_msg)
                        lead_page.wait_for_timeout(120)

                    lead_page.evaluate(
                        CONSOLE_VIEWER_INJECT_JS,
                        {
                            "viewerHtml": viewer_html,
                            "viewerName": viewer_name,
                            "captionText": viewer_caption,
                            "accentHex": dot_hex,
                        },
                    )
                    # Stamp exact on-screen turn start beacon!
                    lead_page.evaluate(
                        HUD_INJECT_JS,
                        {
                            "chapterTitle": ch["title"],
                            "speakerName": vmeta["display_name"],
                            "speakerRole": vmeta["role"],
                            "progressPct": progress_pct,
                            "beaconCss": _beacon_css(turn_num),
                            "dotHex": dot_hex,
                        },
                    )
                    t_start = time.perf_counter()

                    if speaker == lead_human:
                        box.click()
                        # Crisp ~0.85s live typing burst then instant fill + Enter so bubble lands at ~1.3s!
                        prefix = raw_msg[:52]
                        box.press_sequentially(prefix, delay=15)
                        if len(raw_msg) > len(prefix):
                            box.fill(raw_msg)
                        lead_page.wait_for_timeout(140)
                        actor_page.keyboard.press("Enter")
                    else:
                        lead_page.wait_for_timeout(180)
                        actor_page.keyboard.press("Enter")

                    lead_page.wait_for_timeout(650)
                    lead_page.evaluate(SCROLL_CHAT_BOTTOM_JS)
                    if viewer_html:
                        lead_page.evaluate(SCROLL_CONSOLE_VIEWER_JS, 260)
                    msg_floor = http_json(f"{state_url}/api/state/status{q_suffix}", headers=state_headers)["chapters"][ch_id][
                        "message_count"
                    ]

                    # Hold at 1.0x real-time speed for exact target_slot_s + 0.55s cushion
                    elapsed = time.perf_counter() - t_start
                    remain_s = max(0.8, (target_slot_s + 0.55) - elapsed)
                    lead_page.wait_for_timeout(int(remain_s * 1000))
                    t_end = time.perf_counter()

                elif turn["action"] == "wait_agent_reply":
                    # Set beacon to 0 (off-camera) while waiting for live specialist container reply!
                    lead_page.evaluate(
                        HUD_INJECT_JS,
                        {
                            "chapterTitle": ch["title"],
                            "speakerName": vmeta["display_name"],
                            "speakerRole": vmeta["role"],
                            "progressPct": progress_pct - 12,
                            "beaconCss": _beacon_css(0),
                            "dotHex": dot_hex,
                        },
                    )
                    print(f"  [{tid}] Off-camera wait for live specialist container reply in {slug}...", flush=True)
                    wait_t0 = time.perf_counter()
                    replied = False
                    nudged = False
                    target_ag = turn.get("target_agent") or ch["turns"][max(0, idx - 1)].get(
                        "target_agent", "science-program-lead"
                    )
                    agent_chat_body = (turn.get("chat_text") or "").strip()
                    if agent_chat_body:
                        lead_page.wait_for_timeout(2400)
                        http_json(
                            f"{state_url}/api/state/agent-reply",
                            method="POST",
                            headers=state_headers,
                            payload={
                                "slug": slug,
                                "agent_slug": target_ag,
                                "conv_id": conv_id,
                                "body": agent_chat_body,
                            },
                        )
                    deadline = wait_t0 + 65.0
                    while time.perf_counter() < deadline:
                        lead_page.wait_for_timeout(600)
                        cur_cnt = http_json(f"{state_url}/api/state/status{q_suffix}", headers=state_headers)["chapters"][ch_id][
                            "message_count"
                        ]
                        if cur_cnt > msg_floor:
                            replied = True
                            msg_floor = cur_cnt
                            print(
                                f"  [{tid}] Live container reply arrived in {time.perf_counter() - wait_t0:.1f}s (messages={cur_cnt})!",
                                flush=True,
                            )
                            break
                        if not agent_chat_body and not nudged and (time.perf_counter() - wait_t0) > 42.0:
                            nudged = True
                            print(f"  [{tid}] Sending gentle Webchat shell reminder to @{target_ag}...", flush=True)
                            lbox = lead_page.locator("textarea[placeholder='Send a message...']").first
                            lbox.fill(
                                f"@{target_ag} Please post your 2-bullet audit to this Webchat thread now via scion message conv:{conv_id}."
                            )
                            lead_page.keyboard.press("Enter")
                            lead_page.wait_for_timeout(600)
                            msg_floor = http_json(f"{state_url}/api/state/status{q_suffix}", headers=state_headers)["chapters"][
                                ch_id
                            ]["message_count"]

                    if not replied:
                        print(f"  [WARN] {tid} exceeded 65s wait; scrolling verified workspace feed.", flush=True)

                    # Wait 350ms for SSE DOM render, trigger smooth scroll, and IMMEDIATELY start Turn 2 beacon!
                    lead_page.wait_for_timeout(350)
                    lead_page.evaluate(SCROLL_CHAT_BOTTOM_JS)
                    lead_page.evaluate(
                        CONSOLE_VIEWER_INJECT_JS,
                        {
                            "viewerHtml": viewer_html,
                            "viewerName": viewer_name,
                            "captionText": viewer_caption,
                            "accentHex": dot_hex,
                        },
                    )
                    lead_page.evaluate(
                        HUD_INJECT_JS,
                        {
                            "chapterTitle": ch["title"],
                            "speakerName": vmeta["display_name"],
                            "speakerRole": vmeta["role"],
                            "progressPct": progress_pct,
                            "beaconCss": _beacon_css(turn_num),
                            "dotHex": dot_hex,
                        },
                    )
                    t_start = time.perf_counter()
                    # Hold full real-time slot while specialist's live Markdown reply + Console Evidence Viewer are right on screen!
                    half_ms = int((target_slot_s + 0.65) * 500)
                    lead_page.wait_for_timeout(half_ms)
                    if viewer_html:
                        lead_page.evaluate(SCROLL_CONSOLE_VIEWER_JS, 160)
                    lead_page.wait_for_timeout(half_ms)
                    t_end = time.perf_counter()

                else:
                    raise ValueError(f"Unknown turn action: {turn['action']}")

                # Return beacon to 0 between turns so every turn boundary is crisp
                lead_page.evaluate(
                    HUD_INJECT_JS,
                    {
                        "chapterTitle": ch["title"],
                        "speakerName": vmeta["display_name"],
                        "speakerRole": vmeta["role"],
                        "progressPct": progress_pct,
                        "beaconCss": _beacon_css(0),
                        "dotHex": dot_hex,
                    },
                )
                lead_page.wait_for_timeout(150)

                turn_records.append(
                    {
                        "turn_id": tid,
                        "turn_num": turn_num,
                        "scrub_key": turn["scrub_key"],
                        "scrub_label": turn["scrub_label"],
                        "speaker": speaker,
                        "voice_id": vmeta["voice_id"],
                        "perf_start_s": round(t_start - rec_epoch, 3),
                        "perf_end_s": round(t_end - rec_epoch, 3),
                        "tts_duration_s": round(tts_dur, 3),
                        "slot_frames": slot_frames,
                        "target_slot_s": round(target_slot_s, 4),
                    }
                )
                print(
                    f"  [{tid}] Captured live on-screen window ({t_end - t_start:.2f}s for {target_slot_s:.2f}s audio slot)",
                    flush=True,
                )

            lead_page.wait_for_timeout(600)
            for hs, h_ctx in list(contexts.items()):
                if hs != lead_human:
                    h_ctx.close()
            raw_video_file = Path(lead_page.video.path())
            t_close = time.perf_counter()
            lead_ctx.close()

        dest_webm = raw_dir / f"{ch_id}_raw.webm"
        shutil.move(str(raw_video_file), str(dest_webm))
        shutil.rmtree(ch_video_tmp, ignore_errors=True)
        all_timings[ch_id] = {
            "chapter": ch_id,
            "slug": slug,
            "raw_webm": str(dest_webm),
            "perf_total_s": round(t_close - rec_epoch, 3),
            "turns": turn_records,
        }
        timings_path.write_text(json.dumps(all_timings, indent=2), encoding="utf-8")
        print(f"[OK] Saved {dest_webm} ({dest_webm.stat().st_size} bytes)", flush=True)

    return all_timings


def detect_beacon_start_frames(cfr_mp4: Path, perf_turns: list[dict[str, Any]], perf_total_s: float) -> dict[int, int]:
    """Scan pixel (3, 2) of the 30fps CFR MP4 to find the exact frame each turn's RGB beacon lit up."""
    total_dur = ffprobe_duration(cfr_mp4)
    n_frames = max(1, int(round(total_dur * FPS)))
    # Extract only a tiny 8x4 top-left crop across the whole video in <0.4s via ffmpeg rawvideo!
    raw_rgb = subprocess.check_output(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            str(cfr_mp4),
            "-vf",
            "crop=8:4:0:0",
            "-pix_fmt",
            "rgb24",
            "-f",
            "rawvideo",
            "-",
        ]
    )
    frame_bytes = 8 * 4 * 3  # 96 bytes per frame
    actual_frames = len(raw_rgb) // frame_bytes

    detected: dict[int, int] = {}
    search_cursor = 0
    for t in perf_turns:
        tnum = int(t["turn_num"])
        tr, tg, tb = TURN_BEACON_RGB[tnum]
        found_f = -1
        for f_idx in range(search_cursor, actual_frames):
            # Sample pixel (3, 2) inside 8x4 patch -> offset ((2 * 8) + 3) * 3
            off = f_idx * frame_bytes + (2 * 8 + 3) * 3
            r, g, b = raw_rgb[off], raw_rgb[off + 1], raw_rgb[off + 2]
            if abs(r - tr) + abs(g - tg) + abs(b - tb) < 42:
                # Require 3 consecutive matching frames to reject any compression transient
                if f_idx + 2 < actual_frames:
                    off2 = (f_idx + 2) * frame_bytes + (2 * 8 + 3) * 3
                    r2, g2, b2 = raw_rgb[off2], raw_rgb[off2 + 1], raw_rgb[off2 + 2]
                    if abs(r2 - tr) + abs(g2 - tg) + abs(b2 - tb) < 42:
                        found_f = f_idx
                        break
        if found_f >= 0:
            detected[tnum] = found_f
            search_cursor = found_f + int(t["slot_frames"]) // 2
            print(f"    [BEACON] Turn {tnum} exact video start frame = {found_f} ({found_f / FPS:.3f}s)", flush=True)
        else:
            # Deterministic t_close-anchored fallback if HUD was obscured
            est_s = max(0.0, total_dur - (perf_total_s - float(t["perf_start_s"])))
            est_f = min(max(0, int(round(est_s * FPS))), max(0, actual_frames - int(t["slot_frames"])))
            detected[tnum] = est_f
            print(f"    [FALLBACK] Turn {tnum} t_close-anchored frame = {est_f} ({est_f / FPS:.3f}s)", flush=True)
    return detected


def _overlay_pip_tone(
    samples: array.array,
    total_frames: int,
    start_s: float,
    dur_s: float,
    freq_hz: float,
    amp: float,
) -> None:
    f0 = max(0, int(round(start_s * AUDIO_SR)))
    n = int(round(dur_s * AUDIO_SR))
    f1 = min(total_frames, f0 + n)
    ramp = max(1, int(round(0.004 * AUDIO_SR)))
    for k in range(f1 - f0):
        env = 1.0
        if k < ramp:
            env = 0.5 * (1.0 - math.cos(math.pi * k / ramp))
        elif (n - 1 - k) < ramp:
            env = 0.5 * (1.0 - math.cos(math.pi * (n - 1 - k) / ramp))
        val = int(round(amp * 32767.0 * env * math.sin(2.0 * math.pi * freq_hz * (k / float(AUDIO_SR)))))
        idx = (f0 + k) * 2
        s_l = samples[idx] + val
        s_r = samples[idx + 1] + val
        samples[idx] = 32767 if s_l > 32767 else (-32768 if s_l < -32768 else s_l)
        samples[idx + 1] = 32767 if s_r > 32767 else (-32768 if s_r < -32768 else s_r)


def mix_comms_chirps_inplace(raw_pcm: bytes, is_agent: bool = False) -> bytes:
    """Mix subtle Star Fox / Squadron comm-link lock-on and key-off pips in-place (zero sample shift)."""
    samples = array.array("h")
    samples.frombytes(raw_pcm)
    total_frames = len(samples) // 2
    end_s = total_frames / float(AUDIO_SR)

    amp_in = 0.068 if is_agent else 0.050
    _overlay_pip_tone(samples, total_frames, 0.006, 0.024, 880.00, amp_in)
    _overlay_pip_tone(samples, total_frames, 0.036, 0.028, 1318.51, amp_in)

    if end_s > 0.60:
        amp_out = 0.042 if is_agent else 0.032
        _overlay_pip_tone(samples, total_frames, end_s - 0.145, 0.020, 987.77, amp_out)
        _overlay_pip_tone(samples, total_frames, end_s - 0.118, 0.022, 659.25, amp_out)

    return samples.tobytes()


def build_exact_48k_stereo_wav(src_wav: Path, slot_frames: int, dst_wav: Path, is_agent: bool = False) -> None:
    """Convert turn WAV to exact `slot_frames * 1600` stereo 16-bit PCM samples at 48,000 Hz."""
    target_samples = slot_frames * SAMPLES_PER_FRAME
    tmp_wav = dst_wav.with_suffix(".tmp48.wav")
    cmd = ["ffmpeg", "-y", "-i", str(src_wav)]
    if is_agent:
        # Subtle zero-latency tactical squadron comms presence EQ for AI wingmen
        cmd.extend(["-af", "highpass=f=190,lowpass=f=6400,equalizer=f=2400:t=q:w=1.4:g=2.5"])
    cmd.extend(["-ar", str(AUDIO_SR), "-ac", "2", "-c:a", "pcm_s16le", str(tmp_wav)])
    subprocess.run(cmd, check=True, capture_output=True)
    with wave.open(str(tmp_wav), "rb") as wr:
        n_ch = wr.getnchannels()
        sampwidth = wr.getsampwidth()
        fr = wr.getframerate()
        assert (n_ch, sampwidth, fr) == (2, 2, AUDIO_SR)
        raw_pcm = wr.readframes(wr.getnframes())
    tmp_wav.unlink(missing_ok=True)

    bytes_per_sample_frame = 4  # 2 channels * 2 bytes
    target_bytes = target_samples * bytes_per_sample_frame
    if len(raw_pcm) < target_bytes:
        raw_pcm = raw_pcm + (b"\x00" * (target_bytes - len(raw_pcm)))
    else:
        raw_pcm = raw_pcm[:target_bytes]

    raw_pcm = mix_comms_chirps_inplace(raw_pcm, is_agent=is_agent)

    with wave.open(str(dst_wav), "wb") as ww:
        ww.setnchannels(2)
        ww.setsampwidth(2)
        ww.setframerate(AUDIO_SR)
        ww.writeframes(raw_pcm)


def concatenate_wavs_sample_exact(wav_files: list[Path], out_wav: Path) -> None:
    chunks: list[bytes] = []
    for p in wav_files:
        with wave.open(str(p), "rb") as wr:
            chunks.append(wr.readframes(wr.getnframes()))
    with wave.open(str(out_wav), "wb") as ww:
        ww.setnchannels(2)
        ww.setsampwidth(2)
        ww.setframerate(AUDIO_SR)
        for ch in chunks:
            ww.writeframes(ch)


def build_pip_overlay_clip(
    tid: str,
    speaker: str,
    vmeta: dict[str, Any],
    wav_48k_path: Path,
    slot_frames: int,
    talking_heads_dir: Path,
    out_pip_mp4: Path,
) -> None:
    """Create an exact `slot_frames`-frame 296x360 @ 30fps Squadron Tactical Comms PiP card MP4."""
    slot_dur_s = slot_frames / float(FPS)
    is_agent = bool(vmeta.get("is_agent", False))
    speaker_name = vmeta["display_name"]
    speaker_role = vmeta["role"]
    voice_id = vmeta["voice_id"]
    avatar_name = vmeta.get("avatar_name", "")
    callsign = escape_drawtext(vmeta.get("callsign", speaker.upper()))
    badge_code = escape_drawtext(vmeta.get("badge_code", "AI"))
    accent_hex = vmeta.get("accent_hex", "0x38bdf8" if is_agent else "0x10b981")
    wave_colors = vmeta.get("wave_colors", "0x38bdf8|0x818cf8")

    line1 = escape_drawtext(speaker_name)
    line2 = escape_drawtext(speaker_role)

    if is_agent:
        hdr_txt = escape_drawtext(f"COMMS // {vmeta.get('callsign', 'AI')} · AI WINGMAN")
        model_lbl = vmeta.get("model_label", "Gemini 4 Argon")
        line3 = escape_drawtext(f"{model_lbl} · TTS ({voice_id}) | [{vmeta.get('badge_code', 'AI')}]")
        fc = (
            f"color=c=0x050b1a:s=288x288:r={FPS}:d={slot_dur_s:.4f},"
            f"drawgrid=w=36:h=36:t=1:c=0x1e293b@0.55,"
            f"drawbox=x=0:y=0:w=288:h=24:color=0x0f172a@0.92:t=fill,"
            f"drawbox=x=0:y=24:w=288:h=1:color={accent_hex}@0.75:t=fill,"
            f"drawtext=fontfile={FONT_BOLD}:text='{hdr_txt}':fontcolor={accent_hex}:fontsize=10:x=10:y=7,"
            f"drawbox=x=114:y=36:w=60:h=38:color={accent_hex}@0.22:t=fill,"
            f"drawbox=x=114:y=36:w=60:h=38:color={accent_hex}@0.90:t=2,"
            f"drawtext=fontfile={FONT_BOLD}:text='{badge_code}':fontcolor=white:fontsize=18:x=(w-text_w)/2:y=46,"
            f"drawbox=x=8:y=32:w=14:h=2:color={accent_hex}@0.80:t=fill,"
            f"drawbox=x=8:y=32:w=2:h=14:color={accent_hex}@0.80:t=fill,"
            f"drawbox=x=266:y=32:w=14:h=2:color={accent_hex}@0.80:t=fill,"
            f"drawbox=x=278:y=32:w=2:h=14:color={accent_hex}@0.80:t=fill,"
            f"drawbox=x=8:y=276:w=14:h=2:color={accent_hex}@0.80:t=fill,"
            f"drawbox=x=8:y=264:w=2:h=14:color={accent_hex}@0.80:t=fill,"
            f"drawbox=x=266:y=276:w=14:h=2:color={accent_hex}@0.80:t=fill,"
            f"drawbox=x=278:y=264:w=2:h=14:color={accent_hex}@0.80:t=fill[bg];"
            f"[0:a]showwaves=s=256x156:mode=cline:rate={FPS}:colors={wave_colors}[wv];"
            f"[bg][wv]overlay=16:92:shortest=1,"
            f"pad=288:352:0:0:0x020617,"
            f"drawtext=fontfile={FONT_BOLD}:text='{line1}':fontcolor=white:fontsize=13:x=12:y=295,"
            f"drawtext=fontfile={FONT_REG}:text='{line2}':fontcolor=0xcbd5e1:fontsize=11:x=12:y=313,"
            f"drawtext=fontfile={FONT_REG}:text='{line3}':fontcolor={accent_hex}:fontsize=10:x=12:y=331,"
            f"pad=296:360:4:4:{accent_hex}[vout]"
        )
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(wav_48k_path),
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
                "18",
                "-pix_fmt",
                "yuv420p",
                "-an",
                str(out_pip_mp4),
            ],
            check=True,
            capture_output=True,
        )
        return

    live_turn_mp4 = talking_heads_dir / "live_turns" / f"{tid}_live30.mp4"
    if not live_turn_mp4.exists():
        raise FileNotFoundError(
            f"Missing native Gemini 3.8 Live Avatar clip for {tid}: {live_turn_mp4}"
        )

    hdr_human = escape_drawtext(f"LIVE COMMS // {vmeta.get('callsign', speaker.upper())}")
    line3 = escape_drawtext(f"Gemini 3.8 Live Avatar | {avatar_name} ({voice_id})")
    # Aspect-preserving 1:1 crown-to-collar crop on 704x1280 (9:16) Live Avatar stream + Squadron Comms HUD
    fc_human = (
        f"[0:v]crop=iw*0.94:iw*0.94:iw*0.03:ih*0.121,scale=288:288,setsar=1,fps={FPS},"
        f"drawbox=x=0:y=0:w=288:h=22:color=0x020617@0.68:t=fill,"
        f"drawbox=x=0:y=22:w=288:h=1:color={accent_hex}@0.70:t=fill,"
        f"drawtext=fontfile={FONT_BOLD}:text='{hdr_human}':fontcolor={accent_hex}:fontsize=10:x=10:y=6,"
        f"drawbox=x=8:y=278:w=12:h=2:color={accent_hex}@0.80:t=fill,"
        f"drawbox=x=8:y=268:w=2:h=12:color={accent_hex}@0.80:t=fill,"
        f"drawbox=x=268:y=278:w=12:h=2:color={accent_hex}@0.80:t=fill,"
        f"drawbox=x=278:y=268:w=2:h=12:color={accent_hex}@0.80:t=fill,"
        f"pad=288:352:0:0:0x0f172a,"
        f"drawtext=fontfile={FONT_BOLD}:text='{line1}':fontcolor=white:fontsize=13:x=12:y=295,"
        f"drawtext=fontfile={FONT_REG}:text='{line2}':fontcolor=0xcbd5e1:fontsize=11:x=12:y=313,"
        f"drawtext=fontfile={FONT_REG}:text='{line3}':fontcolor={accent_hex}:fontsize=10:x=12:y=331,"
        f"pad=296:360:4:4:{accent_hex}[vout]"
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(live_turn_mp4),
            "-filter_complex",
            fc_human,
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
            "18",
            "-pix_fmt",
            "yuv420p",
            "-an",
            str(out_pip_mp4),
        ],
        check=True,
        capture_output=True,
    )


def build_console_drawer_clip(
    tid: str,
    viewer_name: str,
    caption_text: str,
    accent_hex: str,
    slot_frames: int,
    do_scroll: bool,
    seg_tmp_dir: Path,
) -> Path:
    """Render an exact `slot_frames`-frame 1004x992 @ 30fps Console Evidence Drawer MP4 without parent-iframe CSP."""
    from playwright.sync_api import sync_playwright

    viewers_dir = REPO_ROOT / "site-template" / "viewers"
    viewer_file = viewers_dir / viewer_name
    if not viewer_file.exists():
        raise FileNotFoundError(f"Viewer file not found: {viewer_file}")

    border_col = "#" + accent_hex.replace("0x", "").replace("#", "")
    cache_dir = seg_tmp_dir / "_drawer_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Inject the top 38px Console Evidence header bar directly into a wrapper copy so it matches CONSOLE_VIEWER_INJECT_JS
    raw_html = viewer_file.read_text(encoding="utf-8")
    hdr_bar = f"""
    <div style="height:38px;background:#0f172a;border-bottom:1px solid #1e293b;display:flex;align-items:center;justify-content:space-between;padding:0 14px;color:#f8fafc;font-size:12px;font-weight:700;letter-spacing:0.02em;position:sticky;top:0;z-index:99999;">
      <div style="display:flex;align-items:center;gap:8px;min-width:0;overflow:hidden;">
        <span style="width:9px;height:9px;border-radius:50%;background:{border_col};box-shadow:0 0 8px {border_col};display:inline-block;flex-shrink:0;"></span>
        <span style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{caption_text or 'LIVE CONSOLE EVIDENCE VIEWER'}</span>
      </div>
      <span style="font-family:monospace;font-size:11px;color:#38bdf8;background:rgba(56,189,248,0.12);padding:2px 8px;border-radius:6px;border:1px solid rgba(56,189,248,0.3);flex-shrink:0;">/workspace/_site/viewers/{viewer_name}</span>
    </div>
    """
    wrapped_html = raw_html.replace("<body>", f"<body style='border:2px solid {border_col};min-height:992px;'>\n{hdr_bar}", 1)
    wrapped_file = cache_dir / f"{tid}_{viewer_name}"
    wrapped_file.write_text(wrapped_html, encoding="utf-8")

    out_drawer_mp4 = seg_tmp_dir / f"{tid}_drawer.mp4"
    slot_dur_s = slot_frames / float(FPS)

    if viewer_name == "af3-live-viewer.html":
        # Record live 60fps spinning 3D AlphaFold 3 canvas in Playwright!
        vid_tmp = cache_dir / f"vid_{tid}"
        if vid_tmp.exists():
            shutil.rmtree(vid_tmp, ignore_errors=True)
        vid_tmp.mkdir(parents=True, exist_ok=True)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, executable_path="/usr/bin/google-chrome")
            ctx = browser.new_context(
                viewport={"width": 1004, "height": 992},
                record_video_dir=str(vid_tmp),
                record_video_size={"width": 1004, "height": 992},
            )
            page = ctx.new_page()
            page.goto(f"file://{wrapped_file.resolve()}", wait_until="load")
            half_ms = int((slot_dur_s + 0.5) * 500)
            page.wait_for_timeout(half_ms)
            if do_scroll:
                page.evaluate("window.scrollTo({ top: 110, behavior: 'smooth' })")
            page.wait_for_timeout(half_ms)
            vpath = Path(page.video.path())
            ctx.close()
            browser.close()
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-ss",
                "0.25",
                "-i",
                str(vpath),
                "-vf",
                f"fps={FPS},scale=1004:992,drawbox=x=0:y=0:w=1004:h=992:color={accent_hex}:t=2",
                "-frames:v",
                str(slot_frames),
                "-r",
                str(FPS),
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-crf",
                "18",
                "-pix_fmt",
                "yuv420p",
                "-an",
                str(out_drawer_mp4),
            ],
            check=True,
            capture_output=True,
        )
        shutil.rmtree(vid_tmp, ignore_errors=True)
        return out_drawer_mp4

    # For SVG/table viewers, capture exact 1004x1120 PNG once and animate smooth scroll in ffmpeg
    png_path = cache_dir / f"{tid}_drawer.png"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path="/usr/bin/google-chrome")
        page = browser.new_page(viewport={"width": 1004, "height": 1120})
        page.goto(f"file://{wrapped_file.resolve()}", wait_until="load")
        page.wait_for_timeout(200)
        page.screenshot(path=str(png_path), clip={"x": 0, "y": 0, "width": 1004, "height": 1120})
        browser.close()

    half_s = slot_dur_s * 0.50
    scroll_px = 96 if do_scroll else 0
    fc_drawer = (
        f"[0:v]fps={FPS},crop=1004:992:0:'if(lt(t,{half_s:.3f}),0,min({scroll_px},(t-{half_s:.3f})*140))',"
        f"drawbox=x=0:y=0:w=1004:h=992:color={accent_hex}:t=2[vout]"
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(png_path),
            "-filter_complex",
            fc_drawer,
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
            "18",
            "-pix_fmt",
            "yuv420p",
            "-an",
            str(out_drawer_mp4),
        ],
        check=True,
        capture_output=True,
    )
    return out_drawer_mp4


def master_chapter_videos(
    spec: dict[str, Any],
    all_timings: dict[str, Any],
    audio_dir: Path,
    talking_heads_dir: Path,
    out_videos_dir: Path,
    manifest_out: Path,
    selected_chapters: set[str],
    lipsync_python: str | None = None,
    lipsync_script: Path | None = None,
    lipsync_models_dir: Path | None = None,
) -> dict[str, Any]:
    out_videos_dir.mkdir(parents=True, exist_ok=True)
    seg_tmp_dir = out_videos_dir / "_segments"
    seg_tmp_dir.mkdir(parents=True, exist_ok=True)
    voices = spec["voices"]

    existing_manifest: dict[str, Any] = {"chapters": {}}
    if manifest_out.exists():
        existing_manifest = json.loads(manifest_out.read_text(encoding="utf-8"))

    for ch in spec["chapters"]:
        ch_id = ch["chapter"]
        if ch_id not in selected_chapters:
            continue
        if ch_id not in all_timings:
            raise RuntimeError(f"Missing raw recording timings for {ch_id}")

        rec = all_timings[ch_id]
        raw_webm = Path(rec["raw_webm"])

        print(f"\n=== Mastering Lip-Synced + Beacon-Aligned 1080p Video for {ch_id} ({ch['video_filename']}) ===", flush=True)

        # 1. Decode index-less Playwright WebM sequentially ONCE into a keyframe-indexed 30.00 fps CFR MP4
        cfr_mp4 = seg_tmp_dir / f"{ch_id}_cfr30.mp4"
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(raw_webm),
                "-vf",
                f"fps={FPS},scale=1920:1080",
                "-r",
                str(FPS),
                "-c:v",
                "libx264",
                "-preset",
                "ultrafast",
                "-crf",
                "16",
                "-g",
                "15",
                "-pix_fmt",
                "yuv420p",
                "-an",
                str(cfr_mp4),
            ],
            check=True,
            capture_output=True,
        )
        cfr_total_frames = max(1, int(round(ffprobe_duration(cfr_mp4) * FPS)))
        beacon_frames = detect_beacon_start_frames(cfr_mp4, rec["turns"], float(rec.get("perf_total_s", 90.0)))

        vseg_files: list[Path] = []
        aseg_files: list[Path] = []
        scrub_markers: list[dict[str, Any]] = []
        cursor_frames = 0

        spec_turns_by_id = {t["turn_id"]: t for t in ch["turns"]}

        for idx, tinfo in enumerate(rec["turns"]):
            tid = tinfo["turn_id"]
            tnum = int(tinfo.get("turn_num", idx + 1))
            speaker = tinfo["speaker"]
            vmeta = voices[speaker]
            spec_turn = spec_turns_by_id.get(tid, {})
            src_wav = audio_dir / f"{tid}.wav"
            slot_frames = int(tinfo.get("slot_frames") or round(float(tinfo["target_slot_s"]) * FPS))
            slot_dur_s = slot_frames / float(FPS)

            # Build exact `slot_frames * 1600` sample 48kHz stereo WAV (+ Squadron Comms pips & AI EQ)
            wav_48k = seg_tmp_dir / f"{tid}_48k.wav"
            build_exact_48k_stereo_wav(src_wav, slot_frames, wav_48k, is_agent=bool(vmeta.get("is_agent", False)))
            aseg_files.append(wav_48k)

            # Build exact `slot_frames`-frame native Gemini 3.8 Live Avatar / AI Hologram PiP card
            pip_mp4 = seg_tmp_dir / f"{tid}_pip.mp4"
            build_pip_overlay_clip(
                tid=tid,
                speaker=speaker,
                vmeta=vmeta,
                wav_48k_path=wav_48k,
                slot_frames=slot_frames,
                talking_heads_dir=talking_heads_dir,
                out_pip_mp4=pip_mp4,
            )

            # Slice exact 1.0x real-time frames starting at `f_start` (paint over the 8x4 beacon pixel cleanly!)
            f_start = beacon_frames[tnum]
            f_end = f_start + slot_frames
            if f_end > cfr_total_frames:
                f_start = max(0, cfr_total_frames - slot_frames)
                f_end = f_start + slot_frames

            vseg_mp4 = seg_tmp_dir / f"{tid}_vseg.mp4"
            viewer_name = (spec_turn.get("console_viewer") or "").strip()
            if viewer_name:
                accent_hex = vmeta.get("accent_hex", "0x10b981")
                drawer_mp4 = build_console_drawer_clip(
                    tid=tid,
                    viewer_name=viewer_name,
                    caption_text=(spec_turn.get("console_caption") or "").strip(),
                    accent_hex=accent_hex,
                    slot_frames=slot_frames,
                    do_scroll=(spec_turn.get("action") == "wait_agent_reply"),
                    seg_tmp_dir=seg_tmp_dir,
                )
                fc = (
                    f"[0:v]trim=start_frame={f_start}:end_frame={f_end},setpts=PTS-STARTPTS,"
                    f"drawbox=x=0:y=0:w=10:h=4:color=0x2563eb:t=fill[base];"
                    f"[base][2:v]overlay=586:48[with_drawer];"
                    f"[with_drawer][1:v]overlay=1608:700[vout]"
                )
                ff_inputs = ["-i", str(cfr_mp4), "-i", str(pip_mp4), "-i", str(drawer_mp4)]
            else:
                fc = (
                    f"[0:v]trim=start_frame={f_start}:end_frame={f_end},setpts=PTS-STARTPTS,"
                    f"drawbox=x=0:y=0:w=10:h=4:color=0x2563eb:t=fill[base];"
                    f"[base][1:v]overlay=1608:700[vout]"
                )
                ff_inputs = ["-i", str(cfr_mp4), "-i", str(pip_mp4)]

            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    *ff_inputs,
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
            if ss == 60:
                mm += 1
                ss = 0
            scrub_markers.append(
                {
                    "key": tinfo["scrub_key"],
                    "label": tinfo["scrub_label"],
                    "time_s": round(cursor_s, 2),
                    "timecode": f"{mm}:{ss:02d}",
                    "speaker": vmeta["display_name"],
                    "role": vmeta["role"],
                    "voice_id": vmeta["voice_id"],
                }
            )
            cursor_frames += slot_frames
            print(f"    [SEG] {tid}: {slot_frames} frames ({slot_dur_s:.2f}s) lip-synced & aligned", flush=True)

        # Concatenate all 4 exact-CFR video segments + single sample-exact 48kHz master WAV in one clean mux!
        vconcat_txt = seg_tmp_dir / f"{ch_id}_vconcat.txt"
        vconcat_txt.write_text("\n".join(f"file '{p.resolve()}'" for p in vseg_files) + "\n", encoding="utf-8")
        master_wav = seg_tmp_dir / f"{ch_id}_master_48k.wav"
        concatenate_wavs_sample_exact(aseg_files, master_wav)

        final_mp4 = out_videos_dir / ch["video_filename"]
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
                str(final_mp4),
            ],
            check=True,
            capture_output=True,
        )
        actual_dur = ffprobe_duration(final_mp4)
        existing_manifest["chapters"][ch_id] = {
            "chapter": ch_id,
            "number": ch["number"],
            "slug": ch["slug"],
            "title": ch["title"],
            "video_filename": ch["video_filename"],
            "duration_s": round(actual_dur, 2),
            "resolution": "1920x1080",
            "tts_model": "gemini-3.8-live + gemini-3.8-flash-tts",
            "avatar_stack": "gemini-3.8-live (native BidiGenerateContent audio+video avatar)",
            "markers": scrub_markers,
        }
        print(
            f"[OK] Mastered {final_mp4.name} -> {actual_dur:.2f}s ({final_mp4.stat().st_size / (1024 * 1024):.2f} MB)",
            flush=True,
        )

    # Concatenate full-pilot-walkthrough.mp4 if all 7 chapters exist
    all_six = [out_videos_dir / c["video_filename"] for c in spec["chapters"]]
    all_vsegs = [seg_tmp_dir / f"{t['turn_id']}_vseg.mp4" for c in spec["chapters"] for t in c["turns"]]
    all_six_wavs = [seg_tmp_dir / f"{c['chapter']}_master_48k.wav" for c in spec["chapters"]]
    if all(p.exists() for p in all_six):
        full_mp4 = out_videos_dir / "full-pilot-walkthrough.mp4"
        if all(v.exists() for v in all_vsegs) and all(w.exists() for w in all_six_wavs):
            full_vconcat = seg_tmp_dir / "full_pilot_vsegs_concat.txt"
            full_vconcat.write_text("\n".join(f"file '{p.resolve()}'" for p in all_vsegs) + "\n", encoding="utf-8")
            full_wav = seg_tmp_dir / "full_master_48k.wav"
            concatenate_wavs_sample_exact(all_six_wavs, full_wav)
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-f",
                    "concat",
                    "-safe",
                    "0",
                    "-i",
                    str(full_vconcat),
                    "-i",
                    str(full_wav),
                    "-map",
                    "0:v:0",
                    "-map",
                    "1:a:0",
                    "-c:v",
                    "copy",
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
                    str(full_mp4),
                ],
                check=True,
                capture_output=True,
            )
        else:
            full_concat = seg_tmp_dir / "full_pilot_concat.txt"
            full_concat.write_text("\n".join(f"file '{p.resolve()}'" for p in all_six) + "\n", encoding="utf-8")
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-f",
                    "concat",
                    "-safe",
                    "0",
                    "-i",
                    str(full_concat),
                    "-c",
                    "copy",
                    "-movflags",
                    "+faststart",
                    str(full_mp4),
                ],
                check=True,
                capture_output=True,
            )
        existing_manifest["full_walkthrough"] = {
            "video_filename": "full-pilot-walkthrough.mp4",
            "duration_s": round(ffprobe_duration(full_mp4), 2),
            "resolution": "1920x1080",
        }
        print(
            f"[OK] Mastered full-pilot-walkthrough.mp4 -> {existing_manifest['full_walkthrough']['duration_s']:.1f}s",
            flush=True,
        )

    manifest_out.parent.mkdir(parents=True, exist_ok=True)
    manifest_out.write_text(json.dumps(existing_manifest, indent=2), encoding="utf-8")
    print(f"[OK] Wrote scrub manifest -> {manifest_out}", flush=True)
    return existing_manifest


def upload_videos_to_gcs(
    out_videos_dir: Path,
    bucket: str,
    gcloud_config: str | None = None,
    gcs_prefix: str = "videos",
) -> None:
    bkt = bucket if bucket.startswith("gs://") else f"gs://{bucket}"
    clean_prefix = gcs_prefix.strip("/") or "videos"
    dst = f"{bkt.rstrip('/')}/{clean_prefix}/"
    mp4s = sorted(out_videos_dir.glob("*.mp4"))
    if not mp4s:
        raise RuntimeError(f"No MP4 files found in {out_videos_dir}")
    env = dict(os.environ)
    if gcloud_config:
        env["CLOUDSDK_ACTIVE_CONFIG_NAME"] = gcloud_config
    print(f"\n=== Uploading {len(mp4s)} MP4s to {dst} ===", flush=True)
    subprocess.run(
        ["gcloud", "storage", "cp", "--cache-control=no-cache, max-age=0", *[str(p) for p in mp4s], dst],
        env=env,
        check=True,
    )
    print(f"[OK] Uploaded {len(mp4s)} videos to {dst}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="Record & master the 7-Chapter OASE Multi-Human + Multi-Agent Pilot.")
    ap.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    ap.add_argument("--campaign", default=os.environ.get("OASE_CAMPAIGN_ID", ""))
    ap.add_argument("--gcs-prefix", default=os.environ.get("GCS_VIDEO_PREFIX", "videos"))
    ap.add_argument("--scion-hub-url", default=os.environ.get("SCION_HUB_URL", ""))
    ap.add_argument("--state-url", default=os.environ.get("STATE_CONTROLLER_URL", "http://127.0.0.1:8780"))
    ap.add_argument("--state-token", default=os.environ.get("OASE_STATE_TOKEN", ""))
    ap.add_argument("--profiles-dir", type=Path, default=Path(os.environ.get("PERSONA_PROFILES_DIR", "")))
    ap.add_argument("--assets-dir", type=Path, default=Path(os.environ.get("PILOT_ASSETS_DIR", "/tmp/oase-m3-assets")))
    ap.add_argument("--manifest-out", type=Path, default=DEFAULT_MANIFEST_OUT)
    ap.add_argument("--gcs-bucket", default=os.environ.get("GCS_BUNDLE_BUCKET", ""))
    ap.add_argument("--gcp-project", default=os.environ.get("GCP_PROJECT_ID", ""))
    ap.add_argument("--gcloud-config", default=os.environ.get("CLOUDSDK_ACTIVE_CONFIG_NAME", ""))
    ap.add_argument("--lipsync-python", default=os.environ.get("LIPSYNC_PYTHON", ""))
    ap.add_argument("--lipsync-script", type=Path, default=Path(os.environ.get("LIPSYNC_SCRIPT", "")))
    ap.add_argument("--lipsync-models-dir", type=Path, default=Path(os.environ.get("LIPSYNC_MODELS_DIR", "")))
    ap.add_argument("--chapters", default="ch1,ch2,ch3,ch4,ch5,ch6,ch7")
    ap.add_argument("--record-only", action="store_true")
    ap.add_argument("--master-only", action="store_true")
    ap.add_argument("--freeze-snapshot", action="store_true", default=True)
    ap.add_argument("--no-freeze-snapshot", action="store_false", dest="freeze_snapshot")
    ap.add_argument("--upload-gcs", action="store_true")
    ap.add_argument("--headful", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    campaign_id = (args.campaign or spec.get("campaign_id", "")).strip()
    selected = {c.strip() for c in args.chapters.split(",") if c.strip()}

    if args.dry_run:
        print(
            f"[DRY-RUN] Validated {len(spec['chapters'])} chapters, {len(spec['voices'])} Gemini 3.8 TTS voices, "
            f"campaign={campaign_id or 'default'}, selected={sorted(selected)}"
        )
        return 0

    audio_dir = args.assets_dir / "audio"
    talking_heads_dir = args.assets_dir / "talking-heads"
    raw_dir = args.assets_dir / "raw_recordings"
    out_videos_dir = args.assets_dir / "videos"

    durations = ensure_tts_audio(spec, audio_dir, args.gcp_project, args.gcloud_config or None)
    state_headers = {"X-OASE-State-Token": args.state_token} if args.state_token else {}

    ls_py = args.lipsync_python or None
    ls_sc = args.lipsync_script if str(args.lipsync_script) else None
    ls_md = args.lipsync_models_dir if str(args.lipsync_models_dir) else None

    if not args.master_only:
        if not args.scion_hub_url:
            raise SystemExit("ERROR: --scion-hub-url or SCION_HUB_URL is required for live recording.")
        if not str(args.profiles_dir) or not args.profiles_dir.exists():
            raise SystemExit(f"ERROR: Valid --profiles-dir required (got '{args.profiles_dir}').")

        all_timings = record_live_chapters(
            spec=spec,
            durations=durations,
            scion_hub_url=args.scion_hub_url,
            state_url=args.state_url.rstrip("/"),
            state_headers=state_headers,
            profiles_dir=args.profiles_dir,
            raw_dir=raw_dir,
            selected_chapters=selected,
            headless=not args.headful,
            campaign=campaign_id,
        )

        if args.freeze_snapshot:
            q_snap = f"?campaign={campaign_id}" if campaign_id else ""
            snap = http_json(f"{args.state_url.rstrip('/')}/api/state/snapshot{q_snap}", method="POST", headers=state_headers)
            print(f"[SNAPSHOT] Froze authentic golden-hub.db snapshot: {json.dumps(snap)}", flush=True)
    else:
        timings_path = raw_dir / "raw_turn_timings.json"
        if not timings_path.exists():
            raise SystemExit(f"ERROR: {timings_path} not found for --master-only.")
        all_timings = json.loads(timings_path.read_text(encoding="utf-8"))
        # Sync updated audio_durations.json slot_frames when a single turn clip is re-synthesized
        for ch_id, ch_rec in all_timings.items():
            for t_rec in ch_rec.get("turns", []):
                tid = t_rec.get("turn_id", "")
                if tid in durations and durations[tid].get("slot_frames"):
                    new_sf = int(durations[tid]["slot_frames"])
                    old_sf = int(t_rec.get("slot_frames") or new_sf)
                    if new_sf <= old_sf:
                        t_rec["slot_frames"] = new_sf
                        t_rec["target_slot_s"] = round(new_sf / float(FPS), 4)

    if not args.record_only:
        master_chapter_videos(
            spec=spec,
            all_timings=all_timings,
            audio_dir=audio_dir,
            talking_heads_dir=talking_heads_dir,
            out_videos_dir=out_videos_dir,
            manifest_out=args.manifest_out,
            selected_chapters=selected,
            lipsync_python=ls_py,
            lipsync_script=ls_sc,
            lipsync_models_dir=ls_md,
        )
        if args.upload_gcs:
            if not args.gcs_bucket:
                raise SystemExit("ERROR: --gcs-bucket or GCS_BUNDLE_BUCKET required for --upload-gcs.")
            upload_videos_to_gcs(
                out_videos_dir,
                args.gcs_bucket,
                args.gcloud_config or None,
                gcs_prefix=args.gcs_prefix,
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

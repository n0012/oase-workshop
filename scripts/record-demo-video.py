#!/usr/bin/env python3
"""Repeatable 8-Scene (3-Act) GCP-OASE & Scion Demo Video Generator (Gemini TTS Charon + Smooth Playwright + FFmpeg).

Usage:
  python3 scripts/record-demo-video.py \
    --portal-url http://127.0.0.1:8765 \
    --work-dir /tmp/oase-video-build \
    --quota-project my-oase-workshop

Pronunciation & Pacing Rules Codified:
  1. Uses native Vertex Gemini TTS (`gemini-2.5-flash-tts`, voice `Charon`) at 24kHz PCM,
     transcoded to 44.1kHz stereo MP3.
  2. First mention of OASE is spoken as "O-A-S-E" and referred to as "the Science Engine" thereafter.
  3. Phonetic guidance in narration text ensures natural pronunciation of Elo ("Ee-low"),
     gnomAD ("Nomad"), ADMET ("AD-met"), and hERG ("hurg").
  4. Smooth, simple screen motion: each scene divides its exact audio duration into 3 calm,
     linear top-to-bottom steps (~8-10s per step) with a slow 2.2s cubic-bezier glide, fixed
     horizontal alignment (no left-right zig-zagging), and a subtle 3px top progress bar.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import subprocess
import time
import urllib.request
import wave
from pathlib import Path

SMOOTH_UI_JS = """
(durMs) => {
  if (!document.getElementById('oase-smooth-style')) {
    const style = document.createElement('style');
    style.id = 'oase-smooth-style';
    style.textContent = `
      #oase-demo-cursor {
        position: fixed;
        width: 18px;
        height: 18px;
        border-radius: 50%;
        background: rgba(37, 99, 235, 0.22);
        border: 2px solid rgba(37, 99, 235, 0.75);
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.45);
        pointer-events: none;
        z-index: 999999;
        transition: top 2.2s cubic-bezier(0.25, 0.1, 0.25, 1), left 2.2s cubic-bezier(0.25, 0.1, 0.25, 1);
        left: 520px;
        top: 260px;
      }
      #oase-scene-progress {
        position: fixed;
        top: 0;
        left: 0;
        height: 3px;
        background: linear-gradient(90deg, #2563eb, #38bdf8);
        z-index: 1000000;
        width: 0%;
        pointer-events: none;
      }
      .oase-demo-focus {
        outline: 2px solid rgba(56, 189, 248, 0.75) !important;
        outline-offset: 4px !important;
        transition: outline 0.6s ease !important;
      }
    `;
    document.head.appendChild(style);
  }
  if (!document.getElementById('oase-demo-cursor')) {
    const cur = document.createElement('div');
    cur.id = 'oase-demo-cursor';
    document.body.appendChild(cur);
  }
  let bar = document.getElementById('oase-scene-progress');
  if (!bar) {
    bar = document.createElement('div');
    bar.id = 'oase-scene-progress';
    document.body.appendChild(bar);
  }
  if (durMs && durMs > 0) {
    bar.style.transition = 'none';
    bar.style.width = '0%';
    void bar.offsetWidth;
    bar.style.transition = `width ${durMs}ms linear`;
    bar.style.width = '100%';
  }
}
"""

GLIDE_TO_JS = """
(arg) => {
  const cur = document.getElementById('oase-demo-cursor');
  document.querySelectorAll('.oase-demo-focus').forEach(el => el.classList.remove('oase-demo-focus'));
  if (arg.sel) {
    const els = document.querySelectorAll(arg.sel);
    const el = els[arg.idx || 0];
    if (el) {
      el.scrollIntoView({behavior: 'smooth', block: 'center'});
      el.classList.add('oase-demo-focus');
      const r = el.getBoundingClientRect();
      if (cur) {
        const targetX = arg.x || 520;
        const targetY = Math.max(120, Math.min(920, Math.round(r.top + Math.min(r.height * 0.45, 220))));
        cur.style.left = targetX + 'px';
        cur.style.top = targetY + 'px';
      }
      return;
    }
  }
  if (typeof arg.scrollY === 'number') {
    window.scrollTo({top: arg.scrollY, behavior: 'smooth'});
  }
  if (cur && arg.y) {
    cur.style.left = (arg.x || 520) + 'px';
    cur.style.top = arg.y + 'px';
  }
}
"""


def get_bearer_token(credentials_path: str | None) -> str:
    if credentials_path and Path(credentials_path).is_file():
        from google.auth.transport.requests import Request
        from google.oauth2 import service_account

        creds = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        creds.refresh(Request())
        return str(creds.token)
    out = subprocess.check_output(
        ["gcloud", "auth", "print-access-token"], text=True
    ).strip()
    return out


def synthesize_gemini_tts_scenes(
    manifest_path: Path,
    audio_dir: Path,
    quota_project: str,
    voice_name: str = "Charon",
    model_name: str = "gemini-3.8-flash-tts",
    location: str = "global",
    credentials_path: str | None = None,
) -> dict:
    audio_dir.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    token = get_bearer_token(credentials_path)
    host = (
        "aiplatform.googleapis.com"
        if location == "global"
        else f"{location}-aiplatform.googleapis.com"
    )
    api_ver = "v1beta1" if "3.8" in model_name or location == "global" else "v1"
    url = (
        f"https://{host}/{api_ver}/projects/{quota_project}"
        f"/locations/{location}/publishers/google/models/{model_name}:generateContent"
    )
    is_custom_voice = voice_name.startswith(("voice_", "voicekey_"))

    for scene in manifest["scenes"]:
        num = scene["number"]
        script = scene.get("tts_script") or scene["voiceover"]
        text_input = (
            script
            if "3.8" in model_name
            else (
                "Read the following narration script verbatim in a calm, smooth, authoritative "
                "technical presenter voice. Speak at a steady, natural pace. Output only the spoken script:\n\n"
                f"{script}"
            )
        )
        voice_cfg = (
            {"voice": voice_name}
            if is_custom_voice or "3.8" in model_name
            else {"prebuiltVoiceConfig": {"voiceName": voice_name}}
        )
        body = {
            "contents": [{"role": "user", "parts": [{"text": text_input}]}],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {"voiceConfig": voice_cfg},
            },
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "x-goog-user-project": quota_project,
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=90) as resp:
            res = json.loads(resp.read().decode("utf-8"))
        pcm_bytes = b""
        mime_type = ""
        for cand in res.get("candidates", []):
            for part in cand.get("content", {}).get("parts", []):
                inl = part.get("inlineData")
                if inl and inl.get("data"):
                    pcm_bytes += base64.b64decode(inl["data"])
                    mime_type = inl.get("mimeType", "")

        wav_file = audio_dir / f"scene-{num:02d}.wav"
        if "wav" in mime_type or pcm_bytes[:4] == b"RIFF":
            wav_file.write_bytes(pcm_bytes)
        else:
            with wave.open(str(wav_file), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(24000)
                wf.writeframes(pcm_bytes)

        out_file = audio_dir / f"scene-{num:02d}.mp3"
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(wav_file),
                "-ar",
                "44100",
                "-ac",
                "2",
                "-c:a",
                "libmp3lame",
                "-b:a",
                "192k",
                str(out_file),
            ],
            check=True,
            capture_output=True,
        )
        probe = subprocess.run(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(out_file),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        dur_ms = int(float(probe.stdout.strip()) * 1000)
        scene["audio_path"] = str(out_file)
        scene["audio_duration_ms"] = dur_ms
        scene["tts_model"] = model_name
        scene["tts_voice"] = voice_name
        print(f"✓ Gemini TTS ({voice_name}) Scene {num}: {dur_ms/1000:.1f}s -> {out_file.name}")

    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def record_portal_scenes(
    manifest: dict, portal_url: str, work_dir: Path
) -> Path:
    from playwright.sync_api import sync_playwright

    raw_video_dir = work_dir / "raw_video"
    if raw_video_dir.exists():
        shutil.rmtree(raw_video_dir)
    raw_video_dir.mkdir(parents=True, exist_ok=True)

    audio_dur_ms = {
        s["number"]: int(s.get("audio_duration_ms") or 28000)
        for s in manifest["scenes"]
    }
    scenes_out = []

    with sync_playwright() as p:
        chrome_bin = next(
            (
                c
                for c in [
                    "/usr/bin/google-chrome",
                    "/usr/bin/chromium",
                    "/usr/bin/chromium-browser",
                ]
                if Path(c).exists()
            ),
            None,
        )
        browser = p.chromium.launch(headless=True, executable_path=chrome_bin)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=str(raw_video_dir),
            record_video_size={"width": 1920, "height": 1080},
        )
        page = context.new_page()
        t0 = time.monotonic()

        def at_ms() -> int:
            return int((time.monotonic() - t0) * 1000)

        def run_calm_scene(num: int, title: str, steps: list[dict]):
            start = at_ms()
            target_ms = audio_dur_ms[num] + 250
            step_count = len(steps)
            step_budget = target_ms // step_count

            for i, st in enumerate(steps):
                step_start = at_ms()
                if "goto" in st:
                    page.goto(st["goto"], wait_until="networkidle")
                    rem_dur = max(1000, (start + target_ms) - at_ms())
                    page.evaluate(SMOOTH_UI_JS, rem_dur)
                if "click" in st:
                    page.click(st["click"])
                    page.wait_for_load_state("networkidle")
                    rem_dur = max(1000, (start + target_ms) - at_ms())
                    page.evaluate(SMOOTH_UI_JS, rem_dur)
                if i == 0 and "goto" not in st and "click" not in st:
                    page.evaluate(SMOOTH_UI_JS, target_ms)

                page.evaluate(
                    GLIDE_TO_JS,
                    {
                        "sel": st.get("sel"),
                        "idx": st.get("idx", 0),
                        "x": st.get("x", 520),
                        "y": st.get("y"),
                        "scrollY": st.get("scrollY"),
                    },
                )
                if i < step_count - 1:
                    elapsed_step = at_ms() - step_start
                    wait_ms = max(400, step_budget - elapsed_step)
                    page.wait_for_timeout(wait_ms)
                else:
                    rem_total = (start + target_ms) - at_ms()
                    if rem_total > 0:
                        page.wait_for_timeout(rem_total)

            end = at_ms()
            scenes_out.append(
                {"number": num, "title": title, "start_ms": start, "end_ms": end}
            )

        page.goto(f"{portal_url}/chapters.html#why", wait_until="networkidle")
        page.wait_for_timeout(300)

        run_calm_scene(
            1,
            "Why Single-Player Chatbot Science Fails Governance",
            [
                {"click": "#btn-why", "sel": "#plate-challenges", "idx": 0, "x": 520},
                {"sel": "#why-row-1", "idx": 0, "x": 520},
                {"sel": "#plate-thumb", "idx": 0, "x": 520},
            ],
        )

        run_calm_scene(
            2,
            "Scion + OASE Value Proposition & Multi-Model Projects",
            [
                {"click": "#btn-scion", "sel": "#plate-benefits", "idx": 0, "x": 520},
                {"sel": "#scion-card-1", "idx": 0, "x": 520},
                {"sel": "#scion-card-3", "idx": 0, "x": 520},
            ],
        )

        run_calm_scene(
            3,
            "4-Tier Agent Roster, 9-State Work Orders & Two-Phase Latch",
            [
                {"sel": "#plate-arch", "idx": 0, "x": 520},
                {"sel": "#arch-row-1", "idx": 0, "x": 520},
                {"sel": "#scion-card-4", "idx": 0, "x": 520},
            ],
        )

        run_calm_scene(
            4,
            "Stages 0-1: Hypothesis Tournament & Human Genetics (WO-001..003)",
            [
                {"click": "#btn-ch1", "sel": "#panel-ch1 table", "idx": 0, "x": 520},
                {"click": "#btn-ch2", "sel": "#panel-ch2 table", "idx": 0, "x": 520},
                {
                    "click": "a[href='finding_findings_computational-biology_WO-002_md.html']",
                    "sel": "main, body",
                    "idx": 0,
                    "x": 520,
                    "scrollY": 160,
                },
            ],
        )

        run_calm_scene(
            5,
            "Stages 2-4: Allosteric Co-Folding & Catching the hERG Trap (WO-004..007)",
            [
                {
                    "goto": f"{portal_url}/chapters.html#ch3",
                    "click": "#btn-ch3",
                    "sel": "#panel-ch3 table",
                    "idx": 0,
                    "x": 520,
                },
                {"click": "#btn-ch4", "sel": "#panel-ch4 table", "idx": 0, "x": 520},
                {
                    "click": "a[href='finding_findings_medicinal-chemistry_WO-006_md.html']",
                    "sel": "main, body",
                    "idx": 0,
                    "x": 520,
                    "scrollY": 160,
                },
            ],
        )

        run_calm_scene(
            6,
            "Mechanical Governance Teeth: 4 Adversarial Tamper Drills",
            [
                {
                    "goto": f"{portal_url}/chapters.html#ch5",
                    "click": "#btn-ch5",
                    "sel": "#panel-ch5 table",
                    "idx": 0,
                    "x": 520,
                },
                {"sel": "#panel-ch5 .terminal", "idx": 0, "x": 520},
                {
                    "click": "a[href='workorder_WO-005_r1.html']",
                    "sel": "main, body",
                    "idx": 0,
                    "x": 520,
                    "scrollY": 160,
                },
            ],
        )

        run_calm_scene(
            7,
            "The Complete Picture & 31-Page Stage-Gate Dossier (WO-008)",
            [
                {
                    "goto": f"{portal_url}/chapters.html#ch6",
                    "click": "#btn-ch6",
                    "sel": "#plate-complete",
                    "idx": 0,
                    "x": 520,
                },
                {
                    "goto": f"{portal_url}/index.html",
                    "sel": "table, ul",
                    "idx": 0,
                    "x": 520,
                    "scrollY": 140,
                },
                {
                    "goto": f"{portal_url}/finding_findings_regulatory_WO-008_md.html",
                    "sel": "main, body",
                    "idx": 0,
                    "x": 520,
                    "scrollY": 160,
                },
            ],
        )

        run_calm_scene(
            8,
            "Architecture Scorecard & Field Takeaways",
            [
                {
                    "goto": f"{portal_url}/chapters.html#ch6",
                    "click": "#btn-ch6",
                    "sel": "#score-row-1",
                    "idx": 0,
                    "x": 520,
                },
                {"sel": "#score-row-3", "idx": 0, "x": 520},
                {"sel": "#plate-complete", "idx": 0, "x": 520},
            ],
        )

        video_obj = page.video
        page.close()
        context.close()
        webm_dest = work_dir / "recording.webm"
        video_obj.save_as(str(webm_dest))
        browser.close()

    times_path = work_dir / "scene-times.json"
    times_path.write_text(
        json.dumps({"video": str(webm_dest), "scenes": scenes_out}, indent=2),
        encoding="utf-8",
    )
    return times_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--portal-url",
        default="http://127.0.0.1:8765",
        help="Running Evidence Portal base URL",
    )
    parser.add_argument(
        "--work-dir",
        default="/tmp/oase-video-build",
        help="Scratch build directory for TTS MP3s and Playwright clips",
    )
    parser.add_argument(
        "--quota-project",
        default=os.environ.get("GOOGLE_CLOUD_PROJECT", "gcp-oase-workshop"),
        help="GCP project with Vertex AI API enabled",
    )
    parser.add_argument(
        "--voice",
        default="Charon",
        help="Gemini TTS prebuilt voice name (default: Charon)",
    )
    parser.add_argument(
        "--credentials",
        default=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
        help="Optional service account JSON path",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    work_dir = Path(args.work_dir).resolve()
    work_dir.mkdir(parents=True, exist_ok=True)
    manifest_dst = work_dir / "scenes.json"
    shutil.copy2(repo_root / "docs" / "video-scenes.json", manifest_dst)

    manifest = synthesize_gemini_tts_scenes(
        manifest_dst,
        work_dir / "audio",
        args.quota_project,
        voice_name=args.voice,
        credentials_path=args.credentials,
    )
    times_path = record_portal_scenes(manifest, args.portal_url, work_dir)
    print(f"✓ Recorded scenes and timings to {times_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

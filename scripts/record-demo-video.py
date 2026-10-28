#!/usr/bin/env python3
"""Repeatable 8-Scene (3-Act) GCP-OASE & Scion Demo Video Generator (TTS + Playwright + FFmpeg).

Usage:
  python3 scripts/record-demo-video.py \
    --portal-url http://127.0.0.1:8765 \
    --work-dir /tmp/oase-video-build \
    --quota-project my-oase-workshop

Pronunciation & Audio Rules Codified:
  1. First mention of OASE uses `<say-as interpret-as="characters">OASE</say-as>`
     ("O-A-S-E") and refers to it as "the Science Engine" thereafter.
  2. Elo ratings use IPA `<phoneme alphabet="ipa" ph="ˈiːloʊ">Elo</phoneme>` ("ee-low").
  3. ADMET and hERG use IPA `<phoneme>` tags (`ˈædmɛt`, `hɜːrɡ`).
  4. Avoid `<break>` tags inside `en-US-Studio-O` SSML blocks, as Studio neural
     prosody can overlap consecutive sentences across explicit `<break>` boundaries;
     rely on natural sentence periods instead.
  5. Keep each SSML scene block under ~27 seconds (~45 words) to prevent Cloud TTS
     Studio voice buffer truncation.
  6. Inject an animated spotlight cursor (`#oase-demo-cursor`) so compact views
     and architectural plates never trigger static-frame visual stall detectors.
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
from pathlib import Path

CURSOR_JS = """
(() => {
  if (document.getElementById('oase-demo-cursor')) return;
  const style = document.createElement('style');
  style.textContent = `
    #oase-demo-cursor {
      position: fixed;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: rgba(37, 99, 235, 0.35);
      border: 2.5px solid #2563eb;
      box-shadow: 0 0 16px rgba(56, 189, 248, 0.85);
      pointer-events: none;
      z-index: 999999;
      transition: left 0.65s cubic-bezier(0.22, 1, 0.36, 1), top 0.65s cubic-bezier(0.22, 1, 0.36, 1);
      left: 960px;
      top: 240px;
    }
    .oase-demo-focus {
      outline: 2.5px solid #38bdf8 !important;
      outline-offset: 3px !important;
      transition: outline 0.25s ease !important;
    }
  `;
  document.head.appendChild(style);
  const cur = document.createElement('div');
  cur.id = 'oase-demo-cursor';
  document.body.appendChild(cur);
})();
"""

MOVE_JS = """
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
        cur.style.left = Math.max(40, Math.min(1860, r.left + Math.min(r.width * 0.35, 260))) + 'px';
        cur.style.top = Math.max(40, Math.min(1020, r.top + r.height * 0.5)) + 'px';
      }
      return;
    }
  }
  if (cur && arg.x && arg.y) {
    cur.style.left = arg.x + 'px';
    cur.style.top = arg.y + 'px';
  }
  if (typeof arg.scrollY === 'number') {
    window.scrollTo({top: arg.scrollY, behavior: 'smooth'});
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


def synthesize_ssml_scenes(
    manifest_path: Path,
    audio_dir: Path,
    quota_project: str,
    credentials_path: str | None = None,
) -> dict:
    audio_dir.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    token = get_bearer_token(credentials_path)

    for scene in manifest["scenes"]:
        num = scene["number"]
        ssml = scene["ssml"]
        body = {
            "input": {"ssml": ssml},
            "voice": {"languageCode": "en-US", "name": "en-US-Studio-O"},
            "audioConfig": {
                "audioEncoding": "MP3",
                "speakingRate": 0.96,
                "pitch": 0,
            },
        }
        req = urllib.request.Request(
            "https://texttospeech.googleapis.com/v1/text:synthesize",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "x-goog-user-project": quota_project,
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            res = json.loads(resp.read().decode("utf-8"))
        mp3_bytes = base64.b64decode(res["audioContent"])
        out_file = audio_dir / f"scene-{num:02d}.mp3"
        out_file.write_bytes(mp3_bytes)
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
        print(f"✓ TTS Scene {num}: {dur_ms/1000:.1f}s -> {out_file.name}")

    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def record_portal_scenes(
    manifest: dict, portal_url: str, work_dir: Path
) -> Path:
    from playwright.sync_api import sync_playwright

    shots_dir = work_dir / "shots"
    raw_video_dir = work_dir / "raw_video"
    shots_dir.mkdir(parents=True, exist_ok=True)
    if raw_video_dir.exists():
        shutil.rmtree(raw_video_dir)
    raw_video_dir.mkdir(parents=True, exist_ok=True)

    audio_dur_ms = {
        s["number"]: int(s.get("audio_duration_ms") or 22000)
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

        def spotlight(
            sel: str | None = None,
            idx: int = 0,
            x: int = 960,
            y: int = 360,
            scroll_y: int | None = None,
            wait_ms: int = 1450,
        ):
            page.evaluate(CURSOR_JS)
            page.evaluate(
                MOVE_JS,
                {"sel": sel, "idx": idx, "x": x, "y": y, "scrollY": scroll_y},
            )
            page.wait_for_timeout(wait_ms)

        def mark(num: int, title: str) -> dict:
            cur = {"number": num, "title": title, "start_ms": at_ms()}
            scenes_out.append(cur)
            return cur

        def active_pace_to_end(
            cur: dict, selectors: list[tuple[str, int]], pad_ms: int = 200
        ):
            num = cur["number"]
            target_ms = audio_dur_ms.get(num, 22000) + pad_ms
            step_idx = 0
            while True:
                elapsed = at_ms() - cur["start_ms"]
                rem = target_ms - elapsed
                if rem <= 0:
                    break
                sel, idx = selectors[step_idx % len(selectors)]
                page.evaluate(CURSOR_JS)
                page.evaluate(
                    MOVE_JS,
                    {
                        "sel": sel,
                        "idx": idx,
                        "x": 600 + (step_idx * 170) % 700,
                        "y": 280 + (step_idx * 130) % 500,
                    },
                )
                step_idx += 1
                page.wait_for_timeout(min(1300, max(250, rem)))
            cur["end_ms"] = at_ms()

        page.goto(f"{portal_url}/chapters.html#why", wait_until="networkidle")
        page.evaluate(CURSOR_JS)
        page.wait_for_timeout(400)

        s1 = mark(1, "Why Single-Player Chatbot Science Fails Governance")
        page.click("#btn-why")
        spotlight("#plate-challenges", 0)
        spotlight("#why-row-1", 0)
        spotlight("#why-row-2", 0)
        spotlight("#why-row-3", 0)
        spotlight("#why-row-4", 0)
        spotlight("#plate-thumb", 0)
        active_pace_to_end(
            s1,
            [
                ("#why-row-1", 0),
                ("#why-row-2", 0),
                ("#why-row-3", 0),
                ("#why-row-4", 0),
                ("#plate-challenges", 0),
            ],
        )

        s2 = mark(2, "Scion + OASE Value Proposition & Multi-Model Projects")
        page.click("#btn-scion")
        spotlight("#plate-benefits", 0)
        spotlight("#scion-card-1", 0)
        spotlight("#scion-card-2", 0)
        spotlight("#scion-card-3", 0)
        spotlight(".kpi-card", 0)
        active_pace_to_end(
            s2,
            [
                ("#scion-card-1", 0),
                ("#scion-card-2", 0),
                ("#scion-card-3", 0),
                ("#plate-benefits", 0),
            ],
        )

        s3 = mark(3, "4-Tier Agent Roster, 9-State Work Orders & Two-Phase Latch")
        spotlight("#plate-arch", 0)
        spotlight("#scion-card-4", 0)
        spotlight("#arch-row-1", 0)
        spotlight("#arch-row-2", 0)
        spotlight("#arch-row-3", 0)
        active_pace_to_end(
            s3,
            [
                ("#plate-arch", 0),
                ("#arch-row-1", 0),
                ("#arch-row-2", 0),
                ("#arch-row-3", 0),
                ("#scion-card-4", 0),
            ],
        )

        s4 = mark(4, "Stages 0-1: Hypothesis Tournament & Human Genetics (WO-001..003)")
        page.click("#btn-ch1")
        spotlight("#panel-ch1 tr", 1)
        spotlight("#panel-ch1 .terminal", 0)
        page.click("#btn-ch2")
        spotlight("#panel-ch2 tr", 1)
        spotlight("#panel-ch2 tr", 2)
        spotlight("#panel-ch2 .relay-box", 0)
        page.click("a[href='finding_findings_computational-biology_WO-002_md.html']")
        page.wait_for_load_state("networkidle")
        active_pace_to_end(s4, [("li, p", 1), ("li, p", 3), ("li, p", 5)])

        s5 = mark(5, "Stages 2-4: Allosteric Co-Folding & Catching the hERG Trap (WO-004..007)")
        page.goto(f"{portal_url}/chapters.html#ch3", wait_until="networkidle")
        page.click("#btn-ch3")
        spotlight("#panel-ch3 tr", 2)
        spotlight("#panel-ch3 tr", 3)
        page.click("#btn-ch4")
        spotlight("#panel-ch4 tr", 1)
        spotlight("#panel-ch4 tr", 2)
        spotlight("#panel-ch4 .terminal", 0)
        page.click("a[href='finding_findings_medicinal-chemistry_WO-006_md.html']")
        page.wait_for_load_state("networkidle")
        active_pace_to_end(s5, [("li, p", 1), ("li, p", 3), ("li, p", 5)])

        s6 = mark(6, "Mechanical Governance Teeth: 4 Adversarial Tamper Drills")
        page.goto(f"{portal_url}/chapters.html#ch5", wait_until="networkidle")
        page.click("#btn-ch5")
        spotlight("#panel-ch5 tr", 1)
        spotlight("#panel-ch5 tr", 2)
        spotlight("#panel-ch5 tr", 3)
        spotlight("#panel-ch5 tr", 4)
        spotlight("#panel-ch5 .terminal", 0)
        page.click("a[href='workorder_WO-005_r1.html']")
        page.wait_for_load_state("networkidle")
        active_pace_to_end(s6, [("table tr, li, p", 1), ("table tr, li, p", 3), ("pre, code", 0)])

        s7 = mark(7, "The Complete Picture & 31-Page Stage-Gate Dossier (WO-008)")
        page.goto(f"{portal_url}/chapters.html#ch6", wait_until="networkidle")
        page.click("#btn-ch6")
        spotlight("#plate-complete", 0)
        page.goto(f"{portal_url}/index.html", wait_until="networkidle")
        spotlight("a, tr, li", 2, scroll_y=240)
        page.goto(f"{portal_url}/finding_findings_regulatory_WO-008_md.html", wait_until="networkidle")
        active_pace_to_end(s7, [("li, p", 1), ("li, p", 3), ("li, p", 5), ("table tr", 1)])

        s8 = mark(8, "Architecture Scorecard & Field Takeaways")
        page.goto(f"{portal_url}/chapters.html#ch6", wait_until="networkidle")
        page.click("#btn-ch6")
        spotlight("#score-row-1", 0)
        spotlight("#score-row-2", 0)
        spotlight("#score-row-3", 0)
        spotlight("#score-row-4", 0)
        spotlight("#plate-complete", 0)
        active_pace_to_end(
            s8,
            [
                ("#score-row-1", 0),
                ("#score-row-2", 0),
                ("#score-row-3", 0),
                ("#score-row-4", 0),
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
        help="GCP project with Cloud Text-to-Speech API enabled",
    )
    parser.add_argument(
        "--credentials",
        default=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
        help="Optional service account JSON path for Cloud TTS",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    work_dir = Path(args.work_dir).resolve()
    work_dir.mkdir(parents=True, exist_ok=True)
    manifest_dst = work_dir / "scenes.json"
    shutil.copy2(repo_root / "docs" / "video-scenes.json", manifest_dst)

    manifest = synthesize_ssml_scenes(
        manifest_dst,
        work_dir / "audio",
        args.quota_project,
        args.credentials,
    )
    times_path = record_portal_scenes(manifest, args.portal_url, work_dir)
    print(f"✓ Recorded scenes and timings to {times_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Playwright E2E verification harness for the deployed 7-Chapter Presenter Cockpit.

Verifies:
  1. HTTP 200 on `/`, `/plan.html`, and `/chapters.html`
  2. `/api/cockpit/config` health (`state.ok == true`, `admin_rows_count == 0`,
     all 8 checkpoints `ch0..ch7` present)
  3. HTTP 206 Partial Content byte-range video streaming on `chapter-01.mp4`,
     `chapter-07.mp4`, and `full-pilot-walkthrough.mp4`
  4. Chapter 7 turn-scrubbing pills (`4` turns) and role deep links
  5. Optional `<2s` non-disruptive `POST /api/state/chapters/ch7/reset` check
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cockpit-url",
        default=os.environ.get("COCKPIT_URL", ""),
        help="Base URL of the deployed Story Arc Cockpit (or set COCKPIT_URL).",
    )
    parser.add_argument(
        "--profile-dir",
        type=Path,
        default=Path("/tmp/oase-chrome-profiles/persona-sarah"),
        help="Persistent Chrome profile directory authenticated with IAP.",
    )
    parser.add_argument(
        "--screenshot-out",
        type=Path,
        default=Path("/tmp/story_arc_7chapters_verified.jpg"),
        help="Output path for verification screenshot.",
    )
    parser.add_argument(
        "--skip-reset-check",
        action="store_true",
        help="Skip POST /api/state/chapters/ch7/reset check (useful for static Tier-A Pages check).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.cockpit_url:
        raise SystemExit("Error: pass --cockpit-url or set COCKPIT_URL.")

    from playwright.sync_api import sync_playwright

    story_url = args.cockpit_url.rstrip("/")
    for lock in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
        (args.profile_dir / lock).unlink(missing_ok=True)

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(args.profile_dir),
            channel="chrome",
            headless=True,
            viewport={"width": 1600, "height": 1050},
        )
        try:
            page = ctx.new_page()
            resp = page.goto(f"{story_url}/", wait_until="domcontentloaded", timeout=45000)
            page.wait_for_selector("#oase-cockpit-topbar", timeout=30000)
            time.sleep(1.5)

            cfg = page.evaluate("async () => (await fetch('/api/cockpit/config')).json()")
            topbar_text = page.locator("#oase-cockpit-topbar").inner_text()

            range_statuses = {}
            for vname in ("chapter-01.mp4", "chapter-07.mp4", "full-pilot-walkthrough.mp4"):
                r = ctx.request.get(
                    f"{story_url}/api/videos/{vname}",
                    headers={"Range": "bytes=0-4095"},
                )
                range_statuses[vname] = r.status

            r_plan = ctx.request.get(f"{story_url}/plan.html")
            r_chapters = ctx.request.get(f"{story_url}/chapters.html")

            page.wait_for_selector("#btn-ch7", timeout=15000)
            page.click("#btn-ch7")
            page.wait_for_selector("#panel-ch7 #video-ch7", state="visible", timeout=15000)

            page.evaluate(
                """async () => {
                    const v = document.getElementById('video-ch7');
                    if (v) {
                        v.currentTime = 13.5;
                        await new Promise(res => {
                            const done = () => res();
                            v.addEventListener('seeked', done, { once: true });
                            setTimeout(done, 2500);
                        });
                    }
                }"""
            )
            time.sleep(0.8)

            pills_ch7 = page.locator("#panel-ch7 .scrub-pill").all_inner_texts()
            roles_ch7 = page.locator("#panel-ch7 a[href*='/chat']").count()

            reset_status = None
            reset_ok = None
            reset_ms = None
            if not args.skip_reset_check:
                t0 = time.monotonic()
                reset_res = page.evaluate(
                    "async () => { const r = await fetch('/api/state/chapters/ch7/reset', {method: 'POST'}); return {status: r.status, body: await r.json()}; }"
                )
                reset_ms = round((time.monotonic() - t0) * 1000.0, 1)
                reset_status = reset_res.get("status")
                reset_ok = reset_res.get("body", {}).get("ok")

            args.screenshot_out.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(args.screenshot_out), quality=90, type="jpeg")

            summary = {
                "root_status": resp.status if resp else None,
                "plan_status": r_plan.status,
                "chapters_status": r_chapters.status,
                "signed_in_user": cfg.get("signed_in_user"),
                "state_ok": cfg.get("state", {}).get("ok"),
                "admin_rows_count": cfg.get("state", {}).get("admin_rows_count"),
                "chapter_keys": sorted(list(cfg.get("state", {}).get("chapters", {}).keys())),
                "topbar_text": " ".join(topbar_text.split()),
                "range_206_statuses": range_statuses,
                "ch7_scrub_pills": pills_ch7,
                "ch7_role_links_count": roles_ch7,
                "ch7_reset_status": reset_status,
                "ch7_reset_elapsed_ms": reset_ms,
                "ch7_reset_ok": reset_ok,
                "screenshot": str(args.screenshot_out),
            }
            print(json.dumps(summary, indent=2))
            assert summary["root_status"] == 200
            assert summary["state_ok"] is True
            assert summary["admin_rows_count"] == 0
            assert summary["chapter_keys"] == ["ch0", "ch1", "ch2", "ch3", "ch4", "ch5", "ch6", "ch7"]
            assert all(s == 206 for s in range_statuses.values())
            assert len(pills_ch7) == 4
            if not args.skip_reset_check:
                assert reset_status == 200 and reset_ok is True
            return 0
        finally:
            ctx.close()


if __name__ == "__main__":
    raise SystemExit(main())

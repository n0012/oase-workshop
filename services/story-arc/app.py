#!/usr/bin/env python3
"""Standalone OASE Story Arc Presenter Cockpit & Video Streaming Service (M4).

Cloud Run FastAPI application deployed behind Google Cloud Identity-Aware Proxy
(IAP) with Direct VPC Egress to `oase-state-controller` (:8780):
  1. Top Story Arc Navigation (`Overview & 4 Pillars` -> `Ch 1`..`Ch 7` + `Build Plan`)
  2. Embedded 1080p HTTP `Range` (`206 Partial Content`) video streaming from GCS
     (`gs://$GCS_BUNDLE_BUCKET/videos/*.mp4`) with clickable scrub timestamp pills
  3. "Join Live at This Stage As..." 5-scientist role switcher (`?authuser=oase-<role>@...`)
     deep-linked to each chapter's live Scion Webchat thread + copyable Q&A prompts
  4. Live Facilitator Reset Drawer (`GET /api/state/status`, `POST /api/state/chapters/{ch}/reset`,
     `POST /api/state/reset-all`) for <2s non-disruptive resets
"""

from __future__ import annotations

import json
import mimetypes
import os
import re
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from google.cloud import storage

APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = Path(os.environ.get("STORY_ARC_STATIC_DIR", str(APP_DIR / "static"))).resolve()
if not STATIC_DIR.exists():
    fallback = APP_DIR.parent.parent / "site-template"
    if fallback.exists():
        STATIC_DIR = fallback.resolve()

GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "").strip()
WORKSHOP_DOMAIN = os.environ.get("WORKSHOP_DOMAIN", "").strip()
GCS_BUNDLE_BUCKET = os.environ.get("GCS_BUNDLE_BUCKET", "").strip().removeprefix("gs://").strip("/")
SCION_HUB_URL = os.environ.get("SCION_HUB_URL", "").strip().rstrip("/")
STATE_CONTROLLER_URL = os.environ.get("STATE_CONTROLLER_URL", "http://127.0.0.1:8780").strip().rstrip("/")
STATE_TOKEN = os.environ.get("OASE_STATE_TOKEN", "").strip()
LOCAL_VIDEOS_DIR = Path(os.environ.get("LOCAL_VIDEOS_DIR", "/tmp/oase-m3-assets/videos")).resolve()

PERSONAS = [
    {"key": "sarah", "prefix": "oase-sarah", "name": "Dr. Sarah Chen", "role": "Program Lead", "avatar": "assets/avatars/sarah.jpg"},
    {"key": "marcus", "prefix": "oase-marcus", "name": "Dr. Marcus Vance", "role": "Comp Bio", "avatar": "assets/avatars/marcus.jpg"},
    {"key": "elena", "prefix": "oase-elena", "name": "Dr. Elena Rostova", "role": "Structural Bio", "avatar": "assets/avatars/elena.jpg"},
    {"key": "raj", "prefix": "oase-raj", "name": "Dr. Raj Patel", "role": "Med Chem", "avatar": "assets/avatars/raj.jpg"},
    {"key": "claire", "prefix": "oase-claire", "name": "Dr. Claire Moreau", "role": "DMPK & Safety", "avatar": "assets/avatars/claire.jpg"},
]

FOLLOWUP_PROMPTS = {
    "ch1": [
        "@science-program-lead Summarize how our 3 Co-Scientist input prompt clauses in gates/STEP-01-pre-mission-brief.md map into .oase/thresholds.yaml and our 5 Doctor-to-AI Wingman pairings.",
        "@computational-biologist What specific structural liability caused IC-002 to trail IC-001 by 54.5 Elo points in WO-001, and why keep IC-002 parked on the Amber backup line?",
    ],
    "ch2": [
        "@computational-biologist Compare our PCSK9 hepatocyte TPM in GTEx against extrahepatic CNS tissues in WO-002.",
        "@science-program-lead Why must alphagenome.quantile_not_clinical_effect stay attached after Stage Gate 1?",
    ],
    "ch3": [
        "@structural-biologist Compare cryptic Pocket #1 druggability (0.68) against the flat EGF-A PPI surface (0.24) in WO-004.",
        "@science-program-lead Which chemical liability on PCSK9-A02 (-9.4 kcal/mol) requires MMP triage in Step 4?",
    ],
    "ch4": [
        "@medicinal-chemist Explain how the 1,2,4-oxadiazole swap in OASE-PCSK9-014 resolved the Aronov hERG alert from PCSK9-A02.",
        "@admet-dmpk-scientist List the exact experimental CRO assays required at the Gate 3 Wet-Lab handoff before Step 5 unlocks.",
    ],
    "ch5": [
        "@admet-dmpk-scientist How does OASE-PCSK9-014 (40 mg QD oral tablet, F=52%) compare against macrocyclic PCSK9 comparators?",
        "@science-program-lead Confirm all 8 Work Orders and risk relays verified in executive/CANDIDATE-SUMMARY.md.",
    ],
    "ch6": [
        "@finding-validator Which exact rule blocked Drill 2 when docking.score_not_affinity was omitted from the finding?",
        "@science-program-lead Show the audit record for the PCSK9-B07 Lipinski MW override in .oase/control/events.ndjson.",
    ],
    "ch7": [
        "@science-program-lead Walk through our 5 Doctor-to-AI Wingman post-mission debrief outcomes in gates/STEP-07-portfolio-closeout.md and executive/PORTFOLIO-HANDOFF.md.",
        "@project-curator Which dynamic Subway Map detours and CRO wet-lab receipts were decisive in nominating OASE-PCSK9-014 (40 mg oral QD)?",
    ],
}

app = FastAPI(title="OASE Story Arc Presenter Cockpit", version="1.1.0")
_gcs_client: storage.Client | None = None
DEFAULT_CAMPAIGN = "pcsk9-pilot-v1"
CAMPAIGN_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{1,63}$")


def _get_gcs_client() -> storage.Client:
    global _gcs_client
    if _gcs_client is None:
        _gcs_client = storage.Client(project=GCP_PROJECT_ID or None)
    return _gcs_client


def _state_headers() -> dict[str, str]:
    return {"X-OASE-State-Token": STATE_TOKEN} if STATE_TOKEN else {}


def _load_campaigns_registry() -> dict[str, Any]:
    rpath = STATIC_DIR / "assets" / "campaigns-registry.json"
    if rpath.exists():
        return json.loads(rpath.read_text(encoding="utf-8"))
    return {
        "default_campaign": DEFAULT_CAMPAIGN,
        "campaigns": [
            {
                "id": DEFAULT_CAMPAIGN,
                "short_label": "PCSK9 Oral · Reference Pilot (v1)",
                "status": "ready",
                "gcs_video_prefix": "videos",
                "video_manifest": "assets/video-chapters-manifest.json",
            }
        ],
    }


def _resolve_campaign(campaign: str | None) -> tuple[str, dict[str, Any], dict[str, Any]]:
    reg = _load_campaigns_registry()
    default_cid = reg.get("default_campaign") or DEFAULT_CAMPAIGN
    cid = (campaign or default_cid).strip() or default_cid
    if not CAMPAIGN_RE.fullmatch(cid):
        raise HTTPException(status_code=400, detail=f"Invalid campaign identifier '{cid}'")
    campaigns = reg.get("campaigns", [])
    entry = next((c for c in campaigns if c.get("id") == cid), None)
    if entry is None:
        entry = next((c for c in campaigns if c.get("id") == default_cid), {"id": default_cid, "status": "ready", "gcs_video_prefix": "videos", "video_manifest": "assets/video-chapters-manifest.json"})
        cid = entry.get("id", default_cid)
    return cid, entry, reg


def _load_video_manifest(campaign_entry: dict[str, Any] | None = None) -> dict[str, Any]:
    rel = (campaign_entry or {}).get("video_manifest") or "assets/video-chapters-manifest.json"
    mpath = (STATIC_DIR / rel).resolve()
    if str(mpath).startswith(str(STATIC_DIR)) and mpath.is_file():
        return json.loads(mpath.read_text(encoding="utf-8"))
    return {"chapters": {}}


@app.get("/healthz")
def healthz() -> dict[str, Any]:
    reg = _load_campaigns_registry()
    return {
        "ok": True,
        "service": "oase-story-arc",
        "static_dir": str(STATIC_DIR),
        "gcs_bucket": GCS_BUNDLE_BUCKET,
        "scion_hub_url": SCION_HUB_URL,
        "state_controller_url": STATE_CONTROLLER_URL,
        "campaigns_count": len(reg.get("campaigns", [])),
    }


@app.get("/api/cockpit/config")
async def cockpit_config(request: Request, campaign: str | None = Query(default=None)) -> JSONResponse:
    iap_email = request.headers.get("x-goog-authenticated-user-email", "").removeprefix("accounts.google.com:")
    cid, camp_entry, reg = _resolve_campaign(campaign)
    state_data: dict[str, Any] = {"ok": False, "campaign": cid, "chapters": {}}
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            r = await client.get(
                f"{STATE_CONTROLLER_URL}/api/state/status",
                params={"campaign": cid},
                headers=_state_headers(),
            )
            if r.status_code == 200:
                state_data = r.json()
    except Exception as exc:
        state_data = {"ok": False, "campaign": cid, "error": str(exc), "chapters": {}}

    return JSONResponse(
        {
            "signed_in_user": iap_email,
            "workshop_domain": WORKSHOP_DOMAIN,
            "scion_hub_url": SCION_HUB_URL,
            "active_campaign": cid,
            "campaigns": reg.get("campaigns", []),
            "campaigns_registry": reg,
            "personas": PERSONAS,
            "followup_prompts": FOLLOWUP_PROMPTS,
            "videos": _load_video_manifest(camp_entry),
            "state": state_data,
        }
    )


@app.get("/api/state/status")
async def proxy_state_status(campaign: str | None = Query(default=None)) -> JSONResponse:
    cid, _, _ = _resolve_campaign(campaign)
    async with httpx.AsyncClient(timeout=8.0) as client:
        r = await client.get(
            f"{STATE_CONTROLLER_URL}/api/state/status",
            params={"campaign": cid},
            headers=_state_headers(),
        )
        return JSONResponse(status_code=r.status_code, content=r.json())


@app.post("/api/state/chapters/{chapter}/reset")
async def proxy_reset_chapter(chapter: str, campaign: str | None = Query(default=None)) -> JSONResponse:
    if not re.fullmatch(r"ch[0-7]", chapter):
        raise HTTPException(status_code=400, detail="Invalid chapter ID")
    cid, _, _ = _resolve_campaign(campaign)
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.post(
            f"{STATE_CONTROLLER_URL}/api/state/chapters/{chapter}/reset",
            params={"campaign": cid},
            headers=_state_headers(),
        )
        return JSONResponse(status_code=r.status_code, content=r.json())


@app.post("/api/state/reset-all")
async def proxy_reset_all(campaign: str | None = Query(default=None)) -> JSONResponse:
    cid, _, _ = _resolve_campaign(campaign)
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.post(
            f"{STATE_CONTROLLER_URL}/api/state/reset-all",
            params={"campaign": cid},
            headers=_state_headers(),
        )
        return JSONResponse(status_code=r.status_code, content=r.json())


def _stream_video_impl(filename: str, request: Request, gcs_prefix: str = "videos", local_subdir: str = "") -> Response:
    if not re.fullmatch(r"[A-Za-z0-9._-]+\.mp4", filename):
        raise HTTPException(status_code=400, detail="Invalid video filename")

    range_header = request.headers.get("range")
    local_base = (LOCAL_VIDEOS_DIR / local_subdir).resolve() if local_subdir else LOCAL_VIDEOS_DIR
    local_file = local_base / filename
    if local_file.exists():
        total_size = local_file.stat().st_size
        if not range_header:
            return FileResponse(local_file, media_type="video/mp4", headers={"Accept-Ranges": "bytes"})
        m = re.match(r"bytes=(\d+)-(\d*)", range_header)
        if not m:
            raise HTTPException(status_code=416, detail="Invalid Range header")
        start = int(m.group(1))
        end = int(m.group(2)) if m.group(2) else min(start + 4 * 1024 * 1024 - 1, total_size - 1)
        end = min(end, total_size - 1)
        if start >= total_size or start > end:
            raise HTTPException(status_code=416, detail="Range Not Satisfiable")
        with local_file.open("rb") as fh:
            fh.seek(start)
            chunk = fh.read(end - start + 1)
        return Response(
            content=chunk,
            status_code=206,
            media_type="video/mp4",
            headers={
                "Content-Range": f"bytes {start}-{end}/{total_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(len(chunk)),
                "Cache-Control": "public, max-age=3600",
            },
        )

    if not GCS_BUNDLE_BUCKET:
        raise HTTPException(status_code=404, detail="GCS_BUNDLE_BUCKET not configured and local video absent")

    bucket = _get_gcs_client().bucket(GCS_BUNDLE_BUCKET)
    clean_prefix = gcs_prefix.strip("/")
    blob = bucket.blob(f"{clean_prefix}/{filename}")
    if not blob.exists():
        raise HTTPException(status_code=404, detail=f"Video {clean_prefix}/{filename} not found in GCS")
    blob.reload()
    total_size = int(blob.size or 0)
    if total_size <= 0:
        raise HTTPException(status_code=404, detail=f"Video {filename} empty or missing in GCS")

    if range_header:
        m = re.match(r"bytes=(\d+)-(\d*)", range_header)
        if not m:
            raise HTTPException(status_code=416, detail="Invalid Range header")
        start = int(m.group(1))
        # Stream 4 MiB chunks on open-ended browser Range requests for snappy seeking + Cloud Run 32MB safety
        end = int(m.group(2)) if m.group(2) else min(start + 4 * 1024 * 1024 - 1, total_size - 1)
        end = min(end, total_size - 1)
        if start >= total_size or start > end:
            raise HTTPException(status_code=416, detail="Range Not Satisfiable")
        chunk = blob.download_as_bytes(start=start, end=end)
        return Response(
            content=chunk,
            status_code=206,
            media_type="video/mp4",
            headers={
                "Content-Range": f"bytes {start}-{end}/{total_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(len(chunk)),
                "Cache-Control": "no-cache, max-age=0, must-revalidate",
            },
        )

    # Initial non-range probe: return first 2 MiB as 206 or full if <20 MiB
    if total_size <= 24 * 1024 * 1024:
        full_bytes = blob.download_as_bytes()
        return Response(
            content=full_bytes,
            status_code=200,
            media_type="video/mp4",
            headers={
                "Accept-Ranges": "bytes",
                "Content-Length": str(len(full_bytes)),
                "Cache-Control": "no-cache, max-age=0, must-revalidate",
            },
        )
    end = 2 * 1024 * 1024 - 1
    chunk = blob.download_as_bytes(start=0, end=end)
    return Response(
        content=chunk,
        status_code=206,
        media_type="video/mp4",
        headers={
            "Content-Range": f"bytes 0-{end}/{total_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(len(chunk)),
        },
    )


@app.get("/api/videos/{campaign}/{filename}")
def stream_campaign_video(campaign: str, filename: str, request: Request) -> Response:
    cid, camp_entry, _ = _resolve_campaign(campaign)
    gcs_prefix = camp_entry.get("gcs_video_prefix") or ("videos" if cid == DEFAULT_CAMPAIGN else f"campaigns/{cid}/videos")
    local_sub = "" if cid == DEFAULT_CAMPAIGN else cid
    return _stream_video_impl(filename, request, gcs_prefix=gcs_prefix, local_subdir=local_sub)


@app.get("/api/videos/{filename}")
def stream_video(filename: str, request: Request) -> Response:
    return _stream_video_impl(filename, request, gcs_prefix="videos", local_subdir="")


COCKPIT_ENHANCEMENT_SNIPPET = r"""
<style id="oase-cockpit-style">
  .cockpit-ControlBar {
    background: #0f172a;
    color: #f8fafc;
    border-bottom: 2px solid #10b981;
    padding: 0.55rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    flex-wrap: wrap;
    font-size: 0.84rem;
  }
  .cockpit-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    background: rgba(16, 185, 129, 0.14);
    color: #6ee7b7;
    border: 1px solid rgba(16, 185, 129, 0.4);
    padding: 0.25rem 0.7rem;
    border-radius: 999px;
    font-family: ui-monospace, monospace;
    font-size: 0.78rem;
    font-weight: 600;
  }
  .cockpit-btn {
    background: #1e293b;
    color: #f8fafc;
    border: 1px solid #475569;
    padding: 0.38rem 0.78rem;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
  }
  .cockpit-btn:hover { background: #334155; border-color: #94a3b8; }
  .cockpit-btn.danger { background: #7f1d1d; border-color: #ef4444; color: #fecaca; }
  .cockpit-btn.danger:hover { background: #991b1b; }
  .cockpit-btn.primary { background: #059669; border-color: #10b981; color: #ffffff; }
  .cockpit-btn.primary:hover { background: #047857; }
  .cockpit-drawer {
    display: none;
    background: #020617;
    color: #e2e8f0;
    padding: 1rem 2rem;
    border-bottom: 2px solid #334155;
  }
  .cockpit-drawer.open { display: block; }
  .cockpit-drawer table th { background: #0f172a; color: #94a3b8; border-bottom: 1px solid #1e293b; }
  .cockpit-drawer table td { border-bottom: 1px solid #1e293b; color: #e2e8f0; font-size: 0.82rem; }
  .cockpit-stage-card {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    color: #f8fafc;
    border-radius: 10px;
    padding: 1.15rem 1.35rem;
    margin-bottom: 1.35rem;
    border: 1px solid #334155;
    box-shadow: 0 6px 20px rgba(15, 23, 42, 0.16);
  }
  .cockpit-video-wrap {
    position: relative;
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid #475569;
    background: #000;
  }
  .cockpit-video-wrap video {
    width: 100%;
    max-height: 600px;
    display: block;
    background: #000;
  }
  .scrub-bar {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-top: 0.75rem;
  }
  .scrub-pill {
    background: rgba(37, 99, 235, 0.22);
    color: #93c5fd;
    border: 1px solid rgba(59, 130, 246, 0.5);
    border-radius: 999px;
    padding: 0.32rem 0.75rem;
    font-size: 0.78rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
  }
  .scrub-pill:hover { background: #2563eb; color: #ffffff; }
  .role-bar {
    margin-top: 1rem;
    padding-top: 0.9rem;
    border-top: 1px solid rgba(148, 163, 184, 0.22);
  }
  .role-grid {
    display: flex;
    gap: 0.55rem;
    flex-wrap: wrap;
    margin-top: 0.5rem;
  }
  .role-link {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: #1e293b;
    color: #f8fafc;
    text-decoration: none;
    padding: 0.38rem 0.75rem;
    border-radius: 8px;
    border: 1px solid #475569;
    font-size: 0.8rem;
    font-weight: 600;
    transition: all 0.15s;
  }
  .role-link:hover { background: #2563eb; border-color: #60a5fa; color: #fff; }
  .role-link.lead { border-color: #10b981; background: rgba(16, 185, 129, 0.18); }
  .role-link img { width: 26px; height: 26px; border-radius: 50%; object-fit: cover; border: 1.5px solid #38bdf8; }
  .prompt-chip {
    background: rgba(15, 23, 42, 0.75);
    border: 1px dashed #475569;
    color: #cbd5e1;
    padding: 0.42rem 0.7rem;
    border-radius: 6px;
    font-family: ui-monospace, monospace;
    font-size: 0.76rem;
    cursor: pointer;
    margin-top: 0.45rem;
    display: block;
    text-align: left;
    width: 100%;
  }
  .prompt-chip:hover { border-color: #38bdf8; color: #ffffff; }
  .wetlab-callout {
    margin-top: 0.9rem;
    background: rgba(245, 158, 11, 0.14);
    border-left: 4px solid #f59e0b;
    padding: 0.7rem 0.95rem;
    border-radius: 0 6px 6px 0;
    color: #fde68a;
    font-size: 0.83rem;
  }
  #cockpit-toast {
    position: fixed;
    bottom: 22px;
    right: 22px;
    background: #059669;
    color: #ffffff;
    padding: 0.7rem 1.1rem;
    border-radius: 8px;
    font-weight: 700;
    font-size: 0.85rem;
    box-shadow: 0 8px 24px rgba(0,0,0,0.35);
    display: none;
    z-index: 99999;
  }
</style>
<div id="cockpit-toast"></div>
<script id="oase-cockpit-script">
(function() {
  let cockpitCfg = null;

  function showToast(msg, isErr) {
    const t = document.getElementById('cockpit-toast');
    if (!t) return;
    t.style.background = isErr ? '#dc2626' : '#059669';
    t.textContent = msg;
    t.style.display = 'block';
    setTimeout(() => { t.style.display = 'none'; }, 4200);
  }

  window.oaseSeekVideo = function(chId, sec) {
    const v = document.getElementById('video-' + chId);
    if (!v) return;
    v.currentTime = sec;
    v.play().catch(() => {});
  };

  window.oaseCopyPrompt = function(txt) {
    navigator.clipboard.writeText(txt).then(() => {
      showToast('Copied live follow-up prompt to clipboard!');
    });
  };

  window.oaseResetChapter = async function(chId) {
    showToast('Resetting ' + chId.toUpperCase() + ' Grove + Scion SQLite...');
    try {
      const r = await fetch('/api/state/chapters/' + chId + '/reset', { method: 'POST' });
      const d = await r.json();
      if (!r.ok || !d.ok) throw new Error(d.detail || 'Reset failed');
      showToast('Reset ' + chId.toUpperCase() + ' complete in ' + d.duration_ms + ' ms (commit ' + d.git_commit + ')!');
      await refreshCockpit();
    } catch (e) {
      showToast('Reset error: ' + e.message, true);
    }
  };

  window.oaseResetAll = async function() {
    showToast('Resetting all 8 chapters (ch0..ch7) to Golden Snapshot...');
    try {
      const r = await fetch('/api/state/reset-all', { method: 'POST' });
      const d = await r.json();
      if (!r.ok || !d.ok) throw new Error(d.detail || 'Reset-all failed');
      showToast('Reset all ' + d.chapters_reset + ' chapters to t=0 / Golden State in ' + d.duration_ms + ' ms!');
      await refreshCockpit();
    } catch (e) {
      showToast('Reset-all error: ' + e.message, true);
    }
  };

  window.oaseToggleDrawer = function() {
    const dr = document.getElementById('oase-facilitator-drawer');
    if (dr) dr.classList.toggle('open');
  };

  function buildTopBar(cfg) {
    let bar = document.getElementById('oase-cockpit-topbar');
    if (!bar) {
      bar = document.createElement('div');
      bar.id = 'oase-cockpit-topbar';
      bar.className = 'cockpit-ControlBar';
      const dr = document.createElement('div');
      dr.id = 'oase-facilitator-drawer';
      dr.className = 'cockpit-drawer';
      const nav = document.querySelector('nav');
      if (nav && nav.parentNode) {
        nav.parentNode.insertBefore(dr, nav.nextSibling);
        nav.parentNode.insertBefore(bar, dr);
      }
    }
    const st = cfg.state || {};
    const chCount = Object.keys(st.chapters || {}).length;
    const statusText = st.ok
      ? `● Live Grove Connected · ${chCount} Chapters Ready · Admin Leaks: ${st.admin_rows_count ?? 0}`
      : `● Static Replay Mode (State Controller unreachable)`;

    const ch0 = (st.chapters || {}).ch0;
    const ch0Url = (cfg.scion_hub_url && ch0 && cfg.workshop_domain)
      ? `${cfg.scion_hub_url}/chat/${ch0.slug}/${ch0.general_topic_id}?authuser=oase-sarah@${cfg.workshop_domain}`
      : '#';

    bar.innerHTML = `
      <div style="display:flex;align-items:center;gap:0.75rem;flex-wrap:wrap;">
        <span class="cockpit-status-pill">${statusText}</span>
        ${cfg.signed_in_user ? `<span style="color:#94a3b8;font-family:monospace;font-size:0.78rem;">Signed in: <strong style="color:#fff;">${cfg.signed_in_user}</strong></span>` : ''}
      </div>
      <div style="display:flex;align-items:center;gap:0.55rem;flex-wrap:wrap;">
        ${ch0Url !== '#' ? `<a class="cockpit-btn primary" href="${ch0Url}" target="_blank" rel="noopener" style="text-decoration:none;">🧪 Launch Fresh Sandbox (ch0 · t=0) ↗</a>` : ''}
        <button class="cockpit-btn" onclick="oaseToggleDrawer()">⚙ Facilitator Reset Drawer</button>
        <button class="cockpit-btn danger" onclick="oaseResetAll()">↺ Reset Entire Demo (t=0)</button>
      </div>
    `;

    const dr = document.getElementById('oase-facilitator-drawer');
    if (dr && st.chapters) {
      const rows = Object.values(st.chapters).map(c => `
        <tr>
          <td><strong>${c.chapter.toUpperCase()}</strong></td>
          <td><code>${c.slug}</code></td>
          <td><code>${c.active_git_tag}</code> (<code>${c.git_commit}</code>)</td>
          <td>${c.message_count} msgs · ${c.artifact_count} artifacts</td>
          <td><code>${(c.running_agents || []).join(', ')}</code></td>
          <td>${c.last_reset_duration_ms ? c.last_reset_duration_ms + ' ms' : 'Golden'}</td>
          <td><button class="cockpit-btn" onclick="oaseResetChapter('${c.chapter}')">↺ Reset ${c.chapter.toUpperCase()}</button></td>
        </tr>
      `).join('');
      dr.innerHTML = `
        <div style="max-width:1320px;margin:0 auto;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.6rem;">
            <strong>Facilitator Live Chapter &amp; SQLite Snapshot Controller (Sub-2s Non-Disruptive Reset)</strong>
            <span style="color:#94a3b8;font-size:0.78rem;">Golden Snapshot: ${st.golden_snapshot_updated_at || 'Active'} · Preserves all 5 Chrome sessions</span>
          </div>
          <table>
            <thead><tr><th>Stage</th><th>Scion Project</th><th>Git Tag</th><th>Hub DB State</th><th>Live Specialist Containers</th><th>Last Reset</th><th>Action</th></tr></thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
      `;
    }
  }

  function injectChapterCards(cfg) {
    const videos = (cfg.videos && cfg.videos.chapters) || {};
    const fullVideo = cfg.videos && cfg.videos.full_walkthrough;
    const stChapters = (cfg.state && cfg.state.chapters) || {};
    const personas = cfg.personas || [];
    const promptsMap = cfg.followup_prompts || {};

    if (fullVideo && !document.getElementById('cockpit-full-walkthrough-card')) {
      const whyPanel = document.getElementById('panel-why');
      if (whyPanel) {
        const fwCard = document.createElement('div');
        fwCard.id = 'cockpit-full-walkthrough-card';
        fwCard.className = 'cockpit-stage-card';
        const durMin = fullVideo.duration_s ? (fullVideo.duration_s / 60).toFixed(1) + ' min' : '7 Chapters';
        fwCard.innerHTML = `
          <div style="display:flex;justify-content:space-between;align-items:center;gap:0.75rem;flex-wrap:wrap;margin-bottom:0.55rem;">
            <div>
              <strong style="color:#38bdf8;font-size:0.98rem;">🎬 Interactive 7-Chapter Squadron Walkthrough (${durMin} Total · 1080p)</strong>
              <div style="color:#cbd5e1;font-size:0.81rem;margin-top:0.2rem;">
                Upbeat 100/200-level tactical pod comms (~37s/step) keep the story moving while verbatim metrics, JSONPath citations, and SHA-256 receipts appear live in Scion Webchat and below each video.
              </div>
            </div>
            <div style="display:flex;gap:0.5rem;flex-wrap:wrap;">
              <button class="cockpit-btn primary" onclick="showChapter('ch1')">▶ Jump to Step 1 Video →</button>
            </div>
          </div>
          <details>
            <summary style="cursor:pointer;font-weight:700;color:#93c5fd;font-size:0.88rem;">
              ▶ Or expand continuous ${durMin} full-campaign video reel right here (Steps 1–7 back-to-back)
            </summary>
            <div class="cockpit-video-wrap" style="margin-top:0.8rem;">
              <video id="video-full" controls preload="none" src="/api/videos/${fullVideo.video_filename || 'full-pilot-walkthrough.mp4'}?v=${fullVideo.duration_s || '38'}"></video>
            </div>
          </details>
        `;
        const whatifHero = document.getElementById('whatif-hero');
        const hdr = whyPanel.querySelector('.chapter-header');
        if (whatifHero && whatifHero.parentNode) {
          whatifHero.parentNode.insertBefore(fwCard, whatifHero.nextSibling);
        } else if (hdr && hdr.nextSibling) {
          whyPanel.insertBefore(fwCard, hdr.nextSibling);
        }
      }
    }

    ['ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7'].forEach(chId => {
      const panel = document.getElementById('panel-' + chId);
      if (!panel) return;
      const vmeta = videos[chId];
      const cstate = stChapters[chId] || {};
      const leadKey = cstate.lead_human || 'sarah';
      let card = document.getElementById('cockpit-card-' + chId);
      const isNew = !card;
      if (isNew) {
        card = document.createElement('div');
        card.id = 'cockpit-card-' + chId;
        card.className = 'cockpit-stage-card';
        const hdr = panel.querySelector('.chapter-header');
        if (hdr && hdr.nextSibling) {
          panel.insertBefore(card, hdr.nextSibling);
        } else {
          panel.prepend(card);
        }
      } else {
        // Only update live state counts without resetting an actively playing <video>!
        const badge = document.getElementById('cockpit-state-badge-' + chId);
        if (badge && cstate.git_commit) {
          badge.textContent = `Live Project: ${cstate.slug} · Git ${cstate.git_commit} · ${cstate.message_count} Webchat msgs · ${(cstate.running_agents || []).length} live containers`;
        }
        return;
      }

      const markersHtml = vmeta && vmeta.markers
        ? vmeta.markers.map(m =>
            `<button class="scrub-pill" onclick="oaseSeekVideo('${chId}', ${m.time_s})">▶ ${m.label} (${m.timecode}) · ${m.speaker}</button>`
          ).join('')
        : '';

      const rolesHtml = personas.map(p => {
        const email = cfg.workshop_domain ? `${p.prefix}@${cfg.workshop_domain}` : '';
        const liveHref = (cfg.scion_hub_url && cstate.slug && cstate.general_topic_id && email)
          ? `${cfg.scion_hub_url}/chat/${cstate.slug}/${cstate.general_topic_id}?authuser=${encodeURIComponent(email)}`
          : (cfg.scion_hub_url ? `${cfg.scion_hub_url}/chat` : '#');
        const isLead = p.key === leadKey;
        return `
          <a class="role-link ${isLead ? 'lead' : ''}" href="${liveHref}" target="_blank" rel="noopener">
            <img src="${p.avatar}" alt="${p.name}">
            <span>${p.name} <small style="color:#94a3b8;">(${p.role}${isLead ? ' · LEAD' : ''})</small></span>
          </a>
        `;
      }).join('');

      const promptsHtml = (promptsMap[chId] || []).map(pr =>
        `<button class="prompt-chip" onclick='oaseCopyPrompt(${JSON.stringify(pr)})'>📋 Copy Live Follow-Up Prompt: "${pr}"</button>`
      ).join('');

      const wetlabHtml = chId === 'ch4'
        ? `<div class="wetlab-callout"><strong>⏸ Explicit Future-State Wet-Lab / CRO Assay Handoff Slot:</strong> Campaign pauses on disk at <code>WO-006</code> (<code>gates/GATE-03-wetlab-handoff.md</code>) after disqualifying <code>PCSK9-A02</code> on cardiac hERG—awaiting experimental SPR <code>K<sub>D</sub></code>, manual patch-clamp hERG (<code>&gt;30 µM</code>), and rat/dog cassette PK before <code>WO-007</code> unlocks.</div>`
        : '';

      const videoFilename = vmeta ? vmeta.video_filename : `chapter-0${chId.slice(2)}.mp4`;
      const videoVer = vmeta && vmeta.duration_s ? vmeta.duration_s : '38';

      card.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;margin-bottom:0.75rem;">
          <div>
            <strong style="font-size:1rem;color:#38bdf8;">🎬 Recorded Multi-Human + Multi-Agent Scion Walkthrough (1080p · Native Gemini 3.8 Live Avatars + Multi-Model Grove)</strong>
            <div id="cockpit-state-badge-${chId}" style="font-size:0.77rem;color:#94a3b8;font-family:monospace;margin-top:0.15rem;">
              ${cstate.slug ? `Live Project: ${cstate.slug} · Git ${cstate.git_commit} · ${cstate.message_count} Webchat msgs · ${(cstate.running_agents || []).length} live containers` : 'Pre-staged Scion Grove checkpoint'}
            </div>
          </div>
          <button class="cockpit-btn" onclick="oaseResetChapter('${chId}')">↺ Reset ${chId.toUpperCase()} (&lt;2s)</button>
        </div>
        <div class="cockpit-video-wrap">
          <video id="video-${chId}" controls preload="metadata" src="/api/videos/${videoFilename}?v=${videoVer}"></video>
        </div>
        <div class="scrub-bar">${markersHtml}</div>
        ${wetlabHtml}
        <div class="role-bar">
          <div style="font-size:0.83rem;font-weight:700;color:#e2e8f0;">🚀 Join Live at This Stage As Any of the 5 Discovery Pod Scientists (Zero Admin Noise):</div>
          <div class="role-grid">${rolesHtml}</div>
          <div style="margin-top:0.55rem;">${promptsHtml}</div>
        </div>
      `;
    });
  }

  async function refreshCockpit() {
    try {
      const r = await fetch('/api/cockpit/config');
      if (!r.ok) return;
      cockpitCfg = await r.json();
      buildTopBar(cockpitCfg);
      injectChapterCards(cockpitCfg);
    } catch (e) {
      console.warn('Cockpit refresh skipped:', e);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', refreshCockpit);
  } else {
    refreshCockpit();
  }
})();
</script>
"""


def _render_cockpit_html(filename: str) -> HTMLResponse:
    target = STATIC_DIR / filename
    if not target.exists():
        raise HTTPException(status_code=404, detail=f"{filename} not found in {STATIC_DIR}")
    raw = target.read_text(encoding="utf-8")
    if "oase-cockpit-script" not in raw and "</body>" in raw:
        raw = raw.replace("</body>", f"{COCKPIT_ENHANCEMENT_SNIPPET}\n</body>", 1)
    return HTMLResponse(raw)


@app.get("/", response_class=HTMLResponse)
def root_cockpit() -> HTMLResponse:
    return _render_cockpit_html("chapters.html")


@app.get("/chapters.html", response_class=HTMLResponse)
def chapters_cockpit() -> HTMLResponse:
    return _render_cockpit_html("chapters.html")


@app.get("/{rel_path:path}")
def serve_static_portal(rel_path: str) -> Response:
    safe_target = (STATIC_DIR / rel_path).resolve()
    if not str(safe_target).startswith(str(STATIC_DIR)) or not safe_target.is_file():
        raise HTTPException(status_code=404, detail="Not Found")
    ctype, _ = mimetypes.guess_type(str(safe_target))
    return FileResponse(safe_target, media_type=ctype or "application/octet-stream")

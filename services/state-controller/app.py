#!/usr/bin/env python3
"""FastAPI State Controller for the 8-Checkpoint (ch0..ch7) OASE Team Discovery Pilot.

Provides <2-second non-disruptive chapter and full-environment resets on the
Scion Hub host without logging out any of the 5 authenticated Chrome scientist
sessions or restarting live specialist containers:
  - GET  /healthz
  - GET  /api/state/status
  - POST /api/state/snapshot
  - POST /api/state/chapters/{chapter}/reset
  - POST /api/state/reset-all
"""

from __future__ import annotations

import datetime
import json
import os
import re
import shutil
import sqlite3
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Query

HUB_DIR = Path(os.environ.get("SCION_HUB_DIR", "/home/scion/.scion")).resolve()
DB_PATH = HUB_DIR / "hub.db"
MANIFEST_PATH = HUB_DIR / "pilot-chapters-manifest.json"
SNAPSHOT_DIR = Path(
    os.environ.get("OASE_GOLDEN_SNAPSHOT_DIR", str(HUB_DIR / "snapshots" / "golden-pilot"))
).resolve()
GOLDEN_DB_PATH = SNAPSHOT_DIR / "golden-hub.db"
STATE_TOKEN = os.environ.get("OASE_STATE_TOKEN", "").strip()
DEFAULT_CAMPAIGN = "pcsk9-pilot-v1"
CAMPAIGN_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{1,63}$")

VALID_CHAPTERS = ("ch0", "ch1", "ch2", "ch3", "ch4", "ch5", "ch6", "ch7")
CLEAN_EXCLUDES = ("-e", ".scion", "-e", ".scion-volumes", "-e", ".agents", "-e", "skills", "-e", "templates")

app = FastAPI(
    title="OASE Pilot State Controller",
    version="1.1.0",
    description="Atomic <2s Multi-Campaign Grove Git + Scion SQLite chapter reset daemon.",
)

_reset_lock = threading.Lock()
_reset_history: dict[str, dict[str, Any]] = {}


def _check_auth(x_oase_state_token: str | None) -> None:
    if STATE_TOKEN and (x_oase_state_token or "").strip() != STATE_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing X-OASE-State-Token")


def _campaign_paths(campaign: str | None = None) -> tuple[str, Path, Path, Path]:
    cid = (campaign or DEFAULT_CAMPAIGN).strip() or DEFAULT_CAMPAIGN
    if not CAMPAIGN_RE.fullmatch(cid):
        raise HTTPException(status_code=400, detail=f"Invalid campaign identifier '{cid}'")
    if cid == DEFAULT_CAMPAIGN:
        return cid, MANIFEST_PATH, SNAPSHOT_DIR, GOLDEN_DB_PATH
    c_manifest = (HUB_DIR / "campaigns" / cid / "pilot-chapters-manifest.json").resolve()
    c_snap_dir = (HUB_DIR / "snapshots" / cid).resolve()
    return cid, c_manifest, c_snap_dir, c_snap_dir / "golden-hub.db"


def _load_manifest(manifest_path: Path = MANIFEST_PATH) -> dict[str, Any]:
    if not manifest_path.exists():
        raise HTTPException(status_code=503, detail=f"Chapter manifest not found at {manifest_path}")
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _shared_columns(cur: sqlite3.Cursor, table: str) -> str:
    main_cols = [r[1] for r in cur.execute(f'PRAGMA main.table_info("{table}")').fetchall()]
    gold_cols = {r[1] for r in cur.execute(f'PRAGMA golden.table_info("{table}")').fetchall()}
    common = [f'"{c}"' for c in main_cols if c in gold_cols]
    if not common:
        raise RuntimeError(f"No shared columns between main.{table} and golden.{table}")
    return ", ".join(common)


def _git_reset_workspace(ws_path: Path, chapter: str) -> dict[str, Any]:
    if not (ws_path / ".git").exists():
        return {"git_commit": "uninitialized", "active_git_tag": chapter}
    subprocess.run(["git", "-C", str(ws_path), "checkout", "-q", "-f", chapter], check=True)
    subprocess.run(["git", "-C", str(ws_path), "clean", "-fd", "-q", *CLEAN_EXCLUDES], check=True)
    commit = (
        subprocess.run(["git", "-C", str(ws_path), "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True)
        .stdout.strip()
    )
    return {"git_commit": commit, "active_git_tag": chapter}


def _git_inspect_workspace(ws_path: Path) -> dict[str, Any]:
    if not (ws_path / ".git").exists():
        return {"active_git_tag": "none", "git_commit": "none", "dirty_files_count": 0}
    commit = (
        subprocess.run(["git", "-C", str(ws_path), "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=False)
        .stdout.strip()
    )
    tag = (
        subprocess.run(
            ["git", "-C", str(ws_path), "describe", "--tags", "--exact-match"],
            capture_output=True,
            text=True,
            check=False,
        )
        .stdout.strip()
    )
    porcelain = (
        subprocess.run(["git", "-C", str(ws_path), "status", "--porcelain"], capture_output=True, text=True, check=False)
        .stdout.splitlines()
    )
    return {
        "active_git_tag": tag or "detached",
        "git_commit": commit or "none",
        "dirty_files_count": len(porcelain),
    }


def _restore_projects_from_golden(
    project_ids: list[str], golden_db_path: Path = GOLDEN_DB_PATH
) -> dict[str, dict[str, int]]:
    if not golden_db_path.exists():
        raise HTTPException(status_code=503, detail=f"Golden snapshot DB missing at {golden_db_path}")

    conn = sqlite3.connect(str(DB_PATH), timeout=30.0, isolation_level=None)
    stats: dict[str, dict[str, int]] = {}
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA busy_timeout = 30000;")
        cur.execute("PRAGMA foreign_keys = OFF;")
        cur.execute(f"ATTACH DATABASE '{golden_db_path}' AS golden;")
        cur.execute("BEGIN IMMEDIATE;")

        conv_cols = _shared_columns(cur, "conversations")
        topic_cols = _shared_columns(cur, "webchat_topic")
        part_cols = _shared_columns(cur, "conversation_participants")
        msg_cols = _shared_columns(cur, "messages")
        addr_cols = _shared_columns(cur, "message_addressees")
        ext_cols = _shared_columns(cur, "webchat_message_ext")
        mention_cols = _shared_columns(cur, "webchat_mention")
        thread_cols = _shared_columns(cur, "webchat_thread")
        ctx_cols = _shared_columns(cur, "webchat_conversation_context")
        star_cols = _shared_columns(cur, "webchat_message_star")
        art_cols = _shared_columns(cur, "artifact")
        ver_cols = _shared_columns(cur, "artifact_version")
        file_cols = _shared_columns(cur, "artifact_file")

        for pid in project_ids:
            # 1. Restore Webchat & conversation state (never touching users or user_access_tokens)
            cur.execute("DELETE FROM main.webchat_message_star WHERE project_id = ?", (pid,))
            cur.execute(
                "DELETE FROM main.webchat_mention WHERE message_id IN (SELECT id FROM main.messages WHERE project_id = ?)",
                (pid,),
            )
            cur.execute(
                "DELETE FROM main.webchat_message_ext WHERE message_id IN (SELECT id FROM main.messages WHERE project_id = ?)",
                (pid,),
            )
            cur.execute(
                "DELETE FROM main.message_addressees WHERE message_id IN (SELECT id FROM main.messages WHERE project_id = ?)",
                (pid,),
            )
            cur.execute("DELETE FROM main.webchat_thread WHERE project_id = ?", (pid,))
            cur.execute("DELETE FROM main.webchat_conversation_context WHERE project_id = ?", (pid,))
            cur.execute("DELETE FROM main.messages WHERE project_id = ?", (pid,))
            cur.execute(
                "DELETE FROM main.conversation_participants WHERE conversation_id IN (SELECT id FROM main.conversations WHERE project_id = ?)",
                (pid,),
            )
            cur.execute("DELETE FROM main.webchat_topic WHERE project_id = ?", (pid,))
            cur.execute("DELETE FROM main.conversations WHERE project_id = ?", (pid,))

            cur.execute(
                f"INSERT OR REPLACE INTO main.conversations ({conv_cols}) SELECT {conv_cols} FROM golden.conversations WHERE project_id = ?",
                (pid,),
            )
            cur.execute(
                f"INSERT OR REPLACE INTO main.webchat_topic ({topic_cols}) SELECT {topic_cols} FROM golden.webchat_topic WHERE project_id = ?",
                (pid,),
            )
            cur.execute(
                f"INSERT OR REPLACE INTO main.conversation_participants ({part_cols}) "
                f"SELECT {part_cols} FROM golden.conversation_participants "
                f"WHERE conversation_id IN (SELECT id FROM golden.conversations WHERE project_id = ?)",
                (pid,),
            )
            cur.execute(
                f"INSERT OR REPLACE INTO main.messages ({msg_cols}) SELECT {msg_cols} FROM golden.messages WHERE project_id = ?",
                (pid,),
            )
            cur.execute(
                f"INSERT OR REPLACE INTO main.message_addressees ({addr_cols}) "
                f"SELECT {addr_cols} FROM golden.message_addressees "
                f"WHERE message_id IN (SELECT id FROM golden.messages WHERE project_id = ?)",
                (pid,),
            )
            cur.execute(
                f"INSERT OR REPLACE INTO main.webchat_message_ext ({ext_cols}) "
                f"SELECT {ext_cols} FROM golden.webchat_message_ext "
                f"WHERE message_id IN (SELECT id FROM golden.messages WHERE project_id = ?)",
                (pid,),
            )
            cur.execute(
                f"INSERT OR REPLACE INTO main.webchat_mention ({mention_cols}) "
                f"SELECT {mention_cols} FROM golden.webchat_mention "
                f"WHERE message_id IN (SELECT id FROM golden.messages WHERE project_id = ?)",
                (pid,),
            )
            cur.execute(
                f"INSERT OR REPLACE INTO main.webchat_thread ({thread_cols}) SELECT {thread_cols} FROM golden.webchat_thread WHERE project_id = ?",
                (pid,),
            )
            cur.execute(
                f"INSERT OR REPLACE INTO main.webchat_conversation_context ({ctx_cols}) SELECT {ctx_cols} FROM golden.webchat_conversation_context WHERE project_id = ?",
                (pid,),
            )
            cur.execute(
                f"INSERT OR REPLACE INTO main.webchat_message_star ({star_cols}) SELECT {star_cols} FROM golden.webchat_message_star WHERE project_id = ?",
                (pid,),
            )

            # 2. Restore project-scoped published artifacts
            cur.execute(
                "DELETE FROM main.artifact_file WHERE version_id IN ("
                "SELECT id FROM main.artifact_version WHERE artifact_id IN ("
                "SELECT id FROM main.artifact WHERE scope_kind = 'project' AND scope_ref = ?))",
                (pid,),
            )
            cur.execute(
                "DELETE FROM main.artifact_version WHERE artifact_id IN ("
                "SELECT id FROM main.artifact WHERE scope_kind = 'project' AND scope_ref = ?)",
                (pid,),
            )
            cur.execute("DELETE FROM main.artifact WHERE scope_kind = 'project' AND scope_ref = ?", (pid,))

            cur.execute(
                f"INSERT OR REPLACE INTO main.artifact ({art_cols}) "
                f"SELECT {art_cols} FROM golden.artifact WHERE scope_kind = 'project' AND scope_ref = ?",
                (pid,),
            )
            cur.execute(
                f"INSERT OR REPLACE INTO main.artifact_version ({ver_cols}) "
                f"SELECT {ver_cols} FROM golden.artifact_version "
                f"WHERE artifact_id IN (SELECT id FROM golden.artifact WHERE scope_kind = 'project' AND scope_ref = ?)",
                (pid,),
            )
            cur.execute(
                f"INSERT OR REPLACE INTO main.artifact_file ({file_cols}) "
                f"SELECT {file_cols} FROM golden.artifact_file "
                f"WHERE version_id IN (SELECT id FROM golden.artifact_version WHERE artifact_id IN ("
                f"SELECT id FROM golden.artifact WHERE scope_kind = 'project' AND scope_ref = ?))",
                (pid,),
            )

            msg_cnt = cur.execute("SELECT COUNT(*) FROM main.messages WHERE project_id = ?", (pid,)).fetchone()[0]
            art_cnt = cur.execute(
                "SELECT COUNT(*) FROM main.artifact WHERE scope_kind = 'project' AND scope_ref = ? AND deleted_at IS NULL",
                (pid,),
            ).fetchone()[0]
            stats[pid] = {"restored_messages": msg_cnt, "restored_artifacts": art_cnt}

        cur.execute("COMMIT;")
        cur.execute("DETACH DATABASE golden;")
    except Exception:
        try:
            conn.execute("ROLLBACK;")
        except Exception:
            pass
        raise
    finally:
        conn.close()
    return stats


@app.get("/healthz")
def healthz() -> dict[str, Any]:
    return {
        "ok": True,
        "service": "oase-state-controller",
        "hub_db_exists": DB_PATH.exists(),
        "golden_db_exists": GOLDEN_DB_PATH.exists(),
    }


@app.get("/api/state/status")
def get_state_status(
    campaign: str | None = Query(default=None),
    x_oase_state_token: str | None = Header(default=None),
) -> dict[str, Any]:
    _check_auth(x_oase_state_token)
    cid, manifest_path, _, golden_db = _campaign_paths(campaign)
    if cid != DEFAULT_CAMPAIGN and not manifest_path.exists():
        return {
            "ok": False,
            "campaign": cid,
            "status": "staging",
            "golden_snapshot_exists": golden_db.exists(),
            "golden_snapshot_updated_at": None,
            "admin_rows_count": 0,
            "personas": {},
            "chapters": {},
        }

    manifest = _load_manifest(manifest_path)
    chapters_meta = manifest.get("chapters", {})

    conn = sqlite3.connect(str(DB_PATH), timeout=15.0)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    admin_rows = cur.execute("SELECT COUNT(*) FROM users WHERE email LIKE 'admin@%'").fetchone()[0]
    chapters_out: dict[str, Any] = {}
    for ch in VALID_CHAPTERS:
        cinfo = chapters_meta.get(ch)
        if not cinfo:
            continue
        pid = cinfo["project_id"]
        ws_path = Path(cinfo["workspace_path"])
        git_state = _git_inspect_workspace(ws_path)
        msg_cnt = cur.execute("SELECT COUNT(*) FROM messages WHERE project_id = ?", (pid,)).fetchone()[0]
        topic_cnt = cur.execute(
            "SELECT COUNT(*) FROM webchat_topic WHERE project_id = ? AND deleted_at IS NULL", (pid,)
        ).fetchone()[0]
        art_cnt = cur.execute(
            "SELECT COUNT(*) FROM artifact WHERE scope_kind = 'project' AND scope_ref = ? AND deleted_at IS NULL",
            (pid,),
        ).fetchone()[0]
        running_agents = [
            r["slug"]
            for r in cur.execute(
                "SELECT slug FROM agents WHERE project_id = ? AND phase = 'running' ORDER BY slug", (pid,)
            ).fetchall()
        ]
        hist = _reset_history.get(f"{cid}:{ch}", _reset_history.get(ch, {}))
        chapters_out[ch] = {
            **cinfo,
            **git_state,
            "message_count": msg_cnt,
            "topic_count": topic_cnt,
            "artifact_count": art_cnt,
            "running_agents": running_agents,
            "last_reset_at": hist.get("last_reset_at"),
            "last_reset_duration_ms": hist.get("last_reset_duration_ms"),
        }
    conn.close()

    golden_mtime = None
    if golden_db.exists():
        golden_mtime = datetime.datetime.fromtimestamp(
            golden_db.stat().st_mtime, tz=datetime.timezone.utc
        ).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "ok": True,
        "campaign": cid,
        "golden_snapshot_exists": golden_db.exists(),
        "golden_snapshot_updated_at": golden_mtime,
        "admin_rows_count": admin_rows,
        "personas": manifest.get("personas", {}),
        "chapters": chapters_out,
    }


@app.post("/api/state/snapshot")
def freeze_golden_snapshot(
    campaign: str | None = Query(default=None),
    x_oase_state_token: str | None = Header(default=None),
) -> dict[str, Any]:
    _check_auth(x_oase_state_token)
    cid, manifest_path, snap_dir, golden_db = _campaign_paths(campaign)
    t0 = time.perf_counter()
    with _reset_lock:
        snap_dir.mkdir(parents=True, exist_ok=True)
        tmp_db = snap_dir / "golden-hub.db.tmp"
        if tmp_db.exists():
            tmp_db.unlink()
        src_conn = sqlite3.connect(str(DB_PATH), timeout=30.0)
        dst_conn = sqlite3.connect(str(tmp_db))
        src_conn.backup(dst_conn)
        dst_conn.close()
        src_conn.close()
        tmp_db.replace(golden_db)
        if manifest_path.exists():
            shutil.copy2(manifest_path, snap_dir / "pilot-chapters-manifest.json")
    elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 1)
    return {
        "ok": True,
        "campaign": cid,
        "golden_db": str(golden_db),
        "duration_ms": elapsed_ms,
        "frozen_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


@app.post("/api/state/chapters/{chapter}/reset")
def reset_single_chapter(
    chapter: str,
    campaign: str | None = Query(default=None),
    x_oase_state_token: str | None = Header(default=None),
) -> dict[str, Any]:
    _check_auth(x_oase_state_token)
    if chapter not in VALID_CHAPTERS:
        raise HTTPException(status_code=400, detail=f"Invalid chapter '{chapter}'. Expected ch0..ch7.")

    cid, manifest_path, _, golden_db = _campaign_paths(campaign)
    manifest = _load_manifest(manifest_path)
    cinfo = manifest.get("chapters", {}).get(chapter)
    if not cinfo:
        raise HTTPException(status_code=404, detail=f"Chapter '{chapter}' missing from manifest.")

    t0 = time.perf_counter()
    with _reset_lock:
        pid = cinfo["project_id"]
        ws_path = Path(cinfo["workspace_path"])
        git_res = _git_reset_workspace(ws_path, chapter)
        db_stats = _restore_projects_from_golden([pid], golden_db)[pid]
        elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 1)
        now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        _reset_history[f"{cid}:{chapter}"] = {
            "last_reset_at": now_iso,
            "last_reset_duration_ms": elapsed_ms,
        }

    return {
        "ok": True,
        "campaign": cid,
        "chapter": chapter,
        "project_id": pid,
        "slug": cinfo["slug"],
        "duration_ms": elapsed_ms,
        "reset_at": now_iso,
        **git_res,
        **db_stats,
    }


@app.post("/api/state/reset-all")
def reset_all_chapters(
    campaign: str | None = Query(default=None),
    x_oase_state_token: str | None = Header(default=None),
) -> dict[str, Any]:
    _check_auth(x_oase_state_token)
    cid, manifest_path, _, golden_db = _campaign_paths(campaign)
    manifest = _load_manifest(manifest_path)
    chapters_meta = manifest.get("chapters", {})

    t0 = time.perf_counter()
    with _reset_lock:
        pids: list[str] = []
        git_results: dict[str, Any] = {}
        for ch in VALID_CHAPTERS:
            cinfo = chapters_meta.get(ch)
            if not cinfo:
                continue
            pids.append(cinfo["project_id"])
            git_results[ch] = _git_reset_workspace(Path(cinfo["workspace_path"]), ch)

        db_stats = _restore_projects_from_golden(pids, golden_db)
        elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 1)
        now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        per_chapter = {}
        for ch in VALID_CHAPTERS:
            cinfo = chapters_meta.get(ch)
            if not cinfo:
                continue
            pid = cinfo["project_id"]
            _reset_history[f"{cid}:{ch}"] = {
                "last_reset_at": now_iso,
                "last_reset_duration_ms": elapsed_ms,
            }
            per_chapter[ch] = {
                "project_id": pid,
                "slug": cinfo["slug"],
                **git_results[ch],
                **db_stats.get(pid, {}),
            }

    return {
        "ok": True,
        "campaign": cid,
        "chapters_reset": len(per_chapter),
        "duration_ms": elapsed_ms,
        "reset_at": now_iso,
        "chapters": per_chapter,
    }

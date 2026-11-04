#!/usr/bin/env python3
"""Clone a standalone duplicate PCSK9 pilot grove on Scion Hub (e.g. `pcsk9-oral-sandbox`)
without modifying `pcsk9-oral-live-v2` or `io-cold-to-hot`.

Usage (on `scion-hub-oase` as `scion` user):
  sudo -u scion python3 /home/scion/oase-workshop/scripts/clone-pcsk9-pilot.py --slug pcsk9-oral-sandbox
  sudo -u scion python3 /home/scion/oase-workshop/scripts/clone-pcsk9-pilot.py --slug pcsk9-oral-sandbox --start-lead
  sudo -u scion python3 /home/scion/oase-workshop/scripts/clone-pcsk9-pilot.py --delete pcsk9-oral-sandbox
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import re
import shutil
import sqlite3
import subprocess
from pathlib import Path

PROTECTED_SLUGS = {"pcsk9-oral-live-v2", "io-cold-to-hot"}
HUB_DIR = Path("/home/scion/.scion")
DB_PATH = HUB_DIR / "hub.db"
PROJECTS_DIR = HUB_DIR / "projects"
SOURCE_PROJECT_DIR = PROJECTS_DIR / "pcsk9-oral-live-v2"


def _load_graph_helper():
    script_path = Path(__file__).resolve().parent / "populate-scion-agent-graph.py"
    spec = importlib.util.spec_from_file_location("pop_graph", script_path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def delete_sandbox_grove(slug: str) -> int:
    if slug in PROTECTED_SLUGS:
        raise SystemExit(f"REFUSED: '{slug}' is a protected canonical workshop pilot.")
    # Stop any containers matching scion-<slug>-*
    out = subprocess.check_output(["sudo", "docker", "ps", "-a", "--format", "{{.Names}}"], text=True)
    to_rm = [n.strip() for n in out.splitlines() if n.strip().startswith(f"scion-{slug}-")]
    if to_rm:
        subprocess.run(["sudo", "docker", "rm", "-f", *to_rm], check=False)
        print(f"[docker] Removed {len(to_rm)} container(s) for {slug}")

    conn = sqlite3.connect(str(DB_PATH), timeout=30.0)
    cur = conn.cursor()
    cur.execute("SELECT id FROM projects WHERE slug = ? OR name = ?", (slug, slug))
    rows = [r[0] for r in cur.fetchall()]
    mod = _load_graph_helper()
    for pid in rows:
        mod.remove_project_from_hub_db(cur, pid)
        print(f"[sqlite] Deleted project {slug} ({pid}) from hub.db")
    conn.commit()
    conn.close()

    proj_dir = PROJECTS_DIR / slug
    if proj_dir.exists():
        shutil.rmtree(proj_dir)
        print(f"[fs] Removed {proj_dir}")
    for cfg in (HUB_DIR / "project-configs").glob(f"{slug}__*"):
        shutil.rmtree(cfg, ignore_errors=True)
    print(f"[ok] Cleanly removed sandbox pilot '{slug}'.")
    return 0


def clone_pcsk9_grove(slug: str, start_lead: bool) -> int:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,48}", slug):
        raise SystemExit("ERROR: --slug must be lowercase alphanumeric + hyphens (3..49 chars).")
    if slug in PROTECTED_SLUGS:
        raise SystemExit(f"REFUSED: '{slug}' is an active canonical pilot; pick a new slug like 'pcsk9-oral-sandbox'.")
    if not SOURCE_PROJECT_DIR.exists():
        raise SystemExit(f"ERROR: Source project missing at {SOURCE_PROJECT_DIR}")

    dest_dir = PROJECTS_DIR / slug
    if dest_dir.exists():
        raise SystemExit(f"ERROR: {dest_dir} already exists. Run with --delete {slug} first if you want a fresh copy.")

    dest_dir.mkdir(parents=True, exist_ok=True)
    # 1. Stage t=0 seed, .oase schemas/thresholds, and 41 OASE verification skills
    for item in ("seed", "skills", ".gitignore"):
        src = SOURCE_PROJECT_DIR / item
        if src.is_dir():
            shutil.copytree(src, dest_dir / item)
        elif src.is_file():
            shutil.copy2(src, dest_dir / item)

    # Copy clean .oase config (schemas + thresholds) without completed run state
    src_oase = SOURCE_PROJECT_DIR / ".oase"
    dst_oase = dest_dir / ".oase"
    dst_oase.mkdir(parents=True, exist_ok=True)
    for item in ("thresholds.yaml", "schemas", "workorders"):
        s = src_oase / item
        if s.is_dir():
            shutil.copytree(s, dst_oase / item)
        elif s.is_file():
            shutil.copy2(s, dst_oase / item)

    for sub in ("findings", "gates", "program-state", "executive", "raw"):
        (dest_dir / sub).mkdir(parents=True, exist_ok=True)

    # 2. Initialize git + Scion project & link to Hub
    env = os.environ.copy()
    env["HOME"] = "/home/scion"
    subprocess.run(["git", "init", "-q"], cwd=str(dest_dir), env=env, check=True)
    subprocess.run(["git", "config", "user.email", "scion@workshop.local"], cwd=str(dest_dir), env=env, check=True)
    subprocess.run(["git", "config", "user.name", "Scion Seed"], cwd=str(dest_dir), env=env, check=True)
    subprocess.run(["scion", "init", "--non-interactive"], cwd=str(dest_dir), env=env, check=True)

    # Copy the 17 OASE specialist templates into the new project's .scion/templates
    src_tpl = SOURCE_PROJECT_DIR / ".scion" / "templates"
    dst_tpl = dest_dir / ".scion" / "templates"
    if src_tpl.exists():
        shutil.copytree(src_tpl, dst_tpl, dirs_exist_ok=True)

    subprocess.run(["git", "add", "."], cwd=str(dest_dir), env=env, check=True)
    subprocess.run(["git", "commit", "-q", "-m", f"Initialize t=0 PCSK9 seed for {slug}"], cwd=str(dest_dir), env=env, check=True)
    subprocess.run(["scion", "hub", "link", "--non-interactive"], cwd=str(dest_dir), env=env, check=True)

    # 3. Look up new project UUID in hub.db, grant RBAC to all workshop users, and register 17 templates + 4-tier DAG
    conn = sqlite3.connect(str(DB_PATH), timeout=30.0)
    cur = conn.cursor()
    cur.execute("SELECT id FROM projects WHERE slug = ? OR name = ? ORDER BY created DESC LIMIT 1", (slug, slug))
    row = cur.fetchone()
    if not row:
        raise RuntimeError(f"Project '{slug}' was not found in hub.db after 'scion hub link'.")
    new_pid = row[0]

    cur.execute("SELECT id, email FROM users WHERE email LIKE 'oase-sarah@%'")
    sarah_row = cur.fetchone()
    if not sarah_row:
        raise RuntimeError("Missing oase-sarah user in hub.db")
    sarah_id, sarah_email = sarah_row[0], sarah_row[1]

    # Add all workshop personas to project_members so everyone in the room can see & message it
    cur.execute("SELECT id, email FROM users")
    for uid, uemail in cur.fetchall():
        role = "admin" if ("sarah" in uemail or "admin@" in uemail) else "member"
        cur.execute(
            "INSERT OR IGNORE INTO project_members (project_id, user_id, role, added_by, joined_at) VALUES (?, ?, ?, ?, datetime('now'))",
            (new_pid, uid, role, sarah_id),
        )

    mod = _load_graph_helper()
    kickoff_msgs = [
        ("sarah", "controller", "instruction", f"[Live Workshop Sandbox `{slug}`] Initialize t=0 PCSK9 seed (`seed/pcsk9-oral/campaign-seed.json`), verify `oase doctor` (78/78), and stand by for Stage 0 `WO-001` tournament."),
        ("controller", "bootstrapper", "instruction", "Verify `/workspace/seed/pcsk9-oral/campaign-seed.json` and stage `.oase/thresholds.yaml`."),
        ("bootstrapper", "controller", "state-change", "`oase doctor --json` 78/78 PASS. 41 skills and 17 templates staged at `t=0`."),
        ("controller", "science-program-lead", "instruction", f"Sandbox `{slug}` online at `t=0` — ready for live workshop prompts."),
    ]
    mod.populate_project_hierarchy_and_messages(
        cur=cur,
        project_id=new_pid,
        project_slug=slug,
        sarah_id=sarah_id,
        sarah_email=sarah_email,
        inter_agent_msgs=kickoff_msgs,
    )
    conn.commit()
    conn.close()

    if start_lead:
        subprocess.run(
            [
                "scion",
                "start",
                "science-program-lead",
                "--non-interactive",
                "--harness",
                "antigravity",
                f"You are science-program-lead in live workshop grove '{slug}' (t=0 PCSK9 seed). Stand by for Webchat instructions and reply via scion message.",
            ],
            cwd=str(dest_dir),
            env=env,
            check=False,
        )

    print(f"[SUCCESS] Cloned PCSK9 pilot -> {slug} (UUID: {new_pid})")
    print(f"  Scion UI URL : /projects/{new_pid}")
    print(f"  Workspace    : {dest_dir}")
    print(f"  Teardown cmd : sudo -u scion python3 /home/scion/oase-workshop/scripts/clone-pcsk9-pilot.py --delete {slug}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Clone or delete a standalone PCSK9 workshop sandbox grove.")
    ap.add_argument("--slug", default="pcsk9-oral-sandbox", help="New project slug (default: pcsk9-oral-sandbox)")
    ap.add_argument("--start-lead", action="store_true", help="Also launch a live science-program-lead container")
    ap.add_argument("--delete", metavar="SLUG", help="Cleanly delete a sandbox grove created during the workshop")
    args = ap.parse_args()
    if args.delete:
        return delete_sandbox_grove(args.delete.strip())
    return clone_pcsk9_grove(args.slug.strip(), start_lead=args.start_lead)


if __name__ == "__main__":
    raise SystemExit(main())

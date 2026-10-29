#!/usr/bin/env python3
"""Crop the 5 Gemini 3.8 Live Avatar prebuilt portraits to matching square headshots
and optionally propagate them to:
  1. site-template/assets/avatars/{key}.jpg (512x512) & {key}_40.jpg (40x40 <= 920 B)
  2. Scion Hub SQLite users.avatar_url (live hub.db + golden-pilot snapshot on GCE VM)
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPO_AVATARS = REPO_ROOT / "site-template" / "assets" / "avatars"

CAST_SPECS = [
    ("sarah", "ingrid.png", "Dr. Sarah Chen", "oase-sarah"),
    ("marcus", "sam.png", "Dr. Marcus Vance", "oase-marcus"),
    ("elena", "kira.png", "Dr. Elena Rostova", "oase-elena"),
    ("raj", "jay.png", "Dr. Raj Patel", "oase-raj"),
    ("claire", "vera.png", "Dr. Claire Moreau", "oase-claire"),
]

# Verified 1:1 crown-to-collar crop on 720x1280 portrait PNGs (676x676 at x=22..698, y=155..831)
CROP_BOX = (22, 155, 698, 831)


def generate_crops(
    prebuilt_dir: Path | None,
    repo_avatars: Path,
    out_dir: Path,
) -> dict[str, str]:
    from PIL import Image

    repo_avatars.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    compact_uris: dict[str, str] = {}

    for key, src_name, display_name, _slug in CAST_SPECS:
        if prebuilt_dir and (prebuilt_dir / src_name).exists():
            im = Image.open(prebuilt_dir / src_name).convert("RGB")
            sq = im.crop(CROP_BOX) if im.size == (720, 1280) else im
        elif (repo_avatars / f"{key}.jpg").exists():
            sq = Image.open(repo_avatars / f"{key}.jpg").convert("RGB")
        else:
            raise FileNotFoundError(
                f"Portrait source not found for {key}: pass --prebuilt-dir containing {src_name}"
            )

        im512 = sq.resize((512, 512), Image.Resampling.LANCZOS)
        im512.save(repo_avatars / f"{key}.jpg", format="JPEG", quality=92, optimize=True)
        im512.save(out_dir / f"{key}_avatar.jpg", format="JPEG", quality=92, optimize=True)

        im40 = sq.resize((40, 40), Image.Resampling.LANCZOS)
        raw40 = b""
        for q in (66, 60, 54, 48):
            buf = io.BytesIO()
            im40.save(buf, format="JPEG", quality=q, optimize=True)
            raw40 = buf.getvalue()
            if len(raw40) <= 920 or q == 48:
                break
        (repo_avatars / f"{key}_40.jpg").write_bytes(raw40)
        (out_dir / f"{key}_40.jpg").write_bytes(raw40)
        uri = "data:image/jpeg;base64," + base64.b64encode(raw40).decode("ascii")
        compact_uris[key] = uri
        print(
            f"[CROP] {key} ({display_name}): 512px={(repo_avatars / f'{key}.jpg').stat().st_size}B, "
            f"40px={len(raw40)}B (uri={len(uri)} chars)",
            flush=True,
        )

    (out_dir / "compact_avatar_uris.json").write_text(
        json.dumps(compact_uris, indent=2), encoding="utf-8"
    )
    return compact_uris


def update_scion_hub_db(
    compact_uris: dict[str, str],
    gcp_project: str,
    workshop_domain: str,
    scion_vm: str,
    zone: str,
    gcloud_config: str | None,
) -> None:
    payload = {f"{slug}@{workshop_domain}": compact_uris[key] for key, _, _, slug in CAST_SPECS}
    payload_b64 = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")
    remote_cmd = f"""sudo python3 - <<'PY'
import base64, json, os, sqlite3

mapping = json.loads(base64.b64decode('{payload_b64}').decode('utf-8'))
db_paths = [
    '/home/scion/.scion/hub.db',
    '/home/scion/.scion/snapshots/golden-pilot/golden-hub.db',
    '/home/scion/.scion/snapshots/golden-hub.db',
]
for dbp in db_paths:
    if not os.path.exists(dbp):
        continue
    con = sqlite3.connect(dbp)
    cur = con.cursor()
    for email, uri in mapping.items():
        cur.execute('UPDATE users SET avatar_url = ? WHERE email = ?', (uri, email))
    con.commit()
    rows = list(cur.execute('SELECT email, length(avatar_url) FROM users ORDER BY email'))
    con.close()
    print('UPDATED DB:', dbp, rows)
PY"""
    env = os.environ.copy()
    if gcloud_config:
        env["CLOUDSDK_ACTIVE_CONFIG_NAME"] = gcloud_config
    subprocess.run(
        [
            "gcloud",
            "compute",
            "ssh",
            scion_vm,
            f"--zone={zone}",
            f"--project={gcp_project}",
            f"--command={remote_cmd}",
        ],
        env=env,
        check=True,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--prebuilt-dir",
        type=Path,
        default=None,
        help="Optional directory with 720x1280 portrait PNGs (ingrid.png, sam.png, kira.png, jay.png, vera.png); falls back to existing site-template/assets/avatars/*.jpg.",
    )
    parser.add_argument(
        "--repo-avatars-dir",
        type=Path,
        default=DEFAULT_REPO_AVATARS,
        help="Destination directory for checked-in avatar JPEGs.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("/tmp/oase-avatars-work"),
        help="Working directory for compact_avatar_uris.json.",
    )
    parser.add_argument(
        "--update-hub-db",
        action="store_true",
        help="Push compact 40x40 base64 data URIs into Scion Hub SQLite users.avatar_url.",
    )
    parser.add_argument("--gcp-project", default=os.environ.get("GCP_PROJECT_ID", ""))
    parser.add_argument("--workshop-domain", default=os.environ.get("WORKSHOP_DOMAIN", ""))
    parser.add_argument("--scion-vm", default=os.environ.get("SCION_VM_NAME", "scion-hub-oase"))
    parser.add_argument("--zone", default=os.environ.get("ZONE", "us-central1-c"))
    parser.add_argument("--gcloud-config", default=os.environ.get("GCLOUD_CONFIG", ""))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    uris = generate_crops(args.prebuilt_dir, args.repo_avatars_dir, args.out_dir)
    if args.update_hub_db:
        if not args.gcp_project or not args.workshop_domain:
            raise SystemExit(
                "Error: --update-hub-db requires --gcp-project (or GCP_PROJECT_ID) and --workshop-domain (or WORKSHOP_DOMAIN)."
            )
        update_scion_hub_db(
            compact_uris=uris,
            gcp_project=args.gcp_project,
            workshop_domain=args.workshop_domain,
            scion_vm=args.scion_vm,
            zone=args.zone,
            gcloud_config=args.gcloud_config or None,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

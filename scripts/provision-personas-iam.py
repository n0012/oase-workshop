#!/usr/bin/env python3
"""Grant Cloud Run IAP access to the 5 dedicated OASE Discovery Pod scientist personas.

This script is intentionally generic and parameterized via CLI flags or environment
variables (.env) so the same 5-persona discovery pod (`oase-sarah`, `oase-marcus`,
`oase-elena`, `oase-raj`, `oase-claire`) can be bound to any GCP project and domain.

Usage:
  python3 scripts/provision-personas-iam.py \
    --project-id "$GCP_PROJECT_ID" \
    --workshop-domain "$WORKSHOP_DOMAIN" \
    --region "${REGION:-us-central1}" \
    --iap-service "${SCION_IAP_SERVICE:-scion-hub-iap-proxy}"
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

PERSONAS = [
    ("oase-sarah", "Dr. Sarah Chen", "Program Lead"),
    ("oase-marcus", "Dr. Marcus Vance", "Computational Biologist"),
    ("oase-elena", "Dr. Elena Rostova", "Structural Biologist"),
    ("oase-raj", "Dr. Raj Patel", "Medicinal Chemist"),
    ("oase-claire", "Dr. Claire Moreau", "DMPK & Safety Lead"),
]


def run_cmd(cmd: list[str], dry_run: bool) -> None:
    print("+", " ".join(cmd))
    if dry_run:
        return
    subprocess.run(cmd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-id",
        default=os.environ.get("GCP_PROJECT_ID", ""),
        help="Target GCP project ID hosting the Cloud Run IAP service(s).",
    )
    parser.add_argument(
        "--workshop-domain",
        default=os.environ.get("WORKSHOP_DOMAIN", ""),
        help="Cloud Identity / Google Workspace domain for the 5 oase-* personas.",
    )
    parser.add_argument(
        "--region",
        default=os.environ.get("REGION", "us-central1"),
        help="Cloud Run region (default: us-central1).",
    )
    parser.add_argument(
        "--iap-service",
        action="append",
        dest="iap_services",
        help="Cloud Run service name protected by IAP (repeatable).",
    )
    parser.add_argument(
        "--prefix",
        default=os.environ.get("PERSONA_PREFIX", "oase-"),
        help="Account prefix before scientist given name (default: oase-).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print gcloud IAM binding commands without executing them.",
    )
    args = parser.parse_args()

    if not args.project_id or not args.workshop_domain:
        parser.error("--project-id and --workshop-domain are required (or set GCP_PROJECT_ID and WORKSHOP_DOMAIN).")

    services = args.iap_services or [os.environ.get("SCION_IAP_SERVICE", "scion-hub-iap-proxy")]

    for svc in services:
        for base_slug, display_name, role_title in PERSONAS:
            given = base_slug.removeprefix("oase-")
            email = f"{args.prefix}{given}@{args.workshop_domain}"
            print(f"[iam] Binding {display_name} ({role_title}) -> user:{email} on {svc}")
            cmd = [
                "gcloud",
                "alpha",
                "iap",
                "web",
                "add-iam-policy-binding",
                "--resource-type=cloud-run",
                f"--service={svc}",
                f"--region={args.region}",
                f"--project={args.project_id}",
                f"--member=user:{email}",
                "--role=roles/iap.httpsResourceAccessor",
                "--quiet",
            ]
            run_cmd(cmd, args.dry_run)

    print(f"[ok] Bound {len(PERSONAS)} scientist personas across {len(services)} IAP service(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

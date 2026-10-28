#!/usr/bin/env python3
"""Repeatable Argolis GCP Project & Workshop Identity Provisioner for GCP-OASE.

Creates (or reconciles) an isolated GCP project under an Organization, binds
Owner/Editor IAM roles, enables required IAM/Resource Manager/Vertex APIs, and
provisions the isolated workshop Service Account (`scion-default-agent`).

Usage:
  python3 scripts/provision-argolis-project.py \
    --project-id my-oase-workshop \
    --org-id 123456789012 \
    --admin-user admin@example.com \
    --billing-account billingAccounts/012345-6789AB-CDEF01
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import google.auth
from google.auth.transport.requests import Request
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]
WORKSHOP_SA_ROLES = [
    "roles/aiplatform.user",
    "roles/storage.objectAdmin",
    "roles/logging.logWriter",
]

REQUIRED_APIS = [
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "serviceusage.googleapis.com",
]

BILLING_DEPENDENT_APIS = [
    "aiplatform.googleapis.com",
    "compute.googleapis.com",
    "run.googleapis.com",
    "iap.googleapis.com",
    "cloudbuild.googleapis.com",
    "storage.googleapis.com",
    "bigquery.googleapis.com",
    "texttospeech.googleapis.com",
    "artifactregistry.googleapis.com",
]


def api_call(
    token: str,
    method: str,
    url: str,
    body: dict | None = None,
    quota_project: str | None = None,
) -> tuple[int, dict]:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    if quota_project:
        headers["x-goog-user-project"] = quota_project
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8")
        try:
            return exc.code, json.loads(raw)
        except Exception:
            return exc.code, {"raw": raw}


def ensure_project(token: str, project_id: str, org_id: str) -> dict:
    status, data = api_call(
        token,
        "GET",
        f"https://cloudresourcemanager.googleapis.com/v3/projects/{project_id}",
    )
    if status == 200 and data.get("state") == "ACTIVE":
        print(f"[ok] Project {project_id} exists and is ACTIVE ({data.get('name')})")
        return data

    print(f"[..] Creating net-new project {project_id} under organizations/{org_id}...")
    status, op = api_call(
        token,
        "POST",
        "https://cloudresourcemanager.googleapis.com/v3/projects",
        {
            "projectId": project_id,
            "displayName": "OASE Workshop Environment",
            "parent": f"organizations/{org_id}",
        },
    )
    if status not in (200, 201):
        raise RuntimeError(f"Failed to create project {project_id}: HTTP {status} {op}")

    op_name = op.get("name", "")
    for _ in range(15):
        time.sleep(2)
        _, poll = api_call(
            token,
            "GET",
            f"https://cloudresourcemanager.googleapis.com/v3/{op_name}",
        )
        if poll.get("done"):
            resp = poll.get("response", {})
            print(f"[ok] Created project {project_id} ({resp.get('name')})")
            return resp
    raise RuntimeError(f"Timed out waiting for project creation operation {op_name}")


def ensure_role_bindings(
    token: str, project_id: str, role_to_members: dict[str, list[str]]
) -> None:
    for attempt in range(4):
        status, policy = api_call(
            token,
            "POST",
            f"https://cloudresourcemanager.googleapis.com/v1/projects/{project_id}:getIamPolicy",
            {},
        )
        if status != 200:
            raise RuntimeError(f"getIamPolicy failed: HTTP {status} {policy}")

        bindings = policy.get("bindings", [])
        added: list[str] = []
        for role, members in role_to_members.items():
            binding = next((b for b in bindings if b.get("role") == role), None)
            if binding is None:
                binding = {"role": role, "members": []}
                bindings.append(binding)
            for m in members:
                if m not in binding["members"]:
                    binding["members"].append(m)
                    added.append(f"{role} -> {m}")

        if not added:
            print(f"[ok] IAM bindings already up to date on {project_id}")
            return

        status, updated = api_call(
            token,
            "POST",
            f"https://cloudresourcemanager.googleapis.com/v1/projects/{project_id}:setIamPolicy",
            {"policy": {"bindings": bindings, "etag": policy.get("etag")}},
        )
        if status == 200:
            print(f"[ok] Granted IAM bindings on {project_id}: {added}")
            return
        if status == 409 and attempt < 3:
            time.sleep(1.5 * (attempt + 1))
            continue
        raise RuntimeError(f"setIamPolicy failed: HTTP {status} {updated}")


def enable_apis(token: str, project_num: str, apis: list[str]) -> bool:
    status, op = api_call(
        token,
        "POST",
        f"https://serviceusage.googleapis.com/v1/projects/{project_num}/services:batchEnable",
        {"serviceIds": apis},
    )
    if status == 200:
        print(f"[ok] Enabled APIs on projects/{project_num}: {', '.join(apis)}")
        return True
    msg = op.get("error", {}).get("message", str(op))
    print(f"[warn] Could not batchEnable {apis}: HTTP {status} — {msg}")
    return False


def ensure_service_account(
    token: str, project_id: str, account_id: str, display_name: str
) -> str:
    sa_email = f"{account_id}@{project_id}.iam.gserviceaccount.com"
    status, data = api_call(
        token,
        "GET",
        f"https://iam.googleapis.com/v1/projects/{project_id}/serviceAccounts/{sa_email}",
        quota_project=project_id,
    )
    if status == 200:
        print(f"[ok] Service Account {sa_email} exists ({data.get('uniqueId')})")
        return sa_email

    status, created = api_call(
        token,
        "POST",
        f"https://iam.googleapis.com/v1/projects/{project_id}/serviceAccounts",
        {
            "accountId": account_id,
            "serviceAccount": {
                "displayName": display_name,
                "description": "Isolated workshop agent identity for GCP-OASE",
            },
        },
        quota_project=project_id,
    )
    if status not in (200, 201):
        raise RuntimeError(f"Failed to create SA {sa_email}: HTTP {status} {created}")
    print(f"[ok] Created Service Account {created.get('email')} ({created.get('uniqueId')})")
    return created["email"]


def try_link_billing(
    token: str, project_id: str, billing_account: str
) -> bool:
    status, info = api_call(
        token,
        "GET",
        f"https://cloudbilling.googleapis.com/v1/projects/{project_id}/billingInfo",
    )
    if status == 200 and info.get("billingEnabled"):
        print(f"[ok] Billing already linked: {info.get('billingAccountName')}")
        return True

    status, res = api_call(
        token,
        "PUT",
        f"https://cloudbilling.googleapis.com/v1/projects/{project_id}/billingInfo",
        {"billingAccountName": billing_account},
    )
    if status == 200 and res.get("billingEnabled"):
        print(f"[ok] Linked {project_id} to {billing_account}")
        return True

    print(
        f"[info] Service account lacks roles/billing.user on {billing_account} (HTTP {status}).\n"
        f"       To link billing interactively as the Argolis Org Admin, run:\n"
        f"         gcloud billing projects link {project_id} --billing-account={billing_account.split('/')[-1]}"
    )
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-id",
        default=os.environ.get("OASE_WORKSHOP_PROJECT", "oase-workshop-demo"),
    )
    parser.add_argument(
        "--org-id",
        default=os.environ.get("OASE_ORG_ID", ""),
    )
    parser.add_argument(
        "--admin-user",
        default=os.environ.get("OASE_ADMIN_USER", ""),
        help="Optional user email to grant roles/owner (e.g. admin@<domain>)",
    )
    parser.add_argument(
        "--billing-account",
        default=os.environ.get("OASE_BILLING_ACCOUNT", ""),
        help="Optional billingAccounts/<ID> to link",
    )
    parser.add_argument(
        "--credentials",
        default=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", ""),
        help="Optional path to a service-account JSON key file (defaults to ADC).",
    )
    args = parser.parse_args()

    if not args.org_id:
        print(
            "[error] --org-id (or OASE_ORG_ID) is required to provision an Argolis project.",
            file=sys.stderr,
        )
        return 1

    quota_fallback = None
    caller_email = None
    if args.credentials:
        creds_path = Path(args.credentials).expanduser()
        if not creds_path.is_file():
            print(f"[error] Credentials file not found: {creds_path}", file=sys.stderr)
            return 1
        creds = service_account.Credentials.from_service_account_file(
            str(creds_path), scopes=SCOPES
        )
        quota_fallback = creds.project_id
        caller_email = creds.service_account_email
    else:
        creds, quota_fallback = google.auth.default(scopes=SCOPES)
        caller_email = getattr(creds, "service_account_email", None)

    creds.refresh(Request())
    token = creds.token

    proj = ensure_project(token, args.project_id, args.org_id)
    project_num = proj["name"].split("/")[-1]

    enable_apis(token, project_num, REQUIRED_APIS)
    sa_email = ensure_service_account(
        token,
        args.project_id,
        account_id="scion-default-agent",
        display_name="Scion Default Workshop Agent",
    )

    owners: list[str] = []
    if caller_email:
        owners.append(f"serviceAccount:{caller_email}")
    if args.admin_user:
        owners.append(f"user:{args.admin_user}")

    role_map: dict[str, list[str]] = {
        role: [f"serviceAccount:{sa_email}"] for role in WORKSHOP_SA_ROLES
    }
    if owners:
        role_map["roles/owner"] = owners
    ensure_role_bindings(token, args.project_id, role_map)

    billing_ok = False
    if args.billing_account:
        billing_ok = try_link_billing(token, args.project_id, args.billing_account)
    if billing_ok:
        enable_apis(token, project_num, BILLING_DEPENDENT_APIS)

    summary = {
        "project_id": args.project_id,
        "project_number": project_num,
        "organization": f"organizations/{args.org_id}",
        "workshop_service_account": sa_email,
        "workshop_sa_roles": WORKSHOP_SA_ROLES,
        "quota_project_fallback": quota_fallback,
        "billing_linked": billing_ok,
    }
    print("\n=== Provisioning Summary ===")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

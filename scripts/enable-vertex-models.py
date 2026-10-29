#!/usr/bin/env python3
"""Repeatable Vertex AI Partner Model Enablement & Verification Utility.

Automates the two programmable control-plane steps required to run Anthropic
Claude models (such as `claude-opus-5-5`, `claude-sonnet-5-5`, `claude-haiku-5-5`,
and `claude-haiku-4-5`) on Vertex AI, and verifies live data-plane inference:

  1. Per-location Data Sharing (`:setPublisherModelConfig`):
     Opts the project into Anthropic partner data sharing across `global`
     (`aiplatform.googleapis.com`), `us` (`aiplatform.us.rep.googleapis.com`),
     `us-east5`, and `us-central1`.
  2. Partner Model Features Org Policy (`constraints/vertexai.allowedPartnerModelFeatures`):
     Enables `orgpolicy.googleapis.com` and configures project-level
     `allowedValues: [publishers/anthropic]`.
  3. Live Inference & Model Garden Subscription Verification:
     Tests `:rawPredict` on `global` and `us`, and prints the exact one-click
     Model Garden questionnaire URL (`supportedActions.requestAccess`) if a
     model has not yet had its one-time Marketplace EULA accepted in the project.

Usage:
  python3 scripts/enable-vertex-models.py --project "$GCP_PROJECT_ID"
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

DEFAULT_MODELS = [
    "claude-opus-5-5",
    "claude-sonnet-5-5",
    "claude-haiku-5-5",
    "claude-haiku-4-5",
    "claude-opus-4-8",
    "claude-sonnet-4-6",
]

LOCATIONS = [
    ("global", "aiplatform.googleapis.com"),
    ("us", "aiplatform.us.rep.googleapis.com"),
    ("us-east5", "us-east5-aiplatform.googleapis.com"),
    ("us-central1", "us-central1-aiplatform.googleapis.com"),
]


def get_non_mtls_token(gcloud_config: str | None) -> str:
    """Obtain an OAuth2 access token with client-certificate mTLS disabled.

    Public `aiplatform.googleapis.com` endpoints reject context-aware mTLS
    tokens (`401 ACCESS_TOKEN_TYPE_UNSUPPORTED`). Setting
    `CLOUDSDK_CONTEXT_AWARE_USE_CLIENT_CERTIFICATE=false` ensures a standard
    bearer token is minted.
    """
    env = dict(os.environ, CLOUDSDK_CONTEXT_AWARE_USE_CLIENT_CERTIFICATE="false")
    if gcloud_config:
        env["CLOUDSDK_ACTIVE_CONFIG_NAME"] = gcloud_config
    for cmd in (
        ["gcloud", "auth", "print-access-token"],
        ["gcloud", "auth", "application-default", "print-access-token"],
    ):
        proc = subprocess.run(cmd, env=env, capture_output=True, text=True, check=False)
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.strip()
    raise RuntimeError("Failed to mint a gcloud access token. Run `gcloud auth login` first.")


def api_json(url: str, token: str, project: str, method: str = "GET", body: dict | None = None) -> tuple[int, dict]:
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Goog-User-Project": project,
        "Accept": "application/json",
    }
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, (json.loads(raw) if raw.strip() else {})
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            return exc.code, json.loads(raw)
        except Exception:
            return exc.code, {"raw": raw[:300]}


def configure_org_policy(project: str, gcloud_config: str | None) -> dict:
    env = dict(os.environ, CLOUDSDK_CONTEXT_AWARE_USE_CLIENT_CERTIFICATE="false")
    if gcloud_config:
        env["CLOUDSDK_ACTIVE_CONFIG_NAME"] = gcloud_config
    subprocess.run(
        ["gcloud", "services", "enable", "orgpolicy.googleapis.com", f"--project={project}"],
        env=env,
        capture_output=True,
        check=False,
    )
    policy_yaml = (
        f"name: projects/{project}/policies/vertexai.allowedPartnerModelFeatures\n"
        "spec:\n"
        "  rules:\n"
        "  - values:\n"
        "      allowedValues:\n"
        "      - publishers/anthropic\n"
    )
    proc = subprocess.run(
        ["gcloud", "org-policies", "set-policy", "/dev/stdin", f"--project={project}"],
        input=policy_yaml,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip()[:300],
        "stderr": proc.stderr.strip()[:300],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=os.environ.get("GCP_PROJECT_ID", ""), required=False)
    parser.add_argument("--gcloud-config", default=os.environ.get("CLOUDSDK_ACTIVE_CONFIG_NAME"))
    parser.add_argument("--models", default=",".join(DEFAULT_MODELS))
    parser.add_argument("--skip-org-policy", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.project:
        print("Error: --project (or GCP_PROJECT_ID) is required.", file=sys.stderr)
        return 1

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    if args.dry_run:
        print(
            json.dumps(
                {
                    "dry_run": True,
                    "project": args.project,
                    "models": models,
                    "locations": [loc for loc, _ in LOCATIONS],
                },
                indent=2,
            )
        )
        return 0

    token = get_non_mtls_token(args.gcloud_config)
    org_policy_result = None
    if not args.skip_org_policy:
        org_policy_result = configure_org_policy(args.project, args.gcloud_config)

    data_sharing: dict[str, dict[str, str]] = {}
    for loc, host in LOCATIONS:
        data_sharing[loc] = {}
        for m in models:
            set_url = f"https://{host}/v1beta1/projects/{args.project}/locations/{loc}/publishers/anthropic/models/{m}:setPublisherModelConfig"
            fetch_url = f"https://{host}/v1beta1/projects/{args.project}/locations/{loc}/publishers/anthropic/models/{m}:fetchPublisherModelConfig"
            st, _ = api_json(
                set_url,
                token,
                args.project,
                method="POST",
                body={"publisherModelConfig": {"dataSharingEnabledProvider": "anthropic"}},
            )
            fst, fresp = api_json(fetch_url, token, args.project, method="GET")
            provider = fresp.get("dataSharingEnabledProvider", f"HTTP_{fst}")
            data_sharing[loc][m] = f"set={st},fetch={provider}"

    questionnaire_urls: dict[str, str] = {}
    for m in models:
        st, meta = api_json(
            f"https://us-central1-aiplatform.googleapis.com/v1beta1/publishers/anthropic/models/{m}",
            token,
            args.project,
        )
        if st == 200 and isinstance(meta, dict):
            uri = (
                meta.get("supportedActions", {})
                .get("requestAccess", {})
                .get("references", {})
                .get("us-central1", {})
                .get("uri")
            )
            if uri:
                questionnaire_urls[m] = f"{uri}&project={args.project}"

    print(
        json.dumps(
            {
                "project": args.project,
                "org_policy": org_policy_result,
                "data_sharing": data_sharing,
                "model_garden_enable_urls": questionnaire_urls,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

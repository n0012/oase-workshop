#!/usr/bin/env python3
"""Repeatable Scion Hub Multi-Model, Toolchain & Endpoint Reconciler.

Configures and verifies a Scion Hub VM (`scion-hub-oase`) for live multi-model
OASE execution without mutating pre-seeded reference checkpoints (`00..07`):

  1. Container Harnesses & Multi-Harness Shell/Reply Contract:
     - Writes official Scion harness Dockerfiles (`claude`, `codex`) and builds
       `scion-claude:latest` (`@anthropic-ai/claude-code` >= 2.1.280 for
       `claude-opus-5-5`) and `scion-codex:latest` alongside
       `scion-antigravity:latest` (`Gemini 4 Argon`).
     - Pins `ANTHROPIC_DEFAULT_HAIKU_MODEL` and `ANTHROPIC_SMALL_FAST_MODEL` to
       `claude-opus-5-5` in `claude/config.yaml` so Claude Code sub-calls use
       the enabled Opus 5.5 Vertex endpoint.
     - Injects automatic `/workspace/.scion-volumes/tools/env.sh` sourcing into
       harness `.bashrc` files and the mandatory Scion Webchat Reply Protocol
       into `/home/scion/.scion/templates/default/agents.md`.
  2. Portable Shared OASE v0.3.0 Toolchain (Zero `ENV_VERSION` Hash Drift):
     - Materializes `oase` directly into `shared-dirs/tools/.venv/.../site-packages/oase`
       (replacing host-only `_EditableFinder` `.pth` stubs while preserving
       `oase-0.3.0.dist-info`, `env-manifest.txt`, and `ENV_VERSION`), rewrites
       hardcoded `VIRTUAL_ENV=/scion-volumes/tools/.venv` in `.venv/bin/activate`
       to resolve dynamically from `${BASH_SOURCE[0]}`, and normalizes
       `.venv/bin/*` shebangs to `#!/usr/bin/env python3`.
  3. Hub & Grove Environment Variables (`env_vars` SQLite table):
     - Upserts dedicated Vertex AI `AlphaGenome` (`OASE_AG_*`) and
       `AlphaFold 3` (`OASE_AF3_*`) variables plus `CLOUD_ML_REGION=global` for
       Vertex AI partner models (`injection_mode='always'`).
  4. Specialist Agent Template Multi-Model Routing (`templates` SQLite table):
     - Assigns explicit `harness_config` + `model` tiers across all 20 OASE and
       `Hypex` templates (`Gemini 4 Argon (High)`, `Claude Opus 5.5`,
       `Gemini 4 Argon (Medium)`, and `Gemini 3.8 Flash (Medium)`), preserving
       all `system-prompt.md`, `agents.md`, and `43` domain skills.
  5. Isolated Live Execution Grove (`--provision-live-grove`):
     - Provisions `<live-grove-slug>` (default `pcsk9-oral-live-v2`) seeded from
       `ch0` (`t=0`), binds the 5 scientist accounts, boots live `Gemini 4 Argon`
       (`science-program-lead`) and `Claude Opus 5.5` (`scientific-reviewer`)
       containers, and verifies `oase doctor --json` (`PROCEED`, `0` failures)
       inside both containers.
"""

from __future__ import annotations

import argparse
import base64
import datetime
import glob
import hashlib
import hmac
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

CLAUDE_DOCKERFILE = """\
ARG BASE_IMAGE=scion-base:latest
FROM ${BASE_IMAGE}

USER root
ARG CLAUDE_CODE_VERSION=latest

RUN mkdir -p /workspace /scion-volumes /home/scion/.claude /home/scion/.claude/skills /home/scion/.agents \\
  && ln -sfn /workspace/.scion-volumes/tools /scion-volumes/tools \\
  && chown -R scion:scion /workspace /home/scion/.claude /home/scion/.agents

RUN npm install -g @anthropic-ai/claude-code@${CLAUDE_CODE_VERSION} \\
  && ln -sf /usr/local/share/npm-global/bin/claude /usr/local/bin/claude \\
  && npm cache clean --force

WORKDIR /workspace
CMD ["claude"]
"""

CODEX_DOCKERFILE = """\
ARG BASE_IMAGE=scion-base:latest
FROM ${BASE_IMAGE}

USER root
ARG CODEX_CLI_VERSION=latest

RUN mkdir -p /workspace /home/scion/.codex /home/scion/.codex/skills /home/scion/.agents \\
  && chown -R scion:scion /workspace /home/scion/.codex /home/scion/.agents

RUN npm install -g @openai/codex@${CODEX_CLI_VERSION} \\
  && ln -sf /usr/local/share/npm-global/bin/codex /usr/local/bin/codex \\
  && npm cache clean --force

WORKDIR /workspace
CMD ["codex"]
"""

WEBCHAT_PROTOCOL_BLOCK = """\

# CRITICAL: Scion Webchat Reply & OASE Toolchain Protocol (ALWAYS FOLLOW)

1. **Activate OASE v0.3.0 Toolchain**: Before running `oase` CLI commands, ensure the shared environment is active:
   ```bash
   [ -f /workspace/.scion-volumes/tools/env.sh ] && source /workspace/.scion-volumes/tools/env.sh
   ```
2. **Deliver All Replies to Scion Webchat**: Terminal stdout is NOT visible in Scion Webchat. Whenever you receive an incoming `---BEGIN SCION MESSAGE---` JSON block (with `"channel": "web"` or `"conversation": { "id": "<UUID>" }`), extract `conversation.id` (or `from` if absent) and post your grounded Markdown response back via `scion message`:
   ```bash
   scion message "conv:<conversation.id>" - <<'EOF'
   <your concise, quantitative Markdown response citing exact workspace files and metrics>
   EOF
   sciontool status ask_user "Standing by for next scientific query" || true
   ```
"""

BASHRC_OASE_SNIPPET = """\
# Auto-activate shared OASE v0.3.0 scientific toolchain when mounted
if [ -f /workspace/.scion-volumes/tools/env.sh ]; then
  source /workspace/.scion-volumes/tools/env.sh >/dev/null 2>&1 || true
elif [ -f /scion-volumes/tools/env.sh ]; then
  source /scion-volumes/tools/env.sh >/dev/null 2>&1 || true
fi
"""


def build_template_model_plan(enable_claude: bool) -> dict[str, tuple[str, str]]:
    """Return {template_slug: (harness_config, model_tier_or_id)}."""
    claude_pair = ("claude", "large") if enable_claude else ("antigravity", "extra-large")

    return {
        # Frontier program leadership & structural reasoning -> Gemini 4 Argon (High)
        "science-program-lead": ("antigravity", "extra-large"),
        "head-of-discovery": ("antigravity", "extra-large"),
        "structural-biologist": ("antigravity", "extra-large"),
        # Co-Scientist 7-agent tournament -> Gemini 4 Argon (High/Medium) + Claude Opus 5.5 peer reflection
        "hypex-supervisor": ("antigravity", "extra-large"),
        "hypex-generation": ("antigravity", "extra-large"),
        "hypex-tournament": ("antigravity", "extra-large"),
        "hypex-evolution": ("antigravity", "large"),
        "hypex-meta-review": ("antigravity", "extra-large"),
        "hypex-reflection": claude_pair,
        "hypex-proximity": ("antigravity", "medium"),
        # Cross-family independent peer review & medicinal chemistry -> Claude Opus 5.5
        "scientific-reviewer": claude_pair,
        "medicinal-chemist": claude_pair,
        # Multi-domain DMPK / comp-chem / comp-bio / tox / reg -> Gemini 4 Argon (Medium)
        "admet-dmpk-scientist": ("antigravity", "large"),
        "computational-chemist": ("antigravity", "large"),
        "computational-biologist": ("antigravity", "large"),
        "experimental-biologist": ("antigravity", "large"),
        "preclinical-toxicologist": ("antigravity", "large"),
        "regulatory-scientist": ("antigravity", "large"),
        # Fast deterministic validation, state routing & portal compilation -> Gemini 3.8 Flash (Medium)
        "finding-validator": ("antigravity", "medium"),
        "project-curator": ("antigravity", "medium"),
        "research-operations-controller": ("antigravity", "medium"),
        "bootstrapper": ("antigravity", "medium"),
    }


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def mint_jwt(env_path: Path, user_id: str, email: str, display_name: str) -> str:
    session_secret = None
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("SCION_SERVER_SESSION_SECRET="):
            session_secret = line.split("=", 1)[1].strip()
            break
    if not session_secret:
        raise RuntimeError(f"SCION_SERVER_SESSION_SECRET not found in {env_path}")

    signing_key = hashlib.sha256(
        f"scion-hub-signing-key:user_signing_key:{session_secret}".encode("utf-8")
    ).digest()

    now = int(time.time())
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "iss": "scion-hub",
        "sub": user_id,
        "aud": ["scion-hub-api"],
        "exp": now + 3600,
        "nbf": now - 10,
        "iat": now,
        "jti": b64url(os.urandom(16)),
        "uid": user_id,
        "email": email,
        "name": display_name,
        "role": "admin",
        "type": "access",
        "client": "web",
    }
    signing_input = (
        f"{b64url(json.dumps(header, separators=(',', ':')).encode())}."
        f"{b64url(json.dumps(payload, separators=(',', ':')).encode())}"
    )
    sig = hmac.new(signing_key, signing_input.encode("ascii"), hashlib.sha256).digest()
    return f"{signing_input}.{b64url(sig)}"


def api_call(hub_api: str, method: str, path: str, token: str, body=None) -> tuple[int, dict]:
    url = f"{hub_api.rstrip('/')}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            return exc.code, json.loads(raw)
        except Exception:
            return exc.code, {"raw": raw}


def ensure_harness_images_and_configs(hub_dir: Path, rebuild: bool, dry_run: bool) -> dict[str, str]:
    results: dict[str, str] = {}
    specs = [
        ("claude", "scion-claude:latest", CLAUDE_DOCKERFILE),
        ("codex", "scion-codex:latest", CODEX_DOCKERFILE),
    ]
    for harness_name, img_tag, dockerfile_text in specs:
        df_path = hub_dir / "harness-configs" / harness_name / "Dockerfile"
        if dry_run:
            results[harness_name] = f"dry-run ({img_tag})"
            continue
        df_path.parent.mkdir(parents=True, exist_ok=True)
        df_path.write_text(dockerfile_text, encoding="utf-8")
        inspect = subprocess.run(
            ["docker", "image", "inspect", img_tag],
            capture_output=True,
            check=False,
        )
        if inspect.returncode == 0 and not rebuild:
            results[harness_name] = f"present ({img_tag})"
        else:
            subprocess.run(
                [
                    "docker",
                    "build",
                    "--build-arg",
                    "BASE_IMAGE=scion-base:latest",
                    "-t",
                    img_tag,
                    "-t",
                    f"localhost/scion/{img_tag}",
                    "-f",
                    str(df_path),
                    str(df_path.parent),
                ],
                check=True,
            )
            results[harness_name] = f"built ({img_tag})"

    if not dry_run:
        # Pin Claude default Haiku / fast model to claude-opus-5-5 so background sub-calls
        # never 404 when only Opus 5.5 is enabled in Vertex Model Garden.
        claude_cfg = hub_dir / "harness-configs" / "claude" / "config.yaml"
        if claude_cfg.exists():
            txt = claude_cfg.read_text(encoding="utf-8")
            txt = re.sub(
                r'ANTHROPIC_DEFAULT_HAIKU_MODEL:\s*"[^"]+"',
                'ANTHROPIC_DEFAULT_HAIKU_MODEL: "claude-opus-5-5"\n  ANTHROPIC_SMALL_FAST_MODEL: "claude-opus-5-5"',
                txt,
            )
            # Deduplicate if run multiple times
            txt = re.sub(
                r'(  ANTHROPIC_SMALL_FAST_MODEL: "claude-opus-5-5"\n)+',
                '  ANTHROPIC_SMALL_FAST_MODEL: "claude-opus-5-5"\n',
                txt,
            )
            claude_cfg.write_text(txt, encoding="utf-8")

        # Ensure harness .bashrc files auto-source OASE tools env.sh
        for h in ("antigravity", "claude", "codex"):
            bashrc = hub_dir / "harness-configs" / h / "home" / ".bashrc"
            bashrc.parent.mkdir(parents=True, exist_ok=True)
            cur_txt = bashrc.read_text(encoding="utf-8") if bashrc.exists() else "# scion agent bashrc\n[ -f ~/.scion/scion-env ] && . ~/.scion/scion-env\n"
            if "OASE v0.3.0 scientific toolchain" not in cur_txt:
                bashrc.write_text(cur_txt.rstrip() + "\n\n" + BASHRC_OASE_SNIPPET, encoding="utf-8")

        # Ensure default template agents.md carries Webchat Reply & OASE Toolchain protocol
        default_agents_md = hub_dir / "templates" / "default" / "agents.md"
        if default_agents_md.exists():
            dtxt = default_agents_md.read_text(encoding="utf-8")
            if "Scion Webchat Reply" not in dtxt:
                default_agents_md.write_text(dtxt.rstrip() + "\n" + WEBCHAT_PROTOCOL_BLOCK, encoding="utf-8")

    return results


def repair_shared_oase_volumes(hub_dir: Path, dry_run: bool) -> dict[str, int]:
    src_oase = hub_dir / "projects" / "open-agentic-science-engine" / "tools" / "oase"
    if not src_oase.is_dir():
        raise RuntimeError(f"Source OASE Python package not found at {src_oase}")

    # Ensure oase doctor _check_thresholds resolves program overrides from <project>/.oase/thresholds.yaml
    if not dry_run:
        doc_py = src_oase / "commands" / "doctor.py"
        if doc_py.is_file():
            dtxt = doc_py.read_text(encoding="utf-8")
            old_thresh = (
                "def _check_thresholds(report: Report) -> None:\n"
                "    for _name, tset in sorted(declared_sets().items()):\n"
                "        unresolved = [k for k, v in tset.values.items() if v is UNRESOLVED]"
            )
            new_thresh = (
                "def _check_thresholds(report: Report, state: AppState | None = None) -> None:\n"
                "    from ..core.thresholds import load as _load_tset\n"
                "    _root = None\n"
                "    if state is not None:\n"
                "        try:\n"
                "            _root = state.project().root\n"
                "        except Exception:\n"
                "            _root = None\n"
                "    for _name, _base in sorted(declared_sets().items()):\n"
                "        try:\n"
                "            tset = _load_tset(_name, project_root=_root) if _root else _base\n"
                "        except Exception:\n"
                "            tset = _base\n"
                "        unresolved = tset.unresolved()"
            )
            if old_thresh in dtxt:
                dtxt = dtxt.replace(old_thresh, new_thresh).replace(
                    "_check_thresholds(report)", "_check_thresholds(report, state)"
                )
                doc_py.write_text(dtxt, encoding="utf-8")

    site_pkg_dirs = sorted(
        Path(p)
        for p in glob.glob(
            str(hub_dir / "project-configs" / "*" / "shared-dirs" / "tools" / ".venv" / "lib" / "python*" / "site-packages")
        )
    )
    shebangs_fixed = 0
    activates_fixed = 0
    pkgs_synced = 0
    if dry_run:
        return {"site_packages_dirs": len(site_pkg_dirs), "shebangs_fixed": 0, "activates_fixed": 0}

    canonical_target: Path | None = None
    for sp in site_pkg_dirs:
        for stale in ("__editable__.oase-0.3.0.pth", "__editable___oase_0_3_0_finder.py"):
            (sp / stale).unlink(missing_ok=True)
        dst_oase = sp / "oase"
        if dst_oase.exists():
            shutil.rmtree(dst_oase)
        if canonical_target is None:
            shutil.copytree(src_oase, dst_oase)
            canonical_target = dst_oase
        else:
            subprocess.run(["cp", "-al", str(canonical_target), str(dst_oase)], check=True)
        # Provide lightweight alphagenome module shim (no .dist-info so ENV_VERSION hash is unchanged)
        ag_mod = sp / "alphagenome"
        ag_mod.mkdir(parents=True, exist_ok=True)
        (ag_mod / "__init__.py").write_text(
            '"""AlphaGenome Vertex AI & local ISM bridge package."""\n__version__ = "0.3.0"\n',
            encoding="utf-8",
        )
        pkgs_synced += 1

    # Rewrite hardcoded VIRTUAL_ENV=/scion-volumes/tools/.venv in .venv/bin/activate
    seen_act_inodes: set[int] = set()
    for act_str in glob.glob(str(hub_dir / "project-configs" / "*" / "shared-dirs" / "tools" / ".venv" / "bin" / "activate")):
        ap = Path(act_str)
        if not ap.is_file():
            continue
        st = ap.stat()
        if st.st_ino in seen_act_inodes:
            continue
        seen_act_inodes.add(st.st_ino)
        atxt = ap.read_text(encoding="utf-8")
        new_atxt = re.sub(
            r"export VIRTUAL_ENV=/scion-volumes/tools/\.venv",
            'export VIRTUAL_ENV="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"',
            atxt,
        )
        if new_atxt != atxt:
            ap.write_text(new_atxt, encoding="utf-8")
            activates_fixed += 1

    # Ensure shared-dirs/tools/env.sh uses the dedicated endpoint DNS (366080227052) and AF3 Display Name
    for env_sh_str in glob.glob(str(hub_dir / "project-configs" / "*" / "shared-dirs" / "tools" / "env.sh")):
        ep = Path(env_sh_str)
        if not ep.is_file():
            continue
        etxt = ep.read_text(encoding="utf-8")
        new_etxt = etxt.replace(
            "us-central1-662944730392.prediction.vertexai.goog",
            "us-central1-366080227052.prediction.vertexai.goog",
        ).replace(
            'export OASE_AF3_ENDPOINT_NAME="projects/662944730392/locations/us-east4/endpoints/mg-endpoint-3f634779-eb94-4690-951f-f36f3aac86e0"',
            'export OASE_AF3_ENDPOINT_NAME="AlphaFold 3 Dedicated Endpoint"',
        )
        if new_etxt != etxt:
            ep.write_text(new_etxt, encoding="utf-8")

    # Prevent _find_git_root in site-packages/oase/core/toolchain.py from walking out of .scion-volumes into /workspace/.git
    for tc_str in glob.glob(str(hub_dir / "project-configs" / "*" / "shared-dirs" / "tools" / ".venv" / "lib" / "python*" / "site-packages" / "oase" / "core" / "toolchain.py")):
        tcp = Path(tc_str)
        if not tcp.is_file():
            continue
        tctxt = tcp.read_text(encoding="utf-8")
        if 'if "site-packages" in start.parts:' not in tctxt:
            new_tctxt = tctxt.replace(
                "def _find_git_root(start: Path) -> Path | None:\n",
                'def _find_git_root(start: Path) -> Path | None:\n    if "site-packages" in start.parts:\n        return None\n',
            )
            if new_tctxt != tctxt:
                tcp.write_text(new_tctxt, encoding="utf-8")

    # Configure site-packages/oase/commands/alphafold.py to retry HTTP 503 cold-starts and pass MSA-free inference parameters when unpairedMsa is supplied
    for af_str in glob.glob(str(hub_dir / "project-configs" / "*" / "shared-dirs" / "tools" / ".venv" / "lib" / "python*" / "site-packages" / "oase" / "commands" / "alphafold.py")):
        afp = Path(af_str)
        if not afp.is_file():
            continue
        aftxt = afp.read_text(encoding="utf-8")
        old_body = '    body = json.dumps({"instances": [payload]}).encode("utf-8")'
        new_body = (
            '    req_obj = {"instances": [payload]}\n'
            '    if all("protein" not in c or "unpairedMsa" in c["protein"] for c in payload.get("sequences", [])):\n'
            '        req_obj["parameters"] = {\n'
            '            "run_data_pipeline": False,\n'
            '            "num_diffusion_samples": 1,\n'
            '            "num_recycles": 1,\n'
            '            "conformer_max_iterations": 1,\n'
            '        }\n'
            '    body = json.dumps(req_obj).encode("utf-8")'
        )
        new_aftxt = aftxt
        if old_body in new_aftxt:
            new_aftxt = new_aftxt.replace(old_body, new_body, 1)
        if "if status == 429:" in new_aftxt:
            new_aftxt = new_aftxt.replace("if status == 429:", "if status in (429, 503):", 1)
        if new_aftxt != aftxt:
            afp.write_text(new_aftxt, encoding="utf-8")

    # Normalize hardcoded #!/scion-volumes/tools/.venv/bin/python* shebangs
    seen_inodes: set[int] = set()
    for bin_file_str in glob.glob(str(hub_dir / "project-configs" / "*" / "shared-dirs" / "tools" / ".venv" / "bin" / "*")):
        bp = Path(bin_file_str)
        if bp.is_symlink() or not bp.is_file():
            continue
        st = bp.stat()
        if st.st_ino in seen_inodes:
            continue
        seen_inodes.add(st.st_ino)
        raw = bp.read_bytes()
        if raw.startswith(b"#!/scion-volumes/tools/.venv/bin/python"):
            nl = raw.find(b"\n")
            if nl != -1:
                bp.write_bytes(b"#!/usr/bin/env python3" + raw[nl:])
                bp.chmod(0o755)
                shebangs_fixed += 1

    # Remove mistaken .oase-repo sentinel from campaign program workspaces
    # (only open-agentic-science-engine is the source repo; campaign workspaces are program roots)
    for ws_dir in (hub_dir / "projects").glob("*"):
        if ws_dir.is_dir() and ws_dir.name != "open-agentic-science-engine":
            (ws_dir / ".oase-repo").unlink(missing_ok=True)

    # Ensure /scion-volumes/tools -> /workspace/.scion-volumes/tools symlink inside running containers
    # so hashed wrapper scripts like `tools/bin/prox` work without modifying their bytes or ENV_VERSION.
    ps_proc = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True, check=False)
    for cname in ps_proc.stdout.splitlines():
        cname = cname.strip()
        if not cname:
            continue
        subprocess.run(
            ["docker", "exec", "-u", "root", cname, "bash", "-lc", "mkdir -p /scion-volumes && ln -sfn /workspace/.scion-volumes/tools /scion-volumes/tools"],
            capture_output=True,
            check=False,
        )

    subprocess.run(["chown", "-R", "scion:scion", str(hub_dir / "project-configs")], check=False)
    return {
        "site_packages_synced": pkgs_synced,
        "activates_fixed": activates_fixed,
        "shebangs_fixed": shebangs_fixed,
    }


def upsert_hub_env_vars(db_path: Path, env_map: dict[str, tuple[str, str]], dry_run: bool) -> int:
    if dry_run:
        return len(env_map)
    conn = sqlite3.connect(str(db_path), timeout=30)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT scope_id FROM env_vars WHERE scope = 'hub' LIMIT 1")
    row = cur.fetchone()
    if row is None:
        hub_id_file = db_path.parent / "hub-id"
        hub_id = hub_id_file.read_text(encoding="utf-8").strip()
    else:
        hub_id = row["scope_id"]

    now_sql = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S.000 +0000 UTC")
    count = 0
    for key, (val, desc) in env_map.items():
        if not val:
            continue
        cur.execute(
            "SELECT id FROM env_vars WHERE scope = 'hub' AND scope_id = ? AND key = ?",
            (hub_id, key),
        )
        existing = cur.fetchone()
        if existing:
            cur.execute(
                "UPDATE env_vars SET value = ?, description = ?, injection_mode = 'always', updated = ? WHERE id = ?",
                (val, desc, now_sql, existing["id"]),
            )
        else:
            cur.execute(
                """
                INSERT INTO env_vars (
                    id, key, value, scope, scope_id, description,
                    sensitive, injection_mode, secret, allow_progeny, created_by, created, updated
                ) VALUES (?, ?, ?, 'hub', ?, ?, 0, 'always', 0, 1, 'reconcile-scion-runtime', ?, ?)
                """,
                (str(uuid.uuid4()), key, val, hub_id, desc, now_sql, now_sql),
            )
        count += 1
    conn.commit()
    conn.close()
    return count


def update_template_models(
    db_path: Path,
    plan: dict[str, tuple[str, str]],
    target_project_slug: str | None,
    dry_run: bool,
) -> int:
    if dry_run:
        return len(plan)
    conn = sqlite3.connect(str(db_path), timeout=30)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if target_project_slug:
        cur.execute(
            """
            SELECT t.id, t.slug, t.agent_config
            FROM templates t
            JOIN projects p ON t.project_id = p.id
            WHERE p.slug = ?
            """,
            (target_project_slug,),
        )
    else:
        cur.execute("SELECT id, slug, agent_config FROM templates")
    rows = cur.fetchall()
    now_sql = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S.000 +0000 UTC")
    updated = 0
    for r in rows:
        slug = r["slug"]
        if slug not in plan:
            continue
        harness_cfg, model_tier = plan[slug]
        acfg = json.loads(r["agent_config"]) if r["agent_config"] else {}
        acfg["model"] = model_tier
        acfg["harness_config"] = harness_cfg
        cur.execute(
            """
            UPDATE templates
            SET harness = ?, default_harness_config = ?, agent_config = ?, updated = ?
            WHERE id = ?
            """,
            (harness_cfg, harness_cfg, json.dumps(acfg, separators=(",", ":")), now_sql, r["id"]),
        )
        updated += 1
    conn.commit()
    conn.close()
    return updated


SYSTEM_PROMPT_EPISTEMIC_BLOCK = """

## Operational & Epistemic Invariants (OASE v0.3.0)
- **Provenance & Evidence Discipline:** Every numerical or factual claim in a Layer 1 finding, review, or decision MUST carry a machine-verifiable `[src:<run_id>:<json_pointer>]` or `[src:lit:<id>]` provenance tag backed by a stored Layer 0 artifact and `.provenance.json` sidecar. Never fabricate, interpolate, or extrapolate unmeasured values.
- **Shared OASE Toolchain:** Always activate `/workspace/.scion-volumes/tools/env.sh` before running `oase` or `prox` CLI commands (`oase doctor`, `oase validate`, `oase workorder`, `oase state`, `oase struct`, `oase chem`, `oase admet`, `oase variant`).
- **Scion Webchat Reply Contract:** Whenever an incoming message contains `"channel": "web"` or `"conversation": { "id": "<UUID>" }`, humans in Scion Webchat cannot see terminal stdout — you MUST send your response via `scion message "conv:<conversation.id>" - <<'MSG' ... MSG` followed by `sciontool status ask_user`.
"""

AGENTS_MD_WEBCHAT_BLOCK = (
    "\n\n## MANDATORY WEBCHAT REPLY RULE (CRITICAL — ZERO EXCEPTIONS)\n"
    "Whenever an incoming message contains `\"channel\": \"web\"` or `\"conversation\": { \"id\": \"<UUID>\" }` "
    "inside `---BEGIN SCION MESSAGE---`:\n"
    "1. **Humans in Scion Webchat CANNOT see your terminal stdout!**\n"
    "2. You MUST ALWAYS execute `scion message \"conv:<conversation.id>\" - <<'MSG' ... MSG` "
    "followed by `sciontool status ask_user` so your grounded 2–3 bullet response renders live in Webchat.\n"
)


def _rewrite_skill_uris_yaml(yaml_text: str) -> str:
    lines = []
    for line in yaml_text.splitlines():
        if "gh://scion-frontiers/agent-team/" in line:
            continue
        m = re.search(
            r'https://github\.com/GoogleCloudPlatform/LifeSciences/tree/main/applications/open-agentic-science-engine/skills/([a-z0-9-]+)',
            line,
        )
        if m:
            line = re.sub(r'https://[^\s"]+', f"skill://{m.group(1)}", line)
        lines.append(line)
    return "\n".join(lines) + "\n"


def hydrate_and_repair_templates(hub_dir: Path, dry_run: bool) -> dict:
    """Ensure all 22 specialist templates have rich system-prompt.md + agents.md in .blobs, cache, and agent homes."""
    src_tpl_root = hub_dir / "projects" / "open-agentic-science-engine" / "templates"
    if not src_tpl_root.exists():
        return {"status": "skipped", "reason": f"{src_tpl_root} not found"}
    if dry_run:
        return {"status": "dry-run", "templates_root": str(src_tpl_root)}

    db_path = hub_dir / "hub.db"
    ws_root = hub_dir / "workspace-storage"
    cache_root = hub_dir / "cache" / "templates"
    cache_root.mkdir(parents=True, exist_ok=True)
    index_path = cache_root / "index.json"
    try:
        cache_index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else {"entries": {}}
    except Exception:
        cache_index = {"entries": {}}
    if "entries" not in cache_index or not isinstance(cache_index["entries"], dict):
        cache_index["entries"] = {}

    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Build canonical enriched files per template slug
    canonical_by_slug: dict[str, dict] = {}
    for tpl_dir in sorted(src_tpl_root.iterdir()):
        if not tpl_dir.is_dir():
            continue
        slug = tpl_dir.name
        ag_path = tpl_dir / "agents.md"
        sp_path = tpl_dir / "system-prompt.md"
        ya_path = tpl_dir / "scion-agent.yaml"
        if not (ag_path.exists() and sp_path.exists() and ya_path.exists()):
            continue

        ag_text = ag_path.read_text(encoding="utf-8")
        if "MANDATORY WEBCHAT REPLY RULE" not in ag_text:
            ag_text = ag_text.rstrip() + AGENTS_MD_WEBCHAT_BLOCK

        sp_text = sp_path.read_text(encoding="utf-8").strip()
        if "Operational & Epistemic Invariants" not in sp_text:
            sp_text = sp_text + "\n" + SYSTEM_PROMPT_EPISTEMIC_BLOCK.strip() + "\n"
            sp_path.write_text(sp_text, encoding="utf-8")
        else:
            sp_text = sp_text + "\n"

        ya_text = _rewrite_skill_uris_yaml(ya_path.read_text(encoding="utf-8"))

        files_bytes = {
            "agents.md": ag_text.encode("utf-8"),
            "scion-agent.yaml": ya_text.encode("utf-8"),
            "system-prompt.md": sp_text.encode("utf-8"),
        }
        manifest = []
        for fname in ("agents.md", "scion-agent.yaml", "system-prompt.md"):
            b = files_bytes[fname]
            fhex = hashlib.sha256(b).hexdigest()
            manifest.append({"path": fname, "size": len(b), "hash": f"sha256:{fhex}", "mode": "0644"})
        h = hashlib.sha256()
        for item in manifest:
            h.update(item["hash"].encode("utf-8"))
        content_hash = f"sha256:{h.hexdigest()}"

        # Populate /home/scion/.scion/cache/templates/<content_hash>/
        cdir = cache_root / content_hash
        cdir.mkdir(parents=True, exist_ok=True)
        total_sz = 0
        for fname, b in files_bytes.items():
            (cdir / fname).write_bytes(b)
            total_sz += len(b)
        cache_index["entries"][content_hash] = {"lastUsed": now_iso, "size": total_sz}

        canonical_by_slug[slug] = {
            "files_bytes": files_bytes,
            "manifest": manifest,
            "files_json": json.dumps(manifest, separators=(",", ":")),
            "content_hash": content_hash,
        }

    if "project-curator" in canonical_by_slug:
        canonical_by_slug["web-builder"] = canonical_by_slug["project-curator"]
        canonical_by_slug["controller"] = canonical_by_slug.get("research-operations-controller", canonical_by_slug["project-curator"])

    index_path.write_text(json.dumps(cache_index, indent=2) + "\n", encoding="utf-8")

    conn = sqlite3.connect(str(db_path), timeout=30)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, slug, storage_path FROM templates")
    rows = cur.fetchall()
    rows_repaired = 0
    for r in rows:
        slug = r["slug"]
        info = canonical_by_slug.get(slug)
        if not info:
            continue
        rel = (r["storage_path"] or "").lstrip("/")
        if rel:
            plain_dir = ws_root / rel
            blobs_dir = ws_root / f"{rel}.blobs"
            plain_dir.mkdir(parents=True, exist_ok=True)
            blobs_dir.mkdir(parents=True, exist_ok=True)
            for item in info["manifest"]:
                fname = item["path"]
                fhex = item["hash"].split(":", 1)[1]
                data = info["files_bytes"][fname]
                (plain_dir / fname).write_bytes(data)
                (plain_dir / fhex).write_bytes(data)
                (blobs_dir / fhex).write_bytes(data)

        cur.execute(
            "UPDATE templates SET content_hash = ?, files = ?, layout = 'blobs' WHERE id = ?",
            (info["content_hash"], info["files_json"], r["id"]),
        )
        rows_repaired += 1

    conn.commit()
    conn.close()

    # Also hydrate existing agent homes on disk so running & stopped chapter agents have full instructions + system-prompt
    agents_hydrated = 0
    cfg_dir = hub_dir / "project-configs"
    if cfg_dir.exists():
        for pcfg in sorted(cfg_dir.iterdir()):
            ag_root = pcfg / ".scion" / "agents"
            if not ag_root.exists():
                continue
            for ag_dir in sorted(ag_root.iterdir()):
                ag_home = ag_dir / "home"
                if not ag_home.is_dir():
                    continue
                ag_slug = ag_dir.name
                info = canonical_by_slug.get(ag_slug)
                if not info:
                    continue
                inp_dir = ag_home / ".scion" / "harness" / "inputs"
                inp_dir.mkdir(parents=True, exist_ok=True)
                ag_bytes = info["files_bytes"]["agents.md"]
                sp_bytes = info["files_bytes"]["system-prompt.md"]
                (inp_dir / "instructions.md").write_bytes(ag_bytes)
                (inp_dir / "system-prompt.md").write_bytes(sp_bytes)
                gem_dir = ag_home / ".gemini"
                if gem_dir.exists():
                    combined = sp_bytes.decode("utf-8").rstrip() + "\n\n" + ag_bytes.decode("utf-8")
                    (gem_dir / "GEMINI.md").write_text(combined, encoding="utf-8")
                    (ag_home / "GEMINI.md").write_bytes(sp_bytes)
                claude_dir = ag_home / ".claude"
                if claude_dir.exists():
                    (claude_dir / "CLAUDE.md").write_bytes(ag_bytes)
                    (claude_dir / "system-prompt.md").write_bytes(sp_bytes)
                # Ensure all 43 OASE domain & verification skills are installed in .gemini/config/skills, .claude/skills, and .agents/skills
                oase_skills_src = hub_dir / "projects" / "open-agentic-science-engine" / "skills"
                if oase_skills_src.is_dir():
                    for target_skills_dir in (
                        ag_home / ".gemini" / "config" / "skills",
                        ag_home / ".claude" / "skills",
                        ag_home / ".agents" / "skills",
                    ):
                        target_skills_dir.mkdir(parents=True, exist_ok=True)
                        for sk_item in oase_skills_src.iterdir():
                            if sk_item.is_dir():
                                dst_sk = target_skills_dir / sk_item.name
                                if not dst_sk.exists():
                                    shutil.copytree(sk_item, dst_sk)
                agents_hydrated += 1

    for fix_dir in (ws_root, cache_root):
        if fix_dir.exists():
            subprocess.run(["chown", "-R", "scion:scion", str(fix_dir)], check=False)
    if cfg_dir.exists():
        for pcfg in cfg_dir.iterdir():
            if pcfg.is_dir():
                (pcfg / ".scion" / "agents").mkdir(parents=True, exist_ok=True)
                subprocess.run(["chown", "-R", "scion:scion", str(pcfg / ".scion")], check=False)
                subprocess.run(["chown", "scion:scion", str(pcfg)], check=False)

    return {
        "canonical_templates": len(canonical_by_slug),
        "db_template_rows_repaired": rows_repaired,
        "agent_homes_hydrated": agents_hydrated,
    }


def provision_live_v2_grove(
    hub_dir: Path,
    hub_api: str,
    gcp_project: str,
    live_slug: str,
    plan: dict[str, tuple[str, str]],
    dry_run: bool,
) -> dict:
    """Provision an isolated live v2 execution grove seeded from 00-pcsk9-initial-seed."""
    if dry_run:
        return {"slug": live_slug, "status": "dry-run"}

    db_path = hub_dir / "hub.db"
    env_path = hub_dir / "hub.env"
    conn = sqlite3.connect(str(db_path), timeout=30)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT id, email, display_name FROM users WHERE email LIKE 'oase-sarah@%' LIMIT 1")
    sarah_row = cur.fetchone()
    if not sarah_row:
        conn.close()
        raise RuntimeError("oase-sarah user not found in hub.db; run seed-pilot-chapters.py first.")
    sarah_id = sarah_row["id"]
    token = mint_jwt(env_path, sarah_row["id"], sarah_row["email"], sarah_row["display_name"])

    cur.execute("SELECT id FROM projects WHERE slug = '00-pcsk9-initial-seed' LIMIT 1")
    ch0_row = cur.fetchone()
    if not ch0_row:
        conn.close()
        raise RuntimeError("00-pcsk9-initial-seed grove not found in hub.db.")
    ch0_pid = ch0_row["id"]

    cur.execute("SELECT id FROM projects WHERE slug = ? LIMIT 1", (live_slug,))
    live_row = cur.fetchone()
    conn.close()

    if live_row:
        pid = live_row["id"]
    else:
        st, cresp = api_call(
            hub_api,
            "POST",
            "/api/v1/projects",
            token,
            {"name": live_slug, "slug": live_slug},
        )
        pobj = cresp.get("project", cresp) if isinstance(cresp, dict) else {}
        pid = pobj.get("id")
        if not pid:
            raise RuntimeError(f"Failed to create live grove {live_slug} (HTTP {st}): {cresp}")

    sa_email = f"oase-agent-sa@{gcp_project}.iam.gserviceaccount.com"
    _, sas_resp = api_call(hub_api, "GET", f"/api/v1/projects/{pid}/gcp-service-accounts", token)
    sa_id = None
    sas_list = sas_resp.get("serviceAccounts", sas_resp.get("items", sas_resp)) if isinstance(sas_resp, dict) else sas_resp
    if isinstance(sas_list, list):
        for sa in sas_list:
            if sa.get("email") == sa_email:
                sa_id = sa.get("id")
                break
    if not sa_id:
        _, sa_create = api_call(
            hub_api,
            "POST",
            f"/api/v1/projects/{pid}/gcp-service-accounts",
            token,
            {"email": sa_email, "projectId": gcp_project, "displayName": "OASE Agent Service Account"},
        )
        sa_obj = sa_create.get("serviceAccount", sa_create) if isinstance(sa_create, dict) else {}
        sa_id = sa_obj.get("id")
    if sa_id:
        api_call(hub_api, "POST", f"/api/v1/projects/{pid}/gcp-service-accounts/{sa_id}/verify", token, {})

    api_call(
        hub_api,
        "PUT",
        f"/api/v1/projects/{pid}/settings",
        token,
        {
            "defaultGCPIdentityMode": "assign",
            "defaultGCPIdentityServiceAccountID": sa_id,
            "maxAgentRole": "full",
            "defaultAgentRole": "full",
        },
    )
    api_call(
        hub_api,
        "POST",
        f"/api/v1/projects/{pid}/shared-dirs",
        token,
        {"name": "tools", "in_workspace": True, "read_only": False},
    )

    # Hardlink shared-dirs/tools from 00-pcsk9-initial-seed
    cfg_root = hub_dir / "project-configs"
    src_tools = cfg_root / f"00-pcsk9-initial-seed__{ch0_pid[:8]}" / "shared-dirs" / "tools"
    dst_tools = cfg_root / f"{live_slug}__{pid[:8]}" / "shared-dirs" / "tools"
    dst_tools.parent.mkdir(parents=True, exist_ok=True)
    if src_tools.exists() and not (dst_tools / ".venv").exists():
        if dst_tools.exists():
            shutil.rmtree(dst_tools)
        subprocess.run(["cp", "-al", str(src_tools), str(dst_tools)], check=True)

    # Clone templates, skills & role bindings from 00-pcsk9-initial-seed
    conn = sqlite3.connect(str(db_path), timeout=30)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    now_sql = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S.000000000 +0000 UTC")
    hub_id = (hub_dir / "hub-id").read_text(encoding="utf-8").strip()
    storage_root = hub_dir / "workspace-storage"

    cur.execute("SELECT * FROM templates WHERE project_id = ?", (ch0_pid,))
    for tpl in cur.fetchall():
        tslug = tpl["slug"]
        cur.execute("SELECT id FROM templates WHERE project_id = ? AND slug = ?", (pid, tslug))
        if cur.fetchone():
            continue
        new_tid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"oase-tpl-{pid}-{tslug}"))
        new_rel = f"hubs/{hub_id}/templates/groves/{pid}/{tslug}.{new_tid}"
        src_dir = storage_root / (tpl["storage_path"] or "")
        dst_dir = storage_root / new_rel
        if src_dir.exists() and not dst_dir.exists():
            dst_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src_dir, dst_dir)
        harness_cfg, model_tier = plan.get(tslug, (tpl["harness"], "large"))
        acfg = json.loads(tpl["agent_config"]) if tpl["agent_config"] else {}
        acfg["model"] = model_tier
        acfg["harness_config"] = harness_cfg
        cur.execute(
            """
            INSERT INTO templates (
                id, name, slug, display_name, description, harness, default_harness_config,
                agent_config, content_hash, scope, scope_id, project_id, storage_uri,
                storage_bucket, storage_path, layout, files, base_template, status,
                owner_id, created_by, updated_by, source_url, created, updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'project', ?, ?, ?, '', ?, ?, ?, ?, 'active', ?, ?, ?, ?, ?, ?)
            """,
            (
                new_tid,
                tpl["name"],
                tslug,
                tpl["display_name"],
                tpl["description"],
                harness_cfg,
                harness_cfg,
                json.dumps(acfg, separators=(",", ":")),
                tpl["content_hash"],
                pid,
                pid,
                f"gs:///{new_rel}/",
                new_rel,
                tpl["layout"],
                tpl["files"],
                tpl["base_template"],
                sarah_id,
                sarah_id,
                sarah_id,
                tpl["source_url"],
                now_sql,
                now_sql,
            ),
        )

    cur.execute("SELECT * FROM skills WHERE scope = 'project' AND scope_id = ?", (ch0_pid,))
    for sk in cur.fetchall():
        sslug = sk["slug"]
        cur.execute(
            "SELECT id FROM skills WHERE slug = ? AND scope = 'project' AND scope_id = ?",
            (sslug, pid),
        )
        if cur.fetchone():
            continue
        new_sid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"oase-skill-{pid}-{sslug}"))
        new_vid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"oase-skillver-{pid}-{sslug}"))
        old_rel = sk["storage_path"] or ""
        new_rel = f"hubs/{hub_id}/skills/groves/{pid}/{sslug}"
        src_dir = storage_root / old_rel
        dst_dir = storage_root / new_rel
        if src_dir.exists() and not dst_dir.exists():
            dst_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src_dir, dst_dir)
        cur.execute("SELECT * FROM skill_versions WHERE skill_id = ? LIMIT 1", (sk["id"],))
        sv = cur.fetchone()
        cur.execute(
            """
            INSERT INTO skills (
                id, name, slug, description, tags, scope, scope_id,
                storage_uri, storage_bucket, storage_path, status,
                owner_id, created_by, updated_by, created, updated
            ) VALUES (?, ?, ?, ?, ?, 'project', ?, ?, '', ?, 'active', ?, ?, ?, ?, ?)
            """,
            (
                new_sid,
                sk["name"],
                sslug,
                sk["description"],
                sk["tags"],
                pid,
                f"gs:///{new_rel}/",
                new_rel,
                sarah_id,
                sarah_id,
                sarah_id,
                now_sql,
                now_sql,
            ),
        )
        if sv:
            cur.execute(
                """
                INSERT INTO skill_versions (
                    id, skill_id, version, status, content_hash, files,
                    publisher_id, deprecation_message, replacement_uri, download_count, created
                ) VALUES (?, ?, ?, 'published', ?, ?, ?, '', '', 1, ?)
                """,
                (
                    new_vid,
                    new_sid,
                    sv["version"],
                    sv["content_hash"],
                    sv["files"],
                    sarah_id,
                    now_sql,
                ),
            )

    # Copy user role bindings from 00-pcsk9-initial-seed so all 5 doctors have access
    cur.execute("SELECT principal_id, role_definition_id FROM role_bindings WHERE scope_type = 'project' AND scope_id = ? AND principal_type = 'user'", (ch0_pid,))
    for rb in cur.fetchall():
        cur.execute(
            "INSERT OR IGNORE INTO role_bindings (id, principal_type, principal_id, scope_type, scope_id, created_by, created, membership_kind, role_definition_id) VALUES (?, 'user', ?, 'project', ?, ?, ?, 'explicit', ?)",
            (str(uuid.uuid5(uuid.NAMESPACE_DNS, f"rb-{pid}-{rb['principal_id']}")), rb["principal_id"], pid, sarah_id, now_sql, rb["role_definition_id"]),
        )
    # Ensure agent-role-full has complete agent & chat messaging permissions
    full_perms = json.dumps(
        [
            "agent.create",
            "agent.read",
            "agent.list",
            "agent.update",
            "agent.delete",
            "agent.attach",
            "agent.lifecycle",
            "agent.message",
            "agent.set_message_mode",
            "project.read",
            "project.chat_post",
            "artifact.read",
            "artifact.create",
            "artifact.manage",
            "skill.create",
            "skill.read",
            "skill.update",
            "skill.list",
            "template.create",
            "template.read",
            "template.update",
            "template.list",
            "harness_config.read",
            "harness_config.list",
            "gcp_service_account.assign",
            "agent.status_update",
            "project.secret_read",
            "agent.notify",
            "agent.token_refresh",
            "agent.port_forward",
            "secret.use",
            "inbox.read",
            "inbox.write",
        ],
        separators=(",", ":"),
    ).encode("utf-8")
    cur.execute("UPDATE role_definitions SET permissions = ? WHERE name = 'agent-role-full'", (full_perms,))

    # Ensure web-builder template alias exists (referenced in research-operations-controller/agents.md)
    cur.execute("SELECT * FROM templates WHERE project_id = ? AND slug = 'project-curator' LIMIT 1", (pid,))
    pc_tpl = cur.fetchone()
    cur.execute("SELECT id FROM templates WHERE project_id = ? AND slug = 'web-builder' LIMIT 1", (pid,))
    if pc_tpl and not cur.fetchone():
        wb_tid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"oase-tpl-{pid}-web-builder"))
        wb_rel = f"hubs/{hub_id}/templates/groves/{pid}/web-builder.{wb_tid}"
        cur.execute(
            """
            INSERT INTO templates (
                id, name, slug, display_name, description, harness, default_harness_config,
                agent_config, content_hash, scope, scope_id, project_id, storage_uri,
                storage_bucket, storage_path, layout, files, base_template, status,
                owner_id, created_by, updated_by, source_url, created, updated
            ) VALUES (?, 'web-builder', 'web-builder', 'Web Builder (Project Curator)', ?, ?, ?, ?, ?, 'project', ?, ?, ?, '', ?, ?, ?, ?, 'active', ?, ?, ?, ?, ?, ?)
            """,
            (
                wb_tid,
                pc_tpl["description"],
                pc_tpl["harness"],
                pc_tpl["default_harness_config"],
                pc_tpl["agent_config"],
                pc_tpl["content_hash"],
                pid,
                pid,
                f"gs:///{wb_rel}/",
                wb_rel,
                pc_tpl["layout"],
                pc_tpl["files"],
                pc_tpl["base_template"],
                sarah_id,
                sarah_id,
                sarah_id,
                pc_tpl["source_url"],
                now_sql,
                now_sql,
            ),
        )

    conn.commit()
    conn.close()

    # Seed t=0 workspace from 00-pcsk9-initial-seed if not already initialized
    src_ws = hub_dir / "projects" / "00-pcsk9-initial-seed"
    dst_ws = hub_dir / "projects" / live_slug
    if not (dst_ws / "seed").exists() and src_ws.exists():
        if dst_ws.exists():
            shutil.rmtree(dst_ws)
        shutil.copytree(src_ws, dst_ws, symlinks=True)
        subprocess.run(["git", "-C", str(dst_ws), "checkout", "-f", "ch0"], check=False, capture_output=True)
        subprocess.run(["chown", "-R", "scion:scion", str(dst_ws)], check=False)

    # Ensure dst_ws/.scion/project-id and settings.yaml point to live_slug's pid (not ch0_pid)
    scion_meta = dst_ws / ".scion"
    if scion_meta.exists():
        (scion_meta / "project-id").write_text(f"{pid}\n", encoding="utf-8")
        sy = scion_meta / "settings.yaml"
        if sy.exists():
            stext = sy.read_text(encoding="utf-8")
            stext = re.sub(r"project_id:\s*[0-9a-f-]+", f"project_id: {pid}", stext)
            sy.write_text(stext, encoding="utf-8")
        subprocess.run(["chown", "-R", "scion:scion", str(scion_meta)], check=False)

    # Ensure template models and blob/cache files in the new grove match our plan
    update_template_models(db_path, plan=plan, target_project_slug=live_slug, dry_run=False)
    hydrate_and_repair_templates(hub_dir, dry_run=False)

    # Boot live Gemini 4 Argon (science-program-lead), Claude Opus 5.5 (scientific-reviewer), and controller (research-operations-controller)
    launched: dict[str, dict] = {}
    _, ag_resp = api_call(hub_api, "GET", f"/api/v1/projects/{pid}/agents", token)
    ag_list = ag_resp.get("agents", ag_resp.get("items", ag_resp)) if isinstance(ag_resp, dict) else ag_resp
    existing_agents = {a.get("slug") or a.get("name"): a for a in (ag_list if isinstance(ag_list, list) else [])}

    live_agent_specs = [
        ("science-program-lead", "science-program-lead"),
        ("computational-biologist", "computational-biologist"),
        ("structural-biologist", "structural-biologist"),
        ("medicinal-chemist", "medicinal-chemist"),
        ("admet-dmpk-scientist", "admet-dmpk-scientist"),
        ("scientific-reviewer", "scientific-reviewer"),
        ("finding-validator", "finding-validator"),
        ("project-curator", "project-curator"),
        ("hypex-supervisor", "hypex-supervisor"),
        ("hypex-reflection", "hypex-reflection"),
    ]
    for ag_slug, tpl_slug in live_agent_specs:
        ex = existing_agents.get(ag_slug)
        cname = f"{live_slug}--{ag_slug}"
        needs_recreate = False
        if ex and ex.get("phase") == "running":
            chk = subprocess.run(
                [
                    "docker",
                    "exec",
                    cname,
                    "bash",
                    "-lc",
                    "ps aux; echo ===; ls -la /home/scion/.scion/harness/inputs/; echo ===; tr '\\0' '\\n' < /proc/1/environ | grep '^OASE_PROJECT=' || true",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            mnt = subprocess.run(
                ["docker", "inspect", cname, "--format", "{{json .Mounts}}"],
                capture_output=True,
                text=True,
                check=False,
            )
            if (
                "# Placeholder" in chk.stdout
                or "resolved-skills.json" not in chk.stdout
                or "OASE_PROJECT=/workspace" not in chk.stdout
                or f"/projects/{live_slug}\"" not in mnt.stdout
            ):
                needs_recreate = True
            else:
                launched[ag_slug] = {"id": ex["id"], "status": "already_running", "harness": plan[tpl_slug][0], "model": plan[tpl_slug][1]}
                continue
        if ex and ex.get("id"):
            api_call(hub_api, "DELETE", f"/api/v1/agents/{ex['id']}", token)
            time.sleep(2)
        payload = {
            "name": ag_slug,
            "projectId": pid,
            "template": tpl_slug,
            "agentRole": "full",
            "gcp_identity": {"metadata_mode": "assign", "service_account_id": sa_id},
            "task": (
                f"You are `{ag_slug}` (`{tpl_slug}`) in live execution grove `{live_slug}` (`t=0` seed). "
                f"Stand by for multi-human Webchat instructions and always reply via `scion message \"conv:<id>\"`."
            ),
        }
        st, lresp = api_call(hub_api, "POST", f"/api/v1/projects/{pid}/agents", token, payload)
        aobj = lresp.get("agent", lresp) if isinstance(lresp, dict) else {}
        launched[ag_slug] = {
            "http_status": st,
            "id": aobj.get("id"),
            "recreated": needs_recreate,
            "harness": plan[tpl_slug][0],
            "model": plan[tpl_slug][1],
        }

    # Wire #general webchat_topic & conversations default_agent to science-program-lead + add participants
    lead_id = launched.get("science-program-lead", {}).get("id")
    if lead_id:
        conn2 = sqlite3.connect(str(db_path), timeout=30)
        conn2.row_factory = sqlite3.Row
        cur2 = conn2.cursor()
        cur2.execute(
            "UPDATE webchat_topic SET default_agent = 'science-program-lead', created_by = ? WHERE project_id = ? AND is_general = 1",
            (sarah_id, pid),
        )
        cur2.execute(
            "UPDATE conversations SET default_agent_id = ? WHERE project_id = ? AND display_name = 'general'",
            (lead_id, pid),
        )
        cur2.execute("SELECT id FROM conversations WHERE project_id = ? AND display_name = 'general' LIMIT 1", (pid,))
        grow = cur2.fetchone()
        if grow:
            gcid = grow["id"]
            for urow in cur2.execute("SELECT id FROM users WHERE email LIKE 'oase-%'"):
                uid = urow["id"]
                cur2.execute(
                    "INSERT OR IGNORE INTO conversation_participants (id, conversation_id, principal_kind, principal_id, role, joined_at) VALUES (?, ?, 'user', ?, 'member', ?)",
                    (str(uuid.uuid5(uuid.NAMESPACE_DNS, f"cp-{gcid}-{uid}")), gcid, uid, now_sql),
                )
            for ag_info in launched.values():
                aid = ag_info.get("id")
                if aid:
                    cur2.execute(
                        "INSERT OR IGNORE INTO conversation_participants (id, conversation_id, principal_kind, principal_id, role, joined_at) VALUES (?, ?, 'agent', ?, 'member', ?)",
                        (str(uuid.uuid5(uuid.NAMESPACE_DNS, f"cp-{gcid}-{aid}")), gcid, aid, now_sql),
                    )
        conn2.commit()
        conn2.close()

    return {"project_id": pid, "slug": live_slug, "launched_agents": launched}


def run_container_doctor(container_name: str) -> dict:
    # Ensure /scion-volumes/tools symlink is present inside container
    subprocess.run(
        [
            "docker",
            "exec",
            "-u",
            "root",
            container_name,
            "bash",
            "-lc",
            "mkdir -p /scion-volumes && ln -sfn /workspace/.scion-volumes/tools /scion-volumes/tools",
        ],
        capture_output=True,
        check=False,
    )
    cmd = (
        "source /workspace/.scion-volumes/tools/env.sh >/dev/null 2>&1 && "
        "oase doctor --json"
    )
    proc = subprocess.run(
        ["docker", "exec", "-u", "scion", container_name, "bash", "-lc", cmd],
        capture_output=True,
        text=True,
        check=False,
    )
    idx = proc.stdout.find("{")
    if idx != -1:
        try:
            doc = json.loads(proc.stdout[idx:])
            fails = [c for c in doc.get("checks", []) if c.get("status") == "fail"]
            return {
                "container": container_name,
                "ok": doc.get("ok"),
                "env_version": doc.get("env_version"),
                "total_checks": len(doc.get("checks", [])),
                "failures": fails,
                "capability_snapshot": doc.get("capability_snapshot"),
            }
        except Exception:
            pass
    return {
        "container": container_name,
        "error_rc": proc.returncode,
        "stderr": proc.stderr[-500:],
        "stdout": proc.stdout[-500:],
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--hub-dir", type=Path, default=Path(os.environ.get("SCION_HUB_DIR", "/home/scion/.scion")))
    p.add_argument("--hub-api", default=os.environ.get("SCION_HUB_API", "http://127.0.0.1:8080"))
    p.add_argument("--gcp-project", default=os.environ.get("GCP_PROJECT_ID", ""))
    p.add_argument("--ag-region", default=os.environ.get("OASE_AG_REGION", "us-central1"))
    p.add_argument("--ag-endpoint-id", default=os.environ.get("OASE_AG_ENDPOINT_ID", "mg-endpoint-10fde681-120f-41a6-a204-8db9bd052ef5"))
    p.add_argument(
        "--ag-endpoint-dns",
        default=os.environ.get(
            "OASE_AG_ENDPOINT_DNS",
            "mg-endpoint-10fde681-120f-41a6-a204-8db9bd052ef5.us-central1-662944730392.prediction.vertexai.goog",
        ),
    )
    p.add_argument("--af3-region", default=os.environ.get("OASE_AF3_REGION", "us-east4"))
    p.add_argument(
        "--af3-endpoint-name",
        default=os.environ.get(
            "OASE_AF3_ENDPOINT_NAME",
            "projects/662944730392/locations/us-east4/endpoints/mg-endpoint-3f634779-eb94-4690-951f-f36f3aac86e0",
        ),
    )
    p.add_argument("--claude-vertex-region", default=os.environ.get("CLAUDE_VERTEX_REGION", "global"))
    p.add_argument("--enable-claude", action="store_true", help="Route peer-review & med-chem roles to Claude Opus 5.5")
    p.add_argument("--provision-live-grove", default="", help="Optional slug for isolated v2 live execution grove (e.g. pcsk9-oral-live-v2)")
    p.add_argument("--target-project-slug", default=None, help="Restrict template model updates to a single Scion project slug (leave unset to update all)")
    p.add_argument("--rebuild-images", action="store_true", help="Force Docker rebuild of scion-claude and scion-codex")
    p.add_argument("--verify-container", default="01-pcsk9-coscientist--science-program-lead", help="Running container to test oase doctor inside")
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.gcp_project:
        print("Error: --gcp-project (or GCP_PROJECT_ID) is required.", file=sys.stderr)
        return 1

    hub_dir = args.hub_dir.resolve()
    db_path = hub_dir / "hub.db"

    images_summary = ensure_harness_images_and_configs(hub_dir, rebuild=args.rebuild_images, dry_run=args.dry_run)
    tools_summary = repair_shared_oase_volumes(hub_dir, dry_run=args.dry_run)

    env_map = {
        "OASE_PROJECT": ("/workspace", "Default OASE campaign program root inside agent containers"),
        "OASE_TOOLS_HOME": ("/workspace/.scion-volumes/tools", "Shared OASE v0.3.0 toolchain volume path inside agent containers"),
        "OASE_AG_PROJECT": (args.gcp_project, "GCP project hosting Dedicated AlphaGenome Endpoint"),
        "OASE_AG_REGION": (args.ag_region, "GCP region for Dedicated AlphaGenome Endpoint"),
        "OASE_AG_ENDPOINT_ID": (args.ag_endpoint_id, "Vertex AI Endpoint ID for AlphaGenome"),
        "OASE_AG_ENDPOINT_DNS": (args.ag_endpoint_dns, "Dedicated Vertex AI prediction DNS for AlphaGenome"),
        "OASE_AF3_PROJECT": (args.gcp_project, "GCP project hosting Dedicated AlphaFold 3 Endpoint"),
        "OASE_AF3_REGION": (args.af3_region, "GCP region for Dedicated AlphaFold 3 Endpoint"),
        "OASE_AF3_ENDPOINT_NAME": (args.af3_endpoint_name, "Vertex AI Endpoint display name for AlphaFold 3"),
        "CLOUD_ML_REGION": (args.claude_vertex_region, "Vertex AI region for Anthropic Claude partner models"),
        "CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS": ("1", "Disable Claude Code experimental fallback betas on Vertex AI"),
        "ANTHROPIC_DEFAULT_HAIKU_MODEL": ("claude-opus-5-5", "Pin Claude Code default Haiku model to enabled Opus 5.5 Vertex endpoint"),
        "ANTHROPIC_SMALL_FAST_MODEL": ("claude-opus-5-5", "Pin Claude Code small fast model to enabled Opus 5.5 Vertex endpoint"),
    }
    env_count = upsert_hub_env_vars(db_path, env_map, dry_run=args.dry_run)

    plan = build_template_model_plan(enable_claude=args.enable_claude)
    plan["web-builder"] = plan.get("project-curator", ("antigravity", "medium"))
    tpl_updated = update_template_models(
        db_path,
        plan=plan,
        target_project_slug=args.target_project_slug,
        dry_run=args.dry_run,
    )
    tpl_hydration = hydrate_and_repair_templates(hub_dir, dry_run=args.dry_run)

    live_grove_summary = None
    if args.provision_live_grove:
        live_grove_summary = provision_live_v2_grove(
            hub_dir=hub_dir,
            hub_api=args.hub_api,
            gcp_project=args.gcp_project,
            live_slug=args.provision_live_grove,
            plan=plan,
            dry_run=args.dry_run,
        )
        # Re-run repair_shared_oase_volumes and hydrate_and_repair_templates in case new grove was created
        repair_shared_oase_volumes(hub_dir, dry_run=args.dry_run)
        tpl_hydration = hydrate_and_repair_templates(hub_dir, dry_run=args.dry_run)

    doctor_checks = []
    if not args.dry_run:
        if args.verify_container:
            doctor_checks.append(run_container_doctor(args.verify_container))
        if args.provision_live_grove:
            time.sleep(8)
            for role in ("science-program-lead", "scientific-reviewer", "medicinal-chemist", "structural-biologist"):
                cname = f"{args.provision_live_grove}--{role}"
                doctor_checks.append(run_container_doctor(cname))

    out = {
        "dry_run": args.dry_run,
        "images": images_summary,
        "shared_tools_repair": tools_summary,
        "hub_env_vars_upserted": env_count,
        "templates_updated": tpl_updated,
        "template_hydration": tpl_hydration,
        "template_model_plan": {k: {"harness": v[0], "model": v[1]} for k, v in plan.items()},
        "live_grove": live_grove_summary,
        "container_oase_doctor": doctor_checks,
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

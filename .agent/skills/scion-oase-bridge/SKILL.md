---
name: scion-oase-bridge
description: Connect Antigravity (agy), Gemini CLI, or Jetski directly to the Argolis OASE Scion Hub (`scion-hub-oase` in `losiern-oase-workshop`) to inspect the 17-agent 4-tier discovery hierarchy, read live Grove artifacts (`decision-log.md`, `WO-001..008`, `reports/*.md`), and dispatch live directives to `@science-program-lead`, `@controller`, and domain specialists. Use whenever asked to connect to Scion/OASE, check campaign status (`io-cold-to-hot`, `pcsk9-oral-live-v2`, `open-agentic-science-engine`), message an OASE agent, or run the live Gemini/Antigravity workshop demo.
---

# Scion / OASE Bridge Skill (`scion-oase-bridge`)

This skill connects **Antigravity (`agy`)**, **Gemini CLI**, or **Jetski** to the live **OASE Scion Hub** (`scion-hub-oase`, project `losiern-oase-workshop`, zone `us-central1-c`, Web UI `https://scion-hub-oase-iap-proxy-zw7klespva-uc.a.run.app`).

## 1. Architecture & Canonical Projects

| Project Slug | Project UUID | Therapeutic Campaign | Hierarchy & State |
|---|---|---|---|
| `io-cold-to-hot` | `ab3d65d5-f32c-463e-be48-d535034de34f` | **Cold-to-Hot Immuno-Oncology** (`ENPP1` `IC-101` vs `Trex1` `IC-102` vs `ADAR1` `IC-103`; Series A `oase_enpp1_009` Wet-Lab Wall -> Series B `oase_enpp1_019`) | `17/17` running agents (4-tier DAG), `DEC-001`..`DEC-010` co-signed |
| `pcsk9-oral-live-v2` | `dfe725e0-2c33-4569-84b2-1af9bb7b96fa` | **Oral Small-Molecule PCSK9 Inhibitor** (`IC-001` cryptic `Pocket #1` vs `IC-002` flat `EGF-A`; lead `oase_pcsk9_014`) | `17/17` running agents (4-tier DAG), `DEC-001`..`DEC-010` co-signed |
| `open-agentic-science-engine` | `4df4c1ab-2091-4bd6-944b-da423d69fd3d` | **Base OASE Reference Grove** (`41` domain verification skills, `22` specialist templates, `78/78` `oase doctor` checks) | `17/17` running agents (4-tier DAG), clean sandbox for live prompts |

---

## 2. How to Call Scion Tools (MCP or CLI)

If the `scion` MCP server (`scripts/scion_mcp_server.py`) is registered in your MCP configuration, call its tools directly (`hub_status`, `list_projects`, `list_agents`, `dav_list`, `dav_read`, `get_messages`, `send_message`).

You can also invoke any tool directly via the `--cli` bridge from `/usr/local/google/home/losiern/dev/github/n0012/oase-workshop`:

```bash
# 1. Verify Hub connectivity, persona (Dr. Sarah Chen), and all 3 projects
python3 /usr/local/google/home/losiern/dev/github/n0012/oase-workshop/scripts/scion_mcp_server.py --cli hub_status

# 2. List the 17-agent 4-tier hierarchy for Cold-to-Hot IO (or pcsk9-oral-live-v2)
python3 /usr/local/google/home/losiern/dev/github/n0012/oase-workshop/scripts/scion_mcp_server.py --cli list_agents --project io-cold-to-hot

# 3. List workspace artifacts or read a specific report / Work Order / decision log
python3 /usr/local/google/home/losiern/dev/github/n0012/oase-workshop/scripts/scion_mcp_server.py --cli dav_list --project io-cold-to-hot --path reports
python3 /usr/local/google/home/losiern/dev/github/n0012/oase-workshop/scripts/scion_mcp_server.py --cli dav_read --project io-cold-to-hot --path decision-log.md
python3 /usr/local/google/home/losiern/dev/github/n0012/oase-workshop/scripts/scion_mcp_server.py --cli dav_read --project io-cold-to-hot --path reports/wet-lab-wall-readiness.md

# 4. Dispatch a live instruction to @science-program-lead (logs live into Scion Web UI + Cloud Logging and returns the grounded reply)
python3 /usr/local/google/home/losiern/dev/github/n0012/oase-workshop/scripts/scion_mcp_server.py --cli send_message \
  --project io-cold-to-hot \
  --agent science-program-lead \
  --message "Summarize why extracellular ENPP1 (IC-101) beat intracellular Trex1 (IC-102) in WO-001 and how Series B (oase_enpp1_019) resolved the DEC-008 Wet-Lab Wall."

# 5. Read the live Project Messages feed from Scion Hub
python3 /usr/local/google/home/losiern/dev/github/n0012/oase-workshop/scripts/scion_mcp_server.py --cli get_messages --project io-cold-to-hot --limit 10
```

> **Tip for Sub-100ms Latency During Live Demos:**
> Start a background IAP port-forward on port `18780` before the session so every MCP/CLI call completes in `<100ms`:
> ```bash
> CLOUDSDK_CORE_ACCOUNT=claude-vertex@losiern-vibe.iam.gserviceaccount.com \
>   gcloud compute start-iap-tunnel scion-hub-oase 8780 \
>   --local-host-port=127.0.0.1:18780 \
>   --project=losiern-oase-workshop --zone=us-central1-c &
> ```

---

## 3. Canonical 2-Prompt Live Demo Script (Antigravity × Scion Web UI)

1. **Prompt 1 — Connect & Inspect the 17-Agent Grove:**
   > *"Use the `scion-oase-bridge` skill to connect to our Argolis Scion Hub, verify all 3 OASE projects, and show the 4-tier 17-agent hierarchy and stage-gate status for `io-cold-to-hot`."*
2. **Prompt 2 — Live Directive to `@science-program-lead` & Wet-Lab Wall Audit:**
   > *"Send a live message to `@science-program-lead` in `io-cold-to-hot` asking why `oase_enpp1_009` hit the `DEC-008` Wet-Lab Wall and how Series B (`oase_enpp1_019`) recovered oral absorption, then show me the live Scion project link."*
   - After running Prompt 2, open `https://scion-hub-oase-iap-proxy-zw7klespva-uc.a.run.app/projects/ab3d65d5-f32c-463e-be48-d535034de34f` (Project Messages & Agent Graph) to show the live message and reply logged inside Scion.

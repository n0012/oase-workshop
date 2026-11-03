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

## 2. One-Command Setup in Google Cloud Shell or Local Terminal

Run `bash scripts/setup-sarah-cloudshell.sh` from the repository root (`oase-workshop`) to:
1. Set `GCP_PROJECT_ID=losiern-oase-workshop`, `OASE_GCP_ZONE=us-central1-c`, and `OASE_GCE_INSTANCE=scion-hub-oase`.
2. Symlink `scion-oase-bridge` into `~/.gemini/skills/`, `~/.gemini/antigravity/skills/`, and `~/.claude/skills/`.
3. Register the `scion` stdio MCP server (`scripts/scion_mcp_server.py`) in `~/.gemini/antigravity/mcp_config.json` and `~/.gemini/config/mcp_config.json`.

---

## 3. How to Call Scion Tools (MCP or CLI)

If the `scion` MCP server (`scripts/scion_mcp_server.py`) is registered in your MCP configuration, call its tools directly (`hub_status`, `bootstrap_campaign`, `list_projects`, `list_agents`, `dav_list`, `dav_read`, `get_messages`, `send_message`).

You can also invoke any tool directly via the `--cli` bridge from the `oase-workshop` repository root:

```bash
# 1. Verify Hub connectivity, persona (Dr. Sarah Chen), and all 3 projects
python3 scripts/scion_mcp_server.py --cli hub_status

# 2. Initiate / bootstrap a Science Agent campaign & verify oase doctor (78/78 checks)
python3 scripts/scion_mcp_server.py --cli bootstrap_campaign --project io-cold-to-hot

# 3. List the 17-agent 4-tier hierarchy for Cold-to-Hot IO (or pcsk9-oral-live-v2)
python3 scripts/scion_mcp_server.py --cli list_agents --project io-cold-to-hot

# 4. List workspace artifacts or read a specific report / Work Order / decision log
python3 scripts/scion_mcp_server.py --cli dav_list --project io-cold-to-hot --path executive
python3 scripts/scion_mcp_server.py --cli dav_read --project io-cold-to-hot --path program-state/decision-log.md
python3 scripts/scion_mcp_server.py --cli dav_read --project io-cold-to-hot --path executive/CANDIDATE-SUMMARY.md

# 5. Dispatch a live instruction to @science-program-lead (returns grounded reply in CLI AND logs live into Scion Web UI + Cloud Logging)
python3 scripts/scion_mcp_server.py --cli send_message \
  --project io-cold-to-hot \
  --agent science-program-lead \
  --message "Summarize why extracellular ENPP1 (IC-101) beat intracellular Trex1 (IC-102) in WO-001 and how Series B (oase_enpp1_019) resolved the DEC-008 Wet-Lab Wall."

# 6. Read the live Project Messages feed from Scion Hub
python3 scripts/scion_mcp_server.py --cli get_messages --project io-cold-to-hot --limit 10
```

> **Tip for Sub-100ms Latency During Live Demos:**
> Start a background IAP port-forward on port `18780` before the session so every MCP/CLI call completes in `<100ms`:
> ```bash
> gcloud compute start-iap-tunnel scion-hub-oase 8780 \
>   --local-host-port=127.0.0.1:18780 \
>   --project=losiern-oase-workshop --zone=us-central1-c &
> ```

---

## 4. Canonical 2-Prompt Live Demo Script (Feedback in `agy` CLI → Scion Web UI Reacts)

1. **Prompt 1 — Initiate Campaign & See Kickoff Feedback in `agy` CLI (`cs2_t1` → `cs2_t2`):**
   ```bash
   agy -p "Use scion-oase-bridge to bootstrap the io-cold-to-hot campaign, verify oase doctor (78/78 checks), list the 17-agent 4-tier discovery team, and show @controller and @science-program-lead's live kickoff feedback."
   ```
   - **In `agy` CLI:** Displays `oase doctor` (`78/78 PASS`), the 17-agent 4-tier roster, and `@science-program-lead`'s `DEC-001` / `WO-001` kickoff confirmation right inside the terminal.
   - **In Scion Web UI:** Open `https://scion-hub-oase-iap-proxy-zw7klespva-uc.a.run.app/projects/ab3d65d5-f32c-463e-be48-d535034de34f` (`Graph View` + `Show users` ON) to watch the 17-node 4-tier DAG react live.
2. **Prompt 2 — Analyze Completed Program Run & Audit the `DEC-008` Wet-Lab Wall (`cs2_t3` → `cs2_t4`):**
   ```bash
   agy -p "Use scion-oase-bridge to analyze io-cold-to-hot across WO-001..WO-008: read program-state/decision-log.md and executive/CANDIDATE-SUMMARY.md, and message @science-program-lead to explain why Series A (oase_enpp1_009) hit the DEC-008 Wet-Lab Wall and how Series B (oase_enpp1_019) recovered oral absorption."
   ```
   - **In `agy` CLI:** Displays `@science-program-lead`'s grounded reply and the side-by-side `Series A (oase_enpp1_009)` vs `Series B (oase_enpp1_019)` Wet-Lab Wall table directly in the terminal.
   - **In Scion Web UI:** Scroll to **Messages** on `https://scion-hub-oase-iap-proxy-zw7klespva-uc.a.run.app/projects/ab3d65d5-f32c-463e-be48-d535034de34f` to see both `[Cloud Shell · Antigravity (agy) CLI Feedback]` and `[Grounded Science Agent Reply -> agy CLI]` logged live at the top of the project message stream.

# Scion Grove Specialist Agent Personas & Container Task Prompts

Defines the 11 T-shaped specialist agents provisioned by [`scripts/seed-pilot-chapters.py`](../scripts/seed-pilot-chapters.py) across the 8 Scion Hub campaign checkpoints (`00-pcsk9-initial-seed` through `07-pcsk9-mission-closeout`).

---

## 1. Shared Epistemic & Two-Phase Execution Mandate (All OASE Agents)

Every specialist template inherits the core OASE epistemic contract from upstream `open-agentic-science-engine`:

```text
1. NEVER compute, round, or extrapolate scientific metrics in LLM prose. Every quantitative figure in `findings/<domain>/WO-*.md` MUST be produced by a deterministic Phase-2 `oase <tool> analyze` command and cited inline via `{source: raw/<class>/<stem>.analysis.json $.metrics.<key>}` (one citation per bullet line to avoid KaTeX `$` collisions).
2. Two-Phase Latch:
   - Phase 1 (`fetch` / `run` / `predict`): Writes immutable raw output to `raw/<class>/` alongside a cryptographic `<artifact>.meta.json` SHA-256 sidecar.
   - Phase 2 (`analyze`): Evaluates the raw output offline against version-locked `.oase/thresholds.yaml` schemas (`36/36` resolved) and emits `<stem>.analysis.json` with `verdict`, `metrics`, and `mandatory_relays`.
3. Mandatory Epistemic Caveat Relays: Every domain warning emitted in `.analysis.json` MUST be carried verbatim into the finding report as `**Relay: \`<code>\`**`. Dropping a caveat fails `oase validate check` (`REL-001`).
4. Separation of Powers: Specialist authors (`computational-biologist`, `structural-biologist`, `computational-chemist`, `medicinal-chemist`, `admet-dmpk-scientist`) never approve their own stage gates. All Work Orders pass `finding-validator` (`oase validate check`), independent `scientific-reviewer` critique, and `science-program-lead` + human scientist co-signature.
```

---

## 2. Live Checkpoint Container Task Prompt (`seed-pilot-chapters.py`)

When [`scripts/seed-pilot-chapters.py`](../scripts/seed-pilot-chapters.py) launches the live specialist containers inside each chapter's Scion project (`ch0`..`ch7`), each container receives the following chapter-scoped standby task prompt:

```text
You are `{ag_slug}` for chapter `{ch}` (`{slug}`) of the PCSK9 oral small-molecule discovery campaign in `/workspace`. Verify `/workspace` state (do NOT modify `.oase/` unless explicitly instructed by a scientist in Webchat). When a human scientist messages you in Webchat, give a concise, quantitative, citation-backed answer grounded in `/workspace/program-state/`, `/workspace/findings/`, and `/workspace/gates/`. Stand by.
```

---

## 3. 11-Agent Grove Roster & T-Shaped Tool Scopes

| Agent Slug | Scion Template | Model Tier / Family | Vertical Tool Bench & Responsibility |
| :--- | :--- | :--- | :--- |
| `science-program-lead` | `science-program-lead` | Frontier Reasoning (`Gemini 4 Argon (High)` — `antigravity/extra-large`) | Coordinates multi-stage campaign routing, weighs cross-discipline trade-offs, maintains `program-state/decision-log.md`, and co-signs Stage Gates `1`–`4` + `Step 7` closeout. |
| `computational-biologist` | `computational-biologist` | Frontier Reasoning (`Gemini 4 Argon (Medium)` — `antigravity/large`) | Runs `oase coscientist`, `oase genetics` (`gnomAD`), `oase gwas` (`OpenTargets`), `oase gtex`, `oase expression` (`HPA`), and `oase alphagenome` (`WO-001`..`WO-003`). |
| `structural-biologist` | `structural-biologist` | Frontier Reasoning (`Gemini 4 Argon (High)` — `antigravity/extra-large`) | Runs `oase alphafold fetch/predict` (`AFDB` + `AlphaFold 3` co-folding) and `oase pocket run/analyze` (`fpocket 4.2.2` cryptic groove vs flat PPI surface) (`WO-004`). |
| `computational-chemist` | `computational-chemist` | Frontier Reasoning (`Gemini 4 Argon (Medium)` — `antigravity/large`) | Runs `oase docking prepare/run/analyze` (`Meeko` + `AutoDock Vina 1.2.5`) and `oase docking contacts` (`WO-005`). |
| `medicinal-chemist` | `medicinal-chemist` | Cross-Family (`Claude Opus 5.5` — `claude/large`) | Runs `oase compound`, `oase mmp`, `oase analog`, and `oase retro` to resolve structural liabilities (`PCSK9-A02` CF3-thiazole -> `OASE-PCSK9-014` 1,2,4-oxadiazole) (`WO-006`). |
| `admet-dmpk-scientist` | `admet-dmpk-scientist` | Frontier Reasoning (`Gemini 4 Argon (Medium)` — `antigravity/large`) | Runs `oase admet` (`admet-endpoints@1.0` Aronov hERG gate), stages Wet-Lab / CRO assay handoffs, and runs `oase pk` human allometric dose projection (`40.0 mg QD`) (`WO-006`..`WO-007`). |
| `scientific-reviewer` | `scientific-reviewer` | Cross-Family (`Claude Opus 5.5` — `claude/large`) | Performs independent peer review on specialist findings using a distinct model family (`Anthropic Claude Opus 5.5` vs `Gemini 4 Argon`) to eliminate shared model blind spots. |
| `finding-validator` | `finding-validator` | Deterministic CLI + Fast (`Gemini 3.8 Flash (Medium)` — `antigravity/medium`) | Executes `oase validate check` (`10` checks: SHA-256 `provenance_valid`, ±1% JSONPath `source_tags_resolve`, `relay_coverage`, `analysis_citations`) and blocks tampered/ungrounded claims. |
| `project-curator` | `project-curator` | Fast (`Gemini 3.8 Flash (Medium)` — `antigravity/medium`) | Compiles `WO-008` candidate nomination dossiers, runs `oase trials`, `oase site validate/build/export`, and publishes Scion Hub artifacts. |
| `controller` | `research-operations-controller` | Fast (`Gemini 3.8 Flash (Medium)` — `antigravity/medium`) | Manages `.oase/control/work-orders/WO-*.json`, `.oase/control/events.ndjson`, and human-signed override receipts (`DEC-OVERRIDE-001.json`). |
| `hypex-supervisor` | `hypex-supervisor` | Frontier Reasoning (`Gemini 4 Argon (High)` — `antigravity/extra-large`) | Supervises Stage 0 pairwise hypothesis Elo tournaments (`elo` / `hypex` binaries, with `hypex-reflection` on `Claude Opus 5.5`) and seed lineage verification. |

See [`docs/SCION_RUNTIME_AND_MODELS.md`](../docs/SCION_RUNTIME_AND_MODELS.md) for the repeatable enablement and reconciliation runbook (`scripts/enable-vertex-models.py` and `scripts/reconcile-scion-runtime.py`).

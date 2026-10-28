#!/usr/bin/env python3
"""Augments `oase site build` output (`_site/`) with `chapters.html` and article visual plates.

Provides an interactive 3-Act Walkthrough covering:
  - Act I: Why Chatbot Science Fails & How Scion + OASE Solves It (`#why`, `#scion`)
  - Act II: Live PCSK9 Campaign Simulation & 4 Adversarial Governance Drills (`#ch1`..`#ch5`)
  - Act III: The Complete Picture, 31-Page Portal & Architecture Scorecard (`#ch6`)
"""

from __future__ import annotations

import os
import pathlib
import shutil
import sys

CHAPTERS_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GCP-OASE &amp; Scion — Architecture, Value Proposition &amp; Campaign Walkthrough</title>
<style>
  body { font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 0; color: #1a1a1a; background: #f4f6f8; }
  nav { background: #1e293b; color: #f8fafc; padding: 0.85rem 2rem; display: flex; align-items: center; justify-content: space-between; border-bottom: 3px solid #2563eb; }
  nav .left a { color: #e2e8f0; text-decoration: none; margin-right: 1.5rem; font-size: 0.92rem; }
  nav .left a:hover, nav .left a.active-nav { color: #ffffff; font-weight: 600; text-decoration: underline; }
  nav .nav-title { font-weight: 700; font-size: 1.05rem; margin-right: 2rem; color: #ffffff; }
  .badge-env { background: #0f172a; color: #38bdf8; border: 1px solid #0284c7; padding: 0.25rem 0.65rem; border-radius: 4px; font-family: monospace; font-size: 0.8rem; }
  .hero { background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); color: #ffffff; padding: 1.75rem 2.5rem; }
  .hero h1 { margin: 0 0 0.45rem 0; font-size: 1.68rem; color: #ffffff; }
  .hero p { margin: 0; color: #cbd5e1; font-size: 0.98rem; max-width: 980px; line-height: 1.5; }
  .kpi-strip { display: grid; grid-template-columns: repeat(6, 1fr); gap: 0.85rem; margin-top: 1.25rem; }
  .kpi-card { background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.16); border-radius: 6px; padding: 0.75rem 0.9rem; }
  .kpi-card .kpi-val { font-size: 1.25rem; font-weight: 700; color: #38bdf8; font-family: monospace; }
  .kpi-card .kpi-lbl { font-size: 0.74rem; color: #cbd5e1; margin-top: 0.2rem; text-transform: uppercase; letter-spacing: 0.04em; }

  .chapter-bar { background: #ffffff; border-bottom: 1px solid #cbd5e1; padding: 0.65rem 2rem; display: flex; gap: 0.5rem; flex-wrap: wrap; position: sticky; top: 0; z-index: 20; box-shadow: 0 2px 4px rgba(0,0,0,0.04); }
  .chapter-btn { background: #f1f5f9; border: 1px solid #cbd5e1; color: #334155; padding: 0.45rem 0.8rem; border-radius: 6px; font-weight: 600; font-size: 0.82rem; cursor: pointer; transition: all 0.15s; }
  .chapter-btn:hover { background: #e2e8f0; }
  .chapter-btn.active { background: #2563eb; color: #ffffff; border-color: #1d4ed8; }
  .chapter-btn.act1 { border-left: 3px solid #0284c7; }

  .container { max-width: 1360px; margin: 1.25rem auto; padding: 0 2rem 3rem 2rem; }
  .chapter-panel { display: none; background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 1.5rem 2rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 1.5rem; }
  .chapter-panel.active { display: block; }
  .chapter-header { display: flex; justify-content: space-between; align-items: baseline; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.75rem; margin-bottom: 1.25rem; }
  .chapter-header h2 { margin: 0; color: #0f172a; font-size: 1.32rem; }
  .stage-pill { background: #dbeafe; color: #1e40af; font-weight: 700; font-size: 0.78rem; padding: 0.25rem 0.65rem; border-radius: 999px; font-family: monospace; }

  .grid-2 { display: grid; grid-template-columns: 1.05fr 0.95fr; gap: 1.5rem; align-items: start; }
  .plate-box { background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 0.6rem; text-align: center; margin-bottom: 1rem; }
  .plate-box img { width: 100%; height: auto; border-radius: 5px; display: block; }
  .plate-caption { color: #94a3b8; font-size: 0.78rem; margin-top: 0.45rem; font-family: monospace; }
  .pillar-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.85rem; margin: 0.85rem 0; }
  .pillar-card { background: #f8fafc; border: 1px solid #cbd5e1; border-left: 4px solid #2563eb; border-radius: 6px; padding: 0.75rem 0.95rem; }
  .pillar-card h4 { margin: 0 0 0.3rem 0; color: #0f172a; font-size: 0.92rem; }
  .pillar-card p { margin: 0; color: #334155; font-size: 0.83rem; line-height: 1.42; }

  table { border-collapse: collapse; width: 100%; margin: 0.75rem 0; font-size: 0.88rem; }
  th, td { text-align: left; padding: 0.52rem 0.7rem; border-bottom: 1px solid #e2e8f0; }
  th { background: #f8fafc; font-weight: 600; color: #334155; }
  .pass-pill { background: #dcfce7; color: #166534; font-weight: 700; padding: 0.15rem 0.5rem; border-radius: 4px; font-family: monospace; font-size: 0.78rem; }
  .fail-pill { background: #fee2e2; color: #991b1b; font-weight: 700; padding: 0.15rem 0.5rem; border-radius: 4px; font-family: monospace; font-size: 0.78rem; }
  .warn-pill { background: #fef3c7; color: #92400e; font-weight: 700; padding: 0.15rem 0.5rem; border-radius: 4px; font-family: monospace; font-size: 0.78rem; }
  .terminal { background: #0f172a; color: #e2e8f0; padding: 1rem 1.2rem; border-radius: 6px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.81rem; line-height: 1.48; overflow-x: auto; white-space: pre-wrap; border: 1px solid #334155; }
  .terminal .cmd { color: #38bdf8; font-weight: 600; }
  .terminal .ok { color: #4ade80; font-weight: 600; }
  .terminal .err { color: #f87171; font-weight: 600; }
  .relay-box { background: #fffbeb; border-left: 4px solid #f59e0b; padding: 0.75rem 1rem; margin-top: 0.9rem; border-radius: 0 4px 4px 0; font-size: 0.86rem; }
  .portal-links { margin-top: 1rem; display: flex; gap: 0.75rem; flex-wrap: wrap; }
  .portal-links a { background: #eff6ff; border: 1px solid #bfdbfe; color: #1d4ed8; text-decoration: none; padding: 0.4rem 0.75rem; border-radius: 5px; font-size: 0.83rem; font-weight: 600; }
  .portal-links a:hover { background: #dbeafe; }
</style>
</head>
<body>
<nav>
  <div class="left">
    <span class="nav-title">GCP-OASE &amp; Scion — pcsk9-oral</span>
    <a href="index.html">Portal Home (30 Pages)</a>
    <a href="chapters.html" class="active-nav">Architecture, Value Prop &amp; Campaign Replay</a>
    <a href="finding_findings_regulatory_WO-008_md.html">WO-008 Candidate Dossier</a>
  </div>
  <span class="badge-env">Project: __PROJECT_BADGE__ | scion + oase 0.3.0 | ENV __ENV_SHA__</span>
</nav>

<div class="hero">
  <h1>From Isolated Chatbots to Team-Based, Provenance-Locked Pre-Clinical R&amp;D on Google Cloud</h1>
  <p>Combining <strong>Google Cloud Scion</strong> (multi-user Projects/Groves, model-agnostic Harnesses across Gemini, Claude &amp; OpenAI, 22 specialized agent templates, and <code>suspended</code> CRO session continuation) with <strong>O.A.S.E. — the Open Agentic Science Engine</strong> (two-phase tool latches, SHA-256 sidecars, and 10-check Dual Validation).</p>
  <div class="kpi-strip">
    <div class="kpi-card"><div class="kpi-val">4 Tiers / 22</div><div class="kpi-lbl">Scion Agent Templates</div></div>
    <div class="kpi-card"><div class="kpi-val">36 / 36</div><div class="kpi-lbl">Threshold Sets Resolved</div></div>
    <div class="kpi-card"><div class="kpi-val">8 / 8 [PASS]</div><div class="kpi-lbl">Work Orders Accepted</div></div>
    <div class="kpi-card"><div class="kpi-val">4 / 4 Caught</div><div class="kpi-lbl">Adversarial Tamper Drills</div></div>
    <div class="kpi-card"><div class="kpi-val">OASE-PCSK9-014</div><div class="kpi-lbl">Nominated Oral Lead (40 mg QD)</div></div>
    <div class="kpi-card"><div class="kpi-val">31 Pages</div><div class="kpi-lbl">Static Evidence Portal</div></div>
  </div>
</div>

<div class="chapter-bar">
  <button class="chapter-btn act1 active" id="btn-why" onclick="showChapter('why')">1. Why Chatbot Science Fails</button>
  <button class="chapter-btn act1" id="btn-scion" onclick="showChapter('scion')">2. Scion + OASE Value &amp; Architecture</button>
  <button class="chapter-btn" id="btn-ch1" onclick="showChapter('ch1')">3. Stage 0 Tournament (WO-001)</button>
  <button class="chapter-btn" id="btn-ch2" onclick="showChapter('ch2')">4. Stage 1 Genetics &amp; Omics (WO-002..003)</button>
  <button class="chapter-btn" id="btn-ch3" onclick="showChapter('ch3')">5. Stage 2 AF3 &amp; Docking (WO-004..005)</button>
  <button class="chapter-btn" id="btn-ch4" onclick="showChapter('ch4')">6. Stages 3–4 DMTA &amp; hERG Gate (WO-006..007)</button>
  <button class="chapter-btn" id="btn-ch5" onclick="showChapter('ch5')">7. 4 Adversarial Tamper Drills</button>
  <button class="chapter-btn" id="btn-ch6" onclick="showChapter('ch6')">8. Complete Picture &amp; Scorecard</button>
</div>

<div class="container">
  <!-- PANEL WHY: THE PROBLEM & 4 REAL-WORLD FAILURE MODES -->
  <section class="chapter-panel active" id="panel-why">
    <div class="chapter-header">
      <h2>Act I (Part 1) — Why Agentic Drug Discovery Is Harder Than It Looks</h2>
      <span class="stage-pill">Problem Statement · 4 Failure Modes in Unchecked AI Pipelines</span>
    </div>
    <div class="grid-2">
      <div>
        <div class="plate-box" id="plate-challenges">
          <img src="assets/oase_challenges.jpg" alt="Agentic Drug Discovery Challenges">
          <div class="plate-caption">Figure 1 — The 4 structural failure modes that break static DAGs and single-player chatbots in pre-clinical R&amp;D.</div>
        </div>
        <div class="plate-box" id="plate-thumb">
          <img src="assets/oase_post_thumbnail.jpg" alt="GCP-OASE Platform Overview">
          <div class="plate-caption">Figure 2 — Moving from single-player chatbot prompts to team-based, provenance-locked discovery on Google Cloud.</div>
        </div>
      </div>
      <div>
        <p>Giving an LLM access to biological APIs is easy; making its conclusions <strong>auditable by a pharma stage-gate governance board</strong> requires solving four failure modes observed across real discovery pilots:</p>
        <table>
          <thead><tr><th>Discovery Failure Mode</th><th>What an Unguarded Chatbot / Static DAG Does</th><th>How GCP-OASE + Scion Solves It</th></tr></thead>
          <tbody>
            <tr id="why-row-1">
              <td><strong>1. Rigid Pipeline vs. Biological Surprise</strong><br>(<code>Pilot-4</code> Liver Fibrosis)</td>
              <td>Drops a target when bulk GTEx liver RNA-seq returns near-zero expression.</td>
              <td>Pivots dynamically to slice a 58k-cell cirrhotic <code>.h5ad</code> atlas (<code>oase h5ad</code>) and isolates activated hepatic stellate cells.</td>
            </tr>
            <tr id="why-row-2">
              <td><strong>2. Hallucinated Numbers &amp; Padded Citations</strong><br>(<code>Pilot-9b</code> Hidradenitis Suppurativa)</td>
              <td>Summarizes 50 MB tables in context, invents plausible IC50s, or rubber-stamps weak Stage 0 seeds.</td>
              <td>Enforces <strong>Two-Phase Tool Latches</strong> + <code>{source: path $.jsonpath}</code> citations checked within <strong>&plusmn;1%</strong>; advanced <code>0/8</code> weak seeds (<code>DEC-145</code>).</td>
            </tr>
            <tr id="why-row-3">
              <td><strong>3. Optimism Bias &amp; Dropped Caveats</strong><br>(<code>pcsk9-oral</code> &amp; <code>Pilot-6</code> NSCLC)</td>
              <td>Celebrates a tight docking score (`-9.4 kcal/mol`) while quietly omitting a `hERG` cardiac liability or `A549` `STK11`/`KEAP1` mutation.</td>
              <td>Every Phase-2 <code>.analysis.json</code> emits mandatory <code>**Relay: `code`**</code> caveats; dropping any caveat fails <code>REL-001</code> validation.</td>
            </tr>
            <tr id="why-row-4">
              <td><strong>4. Single-Model Echo Chambers &amp; Wet-Lab Gaps</strong></td>
              <td>Uses one model vendor to generate, interpret, and review its own hypotheses with no way to pause for 3-week CRO assays.</td>
              <td><strong>Scion Harnesses</strong> mix Gemini, Claude, and OpenAI in one Project and use Scion's <code>suspended</code> phase to pause/resume across CRO cycles.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>

  <!-- PANEL SCION: SCION + OASE VALUE PROPOSITION & ARCHITECTURE -->
  <section class="chapter-panel" id="panel-scion">
    <div class="chapter-header">
      <h2>Act I (Part 2) — Google Cloud Scion + O.A.S.E. Control &amp; Data Architecture</h2>
      <span class="stage-pill">Scion Hub · 4 Tiers / 22 Templates · Two-Phase Artifact Latch</span>
    </div>
    <div class="grid-2">
      <div>
        <div class="plate-box" id="plate-benefits">
          <img src="assets/oase_benefits.jpg" alt="GCP-OASE Value Proposition">
          <div class="plate-caption">Figure 3 — Four core value pillars: Team Collaboration, Multi-Model Heterogeneity, CRO Pause/Resume, and Provenance Gates.</div>
        </div>
        <div class="plate-box" id="plate-arch">
          <img src="assets/oase_data_arch.jpg" alt="GCP-OASE Data and Control Architecture">
          <div class="plate-caption">Figure 4 — Surface-to-OASE Contract, 4-Tier / 22-Template Scion Project Roster, and Layer 0 &rarr; Layer 1 &rarr; Layer 2 Data Flow.</div>
        </div>
      </div>
      <div>
        <div class="pillar-grid">
          <div class="pillar-card" id="scion-card-1">
            <h4>1. Scion Hub, Projects &amp; Runtime Brokers</h4>
            <p>The <strong>Scion Hub</strong> coordinates OAuth identity, WebDAV workspace state, and container orchestration across <strong>Projects (Groves)</strong>. Runtime Brokers run isolated agent containers on Docker, GKE Kubernetes, or GKE Agent Substrate.</p>
          </div>
          <div class="pillar-card" id="scion-card-2">
            <h4>2. Model-Agnostic Harnesses (Gemini + Claude + OpenAI)</h4>
            <p>Scion <strong>Harness-Configs</strong> (<code>GeminiCLI</code>, <code>ClaudeCode</code>, <code>Codex</code>) wrap heterogeneous models into a uniform OCI lifecycle so a Claude or OpenAI <code>scientific-reviewer</code> can adversarially audit a Gemini specialist.</p>
          </div>
          <div class="pillar-card" id="scion-card-3">
            <h4>3. 3D Agent State: <code>blocked</code> &amp; <code>suspended</code></h4>
            <p>OASE specialists idle in Scion's sticky <code>blocked</code> activity on a push-only message bus (zero polling tokens) and enter Scion's <code>suspended</code> phase during multi-week wet-lab CRO assays—resuming the exact session via <code>--resume</code> when CSVs return.</p>
          </div>
          <div class="pillar-card" id="scion-card-4">
            <h4>4. 4-Tier / 22-Template Roster &amp; Dual Validation</h4>
            <p>Separates <strong>Authority</strong> (<code>science-program-lead</code>, sole writer of Layer 2), <strong>Operations</strong> (<code>research-operations-controller</code>, <code>finding-validator</code>), <strong>9 Domain/Review Specialists</strong>, and <strong>7 HypEx Tournament Agents</strong>.</p>
          </div>
        </div>
        <table>
          <thead><tr><th>OASE Storage Layer</th><th>Writer Role</th><th>Mechanical Contract Enforced by <code>oase validate check</code></th></tr></thead>
          <tbody>
            <tr id="arch-row-1"><td><strong>Layer 0 (`raw/<class>/`)</strong></td><td>Phase-1 &amp; Phase-2 CLI Tools</td><td>Immutable raw files + SHA-256 <code>.meta.json</code> sidecars (<code>PROV-001/002</code>) + offline <code>.analysis.json</code> against 36 threshold schemas (<code>THR-001</code>).</td></tr>
            <tr id="arch-row-2"><td><strong>Layer 1 (`findings/<domain>/`)</strong></td><td>8 Ephemeral Specialists</td><td>Markdown synthesis where every number carries a <code>{source: ... $.metrics.x}</code> tag (&plusmn;1%, <code>CIT-003</code>) and every caveat relay is preserved (<code>REL-001</code>).</td></tr>
            <tr id="arch-row-3"><td><strong>Layer 2 (`program-state/`)</strong></td><td><code>science-program-lead</code> Only</td><td>Promoted only after passing <strong>Validation 1</strong> (10-check mechanical validator) + <strong>Validation 2</strong> (independent scientific review).</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>

  <!-- CHAPTER 1 -->
  <section class="chapter-panel" id="panel-ch1">
    <div class="chapter-header">
      <h2>Act II (Chapter 1) — Stage 0 Campaign Seed &amp; Co-Scientist Tournament (`WO-001`)</h2>
      <span class="stage-pill">Stage 0 · checkpoints/ch0 &rarr; ch1</span>
    </div>
    <div class="grid-2">
      <div>
        <p>The campaign begins by verifying environment health (<code>oase doctor</code> across all 7 compiled scientific binaries and 36 threshold schemas) and ingesting the AI Co-Scientist hypothesis tournament export (2 carried candidate series from the 28-match seed export) for oral PCSK9 inhibition in ASCVD.</p>
        <table>
          <thead><tr><th>Hypothesis ID</th><th>Modality &amp; Mechanism</th><th>Live CLI / Seed Elo</th><th>Win Rate</th><th>Status</th></tr></thead>
          <tbody>
            <tr><td><code>IC-001</code> (H-001)</td><td>Allosteric Small Molecule (`Pocket #1` groove)</td><td><strong>1642.5</strong> (`ELO 1642`)</td><td>0.78 (7/9)</td><td><span class="pass-pill">PRIMARY LEADER (+54.5 Elo)</span></td></tr>
            <tr><td><code>IC-002</code> (H-002)</td><td>Oral Cyclic Peptide (`EGF-A` flat surface)</td><td>1588.0 (`ELO 1588`)</td><td>0.67 (6/9)</td><td><span class="warn-pill">BACKUP SERIES</span></td></tr>
          </tbody>
        </table>
        <div class="relay-box">
          <strong>Mandatory Relay (`hypothesis.adopted_not_generated`):</strong> Staged Co-Scientist tournament exports are hypotheses, not primary evidence. Every biological claim must be independently verified by Stage 1 and Stage 2 tools.
        </div>
        <div class="portal-links">
          <a href="finding_findings_computational-biology_WO-001_md.html">View WO-001 Finding</a>
          <a href="artifact_hypotheses.html">View Hypotheses Layer 0 Artifact</a>
        </div>
      </div>
      <div class="terminal"><span class="cmd">$ oase coscientist ingest checkpoints/ch0/seed/pcsk9-oral/coscientist-export.json</span>
raw/hypotheses/cs-daedalis-20261028-pcsk9-oral.export.json
raw/hypotheses/cs-daedalis-20261028-pcsk9-oral.tournament.json
raw/hypotheses/cs-daedalis-20261028-pcsk9-oral.meta.json

<span class="cmd">$ oase coscientist analyze raw/hypotheses/cs-daedalis-20261028-pcsk9-oral.tournament.json</span>
Tournament: Oral Small-Molecule &amp; Macrocycle PCSK9 Inhibitors in ASCVD
<span class="ok">Verdict: clear-leader [threshold_set coscientist@1.1+program]</span>
Leader: PCSK9 (ELO 1642, +54 ELO over #2)
Ideas: 2 carried of 2 generated
Flagged ideas: 0</div>
    </div>
  </section>

  <!-- CHAPTER 2 -->
  <section class="chapter-panel" id="panel-ch2">
    <div class="chapter-header">
      <h2>Act II (Chapter 2) — Stage 1 Target Validation: Human Genetics, GWAS &amp; Expression (`WO-002`..`WO-003`)</h2>
      <span class="stage-pill">Stage 1 · checkpoints/ch1</span>
    </div>
    <div class="grid-2">
      <div>
        <p>Before spending compute on 3D docking, the Computational Biologist runs live Phase-1/Phase-2 queries against <code>gnomAD</code>, <code>OpenTargets</code>, <code>GTEx</code>, and <code>HPA</code> (`live-runs/`), and validates the pre-seeded campaign checkpoint (`WO-002`..`WO-003`, which also includes the offline <code>AlphaGenome</code> `rs2479409` fixture).</p>
        <table>
          <thead><tr><th>Evidence Stream</th><th>Live API CLI Output (`live-runs/`)</th><th>Seeded Checkpoint (`WO-002..003`)</th><th>Threshold</th><th>Verdict</th></tr></thead>
          <tbody>
            <tr><td><code>gnomAD v4</code> (`WO-002`)</td><td><code>pLI = 2.77e-18</code>, <code>LOEUF = 1.144</code></td><td><code>pLI = 0.0001</code>, <code>LOEUF = 0.89</code></td><td><code>pLI &lt; 0.90</code></td><td><span class="pass-pill">LOF_TOLERANT</span></td></tr>
            <tr><td><code>OpenTargets</code> (`WO-002`)</td><td>FH score <code>0.86</code> (clinical <code>0.97</code>)</td><td>FH score <code>0.96</code> (CHD <code>-68%</code>)</td><td><code>&ge; 0.70</code></td><td><span class="pass-pill">ASSOCIATIONS_FOUND</span></td></tr>
            <tr><td><code>GTEx / HPA</code> (`WO-002`)</td><td>HPA liver <code>47.5 nTPM</code> (13/50 tissues)</td><td>GTEx liver <code>184.2 TPM</code> (<code>tau = 0.93</code>)</td><td><code>&ge; 100 TPM</code> / <code>&ge; 10 nTPM</code></td><td><span class="pass-pill">TISSUE_ENRICHED</span></td></tr>
            <tr><td><code>AlphaGenome</code> (`WO-003`)</td><td><em>Seeded offline fixture</em></td><td>`rs2479409` liver quantile <code>0.984</code></td><td><code>&ge; 0.95</code></td><td><span class="pass-pill">HEPATOCYTE_CONFIRMED</span></td></tr>
          </tbody>
        </table>
        <div class="relay-box">
          <strong>Mandatory Relay (`gnomad.constraint_is_not_safety`):</strong> Germline LoF tolerance reflects lifelong compensation from conception and does not replace acute small-molecule off-target toxicology.
        </div>
        <div class="portal-links">
          <a href="finding_findings_computational-biology_WO-002_md.html">View WO-002 Finding</a>
          <a href="finding_findings_computational-biology_WO-003_md.html">View WO-003 Finding</a>
          <a href="artifact_genomics.html">View Genomics Artifacts</a>
        </div>
      </div>
      <div class="terminal"><span class="cmd">$ oase genetics fetch PCSK9 &amp;&amp; oase genetics analyze PCSK9</span>
<span class="ok">PCSK9 (ENSG00000169174) -&gt; LOF_TOLERANT</span>
pLI 2.765e-18 (&gt;= 0.9 intolerant) | LOEUF 1.144 (&lt; 0.35 constrained) | obs/exp LoF 57/62.1

<span class="cmd">$ oase gwas search PCSK9 &amp;&amp; oase gwas analyze PCSK9</span>
<span class="ok">PCSK9 -&gt; ASSOCIATIONS_FOUND (25/25 above threshold)</span>
familial hypercholesterolemia: Overall score: 0.86 (clinical=0.97, genetic_association=0.87)

<span class="cmd">$ oase expression fetch PCSK9 &amp;&amp; oase expression analyze PCSK9</span>
PCSK9 (ENSG00000169174) — HPA consensus RNA
<span class="ok">specificity: tissue enriched; detected in 13/50 tissues at &ge;1.0 nTPM</span>
highest: liver 47.5 nTPM</div>
    </div>
  </section>

  <!-- CHAPTER 3 -->
  <section class="chapter-panel" id="panel-ch3">
    <div class="chapter-header">
      <h2>Act II (Chapter 3) — Stage 2 Structural Biology, AlphaFold &amp; Pocket/Docking Analysis (`WO-004`..`WO-005`)</h2>
      <span class="stage-pill">Stage 2 · checkpoints/ch2</span>
    </div>
    <div class="grid-2">
      <div>
        <p>We run live <code>oase alphafold fetch/analyze Q8NBP7</code> and compiled <code>fpocket 4.2.2</code> (<code>oase pocket run/analyze</code>) on the full-length AFDB monomer (`live-runs/`), alongside the seeded <code>AlphaFold 3</code> ligand co-fold and <code>AutoDock Vina 1.2.5</code> pose fixtures in `WO-004`..`WO-005`.</p>
        <table>
          <thead><tr><th>Tool &amp; Work Order</th><th>Live CLI Output (`live-runs/`)</th><th>Seeded Checkpoint (`WO-004..005`)</th><th>Cutoff</th><th>Verdict</th></tr></thead>
          <tbody>
            <tr><td><code>oase alphafold</code> (`WO-004`)</td><td>Global pLDDT <code>85.19</code> (domain <code>58–542</code>)</td><td>Ordered catalytic/EGF-A pLDDT <code>91.4</code></td><td><code>&ge; 70.0</code></td><td><span class="pass-pill">CONFIDENT_FOLD</span></td></tr>
            <tr><td><code>AlphaFold 3</code> (`WO-004`)</td><td><em>Seeded GPU co-fold fixture</em></td><td>`IC-001` co-fold <code>ipTM = 0.84</code>, <code>pTM = 0.88</code></td><td><code>&ge; 0.80</code></td><td><span class="pass-pill">HIGH_CONFIDENCE</span></td></tr>
            <tr><td><code>oase pocket</code> (`WO-004`)</td><td>Best pocket <code>0.788</code> (48 pockets on `Q8NBP7`)</td><td>`Pocket #1` groove <code>0.68</code> vs `EGF-A` <code>0.24</code></td><td><code>&ge; 0.50</code></td><td><span class="pass-pill">DRUGGABLE_POCKET</span></td></tr>
            <tr><td><code>oase docking</code> (`WO-005`)</td><td><em>Seeded Vina 1.2.5 pose fixture</em></td><td><code>-9.4 kcal/mol</code> (`2.34 Å` to `Arg194/Asp238`)</td><td><code>&le; -8.5</code></td><td><span class="pass-pill">STRONG_BINDING</span></td></tr>
          </tbody>
        </table>
        <div class="relay-box">
          <strong>Mandatory Relays (`af3.low_confidence_segments` &amp; `docking.score_is_not_affinity`):</strong> Disordered residues `1–30` and `152–162` (`pLDDT &lt; 50`) are excluded from pocket definition; Vina `-9.4 kcal/mol` is a pose energy estimate, never a biochemical `IC50`.
        </div>
        <div class="portal-links">
          <a href="finding_findings_structural-biology_WO-004_md.html">View WO-004 Finding</a>
          <a href="finding_findings_computational-chemistry_WO-005_md.html">View WO-005 Finding</a>
          <a href="artifact_docking.html">View Docking Artifacts</a>
        </div>
      </div>
      <div class="terminal"><span class="cmd">$ oase alphafold fetch Q8NBP7 &amp;&amp; oase alphafold analyze Q8NBP7</span>
AF-Q8NBP7-F1 [threshold_set alphafold@1.0]
<span class="ok">pLDDT: global 85.19, confident fraction 0.82 -&gt; confident</span>
PAE: mean 10.936 A, 42% confident pairs -&gt; single-domain
Ordered domains (1): 58-542

<span class="cmd">$ oase pocket run raw/structures/AF-Q8NBP7-F1.cif &amp;&amp; oase pocket analyze ...</span>
AF-Q8NBP7-F1 [threshold_set pocket@1.0+program]
<span class="ok">druggable-pocket-present: Best pocket scores 0.788 (druggable) across 48 detected pocket(s).</span>
relay fpocket.druggability_is_not_affinity: 0.788 is cavity shape; not an affinity, not a potency.</div>
    </div>
  </section>

  <!-- CHAPTER 4 -->
  <section class="chapter-panel" id="panel-ch4">
    <div class="chapter-header">
      <h2>Act II (Chapter 4) — Stages 3–4 DMTA Lead Optimization: Catching the hERG Trap (`WO-006`..`WO-007`)</h2>
      <span class="stage-pill">Stages 3–4 · checkpoints/ch3</span>
    </div>
    <div class="grid-2">
      <div>
        <p><strong>The Critical Governance Moment:</strong> Live execution of <code>oase compound</code> and <code>oase admet</code> (`admet-endpoints@1.0`) flags <code>PCSK9-A02</code> (`cLogP = 5.09`, `MW = 378.4 Da`, `TPSA = 51.2 Å²`, `LogS = -5.613`) with <strong>3 critical liabilities (`metabolic_stability`, `herg_liability`, `solubility`)</strong>. Substituting the polar F,CN-oxadiazole in <code>PCSK9-A03</code> (`cLogP = 3.01`, `MW = 338.3 Da`, `TPSA = 101.0 Å²`, `LogS = -4.25`) clears all 3 rule-based liabilities (`0` liabilities) and corresponds to nominated lead <code>OASE-PCSK9-014</code> in the seeded translational PK fixture (`WO-007`, `F = 52%`, `t1/2 = 14.8 h`, `40 mg QD`).</p>
        <table>
          <thead><tr><th>Candidate</th><th>Live RDKit Descriptors (`oase compound`)</th><th>Live `oase admet` Verdict (`admet-endpoints@1.0`)</th><th>Seeded PK Fixture (`WO-007`)</th><th>Decision</th></tr></thead>
          <tbody>
            <tr><td><code>PCSK9-A02</code> (CF3-thiazole)</td><td><code>cLogP = 5.09</code>, <code>MW = 378.4</code>, <code>TPSA = 51.2 Å²</code></td><td><span class="fail-pill">3 LIABILITIES (hERG + MetStab + Sol)</span></td><td>Disqualified at ADMET gate</td><td><span class="fail-pill">REJECTED</span></td></tr>
            <tr><td><code>PCSK9-A03</code> / <code>OASE-PCSK9-014</code></td><td><code>cLogP = 3.01</code>, <code>MW = 338.3</code>, <code>TPSA = 101.0 Å²</code></td><td><span class="pass-pill">0 CRITICAL LIABILITIES (LogP &le; 3.7)</span></td><td><code>F = 52%</code>, <code>t1/2 = 14.8 h</code>, <code>40 mg QD</code></td><td><span class="pass-pill">NOMINATED</span></td></tr>
          </tbody>
        </table>
        <div class="relay-box">
          <strong>Engineering Discovery (`_BASIC_NITROGEN_SMARTS` in `admet.py:227`):</strong> Inspecting <code>oase/commands/admet.py</code> revealed that <code>[NH2,NH1,NH0;!$(N=*);!$(N#*)]</code> omits <code>!$(NC=O)</code>, so neutral amide <code>-C(=O)NH-</code> groups match <code>has_basic_nitrogen = True</code>! <code>PCSK9-A03</code> clears the Aronov hERG rule because its <code>LogP = 3.01</code> drops below the <code>LogP &gt; 3.7</code> threshold—proving why auditable provenance is essential for spotting heuristic over-reach.
        </div>
        <div class="portal-links">
          <a href="finding_findings_medicinal-chemistry_WO-006_md.html">View WO-006 Finding</a>
          <a href="finding_findings_admet-dmpk_WO-007_md.html">View WO-007 Finding</a>
          <a href="artifact_admet.html">View ADMET Artifacts</a>
          <a href="artifact_pk.html">View PK Artifacts</a>
        </div>
      </div>
      <div class="terminal"><span class="cmd">$ oase admet analyze --name PCSK9-A02 "COc1ccc(-c2nc(C(=O)Nc3ccc(C(F)(F)F)cc3)cs2)cc1"</span>
<span class="err">liabilities-identified: PCSK9-A02 has 3 ADMET liability(ies):</span>
  - metabolic_stability (high liability, LogP = 5.09)
  - <span class="err">herg_liability (structural features flagged: basic N + LogP 5.09 &gt; 3.7 + 3 aromatic rings)</span>
  - solubility (insoluble, LogS = -5.613)

<span class="cmd">$ oase admet analyze --name PCSK9-A03 "COc1ccc(-c2nc(C(=O)Nc3ccc(F)c(C#N)c3)no2)cc1"</span>
<span class="ok">acceptable: PCSK9-A03 has 0 ADMET liability(ies) [admet-endpoints@1.0]</span>
  - herg_liability: <span class="ok">acceptable (LogP = 3.01 &le; 3.7 cutoff; 0 critical liabilities)</span>
  - permeability: <span class="ok">acceptable (TPSA = 101.05 A^2, MW = 338.29 Da, LogS = -4.25)</span></div>
    </div>
  </section>

  <!-- CHAPTER 5 -->
  <section class="chapter-panel" id="panel-ch5">
    <div class="chapter-header">
      <h2>Act II (Chapter 5) — Mechanical Governance Drills (`oase validate check` Adversarial Tests)</h2>
      <span class="stage-pill">Control Plane · checkpoints/ch4</span>
    </div>
    <div class="grid-2">
      <div>
        <p>Before compiling the final Pre-Clinical Candidate Dossier (`WO-008`), we verify all 9 live Phase-1/Phase-2 runs in <code>live-runs/</code> plus all 8 campaign work orders (`WO-001`..`WO-008`), and run 4 negative adversarial tamper drills against <code>oase validate check</code>.</p>
        <table>
          <thead><tr><th>Adversarial Drill</th><th>Injected Fault</th><th>Validator Check</th><th>Exit Code</th><th>Outcome</th></tr></thead>
          <tbody>
            <tr><td><strong>Drill 1 (`PROV-002`)</strong></td><td>Append 1 byte to `raw/docking/pcsk9_pocket1_vina.sdf` (SHA-256 mismatch)</td><td><code>provenance_valid</code></td><td><code>exit=1</code></td><td><span class="pass-pill">CAUGHT &amp; BLOCKED</span></td></tr>
            <tr><td><strong>Drill 2 (`CIT-003`)</strong></td><td>Inflate docking score from `-9.4` to `-11.2 kcal/mol` in `WO-005.md` (`&gt; &plusmn;1%`)</td><td><code>source_tags_resolve</code></td><td><code>exit=1</code></td><td><span class="pass-pill">CAUGHT &amp; BLOCKED</span></td></tr>
            <tr><td><strong>Drill 3 (`REL-001`)</strong></td><td>Delete mandatory relay `af3.low_confidence_segments` from `WO-004.md`</td><td><code>relay_coverage</code></td><td><code>exit=1</code></td><td><span class="pass-pill">CAUGHT &amp; BLOCKED</span></td></tr>
            <tr><td><strong>Drill 4 (`THR-001`)</strong></td><td>Strip `threshold_set` attribution from `pcsk9_ic001_series_admet.analysis.json`</td><td><code>analysis_citations</code></td><td><code>exit=1</code></td><td><span class="pass-pill">CAUGHT &amp; BLOCKED</span></td></tr>
          </tbody>
        </table>
        <div class="portal-links">
          <a href="workorder_WO-005_r1.html">Inspect WO-005 Record</a>
          <a href="finding_findings_regulatory_WO-008_md.html">Inspect WO-008 Dossier</a>
        </div>
      </div>
      <div class="terminal"><span class="cmd">$ ./scripts/run-e2e-simulation.sh  # Chapter 5 Output</span>
======================================================================
CHAPTER 5C: 4 Adversarial Governance Drills (Negative Tests)
======================================================================
<span class="ok">[PASS - CAUGHT] Drill 1: SHA-256 Bit-Flip Tampering (PROV-002)</span>
  -&gt; WO-005 failed on provenance_valid with exit=1
<span class="ok">[PASS - CAUGHT] Drill 2: Inflated Numeric Claim -11.2 vs -9.4 kcal/mol (CIT-003)</span>
  -&gt; WO-005 failed on source_tags_resolve with exit=1
<span class="ok">[PASS - CAUGHT] Drill 3: Omitted Mandatory Caveat Relay af3.low_confidence_segments (REL-001)</span>
  -&gt; WO-004 failed on relay_coverage with exit=1
<span class="ok">[PASS - CAUGHT] Drill 4: Missing Threshold Set Attribution (THR-001)</span>
  -&gt; WO-006 failed on analysis_citations with exit=1</div>
    </div>
  </section>

  <!-- CHAPTER 6 -->
  <section class="chapter-panel" id="panel-ch6">
    <div class="chapter-header">
      <h2>Act III (Chapter 6) — The Complete Picture, Stage-Gate Dossier &amp; Architecture Scorecard</h2>
      <span class="stage-pill">Enterprise Scale · 5 Field Discoveries</span>
    </div>
    <div class="grid-2">
      <div>
        <div class="plate-box" id="plate-complete">
          <img src="assets/oase_complete_picture.jpg" alt="GCP-OASE Complete Architecture Picture">
          <div class="plate-caption">Figure 5 — End-to-End GCP-OASE Architecture: Scion Hub, Multi-Model Groves, Cloud Batch/Vertex Compute, and Static Evidence Portal.</div>
        </div>
        <div class="portal-links">
          <a href="index.html">Open 30-Page Evidence Portal Index</a>
          <a href="finding_findings_regulatory_WO-008_md.html">Open WO-008 Candidate Nomination Dossier</a>
        </div>
      </div>
      <div>
        <p>Summary of the compiled 31-page Static Evidence Portal (`WO-008` Pre-Clinical Candidate Dossier) and the architectural outcomes measured across our live Google Cloud Argolis execution:</p>
        <table>
          <thead><tr><th>Architecture Pillar</th><th>Target Outcome</th><th>Measured Simulation Result</th><th>Field Discovery &amp; Takeaway</th><th>Verdict</th></tr></thead>
          <tbody>
            <tr id="score-row-1">
              <td><strong>1. Two-Phase Tool Latch</strong><br>(Fetch/Compute vs. Offline Analyze)</td>
              <td>100% of Phase-2 <code>analyze</code> commands run offline against immutable JSON + thresholds</td>
              <td><code>51 / 51</code> Phase-2 commands verified offline by <code>oase doctor</code>; <code>9</code> live + <code>11</code> checkpoint <code>.analysis.json</code> records verified</td>
              <td><strong>Discovery 1:</strong> 13 of 36 default threshold schemas ship with <code>UNRESOLVED</code> sentinels that halt execution unless populated in <code>.oase/thresholds.yaml</code>.</td>
              <td><span class="pass-pill">LANDED (36/36 RESOLVED)</span></td>
            </tr>
            <tr id="score-row-2">
              <td><strong>2. Zero-Fabrication Citations</strong><br>(<code>{source: path $.jsonpath}</code>)</td>
              <td>Every numeric claim in Markdown is mechanically checked within &plusmn;1% of raw JSON</td>
              <td><code>28 / 28</code> scalar JSONPath citations verified within &plusmn;1%; Drill 2 caught <code>-11.2</code> vs <code>-9.4</code> in &lt;0.2s</td>
              <td><strong>Discovery 2:</strong> Putting one <code>{source: ... $.metrics.x}</code> tag per Markdown line prevents KaTeX <code>$ ... $</code> math collisions in <code>oase site build</code>.</td>
              <td><span class="pass-pill">LANDED (ZERO DRIFT)</span></td>
            </tr>
            <tr id="score-row-3">
              <td><strong>3. Mandatory Caveat Relays</strong><br>(<code>**Relay: `code`**</code>)</td>
              <td>Agents cannot drop negative caveats (e.g. disorder, hERG pharmacophore limits)</td>
              <td>All 8 work orders enforce mandatory relays; Drill 3 caught dropped <code>af3.low_confidence_segments</code></td>
              <td><strong>Discovery 4:</strong> Provenance exposed that <code>_BASIC_NITROGEN_SMARTS</code> in <code>admet.py:227</code> matches neutral amides—making heuristics transparent and auditable.</td>
              <td><span class="pass-pill">STRONGEST DIFFERENTIATOR</span></td>
            </tr>
            <tr id="score-row-4">
              <td><strong>4. Scion + OASE Reproducibility</strong><br>(<code>ENV_VERSION</code> + 22 Templates)</td>
              <td>Single-command install of Python + 7 C/C++/Go binaries stamped with SHA-256</td>
              <td>All 7 binaries (<code>vina</code>, <code>fpocket</code>, <code>rate4site</code>, <code>muscle</code>, <code>hypex</code>, <code>elo</code>, <code>prox</code>) stamped</td>
              <td><strong>Discovery 3 &amp; 5:</strong> Codified 4 Linux GCC 14 / offline KaTeX fixes in <code>bootstrap-oase-env.sh</code>; mechanical latches ensure epistemic honesty up to wet-lab validation.</td>
              <td><span class="pass-pill">REPEATABLE E2E</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</div>

<script>
function showChapter(ch) {
  document.querySelectorAll('.chapter-panel').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.chapter-btn').forEach(el => el.classList.remove('active'));
  const p = document.getElementById('panel-' + ch);
  const b = document.getElementById('btn-' + ch);
  if (p) p.classList.add('active');
  if (b) b.classList.add('active');
}
const hash = window.location.hash.replace('#', '');
if (hash && document.getElementById('panel-' + hash)) {
  showChapter(hash);
}
</script>
</body>
</html>
"""


def main() -> int:
    site_dir = pathlib.Path(
        sys.argv[1]
        if len(sys.argv) > 1
        else "/tmp/sim-pcsk9-oral/_site"
    )
    if not site_dir.is_dir():
        print(f"[error] _site directory not found: {site_dir}", file=sys.stderr)
        return 1

    # Copy article visual plates from repo assets/ into _site/assets/
    repo_assets = pathlib.Path(__file__).resolve().parent.parent / "assets"
    site_assets = site_dir / "assets"
    site_assets.mkdir(parents=True, exist_ok=True)
    copied_imgs = 0
    if repo_assets.is_dir():
        for jpg in sorted(repo_assets.glob("*.jpg")):
            shutil.copy2(jpg, site_assets / jpg.name)
            copied_imgs += 1

    proj_badge = os.environ.get(
        "OASE_PROJECT_BADGE", "gcp-oase-workshop (Argolis)"
    )
    env_sha = "sha256:61020936449a"
    tools_home = os.environ.get("OASE_TOOLS_HOME", "")
    if tools_home:
        ev_file = pathlib.Path(tools_home) / "ENV_VERSION"
        if ev_file.is_file():
            env_sha = ev_file.read_text(encoding="utf-8").strip()[:19]

    chapters_path = site_dir / "chapters.html"
    chapters_path.write_text(
        CHAPTERS_HTML.replace("__PROJECT_BADGE__", proj_badge).replace(
            "__ENV_SHA__", env_sha
        ),
        encoding="utf-8",
    )

    nav_target = '<a href="index.html">Home</a>'
    nav_replacement = (
        '<a href="index.html">Home</a>\n'
        '  <a href="chapters.html" style="color:#38bdf8;font-weight:600;">'
        "Architecture, Value Prop &amp; Campaign Replay</a>"
    )
    patched = 0
    for html_file in sorted(site_dir.glob("*.html")):
        if html_file.name == "chapters.html":
            continue
        txt = html_file.read_text(encoding="utf-8")
        if "chapters.html" not in txt and nav_target in txt:
            txt = txt.replace(nav_target, nav_replacement, 1)
            html_file.write_text(txt, encoding="utf-8")
            patched += 1

    print(
        f"[ok] Wrote {chapters_path} (copied {copied_imgs} visual plates to {site_assets}) and linked from {patched} portal pages."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

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
  .stack-full { display: flex; flex-direction: column; gap: 1.35rem; }
  .plate-box { background: #ffffff; border: 2px solid #cbd5e1; border-radius: 10px; padding: 0.85rem; text-align: center; margin: 0.5rem 0; box-shadow: 0 2px 8px rgba(15,23,42,0.06); position: relative; }
  .plate-box img { width: 100%; max-width: 1240px; height: auto; border-radius: 6px; display: block; margin: 0 auto; cursor: zoom-in; transition: transform 0.15s ease; }
  .plate-box img:hover { opacity: 0.98; }
  .plate-caption { color: #334155; font-size: 0.86rem; font-weight: 600; margin-top: 0.6rem; font-family: system-ui, -apple-system, sans-serif; display: flex; justify-content: space-between; align-items: center; padding: 0 0.25rem; }
  .zoom-hint { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; border-radius: 999px; padding: 0.18rem 0.65rem; font-size: 0.76rem; font-weight: 600; cursor: pointer; }
  .lightbox-backdrop { display: none; position: fixed; inset: 0; background: rgba(15, 23, 42, 0.92); z-index: 9999; align-items: center; justify-content: center; flex-direction: column; padding: 1.5rem; cursor: zoom-out; }
  .lightbox-backdrop.open { display: flex; }
  .lightbox-backdrop img { max-width: 96vw; max-height: 86vh; width: auto; height: auto; border-radius: 8px; background: #ffffff; padding: 0.5rem; box-shadow: 0 12px 40px rgba(0,0,0,0.5); }
  .lightbox-caption { color: #f8fafc; margin-top: 0.75rem; font-size: 0.95rem; font-weight: 600; text-align: center; }
  .subpage-bar { background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 6px; padding: 0.65rem 1rem; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; }
  .subpage-back-btn { background: #2563eb; color: #ffffff; border: none; padding: 0.45rem 0.9rem; border-radius: 5px; font-weight: 600; cursor: pointer; font-size: 0.85rem; }
  .subpage-back-btn:hover { background: #1d4ed8; }
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
  <h1>Introducing GCP-OASE: Team-Based Agentic Drug Discovery on Google Cloud</h1>
  <p><strong>OASE (Open Agentic Science Engine)</strong> is a drug discovery solution on Google Cloud that traces AI model predictions, wet-lab measurements, computed results, and stage-gate decisions across five layers of artifacts. Built on top of the open-source, multi-agent, multi-user <strong>SCION</strong> agent platform, GCP-OASE pairs a 5-scientist human discovery pod with a mirrored multi-model AI agent team (Gemini, Claude, OpenAI).</p>
  <div class="kpi-strip">
    <div class="kpi-card"><div class="kpi-val">5 Human + 11 AI</div><div class="kpi-lbl">Pod &amp; Agent Roles in Grove</div></div>
    <div class="kpi-card"><div class="kpi-val">5 Artifact Layers</div><div class="kpi-lbl">Separation of Powers</div></div>
    <div class="kpi-card"><div class="kpi-val">36 / 36</div><div class="kpi-lbl">Threshold Sets Resolved</div></div>
    <div class="kpi-card"><div class="kpi-val">8 / 8 [PASS]</div><div class="kpi-lbl">Work Orders Accepted</div></div>
    <div class="kpi-card"><div class="kpi-val">3 Blocked + 1 Logged</div><div class="kpi-lbl">Tamper &amp; Override Checks</div></div>
    <div class="kpi-card"><div class="kpi-val">OASE-PCSK9-014</div><div class="kpi-lbl">Nominated Lead (40 mg QD)</div></div>
  </div>
</div>

<div class="chapter-bar">
  <button class="chapter-btn act1 active" id="btn-why" onclick="showChapter('why')">1. Challenges &amp; Demo Overview</button>
  <button class="chapter-btn act1" id="btn-scion" onclick="showChapter('scion')">2. Data &amp; Control Architecture (4 Pillars)</button>
  <button class="chapter-btn" id="btn-ch1" onclick="showChapter('ch1')">3. Step 1: Rank Hypotheses (WO-001)</button>
  <button class="chapter-btn" id="btn-ch2" onclick="showChapter('ch2')">4. Step 2: Genetics &amp; Gate 1 (WO-002..003)</button>
  <button class="chapter-btn" id="btn-ch3" onclick="showChapter('ch3')">5. Step 3: AF3, Pockets &amp; Gate 2 (WO-004..005)</button>
  <button class="chapter-btn" id="btn-ch4" onclick="showChapter('ch4')">6. Step 4 &amp; Lab Gate: ADMET &amp; Gate 3 (WO-006)</button>
  <button class="chapter-btn" id="btn-ch5" onclick="showChapter('ch5')">7. Step 5: Human PK, Dossier &amp; Gate 4 (WO-007..008)</button>
  <button class="chapter-btn" id="btn-ch6" onclick="showChapter('ch6')">8. Step 6: Validation &amp; Override Review</button>
</div>

<div class="container">
  <!-- PANEL WHY: THE PROBLEM, 4 CHALLENGES & WHAT YOU'LL SEE IN THIS DEMO -->
  <section class="chapter-panel active" id="panel-why">
    <div class="chapter-header">
      <h2>Act I (Part 1) — Why Agentic Drug Discovery Is Harder Than It Looks &amp; What You'll See in This Demo</h2>
      <span class="stage-pill">4 Challenges · 5 Artifact Layers · 6 Steps + Wet-Lab Gate</span>
    </div>
    <div class="stack-full">
      <div class="plate-box" id="plate-thumb">
        <img src="assets/oase_post_thumbnail.jpg" alt="Introducing GCP-OASE: Team-Based Agentic Drug Discovery on Google Cloud" onclick="openLightbox(this.src, this.alt)">
        <div class="plate-caption">
          <span>Figure 1 — Introducing GCP-OASE: Team-Based Agentic Drug Discovery on Google Cloud (5-Role Human Pod + Mirrored Multi-Model Agent Team + 5 Artifact Layers).</span>
          <span class="zoom-hint" onclick="openLightbox(this.parentElement.previousElementSibling.src, this.parentElement.previousElementSibling.alt)">&#128269; Click to enlarge</span>
        </div>
      </div>

      <div>
        <p>Building production-ready agentic science that a <strong>pharma portfolio review committee can sign off on</strong> requires addressing four core challenges:</p>
        <div class="plate-box" id="plate-challenges">
          <img src="assets/oase_challenges.jpg" alt="Agentic Drug Discovery Challenges" onclick="openLightbox(this.src, this.alt)">
          <div class="plate-caption">
            <span>Figure 2 — The 4 challenges in production pharmaceutical R&amp;D: Rigid Workflows, Chatbot Fabrication, Single-Model Echo Chambers, and Lack of Organizational Governance.</span>
            <span class="zoom-hint" onclick="openLightbox(this.parentElement.previousElementSibling.src, this.parentElement.previousElementSibling.alt)">&#128269; Click to enlarge</span>
          </div>
        </div>
        <table>
          <thead><tr><th>Discovery Challenge</th><th>What Breaks in Standard Pipelines / Chatbots</th><th>How GCP-OASE Solves It</th></tr></thead>
          <tbody>
            <tr id="why-row-1">
              <td><strong>1. The Rigid Workflow Problem</strong></td>
              <td>Static pipelines (Nextflow, Snakemake) drop a target when bulk RNA-seq returns near-zero expression and cannot pause for multi-week wet-lab assays.</td>
              <td><strong>Dynamic routing &amp; lab handoff gates:</strong> Pivots to single-cell data when bulk tissue is low, and pauses on disk across multi-week wet-lab CRO assays.</td>
            </tr>
            <tr id="why-row-2">
              <td><strong>2. The Chatbot Fabrication Trap</strong></td>
              <td>Summarizes large tables in prompt context, invents plausible binding numbers, pads citations, or confuses <code>NA</code> with <code>0</code>.</td>
              <td><strong>Two-phase tool execution &amp; verified citations:</strong> Raw tool outputs + SHA-256 receipts are scored offline; every number in prose is checked within <strong>&plusmn;1%</strong> (<code>CIT-003</code>).</td>
            </tr>
            <tr id="why-row-3">
              <td><strong>3. The Single-Model Echo Chamber</strong></td>
              <td>Uses a single model family to generate hypotheses, interpret literature, and review its own work, reinforcing correlated bias.</td>
              <td><strong>Multi-model agent teams:</strong> Runs Gemini, Claude, and OpenAI side-by-side inside a shared Grove for blind hypothesis tournaments and cross-model review.</td>
            </tr>
            <tr id="why-row-4">
              <td><strong>4. Lack of Organizational Governance in Foundation Models</strong></td>
              <td>General-purpose LLMs lack a pharma organization's stage-gate criteria, risk tolerance, and decision-making rigor.</td>
              <td><strong>Clear separation of powers across 5 artifact layers:</strong> Raw data files, specialist findings, scientific decision logs, organization stage gates, and executive views.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div>
        <h3 style="margin: 0.5rem 0 0.4rem 0; color: #0f172a;">What You'll See in This Demo: Oral PCSK9 Campaign (<code>pcsk9-oral</code>)</h3>
        <p style="font-size: 0.92rem; color: #334155; margin: 0 0 0.75rem 0;">A <strong>human discovery pod of 5</strong> (Program Lead, Computational Biologist, Structural Biologist, Medicinal Chemist, DMPK &amp; Safety Lead) collaborates with a <strong>mirrored 11-agent AI team</strong> (AI Program Lead, 8 Domain Specialists, Independent Reviewer, and Validator) across 6 steps, 4 go/no-go stage gates, and 1 physical lab handoff:</p>
        <div class="plate-box" id="plate-stage-gate">
          <img src="assets/oase_stage_gate_process.png" alt="GCP-OASE Stage-Gate Process" onclick="openLightbox(this.src, this.alt)">
          <div class="plate-caption">
            <span>Figure 3 — Stage-Gate Process: Six demo steps, four logged go/no-go gates, and one lab handoff.</span>
            <span class="zoom-hint" onclick="openLightbox(this.parentElement.previousElementSibling.src, this.parentElement.previousElementSibling.alt)">&#128269; Click to enlarge</span>
          </div>
        </div>
        <table>
          <thead><tr><th>Step</th><th>Stage, Gate &amp; Work Orders</th><th>What Happens &amp; Key Outcome</th></tr></thead>
          <tbody>
            <tr><td><strong>Step 1</strong></td><td>Stage 0 (<code>WO-001</code>)</td><td>Ingest &amp; rank upstream AI Co-Scientist Elo tournament: allosteric small-molecule <code>IC-001</code> (<code>1642.5 Elo</code>) leads cyclic peptide <code>IC-002</code> (<code>1588.0 Elo</code>); logs caveat <code>hypothesis.adopted_not_generated</code>.</td></tr>
            <tr><td><strong>Step 2</strong></td><td>Stage 1 &rarr; <strong>Gate 1</strong> (<code>WO-002..003</code>)</td><td>Validate PCSK9 in human genetics &amp; liver omics (<code>gnomAD pLI = 0.0001</code>, <code>OpenTargets 0.96</code>, <code>GTEx 184.2 TPM</code>, <code>AlphaGenome 0.984</code>). <strong>AI + Human Program Leads co-sign Gate 1 (Target Validation).</strong></td></tr>
            <tr><td><strong>Step 3</strong></td><td>Stage 2 &rarr; <strong>Gate 2</strong> (<code>WO-004..005</code>)</td><td>AlphaFold 3 co-fold (<code>ipTM = 0.84</code>, <code>pTM = 0.88</code>), <code>fpocket</code> (<code>0.68</code> groove vs <code>0.24</code> flat surface), and AutoDock Vina (<code>-9.4 kcal/mol</code>). <strong>AI Program Lead signs Gate 2 (Hit Identification) &amp; logs liability <code>L-002</code>.</strong></td></tr>
            <tr><td><strong>Step 4</strong></td><td>Stage 3 &rarr; <strong>Gate 3</strong> (<code>WO-006</code>)</td><td>Multiparameter chemistry &amp; ADMET filter flags high-lipophilicity cardiac (hERG) alert; optimizes polar heterocycle <code>OASE-PCSK9-014</code> (<code>cLogP = 3.1</code>, <code>LipE = 5.2</code>, <code>0</code> alerts, <code>4</code>-step synthesis). <strong>AI Program Lead signs Gate 3 (Lead Optimization).</strong></td></tr>
            <tr><td><strong>&#9208; Lab Gate</strong></td><td>Lab Handoff (Seeded in Demo)</td><td><strong>Human Program Lead signs Lab Handoff</strong> for synthesis &amp; animal PK studies; agents pause cleanly on disk until measured rat (<code>54%</code>) and dog (<code>61%</code>) oral bioavailability files return.</td></tr>
            <tr><td><strong>Step 5</strong></td><td>Stage 4 &rarr; <strong>Gate 4</strong> (<code>WO-007..008</code>)</td><td>Project human once-daily dose (<code>40 mg QD</code>, <code>F = 52%</code>, <code>t1/2 = 14.8 h</code>) and compile candidate dossier + HTML Evidence Portal. <strong>AI + Human Program Leads co-sign Gate 4 (Candidate Nomination).</strong></td></tr>
            <tr><td><strong>Step 6</strong></td><td>Governance &amp; Override Checks</td><td>Run test cases against the 10-check validator: <strong>blocks</strong> missing caveats (<code>REL-001</code>), out-of-tolerance numbers (<code>CIT-003</code>), and altered raw hashes (<code>PROV-002</code>), while <strong>permitting &amp; logging</strong> an audited reviewer override.</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>

  <!-- PANEL SCION: DATA AND CONTROL ARCHITECTURE (4 PILLARS) -->
  <section class="chapter-panel" id="panel-scion">
    <div class="chapter-header">
      <h2>Act I (Part 2) — GCP-OASE Data and Control Architecture</h2>
      <span class="stage-pill">1. The Grove · 2. Work Orders &amp; Dual Validation · 3. Stage-Gate Review · 4. Two-Phase Tool Execution</span>
    </div>
    <div class="stack-full">
      <div class="plate-box" id="plate-benefits">
        <img src="assets/oase_benefits.jpg" alt="GCP-OASE Value Proposition" onclick="openLightbox(this.src, this.alt)">
        <div class="plate-caption">
          <span>Figure 4 — Four core solutions: Dynamic Routing &amp; Lab Gates, Two-Phase Tool Execution, Multi-Model Agent Teams, and 5-Layer Separation of Powers.</span>
          <span class="zoom-hint" onclick="openLightbox(this.parentElement.previousElementSibling.src, this.parentElement.previousElementSibling.alt)">&#128269; Click to enlarge</span>
        </div>
      </div>

      <div class="plate-box" id="plate-arch">
        <img src="assets/oase_data_arch.jpg" alt="GCP-OASE Data and Control Architecture" onclick="openLightbox(this.src, this.alt)">
        <div class="plate-caption">
          <span>Figure 5 — The 4 Architectural Mechanisms: The Grove, Work Orders &amp; Dual Validation, Stage-Gate Review, and Two-Phase Tool Execution across 5 Artifact Layers.</span>
          <span class="zoom-hint" onclick="openLightbox(this.parentElement.previousElementSibling.src, this.parentElement.previousElementSibling.alt)">&#128269; Click to enlarge</span>
        </div>
      </div>

      <div>
        <div class="pillar-grid">
          <div class="pillar-card" id="scion-card-1">
            <h4>1. The Grove ("Who is doing the work?")</h4>
            <p>Shared project workspace on SCION where the 5-scientist human pod and mirrored AI agent team (Gemini, Claude, OpenAI) collaborate. Specialists write findings to their own folders; only the <strong>AI Program Lead</strong> writes official decisions.</p>
          </div>
          <div class="pillar-card" id="scion-card-2">
            <h4>2. Work Orders &amp; Dual Validation ("How is work checked?")</h4>
            <p>Every assignment is a numbered Work Order (<code>WO-001</code>..<code>WO-008</code>). Before promotion, every finding must pass <strong>10 automated mechanical checks</strong> (<code>oase validate check</code>) plus an independent <strong>scientific review</strong>.</p>
          </div>
          <div class="pillar-card" id="scion-card-3">
            <h4>3. Stage-Gate Review ("Who decides to move forward?")</h4>
            <p>Work orders roll up into five logged gates: <strong>1. Target validation</strong> (AI + human sign), <strong>2. Hit ID</strong> (AI signs, logs liabilities), <strong>3. Lead opt</strong> (AI signs once resolved), <strong>4. Lab handoff</strong> (human signs; pauses on disk), and <strong>5. Candidate nomination</strong> (AI + human sign).</p>
          </div>
          <div class="pillar-card" id="scion-card-4">
            <h4>4. Two-Phase Tool Execution ("Why trust the numbers?")</h4>
            <p><strong>Phase 1 (Run/Fetch)</strong> writes raw tool outputs + SHA-256 receipts (<code>.meta.json</code>). <strong>Phase 2 (Analyze)</strong> scores outputs offline against 36 fixed threshold sets (<code>.analysis.json</code>) and emits mandatory <code>**Relay:**</code> caveats.</p>
          </div>
        </div>
        <h4 style="margin: 0.9rem 0 0.4rem 0; color: #0f172a;">Worked Example of Two-Phase Execution (Step 3 Pocket Analysis)</h4>
        <table>
          <thead><tr><th>Phase</th><th>Command</th><th>File Written</th><th>What Happens</th></tr></thead>
          <tbody>
            <tr><td><strong>Phase 1 — Run</strong></td><td><code>oase pocket run raw/structures/AF-Q8NBP7-F1.cif</code></td><td><code>raw/pockets/AF-Q8NBP7-F1.pockets.json</code> + <code>.meta.json</code></td><td>Runs compiled <code>fpocket 4.2.2</code> on PCSK9 and writes raw cavity scores plus a SHA-256 receipt.</td></tr>
            <tr><td><strong>Phase 2 — Analyze</strong></td><td><code>oase pocket analyze raw/pockets/AF-Q8NBP7-F1.pockets.json</code></td><td><code>raw/pockets/AF-Q8NBP7-F1.analysis.json</code></td><td>Applies fixed threshold set <code>pocket@1.0+program</code> (<code>&ge; 0.50</code> cutoff): catalytic groove <code>0.68</code> passes; flat EGF-A <code>0.24</code> fails; attaches mandatory caveat <code>fpocket.druggability_is_not_affinity</code>.</td></tr>
            <tr><td><strong>Specialist Report</strong></td><td>Structural Biologist writes <code>WO-004.md</code></td><td><code>findings/structural-biology/WO-004.md</code></td><td>Cites <code>0.68 {source: raw/pockets/... $.best_druggability_score}</code> and carries the caveat relay verbatim; verified by <code>oase validate check</code>.</td></tr>
          </tbody>
        </table>
        <h4 style="margin: 0.9rem 0 0.4rem 0; color: #0f172a;">Separation of Powers Across 5 Layers of Artifacts</h4>
        <table>
          <thead><tr><th>Artifact Layer</th><th>Directory / Surface</th><th>Writer &amp; Governance Rule</th></tr></thead>
          <tbody>
            <tr id="arch-row-1"><td><strong>1. Raw Data &amp; Receipts</strong></td><td><code>raw/&lt;class&gt;/</code> (<code>.json</code>, <code>.meta.json</code>, <code>.analysis.json</code>)</td><td>Written only by deterministic Phase-1 &amp; Phase-2 CLI tools; SHA-256 hash-locked (<code>PROV-001/002</code>, <code>THR-001</code>).</td></tr>
            <tr id="arch-row-2"><td><strong>2. Specialist Findings</strong></td><td><code>findings/&lt;domain&gt;/WO-XXX.md</code></td><td>Written by domain specialists; every number requires a JSONPath citation within &plusmn;1% (<code>CIT-003</code>) and all caveat relays (<code>REL-001</code>).</td></tr>
            <tr id="arch-row-3"><td><strong>3. Scientific Decision Logs</strong></td><td><code>program-state/decision-log.md</code> &amp; <code>liability-tracker.md</code></td><td>Written exclusively by the AI Program Lead after Dual Validation passes.</td></tr>
            <tr><td><strong>4. Organization Stage Gates</strong></td><td><code>program-state/PROGRAM_SUMMARY.md</code> &amp; Gate Co-Signs</td><td>Human Program Lead co-signs Gate 1 and Gate 4 go/no-go checkpoints and wet-lab assay handoffs.</td></tr>
            <tr><td><strong>5. Executive Views</strong></td><td><code>_site/index.html</code> &amp; <code>_site/chapters.html</code> (31 pages)</td><td>Compiled by <code>oase site build</code> into a self-contained static HTML Evidence Portal for portfolio review.</td></tr>
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

  <!-- CHAPTER 4: STEP 4 & LAB GATE -->
  <section class="chapter-panel" id="panel-ch4">
    <div class="chapter-header">
      <h2>Step 4 &amp; &#9208; Lab Gate — Multiparameter Chemistry, ADMET Filtering &amp; Wet-Lab Handoff (`WO-006`)</h2>
      <span class="stage-pill">Stage 3 &rarr; Gate 3 &rarr; Lab Gate · checkpoints/ch3..ch4</span>
    </div>
    <div class="grid-2">
      <div>
        <p><strong>Step 4 (Multiparameter Lead Optimization):</strong> Using the Step 3 structures, the Medicinal Chemist runs <code>RDKit</code> descriptors, <code>BRICS</code> matched molecular pairs, <code>ASKCOS</code> retrosynthesis, and rule-based <code>ADMET</code> structural alerts (`WO-006`). High-lipophilicity dockers trigger cardiac-safety (Aronov hERG) and metabolic liabilities, whereas polar heterocycle analogs resolve all alerts and advance at <strong>Gate 3 (Lead Optimization)</strong>:</p>
        <table>
          <thead><tr><th>Series / Run</th><th>Unoptimized High-Scoring Docker</th><th>Optimized Polar Lead (`OASE-PCSK9-014` / `PCSK9-A03`)</th><th>Gate 3 Verdict</th></tr></thead>
          <tbody>
            <tr><td><strong>Seeded Campaign (`WO-006`)</strong></td><td><code>pcsk9_analog_02</code>: <code>cLogP = 4.8</code> (&gt; <code>3.5</code> cutoff), basic-amine hERG liability <code>L-002</code></td><td><strong><code>OASE-PCSK9-014</code></strong>: <code>cLogP = 3.1</code>, <code>LipE = 5.2</code>, <code>MW = 462.5 Da</code>, <code>TPSA = 88.4 Å²</code>, <code>0</code> alerts, <code>4</code>-step synthesis (<code>0.87</code>)</td><td><span class="pass-pill">L-002 MITIGATED</span></td></tr>
            <tr><td><strong>Live CLI Pair (`live-runs/`)</strong></td><td><code>PCSK9-A02</code>: <code>cLogP = 5.09</code>, <code>MW = 378.4 Da</code>, <strong>3 liabilities</strong> (hERG + MetStab + Sol)</td><td><strong><code>PCSK9-A03</code></strong>: <code>cLogP = 3.01</code>, <code>MW = 338.3 Da</code>, <code>TPSA = 101.0 Å²</code>, <strong>0 liabilities</strong></td><td><span class="pass-pill">0 ALERTS PASS</span></td></tr>
          </tbody>
        </table>
        <div class="relay-box">
          <strong>&#9208; Lab Gate (Stopping-Gate Handoff &amp; Assay Re-Ingestion):</strong> Steps 1–4 are entirely <em>in silico</em>. Before Step 5 can project human dosing, the Human Program Lead signs the Lab Handoff work order for synthesis and <em>in vivo</em> animal PK studies. Agents pause cleanly on disk until measured rat (<code>54%</code>) and dog (<code>61%</code>) oral bioavailability files return (pre-staged in the workshop).
        </div>
        <div class="portal-links">
          <a href="finding_findings_medicinal-chemistry_WO-006_md.html">View WO-006 Finding</a>
          <a href="artifact_admet.html">View ADMET Artifacts</a>
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

  <!-- CHAPTER 5: STEP 5 HUMAN DOSE, DOSSIER & GATE 4 + COMPLETE PICTURE -->
  <section class="chapter-panel" id="panel-ch5">
    <div class="chapter-header">
      <h2>Step 5 — Human Oral Dose Projection, Candidate Dossier &amp; Gate 4 (`WO-007`..`WO-008`)</h2>
      <span class="stage-pill">Stage 4 &rarr; Gate 4 (AI + Human Co-Sign) · checkpoints/ch4</span>
    </div>
    <div class="stack-full">
      <div class="grid-2">
        <div>
          <p>Once measured rat (<code>54.0%</code>) and dog (<code>61.0%</code>) oral bioavailability files return from the Lab Gate, the DMPK and Regulatory specialists execute <code>WO-007</code> (two-species allometric PK scaling) and <code>WO-008</code> (ClinicalTrials.gov &amp; OpenFDA FAERS differentiation + candidate dossier compilation), culminating in <strong>Gate 4 (Candidate Nomination)</strong> co-signed by the AI Program Lead and Human Program Lead:</p>
          <table>
            <thead><tr><th>Work Order &amp; Metric</th><th>Verified Value (`WO-007` / `WO-008`)</th><th>Program Threshold</th><th>Verdict</th></tr></thead>
            <tbody>
              <tr><td><strong>Rat / Dog Oral Bioavailability (`WO-007`)</strong></td><td>Rat <code>F = 54.0%</code> · Dog <code>F = 61.0%</code> (NCA)</td><td><code>&ge; 30%</code> oral <code>F</code></td><td><span class="pass-pill">LAB DATA VERIFIED</span></td></tr>
              <tr><td><strong>Projected 70 kg Human Oral PK (`WO-007`)</strong></td><td><strong><code>40.0 mg QD</code></strong> (<code>F = 52.0%</code>, <code>t1/2 = 14.8 h</code>)</td><td>Once-daily <code>&le; 100 mg QD</code></td><td><span class="pass-pill">QD ORAL FEASIBLE</span></td></tr>
              <tr><td><strong>Clinical Landscape (`WO-008`)</strong></td><td><code>84</code> PCSK9 trials · <code>3</code> Phase 3/approved comparators · <strong><code>0</code> approved oral small molecules</strong></td><td>Differentiated oral profile</td><td><span class="pass-pill">WHITESPACE CONFIRMED</span></td></tr>
              <tr><td><strong>Gate 4 — Candidate Nomination (`DEC-011/012`)</strong></td><td><strong><code>OASE-PCSK9-014</code></strong> nominated; HTML Evidence Portal compiled</td><td>8/8 WOs + Dual Validation</td><td><span class="pass-pill">AI + HUMAN CO-SIGNED</span></td></tr>
            </tbody>
          </table>
          <div class="relay-box">
            <strong>Mandatory Relays (`pk.allometric_scaling_is_projection` &amp; `trials.active_competitor_pipeline`):</strong> Two-species human PK projections require Phase 1 clinical SAD/MAD verification, and active Phase 3 oral macrocycle (`MK-0616`) / injectable mAb comparators require explicit food-effect and CoGS differentiation.
          </div>
          <div class="portal-links">
            <a href="finding_findings_admet-dmpk_WO-007_md.html">View WO-007 PK Finding</a>
            <a href="finding_findings_regulatory_WO-008_md.html">View WO-008 Candidate Dossier</a>
            <a href="artifact_pk.html">View PK Layer 0 Artifacts</a>
            <a href="index.html">Open Full Evidence Portal Index</a>
          </div>
        </div>
        <div class="terminal"><span class="cmd">$ oase pk analyze raw/pk/oase_pcsk9_014_scaled_pk.json</span>
oase_pcsk9_014_scaled_pk [threshold_set pk-parameters@1.0+program]
<span class="ok">oral-qd-supported: Rat F=54.0%, Dog F=61.0% -&gt; Human F=52.0%, t1/2=14.8 h, Projected Dose=40.0 mg QD</span>
relay pk.allometric_scaling_is_projection: Two-species projections require clinical verification.

<span class="cmd">$ oase site validate &amp;&amp; oase site build &amp;&amp; oase site export</span>
<span class="ok">[PASS] Validated 8/8 work orders (WO-001..WO-008), 28/28 inline JSONPath citations, and SHA-256 receipts</span>
<span class="ok">[PASS] Built static HTML Evidence Portal (_site/index.html + _site/chapters.html)</span></div>
      </div>

      <div class="plate-box" id="plate-complete">
        <img src="assets/oase_complete_picture.jpg" alt="GCP-OASE Complete Architecture Picture" onclick="openLightbox(this.src, this.alt)">
        <div class="plate-caption">
          <span>Figure 6 — The Complete Picture: Six Steps, Four Logged Stage Gates, and One Lab Handoff from Hypothesis Tournament to Candidate Nomination.</span>
          <span class="zoom-hint" onclick="openLightbox(this.parentElement.previousElementSibling.src, this.parentElement.previousElementSibling.alt)">&#128269; Click to enlarge</span>
        </div>
      </div>
    </div>
  </section>

  <!-- CHAPTER 6: STEP 6 VALIDATION CHECKS & OVERRIDE REVIEW -->
  <section class="chapter-panel" id="panel-ch6">
    <div class="chapter-header">
      <h2>Step 6 — Validation Checks, Override Review &amp; Architecture Scorecard</h2>
      <span class="stage-pill">10-Check Validator · 3 Tamper Cases Blocked + 1 Override Logged</span>
    </div>
    <div class="stack-full">
      <div class="grid-2">
        <div>
          <p>In <strong>Step 6</strong>, the Program Lead tests how OASE verifies that specialist reports match underlying data and tracks human or lead overrides. The deterministic validator (<code>oase validate check</code>) <strong>blocks work-order closure on tampering/fabrication cases</strong> while <code>oase workorder override</code> <strong>permits and logs an explicit scientific override</strong> with actor and rationale in <code>program-state/decision-log.md</code>:</p>
          <table>
            <thead><tr><th>Governance Test Case</th><th>Tested Condition</th><th>Mechanism / Check</th><th>Result</th></tr></thead>
            <tbody>
              <tr><td><strong>Case 1 — Missing Required Caveat</strong></td><td>Remove mandatory relay <code>af3.low_confidence_segments</code> from <code>WO-004.md</code></td><td><code>relay_coverage</code> (<code>REL-001</code>)</td><td><span class="fail-pill">BLOCKED (exit=1)</span></td></tr>
              <tr><td><strong>Case 2 — Citation Drift &gt; &plusmn;1%</strong></td><td>Alter cited Vina score from <code>-9.4</code> to <code>-11.2 kcal/mol</code> in <code>WO-005.md</code></td><td><code>source_tags_resolve</code> (<code>CIT-003</code>)</td><td><span class="fail-pill">BLOCKED (exit=1)</span></td></tr>
              <tr><td><strong>Case 3 — Altered Raw Data File</strong></td><td>Modify <code>raw/docking/pcsk9_pocket1_vina.sdf</code> so SHA-256 mismatches <code>.meta.json</code> (plus stripped <code>THR-001</code> check)</td><td><code>provenance_valid</code> (<code>PROV-002</code>)</td><td><span class="fail-pill">BLOCKED (exit=1)</span></td></tr>
              <tr><td><strong>Case 4 — Audited Reviewer Override</strong></td><td>Valid Layer 0 data accepted, while reviewer overrides specialist's interpretation of a marginal <code>0.2 kcal/mol</code> difference</td><td><code>oase workorder override</code> &rarr; <code>decision-log.md</code></td><td><span class="pass-pill">PERMITTED &amp; LOGGED</span></td></tr>
            </tbody>
          </table>
          <div class="portal-links">
            <a href="workorder_WO-005_r1.html">Inspect WO-005 Validation Record</a>
            <a href="finding_findings_regulatory_WO-008_md.html">Inspect WO-008 Dossier</a>
          </div>
        </div>
        <div class="terminal"><span class="cmd">$ ./scripts/run-e2e-simulation.sh  # Validator Tamper &amp; Override Verification</span>
<span class="ok">[BLOCKED AS EXPECTED] Case 1: Omitted Mandatory Caveat Relay af3.low_confidence_segments (REL-001)</span>
  -&gt; WO-004 failed on relay_coverage with exit=1
<span class="ok">[BLOCKED AS EXPECTED] Case 2: Altered Cited Number -11.2 vs -9.4 kcal/mol &gt; &plusmn;1% (CIT-003)</span>
  -&gt; WO-005 failed on source_tags_resolve with exit=1
<span class="ok">[BLOCKED AS EXPECTED] Case 3: Modified Raw Data File SHA-256 Mismatch (PROV-002 &amp; THR-001)</span>
  -&gt; WO-005 failed on provenance_valid with exit=1

<span class="cmd">$ oase workorder override WO-006 --actor science-program-lead \</span>
<span class="cmd">    --reason "Accept valid Layer 0 docking/ADMET files; prioritize LipE 5.2 &amp; 0 alerts over 0.2 kcal/mol pose delta"</span>
<span class="ok">[PERMITTED &amp; LOGGED] Recorded direction_override with actor + rationale in program-state/decision-log.md</span></div>
      </div>

      <div>
        <h4 style="margin: 0.4rem 0 0.5rem 0; color: #0f172a;">Measured Architecture Scorecard &amp; Five Engineering Takeaways</h4>
        <table>
          <thead><tr><th>Architecture Pillar</th><th>Target Outcome</th><th>Measured Simulation Result</th><th>Field Discovery &amp; Takeaway</th><th>Verdict</th></tr></thead>
          <tbody>
            <tr id="score-row-1">
              <td><strong>1. Two-Phase Tool Latch</strong><br>(Fetch/Compute vs. Offline Analyze)</td>
              <td>100% of Phase-2 <code>analyze</code> commands run offline against immutable JSON + thresholds</td>
              <td><code>51 / 51</code> Phase-2 commands verified offline by <code>oase doctor</code>; <code>9</code> live + <code>11</code> checkpoint <code>.analysis.json</code> records verified</td>
              <td><strong>Takeaway 1:</strong> 13 of 36 default threshold schemas ship with <code>UNRESOLVED</code> sentinels so each organization sets its own cutoffs in <code>.oase/thresholds.yaml</code>.</td>
              <td><span class="pass-pill">LANDED (36/36 RESOLVED)</span></td>
            </tr>
            <tr id="score-row-2">
              <td><strong>2. Zero-Fabrication Citations</strong><br>(<code>{source: path $.jsonpath}</code>)</td>
              <td>Every numeric claim in Markdown is mechanically checked within &plusmn;1% of raw JSON</td>
              <td><code>28 / 28</code> scalar JSONPath citations verified within &plusmn;1%; validator caught <code>-11.2</code> vs <code>-9.4</code> in &lt;0.2s</td>
              <td><strong>Takeaway 2:</strong> Putting one <code>{source: ... $.metrics.x}</code> tag per Markdown line prevents KaTeX <code>$ ... $</code> math collisions in <code>oase site build</code>.</td>
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
        <div class="portal-links">
          <a href="index.html">Open 30-Page Evidence Portal Index</a>
          <a href="finding_findings_regulatory_WO-008_md.html">Open WO-008 Candidate Nomination Dossier</a>
        </div>
      </div>
    </div>
  </section>

  <!-- INLINE SUBPAGE VIEWER PANEL -->
  <section class="chapter-panel" id="panel-subpage">
    <div class="subpage-bar">
      <div><strong id="subpage-title">Evidence Portal Document</strong></div>
      <button class="subpage-back-btn" onclick="returnFromSubpage()">&larr; Back to Chapter Walkthrough</button>
    </div>
    <div id="subpage-content"></div>
  </section>
</div>

<!-- FULL-SCREEN IMAGE LIGHTBOX -->
<div class="lightbox-backdrop" id="lightbox" onclick="closeLightbox()">
  <img id="lightbox-img" src="" alt="">
  <div class="lightbox-caption" id="lightbox-caption"></div>
</div>

<script>
const SUBPAGES = __SUBPAGES_JSON__;
let lastChapter = 'why';

function showChapter(ch) {
  lastChapter = ch;
  document.querySelectorAll('.chapter-panel').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.chapter-btn').forEach(el => el.classList.remove('active'));
  const p = document.getElementById('panel-' + ch);
  const b = document.getElementById('btn-' + ch);
  if (p) p.classList.add('active');
  if (b) b.classList.add('active');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function openLightbox(src, caption) {
  const lb = document.getElementById('lightbox');
  document.getElementById('lightbox-img').src = src;
  document.getElementById('lightbox-caption').textContent = caption + ' (Click anywhere or press Esc to close)';
  lb.classList.add('open');
}

function closeLightbox() {
  document.getElementById('lightbox').classList.remove('open');
}

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeLightbox();
});

function openSubpage(filename) {
  if (filename === 'chapters.html') {
    showChapter(lastChapter || 'why');
    return false;
  }
  const html = SUBPAGES[filename];
  if (!html) return true;
  document.querySelectorAll('.chapter-panel').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.chapter-btn').forEach(el => el.classList.remove('active'));
  document.getElementById('subpage-title').textContent = filename;
  const container = document.getElementById('subpage-content');
  container.innerHTML = html;
  bindSubpageLinks(container);
  document.getElementById('panel-subpage').classList.add('active');
  window.scrollTo({ top: 0, behavior: 'smooth' });
  return false;
}

function returnFromSubpage() {
  showChapter(lastChapter || 'why');
}

function bindSubpageLinks(root) {
  root.querySelectorAll('a[href]').forEach(a => {
    const href = a.getAttribute('href') || '';
    const clean = href.split('#')[0].split('?')[0];
    if (clean === 'chapters.html' || SUBPAGES[clean]) {
      a.addEventListener('click', (e) => {
        e.preventDefault();
        openSubpage(clean);
      });
    }
  });
}

bindSubpageLinks(document);

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
        for img in sorted(list(repo_assets.glob("*.jpg")) + list(repo_assets.glob("*.png"))):
            shutil.copy2(img, site_assets / img.name)
            copied_imgs += 1

    proj_badge = os.environ.get(
        "OASE_PROJECT_BADGE", "gcp-oase-workshop (Google Cloud)"
    )
    env_sha = "sha256:61020936449a"
    tools_home = os.environ.get("OASE_TOOLS_HOME", "")
    if tools_home:
        ev_file = pathlib.Path(tools_home) / "ENV_VERSION"
        if ev_file.is_file():
            env_sha = ev_file.read_text(encoding="utf-8").strip()[:19]

    import base64
    import json
    import re

    subpages = {}
    for html_file in sorted(site_dir.glob("*.html")):
        if html_file.name == "chapters.html":
            continue
        raw_html = html_file.read_text(encoding="utf-8")
        m = re.search(r"<body[^>]*>(.*)</body>", raw_html, re.DOTALL | re.IGNORECASE)
        body_inner = m.group(1) if m else raw_html
        # Strip top <nav>...</nav> from subpage body since chapters.html already has top nav
        body_inner = re.sub(r"<nav[^>]*>.*?</nav>", "", body_inner, count=1, flags=re.DOTALL | re.IGNORECASE)
        subpages[html_file.name] = body_inner.strip()

    html_out = (
        CHAPTERS_HTML.replace("__PROJECT_BADGE__", proj_badge)
        .replace("__ENV_SHA__", env_sha)
        .replace("__SUBPAGES_JSON__", json.dumps(subpages))
    )
    # Inline assets/* as base64 data URIs so chapters.html renders all figures in sandboxed iframes, srcdoc viewers, and standalone HTML exports
    for img_path in sorted(site_assets.iterdir()):
        if img_path.suffix.lower() in (".jpg", ".jpeg", ".png"):
            mime = "image/png" if img_path.suffix.lower() == ".png" else "image/jpeg"
            b64 = base64.b64encode(img_path.read_bytes()).decode("ascii")
            html_out = html_out.replace(
                f'src="assets/{img_path.name}"',
                f'src="data:{mime};base64,{b64}"',
            )

    chapters_path = site_dir / "chapters.html"
    chapters_path.write_text(html_out, encoding="utf-8")

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

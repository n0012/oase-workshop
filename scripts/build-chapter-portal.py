#!/usr/bin/env python3
"""Augments `oase site build` output (`_site/`) with `chapters.html`, `plan.html`, and visual plates.

Provides an interactive 3-Act Walkthrough covering:
  - Act I: Why Chatbot Science Fails & How Scion + OASE Solves It (`#why`, `#scion`)
  - Act II: Live PCSK9 Campaign Simulation & Adversarial Governance Drills (`#ch1`..`#ch6`)
  - Act III: Executive Portfolio Closeout (`Grove-1`), 30-Page Portal & Architecture Scorecard (`#ch7`)
"""

from __future__ import annotations

import os
import pathlib
import shutil
import sys

CHAPTERS_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow" />
<meta name="googlebot" content="noindex, nofollow" />
<title>GCP-OASE &amp; Scion — Architecture, Value Proposition &amp; Campaign Walkthrough</title>
<style>
  body { font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 0; color: #1a1a1a; background: #f4f6f8; }
  nav { background: #1e293b; color: #f8fafc; padding: 0.75rem 2rem; display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap; border-bottom: 3px solid #2563eb; position: relative; z-index: 40; }
  nav .left { display: flex; align-items: center; gap: 1.15rem; flex-wrap: wrap; }
  nav .left a { color: #e2e8f0; text-decoration: none; font-size: 0.9rem; }
  nav .left a:hover, nav .left a.active-nav { color: #ffffff; font-weight: 600; text-decoration: underline; }
  nav .nav-title { font-weight: 700; font-size: 1.05rem; color: #ffffff; margin-right: 0.25rem; }
  .pilot-switcher-wrap { position: relative; display: inline-block; }
  .pilot-switcher-btn { background: #0f172a; color: #f8fafc; border: 1px solid #38bdf8; border-radius: 7px; padding: 0.36rem 0.75rem; font-size: 0.82rem; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 0.45rem; transition: all 0.15s; }
  .pilot-switcher-btn:hover { background: #1e293b; border-color: #7dd3fc; }
  .pilot-badge-pill { font-family: ui-monospace, monospace; font-size: 0.7rem; font-weight: 700; padding: 0.12rem 0.45rem; border-radius: 999px; }
  .pilot-badge-pill.ready { background: rgba(16, 185, 129, 0.2); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.45); }
  .pilot-badge-pill.staging { background: rgba(245, 158, 11, 0.2); color: #fcd34d; border: 1px solid rgba(245, 158, 11, 0.45); }
  .pilot-menu { display: none; position: absolute; top: calc(100% + 0.45rem); left: 0; min-width: 440px; max-width: 92vw; background: #0f172a; border: 1px solid #38bdf8; border-radius: 10px; box-shadow: 0 14px 36px rgba(2, 6, 23, 0.65); padding: 0.55rem; z-index: 999; }
  .pilot-menu.open { display: block; }
  .pilot-menu-hdr { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8; padding: 0.3rem 0.55rem 0.45rem; border-bottom: 1px solid #1e293b; font-weight: 700; }
  .pilot-menu-item { display: block; width: 100%; text-align: left; background: transparent; border: 1px solid transparent; color: #f8fafc; padding: 0.65rem 0.75rem; border-radius: 7px; cursor: pointer; margin-top: 0.3rem; transition: all 0.12s; }
  .pilot-menu-item:hover { background: #1e293b; border-color: #334155; }
  .pilot-menu-item.active { background: rgba(37, 99, 235, 0.22); border-color: #3b82f6; }
  .pilot-menu-ftr { font-size: 0.73rem; color: #94a3b8; padding: 0.45rem 0.55rem 0.25rem; border-top: 1px solid #1e293b; margin-top: 0.35rem; font-family: ui-monospace, monospace; }
  .badge-env { background: #0f172a; color: #38bdf8; border: 1px solid #0284c7; padding: 0.25rem 0.65rem; border-radius: 4px; font-family: monospace; font-size: 0.8rem; }
  .hero { background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); color: #ffffff; padding: 1.45rem 2.5rem; }
  .hero h1 { margin: 0 0 0.35rem 0; font-size: 1.58rem; color: #ffffff; }
  .hero p { margin: 0; color: #cbd5e1; font-size: 0.95rem; max-width: 960px; line-height: 1.45; }
  .hero-pilot-tag { display: inline-flex; align-items: center; gap: 0.5rem; margin-top: 0.65rem; background: rgba(15, 23, 42, 0.55); border: 1px solid rgba(56, 189, 248, 0.4); border-radius: 999px; padding: 0.24rem 0.75rem; font-size: 0.78rem; color: #e2e8f0; font-family: ui-monospace, monospace; }
  .kpi-strip { display: grid; grid-template-columns: repeat(6, 1fr); gap: 0.85rem; margin-top: 1rem; }
  .kpi-card { background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.16); border-radius: 6px; padding: 0.75rem 0.9rem; }
  .kpi-card .kpi-val { font-size: 1.25rem; font-weight: 700; color: #38bdf8; font-family: monospace; }
  .kpi-card .kpi-lbl { font-size: 0.74rem; color: #cbd5e1; margin-top: 0.2rem; text-transform: uppercase; letter-spacing: 0.04em; }

  .chapter-bar { background: #ffffff; border-bottom: 1px solid #cbd5e1; padding: 0.65rem 2rem; display: flex; gap: 0.5rem; flex-wrap: wrap; position: sticky; top: 0; z-index: 20; box-shadow: 0 2px 4px rgba(0,0,0,0.04); }
  .chapter-btn { background: #f1f5f9; border: 1px solid #cbd5e1; color: #334155; padding: 0.45rem 0.8rem; border-radius: 6px; font-weight: 600; font-size: 0.82rem; cursor: pointer; transition: all 0.15s; }
  .chapter-btn:hover { background: #e2e8f0; }
  .chapter-btn.active { background: #2563eb; color: #ffffff; border-color: #1d4ed8; }
  .chapter-btn.act1 { border-left: 3px solid #0284c7; }
  .chapter-btn.lab-btn { border-left: 3px solid #10b981; background: #ecfdf5; color: #065f46; border-color: #a7f3d0; }
  .chapter-btn.lab-btn:hover { background: #d1fae5; }
  .chapter-btn.lab-btn.active { background: #059669; color: #ffffff; border-color: #047857; border-left: 3px solid #34d399; }
  .chapter-btn.subway-btn { border-left: 3px solid #f59e0b; background: #fffbeb; color: #92400e; border-color: #fde68a; }
  .chapter-btn.subway-btn:hover { background: #fef3c7; }
  .chapter-btn.subway-btn.active { background: #d97706; color: #ffffff; border-color: #b45309; border-left: 3px solid #fbbf24; }
  .subway-board { background: #0f172a; border-radius: 10px; padding: 1.15rem 1.25rem; border: 1px solid #334155; color: #f8fafc; }
  .subway-legend { display: flex; gap: 1.1rem; flex-wrap: wrap; font-size: 0.79rem; color: #cbd5e1; margin-bottom: 0.65rem; }
  .subway-station-pills { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.85rem; }
  .stn-pill { background: #1e293b; color: #cbd5e1; border: 1px solid #475569; padding: 0.4rem 0.78rem; border-radius: 999px; font-size: 0.8rem; font-weight: 600; cursor: pointer; transition: all 0.15s; }
  .stn-pill:hover { border-color: #38bdf8; color: #ffffff; }
  .stn-pill.active { background: #2563eb; color: #ffffff; border-color: #60a5fa; }
  .stn-node { cursor: pointer; transition: transform 0.15s; }
  .stn-node:hover circle { stroke-width: 4.5px; }

  .whatif-banner { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #f8fafc; border-radius: 10px; padding: 1.25rem 1.4rem; border: 1px solid #334155; box-shadow: 0 4px 16px rgba(15, 23, 42, 0.12); }
  .whatif-banner h3 { margin: 0 0 0.35rem 0; font-size: 1.08rem; color: #38bdf8; }
  .whatif-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.9rem; margin-top: 0.85rem; }
  .whatif-card { background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(148, 163, 184, 0.25); border-top: 3px solid #38bdf8; border-radius: 8px; padding: 0.9rem 1rem; }
  .whatif-card .wi-num { font-family: monospace; font-size: 0.75rem; font-weight: 700; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.05em; }
  .whatif-card .wi-q { font-size: 0.95rem; font-weight: 700; color: #ffffff; line-height: 1.4; margin: 0.35rem 0 0.45rem 0; }
  .whatif-card .wi-a { font-size: 0.81rem; color: #cbd5e1; line-height: 1.42; margin: 0; }
  .whatif-pivot { margin-top: 0.95rem; padding-top: 0.85rem; border-top: 1px solid rgba(148, 163, 184, 0.22); display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap; font-size: 0.9rem; color: #e2e8f0; }
  .whatif-actions { display: flex; gap: 0.6rem; flex-wrap: wrap; }
  .whatif-cta { background: #059669; color: #ffffff; border: 1px solid #10b981; border-radius: 6px; padding: 0.45rem 0.9rem; font-weight: 700; font-size: 0.82rem; cursor: pointer; }
  .whatif-cta:hover { background: #047857; }
  .whatif-cta.secondary { background: #2563eb; border-color: #3b82f6; }
  .whatif-cta.secondary:hover { background: #1d4ed8; }
  .lab-block { background: #f8fafc; border: 1px solid #cbd5e1; border-left: 4px solid #059669; border-radius: 8px; padding: 1.05rem 1.25rem; margin-bottom: 1rem; }
  .lab-block-hdr { display: flex; justify-content: space-between; align-items: center; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 0.5rem; }
  .lab-block-hdr h4 { margin: 0; color: #0f172a; font-size: 1rem; }
  @media (max-width: 960px) { .whatif-grid { grid-template-columns: 1fr; } .grid-2 { grid-template-columns: 1fr; } .kpi-strip { grid-template-columns: repeat(2, 1fr); } }

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
    <span class="nav-title">GCP-OASE &amp; Scion</span>
    <div class="pilot-switcher-wrap" id="oase-campaign-switcher">
      <button type="button" class="pilot-switcher-btn" id="oase-campaign-btn" onclick="oaseToggleCampaignMenu(event)">
        <span>&#128450; Pilot:</span>
        <strong id="oase-campaign-btn-label">PCSK9 Oral · Reference Pilot (v1)</strong>
        <span class="pilot-badge-pill ready" id="oase-campaign-btn-badge">LIVE · 8 GROVES</span>
        <span style="opacity:0.75;">&#9662;</span>
      </button>
      <div class="pilot-menu" id="oase-campaign-menu"></div>
    </div>
    <a href="index.html">Portal Home (30 Pages)</a>
    <a href="chapters.html" class="active-nav">Story Arc &amp; Replay</a>
    <a href="finding_findings_regulatory_WO-008_md.html">WO-008 Dossier</a>
    <a href="plan.html" style="color:#4ade80;font-weight:700;">Build Tracker</a>
  </div>
  <span class="badge-env">Project: __PROJECT_BADGE__ | scion + oase 0.3.0 | ENV __ENV_SHA__</span>
</nav>

<div class="hero">
  <h1 id="hero-title">GCP-OASE: Team-Based Agentic Drug Discovery on Google Cloud</h1>
  <p id="hero-subtitle">Open-source, multi-user, multi-model drug discovery on Google Cloud—pairing a 5-scientist human pod with specialist AI wingmen and cryptographically verified stage gates.</p>
  <div class="hero-pilot-tag" id="hero-active-pilot-line">Active Scion Pilot: PCSK9 Oral · Reference Pilot (v1) — PCSK9 (Q8NBP7) · Oral Rule-of-5 Small Molecule</div>
  <div class="kpi-strip" id="hero-kpi-strip">
    <div class="kpi-card"><div class="kpi-val">5 Human + 11 AI</div><div class="kpi-lbl">Discovery Pod &amp; Agent Team</div></div>
    <div class="kpi-card"><div class="kpi-val">4 Core Pillars</div><div class="kpi-lbl">Grove · WOs · 2-Phase · Gates</div></div>
    <div class="kpi-card"><div class="kpi-val">5 Artifact Layers</div><div class="kpi-lbl">Separation of Powers</div></div>
    <div class="kpi-card"><div class="kpi-val">8 / 8 [PASS]</div><div class="kpi-lbl">Work Orders Accepted</div></div>
    <div class="kpi-card"><div class="kpi-val">3 Blocked + 1 Signed</div><div class="kpi-lbl">Tamper &amp; Override Audit</div></div>
    <div class="kpi-card"><div class="kpi-val">OASE-PCSK9-014</div><div class="kpi-lbl">Nominated Lead (40 mg QD)</div></div>
  </div>
</div>

<div class="chapter-bar">
  <button class="chapter-btn act1 active" id="btn-why" onclick="showChapter('why')">Overview &amp; Challenges</button>
  <button class="chapter-btn act1" id="btn-scion" onclick="showChapter('scion')">4 Core Pillars</button>
  <button class="chapter-btn lab-btn" id="btn-lab" onclick="showChapter('lab')">2.5-Hr Lab Guide</button>
  <button class="chapter-btn" id="btn-ch1" onclick="showChapter('ch1')">Step 1: Pre-Brief &amp; Co-Scientist (WO-001)</button>
  <button class="chapter-btn" id="btn-ch2" onclick="showChapter('ch2')">Step 2: Genetics &amp; Gate 1 (WO-002..003)</button>
  <button class="chapter-btn" id="btn-ch3" onclick="showChapter('ch3')">Step 3: AF3, Pockets &amp; Gate 2 (WO-004..005)</button>
  <button class="chapter-btn" id="btn-ch4" onclick="showChapter('ch4')">Step 4 &amp; Lab Gate: ADMET &amp; Gate 3 (WO-006)</button>
  <button class="chapter-btn" id="btn-ch5" onclick="showChapter('ch5')">Step 5: Human PK &amp; Gate 4 (WO-007..008)</button>
  <button class="chapter-btn" id="btn-ch6" onclick="showChapter('ch6')">Step 6: Tamper &amp; Override Audit</button>
  <button class="chapter-btn" id="btn-ch7" onclick="showChapter('ch7')">Step 7: Post-Debrief &amp; Route Recap</button>
</div>

<div class="container">
  <!-- PANEL WHY: THE PROBLEM, 4 CHALLENGES & WHAT YOU'LL SEE IN THIS DEMO -->
  <section class="chapter-panel active" id="panel-why">
    <div class="chapter-header">
      <h2>Three "What Ifs" Behind GCP-OASE</h2>
      <span class="stage-pill">Apache 2.0 ($0/Seat) · Sovereign Customer VPC · Subway-Map Routing</span>
    </div>
    <div class="stack-full">
      <div class="whatif-banner" id="whatif-hero">
        <h3>Three "What Ifs" for Biopharma R&amp;D</h3>
        <div class="whatif-grid">
          <div class="whatif-card">
            <div class="wi-num">1 · Multiplayer Science</div>
            <div class="wi-q">"What if your whole pod shared one AI workspace?"</div>
            <p class="wi-a">5 scientists + 11 AI wingmen in one live <strong>Scion Grove</strong>—not isolated chat tabs.</p>
          </div>
          <div class="whatif-card">
            <div class="wi-num">2 · Model Optionality</div>
            <div class="wi-q">"What if frontier models challenged each other?"</div>
            <p class="wi-a"><strong>Gemini</strong>, <strong>Claude</strong> &amp; <strong>OpenAI</strong> + 1P <strong>AlphaGenome</strong> &amp; <strong>AlphaFold 3</strong> inside your VPC.</p>
          </div>
          <div class="whatif-card">
            <div class="wi-num">3 · Verified Stage Gates</div>
            <div class="wi-q">"What if every AI claim carried a SHA-256 receipt?"</div>
            <p class="wi-a">Two-phase tools verify numbers (&plusmn;1%) and caveats before any gate closes.</p>
          </div>
        </div>
        <div class="whatif-pivot">
          <div>
            <strong style="color:#4ade80;">We built it:</strong> Open-source (<code>Apache 2.0</code>) subway-map routing in your VPC with wet-lab CRO gates.
          </div>
          <div class="whatif-actions">
            <button class="whatif-cta secondary" onclick="showChapter('ch1')">&#9654; Start Step 1 &rarr;</button>
            <button class="whatif-cta" onclick="showChapter('lab')">2.5-Hr Lab &rarr;</button>
            <button class="whatif-cta" style="background:#334155;border-color:#64748b;" onclick="jumpToRecapMap()">Route Recap &rarr;</button>
          </div>
        </div>
      </div>

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
              <td><strong>Two-phase execution &amp; dual validation:</strong> Deterministic Phase-1/2 tools write raw SHA-256 receipts and check human-defined cutoffs offline before AI Program Lead peer review.</td>
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
        <p style="font-size: 0.92rem; color: #334155; margin: 0 0 0.75rem 0;">A <strong>human discovery pod of 5</strong> (Program Lead <code>GOLD-1</code>, Computational Biologist <code>GOLD-2</code>, Structural Biologist <code>GOLD-3</code>, Medicinal Chemist <code>GOLD-4</code>, DMPK &amp; Safety Lead <code>GOLD-5</code>) collaborates with a <strong>mirrored 11-agent AI team</strong> (including 6 voiced specialist wingmen: <code>Grove-1</code>, <code>Helix-2</code>, <code>Fold-3</code>, <code>Spark-4</code>, <code>Shield-5</code>, and <code>Aegis-6</code>) across 7 steps, 4 go/no-go stage gates, and 1 physical lab handoff:</p>
        <div class="plate-box" id="plate-stage-gate">
          <img src="assets/oase_stage_gate_process.png" alt="GCP-OASE Stage-Gate Process" onclick="openLightbox(this.src, this.alt)">
          <div class="plate-caption">
            <span>Figure 3 — Stage-Gate Process: Campaign stages, four logged go/no-go gates, and one wet-lab handoff.</span>
            <span class="zoom-hint" onclick="openLightbox(this.parentElement.previousElementSibling.src, this.parentElement.previousElementSibling.alt)">&#128269; Click to enlarge</span>
          </div>
        </div>
        <table>
          <thead><tr><th>Step</th><th>Stage, Gate &amp; Work Orders</th><th>What Happens &amp; Key Outcome</th></tr></thead>
          <tbody>
            <tr><td><strong>Step 1</strong></td><td>Pre-Mission Brief &amp; Stage 0 (<code>WO-001</code>)</td><td><strong>All 5 Doctors + <code>Grove-1</code> &amp; <code>Helix-2</code></strong> co-author the Co-Scientist input prompt &amp; TPP, audit the 24-match Elo tournament (cryptic groove <code>IC-001</code> <code>1642.5 Elo</code> vs parked macrocycle <code>IC-002</code> <code>1588.0 Elo</code>), arm the Subway Map, and lock the <strong>5 Doctor &harr; AI Wingman mission pairings</strong>.</td></tr>
            <tr><td><strong>Step 2</strong></td><td>Stage 1 &rarr; <strong>Gate 1</strong> (<code>WO-002..003</code>)</td><td><strong><code>Helix-2</code> (<code>@computational-biologist</code>)</strong> validates PCSK9 in human genetics &amp; liver omics (<code>gnomAD pLI = 0.0001</code>, <code>OpenTargets 0.96</code>, <code>GTEx 184.2 TPM</code>, <code>AlphaGenome 0.984</code>). <strong>AI + Human Program Leads co-sign Gate 1 (Target Validation).</strong></td></tr>
            <tr><td><strong>Step 3</strong></td><td>Stage 2 &rarr; <strong>Gate 2</strong> (<code>WO-004..005</code>)</td><td><strong><code>Fold-3</code> (<code>@structural-biologist</code>)</strong> runs AlphaFold 3 co-fold (<code>ipTM = 0.84</code>, <code>pTM = 0.88</code>), <code>fpocket</code> (<code>0.68</code> groove vs <code>0.24</code> flat surface), and AutoDock Vina (<code>-9.4 kcal/mol</code>). <strong>AI Program Lead signs Gate 2 (Hit Identification) &amp; logs liability <code>L-002</code>.</strong></td></tr>
            <tr><td><strong>Step 4</strong></td><td>Stage 3 &rarr; <strong>Gate 3</strong> (<code>WO-006</code>)</td><td><strong><code>Spark-4</code> (<code>@medicinal-chemist</code>)</strong> flags high-lipophilicity cardiac (hERG) alert on <code>PCSK9-A02</code> and optimizes polar heterocycle <code>OASE-PCSK9-014</code> (<code>cLogP = 3.1</code>, <code>LipE = 5.2</code>, <code>0</code> alerts, <code>4</code>-step synthesis). <strong>AI Program Lead signs Gate 3 (Lead Optimization).</strong></td></tr>
            <tr><td><strong>&#9208; Lab Gate</strong></td><td>Lab Handoff (Seeded in Demo)</td><td><strong>Human Program Lead signs Lab Handoff</strong> for synthesis &amp; animal PK studies; agents pause cleanly on disk until measured rat (<code>54%</code>) and dog (<code>61%</code>) oral bioavailability files return.</td></tr>
            <tr><td><strong>Step 5</strong></td><td>Stage 4 &rarr; <strong>Gate 4</strong> (<code>WO-007..008</code>)</td><td><strong><code>Shield-5</code> (<code>@admet-dmpk-scientist</code>)</strong> projects human once-daily dose (<code>40 mg QD</code>, <code>F = 52%</code>, <code>t1/2 = 14.8 h</code>) and compiles the candidate dossier. <strong>AI + Human Program Leads co-sign Gate 4 (Candidate Nomination).</strong></td></tr>
            <tr><td><strong>Step 6</strong></td><td>Governance &amp; Override Checks</td><td><strong><code>Aegis-6</code> (<code>@finding-validator</code>)</strong> stress-tests the 10-check validator: <strong>blocks</strong> missing caveats (<code>REL-001</code>), out-of-tolerance numbers (<code>CIT-003</code>), and altered raw hashes (<code>PROV-002</code>), while <strong>permitting &amp; logging</strong> an audited reviewer override.</td></tr>
            <tr><td><strong>Step 7</strong></td><td>Post-Mission Debrief &amp; Portfolio Launch</td><td><strong>All 5 Doctors + <code>Grove-1</code> (<code>@science-program-lead</code>)</strong> reunite for a pair-by-pair Post-Mission Debrief against the Step 1 Research Brief, walk the traversed Subway Map, co-sign <code>executive/PORTFOLIO-HANDOFF.md</code> + the 30-page Evidence Portal, and invite attendees into the 5 live Grove seats.</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>

  <!-- PANEL SCION: DATA AND CONTROL ARCHITECTURE (4 PILLARS) -->
  <section class="chapter-panel" id="panel-scion">
    <div class="chapter-header">
      <h2>Act I (Part 2) — GCP-OASE Data and Control Architecture</h2>
      <span class="stage-pill">1. The Grove · 2. Work Orders &amp; Dual Validation · 3. Two-Phase Tool Execution · 4. Stage-Gate Review</span>
    </div>
    <div class="stack-full">
      <div class="plate-box" id="plate-benefits">
        <img src="assets/oase_benefits.jpg" alt="GCP-OASE Value Proposition" onclick="openLightbox(this.src, this.alt)">
        <div class="plate-caption">
          <span>Figure 4 — Four core solutions: Dynamic Routing &amp; Lab Gates, Two-Phase Tool Execution &amp; Dual Validation, Multi-Model Agent Teams, and 5-Layer Separation of Powers.</span>
          <span class="zoom-hint" onclick="openLightbox(this.parentElement.previousElementSibling.src, this.parentElement.previousElementSibling.alt)">&#128269; Click to enlarge</span>
        </div>
      </div>

      <div class="plate-box" id="plate-arch">
        <img src="assets/oase_data_arch.jpg" alt="GCP-OASE Data and Control Architecture" onclick="openLightbox(this.src, this.alt)">
        <div class="plate-caption">
          <span>Figure 5 — The 4 Core Pillars: 1. The Grove, 2. Work Orders &amp; Dual Validation, 3. Two-Phase Tool Execution, and 4. Stage-Gate Review.</span>
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
            <p>Every assignment is a numbered Work Order (<code>WO-001</code>..<code>WO-008</code>). Before closure, every finding must pass automated <strong>data-integrity verification</strong> (<code>oase validate check</code>) plus an independent <strong>scientific peer review</strong> by the AI Program Lead.</p>
          </div>
          <div class="pillar-card" id="scion-card-3">
            <h4>3. Two-Phase Tool Execution ("Why trust the numbers?")</h4>
            <p><strong>Phase 1 (Data Acquisition)</strong> processes primary datasets with deterministic tools and saves raw outputs + SHA-256 provenance records (<code>.meta.json</code>). <strong>Phase 2 (Threshold Evaluation)</strong> evaluates outputs offline against human expert-defined program cutoffs (<code>.analysis.json</code>) and attaches required caveats.</p>
          </div>
          <div class="pillar-card" id="scion-card-4">
            <h4>4. Stage-Gate Review ("Who decides to move forward?")</h4>
            <p>Work orders roll up into five logged gates: <strong>1. Target validation</strong> (AI + human sign), <strong>2. Hit ID</strong> (AI signs, logs liabilities), <strong>3. Lead opt</strong> (AI signs once resolved), <strong>4. Lab handoff</strong> (human signs; pauses on disk), and <strong>5. Candidate nomination</strong> (AI + human sign).</p>
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
            <tr><td><strong>5. Executive Views</strong></td><td><code>_site/index.html</code> &amp; <code>_site/chapters.html</code> (32 pages)</td><td>Compiled by <code>oase site build</code> into a self-contained static HTML Evidence Portal for portfolio review.</td></tr>
          </tbody>
        </table>
        <h4 style="margin: 0.9rem 0 0.4rem 0; color: #0f172a;">How a Campaign Enters GCP-OASE (3 Upstream Initiation Modes)</h4>
        <table>
          <thead><tr><th>Initiation Mode</th><th>Upstream Handoff Contract</th><th>Controller Bootstrap Action</th></tr></thead>
          <tbody>
            <tr><td><strong>Mode 1 — AI Co-Scientist / Enterprise Handoff</strong> <em>(Shown in Demo)</em></td><td>Structured tournament export (<code>seed/pcsk9-oral/coscientist-export.json</code> + <code>CHECKSUMS.json</code>)</td><td>Runs <code>oase coscientist ingest</code>, locks SHA-256 Layer-0 receipt, attaches caveat <code>hypothesis.adopted_not_generated</code>, and opens <code>WO-001</code>.</td></tr>
            <tr><td><strong>Mode 2 — Scientist-Authored Campaign Charter</strong></td><td>Human Program Lead defines target (<code>ENSG</code> / UniProt), indication, modality, and <code>.oase/thresholds.yaml</code> program cutoffs</td><td>Initializes Grove state at <code>t=0</code> and dispatches Stage 1 Target Validation work orders directly from Scion Webchat.</td></tr>
            <tr><td><strong>Mode 3 — Existing Internal Assay / Hit-List Re-Entry</strong></td><td>Internal HTS hit table (<code>.sdf</code> / <code>.csv</code>), crystal structure, or CRO assay readout</td><td>Registers cryptographic Layer-0 receipts in <code>raw/</code> and opens stage-appropriate Work Orders mid-funnel (e.g., Stage 2 or Stage 3).</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>

  <!-- CHAPTER 1 -->
  <section class="chapter-panel" id="panel-ch1">
    <div class="chapter-header">
      <h2>Step 1 — Pre-Mission Brief, Co-Scientist Prompt Co-Design &amp; Wingman Roster (`WO-001`)</h2>
      <span class="stage-pill">Pre-Mission Brief · 8-Turn Squadron Outset · checkpoints/ch0 &rarr; ch1</span>
    </div>
    <div class="stack-full">
      <div class="lab-block" style="border-left-color:#2563eb;background:#f8fafc;margin-bottom:0.25rem;">
        <div class="lab-block-hdr">
          <h4>Pre-Mission Huddle: Co-Authoring the Co-Scientist Input Prompt &amp; Locking Doctor &harr; AI Wingman Pairings</h4>
          <button class="subpage-back-btn" style="background:#d97706;" onclick="jumpToRecapMap()">See Route Map in Step 7 Debrief &rarr;</button>
        </div>
        <p style="margin:0 0 0.65rem 0;font-size:0.87rem;color:#334155;">Before a single GPU or chemistry work order runs, all <strong>5 human scientists</strong> huddle inside the Grove to co-design the <strong>Co-Scientist Research Brief &amp; Target Product Profile</strong> (<code>gates/STEP-01-pre-mission-brief.md</code> &amp; <code>seed/pcsk9-oral/campaign-seed.json</code>), debate the 24-match Elo tournament split, and assign each Doctor an AI specialist Wingman:</p>
        <div class="grid-2" style="gap:1rem;">
          <div class="terminal" style="margin:0;font-size:0.78rem;"><span class="cmd"># Co-Authored Co-Scientist Research Brief (daedalis-20261028-pcsk9-oral)</span>
<span class="ok">goal:</span> "Evaluate oral allosteric small-molecule and tricyclic macrocycle
  PCSK9 inhibitors disrupting LDLR EGF-A binding in ASCVD as a room-temp,
  once-daily alternative to injectable mAbs."
<span class="ok">preferences (authored by Marcus, Elena, Raj &amp; Claire):</span>
  - "Enforce human LoF cardioprotection (PCSK9 R46L / gnomAD) + hepatocyte
     selectivity (GTEx &ge; 100 TPM &amp; 1P AlphaGenome 1 Mb scoring)"
  - "Prioritize classical Rule-of-5 oral hepatocyte bioavailability
     (cLogP &le; 3.5, MW &le; 500, 0 Aronov hERG alerts, no permeation enhancers)"
<span class="ok">falsifiable_predictions:</span>
  - <span class="cmd">FP-001 (IC-001 Allosteric SM):</span> fpocket druggability &ge; 0.50 &amp; 1P AF3
    ligand ipTM &ge; 0.70 | <span class="err">KILL if druggability &lt; 0.30 or steric clash</span>
  - <span class="cmd">FP-002 (IC-002 Macrocycle):</span> EGF-A hot-spot coverage vs MK-0616 |
    <span class="err">PARK on Amber Backup Line behind Gate 3 CRO wet-lab hold</span></div>
          <div>
            <table style="margin:0;font-size:0.82rem;">
              <thead><tr><th>Human Scientist</th><th>Paired AI Wingman</th><th>Assigned Mission Scope</th></tr></thead>
              <tbody>
                <tr><td><strong>Dr. Sarah Chen</strong> (<code>GOLD-1</code>)</td><td><strong><code>Grove-1</code></strong> (<code>@science-program-lead</code>) + <strong><code>Aegis-6</code></strong></td><td>Charter, Gate 1 &amp; Gate 4 co-sign, Step 6 tamper audit &amp; Step 7 portfolio handoff</td></tr>
                <tr><td><strong>Dr. Marcus Vance</strong> (<code>GOLD-2</code>)</td><td><strong><code>Helix-2</code></strong> (<code>@computational-biologist</code>)</td><td><code>WO-001</code> Co-Scientist Elo audit + <code>WO-002..003</code> gnomAD, GTEx &amp; 1P <code>AlphaGenome</code></td></tr>
                <tr><td><strong>Dr. Elena Rostova</strong> (<code>GOLD-3</code>)</td><td><strong><code>Fold-3</code></strong> (<code>@structural-biologist</code>)</td><td><code>WO-004..005</code> 1P <code>AlphaFold 3</code> co-folding, <code>fpocket</code> groove check &amp; 3-phase Vina</td></tr>
                <tr><td><strong>Dr. Raj Patel</strong> (<code>GOLD-4</code>)</td><td><strong><code>Spark-4</code></strong> (<code>@medicinal-chemist</code>)</td><td><code>WO-006</code> Aronov hERG triage, <code>BRICS</code> oxadiazole rescue &amp; signed backup override</td></tr>
                <tr><td><strong>Dr. Claire Moreau</strong> (<code>GOLD-5</code>)</td><td><strong><code>Shield-5</code></strong> (<code>@admet-dmpk-scientist</code>)</td><td>Gate 3 CRO wet-lab hold, <code>WO-007..008</code> rat/dog &rarr; <code>40 mg QD</code> human PK &amp; dossier</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="grid-2">
        <div>
          <p>Entering via <strong>Initiation Mode 1 (AI Co-Scientist Seed Handoff)</strong>, the pod verifies environment readiness (<code>oase doctor</code>) and ingests the 24-match pairwise Co-Scientist tournament export (<code>seed/pcsk9-oral/coscientist-export.json</code>) comparing candidate oral PCSK9 strategies in ASCVD.</p>
          <table>
            <thead><tr><th>Hypothesis ID</th><th>Modality &amp; Mechanism</th><th>Tournament Elo</th><th>Match Record / Win Rate</th><th>Status</th></tr></thead>
            <tbody>
              <tr><td><code>IC-001</code> (H-001)</td><td>Allosteric Small Molecule (`Pocket #1` cryptic groove)</td><td><strong>1642.5</strong> (`ELO 1642`)</td><td><code>10W-2L</code> (<code>0.83</code> win rate)</td><td><span class="pass-pill">PRIMARY LINE (+54.5 Elo)</span></td></tr>
              <tr><td><code>IC-002</code> (H-002)</td><td>Oral Tricyclic Macrocycle (`EGF-A` flat surface)</td><td>1588.0 (`ELO 1588`)</td><td><code>8W-4L</code> (<code>0.67</code> win rate)</td><td><span class="warn-pill">PARALLEL BACKUP LINE</span></td></tr>
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
    </div>
  </section>

  <!-- CHAPTER 2 -->
  <section class="chapter-panel" id="panel-ch2">
    <div class="chapter-header">
      <h2>Act II (Chapter 2) — Stage 1 Target Validation: Human Genetics, GWAS &amp; Expression (`WO-002`..`WO-003`)</h2>
      <span class="stage-pill">Stage 1 &rarr; Gate 1 · checkpoints/ch2</span>
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
      <span class="stage-pill">Stage 2 &rarr; Gate 2 · checkpoints/ch3</span>
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
      <span class="stage-pill">Stage 3 &rarr; Gate 3 &rarr; Lab Gate · checkpoints/ch4</span>
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
      <span class="stage-pill">Stage 4 &rarr; Gate 4 (AI + Human Co-Sign) · checkpoints/ch5</span>
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
      <h2>Step 6 — Adversarial Tamper Drills &amp; Co-Signed Human Override</h2>
      <span class="stage-pill">10-Check Validator · 3 Tamper Cases Blocked + 1 Override Logged · checkpoints/ch6</span>
    </div>
    <div class="stack-full">
      <div class="grid-2">
        <div>
          <p>In <strong>Step 6</strong>, the pod stress-tests how OASE verifies that specialist reports match underlying data and tracks human overrides. The deterministic validator (<code>oase validate check</code>) <strong>blocks work-order closure on tampering/fabrication cases</strong> while <code>oase workorder override</code> <strong>permits and logs an explicit co-signed scientific override</strong> with actor and rationale in <code>program-state/decision-log.md</code>:</p>
          <table>
            <thead><tr><th>Governance Test Case</th><th>Tested Condition</th><th>Mechanism / Check</th><th>Result</th></tr></thead>
            <tbody>
              <tr><td><strong>Case 1 — Missing Required Caveat</strong></td><td>Remove mandatory relay <code>af3.low_confidence_segments</code> from <code>WO-004.md</code></td><td><code>relay_coverage</code> (<code>REL-001</code>)</td><td><span class="fail-pill">BLOCKED (exit=1)</span></td></tr>
              <tr><td><strong>Case 2 — Citation Drift &gt; &plusmn;1%</strong></td><td>Alter cited Vina score from <code>-9.4</code> to <code>-11.2 kcal/mol</code> in <code>WO-005.md</code></td><td><code>source_tags_resolve</code> (<code>CIT-003</code>)</td><td><span class="fail-pill">BLOCKED (exit=1)</span></td></tr>
              <tr><td><strong>Case 3 — Altered Raw Data File</strong></td><td>Modify <code>raw/docking/pcsk9_pocket1_vina.sdf</code> so SHA-256 mismatches <code>.meta.json</code> (plus stripped <code>THR-001</code> check)</td><td><code>provenance_valid</code> (<code>PROV-002</code>)</td><td><span class="fail-pill">BLOCKED (exit=1)</span></td></tr>
              <tr><td><strong>Case 4 — Co-Signed Backup Exception</strong></td><td>Retain exploratory backup scaffold <code>PCSK9-B07</code> (<code>MW = 512 Da &gt; 500 Da</code> soft Lipinski limit, <code>QED = 0.61</code>, <code>0</code> hERG alerts) without editing immutable <code>.oase/thresholds.yaml</code></td><td><code>oase workorder override</code> &rarr; <code>events.ndjson</code> &amp; <code>decision-log.md</code></td><td><span class="pass-pill">CO-SIGNED &amp; LOGGED</span></td></tr>
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

<span class="cmd">$ oase workorder override WO-006 --actor medicinal-chemist --cosign science-program-lead \</span>
<span class="cmd">    --reason "Retain backup scaffold PCSK9-B07 (MW 512 Da > 500 Da soft Lipinski limit, QED 0.61, 0 hERG alerts) pending 14-day patch-clamp counter-screen"</span>
<span class="ok">[CO-SIGNED &amp; LOGGED] Appended workorder.overridden to .oase/control/events.ndjson &amp; decision-log.md (.oase/thresholds.yaml untouched)</span></div>
      </div>
    </div>
  </section>

  <!-- CHAPTER 7: STEP 7 MISSION CLOSEOUT, ROUTE RECAP, PORTFOLIO SIGN-OFF & SCORECARD -->
  <section class="chapter-panel" id="panel-ch7">
    <div class="chapter-header">
      <h2>Step 7 — Post-Mission Debrief, Subway Map Recap &amp; Portfolio Sign-Off</h2>
      <span class="stage-pill">7-Turn Squadron Debrief · 8/8 WOs · OASE-PCSK9-014 (40 mg QD) · checkpoints/ch7</span>
    </div>
    <div class="stack-full">
      <div>
        <p>In <strong>Step 7</strong>, all <strong>5 human scientists</strong> (<code>Sarah</code>, <code>Marcus</code>, <code>Elena</code>, <code>Raj</code>, <code>Claire</code>) and <strong><code>Grove-1</code> (<code>@science-program-lead</code>)</strong> reunite for a structured <strong>Post-Mission Debrief</strong> against their Step 1 Co-Scientist Research Brief (`gates/STEP-01-pre-mission-brief.md` &rarr; `gates/STEP-07-portfolio-closeout.md`), reporting what each Doctor + AI Wingman pair proved, where biology forced a dynamic reroute, and co-signing <code>executive/PORTFOLIO-HANDOFF.md</code> for IND-enabling GLP toxicology:</p>
        <h4 style="margin: 0.6rem 0 0.5rem 0; color: #0f172a;">Squadron Pair-by-Pair Post-Mission Debrief (<code>gates/STEP-07-portfolio-closeout.md</code>)</h4>
        <table>
          <thead><tr><th>Doctor &harr; AI Wingman Pair</th><th>Step 1 Outset Hypothesis / Rule</th><th>What Happened in Execution</th><th>Verified Outcome</th></tr></thead>
          <tbody>
            <tr><td><strong>Dr. Marcus Vance + <code>Helix-2</code></strong></td><td>Require human LoF safety &amp; liver-restricted regulation</td><td><code>WO-002..003</code> cleared gnomAD <code>pLI = 0.0001</code>, GTEx <code>184.2 TPM</code> (brain <code>&lt;0.8 TPM</code>), and 1P <code>AlphaGenome rs2479409 = 0.984</code></td><td><span class="pass-pill">CNS RISK CLEARED</span></td></tr>
            <tr><td><strong>Dr. Elena Rostova + <code>Fold-3</code></strong></td><td><code>FP-001</code>: Prove cryptic groove (&ge;0.50) or kill small molecule</td><td>1P <code>AlphaFold 3</code> co-fold (<code>ipTM = 0.84</code>) + <code>fpocket</code> (<code>0.68</code> groove vs <code>0.24</code> flat EGF-A) + Vina (<code>-9.4 kcal/mol</code>)</td><td><span class="pass-pill">FLAT SPUR KILLED</span></td></tr>
            <tr><td><strong>Dr. Raj Patel + <code>Spark-4</code></strong></td><td>Classical Rule-of-5 oral chemistry + <code>0</code> Aronov hERG alerts</td><td>Top docker <code>PCSK9-A02</code> tripped hERG (<code>cLogP 5.09</code>) &rarr; <code>BRICS</code> reroute rescued <strong><code>OASE-PCSK9-014</code></strong> (<code>cLogP 3.01</code>, <code>0</code> alerts) + signed override on <code>PCSK9-B07</code></td><td><span class="pass-pill">BRICS RESCUED</span></td></tr>
            <tr><td><strong>Dr. Claire Moreau + <code>Shield-5</code></strong></td><td>Enforce Gate 3 CRO wet-lab hold &amp; <code>&le;100 mg QD</code> unenhanced tablet</td><td>Ingested patch-clamp hERG (<code>&gt;30 &mu;M</code>) + rat (<code>54%</code>) / dog (<code>61%</code>) PK &rarr; projected <strong><code>40.0 mg QD</code></strong> human oral tablet (<code>F = 52%</code>)</td><td><span class="pass-pill">40 MG QD LOCKED</span></td></tr>
            <tr><td><strong>Dr. Sarah Chen + <code>Grove-1</code> / <code>Aegis-6</code></strong></td><td>Zero-fabrication provenance across all 5 artifact layers</td><td><code>8/8</code> Work Orders accepted, <code>4/4</code> Stage Gates signed, <code>3/3</code> tamper drills blocked, 30-page Evidence Portal published</td><td><span class="pass-pill">PORTFOLIO SIGNED</span></td></tr>
          </tbody>
        </table>
        <h4 style="margin: 0.9rem 0 0.5rem 0; color: #0f172a;">Executive Candidate Nomination &amp; Stage-Gate Sign-Off Ledger (<code>OASE-PCSK9-014</code>)</h4>
        <table>
          <thead><tr><th>Campaign Milestone</th><th>Work Orders &amp; Signatories</th><th>Key Verified Scientific Evidence</th><th>Gate Status</th></tr></thead>
          <tbody>
            <tr>
              <td><strong>Stage 0–1 &rarr; Gate 1: Target Validation</strong></td>
              <td><code>WO-001..003</code> · Co-signed by Human + AI Program Leads</td>
              <td><code>IC-001</code> cryptic groove ranked #1 (<code>1642.5 Elo</code>); human LoF cardioprotection (<code>gnomAD pLI = 0.0001</code>, <code>OpenTargets 0.96</code>) and liver-selective expression (<code>GTEx 184.2 TPM</code>, <code>AlphaGenome 0.984</code>; brain <code>&lt; 0.8 TPM</code>).</td>
              <td><span class="pass-pill">GATE 1 SIGNED</span></td>
            </tr>
            <tr>
              <td><strong>Stage 2 &rarr; Gate 2: Structural Hit ID</strong></td>
              <td><code>WO-004..005</code> · Signed by Structural Bio + AI Lead</td>
              <td><code>AlphaFold 3</code> co-fold (<code>ipTM = 0.84</code>), <code>fpocket</code> cryptic groove druggability (<code>0.68</code> vs <code>0.24</code> flat EGF-A), and <code>AutoDock Vina</code> pose (<code>-9.4 kcal/mol</code>); lipophilicity risk <code>L-002</code> logged for Step 4.</td>
              <td><span class="pass-pill">GATE 2 SIGNED</span></td>
            </tr>
            <tr>
              <td><strong>Stage 3 &rarr; Gate 3 + &#9208; Wet-Lab Bridge</strong></td>
              <td><code>WO-006</code> · Signed by Med Chem, DMPK &amp; Program Lead</td>
              <td><code>PCSK9-A02</code> (<code>cLogP = 5.09</code>) eliminated on cardiac hERG alert; neutral 1,2,4-oxadiazole <strong><code>OASE-PCSK9-014</code></strong> (<code>cLogP = 3.1</code>, <code>LipE = 5.2</code>, <code>0</code> alerts) cleared in wet-lab SPR, patch-clamp hERG (<code>&gt;30 &mu;M</code>), and rat (<code>54%</code>) / dog (<code>61%</code>) cassette PK.</td>
              <td><span class="pass-pill">LAB VERIFIED</span></td>
            </tr>
            <tr>
              <td><strong>Stage 4 &rarr; Gate 4: Candidate Nomination</strong></td>
              <td><code>WO-007..008</code> + Governance Audit · Pod &amp; Portfolio Sign-Off</td>
              <td>Projected human oral dose <strong><code>40.0 mg QD</code></strong> (<code>F = 52%</code>, <code>t1/2 = 14.8 h</code>, conventional tablet); <code>3 / 3</code> tamper drills blocked, <code>PCSK9-B07</code> backup exception logged, and 30-page Evidence Portal published with <code>0</code> ungrounded claims.</td>
              <td><span class="pass-pill">READY FOR GLP TOX</span></td>
            </tr>
          </tbody>
        </table>
        <div class="portal-links" style="margin-bottom: 1.15rem;">
          <a href="finding_findings_regulatory_WO-008_md.html">Open WO-008 Candidate Nomination Dossier</a>
          <a href="index.html">Open Full 30-Page Evidence Portal Index</a>
          <a href="plan.html">Open Pilot Build Plan &amp; Architecture Spec</a>
        </div>

        <!-- CAMPAIGN ROUTE RECAP: INTERACTIVE SUBWAY MAP -->
        <div id="recap-subway-section" style="margin: 1.25rem 0 1.15rem 0; padding-top: 1rem; border-top: 2px solid #e2e8f0;">
          <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;margin-bottom:0.45rem;">
            <h3 style="margin:0;color:#0f172a;font-size:1.12rem;">Recap: Map of What We Ran &mdash; How the Campaign Dynamically Routed Across 6 Stations</h3>
            <span class="stage-pill">Click Any Station (`S0`..`S5`) to Inspect Track Switches</span>
          </div>
          <p style="margin:0 0 0.8rem 0;font-size:0.9rem;color:#334155;line-height:1.5;">
            Looking back across <code>Steps 1&ndash;6</code>, watching one completed replay can look linear&mdash;just like tracing one commuter's trip makes a city subway look like a single track. Here is the actual map of what happened under the hood: the Step 1 <strong>Co-Scientist Research Brief</strong> split two modality lines (<strong>Green: <code>IC-001</code> Small Molecule</strong> &amp; <strong>Amber: <code>IC-002</code> Macrocycle Backup</strong>), Step 3 terminated the flat <code>EGF-A</code> orthosteric spur (<code>0.24</code>) and clashing <code>Analog-05</code> (<code>1.72 &Aring;</code>), Step 4 hit a <strong>Red Signal on top docker <code>PCSK9-A02</code> (<code>hERG</code> / <code>cLogP 5.09</code>) and dynamically took the <code>BRICS</code> Reroute Loop to rescue <code>OASE-PCSK9-014</code></strong>, and Step 5 paused cleanly on disk across the CRO wet-lab PK hold. Click any station to inspect what happened&mdash;and copy a live Scion prompt to test what OASE does when data comes back differently:
          </p>

          <div class="subway-board" style="margin-bottom:0.85rem;">
            <div class="subway-legend">
              <span><strong style="color:#10b981;">&#9644;&#9644; Green Line:</strong> Primary Allosteric Small Molecule (<code>IC-001</code> &rarr; <code>OASE-PCSK9-014</code>)</span>
              <span><strong style="color:#f59e0b;">&#9644;&#9644; Amber Line:</strong> Parallel Tricyclic Macrocycle Backup (<code>IC-002</code> / <code>PCSK9-B07</code> Override)</span>
              <span><strong style="color:#38bdf8;">&#9644;&#9644; Blue Loops:</strong> Data-Driven Detours (<code>scRNA-seq .h5ad</code> &amp; <code>BRICS</code> Med-Chem Rescue)</span>
              <span><strong style="color:#ef4444;">&#10005; Red Spurs:</strong> Disqualified by Phase-2 Cutoffs</span>
            </div>

            <svg viewBox="0 0 1160 330" style="width:100%;height:auto;display:block;background:#020617;border-radius:8px;border:1px solid #1e293b;">
              <!-- S1 Single-cell h5ad detour loop (dashed blue) -->
              <path d="M 275 155 C 295 55, 435 55, 465 155" fill="none" stroke="#38bdf8" stroke-width="3.5" stroke-dasharray="7,5"/>
              <rect x="295" y="28" width="150" height="24" rx="5" fill="#0c4a6e" stroke="#38bdf8" stroke-width="1"/>
              <text x="370" y="44" fill="#e0f2fe" font-size="11" font-family="monospace" text-anchor="middle">Bulk &lt;5 TPM &rarr; scRNA h5ad</text>

              <!-- S3 BRICS Med-Chem Active Reroute Loop (solid cyan/green: ACTUALLY TAKEN!) -->
              <path d="M 655 155 C 680 55, 815 55, 850 155" fill="none" stroke="#10b981" stroke-width="5.5"/>
              <rect x="662" y="24" width="186" height="26" rx="5" fill="#064e3b" stroke="#34d399" stroke-width="1.5"/>
              <text x="755" y="41" fill="#ecfdf5" font-size="11.5" font-weight="bold" font-family="monospace" text-anchor="middle">&#8618; BRICS Loop: OASE-PCSK9-014</text>

              <!-- Amber Backup Line (IC-002 Macrocycle) -->
              <path d="M 95 165 C 145 270, 200 270, 275 270 L 850 270 C 930 270, 995 235, 1055 155" fill="none" stroke="#f59e0b" stroke-width="4" stroke-dasharray="8,5"/>
              <text x="545" y="294" fill="#fbbf24" font-size="11.5" font-family="monospace" text-anchor="middle">Amber Backup Line: IC-002 Oral Macrocycle (Parked at S0 &middot; Reopened via S5 Override if S4 Fails)</text>

              <!-- Vertical transfer connectors -->
              <line x1="465" y1="155" x2="465" y2="270" stroke="#64748b" stroke-width="2" stroke-dasharray="4,4"/>
              <line x1="850" y1="155" x2="850" y2="270" stroke="#64748b" stroke-width="2" stroke-dasharray="4,4"/>

              <!-- Red Dead-End Spurs -->
              <!-- S2 EGF-A 0.24 & Clash spur -->
              <path d="M 465 155 L 548 212" fill="none" stroke="#ef4444" stroke-width="4"/>
              <text x="556" y="220" fill="#fca5a5" font-size="11" font-weight="bold" font-family="monospace">&#10005; EGF-A 0.24 / Clash 1.72&Aring;</text>

              <!-- S3 PCSK9-A02 hERG Red Signal spur -->
              <path d="M 655 155 L 748 155" fill="none" stroke="#ef4444" stroke-width="5"/>
              <text x="756" y="159" fill="#fca5a5" font-size="11.5" font-weight="bold" font-family="monospace">&#10005; A02 (hERG cLogP 5.09)</text>

              <!-- Green Main Line segments -->
              <line x1="95" y1="155" x2="655" y2="155" stroke="#10b981" stroke-width="6"/>
              <line x1="850" y1="155" x2="1055" y2="155" stroke="#10b981" stroke-width="6"/>

              <!-- Clickable Transfer Stations -->
              <g class="stn-node" onclick="selectStation('s0')">
                <circle id="svg-stn-s0" cx="95" cy="155" r="15" fill="#0f172a" stroke="#38bdf8" stroke-width="4"/>
                <text x="95" y="159" fill="#fff" font-size="11" font-weight="bold" font-family="monospace" text-anchor="middle">S0</text>
                <text x="95" y="192" fill="#e2e8f0" font-size="12" font-weight="bold" text-anchor="middle">Co-Scientist</text>
                <text x="95" y="207" fill="#94a3b8" font-size="10.5" font-family="monospace" text-anchor="middle">WO-001 Seed</text>
              </g>

              <g class="stn-node" onclick="selectStation('s1')">
                <circle id="svg-stn-s1" cx="275" cy="155" r="15" fill="#0f172a" stroke="#10b981" stroke-width="3.5"/>
                <text x="275" y="159" fill="#fff" font-size="11" font-weight="bold" font-family="monospace" text-anchor="middle">S1</text>
                <text x="275" y="192" fill="#e2e8f0" font-size="12" font-weight="bold" text-anchor="middle">Genetics &amp; GTEx</text>
                <text x="275" y="207" fill="#94a3b8" font-size="10.5" font-family="monospace" text-anchor="middle">Gate 1 (WO-002..3)</text>
              </g>

              <g class="stn-node" onclick="selectStation('s2')">
                <circle id="svg-stn-s2" cx="465" cy="155" r="15" fill="#0f172a" stroke="#10b981" stroke-width="3.5"/>
                <text x="465" y="159" fill="#fff" font-size="11" font-weight="bold" font-family="monospace" text-anchor="middle">S2</text>
                <text x="465" y="128" fill="#e2e8f0" font-size="12" font-weight="bold" text-anchor="middle">AF3 &amp; Pockets</text>
                <text x="465" y="113" fill="#94a3b8" font-size="10.5" font-family="monospace" text-anchor="middle">Gate 2 (WO-004..5)</text>
              </g>

              <g class="stn-node" onclick="selectStation('s3')">
                <circle id="svg-stn-s3" cx="655" cy="155" r="15" fill="#0f172a" stroke="#10b981" stroke-width="3.5"/>
                <text x="655" y="159" fill="#fff" font-size="11" font-weight="bold" font-family="monospace" text-anchor="middle">S3</text>
                <text x="655" y="192" fill="#e2e8f0" font-size="12" font-weight="bold" text-anchor="middle">ADMET Reroute</text>
                <text x="655" y="207" fill="#94a3b8" font-size="10.5" font-family="monospace" text-anchor="middle">Gate 3 (WO-006)</text>
              </g>

              <g class="stn-node" onclick="selectStation('s4')">
                <circle id="svg-stn-s4" cx="850" cy="155" r="15" fill="#0f172a" stroke="#f59e0b" stroke-width="3.5"/>
                <text x="850" y="159" fill="#fde68a" font-size="11" font-weight="bold" font-family="monospace" text-anchor="middle">&#9208;</text>
                <text x="850" y="192" fill="#fde68a" font-size="12" font-weight="bold" text-anchor="middle">Wet-Lab &amp; PK</text>
                <text x="850" y="207" fill="#94a3b8" font-size="10.5" font-family="monospace" text-anchor="middle">CRO Hold + WO-007</text>
              </g>

              <g class="stn-node" onclick="selectStation('s5')">
                <circle id="svg-stn-s5" cx="1055" cy="155" r="15" fill="#0f172a" stroke="#10b981" stroke-width="3.5"/>
                <text x="1055" y="159" fill="#fff" font-size="11" font-weight="bold" font-family="monospace" text-anchor="middle">S5</text>
                <text x="1055" y="128" fill="#4ade80" font-size="12" font-weight="bold" text-anchor="middle">Gate 4 &amp; Audit</text>
                <text x="1055" y="113" fill="#94a3b8" font-size="10.5" font-family="monospace" text-anchor="middle">40 mg QD (WO-008)</text>
              </g>
            </svg>

            <div class="subway-station-pills">
              <button class="stn-pill active" id="pill-s0" onclick="selectStation('s0')">S0: Co-Scientist Prompt &amp; Split</button>
              <button class="stn-pill" id="pill-s1" onclick="selectStation('s1')">S1: Genetics / scRNA-seq Switch</button>
              <button class="stn-pill" id="pill-s2" onclick="selectStation('s2')">S2: Cryptic Groove vs EGF-A</button>
              <button class="stn-pill" id="pill-s3" onclick="selectStation('s3')">S3: hERG Block &rarr; BRICS Loop</button>
              <button class="stn-pill" id="pill-s4" onclick="selectStation('s4')">S4: &#9208; Wet-Lab Hold &amp; Oral PK</button>
              <button class="stn-pill" id="pill-s5" onclick="selectStation('s5')">S5: Gate 4 &amp; Macrocycle Override</button>
            </div>
          </div>

          <div id="subway-inspector" class="grid-2" style="margin-bottom:0.85rem;"></div>

          <details style="background:#f8fafc;border:1px solid #cbd5e1;border-radius:8px;padding:0.75rem 1.05rem;">
            <summary style="cursor:pointer;font-weight:700;color:#1e3a8a;font-size:0.88rem;">
              &#8644; Why Pair a Linear 7-Step Replay With a Dynamic Subway State Machine?
            </summary>
            <table style="margin-top:0.65rem;">
              <thead><tr><th>Dimension</th><th>Linear 7-Step Replay Spine (<code>Step 1 &rarr; Step 7</code>)</th><th>Dynamic Subway Map (<code>.oase/control/</code> State Machine)</th><th>How They Work Together</th></tr></thead>
              <tbody>
                <tr><td><strong>Primary Role</strong></td><td>Easy for 20 scientists and executives to follow in 4.5 minutes of recorded video without getting lost in 16 branches.</td><td>Proves OASE is <strong>not</strong> a rigid Nextflow DAG: tool outputs spawn detours, pause for wet-lab CRO assays, or switch chemotype lines.</td><td>The <strong>7 chapters</strong> trace our winning journey (including the Step 4 <code>hERG</code> reroute), while the <strong>Recap Map + Live Scion Prompts</strong> let you test alternate branches on demand.</td></tr>
                <tr><td><strong>Upstream Seed Brief</strong></td><td>Introduced up front in <code>Step 1</code>.</td><td><strong>Draws the map:</strong> TPP rules (unenhanced oral Ro5, LoF safety, <code>FP-001</code> kill criteria) lock <code>.oase/thresholds.yaml</code> and park <code>IC-002</code> as backup.</td><td>Every threshold and detour above traces directly back to the initial human + Co-Scientist goal definition.</td></tr>
                <tr><td><strong>Workshop Reset Safety</strong></td><td>Deterministic <code>ch0..ch7</code> Git + SQLite snapshots reset in <code>&lt;2s</code>.</td><td>Live Scion Webchat lets attendees ask <code>@science-program-lead</code> to switch tracks mid-session.</td><td>Branch freely in live Scion Webchat, then click <strong><code>&#8634; Reset CHN (&lt;2s)</code></strong> to snap back cleanly.</td></tr>
              </tbody>
            </table>
          </details>
        </div>

        <details style="background:#f8fafc;border:1px solid #cbd5e1;border-radius:8px;padding:0.85rem 1.1rem;margin-top:0.75rem;">
          <summary style="cursor:pointer;font-weight:700;color:#1e3a8a;font-size:0.9rem;">
            &#128300; Expand Under-the-Hood Architecture Scorecard &amp; Engineering Verification Notes
          </summary>
          <table style="margin-top:0.75rem;">
            <thead><tr><th>Architecture Pillar</th><th>Target Outcome</th><th>Measured Simulation Result</th><th>Engineering Verification Note</th><th>Verdict</th></tr></thead>
            <tbody>
              <tr id="score-row-1">
                <td><strong>1. Two-Phase Tool Latch</strong><br>(Fetch/Compute vs. Offline Analyze)</td>
                <td>100% of Phase-2 <code>analyze</code> commands run offline against immutable JSON + thresholds</td>
                <td><code>51 / 51</code> Phase-2 commands verified offline by <code>oase doctor</code>; <code>9</code> live + <code>11</code> checkpoint <code>.analysis.json</code> records verified</td>
                <td>All 36 program threshold sets resolved explicitly in <code>.oase/thresholds.yaml</code> so cutoffs remain versioned and human-owned.</td>
                <td><span class="pass-pill">LANDED (36/36 RESOLVED)</span></td>
              </tr>
              <tr id="score-row-2">
                <td><strong>2. Zero-Fabrication Citations</strong><br>(<code>{source: path $.jsonpath}</code>)</td>
                <td>Every numeric claim in Markdown is mechanically checked within &plusmn;1% of raw JSON</td>
                <td><code>28 / 28</code> scalar JSONPath citations verified within &plusmn;1%; validator caught <code>-11.2</code> vs <code>-9.4</code> in &lt;0.2s</td>
                <td>Single-citation-per-line formatting keeps Markdown prose and static portal rendering 100% deterministic.</td>
                <td><span class="pass-pill">LANDED (ZERO DRIFT)</span></td>
              </tr>
              <tr id="score-row-3">
                <td><strong>3. Mandatory Caveat Relays</strong><br>(<code>**Relay: `code`**</code>)</td>
                <td>Agents cannot drop negative caveats (e.g. disorder, hERG pharmacophore limits)</td>
                <td>All 8 work orders enforce mandatory relays; Drill 3 caught dropped <code>af3.low_confidence_segments</code></td>
                <td>Full provenance makes underlying tool heuristics (such as SMARTS pharmacophore definitions in <code>oase admet</code>) transparent and auditable by medicinal chemists.</td>
                <td><span class="pass-pill">STRONGEST DIFFERENTIATOR</span></td>
              </tr>
              <tr id="score-row-4">
                <td><strong>4. Scion + OASE Reproducibility</strong><br>(<code>ENV_VERSION</code> + 8 Checkpoints)</td>
                <td>Single-command install of Python + 7 C/C++/Go binaries stamped with SHA-256</td>
                <td>All 7 binaries (<code>vina</code>, <code>fpocket</code>, <code>rate4site</code>, <code>muscle</code>, <code>hypex</code>, <code>elo</code>, <code>prox</code>) stamped</td>
                <td>Reproducible Linux bootstrap (<code>bootstrap-oase-env.sh</code>) + sub-250ms Scion Hub checkpoint resets across <code>ch0..ch7</code>.</td>
                <td><span class="pass-pill">REPEATABLE E2E</span></td>
              </tr>
            </tbody>
          </table>
        </details>
      </div>
    </div>
  </section>

  <!-- 2.5-HOUR (150-MINUTE) GUIDED WORKSHOP & HANDS-ON LAB PANEL -->
  <section class="chapter-panel" id="panel-lab">
    <div class="chapter-header">
      <h2>2.5-Hour (150-Minute) Guided Workshop &amp; Hands-On Lab Playbook (`pcsk9-oral`)</h2>
      <span class="stage-pill">0:00&ndash;2:30 · 3 "What Ifs" · 5 Scientist Seats · 6 Hands-On Blocks</span>
    </div>
    <div class="stack-full">
      <div class="whatif-banner">
        <h3>Part 0 (`0:00&ndash;0:15` &middot; 15 min) &mdash; Open With Three "What If" Provocations, Then Pivot: <em>"Well &mdash; We Built It."</em></h3>
        <p style="margin:0.2rem 0 0.7rem 0;font-size:0.86rem;color:#cbd5e1;">Before opening a terminal or architecture diagram, put these three questions to the discovery scientists and platform leads in the room and debate where today's chatbots and static DAGs break:</p>
        <div class="whatif-grid">
          <div class="whatif-card">
            <div class="wi-num">Slide / Question 1 &middot; Multiplayer Grove</div>
            <div class="wi-q">"What if we had an agentic AI surface all of our scientists could use together at the same time?"</div>
            <p class="wi-a">Demonstrate 2+ human scientists typing simultaneously inside one shared Scion Grove alongside 11 specialist AI agents.</p>
          </div>
          <div class="whatif-card">
            <div class="wi-num">Slide / Question 2 &middot; Zero Vendor Lock-In</div>
            <div class="wi-q">"What if we had optionality in the frontier models we use—not locking our science into one vendor or one model's blind spots?"</div>
            <p class="wi-a">Show <strong>Gemini</strong>, <strong>Anthropic Claude</strong>, and <strong>OpenAI</strong> collaborating via portable tiers so no model family ever reviews its own work.</p>
          </div>
          <div class="whatif-card">
            <div class="wi-num">Slide / Question 3 &middot; Verified Governance</div>
            <div class="wi-q">"What if every AI-assisted claim, threshold check, and stage-gate decision was cryptographically verified against raw data?"</div>
            <p class="wi-a">Let participants actively tamper with raw files and findings in Block 4&mdash;and watch <code>oase validate check</code> block every violation in &lt;1s.</p>
          </div>
        </div>
      </div>

      <div>
        <h3 style="margin:0.2rem 0 0.45rem 0;color:#0f172a;">Assign the 5 Discovery Pod Seats (Individual or 2&ndash;4 Person Breakout Pods)</h3>
        <p style="margin:0 0 0.65rem 0;font-size:0.88rem;color:#334155;">Each chapter video is <strong>36&ndash;43 seconds</strong> long to establish crisp context; spend the remaining 15&ndash;25 minutes of each block in live Scion Webchat Q&amp;A, CLI inspection, and scientific debate across the 5 roles:</p>
        <table>
          <thead><tr><th>Pod Seat</th><th>Scientist Persona</th><th>Login Handle</th><th>Stages Led in Workshop</th><th>Paired AI Wingmen</th></tr></thead>
          <tbody>
            <tr><td><strong>Seat 1 (<code>GOLD-1</code>)</strong></td><td><strong>Dr. Sarah Chen</strong> &mdash; Program Lead</td><td><code>oase-sarah</code></td><td>Step 1 Kickoff, Gate 1 &amp; Gate 4 Co-Sign, Step 7 Portfolio Handoff</td><td><code>@science-program-lead</code> (<code>Grove-1</code>) &middot; <code>@project-curator</code></td></tr>
            <tr><td><strong>Seat 2 (<code>GOLD-2</code>)</strong></td><td><strong>Dr. Marcus Vance</strong> &mdash; Comp Biologist</td><td><code>oase-marcus</code></td><td>Step 1 (<code>WO-001</code> Elo) &amp; Step 2 (<code>WO-002..003</code> Genetics, GTEx, AlphaGenome)</td><td><code>@computational-biologist</code> (<code>Helix-2</code>)</td></tr>
            <tr><td><strong>Seat 3 (<code>GOLD-3</code>)</strong></td><td><strong>Dr. Elena Rostova</strong> &mdash; Structural Biologist</td><td><code>oase-elena</code></td><td>Step 3 (<code>WO-004..005</code> AF3, <code>fpocket</code>, Vina) &amp; Step 6 Governance Audit</td><td><code>@structural-biologist</code> (<code>Fold-3</code>) &middot; <code>@finding-validator</code> (<code>Aegis-6</code>)</td></tr>
            <tr><td><strong>Seat 4 (<code>GOLD-4</code>)</strong></td><td><strong>Dr. Raj Patel</strong> &mdash; Medicinal Chemist</td><td><code>oase-raj</code></td><td>Step 4 (<code>WO-006</code> RDKit, ADMET hERG Takedown, BRICS MMP &amp; Synthesis)</td><td><code>@medicinal-chemist</code> (<code>Spark-4</code>)</td></tr>
            <tr><td><strong>Seat 5 (<code>GOLD-5</code>)</strong></td><td><strong>Dr. Claire Moreau</strong> &mdash; DMPK &amp; Safety Lead</td><td><code>oase-claire</code></td><td>&#9208; Lab Gate &amp; Step 5 (<code>WO-007..008</code> Oral PK <code>40 mg QD</code> &amp; Dossier)</td><td><code>@admet-dmpk-scientist</code> (<code>Shield-5</code>) &middot; <code>@regulatory-scientist</code></td></tr>
          </tbody>
        </table>
      </div>

      <div>
        <h3 style="margin:0.2rem 0 0.65rem 0;color:#0f172a;">Minute-by-Minute 2.5-Hour (`150m`) Guided Lab Walkthrough</h3>

        <div class="lab-block">
          <div class="lab-block-hdr">
            <h4>Block 1 (`0:15&ndash;0:40` &middot; 25 min) &mdash; Multiplayer Grove Kickoff &amp; Human Genetic Target Validation (`Steps 1&ndash;2` &middot; `WO-001..003` &middot; Gate 1)</h4>
            <div>
              <button class="subpage-back-btn" onclick="showChapter('ch1')">Jump to Step 1 &rarr;</button>
              <button class="subpage-back-btn" onclick="showChapter('ch2')">Jump to Step 2 &rarr;</button>
            </div>
          </div>
          <p style="margin:0 0 0.5rem 0;font-size:0.86rem;color:#334155;"><strong>Goal:</strong> Prove <strong>What If #1 (Multiplayer)</strong> &amp; <strong>What If #2 (Multi-Model)</strong>. Watch the Step 1 &amp; Step 2 clips (~75s total), have <code>oase-sarah</code> and <code>oase-marcus</code> join the same Scion Grove thread simultaneously, inspect <code>.oase/thresholds.yaml</code> (36 locked schemas), and co-sign <strong>Gate 1</strong>.</p>
          <button class="prompt-chip" style="background:#0f172a;color:#e2e8f0;" onclick="oaseCopyPrompt('@computational-biologist Why did allosteric small-molecule hypothesis IC-001 (1642.5 Elo) outperform cyclic peptide IC-002 (1588.0 Elo) in WO-001, and what caveat must travel forward?')">&#128203; Click to copy Scion prompt: @computational-biologist Why did allosteric small-molecule hypothesis IC-001 (1642.5 Elo) outperform cyclic peptide IC-002 (1588.0 Elo) in WO-001, and what caveat must travel forward?</button>
          <button class="prompt-chip" style="background:#0f172a;color:#e2e8f0;" onclick="oaseCopyPrompt('@computational-biologist Compare PCSK9 hepatocyte expression in GTEx against extrahepatic CNS tissues in WO-002, and explain how gnomAD LoF tolerance supports chronic inhibition safety.')">&#128203; Click to copy Scion prompt: @computational-biologist Compare PCSK9 hepatocyte expression in GTEx against extrahepatic CNS tissues in WO-002, and explain how gnomAD LoF tolerance supports chronic inhibition safety.</button>
          <button class="prompt-chip" style="background:#1e3a8a;color:#e0f2fe;border-color:#38bdf8;" onclick="oaseCopyPrompt('@science-program-lead SUBWAY ROUTING DRILL: Suppose bulk GTEx liver expression had returned 0.4 TPM instead of 184.2 TPM. How would you dynamically re-route the Grove using oase h5ad single-cell data rather than killing the target?')">&harr; Click to copy Dynamic Track-Switch Drill: @science-program-lead Suppose bulk GTEx liver returned 0.4 TPM—how would you dynamically re-route via oase h5ad?</button>
        </div>

        <div class="lab-block">
          <div class="lab-block-hdr">
            <h4>Block 2 (`0:40&ndash;1:10` &middot; 30 min) &mdash; 3D Co-Folding, Cryptic Pockets &amp; Ligand Docking (`Step 3` &middot; `WO-004..005` &middot; Gate 2)</h4>
            <button class="subpage-back-btn" onclick="showChapter('ch3')">Jump to Step 3 &rarr;</button>
          </div>
          <p style="margin:0 0 0.5rem 0;font-size:0.86rem;color:#334155;"><strong>Goal:</strong> Pair GPU structure prediction (<code>AlphaFold 3</code> co-fold <code>ipTM = 0.84</code>) with deterministic cavity &amp; pose tools (<code>fpocket 4.2.2</code> scoring <code>0.68</code> co-fold / <code>0.788</code> live apo vs <code>0.24</code> flat EGF-A; <code>AutoDock Vina 1.2.5</code> at <code>-9.4 kcal/mol</code> seeded / <code>-9.6 kcal/mol</code> live <code>PCSK9-A03</code>). Sign <strong>Gate 2</strong> while logging lipophilicity liability <code>L-002</code> and mandatory caveat <code>docking.score_is_not_affinity</code>.</p>
          <button class="prompt-chip" style="background:#0f172a;color:#e2e8f0;" onclick="oaseCopyPrompt('@structural-biologist Compare cryptic Pocket #1 druggability (0.68 in co-fold / 0.788 apo) against the flat EGF-A PPI interface (0.24) in WO-004. Which residues anchor the groove?')">&#128203; Click to copy Scion prompt: @structural-biologist Compare cryptic Pocket #1 druggability (0.68 in co-fold / 0.788 apo) against the flat EGF-A PPI interface (0.24) in WO-004. Which residues anchor the groove?</button>
        </div>

        <div class="lab-block">
          <div class="lab-block-hdr">
            <h4>Block 3 (`1:10&ndash;1:45` &middot; 35 min, incl. 5m break) &mdash; ADMET Takedown, &#9208; Wet-Lab Stopping Gate &amp; Oral PK (`Steps 4&ndash;5` &middot; `WO-006..008`)</h4>
            <div>
              <button class="subpage-back-btn" onclick="showChapter('ch4')">Jump to Step 4 &rarr;</button>
              <button class="subpage-back-btn" onclick="showChapter('ch5')">Jump to Step 5 &rarr;</button>
            </div>
          </div>
          <p style="margin:0 0 0.5rem 0;font-size:0.86rem;color:#334155;"><strong>Goal:</strong> Walk through the classic med-chem trade-off: top docker <code>PCSK9-A02</code> (<code>cLogP = 5.09</code>, Aronov <code>herg_liability</code>) is disqualified while polar oxadiazole <code>OASE-PCSK9-014</code> (<code>cLogP = 3.01</code>, <code>0</code> critical alerts) clears <strong>Gate 3</strong>. Show how agents hibernate cleanly on disk across the <strong>&#9208; Wet-Lab CRO Stopping Gate</strong> until measured rat (<code>54%</code>) &amp; dog (<code>61%</code>) PK return to project <code>40 mg QD</code> human oral dosing at <strong>Gate 4</strong>.</p>
          <button class="prompt-chip" style="background:#0f172a;color:#e2e8f0;" onclick="oaseCopyPrompt('@medicinal-chemist Walk through the exact RDKit descriptors (cLogP, TPSA, basic amine count) that triggered the Aronov hERG alert on PCSK9-A02 and how OASE-PCSK9-014 resolved L-002.')">&#128203; Click to copy Scion prompt: @medicinal-chemist Walk through the exact RDKit descriptors (cLogP, TPSA, basic amine count) that triggered the Aronov hERG alert on PCSK9-A02 and how OASE-PCSK9-014 resolved L-002.</button>
        </div>

        <div class="lab-block">
          <div class="lab-block-hdr">
            <h4>Block 4 (`1:45&ndash;2:10` &middot; 25 min) &mdash; Red-Team the Validator: Break the Science &amp; Test Overrides (`Step 6`)</h4>
            <button class="subpage-back-btn" onclick="showChapter('ch6')">Jump to Step 6 &rarr;</button>
          </div>
          <p style="margin:0 0 0.5rem 0;font-size:0.86rem;color:#334155;"><strong>Goal:</strong> Deliver the <strong>What If #3 (Cryptographic Governance)</strong> lightbulb moment. Challenge attendees to tamper with raw files, inflate prose metrics, or strip caveats&mdash;and watch <code>oase validate check</code> reject all three before testing an audited human override (<code>DEC-OVERRIDE-001</code>) and <code>&lt;2s</code> chapter reset:</p>
          <div class="terminal"><span class="cmd">$ cp -r checkpoints/ch5 /tmp/redteam-lab &amp;&amp; cd /tmp/redteam-lab</span>
<span class="cmd">$ sed -i 's/-9.4/-9.9/' raw/docking/pcsk9_pocket1_vina.json &amp;&amp; oase validate check WO-005</span>
<span class="err">[FAIL] PROV-002: SHA-256 digest mismatch against pcsk9_pocket1_vina.meta.json (exit=1)</span>

<span class="cmd">$ cp "$OLDPWD/checkpoints/ch5/raw/docking/pcsk9_pocket1_vina.json" raw/docking/pcsk9_pocket1_vina.json</span>
<span class="cmd">$ sed -i 's/-9.4/-11.2/' findings/computational-chemistry/WO-005.md &amp;&amp; oase validate check WO-005</span>
<span class="err">[FAIL] CIT-003: Cited value -11.2 exceeds &plusmn;1% tolerance of $.metrics.pcsk9_analog_02_kcal (-9.4) (exit=1)</span>

<span class="cmd">$ cp "$OLDPWD/checkpoints/ch5/findings/computational-chemistry/WO-005.md" findings/computational-chemistry/WO-005.md</span>
<span class="cmd">$ sed -i '/docking.score_is_not_affinity/d' findings/computational-chemistry/WO-005.md &amp;&amp; oase validate check WO-005</span>
<span class="err">[FAIL] REL-001: Mandatory caveat relay `docking.score_is_not_affinity` omitted from finding (exit=1)</span></div>
        </div>

        <div class="lab-block">
          <div class="lab-block-hdr">
            <h4>Block 5 (`2:10&ndash;2:30` &middot; 20 min) &mdash; Campaign Route Recap, Custom Internal Tools &amp; Deploying in Your Own GCP Environment (`Step 7`)</h4>
            <button class="subpage-back-btn" onclick="jumpToRecapMap()">Open Step 7 Route Recap &rarr;</button>
          </div>
          <p style="margin:0 0 0.5rem 0;font-size:0.86rem;color:#334155;"><strong>Goal:</strong> Walk through the <strong>Interactive Campaign Route Recap Map</strong> in <code>Step 7</code> (showing how <code>pcsk9-oral</code> dynamically routed across 6 stations), tour the compiled 30-page static HTML Evidence Portal (<code>WO-008</code>), review the ~100-line two-phase adapter pattern for internal assays/LIMS tools (<code>oase h5ad</code>), and map a concrete 2-week pilot in the organization's own Google Cloud environment:</p>
          <div class="terminal"><span class="cmd"># 1. Provision isolated GCP project + least-privilege service account</span>
$ python3 scripts/provision-gcp-project.py --project-id &lt;your-pilot-project&gt; --org-id &lt;your-org-id&gt;

<span class="cmd"># 2. Bootstrap OASE v0.3.0 scientific binaries + run full 7-chapter verification</span>
$ OASE_TOOLS_HOME=/scion-volumes/tools ./scripts/bootstrap-oase-env.sh
$ OASE_TOOLS_HOME=/scion-volumes/tools ./scripts/run-e2e-simulation.sh /tmp/sim-pcsk9-oral

<span class="cmd"># 3. Deploy the multi-user Scion Hub + 5-seat Story Arc Cockpit behind Cloud Run IAP</span>
$ ./scripts/deploy-pilot-stack.sh</div>
          <div class="relay-box" style="border-left-color:#10b981;background:#ecfdf5;">
            <strong>Closeout Alignment Questions for the Room:</strong> (1) Which <strong>internal target or hit series</strong> makes the sharpest 2-week validation pilot? (2) Which <strong>1&ndash;2 internal assays or tools</strong> (e.g., scRNA-seq <code>.h5ad</code> atlas, proprietary docking/FEP, or CRO PK sheet) should we wrap first? (3) Who are the <strong>5 discovery pod counterparts</strong> to seat in your pilot Grove?
          </div>
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
  if (history.replaceState) history.replaceState(null, '', window.location.pathname + window.location.search + '#' + ch);
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

window.jumpToRecapMap = function() {
  showChapter('ch7');
  setTimeout(() => {
    const el = document.getElementById('recap-subway-section');
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 100);
};

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
if (hash === 'subway' || hash === 'recap-subway-section') {
  jumpToRecapMap();
} else if (hash && document.getElementById('panel-' + hash)) {
  showChapter(hash);
}

const SUBWAY_STATIONS = {
  s0: {
    title: "Station S0 — Co-Scientist Input Prompt & Modality Split (WO-001)",
    step: "ch1",
    stepLabel: "Open Step 1 Replay & Seed Brief →",
    seedRule: "TPP Preference: Unenhanced oral Rule-of-5 hepatocyte bioavailability + human LoF cardioprotection (coscientist@1.1+program).",
    actual: "Allosteric small molecule IC-001 wins 1642.5 Elo (+54.5 over tricyclic macrocycle IC-002 at 1588.0). Opens Green Line (IC-001) as primary and parks Amber Line (IC-002) as live backup—attaching mandatory relay hypothesis.adopted_not_generated.",
    altTrigger: "What if the input prompt allowed permeation enhancers, or Elo returned a statistical tie (<25 ΔElo)?",
    altAction: "@science-program-lead dispatches parallel Stage 2 structural work orders on BOTH Green (allosteric groove) and Amber (EGF-A macrocycle) lines simultaneously instead of parking IC-002.",
    prompt: "@science-program-lead SUBWAY DRILL: Suppose our Target Product Profile allowed sodium caprate permeation enhancers and IC-001 vs IC-002 tied within 12 Elo points. Which parallel Stage 2 Work Orders would you open?"
  },
  s1: {
    title: "Station S1 — Human Genetics & Tissue Expression Switch (WO-002..003 · Gate 1)",
    step: "ch2",
    stepLabel: "Open Step 2 Genetics Replay →",
    seedRule: "Require human germline LoF tolerance (gnomAD pLI < 0.90) + hepatic expression enrichment (GTEx >= 100 TPM) + AlphaGenome regulatory polarity.",
    actual: "PCSK9 passes Express Track: gnomAD LOF_TOLERANT (pLI = 2.77e-18 live / 0.0001 seeded), GTEx liver = 184.2 TPM (tau = 0.93), and AlphaGenome rs2479409 quantile = 0.984. AI + Human Program Leads co-sign Gate 1.",
    altTrigger: "What if bulk tissue RNA-seq returned near-zero (<5 TPM) because only a rare disease-activated cell state expresses the target?",
    altAction: "A rigid Nextflow DAG drops the gene. OASE switches onto the Blue Single-Cell Detour Loop—spawning an oase h5ad work order to check cell-type-specific expression (distinguishing measured 0 from searched_absent NA) before Gate 1.",
    prompt: "@science-program-lead SUBWAY DRILL: Suppose bulk GTEx liver expression returned 0.4 TPM instead of 184.2 TPM. Show the exact oase h5ad single-cell Work Order you would dispatch before killing the target."
  },
  s2: {
    title: "Station S2 — 3D Co-Folding, Cryptic Groove vs. Flat EGF-A (WO-004..005 · Gate 2)",
    step: "ch3",
    stepLabel: "Open Step 3 Structure & Docking Replay →",
    seedRule: "Pre-registered FP-001: cryptic pocket druggability >= 0.50 & AF3 ipTM >= 0.70; KILL Line A if druggability < 0.30.",
    actual: "Cryptic inter-domain Pocket #1 scores 0.68 (0.788 live apo fpocket; AF3 ipTM = 0.84), while the flat EGF-A PPI patch scores 0.24 (terminating the Ro5 orthosteric spur) and Analog-05 clashes at 1.72 Å (terminated). Green Line advances to Gate 2 carrying liability L-002.",
    altTrigger: "What if cryptic Pocket #1 had collapsed (<0.30 druggability) across all AlphaFold 3 conformers?",
    altAction: "FP-001 kill criterion fires mechanically at Gate 2: OASE terminates Green Line (small molecule) before wasting med-chem synthesis spend and transfers the pod onto Amber Backup Line IC-002 (tricyclic macrocycle / biologic).",
    prompt: "@structural-biologist SUBWAY DRILL: If Pocket #1 had scored 0.22 in fpocket (<0.30 kill criterion FP-001), how would Gate 2 transition the campaign onto backup macrocycle concept IC-002?"
  },
  s3: {
    title: "Station S3 — Active Med-Chem Reroute Around hERG Red Signal (WO-006 · Gate 3)",
    step: "ch4",
    stepLabel: "Open Step 4 ADMET Reroute Replay →",
    seedRule: "Oral Ro5 brief locks max_clogp <= 3.5, TPSA <= 120 Å², and 0 critical PAINS/Brenk/Aronov hERG alerts.",
    actual: "ACTUAL REROUTE IN DEMO: Straight-line top docker PCSK9-A02 (-9.4 kcal/mol) hits a RED SIGNAL (cLogP = 5.09, 3 critical alerts incl. Aronov hERG) and is terminated! Spark-4 routes onto the BRICS Bioisostere Loop, swapping in a polar oxadiazole to rescue OASE-PCSK9-014 (cLogP = 3.01, -9.6 kcal/mol live Vina, 0 alerts).",
    altTrigger: "What if every polar bioisostere lost >2.5 kcal/mol of Pocket #1 binding energy?",
    altAction: "Gate 3 blocks CRO synthesis of the thiazole/oxadiazole series and loops back to Station S2 for an alternate scaffold hop—or escalates to Amber Backup Line IC-002.",
    prompt: "@medicinal-chemist Explain why a naive docking pipeline would have advanced toxic hit PCSK9-A02 (-9.4 kcal/mol) into animal studies, and how the Stage 3 BRICS loop rescued OASE-PCSK9-014."
  },
  s4: {
    title: "Station S4 — ⏸ Wet-Lab CRO Stopping Gate & Human Oral PK (WO-007)",
    step: "ch5",
    stepLabel: "Open Step 5 Oral PK Replay →",
    seedRule: "Manual Wet-Lab Handoff Policy: hibernate Grove on disk until experimental SPR, patch-clamp hERG, and 2-species PK files return.",
    actual: "Agents pause cleanly on disk (zero idle GPU/LLM spend) while CRO-SYN-014 runs. Returned rat (F = 54%) & dog (F = 61%) PK files unlock WO-007, projecting a 40 mg QD human oral tablet (F = 52%, t1/2 = 14.8 h).",
    altTrigger: "What if wet-lab SPR returned KD > 25 µM (docking false positive) or rat oral bioavailability returned F = 3%?",
    altAction: "Phase-2 pk/assay analyze flags FAIL against .oase/thresholds.yaml, blocking Gate 4 nomination and transferring the pod either to a back-up prodrug cycle or onto Amber Line macrocycle PCSK9-B07.",
    prompt: "@admet-dmpk-scientist SUBWAY DRILL: Suppose returned rat oral bioavailability for OASE-PCSK9-014 came back at F = 4% due to first-pass CYP3A4 clearance. What dynamic Work Orders trigger next?"
  },
  s5: {
    title: "Station S5 — Gate 4 Nomination & Audited Macrocycle Override (WO-008 · Steps 6–7)",
    step: "ch6",
    stepLabel: "Open Step 6 Tamper & Override Replay →",
    seedRule: "10-check deterministic validator (PROV, CIT ±1%, REL, THR) + human-co-signed governance overrides (oase workorder override).",
    actual: "OASE-PCSK9-014 passes all 8/8 Work Orders and 28/28 citations for Gate 4 co-sign. In Step 6, Aegis-6 blocks 3 tamper drills while demonstrating how Amber Backup macrocycle PCSK9-B07 (failing default Ro5 MW <= 500) can be promoted ONLY via an explicit, human-signed override (DEC-OVERRIDE-001).",
    altTrigger: "What if a specialist agent tried to silently relax MW <= 500 or drop a caveat without human co-sign?",
    altAction: "oase validate check immediately blocks Work Order closure with THR-001 / REL-001 (exit=1)—preventing silent scope drift against the original Co-Scientist brief.",
    prompt: "@finding-validator Show how DEC-OVERRIDE-001 permits an intentional human beyond-Rule-of-5 exception on backup macrocycle PCSK9-B07 while blocking any unsigned threshold edit."
  }
};

window.selectStation = function(stId) {
  const d = SUBWAY_STATIONS[stId] || SUBWAY_STATIONS.s0;
  document.querySelectorAll('.stn-pill').forEach(el => el.classList.remove('active'));
  const pill = document.getElementById('pill-' + stId);
  if (pill) pill.classList.add('active');
  ['s0','s1','s2','s3','s4','s5'].forEach(k => {
    const c = document.getElementById('svg-stn-' + k);
    if (c) {
      c.setAttribute('r', k === stId ? '18' : '15');
      c.setAttribute('stroke', k === stId ? '#38bdf8' : (k === 's4' ? '#f59e0b' : '#10b981'));
      c.setAttribute('stroke-width', k === stId ? '4.5' : '3.5');
    }
  });
  const box = document.getElementById('subway-inspector');
  if (!box) return;
  const safePrompt = d.prompt.replace(/'/g, "\\'");
  box.innerHTML = `
    <div class="lab-block" style="margin:0;border-left-color:#10b981;">
      <div class="lab-block-hdr">
        <h4 style="color:#065f46;">&#128994; Recorded Trace in <code>pcsk9-oral</code>: ${d.title}</h4>
        <button class="subpage-back-btn" style="background:#059669;" onclick="showChapter('${d.step}')">${d.stepLabel}</button>
      </div>
      <p style="margin:0 0 0.45rem 0;font-size:0.83rem;color:#475569;"><strong>Upstream Seed Rule:</strong> ${d.seedRule}</p>
      <p style="margin:0;font-size:0.87rem;color:#1e293b;line-height:1.48;">${d.actual}</p>
    </div>
    <div class="lab-block" style="margin:0;border-left-color:#2563eb;background:#eff6ff;">
      <div class="lab-block-hdr">
        <h4 style="color:#1e3a8a;">&#128256; Dynamic Subway Switch &mdash; ${d.altTrigger}</h4>
      </div>
      <p style="margin:0 0 0.55rem 0;font-size:0.87rem;color:#1e293b;line-height:1.48;">${d.altAction}</p>
      <button class="prompt-chip" style="background:#0f172a;color:#e2e8f0;margin-top:0.35rem;" onclick="oaseCopyPrompt('${safePrompt}')">&#128203; Test This Branch Live in Scion (Click to Copy): ${d.prompt}</button>
    </div>
  `;
};
selectStation('s3');
</script>

<style id="oase-cockpit-style">
  .cockpit-ControlBar {
    background: #0f172a;
    color: #f8fafc;
    border-bottom: 2px solid #10b981;
    padding: 0.55rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    flex-wrap: wrap;
    font-size: 0.84rem;
  }
  .cockpit-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    background: rgba(16, 185, 129, 0.14);
    color: #6ee7b7;
    border: 1px solid rgba(16, 185, 129, 0.4);
    padding: 0.25rem 0.7rem;
    border-radius: 999px;
    font-family: ui-monospace, monospace;
    font-size: 0.78rem;
    font-weight: 600;
  }
  .cockpit-btn {
    background: #1e293b;
    color: #f8fafc;
    border: 1px solid #475569;
    padding: 0.38rem 0.78rem;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
  }
  .cockpit-btn:hover { background: #334155; border-color: #94a3b8; }
  .cockpit-btn.danger { background: #7f1d1d; border-color: #ef4444; color: #fecaca; }
  .cockpit-btn.danger:hover { background: #991b1b; }
  .cockpit-btn.primary { background: #059669; border-color: #10b981; color: #ffffff; }
  .cockpit-btn.primary:hover { background: #047857; }
  .cockpit-drawer {
    display: none;
    background: #020617;
    color: #e2e8f0;
    padding: 1rem 2rem;
    border-bottom: 2px solid #334155;
  }
  .cockpit-drawer.open { display: block; }
  .cockpit-drawer table th { background: #0f172a; color: #94a3b8; border-bottom: 1px solid #1e293b; }
  .cockpit-drawer table td { border-bottom: 1px solid #1e293b; color: #e2e8f0; font-size: 0.82rem; }
  .cockpit-stage-card {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    color: #f8fafc;
    border-radius: 10px;
    padding: 1.15rem 1.35rem;
    margin-bottom: 1.35rem;
    border: 1px solid #334155;
    box-shadow: 0 6px 20px rgba(15, 23, 42, 0.16);
  }
  .cockpit-video-wrap {
    position: relative;
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid #475569;
    background: #000;
  }
  .cockpit-video-wrap video {
    width: 100%;
    max-height: 600px;
    display: block;
    background: #000;
  }
  .scrub-bar {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-top: 0.75rem;
  }
  .scrub-pill {
    background: rgba(37, 99, 235, 0.22);
    color: #93c5fd;
    border: 1px solid rgba(59, 130, 246, 0.5);
    border-radius: 999px;
    padding: 0.32rem 0.75rem;
    font-size: 0.78rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
  }
  .scrub-pill:hover { background: #2563eb; color: #ffffff; }
  .pause-prove-bar {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    flex-wrap: wrap;
    margin-top: 0.65rem;
    padding: 0.5rem 0.7rem;
    background: rgba(15, 23, 42, 0.68);
    border: 1px solid rgba(56, 189, 248, 0.32);
    border-radius: 8px;
  }
  .pause-prove-lbl {
    font-size: 0.75rem;
    font-weight: 700;
    color: #7dd3fc;
    font-family: ui-monospace, monospace;
    margin-right: 0.2rem;
  }
  .pause-pill {
    background: #1e293b;
    color: #e2e8f0;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 0.26rem 0.62rem;
    font-size: 0.76rem;
    font-weight: 600;
    cursor: pointer;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    transition: all 0.14s;
  }
  .pause-pill:hover { background: #0284c7; border-color: #7dd3fc; color: #ffffff; }
  .staging-pilot-banner {
    background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
    border: 1.5px solid #f59e0b;
    border-radius: 10px;
    padding: 1.15rem 1.35rem;
    margin-bottom: 1.15rem;
    color: #f8fafc;
    box-shadow: 0 6px 20px rgba(15, 23, 42, 0.18);
  }
  .role-bar {
    margin-top: 1rem;
    padding-top: 0.9rem;
    border-top: 1px solid rgba(148, 163, 184, 0.22);
  }
  .role-grid {
    display: flex;
    gap: 0.55rem;
    flex-wrap: wrap;
    margin-top: 0.5rem;
  }
  .role-link {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: #1e293b;
    color: #f8fafc;
    text-decoration: none;
    padding: 0.38rem 0.75rem;
    border-radius: 8px;
    border: 1px solid #475569;
    font-size: 0.8rem;
    font-weight: 600;
    transition: all 0.15s;
  }
  a.role-link:hover { background: #2563eb; border-color: #60a5fa; color: #fff; }
  .role-link.lead { border-color: #10b981; background: rgba(16, 185, 129, 0.18); }
  .role-link img { width: 26px; height: 26px; border-radius: 50%; object-fit: cover; border: 1.5px solid #38bdf8; }
  .prompt-chip {
    background: rgba(15, 23, 42, 0.75);
    border: 1px dashed #475569;
    color: #cbd5e1;
    padding: 0.42rem 0.7rem;
    border-radius: 6px;
    font-family: ui-monospace, monospace;
    font-size: 0.76rem;
    cursor: pointer;
    margin-top: 0.45rem;
    display: block;
    text-align: left;
    width: 100%;
  }
  .prompt-chip:hover { border-color: #38bdf8; color: #ffffff; }
  .wetlab-callout {
    margin-top: 0.9rem;
    background: rgba(245, 158, 11, 0.14);
    border-left: 4px solid #f59e0b;
    padding: 0.7rem 0.95rem;
    border-radius: 0 6px 6px 0;
    color: #fde68a;
    font-size: 0.83rem;
  }
  #cockpit-toast {
    position: fixed;
    bottom: 22px;
    right: 22px;
    background: #059669;
    color: #ffffff;
    padding: 0.7rem 1.1rem;
    border-radius: 8px;
    font-weight: 700;
    font-size: 0.85rem;
    box-shadow: 0 8px 24px rgba(0,0,0,0.35);
    display: none;
    z-index: 99999;
  }
</style>
<div id="cockpit-toast"></div>
<script id="oase-cockpit-script">
(function() {
  const STATIC_VIDEO_MANIFEST = __VIDEO_MANIFEST_JSON__;
  const STATIC_VIDEO_MANIFESTS_BY_CAMPAIGN = __VIDEO_MANIFESTS_BY_CAMPAIGN_JSON__;
  const STATIC_CAMPAIGNS_REGISTRY = __CAMPAIGNS_REGISTRY_JSON__;
  const DEFAULT_PERSONAS = [
    {"key": "sarah", "prefix": "oase-sarah", "name": "Dr. Sarah Chen", "role": "Program Lead", "avatar": "assets/avatars/sarah.jpg"},
    {"key": "marcus", "prefix": "oase-marcus", "name": "Dr. Marcus Vance", "role": "Comp Bio", "avatar": "assets/avatars/marcus.jpg"},
    {"key": "elena", "prefix": "oase-elena", "name": "Dr. Elena Rostova", "role": "Structural Bio", "avatar": "assets/avatars/elena.jpg"},
    {"key": "raj", "prefix": "oase-raj", "name": "Dr. Raj Patel", "role": "Med Chem", "avatar": "assets/avatars/raj.jpg"},
    {"key": "claire", "prefix": "oase-claire", "name": "Dr. Claire Moreau", "role": "DMPK & Safety", "avatar": "assets/avatars/claire.jpg"}
  ];
  const DEFAULT_LEADS = { ch1: "sarah", ch2: "marcus", ch3: "elena", ch4: "raj", ch5: "claire", ch6: "elena", ch7: "sarah" };
  const DEFAULT_PROMPTS = {
    ch1: [
      "@science-program-lead Summarize how our 3 Co-Scientist input prompt clauses in gates/STEP-01-pre-mission-brief.md map into .oase/thresholds.yaml and our 5 Doctor-to-AI Wingman pairings.",
      "@computational-biologist What specific structural liability caused IC-002 to trail IC-001 by 54.5 Elo points in WO-001, and why keep IC-002 parked on the Amber backup line?"
    ],
    ch2: [
      "@computational-biologist Compare our PCSK9 hepatocyte TPM in GTEx against extrahepatic CNS tissues in WO-002.",
      "@science-program-lead Why must alphagenome.quantile_not_clinical_effect stay attached after Stage Gate 1?"
    ],
    ch3: [
      "@structural-biologist Compare cryptic Pocket #1 druggability (0.68) against the flat EGF-A PPI surface (0.24) in WO-004.",
      "@science-program-lead Which chemical liability on PCSK9-A02 (-9.4 kcal/mol) requires MMP triage in Step 4?"
    ],
    ch4: [
      "@medicinal-chemist Explain how the 1,2,4-oxadiazole swap in OASE-PCSK9-014 resolved the Aronov hERG alert from PCSK9-A02.",
      "@admet-dmpk-scientist List the exact experimental CRO assays required at the Gate 3 Wet-Lab handoff before Step 5 unlocks."
    ],
    ch5: [
      "@admet-dmpk-scientist How does OASE-PCSK9-014 (40 mg QD oral tablet, F=52%) compare against macrocyclic PCSK9 comparators?",
      "@science-program-lead Confirm all 8 Work Orders and risk relays verified in executive/CANDIDATE-SUMMARY.md."
    ],
    ch6: [
      "@finding-validator Which exact rule blocked Drill 2 when docking.score_not_affinity was omitted from the finding?",
      "@science-program-lead Show the audit record for the PCSK9-B07 Lipinski MW override in .oase/control/events.ndjson."
    ],
    ch7: [
      "@science-program-lead Walk through our 5 Doctor-to-AI Wingman post-mission debrief outcomes in gates/STEP-07-portfolio-closeout.md and executive/PORTFOLIO-HANDOFF.md.",
      "@project-curator Which dynamic Subway Map detours and CRO wet-lab receipts were decisive in nominating OASE-PCSK9-014 (40 mg oral QD)?"
    ]
  };

  function resolveInitialCampaign() {
    const q = new URLSearchParams(window.location.search).get('campaign');
    const list = (STATIC_CAMPAIGNS_REGISTRY && STATIC_CAMPAIGNS_REGISTRY.campaigns) || [];
    if (q && list.some(c => c.id === q)) return q;
    return (STATIC_CAMPAIGNS_REGISTRY && STATIC_CAMPAIGNS_REGISTRY.default_campaign) || 'pcsk9-pilot-v1';
  }

  let activeCampaignId = resolveInitialCampaign();

  function getCampaignObj(registry, cid) {
    const reg = registry || STATIC_CAMPAIGNS_REGISTRY || {};
    const list = reg.campaigns || [];
    return list.find(c => c.id === cid) || list[0] || { id: 'pcsk9-pilot-v1', short_label: 'PCSK9 Oral · Reference Pilot (v1)', status: 'ready', badge: 'LIVE · 8 GROVES' };
  }

  function showToast(msg, isErr) {
    const t = document.getElementById('cockpit-toast');
    if (!t) return;
    t.style.background = isErr ? '#dc2626' : '#059669';
    t.textContent = msg;
    t.style.display = 'block';
    setTimeout(() => { t.style.display = 'none'; }, 4200);
  }

  window.oaseToggleCampaignMenu = function(ev) {
    if (ev) ev.stopPropagation();
    const m = document.getElementById('oase-campaign-menu');
    if (m) m.classList.toggle('open');
  };

  document.addEventListener('click', (ev) => {
    const wrap = document.getElementById('oase-campaign-switcher');
    const menu = document.getElementById('oase-campaign-menu');
    if (menu && wrap && !wrap.contains(ev.target)) {
      menu.classList.remove('open');
    }
  });

  window.oaseSelectCampaign = async function(cid) {
    activeCampaignId = cid;
    const menu = document.getElementById('oase-campaign-menu');
    if (menu) menu.classList.remove('open');
    if (history.replaceState) {
      const u = new URL(window.location.href);
      u.searchParams.set('campaign', cid);
      history.replaceState(null, '', u.pathname + u.search + u.hash);
    }
    // Pause any playing video and clear dynamic stage cards before re-rendering for the selected pilot
    document.querySelectorAll('video').forEach(v => { try { v.pause(); } catch (_) {} });
    const fw = document.getElementById('cockpit-full-walkthrough-card');
    if (fw) fw.remove();
    const sb = document.getElementById('oase-staging-banner');
    if (sb) sb.remove();
    ['ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7'].forEach(chId => {
      const c = document.getElementById('cockpit-card-' + chId);
      if (c) c.remove();
    });
    await refreshCockpit();
    const camp = getCampaignObj(null, cid);
    showToast('Switched Scion Pilot to: ' + camp.short_label);
  };

  window.oasePauseVideoOnly = function(chId) {
    const v = document.getElementById('video-' + chId);
    if (v) { try { v.pause(); } catch (_) {} }
  };

  window.oasePauseAndInspect = function(chId, href, mode) {
    window.oasePauseVideoOnly(chId);
    if (mode === 'subpage' && typeof openSubpage === 'function') {
      openSubpage(href);
      showToast('Video paused · Inspecting ' + href);
    } else if (href) {
      window.open(href, '_blank', 'noopener');
    }
  };

  function renderCampaignChrome(registry, cid) {
    const reg = registry || STATIC_CAMPAIGNS_REGISTRY || {};
    const list = reg.campaigns || [];
    const active = getCampaignObj(reg, cid);

    const lbl = document.getElementById('oase-campaign-btn-label');
    if (lbl) lbl.textContent = active.short_label || active.id;
    const bdg = document.getElementById('oase-campaign-btn-badge');
    if (bdg) {
      bdg.textContent = active.badge || (active.status === 'ready' ? 'READY' : 'STAGING');
      bdg.className = 'pilot-badge-pill ' + (active.status === 'ready' ? 'ready' : 'staging');
    }
    const heroTag = document.getElementById('hero-active-pilot-line');
    if (heroTag) {
      heroTag.textContent = `Active Scion Pilot: ${active.short_label} — ${active.target || ''}`;
    }
    const kpiStrip = document.getElementById('hero-kpi-strip');
    if (kpiStrip && Array.isArray(active.kpis) && active.kpis.length > 0) {
      kpiStrip.innerHTML = active.kpis.map(k =>
        `<div class="kpi-card"><div class="kpi-val">${k.val}</div><div class="kpi-lbl">${k.lbl}</div></div>`
      ).join('');
    }
    const menu = document.getElementById('oase-campaign-menu');
    if (menu) {
      const itemsHtml = list.map(c => {
        const isAct = c.id === active.id;
        const bCls = c.status === 'ready' ? 'ready' : 'staging';
        return `
          <button type="button" class="pilot-menu-item ${isAct ? 'active' : ''}" onclick="oaseSelectCampaign('${c.id}')">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:0.5rem;">
              <strong style="font-size:0.86rem;color:#ffffff;">${isAct ? '✓ ' : ''}${c.short_label}</strong>
              <span class="pilot-badge-pill ${bCls}">${c.badge || c.status.toUpperCase()}</span>
            </div>
            <div style="font-size:0.77rem;color:#93c5fd;margin-top:0.2rem;">${c.target || ''}</div>
            <div style="font-size:0.74rem;color:#cbd5e1;margin-top:0.15rem;line-height:1.35;">${c.stack_summary || ''}</div>
          </button>
        `;
      }).join('');
      menu.innerHTML = `
        <div class="pilot-menu-hdr">Scion Campaign / Pilot Workspaces (${list.length})</div>
        ${itemsHtml}
        <div class="pilot-menu-ftr">Isolated Grove DBs, Git tags, 1080p reels &amp; SHA-256 receipts (?campaign=&lt;id&gt;)</div>
      `;
    }
    return active;
  }

  window.oaseSeekVideo = function(chId, sec) {
    const v = document.getElementById('video-' + chId);
    if (!v) return;
    v.currentTime = sec;
    v.play().catch(() => {});
  };

  window.oaseCopyPrompt = function(txt) {
    navigator.clipboard.writeText(txt).then(() => {
      showToast('Copied follow-up prompt to clipboard!');
    });
  };

  window.oaseResetChapter = async function(chId) {
    showToast('Resetting ' + chId.toUpperCase() + ' Grove + Scion SQLite (' + activeCampaignId + ')...');
    try {
      const r = await fetch('/api/state/chapters/' + chId + '/reset?campaign=' + encodeURIComponent(activeCampaignId), { method: 'POST' });
      const d = await r.json();
      if (!r.ok || !d.ok) throw new Error(d.detail || 'Reset failed');
      showToast('Reset ' + chId.toUpperCase() + ' complete in ' + d.duration_ms + ' ms (commit ' + d.git_commit + ')!');
      await refreshCockpit();
    } catch (e) {
      showToast('Reset error: ' + e.message, true);
    }
  };

  window.oaseResetAll = async function() {
    showToast('Resetting all chapters to Golden Snapshot (' + activeCampaignId + ')...');
    try {
      const r = await fetch('/api/state/reset-all?campaign=' + encodeURIComponent(activeCampaignId), { method: 'POST' });
      const d = await r.json();
      if (!r.ok || !d.ok) throw new Error(d.detail || 'Reset-all failed');
      showToast('Reset all ' + d.chapters_reset + ' chapters to t=0 / Golden State in ' + d.duration_ms + ' ms!');
      await refreshCockpit();
    } catch (e) {
      showToast('Reset-all error: ' + e.message, true);
    }
  };

  window.oaseToggleDrawer = function() {
    const dr = document.getElementById('oase-facilitator-drawer');
    if (dr) dr.classList.toggle('open');
  };

  function buildTopBar(cfg, isLive, activeCamp) {
    let bar = document.getElementById('oase-cockpit-topbar');
    if (!bar) {
      bar = document.createElement('div');
      bar.id = 'oase-cockpit-topbar';
      bar.className = 'cockpit-ControlBar';
      const dr = document.createElement('div');
      dr.id = 'oase-facilitator-drawer';
      dr.className = 'cockpit-drawer';
      const nav = document.querySelector('nav');
      if (nav && nav.parentNode) {
        nav.parentNode.insertBefore(dr, nav.nextSibling);
        nav.parentNode.insertBefore(bar, dr);
      }
    }
    const isStaging = activeCamp && activeCamp.status !== 'ready';
    if (!isLive) {
      bar.innerHTML = `
        <div style="display:flex;align-items:center;gap:0.75rem;flex-wrap:wrap;">
          <span class="cockpit-status-pill">${isStaging ? '⚡ Staging Pilot Workspace · Queued for Live Sovereign GPU Run' : '● Public Replay Preview · 7 Recorded Squadron Chapters Ready (1080p)'}</span>
          <span style="color:#94a3b8;font-family:monospace;font-size:0.78rem;">${activeCamp ? activeCamp.short_label : 'Native Gemini 3.8 Live Avatars + 6 Specialist AI Wingmen'}</span>
        </div>
        <div style="display:flex;align-items:center;gap:0.55rem;flex-wrap:wrap;">
          ${isStaging ? `<button class="cockpit-btn primary" onclick="oaseSelectCampaign('pcsk9-pilot-v1')">← Switch to Reference Pilot (v1 · Ready)</button>` : `<span style="color:#94a3b8;font-size:0.78rem;">Live 5-Persona Scion Grove &amp; &lt;2s Reset Active on Cloud Run Cockpit</span>`}
        </div>
      `;
      return;
    }

    const st = cfg.state || {};
    const chCount = Object.keys(st.chapters || {}).length;
    const statusText = isStaging
      ? `⚡ Staging Pilot (${activeCamp.nav_slug || activeCamp.id}) · Provisioned & Ready for Live Run`
      : (st.ok
          ? `● Live Grove Connected (${activeCamp.nav_slug || activeCamp.id}) · ${chCount} Chapters Ready · Admin Leaks: ${st.admin_rows_count ?? 0}`
          : `● Static Replay Mode (State Controller unreachable)`);

    const ch0 = (st.chapters || {}).ch0;
    const ch0Url = (cfg.scion_hub_url && ch0 && cfg.workshop_domain)
      ? `${cfg.scion_hub_url}/chat/${ch0.slug}/${ch0.general_topic_id}?authuser=oase-sarah@${cfg.workshop_domain}`
      : '#';

    bar.innerHTML = `
      <div style="display:flex;align-items:center;gap:0.75rem;flex-wrap:wrap;">
        <span class="cockpit-status-pill">${statusText}</span>
        ${cfg.signed_in_user ? `<span style="color:#94a3b8;font-family:monospace;font-size:0.78rem;">Signed in: <strong style="color:#fff;">${cfg.signed_in_user}</strong></span>` : ''}
      </div>
      <div style="display:flex;align-items:center;gap:0.55rem;flex-wrap:wrap;">
        ${isStaging ? `<button class="cockpit-btn primary" onclick="oaseSelectCampaign('pcsk9-pilot-v1')">← Return to Reference Pilot (v1)</button>` : ''}
        ${(!isStaging && ch0Url !== '#') ? `<a class="cockpit-btn primary" href="${ch0Url}" target="_blank" rel="noopener" style="text-decoration:none;">🧪 Launch Fresh Sandbox (ch0 · t=0) ↗</a>` : ''}
        ${!isStaging ? `<button class="cockpit-btn" onclick="oaseToggleDrawer()">⚙ Facilitator Reset Drawer</button>` : ''}
        ${!isStaging ? `<button class="cockpit-btn danger" onclick="oaseResetAll()">↺ Reset Entire Demo (t=0)</button>` : ''}
      </div>
    `;

    const dr = document.getElementById('oase-facilitator-drawer');
    if (dr && st.chapters && !isStaging) {
      const rows = Object.values(st.chapters).map(c => `
        <tr>
          <td><strong>${c.chapter.toUpperCase()}</strong></td>
          <td><code>${c.slug}</code></td>
          <td><code>${c.active_git_tag}</code> (<code>${c.git_commit}</code>)</td>
          <td>${c.message_count} msgs · ${c.artifact_count} artifacts</td>
          <td><code>${(c.running_agents || []).join(', ')}</code></td>
          <td>${c.last_reset_duration_ms ? c.last_reset_duration_ms + ' ms' : 'Golden'}</td>
          <td><button class="cockpit-btn" onclick="oaseResetChapter('${c.chapter}')">↺ Reset ${c.chapter.toUpperCase()}</button></td>
        </tr>
      `).join('');
      dr.innerHTML = `
        <div style="max-width:1320px;margin:0 auto;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.6rem;">
            <strong>Facilitator Live Chapter &amp; SQLite Snapshot Controller (Sub-2s Non-Disruptive Reset)</strong>
            <span style="color:#94a3b8;font-size:0.78rem;">Golden Snapshot: ${st.golden_snapshot_updated_at || 'Active'} · Preserves all 5 Chrome sessions</span>
          </div>
          <table>
            <thead><tr><th>Stage</th><th>Scion Project</th><th>Git Tag</th><th>Hub DB State</th><th>Live Specialist Containers</th><th>Last Reset</th><th>Action</th></tr></thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
      `;
    } else if (dr) {
      dr.classList.remove('open');
    }
  }

  function renderPauseLinksHtml(activeCamp, chId) {
    const links = (activeCamp && activeCamp.pause_links && activeCamp.pause_links[chId]) || [];
    if (!links.length) return '';
    const pills = links.map(lnk => {
      if (lnk.mode === 'subpage') {
        return `<button type="button" class="pause-pill" onclick="oasePauseAndInspect('${chId}', '${lnk.href}', 'subpage')">${lnk.label}</button>`;
      }
      return `<a class="pause-pill" href="${lnk.href}" target="_blank" rel="noopener" onclick="oasePauseVideoOnly('${chId}')">${lnk.label} ↗</a>`;
    }).join('');
    return `
      <div class="pause-prove-bar">
        <span class="pause-prove-lbl">⏸ Pause &amp; Inspect Same Artifacts:</span>
        ${pills}
      </div>
    `;
  }

  function injectChapterCards(cfg, isLive, activeCamp) {
    const isStaging = activeCamp && activeCamp.status !== 'ready';
    const whyPanel = document.getElementById('panel-why');

    if (isStaging) {
      if (whyPanel && !document.getElementById('oase-staging-banner')) {
        const sb = document.createElement('div');
        sb.id = 'oase-staging-banner';
        sb.className = 'staging-pilot-banner';
        const surfaces = (activeCamp.planned_surfaces || []).map(s => `<li style="margin-bottom:0.28rem;">${s}</li>`).join('');
        sb.innerHTML = `
          <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;flex-wrap:wrap;">
            <div>
              <span class="pilot-badge-pill staging" style="margin-bottom:0.4rem;display:inline-block;">⚡ STAGING PILOT WORKSPACE · NEXT LIVE EXECUTION</span>
              <h3 style="margin:0.2rem 0 0.35rem 0;color:#ffffff;font-size:1.08rem;">${activeCamp.title}</h3>
              <p style="margin:0;color:#cbd5e1;font-size:0.85rem;">${activeCamp.stack_summary || ''}</p>
            </div>
            <button class="cockpit-btn primary" onclick="oaseSelectCampaign('pcsk9-pilot-v1')">← View Completed Reference Pilot (v1) →</button>
          </div>
          <ul style="margin:0.75rem 0 0 1.2rem;padding:0;font-size:0.82rem;color:#e2e8f0;line-height:1.45;">${surfaces}</ul>
        `;
        const whatifHero = document.getElementById('whatif-hero');
        if (whatifHero && whatifHero.parentNode) {
          whatifHero.parentNode.insertBefore(sb, whatifHero);
        }
      }
      ['ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7'].forEach(chId => {
        const panel = document.getElementById('panel-' + chId);
        if (!panel || document.getElementById('cockpit-card-' + chId)) return;
        const card = document.createElement('div');
        card.id = 'cockpit-card-' + chId;
        card.className = 'cockpit-stage-card';
        card.innerHTML = `
          <div style="display:flex;justify-content:space-between;align-items:center;gap:0.75rem;flex-wrap:wrap;">
            <div>
              <span class="pilot-badge-pill staging">⚡ STAGING · ${chId.toUpperCase()}</span>
              <strong style="font-size:0.98rem;color:#fcd34d;margin-left:0.45rem;">${activeCamp.short_label} — Live Run Slot Ready</strong>
              <div style="font-size:0.81rem;color:#cbd5e1;margin-top:0.3rem;">
                This isolated campaign slot will capture unscripted Scion Grove messages, dedicated Vertex AI GPU telemetry, interactive 3D/genomics viewers, and Flight-Recorder logs during the live run.
              </div>
            </div>
            <button class="cockpit-btn primary" onclick="oaseSelectCampaign('pcsk9-pilot-v1')">← Open Reference Pilot (v1) Video &amp; Grove</button>
          </div>
          ${renderPauseLinksHtml(activeCamp, chId)}
        `;
        const hdr = panel.querySelector('.chapter-header');
        if (hdr && hdr.nextSibling) panel.insertBefore(card, hdr.nextSibling);
        else panel.prepend(card);
      });
      return;
    }

    const cid = (activeCamp && activeCamp.id) || 'pcsk9-live-argolis';
    const manifest = (cfg && cfg.videos) || (STATIC_VIDEO_MANIFESTS_BY_CAMPAIGN && STATIC_VIDEO_MANIFESTS_BY_CAMPAIGN[cid]) || STATIC_VIDEO_MANIFEST || {};
    const videos = manifest.chapters || {};
    const fullVideo = manifest.full_walkthrough;
    const stChapters = (cfg && cfg.state && cfg.state.chapters) || {};
    const personas = (cfg && cfg.personas) || DEFAULT_PERSONAS;
    const promptsMap = (cfg && cfg.followup_prompts) || DEFAULT_PROMPTS;
    const staticPrefix = ((activeCamp && activeCamp.static_video_prefix) || 'assets/videos').replace(/\/?$/, '/');
    const videoBase = isLive
      ? (cid === 'pcsk9-pilot-v1' ? '/api/videos/' : `/api/videos/${encodeURIComponent(cid)}/`)
      : staticPrefix;

    if (fullVideo && !document.getElementById('cockpit-full-walkthrough-card')) {
      if (whyPanel) {
        const fwCard = document.createElement('div');
        fwCard.id = 'cockpit-full-walkthrough-card';
        fwCard.className = 'cockpit-stage-card';
        const durMin = fullVideo.duration_s ? (fullVideo.duration_s / 60).toFixed(1) + ' min' : '7 Chapters';
        const fwFile = fullVideo.video_filename || 'full-pilot-walkthrough.mp4';
        const fwVer = fullVideo.duration_s || '474';
        const fwSrc = `${videoBase}${fwFile}?v=${fwVer}`;
        fwCard.innerHTML = `
          <div style="display:flex;justify-content:space-between;align-items:center;gap:0.75rem;flex-wrap:wrap;margin-bottom:0.55rem;">
            <div>
              <strong style="color:#38bdf8;font-size:0.98rem;">🎬 Interactive 7-Chapter Squadron Walkthrough (${durMin} Total · 1080p)</strong>
              <div style="color:#cbd5e1;font-size:0.81rem;margin-top:0.2rem;">
                Bookended by a full-pod <strong>Step 1 Pre-Mission Brief</strong> (Co-Scientist prompt co-design + Doctor &harr; Wingman pairings) and <strong>Step 7 Post-Mission Debrief</strong>, with live SHA-256 artifacts below every step.
              </div>
            </div>
            <div style="display:flex;gap:0.5rem;flex-wrap:wrap;">
              <button class="cockpit-btn primary" onclick="showChapter('ch1')">▶ Jump to Step 1 Video →</button>
            </div>
          </div>
          <details>
            <summary style="cursor:pointer;font-weight:700;color:#93c5fd;font-size:0.88rem;">
              ▶ Or expand continuous ${durMin} full-campaign video reel right here (Steps 1–7 back-to-back)
            </summary>
            <div class="cockpit-video-wrap" style="margin-top:0.8rem;">
              <video id="video-full" controls preload="none" src="${fwSrc}"></video>
            </div>
          </details>
        `;
        const whatifHero = document.getElementById('whatif-hero');
        const hdr = whyPanel.querySelector('.chapter-header');
        if (whatifHero && whatifHero.parentNode) {
          whatifHero.parentNode.insertBefore(fwCard, whatifHero.nextSibling);
        } else if (hdr && hdr.nextSibling) {
          whyPanel.insertBefore(fwCard, hdr.nextSibling);
        }
      }
    }

    ['ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7'].forEach(chId => {
      const panel = document.getElementById('panel-' + chId);
      if (!panel) return;
      const vmeta = videos[chId];
      const cstate = stChapters[chId] || {};
      const leadKey = cstate.lead_human || DEFAULT_LEADS[chId] || 'sarah';
      let card = document.getElementById('cockpit-card-' + chId);
      const isNew = !card;
      if (isNew) {
        card = document.createElement('div');
        card.id = 'cockpit-card-' + chId;
        card.className = 'cockpit-stage-card';
        const hdr = panel.querySelector('.chapter-header');
        if (hdr && hdr.nextSibling) {
          panel.insertBefore(card, hdr.nextSibling);
        } else {
          panel.prepend(card);
        }
      } else {
        const badge = document.getElementById('cockpit-state-badge-' + chId);
        if (badge && cstate.git_commit) {
          badge.textContent = `Live Project: ${cstate.slug} · Git ${cstate.git_commit} · ${cstate.message_count} Webchat msgs · ${(cstate.running_agents || []).length} live containers`;
        }
        return;
      }

      const markersHtml = vmeta && vmeta.markers
        ? vmeta.markers.map(m =>
            `<button class="scrub-pill" onclick="oaseSeekVideo('${chId}', ${m.time_s})">▶ ${m.label} (${m.timecode}) · ${m.speaker}</button>`
          ).join('')
        : '';

      const pauseBarHtml = renderPauseLinksHtml(activeCamp, chId);

      const rolesHtml = personas.map(p => {
        const isLead = p.key === leadKey;
        if (isLive) {
          const email = cfg.workshop_domain ? `${p.prefix}@${cfg.workshop_domain}` : '';
          const liveHref = (cfg.scion_hub_url && cstate.slug && cstate.general_topic_id && email)
            ? `${cfg.scion_hub_url}/chat/${cstate.slug}/${cstate.general_topic_id}?authuser=${encodeURIComponent(email)}`
            : (cfg.scion_hub_url ? `${cfg.scion_hub_url}/chat` : '#');
          return `
            <a class="role-link ${isLead ? 'lead' : ''}" href="${liveHref}" target="_blank" rel="noopener" onclick="oasePauseVideoOnly('${chId}')">
              <img src="${p.avatar}" alt="${p.name}">
              <span>${p.name} <small style="color:#94a3b8;">(${p.role}${isLead ? ' · LEAD' : ''})</small></span>
            </a>
          `;
        }
        return `
          <span class="role-link ${isLead ? 'lead' : ''}" title="Deploy or open the Cloud Run Story Arc Cockpit to jump live into Scion Hub as ${p.name}">
            <img src="${p.avatar}" alt="${p.name}">
            <span>${p.name} <small style="color:#94a3b8;">(${p.role}${isLead ? ' · LEAD' : ''})</small></span>
          </span>
        `;
      }).join('');

      const promptsHtml = (promptsMap[chId] || []).map(pr =>
        `<button class="prompt-chip" onclick='oaseCopyPrompt(${JSON.stringify(pr)})'>📋 Copy Live Follow-Up Prompt: "${pr}"</button>`
      ).join('');

      const wetlabHtml = chId === 'ch4'
        ? `<div class="wetlab-callout"><strong>⏸ Explicit Future-State Wet-Lab / CRO Assay Handoff Slot:</strong> Campaign pauses on disk at <code>WO-006</code> (<code>gates/GATE-03-wetlab-handoff.md</code>) after disqualifying <code>PCSK9-A02</code> on cardiac hERG—awaiting experimental SPR <code>K<sub>D</sub></code>, manual patch-clamp hERG (<code>&gt;30 µM</code>), and rat/dog cassette PK before <code>WO-007</code> unlocks.</div>`
        : '';

      const videoFilename = vmeta ? vmeta.video_filename : `chapter-0${chId.slice(2)}.mp4`;
      const videoVer = vmeta && vmeta.duration_s ? vmeta.duration_s : '38';
      const videoSrc = `${videoBase}${videoFilename}?v=${videoVer}`;
      const subBadge = isLive && cstate.slug
        ? `Live Project: ${cstate.slug} · Git ${cstate.git_commit} · ${cstate.message_count} Webchat msgs · ${(cstate.running_agents || []).length} live containers`
        : `Scion Grove Checkpoint: ${(vmeta && vmeta.slug) || chId} · ${vmeta && vmeta.duration_s ? vmeta.duration_s + 's' : '1080p'} · 5 Live Avatars + 6 AI Wingmen`;
      const resetBtnHtml = isLive
        ? `<button class="cockpit-btn" onclick="oaseResetChapter('${chId}')">↺ Reset ${chId.toUpperCase()} (&lt;2s)</button>`
        : '';
      const roleHeader = isLive
        ? `🚀 Pause &amp; Join Live Scion Grove As Any of the 5 Discovery Pod Scientists (Zero Admin Noise):`
        : `👩‍🔬 5-Scientist Human Discovery Pod Roster &amp; Follow-Up Q&amp;A Prompts (Live Webchat Active on Cloud Run):`;

      card.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;margin-bottom:0.75rem;">
          <div>
            <strong style="font-size:1rem;color:#38bdf8;">🎬 Recorded Multi-Human + Multi-Agent Scion Walkthrough (1080p · Native Gemini 3.8 Live Avatars + Multi-Model Grove)</strong>
            <div id="cockpit-state-badge-${chId}" style="font-size:0.77rem;color:#94a3b8;font-family:monospace;margin-top:0.15rem;">
              ${subBadge}
            </div>
          </div>
          ${resetBtnHtml}
        </div>
        <div class="cockpit-video-wrap">
          <video id="video-${chId}" controls preload="metadata" src="${videoSrc}"></video>
        </div>
        <div class="scrub-bar">${markersHtml}</div>
        ${pauseBarHtml}
        ${wetlabHtml}
        <div class="role-bar">
          <div style="font-size:0.83rem;font-weight:700;color:#e2e8f0;">${roleHeader}</div>
          <div style="font-size:0.75rem;color:#94a3b8;margin-top:0.15rem;">Note: Inside Scion Webchat, the right-hand <code>PEOPLE — 4</code> list displays your 4 co-pilots alphabetically while your active signed-in seat appears under <code>Profile</code>.</div>
          <div class="role-grid">${rolesHtml}</div>
          <div style="margin-top:0.55rem;">${promptsHtml}</div>
        </div>
      `;
    });
  }

  async function refreshCockpit() {
    try {
      const r = await fetch('/api/cockpit/config?campaign=' + encodeURIComponent(activeCampaignId), { cache: 'no-store' });
      if (r.ok) {
        const cfg = await r.json();
        const activeCamp = renderCampaignChrome(cfg.campaigns_registry || STATIC_CAMPAIGNS_REGISTRY, cfg.active_campaign || activeCampaignId);
        buildTopBar(cfg, true, activeCamp);
        injectChapterCards(cfg, true, activeCamp);
        return;
      }
    } catch (_) {}
    const activeCamp = renderCampaignChrome(STATIC_CAMPAIGNS_REGISTRY, activeCampaignId);
    buildTopBar(null, false, activeCamp);
    injectChapterCards(null, false, activeCamp);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', refreshCockpit);
  } else {
    refreshCockpit();
  }
})();
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
    import html as html_lib
    import json
    import re

    repo_root = pathlib.Path(__file__).resolve().parent.parent
    plan_md_path = repo_root / "docs" / "PILOT_IMPLEMENTATION_PLAN.md"
    if plan_md_path.is_file():
        plan_md = plan_md_path.read_text(encoding="utf-8")
        done_cnt = len(re.findall(r"`\[x\]\s*Complete`", plan_md))
        total_cnt = len(re.findall(r"\|\s*\*\*M\d+\*\*\s*\|", plan_md)) or 6
        pct = int(round((done_cnt / total_cnt) * 100))

        def _fmt_inline(s: str) -> str:
            s = html_lib.escape(s)
            s = re.sub(r"^\[x\]\s*", '<span class="pass-pill">✓</span> ', s)
            s = re.sub(r"^\[\s*\]\s*", '<span class="warn-pill">☐</span> ', s)
            s = re.sub(r"`\[x\]\s*Complete`", '<span class="pass-pill">✓ Complete</span>', s)
            s = re.sub(r"`\[\s*\]\s*Next Up`", '<span class="stage-pill">→ Next Up</span>', s)
            s = re.sub(r"`\[\s*\]\s*In Progress`", '<span class="stage-pill">⟳ In Progress</span>', s)
            s = re.sub(r"`\[\s*\]\s*Pending`", '<span class="warn-pill">Pending</span>', s)
            s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
            s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
            s = re.sub(r"`([^`]+)`", r"<code style='background:#f1f5f9;padding:0.12rem 0.35rem;border-radius:4px;font-size:0.84em;'>\1</code>", s)
            return s

        lines = plan_md.splitlines()
        out_blocks: list[str] = []
        in_code = False
        code_buf: list[str] = []
        in_table = False
        table_rows: list[list[str]] = []
        in_list = False
        list_tag = "ul"

        def _flush_table() -> None:
            nonlocal in_table, table_rows
            if not in_table or not table_rows:
                in_table = False
                table_rows = []
                return
            t_html = ["<table><thead><tr>"]
            for cell in table_rows[0]:
                t_html.append(f"<th>{_fmt_inline(cell)}</th>")
            t_html.append("</tr></thead><tbody>")
            for row in table_rows[1:]:
                if all(set(c.strip()) <= set(":-") for c in row):
                    continue
                t_html.append("<tr>" + "".join(f"<td>{_fmt_inline(c)}</td>" for c in row) + "</tr>")
            t_html.append("</tbody></table>")
            out_blocks.append("".join(t_html))
            in_table = False
            table_rows = []

        def _flush_list() -> None:
            nonlocal in_list
            if in_list:
                out_blocks.append(f"</{list_tag}>")
                in_list = False

        for ln in lines:
            if ln.startswith("```"):
                _flush_table()
                _flush_list()
                if not in_code:
                    in_code = True
                    code_buf = []
                else:
                    in_code = False
                    out_blocks.append("<pre class='terminal'>" + html_lib.escape("\n".join(code_buf)) + "</pre>")
                continue
            if in_code:
                code_buf.append(ln)
                continue
            if ln.strip().startswith("|") and ln.strip().endswith("|"):
                _flush_list()
                in_table = True
                cells = [c.strip() for c in ln.strip()[1:-1].split("|")]
                table_rows.append(cells)
                continue
            else:
                _flush_table()

            stripped = ln.strip()
            if not stripped:
                _flush_list()
                continue
            if stripped == "---":
                _flush_list()
                out_blocks.append("<hr style='border:none;border-top:1px solid #e2e8f0;margin:1.5rem 0;'/>")
                continue
            if stripped.startswith("# "):
                _flush_list()
                continue  # rendered in hero
            if stripped.startswith("## "):
                _flush_list()
                out_blocks.append(f"<h2 style='color:#0f172a;border-bottom:2px solid #e2e8f0;padding-bottom:0.45rem;margin-top:1.6rem;'>{_fmt_inline(stripped[3:])}</h2>")
                continue
            if stripped.startswith("### "):
                _flush_list()
                out_blocks.append(f"<h3 style='color:#1e3a8a;margin-top:1.2rem;'>{_fmt_inline(stripped[4:])}</h3>")
                continue
            if stripped.startswith("> "):
                _flush_list()
                out_blocks.append(f"<div class='relay-box' style='border-left-color:#2563eb;background:#eff6ff;'>{_fmt_inline(stripped[2:])}</div>")
                continue
            m_ul = re.match(r"^[-*]\s+(.*)$", stripped)
            m_ol = re.match(r"^\d+\.\s+(.*)$", stripped)
            if m_ul:
                if not in_list or list_tag != "ul":
                    _flush_list()
                    in_list = True
                    list_tag = "ul"
                    out_blocks.append("<ul style='line-height:1.6;color:#334155;'>")
                out_blocks.append(f"<li>{_fmt_inline(m_ul.group(1))}</li>")
                continue
            if m_ol:
                if not in_list or list_tag != "ol":
                    _flush_list()
                    in_list = True
                    list_tag = "ol"
                    out_blocks.append("<ol style='line-height:1.6;color:#334155;'>")
                out_blocks.append(f"<li>{_fmt_inline(m_ol.group(1))}</li>")
                continue
            _flush_list()
            out_blocks.append(f"<p style='line-height:1.6;color:#334155;'>{_fmt_inline(stripped)}</p>")

        _flush_table()
        _flush_list()

        plan_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow" />
<meta name="googlebot" content="noindex, nofollow" />
<title>Pilot Vision, Architecture &amp; Live Build Tracker — GCP-OASE</title>
<style>
  body {{ font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 0; color: #1a1a1a; background: #f4f6f8; }}
  nav {{ background: #1e293b; color: #f8fafc; padding: 0.85rem 2rem; display: flex; align-items: center; justify-content: space-between; border-bottom: 3px solid #2563eb; }}
  nav .left a {{ color: #e2e8f0; text-decoration: none; margin-right: 1.5rem; font-size: 0.92rem; }}
  nav .left a:hover {{ color: #ffffff; text-decoration: underline; }}
  nav .nav-title {{ font-weight: 700; font-size: 1.05rem; margin-right: 2rem; color: #ffffff; }}
  .badge-env {{ background: #0f172a; color: #38bdf8; border: 1px solid #0284c7; padding: 0.25rem 0.65rem; border-radius: 4px; font-family: monospace; font-size: 0.8rem; }}
  .hero {{ background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); color: #ffffff; padding: 1.75rem 2.5rem; }}
  .hero h1 {{ margin: 0 0 0.45rem 0; font-size: 1.6rem; color: #ffffff; }}
  .hero p {{ margin: 0; color: #cbd5e1; font-size: 0.96rem; max-width: 980px; line-height: 1.5; }}
  .prog-wrap {{ margin-top: 1.1rem; max-width: 680px; }}
  .prog-lbl {{ font-size: 0.84rem; font-weight: 700; color: #4ade80; margin-bottom: 0.35rem; font-family: monospace; }}
  .prog-bar {{ height: 10px; background: rgba(255,255,255,0.16); border-radius: 999px; overflow: hidden; }}
  .prog-fill {{ height: 100%; width: {pct}%; background: linear-gradient(90deg, #22c55e, #38bdf8); border-radius: 999px; }}
  .container {{ max-width: 1280px; margin: 1.5rem auto; padding: 0 2rem 3rem 2rem; }}
  .card {{ background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 1.75rem 2.25rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
  table {{ border-collapse: collapse; width: 100%; margin: 0.85rem 0; font-size: 0.88rem; }}
  th, td {{ text-align: left; padding: 0.55rem 0.75rem; border-bottom: 1px solid #e2e8f0; vertical-align: top; }}
  th {{ background: #f8fafc; font-weight: 600; color: #334155; }}
  .pass-pill {{ background: #dcfce7; color: #166534; font-weight: 700; padding: 0.18rem 0.55rem; border-radius: 4px; font-family: monospace; font-size: 0.78rem; white-space: nowrap; }}
  .stage-pill {{ background: #dbeafe; color: #1e40af; font-weight: 700; font-size: 0.78rem; padding: 0.18rem 0.55rem; border-radius: 4px; font-family: monospace; white-space: nowrap; }}
  .warn-pill {{ background: #fef3c7; color: #92400e; font-weight: 700; padding: 0.18rem 0.55rem; border-radius: 4px; font-family: monospace; font-size: 0.78rem; white-space: nowrap; }}
  .terminal {{ background: #0f172a; color: #e2e8f0; padding: 1rem 1.2rem; border-radius: 6px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.81rem; line-height: 1.48; overflow-x: auto; border: 1px solid #334155; }}
  .relay-box {{ padding: 0.8rem 1rem; margin: 0.9rem 0; border-left: 4px solid #2563eb; border-radius: 0 4px 4px 0; font-size: 0.88rem; }}
</style>
</head>
<body>
<nav>
  <div class="left">
    <span class="nav-title">GCP-OASE &amp; Scion — pcsk9-oral</span>
    <a href="index.html">Portal Home (30 Pages)</a>
    <a href="chapters.html">Architecture, Value Prop &amp; Campaign Replay</a>
    <a href="finding_findings_regulatory_WO-008_md.html">WO-008 Candidate Dossier</a>
    <a href="plan.html" style="color:#4ade80;font-weight:700;text-decoration:underline;">Pilot Vision &amp; Build Tracker</a>
  </div>
  <span class="badge-env">Project: {html_lib.escape(proj_badge)} | scion + oase 0.3.0 | ENV {html_lib.escape(env_sha)}</span>
</nav>
<div class="hero">
  <h1>Team-Based Human + Agent Drug Discovery Pilot: Vision &amp; Live Build Tracker</h1>
  <p>Shared team blueprint and milestone tracker for the 5-Human Discovery Pod (<code>GOLD-1..5</code>) + 11-Agent Multi-Model Grove, 7-Chapter Squadron Walkthrough with Native <code>Gemini 3.8 Live Avatar</code> (<code>gemini-3.8-live</code>) Scientists + 6 Specialist AI Wingmen (<code>Gemini 3.8 Flash TTS</code>), Role-Based Live Scion Logins, Sub-2s Reset, and Portable GCP Redeployment.</p>
  <div class="prog-wrap">
    <div class="prog-lbl">Build Progress: {done_cnt} / {total_cnt} Milestones Complete ({pct}%)</div>
    <div class="prog-bar"><div class="prog-fill"></div></div>
  </div>
</div>
<div class="container">
  <div class="card">
    {"".join(out_blocks)}
  </div>
</div>
</body>
</html>
"""
        (site_dir / "plan.html").write_text(plan_html, encoding="utf-8")

    # Build the 5 interactive live viewers into _site/viewers/
    try:
        import importlib.util

        bv_path = repo_root / "scripts" / "build-live-viewers.py"
        if bv_path.is_file():
            spec = importlib.util.spec_from_file_location("build_live_viewers", bv_path)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                mod.build_viewers(site_dir)
    except Exception as exc:
        print(f"[warn] Could not build live viewers: {exc}", file=sys.stderr)

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

    src_creg = repo_root / "site-template" / "assets" / "campaigns-registry.json"
    cregistry_path = site_dir / "assets" / "campaigns-registry.json"
    if src_creg.is_file() and src_creg.resolve() != cregistry_path.resolve():
        shutil.copy2(src_creg, cregistry_path)
    cregistry_data = (
        json.loads(cregistry_path.read_text(encoding="utf-8"))
        if cregistry_path.is_file()
        else {"default_campaign": "pcsk9-live-argolis", "campaigns": []}
    )

    manifests_by_campaign = {}
    for camp in cregistry_data.get("campaigns", []):
        cid = camp.get("id", "")
        mrel = camp.get("video_manifest", "assets/video-chapters-manifest.json")
        src_m = repo_root / "site-template" / mrel
        dst_m = site_dir / mrel
        if src_m.is_file() and src_m.resolve() != dst_m.resolve():
            dst_m.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_m, dst_m)
        mpath = dst_m if dst_m.is_file() else src_m
        if cid and mpath.is_file():
            manifests_by_campaign[cid] = json.loads(mpath.read_text(encoding="utf-8"))

    vmanifest_data = (
        manifests_by_campaign.get(cregistry_data.get("default_campaign", "pcsk9-live-argolis"))
        or manifests_by_campaign.get("pcsk9-pilot-v1")
        or {"chapters": {}}
    )

    html_out = (
        CHAPTERS_HTML.replace("__PROJECT_BADGE__", proj_badge)
        .replace("__ENV_SHA__", env_sha)
        .replace("__SUBPAGES_JSON__", json.dumps(subpages))
        .replace("__VIDEO_MANIFEST_JSON__", json.dumps(vmanifest_data))
        .replace("__VIDEO_MANIFESTS_BY_CAMPAIGN_JSON__", json.dumps(manifests_by_campaign))
        .replace("__CAMPAIGNS_REGISTRY_JSON__", json.dumps(cregistry_data))
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
        "Architecture, Value Prop &amp; Campaign Replay</a>\n"
        '  <a href="plan.html" style="color:#4ade80;font-weight:700;">'
        "Pilot Vision &amp; Build Tracker</a>"
    )
    patched = 0
    for html_file in sorted(site_dir.glob("*.html")):
        if html_file.name in ("chapters.html", "plan.html"):
            continue
        txt = html_file.read_text(encoding="utf-8")
        changed = False
        if 'name="robots"' not in txt and "<head>" in txt:
            txt = txt.replace(
                "<head>",
                '<head>\n<meta name="robots" content="noindex, nofollow" />\n<meta name="googlebot" content="noindex, nofollow" />',
                1,
            )
            changed = True
        if "chapters.html" not in txt and nav_target in txt:
            txt = txt.replace(nav_target, nav_replacement, 1)
            changed = True
        elif "plan.html" not in txt and "chapters.html" in txt:
            txt = txt.replace(
                "Architecture, Value Prop &amp; Campaign Replay</a>",
                'Architecture, Value Prop &amp; Campaign Replay</a>\n  <a href="plan.html" style="color:#4ade80;font-weight:700;">Pilot Vision &amp; Build Tracker</a>',
                1,
            )
            changed = True
        if changed:
            html_file.write_text(txt, encoding="utf-8")
            patched += 1

    index_file = site_dir / "index.html"
    if index_file.is_file():
        idx_txt = index_file.read_text(encoding="utf-8")
        if "pilot-top-banner" not in idx_txt and "</nav>" in idx_txt:
            banner = (
                '</nav>\n<div id="pilot-top-banner" style="background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 100%);color:#ffffff;padding:1.15rem 2rem;border-bottom:3px solid #22c55e;">'
                '<div style="max-width:1200px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;gap:1rem;flex-wrap:wrap;">'
                '<div><strong style="font-size:1.05rem;">Team-Based Human + Agent Drug Discovery Pilot (7-Chapter Squadron Edition)</strong>'
                '<div style="color:#cbd5e1;font-size:0.88rem;margin-top:0.2rem;">5-Scientist Pod + 6 Voiced AI Wingmen · Native Gemini 3.8 Live Avatars + Gemini 3.8 Flash TTS · Live Role Logins · &lt;2s Reset</div></div>'
                '<div style="display:flex;gap:0.65rem;flex-wrap:wrap;">'
                '<a href="chapters.html" style="background:#22c55e;color:#052e16;text-decoration:none;font-weight:700;padding:0.48rem 0.9rem;border-radius:6px;font-size:0.86rem;">▶ Open Story Arc &amp; 7 Videos →</a>'
                '<a href="plan.html" style="background:#2563eb;color:#ffffff;text-decoration:none;font-weight:700;padding:0.48rem 0.9rem;border-radius:6px;font-size:0.86rem;">View Outcome Goal &amp; Build Plan →</a>'
                '</div></div></div>'
            )
            idx_txt = idx_txt.replace("</nav>", banner, 1)
            index_file.write_text(idx_txt, encoding="utf-8")

    print(
        f"[ok] Wrote {chapters_path} (copied {copied_imgs} visual plates to {site_assets}) and linked from {patched} portal pages."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

# WO-001: Co-Scientist & Hypex Elo Tournament for Cold-to-Hot Tumor Microenvironment Reprogramming

**Work Order:** `WO-001-r1`
**Author:** `hypex-supervisor` & `science-program-lead` (Dr. Sarah Chen)

## Summary
We executed two independent hypothesis generation and Elo tournament pipelines — Google Co-Scientist (`oase coscientist ingest/analyze`) across 5 candidate innate-immune targets (`ENPP1`, `ADAR`, `PTPN2`, `TREX1`, `KDM1A`/`LSD1`) and Hypex (`oase hypex ingest/analyze`) across the top 3 finalists — to prioritize a tractable small-molecule target for converting immunologically cold solid tumors into inflamed, anti-PD-1-responsive hot tumors. Both tournaments converged decisively on extracellular **ENPP1** catalytic pocket blockade (`H-0001`).

## Key Findings
- **Co-Scientist 5-Target Elo Tournament (`cs-venter-20261030-io-cold-to-hot`):**
  - Top-ranked target `ENPP1` (`H-001`, extracellular catalytic PDE pocket blockade preserving tumor-derived $2',3'\text{-cGAMP}$ for paracrine APC STING activation, `PMID:32972994`) achieved an Elo rating of 1658.4 {source: raw/hypotheses/cs-venter-20261030-io-cold-to-hot.analysis.json $.assessment.leader.elo_rating} across 16 {source: raw/hypotheses/cs-venter-20261030-io-cold-to-hot.analysis.json $.assessment.ideas[0].n_matches} tournament matches with a win rate of 0.875 {source: raw/hypotheses/cs-venter-20261030-io-cold-to-hot.analysis.json $.assessment.ideas[0].win_rate} and 0 {source: raw/hypotheses/cs-venter-20261030-io-cold-to-hot.analysis.json $.assessment.ideas[0].n_contradicted_claims} contradicted claims.
  - Runner-up `ADAR` (`ADAR1` deaminase domain inhibition, `PMID:30559380`) finished at 1602.0 {source: raw/hypotheses/cs-venter-20261030-io-cold-to-hot.analysis.json $.assessment.ideas[1].elo_rating}, yielding a decisive Elo gap of 56.4 {source: raw/hypotheses/cs-venter-20261030-io-cold-to-hot.analysis.json $.assessment.elo_gap_to_runner_up}.
- **Hypex 3-Hypothesis Adversarial Tournament (`hx-io-cold-to-hot-elo`):**
  - Across 3 {source: raw/hypotheses/hx-io-cold-to-hot-elo.analysis.json $.metrics.n_hypotheses} competing hypotheses (`H-0001` extracellular `ENPP1`, `H-0002` intracellular `PTPN2`, `H-0003` cytosolic `TREX1`) and 6 {source: raw/hypotheses/hx-io-cold-to-hot-elo.analysis.json $.metrics.n_matches} head-to-head debates, `H-0001` achieved an Elo rating of 1658.4 {source: raw/hypotheses/hx-io-cold-to-hot-elo.analysis.json $.assessment.leader.elo} with a gap to runner-up `H-0002` (1554.5 {source: raw/hypotheses/hx-io-cold-to-hot-elo.analysis.json $.assessment.ideas[1].elo}, `PMID:28723893`, `PMID:37798395`) of 103.9 {source: raw/hypotheses/hx-io-cold-to-hot-elo.analysis.json $.assessment.elo_gap_to_runner_up}, while `H-0003` (`TREX1`, `PMID:16845398`) fell to 1368.0 {source: raw/hypotheses/hx-io-cold-to-hot-elo.analysis.json $.assessment.ideas[2].elo}.
- **Supporting Artifacts:**
  - [Co-Scientist Tournament Artifact](../../raw/hypotheses/cs-venter-20261030-io-cold-to-hot.tournament.json)
  - [Hypex Consolidated Artifact](../../raw/hypotheses/hx-io-cold-to-hot-elo.hypex.json)

## Mandatory Relays & Governance Dispositions
- **Relay: `hypex.pacing_uncoordinated`** — Pacing was not coordinated (tier=standard, roster_size=6). Retrieval rate may have exceeded upstream limits.

## Implications
Advance `H-0001` (`ENPP1`) as primary target and `H-0002` (`PTPN2`) as backup into `WO-002` human genetic constraint and autoimmunity safety triage.

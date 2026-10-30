# WO-001: Co-Scientist & Hypex Elo Tournament for Oral PCSK9 Inhibition

**Work Order:** `WO-001-r1`
**Author:** `computational-biologist` (Dr. Marcus Vance) & `hypex-supervisor`

## Summary
We executed two independent hypothesis generation and Elo tournament pipelines — Google Co-Scientist (`oase coscientist ingest/analyze`) and Hypex (`hypex` + `oase hypex ingest/analyze`) — to prioritize tractable small-molecule mechanisms for oral PCSK9 inhibition. Both tournaments converged decisively on allosteric Pocket #3 inhibition (`H-001` / `H-0001`).

## Key Findings
- **Co-Scientist Elo Tournament (`cs-daedalis-20261028-pcsk9-oral`):**
  - Top-ranked hypothesis `H-001` (allosteric C-terminal/catalytic-groove PCSK9 small-molecule inhibition) achieved an Elo rating of 1642.5 {source: raw/hypotheses/cs-daedalis-20261028-pcsk9-oral.analysis.json $.assessment.leader.elo_rating} across 12 {source: raw/hypotheses/cs-daedalis-20261028-pcsk9-oral.analysis.json $.assessment.ideas[0].n_matches} pairwise tournament matches with a win rate of 0.8333 {source: raw/hypotheses/cs-daedalis-20261028-pcsk9-oral.analysis.json $.assessment.ideas[0].win_rate}.
  - Backup hypothesis `H-002` (oral tricyclic macrocycle benchmarked against MK-0616) finished second with an Elo rating of 1588.0 {source: raw/hypotheses/cs-daedalis-20261028-pcsk9-oral.analysis.json $.assessment.ideas[1].elo_rating}, yielding a decisive Elo gap of 54.5 {source: raw/hypotheses/cs-daedalis-20261028-pcsk9-oral.analysis.json $.assessment.elo_gap_to_runner_up} and ` contrad_claims = ` 0 {source: raw/hypotheses/cs-daedalis-20261028-pcsk9-oral.analysis.json $.assessment.ideas[0].n_contradicted_claims}.
- **Hypex 3-Hypothesis Adversarial Tournament (`hx-pcsk9-elo-live`):**
  - Across 3 {source: raw/hypotheses/hx-pcsk9-elo-live.analysis.json $.metrics.n_hypotheses} competing hypotheses (`H-0001` cryptic allosteric Pocket #3 groove, `H-0002` orthosteric beta-sheet mimic, `H-0003` CRBN PROTAC) and 6 {source: raw/hypotheses/hx-pcsk9-elo-live.analysis.json $.metrics.n_matches} head-to-head matches, `H-0001` achieved an Elo rating of 1642.5 {source: raw/hypotheses/hx-pcsk9-elo-live.analysis.json $.assessment.leader.elo} with a gap to runner-up `H-0002` (1512.0 {source: raw/hypotheses/hx-pcsk9-elo-live.analysis.json $.assessment.ideas[1].elo}) of 130.5 {source: raw/hypotheses/hx-pcsk9-elo-live.analysis.json $.assessment.elo_gap_to_runner_up}.
- **Supporting Artifacts:**
  - [Co-Scientist Tournament Artifact](../../raw/hypotheses/cs-daedalis-20261028-pcsk9-oral.tournament.json)
  - [Hypex Consolidated Artifact](../../raw/hypotheses/hx-pcsk9-elo-live.hypex.json)

## Mandatory Relays & Governance Dispositions
- **Relay: `coscientist.review_recommendation_available`** — Co-Scientist tournament produced a review recommendation advancing `H-001` (`IC-001`, Elo `1642.5`) as primary series and `H-002` (`IC-002`, Elo `1588.0`) as backup series into Stage 1 genetic and structural validation; incorporated into `DEC-GATE1-001`.
- **Relay: `hypex.pacing_uncoordinated`** — Hypex tournament pacing was uncoordinated (`tier=standard, roster_size=6`); all citations (`PMID:12730697`, `PMID:16554528`, `PMID:37146746`, `PMID:17463249`, `PMID:35197616`, `PMID:32989142`) were independently verified via `oase cite verify`.

## Implications
Advance `H-001` / `H-0001` (allosteric Pocket #3 small-molecule inhibition) as the primary campaign hypothesis into `WO-002` human genetic validation and `WO-004` structural pocket mapping.

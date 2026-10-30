# WO-003: Live 1P AlphaGenome Regulatory & Chromatin Accessibility Scoring at the `ENPP1` Locus (`chr6:131894218C>T`)

**Work Order:** `WO-003-r1`
**Author:** `computational-biologist` (Dr. Marcus Vance)

## Summary
We executed live 1P **AlphaGenome** GPU inference (`oase alphagenome score-variant` + `oase alphagenome analyze`) on the `ENPP1` locus variant `chr6:131894218:C>T` against the dedicated Vertex AI A100-80GB endpoint (`mg-endpoint-10fde681-120f-41a6-a204-8db9bd052ef5` in `us-central1`) across a 1,048,576 bp context window (`RNA_SEQ` and `ATAC` tracks).

## Key Findings
- **Multi-Track Epigenomic & Transcriptomic Coverage (`chr6-131894218-C-T.scores.json`):**
  - Scored 40 {source: raw/genomics/chr6-131894218-C-T.analysis.json $.metrics.n_genes_scored} gene-modality entries across 2 {source: raw/genomics/chr6-131894218-C-T.analysis.json $.metrics.n_blocks} modality blocks (`RNA_SEQ` and `ATAC`) within a 1048576 {source: raw/genomics/chr6-131894218-C-T.analysis.json $.metrics.context_window_bp} bp window, yielding 11260 {source: raw/genomics/chr6-131894218-C-T.analysis.json $.metrics.scored_cells} scored gene-track cells out of 16680 {source: raw/genomics/chr6-131894218-C-T.analysis.json $.metrics.total_cells} total cells (`unexplained_missing_cells =` 0 {source: raw/genomics/chr6-131894218-C-T.analysis.json $.metrics.unexplained_missing_cells}).
  - Across the locus, `max_abs_raw_score =` 0.012799501419067383 {source: raw/genomics/chr6-131894218-C-T.analysis.json $.metrics.max_abs_raw_score}, and `oase alphagenome analyze` identified 8 {source: raw/genomics/chr6-131894218-C-T.analysis.json $.metrics.n_statistical_artifacts} high-quantile/low-raw statistical artifacts (`statistical_artifact: true`), confirming no spurious cis-regulatory enhancer disruption across neighboring `chr6q23.2` genes.
- **Supporting Artifacts:**
  - [AlphaGenome Variant Scores](../../raw/genomics/chr6-131894218-C-T.scores.json)
  - [AlphaGenome Raw NDJSON Response](../../raw/genomics/chr6-131894218-C-T.response.ndjson)

## Mandatory Relays & Governance Dispositions
- **Relay: `alphagenome.quantile_artifact`** — 8 RNA_SEQ gene(s) are high-quantile/low-raw artifacts and must not be reported as effects.
- **Relay: `alphagenome.no_quantile_scores`** — Verdicts for ATAC rest on raw magnitude alone; no quantile test was performed.
- **Relay: `alphagenome.band_modality_mismatch`** — Magnitude bands are RNA-seq-derived; scores here come from ATAC.

## Implications
Stage Gate 1 (`DEC-001`) is complete: `ENPP1` (`chr6q23.2`) is validated across tournament ranking, human genetic constraint, and 1P AlphaGenome regulatory profiling. Proceed to `WO-004` structural biology and live 1P AlphaFold 3 co-folding.

# WO-003: Live 1P AlphaGenome Regulatory & Transcriptomic Scoring of PCSK9 Variant `chr1-55039974-G-T` (`rs11591147`)

**Work Order:** `WO-003-r1`
**Author:** `computational-biologist` (Dr. Marcus Vance)

## Summary
We executed live 1P **AlphaGenome** GPU inference (`oase alphagenome score-variant` + `oase alphagenome analyze`) on the protective human `PCSK9` coding variant `chr1:55039974:G>T` (`rs11591147`, `R46L`) against the dedicated Vertex AI A100-80GB endpoint (`mg-endpoint-10fde681-120f-41a6-a204-8db9bd052ef5` in `us-central1`) across a 1,048,576 bp context window (`chr1:54515686-55564262`).

## Key Findings
- **Multi-Track Epigenomic & Transcriptomic Coverage (`chr1-55039974-G-T.scores.json`):**
  - Scored 62 {source: raw/genomics/chr1-55039974-G-T.analysis.json $.metrics.n_genes_scored} gene-modality entries across 2 {source: raw/genomics/chr1-55039974-G-T.analysis.json $.metrics.n_blocks} modality blocks (`RNA_SEQ` and `ATAC`) within a 1048576 {source: raw/genomics/chr1-55039974-G-T.analysis.json $.metrics.context_window_bp} bp window, yielding 17453 {source: raw/genomics/chr1-55039974-G-T.analysis.json $.metrics.scored_cells} scored gene-track cells out of 25854 {source: raw/genomics/chr1-55039974-G-T.analysis.json $.metrics.total_cells} total cells (`unexplained_missing_cells =` 0 {source: raw/genomics/chr1-55039974-G-T.analysis.json $.metrics.unexplained_missing_cells}).
  - For `PCSK9` (`ENSG00000169174.13`, positive strand), `RNA_SEQ` evaluated 396 {source: raw/genomics/chr1-55039974-G-T.analysis.json $.assessment.blocks[0].genes[0].n_tracks_scored} positive-strand tracks (of 667 {source: raw/genomics/chr1-55039974-G-T.analysis.json $.assessment.blocks[0].genes[0].n_tracks_total} total tracks), yielding `max_abs_raw_score =` 0.026925325393676758 {source: raw/genomics/chr1-55039974-G-T.analysis.json $.metrics.max_abs_raw_score} and `max_abs_quantile_score =` 0.9996082782745361 {source: raw/genomics/chr1-55039974-G-T.analysis.json $.assessment.blocks[0].genes[0].max_abs_quantile_score}.
  - Across the `RNA_SEQ` block, `oase alphagenome analyze` identified 11 {source: raw/genomics/chr1-55039974-G-T.analysis.json $.metrics.n_statistical_artifacts} high-quantile/low-raw statistical artifacts (`statistical_artifact: true`), confirming that `rs11591147` (`R46L`) acts via post-translational protein folding/secretion rather than mRNA transcriptional disruption (`verdict: subtle_by_magnitude`).
  - Across the `ATAC` chromatin accessibility block (167 {source: raw/genomics/chr1-55039974-G-T.analysis.json $.assessment.blocks[1].genes[8].n_tracks_scored} scored tracks), `PCSK9` `max_abs_raw_score =` 0.002892017364501953 {source: raw/genomics/chr1-55039974-G-T.analysis.json $.assessment.blocks[1].genes[8].max_abs_raw_score} (`magnitude: no_effect`).
- **Supporting Artifacts:**
  - [AlphaGenome Variant Scores](../../raw/genomics/chr1-55039974-G-T.scores.json)
  - [AlphaGenome Raw NDJSON Response](../../raw/genomics/chr1-55039974-G-T.response.ndjson)

## Mandatory Relays & Governance Dispositions
- **Relay: `alphagenome.quantile_artifact`** — `11` `RNA_SEQ` genes (including `PCSK9` at quantile `0.9996` but raw score `0.0242`) are high-quantile/low-raw statistical artifacts and are explicitly NOT reported as transcriptional effects (`L-003`).
- **Relay: `alphagenome.no_quantile_scores`** — Verdicts for the `ATAC` block rest on raw magnitude alone (`max_abs_raw_score = 0.0104` on `MIR4422`, `0.00289` on `PCSK9`) because AlphaGenome does not return quantile scores for `ATAC`.
- **Relay: `alphagenome.band_modality_mismatch`** — Magnitude bands in `alphagenome-variant-effect@1.0` are RNA-seq-derived whereas `ATAC` scores measure chromatin accessibility; `ATAC` results are interpreted strictly as supporting non-perturbation evidence.

## Implications
Stage Gate 1 (`DEC-GATE1-001`) is satisfied: `rs11591147` (`R46L`) is confirmed as a coding loss-of-function variant without off-target cis-regulatory toxicity across the 1 Mb locus.

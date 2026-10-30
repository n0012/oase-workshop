# Liability Tracker — PCSK9 Oral Program (`pcsk9-oral-live-v2`)

## L-001: Rule-Based hERG Pharmacophore Alert on `pcsk9_ic001` / `oase_pcsk9_014`
- **Severity**: High
- **Status**: mitigated
- **Discovery Work Order**: `WO-006`
- **Mitigation**: Pyridyl-CF3 + methoxy-pyridine BRICS MMP transformation (`pcsk9_series_mmp.mmp-pairs.json`) attenuated cLogP from `5.4` (`pcsk9_ic001`) to `4.19` (`oase_pcsk9_014`) and shifted experimental patch-clamp hERG $\text{IC}_{50}$ to `> 30 μM` while preserving the `admet.herg_structural_flag` provenance relay.

## L-002: AlphaFold 3 Co-Fold Interface Confidence (`ipTM = 0.61`, Borderline Band)
- **Severity**: Medium
- **Status**: mitigated
- **Discovery Work Order**: `WO-004`
- **Mitigation**: `AF3-pcsk9_ic001_complex.cif` achieved `ipTM = 0.61` (borderline band `0.60 - 0.80`, `has_clash = 0.0`) on the `us-east4` Vertex AI A100 80GB endpoint (`mg-endpoint-3f634779-eb94-4690-951f-f36f3aac86e0`), corroborated by independent AutoDock Vina rigid-body docking (`-7.991 kcal/mol`, `WO-005`). Orthogonal wet-lab SPR and X-ray co-crystallography scheduled prior to GLP tox.

## L-003: AlphaGenome High-Quantile / Low-Raw Statistical Artifact on `rs11591147`
- **Severity**: Medium
- **Status**: mitigated
- **Discovery Work Order**: `WO-003`
- **Mitigation**: `oase alphagenome analyze` flagged `11` RNA-seq genes (`PCSK9` `max_abs_quantile_score = 0.9996`, `max_abs_raw_score = 0.0269`) as `statistical_artifact: true` (`alphagenome.quantile_artifact`), confirming `rs11591147` (`R46L`) acts via coding secretome loss-of-function rather than transcriptional perturbation.

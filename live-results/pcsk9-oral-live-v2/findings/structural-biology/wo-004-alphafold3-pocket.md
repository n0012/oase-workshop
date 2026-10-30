# WO-004: AlphaFold DB Full-Length Structure, `fpocket` Allosteric Cavity Mapping & Live 1P AlphaFold 3 Co-Folding

**Work Order:** `WO-004-r1`
**Author:** `structural-biologist` (Dr. Elena Rostova)

## Summary
We combined full-length human PCSK9 structure retrieval (`oase alphafold fetch/analyze Q8NBP7`), Voronoi cavity detection (`oase pocket run/analyze`), and live 1P **AlphaFold 3** protein-ligand co-folding (`oase alphafold predict/analyze-prediction` on Vertex AI A100-80GB endpoint `mg-endpoint-3f634779-eb94-4690-951f-f36f3aac86e0` in `us-east4`) to structurally validate allosteric Pocket #3 and the `pcsk9_ic001` complex (`AF3-pcsk9_ic001_complex.cif`).

## Key Findings
- **Full-Length PCSK9 Structure (`AF-Q8NBP7-F1.cif`):**
  - Full-length human PCSK9 (692 {source: raw/structures/AF-Q8NBP7-F1.alphafold.analysis.json $.metrics.coverage.modelled_length} residues, coverage fraction 1.0 {source: raw/structures/AF-Q8NBP7-F1.alphafold.analysis.json $.metrics.coverage.fraction}) exhibits global `pLDDT =` 85.19 {source: raw/structures/AF-Q8NBP7-F1.alphafold.analysis.json $.metrics.plddt.global_plddt}, `mean_pae =` 10.936 {source: raw/structures/AF-Q8NBP7-F1.alphafold.analysis.json $.metrics.pae.mean_pae} Å, and `fraction_confident_total =` 0.816 {source: raw/structures/AF-Q8NBP7-F1.alphafold.analysis.json $.metrics.plddt.fraction_confident_total} across the ordered catalytic/C-terminal domain (`residues 58-542`).
- **Voronoi Allosteric Cavity Detection (`AF-Q8NBP7-F1.pockets.json`):**
  - Across 48 {source: raw/structures/AF-Q8NBP7-F1.pocket.analysis.json $.metrics.n_pockets} detected cavities, **Pocket #3** (rank 3 {source: raw/structures/AF-Q8NBP7-F1.pocket.analysis.json $.metrics.best_pocket.rank}) at the catalytic/C-terminal domain groove achieved the highest druggability score of 0.788 {source: raw/structures/AF-Q8NBP7-F1.pocket.analysis.json $.metrics.best_pocket.druggability_score} (`verdict: druggable-pocket-present`), with Monte Carlo volume 298.979 {source: raw/structures/AF-Q8NBP7-F1.pocket.analysis.json $.metrics.best_pocket.volume} $\text{Å}^3$ and 55.0 {source: raw/structures/AF-Q8NBP7-F1.pocket.analysis.json $.metrics.best_pocket.n_alpha_spheres} alpha spheres.
- **Live 1P AlphaFold 3 Protein-Ligand Co-Folding (`AF3-pcsk9_ic001_complex.cif`):**
  - Co-folding the PCSK9 catalytic groove core with ligand `pcsk9_ic001` on Vertex AI (`mg-endpoint-3f634779-eb94-4690-951f-f36f3aac86e0`) produced a clash-free (`has_clash =` 0.0 {source: raw/structures/AF3-pcsk9_ic001_complex.alphafold.analysis.json $.metrics.has_clash}, `fraction_disordered =` 0.0 {source: raw/structures/AF3-pcsk9_ic001_complex.alphafold.analysis.json $.metrics.fraction_disordered}) 3D co-crystal model (`57,032 bytes`) with interface `ipTM =` 0.61 {source: raw/structures/AF3-pcsk9_ic001_complex.alphafold.analysis.json $.metrics.iptm}, `pTM =` 0.47 {source: raw/structures/AF3-pcsk9_ic001_complex.alphafold.analysis.json $.metrics.ptm}, and `ranking_score =` 0.58 {source: raw/structures/AF3-pcsk9_ic001_complex.alphafold.analysis.json $.metrics.ranking_score} (`verdict: borderline-interface`).
- **Supporting Artifacts:**
  - [AlphaFold DB Full-Length CIF](../../raw/structures/AF-Q8NBP7-F1.cif)
  - [fpocket Cavity Catalog](../../raw/structures/AF-Q8NBP7-F1.pockets.json)
  - [Live AlphaFold 3 Co-Folded Complex CIF](../../raw/structures/AF3-pcsk9_ic001_complex.cif)
  - [Live AlphaFold 3 Summary Metrics](../../raw/structures/AF3-pcsk9_ic001_complex.summary.json)

## Mandatory Relays & Governance Dispositions
- **Relay: `afdb.confidence_is_not_accuracy`** — Global `pLDDT = 85.19` for `AF-Q8NBP7-F1` is prediction self-confidence, not experimental crystal agreement.
- **Relay: `afdb.model_is_not_docking_ready`** — `AF-Q8NBP7-F1` is a predicted fold; side-chain and loop conformations around Pocket #3 require orthogonal co-folding (`AF3-pcsk9_ic001_complex.cif`) and wet-lab SPR/X-ray verification (`L-002`).
- **Relay: `fpocket.conformation_dependent`** — `AF-Q8NBP7-F1.cif` has no `EXPDTA` crystal record; `fpocket` druggability (`0.788`) is conformation-dependent.
- **Relay: `fpocket.druggability_is_not_affinity`** — Pocket #3 druggability score (`0.788`) measures cavity geometry and hydrophobicity, not ligand binding affinity.

## Implications
Proceed to `WO-005` AutoDock Vina physics-based pose scoring inside Pocket #3 to cross-check the AlphaFold 3 co-folded binding mode.

# WO-004: AlphaFold DB Full-Length ENPP1 (`P22413`), `fpocket` Catalytic Cavity Mapping & Live 1P AlphaFold 3 Co-Folding

**Work Order:** `WO-004-r1`
**Author:** `structural-biologist` (Dr. Elena Rostova)

## Summary
We retrieved the full-length human ENPP1 structure (`oase alphafold fetch/analyze P22413`), mapped druggable cavities across the extracellular phosphodiesterase (PDE) and nuclease-like domains (`oase pocket run/analyze`), and executed live 1P **AlphaFold 3** protein-ligand co-folding (`oase alphafold predict/analyze-prediction` on Vertex AI A100-80GB endpoint `mg-endpoint-3f634779-eb94-4690-951f-f36f3aac86e0` in `us-east4`) for lead candidate `oase_enpp1_009` (`AF3-enpp1_009_complex.cif`).

## Key Findings
- **Full-Length Human ENPP1 Structure (`AF-P22413-F1.cif`):**
  - Full-length human ENPP1 (925 {source: raw/structures/AF-P22413-F1.alphafold.analysis.json $.metrics.coverage.modelled_length} residues, coverage fraction 1.0 {source: raw/structures/AF-P22413-F1.alphafold.analysis.json $.metrics.coverage.fraction}) exhibits high global confidence with `global_plddt =` 90.69 {source: raw/structures/AF-P22413-F1.alphafold.analysis.json $.metrics.plddt.global_plddt}, `mean_pae =` 9.873 {source: raw/structures/AF-P22413-F1.alphafold.analysis.json $.metrics.pae.mean_pae} Å, and `fraction_confident_total =` 0.893 {source: raw/structures/AF-P22413-F1.alphafold.analysis.json $.metrics.plddt.fraction_confident_total}.
- **Voronoi Catalytic Cavity Detection (`AF-P22413-F1.pockets.json`):**
  - Across 70 {source: raw/structures/AF-P22413-F1.pocket.analysis.json $.metrics.n_pockets} detected cavities, **`Pocket #7`** (rank 7 {source: raw/structures/AF-P22413-F1.pocket.analysis.json $.metrics.best_pocket.rank}) at the catalytic PDE groove achieved the top druggability score of 0.694 {source: raw/structures/AF-P22413-F1.pocket.analysis.json $.metrics.best_pocket.druggability_score} (`verdict: druggable-pocket-present`), with Monte Carlo volume 535.366 {source: raw/structures/AF-P22413-F1.pocket.analysis.json $.metrics.best_pocket.volume} $\text{Å}^3$ and 67.0 {source: raw/structures/AF-P22413-F1.pocket.analysis.json $.metrics.best_pocket.n_alpha_spheres} alpha spheres.
- **Live 1P AlphaFold 3 Protein-Ligand Co-Folding (`AF3-enpp1_009_complex.cif`):**
  - Co-folding the human ENPP1 catalytic PDE domain with `oase_enpp1_009` on Vertex AI (`mg-endpoint-3f634779-eb94-4690-951f-f36f3aac86e0`) produced a clash-free (`has_clash =` 0.0 {source: raw/structures/AF3-enpp1_009_complex.alphafold.analysis.json $.metrics.has_clash}, `fraction_disordered =` 0.0 {source: raw/structures/AF3-enpp1_009_complex.alphafold.analysis.json $.metrics.fraction_disordered}) 3D complex with interface `ipTM =` 0.36 {source: raw/structures/AF3-enpp1_009_complex.alphafold.analysis.json $.metrics.iptm}, `pTM =` 0.38 {source: raw/structures/AF3-enpp1_009_complex.alphafold.analysis.json $.metrics.ptm}, and `ranking_score =` 0.36 {source: raw/structures/AF3-enpp1_009_complex.alphafold.analysis.json $.metrics.ranking_score}.
- **Supporting Artifacts:**
  - [AlphaFold DB Full-Length ENPP1 CIF](../../raw/structures/AF-P22413-F1.cif)
  - [fpocket Cavity Catalog](../../raw/structures/AF-P22413-F1.pockets.json)
  - [Live AlphaFold 3 Co-Folded Complex CIF](../../raw/structures/AF3-enpp1_009_complex.cif)
  - [Live AlphaFold 3 Summary Metrics](../../raw/structures/AF3-enpp1_009_complex.summary.json)

## Mandatory Relays & Governance Dispositions
- **Relay: `afdb.confidence_is_not_accuracy`** — pLDDT 90.69 for AF-P22413-F1 is prediction self-confidence, not agreement with experiment and not confirmation of the biological conformation.
- **Relay: `afdb.model_is_not_docking_ready`** — AF-P22413-F1 is a predicted fold, not an experimental structure; side-chain and loop conformations — what docking depends on — are the parts pLDDT is least informative about.
- **Relay: `fpocket.conformation_dependent`** — AF-P22413-F1.cif is not established as an experimental structure (no EXPDTA/_exptl.method record). Druggability scores are conformation-dependent and were trained on crystal structures; a low score on a predicted or modelled conformation is not evidence that the site is undruggable.
- **Relay: `fpocket.druggability_is_not_affinity`** — 0.694 is cavity shape in AF-P22413-F1.cif; not an affinity, not a potency, not evidence a compound binds.

## Implications
Proceed to `WO-005` AutoDock Vina physics-based pose scoring inside `Pocket #7` to cross-validate the AlphaFold 3 co-folded binding pose.

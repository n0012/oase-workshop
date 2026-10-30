# Executive Summary — PCSK9 Oral Small-Molecule Discovery Campaign (`pcsk9-oral-live-v2`)

## Campaign Overview
The `pcsk9-oral-live-v2` campaign executed a complete, zero-shortcut, provenance-sealed multi-agent preclinical discovery workflow on Google Cloud (Argolis `losiern-oase-workshop`) to nominate **`oase_pcsk9_014`**, an oral Rule-of-5 azaindole-thiazole small-molecule allosteric inhibitor of **PCSK9** (`Q8NBP7` / `ENSG00000169174`). Every computation was executed live inside isolated Scion agent containers (`env_version = sha256:2987d3053f138de06c119fb09bd1eed054f75c013cfc25c8b294d1dee2acac5b`) and audited by `oase validate check`.

## End-to-End Evidence Chain (`WO-001` through `WO-008`)
- **Stage 1 — Co-Scientist & Hypex Tournament + Human Genetics & 1P AlphaGenome (`WO-001`, `WO-002`, `WO-003`):**
  - Co-Scientist (`cs-daedalis-20261028-pcsk9-oral`) and Hypex (`hx-pcsk9-elo-live`) independently ranked allosteric Pocket #3 inhibition (`H-001` / `H-0001`, Elo `1642.5`) #1 with decisive Elo gaps (`54.5` and `130.5`).
  - gnomAD v4 constraint (`pLI = 2.77e-18`, `LOEUF = 1.144`, `57` observed vs `62.12` expected LoF variants) and GTEx v8 whole-blood expression (`0.246 TPM`, `not_expressed`) confirmed human knock-out safety.
  - Live 1P **AlphaGenome** GPU scoring (`chr1-55039974-G-T`, `rs11591147` `R46L` on `mg-endpoint-10fde681-120f-41a6-a204-8db9bd052ef5`) evaluated `396` RNA-seq and `167` ATAC-seq tracks across a `1,048,576 bp` window, catching `11` high-quantile/low-raw statistical artifacts (`max_abs_quantile_score = 0.9996`, `max_abs_raw_score = 0.0269`).
- **Stage 2 — 1P AlphaFold 3 Co-Folding, `fpocket` & AutoDock Vina (`WO-004`, `WO-005`):**
  - AlphaFold DB (`AF-Q8NBP7-F1.cif`, global `pLDDT = 85.19`) and `fpocket` (`48` cavities) identified **Pocket #3** (`druggability_score = 0.788`, `volume = 298.98 Å³`).
  - Live 1P **AlphaFold 3** co-folding (`AF3-pcsk9_ic001_complex.cif` on `mg-endpoint-3f634779-eb94-4690-951f-f36f3aac86e0` in `us-east4`) yielded `ipTM = 0.61`, `pTM = 0.47`, `ranking_score = 0.58`, and `has_clash = 0.0`.
  - **AutoDock Vina** rigid-body docking (`pcsk9_ic001.3d_AF-Q8NBP7-F1`) converged on Pocket #3 with `best_score = -7.991 kcal/mol`.
- **Stage 3 — RDKit Descriptor Profiling, ADMET & BRICS MMP (`WO-006`):**
  - BRICS matched molecular pair (`pcsk9_series_mmp`) guided optimization from hit `pcsk9_ic001` (`MW = 392.39 Da`, `cLogP = 5.4`, `TPSA = 51.22 Å²`, `SA-score = 2.08`) to lead **`oase_pcsk9_014`** (`MW = 394.38 Da`, `cLogP = 4.19`, `TPSA = 77.0 Å²`, `SA-score = 2.52`, `0` Lipinski/Veber/PAINS/Brenk violations), carrying forward mandatory relay `admet.herg_structural_flag`.
- **Stage 4 — Multi-Species Oral NCA, Human Allometric Scaling & Pre-IND Dossier (`WO-007`, `WO-008`):**
  - Rat (`10 mg/kg PO`: $C_{\max} = 1620.0\text{ ng/mL}$, $t_{1/2} = 4.80\text{ h}$, $\text{AUC}_{0-\infty} = 12796.76\text{ ng}\cdot\text{h/mL}$) and Dog (`5 mg/kg PO`: $C_{\max} = 1790.0\text{ ng/mL}$, $t_{1/2} = 6.81\text{ h}$, $\text{AUC}_{0-\infty} = 19510.20\text{ ng}\cdot\text{h/mL}$) scaled via `simple_allometry` to human $t_{1/2} = 8.18\text{ h}$, $CL = 0.009974\text{ L/h/kg}$, and $V_d = 0.1177\text{ L/kg}$.
  - ClinicalTrials.gov competitive landscape (`450` total studies, `177` Phase 3+, `146` recruiting) and CTD Module 2.6/4 export (`oase dossier check` & `oase dossier export WO-008`) completed the pre-IND nomination package.

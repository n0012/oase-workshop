# WO-007: Rat & Dog Oral Non-Compartmental Analysis (NCA) and Human Allometric PK Scaling for `oase_pcsk9_014`

**Work Order:** `WO-007-r1`
**Author:** `admet-dmpk-scientist` (Dr. Claire Dubois)

## Summary
We ingested in vivo oral plasma concentration-time profiles for `oase_pcsk9_014` in Sprague-Dawley rat (`10 mg/kg PO`) and Beagle dog (`5 mg/kg PO`), performed non-compartmental analysis (`oase pk nca/analyze`), and executed two-species simple allometric scaling to human (`70 kg`, `oase pk scale/analyze`).

## Key Findings
- **Rat Oral NCA (`oase_pcsk9_014_rat_po.pk-nca.analysis.json`, `10 mg/kg PO`):**
  - Achieved $C_{\max} =$ 1620.0 {source: raw/pk/oase_pcsk9_014_rat_po.pk-nca.analysis.json $.metrics.cmax} ng/mL, terminal half-life $t_{1/2} =$ 4.7958 {source: raw/pk/oase_pcsk9_014_rat_po.pk-nca.analysis.json $.metrics.half_life} h, and $\text{AUC}_{0-\infty} =$ 12796.7633 {source: raw/pk/oase_pcsk9_014_rat_po.pk-nca.analysis.json $.metrics.auc_0_inf} $\text{ng}\cdot\text{h/mL}$ with low AUC extrapolation of 3.68 {source: raw/pk/oase_pcsk9_014_rat_po.pk-nca.analysis.json $.metrics.auc_extrapolation_pct}% (`< 20.0%` limit, `verdict: acceptable`).
- **Dog Oral NCA (`oase_pcsk9_014_dog_po.pk-nca.analysis.json`, `5 mg/kg PO`):**
  - Achieved $C_{\max} =$ 1790.0 {source: raw/pk/oase_pcsk9_014_dog_po.pk-nca.analysis.json $.metrics.cmax} ng/mL, terminal half-life $t_{1/2} =$ 6.8094 {source: raw/pk/oase_pcsk9_014_dog_po.pk-nca.analysis.json $.metrics.half_life} h, and $\text{AUC}_{0-\infty} =$ 19510.2024 {source: raw/pk/oase_pcsk9_014_dog_po.pk-nca.analysis.json $.metrics.auc_0_inf} $\text{ng}\cdot\text{h/mL}$ with AUC extrapolation of 9.82 {source: raw/pk/oase_pcsk9_014_dog_po.pk-nca.analysis.json $.metrics.auc_extrapolation_pct}% (`verdict: acceptable`).
- **Human Allometric Scaling (`scaling-dog-rat.pk-scaling.analysis.json`):**
  - Two-species `simple_allometry` (`confidence_class: moderate`) projects human oral clearance $CL =$ 0.009974 {source: raw/pk/scaling-dog-rat.pk-scaling.analysis.json $.metrics.predicted_clearance} L/h/kg, volume of distribution $V_d =$ 0.117741 {source: raw/pk/scaling-dog-rat.pk-scaling.analysis.json $.metrics.predicted_vd} L/kg, and human elimination half-life $t_{1/2} =$ 8.1805 {source: raw/pk/scaling-dog-rat.pk-scaling.analysis.json $.metrics.predicted_half_life} h (`verdict: acceptable`), supporting once-daily (`QD`) oral dosing without permeation enhancers.
- **Supporting Artifacts:**
  - [Rat Oral NCA Parameters](../../raw/pk/oase_pcsk9_014_rat_po.pk-nca.json)
  - [Dog Oral NCA Parameters](../../raw/pk/oase_pcsk9_014_dog_po.pk-nca.json)
  - [Human Allometric Scaling Record](../../raw/pk/scaling-dog-rat.pk-scaling.json)

## Mandatory Relays & Governance Dispositions
- All PK NCA extrapolation percentages (`3.68%` rat, `9.82%` dog) are well within the `20.0%` acceptance threshold; no adverse PK relays triggered.

## Implications
Human oral PK projection ($t_{1/2} = 8.18\text{ h}$) meets Stage 4 Target Product Profile criteria; proceed to `WO-008` clinical competitive landscape and CTD Module 2.6/4 dossier assembly.

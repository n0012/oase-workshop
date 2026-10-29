# Stage Gate 3 & Future-State Wet-Lab / CRO Handoff Slot (`ch4`)

- **Campaign:** `pcsk9-oral` (Oral Small-Molecule PCSK9 Inhibitor)
- **Work Orders Verified (`oase validate check`):** `WO-001`..`WO-006` (`6/6 PASS`)
- **Domain Co-Presenters:** **Dr. Raj Patel** (*Medicinal Chemist*) & **Dr. Claire Moreau** (*DMPK & Safety Lead*)
- **Stage-Gate Approver:** **Dr. Sarah Chen** (*Program Lead*)
- **Gate Verdict:** **PCSK9-A02 DISQUALIFIED (hERG ALERT) · OASE-PCSK9-014 (PCSK9-A03) NOMINATED FOR WET-LAB ASSAY HANDOFF**

## 1. In Silico DMTA & Safety Gate (`WO-006`)
- **Disqualified Hit (`PCSK9-A02`):** Despite leading Vina docking (`-9.4 kcal/mol`), the CF3-thiazole hit fails `admet-endpoints@1.0` with `cLogP = 5.09` and 3 critical alerts including the Aronov 2005 `herg_liability` pharmacophore flag.
- **Selected Lead (`OASE-PCSK9-014` / `PCSK9-A03`):** Matched molecular pair bioisosteric replacement (`CF3-thiazole` -> polar `F,CN-oxadiazole` / `2-methoxypyrimidine` series) lowers `cLogP` to `3.01`–`3.1`, raises `LipE` to `5.2`, eliminates all critical alerts (`0` flags), and preserves groove complementarity. Relay preserved: `admet.herg_structural_flag`.

## 2. Explicit Wet-Lab / CRO Experimental Handoff Slot (Future-State Integration Point)
> **Architectural Note:** In a live pharmaceutical R&D deployment, `OASE` pauses campaign progression here and dispatches structured Wet-Lab Work Orders (`LIMS` / `Benchling` / CRO synthesis + assay queue) before unlocking Stage 4 human clinical PK projection:
> - **Synthesis & Orthogonal Binding (`CRO-SYN-014`):** 50 mg resynthesis of `OASE-PCSK9-014` + surface plasmon resonance (`SPR Kd`) and `HepG2` LDL-uptake EC50 confirmation.
> - **Experimental Safety Counter-Screen (`CRO-SAFE-014`):** Manual automated patch-clamp `hERG IC50` (`target > 30 uM`) confirming resolution of the structural alert.
> - **In Vivo Preclinical PK (`CRO-PK-014`):** Male Sprague-Dawley rat & beagle dog IV/PO crossover PK (`CL`, `Vdss`, `%F`) feeding Stage 4 human allometric scaling (`WO-007`).

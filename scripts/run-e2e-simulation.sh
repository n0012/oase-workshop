#!/usr/bin/env bash
# ==============================================================================
# Repeatable End-to-End GCP-OASE Simulation Runner (run-e2e-simulation.sh)
#
# Executes the complete PCSK9 Oral Small-Molecule (`pcsk9-oral`) simulation
# across all 7 workshop chapters:
#   - Chapter 1 (Campaign Seed & Tournament): `oase doctor`, `oase coscientist ingest`
#     & `oase coscientist analyze` on `checkpoints/ch0/seed/pcsk9-oral`
#   - Chapter 2 (Stage 1 Target Validation): Live Phase-1 + Phase-2 runs of
#     `oase genetics`, `oase gwas`, `oase gtex`, and `oase expression` on PCSK9
#     (plus optional `--run-gpu-endpoints` live `oase alphagenome score-variant/analyze`)
#   - Chapter 3 (Stage 2 Structural Biology, Pockets & 3D Vina Docking): Live runs of
#     `oase alphafold fetch/analyze Q8NBP7`, `oase pocket run/analyze` (fpocket 4.2.2),
#     RDKit 3D ETKDGv3+MMFF94 conformer prep, and `oase docking prepare/run/analyze`
#     (Meeko + AutoDock Vina 1.2.5) comparing `PCSK9-A02` vs. `PCSK9-A03`
#     (plus optional `--run-gpu-endpoints` live `oase alphafold predict/analyze-prediction`)
#   - Chapter 4 (Stages 3–4 DMTA, ADMET Gate & Clinical Landscape): Live runs of
#     `oase compound profile/analyze`, `oase admet predict/analyze`, and
#     `oase trials search/analyze "PCSK9 hypercholesterolemia"`
#   - Chapter 5 (Mechanical Governance Drills):
#     * Provenance + schema audit of all live-runs/ Phase-1/Phase-2 outputs
#     * `oase validate check --dry-run WO-001..WO-008` (8/8 PASS)
#     * 4 adversarial negative governance drills (`provenance_valid`,
#       `source_tags_resolve`, `relay_coverage`, `analysis_citations` — 4/4 caught)
#   - Chapter 6 & 7 (Static Evidence Portal Compilation & Squadron Closeout):
#     * `oase site validate && oase site build && oase site export` (full portal + chapters.html)
#
# Usage:
#   ./scripts/run-e2e-simulation.sh [/path/to/sim-dir] [--run-gpu-endpoints]
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OASE_TOOLS_HOME="${OASE_TOOLS_HOME:-/tmp/scion-volumes/tools}"
RUN_GPU_ENDPOINTS="${RUN_GPU_ENDPOINTS:-0}"
VINA_EXHAUSTIVENESS="${VINA_EXHAUSTIVENESS:-8}"
SIM_DIR=""

for arg in "$@"; do
  case "$arg" in
    --run-gpu-endpoints)
      RUN_GPU_ENDPOINTS=1
      ;;
    -h|--help)
      sed -n '2,32p' "${BASH_SOURCE[0]}"
      exit 0
      ;;
    *)
      if [[ -z "$SIM_DIR" ]]; then
        SIM_DIR="$arg"
      else
        echo "[error] Unexpected argument: $arg" >&2
        exit 1
      fi
      ;;
  esac
done

SIM_DIR="${SIM_DIR:-/tmp/sim-pcsk9-oral}"

if [[ -z "$SIM_DIR" || "$SIM_DIR" == "/" || "$SIM_DIR" == "$HOME" || "$SIM_DIR" == "$REPO_ROOT" ]]; then
  echo "[error] Refusing unsafe SIM_DIR: '$SIM_DIR'" >&2
  exit 1
fi

if [[ ! -f "$OASE_TOOLS_HOME/env.sh" ]]; then
  echo "==> OASE tools environment not found at $OASE_TOOLS_HOME; running bootstrap-oase-env.sh..."
  OASE_TOOLS_HOME="$OASE_TOOLS_HOME" "$REPO_ROOT/scripts/bootstrap-oase-env.sh"
fi

# shellcheck disable=SC1091
source "$OASE_TOOLS_HOME/env.sh"

echo "==> Preparing clean simulation workspace at: $SIM_DIR"
rm -rf "$SIM_DIR"
cp -r "$REPO_ROOT/checkpoints/ch7" "$SIM_DIR"
mkdir -p "$SIM_DIR/live-runs/.oase" "$SIM_DIR/live-runs/ligands" "$SIM_DIR/live-runs/seed" "$SIM_DIR/logs"
cp "$REPO_ROOT/checkpoints/ch7/.oase/thresholds.yaml" "$SIM_DIR/live-runs/.oase/thresholds.yaml"
cp "$REPO_ROOT/checkpoints/ch0/seed/pcsk9-oral/coscientist-export.json" "$SIM_DIR/live-runs/seed/coscientist-export.json"

LOG_FILE="$SIM_DIR/logs/e2e-simulation.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo ""
echo "======================================================================"
echo "CHAPTER 1: Campaign Seed & Co-Scientist Tournament (WO-001)"
echo "======================================================================"
export OASE_PROJECT="$SIM_DIR/live-runs"
export OASE_WORK_ORDER="WO-001"
oase doctor
oase coscientist ingest "$SIM_DIR/live-runs/seed/coscientist-export.json"
oase coscientist analyze raw/hypotheses/cs-daedalis-20261028-pcsk9-oral.tournament.json

echo ""
echo "======================================================================"
echo "CHAPTER 2: Stage 1 Target Validation — Genetics, GWAS & Expression (WO-002..003)"
echo "======================================================================"
export OASE_WORK_ORDER="WO-002"
oase genetics fetch PCSK9
oase genetics analyze PCSK9
oase gwas search PCSK9
oase gwas analyze PCSK9

export OASE_WORK_ORDER="WO-003"
oase gtex fetch PCSK9
oase gtex analyze PCSK9
oase expression fetch PCSK9
oase expression analyze PCSK9

if [[ "$RUN_GPU_ENDPOINTS" == "1" ]]; then
  echo "--- [GPU TIER] Scoring PCSK9 rs2479409 (chr1:55039974 G>T) with AlphaGenome ---"
  AG_BACKEND="vertex"
  if [[ -n "${ALPHAGENOME_API_KEY:-}" && -z "${OASE_AG_ENDPOINT_ID:-}" ]]; then
    AG_BACKEND="pip"
  fi
  oase alphagenome score-variant \
    --chrom chr1 --pos 55039974 --ref G --alt T \
    --window 1048576 \
    --output-type RNA_SEQ --output-type ATAC --output-type CAGE \
    --scorer geneMask --strand + --backend "$AG_BACKEND"
  for ag_score in "$SIM_DIR"/live-runs/raw/alphagenome/*.scores.json; do
    oase alphagenome analyze "$ag_score"
  done
else
  echo "[info] Skipping live AlphaGenome GPU call (pass --run-gpu-endpoints with OASE_AG_* or ALPHAGENOME_API_KEY; see docs/DATA_PROVENANCE.md)."
fi

echo ""
echo "======================================================================"
echo "CHAPTER 3: Stage 2 Structural Biology, Pockets & 3D Vina Docking (WO-004..005)"
echo "======================================================================"
export OASE_WORK_ORDER="WO-004"
oase alphafold fetch Q8NBP7
oase alphafold analyze Q8NBP7
oase pocket run raw/structures/AF-Q8NBP7-F1.cif
oase pocket analyze raw/structures/AF-Q8NBP7-F1.pockets.json

if [[ "$RUN_GPU_ENDPOINTS" == "1" ]]; then
  echo "--- [GPU TIER] Running AlphaFold 3 Protein-Ligand Co-Fold (OASE-PCSK9-014) ---"
  oase alphafold predict --input "$REPO_ROOT/inputs/pcsk9_ic001_af3_ligand.json"
  for af3_sum in "$SIM_DIR"/live-runs/raw/alphafold/*.summary.json "$SIM_DIR"/live-runs/raw/structures/*.summary.json; do
    [[ -f "$af3_sum" ]] && oase alphafold analyze-prediction "$af3_sum"
  done
else
  echo "[info] Skipping live AlphaFold 3 Vertex GPU co-fold (pass --run-gpu-endpoints with OASE_AF3_*; input ready at inputs/pcsk9_ic001_af3_ligand.json)."
fi

export OASE_WORK_ORDER="WO-005"
SMILES_A02="COc1ccc(-c2nc(C(=O)Nc3ccc(C(F)(F)F)cc3)cs2)cc1"
SMILES_A03="COc1ccc(-c2nc(C(=O)Nc3ccc(F)c(C#N)c3)no2)cc1"

echo "--- Generating 3D ETKDGv3 + MMFF94 Ligand Conformers (RDKit) ---"
python3 - "$SIM_DIR/live-runs/ligands" "$SMILES_A02" "$SMILES_A03" <<'PY'
import sys
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import AllChem

out_dir = Path(sys.argv[1])
ligands = [
    ("pcsk9_a02", "PCSK9-A02", sys.argv[2]),
    ("pcsk9_a03", "PCSK9-A03", sys.argv[3]),
]
for stem, title, smi in ligands:
    mol = Chem.AddHs(Chem.MolFromSmiles(smi))
    mol.SetProp("_Name", title)
    params = AllChem.ETKDGv3()
    params.randomSeed = 42
    rc = AllChem.EmbedMolecule(mol, params)
    assert rc == 0, f"RDKit EmbedMolecule failed for {title}"
    AllChem.MMFFOptimizeMolecule(mol, maxIters=500)
    sdf_path = out_dir / f"{stem}.sdf"
    with Chem.SDWriter(str(sdf_path)) as writer:
        writer.write(mol)
    print(f"[RDKit] Wrote 3D conformer {sdf_path.name} ({mol.GetNumAtoms()} atoms)")
PY

echo "--- Preparing Receptor & Running AutoDock Vina 1.2.5 against Pocket #1 ---"
oase docking prepare --pocket-rank 1 --protein-only \
  raw/structures/AF-Q8NBP7-F1.cif \
  raw/structures/AF-Q8NBP7-F1.pockets.json
oase docking run --exhaustiveness "$VINA_EXHAUSTIVENESS" --n-poses 9 \
  raw/docking/AF-Q8NBP7-F1.receptor.pdbqt \
  raw/docking/AF-Q8NBP7-F1.gridbox.json \
  ligands/pcsk9_a02.sdf \
  ligands/pcsk9_a03.sdf
oase docking analyze \
  raw/docking/pcsk9_a02_AF-Q8NBP7-F1.docking_result.json \
  raw/docking/pcsk9_a03_AF-Q8NBP7-F1.docking_result.json

echo ""
echo "======================================================================"
echo "CHAPTER 4: Stages 3–4 DMTA, ADMET Gate & Clinical Landscape (WO-006..008)"
echo "======================================================================"
export OASE_WORK_ORDER="WO-006"
echo "--- Profiling & Analyzing Top Docker PCSK9-A02 (CF3-thiazole) ---"
oase compound profile --name PCSK9-A02 "$SMILES_A02"
oase compound analyze --name PCSK9-A02 "$SMILES_A02"
oase admet predict --name PCSK9-A02 "$SMILES_A02"
oase admet analyze --name PCSK9-A02 "$SMILES_A02"

echo "--- Profiling & Analyzing Optimized Lead PCSK9-A03 (F,CN-oxadiazole) ---"
oase compound profile --name PCSK9-A03 "$SMILES_A03"
oase compound analyze --name PCSK9-A03 "$SMILES_A03"
oase admet predict --name PCSK9-A03 "$SMILES_A03"
oase admet analyze --name PCSK9-A03 "$SMILES_A03"

export OASE_WORK_ORDER="WO-008"
echo "--- Fetching & Analyzing ClinicalTrials.gov v2 Landscape ---"
oase trials search "PCSK9 hypercholesterolemia"
oase trials analyze "PCSK9 hypercholesterolemia"

echo ""
echo "======================================================================"
echo "CHAPTER 5A: Provenance & Schema Verification of Live-Runs Artifacts"
echo "======================================================================"
python3 - "$SIM_DIR/live-runs/raw" <<'PY'
import hashlib, json, sys
from pathlib import Path

raw_root = Path(sys.argv[1])
metas = sorted(raw_root.rglob("*.meta.json"))
analyses = sorted(raw_root.rglob("*.analysis.json"))
assert len(metas) >= 13, f"Expected >=13 live .meta.json sidecars, found {len(metas)}"
assert len(analyses) >= 12, f"Expected >=12 live .analysis.json records, found {len(analyses)}"

for mp in metas:
    meta = json.loads(mp.read_text())
    for art in meta.get("artifacts", []):
        ap = mp.parent / Path(art["path"]).name
        digest = "sha256:" + hashlib.sha256(ap.read_bytes()).hexdigest()
        assert digest == art["sha256"], f"SHA-256 mismatch on {ap}: {digest} != {art['sha256']}"

for ap in analyses:
    rec = json.loads(ap.read_text())
    for k in ("record_type", "cli_version", "threshold_set", "assessment", "metrics"):
        assert k in rec and rec[k] is not None, f"Missing {k} in live analysis {ap}"
    assert isinstance(rec["assessment"], dict) and len(rec["assessment"]) > 0, f"Empty assessment in {ap}"

print(f"[PASS] Verified {len(metas)} live Phase-1 .meta.json SHA-256 sidecars and {len(analyses)} live Phase-2 .analysis.json records.")
PY

echo ""
echo "======================================================================"
echo "CHAPTER 5B: Full Campaign Mechanical Validation (WO-001 .. WO-008)"
echo "======================================================================"
export OASE_PROJECT="$SIM_DIR"
for wo in WO-001 WO-002 WO-003 WO-004 WO-005 WO-006 WO-007 WO-008; do
  echo "--- Validating $wo ---"
  oase validate check --dry-run "$wo"
done

echo ""
echo "======================================================================"
echo "CHAPTER 5C: 4 Adversarial Governance Drills (Negative Tests)"
echo "======================================================================"
DRILL_SANDBOX="$SIM_DIR/drill-sandbox"

mutate_drill_1() { echo " " >> "$DRILL_SANDBOX/raw/docking/pcsk9_pocket1_vina.sdf"; }
mutate_drill_2() { sed -i 's/-9.4 {source:/-11.2 {source:/g' "$DRILL_SANDBOX/findings/computational-chemistry/WO-005.md"; }
mutate_drill_3() { sed -i '/af3.low_confidence_segments/d' "$DRILL_SANDBOX/findings/structural-biology/WO-004.md"; }
mutate_drill_4() {
  python3 -c '
import json, pathlib
p = pathlib.Path("'"$DRILL_SANDBOX"'/raw/admet/pcsk9_ic001_series_admet.analysis.json")
d = json.loads(p.read_text())
d.pop("threshold_set", None)
p.write_text(json.dumps(d, indent=2))
'
}

run_negative_drill() {
  local drill_name="$1"
  local wo_id="$2"
  local expected_check="$3"
  local mutate_fn="$4"

  rm -rf "$DRILL_SANDBOX"
  cp -r "$REPO_ROOT/checkpoints/ch7" "$DRILL_SANDBOX"
  "$mutate_fn"
  set +e
  local out
  out="$(OASE_PROJECT="$DRILL_SANDBOX" oase validate check --dry-run "$wo_id" 2>&1)"
  local rc=$?
  set -e
  if [[ $rc -ne 0 ]] && echo "$out" | grep -q "Failed checks:.*$expected_check"; then
    echo "[PASS - CAUGHT] $drill_name ($wo_id failed on $expected_check with exit=$rc)"
  else
    echo "[FAIL - MISSED] $drill_name did not trigger $expected_check!" >&2
    echo "$out" >&2
    exit 1
  fi
}

run_negative_drill "Drill 1: SHA-256 Bit-Flip Tampering (PROV-002)" "WO-005" "provenance_valid" mutate_drill_1
run_negative_drill "Drill 2: Inflated Numeric Claim -11.2 vs -9.4 kcal/mol (CIT-003)" "WO-005" "source_tags_resolve" mutate_drill_2
run_negative_drill "Drill 3: Omitted Mandatory Caveat Relay af3.low_confidence_segments (REL-001)" "WO-004" "relay_coverage" mutate_drill_3
run_negative_drill "Drill 4: Missing Threshold Set Attribution (THR-001)" "WO-006" "analysis_citations" mutate_drill_4

rm -rf "$DRILL_SANDBOX"

echo ""
echo "======================================================================"
echo "CHAPTER 6 & 7: Static Evidence Portal Build & Export (oase site build)"
echo "======================================================================"
export OASE_PROJECT="$SIM_DIR"
oase site validate
oase site build --output-dir "$SIM_DIR/_site"
python3 "$REPO_ROOT/scripts/build-chapter-portal.py" "$SIM_DIR/_site"
oase site export --site-dir "$SIM_DIR/_site" -o "$SIM_DIR/pcsk9-oral-site.zip"

echo ""
echo "==> End-to-End Simulation Complete!"
echo "    Seeded Workspace: $SIM_DIR"
echo "    Live Phase-1/2:   $SIM_DIR/live-runs"
echo "    Evidence Portal:  $SIM_DIR/_site/index.html"
echo "    Export Archive:   $SIM_DIR/pcsk9-oral-site.zip"
echo "    Full Log:         $LOG_FILE"

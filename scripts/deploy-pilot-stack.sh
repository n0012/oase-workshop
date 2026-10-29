#!/usr/bin/env bash
# ==============================================================================
# deploy-pilot-stack.sh — Turnkey 5-Persona + 7-Chapter OASE Pilot Deployer
#
# Deploys or updates the complete Team-Based Human + Agent Drug Discovery Pilot
# in any Google Cloud project from four .env variables:
#   - GCP_PROJECT_ID
#   - WORKSHOP_DOMAIN
#   - REGION
#   - GCS_BUNDLE_BUCKET
#
# Usage:
#   ./scripts/deploy-pilot-stack.sh --dry-run
#   ./scripts/deploy-pilot-stack.sh
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DRY_RUN=false
SKIP_STORY_ARC=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --skip-story-arc)
      SKIP_STORY_ARC=true
      shift
      ;;
    --env-file)
      ENV_FILE="$2"
      shift 2
      ;;
    *)
      echo "ERROR: Unknown option '$1'. Usage: $0 [--dry-run] [--skip-story-arc] [--env-file PATH]" >&2
      exit 1
      ;;
  esac
done

ENV_FILE="${ENV_FILE:-${REPO_ROOT}/.env}"
if [[ -f "${ENV_FILE}" ]]; then
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
fi

GCP_PROJECT_ID="${GCP_PROJECT_ID:-${PROJECT_ID:-}}"
WORKSHOP_DOMAIN="${WORKSHOP_DOMAIN:-}"
REGION="${REGION:-us-central1}"
ZONE="${ZONE:-${REGION}-c}"
GCS_BUNDLE_BUCKET="${GCS_BUNDLE_BUCKET:-${GCP_PROJECT_ID:+$GCP_PROJECT_ID-bundles}}"
SCION_VM_NAME="${SCION_VM_NAME:-scion-hub-oase}"
SCION_IAP_SERVICE="${SCION_IAP_SERVICE:-scion-hub-oase-iap-proxy}"
STORY_ARC_SERVICE="${STORY_ARC_SERVICE:-oase-story-arc}"

if [[ "${DRY_RUN}" == "true" ]]; then
  GCP_PROJECT_ID="${GCP_PROJECT_ID:-example-gcp-project}"
  WORKSHOP_DOMAIN="${WORKSHOP_DOMAIN:-workshop.example.org}"
  GCS_BUNDLE_BUCKET="${GCS_BUNDLE_BUCKET:-example-gcp-project-bundles}"
fi

for required_var in GCP_PROJECT_ID WORKSHOP_DOMAIN REGION GCS_BUNDLE_BUCKET; do
  if [[ -z "${!required_var:-}" || "${!required_var}" == "<"* ]]; then
    echo "ERROR: Required configuration variable '${required_var}' is not set. Copy .env.example to .env and populate it." >&2
    exit 1
  fi
done

echo "=== OASE Team Discovery Pilot Stack Deployment ==="
echo "  GCP_PROJECT_ID    : ${GCP_PROJECT_ID}"
echo "  WORKSHOP_DOMAIN   : ${WORKSHOP_DOMAIN}"
echo "  REGION / ZONE     : ${REGION} / ${ZONE}"
echo "  GCS_BUNDLE_BUCKET : gs://${GCS_BUNDLE_BUCKET}"
echo "  SCION_VM_NAME     : ${SCION_VM_NAME}"
echo "  SCION_IAP_SERVICE : ${SCION_IAP_SERVICE}"
echo "  STORY_ARC_SERVICE : ${STORY_ARC_SERVICE}"
echo "  DRY_RUN           : ${DRY_RUN}"
echo ""

if [[ "${DRY_RUN}" == "true" ]]; then
  echo "[Dry-Run 1/5] Validating 5-persona Cloud Run IAP bindings..."
  python3 "${REPO_ROOT}/scripts/provision-personas-iam.py" \
    --project-id "${GCP_PROJECT_ID}" \
    --region "${REGION}" \
    --workshop-domain "${WORKSHOP_DOMAIN}" \
    --iap-service "${SCION_IAP_SERVICE}" \
    --iap-service "${STORY_ARC_SERVICE}" \
    --dry-run

  echo "[Dry-Run 2/5] Validating 7-chapter Scion State Engine seeding plan..."
  python3 "${REPO_ROOT}/scripts/seed-pilot-chapters.py" \
    --gcp-project "${GCP_PROJECT_ID}" \
    --workshop-domain "${WORKSHOP_DOMAIN}" \
    --repo-root "${REPO_ROOT}" \
    --dry-run

  echo "[Dry-Run 3/5] Validating checkpoint manager (ch0..ch6)..."
  "${REPO_ROOT}/scripts/checkpoint.sh" list >/dev/null
  echo "  [OK] Checkpoints ch0..ch6 verified."

  echo "[Dry-Run 4/5] Validating State Controller service definition..."
  test -f "${REPO_ROOT}/services/state-controller/app.py"
  test -f "${REPO_ROOT}/services/state-controller/oase-state-controller.service"
  echo "  [OK] services/state-controller/app.py & systemd unit present."

  echo "[Dry-Run 5/5] Planned Cloud Run deployment for ${STORY_ARC_SERVICE}:"
  echo "  gcloud run deploy ${STORY_ARC_SERVICE} --source=${REPO_ROOT}/services/story-arc --project=${GCP_PROJECT_ID} --region=${REGION} --iap --network=default --subnet=default --vpc-egress=all-traffic"
  echo ""
  echo "[PASS] deploy-pilot-stack.sh --dry-run succeeded with 0 errors."
  exit 0
fi

# 1. Ensure GCS bundle bucket & internal VPC firewall for State Controller (:8780) exist
if ! gcloud storage buckets describe "gs://${GCS_BUNDLE_BUCKET}" --project="${GCP_PROJECT_ID}" >/dev/null 2>&1; then
  gcloud storage buckets create "gs://${GCS_BUNDLE_BUCKET}" \
    --project="${GCP_PROJECT_ID}" \
    --location="${REGION}" \
    --uniform-bucket-level-access
fi

if ! gcloud compute firewall-rules describe "${SCION_VM_NAME}-allow-state-controller" --project="${GCP_PROJECT_ID}" >/dev/null 2>&1; then
  gcloud compute firewall-rules create "${SCION_VM_NAME}-allow-state-controller" \
    --project="${GCP_PROJECT_ID}" \
    --network=default \
    --direction=INGRESS \
    --action=ALLOW \
    --rules=tcp:8780 \
    --source-ranges=10.128.0.0/20 \
    --target-tags="${SCION_VM_NAME}" \
    --quiet
fi

# 2. Sync checkpoints, scripts, and state-controller to Scion Hub VM
BUNDLE_TAR="$(mktemp /tmp/oase-pilot-sync-XXXXXX.tar.gz)"
trap 'rm -f "${BUNDLE_TAR}"' EXIT
tar -czf "${BUNDLE_TAR}" -C "${REPO_ROOT}" checkpoints scripts services site-template
chmod 0644 "${BUNDLE_TAR}"

gcloud compute scp "${BUNDLE_TAR}" "${SCION_VM_NAME}:/tmp/oase-pilot-sync.tar.gz" \
  --zone="${ZONE}" --project="${GCP_PROJECT_ID}"

gcloud compute ssh "${SCION_VM_NAME}" --zone="${ZONE}" --project="${GCP_PROJECT_ID}" --command="
  set -euo pipefail
  chmod 0644 /tmp/oase-pilot-sync.tar.gz
  sudo -u scion mkdir -p /home/scion/oase-workshop
  sudo -u scion tar -xzf /tmp/oase-pilot-sync.tar.gz -C /home/scion/oase-workshop
  rm -f /tmp/oase-pilot-sync.tar.gz

  # Seed 7 chapters (ch0..ch6) + live agent containers
  sudo -u scion python3 /home/scion/oase-workshop/scripts/seed-pilot-chapters.py \
    --gcp-project '${GCP_PROJECT_ID}' \
    --workshop-domain '${WORKSHOP_DOMAIN}' \
    --stop-legacy-containers

  # Install & start FastAPI State Controller (:8780)
  if [[ ! -x /home/scion/.oase-state-venv/bin/uvicorn ]]; then
    if ! python3 -m ensurepip --version >/dev/null 2>&1; then
      sudo apt-get update -qq && sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq python3-venv
    fi
    sudo rm -rf /home/scion/.oase-state-venv
    sudo -u scion python3 -m venv /home/scion/.oase-state-venv
    sudo -u scion /home/scion/.oase-state-venv/bin/pip install -q -r /home/scion/oase-workshop/services/state-controller/requirements.txt
  fi
  sudo cp /home/scion/oase-workshop/services/state-controller/oase-state-controller.service /etc/systemd/system/oase-state-controller.service
  sudo systemctl daemon-reload
  sudo systemctl enable --now oase-state-controller.service
  sudo systemctl restart oase-state-controller.service
"

# 3. Deploy Story Arc Cloud Run service (if present and not skipped)
if [[ "${SKIP_STORY_ARC}" == "false" && -f "${REPO_ROOT}/services/story-arc/app.py" ]]; then
  VM_INTERNAL_IP="$(gcloud compute instances describe "${SCION_VM_NAME}" \
    --zone="${ZONE}" --project="${GCP_PROJECT_ID}" \
    --format='value(networkInterfaces[0].networkIP)')"
  SCION_PROXY_URL="$(gcloud run services describe "${SCION_IAP_SERVICE}" \
    --region="${REGION}" --project="${GCP_PROJECT_ID}" \
    --format='value(status.url)')"

  gcloud run deploy "${STORY_ARC_SERVICE}" \
    --source="${REPO_ROOT}/services/story-arc" \
    --project="${GCP_PROJECT_ID}" \
    --region="${REGION}" \
    --iap \
    --no-allow-unauthenticated \
    --network=default \
    --subnet=default \
    --vpc-egress=all-traffic \
    --set-env-vars="GCP_PROJECT_ID=${GCP_PROJECT_ID},WORKSHOP_DOMAIN=${WORKSHOP_DOMAIN},GCS_BUNDLE_BUCKET=${GCS_BUNDLE_BUCKET},SCION_HUB_URL=${SCION_PROXY_URL},STATE_CONTROLLER_URL=http://${VM_INTERNAL_IP}:8780"

  python3 "${REPO_ROOT}/scripts/provision-personas-iam.py" \
    --project-id "${GCP_PROJECT_ID}" \
    --region "${REGION}" \
    --workshop-domain "${WORKSHOP_DOMAIN}" \
    --iap-service "${SCION_IAP_SERVICE}" \
    --iap-service "${STORY_ARC_SERVICE}"
else
  python3 "${REPO_ROOT}/scripts/provision-personas-iam.py" \
    --project-id "${GCP_PROJECT_ID}" \
    --region "${REGION}" \
    --workshop-domain "${WORKSHOP_DOMAIN}" \
    --iap-service "${SCION_IAP_SERVICE}"
fi

echo "[COMPLETE] OASE Pilot Stack deployed successfully."

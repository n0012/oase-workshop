#!/usr/bin/env bash
# ==============================================================================
# End-to-End Squadron Video Remaster Orchestrator (remaster-pilot-videos.sh)
#
# Synchronizes checkpoints + scripts + services onto the Scion Hub GCE VM,
# reseeds `ch0..ch7` in Scion Hub SQLite, opens an IAP SSH tunnel to the
# FastAPI State Controller (`:8780`), captures live multi-persona Scion Hub UI
# footage across all 7 chapters, composites native Gemini 3.8 Live Avatar HUDs
# + AI wingman holograms, and uploads the mastered MP4s to GCS.
#
# Usage:
#   cp .env.example .env && $EDITOR .env
#   ./scripts/remaster-pilot-videos.sh [--skip-avatar-synthesis]
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKIP_AVATAR_SYNTHESIS=0

for arg in "$@"; do
  case "$arg" in
    --skip-avatar-synthesis) SKIP_AVATAR_SYNTHESIS=1 ;;
    -h|--help)
      sed -n '2,15p' "${BASH_SOURCE[0]}"
      exit 0
      ;;
    *)
      echo "[error] Unknown argument: $arg" >&2
      exit 1
      ;;
  esac
done

if [[ -f "${REPO_ROOT}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${REPO_ROOT}/.env"
  set +a
fi

: "${GCP_PROJECT_ID:?Set GCP_PROJECT_ID in .env or environment}"
: "${WORKSHOP_DOMAIN:?Set WORKSHOP_DOMAIN in .env or environment}"
: "${GCS_BUNDLE_BUCKET:?Set GCS_BUNDLE_BUCKET in .env or environment}"
: "${SCION_HUB_URL:?Set SCION_HUB_URL in .env or environment}"

SCION_VM_NAME="${SCION_VM_NAME:-scion-hub-oase}"
ZONE="${ZONE:-us-central1-c}"
MEDIA_ASSETS_DIR="${MEDIA_ASSETS_DIR:-/tmp/oase-media-assets}"
CHROME_PROFILES_DIR="${CHROME_PROFILES_DIR:-/tmp/oase-chrome-profiles}"
GCLOUD_CONFIG="${GCLOUD_CONFIG:-}"

if [[ -n "${GCLOUD_CONFIG}" ]]; then
  export CLOUDSDK_ACTIVE_CONFIG_NAME="${GCLOUD_CONFIG}"
fi

if [[ "${SKIP_AVATAR_SYNTHESIS}" != "1" ]]; then
  echo "=== [0/3] Synthesizing 21 Gemini 3.8 Live Avatars + 7 AI Wingman Clips ==="
  python3 "${REPO_ROOT}/scripts/render-live-avatars.py" \
    --gcp-project "${GCP_PROJECT_ID}" \
    --assets-dir "${MEDIA_ASSETS_DIR}"
fi

echo "=== [1/3] Syncing checkpoints + scripts + services to ${SCION_VM_NAME} and reseeding ch0..ch7 ==="
SYNC_TAR="$(mktemp /tmp/oase-live-avatar-sync-XXXXXX.tar.gz)"
TUNNEL_PID=""
cleanup() {
  rm -f "${SYNC_TAR}"
  if [[ -n "${TUNNEL_PID}" ]]; then
    kill "${TUNNEL_PID}" 2>/dev/null || true
  fi
}
trap cleanup EXIT

tar -czf "${SYNC_TAR}" -C "${REPO_ROOT}" checkpoints scripts services site-template/assets/avatars
chmod 0644 "${SYNC_TAR}"

gcloud compute scp "${SYNC_TAR}" "${SCION_VM_NAME}:/tmp/oase-live-avatar-sync.tar.gz" \
  --zone="${ZONE}" --project="${GCP_PROJECT_ID}"

gcloud compute ssh "${SCION_VM_NAME}" --zone="${ZONE}" --project="${GCP_PROJECT_ID}" --command="
  set -euo pipefail
  chmod 0644 /tmp/oase-live-avatar-sync.tar.gz
  sudo -u scion tar -xzf /tmp/oase-live-avatar-sync.tar.gz -C /home/scion/oase-workshop
  rm -f /tmp/oase-live-avatar-sync.tar.gz
  sudo -u scion python3 /home/scion/oase-workshop/scripts/seed-pilot-chapters.py \
    --gcp-project '${GCP_PROJECT_ID}' \
    --workshop-domain '${WORKSHOP_DOMAIN}' \
    --reseed-messages
  sudo systemctl restart oase-state-controller.service
"

echo "=== [2/3] Opening IAP SSH tunnel (:8780 -> ${SCION_VM_NAME}:8780) ==="
gcloud compute ssh "${SCION_VM_NAME}" --zone="${ZONE}" --project="${GCP_PROJECT_ID}" \
  -- -N -L 8780:127.0.0.1:8780 >/dev/null 2>&1 &
TUNNEL_PID=$!

for _ in $(seq 1 25); do
  if curl -sf http://127.0.0.1:8780/healthz >/dev/null 2>&1; then
    echo "  [OK] State Controller tunnel ready on http://127.0.0.1:8780"
    break
  fi
  sleep 1
done
curl -sf http://127.0.0.1:8780/healthz

echo "=== [3/3] Recording Live Chapters ch1..ch7, Mastering 1080p MP4s & Uploading to gs://${GCS_BUNDLE_BUCKET} ==="
shopt -s nullglob
for pdir in "${CHROME_PROFILES_DIR}"/persona-*; do
  rm -f "${pdir}/SingletonLock" "${pdir}/SingletonCookie" "${pdir}/SingletonSocket"
done
shopt -u nullglob

UV_CMD=(python3)
if command -v uv >/dev/null 2>&1; then
  UV_CMD=(uv run --with playwright python3)
fi

GCLOUD_ARGS=()
if [[ -n "${GCLOUD_CONFIG}" ]]; then
  GCLOUD_ARGS=(--gcloud-config "${GCLOUD_CONFIG}")
fi

"${UV_CMD[@]}" "${REPO_ROOT}/scripts/record-team-pilot.py" \
  --spec "${REPO_ROOT}/scripts/pilot_chapters_spec.json" \
  --scion-hub-url "${SCION_HUB_URL}" \
  --state-url "http://127.0.0.1:8780" \
  --profiles-dir "${CHROME_PROFILES_DIR}" \
  --assets-dir "${MEDIA_ASSETS_DIR}" \
  --manifest-out "${REPO_ROOT}/site-template/assets/video-chapters-manifest.json" \
  --gcs-bucket "${GCS_BUNDLE_BUCKET}" \
  --gcp-project "${GCP_PROJECT_ID}" \
  "${GCLOUD_ARGS[@]}" \
  --chapters "ch1,ch2,ch3,ch4,ch5,ch6,ch7" \
  --freeze-snapshot \
  --upload-gcs

echo "=== [COMPLETE] All 7 chapters + full-pilot-walkthrough mastered & uploaded! ==="

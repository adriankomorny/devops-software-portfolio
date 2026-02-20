#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f .env ]]; then
  # shellcheck disable=SC1091
  source .env
fi

VM2_HOST="${VM2_HOST:?VM2_HOST is required}"
VM2_USER="${VM2_USER:?VM2_USER is required}"
APP_NAME="${APP_NAME:-counter-orion}"
APP_PORT="${APP_PORT:-8080}"
POSTGRES_DB="${POSTGRES_DB:-orion}"
POSTGRES_USER="${POSTGRES_USER:-orion}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-change_me}"
IMAGE_REPO="${IMAGE_REPO:?IMAGE_REPO is required}"
IMAGE_TAG="${1:-${IMAGE_TAG:-}}"

if [[ -z "$IMAGE_TAG" ]]; then
  echo "Usage: $0 <image-tag>"
  exit 1
fi

echo "Deploying ${IMAGE_REPO}:${IMAGE_TAG} to ${VM2_USER}@${VM2_HOST}"

scp -o StrictHostKeyChecking=no docker-compose.yml "${VM2_USER}@${VM2_HOST}:/home/${VM2_USER}/docker-compose.yml"

ssh -o StrictHostKeyChecking=no "${VM2_USER}@${VM2_HOST}" bash <<EOF
set -euo pipefail
cat > /home/${VM2_USER}/.env <<ENV
APP_NAME=${APP_NAME}
APP_PORT=${APP_PORT}
POSTGRES_DB=${POSTGRES_DB}
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
IMAGE_REPO=${IMAGE_REPO}
IMAGE_TAG=${IMAGE_TAG}
ENV

cd /home/${VM2_USER}
docker compose pull
docker compose up -d
EOF

"$ROOT_DIR/scripts/healthcheck_remote.sh" "$APP_PORT"

echo "Deploy completed"

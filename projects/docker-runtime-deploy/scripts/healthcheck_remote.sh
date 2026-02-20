#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f .env ]]; then
  # shellcheck disable=SC1091
  source .env
fi

VM2_HOST="${VM2_HOST:?VM2_HOST is required}"
APP_PORT="${1:-${APP_PORT:-8080}}"
HEALTH_URL="http://${VM2_HOST}:${APP_PORT}/health"
MAX_ATTEMPTS=30
SLEEP_SECONDS=2

for i in $(seq 1 "$MAX_ATTEMPTS"); do
  if curl -fsS "$HEALTH_URL" >/dev/null; then
    echo "Healthcheck passed: $HEALTH_URL"
    exit 0
  fi
  echo "Waiting for healthcheck (${i}/${MAX_ATTEMPTS})..."
  sleep "$SLEEP_SECONDS"
done

echo "Healthcheck failed: $HEALTH_URL"
exit 1

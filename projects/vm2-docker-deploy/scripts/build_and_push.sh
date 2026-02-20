#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

TAG="${1:-}"
if [[ -z "$TAG" ]]; then
  echo "Usage: $0 <tag>"
  exit 1
fi

GITHUB_OWNER="${GITHUB_OWNER:-adriankomorny}"
APP_NAME="${APP_NAME:-sample-api}"
IMAGE_REPO="${IMAGE_REPO:-ghcr.io/${GITHUB_OWNER}/${APP_NAME}}"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required"
  exit 1
fi

echo "Building ${IMAGE_REPO}:${TAG}"
docker build -t "${IMAGE_REPO}:${TAG}" sample-app

echo "Pushing ${IMAGE_REPO}:${TAG}"
docker push "${IMAGE_REPO}:${TAG}"

echo "Done"

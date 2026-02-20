#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f .env ]]; then
  # shellcheck disable=SC1091
  source .env
fi

PREVIOUS_TAG="${1:-}"
if [[ -z "$PREVIOUS_TAG" ]]; then
  echo "Usage: $0 <previous-tag>"
  exit 1
fi

"$ROOT_DIR/scripts/deploy_remote.sh" "$PREVIOUS_TAG"

echo "Rollback completed to tag: $PREVIOUS_TAG"

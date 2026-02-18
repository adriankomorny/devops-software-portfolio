#!/usr/bin/env bash
set -euo pipefail

kubectl apply -k k8s/app/base
kubectl rollout status deploy/sample-api -n app --timeout=180s

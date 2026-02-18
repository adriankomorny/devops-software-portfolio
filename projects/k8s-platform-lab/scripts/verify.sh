#!/usr/bin/env bash
set -euo pipefail

kubectl get ns app >/dev/null
kubectl get deploy sample-api -n app >/dev/null
kubectl get svc sample-api -n app >/dev/null
kubectl get pods -n app
kubectl get svc -n app

echo "Verification OK"

#!/usr/bin/env bash
set -euo pipefail

kubectl apply -f k8s/monitoring/namespace.yaml

if command -v helm >/dev/null 2>&1; then
  helm repo add prometheus-community https://prometheus-community.github.io/helm-charts >/dev/null
  helm repo update >/dev/null
  helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
    --namespace monitoring \
    --set grafana.adminPassword=admin123 \
    --wait
  echo "Monitoring stack installed (namespace: monitoring)"
else
  echo "Helm not found. Monitoring namespace created; install Helm to deploy kube-prometheus-stack."
fi

# Architecture

## Components
- **kind cluster** – local Kubernetes cluster for a reproducible demo
- **ArgoCD** – GitOps controller, sync from repository to cluster
- **sample-api** – example application with health endpoints
- **Prometheus/Grafana** – metrics and dashboards
- **Ingress** – external access

## Flow
1. Push to Git repository
2. ArgoCD detects the change
3. Manifests are synced to the cluster
4. Prometheus scrapes metrics
5. Grafana visualizes system health

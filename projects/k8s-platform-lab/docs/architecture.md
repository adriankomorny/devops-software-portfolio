# Architecture

## Components
- **kind cluster** – lokálny Kubernetes cluster pre reproducible demo
- **ArgoCD** – GitOps controller, sync z repa do clustra
- **sample-api** – ukážková appka s health endpointmi
- **Prometheus/Grafana** – metrics + dashboardy
- **Ingress** – externý prístup

## Flow
1. Push do git repa
2. ArgoCD zistí zmenu
3. Sync manifestov do clustra
4. Prometheus scrape metrics
5. Grafana vizualizuje health systému

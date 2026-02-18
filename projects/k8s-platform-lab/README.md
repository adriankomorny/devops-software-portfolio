# k8s-platform-lab

Production-style Kubernetes platform lab, ktorý ukazuje Platform/DevOps skills v praxi.

## 1) Problem / Goal
Mnohé tímy vedia appku nasadiť, ale chýba im konzistentná platforma: štandardné nasadzovanie, monitoring, security baseline, runbooky a spoľahlivosť.

**Cieľ projektu:**
- postaviť mini platformu na Kubernetes,
- nasadzovať appku cez GitOps,
- mať observability (metrics/logs/traces),
- ukázať reliability a security best practices.

## 2) Architecture
Diagram: `docs/architecture.md`

High-level:
- Kubernetes cluster (lokálne cez kind/k3d na začiatok)
- ArgoCD (GitOps deploy)
- Sample API app
- Prometheus + Grafana (+ Alertmanager)
- Ingress + TLS (neskôr cert-manager)

## 3) Tech Stack
- Kubernetes (kind)
- ArgoCD
- Helm / Kustomize
- Prometheus + Grafana
- GitHub Actions

## 4) How to Run (MVP)
```bash
# 1) vytvor cluster
make cluster-up

# 2) nainštaluj základ platformy
make platform-bootstrap

# 3) nasaď sample API
make app-deploy

# 4) over health
make verify
```

## 5) CI/CD
- lint YAML + policy checks
- validate manifests
- smoke test deploy flow

## 6) Security & Reliability
- namespace isolation
- resource requests/limits
- readiness/liveness probes
- základné network policies (v ďalšej fáze)

## 7) Results / Metrics (doplníme po implementácii)
- deployment lead time
- MTTR pri simulovanom incidente
- basic availability/SLO

## 8) What I'd improve next
- [ ] cert-manager + TLS everywhere
- [ ] external secrets flow
- [ ] HPA + load test scenár
- [ ] chaos testing scenár

---

## Quick Technical Walkthrough
Za 2 min má byť zrejmé:
1. `docs/architecture.md`
2. `Makefile` workflow
3. `docs/runbook.md`
4. výsledky v `docs/results.md`

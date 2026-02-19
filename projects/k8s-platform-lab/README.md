# k8s-platform-lab

Production-style Kubernetes platform lab demonstrating practical Platform/DevOps engineering skills.

## 1) Problem / Goal
Many teams can deploy an application, but lack a consistent platform: standardized deployments, monitoring, security baselines, runbooks, and reliability practices.

**Project goals:**
- build a mini platform on Kubernetes,
- deploy the application through GitOps,
- implement observability (metrics/logs/traces),
- demonstrate reliability and security best practices.

## 2) Architecture
Diagram: `docs/architecture.md`

High-level:
- Kubernetes cluster (local kind/k3d in the first phase)
- ArgoCD (GitOps deploy)
- Sample API app
- Prometheus + Grafana (+ Alertmanager)
- Ingress + TLS (later with cert-manager)

## 3) Tech Stack
- Kubernetes (kind)
- ArgoCD
- Helm / Kustomize
- Prometheus + Grafana
- GitHub Actions

## 4) How to Run (MVP)
Prerequisites: `docker`, `kind`, `kubectl` (and optionally `helm`).

```bash
# 1) create cluster
make cluster-up

# 2) bootstrap platform components
make platform-bootstrap

# 3) deploy sample API
make app-deploy

# 4) verify health
make verify
```

## 5) CI/CD
- YAML lint + policy checks
- manifest validation
- deploy flow smoke test

## 6) Security & Reliability
- namespace isolation
- resource requests/limits
- readiness/liveness probes
- baseline network policies (next phase)

## 7) Results / Metrics
- deployment lead time
- MTTR for a simulated incident
- basic availability/SLO

## 8) What I'd improve next
- [ ] cert-manager + TLS everywhere
- [ ] external secrets flow
- [ ] HPA + load testing scenario
- [ ] chaos testing scenario

---

## Quick Technical Walkthrough
A 2-minute walkthrough should make these clear:
1. `docs/architecture.md`
2. `Makefile` workflow
3. `docs/runbook.md`
4. results in `docs/results.md`

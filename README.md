# Adrian Komorny — DevOps & Software Portfolio

A concise collection of production-oriented projects (infrastructure + software) that demonstrate:
- infrastructure as code design
- cloud-native operations
- observability, reliability, and security best practices
- end-to-end delivery skills

## ⚡ Project Index (Quick Overview)

| Project | Domain | Stack | First checkpoints |
|---|---|---|---|
| [k8s-platform-lab](./projects/k8s-platform-lab/README.md) | Platform Engineering | Kubernetes, ArgoCD, Helm, Prometheus | `Architecture`, `Runbook`, `Results` |
| [terraform-cloud-foundation](./projects/terraform-cloud-foundation/README.md) | IaC / Cloud | Terraform, OPA/Conftest, GitHub Actions | `Modules`, `Policy checks`, `CI pipeline` |
| [production-api-service](./projects/production-api-service/README.md) | Backend + Ops | Go/Node, Postgres, Docker, OpenTelemetry | `SLO`, `Tracing`, `Deployment strategy` |
| [vm2-docker-deploy](./projects/vm2-docker-deploy/README.md) | Deployment Runtime | Docker, Docker Compose, GHCR, SSH | `Architecture`, `Operations`, `Scripts` |

## Repository Structure

```text
.
├─ docs/
│  ├─ architecture-principles.md
│  ├─ decision-log.md
│  └─ project-walkthrough.md
├─ projects/
│  ├─ k8s-platform-lab/
│  ├─ terraform-cloud-foundation/
│  ├─ production-api-service/
│  └─ vm2-docker-deploy/
└─ README.md
```

## Standards for Every Project

Each project README should include these sections:
1. **Problem / Goal** (what it solves and why)
2. **Architecture** (diagram + components)
3. **Tech Stack**
4. **How to Run**
5. **CI/CD**
6. **Security & Reliability**
7. **Results / Metrics**
8. **What I'd improve next**

## Engineering Quality Bar

- clear scope and context
- transparent trade-offs
- monitoring + alerting + runbooks
- tests and quality gates in CI
- concise and consistent documentation

---

The repository goal is to keep projects technically consistent, reproducible, and easy to understand.

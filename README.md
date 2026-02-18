# Adrian Komorny — DevOps & Software Portfolio

Krátky prehľad produkčne orientovaných projektov (infra + software), ktoré ukazujú:
- návrh infraštruktúry ako kód
- cloud-native prevádzku
- observability, reliability a security best practices
- schopnosť dodávať end-to-end riešenia

## ⚡ Project Index (Quick Overview)

| Project | Domain | Stack | First checkpoints |
|---|---|---|---|
| [k8s-platform-lab](./projects/k8s-platform-lab/README.md) | Platform Engineering | Kubernetes, ArgoCD, Helm, Prometheus | `Architecture`, `Runbook`, `Results` |
| [terraform-cloud-foundation](./projects/terraform-cloud-foundation/README.md) | IaC / Cloud | Terraform, OPA/Conftest, GitHub Actions | `Modules`, `Policy checks`, `CI pipeline` |
| [production-api-service](./projects/production-api-service/README.md) | Backend + Ops | Go/Node, Postgres, Docker, OpenTelemetry | `SLO`, `Tracing`, `Deployment strategy` |

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
│  └─ production-api-service/
└─ README.md
```

## Standards for Every Project

Každý projekt musí mať v README tieto sekcie:
1. **Problem / Goal** (čo rieši a prečo)
2. **Architecture** (diagram + komponenty)
3. **Tech Stack**
4. **How to Run**
5. **CI/CD**
6. **Security & Reliability**
7. **Results / Metrics**
8. **What I'd improve next**

## Engineering Quality Bar

- jasný scope a kontext
- transparentné trade-offy
- monitoring + alerting + runbooks
- testy a quality gates v CI
- stručná a konzistentná dokumentácia

---

Cieľ repozitára je udržať projekty technicky konzistentné, reprodukovateľné a dobre čitateľné.

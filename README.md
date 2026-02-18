# Adrian Komorny — DevOps & Software Portfolio

Krátky prehľad produkčne orientovaných projektov (infra + software), ktoré ukazujú:
- návrh infraštruktúry ako kód
- cloud-native prevádzku
- observability, reliability a security best practices
- schopnosť dodávať end-to-end riešenia

## ⚡ Quick Interview Index (2–3 min)

| Project | Domain | Stack | What to look at first |
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
│  └─ interview-walkthrough.md
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

## What Recruiters Usually Appreciate

- jasný scope a business context
- reálne trade-offy (nie len „happy path“)
- monitoring + alerting + runbooks
- testy a quality gates v CI
- stručnosť a čitateľnosť dokumentácie

---

Ak si recruiter vie za 2 min prejsť index + jeden README a pochopí, že vieš dodať systém v produkčnej kvalite, cieľ je splnený.

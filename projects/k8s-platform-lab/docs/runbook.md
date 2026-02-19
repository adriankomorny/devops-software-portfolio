# Runbook

## Incident: app returns 5xx
1. `kubectl get pods -n app`
2. `kubectl logs deploy/sample-api -n app --tail=100`
3. `kubectl describe pod <pod> -n app`
4. check Grafana dashboard (error rate, latency)
5. roll back deployment if the latest release introduced a regression

## Recovery target
- restore baseline service availability within 15 minutes

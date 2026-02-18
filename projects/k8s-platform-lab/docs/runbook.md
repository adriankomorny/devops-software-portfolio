# Runbook

## Incident: app returns 5xx
1. `kubectl get pods -n app`
2. `kubectl logs deploy/sample-api -n app --tail=100`
3. `kubectl describe pod <pod> -n app`
4. check Grafana dashboard (error rate, latency)
5. rollback deployment, ak posledný release spôsobil regresiu

## Recovery target
- do 15 min obnoviť základnú dostupnosť služby

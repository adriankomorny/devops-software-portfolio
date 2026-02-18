# Results

## Baseline metrics (Sprint 1)
- cluster status: `platform-lab` created (kind)
- app replicas: `2/2 Running`
- service: `sample-api` (ClusterIP, port 80 -> 5678)
- verify target: passed (`make verify`)

## Evidence snapshot
```text
NAME                          READY   STATUS    RESTARTS   AGE
sample-api-7f6d877c88-glrlk   1/1     Running   0          33s
sample-api-7f6d877c88-mswk4   1/1     Running   0          33s

NAME         TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
sample-api   ClusterIP   10.96.243.56   <none>        80/TCP    36s
```

## Next measurements
- p95 latency under load
- deployment lead time (from commit to rollout complete)
- basic availability window (24h)

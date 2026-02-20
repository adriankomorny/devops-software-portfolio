# Operations

## Prerequisites
- VM1: docker, curl, ssh, scp
- VM2: docker + docker compose plugin
- GHCR credentials configured on VM1 and VM2 (`docker login ghcr.io`)

## Build and push
```bash
./scripts/build_and_push.sh v0.1.0
```

## Deploy to VM2
```bash
cp .env.example .env
# edit VM2_HOST / VM2_USER / IMAGE_REPO if needed
./scripts/deploy_remote.sh v0.1.0
```

## Healthcheck only
```bash
./scripts/healthcheck_remote.sh
```

## Rollback
```bash
./scripts/rollback_remote.sh v0.0.9
```

## Logs on VM2
```bash
ssh vm2@192.168.56.101 'docker compose -f /home/vm2/docker-compose.yml logs -f'
```

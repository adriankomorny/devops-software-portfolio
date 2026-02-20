# docker-runtime-deploy

Lightweight deployment workflow for constrained environments where Kubernetes is unnecessary overhead.

## What this project provides
- a reusable deployment flow from VM1 to VM2
- a sample app with health/version endpoints
- scripts for build, deploy, healthcheck, and rollback
- versioned image rollout model using GHCR tags

## Project structure
```text
docker-runtime-deploy/
├─ sample-app/
├─ scripts/
├─ docs/
├─ docker-compose.yml
└─ .env.example
```

## Quick start
```bash
cp .env.example .env
# update VM2_HOST/VM2_USER/IMAGE_REPO

./scripts/build_and_push.sh v0.1.0
./scripts/deploy_remote.sh v0.1.0
./scripts/healthcheck_remote.sh
```

## Endpoints
- `/health`
- `/version`
- `/`

## Notes
- Use immutable tags (e.g. `v0.1.0`, git SHA), avoid `latest`.
- Keep `.env` out of git if it contains sensitive values.

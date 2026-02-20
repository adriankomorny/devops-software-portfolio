# docker-runtime-deploy

Lightweight deployment workflow for constrained environments where Kubernetes is unnecessary overhead.

## What this project provides
- a reusable deployment flow from VM1 to VM2
- a sample browser app with frontend + health/version endpoints
- Docker Compose runtime with PostgreSQL + persistent volume
- scripts for build, deploy, healthcheck, and rollback
- versioned image rollout model using GHCR tags

## Project structure
```text
docker-runtime-deploy/
├─ sample-browser-app/
├─ scripts/
├─ docs/
├─ docker-compose.yml
└─ .env.example
```

## Quick start
```bash
cp .env.example .env
# update VM2_HOST/VM2_USER/IMAGE_REPO and POSTGRES_* values

./scripts/build_and_push.sh v0.1.0
./scripts/deploy_remote.sh v0.1.0
./scripts/healthcheck_remote.sh
```

## Endpoints
- `/` (browser UI)
- `/health`
- `/version`
- `/api/message`

## Notes
- Use immutable tags (e.g. `v0.1.0`, git SHA), avoid `latest`.
- Keep `.env` out of git if it contains sensitive values.

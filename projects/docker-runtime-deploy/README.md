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
├─ counter-orion/
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

`deploy_remote.sh` now runs DB migrations automatically (`flask db upgrade`) before bringing up the full stack.

## Endpoints
- `/` (login/register UI)
- `/profile` (authenticated profile page)
- `/health`
- `/version`
- `/api/message`
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `GET /me` (Bearer access token)
- `GET /catalog/skins` (Bearer; pagination + filters)
- `GET /catalog/skins/search?q=...` (Bearer)
- `GET /skins` (Bearer; my inventory)
- `POST /skins` (Bearer; add to inventory)
- `PUT /skins/{id}` (Bearer; update inventory entry)
- `DELETE /skins/{id}` (Bearer; delete inventory entry)

## DB migration bootstrap (one-time for developers)
```bash
cd counter-orion
flask --app manage.py db init
flask --app manage.py db migrate -m "init users"
flask --app manage.py db upgrade
```

## Sprint 1 verification checklist
1. Open `http://localhost:8082`
2. Register a new user (email + username + password)
3. Login with email + password
4. Confirm redirect to `http://localhost:8082/profile`
5. On `/profile`, verify profile JSON loads
6. Logout and verify redirect back to `/`
7. (API) `GET /me` without token returns 401

## Sprint 2 / Task 1 schema baseline
- `skins_catalog` (central CS2 catalog)
- `user_skins` (user-owned inventory entries)
- migration revision: `07e6fa35699e`

## Sprint 2 / Task 2 catalog seed
- seed source file: `counter-orion/data/cs2_skins_seed.json`
- seed script: `counter-orion/scripts/seed_catalog.py`
- indexing/uniqueness migration: `21902f4f0fa1`
- current simplified catalog fields: `weapon`, `skin_name`, `rarity`
- currently allowed rarities: `Covert`, `Extraordinary`

Run seed in deployed stack:
```bash
cd /home/vm2
APP_PORT=8082 docker compose --env-file .env -f docker-compose.yml run --rm counter-orion python scripts/seed_catalog.py
```

## Notes
- Use immutable tags (e.g. `v0.1.0`, git SHA), avoid `latest`.
- Keep `.env` out of git if it contains sensitive values.

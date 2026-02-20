# Sprint 1 Plan — Auth + User Profile

Project: Orion (CS2 Skin Vault)
Sprint goal: Implement end-to-end authentication and user profile basics.

## Scope
- User registration
- User login
- JWT access token auth
- Refresh token endpoint
- Authenticated profile endpoint (`/me`)
- Frontend login/register/profile flow

## Tasks

### Backend
1. Add PostgreSQL + SQLAlchemy setup
2. Add Alembic migrations scaffold
3. Create `users` model
4. Implement password hashing (bcrypt/argon2)
5. Implement auth API:
   - `POST /auth/register`
   - `POST /auth/login`
   - `POST /auth/refresh`
6. Implement `GET /me` (requires access token)
7. Add validation + error handling

### Frontend
1. Create login page
2. Create register page
3. Store and use JWT (basic secure approach for V1)
4. Create profile page and fetch `/me`
5. Add logout action

### Infra
1. Add PostgreSQL service to docker-compose
2. Add DB env variables to `.env.example`
3. Add healthcheck for API + DB dependency order

## Acceptance Criteria
- New user can register and login
- Logged-in user can call `/me` successfully
- Unauthenticated request to `/me` fails (401)
- Frontend supports register → login → profile → logout flow
- App and DB run via docker-compose locally and on VM2

## Out of scope
- Skins CRUD
- Advanced RBAC
- Social login

## Deliverables
- Working Sprint 1 implementation
- Updated README with run instructions
- Short demo script for verification

# Deployment Guide

Step-by-step instructions for deploying PayVerify AI from a clean checkout to a live,
production-configured environment.

## Prerequisites

- Docker + Docker Compose (local/self-hosted deployment) **or** a Render account
  (managed deployment)
- A Neon PostgreSQL project (or any managed Postgres) — production deployments only;
  local Docker Compose ships its own Postgres container
- An Upstash Redis database (or any managed Redis) — optional but recommended for
  AI Gateway caching (Phase 3.5)
- A Google Gemini API key (optional — the app runs fully functional with a
  deterministic stub explainer if omitted)

## Option A — Local / Self-Hosted (Docker Compose)

1. Clone the repository and change into it:
   ```bash
   git clone <repo-url> payverify-ai
   cd payverify-ai
   ```
2. Copy the environment template and fill in secrets:
   ```bash
   cp .env.example .env
   ```
   At minimum, set a real `POSTGRES_PASSWORD`. Leave `GEMINI_API_KEY` blank to use
   the stub explainer, or leave `AUTH_ENABLED=false` for the simplest local setup.
3. Build and start all services:
   ```bash
   docker compose up --build
   ```
   This starts Postgres, Redis, the FastAPI backend (port 8000), and the Next.js
   frontend (port 3000), all health-checked before dependents start.
4. The backend automatically applies Alembic migrations on startup (see
   `backend/entrypoint.sh`) — no manual migration step needed.
5. Verify:
   - Frontend: http://localhost:3000
   - Backend docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health
   - Readiness: http://localhost:8000/status

## Option B — Render (managed, production)

Full walkthrough: [docs/deployment/render-deployment.md](../deployment/render-deployment.md).
Summary:

1. Create external managed services:
   - Neon PostgreSQL project → copy the `DATABASE_URL` connection string
   - Upstash Redis database → copy the `REDIS_URL` (TLS/`rediss://`) connection string
2. Generate an admin password hash for JWT auth:
   ```bash
   python scripts/hash_password.py
   ```
   Save the printed bcrypt hash — you'll paste it into Render as `ADMIN_PASSWORD_HASH`.
3. Generate a JWT signing secret:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```
4. Push `render.yaml` to your repository's default branch, then in the Render
   dashboard: **New → Blueprint**, point it at the repo. Render provisions both
   `payverify-backend` and `payverify-frontend` services.
5. When prompted for the `sync: false` secrets, provide:
   - `DATABASE_URL`, `REDIS_URL` (from step 1)
   - `GEMINI_API_KEY` (optional)
   - `JWT_SECRET` (from step 3)
   - `ADMIN_USERNAME` (pick a value, e.g. `admin`)
   - `ADMIN_PASSWORD_HASH` (from step 2)
6. After the first deploy, confirm the actual assigned URLs (Render appends a
   random suffix if your service name is taken) and update `CORS_ALLOWED_ORIGINS`
   (backend) / `NEXT_PUBLIC_API_BASE_URL` (frontend) env vars to match, then
   redeploy.
7. Verify:
   - `GET https://<backend-url>/health` → `{"status": "ok"}`
   - `GET https://<backend-url>/status` → all dependencies `healthy: true`
   - Frontend loads and can create a project without CORS errors

## Applying Database Migrations

Migrations are managed by Alembic (`migrations/`). They run automatically on every
container start via `backend/entrypoint.sh` (`alembic upgrade head`), so day-to-day
deploys require no manual step. To run them manually (e.g. against a fresh Neon
instance, or to check pending migrations before a deploy):

```bash
# Point at the target database
export DATABASE_URL="postgresql://user:pass@host/dbname"

# See current revision applied to the DB
python -m alembic current

# See pending migrations
python -m alembic history

# Apply all pending migrations
python -m alembic upgrade head
```

## Creating a New Migration

When you change `backend/app/models.py`:

```bash
python -m alembic revision --autogenerate -m "describe the change"
```

Always review the generated file in `migrations/versions/` before committing —
autogenerate does not reliably detect every change (e.g. some column type changes,
server defaults, check constraints) and may need manual edits.

## Post-Deployment Verification Checklist

- [ ] `/health` responds 200 in <50ms
- [ ] `/status` shows all dependencies `healthy: true`
- [ ] `/metrics` returns Prometheus-formatted output
- [ ] Frontend can create a project, upload registers, run validation end-to-end
- [ ] `POST /auth/token` issues a token (if `AUTH_ENABLED=true`)
- [ ] Mutating endpoints (`POST /api/projects`, etc.) reject requests without a
      valid bearer token (if `AUTH_ENABLED=true`)
- [ ] CORS only allows the actual deployed frontend origin (not `*`)

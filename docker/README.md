# Running PayVerify AI with Docker

This runs the full stack — frontend, backend, PostgreSQL, Redis, and an Nginx reverse proxy —
with a single command. Useful for local parity-with-production testing, demos, or as a base
for cloud deployment (Phase 3.4).

## Prerequisites

- Docker Desktop (or Docker Engine + Compose plugin) installed and running.

## Quick start

```powershell
cd payverify-ai
Copy-Item .env.example .env   # then edit .env if you want a real GEMINI_API_KEY
docker compose up --build
```

Once all services report healthy:

| URL | What it is |
|---|---|
| http://localhost:8080 | Full app via Nginx (frontend + `/api/*` proxied to backend) |
| http://localhost:3000 | Frontend directly (bypasses Nginx — for debugging) |
| http://localhost:8000/docs | Backend OpenAPI/Swagger docs directly |
| http://localhost:8000/health | Backend liveness check |

Use **http://localhost:8080** as the main entry point — it's the single origin the frontend's
bundled `NEXT_PUBLIC_API_BASE_URL` is built against, and the origin Nginx proxies both the UI
and the API from (no CORS involved at that entry point).

## What each service does

- **postgres** — PostgreSQL 16, replaces SQLite for containerized/deployed runs. Data persists
  in the `postgres_data` named volume across restarts.
- **redis** — Redis 7. Not yet used by the application (reserved for the Phase 3.5 AI Gateway
  caching layer), but included now so the compose topology matches the target deployment shape.
- **backend** — FastAPI app, built from [`backend/Dockerfile`](../backend/Dockerfile) (build
  context is the repo root, since the app imports sibling `rule-engine/`, `validation-engine/`,
  `services/`, and `agents/` directories). Connects to `postgres` via `DATABASE_URL` and waits
  for it to report healthy before starting.
- **frontend** — Next.js app, built from [`frontend/Dockerfile`](../frontend/Dockerfile) using
  the `output: "standalone"` build for a minimal image. `NEXT_PUBLIC_API_BASE_URL` is baked in
  at build time via a Docker build arg (Next.js inlines `NEXT_PUBLIC_*` vars at build, not
  runtime — changing it requires a rebuild).
- **nginx** — Reverse proxy exposed on port 8080. Routes `/api/*` to the backend and everything
  else to the frontend, so the browser only ever talks to one origin.

## Health checks

Every service has a health check:

- `postgres` — `pg_isready`
- `redis` — `redis-cli ping`
- `backend` — Dockerfile-defined `HEALTHCHECK` hitting `GET /health`
- `frontend` — Dockerfile-defined `HEALTHCHECK` hitting `GET /`
- `nginx` — compose-defined check hitting its own `/health` location

`docker compose ps` shows the health status of each container. `backend`/`frontend` startup is
gated on their dependencies (`postgres`/`redis`, `backend` respectively) being healthy first via
`depends_on: condition: service_healthy`.

## Rebuilding after code changes

```powershell
docker compose up --build
```

To rebuild a single service:

```powershell
docker compose build backend
docker compose up -d backend
```

## Stopping / cleaning up

```powershell
docker compose down          # stop containers, keep the postgres_data volume
docker compose down -v       # stop containers AND delete the postgres_data volume (data loss)
```

## Switching the backend back to SQLite

The backend defaults to SQLite (`backend/payverify.db`) whenever `DATABASE_URL` is unset — this
is what running the backend directly with `uvicorn` (outside Docker) still does. `DATABASE_URL`
is only set inside `docker-compose.yml`, pointing at the `postgres` service.

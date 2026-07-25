# Phase 3.1 — Dockerization

**Goal:** Containerize the application for cloud deployment.

## Context

PayVerify AI currently consists of:

- **Frontend:** Next.js 16 + React 19 + TypeScript + Tailwind CSS (App Router, `frontend/`)
- **Backend:** Python FastAPI (`backend/app/main.py`), SQLite (`backend/payverify.db`)
- **AI:** Claude Sonnet integration for variance explanation only (`agents/explanation_agent.py`),
  with a deterministic stub fallback — never used for the actual statutory calculation
- **Tests:** 59 passing pytest tests (`tests/`)

For containerized/cloud deployment, the database moves from SQLite to **PostgreSQL**, and
**Redis** is introduced for caching (e.g. mapping-suggestion caching, AI explanation caching).

## Tasks

1. Create production-ready Dockerfiles for the frontend and backend.
2. Use multi-stage Docker builds to minimize final image size.
3. Create a `docker-compose.yml` that starts:
   - Frontend
   - Backend
   - PostgreSQL
   - Redis
   - Nginx reverse proxy
4. Add health checks for every service.
5. Configure environment variables using a `.env.example` file.
6. Ensure `docker compose up` starts the entire application end-to-end.
7. Generate documentation for running the stack locally via Docker.

## Deliverable

```
docker/
docker-compose.yml
Dockerfiles          (frontend/Dockerfile, backend/Dockerfile)
.env.example
README (docker/README.md — local Docker usage instructions)
```

## Acceptance Criteria

- `docker compose up` brings up all 5 services with no manual steps.
- Backend switches its SQLAlchemy connection string to PostgreSQL when running in Docker
  (via `DATABASE_URL` env var), while still supporting SQLite for local non-Docker dev.
- All existing 59 pytest tests still pass inside the backend container.
- Nginx correctly proxies `/` to the frontend and `/api` (or similar) to the backend.
- Health check endpoints return 200 for frontend, backend, Postgres, and Redis.

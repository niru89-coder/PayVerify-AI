# Phase 3.4 — Render Deployment

**Goal:** Deploy PayVerify AI to production using free/low-cost managed services.

## Target services

- **Backend:** Render (Web Service, Docker-based, from Phase 3.1 backend image)
- **Frontend:** Render (Static Site or Web Service) — or Vercel if simpler for Next.js
- **Database:** Neon PostgreSQL (managed, serverless Postgres)
- **Redis:** Upstash (managed, serverless Redis)

## Tasks

Configure:

- Environment variables per service (`DATABASE_URL` from Neon, `REDIS_URL` from Upstash,
  `ANTHROPIC_API_KEY`, `NEXT_PUBLIC_API_BASE_URL` pointing at the deployed backend URL)
- Custom domains (optional)
- Automatic deployment from GitHub (on merge to `main`, via Render's GitHub integration or the
  `deploy.yml` workflow from Phase 3.3)
- Health checks (Render health check path hitting the `/health` endpoint from Phase 3.6)
- HTTPS (enabled by default on Render/Vercel/Neon/Upstash — verify and document)
- Logging (Render's built-in log streaming; document how to access it)

## Deliverable

- `render.yaml` (Render Blueprint defining backend + frontend services)
- Deployment documentation: `docs/deployment/render-deployment.md` covering:
  - Step-by-step account setup for Render, Neon, Upstash
  - How to wire environment variables/secrets
  - How to trigger and verify a deployment
  - How to view logs and roll back

## Acceptance Criteria

- The deployed frontend can talk to the deployed backend over HTTPS with no CORS errors.
- The deployed backend connects successfully to Neon Postgres and Upstash Redis.
- A push to `main` results in an automatic, verified deployment within a few minutes.

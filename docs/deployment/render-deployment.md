# Render Deployment Guide

This guide walks through deploying PayVerify AI's backend and frontend to
[Render](https://render.com) using the Blueprint at [`render.yaml`](../../render.yaml),
with [Neon](https://neon.tech) providing managed PostgreSQL and
[Upstash](https://upstash.com) providing managed Redis.

Render hosts the two Docker-based web services (`payverify-backend`,
`payverify-frontend`). Neon and Upstash are **not** Render resources - they're
external managed services that the backend connects to over the internet via
`DATABASE_URL` and `REDIS_URL`.

## 1. Create the external managed services

### 1.1 Neon (PostgreSQL)

1. Sign up at [neon.tech](https://neon.tech) and create a new project (any
   region; picking one close to Render's `singapore` region minimizes latency).
2. Open the project's **Connection Details** panel and copy the connection
   string. It looks like:
   ```
   postgresql://<user>:<password>@<host>.neon.tech/<database>?sslmode=require
   ```
3. **Do not change the scheme yourself** - the backend
   ([`backend/app/database.py`](../../backend/app/database.py)) automatically
   rewrites `postgres://`/`postgresql://` to `postgresql+psycopg://` so it
   works with the `psycopg` v3 driver already in
   [`requirements.txt`](../../requirements.txt). Paste the string exactly as
   Neon gives it to you.
4. Keep this connection string handy for step 3 (`DATABASE_URL`).

### 1.2 Upstash (Redis)

1. Sign up at [upstash.com](https://upstash.com) and create a new Redis
   database (again, a region close to `singapore` is ideal).
2. From the database's **Details** page, copy the **Redis connection string**
   (the `rediss://...` URL, which uses TLS - Upstash's default).
3. Keep this connection string handy for step 3 (`REDIS_URL`).

## 2. Push the Blueprint

The Blueprint file already lives at the repo root: [`render.yaml`](../../render.yaml).
Make sure it's committed and pushed to the `main` branch of
`niru89-coder/PayVerify-AI` before continuing (Render reads it directly from
GitHub).

## 3. Create the Blueprint on Render

1. Sign up / log in at [dashboard.render.com](https://dashboard.render.com).
2. Click **New > Blueprint**.
3. Connect your GitHub account if you haven't already, then select the
   `niru89-coder/PayVerify-AI` repository.
4. Render detects `render.yaml` and shows a preview of the two services
   (`payverify-backend`, `payverify-frontend`).
5. Because `DATABASE_URL`, `REDIS_URL`, and `GEMINI_API_KEY` are declared
   with `sync: false` in `render.yaml`, Render prompts you to fill in a value
   for each before creating the services:
   - **`DATABASE_URL`**: paste the Neon connection string from step 1.1.
   - **`REDIS_URL`**: paste the Upstash connection string from step 1.2.
   - **`GEMINI_API_KEY`**: optional. Paste a real
     [Gemini API key](https://aistudio.google.com/apikey) to get
     AI-generated variance explanations, or leave it blank - the backend
     automatically falls back to a deterministic, rule-based explanation
     (`StubExplanationProvider`) with no loss of core functionality.
6. Click **Apply** / **Create New Resources**. Render builds both Docker
   images and deploys them.

## 4. Verify the deployment

1. Watch the build logs for each service from its **Deploys** page in the
   Render Dashboard until both show a healthy deploy.
2. Note the two assigned public URLs.
   - `render.yaml` assumes the services get `https://payverify-backend.onrender.com`
     and `https://payverify-frontend.onrender.com`. Render normally hands out
     exactly `https://<name>.onrender.com`, but if either name was already
     taken, Render appends a random suffix instead.
3. **If either URL differs from the assumed one**, update the affected
   environment variable and redeploy:
   - Backend service → `CORS_ALLOWED_ORIGINS` must equal the frontend's actual
     URL (no trailing slash).
   - Frontend service → `NEXT_PUBLIC_API_BASE_URL` must equal the backend's
     actual URL (no trailing slash), then **manually trigger a new deploy**
     for the frontend - this value is baked into the browser bundle at Docker
     build time via Render's [environment variable
     translation](https://render.com/docs/docker#environment-variable-translation),
     so a plain env var change without a rebuild has no effect.
4. Open the frontend URL in a browser. Confirm:
   - The page loads over HTTPS with a valid certificate (Render provisions
     this automatically).
   - No CORS errors appear in the browser console when the frontend calls the
     backend.
   - Creating/viewing a project round-trips through the backend successfully.
5. Confirm the backend health check: `https://<backend-url>/health` should
   return `200 OK`. Render also polls this path automatically (configured via
   `healthCheckPath` in `render.yaml`) and will restart the service if it
   fails.

## 5. Auto-deploy on push

`render.yaml` sets `autoDeployTrigger: commit` for both services, so once the
Blueprint is created, every push to `main` (including the deploys triggered by
[`.github/workflows/deploy.yml`](../../.github/workflows/deploy.yml)) causes
Render to rebuild and redeploy automatically - no extra setup required.

To also let the CI/CD pipeline notify Render directly (rather than relying
solely on Render's own GitHub polling), add each service's **Deploy Hook**
URL (Service → **Settings** → **Deploy Hook**) as the
`RENDER_DEPLOY_HOOK_BACKEND` / `RENDER_DEPLOY_HOOK_FRONTEND` repository
secrets used by `deploy.yml`.

## 6. Viewing logs

Each service's **Logs** tab in the Render Dashboard streams build and runtime
logs live, and supports filtering/searching. No extra configuration is
required beyond what's in `render.yaml`.

## 7. Rolling back

Two options, from quickest to most manual:

1. **Render Dashboard**: open the service's **Deploys** page and click
   **Rollback** next to any previous successful deploy (uses Render's
   [instant rollback](https://render.com/docs/rollbacks) feature).
2. **GitHub Actions**: run the
   [`rollback.yml`](../../.github/workflows/rollback.yml) workflow manually
   (`workflow_dispatch`), supplying the Render `render_service_id` (found in
   the service's Dashboard URL or Settings page) and optionally a specific
   `deploy_id`. Requires the `RENDER_API_KEY` repository secret to be set.

## Notes / limitations

- Both services use the **free** Render plan (per `render.yaml`), which spins
  down after inactivity and cold-starts on the next request - acceptable for
  an MVP, but worth upgrading to a paid plan before real production traffic.
- Neon and Upstash are not provisioned by `render.yaml` - they must be created
  manually as described in step 1, since they're external to Render.
- `/status` and `/metrics` endpoints (deeper dependency + usage monitoring)
  are introduced in Phase 3.6 and are not required for this deployment to
  function - only `/health` is used here.

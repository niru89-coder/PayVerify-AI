# Release Checklist

A literal, step-by-step checklist to run through before every production
release. Intended to be followed by someone unfamiliar with the codebase.

## 1. Pre-Merge (CI)

- [ ] All CI checks green on the pull request (`ci.yml`: ruff lint, pip-audit,
      pytest, eslint, npm audit)
- [ ] No new dependency introduces a known critical/high vulnerability
      (`pip-audit` / `npm audit` output reviewed, not just "passed")
- [ ] If `backend/app/models.py` changed: an Alembic migration was generated
      (`python -m alembic revision --autogenerate -m "..."`) and is included in
      the PR — reviewed by hand, not blindly trusted
- [ ] If a new environment variable was introduced: it's documented in
      `.env.example` with a comment explaining its purpose and default

## 2. Local Verification

- [ ] `python -m pytest tests/ -q` passes (all tests, no skips added to hide
      failures)
- [ ] `docker compose up --build` starts cleanly from a clean checkout (no
      cached state assumed)
- [ ] `GET http://localhost:8000/health` → `{"status": "ok"}`
- [ ] `GET http://localhost:8000/status` → all dependencies `healthy: true`
- [ ] Manually exercise the full pipeline once end-to-end via the frontend UI:
      create project → upload employee master → upload client + platform
      registers → run validation → view variances → submit feedback

## 3. Secrets & Security

- [ ] No secrets committed to git — run a scan before release:
      ```bash
      git log -p | grep -iE "(api[_-]?key|secret|password|token)\s*=" 
      ```
      or use a dedicated tool (gitleaks, trufflehog) if available
- [ ] `DEBUG=false` in the production environment (confirm in the Render
      dashboard, not just `.env.example`)
- [ ] `AUTH_ENABLED=true` in the production environment
- [ ] `CORS_ALLOWED_ORIGINS` on the backend matches the actual deployed
      frontend origin exactly (not `*`, not a stale URL from a previous
      deploy)
- [ ] `JWT_SECRET` and `ADMIN_PASSWORD_HASH` are set via the platform's secret
      manager (Render dashboard `sync: false` prompt), not hardcoded in
      `render.yaml`

## 4. Database

- [ ] Pending migrations reviewed: `python -m alembic history` shows the
      expected chain, no unexpected branches
- [ ] Migration tested against a disposable copy of production-like data
      before applying to the real production database (or rely on
      `backend/entrypoint.sh`'s automatic `alembic upgrade head` only after
      confirming the migration is safe/reversible)
- [ ] Neon (or your Postgres provider) automated backups are confirmed enabled
      (see [operations-guide.md](operations-guide.md#backup--restore-neon-postgresql))

## 5. Deploy

- [ ] Push to the branch that triggers `deploy.yml` (typically `main`)
- [ ] Watch the GitHub Actions run to completion (build + push to GHCR +
      Render deploy hook)
- [ ] Watch the Render deploy logs for the target service(s) until "Live"
- [ ] Confirm `backend/entrypoint.sh`'s migration step succeeded (check deploy
      logs for "Applying database migrations" → no errors)

## 6. Post-Deploy Verification

- [ ] `GET https://<backend-url>/health` → 200 OK
- [ ] `GET https://<backend-url>/status` → all dependencies `healthy: true`
- [ ] `GET https://<backend-url>/metrics` → returns Prometheus text (not an
      error)
- [ ] Frontend loads without console errors (check for CORS/network issues)
- [ ] Create a test project through the live frontend, run the full pipeline,
      confirm a variance and its AI explanation render correctly
- [ ] `POST /auth/token` with valid admin credentials issues a token
- [ ] A mutating endpoint (`POST /api/projects`) rejects an unauthenticated
      request with 401

## 7. Rollback Plan (Have This Ready Before You Need It)

- [ ] Know the previous known-good Render deploy (Dashboard → service →
      Events/Deploys tab shows history) — Render supports one-click rollback
      to a previous successful deploy
- [ ] `rollback.yml` GitHub Action is available for a manual restore trigger
      if needed
- [ ] If the release included a database migration, confirm you have (or have
      written) the corresponding `downgrade()` in the migration file, and that
      it was tested (`python -m alembic downgrade -1`) against a disposable
      database before relying on it in an emergency

## 8. After Release

- [ ] Update `CHANGELOG.md` with what shipped
- [ ] Note any new known limitations in the relevant `docs/production/*.md`
      file (administrator-guide.md, troubleshooting-guide.md) — don't let gaps
      go undocumented

# Phase 3.7 — Production Readiness

**Goal:** Final validation and documentation pass before PayVerify AI is considered production-ready.

## Validate

- Docker images (build cleanly, correct size, no unnecessary layers/secrets baked in)
- Environment variables (all required vars documented in `.env.example`, no missing/unused vars)
- CI/CD (pipelines from Phase 3.3 green end-to-end, rollback tested at least once)
- Deployment (Render deployment from Phase 3.4 verified live)
- Database migration (a real migration tool — e.g. Alembic — in place for schema changes,
  not just `create_all()`; verify a migration applies cleanly to a fresh Neon Postgres instance)
- Secrets (no secrets committed to git history; confirm via a secret-scanning pass)
- Logging (structured logs from Phase 3.6 present and useful in the deployed environment)
- API security (input validation, rate limiting on public endpoints, HTTPS enforced, CORS
  restricted to the actual frontend origin — not `*`)
- Authentication (basic auth layer added — even if minimal, e.g. API key or JWT — since the MVP
  currently has none)
- Authorization (role separation if applicable — e.g. consultant vs admin — or explicitly
  documented as out of scope for this release)
- Performance (basic load test on the validation-run endpoint with a realistic employee count)
- Error handling (no unhandled exceptions leak stack traces to API responses in production mode)
- Backup strategy (Neon Postgres automated backups confirmed enabled; document restore procedure)

## Produce

- **Deployment Guide** — step-by-step, from a clean checkout to a live deployment
- **Operations Guide** — day-2 operations: how to check health, read logs, scale, rotate secrets
- **Troubleshooting Guide** — common failure modes and their fixes (DB connection errors, Claude
  API outages, CORS issues, failed deployments)
- **Administrator Guide** — how to manage projects/users/data retention (as applicable to this MVP)
- **Release Checklist** — a literal checklist to run through before every production release

## Deliverable

```
docs/production/
  deployment-guide.md
  operations-guide.md
  troubleshooting-guide.md
  administrator-guide.md
  release-checklist.md
```

## Acceptance Criteria

- Every item in "Validate" above has either a passing check or an explicit, documented
  known-limitation entry (no silent gaps).
- The Release Checklist can be followed by someone unfamiliar with the codebase to safely ship
  a new release.

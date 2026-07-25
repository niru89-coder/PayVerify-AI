# Phase 3.3 — CI/CD (GitHub Actions)

**Goal:** Automate build, test, and deployment via GitHub Actions.

## Pipeline stages

1. Install dependencies (Python + Node)
2. Build frontend (`npm run build`)
3. Build backend (import/syntax check, dependency install)
4. Run unit tests (`pytest tests/ -q`, frontend tests if/when added)
5. Run linting (ESLint for frontend, `ruff`/`flake8` for backend)
6. Security scan (`npm audit`, `pip-audit` or `safety`, Docker image scan e.g. Trivy)
7. Build Docker images (frontend + backend, from Phase 3.1 Dockerfiles)
8. Publish Docker images (to GitHub Container Registry or Docker Hub)
9. Deploy automatically to Render (on merge to `main`)

## Requirements

- Store all secrets (Render API key/service IDs, Docker registry credentials, `ANTHROPIC_API_KEY`,
  database URLs) using **GitHub Secrets** — never hardcoded in workflow files.
- Provide rollback support (e.g. Render's built-in rollback-to-previous-deploy, or a workflow
  step that redeploys the previous known-good image tag on failure).
- Pipeline must fail fast — later stages (build/publish/deploy) must not run if tests or lint fail.
- Use path filters or a matrix so frontend-only or backend-only changes don't rebuild everything
  unnecessarily (optional optimization).

## Deliverable

```
.github/workflows/
  ci.yml           (install, build, test, lint, security scan — runs on every PR)
  deploy.yml       (build+publish Docker images, deploy to Render — runs on merge to main)
```

## Acceptance Criteria

- Opening a PR triggers `ci.yml` and shows pass/fail status checks before merge is allowed.
- Merging to `main` triggers `deploy.yml`, which builds, publishes, and deploys automatically.
- A failed deployment can be rolled back without manual server access.

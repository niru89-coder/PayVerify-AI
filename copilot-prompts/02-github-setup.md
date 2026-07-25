# Phase 3.2 — GitHub Repository Setup

**Goal:** Prepare the repository for enterprise-grade collaborative development.

## Tasks

Configure:

- Branch strategy (e.g. `main` protected, `develop`, feature branches, PR-only merges to `main`)
- GitHub Issue templates (bug report, feature request)
- Pull Request template
- `CODEOWNERS`
- `.gitignore` (Python `.venv`, `__pycache__`, `node_modules`, `.next`, `payverify.db`, `.env*`)
- `CONTRIBUTING.md`
- `SECURITY.md` (vulnerability disclosure process)
- `LICENSE`
- Semantic Versioning policy (documented, e.g. in `CONTRIBUTING.md` or a `VERSIONING.md`)
- `CHANGELOG.md` (Keep a Changelog format, starting at `0.1.0`)
- `README.md` — must include:
  - Architecture diagram (three-way comparison: Client Register vs Platform Register vs
    deterministic Rule Engine, with AI explanation-only layer)
  - Deployment instructions
  - API documentation (link to FastAPI `/docs`, plus a summary table of key endpoints)
  - Screenshots of the frontend (Dashboard, Variance Dashboard, Drill-Down)
  - Troubleshooting section

## Deliverable

```
.github/
  ISSUE_TEMPLATE/
  PULL_REQUEST_TEMPLATE.md
  CODEOWNERS
.gitignore
CONTRIBUTING.md
SECURITY.md
LICENSE
CHANGELOG.md
README.md (updated)
```

## Acceptance Criteria

- A new contributor can clone the repo and follow `README.md` + `CONTRIBUTING.md` to get a
  working local environment without asking questions.
- Opening a new GitHub Issue offers a choice of templates.
- Opening a PR auto-populates the PR template and requests review from `CODEOWNERS`.

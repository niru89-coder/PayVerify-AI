# Contributing to PayVerify AI

Thanks for your interest in contributing. This document covers branch strategy, commit
conventions, and the PR process.

## Branch strategy

- `main` — protected, always deployable. Direct pushes are disabled; changes land via PR only.
- `develop` — integration branch for the next release (optional; skip for small teams and PR
  straight to `main` if preferred).
- Feature branches: `feature/<short-description>` (e.g. `feature/pcb-rule-implementation`)
- Bug fix branches: `fix/<short-description>` (e.g. `fix/nginx-upload-size-limit`)
- Release branches (once versioning is in use): `release/vX.Y.Z`

Rebase or squash-merge feature branches into `main`/`develop` to keep history readable.

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/) style where practical:

```
feat: add PCB Schedule 1 calculation
fix: raise nginx client_max_body_size for large register uploads
docs: update deployment guide for Render
chore: bump fastapi to 0.140.0
```

## Development setup

See [README.md](README.md) for full backend/frontend setup instructions. Quick summary:

```powershell
# Backend
cd payverify-ai
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pytest tests\ -q
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --port 8000

# Frontend (separate terminal)
cd payverify-ai\frontend
npm install
npm run dev
```

Or via Docker — see [docker/README.md](docker/README.md).

## Before opening a PR

- [ ] `pytest tests/ -q` passes (backend)
- [ ] `npm run build` and `npm run lint` pass (frontend, if touched)
- [ ] New behavior has test coverage
- [ ] Statutory rule changes cite the exact source document/clause and update
      `rules/`, `knowledge-base/`, and `metadata/` accordingly — rule correctness is the single
      most important property of this codebase; deterministic calculations must never be
      "adjusted" without a traceable legal/regulatory source
- [ ] `CHANGELOG.md` updated for any user-facing change

Fill out the PR template completely — reviewers will ask you to if you don't.

## Semantic Versioning

This project follows [SemVer](https://semver.org/): `MAJOR.MINOR.PATCH`.

- **MAJOR** — breaking API/schema changes, or a statutory rule change that alters previously
  computed results in a way existing consumers must account for.
- **MINOR** — new backwards-compatible functionality (new rule, new screen, new endpoint).
- **PATCH** — backwards-compatible bug fixes.

Current version: see [CHANGELOG.md](CHANGELOG.md). Pre-1.0 (`0.x.y`) releases may include
breaking changes in MINOR bumps, per SemVer's pre-release convention — this will be called out
explicitly in the changelog entry when it happens.

## Code of conduct

Be respectful and constructive. This is a small project; assume good faith and ask questions
in the issue/PR before assuming malice or incompetence.

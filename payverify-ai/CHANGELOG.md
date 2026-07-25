# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Phase 3.1: Dockerization — multi-stage Dockerfiles for backend/frontend, `docker-compose.yml`
  (Postgres + Redis + Nginx reverse proxy), `.env.example`, health checks on every service.
- Phase 3.2: Repository setup — issue/PR templates, `CODEOWNERS`, `CONTRIBUTING.md`,
  `SECURITY.md`, `LICENSE` (MIT), this changelog, root `.gitignore`.
- `DATABASE_URL` env-var support in the backend (PostgreSQL in Docker, SQLite for local dev).
- `CORS_ALLOWED_ORIGINS` env-var support (configurable allowed origins).
- Minimal `GET /health` liveness endpoint.

### Fixed
- Nginx `client_max_body_size` raised to 20m to allow larger Client/Platform register CSV
  uploads through the Docker Compose reverse-proxy entrypoint.

## [0.1.0] - 2026-07-25

Initial MVP.

### Added
- Deterministic rule engine for Malaysia statutory components: EPF, SOCSO, EIS, HRDF, PCB,
  Overtime, Proration (EIS/PCB pending SME validation — see README known limitations).
- Three-way reconciliation/validation engine (Client Register vs Platform Register vs
  Rule-Engine expected value) with 7-way variance classification.
- Column mapping engine (synonym + fuzzy matching to canonical component codes).
- FastAPI REST API: projects, employee master upload, client/platform register upload +
  mapping preview/confirm, validation run, variance list/detail/feedback, AI explanation,
  rule catalog.
- AI explanation agent: deterministic `StubExplanationProvider` by default, optional
  `ClaudeExplanationProvider` when `ANTHROPIC_API_KEY` is set. AI never computes or overrides a
  figure — it only narrates an already-classified variance.
- Next.js 16 + TypeScript + Tailwind frontend: Dashboard, New Project, Upload Wizard (employee
  master + client/platform register mapping), Variance Dashboard, Variance Drill-Down (AI
  explanation + consultant feedback), Rule Catalog.
- 59 passing pytest tests covering the rule engine, mapping engine, reconciliation logic, and
  API endpoints.

# Phase 3.6 — Monitoring

**Goal:** Add production-grade observability to the backend.

## Tasks

Build:

- Health API — is the process up at all (no dependency checks)
- Readiness API — are dependencies (Postgres, Redis, Anthropic reachability) actually usable
- Liveness API — should the orchestrator (Render/Docker) restart this instance
- Structured logging (JSON logs with request ID, timestamp, level, route, status, duration)
- Centralized error handling (a single FastAPI exception handler producing consistent error
  response shapes, with correlation IDs for tracing)
- Request tracing (a middleware assigning a request/correlation ID propagated through logs)
- Audit trail (persist who ran a validation, uploaded a register, submitted feedback, and when —
  likely a new `audit_log` table)
- Dashboard metrics (request counts, latency percentiles, variance counts by classification,
  Claude token usage from Phase 3.5)

## Endpoints to provide

- `GET /health` — liveness/basic health, always fast, no DB calls
- `GET /status` — readiness, checks DB + Redis + (optionally) Anthropic connectivity, returns
  per-dependency status
- `GET /metrics` — machine-readable metrics (Prometheus text format recommended) covering
  request counts/latency, variance classification counts, AI Gateway token usage and cache hit
  rate from Phase 3.5

## Deliverable

- `backend/app/routes/monitoring.py` (or equivalent) implementing the three endpoints above
- `backend/app/middleware/logging.py` (or equivalent) for structured logging + request tracing
- `audit_log` table + model + write hooks on key mutating endpoints
- Documentation: `docs/monitoring.md` explaining each endpoint and how to wire them into an
  external monitor (e.g. Render health checks, an uptime monitor, or a Grafana/Prometheus setup)

## Acceptance Criteria

- `/health` responds in under ~50ms with no external calls.
- `/status` accurately reflects a simulated Postgres or Redis outage as "unhealthy" for that
  dependency, without crashing the endpoint itself.
- `/metrics` output is scrapeable by Prometheus (or documented as JSON if that format is chosen
  instead — be explicit about which).
- Every request in the logs has a traceable correlation/request ID.

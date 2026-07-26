# Operations Guide (Day-2 Operations)

How to operate PayVerify AI once it is live: health checks, logs, scaling, secret
rotation, and routine maintenance.

## Checking Health

| Endpoint | Purpose | Expected response |
|---|---|---|
| `GET /health` | Is the process alive? | `{"status": "ok"}`, <50ms |
| `GET /status` | Are DB/Redis/Gemini reachable? | `status: "ready"`, all deps `healthy: true` |
| `GET /metrics` | Prometheus metrics | Text format; scrape with Prometheus/Grafana |

See [docs/monitoring.md](../monitoring.md) for full endpoint documentation and
example Prometheus/Grafana configuration.

**Quick manual check:**
```bash
curl -s https://<backend-url>/status | python -m json.tool
```
If any dependency shows `healthy: false`, see the
[Troubleshooting Guide](troubleshooting-guide.md).

## Reading Logs

Every request is logged as a single line of structured JSON to stdout (see
`backend/app/middleware/logging.py`), including a `request_id` correlating it
across the request lifecycle:

```json
{"request_id": "5c8b...", "timestamp": "2026-07-26T14:32:15Z", "level": "INFO", "method": "POST", "path": "/api/projects", "status": 201, "duration_ms": 45.2, "remote_addr": "203.0.113.7"}
```

**On Render:** Dashboard → service → Logs tab (or `render logs -f` via the CLI).

**On Docker Compose:**
```bash
docker compose logs -f backend
```

**Correlating a user-reported error:** ask for the `request_id` from the error
response body (every error response includes one, see
[troubleshooting-guide.md](troubleshooting-guide.md#reading-error-responses)),
then grep the logs:
```bash
docker compose logs backend | grep <request_id>
```

## Scaling

- **Render (free/starter plans):** scaling is manual via the dashboard (Settings →
  Scaling). The free plan is single-instance and sleeps after inactivity — expect
  a cold-start delay on the first request after idle.
- **Horizontal scaling:** the backend is stateless (all state in Postgres/Redis),
  so multiple instances behind a load balancer work without additional
  configuration. Ensure `DATABASE_URL`/`REDIS_URL` point at the same shared
  managed instances.
- **Database:** Neon scales storage/compute independently; check the Neon
  dashboard for connection limits if you scale backend instances up.

## Rotating Secrets

| Secret | How to rotate |
|---|---|
| `JWT_SECRET` | Generate a new value (`python -c "import secrets; print(secrets.token_urlsafe(48))"`), update the env var, redeploy. **All existing tokens are invalidated immediately** — clients must re-authenticate via `/auth/token`. |
| `ADMIN_PASSWORD_HASH` | Run `python scripts/hash_password.py`, update the env var, redeploy. |
| `GEMINI_API_KEY` | Rotate in Google AI Studio, update the env var, redeploy. No downtime — falls back to the stub explainer if temporarily blank. |
| `DATABASE_URL` / `REDIS_URL` password | Rotate in the Neon/Upstash dashboard, update the env var, redeploy. |

Never commit secrets to git. `.env` is gitignored; Render secrets use `sync: false`
in `render.yaml` and are entered directly in the dashboard.

## Database Migrations in Production

Migrations apply automatically on every container start
(`backend/entrypoint.sh` runs `alembic upgrade head` before starting uvicorn).
To check migration status without deploying:
```bash
DATABASE_URL=<prod-url> python -m alembic current
DATABASE_URL=<prod-url> python -m alembic history
```

## Backup & Restore (Neon PostgreSQL)

Neon's free and paid tiers include automated point-in-time recovery (PITR) with a
retention window (check your plan — typically 7 days on paid, less on free).

**To confirm backups are enabled:** Neon dashboard → your project → Backup/Restore
tab.

**To restore:**
1. Neon dashboard → Backup/Restore → choose a timestamp
2. Restore to a new branch (non-destructive — does not touch the live branch)
3. Verify data on the new branch, then update `DATABASE_URL` to point at it (or
   promote the branch), and redeploy the backend

**Known limitation:** this MVP does not run its own separate backup job; it
relies entirely on the managed Postgres provider's backup feature. Document any
change of database provider by re-verifying this section.

## Cache Invalidation (Redis / AI Gateway)

The AI Gateway (Phase 3.5) caches Gemini explanations in Redis keyed by a
deterministic hash of the (minimized) variance payload. Cached entries expire
naturally per `services/ai_gateway.py`'s cache logic; to force a full cache
flush (e.g. after a Gemini prompt/model change):
```bash
redis-cli -u $REDIS_URL FLUSHDB
```

## Routine Maintenance Checklist

- Weekly: review `/status` and `/metrics` for anomalies (cache hit rate drop,
  rising error counts)
- Monthly: rotate `JWT_SECRET` and `ADMIN_PASSWORD_HASH` if this is a
  higher-sensitivity deployment
- Per release: follow [release-checklist.md](release-checklist.md)

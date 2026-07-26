# Phase 3.6 — Monitoring & Observability

Production-grade observability for the PayVerify AI backend. Three monitoring endpoints expose health, readiness, and Prometheus metrics. Structured JSON logging provides request tracing and audit trails.

## Endpoints

### `GET /health` — Liveness Probe

**Purpose:** Lightweight health check used by orchestrators (Docker, Render, Kubernetes) to verify the process is alive.

**Behavior:**
- No external dependencies checked (no DB calls, no Redis calls)
- Response time: < 50ms
- Returns immediately regardless of dependency state

**Example:**
```bash
curl http://localhost:8000/health
```

**Response (200 OK):**
```json
{
  "status": "ok",
  "timestamp": 1690376400.123
}
```

**Use Case:** Docker health checks, Render restart policies, Kubernetes liveness probes.

---

### `GET /status` — Readiness Probe

**Purpose:** Detailed dependency health check. Verifies critical dependencies (PostgreSQL, Redis, Gemini) are reachable and working before accepting traffic.

**Behavior:**
- Checks PostgreSQL: runs `SELECT 1`
- Checks Redis: runs `PING` (if `REDIS_URL` env var set)
- Checks Gemini: verifies `GEMINI_API_KEY` env var is present
- Does NOT crash if a dependency is down; returns per-dependency status
- Marks overall status as "degraded" if any dependency is unhealthy

**Example:**
```bash
curl http://localhost:8000/status
```

**Response (200 OK, all healthy):**
```json
{
  "status": "ready",
  "timestamp": 1690376400.456,
  "dependencies": {
    "postgres": {
      "healthy": true,
      "message": "Connected"
    },
    "redis": {
      "healthy": true,
      "message": "Pong"
    },
    "gemini": {
      "healthy": true,
      "message": "GEMINI_API_KEY set"
    }
  }
}
```

**Response (200 OK, Redis unavailable):**
```json
{
  "status": "degraded",
  "timestamp": 1690376400.789,
  "dependencies": {
    "postgres": {
      "healthy": true,
      "message": "Connected"
    },
    "redis": {
      "healthy": false,
      "message": "Connection refused (localhost:6379)"
    },
    "gemini": {
      "healthy": true,
      "message": "GEMINI_API_KEY set"
    }
  }
}
```

**Use Case:**
- Render deployment health checks (set Health Check Path to `/status`)
- Kubernetes readiness probes (determines if pod should receive traffic)
- Uptime monitors and alerts
- Blue-green deployment pre-switch validation

---

### `GET /metrics` — Prometheus Metrics

**Purpose:** Machine-readable metrics in Prometheus text format for scraping by monitoring systems (Prometheus, Grafana, Datadog, New Relic, etc.).

**Behavior:**
- Exposes AI Gateway token usage (input/output cumulative)
- Exposes AI Gateway cache hit rate
- Exposes variance count by classification (from database)
- Returns Prometheus text format (`# HELP`, `# TYPE`, metric lines)

**Example:**
```bash
curl http://localhost:8000/metrics
```

**Response (200 OK):**
```
# HELP gemini_requests_total Total Gemini API requests (from Phase 3.5)
# TYPE gemini_requests_total counter
gemini_requests_total 123

# HELP gemini_tokens_input_cumulative Cumulative input tokens sent to Gemini
# TYPE gemini_tokens_input_cumulative counter
gemini_tokens_input_cumulative 45000

# HELP gemini_tokens_output_cumulative Cumulative output tokens from Gemini
# TYPE gemini_tokens_output_cumulative counter
gemini_tokens_output_cumulative 12000

# HELP gemini_cache_hits_total Total cache hits on Gemini requests
# TYPE gemini_cache_hits_total counter
gemini_cache_hits_total 80

# HELP gemini_cache_hit_rate Cache hit rate (0.0-1.0)
# TYPE gemini_cache_hit_rate gauge
gemini_cache_hit_rate 0.65

# HELP variance_count Variance count by classification
# TYPE variance_count gauge
variance_count{classification="no_variance"} 1234
variance_count{classification="amount_mismatch_within_tolerance"} 56
variance_count{classification="amount_mismatch_beyond_tolerance"} 12
variance_count{classification="eligibility_mismatch"} 3

# HELP variance_total Total variance records
# TYPE variance_total gauge
variance_total 1305
```

**Use Case:**
- Prometheus scrape target (add to `prometheus.yml`)
- Grafana dashboards (query Prometheus datasource)
- Third-party monitoring (Datadog agent, New Relic, CloudWatch, etc.)
- Alert rules (e.g., trigger alert if `gemini_cache_hit_rate < 0.5`)

**Prometheus Configuration Example:**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'payverify-ai'
    static_configs:
      - targets: ['http://localhost:8000']
    metrics_path: '/metrics'
```

**Grafana Dashboard Example:**
```
- Title: "Gemini API Efficiency"
  Queries:
    - gemini_requests_total (rate)
    - gemini_cache_hit_rate
    - gemini_tokens_input_cumulative (rate)
    - gemini_tokens_output_cumulative (rate)
```

---

## Structured JSON Logging

Every HTTP request and response is logged to stdout as a single line of JSON. Includes:
- `request_id`: Unique correlation ID for tracing a request through logs
- `timestamp`: ISO 8601 UTC time
- `level`: INFO, ERROR, etc.
- `method`: HTTP verb (GET, POST, etc.)
- `path`: Request path
- `status`: Response status code
- `duration_ms`: Request duration in milliseconds
- `remote_addr`: Client IP address

**Example log output:**
```json
{"request_id": "5c8b1d89-ef91-4e98-9f2c-12a3b4c5d6e7", "timestamp": "2026-07-26T14:32:15.123456+00:00", "level": "INFO", "method": "POST", "path": "/api/projects", "status": 201, "duration_ms": 45.2, "remote_addr": "192.168.1.100"}
```

**Use Case:**
- Log aggregation systems (ELK Stack, Splunk, CloudWatch Logs, Datadog Logs)
- Request tracing (correlate all logs from a single request using `request_id`)
- Performance analysis (duration_ms per endpoint)
- Error troubleshooting (status code and request details)

**Centralized Logging Setup Example (Docker Compose + ELK):**
```yaml
version: '3'
services:
  backend:
    image: payverify-ai:latest
    logging:
      driver: "awslogs"  # or "splunk", "datadog", etc.
      options:
        awslogs-group: "/payverify/backend"
        awslogs-stream: "production"
```

---

## Audit Trail (`audit_log` Table)

The `audit_log` table (already defined in Phase 3.6) captures immutable records of key mutations:
- Who uploaded a register
- When a validation ran
- Which consultant provided feedback
- What changes were made

**Schema:**
```sql
CREATE TABLE audit_log (
  id INTEGER PRIMARY KEY,
  project_id INTEGER FOREIGN KEY,
  entity_type VARCHAR(50),     -- "register", "validation", "feedback", etc.
  entity_id INTEGER,           -- ID of the modified entity
  action VARCHAR(100),         -- "upload", "validation_run", "feedback_submitted", etc.
  detail JSON,                 -- Optional additional context (no PII)
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Audit hooks are added to:**
- `/api/projects/{project_id}/registers/upload` — logs each register upload
- `/api/projects/{project_id}/validate` — logs each validation run
- `/api/variances/{variance_id}/feedback` — logs each feedback submission

**Example usage (querying audit logs):**
```sql
-- Who uploaded the most recent client register for project 42?
SELECT * FROM audit_log
WHERE project_id = 42
  AND entity_type = 'register'
  AND detail->>'register_type' = 'client'
ORDER BY created_at DESC
LIMIT 1;

-- How many validation runs in the last 24 hours?
SELECT COUNT(*) FROM audit_log
WHERE entity_type = 'validation'
  AND created_at > NOW() - INTERVAL '1 day';

-- Feedback timeline for a variance:
SELECT * FROM audit_log
WHERE entity_type = 'feedback'
  AND entity_id = 12345
ORDER BY created_at ASC;
```

---

## Deployment Integration

### Docker Health Checks

**Dockerfile example:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

### Render Deployment

1. **In Render Dashboard:**
   - Set **Health Check Path** to `/status`
   - Set **Health Check Interval** to 30 seconds
   - Set **Initial Delay** to 60 seconds

2. **In render.yaml (Blueprint):**
   ```yaml
   healthCheckPath: /status
   ```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payverify-backend
spec:
  template:
    spec:
      containers:
      - name: backend
        image: payverify-ai:latest
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /status
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
          failureThreshold: 2
```

---

## Grafana Dashboard Setup

**Example Prometheus queries for a dashboard:**

```
Query A: Gemini cache efficiency
  Expression: rate(gemini_cache_hits_total[5m]) / rate(gemini_requests_total[5m])
  Legend: Cache Hit Rate

Query B: Token costs per minute
  Expression: rate(gemini_tokens_input_cumulative[1m]) + rate(gemini_tokens_output_cumulative[1m])
  Legend: Tokens/minute

Query C: Variance distribution
  Expression: variance_count
  Legend: {{classification}}

Query D: Request latency
  Expression: rate(http_request_duration_seconds_bucket[5m])
  Legend: {{path}} - {{le}}s
```

---

## Troubleshooting

| Symptom | Cause | Solution |
|---------|-------|----------|
| `/health` returning 5xx | Process crashed or not running | Check Docker logs: `docker logs <container>` |
| `/status` shows Redis unhealthy but Redis is running | Connection timeout | Check `REDIS_URL` env var, verify Redis is accessible |
| `/status` shows Postgres unhealthy | DB connection failed | Verify `DATABASE_URL`, check network connectivity |
| `/metrics` empty or missing AI Gateway metrics | Gateway not initialized | Ensure `GEMINI_API_KEY` or fallback to stub is set |
| Prometheus can't scrape `/metrics` | CORS or firewall blocking | Check `CORS_ALLOWED_ORIGINS`, verify port 8000 is open |
| Missing request logs | Logging middleware not loaded | Verify `RequestLoggingMiddleware` is registered in `main.py` |

---

## Next Steps (Phase 3.7)

- **JWT Authentication:** Add `POST /auth/token` and request-level JWT validation
- **Rate limiting:** Prevent abuse with token bucket or sliding window
- **Error response standardization:** Wrap all errors in consistent schema with correlation IDs
- **Production Readiness Checklist:** Deployment guide, environment variable documentation, incident response playbook

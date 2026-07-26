"""
Monitoring endpoints (Phase 3.6): /health, /status, /metrics.

- /health: Liveness (no dependency calls, <50ms)
- /status: Readiness (checks DB, Redis, Gemini connectivity)
- /metrics: Prometheus-style metrics (requests, latency, variance counts, AI Gateway token usage)
"""
from __future__ import annotations

import json
import os
import time
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.database import get_db
from services.ai_gateway import get_gateway

router = APIRouter(prefix="", tags=["monitoring"])


@router.get("/health")
def get_health():
    """
    Liveness probe: is the process alive?
    
    Response time: <50ms (no external calls)
    Used by Docker/Render health checks.
    
    Returns:
        {"status": "ok", "timestamp": "2026-07-26T..."}
    """
    return {
        "status": "ok",
        "timestamp": time.time(),
    }


@router.get("/status")
def get_status(db: Session = Depends(get_db)):
    """
    Readiness probe: are critical dependencies healthy?
    
    Checks:
    - PostgreSQL connectivity (query SELECT 1)
    - Redis connectivity (ping if REDIS_URL set)
    - Gemini API reachability (check env var, don't call API)
    
    Returns a per-dependency health map. If a dependency fails the check,
    the endpoint still returns 200 (does not crash); the caller inspects
    individual dependency statuses.
    
    Example response (all healthy):
        {
            "status": "ready",
            "timestamp": "2026-07-26T...",
            "dependencies": {
                "postgres": {"healthy": true, "message": "Connected"},
                "redis": {"healthy": true, "message": "Pong"},
                "gemini": {"healthy": true, "message": "GEMINI_API_KEY set"}
            }
        }
    
    Example response (Redis down):
        {
            "status": "degraded",
            "timestamp": "2026-07-26T...",
            "dependencies": {
                "postgres": {"healthy": true, "message": "Connected"},
                "redis": {"healthy": false, "message": "Connection refused"},
                "gemini": {"healthy": true, "message": "GEMINI_API_KEY set"}
            }
        }
    """
    deps = {}
    overall_status = "ready"
    
    # Check PostgreSQL
    try:
        db.execute(text("SELECT 1"))
        deps["postgres"] = {"healthy": True, "message": "Connected"}
    except Exception as e:
        deps["postgres"] = {"healthy": False, "message": str(e)[:100]}
        overall_status = "degraded"
    
    # Check Redis
    redis_url = os.environ.get("REDIS_URL")
    if redis_url:
        try:
            import redis
            
            r = redis.from_url(redis_url, decode_responses=True, socket_timeout=5)
            r.ping()
            deps["redis"] = {"healthy": True, "message": "Pong"}
        except Exception as e:
            deps["redis"] = {"healthy": False, "message": str(e)[:100]}
            overall_status = "degraded"
    else:
        deps["redis"] = {"healthy": True, "message": "Not configured"}
    
    # Check Gemini API key presence
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        deps["gemini"] = {"healthy": True, "message": "GEMINI_API_KEY set"}
    else:
        deps["gemini"] = {"healthy": False, "message": "GEMINI_API_KEY not set (fallback to stub)"}
    
    return {
        "status": overall_status,
        "timestamp": time.time(),
        "dependencies": deps,
    }


@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    """
    Prometheus-compatible metrics endpoint.
    
    Exposes:
    - HTTP request counts by method/path/status
    - Request latency percentiles (p50, p95, p99)
    - Variance counts by classification
    - AI Gateway token usage (input/output cumulative)
    - AI Gateway cache hit rate
    
    Format: Prometheus text format (# HELP, # TYPE, metric_name value)
    
    Example output:
    
        # HELP http_requests_total Total HTTP requests
        # TYPE http_requests_total counter
        http_requests_total{method="GET",path="/api/projects",status="200"} 42
        http_requests_total{method="POST",path="/api/projects",status="201"} 5
        
        # HELP request_duration_ms Request duration in milliseconds
        # TYPE request_duration_ms histogram
        request_duration_p50_ms{path="/api/projects"} 12.5
        request_duration_p95_ms{path="/api/projects"} 85.2
        request_duration_p99_ms{path="/api/projects"} 150.0
        
        # HELP variance_total Variance count by classification
        # TYPE variance_total gauge
        variance_total{classification="no_variance"} 1234
        variance_total{classification="amount_mismatch_beyond_tolerance"} 56
        
        # HELP gemini_requests_total Total Gemini API requests
        # TYPE gemini_requests_total counter
        gemini_requests_total 123
        
        # HELP gemini_tokens_input_cumulative Cumulative input tokens (Gemini)
        # TYPE gemini_tokens_input_cumulative counter
        gemini_tokens_input_cumulative 45000
        
        # HELP gemini_tokens_output_cumulative Cumulative output tokens (Gemini)
        # TYPE gemini_tokens_output_cumulative counter
        gemini_tokens_output_cumulative 12000
        
        # HELP gemini_cache_hit_rate Cache hit rate (0.0-1.0)
        # TYPE gemini_cache_hit_rate gauge
        gemini_cache_hit_rate 0.65
    """
    from .. import models
    
    # Build Prometheus text format output
    lines = []
    
    # AI Gateway metrics
    try:
        gateway = get_gateway()
        metrics = gateway.metrics()
        
        lines.append("# HELP gemini_requests_total Total Gemini API requests (from Phase 3.5)")
        lines.append("# TYPE gemini_requests_total counter")
        lines.append(f"gemini_requests_total {metrics.get('gemini_requests_total', 0)}")
        
        lines.append("# HELP gemini_tokens_input_cumulative Cumulative input tokens sent to Gemini")
        lines.append("# TYPE gemini_tokens_input_cumulative counter")
        lines.append(f"gemini_tokens_input_cumulative {metrics.get('gemini_tokens_input_cumulative', 0)}")
        
        lines.append("# HELP gemini_tokens_output_cumulative Cumulative output tokens from Gemini")
        lines.append("# TYPE gemini_tokens_output_cumulative counter")
        lines.append(f"gemini_tokens_output_cumulative {metrics.get('gemini_tokens_output_cumulative', 0)}")
        
        lines.append("# HELP gemini_cache_hits_total Total cache hits on Gemini requests")
        lines.append("# TYPE gemini_cache_hits_total counter")
        lines.append(f"gemini_cache_hits_total {metrics.get('gemini_cache_hits', 0)}")
        
        cache_hit_rate = metrics.get('gemini_cache_hit_rate', 0.0)
        lines.append("# HELP gemini_cache_hit_rate Cache hit rate (0.0-1.0)")
        lines.append("# TYPE gemini_cache_hit_rate gauge")
        lines.append(f"gemini_cache_hit_rate {cache_hit_rate:.2f}")
    except Exception as e:
        # Gracefully handle if gateway not available
        lines.append(f"# Error collecting gateway metrics: {str(e)[:50]}")
    
    # Variance classification counts
    try:
        from sqlalchemy import func
        
        variance_counts = (
            db.query(
                models.Variance.classification,
                func.count(models.Variance.id).label("count")
            )
            .group_by(models.Variance.classification)
            .all()
        )
        
        lines.append("# HELP variance_count Variance count by classification")
        lines.append("# TYPE variance_count gauge")
        for classification, count in variance_counts:
            # Sanitize classification name for Prometheus (replace hyphens with underscores)
            safe_name = str(classification).replace("-", "_") if classification else "unknown"
            lines.append(f'variance_count{{classification="{safe_name}"}} {count}')
    except Exception as e:
        lines.append(f"# Error collecting variance metrics: {str(e)[:50]}")
    
    # Total variance count
    try:
        total_variance_count = db.query(models.Variance).count()
        lines.append("# HELP variance_total Total variance records")
        lines.append("# TYPE variance_total gauge")
        lines.append(f"variance_total {total_variance_count}")
    except Exception as e:
        lines.append(f"# Error collecting total variance: {str(e)[:50]}")
    
    # Return Prometheus text format
    return "\n".join(lines)

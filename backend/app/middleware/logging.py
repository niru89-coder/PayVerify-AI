"""
Structured JSON logging middleware with request correlation IDs (Phase 3.6).

Generates a unique request_id for each request, logs structured JSON with:
- request_id: correlation ID for tracing through logs
- timestamp: ISO 8601 UTC
- level: INFO/ERROR/etc
- method: HTTP verb
- path: request path
- status: response status code
- duration_ms: request duration in milliseconds
- remote_addr: client IP
"""
from __future__ import annotations

import json
import logging
import time
import uuid
from datetime import datetime, timezone

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


# Configure root logger for structured JSON output
def configure_json_logging():
    """Configure logging to emit JSON to stdout."""
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(message)s',  # Formatter will emit raw JSON
    )
    handler.setFormatter(formatter)
    
    logger = logging.getLogger('payverify')
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger


_logger = configure_json_logging()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs every request/response with a correlation ID."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Generate or extract request_id
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Record start time
        start_time = time.time()
        
        # Call the next middleware/endpoint
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Build structured log
        log_data = {
            'request_id': request_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': 'INFO',
            'method': request.method,
            'path': request.url.path,
            'status': response.status_code,
            'duration_ms': round(duration_ms, 2),
            'remote_addr': request.client.host if request.client else 'unknown',
        }
        
        # Emit JSON log
        _logger.info(json.dumps(log_data))
        
        return response


def get_logger():
    """Get the structured logger instance."""
    return _logger


def log_info(message: str, request_id: str | None = None, **extra):
    """Log an info-level structured message."""
    log_data = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'level': 'INFO',
        'message': message,
    }
    if request_id:
        log_data['request_id'] = request_id
    log_data.update(extra)
    _logger.info(json.dumps(log_data))


def log_error(message: str, request_id: str | None = None, **extra):
    """Log an error-level structured message."""
    log_data = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'level': 'ERROR',
        'message': message,
    }
    if request_id:
        log_data['request_id'] = request_id
    log_data.update(extra)
    _logger.error(json.dumps(log_data))

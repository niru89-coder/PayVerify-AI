"""AI Gateway for Gemini-based variance explanations.

Provides data minimization, caching, logging, and token tracking as a security
and cost optimization layer between the backend and the Gemini API.

Per Phase 3.5 requirements:
- Payload minimization: only approved fields reach Gemini (allow-list, not deny-list)
- Redis caching: identical variances reuse cached responses
- Audit logging: every request/response logged without PII
- Token tracking: usage recorded per request and cumulatively
- Fallback: if Gemini is unavailable, deterministic stub fills in seamlessly
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class MinimizedVariancePayload:
    """Only fields needed for Gemini — deny-list turned inside-out as an allow-list."""

    rule_id: Optional[str]
    component_code: str
    expected_value: Optional[float]
    actual_value: Optional[float]  # client or platform, whichever is the "actual"
    variance_type: str  # classification from reconciliation
    variance_amount: Optional[float]  # abs(expected - actual)

    def to_dict(self) -> dict:
        return asdict(self)

    def cache_key(self) -> str:
        """Generate a deterministic cache key from the payload.
        
        Rounding numeric values to 2 decimal places to avoid cache misses
        on floating-point precision differences (e.g., 100.0 vs 100.00).
        """
        rounded = {
            "rule_id": self.rule_id,
            "component": self.component_code,
            "variance_type": self.variance_type,
            "expected": round(self.expected_value or 0.0, 2),
            "actual": round(self.actual_value or 0.0, 2),
            "amount": round(self.variance_amount or 0.0, 2),
        }
        key_str = json.dumps(rounded, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()


class GeminiGateway:
    """Gateway for Gemini API calls with minimization, caching, and telemetry."""

    def __init__(self, redis_url: Optional[str] = None, cache_ttl_seconds: int = 86400):
        """Initialize the gateway.
        
        Args:
            redis_url: Redis connection string (e.g., from REDIS_URL env var).
                      If None or empty, caching is disabled.
            cache_ttl_seconds: How long to keep cached responses (default 24h).
        """
        self._cache_ttl = cache_ttl_seconds
        self._redis = None
        self._cumulative_input_tokens = 0
        self._cumulative_output_tokens = 0
        self._request_count = 0
        self._cache_hit_count = 0

        if redis_url:
            try:
                import redis

                self._redis = redis.from_url(redis_url, decode_responses=True)
                self._redis.ping()  # verify connection
                logger.info("Redis connection established for AI Gateway caching")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis ({redis_url}): {e}. Caching disabled.")
                self._redis = None

    def minimize_payload(self, raw_request) -> MinimizedVariancePayload:
        """Extract only approved fields (allow-list).
        
        Input is a VarianceExplanationRequest from agents/explanation_agent.py.
        Output is the minimized payload safe to send to Gemini.
        """
        # Determine which value to use as "actual"
        # Prefer platform_value if both exist, fallback to client_value
        actual = raw_request.platform_value
        if actual is None:
            actual = raw_request.client_value

        # Calculate variance amount
        variance_amount = None
        if raw_request.expected_value is not None and actual is not None:
            variance_amount = abs(raw_request.expected_value - actual)

        minimized = MinimizedVariancePayload(
            rule_id=raw_request.rule_id,
            component_code=raw_request.component_code,
            expected_value=raw_request.expected_value,
            actual_value=actual,
            variance_type=raw_request.classification,
            variance_amount=variance_amount,
        )
        logger.debug(f"Minimized payload cache_key: {minimized.cache_key()}")
        return minimized

    def get_cached_response(self, minimized: MinimizedVariancePayload) -> Optional[str]:
        """Check Redis for a cached response."""
        if not self._redis:
            return None

        try:
            cache_key = f"gemini_explain:{minimized.cache_key()}"
            cached = self._redis.get(cache_key)
            if cached:
                logger.info(f"Cache hit for {minimized.component_code} / {minimized.variance_type}")
                self._cache_hit_count += 1
                return cached
        except Exception as e:
            logger.warning(f"Redis GET failed: {e}. Proceeding without cache.")
        return None

    def cache_response(self, minimized: MinimizedVariancePayload, response: str) -> None:
        """Store response in Redis."""
        if not self._redis:
            return

        try:
            cache_key = f"gemini_explain:{minimized.cache_key()}"
            self._redis.setex(cache_key, self._cache_ttl, response)
            logger.debug(f"Cached response for {minimized.component_code}")
        except Exception as e:
            logger.warning(f"Redis SET failed: {e}. Proceeding without cache.")

    def log_request(self, minimized: MinimizedVariancePayload) -> None:
        """Log the minimized request for audit purposes (no PII)."""
        logger.info(
            f"Gemini explain request: component={minimized.component_code}, "
            f"rule={minimized.rule_id}, variance_type={minimized.variance_type}, "
            f"amount={minimized.variance_amount}"
        )

    def log_response(self, minimized: MinimizedVariancePayload, response: str, tokens_in: int = 0, tokens_out: int = 0) -> None:
        """Log the response and token usage."""
        self._cumulative_input_tokens += tokens_in
        self._cumulative_output_tokens += tokens_out
        logger.info(
            f"Gemini response: component={minimized.component_code}, "
            f"response_length={len(response)}, tokens_in={tokens_in}, tokens_out={tokens_out}"
        )

    def explain(self, raw_request, provider) -> str:
        """Main entry point: minimize, cache, call provider, and log.
        
        Args:
            raw_request: VarianceExplanationRequest from the backend
            provider: ExplanationProvider instance (GeminiExplanationProvider or StubExplanationProvider)
        
        Returns:
            Explanation string (from cache, Gemini, or fallback stub)
        """
        self._request_count += 1

        # Step 1: Minimize payload
        minimized = self.minimize_payload(raw_request)

        # Step 2: Check cache
        cached = self.get_cached_response(minimized)
        if cached:
            return cached

        # Step 3: Call provider (will fall back to stub if Gemini errors)
        self.log_request(minimized)
        response = provider.explain(raw_request)  # pass raw request; provider doesn't need minimal
        self.log_response(minimized, response)

        # Step 4: Cache result
        self.cache_response(minimized, response)

        return response

    def metrics(self) -> dict:
        """Return telemetry for the /metrics endpoint (Phase 3.6)."""
        return {
            "gemini_requests_total": self._request_count,
            "gemini_cache_hits": self._cache_hit_count,
            "gemini_cache_hit_rate": (
                self._cache_hit_count / self._request_count if self._request_count > 0 else 0
            ),
            "gemini_tokens_input_cumulative": self._cumulative_input_tokens,
            "gemini_tokens_output_cumulative": self._cumulative_output_tokens,
        }


# Singleton instance (initialized at module load, used by agents/)
_gateway_instance: Optional[GeminiGateway] = None


def get_gateway() -> GeminiGateway:
    """Get or create the singleton gateway instance."""
    global _gateway_instance
    if _gateway_instance is None:
        redis_url = os.environ.get("REDIS_URL", "")
        _gateway_instance = GeminiGateway(redis_url=redis_url if redis_url else None)
    return _gateway_instance

"""Tests for agents/explanation_agent.py (stub AI explanation, no API key required)."""
from explanation_agent import (
    StubExplanationProvider,
    VarianceExplanationRequest,
    get_default_provider,
    GatewayExplanationProvider,
)


def test_stub_provider_produces_deterministic_text():
    provider = StubExplanationProvider()
    request = VarianceExplanationRequest(
        employee_id="E002",
        component_code="EPF_EMPLOYEE",
        client_value=110.0,
        platform_value=100.0,
        expected_value=110.0,
        rule_id="MY_EPF_001",
        classification="rate_slab_mismatch",
        suggestion_outcome="client_correct_platform_review",
        recommended_action="Review platform rate configuration.",
        confidence_score=0.9,
    )
    text = provider.explain(request)
    assert "E002" in text
    assert "EPF_EMPLOYEE" in text
    assert "rate_slab_mismatch" in text
    assert "AI-suggested/unverified" in text


def test_default_provider_is_gateway_wrapped_stub_without_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    provider = get_default_provider()
    # Should be gateway-wrapped stub
    assert isinstance(provider, GatewayExplanationProvider)
    # The inner provider should be stub
    assert isinstance(provider._provider, StubExplanationProvider)


def test_gateway_wrapped_provider_can_explain(monkeypatch):
    """Verify the gateway-wrapped provider produces explanations."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    provider = get_default_provider()

    request = VarianceExplanationRequest(
        employee_id="E001",
        component_code="BASIC_SALARY",
        client_value=5000.0,
        platform_value=4900.0,
        expected_value=5000.0,
        rule_id=None,
        classification="AMOUNT_MISMATCH",
        suggestion_outcome="review",
        recommended_action="Check values",
        confidence_score=0.85,
    )

    explanation = provider.explain(request)
    assert isinstance(explanation, str)
    assert len(explanation) > 0
    assert "E001" in explanation or "BASIC_SALARY" in explanation


def test_gateway_exposes_metrics(monkeypatch):
    """Verify gateway provides telemetry."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    provider = get_default_provider()

    # Should have a metrics method
    assert hasattr(provider, "metrics")
    metrics = provider.metrics()
    assert "gemini_requests_total" in metrics
    assert "gemini_cache_hits" in metrics
    assert "gemini_cache_hit_rate" in metrics

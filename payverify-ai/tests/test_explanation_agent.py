"""Tests for agents/explanation_agent.py (stub AI explanation, no API key required)."""
from explanation_agent import StubExplanationProvider, VarianceExplanationRequest, get_default_provider


def test_stub_provider_produces_deterministic_text():
    provider = StubExplanationProvider()
    request = VarianceExplanationRequest(
        employee_id="E002", component_code="EPF_EMPLOYEE", client_value=110.0,
        platform_value=100.0, expected_value=110.0, rule_id="MY_EPF_001",
        classification="rate_slab_mismatch", suggestion_outcome="client_correct_platform_review",
        recommended_action="Review platform rate configuration.", confidence_score=0.9,
    )
    text = provider.explain(request)
    assert "E002" in text
    assert "EPF_EMPLOYEE" in text
    assert "rate_slab_mismatch" in text
    assert "AI-suggested/unverified" in text


def test_default_provider_is_stub_without_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    provider = get_default_provider()
    assert isinstance(provider, StubExplanationProvider)

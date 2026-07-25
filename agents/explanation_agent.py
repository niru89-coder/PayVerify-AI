"""
AI Explanation Agent (BRD Section 11 - AI Assistance Layer, Guardrails 11.2).

CRITICAL GUARDRAIL: This module NEVER computes or overrides a payroll figure.
It only receives an already-fully-classified Variance (produced deterministically
by validation-engine/reconciliation.py) and produces a natural-language
explanation for a human consultant. If no LLM credentials are configured, the
StubExplanationProvider produces a deterministic templated explanation from
the same structured fields - so the system is 100% usable without any AI key,
per the master prompt's requirement that "AI is only for document
understanding / explanation, never runtime calculation."
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class VarianceExplanationRequest:
    """Structured, already-computed facts handed to the explanation provider.
    No raw documents or free-form data are passed - only the deterministic
    output of the reconciliation engine, per BRD 11.2 Guardrails."""

    employee_id: str
    component_code: str
    client_value: float | None
    platform_value: float | None
    expected_value: float | None
    rule_id: str | None
    classification: str
    suggestion_outcome: str
    recommended_action: str
    confidence_score: float


class ExplanationProvider(ABC):
    @abstractmethod
    def explain(self, request: VarianceExplanationRequest) -> str:
        """Return a short, consultant-facing natural-language explanation."""


class StubExplanationProvider(ExplanationProvider):
    """Deterministic, templated explanation - active by default (no API key required)."""

    def explain(self, request: VarianceExplanationRequest) -> str:
        parts = [
            f"Employee {request.employee_id}, component {request.component_code}: "
            f"classified as '{request.classification}'.",
        ]
        values = []
        if request.client_value is not None:
            values.append(f"Client=RM{request.client_value:.2f}")
        if request.platform_value is not None:
            values.append(f"Platform=RM{request.platform_value:.2f}")
        if request.expected_value is not None:
            values.append(f"Rule-Engine Expected=RM{request.expected_value:.2f}")
        if values:
            parts.append(" vs ".join(values) + ".")
        if request.rule_id:
            parts.append(f"Evaluated against rule {request.rule_id}.")
        parts.append(f"Suggested outcome: {request.suggestion_outcome}.")
        parts.append(request.recommended_action)
        parts.append(f"(AI-suggested/unverified, confidence {request.confidence_score:.0%} - deterministic rule engine result is authoritative.)")
        return " ".join(parts)


class GeminiExplanationProvider(ExplanationProvider):
    """Uses Google Gemini to phrase the explanation. Inactive unless
    GEMINI_API_KEY is set; the prompt sent to the model contains ONLY the
    structured fields above - the model is explicitly instructed not to
    recompute or contradict the deterministic classification."""

    MODEL = "gemini-2.0-flash"

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self._api_key:
            raise RuntimeError("GEMINI_API_KEY not set; use StubExplanationProvider instead.")
        import google.generativeai as genai  # imported lazily so the stub path has no hard dependency at runtime

        genai.configure(api_key=self._api_key)
        self._client = genai.GenerativeModel(self.MODEL)

    def explain(self, request: VarianceExplanationRequest) -> str:
        prompt = (
            "You are a payroll validation assistant. You are given an ALREADY "
            "COMPUTED, deterministic variance finding. Do NOT recompute any "
            "figures or contradict the classification/suggestion - only phrase "
            "a clear, concise explanation (2-4 sentences) for a payroll "
            "implementation consultant.\n\n"
            f"Employee ID: {request.employee_id}\n"
            f"Component: {request.component_code}\n"
            f"Client value: {request.client_value}\n"
            f"Platform value: {request.platform_value}\n"
            f"Rule-engine expected value: {request.expected_value}\n"
            f"Rule ID: {request.rule_id}\n"
            f"Classification: {request.classification}\n"
            f"Suggestion outcome: {request.suggestion_outcome}\n"
            f"Recommended action: {request.recommended_action}\n"
            f"Confidence score: {request.confidence_score}\n"
        )
        response = self._client.generate_content(
            prompt,
            generation_config={"max_output_tokens": 300},
        )
        return response.text


def get_default_provider() -> ExplanationProvider:
    """Factory: uses Gemini if GEMINI_API_KEY is configured, else the stub."""
    if os.environ.get("GEMINI_API_KEY"):
        try:
            return GeminiExplanationProvider()
        except Exception:
            return StubExplanationProvider()
    return StubExplanationProvider()

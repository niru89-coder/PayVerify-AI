"""
Reconciliation / Validation Engine (BRD Section 8.3, 10).

Implements the "Generalized Decision Pattern" for the three-way comparison:
    Client Register value  vs  Platform (Darwinbox) Register value  vs
    Rule-Engine expected value (independently computed, deterministic).

This module contains NO AI/LLM calls. All classification and suggestion logic
is deterministic and rule-based, per BRD Section 11.2 Guardrails ("the AI
never overrides deterministic results; it may only narrate them"). The only
place an LLM may plug in is to phrase `ai_explanation` text for a Variance
row that is already fully computed here (see agents/explanation_agent.py).

Pipeline position:
    Upload -> Mapping Engine -> Rule Engine (per employee x component)
           -> THIS MODULE (3-way compare, classify, suggest) -> Variance rows
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

# Allow importing the flat rule-engine modules regardless of caller's cwd.
_RULE_ENGINE_DIR = Path(__file__).resolve().parent.parent / "rule-engine"
if str(_RULE_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(_RULE_ENGINE_DIR))

from base import RuleResult, RuleStatus  # noqa: E402

DEFAULT_TOLERANCE = 0.02  # RM 2 sen - accounts for benign rounding differences

# Component codes that represent the *employee* half of a statutory component,
# used to pick expected_employee_amount vs expected_employer_amount from a RuleResult.
EMPLOYEE_SUFFIXES = ("_EMPLOYEE",)
EMPLOYER_SUFFIXES = ("_EMPLOYER", "_LEVY")  # HRDF_LEVY is employer-only


class Classification:
    NOT_CALCULATED_ONE_SIDE = "component_not_calculated_one_side"
    AMOUNT_MISMATCH_WITHIN_TOLERANCE = "amount_mismatch_within_tolerance"
    AMOUNT_MISMATCH_BEYOND_TOLERANCE = "amount_mismatch_beyond_tolerance"
    RATE_SLAB_MISMATCH = "rate_slab_mismatch"
    ELIGIBILITY_MISMATCH = "eligibility_mismatch"
    DATA_QUALITY_ISSUE = "data_quality_issue"
    NO_VARIANCE = "no_variance"


class Suggestion:
    PLATFORM_CORRECT = "platform_correct_client_review"
    CLIENT_CORRECT = "client_correct_platform_review"
    INCONCLUSIVE = "inconclusive_clarification_required"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class VarianceFinding:
    employee_id: str
    component_code: str
    client_value: float | None
    platform_value: float | None
    expected_value: float | None
    rule_id: str | None
    rule_status: str | None
    classification: str
    suggestion_outcome: str
    recommended_action: str
    explanation: str
    confidence_score: float

    def to_dict(self) -> dict:
        return {
            "employee_id": self.employee_id,
            "component_code": self.component_code,
            "client_value": self.client_value,
            "platform_value": self.platform_value,
            "expected_value": self.expected_value,
            "rule_id": self.rule_id,
            "rule_status": self.rule_status,
            "classification": self.classification,
            "suggestion_outcome": self.suggestion_outcome,
            "recommended_action": self.recommended_action,
            "explanation": self.explanation,
            "confidence_score": self.confidence_score,
        }


def _is_present(value: float | None) -> bool:
    return value is not None


def _close(a: float | None, b: float | None, tolerance: float) -> bool:
    if a is None or b is None:
        return False
    return abs(a - b) <= tolerance


def expected_amount_for_component(component_code: str, rule_result: RuleResult) -> float | None:
    """Pick the correct half (employee/employer) of a RuleResult for a given component code."""
    if any(component_code.endswith(suf) for suf in EMPLOYEE_SUFFIXES):
        return rule_result.expected_employee_amount
    if any(component_code.endswith(suf) for suf in EMPLOYER_SUFFIXES):
        return rule_result.expected_employer_amount
    return rule_result.expected_total_amount


def classify_variance(
    employee_id: str,
    component_code: str,
    client_value: float | None,
    platform_value: float | None,
    rule_result: RuleResult | None,
    tolerance: float = DEFAULT_TOLERANCE,
) -> VarianceFinding:
    """Apply the BRD Section 8.3 generalized decision pattern to one employee x component."""

    rule_id = rule_result.rule_id if rule_result else None
    rule_status = rule_result.status.value if rule_result else None
    expected_value = expected_amount_for_component(component_code, rule_result) if rule_result else None

    client_present = _is_present(client_value)
    platform_present = _is_present(platform_value)

    # Step 1: component present in one register but not the other.
    if client_present != platform_present:
        missing_side = "platform" if client_present else "client"
        return VarianceFinding(
            employee_id, component_code, client_value, platform_value, expected_value, rule_id, rule_status,
            classification=Classification.NOT_CALCULATED_ONE_SIDE,
            suggestion_outcome=Suggestion.INCONCLUSIVE,
            recommended_action=(
                f"Component '{component_code}' is missing from the {missing_side} register. "
                f"Verify whether it should be configured/enabled there, or whether the value is "
                f"genuinely zero/not applicable for this employee."
            ),
            explanation=f"{component_code} present in one register only ({'client' if client_present else 'platform'}).",
            confidence_score=0.55,
        )

    # Step 2: rule engine says this component is not applicable to this employee at all.
    if rule_result is not None and rule_result.status == RuleStatus.NOT_APPLICABLE:
        client_nonzero = client_present and abs(client_value) > tolerance
        platform_nonzero = platform_present and abs(platform_value) > tolerance
        if client_nonzero or platform_nonzero:
            offending = []
            if client_nonzero:
                offending.append("client")
            if platform_nonzero:
                offending.append("platform")
            return VarianceFinding(
                employee_id, component_code, client_value, platform_value, expected_value, rule_id, rule_status,
                classification=Classification.ELIGIBILITY_MISMATCH,
                suggestion_outcome=Suggestion.INCONCLUSIVE,
                recommended_action=(
                    f"Rule engine ({rule_id}) determined this employee is NOT eligible for "
                    f"'{component_code}', but {' and '.join(offending)} register(s) show a non-zero "
                    f"value. Verify employee eligibility master data (age, nationality, employment type)."
                ),
                explanation=rule_result.explanation,
                confidence_score=0.6,
            )
        return VarianceFinding(
            employee_id, component_code, client_value, platform_value, expected_value, rule_id, rule_status,
            classification=Classification.NO_VARIANCE,
            suggestion_outcome=Suggestion.NOT_APPLICABLE,
            recommended_action="No action required - both registers correctly show no value for a not-applicable component.",
            explanation=rule_result.explanation,
            confidence_score=0.95,
        )

    # Step 3: rule engine could not compute an authoritative expected value (pending SME data).
    if rule_result is not None and rule_result.status == RuleStatus.PENDING_SME_VALIDATION:
        if _close(client_value, platform_value, tolerance):
            return VarianceFinding(
                employee_id, component_code, client_value, platform_value, expected_value, rule_id, rule_status,
                classification=Classification.NO_VARIANCE,
                suggestion_outcome=Suggestion.NOT_APPLICABLE,
                recommended_action="Client and platform agree; rule engine expected value is still pending SME validation for this component.",
                explanation=rule_result.explanation,
                confidence_score=0.5,
            )
        return VarianceFinding(
            employee_id, component_code, client_value, platform_value, expected_value, rule_id, rule_status,
            classification=Classification.DATA_QUALITY_ISSUE,
            suggestion_outcome=Suggestion.INCONCLUSIVE,
            recommended_action=(
                f"Client and platform values differ for '{component_code}', but the rule engine cannot "
                f"yet compute an authoritative expected value ({rule_result.explanation}). "
                f"Manual SME review required."
            ),
            explanation=rule_result.explanation,
            confidence_score=0.35,
        )

    # Step 4: full three-way numeric comparison (rule engine has a real expected value, or none was supplied).
    client_matches_expected = _close(client_value, expected_value, tolerance)
    platform_matches_expected = _close(platform_value, expected_value, tolerance)
    client_matches_platform = _close(client_value, platform_value, tolerance)

    if client_matches_platform and (expected_value is None or client_matches_expected):
        return VarianceFinding(
            employee_id, component_code, client_value, platform_value, expected_value, rule_id, rule_status,
            classification=Classification.NO_VARIANCE,
            suggestion_outcome=Suggestion.NOT_APPLICABLE,
            recommended_action="No action required - client, platform and rule engine agree.",
            explanation=(rule_result.explanation if rule_result else ""),
            confidence_score=0.98,
        )

    if expected_value is None:
        # No rule coverage to arbitrate; only report the raw client/platform gap.
        gap = abs((client_value or 0) - (platform_value or 0))
        classification = (
            Classification.AMOUNT_MISMATCH_WITHIN_TOLERANCE if gap <= tolerance
            else Classification.AMOUNT_MISMATCH_BEYOND_TOLERANCE
        )
        return VarianceFinding(
            employee_id, component_code, client_value, platform_value, expected_value, rule_id, rule_status,
            classification=classification,
            suggestion_outcome=Suggestion.INCONCLUSIVE,
            recommended_action="No rule engine coverage available for this component; manual comparison only.",
            explanation="No expected value available from rule engine.",
            confidence_score=0.4,
        )

    if client_matches_expected and not platform_matches_expected:
        return VarianceFinding(
            employee_id, component_code, client_value, platform_value, expected_value, rule_id, rule_status,
            classification=Classification.RATE_SLAB_MISMATCH,
            suggestion_outcome=Suggestion.CLIENT_CORRECT,
            recommended_action=(
                f"Client value matches the independently computed expected value (RM{expected_value:.2f}). "
                f"Platform value (RM{platform_value:.2f}) appears incorrect - review platform rate/slab "
                f"configuration for '{component_code}'."
            ),
            explanation=(rule_result.explanation if rule_result else ""),
            confidence_score=0.9,
        )

    if platform_matches_expected and not client_matches_expected:
        return VarianceFinding(
            employee_id, component_code, client_value, platform_value, expected_value, rule_id, rule_status,
            classification=Classification.RATE_SLAB_MISMATCH,
            suggestion_outcome=Suggestion.PLATFORM_CORRECT,
            recommended_action=(
                f"Platform value matches the independently computed expected value (RM{expected_value:.2f}). "
                f"Client value (RM{client_value:.2f}) appears incorrect - likely a legacy system data or "
                f"configuration issue."
            ),
            explanation=(rule_result.explanation if rule_result else ""),
            confidence_score=0.9,
        )

    # Neither side matches the rule engine, and client != platform.
    gap = abs((client_value or 0) - (expected_value or 0))
    classification = (
        Classification.AMOUNT_MISMATCH_WITHIN_TOLERANCE if gap <= tolerance
        else Classification.AMOUNT_MISMATCH_BEYOND_TOLERANCE
    )
    return VarianceFinding(
        employee_id, component_code, client_value, platform_value, expected_value, rule_id, rule_status,
        classification=classification,
        suggestion_outcome=Suggestion.INCONCLUSIVE,
        recommended_action=(
            f"Neither client (RM{client_value}) nor platform (RM{platform_value}) matches the "
            f"expected value (RM{expected_value:.2f}). Manual investigation required - possible "
            f"data quality issue in both source systems."
        ),
        explanation=(rule_result.explanation if rule_result else ""),
        confidence_score=0.65,
    )


@dataclass
class ReconciliationRequest:
    employee_id: str
    component_code: str
    client_value: float | None
    platform_value: float | None
    rule_result: RuleResult | None


def reconcile_batch(requests: list[ReconciliationRequest], tolerance: float = DEFAULT_TOLERANCE) -> list[VarianceFinding]:
    """Run classify_variance() across a batch of employee x component comparisons."""
    return [
        classify_variance(
            r.employee_id, r.component_code, r.client_value, r.platform_value, r.rule_result, tolerance
        )
        for r in requests
    ]

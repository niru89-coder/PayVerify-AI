"""Tests for validation-engine/reconciliation.py (3-way variance classification)."""
from reconciliation import Classification, Suggestion, classify_variance
from base import RuleResult, RuleStatus


def _rule_result(status=RuleStatus.OK, expected_employee=None, expected_employer=None, rule_id="MY_EPF_001"):
    return RuleResult(
        rule_id=rule_id,
        component="EPF",
        status=status,
        expected_employee_amount=expected_employee,
        expected_employer_amount=expected_employer,
        explanation="test explanation",
        source="test",
    )


def test_no_variance_all_three_agree():
    rr = _rule_result(expected_employee=110.0)
    finding = classify_variance("E001", "EPF_EMPLOYEE", 110.0, 110.0, rr)
    assert finding.classification == Classification.NO_VARIANCE
    assert finding.suggestion_outcome == Suggestion.NOT_APPLICABLE
    assert finding.confidence_score > 0.9


def test_component_missing_one_side():
    rr = _rule_result(expected_employee=110.0)
    finding = classify_variance("E001", "EPF_EMPLOYEE", 110.0, None, rr)
    assert finding.classification == Classification.NOT_CALCULATED_ONE_SIDE
    assert finding.suggestion_outcome == Suggestion.INCONCLUSIVE


def test_eligibility_mismatch_not_applicable_but_value_present():
    rr = _rule_result(status=RuleStatus.NOT_APPLICABLE)
    finding = classify_variance("E001", "EPF_EMPLOYEE", 50.0, 50.0, rr)
    assert finding.classification == Classification.ELIGIBILITY_MISMATCH


def test_not_applicable_and_both_zero_is_no_variance():
    rr = _rule_result(status=RuleStatus.NOT_APPLICABLE)
    finding = classify_variance("E001", "EPF_EMPLOYEE", 0.0, 0.0, rr)
    assert finding.classification == Classification.NO_VARIANCE
    assert finding.suggestion_outcome == Suggestion.NOT_APPLICABLE


def test_client_correct_platform_wrong():
    rr = _rule_result(expected_employee=110.0)
    finding = classify_variance("E001", "EPF_EMPLOYEE", 110.0, 120.0, rr)
    assert finding.classification == Classification.RATE_SLAB_MISMATCH
    assert finding.suggestion_outcome == Suggestion.CLIENT_CORRECT


def test_platform_correct_client_wrong():
    rr = _rule_result(expected_employee=110.0)
    finding = classify_variance("E001", "EPF_EMPLOYEE", 100.0, 110.0, rr)
    assert finding.classification == Classification.RATE_SLAB_MISMATCH
    assert finding.suggestion_outcome == Suggestion.PLATFORM_CORRECT


def test_neither_matches_expected_inconclusive():
    rr = _rule_result(expected_employee=110.0)
    finding = classify_variance("E001", "EPF_EMPLOYEE", 90.0, 95.0, rr)
    assert finding.suggestion_outcome == Suggestion.INCONCLUSIVE
    assert finding.classification == Classification.AMOUNT_MISMATCH_BEYOND_TOLERANCE


def test_pending_sme_validation_agree():
    rr = _rule_result(status=RuleStatus.PENDING_SME_VALIDATION, rule_id="MY_EIS_001")
    finding = classify_variance("E001", "EIS_EMPLOYEE", 10.0, 10.0, rr)
    assert finding.classification == Classification.NO_VARIANCE


def test_pending_sme_validation_disagree():
    rr = _rule_result(status=RuleStatus.PENDING_SME_VALIDATION, rule_id="MY_EIS_001")
    finding = classify_variance("E001", "EIS_EMPLOYEE", 10.0, 15.0, rr)
    assert finding.classification == Classification.DATA_QUALITY_ISSUE


def test_no_rule_coverage_at_all():
    finding = classify_variance("E001", "SOME_COMPONENT", 10.0, 15.0, None)
    assert finding.suggestion_outcome == Suggestion.INCONCLUSIVE
    assert finding.expected_value is None


def test_employer_amount_selected_for_employer_suffix():
    rr = _rule_result(expected_employee=110.0, expected_employer=130.0)
    finding = classify_variance("E001", "EPF_EMPLOYER", 130.0, 130.0, rr)
    assert finding.expected_value == 130.0
    assert finding.classification == Classification.NO_VARIANCE

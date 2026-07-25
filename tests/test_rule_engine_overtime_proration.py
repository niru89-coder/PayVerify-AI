"""Unit tests for MY_OT_001 (overtime multipliers) and MY_PRORATION_001
(calendar-day proration), per MY Labour law and statutory calculation.txt."""
from overtime import calculate_overtime, hourly_rate_of_pay
from proration import calculate_proration
from base import RuleStatus


def test_hourly_rate_of_pay_formula():
    # HRP = Monthly Basic Wages / 26 / daily normal hours
    assert hourly_rate_of_pay(2080.0, 8.0) == round(2080.0 / 26 / 8, 4)


def test_normal_working_day_1_5x():
    result = calculate_overtime(monthly_basic_wages=2080.0, ot_hours=2, day_type="normal_working_day")
    hrp = hourly_rate_of_pay(2080.0, 8.0)
    assert result.status == RuleStatus.OK
    assert result.expected_total_amount == round(hrp * 1.5 * 2, 2)


def test_rest_day_exceeding_hours_2x():
    result = calculate_overtime(monthly_basic_wages=2080.0, ot_hours=3, day_type="rest_day")
    hrp = hourly_rate_of_pay(2080.0, 8.0)
    assert result.expected_total_amount == round(hrp * 2.0 * 3, 2)


def test_public_holiday_3x():
    result = calculate_overtime(monthly_basic_wages=2080.0, ot_hours=4, day_type="public_holiday")
    hrp = hourly_rate_of_pay(2080.0, 8.0)
    assert result.expected_total_amount == round(hrp * 3.0 * 4, 2)


def test_rest_day_standard_hours_pending_sme_validation():
    result = calculate_overtime(
        monthly_basic_wages=2080.0, ot_hours=8, day_type="rest_day", rest_day_standard_hours_worked=True
    )
    assert result.status == RuleStatus.PENDING_SME_VALIDATION


def test_proration_new_joiner_mid_month():
    # 30-day month, employee eligible for 15 days -> half pay
    result = calculate_proration(monthly_amount=3000.0, year=2026, month=4, eligible_days=15)
    assert result.status == RuleStatus.OK
    assert result.expected_total_amount == 1500.0


def test_proration_full_month():
    result = calculate_proration(monthly_amount=3000.0, year=2026, month=2, eligible_days=28)
    assert result.expected_total_amount == 3000.0

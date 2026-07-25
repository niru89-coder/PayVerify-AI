"""
MY_OT_001 - Overtime pay calculation.

Source: "MY Labour law and statutory calculation.txt" (verbatim):
  "Normal Working Day: 1.5 times the hourly rate for any work exceeding the
   regular daily limit (over 8 hours).
   Rest Day: 2.0 times the hourly rate if working beyond normal hours, or
   specific half/full-day ordinary rates if working standard hours on a rest
   day.
   Public Holiday: 3.0 times the hourly rate. [1, 2, 3]
   Hourly Rate of Pay (HRP): Monthly Basic Wages % 26 %Daily normal working
   hours (usually 8)"

HRP formula transcribed literally uses "%" where the source clearly intends
division (Monthly Basic Wages / 26 / daily normal working hours) - "26" being
the standard days-per-month divisor used in Malaysian OT calculations.

The Rest Day "specific half/full-day ordinary rates if working standard hours"
sub-case is NOT fully specified in the source (no numeric multiplier given for
that specific scenario) - marked pending SME validation; the 2.0x multiplier
is used whenever hours worked exceed normal hours on a rest day, which IS
fully specified.
"""
from __future__ import annotations

from base import RuleResult, RuleStatus

RULE_ID = "MY_OT_001"
SOURCE = "MY Labour law and statutory calculation.txt"

DAYS_DIVISOR = 26

MULTIPLIERS = {
    "normal_working_day": 1.5,
    "rest_day_exceeding_normal_hours": 2.0,
    "public_holiday": 3.0,
}


def hourly_rate_of_pay(monthly_basic_wages: float, daily_normal_hours: float = 8.0) -> float:
    return round(monthly_basic_wages / DAYS_DIVISOR / daily_normal_hours, 4)


def calculate_overtime(
    monthly_basic_wages: float,
    ot_hours: float,
    day_type: str,
    daily_normal_hours: float = 8.0,
    rest_day_standard_hours_worked: bool = False,
) -> RuleResult:
    hrp = hourly_rate_of_pay(monthly_basic_wages, daily_normal_hours)

    if day_type == "rest_day" and rest_day_standard_hours_worked:
        return RuleResult(
            rule_id=RULE_ID,
            component="Overtime",
            status=RuleStatus.PENDING_SME_VALIDATION,
            explanation=(
                "Source document specifies 'specific half/full-day ordinary rates' for "
                "standard-hours work on a rest day, without giving the exact numeric "
                "multiplier. Requires SME Validation before this scenario can be computed."
            ),
            source=SOURCE,
            metadata={"hourly_rate_of_pay": hrp},
        )

    key = "rest_day_exceeding_normal_hours" if day_type == "rest_day" else day_type
    multiplier = MULTIPLIERS.get(key)
    if multiplier is None:
        return RuleResult(
            rule_id=RULE_ID,
            component="Overtime",
            status=RuleStatus.ERROR,
            explanation=f"Unknown day_type '{day_type}'.",
            source=SOURCE,
        )

    amount = round(hrp * multiplier * ot_hours, 2)
    return RuleResult(
        rule_id=RULE_ID,
        component="Overtime",
        status=RuleStatus.OK,
        expected_employee_amount=amount,
        expected_employer_amount=amount,
        expected_total_amount=amount,
        explanation=(
            f"HRP = {monthly_basic_wages:,.2f} / {DAYS_DIVISOR} / {daily_normal_hours} = RM{hrp:.4f}; "
            f"OT pay = HRP x {multiplier} x {ot_hours}h = RM{amount:,.2f} ({day_type})."
        ),
        source=SOURCE,
        metadata={"hourly_rate_of_pay": hrp, "multiplier": multiplier, "ot_hours": ot_hours, "day_type": day_type},
    )

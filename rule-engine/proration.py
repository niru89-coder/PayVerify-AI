"""
MY_PRORATION_001 - Calendar-day proration of fixed income components.

Source: "MY Labour law and statutory calculation.txt" (verbatim):
  "Fixed Income such as Basic salary, Transport allowance etc should follow
   Calendar days proration for new joiner, exit and unpaid leave during the
   month."

Formula (standard calendar-day proration, applying the stated rule): the
monthly fixed-income amount is prorated by the ratio of eligible calendar
days in the month to total calendar days in the month.
"""
from __future__ import annotations

import calendar

from base import RuleResult, RuleStatus

RULE_ID = "MY_PRORATION_001"
SOURCE = "MY Labour law and statutory calculation.txt"


def calculate_proration(
    monthly_amount: float,
    year: int,
    month: int,
    eligible_days: int,
) -> RuleResult:
    total_days = calendar.monthrange(year, month)[1]
    if eligible_days < 0 or eligible_days > total_days:
        return RuleResult(
            rule_id=RULE_ID,
            component="Proration",
            status=RuleStatus.ERROR,
            explanation=f"eligible_days ({eligible_days}) out of range for {year}-{month:02d} ({total_days} days).",
            source=SOURCE,
        )

    prorated = round(monthly_amount * eligible_days / total_days, 2)
    return RuleResult(
        rule_id=RULE_ID,
        component="Proration",
        status=RuleStatus.OK,
        expected_employee_amount=prorated,
        expected_employer_amount=prorated,
        expected_total_amount=prorated,
        explanation=(
            f"Prorated = RM{monthly_amount:,.2f} x {eligible_days}/{total_days} calendar days = RM{prorated:,.2f}."
        ),
        source=SOURCE,
        metadata={"total_days": total_days, "eligible_days": eligible_days},
    )

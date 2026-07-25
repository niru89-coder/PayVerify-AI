"""
MY_EPF_001 - Employees Provident Fund (KWSP) monthly contribution.

Source: EPF employee and employer contribution 10. Effective 1 October 2025.pdf
(see docs/markdown/epf-employee-and-employer-contribution-10-effective-1-october-2025.md)

The source PDF's Third Schedule (Parts A, C, E, F; Parts B and D were repealed
by Act A1760/2025) specifies a fixed-amount table for wages up to RM20,000 and
an exact-percentage rule above RM20,000. Row-by-row verification against the
extracted table (see knowledge-base/malaysia/epf.md "Formula Verification"
section) confirmed every sampled row equals:

    amount = ceil_to_next_ringgit(rate * band_upper_bound)

...where `band_upper_bound` is the upper bound of the RM20 band (wages <=
RM5,000) or RM100 band (RM5,000 < wages <= RM20,000) the wage falls into, and
`rate` depends on which Part applies. This is implemented as a formula (not a
hand-copied 650-row table) to eliminate manual transcription risk, and is
unit-tested against multiple rows read directly from the source PDF.

Parts implemented:
  Part A - age < 60, Malaysian citizen OR permanent resident OR non-citizen who
           elected to contribute before 1 Aug 1998: employee 11%; employer 13%
           (wage <= RM5,000) / 12% (wage > RM5,000).
  Part C - age >= 60, permanent resident OR non-citizen elected before 1 Aug
           1998 (NOT plain Malaysian citizens - see Part E): employee 5.5%;
           employer 6.5% (wage <= RM5,000) / 6% (wage > RM5,000).
  Part E - age >= 60, Malaysian citizen: employee 0%; employer 4%.
  Part F - non-Malaysian citizen, not PR, not a pre-1998 elector (typical
           foreign worker): employee 2%; employer 2% (flat, on actual wage,
           no banding - PART F does not use the banded table).

Eligibility (age 14-75 mandatory) is per "MY Labour law and statutory
calculation.txt" - Requires SME Validation for the exact legal citation to the
EPF Act since this specific PDF only contains the rate schedule.
"""
from __future__ import annotations

import math

from base import EmployeeContext, RuleResult, RuleStatus, WageContext, ceil_to_ringgit

RULE_ID = "MY_EPF_001"
SOURCE = "EPF employee and employer contribution 10. Effective 1 October 2025.pdf (Third Schedule, Parts A/C/E/F)"

MIN_AGE = 14
MAX_AGE = 75


def _band_upper_bound(wage: float) -> float:
    if wage <= 5000:
        return math.ceil(wage / 20) * 20 if wage % 20 != 0 else wage
    return math.ceil(wage / 100) * 100 if wage % 100 != 0 else wage


def _part_a(wage: float) -> tuple[float, float]:
    if wage <= 10:
        return 0.0, 0.0
    if wage <= 20000:
        upper = _band_upper_bound(wage)
        employer_rate = 0.13 if upper <= 5000 else 0.12
        return ceil_to_ringgit(0.11 * upper), ceil_to_ringgit(employer_rate * upper)
    return ceil_to_ringgit(0.11 * wage), ceil_to_ringgit(0.12 * wage)


def _part_c(wage: float) -> tuple[float, float]:
    if wage <= 10:
        return 0.0, 0.0
    if wage <= 20000:
        upper = _band_upper_bound(wage)
        employer_rate = 0.065 if upper <= 5000 else 0.06
        return ceil_to_ringgit(0.055 * upper), ceil_to_ringgit(employer_rate * upper)
    return ceil_to_ringgit(0.055 * wage), ceil_to_ringgit(0.06 * wage)


def _part_e(wage: float) -> tuple[float, float]:
    if wage <= 10:
        return 0.0, 0.0
    if wage <= 20000:
        upper = _band_upper_bound(wage)
        return 0.0, ceil_to_ringgit(0.04 * upper)
    return 0.0, ceil_to_ringgit(0.04 * wage)


def _part_f(wage: float) -> tuple[float, float]:
    return ceil_to_ringgit(0.02 * wage), ceil_to_ringgit(0.02 * wage)


def calculate_epf(employee: EmployeeContext, wage: WageContext) -> RuleResult:
    epf_wage = round(
        wage.basic_salary + wage.fixed_allowance + wage.other_epf_wages - wage.unpaid_leave_deduction, 2
    )

    if employee.age_years is not None and not (MIN_AGE <= employee.age_years <= MAX_AGE):
        return RuleResult(
            rule_id=RULE_ID,
            component="EPF",
            status=RuleStatus.NOT_APPLICABLE,
            expected_employee_amount=0.0,
            expected_employer_amount=0.0,
            expected_total_amount=0.0,
            explanation=(
                f"Employee age {employee.age_years} is outside the mandatory EPF age range "
                f"({MIN_AGE}-{MAX_AGE}); no statutory contribution expected."
            ),
            source=SOURCE,
            metadata={"epf_wage": epf_wage},
        )

    is_malaysian = employee.nationality == "MY"
    is_senior = (employee.age_years or 0) >= 60

    if is_malaysian and is_senior:
        part = "E"
        employee_amt, employer_amt = _part_e(epf_wage)
    elif is_malaysian and not is_senior:
        part = "A"
        employee_amt, employer_amt = _part_a(epf_wage)
    elif not is_malaysian and (employee.is_permanent_resident or employee.elected_before_1998_08_01) and is_senior:
        part = "C"
        employee_amt, employer_amt = _part_c(epf_wage)
    elif not is_malaysian and (employee.is_permanent_resident or employee.elected_before_1998_08_01) and not is_senior:
        part = "A"
        employee_amt, employer_amt = _part_a(epf_wage)
    elif not is_malaysian:
        part = "F"
        employee_amt, employer_amt = _part_f(epf_wage)
    else:
        return RuleResult(
            rule_id=RULE_ID,
            component="EPF",
            status=RuleStatus.PENDING_SME_VALIDATION,
            explanation="Unable to determine applicable EPF Part for this employee profile.",
            source=SOURCE,
            metadata={"epf_wage": epf_wage},
        )

    return RuleResult(
        rule_id=RULE_ID,
        component="EPF",
        status=RuleStatus.OK,
        expected_employee_amount=employee_amt,
        expected_employer_amount=employer_amt,
        expected_total_amount=round(employee_amt + employer_amt, 2),
        explanation=f"EPF Third Schedule Part {part} applied on EPF wage RM{epf_wage:,.2f}.",
        source=SOURCE,
        metadata={"epf_wage": epf_wage, "part": part},
    )

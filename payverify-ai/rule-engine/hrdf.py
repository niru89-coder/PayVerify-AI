"""
MY_HRDF_001 - Human Resources Development Fund (HRD Corp) levy.

Source: "MY Labour law and statutory calculation.txt" (verbatim):
  "LEVY = [(BASIC SALARY - UNPAID LEAVE) + FIXED ALLOWANCE] x 1%"

Eligibility (verbatim from same source):
  "Any citizen of Malaysia who is employed for wages under a contract of
  service (under full-time employment whether contract or permanent staff)
  with an employer, but does not include any domestic servant. If the company
  director/owner/partner is paid a salary, he/she is regarded as an employee
  of the company, whereas a director who only accepts director fees is not
  considered an employee."

Note: HRDF levy is fundamentally an EMPLOYER-level registration levy (the levy
rate/registration itself depends on the employer's HRD Corp registration
category and sector, not each individual employee). This calculator computes
the PER-EMPLOYEE wage base contribution to that levy, assuming the employer is
HRD-registered and required to contribute - employer registration status is
an employer master-data input out of scope for this per-employee rule and is
flagged accordingly.
"""
from __future__ import annotations

from base import EmployeeContext, RuleResult, RuleStatus, WageContext

RULE_ID = "MY_HRDF_001"
SOURCE = "MY Labour law and statutory calculation.txt"

LEVY_RATE = 0.01


def calculate_hrdf(employee: EmployeeContext, wage: WageContext, employer_hrdf_registered: bool = True) -> RuleResult:
    if employee.employment_type == "domestic_servant":
        return RuleResult(
            rule_id=RULE_ID,
            component="HRDF",
            status=RuleStatus.NOT_APPLICABLE,
            expected_employee_amount=0.0,
            expected_employer_amount=0.0,
            expected_total_amount=0.0,
            explanation="Domestic servants are explicitly excluded from HRDF levy eligibility.",
            source=SOURCE,
            metadata={},
        )

    if employee.is_director_fee_only:
        return RuleResult(
            rule_id=RULE_ID,
            component="HRDF",
            status=RuleStatus.NOT_APPLICABLE,
            expected_employee_amount=0.0,
            expected_employer_amount=0.0,
            expected_total_amount=0.0,
            explanation="A director who only accepts director fees (no salary) is not considered an employee for HRDF purposes.",
            source=SOURCE,
            metadata={},
        )

    if employee.nationality != "MY":
        return RuleResult(
            rule_id=RULE_ID,
            component="HRDF",
            status=RuleStatus.NOT_APPLICABLE,
            expected_employee_amount=0.0,
            expected_employer_amount=0.0,
            expected_total_amount=0.0,
            explanation="HRDF levy per source document applies to Malaysian citizens; non-citizen employee is not eligible.",
            source=SOURCE,
            metadata={},
        )

    if not employer_hrdf_registered:
        return RuleResult(
            rule_id=RULE_ID,
            component="HRDF",
            status=RuleStatus.NOT_APPLICABLE,
            explanation="Employer is not registered with HRD Corp; levy not applicable.",
            source=SOURCE,
            metadata={},
        )

    levy_base = round(wage.basic_salary - wage.unpaid_leave_deduction + wage.fixed_allowance, 2)
    levy = round(levy_base * LEVY_RATE, 2)

    return RuleResult(
        rule_id=RULE_ID,
        component="HRDF",
        status=RuleStatus.OK,
        expected_employee_amount=0.0,
        expected_employer_amount=levy,
        expected_total_amount=levy,
        explanation=f"LEVY = [(Basic Salary - Unpaid Leave) + Fixed Allowance] x 1% = RM{levy_base:,.2f} x 1% = RM{levy:,.2f}.",
        source=SOURCE,
        metadata={"levy_base": levy_base},
    )

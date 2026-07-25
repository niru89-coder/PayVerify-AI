"""
MY_SOCSO_001 - Social Security Organisation (PERKESO) monthly contribution.

Source: SOCSO employee and employer NewContributionRateIncludingSKBBK.pdf
(see docs/markdown/socso-employee-and-employer-newcontributionrateincludingskbbk.md
and the extracted lookup table rule-engine/rates/socso_rates.json, parsed
programmatically from the PDF's own tables - not manually re-typed).

Category 1 (Employment Injury + Invalidity Pension + SKBBK) vs Category 2
(Employment Injury + SKBBK only, no Invalidity Pension) is the categorisation
printed in the source document's column headers. The source PDF contains ONLY
the rate table; it does NOT state the eligibility test for which employees
fall into Category 1 vs Category 2. Per project policy this eligibility
mapping is marked "Requires SME Validation" - the commonly used industry rule
(Category 2 applies to employees who are 60 years or older, or foreign
workers not covered by the Invalidity Pension Scheme) is used here ONLY as a
placeholder default and MUST be confirmed by a compliance SME before
production use.

Wage ceiling: RM6,000 (row 65 in the source table repeats the RM5,900-6,000
amount for "wages exceed RM6,000", i.e. contributions are capped at the
RM6,000 band).
"""
from __future__ import annotations

import json
import pathlib

from base import EmployeeContext, RuleResult, RuleStatus, WageContext

RULE_ID = "MY_SOCSO_001"
SOURCE = "SOCSO employee and employer NewContributionRateIncludingSKBBK.pdf"

_RATES_PATH = pathlib.Path(__file__).resolve().parent / "rates" / "socso_rates.json"
_rates_cache: dict | None = None


def _load_rates() -> dict:
    global _rates_cache
    if _rates_cache is None:
        _rates_cache = json.loads(_RATES_PATH.read_text(encoding="utf-8"))
    return _rates_cache


def _find_band(wage: float, rows: list[dict]) -> dict | None:
    for row in rows:
        lo = row["wage_min_exclusive"]
        hi = row["wage_max_inclusive"]
        if hi is None:
            if wage > lo:
                return row
        elif lo < wage <= hi:
            return row
    return None


def calculate_socso(employee: EmployeeContext, wage: WageContext, category: int | None = None) -> RuleResult:
    """category: 1 or 2. If None, defaults via the placeholder SME-pending rule
    (age >= 60 -> Category 2, else Category 1)."""
    data = _load_rates()
    socso_wage = round(wage.basic_salary + wage.fixed_allowance + wage.other_epf_wages, 2)

    if category is None:
        category = 2 if (employee.age_years or 0) >= 60 else 1
        category_source = "pending_sme_validation_default"
    else:
        category_source = "explicit"

    row = _find_band(socso_wage, data["rows"])
    if row is None:
        return RuleResult(
            rule_id=RULE_ID,
            component="SOCSO",
            status=RuleStatus.ERROR,
            explanation=f"No SOCSO wage band matched for wage RM{socso_wage:,.2f}.",
            source=SOURCE,
            metadata={"socso_wage": socso_wage},
        )

    cat_key = f"category_{category}"
    amounts = row[cat_key]

    status = RuleStatus.OK if category_source == "explicit" else RuleStatus.PENDING_SME_VALIDATION
    return RuleResult(
        rule_id=RULE_ID,
        component="SOCSO",
        status=status,
        expected_employee_amount=amounts["employee"],
        expected_employer_amount=amounts["employer_total"],
        expected_total_amount=amounts["total"],
        explanation=(
            f"SOCSO Category {category} rate applied for wage band "
            f"RM{row['wage_min_exclusive']:,.2f}-{row['wage_max_inclusive']}."
            + (" Category assignment is a placeholder pending SME validation." if category_source != "explicit" else "")
        ),
        source=SOURCE,
        metadata={"socso_wage": socso_wage, "category": category, "category_source": category_source},
    )

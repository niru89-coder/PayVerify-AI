"""Unit tests for MY_SOCSO_001 against the extracted rate table."""
from base import EmployeeContext, RuleStatus, WageContext
from socso import calculate_socso


def emp(age=30) -> EmployeeContext:
    return EmployeeContext(employee_id="E1", nationality="MY", age_years=age)


def wage(basic: float) -> WageContext:
    return WageContext(basic_salary=basic)


def test_first_band_category_1():
    # Source row 1: wages up to RM30 -> category1 employee 0.40, employer 0.30, total 0.70
    result = calculate_socso(emp(age=30), wage(30.0), category=1)
    assert result.status == RuleStatus.OK
    assert result.expected_employee_amount == 0.4
    assert result.expected_employer_amount == 0.3
    assert result.expected_total_amount == 0.7


def test_first_band_category_2():
    result = calculate_socso(emp(age=30), wage(30.0), category=2)
    assert result.expected_employee_amount == 0.3
    assert result.expected_employer_amount == 0.2
    assert result.expected_total_amount == 0.5


def test_wage_ceiling_row_65():
    # Source row 65: wages exceed RM6,000 -> capped at the RM5,900-6,000 amount
    result = calculate_socso(emp(age=30), wage(10000.0), category=1)
    assert result.expected_employee_amount == 104.15
    assert result.expected_employer_amount == 74.4
    assert result.expected_total_amount == 178.55


def test_default_category_by_age_is_pending_sme_validation():
    result = calculate_socso(emp(age=61), wage(30.0))
    assert result.status == RuleStatus.PENDING_SME_VALIDATION
    assert result.metadata["category"] == 2

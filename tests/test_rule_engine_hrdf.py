"""Unit tests for MY_HRDF_001 (levy formula) per MY Labour law and statutory
calculation.txt: LEVY = [(BASIC SALARY - UNPAID LEAVE) + FIXED ALLOWANCE] x 1%"""
from base import EmployeeContext, RuleStatus, WageContext
from hrdf import calculate_hrdf


def test_levy_formula():
    employee = EmployeeContext(employee_id="E1", nationality="MY")
    wage = WageContext(basic_salary=5000.0, unpaid_leave_deduction=200.0, fixed_allowance=300.0)
    result = calculate_hrdf(employee, wage)
    assert result.status == RuleStatus.OK
    # (5000 - 200 + 300) * 1% = 51.00
    assert result.expected_employer_amount == 51.0
    assert result.expected_employee_amount == 0.0


def test_domestic_servant_excluded():
    employee = EmployeeContext(employee_id="E1", nationality="MY", employment_type="domestic_servant")
    wage = WageContext(basic_salary=3000.0)
    result = calculate_hrdf(employee, wage)
    assert result.status == RuleStatus.NOT_APPLICABLE


def test_director_fee_only_excluded():
    employee = EmployeeContext(employee_id="E1", nationality="MY", is_director_fee_only=True)
    wage = WageContext(basic_salary=3000.0)
    result = calculate_hrdf(employee, wage)
    assert result.status == RuleStatus.NOT_APPLICABLE


def test_non_malaysian_excluded():
    employee = EmployeeContext(employee_id="E1", nationality="ID")
    wage = WageContext(basic_salary=3000.0)
    result = calculate_hrdf(employee, wage)
    assert result.status == RuleStatus.NOT_APPLICABLE


def test_employer_not_registered():
    employee = EmployeeContext(employee_id="E1", nationality="MY")
    wage = WageContext(basic_salary=3000.0)
    result = calculate_hrdf(employee, wage, employer_hrdf_registered=False)
    assert result.status == RuleStatus.NOT_APPLICABLE

"""Unit tests for MY_EPF_001, spot-checked directly against rows read from the
source PDF (EPF employee and employer contribution 10. Effective 1 October
2025.pdf) to prove the formula reproduces the statutory table exactly."""
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "rule-engine"))

from base import EmployeeContext, RuleStatus, WageContext  # noqa: E402
from epf import calculate_epf  # noqa: E402


def emp(nationality="MY", age=30, pr=False, pre1998=False) -> EmployeeContext:
    return EmployeeContext(
        employee_id="E1",
        nationality=nationality,
        age_years=age,
        is_permanent_resident=pr,
        elected_before_1998_08_01=pre1998,
    )


def wage(basic: float) -> WageContext:
    return WageContext(basic_salary=basic)


def test_part_a_wage_120_matches_source_table():
    # Source: "From 100.01 to 120.00 | 16.00 | 14.00 | 30.00" -> employer 16, employee 14
    # (row applies to wages in the (100, 120] band, so use the band's upper bound)
    result = calculate_epf(emp(age=30), wage(120.0))
    assert result.status == RuleStatus.OK
    assert result.expected_employer_amount == 16.0
    assert result.expected_employee_amount == 14.0


def test_part_a_wage_240_matches_source_table():
    # Source: "From 220.01 to 240.00 | 32.00 | 27.00 | 59.00"
    result = calculate_epf(emp(age=30), wage(240.0))
    assert result.expected_employer_amount == 32.0
    assert result.expected_employee_amount == 27.0


def test_part_a_wage_5000_matches_source_table():
    # Source: employer 650.00, employee 550.00, total 1200.00 (13%/11% at RM5,000 boundary)
    result = calculate_epf(emp(age=30), wage(5000.0))
    assert result.expected_employer_amount == 650.0
    assert result.expected_employee_amount == 550.0


def test_part_a_wage_5100_matches_source_table():
    # Source: "From 5,000.01 to 5,100.00 | 612.00 | 561.00 | 1,173.00" (12%/11% above RM5,000)
    result = calculate_epf(emp(age=30), wage(5100.0))
    assert result.expected_employer_amount == 612.0
    assert result.expected_employee_amount == 561.0


def test_part_a_wage_20000_boundary():
    # Source: "From 19,900.01 to 20,000.00 | 2,400.00 | 2,200.00 | 4,600.00"
    result = calculate_epf(emp(age=30), wage(20000.0))
    assert result.expected_employer_amount == 2400.0
    assert result.expected_employee_amount == 2200.0


def test_part_a_wage_above_20000_uses_exact_percentage():
    # Source: exact 12% employer / 11% employee on actual wage above RM20,000
    result = calculate_epf(emp(age=30), wage(25000.0))
    assert result.expected_employer_amount == 3000.0  # 12% * 25000
    assert result.expected_employee_amount == 2750.0  # 11% * 25000


def test_part_e_malaysian_citizen_60_plus():
    # Source Part E: "From 100.01 to 120.00 | 5.00 | 0.00 | 5.00"
    result = calculate_epf(emp(age=61), wage(120.0))
    assert result.status == RuleStatus.OK
    assert result.expected_employer_amount == 5.0
    assert result.expected_employee_amount == 0.0
    assert result.metadata["part"] == "E"


def test_part_c_pr_60_plus_half_of_part_a():
    # Source Part C: "From 220.01 to 240.00 | 16.00 | 14.00 | 30.00" (half of Part A's 32/27,
    # rounded up independently)
    result = calculate_epf(emp(nationality="SG", age=61, pr=True), wage(240.0))
    assert result.expected_employer_amount == 16.0
    assert result.expected_employee_amount == 14.0
    assert result.metadata["part"] == "C"


def test_part_f_foreign_worker_flat_2_percent():
    result = calculate_epf(emp(nationality="ID", age=30, pr=False, pre1998=False), wage(2000.0))
    assert result.status == RuleStatus.OK
    assert result.expected_employer_amount == 40.0  # 2% * 2000
    assert result.expected_employee_amount == 40.0
    assert result.metadata["part"] == "F"


def test_wage_below_10_is_nil():
    result = calculate_epf(emp(age=30), wage(8.0))
    assert result.expected_employer_amount == 0.0
    assert result.expected_employee_amount == 0.0


def test_age_outside_mandatory_range_not_applicable():
    result = calculate_epf(emp(age=80), wage(3000.0))
    assert result.status == RuleStatus.NOT_APPLICABLE

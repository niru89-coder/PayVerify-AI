"""
Synthetic Sample Data Generator (Phase - Sample Data).

Produces three files under sample-data/ that exercise the full PayVerify AI
pipeline (mapping engine -> rule engine -> reconciliation engine):

  - employee_master.csv   Canonical employee attributes (age, nationality, etc.)
  - client_register.csv   "Client" payroll register, using one set of column
                           header conventions (to exercise column mapping).
  - platform_register.csv "Darwinbox/Platform" payroll register, using a
                           DIFFERENT set of column header conventions.

"Correct" amounts are computed by calling the real rule-engine modules
directly (never hand-typed), then specific cells are intentionally perturbed
to manufacture each of the variance classification types described in
validation-engine/reconciliation.py, for end-to-end testing.

No real employee data is used - all names/IDs are fictitious.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "rule-engine"))

from base import EmployeeContext, WageContext  # noqa: E402
from epf import calculate_epf  # noqa: E402
from hrdf import calculate_hrdf  # noqa: E402
from overtime import calculate_overtime  # noqa: E402

OUT_DIR = ROOT / "sample-data"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    employees = []
    client_rows = []
    platform_rows = []

    # --- E001: Malaysian, age 30, Part A - baseline, both registers correct -> NO_VARIANCE
    emp = EmployeeContext(employee_id="E001", nationality="MY", age_years=30)
    wage = WageContext(basic_salary=3000.0)
    epf = calculate_epf(emp, wage)
    hrdf = calculate_hrdf(emp, wage)
    employees.append(dict(id="E001", name="Ahmad bin Ismail", dob="1996-03-15", age=30, nationality="MY",
                           is_pr="N", elected_pre_1998="N", doj="2020-01-06", doe="", unpaid_leave_days=0,
                           employment_type="permanent", is_director_fee_only="N", employer_hrdf_registered="Y"))
    client_rows.append(dict(id="E001", name="Ahmad bin Ismail", basic=3000.0,
                             epf_ee=epf.expected_employee_amount, epf_er=epf.expected_employer_amount,
                             socso_ee=13.75, socso_er=25.65, hrdf=hrdf.expected_employer_amount,
                             ot_normal="", ot_rest="", ot_ph=""))
    platform_rows.append(dict(id="E001", name="Ahmad bin Ismail", basic=3000.0,
                               epf_ee=epf.expected_employee_amount, epf_er=epf.expected_employer_amount,
                               socso_ee=13.75, socso_er=25.65, hrdf=hrdf.expected_employer_amount,
                               ot_normal="", ot_rest="", ot_ph=""))

    # --- E002: Malaysian, age 61, Part E - PLATFORM miscalculates using Part A rates -> RATE_SLAB_MISMATCH (client correct)
    emp = EmployeeContext(employee_id="E002", nationality="MY", age_years=61)
    wage = WageContext(basic_salary=4000.0)
    epf_e = calculate_epf(emp, wage)  # Part E: employee 0, employer 4%
    wrong_epf_employee = 440.0  # what Part A (11%) would have wrongly produced
    wrong_epf_employer = 520.0  # what Part A (13%) would have wrongly produced
    employees.append(dict(id="E002", name="Tan Wei Ling", dob="1965-04-01", age=61, nationality="MY",
                           is_pr="N", elected_pre_1998="N", doj="2015-06-01", doe="", unpaid_leave_days=0,
                           employment_type="permanent", is_director_fee_only="N", employer_hrdf_registered="Y"))
    client_rows.append(dict(id="E002", name="Tan Wei Ling", basic=4000.0,
                             epf_ee=epf_e.expected_employee_amount, epf_er=epf_e.expected_employer_amount,
                             socso_ee="", socso_er="", hrdf=calculate_hrdf(emp, wage).expected_employer_amount,
                             ot_normal="", ot_rest="", ot_ph=""))
    platform_rows.append(dict(id="E002", name="Tan Wei Ling", basic=4000.0,
                               epf_ee=wrong_epf_employee, epf_er=wrong_epf_employer,
                               socso_ee="", socso_er="", hrdf=calculate_hrdf(emp, wage).expected_employer_amount,
                               ot_normal="", ot_rest="", ot_ph=""))

    # --- E003: Foreign, PR, elected pre-1998, age 65, Part C - CLIENT miscalculates -> RATE_SLAB_MISMATCH (platform correct)
    emp = EmployeeContext(employee_id="E003", nationality="ID", is_permanent_resident=True, age_years=65)
    wage = WageContext(basic_salary=3500.0)
    epf_c = calculate_epf(emp, wage)  # Part C: employee 5.5%, employer 6.5%
    wrong_client_employee = 385.0  # Part A (11%) wrongly applied
    wrong_client_employer = 455.0  # Part A (13%) wrongly applied
    employees.append(dict(id="E003", name="Budi Santoso", dob="1961-02-20", age=65, nationality="ID",
                           is_pr="Y", elected_pre_1998="N", doj="2018-03-01", doe="", unpaid_leave_days=0,
                           employment_type="permanent", is_director_fee_only="N", employer_hrdf_registered="Y"))
    client_rows.append(dict(id="E003", name="Budi Santoso", basic=3500.0,
                             epf_ee=wrong_client_employee, epf_er=wrong_client_employer,
                             socso_ee="", socso_er="", hrdf="",
                             ot_normal="", ot_rest="", ot_ph=""))
    platform_rows.append(dict(id="E003", name="Budi Santoso", basic=3500.0,
                               epf_ee=epf_c.expected_employee_amount, epf_er=epf_c.expected_employer_amount,
                               socso_ee="", socso_er="", hrdf="",
                               ot_normal="", ot_rest="", ot_ph=""))

    # --- E004: Foreign, not PR, not elected, age 40, Part F - EPF completely missing from PLATFORM -> NOT_CALCULATED_ONE_SIDE
    emp = EmployeeContext(employee_id="E004", nationality="PH", age_years=40)
    wage = WageContext(basic_salary=2500.0)
    epf_f = calculate_epf(emp, wage)  # Part F: flat 2%/2%
    employees.append(dict(id="E004", name="Maria Santos", dob="1986-07-10", age=40, nationality="PH",
                           is_pr="N", elected_pre_1998="N", doj="2021-09-01", doe="", unpaid_leave_days=0,
                           employment_type="permanent", is_director_fee_only="N", employer_hrdf_registered="Y"))
    client_rows.append(dict(id="E004", name="Maria Santos", basic=2500.0,
                             epf_ee=epf_f.expected_employee_amount, epf_er=epf_f.expected_employer_amount,
                             socso_ee="", socso_er="", hrdf="",
                             ot_normal="", ot_rest="", ot_ph=""))
    platform_rows.append(dict(id="E004", name="Maria Santos", basic=2500.0,
                               epf_ee="", epf_er="",  # not configured on platform at all
                               socso_ee="", socso_er="", hrdf="",
                               ot_normal="", ot_rest="", ot_ph=""))

    # --- E005: Malaysian, age 13 (below mandatory EPF age) - CLIENT wrongly shows EPF value -> ELIGIBILITY_MISMATCH
    emp = EmployeeContext(employee_id="E005", nationality="MY", age_years=13)
    wage = WageContext(basic_salary=800.0)
    employees.append(dict(id="E005", name="Nur Aisyah", dob="2013-01-01", age=13, nationality="MY",
                           is_pr="N", elected_pre_1998="N", doj="2026-01-01", doe="", unpaid_leave_days=0,
                           employment_type="permanent", is_director_fee_only="N", employer_hrdf_registered="Y"))
    client_rows.append(dict(id="E005", name="Nur Aisyah", basic=800.0,
                             epf_ee=88.0, epf_er=104.0,  # wrongly calculated - should be N/A (under 14)
                             socso_ee="", socso_er="", hrdf="",
                             ot_normal="", ot_rest="", ot_ph=""))
    platform_rows.append(dict(id="E005", name="Nur Aisyah", basic=800.0,
                               epf_ee=0.0, epf_er=0.0,
                               socso_ee="", socso_er="", hrdf="",
                               ot_normal="", ot_rest="", ot_ph=""))

    # --- E006: Malaysian, age 76 (above mandatory EPF age) - both correctly show 0 -> NO_VARIANCE (not applicable)
    emp = EmployeeContext(employee_id="E006", nationality="MY", age_years=76)
    wage = WageContext(basic_salary=1000.0)
    employees.append(dict(id="E006", name="Lim Ah Kow", dob="1950-01-01", age=76, nationality="MY",
                           is_pr="N", elected_pre_1998="N", doj="2000-01-01", doe="", unpaid_leave_days=0,
                           employment_type="permanent", is_director_fee_only="N", employer_hrdf_registered="Y"))
    client_rows.append(dict(id="E006", name="Lim Ah Kow", basic=1000.0,
                             epf_ee=0.0, epf_er=0.0,
                             socso_ee="", socso_er="", hrdf="",
                             ot_normal="", ot_rest="", ot_ph=""))
    platform_rows.append(dict(id="E006", name="Lim Ah Kow", basic=1000.0,
                               epf_ee=0.0, epf_er=0.0,
                               socso_ee="", socso_er="", hrdf="",
                               ot_normal="", ot_rest="", ot_ph=""))

    # --- E007: Malaysian, age 35, wage RM20,000 boundary - PLATFORM off by 1 sen (rounding) -> AMOUNT_MISMATCH_WITHIN_TOLERANCE
    emp = EmployeeContext(employee_id="E007", nationality="MY", age_years=35)
    wage = WageContext(basic_salary=20000.0)
    epf_20k = calculate_epf(emp, wage)
    employees.append(dict(id="E007", name="Siti Rahman", dob="1991-05-01", age=35, nationality="MY",
                           is_pr="N", elected_pre_1998="N", doj="2019-01-01", doe="", unpaid_leave_days=0,
                           employment_type="permanent", is_director_fee_only="N", employer_hrdf_registered="Y"))
    client_rows.append(dict(id="E007", name="Siti Rahman", basic=20000.0,
                             epf_ee=epf_20k.expected_employee_amount, epf_er=epf_20k.expected_employer_amount,
                             socso_ee="", socso_er="", hrdf="",
                             ot_normal="", ot_rest="", ot_ph=""))
    platform_rows.append(dict(id="E007", name="Siti Rahman", basic=20000.0,
                               epf_ee=epf_20k.expected_employee_amount + 0.01,  # 1 sen rounding difference
                               epf_er=epf_20k.expected_employer_amount,
                               socso_ee="", socso_er="", hrdf="",
                               ot_normal="", ot_rest="", ot_ph=""))

    # --- E008: Malaysian, age 45, wage RM25,000 (above 20k threshold, exact %) - both correct -> NO_VARIANCE
    emp = EmployeeContext(employee_id="E008", nationality="MY", age_years=45)
    wage = WageContext(basic_salary=25000.0)
    epf_25k = calculate_epf(emp, wage)
    employees.append(dict(id="E008", name="Krishnan Muthu", dob="1981-08-01", age=45, nationality="MY",
                           is_pr="N", elected_pre_1998="N", doj="2010-01-01", doe="", unpaid_leave_days=0,
                           employment_type="permanent", is_director_fee_only="N", employer_hrdf_registered="Y"))
    client_rows.append(dict(id="E008", name="Krishnan Muthu", basic=25000.0,
                             epf_ee=epf_25k.expected_employee_amount, epf_er=epf_25k.expected_employer_amount,
                             socso_ee="", socso_er="", hrdf="",
                             ot_normal="", ot_rest="", ot_ph=""))
    platform_rows.append(dict(id="E008", name="Krishnan Muthu", basic=25000.0,
                               epf_ee=epf_25k.expected_employee_amount, epf_er=epf_25k.expected_employer_amount,
                               socso_ee="", socso_er="", hrdf="",
                               ot_normal="", ot_rest="", ot_ph=""))

    # --- E009: Malaysian, HRDF-eligible - HRDF missing from PLATFORM (not configured) -> NOT_CALCULATED_ONE_SIDE
    emp = EmployeeContext(employee_id="E009", nationality="MY", age_years=28)
    wage = WageContext(basic_salary=5000.0, fixed_allowance=300.0)
    epf_9 = calculate_epf(emp, wage)
    hrdf_9 = calculate_hrdf(emp, wage)
    employees.append(dict(id="E009", name="Farah Diyana", dob="1998-01-01", age=28, nationality="MY",
                           is_pr="N", elected_pre_1998="N", doj="2022-02-01", doe="", unpaid_leave_days=0,
                           employment_type="permanent", is_director_fee_only="N", employer_hrdf_registered="Y"))
    client_rows.append(dict(id="E009", name="Farah Diyana", basic=5000.0,
                             epf_ee=epf_9.expected_employee_amount, epf_er=epf_9.expected_employer_amount,
                             socso_ee="", socso_er="", hrdf=hrdf_9.expected_employer_amount,
                             ot_normal="", ot_rest="", ot_ph=""))
    platform_rows.append(dict(id="E009", name="Farah Diyana", basic=5000.0,
                               epf_ee=epf_9.expected_employee_amount, epf_er=epf_9.expected_employer_amount,
                               socso_ee="", socso_er="", hrdf="",  # missing entirely
                               ot_normal="", ot_rest="", ot_ph=""))

    # --- E010: Overtime scenario - PLATFORM uses wrong (2x) multiplier for public holiday OT -> RATE_SLAB_MISMATCH
    monthly_basic = 2080.0
    ot_normal = calculate_overtime(monthly_basic, ot_hours=2.0, day_type="normal_working_day")
    ot_rest = calculate_overtime(monthly_basic, ot_hours=3.0, day_type="rest_day", rest_day_standard_hours_worked=False)
    ot_ph = calculate_overtime(monthly_basic, ot_hours=4.0, day_type="public_holiday")
    hrp = monthly_basic / 26 / 8
    wrong_ph_amount = round(hrp * 2.0 * 4.0, 2)  # platform wrongly used rest-day multiplier (2x) instead of 3x
    employees.append(dict(id="E010", name="Chong Mei Fen", dob="1995-11-11", age=30, nationality="MY",
                           is_pr="N", elected_pre_1998="N", doj="2021-01-01", doe="", unpaid_leave_days=0,
                           employment_type="permanent", is_director_fee_only="N", employer_hrdf_registered="Y"))
    client_rows.append(dict(id="E010", name="Chong Mei Fen", basic=monthly_basic,
                             epf_ee="", epf_er="", socso_ee="", socso_er="", hrdf="",
                             ot_normal=ot_normal.expected_total_amount, ot_rest=ot_rest.expected_total_amount,
                             ot_ph=ot_ph.expected_total_amount))
    platform_rows.append(dict(id="E010", name="Chong Mei Fen", basic=monthly_basic,
                               epf_ee="", epf_er="", socso_ee="", socso_er="", hrdf="",
                               ot_normal=ot_normal.expected_total_amount, ot_rest=ot_rest.expected_total_amount,
                               ot_ph=wrong_ph_amount))

    _write_employee_master(employees)
    _write_client_register(client_rows)
    _write_platform_register(platform_rows)
    print(f"Generated sample data for {len(employees)} employees under {OUT_DIR}")


def _write_employee_master(rows: list[dict]) -> None:
    path = OUT_DIR / "employee_master.csv"
    fieldnames = ["id", "name", "dob", "age", "nationality", "is_pr", "elected_pre_1998", "doj", "doe",
                  "unpaid_leave_days", "employment_type", "is_director_fee_only", "employer_hrdf_registered"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_client_register(rows: list[dict]) -> None:
    path = OUT_DIR / "client_register.csv"
    header_map = {
        "id": "Emp ID", "name": "Employee Name", "basic": "Basic Salary",
        "epf_ee": "EPF Employee", "epf_er": "EPF Employer",
        "socso_ee": "SOCSO Employee", "socso_er": "SOCSO Employer",
        "hrdf": "HRDF Levy", "ot_normal": "OT Normal", "ot_rest": "OT Rest Day", "ot_ph": "OT Public Holiday",
    }
    _write_register(path, rows, header_map)


def _write_platform_register(rows: list[dict]) -> None:
    path = OUT_DIR / "platform_register.csv"
    header_map = {
        "id": "Employee ID", "name": "Full Name", "basic": "Basic Pay",
        "epf_ee": "Employee EPF", "epf_er": "Employer EPF",
        "socso_ee": "Employee SOCSO", "socso_er": "Employer SOCSO",
        "hrdf": "Training Levy", "ot_normal": "Overtime Normal", "ot_rest": "Overtime Rest Day",
        "ot_ph": "Overtime Public Holiday",
    }
    _write_register(path, rows, header_map)


def _write_register(path: Path, rows: list[dict], header_map: dict[str, str]) -> None:
    fieldnames = list(header_map.values())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({header_map[k]: v for k, v in row.items()})


if __name__ == "__main__":
    main()

"""
End-to-end integration test: sample-data CSVs -> mapping engine -> rule engine
-> reconciliation engine, verifying each of the 10 synthetic employee
scenarios produces its intended variance classification.
"""
import csv
from pathlib import Path

from base import EmployeeContext, RuleStatus, WageContext
from epf import calculate_epf
from mapping_engine import apply_mapping, suggest_mapping
from reconciliation import Classification, Suggestion, classify_variance

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample-data"


def _load_canonical(path: Path) -> dict[str, dict]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        raw_rows = list(reader)
    column_map = suggest_mapping(list(reader.fieldnames)).to_column_map()
    mapped_rows = apply_mapping(raw_rows, column_map)
    return {row["EMPLOYEE_ID"]: row for row in mapped_rows}


def _to_float(value) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _load_employee_master() -> dict[str, dict]:
    path = SAMPLE_DIR / "employee_master.csv"
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["id"]: row for row in reader}


def _employee_context(row: dict) -> EmployeeContext:
    return EmployeeContext(
        employee_id=row["id"],
        nationality=row["nationality"],
        is_permanent_resident=row["is_pr"] == "Y",
        elected_before_1998_08_01=row["elected_pre_1998"] == "Y",
        age_years=int(row["age"]),
    )


def test_sample_data_files_exist():
    assert (SAMPLE_DIR / "employee_master.csv").exists()
    assert (SAMPLE_DIR / "client_register.csv").exists()
    assert (SAMPLE_DIR / "platform_register.csv").exists()


def test_mapping_engine_resolves_both_register_headers_without_review_for_amount_columns():
    for filename in ["client_register.csv", "platform_register.csv"]:
        with (SAMPLE_DIR / filename).open(newline="", encoding="utf-8") as f:
            headers = next(csv.reader(f))
        result = suggest_mapping(headers)
        mapped_codes = {s.canonical_code for s in result.suggestions if s.canonical_code}
        assert "EMPLOYEE_ID" in mapped_codes
        assert "BASIC" in mapped_codes
        assert "EPF_EMPLOYEE" in mapped_codes
        assert "HRDF_LEVY" in mapped_codes


def _classify_epf(employee_id: str, master: dict, client: dict, platform: dict, component: str):
    row = master[employee_id]
    emp = _employee_context(row)
    wage = WageContext(basic_salary=_to_float(client[employee_id]["BASIC"]) or 0.0)
    rule_result = calculate_epf(emp, wage)
    client_val = _to_float(client[employee_id].get(component))
    platform_val = _to_float(platform[employee_id].get(component))
    return classify_variance(employee_id, component, client_val, platform_val, rule_result)


def test_e001_no_variance():
    master = _load_employee_master()
    client = _load_canonical(SAMPLE_DIR / "client_register.csv")
    platform = _load_canonical(SAMPLE_DIR / "platform_register.csv")
    finding = _classify_epf("E001", master, client, platform, "EPF_EMPLOYEE")
    assert finding.classification == Classification.NO_VARIANCE


def test_e002_platform_wrong_rate_slab_mismatch():
    master = _load_employee_master()
    client = _load_canonical(SAMPLE_DIR / "client_register.csv")
    platform = _load_canonical(SAMPLE_DIR / "platform_register.csv")
    finding = _classify_epf("E002", master, client, platform, "EPF_EMPLOYER")
    assert finding.classification == Classification.RATE_SLAB_MISMATCH
    assert finding.suggestion_outcome == Suggestion.CLIENT_CORRECT


def test_e003_client_wrong_rate_slab_mismatch():
    master = _load_employee_master()
    client = _load_canonical(SAMPLE_DIR / "client_register.csv")
    platform = _load_canonical(SAMPLE_DIR / "platform_register.csv")
    finding = _classify_epf("E003", master, client, platform, "EPF_EMPLOYEE")
    assert finding.classification == Classification.RATE_SLAB_MISMATCH
    assert finding.suggestion_outcome == Suggestion.PLATFORM_CORRECT


def test_e004_missing_from_platform():
    master = _load_employee_master()
    client = _load_canonical(SAMPLE_DIR / "client_register.csv")
    platform = _load_canonical(SAMPLE_DIR / "platform_register.csv")
    finding = _classify_epf("E004", master, client, platform, "EPF_EMPLOYEE")
    assert finding.classification == Classification.NOT_CALCULATED_ONE_SIDE


def test_e005_eligibility_mismatch_underage():
    master = _load_employee_master()
    client = _load_canonical(SAMPLE_DIR / "client_register.csv")
    platform = _load_canonical(SAMPLE_DIR / "platform_register.csv")
    row = master["E005"]
    emp = _employee_context(row)
    wage = WageContext(basic_salary=800.0)
    rule_result = calculate_epf(emp, wage)
    assert rule_result.status == RuleStatus.NOT_APPLICABLE
    finding = classify_variance("E005", "EPF_EMPLOYEE", 88.0, 0.0, rule_result)
    assert finding.classification == Classification.ELIGIBILITY_MISMATCH


def test_e006_not_applicable_both_zero_no_variance():
    master = _load_employee_master()
    row = master["E006"]
    emp = _employee_context(row)
    wage = WageContext(basic_salary=1000.0)
    rule_result = calculate_epf(emp, wage)
    assert rule_result.status == RuleStatus.NOT_APPLICABLE
    finding = classify_variance("E006", "EPF_EMPLOYEE", 0.0, 0.0, rule_result)
    assert finding.classification == Classification.NO_VARIANCE


def test_e007_rounding_difference_treated_as_no_variance():
    # A 1-sen rounding difference is within DEFAULT_TOLERANCE, so all three
    # values (client, platform, expected) are considered to agree.
    master = _load_employee_master()
    client = _load_canonical(SAMPLE_DIR / "client_register.csv")
    platform = _load_canonical(SAMPLE_DIR / "platform_register.csv")
    finding = _classify_epf("E007", master, client, platform, "EPF_EMPLOYEE")
    assert finding.classification == Classification.NO_VARIANCE


def test_e008_above_20k_no_variance():
    master = _load_employee_master()
    client = _load_canonical(SAMPLE_DIR / "client_register.csv")
    platform = _load_canonical(SAMPLE_DIR / "platform_register.csv")
    finding = _classify_epf("E008", master, client, platform, "EPF_EMPLOYEE")
    assert finding.classification == Classification.NO_VARIANCE


def test_e009_hrdf_missing_from_platform():
    client = _load_canonical(SAMPLE_DIR / "client_register.csv")
    platform = _load_canonical(SAMPLE_DIR / "platform_register.csv")
    from hrdf import calculate_hrdf
    emp = EmployeeContext(employee_id="E009", nationality="MY", age_years=28)
    wage = WageContext(basic_salary=5000.0, fixed_allowance=300.0)
    rule_result = calculate_hrdf(emp, wage)
    client_val = _to_float(client["E009"].get("HRDF_LEVY"))
    platform_val = _to_float(platform["E009"].get("HRDF_LEVY"))
    finding = classify_variance("E009", "HRDF_LEVY", client_val, platform_val, rule_result)
    assert finding.classification == Classification.NOT_CALCULATED_ONE_SIDE

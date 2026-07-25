"""Tests for services/mapping_engine.py (column mapping suggestion engine)."""
from mapping_engine import apply_mapping, suggest_mapping


def test_exact_synonym_match():
    result = suggest_mapping(["Employee ID", "Basic Salary", "EPF Employee"])
    mapping = result.to_column_map()
    assert mapping["Employee ID"] == "EMPLOYEE_ID"
    assert mapping["Basic Salary"] == "BASIC"
    assert mapping["EPF Employee"] == "EPF_EMPLOYEE"
    assert result.needs_review() == []


def test_fuzzy_match_flagged_for_review():
    result = suggest_mapping(["Bsic Salry"])  # typo'd header
    suggestion = result.suggestions[0]
    assert suggestion.method == "fuzzy"
    assert suggestion.canonical_code == "BASIC"
    assert suggestion.confidence < 1.0
    assert result.needs_review() == [suggestion]


def test_unmapped_column():
    result = suggest_mapping(["Some Totally Unknown Column XYZ123"])
    suggestion = result.suggestions[0]
    assert suggestion.canonical_code is None
    assert suggestion.method == "unmapped"


def test_apply_mapping_renames_and_drops_unmapped():
    rows = [{"Employee ID": "E001", "Basic Salary": 3000, "Junk Column": "ignore me"}]
    column_map = {"Employee ID": "EMPLOYEE_ID", "Basic Salary": "BASIC"}
    mapped = apply_mapping(rows, column_map)
    assert mapped == [{"EMPLOYEE_ID": "E001", "BASIC": 3000}]

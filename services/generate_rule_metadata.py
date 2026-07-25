"""
Phase 3/6 - Rule Extraction + Metadata generation.

Generates the rule repository (JSON, YAML, Markdown) with full metadata for
every deterministic rule implemented in rule-engine/. This is the single
source-controlled definition of rule metadata; rule-engine/*.py implements
the executable logic and cites the same Rule IDs defined here.

Usage:
    .venv\\Scripts\\python.exe services\\generate_rule_metadata.py
"""
from __future__ import annotations

import json
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
JSON_DIR = ROOT / "rules" / "json"
YAML_DIR = ROOT / "rules" / "yaml"
MD_DIR = ROOT / "rules" / "markdown"

RULES = [
    {
        "RuleId": "MY_EPF_001",
        "Country": "Malaysia",
        "Component": "EPF",
        "BusinessArea": "Statutory Retirement Contribution",
        "Category": "Statutory",
        "Priority": "Critical",
        "SourceDocument": "EPF employee and employer contribution 10. Effective 1 October 2025.pdf",
        "Section": "Third Schedule, Parts A, C, E, F (Parts B, D repealed by Act A1760/2025)",
        "EffectiveDate": "2025-10-01",
        "Version": "1.0",
        "ValidationType": "Formula + Age-band + Nationality eligibility",
        "Inputs": ["BasicSalary", "FixedAllowance", "UnpaidLeaveDeduction", "Age", "Nationality",
                    "IsPermanentResident", "ElectedBefore1998_08_01"],
        "Expected": ["EmployerContribution", "EmployeeContribution"],
        "Dependencies": [],
        "ExecutionOrder": 10,
        "ErrorCode": "EPF001",
        "Severity": "Critical",
        "Owner": "Payroll Compliance SME (Malaysia)",
        "SME": "Requires SME Validation - assignment pending",
        "AuditReference": "docs/markdown/epf-employee-and-employer-contribution-10-effective-1-october-2025.md",
        "TestScenario": {
            "Positive": "Malaysian employee age 30, wage RM120 -> employer RM16, employee RM14 (matches source table)",
            "Negative": "Employee age 80 (outside 14-75 mandatory range) -> NOT_APPLICABLE, no contribution expected",
        },
        "Risk": "High if mis-applied (financial + statutory compliance exposure)",
        "Confidence": "High (formula verified row-by-row against 11 sampled table rows)",
        "Status": "implemented",
        "Notes": "Age eligibility band (14-75) sourced from MY Labour law and statutory calculation.txt; exact legal citation Requires SME Validation.",
    },
    {
        "RuleId": "MY_SOCSO_001",
        "Country": "Malaysia",
        "Component": "SOCSO",
        "BusinessArea": "Statutory Social Security Contribution",
        "Category": "Statutory",
        "Priority": "Critical",
        "SourceDocument": "SOCSO employee and employer NewContributionRateIncludingSKBBK.pdf",
        "Section": "Contribution rate table (Category 1 & Category 2), rows 1-65",
        "EffectiveDate": "Requires SME Validation - not stated in source PDF",
        "Version": "1.0",
        "ValidationType": "Lookup table (wage band) + Category eligibility",
        "Inputs": ["BasicSalary", "FixedAllowance", "Age", "SocsoCategory"],
        "Expected": ["EmployerContribution", "EmployeeContribution"],
        "Dependencies": [],
        "ExecutionOrder": 20,
        "ErrorCode": "SOCSO001",
        "Severity": "Critical",
        "Owner": "Payroll Compliance SME (Malaysia)",
        "SME": "Requires SME Validation - Category 1 vs Category 2 eligibility test not stated in source PDF",
        "AuditReference": "rule-engine/rates/socso_rates.json (parsed programmatically from PDF tables)",
        "TestScenario": {
            "Positive": "Wage RM30, Category 1 -> employee RM0.40, employer RM0.30, total RM0.70",
            "Negative": "Wage RM10,000 (above RM6,000 ceiling) -> capped at RM5,900-6,000 band amount",
        },
        "Risk": "Medium-High - category eligibility placeholder needs SME sign-off before production use",
        "Confidence": "High for rates (extracted from source table); Low for category-assignment default (placeholder)",
        "Status": "implemented_pending_category_sme_validation",
        "Notes": "Wage ceiling RM6,000 confirmed from source (row 65 repeats capped amount).",
    },
    {
        "RuleId": "MY_EIS_001",
        "Country": "Malaysia",
        "Component": "EIS",
        "BusinessArea": "Statutory Employment Insurance Contribution",
        "Category": "Statutory",
        "Priority": "Critical",
        "SourceDocument": "EIS employee and employer 151124-Rate Contribution ACT 800.PDF",
        "Section": "Unknown - source is a scanned image, not machine-readable",
        "EffectiveDate": "Requires SME Validation",
        "Version": "0.0-placeholder",
        "ValidationType": "Lookup table (not yet available)",
        "Inputs": ["BasicSalary", "FixedAllowance"],
        "Expected": ["EmployerContribution", "EmployeeContribution"],
        "Dependencies": [],
        "ExecutionOrder": 30,
        "ErrorCode": "EIS001",
        "Severity": "Critical",
        "Owner": "Payroll Compliance SME (Malaysia)",
        "SME": "Requires SME Validation - full rate table transcription required",
        "AuditReference": "docs/markdown/assets/eis-employee-and-employer-151124-rate-contribution-act-800-page1.png",
        "TestScenario": {
            "Positive": "N/A until rate table is transcribed",
            "Negative": "Any input -> PENDING_SME_VALIDATION (no computation performed)",
        },
        "Risk": "Critical - EIS validation cannot run at all until this placeholder is resolved",
        "Confidence": "None - no rate figures available",
        "Status": "pending_sme_validation",
        "Notes": "Source PDF is scanned/image-only; pdfplumber text and table extraction both returned empty content.",
    },
    {
        "RuleId": "MY_HRDF_001",
        "Country": "Malaysia",
        "Component": "HRDF",
        "BusinessArea": "Statutory Training Levy",
        "Category": "Statutory",
        "Priority": "High",
        "SourceDocument": "MY Labour law and statutory calculation.txt",
        "Section": "HRDF Levy calculation",
        "EffectiveDate": "Requires SME Validation",
        "Version": "1.0",
        "ValidationType": "Formula + Eligibility (nationality, employment type, director status, employer registration)",
        "Inputs": ["BasicSalary", "UnpaidLeaveDeduction", "FixedAllowance", "Nationality", "EmploymentType",
                    "IsDirectorFeeOnly", "EmployerHrdfRegistered"],
        "Expected": ["EmployerContribution"],
        "Dependencies": [],
        "ExecutionOrder": 40,
        "ErrorCode": "HRDF001",
        "Severity": "High",
        "Owner": "Payroll Compliance SME (Malaysia)",
        "SME": "Requires SME Validation - legal citation to HRD Corp Act",
        "AuditReference": "docs/markdown/my-labour-law-and-statutory-calculation-txt.md",
        "TestScenario": {
            "Positive": "Malaysian employee, basic RM5000, unpaid leave RM200, fixed allowance RM300 -> levy RM51.00",
            "Negative": "Domestic servant -> NOT_APPLICABLE",
        },
        "Risk": "Medium",
        "Confidence": "High (formula stated verbatim in source)",
        "Status": "implemented",
        "Notes": "HRDF levy is an employer-level registration matter; employer_hrdf_registered flag is employer master data, out of scope of per-employee eligibility.",
    },
    {
        "RuleId": "MY_PCB_001",
        "Country": "Malaysia",
        "Component": "PCB",
        "BusinessArea": "Statutory Monthly Tax Deduction (MTD)",
        "Category": "Statutory",
        "Priority": "Critical",
        "SourceDocument": "NO SOURCE DOCUMENT SUPPLIED",
        "Section": "N/A",
        "EffectiveDate": "Requires SME Validation",
        "Version": "0.0-placeholder",
        "ValidationType": "Not implemented",
        "Inputs": [],
        "Expected": ["EmployeeDeduction"],
        "Dependencies": [],
        "ExecutionOrder": 50,
        "ErrorCode": "PCB001",
        "Severity": "Critical",
        "Owner": "Payroll Compliance SME (Malaysia)",
        "SME": "Requires SME Validation - full PCB/MTD schedule needed from LHDN",
        "AuditReference": "N/A",
        "TestScenario": {"Positive": "N/A", "Negative": "Any input -> PENDING_SME_VALIDATION"},
        "Risk": "Critical",
        "Confidence": "None",
        "Status": "pending_sme_validation",
        "Notes": "Referenced by the BRD (Section 21.1) as an in-scope component, but no PCB source document exists in the workspace.",
    },
    {
        "RuleId": "MY_OT_001",
        "Country": "Malaysia",
        "Component": "Overtime",
        "BusinessArea": "Working Time / Overtime Pay",
        "Category": "Business Rule",
        "Priority": "High",
        "SourceDocument": "MY Labour law and statutory calculation.txt",
        "Section": "Overtime calculation",
        "EffectiveDate": "Requires SME Validation",
        "Version": "1.0",
        "ValidationType": "Formula (multiplier table)",
        "Inputs": ["MonthlyBasicWages", "OtHours", "DayType", "DailyNormalHours"],
        "Expected": ["OvertimePay"],
        "Dependencies": [],
        "ExecutionOrder": 60,
        "ErrorCode": "OT001",
        "Severity": "High",
        "Owner": "Payroll Compliance SME (Malaysia)",
        "SME": "Requires SME Validation - rest-day standard-hours sub-case multiplier not specified in source",
        "AuditReference": "docs/markdown/my-labour-law-and-statutory-calculation-txt.md",
        "TestScenario": {
            "Positive": "Monthly basic RM2080, 2h normal-day OT -> HRP x 1.5 x 2",
            "Negative": "Rest day, standard hours worked (no OT) -> PENDING_SME_VALIDATION (multiplier not specified)",
        },
        "Risk": "Medium",
        "Confidence": "High for normal/rest(exceeding)/public holiday cases; Low for rest-day standard-hours sub-case",
        "Status": "implemented_partial",
        "Notes": "HRP = Monthly Basic Wages / 26 / daily normal hours (usually 8).",
    },
    {
        "RuleId": "MY_PRORATION_001",
        "Country": "Malaysia",
        "Component": "Proration",
        "BusinessArea": "Fixed Income Proration",
        "Category": "Business Rule",
        "Priority": "High",
        "SourceDocument": "MY Labour law and statutory calculation.txt",
        "Section": "Fixed Income proration statement",
        "EffectiveDate": "Requires SME Validation",
        "Version": "1.0",
        "ValidationType": "Formula (calendar-day ratio)",
        "Inputs": ["MonthlyAmount", "Year", "Month", "EligibleDays"],
        "Expected": ["ProratedAmount"],
        "Dependencies": [],
        "ExecutionOrder": 5,
        "ErrorCode": "PRORATION001",
        "Severity": "High",
        "Owner": "Payroll Compliance SME (Malaysia)",
        "SME": "Requires SME Validation",
        "AuditReference": "docs/markdown/my-labour-law-and-statutory-calculation-txt.md",
        "TestScenario": {
            "Positive": "RM3000 monthly, 15/30 eligible calendar days -> RM1500",
            "Negative": "eligible_days > total_days in month -> ERROR",
        },
        "Risk": "Medium",
        "Confidence": "High (standard calendar-day proration explicitly stated)",
        "Status": "implemented",
        "Notes": "Applies to new joiners, exits, and unpaid leave during the month for fixed income components (Basic, Transport allowance, etc.).",
    },
]


def rule_to_markdown(rule: dict) -> str:
    lines = [f"# {rule['RuleId']} - {rule['Component']}", ""]
    for key, value in rule.items():
        if key in ("RuleId", "Component"):
            continue
        if isinstance(value, dict):
            lines.append(f"**{key}:**")
            for k, v in value.items():
                lines.append(f"- {k}: {v}")
        elif isinstance(value, list):
            lines.append(f"**{key}:** {', '.join(str(v) for v in value) if value else '_(none)_'}")
        else:
            lines.append(f"**{key}:** {value}")
    return "\n".join(lines) + "\n"


def main() -> int:
    for d in (JSON_DIR, YAML_DIR, MD_DIR):
        d.mkdir(parents=True, exist_ok=True)

    for rule in RULES:
        rid = rule["RuleId"]
        (JSON_DIR / f"{rid}.json").write_text(json.dumps(rule, indent=2), encoding="utf-8")
        (YAML_DIR / f"{rid}.yaml").write_text(yaml.safe_dump(rule, sort_keys=False), encoding="utf-8")
        (MD_DIR / f"{rid}.md").write_text(rule_to_markdown(rule), encoding="utf-8")

    # Duplicate Rule ID guard
    ids = [r["RuleId"] for r in RULES]
    assert len(ids) == len(set(ids)), "Duplicate Rule IDs detected!"

    print(f"Generated {len(RULES)} rule definitions in JSON, YAML and Markdown under rules/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

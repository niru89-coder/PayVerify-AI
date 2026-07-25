# MY_EPF_001 - EPF

**Country:** Malaysia
**BusinessArea:** Statutory Retirement Contribution
**Category:** Statutory
**Priority:** Critical
**SourceDocument:** EPF employee and employer contribution 10. Effective 1 October 2025.pdf
**Section:** Third Schedule, Parts A, C, E, F (Parts B, D repealed by Act A1760/2025)
**EffectiveDate:** 2025-10-01
**Version:** 1.0
**ValidationType:** Formula + Age-band + Nationality eligibility
**Inputs:** BasicSalary, FixedAllowance, UnpaidLeaveDeduction, Age, Nationality, IsPermanentResident, ElectedBefore1998_08_01
**Expected:** EmployerContribution, EmployeeContribution
**Dependencies:** _(none)_
**ExecutionOrder:** 10
**ErrorCode:** EPF001
**Severity:** Critical
**Owner:** Payroll Compliance SME (Malaysia)
**SME:** Requires SME Validation - assignment pending
**AuditReference:** docs/markdown/epf-employee-and-employer-contribution-10-effective-1-october-2025.md
**TestScenario:**
- Positive: Malaysian employee age 30, wage RM120 -> employer RM16, employee RM14 (matches source table)
- Negative: Employee age 80 (outside 14-75 mandatory range) -> NOT_APPLICABLE, no contribution expected
**Risk:** High if mis-applied (financial + statutory compliance exposure)
**Confidence:** High (formula verified row-by-row against 11 sampled table rows)
**Status:** implemented
**Notes:** Age eligibility band (14-75) sourced from MY Labour law and statutory calculation.txt; exact legal citation Requires SME Validation.

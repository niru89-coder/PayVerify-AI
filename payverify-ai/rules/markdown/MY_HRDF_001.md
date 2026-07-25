# MY_HRDF_001 - HRDF

**Country:** Malaysia
**BusinessArea:** Statutory Training Levy
**Category:** Statutory
**Priority:** High
**SourceDocument:** MY Labour law and statutory calculation.txt
**Section:** HRDF Levy calculation
**EffectiveDate:** Requires SME Validation
**Version:** 1.0
**ValidationType:** Formula + Eligibility (nationality, employment type, director status, employer registration)
**Inputs:** BasicSalary, UnpaidLeaveDeduction, FixedAllowance, Nationality, EmploymentType, IsDirectorFeeOnly, EmployerHrdfRegistered
**Expected:** EmployerContribution
**Dependencies:** _(none)_
**ExecutionOrder:** 40
**ErrorCode:** HRDF001
**Severity:** High
**Owner:** Payroll Compliance SME (Malaysia)
**SME:** Requires SME Validation - legal citation to HRD Corp Act
**AuditReference:** docs/markdown/my-labour-law-and-statutory-calculation-txt.md
**TestScenario:**
- Positive: Malaysian employee, basic RM5000, unpaid leave RM200, fixed allowance RM300 -> levy RM51.00
- Negative: Domestic servant -> NOT_APPLICABLE
**Risk:** Medium
**Confidence:** High (formula stated verbatim in source)
**Status:** implemented
**Notes:** HRDF levy is an employer-level registration matter; employer_hrdf_registered flag is employer master data, out of scope of per-employee eligibility.

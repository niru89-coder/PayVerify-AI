# HRDF (Human Resources Development Fund / HRD Corp Levy) — Malaysia

## Purpose
Statutory training levy paid by HRD Corp-registered employers, based on employee wages.

## Business Rules
- **BR-HRDF-01 (eligibility, verbatim from source)**: "Any citizen of Malaysia who is
  employed for wages under a contract of service (under full-time employment whether
  contract or permanent staff) with an employer, but does not include any domestic servant.
  If the company director/owner/partner is paid a salary, he/she is regarded as an employee
  of the company, whereas a director who only accepts director fees is not considered an
  employee."
- **BR-HRDF-02**: The levy is fundamentally an **employer-level** registration matter — only
  employers registered with HRD Corp are liable. `employer_hrdf_registered` is employer
  master data, out of scope of the per-employee rule.

## Validation Rules
- Non-Malaysian citizens → NOT_APPLICABLE.
- Domestic servants → NOT_APPLICABLE.
- Directors who receive director fees only (no salary) → NOT_APPLICABLE.
- Employer not HRD Corp-registered → NOT_APPLICABLE.

## Formula
```
LEVY = [(BASIC SALARY - UNPAID LEAVE) + FIXED ALLOWANCE] x 1%
```
(verbatim from `MY Labour law and statutory calculation.txt`)

## Examples
- Basic RM5,000, Unpaid Leave RM200, Fixed Allowance RM300 → Levy = (5000-200+300) × 1% =
  RM51.00.

## Exceptions
- Domestic servants.
- Director-fee-only directors.
- Non-Malaysian citizens.
- Employers not registered with HRD Corp.

## Dependencies
- Employee nationality, employment type, director-fee-only flag.
- Employer HRD Corp registration status (master data, not employee-level).

## Metadata
- **Rule ID**: MY_HRDF_001
- **Source Reference**: `MY Labour law and statutory calculation.txt`
- **Version**: 1.0
- **Effective Date**: Requires SME Validation (legal citation to HRD Corp Act not in source)
- **Status**: Implemented.

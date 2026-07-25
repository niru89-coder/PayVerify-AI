# Proration — Malaysia

## Purpose
Prorate fixed-income pay components (Basic Salary, Transport Allowance, etc.) for partial
months caused by new joiners, exits, or unpaid leave.

## Business Rules (verbatim from source)
"Fixed Income such as Basic salary, Transport allowance etc should follow Calendar days
proration for new joiner, exit and unpaid leave during the month."

## Validation Rules
- Applies to fixed-income components only (not to statutory contributions directly — those
  are computed on the already-prorated wage where applicable).
- `eligible_days` must be between 0 and the total calendar days in the month.

## Formula
```
Prorated Amount = Monthly Amount x (Eligible Calendar Days / Total Calendar Days in Month)
```

## Examples
- RM3,000 monthly Basic Salary, employee eligible for 15 of 30 calendar days (e.g. joined
  mid-month) → Prorated = RM1,500.00.

## Exceptions
None specified beyond the stated scenarios (new joiner, exit, unpaid leave).

## Dependencies
- Calendar (total days in month), employee join/exit dates, unpaid leave days.

## Metadata
- **Rule ID**: MY_PRORATION_001
- **Source Reference**: `MY Labour law and statutory calculation.txt`
- **Version**: 1.0
- **Effective Date**: Requires SME Validation
- **Status**: Implemented.

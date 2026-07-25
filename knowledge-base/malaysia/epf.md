# EPF (Employees Provident Fund / KWSP) — Malaysia

## Purpose
Statutory retirement savings scheme. Employers and employees make monthly contributions on
EPF-liable wages, at rates that depend on the employee's age band and citizenship/residency
category.

## Business Rules
- **BR-EPF-01**: Mandatory for employees aged 14 to 75 (per `MY Labour law and statutory
  calculation.txt`; exact legal citation to the EPF Act 1991 Requires SME Validation).
- **BR-EPF-02**: Contribution rate depends on which "Part" of the Third Schedule applies:
  - **Part A** — age < 60, Malaysian citizen OR permanent resident OR non-citizen who elected
    to contribute before 1 August 1998: Employee 11%; Employer 13% (wage ≤ RM5,000) / 12%
    (wage > RM5,000).
  - **Part B** — repealed (Act A1760/2025).
  - **Part C** — age ≥ 60, permanent resident OR non-citizen elected before 1 Aug 1998 (NOT
    plain Malaysian citizens): Employee 5.5%; Employer 6.5% (wage ≤ RM5,000) / 6% (wage >
    RM5,000).
  - **Part D** — repealed (Act A1760/2025).
  - **Part E** — age ≥ 60, Malaysian citizen: Employee 0%; Employer 4%.
  - **Part F** — non-Malaysian citizen (not PR, not pre-1998 elector): flat 2% employee / 2%
    employer on actual wage, no banding.
- **BR-EPF-03**: For wages ≤ RM20,000, use the fixed statutory table (banded to the next
  RM20 up to RM5,000, then next RM100 up to RM20,000). For wages > RM20,000, use the exact
  percentage on actual wage.
- **BR-EPF-04**: All contribution amounts are rounded UP to the next whole Ringgit ("rounded
  to the next ringgit").
- **BR-EPF-05**: Wages ≤ RM10 in a month → NIL contribution (Parts A/C/E).
- **BR-EPF-06 (bonus rule)**: Where an employer pays a bonus to an employee whose monthly
  wage is ≤ RM5,000, and the bonus pushes total wages for that month above RM5,000, the
  employer contribution for that month is calculated at 13% (not 12%).

## Formula
```
Part A (age<60): Employee = ceil(11% * wage);  Employer = ceil(13% * wage) if wage<=5000 else ceil(12% * wage)
Part C (age>=60, PR/pre-1998 elector): Employee = ceil(5.5% * wage); Employer = ceil(6.5% * wage) if wage<=5000 else ceil(6% * wage)
Part E (age>=60, MY citizen): Employee = 0; Employer = ceil(4% * wage)
Part F (foreign, not PR/pre-1998 elector): Employee = ceil(2% * wage); Employer = ceil(2% * wage)
```
For wages ≤ RM20,000, `wage` in the formula above is the upper bound of the RM20/RM100 band
the actual wage falls into (this is how the statutory table is legally constructed); for
wages > RM20,000, `wage` is the actual wage amount.

## Formula Verification (traceability evidence)
The formula was verified to exactly reproduce the source PDF's printed table for every
sampled row (see `tests/test_rule_engine_epf.py`, 11 passing assertions), including:
| Wage band (source) | Employer (source) | Employee (source) | Formula result |
| --- | --- | --- | --- |
| 100.01–120.00 | 16.00 | 14.00 | matches |
| 220.01–240.00 | 32.00 | 27.00 | matches |
| 4,980.01–5,000.00 | 650.00 | 550.00 | matches |
| 5,000.01–5,100.00 | 612.00 | 561.00 | matches |
| 19,900.01–20,000.00 | 2,400.00 | 2,200.00 | matches |
| Part E 100.01–120.00 | 5.00 | 0.00 | matches |
| Part C 220.01–240.00 | 16.00 | 14.00 | matches |

## Examples
- Malaysian employee, age 30, EPF wage RM120 → Employer RM16, Employee RM14.
- Malaysian employee, age 61, EPF wage RM120 → Employer RM5, Employee RM0 (Part E).
- Indonesian worker (not PR), EPF wage RM2,000 → Employer RM40, Employee RM40 (Part F, if
  the employer/employee elect to contribute; EPF is NOT mandatory for this category).

## Exceptions
- Domestic servants — outside EPF scope entirely (not addressed by this source PDF;
  Requires SME Validation if applicable to a given project).
- Foreign workers who are not PR and did not elect before 1 Aug 1998 — Part F contribution
  is available but voluntary in practice; treat "not contributing" as a valid, non-variance
  state unless the client/platform registers state otherwise. Requires SME Validation for
  the exact voluntary/mandatory framing.

## Dependencies
- Employee age (computed from Date of Birth as of the statutory reference date).
- Employee nationality / citizenship.
- Permanent resident status / pre-1 Aug 1998 election status.
- EPF-liable wage composition (Basic Salary + Fixed Allowance + other EPF wages, per the
  client's configured wage definition — see BRD Section 8.2).

## Metadata
- **Rule ID**: MY_EPF_001
- **Source Reference**: `EPF employee and employer contribution 10. Effective 1 October 2025.pdf`
- **Version**: 1.0
- **Effective Date**: 2025-10-01
- **Status**: Implemented (rates + eligibility); age-band legal citation Requires SME Validation

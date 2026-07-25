# Payroll Components — Malaysia (Canonical Reference)

## Purpose
Canonical list of pay components referenced across the Malaysia knowledge base, for mapping
client/platform register column names to a single canonical component code (see
`services/mapping_engine.py`).

## Components
| Canonical Code | Description | Category | Statutory? | Rule ID |
| --- | --- | --- | --- | --- |
| BASIC | Basic Salary | Earning (fixed) | No | — |
| TRANSPORT_ALLOWANCE | Transport Allowance | Earning (fixed) | No | — |
| FIXED_ALLOWANCE | Other fixed allowance(s) | Earning (fixed) | No | — |
| OT_NORMAL | Overtime — normal working day | Earning (variable) | No | MY_OT_001 |
| OT_REST_DAY | Overtime — rest day | Earning (variable) | No | MY_OT_001 |
| OT_PUBLIC_HOLIDAY | Overtime — public holiday | Earning (variable) | No | MY_OT_001 |
| EPF_EMPLOYEE | EPF employee contribution | Deduction | Yes | MY_EPF_001 |
| EPF_EMPLOYER | EPF employer contribution | Employer cost | Yes | MY_EPF_001 |
| SOCSO_EMPLOYEE | SOCSO employee contribution | Deduction | Yes | MY_SOCSO_001 |
| SOCSO_EMPLOYER | SOCSO employer contribution | Employer cost | Yes | MY_SOCSO_001 |
| EIS_EMPLOYEE | EIS employee contribution | Deduction | Yes | MY_EIS_001 (pending) |
| EIS_EMPLOYER | EIS employer contribution | Employer cost | Yes | MY_EIS_001 (pending) |
| HRDF_LEVY | HRDF levy | Employer cost | Yes | MY_HRDF_001 |
| PCB | Monthly Tax Deduction (PCB/MTD) | Deduction | Yes | MY_PCB_001 (pending) |

## Exceptions
Components not in this table are treated as "unmapped" by the mapping engine and flagged
per FR-07 (component present in one register but absent/unmapped in the other).

## Metadata
- **Source Reference**: Derived from `MY Labour law and statutory calculation.txt` and BRD
  Section 5/9.2/21.1.
- **Version**: 1.0

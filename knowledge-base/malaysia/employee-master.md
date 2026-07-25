# Employee Master Data Requirements — Malaysia

## Purpose
Minimum employee master fields required to evaluate Malaysia statutory eligibility logic,
per BRD Section 9.1.

## Fields
| Field | Purpose | Used By |
| --- | --- | --- |
| Employee ID | Primary key for matching across registers | All rules |
| Date of Birth | Age-band statutory calculations | MY_EPF_001, MY_SOCSO_001 (category default) |
| Nationality / Citizenship | Nationality-dependent applicability | MY_EPF_001, MY_HRDF_001 |
| Permanent Resident flag | EPF Part A/C eligibility for non-citizens | MY_EPF_001 |
| Elected before 1 Aug 1998 flag | EPF Part A/C eligibility for non-citizens | MY_EPF_001 |
| Date of Joining / Date of Exit | Proration eligibility | MY_PRORATION_001 |
| Employment Type (permanent/contract/domestic servant) | HRDF eligibility | MY_HRDF_001 |
| Is Director (fee-only vs salaried) | HRDF eligibility | MY_HRDF_001 |
| Work Location / State | State/region-specific rules (none yet encoded for MY) | Future |

## Exceptions
Missing/blank required fields (e.g. blank DOB, blank nationality) block statutory computation
and must be flagged as a **data-quality issue**, distinct from a calculation variance (BRD
FR-18).

## Metadata
- **Source Reference**: BRD Section 9.1 + rule-specific requirements above.
- **Version**: 1.0

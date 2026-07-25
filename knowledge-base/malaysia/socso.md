# SOCSO (Social Security Organisation / PERKESO) — Malaysia

## Purpose
Statutory social security contribution covering Employment Injury Scheme, Invalidity Pension
Scheme, and the Non-Employment Injury Security Scheme (SKBBK).

## Business Rules
- **BR-SOCSO-01**: Two contribution categories exist, per the source rate table's own column
  headers:
  - **Category 1** — Employment Injury Scheme + Invalidity Pension Scheme + SKBBK.
  - **Category 2** — Employment Injury Scheme + SKBBK only (no Invalidity Pension).
- **BR-SOCSO-02 (⚠ Requires SME Validation)**: The source PDF contains ONLY the rate table —
  it does NOT state which employees fall into Category 1 vs Category 2. The current
  implementation uses a placeholder default (age ≥ 60 → Category 2, else Category 1) and
  flags every such result as `pending_sme_validation`. An SME must confirm the real
  eligibility test (commonly: first-time contributors aged 60+, or continuing insured
  persons) before this is treated as authoritative.
- **BR-SOCSO-03**: Wage ceiling is RM6,000 — contributions for wages above RM6,000 are capped
  at the RM5,900.01–6,000.00 band amount (confirmed: source table row 65 "wages exceed
  RM6,000" repeats the row 64 amount).

## Validation Rules
- Wage band lookup: 65 discrete bands from RM0.01 up to RM6,000+ (RM10/RM20/RM50/RM100
  increments depending on range — irregular, not a clean percentage, hence implemented as an
  exact lookup table, not a formula).

## Formula
Lookup table only (see `rule-engine/rates/socso_rates.json`, extracted directly and
programmatically from the source PDF's own tables via `services/extract_rates.py` — not
manually retyped, to eliminate transcription risk).

## Examples
- Wage RM30, Category 1 → Employee RM0.40, Employer RM0.30, Total RM0.70.
- Wage RM10,000 (above ceiling), Category 1 → capped at Employee RM104.15, Employer RM74.40
  (the RM5,900.01–6,000.00 band amount).

## Exceptions
- Category assignment logic — Requires SME Validation (see BR-SOCSO-02).
- Effective date of this specific rate schedule is not printed in the source PDF — Requires
  SME Validation.

## Dependencies
- Employee age (for the current placeholder category default).
- SOCSO-liable wage composition (Basic Salary + Fixed Allowance, consistent with EPF wage
  definition unless client configuration states otherwise).

## Metadata
- **Rule ID**: MY_SOCSO_001
- **Source Reference**: `SOCSO employee and employer NewContributionRateIncludingSKBBK.pdf`
- **Version**: 1.0
- **Effective Date**: Requires SME Validation (not stated in source)
- **Status**: Rates implemented and extracted with full confidence; category-eligibility test
  pending SME validation.

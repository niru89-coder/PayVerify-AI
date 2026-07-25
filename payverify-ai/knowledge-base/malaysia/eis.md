# EIS (Employment Insurance System, Act 800) — Malaysia

## Purpose
Statutory unemployment/employment insurance contribution under the Employment Insurance
System Act 2017 (Act 800).

## ⚠ Requires SME Validation
The source file `EIS employee and employer 151124-Rate Contribution ACT 800.PDF` is a
**scanned image with no extractable text layer**. Both `pdfplumber` text extraction and table
extraction returned empty content for the single page in this PDF. Per project policy ("Do not
invent payroll rules... If information is missing, create placeholders and identify them as
Requires SME Validation"), **no rate figures are recorded here**.

The rendered page image is preserved for manual transcription at:
`docs/markdown/assets/eis-employee-and-employer-151124-rate-contribution-act-800-page1.png`

## Business Rules
- Structurally, EIS in Malaysia is known to follow a wage-banded contribution table similar
  in shape to SOCSO (small employer/employee shares below a wage ceiling), but the **exact
  bands and amounts must come from this specific source document** once transcribed — no
  external/internet rate figures have been used.

## Validation Rules
- Pending. `rule-engine/eis.py` always returns `PENDING_SME_VALIDATION` and performs no
  calculation until `rule-engine/rates/eis_rates.json` is populated by an SME (same JSON
  shape as `rule-engine/rates/socso_rates.json`).

## Formula
Not available.

## Examples
Not available (no rate data).

## Exceptions
Entire component is a placeholder.

## Dependencies
- Once populated: EIS-liable wage composition, wage ceiling.

## Metadata
- **Rule ID**: MY_EIS_001
- **Source Reference**: `EIS employee and employer 151124-Rate Contribution ACT 800.PDF` (image, unreadable)
- **Version**: 0.0-placeholder
- **Effective Date**: Requires SME Validation
- **Status**: `pending_sme_validation` — blocking for full EIS reconciliation coverage.

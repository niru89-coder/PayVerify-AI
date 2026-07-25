# PCB / MTD (Potongan Cukai Bulanan / Monthly Tax Deduction) — Malaysia

## ⚠ Requires SME Validation — No Source Document Supplied
No PCB/MTD source document (LHDN PCB calculation schedule, PCB2/TP1/TP3 forms, relief and
exemption tables) was supplied in this workspace. Per project policy, this file is an
explicit placeholder. **Do not invent tax computation rules.**

The Business & Functional Requirements Document (`AI_Payroll_Validation_Agent_Requirements.docx`)
references PCB/MTD as an in-scope statutory component (Sections 3.1, 8.3, 21.1) with the
generic diagnostic pattern: "Residency status → cumulative YTD income basis → relief/exemption
configuration", but does not itself provide the calculation schedule.

## Purpose (per BRD, not yet implementable)
Monthly tax deduction computed on an employee's chargeable income, dependent on tax residency
status, cumulative year-to-date income, and applicable reliefs/exemptions.

## Business Rules
Pending SME input.

## Validation Rules
`rule-engine/pcb.py` always returns `PENDING_SME_VALIDATION`.

## Formula
Not available.

## Dependencies (anticipated, per BRD pattern)
- Tax residency status.
- Cumulative YTD income.
- Relief/exemption configuration (spouse, children, EPF relief, etc.).

## Metadata
- **Rule ID**: MY_PCB_001
- **Source Reference**: NO SOURCE DOCUMENT SUPPLIED
- **Version**: 0.0-placeholder
- **Effective Date**: Requires SME Validation
- **Status**: `pending_sme_validation` — obtain the LHDN PCB schedule before implementation.

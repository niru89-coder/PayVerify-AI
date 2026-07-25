# Implementation Guide — Malaysia (PayVerify AI Phase 1 MVP)

## Purpose
Summarizes how the Malaysia knowledge base + rule engine are wired into the PayVerify AI
validation platform, per the BRD's core architecture (Section 10-11).

## Architecture recap
1. **Ingestion** — Client Register + Darwinbox (Platform) Register uploaded (Excel/CSV),
   mapped to canonical schema via `services/mapping_engine.py`.
2. **Rule Engine** (`rule-engine/`) — independently computes the expected value for every
   employee × statutory component, using only the rules documented in this knowledge base.
3. **Reconciliation Engine** (`validation-engine/`) — three-way comparison: Client value vs.
   Platform value vs. Rule-Engine expected value; classifies variances and generates a
   deterministic suggestion following the BRD Section 8.3 generalized decision pattern.
4. **AI Explanation Agent** (`agents/`) — stubbed; only narrates/polishes the deterministic
   reconciliation output. Never computes figures itself.

## Coverage status (Phase 1 MVP)
| Component | Rule ID | Status |
| --- | --- | --- |
| EPF | MY_EPF_001 | Implemented, fully tested |
| SOCSO | MY_SOCSO_001 | Rates implemented; category-eligibility test pending SME validation |
| EIS | MY_EIS_001 | Pending SME validation (source is unreadable scanned image) |
| HRDF | MY_HRDF_001 | Implemented, fully tested |
| PCB/MTD | MY_PCB_001 | Pending SME validation (no source document) |
| Overtime | MY_OT_001 | Implemented (rest-day standard-hours sub-case pending) |
| Proration | MY_PRORATION_001 | Implemented, fully tested |

## Known gaps / Requires SME Validation
- EIS rate table (scanned PDF, not machine-readable).
- PCB/MTD calculation schedule (no source document supplied).
- SOCSO Category 1 vs Category 2 eligibility test (source PDF has rates only, no eligibility clause).
- Overtime "rest day standard hours" multiplier.
- Exact legal citations/effective dates for several rules (flagged per-rule above).

## Metadata
- **Version**: 1.0
- **Source Reference**: This document synthesizes all Malaysia knowledge-base files above.

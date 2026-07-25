"""
MY_EIS_001 - Employment Insurance System (Act 800) monthly contribution.

Source: EIS employee and employer 151124-Rate Contribution ACT 800.PDF
This source file is a SCANNED IMAGE with no extractable text layer (confirmed:
pdfplumber text/table extraction both returned empty content - see
docs/markdown/eis-employee-and-employer-151124-rate-contribution-act-800.md).

Per project policy ("If information is missing, create placeholders and
identify them as Requires SME Validation" / "Do not invent payroll rules"),
NO rate table or percentage is invented here. This calculator always returns
PENDING_SME_VALIDATION until an SME transcribes the real rate table from
`docs/markdown/assets/eis-employee-and-employer-151124-rate-contribution-act-800-page1.png`
into rule-engine/rates/eis_rates.json (same shape as socso_rates.json) and
this module is updated to load it.
"""
from __future__ import annotations

from base import EmployeeContext, RuleResult, RuleStatus, WageContext

RULE_ID = "MY_EIS_001"
SOURCE = "EIS employee and employer 151124-Rate Contribution ACT 800.PDF (scanned - not machine-readable)"


def calculate_eis(employee: EmployeeContext, wage: WageContext) -> RuleResult:
    return RuleResult(
        rule_id=RULE_ID,
        component="EIS",
        status=RuleStatus.PENDING_SME_VALIDATION,
        explanation=(
            "EIS source document is a scanned image; no rate table could be extracted "
            "automatically. An SME must transcribe the rate table before EIS validation "
            "can run. See docs/markdown/assets/ for the rendered source page."
        ),
        source=SOURCE,
        metadata={"reason": "scanned_pdf_no_text_layer"},
    )

"""
MY_PCB_001 - Potongan Cukai Bulanan / Monthly Tax Deduction (MTD).

No source document for PCB/MTD was supplied in this workspace (only EPF,
SOCSO, EIS and general labour-law notes were provided). Per project policy,
this is an explicit placeholder - "Requires SME Validation" - and does not
compute any figure. Referenced by knowledge-base/malaysia/pcb.md.
"""
from __future__ import annotations

from base import RuleResult, RuleStatus

RULE_ID = "MY_PCB_001"
SOURCE = "NO SOURCE DOCUMENT SUPPLIED"


def calculate_pcb(*args, **kwargs) -> RuleResult:
    return RuleResult(
        rule_id=RULE_ID,
        component="PCB",
        status=RuleStatus.PENDING_SME_VALIDATION,
        explanation=(
            "No PCB/MTD source document was supplied. Requires SME Validation: obtain the "
            "LHDN PCB calculation schedule/formula (PCB 2, PCB TP1/TP3, relief tables) before "
            "this rule can be implemented."
        ),
        source=SOURCE,
        metadata={"reason": "no_source_document"},
    )

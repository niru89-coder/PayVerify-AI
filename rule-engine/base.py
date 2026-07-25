"""Core primitives for the deterministic PayVerify AI rule engine.

Design principles (see docs/markdown/ai_payroll_validation_agent_requirements.md
Section 10-11): all numeric statutory computation lives here, in plain
deterministic Python. No LLM call is ever made from this package. Every
result carries the Rule ID and source citation that produced it so that
findings remain fully auditable back to the originating document.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


def ceil_to_ringgit(amount: float) -> float:
    """Round UP to the next whole Ringgit ("rounded to the next ringgit" per
    EPF/SOCSO source documents), never down, matching statutory rounding."""
    return math.ceil(round(amount, 6))


class RuleStatus(str, Enum):
    OK = "ok"
    NOT_APPLICABLE = "not_applicable"
    PENDING_SME_VALIDATION = "pending_sme_validation"
    ERROR = "error"


@dataclass
class RuleResult:
    rule_id: str
    component: str
    status: RuleStatus
    expected_employee_amount: float | None = None
    expected_employer_amount: float | None = None
    expected_total_amount: float | None = None
    explanation: str = ""
    source: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "component": self.component,
            "status": self.status.value,
            "expected_employee_amount": self.expected_employee_amount,
            "expected_employer_amount": self.expected_employer_amount,
            "expected_total_amount": self.expected_total_amount,
            "explanation": self.explanation,
            "source": self.source,
            "metadata": self.metadata,
        }


@dataclass
class EmployeeContext:
    """Minimal canonical employee attributes required for MY statutory rules."""

    employee_id: str
    nationality: str  # "MY" for Malaysian citizen, else ISO country code
    is_permanent_resident: bool = False
    elected_before_1998_08_01: bool = False
    date_of_birth: str | None = None  # ISO date
    age_years: int | None = None
    employment_type: str = "permanent"  # permanent | contract | domestic_servant
    is_director_fee_only: bool = False
    work_state: str | None = None


@dataclass
class WageContext:
    """Wage figures for a single pay period, in RM."""

    basic_salary: float = 0.0
    fixed_allowance: float = 0.0
    unpaid_leave_deduction: float = 0.0
    other_epf_wages: float = 0.0  # any other EPF-liable wage components
    reference_date: str | None = None

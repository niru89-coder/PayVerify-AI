"""
Rule Engine Registry - dispatches component code -> calculator function.

This is the single entry point the Validation Engine (Phase 8) uses to invoke
deterministic rule calculations. It never contains statutory logic itself -
only routing - so that adding a new country/component means adding a module
plus one registry entry.
"""
from __future__ import annotations

from typing import Callable

from base import EmployeeContext, RuleResult, WageContext
from eis import calculate_eis
from epf import calculate_epf
from hrdf import calculate_hrdf
from pcb import calculate_pcb
from socso import calculate_socso

ComponentCalculator = Callable[..., RuleResult]

REGISTRY: dict[str, ComponentCalculator] = {
    "EPF": calculate_epf,
    "SOCSO": calculate_socso,
    "EIS": calculate_eis,
    "HRDF": calculate_hrdf,
    "PCB": calculate_pcb,
}


def get_calculator(component: str) -> ComponentCalculator:
    try:
        return REGISTRY[component.upper()]
    except KeyError as exc:
        raise ValueError(f"No rule engine calculator registered for component '{component}'.") from exc


def calculate(component: str, employee: EmployeeContext, wage: WageContext, **kwargs) -> RuleResult:
    calculator = get_calculator(component)
    return calculator(employee, wage, **kwargs)

"""
Column Mapping Engine (BRD FR-06, FR-07, FR-08).

Maps arbitrary client/platform register column headers to the canonical
payroll component codes defined in knowledge-base/malaysia/payroll-components.md.

Two independent mapping flows are supported (Client Register, Platform/Darwinbox
Register) because the two systems rarely use the same column names. Mapping is:
  1. Exact match (case/whitespace-insensitive) against known synonyms.
  2. Fuzzy match (difflib) as a fallback suggestion - NEVER auto-applied silently;
     fuzzy matches are returned with a confidence score for human confirmation.
  3. Manual override always wins and can be saved as a reusable MappingTemplate.

This module performs NO payroll calculation - it only renames/aligns columns.
"""
from __future__ import annotations

import difflib
from dataclasses import dataclass, field

# Canonical component codes, per knowledge-base/malaysia/payroll-components.md
CANONICAL_COMPONENTS = [
    "EMPLOYEE_ID",
    "EMPLOYEE_NAME",
    "DATE_OF_BIRTH",
    "NATIONALITY",
    "IS_PERMANENT_RESIDENT",
    "ELECTED_BEFORE_1998_08_01",
    "DATE_OF_JOINING",
    "DATE_OF_EXIT",
    "UNPAID_LEAVE_DAYS",
    "EMPLOYMENT_TYPE",
    "IS_DIRECTOR_FEE_ONLY",
    "BASIC",
    "TRANSPORT_ALLOWANCE",
    "FIXED_ALLOWANCE",
    "OT_NORMAL",
    "OT_REST_DAY",
    "OT_PUBLIC_HOLIDAY",
    "EPF_EMPLOYEE",
    "EPF_EMPLOYER",
    "SOCSO_EMPLOYEE",
    "SOCSO_EMPLOYER",
    "EIS_EMPLOYEE",
    "EIS_EMPLOYER",
    "HRDF_LEVY",
    "PCB",
]

# Known synonyms per canonical code. Keys are normalized (lower, no punctuation/spaces).
SYNONYMS: dict[str, list[str]] = {
    "EMPLOYEE_ID": ["employee id", "emp id", "empid", "staff id", "employee no", "emp no", "id"],
    "EMPLOYEE_NAME": ["employee name", "emp name", "name", "staff name"],
    "DATE_OF_BIRTH": ["date of birth", "dob", "birth date"],
    "NATIONALITY": ["nationality", "citizenship", "country of citizenship"],
    "IS_PERMANENT_RESIDENT": ["permanent resident", "pr status", "is pr", "pr"],
    "ELECTED_BEFORE_1998_08_01": ["elected before 1998", "pre 1998 election", "elected pre 1998"],
    "DATE_OF_JOINING": ["date of joining", "doj", "join date", "hire date"],
    "DATE_OF_EXIT": ["date of exit", "doe", "resignation date", "last working day", "exit date"],
    "UNPAID_LEAVE_DAYS": ["unpaid leave", "unpaid leave days", "leave without pay", "lwop days"],
    "EMPLOYMENT_TYPE": ["employment type", "employee type", "staff type"],
    "IS_DIRECTOR_FEE_ONLY": ["director fee only", "director fees only", "is director"],
    "BASIC": ["basic salary", "basic pay", "basic wage", "basic"],
    "TRANSPORT_ALLOWANCE": ["transport allowance", "travel allowance", "transport"],
    "FIXED_ALLOWANCE": ["fixed allowance", "other allowance", "allowance"],
    "OT_NORMAL": ["ot normal", "overtime normal", "ot normal day", "overtime pay"],
    "OT_REST_DAY": ["ot rest day", "overtime rest day", "rest day ot"],
    "OT_PUBLIC_HOLIDAY": ["ot public holiday", "overtime public holiday", "ph ot"],
    "EPF_EMPLOYEE": ["epf employee", "epf ee", "kwsp employee", "employee epf"],
    "EPF_EMPLOYER": ["epf employer", "epf er", "kwsp employer", "employer epf"],
    "SOCSO_EMPLOYEE": ["socso employee", "socso ee", "perkeso employee", "employee socso"],
    "SOCSO_EMPLOYER": ["socso employer", "socso er", "perkeso employer", "employer socso"],
    "EIS_EMPLOYEE": ["eis employee", "eis ee", "employee eis"],
    "EIS_EMPLOYER": ["eis employer", "eis er", "employer eis"],
    "HRDF_LEVY": ["hrdf levy", "hrdf", "hrd corp levy", "training levy"],
    "PCB": ["pcb", "mtd", "monthly tax deduction", "potongan cukai bulanan", "income tax"],
}


def _normalize(text: str) -> str:
    return " ".join(text.strip().lower().replace("_", " ").replace("-", " ").split())


@dataclass
class MappingSuggestion:
    source_column: str
    canonical_code: str | None
    confidence: float  # 0.0-1.0
    method: str  # "exact" | "fuzzy" | "unmapped"


@dataclass
class MappingResult:
    suggestions: list[MappingSuggestion] = field(default_factory=list)

    def to_column_map(self, min_confidence: float = 0.999) -> dict[str, str]:
        """Only auto-accept exact (confidence>=min_confidence) matches; the rest need human review."""
        return {
            s.source_column: s.canonical_code
            for s in self.suggestions
            if s.canonical_code and s.confidence >= min_confidence
        }

    def needs_review(self) -> list[MappingSuggestion]:
        return [s for s in self.suggestions if s.canonical_code is None or s.confidence < 0.999]


# Build a reverse lookup: normalized synonym -> canonical code
_SYNONYM_LOOKUP: dict[str, str] = {}
for code, synonyms in SYNONYMS.items():
    _SYNONYM_LOOKUP[_normalize(code)] = code
    for syn in synonyms:
        _SYNONYM_LOOKUP[_normalize(syn)] = code


def suggest_mapping(source_columns: list[str], fuzzy_cutoff: float = 0.72) -> MappingResult:
    """Suggest a canonical mapping for each source column header.

    Exact synonym matches get confidence 1.0. Fuzzy matches (difflib) get a
    confidence equal to the similarity ratio, capped below 1.0, and must be
    confirmed by a human before being persisted into a MappingTemplate.
    """
    result = MappingResult()
    normalized_keys = list(_SYNONYM_LOOKUP.keys())

    for col in source_columns:
        norm = _normalize(col)
        if norm in _SYNONYM_LOOKUP:
            result.suggestions.append(
                MappingSuggestion(source_column=col, canonical_code=_SYNONYM_LOOKUP[norm], confidence=1.0, method="exact")
            )
            continue

        close = difflib.get_close_matches(norm, normalized_keys, n=1, cutoff=fuzzy_cutoff)
        if close:
            match_key = close[0]
            ratio = difflib.SequenceMatcher(None, norm, match_key).ratio()
            result.suggestions.append(
                MappingSuggestion(
                    source_column=col,
                    canonical_code=_SYNONYM_LOOKUP[match_key],
                    confidence=round(ratio, 3),
                    method="fuzzy",
                )
            )
        else:
            result.suggestions.append(
                MappingSuggestion(source_column=col, canonical_code=None, confidence=0.0, method="unmapped")
            )

    return result


def apply_mapping(rows: list[dict], column_map: dict[str, str]) -> list[dict]:
    """Rename each row's keys from source column names to canonical codes.

    Unmapped columns (not present in column_map) are dropped from the output -
    callers should surface `needs_review()` results to the user beforehand so
    nothing is silently discarded.
    """
    mapped_rows = []
    for row in rows:
        mapped_rows.append({column_map[k]: v for k, v in row.items() if k in column_map})
    return mapped_rows

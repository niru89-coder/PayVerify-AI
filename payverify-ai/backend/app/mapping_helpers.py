"""Thin adapters between the FastAPI layer and services/mapping_engine.py,
plus a fixed-schema parser for the Employee Master CSV (see
knowledge-base/malaysia/employee-master.md)."""
from __future__ import annotations

import csv
import io

from mapping_engine import suggest_mapping
from . import schemas


def build_mapping_preview(headers: list[str]) -> schemas.MappingPreviewOut:
    result = suggest_mapping(headers)
    suggestions = [
        schemas.MappingSuggestionOut(
            source_column=s.source_column, canonical_code=s.canonical_code,
            confidence=s.confidence, method=s.method,
        )
        for s in result.suggestions
    ]
    return schemas.MappingPreviewOut(
        suggestions=suggestions,
        auto_accepted_column_map=result.to_column_map(),
        needs_review=[
            schemas.MappingSuggestionOut(
                source_column=s.source_column, canonical_code=s.canonical_code,
                confidence=s.confidence, method=s.method,
            )
            for s in result.needs_review()
        ],
    )


_BOOL_TRUE = {"y", "yes", "true", "1"}


def _bool(value: str) -> bool:
    return (value or "").strip().lower() in _BOOL_TRUE


def _int_or_none(value: str) -> int | None:
    value = (value or "").strip()
    return int(value) if value else None


def parse_employee_master_csv(content: str) -> list[dict]:
    """Parses the fixed Employee Master schema (see sample-data/employee_master.csv)
    into kwargs ready for the Employee ORM model."""
    reader = csv.DictReader(io.StringIO(content))
    rows = []
    for row in reader:
        rows.append({
            "external_employee_id": row["id"],
            "date_of_birth": row.get("dob") or None,
            "age_years": _int_or_none(row.get("age")),
            "nationality": row.get("nationality") or None,
            "is_permanent_resident": _bool(row.get("is_pr")),
            "elected_before_1998_08_01": _bool(row.get("elected_pre_1998")),
            "date_of_joining": row.get("doj") or None,
            "date_of_exit": row.get("doe") or None,
            "unpaid_leave_days": _int_or_none(row.get("unpaid_leave_days")) or 0,
            "work_state": None,
            "employment_type": row.get("employment_type") or "permanent",
            "is_director_fee_only": _bool(row.get("is_director_fee_only")),
        })
    return rows

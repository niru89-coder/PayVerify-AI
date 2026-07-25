"""Pydantic request/response schemas for the PayVerify AI REST API."""
from __future__ import annotations

import datetime

from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    name: str
    country: str = "MY"
    pay_period_year: int
    pay_period_month: int


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    country: str
    pay_period_year: int
    pay_period_month: int
    created_at: datetime.datetime


class MappingSuggestionOut(BaseModel):
    source_column: str
    canonical_code: str | None
    confidence: float
    method: str


class MappingPreviewOut(BaseModel):
    suggestions: list[MappingSuggestionOut]
    auto_accepted_column_map: dict[str, str]
    needs_review: list[MappingSuggestionOut]


class RegisterUploadResult(BaseModel):
    register_id: int
    register_type: str
    row_count: int
    employees_created: int
    employees_matched: int


class VarianceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    employee_id: int
    component_code: str
    client_value: float | None
    platform_value: float | None
    expected_value: float | None
    rule_id: str | None
    classification: str
    suggestion_outcome: str
    recommended_action: str
    explanation: str
    confidence_score: float
    ai_explanation: str | None
    resolution_status: str
    created_at: datetime.datetime


class ValidationRunResult(BaseModel):
    project_id: int
    variances_created: int
    classification_summary: dict[str, int]


class FeedbackCreate(BaseModel):
    action: str  # confirmed | rejected | needs_correction
    consultant: str = ""
    notes: str = ""


class FeedbackOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    variance_id: int
    action: str
    consultant: str
    notes: str
    created_at: datetime.datetime


class RuleSummaryOut(BaseModel):
    rule_id: str
    component: str
    country: str
    status: str
    version: str
    effective_date: str
    source_document: str

"""
Canonical Payroll Data Model (Phase 7 / BRD Section 9-10).

Reflects the BRD's core architecture: every payroll component value is
recorded per REGISTER (Client or Platform/Darwinbox), and reconciled against
an independently computed Rule Engine expected value - a genuine three-way
comparison, not a simple single-register validation.
"""
from __future__ import annotations

import datetime
import enum

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def _utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


class RegisterType(str, enum.Enum):
    CLIENT = "client"
    PLATFORM = "platform"


class VarianceClassification(str, enum.Enum):
    NOT_CALCULATED_ONE_SIDE = "component_not_calculated_one_side"
    AMOUNT_MISMATCH_WITHIN_TOLERANCE = "amount_mismatch_within_tolerance"
    AMOUNT_MISMATCH_BEYOND_TOLERANCE = "amount_mismatch_beyond_tolerance"
    RATE_SLAB_MISMATCH = "rate_slab_mismatch"
    ELIGIBILITY_MISMATCH = "eligibility_mismatch"
    DATA_QUALITY_ISSUE = "data_quality_issue"
    NO_VARIANCE = "no_variance"


class SuggestionOutcome(str, enum.Enum):
    PLATFORM_CORRECT = "platform_correct_client_review"
    CLIENT_CORRECT = "client_correct_platform_review"
    INCONCLUSIVE = "inconclusive_clarification_required"
    NOT_APPLICABLE = "not_applicable"


class ResolutionStatus(str, enum.Enum):
    OPEN = "open"
    PENDING_CLIENT = "pending_client"
    PENDING_INTERNAL = "pending_internal"
    RESOLVED = "resolved"


class FeedbackAction(str, enum.Enum):
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    NEEDS_CORRECTION = "needs_correction"


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=_utcnow)

    projects: Mapped[list["Project"]] = relationship(back_populates="organization")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(200))
    country: Mapped[str] = mapped_column(String(10), default="MY")
    pay_period_year: Mapped[int] = mapped_column(Integer)
    pay_period_month: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=_utcnow)

    organization: Mapped[Organization | None] = relationship(back_populates="projects")
    employees: Mapped[list["Employee"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    registers: Mapped[list["Register"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    variances: Mapped[list["Variance"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (UniqueConstraint("project_id", "external_employee_id", name="uq_employee_project_extid"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    external_employee_id: Mapped[str] = mapped_column(String(50))
    date_of_birth: Mapped[str | None] = mapped_column(String(10), nullable=True)  # ISO date
    age_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    nationality: Mapped[str | None] = mapped_column(String(10), nullable=True)
    is_permanent_resident: Mapped[bool] = mapped_column(Boolean, default=False)
    elected_before_1998_08_01: Mapped[bool] = mapped_column(Boolean, default=False)
    date_of_joining: Mapped[str | None] = mapped_column(String(10), nullable=True)
    date_of_exit: Mapped[str | None] = mapped_column(String(10), nullable=True)
    unpaid_leave_days: Mapped[int] = mapped_column(Integer, default=0)
    work_state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    employment_type: Mapped[str] = mapped_column(String(30), default="permanent")
    is_director_fee_only: Mapped[bool] = mapped_column(Boolean, default=False)
    data_quality_flags: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    project: Mapped[Project] = relationship(back_populates="employees")
    pay_component_values: Mapped[list["PayComponentValue"]] = relationship(
        back_populates="employee", cascade="all, delete-orphan"
    )


class Register(Base):
    """One uploaded file (Client or Platform/Darwinbox) for a project."""

    __tablename__ = "registers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    register_type: Mapped[RegisterType] = mapped_column(Enum(RegisterType))
    original_filename: Mapped[str] = mapped_column(String(255))
    mapping_template_id: Mapped[int | None] = mapped_column(ForeignKey("mapping_templates.id"), nullable=True)
    uploaded_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=_utcnow)
    row_count: Mapped[int] = mapped_column(Integer, default=0)

    project: Mapped[Project] = relationship(back_populates="registers")
    pay_component_values: Mapped[list["PayComponentValue"]] = relationship(
        back_populates="register", cascade="all, delete-orphan"
    )


class PayComponentValue(Base):
    """A single pay-component amount, from either a Client or Platform register."""

    __tablename__ = "pay_component_values"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    register_id: Mapped[int] = mapped_column(ForeignKey("registers.id"))
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    component_code: Mapped[str] = mapped_column(String(50))
    amount: Mapped[float] = mapped_column(Float)

    register: Mapped[Register] = relationship(back_populates="pay_component_values")
    employee: Mapped[Employee] = relationship(back_populates="pay_component_values")


class MappingTemplate(Base):
    """Reusable client/country column-mapping template (FR-06, FR-08)."""

    __tablename__ = "mapping_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    register_type: Mapped[RegisterType] = mapped_column(Enum(RegisterType))
    country: Mapped[str] = mapped_column(String(10), default="MY")
    column_map: Mapped[dict] = mapped_column(JSON)  # {"EMP ID": "external_employee_id", ...}
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=_utcnow)


class RuleExecutionResult(Base):
    """Cached deterministic rule-engine output for one employee x component."""

    __tablename__ = "rule_execution_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    component_code: Mapped[str] = mapped_column(String(50))
    rule_id: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(30))
    expected_employee_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    expected_employer_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    expected_total_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    explanation: Mapped[str] = mapped_column(String(1000), default="")
    computed_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=_utcnow)


class Variance(Base):
    """Three-way comparison result: Client value vs Platform value vs Rule-Engine expected."""

    __tablename__ = "variances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    component_code: Mapped[str] = mapped_column(String(50))
    client_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    platform_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    expected_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    rule_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    classification: Mapped[VarianceClassification] = mapped_column(Enum(VarianceClassification))
    suggestion_outcome: Mapped[SuggestionOutcome] = mapped_column(Enum(SuggestionOutcome))
    recommended_action: Mapped[str] = mapped_column(String(1000), default="")
    explanation: Mapped[str] = mapped_column(String(2000), default="")
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    ai_explanation: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    resolution_status: Mapped[ResolutionStatus] = mapped_column(Enum(ResolutionStatus), default=ResolutionStatus.OPEN)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=_utcnow)

    project: Mapped[Project] = relationship(back_populates="variances")
    feedback_entries: Mapped[list["Feedback"]] = relationship(back_populates="variance", cascade="all, delete-orphan")


class Feedback(Base):
    """Consultant confirm/reject/correct feedback loop (FR-25 to FR-27)."""

    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    variance_id: Mapped[int] = mapped_column(ForeignKey("variances.id"))
    action: Mapped[FeedbackAction] = mapped_column(Enum(FeedbackAction))
    consultant: Mapped[str] = mapped_column(String(200), default="")
    notes: Mapped[str] = mapped_column(String(2000), default="")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=_utcnow)

    variance: Mapped[Variance] = relationship(back_populates="feedback_entries")


class AuditLogEntry(Base):
    """Immutable audit trail (BRD Section 10 - Audit & Logging Layer)."""

    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    action: Mapped[str] = mapped_column(String(100))
    detail: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=_utcnow)

"""
PayVerify AI - FastAPI REST API (Phase 9/12).

Endpoints implement the pipeline described in the BRD: Project setup ->
Employee master upload -> Client/Platform register upload (via the column
Mapping Engine) -> Validation run (Rule Engine + Reconciliation Engine,
three-way comparison) -> Variance review + consultant Feedback loop.

All statutory computation and variance classification is 100% deterministic
(rule-engine/ + validation-engine/). The AI explanation agent (agents/) is
stubbed and only narrates already-computed Variance rows; it is NEVER used
to calculate or override a figure.
"""
from __future__ import annotations

# Bootstrap must run before importing any flat-module engine packages.
from . import bootstrap  # noqa: F401,E402

import csv
import io
import json
import os
import pathlib
from collections import Counter
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import delete
from sqlalchemy.orm import Session

from . import models, schemas
from .database import get_db, init_db
from .mapping_helpers import build_mapping_preview, parse_employee_master_csv
from .middleware.logging import RequestLoggingMiddleware
from .routes import monitoring

from base import EmployeeContext, RuleStatus, WageContext  # noqa: E402
from epf import calculate_epf  # noqa: E402
from hrdf import calculate_hrdf  # noqa: E402
from reconciliation import classify_variance  # noqa: E402
from explanation_agent import VarianceExplanationRequest, get_default_provider  # noqa: E402

RULES_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "rules" / "json"


@asynccontextmanager
async def _lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="PayVerify AI", version="0.1.0", lifespan=_lifespan)

# Local dev frontend (Next.js) - restrict to known origins only. Override via
# CORS_ALLOWED_ORIGINS (comma-separated) in deployed environments, e.g. Docker/Render.
_default_origins = "http://localhost:3000,http://127.0.0.1:3000"
_cors_origins = [
    origin.strip()
    for origin in os.environ.get("CORS_ALLOWED_ORIGINS", _default_origins).split(",")
    if origin.strip()
]

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include monitoring routes (Phase 3.6: /health, /status, /metrics)
app.include_router(monitoring.router)


# --------------------------------------------------------------------------
# Projects
# --------------------------------------------------------------------------

@app.post("/api/projects", response_model=schemas.ProjectOut)
def create_project(payload: schemas.ProjectCreate, db: Session = Depends(get_db)):
    project = models.Project(
        name=payload.name,
        country=payload.country,
        pay_period_year=payload.pay_period_year,
        pay_period_month=payload.pay_period_month,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@app.get("/api/projects", response_model=list[schemas.ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return db.query(models.Project).order_by(models.Project.id).all()


@app.get("/api/projects/{project_id}", response_model=schemas.ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(models.Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# --------------------------------------------------------------------------
# Employee master upload
# --------------------------------------------------------------------------

@app.post("/api/projects/{project_id}/employees/upload")
def upload_employee_master(project_id: int, file: UploadFile, db: Session = Depends(get_db)):
    project = db.get(models.Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    content = file.file.read().decode("utf-8-sig")
    rows = parse_employee_master_csv(content)

    created = 0
    for row in rows:
        existing = (
            db.query(models.Employee)
            .filter_by(project_id=project_id, external_employee_id=row["external_employee_id"])
            .first()
        )
        if existing:
            for key, value in row.items():
                setattr(existing, key, value)
        else:
            db.add(models.Employee(project_id=project_id, **row))
            created += 1
    db.commit()
    return {"rows_processed": len(rows), "employees_created": created}


# --------------------------------------------------------------------------
# Register upload (Client / Platform) via the Mapping Engine
# --------------------------------------------------------------------------

@app.post("/api/projects/{project_id}/registers/preview-mapping", response_model=schemas.MappingPreviewOut)
def preview_register_mapping(project_id: int, file: UploadFile, db: Session = Depends(get_db)):
    if not db.get(models.Project, project_id):
        raise HTTPException(status_code=404, detail="Project not found")

    content = file.file.read().decode("utf-8-sig")
    reader = csv.reader(io.StringIO(content))
    headers = next(reader)
    return build_mapping_preview(headers)


@app.post("/api/projects/{project_id}/registers/upload", response_model=schemas.RegisterUploadResult)
def upload_register(
    project_id: int,
    register_type: str,
    file: UploadFile,
    column_map: str = "",
    db: Session = Depends(get_db),
):
    """`register_type` is "client" or "platform". `column_map` is a JSON string
    ({"Source Column": "CANONICAL_CODE", ...}) confirmed by the user after
    reviewing the mapping preview; falls back to auto-accepted exact matches
    if omitted."""
    project = db.get(models.Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        reg_type = models.RegisterType(register_type.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail="register_type must be 'client' or 'platform'")

    content = file.file.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))
    headers = reader.fieldnames or []
    rows = list(reader)

    if column_map:
        col_map = json.loads(column_map)
    else:
        col_map = build_mapping_preview(headers).auto_accepted_column_map

    register = models.Register(
        project_id=project_id,
        register_type=reg_type,
        original_filename=file.filename or "unknown.csv",
        row_count=len(rows),
    )
    db.add(register)
    db.flush()

    employees_created = 0
    employees_matched = 0
    for row in rows:
        mapped = {col_map[k]: v for k, v in row.items() if k in col_map}
        ext_id = mapped.get("EMPLOYEE_ID")
        if not ext_id:
            continue

        employee = (
            db.query(models.Employee)
            .filter_by(project_id=project_id, external_employee_id=ext_id)
            .first()
        )
        if not employee:
            employee = models.Employee(project_id=project_id, external_employee_id=ext_id)
            db.add(employee)
            db.flush()
            employees_created += 1
        else:
            employees_matched += 1

        for code, value in mapped.items():
            if code in ("EMPLOYEE_ID", "EMPLOYEE_NAME") or value in (None, ""):
                continue
            try:
                amount = float(value)
            except ValueError:
                continue
            db.add(models.PayComponentValue(
                register_id=register.id, employee_id=employee.id, component_code=code, amount=amount,
            ))

    db.commit()
    return schemas.RegisterUploadResult(
        register_id=register.id,
        register_type=reg_type.value,
        row_count=len(rows),
        employees_created=employees_created,
        employees_matched=employees_matched,
    )


# --------------------------------------------------------------------------
# Validation run (Rule Engine + Reconciliation Engine)
# --------------------------------------------------------------------------

# Component codes this MVP can independently compute an expected value for.
_EPF_CODES = {"EPF_EMPLOYEE", "EPF_EMPLOYER"}
_HRDF_CODES = {"HRDF_LEVY"}


def _employee_context(emp: models.Employee) -> EmployeeContext:
    return EmployeeContext(
        employee_id=emp.external_employee_id,
        nationality=emp.nationality or "MY",
        is_permanent_resident=bool(emp.is_permanent_resident),
        elected_before_1998_08_01=bool(emp.elected_before_1998_08_01),
        age_years=emp.age_years,
        employment_type=emp.employment_type or "permanent",
        is_director_fee_only=bool(emp.is_director_fee_only),
    )


@app.post("/api/projects/{project_id}/validate", response_model=schemas.ValidationRunResult)
def run_validation(project_id: int, db: Session = Depends(get_db)):
    project = db.get(models.Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Idempotent re-run: clear previous variances for this project.
    db.execute(delete(models.Variance).where(models.Variance.project_id == project_id))
    db.commit()

    employees = db.query(models.Employee).filter_by(project_id=project_id).all()
    client_register = (
        db.query(models.Register)
        .filter_by(project_id=project_id, register_type=models.RegisterType.CLIENT)
        .order_by(models.Register.uploaded_at.desc())
        .first()
    )
    platform_register = (
        db.query(models.Register)
        .filter_by(project_id=project_id, register_type=models.RegisterType.PLATFORM)
        .order_by(models.Register.uploaded_at.desc())
        .first()
    )
    if not client_register or not platform_register:
        raise HTTPException(status_code=400, detail="Both a client and a platform register must be uploaded before validation.")

    classification_summary: Counter = Counter()
    variances_created = 0

    for employee in employees:
        client_values = {
            v.component_code: v.amount
            for v in db.query(models.PayComponentValue).filter_by(
                register_id=client_register.id, employee_id=employee.id
            )
        }
        platform_values = {
            v.component_code: v.amount
            for v in db.query(models.PayComponentValue).filter_by(
                register_id=platform_register.id, employee_id=employee.id
            )
        }
        all_components = set(client_values) | set(platform_values)
        emp_ctx = _employee_context(employee)
        basic = client_values.get("BASIC") or platform_values.get("BASIC") or 0.0
        wage_ctx = WageContext(basic_salary=float(basic))

        for component in sorted(all_components):
            rule_result = None
            if component in _EPF_CODES:
                rule_result = calculate_epf(emp_ctx, wage_ctx)
            elif component in _HRDF_CODES:
                rule_result = calculate_hrdf(emp_ctx, wage_ctx)

            finding = classify_variance(
                employee.external_employee_id,
                component,
                client_values.get(component),
                platform_values.get(component),
                rule_result,
            )
            db.add(models.Variance(
                project_id=project_id,
                employee_id=employee.id,
                component_code=component,
                client_value=finding.client_value,
                platform_value=finding.platform_value,
                expected_value=finding.expected_value,
                rule_id=finding.rule_id,
                classification=models.VarianceClassification(finding.classification),
                suggestion_outcome=models.SuggestionOutcome(finding.suggestion_outcome),
                recommended_action=finding.recommended_action,
                explanation=finding.explanation,
                confidence_score=finding.confidence_score,
            ))
            classification_summary[finding.classification] += 1
            variances_created += 1

    db.commit()
    return schemas.ValidationRunResult(
        project_id=project_id,
        variances_created=variances_created,
        classification_summary=dict(classification_summary),
    )


# --------------------------------------------------------------------------
# Variances + Feedback
# --------------------------------------------------------------------------

@app.get("/api/projects/{project_id}/variances", response_model=list[schemas.VarianceOut])
def list_variances(
    project_id: int,
    classification: str | None = Query(default=None),
    resolution_status: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(models.Variance).filter_by(project_id=project_id)
    if classification:
        query = query.filter_by(classification=models.VarianceClassification(classification))
    if resolution_status:
        query = query.filter_by(resolution_status=models.ResolutionStatus(resolution_status))
    variances = query.order_by(models.Variance.id).all()
    return [_variance_to_schema(v) for v in variances]


@app.get("/api/variances/{variance_id}", response_model=schemas.VarianceOut)
def get_variance(variance_id: int, db: Session = Depends(get_db)):
    variance = db.get(models.Variance, variance_id)
    if not variance:
        raise HTTPException(status_code=404, detail="Variance not found")
    return _variance_to_schema(variance)


@app.post("/api/variances/{variance_id}/explain", response_model=schemas.VarianceOut)
def explain_variance(variance_id: int, db: Session = Depends(get_db)):
    """Generates (or regenerates) the AI narrative explanation for an already
    fully-classified variance. Never recomputes or overrides the deterministic
    classification/suggestion - see agents/explanation_agent.py guardrails."""
    variance = db.get(models.Variance, variance_id)
    if not variance:
        raise HTTPException(status_code=404, detail="Variance not found")

    provider = get_default_provider()
    request = VarianceExplanationRequest(
        employee_id=str(variance.employee_id),
        component_code=variance.component_code,
        client_value=variance.client_value,
        platform_value=variance.platform_value,
        expected_value=variance.expected_value,
        rule_id=variance.rule_id,
        classification=variance.classification.value,
        suggestion_outcome=variance.suggestion_outcome.value,
        recommended_action=variance.recommended_action,
        confidence_score=variance.confidence_score,
    )
    variance.ai_explanation = provider.explain(request)
    db.commit()
    db.refresh(variance)
    return _variance_to_schema(variance)


@app.post("/api/variances/{variance_id}/feedback", response_model=schemas.FeedbackOut)
def add_feedback(variance_id: int, payload: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    variance = db.get(models.Variance, variance_id)
    if not variance:
        raise HTTPException(status_code=404, detail="Variance not found")
    try:
        action = models.FeedbackAction(payload.action)
    except ValueError:
        raise HTTPException(status_code=400, detail="action must be confirmed|rejected|needs_correction")

    feedback = models.Feedback(
        variance_id=variance_id, action=action, consultant=payload.consultant, notes=payload.notes,
    )
    db.add(feedback)

    if action == models.FeedbackAction.CONFIRMED:
        variance.resolution_status = models.ResolutionStatus.RESOLVED
    elif action == models.FeedbackAction.NEEDS_CORRECTION:
        variance.resolution_status = models.ResolutionStatus.PENDING_INTERNAL
    elif action == models.FeedbackAction.REJECTED:
        variance.resolution_status = models.ResolutionStatus.PENDING_CLIENT

    db.commit()
    db.refresh(feedback)
    return feedback


def _variance_to_schema(v: models.Variance) -> schemas.VarianceOut:
    return schemas.VarianceOut(
        id=v.id,
        project_id=v.project_id,
        employee_id=v.employee_id,
        component_code=v.component_code,
        client_value=v.client_value,
        platform_value=v.platform_value,
        expected_value=v.expected_value,
        rule_id=v.rule_id,
        classification=v.classification.value,
        suggestion_outcome=v.suggestion_outcome.value,
        recommended_action=v.recommended_action,
        explanation=v.explanation,
        confidence_score=v.confidence_score,
        ai_explanation=v.ai_explanation,
        resolution_status=v.resolution_status.value,
        created_at=v.created_at,
    )


# --------------------------------------------------------------------------
# Rule catalog (read-only, backed by rules/json/*.json)
# --------------------------------------------------------------------------

@app.get("/api/rules", response_model=list[schemas.RuleSummaryOut])
def list_rules():
    rules = []
    for path in sorted(RULES_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        rules.append(schemas.RuleSummaryOut(
            rule_id=data["RuleId"],
            component=data["Component"],
            country=data["Country"],
            status=data["Status"],
            version=data["Version"],
            effective_date=data["EffectiveDate"],
            source_document=data["SourceDocument"],
        ))
    return rules

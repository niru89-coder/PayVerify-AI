"""Integration tests for the FastAPI REST API using the synthetic sample data."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from fastapi.testclient import TestClient

from app.main import app  # noqa: E402

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample-data"

client = TestClient(app)


def _create_project() -> int:
    resp = client.post("/api/projects", json={
        "name": "Acme Corp MY Parallel Run", "country": "MY",
        "pay_period_year": 2026, "pay_period_month": 1,
    })
    assert resp.status_code == 200, resp.text
    return resp.json()["id"]


def _upload_csv(path: str, project_id: int, content_type_field: str) -> dict:
    with open(SAMPLE_DIR / path, "rb") as f:
        resp = client.post(
            f"/api/projects/{project_id}/{content_type_field}",
            files={"file": (path, f, "text/csv")},
        )
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_full_pipeline_end_to_end():
    project_id = _create_project()

    result = _upload_csv("employee_master.csv", project_id, "employees/upload")
    assert result["employees_created"] == 10

    with open(SAMPLE_DIR / "client_register.csv", "rb") as f:
        resp = client.post(
            f"/api/projects/{project_id}/registers/upload",
            params={"register_type": "client"},
            files={"file": ("client_register.csv", f, "text/csv")},
        )
    assert resp.status_code == 200, resp.text
    client_result = resp.json()
    assert client_result["row_count"] == 10

    with open(SAMPLE_DIR / "platform_register.csv", "rb") as f:
        resp = client.post(
            f"/api/projects/{project_id}/registers/upload",
            params={"register_type": "platform"},
            files={"file": ("platform_register.csv", f, "text/csv")},
        )
    assert resp.status_code == 200, resp.text

    resp = client.post(f"/api/projects/{project_id}/validate")
    assert resp.status_code == 200, resp.text
    validation_result = resp.json()
    assert validation_result["variances_created"] > 0
    assert "no_variance" in validation_result["classification_summary"]

    resp = client.get(f"/api/projects/{project_id}/variances")
    assert resp.status_code == 200
    variances = resp.json()
    assert len(variances) > 0

    not_calculated = [v for v in variances if v["classification"] == "component_not_calculated_one_side"]
    assert len(not_calculated) > 0

    # Submit feedback on the first variance and confirm resolution status updates.
    variance_id = variances[0]["id"]
    resp = client.post(f"/api/variances/{variance_id}/feedback", json={
        "action": "confirmed", "consultant": "test-consultant", "notes": "Looks correct.",
    })
    assert resp.status_code == 200, resp.text
    resp = client.get(f"/api/variances/{variance_id}")
    assert resp.json()["resolution_status"] == "resolved"


def test_explain_variance_endpoint():
    project_id = _create_project()
    _upload_csv("employee_master.csv", project_id, "employees/upload")
    with open(SAMPLE_DIR / "client_register.csv", "rb") as f:
        client.post(f"/api/projects/{project_id}/registers/upload", params={"register_type": "client"},
                    files={"file": ("client_register.csv", f, "text/csv")})
    with open(SAMPLE_DIR / "platform_register.csv", "rb") as f:
        client.post(f"/api/projects/{project_id}/registers/upload", params={"register_type": "platform"},
                    files={"file": ("platform_register.csv", f, "text/csv")})
    client.post(f"/api/projects/{project_id}/validate")

    variances = client.get(f"/api/projects/{project_id}/variances").json()
    variance_id = variances[0]["id"]

    resp = client.post(f"/api/variances/{variance_id}/explain")
    assert resp.status_code == 200, resp.text
    assert resp.json()["ai_explanation"]


def test_mapping_preview_endpoint():
    project_id = _create_project()
    with open(SAMPLE_DIR / "client_register.csv", "rb") as f:
        resp = client.post(
            f"/api/projects/{project_id}/registers/preview-mapping",
            files={"file": ("client_register.csv", f, "text/csv")},
        )
    assert resp.status_code == 200, resp.text
    preview = resp.json()
    codes = {s["canonical_code"] for s in preview["suggestions"]}
    assert "EMPLOYEE_ID" in codes
    assert "BASIC" in codes


def test_rules_catalog_endpoint():
    resp = client.get("/api/rules")
    assert resp.status_code == 200
    rules = resp.json()
    rule_ids = {r["rule_id"] for r in rules}
    assert "MY_EPF_001" in rule_ids
    assert "MY_SOCSO_001" in rule_ids

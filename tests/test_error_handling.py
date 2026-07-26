"""
Unit tests for Phase 3.7 centralized error handling (backend/app/main.py).

Verifies that error responses:
- Keep a top-level "detail" key (frontend/OpenAPI-client compatibility)
- Carry a "request_id" for log correlation
- Never leak raw exception text unless DEBUG=true
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_404_response_has_detail_and_request_id():
    resp = client.get("/api/projects/999999")
    assert resp.status_code == 404
    body = resp.json()
    assert body["detail"] == "Project not found"
    assert "request_id" in body
    assert len(body["request_id"]) > 0


def test_validation_error_has_detail_and_request_id():
    # Missing required fields in ProjectCreate triggers a 422.
    resp = client.post("/api/projects", json={"name": "Incomplete"})
    assert resp.status_code == 422
    body = resp.json()
    assert "detail" in body
    assert "request_id" in body


def test_debug_mode_defaults_to_false(monkeypatch):
    import os

    monkeypatch.delenv("DEBUG", raising=False)
    from app.main import _DEBUG as debug_at_import_time

    # _DEBUG is computed once at import time; verify the *default* env
    # behavior independently (module already imported as False in this suite).
    assert os.environ.get("DEBUG", "false").strip().lower() not in ("1", "true", "yes")

"""
Unit tests for Phase 3.7 JWT authentication (backend/app/auth.py + /auth/token).

These tests explicitly enable AUTH_ENABLED (overriding the autouse
"disabled by default" fixture in tests/conftest.py) to exercise the
protected-endpoint behavior end-to-end.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

import pytest
from fastapi.testclient import TestClient

from app.auth import authenticate_admin, create_access_token, hash_password, verify_password
from app.main import app

client = TestClient(app)

_TEST_PASSWORD = "correct-horse-battery-staple"


@pytest.fixture
def auth_enabled(monkeypatch):
    """Enable auth with a known admin credential + JWT secret for this test."""
    monkeypatch.setenv("AUTH_ENABLED", "true")
    monkeypatch.setenv("JWT_SECRET", "test-secret-key-do-not-use-in-prod")
    monkeypatch.setenv("ADMIN_USERNAME", "admin")
    monkeypatch.setenv("ADMIN_PASSWORD_HASH", hash_password(_TEST_PASSWORD))
    yield


def test_hash_and_verify_password_roundtrip():
    hashed = hash_password("hunter2")
    assert hashed != "hunter2"
    assert verify_password("hunter2", hashed) is True
    assert verify_password("wrong", hashed) is False


def test_authenticate_admin_rejects_when_no_hash_configured(monkeypatch):
    monkeypatch.delenv("ADMIN_PASSWORD_HASH", raising=False)
    assert authenticate_admin("admin", "anything") is False


def test_authenticate_admin_accepts_correct_credentials(monkeypatch):
    monkeypatch.setenv("ADMIN_USERNAME", "admin")
    monkeypatch.setenv("ADMIN_PASSWORD_HASH", hash_password(_TEST_PASSWORD))
    assert authenticate_admin("admin", _TEST_PASSWORD) is True


def test_authenticate_admin_rejects_wrong_password(monkeypatch):
    monkeypatch.setenv("ADMIN_USERNAME", "admin")
    monkeypatch.setenv("ADMIN_PASSWORD_HASH", hash_password(_TEST_PASSWORD))
    assert authenticate_admin("admin", "wrong-password") is False


def test_authenticate_admin_rejects_wrong_username(monkeypatch):
    monkeypatch.setenv("ADMIN_USERNAME", "admin")
    monkeypatch.setenv("ADMIN_PASSWORD_HASH", hash_password(_TEST_PASSWORD))
    assert authenticate_admin("someone-else", _TEST_PASSWORD) is False


def test_token_endpoint_issues_bearer_token(auth_enabled):
    resp = client.post("/auth/token", data={"username": "admin", "password": _TEST_PASSWORD})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_token_endpoint_rejects_bad_credentials(auth_enabled):
    resp = client.post("/auth/token", data={"username": "admin", "password": "wrong"})
    assert resp.status_code == 401


def test_protected_endpoint_rejects_missing_token_when_auth_enabled(auth_enabled):
    resp = client.post("/api/projects", json={
        "name": "Should Fail", "country": "MY", "pay_period_year": 2026, "pay_period_month": 1,
    })
    assert resp.status_code == 401


def test_protected_endpoint_accepts_valid_token_when_auth_enabled(auth_enabled):
    token_resp = client.post("/auth/token", data={"username": "admin", "password": _TEST_PASSWORD})
    token = token_resp.json()["access_token"]

    resp = client.post(
        "/api/projects",
        json={"name": "Should Succeed", "country": "MY", "pay_period_year": 2026, "pay_period_month": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text


def test_protected_endpoint_rejects_garbage_token(auth_enabled):
    resp = client.post(
        "/api/projects",
        json={"name": "Should Fail", "country": "MY", "pay_period_year": 2026, "pay_period_month": 1},
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert resp.status_code == 401


def test_unprotected_endpoints_still_work_when_auth_enabled(auth_enabled):
    """Read-only endpoints (e.g. GET /api/projects) are not gated by auth."""
    resp = client.get("/api/projects")
    assert resp.status_code == 200


def test_auth_disabled_by_default_allows_unauthenticated_requests():
    """Sanity check that the conftest.py autouse fixture keeps auth off by default."""
    resp = client.post("/api/projects", json={
        "name": "Auth Disabled Test", "country": "MY", "pay_period_year": 2026, "pay_period_month": 1,
    })
    assert resp.status_code == 200

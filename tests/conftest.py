"""Shared pytest fixtures for the PayVerify AI test suite.

Auth (Phase 3.7) is feature-flagged via the AUTH_ENABLED environment variable
so existing endpoint tests do not need to be rewritten to carry a bearer
token. Auth-specific behavior is exercised explicitly in test_auth.py, which
overrides AUTH_ENABLED=true for its own test functions.
"""
from __future__ import annotations

import os

import pytest


@pytest.fixture(autouse=True)
def _disable_auth_by_default(monkeypatch):
    """Keep auth disabled for the general test suite unless a test opts in."""
    monkeypatch.setenv("AUTH_ENABLED", "false")

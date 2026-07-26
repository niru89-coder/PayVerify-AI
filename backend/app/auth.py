"""
JWT authentication layer (Phase 3.7).

Minimal, MVP-appropriate authentication: PayVerify AI has no multi-tenant
user table today, so this issues bearer tokens for a single configured
service/admin credential (env-provided bcrypt hash - never a plaintext
password at rest) rather than modeling a full user directory. Role-based
authorization (e.g. consultant vs admin) is explicitly out of scope for
this release - see docs/production/administrator-guide.md.

Feature flag:
    AUTH_ENABLED=true|false (default: false)
    When false (local dev / test convenience), `require_auth` is a no-op so
    the existing unauthenticated test suite and local `docker compose up`
    workflow keep working unchanged. Production deployments (render.yaml,
    docker-compose.yml) set AUTH_ENABLED=true by default.

Environment variables:
    JWT_SECRET            Required when AUTH_ENABLED=true. HMAC signing key.
    JWT_ALGORITHM          Default "HS256".
    JWT_EXPIRE_MINUTES      Default 60.
    ADMIN_USERNAME          Default "admin".
    ADMIN_PASSWORD_HASH     bcrypt hash of the admin password (see
                            scripts/hash_password.py to generate one).
"""
from __future__ import annotations

import os
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)


def _auth_enabled() -> bool:
    return os.environ.get("AUTH_ENABLED", "false").strip().lower() in ("1", "true", "yes")


def _jwt_secret() -> str:
    secret = os.environ.get("JWT_SECRET")
    if not secret:
        if _auth_enabled():
            raise RuntimeError(
                "AUTH_ENABLED=true but JWT_SECRET is not set. Refusing to start "
                "with an authentication layer that has no signing key."
            )
        # Auth is disabled; a placeholder is fine since no token is ever issued
        # or verified in this mode.
        secret = "unused-dev-secret-auth-disabled"
    return secret


def _jwt_algorithm() -> str:
    return os.environ.get("JWT_ALGORITHM", "HS256")


def _jwt_expire_minutes() -> int:
    return int(os.environ.get("JWT_EXPIRE_MINUTES", "60"))


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        # Malformed/empty hash - never let a config error look like a match.
        return False


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def authenticate_admin(username: str, password: str) -> bool:
    """Check credentials against the single configured admin account.

    Returns False (never raises) on any misconfiguration or mismatch so
    callers can respond with a uniform 401 without leaking which check failed.
    """
    expected_username = os.environ.get("ADMIN_USERNAME", "admin")
    expected_hash = os.environ.get("ADMIN_PASSWORD_HASH", "")
    if not expected_hash:
        return False
    # Always run a dummy check so timing doesn't reveal whether the
    # username matched before the password was compared.
    dummy_hash = bcrypt.hashpw(b"placeholder", bcrypt.gensalt())
    bcrypt.checkpw(password.encode("utf-8"), dummy_hash)
    if not secrets.compare_digest(username, expected_username):
        return False
    return verify_password(password, expected_hash)


def create_access_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=_jwt_expire_minutes())
    payload = {"sub": subject, "iat": now, "exp": expire}
    return jwt.encode(payload, _jwt_secret(), algorithm=_jwt_algorithm())


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, _jwt_secret(), algorithms=[_jwt_algorithm()])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_auth(token: str | None = Depends(_oauth2_scheme)) -> str:
    """FastAPI dependency guarding mutating endpoints.

    No-op (returns "anonymous") when AUTH_ENABLED=false. When enabled,
    requires a valid, non-expired bearer token and returns its subject.
    """
    if not _auth_enabled():
        return "anonymous"
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    claims = _decode_token(token)
    return claims.get("sub", "unknown")

"""Generate a bcrypt hash for ADMIN_PASSWORD_HASH (Phase 3.7 auth).

Usage:
    python scripts/hash_password.py

Prompts for a password (not echoed) and prints the bcrypt hash to store as
the ADMIN_PASSWORD_HASH environment variable. Never commit the plaintext
password or the hash to source control; set it via your deployment
platform's secret manager (Render dashboard env var, Docker secret, etc.).
"""
from __future__ import annotations

import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.auth import hash_password  # noqa: E402


def main() -> None:
    password = getpass.getpass("Password to hash: ")
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("Passwords do not match.", file=sys.stderr)
        raise SystemExit(1)
    if not password:
        print("Password must not be empty.", file=sys.stderr)
        raise SystemExit(1)
    print(hash_password(password))


if __name__ == "__main__":
    main()

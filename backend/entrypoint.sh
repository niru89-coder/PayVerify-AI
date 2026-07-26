#!/usr/bin/env sh
# Entrypoint for the PayVerify AI backend container (Phase 3.7).
#
# Applies pending Alembic migrations before starting the API so the schema
# is always in sync with the deployed code - no manual migration step to
# forget on deploy. Safe to run on every container start: `alembic upgrade
# head` is a no-op when the database is already at the latest revision.
set -e

echo "Applying database migrations (alembic upgrade head)..."
python -m alembic upgrade head

echo "Starting API server..."
exec python -m uvicorn backend.app.main:app --host 0.0.0.0 --port "${PORT:-8000}"

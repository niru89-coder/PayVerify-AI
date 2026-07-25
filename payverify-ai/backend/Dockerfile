# PayVerify AI - Backend (FastAPI) production image.
# Build context MUST be the payverify-ai/ repo root (not backend/), since the
# rule-engine/validation-engine/services/agents flat-module directories live
# alongside backend/, not inside it. See docker-compose.yml.

# ---- Stage 1: install Python dependencies ----
FROM python:3.12-slim AS builder
WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Stage 2: runtime image ----
FROM python:3.12-slim AS runtime
WORKDIR /app

RUN useradd --create-home --uid 1000 appuser

COPY --from=builder /install /usr/local

# Only the directories actually imported at runtime (see backend/app/bootstrap.py).
COPY backend/ backend/
COPY rule-engine/ rule-engine/
COPY validation-engine/ validation-engine/
COPY services/ services/
COPY agents/ agents/
COPY rules/ rules/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=5 \
    CMD python -c "import urllib.request,sys; urllib.request.urlopen('http://localhost:8000/health', timeout=3)" || exit 1

CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

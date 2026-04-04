# ---------------------------------------------------------------------------
# Stage 1 — dependency resolver
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS deps

WORKDIR /app

# Install uv for fast dependency resolution
RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
# Resolve and install dependencies into an isolated venv so the final stage
# only needs to copy the pre-built environment
RUN uv venv /opt/venv && \
    uv pip install --python /opt/venv/bin/python --no-cache -r <(uv pip compile pyproject.toml)

# ---------------------------------------------------------------------------
# Stage 2 — production image
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy the pre-built venv from the deps stage
COPY --from=deps /opt/venv /opt/venv

# Copy application source
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Non-root user for security
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --ingroup appgroup appuser
USER appuser

EXPOSE 8000

# Run Alembic migrations then start the server.
# The entrypoint script handles the correct signal forwarding (exec).
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 2"]

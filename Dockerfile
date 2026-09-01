# API image: two-stage uv build -> slim runtime, non-root.
# The worker reuses this image with a `command:` override.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS builder

WORKDIR /app
ENV UV_PROJECT_ENVIRONMENT=/app/.venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Deps first so this layer caches across code edits.
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --no-install-project --frozen

# Then the project itself.
COPY src/ ./src/
COPY migrations/ ./migrations/
COPY alembic.ini ./
RUN uv sync --no-dev --frozen


FROM python:3.12-slim-bookworm

WORKDIR /app
# curl is used by the compose healthcheck against /health.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# The project source + migrations (needed at runtime for `alembic upgrade head`).
COPY src/ ./src/
COPY migrations/ ./migrations/
COPY alembic.ini pyproject.toml uv.lock ./

RUN useradd --create-home --uid 1000 appuser && chown -R appuser /app
USER 1000:1000

EXPOSE 8000
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

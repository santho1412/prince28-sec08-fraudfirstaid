
# syntax=docker/dockerfile:1

# ---------- Stage 1: build the virtual environment ----------
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.11.32 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# 1) Dependencies only
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# 2) Application code
COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

# ---------- Stage 2: runtime image ----------
FROM python:3.12-slim

RUN groupadd --system app && \
    useradd --system --gid app --home-dir /app --no-create-home app

WORKDIR /app

# Copy only runtime requirements
COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --chown=app:app alembic.ini ./
COPY --chown=app:app alembic ./alembic
COPY --chown=app:app scripts ./scripts
COPY --chown=app:app data ./data

# Embed the Git commit used to build this image
ARG GIT_SHA=dev

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    GIT_SHA=${GIT_SHA}

USER app

EXPOSE 8000

CMD ["sh", "-c", "exec uvicorn fraudfirstaid.api.main:create_app --factory --host 0.0.0.0 --port ${PORT:-8000} --no-access-log"]

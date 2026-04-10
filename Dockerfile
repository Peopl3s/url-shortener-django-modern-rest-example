# =============================================================================
# Stage 1 — builder: resolve and install Python dependencies with uv
# =============================================================================
FROM python:3.13.5-slim AS builder

# Pull uv binary from its official image — pin to minor version for stability
COPY --from=ghcr.io/astral-sh/uv:0.6 /uv /usr/local/bin/uv

# UV tunables:
#   UV_COMPILE_BYTECODE  — pre-compile *.py → *.pyc for faster cold starts
#   UV_LINK_MODE=copy    — copy files instead of hardlinks (safe across layers)
#   UV_PYTHON_DOWNLOADS  — never download Python; use the image's interpreter
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Copy dependency manifests BEFORE source code.
# This layer is only invalidated when pyproject.toml or uv.lock change,
# not on every source-code edit — keeping rebuilds fast.
COPY pyproject.toml uv.lock ./

# INSTALL_DEV=true installs dev dependency groups (pytest, ruff, mypy …).
# Production builds never set this arg; the default is "false".
ARG INSTALL_DEV=false

# --frozen              : fail-fast if uv.lock is stale (reproducible builds)
# --no-install-project  : install deps only, not the project itself as a pkg
# --mount=type=cache    : reuse the uv download cache across rebuilds
RUN --mount=type=cache,target=/root/.cache/uv \
    if [ "$INSTALL_DEV" = "true" ]; then \
        uv sync --frozen --no-install-project; \
    else \
        uv sync --frozen --no-dev --no-install-project; \
    fi

# =============================================================================
# Stage 2 — runtime: lean, non-root production image
# =============================================================================
FROM python:3.13.5-slim AS runtime

# Python runtime hardening:
#   PYTHONDONTWRITEBYTECODE — skip *.pyc creation (already pre-compiled above)
#   PYTHONUNBUFFERED        — flush stdout/stderr immediately (no log buffering)
#   PYTHONFAULTHANDLER      — dump tracebacks on fatal signals (SIGSEGV etc.)
#   PATH                   — activate the virtual environment from the builder
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    DJANGO_SETTINGS_MODULE=config.settings \
    PATH="/app/.venv/bin:$PATH"

# wget is the smallest available HTTP client; used only for health-check probes
RUN apt-get update \
    && apt-get install -y --no-install-recommends wget \
    && rm -rf /var/lib/apt/lists/*

# Dedicated non-root user — containers should never run as root in production
RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --no-create-home --shell /sbin/nologin app

WORKDIR /app

# Copy the pre-built virtual environment from the builder stage.
# No uv is required at runtime, which keeps the final image leaner.
COPY --from=builder /app/.venv /app/.venv

# Copy application source last — this layer changes most frequently.
# Placing it after the venv copy preserves the venv cache layer on rebuilds.
COPY --chown=app:app . .

# Dedicated directory for the SQLite database file.
# Mounted as a named volume in docker-compose so data persists across
# container recreations without touching the rest of /app.
RUN mkdir -p /data && chown app:app /data

USER app

EXPOSE 8000

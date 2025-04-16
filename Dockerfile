FROM ghcr.io/astral-sh/uv:python12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


FROM python:3.12-slim-bookworm

ARG USERNAME=lee_w

RUN useradd -m $USERNAME
USER $USERNAME
WORKDIR /app

COPY --from=builder --chown=$USERNAME:$USERNAME /app /app

ENV PATH="/app/.venv/bin:$PATH"

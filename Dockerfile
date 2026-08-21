# syntax=docker/dockerfile:1.7
FROM ghcr.io/astral-sh/uv:0.11.31 AS uv

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

RUN addgroup --system amesh && adduser --system --ingroup amesh amesh

WORKDIR /app
COPY --from=uv /uv /uvx /bin/
COPY pyproject.toml uv.lock README.md LICENSE ./
COPY src ./src
COPY migrations ./migrations
COPY scripts/soak_mvp.py ./scripts/soak_mvp.py
RUN uv sync --frozen --no-dev --extra runtime --no-editable

USER 100:101
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"

CMD ["python", "-m", "amesh.server"]

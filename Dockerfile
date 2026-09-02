# syntax=docker/dockerfile:1.7
FROM ghcr.io/astral-sh/uv:0.11.31 AS uv

FROM node:22-bookworm-slim AS web
WORKDIR /web
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/index.html frontend/tsconfig.json frontend/tsconfig.app.json frontend/tsconfig.node.json ./
COPY frontend/vite.config.ts ./
COPY frontend/src ./src
RUN npm run build

WORKDIR /pi
COPY harnesses/pi/package.json harnesses/pi/package-lock.json ./
RUN npm ci --omit=dev
COPY harnesses/pi/src ./src

FROM node:22-bookworm-slim AS model-engine-tools
ENV COPILOT_AUTO_UPDATE=false
WORKDIR /opt/amesh/model-engines
COPY docker/model-engines/package.json docker/model-engines/package-lock.json ./
RUN npm ci --omit=dev --no-audit --no-fund \
    && ./node_modules/.bin/codex --version \
    && ./node_modules/.bin/copilot --version

FROM python:3.12-slim-bookworm AS runtime-base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && addgroup --system amesh \
    && adduser --system --ingroup amesh amesh \
    && install -d -o amesh -g amesh /var/lib/amesh/plugins

WORKDIR /app
COPY --from=uv /uv /uvx /bin/
COPY --from=web /usr/local/bin/node /usr/local/bin/node
COPY pyproject.toml uv.lock README.md LICENSE ./
COPY src ./src
COPY --from=web /web/dist ./src/amesh/web
COPY --from=web /pi ./harnesses/pi
COPY migrations ./migrations
COPY scripts/soak_mvp.py ./scripts/soak_mvp.py
COPY scripts/hardened-entrypoint.sh ./scripts/hardened-entrypoint.sh
RUN chmod 0755 ./scripts/hardened-entrypoint.sh
RUN uv sync --frozen --no-dev --extra runtime --no-editable

USER 100:101
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"

CMD ["python", "-m", "amesh.server"]

FROM runtime-base AS runtime-model-engines
USER root
COPY --from=model-engine-tools /opt/amesh/model-engines /opt/amesh/model-engines
RUN apt-get update \
    && apt-get install -y --no-install-recommends bsdutils \
    && rm -rf /var/lib/apt/lists/* \
    && install -d -m 0700 -o amesh -g amesh /var/lib/amesh/model-engines \
    /var/lib/amesh/model-engines/.runtime-home \
    && /opt/amesh/model-engines/node_modules/.bin/codex --version \
    && /opt/amesh/model-engines/node_modules/.bin/copilot --version
ENV COPILOT_AUTO_UPDATE=false \
    HOME=/var/lib/amesh/model-engines/.runtime-home \
    PATH="/opt/amesh/model-engines/node_modules/.bin:$PATH"
USER 100:101

FROM runtime-base AS runtime

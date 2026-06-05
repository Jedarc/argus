FROM python:3.12-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN addgroup --system app && adduser --system --ingroup app app

COPY src/api/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ── Development ──────────────────────────────────────────────────────────────
FROM base AS development

COPY src/api/ ./api/
COPY docker/api-entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

USER app
EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]

# ── Production ───────────────────────────────────────────────────────────────
FROM base AS production

COPY src/api/ ./api/
COPY docker/api-entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

USER app
EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]

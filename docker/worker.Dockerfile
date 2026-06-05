FROM python:3.12-slim AS base

WORKDIR /app

# Runtime dependencies for CLI modules:
#   - sherlock-project  → pure Python, installed via pip
#   - holehe            → pure Python, installed via pip
#   - subfinder         → Go binary, installed below
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install subfinder binary (projectdiscovery/subfinder)
RUN ARCH=$(dpkg --print-architecture) \
    && curl -sSL "https://github.com/projectdiscovery/subfinder/releases/latest/download/subfinder_linux_${ARCH}.zip" \
       -o /tmp/subfinder.zip \
    && unzip /tmp/subfinder.zip -d /usr/local/bin subfinder \
    && rm /tmp/subfinder.zip \
    && chmod +x /usr/local/bin/subfinder

RUN addgroup --system app && adduser --system --ingroup app app

COPY src/api/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir sherlock-project holehe

# ── Development ──────────────────────────────────────────────────────────────
FROM base AS development

COPY src/api/ ./api/
COPY docker/worker-entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

USER app
ENTRYPOINT ["./entrypoint.sh"]

# ── Production ───────────────────────────────────────────────────────────────
FROM base AS production

COPY src/api/ ./api/
COPY docker/worker-entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

USER app
ENTRYPOINT ["./entrypoint.sh"]

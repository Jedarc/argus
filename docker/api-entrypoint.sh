#!/bin/sh
set -e

echo "[argus] Running database migrations..."
alembic -c api/alembic.ini upgrade head

echo "[argus] Starting API server..."
exec uvicorn api.main:app --host 0.0.0.0 --port 8000

#!/bin/sh
set -e

echo "[argus] Starting Celery worker..."
exec celery -A api.tasks worker --loglevel=info --concurrency=4

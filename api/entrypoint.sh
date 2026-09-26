#!/bin/sh
set -e
alembic upgrade head
python -m app.cli bootstrap
[ "$SEED_EXAMPLES" = "1" ] && python -m app.cli seed || true
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 \
  --workers "${API_WORKERS:-2}" --proxy-headers --forwarded-allow-ips="*"

#!/bin/sh

set -e

echo "========================================"
echo "MedLab Platform - Container Startup"
echo "========================================"

echo "[1/3] Running database migrations..."
alembic upgrade head

echo "[2/3] Initializing database seed..."
python -m app.seed

echo "[3/3] Starting MedLab API..."
exec python -m app.runtime.render
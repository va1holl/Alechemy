#!/bin/bash
# =============================================================================
# Production entrypoint script for Alechemy
# Ensures static files are collected into volume on container start
# =============================================================================

set -e

echo "Starting Alechemy production container..."

# Collect static files into volume (runs every start to ensure volume is populated)
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run database migrations (optional, can be disabled via env var)
if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
    echo "Running database migrations..."
    python manage.py migrate --noinput
fi

# Execute the main command (gunicorn)
echo "Starting Gunicorn..."
exec "$@"

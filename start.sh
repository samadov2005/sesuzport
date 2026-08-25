#!/usr/bin/env bash
set -o errexit

echo "🤖 Starting Telegram Bot in background..."
python bot/main.py &

echo "🌐 Starting Django Gunicorn server on port ${PORT:-8000}..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --threads 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -

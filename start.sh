#!/usr/bin/env bash
set -o errexit

if [ "${USE_WEBHOOK:-false}" = "true" ]; then
    echo "🌐 Webhook mode active — Telegram updates handled by Gunicorn at /bot/webhook/"
else
    echo "🤖 Starting Telegram Bot supervisor in background..."
    (
        while true; do
            echo "🤖 [bot supervisor] Telegram Bot ishga tushirildi..."
            python bot/main.py || true
            echo "⚠️ [bot supervisor] Telegram Bot to'xtadi (crash/restart). 3 soniyada qayta ishga tushadi..."
            sleep 3
        done
    ) &
fi

echo "🌐 Starting Django Gunicorn server on port ${PORT:-8000}..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --threads 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -

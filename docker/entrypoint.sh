#!/bin/sh
# ============================================================
# SESPORT container entrypoint
#
# Bosqichlar (har biri env flag bilan boshqariladi):
#   1. Ma'lumotlar bazasi ko'tarilishini kutish
#   2. RUN_MIGRATIONS=true      -> manage.py migrate
#   3. RUN_COLLECTSTATIC=true   -> manage.py collectstatic
#   4. CREATE_SUPERUSER=true    -> superuser (agar mavjud bo'lmasa)
#   5. exec "$@"  (gunicorn yoki `python -m bot.main`)
#
# Migratsiya faqat `web` servisida yoqiladi — bot bilan bir vaqtda
# ishga tushsa, ikkalasi bir xil migratsiyani parallel bajarib
# race condition hosil qiladi.
# ============================================================
set -e

log() { echo "[entrypoint] $*"; }

# ── 1. DB ni kutish ────────────────────────────────────────
python - <<'PY'
import os, re, socket, sys, time

url = os.environ.get("DATABASE_URL", "")
host = os.environ.get("POSTGRES_HOST", "")
port = os.environ.get("POSTGRES_PORT", "5432")

m = re.match(r"postgres(?:ql)?://[^:/@]+:[^@]*@([^:/]+):(\d+)/", url)
if m:
    host, port = m.group(1), m.group(2)

if not host:
    print("[entrypoint] SQLite rejimi — DB kutish o'tkazib yuborildi")
    sys.exit(0)

port = int(port)
timeout = float(os.environ.get("DB_WAIT_TIMEOUT", "60"))
deadline = time.monotonic() + timeout

while True:
    try:
        with socket.create_connection((host, port), timeout=3):
            print(f"[entrypoint] baza tayyor: {host}:{port}")
            sys.exit(0)
    except OSError as exc:
        if time.monotonic() >= deadline:
            print(f"[entrypoint] XATO: {host}:{port} {timeout:.0f}s ichida javob bermadi ({exc})",
                  file=sys.stderr)
            sys.exit(1)
        time.sleep(1)
PY

# ── 2. Migratsiyalar ───────────────────────────────────────
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
    log "migratsiyalar bajarilmoqda..."
    python manage.py migrate --noinput || true
fi

# ── 2.1 Boshlang'ich ma'lumotlar (Huquqlar, Do'konlar) ──────
if [ "${RUN_SEED:-true}" = "true" ]; then
    log "boshlang'ich huquqlar va do'konlar (seed) kiritilmoqda..."
    python manage.py seed --mode real || true
fi

# ── 3. Static fayllar ──────────────────────────────────────
if [ "${RUN_COLLECTSTATIC:-true}" = "true" ]; then
    log "static fayllar yig'ilmoqda..."
    python manage.py collectstatic --noinput || true
fi

# ── 4. Superuser ───────────────────────────────────────────
if [ "${CREATE_SUPERUSER:-true}" = "true" ]; then
    log "superuser tekshirilmoqda..."
    python - <<'PY' || true
import os
import django

django.setup()
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin").strip()
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "admin123").strip()
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@sesport.uz").strip()

if not username or not password:
    print("[entrypoint] DJANGO_SUPERUSER_USERNAME/PASSWORD berilmagan — o'tkazib yuborildi")
elif User.objects.filter(username=username).exists():
    print(f"[entrypoint] superuser '{username}' allaqachon mavjud")
else:
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"[entrypoint] superuser '{username}' yaratildi (login: {username}, parol: {password})")
PY
fi

# ── 5. Telegram Botni fonda ishga tushirish (agar web rolida bo'lsa) ────────
if [ -n "$BOT_TOKEN" ] && [ "${RUN_BOT:-true}" = "true" ] && [ "$1" = "gunicorn" ]; then
    log "Telegram bot fonda ishga tushirilmoqda..."
    python bot/main.py &
fi

# ── 6. Asosiy jarayon ──────────────────────────────────────
PORT="${PORT:-8000}"
log "Servis porti: $PORT, ishga tushirilmoqda: $*"

if [ "$1" = "gunicorn" ]; then
    exec gunicorn config.wsgi:application \
        --bind "0.0.0.0:${PORT}" \
        --workers "${WEB_CONCURRENCY:-2}" \
        --timeout 120 \
        --graceful-timeout 30 \
        --keep-alive 5 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --forwarded-allow-ips "*" \
        --access-logfile - \
        --error-logfile -
else
    exec "$@"
fi

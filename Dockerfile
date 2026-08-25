# syntax=docker/dockerfile:1
# ============================================================
# SESPORT — Production image (Django admin + Aiogram bot)
# Bitta image, ikkita rol: `web` (gunicorn) va `bot` (polling).
# Rol CMD orqali tanlanadi — docker-compose.yml ga qarang.
# ============================================================

# ------------------------------------------------------------
# Stage 1 — builder: wheel'larni kompilyatsiya qilamiz
# ------------------------------------------------------------
FROM python:3.13-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY requirements.txt .
RUN pip wheel --wheel-dir /wheels -r requirements.txt


# ------------------------------------------------------------
# Stage 2 — runtime: kompilyator yo'q, faqat kerakli kutubxonalar
# ------------------------------------------------------------
FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    WEB_CONCURRENCY=4

# libpq5 — psycopg2 uchun runtime kutubxona; curl — HEALTHCHECK uchun
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Root'siz foydalanuvchi
RUN groupadd --system --gid 1000 app \
    && useradd --system --uid 1000 --gid app --create-home --home-dir /home/app app

WORKDIR /app

COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

# Loyiha kodi (.dockerignore nima kirmasligini belgilaydi)
COPY --chown=app:app . .

# Entrypoint — Windows'da CRLF bo'lib qolishi mumkin, tozalab olamiz
RUN sed -i 's/\r$//' /app/docker/entrypoint.sh \
    && chmod +x /app/docker/entrypoint.sh

# Yozish kerak bo'ladigan kataloglar (volume mount qilinsa ham egasi to'g'ri qoladi)
RUN mkdir -p /app/logs /app/media /app/staticfiles \
    && chown -R app:app /app/logs /app/media /app/staticfiles

USER app

EXPOSE 8000 10000

# /healthz/ SECURE_REDIRECT_EXEMPT ro'yxatida — ENABLE_HTTPS=true bo'lsa ham
# 301 qaytarmaydi. 'localhost' esa production.py da ALLOWED_HOSTS ga doim qo'shiladi.
HEALTHCHECK --interval=30s --timeout=5s --start-period=45s --retries=3 \
    CMD curl -fsS -H "Host: localhost" http://127.0.0.1:${PORT:-8000}/healthz/ >/dev/null || exit 1

ENTRYPOINT ["/app/docker/entrypoint.sh"]

# Standart rol — web. Bot uchun compose'da `command: python -m bot.main`
#
# --workers berilmagan: gunicorn WEB_CONCURRENCY env'ini o'qiydi (yuqorida 4).
# --forwarded-allow-ips="*": 8000 porti host'ga umuman chiqarilmagan
#   (compose'da `expose`, `ports` emas), ya'ni unga faqat nginx yetadi —
#   shuning uchun X-Forwarded-* sarlavhalariga ishonish xavfsiz.
# --max-requests: mumkin bo'lgan xotira oqishlariga qarshi worker'ni
#   davriy ravishda yangilaydi; jitter ularni bir vaqtda qayta ishga
#   tushishidan saqlaydi.
CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--graceful-timeout", "30", \
     "--keep-alive", "5", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "100", \
     "--forwarded-allow-ips", "*", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]

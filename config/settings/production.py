from .base import *  # noqa: F403
import os


def _env_bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in ('1', 'true', 'yes', 'on')


def _env_list(name: str) -> list[str]:
    return [item.strip() for item in os.environ.get(name, '').split(',') if item.strip()]


DEBUG = False

# ----------------------------------------------------------------
# ALLOWED_HOSTS
# localhost/127.0.0.1 doim qo'shiladi — Docker HEALTHCHECK shu Host
# bilan keladi (curl -H "Host: localhost").
# NPM `Host` sarlavhasini o'zgartirmasdan uzatadi, shuning uchun bu
# yerda haqiqiy domen bo'lishi shart.
# ----------------------------------------------------------------
ALLOWED_HOSTS = _env_list('ALLOWED_HOSTS') + ['localhost', '127.0.0.1']

# Admin panelga POST qilish uchun (Django 4+ talabi).
# NPM SSL termination qilgani uchun sxema DOIM https bo'ladi:
#   CSRF_TRUSTED_ORIGINS=https://sesport.uz,https://www.sesport.uz
CSRF_TRUSTED_ORIGINS = _env_list('CSRF_TRUSTED_ORIGINS')

# ----------------------------------------------------------------
# Reverse proxy — Nginx Proxy Manager (NPM) ortida ishlash
#
# NPM o'zining standart proxy shablonida quyidagilarni uzatadi:
#   X-Forwarded-Scheme, X-Forwarded-Proto, X-Forwarded-For, X-Real-IP
# Django originalda so'rov HTTPS bo'lganini X-Forwarded-Proto orqali
# biladi. Bu sarlavhaga ISHONISH faqat shu sababli xavfsiz:
# web:8000 host'ga publish qilinmagan (compose'da `expose`), ya'ni
# unga NPM'dan boshqa hech kim yeta olmaydi.
# ----------------------------------------------------------------
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ----------------------------------------------------------------
# HTTPS
#
# NPM'da domen uchun SSL sertifikat olingandan KEYIN .env da
# ENABLE_HTTPS=true qiling.
#
# Redirect loop bo'lmaydi, chunki:
#   Browser --https--> NPM --http + X-Forwarded-Proto: https--> Django
# Django bu sarlavhani ko'rib so'rovni "xavfsiz" deb hisoblaydi va
# qayta redirect qilmaydi.
#
# TAVSIYA: NPM Proxy Host sozlamalarida "Force SSL" ni YOQING —
# u holda http->https redirect NPM darajasida bo'ladi va Django'ga
# umuman yetib kelmaydi (bitta hop kam).
# ----------------------------------------------------------------
ENABLE_HTTPS = _env_bool('ENABLE_HTTPS', False)

SECURE_SSL_REDIRECT = ENABLE_HTTPS
SESSION_COOKIE_SECURE = ENABLE_HTTPS
CSRF_COOKIE_SECURE = ENABLE_HTTPS
SECURE_HSTS_SECONDS = 31536000 if ENABLE_HTTPS else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = ENABLE_HTTPS
SECURE_HSTS_PRELOAD = ENABLE_HTTPS

# Docker healthcheck konteyner ichida http:// orqali keladi — uni
# https redirectdan ozod qilamiz, aks holda ENABLE_HTTPS=true bo'lganda
# curl 301 oladi va konteyner "unhealthy" bo'lib qoladi.
SECURE_REDIRECT_EXEMPT = [r'^healthz/?$', r'^health/?$']

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'

X_FRAME_OPTIONS = 'DENY'

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 60 * 60 * 8  # admin sessiyasi — 8 soat

CSRF_COOKIE_HTTPONLY = False  # Django admin JS uchun o'qilishi kerak
CSRF_COOKIE_SAMESITE = 'Lax'

# Yuklamalar hajmi.
# NPM'da mos sozlama: Proxy Host -> Advanced -> client_max_body_size 20m
DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

# ----------------------------------------------------------------
# Static fayllar — WhiteNoise
#
# Loyihada nginx servisi yo'q, shuning uchun /static/ ni to'liq
# WhiteNoise beradi (gunicorn ichida). NPM tomonida static uchun
# alohida konfiguratsiya QILISH SHART EMAS.
# ----------------------------------------------------------------
_WHITENOISE = 'whitenoise.middleware.WhiteNoiseMiddleware'
if _WHITENOISE not in MIDDLEWARE:  # noqa: F405
    MIDDLEWARE.insert(  # noqa: F405
        MIDDLEWARE.index('django.middleware.security.SecurityMiddleware') + 1,  # noqa: F405
        _WHITENOISE,
    )

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        # Manifest'siz variant: shablonda yo'q faylga havola bo'lsa ham
        # collectstatic yiqilmaydi.
        'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
    },
}

# ----------------------------------------------------------------
# Media (foydalanuvchi yuklaydigan fayllar)
#
# HOZIRGI HOLAT: loyihada birorta ham FileField/ImageField yo'q —
# shikoyat rasm/ovozlari Telegram tomonida `file_id` sifatida
# saqlanadi (apps/complaints/models.py: photo_file_id).
# Ya'ni /media/ hozircha ISHLATILMAYDI va shu sababli o'chirilgan.
#
# Kelajakda FileField qo'shsangiz, quyidagini .env da yoqing:
#   SERVE_MEDIA_FILES=true
# Bu Django'ning o'zi orqali /media/ ni beradi (config/urls.py),
# xavfsiz sarlavhalar bilan. Katta yuklama uchun esa NPM'da
# alohida "Custom location" sozlagan ma'qul — pastdagi README ga qarang.
# ----------------------------------------------------------------
SERVE_MEDIA_FILES = _env_bool('SERVE_MEDIA_FILES', False)

# ----------------------------------------------------------------
# Bot FSM storage
# ----------------------------------------------------------------
BOT_FSM_STORAGE = 'redis'
BOT_REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/1')

# ----------------------------------------------------------------
# Logging
# Konsol (docker logs / json-file driver) + aylanuvchi fayl (logs_volume).
# `docker logs` va persistent fayl — ikkalasi ham ishlaydi.
# ----------------------------------------------------------------
_LOG_DIR = BASE_DIR / 'logs'  # noqa: F405
try:
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    _LOG_FILE_OK = os.access(_LOG_DIR, os.W_OK)
except OSError:
    _LOG_FILE_OK = False

if _LOG_FILE_OK:
    LOGGING['handlers']['file'] = {  # noqa: F405
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': str(_LOG_DIR / 'sesport.log'),
        'maxBytes': 10 * 1024 * 1024,
        'backupCount': 5,
        'formatter': 'verbose',
        'encoding': 'utf-8',
    }
    for _logger in (LOGGING['root'], *LOGGING['loggers'].values()):  # noqa: F405
        if 'file' not in _logger['handlers']:
            _logger['handlers'].append('file')

# Har bir so'rovdagi 4xx/5xx serverda ko'rinsin
LOGGING['loggers']['django.request'] = {  # noqa: F405
    'handlers': ['console'] + (['file'] if _LOG_FILE_OK else []),
    'level': 'WARNING',
    'propagate': False,
}
# DIQQAT: django.db.backends ataylab DEBUG darajaga qo'yilmagan —
# u SQL parametrlarini (parollar, tokenlar) logga chiqarib yuboradi.

# ----------------------------------------------------------------
# SECRET_KEY production'da majburiy
# ----------------------------------------------------------------
SECRET_KEY = os.environ.get('SECRET_KEY', '')  # noqa: F811
if not SECRET_KEY or SECRET_KEY.startswith(('dev-unsafe', 'your-')):
    raise RuntimeError(
        "SECRET_KEY .env faylida belgilanishi shart (shablon qiymat qabul "
        "qilinmaydi). Yangi kalit yaratish:\n"
        '  python -c "from django.core.management.utils import get_random_secret_key;'
        ' print(get_random_secret_key())"'
    )

# ----------------------------------------------------------------
# Production'da SQLite QAT'IYAN mumkin emas
#
# DATABASE_URL berilmasa base.py SQLite'ga o'tadi. Konteynerda bu
# jimgina "ishlaydi", lekin baza image ichidagi vaqtinchalik qatlamda
# qoladi va HAR BIR `docker compose up --build` da butun ma'lumot
# yo'qoladi. Shuning uchun bu yerda qattiq to'xtatamiz.
# ----------------------------------------------------------------
if 'sqlite' in DATABASES['default']['ENGINE']:  # noqa: F405
    raise RuntimeError(
        "Production sozlamalarida SQLite aniqlandi — bu ruxsat etilmaydi.\n"
        "Sabab: .env faylida DATABASE_URL yo'q yoki bo'sh.\n"
        "Yechim — .env ga qo'shing:\n"
        "  DATABASE_URL=postgresql://<user>:<parol>@db:5432/<baza>\n"
        "(parolda @ : / # bo'lsa percent-encode qiling, masalan @ -> %40)"
    )

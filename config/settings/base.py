import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-unsafe-secret-key-change-in-production-xyz123')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'apps.users',
    'apps.complaints',
    'apps.stores',
    'apps.cashback',
    'apps.rights',
    'apps.support',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# ----------------------------------------------------------------
# DATABASE — SQLite by default (change to PostgreSQL in production)
# ----------------------------------------------------------------
_db_url = os.environ.get('DATABASE_URL', '').strip()

if _db_url:
    # PostgreSQL (production): psycopg2-binary talab qilinadi.
    #
    # Bu yerda ataylab regex emas, urllib.parse ishlatilgan:
    # regex `@` yoki `/` belgisi bo'lgan parollarni va `postgres://`
    # sxemasini tanimay qolardi va natijada konteyner JIMGINA SQLite'ga
    # tushib ketardi — ya'ni har bir deploy'da ma'lumotlar yo'qolardi.
    # Endi noto'g'ri URL jim qolmasdan, xato bilan to'xtatadi.
    from urllib.parse import urlparse, unquote

    _parsed = urlparse(_db_url)

    if _parsed.scheme not in ('postgres', 'postgresql'):
        raise ValueError(
            f"DATABASE_URL sxemasi qo'llab-quvvatlanmaydi: '{_parsed.scheme}'. "
            "Kutilgan format: postgresql://user:password@host:5432/dbname "
            "(SQLite uchun DATABASE_URL ni umuman bermang)."
        )
    if not _parsed.hostname or not _parsed.path.lstrip('/'):
        raise ValueError(
            "DATABASE_URL noto'g'ri: host yoki baza nomi topilmadi. "
            "Format: postgresql://user:password@host:5432/dbname"
        )

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': _parsed.path.lstrip('/'),
            # Parolda @ : / # kabi belgilar bo'lsa, ular URL'da
            # %40, %3A ... ko'rinishida yoziladi — unquote ochib beradi.
            'USER': unquote(_parsed.username or ''),
            'PASSWORD': unquote(_parsed.password or ''),
            'HOST': _parsed.hostname,
            'PORT': str(_parsed.port or 5432),
            'CONN_MAX_AGE': 600,
            'CONN_HEALTH_CHECKS': True,
            'OPTIONS': {'connect_timeout': 10},
        }
    }
elif os.environ.get('POSTGRES_HOST', '').strip():
    # DATABASE_URL berilmagan, lekin alohida POSTGRES_* o'zgaruvchilari bor.
    #
    # Bu yo'l AFZAL: bu yerda percent-encoding umuman kerak emas, ya'ni
    # parolda @ : / # bo'lsa ham hech narsani kodlash shart emas.
    # DATABASE_URL ishlatilganda esa POSTGRES_PASSWORD (xom) va URL
    # ichidagi parol (kodlangan) bir-biriga mos kelmay qolishi mumkin —
    # bu "password authentication failed" xatosining eng keng tarqalgan sababi.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB', ''),
            'USER': os.environ.get('POSTGRES_USER', ''),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
            'HOST': os.environ['POSTGRES_HOST'].strip(),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
            'CONN_MAX_AGE': 600,
            'CONN_HEALTH_CHECKS': True,
            'OPTIONS': {'connect_timeout': 10},
        }
    }
else:
    # SQLite (development default)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.environ.get('LOG_LEVEL', 'INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'bot': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

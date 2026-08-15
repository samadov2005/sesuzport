from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000

BOT_FSM_STORAGE = 'redis'
BOT_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

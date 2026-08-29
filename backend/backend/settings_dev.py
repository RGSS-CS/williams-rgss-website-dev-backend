import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent # this is specifically only for use in this file

SECRET_KEY = 'django-insecure-s7!$t5-_^uy$6%8v^-rw!ndwr19-@pht1f1yw#2n&k*a62@+=n'
DEBUG = True
ALLOWED_HOSTS = ["localhost","127.0.0.1"]
CSRF_TRUSTED_ORIGINS = ["http://localhost:8000","http://127.0.0.1:8000"]
CSRF_COOKIE_SECURE = False

SIGNING_KEY = '2f27a65af8d54ca5a4ae0b7a0db2f4dc85ad9e4b4659ce9ec6dcdf95a95f36eb'
FRONTEND_REVALIDATE_URL = 'http://localhost:3000/api/revalidate'
REVALIDATE_SECRET = 'dev-insecure-revalidate-secret'
CAPTCHA_VERIFY_URL = 'https://(url)/siteverify'
CAP_SECRET = ''

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3'
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING"
    }
}

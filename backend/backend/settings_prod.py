from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent # this is specifically only for use in this file

SECRET_KEY = os.environ.get("SECRET_KEY", "build-fallback-secret-key")
DEBUG = os.environ.get("DEBUG", "False")
ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h.strip()
]
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()
]
CSRF_COOKIE_SECURE = True

# TLS is terminated by the reverse proxy before traffic reaches Django.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SIGNING_KEY = os.environ.get("SIGNING_KEY", "build-fallback-signing-key")

FRONTEND_REVALIDATE_URL = os.environ.get("REVALIDATE_URL", "")
REVALIDATE_SECRET = os.environ.get("REVALIDATE_SECRET", "")
CAPTCHA_VERIFY_URL = os.environ.get("CAPTCHA_VERIFY_URL", "")
CAP_SECRET = os.environ.get("CAP_SECRET", "")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get("POSTGRES_DB"),
        'USER': os.environ.get("POSTGRES_USER"),
        'PASSWORD': os.environ.get("POSTGRES_PASSWORD"),
        'HOST': os.environ.get("DB_HOST", "db"),
        'PORT': os.environ.get("DB_PORT", "5432")
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
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False
        }
    }
}

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent # this is specifically only for use in this file

SECRET_KEY = 'django-insecure-s7!$t5-_^uy$6%8v^-rw!ndwr19-@pht1f1yw#2n&k*a62@+=n'
DEBUG = True
ALLOWED_HOSTS = ["localhost"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

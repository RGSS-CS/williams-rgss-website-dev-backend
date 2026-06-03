#!/bin/sh
set -e

echo "==> Running migrations..."
python manage.py migrate --no-input

echo "==> Collecting static files..."
python manage.py collectstatic --no-input --clear

echo "==> Creating superuser if not exists..."
python manage.py shell << 'EOF'
import os
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
email    = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
if not username or not password:
    print("WARNING: DJANGO_SUPERUSER_USERNAME or DJANGO_SUPERUSER_PASSWORD not set, skipping.")
elif User.objects.filter(username=username).exists():
    print(f"Superuser '{username}' already exists, skipping.")
else:
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created.")
EOF

echo "==> Running deployment checks..."
python manage.py check --deploy

echo "==> Starting gunicorn..."
exec gunicorn backend.wsgi:application --bind 0.0.0.0:8000 --workers 3
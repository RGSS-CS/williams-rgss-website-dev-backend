#!/bin/sh
set -e

echo "==> Running migrations..."
python manage.py migrate --no-input

echo "==> Creating/updating superuser..."
python manage.py shell << 'EOF'
import os
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
email    = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
if not username or not password:
    print("WARNING: DJANGO_SUPERUSER_USERNAME or DJANGO_SUPERUSER_PASSWORD not set, skipping.")
else:
    user, created = User.objects.update_or_create(
        username=username,
        defaults={"email": email, "is_staff": True, "is_superuser": True},
    )
    user.set_password(password)
    user.save()
    print(f"Superuser '{username}' {'created' if created else 'updated'}.")
EOF


echo "==> Starting gunicorn..."
exec gunicorn backend.wsgi:application --bind 0.0.0.0:8000 --workers 3
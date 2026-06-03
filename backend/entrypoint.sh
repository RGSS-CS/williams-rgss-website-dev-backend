#!/bin/sh
set -e

echo "==> Running migrations..."
python manage.py migrate --no-input

echo "==> Collecting static files..."
python manage.py collectstatic --no-input --clear

python manage.py runserver

echo "==> Container started successfully!"

echo "==> Creating superuser if it doesn't exist..."
python manage.py createsuperuser --no-input || true
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/app

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN addgroup --system app && \
    adduser --system --ingroup app --home /app app && \
    chown -R app:app /app

COPY --chown=app:app backend/ .
COPY --chown=root:root backend/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN cp backend/settings_prod.py backend/settings_local.py
# Build-time-only placeholders so settings_prod.py can be imported by collectstatic.
# Set inline (not ARG/ENV) so they are not baked into the image; real values come from .env at runtime.
RUN ALLOWED_HOSTS=build.invalid \
    CSRF_TRUSTED_ORIGINS=https://build.invalid \
    SECRET_KEY=build-only-placeholder \
    SIGNING_KEY=build-only-placeholder \
    python manage.py collectstatic --noinput
RUN chown -R app:app /app/staticfiles
USER app

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
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
RUN python manage.py collectstatic --noinput

USER app

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

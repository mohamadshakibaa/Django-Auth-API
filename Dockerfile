FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HOME=/home/app

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && addgroup --system app \
    && adduser --system --ingroup app --home /home/app --disabled-login app \
    && mkdir -p /home/app \
    && chown app:app /home/app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# SECRET_KEY here is only used so collectstatic can import settings at build time.
RUN SECRET_KEY=build-only-secret-key python manage.py collectstatic --noinput \
    && mkdir -p /app/media \
    && chown -R app:app /app/media /app/staticfiles

USER app

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-10000} --workers 3 --timeout 60"]

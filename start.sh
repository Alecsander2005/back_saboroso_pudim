#!/bin/sh
set -eu

python manage.py migrate --noinput
python manage.py ensure_admin
python manage.py collectstatic --noinput

exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${WEB_CONCURRENCY:-2}" \
    --access-logfile -

#!/bin/sh

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Applying migrations..."
python manage.py migrate --noinput || {
  echo "Migrations failed. Exiting..."
  exit 1
}

echo "Starting supervisord..."
exec supervisord -c /etc/supervisor/conf.d/supervisord.conf
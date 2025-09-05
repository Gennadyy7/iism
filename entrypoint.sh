#!/bin/sh

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting supervisord..."
exec supervisord -c /etc/supervisor/conf.d/supervisord.conf
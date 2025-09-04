#!/bin/sh

echo "Starting supervisord..."
exec supervisord -c /etc/supervisor/conf.d/supervisord.conf
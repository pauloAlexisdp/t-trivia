#!/bin/sh

echo "Running migrations..."
python manage.py migrate --noinput

echo "Seeding database..."
python manage.py seed

echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8000

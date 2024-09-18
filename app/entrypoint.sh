#!/bin/sh

# Wait for the database to be ready
echo "Waiting for the database to be ready..."
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 1
done
echo "Database is ready!"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run the command passed to the entrypoint
exec "$@"
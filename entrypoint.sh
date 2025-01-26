#!/bin/bash

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
while ! nc -z ${DB_HOST:-db} ${DB_PORT:-5432}; do
    sleep 1
done
echo "PostgreSQL is up"

# Wait for Redis
echo "Waiting for Redis..."
while ! nc -z ${REDIS_HOST:-redis} ${REDIS_PORT:-6379}; do
    sleep 1
done
echo "Redis is up"

# Initialize database
echo "Initializing database..."
# Remove existing migrations
rm -rf migrations/
# Initialize migrations
flask db init
# Create initial migration
flask db migrate -m "Initial migration"
# Apply migration
flask db upgrade

# Start application based on container role
if [ "${CONTAINER_ROLE:-web}" = "web" ]; then
    echo "Starting web server..."
    gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 "app:create_app()"
elif [ "${CONTAINER_ROLE}" = "celery" ]; then
    echo "Starting Celery worker..."
    celery -A app.celery worker --loglevel=info
else
    echo "Unknown container role: ${CONTAINER_ROLE}"
    exit 1
fi
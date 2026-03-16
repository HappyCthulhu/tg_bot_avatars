#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
while ! nc -z "${POSTGRES_HOST:-postgres}" "${POSTGRES_PORT:-5432}"; do
  sleep 0.2
done
echo "PostgreSQL started"

echo "Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 0.2
done
echo "Redis started"

echo "Starting bot..."
exec "$@"

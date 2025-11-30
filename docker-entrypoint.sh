#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
while ! nc -z postgres 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

VENV_PYTHON="/app/.venv/bin/python"

echo "Running migrations..."
"${VENV_PYTHON}" manage.py migrate --noinput

echo "Collecting static files..."
"${VENV_PYTHON}" manage.py collectstatic --noinput || true

if [ -n "${ADMIN_LOGIN}" ] && [ -n "${ADMIN_EMAIL}" ] && [ -n "${ADMIN_PASSWORD}" ]; then
    echo "Creating superuser..."
    "${VENV_PYTHON}" manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email="${ADMIN_EMAIL}").exists():
    User.objects.create_superuser("${ADMIN_EMAIL}", "${ADMIN_PASSWORD}")
    print("Superuser '${ADMIN_LOGIN}' created successfully")
else:
    print("Superuser '${ADMIN_LOGIN}' already exists")
EOF
else
    echo "Skipping superuser creation (ADMIN_LOGIN, ADMIN_EMAIL, ADMIN_PASSWORD not set)"
fi

echo "Starting server..."
exec "$@"


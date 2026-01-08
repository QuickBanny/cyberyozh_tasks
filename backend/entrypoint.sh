#!/bin/sh

# Ожидание готовности базы данных
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 1
done
echo "PostgreSQL started"

# Выполнение миграций
echo "Running migrations..."
python manage.py migrate --settings=config.settings.docker

# Сбор статических файлов
echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=config.settings.docker

# Создание суперпользователя (опционально)
echo "Creating superuser..."
python manage.py shell --settings=config.settings.docker << 'EOF'
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
EOF

# Запуск сервера
echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000 --settings=config.settings.docker

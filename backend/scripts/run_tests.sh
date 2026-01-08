#!/bin/bash

# Скрипт для запуска тестов в Docker контейнере

set -e

echo "🧪 Запуск тестов в Docker контейнере..."

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Функция для вывода цветного текста
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверяем, что Docker Compose доступен
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose не найден. Установите Docker Compose."
    exit 1
fi

# Проверяем, что контейнеры запущены
if ! docker-compose ps | grep -q "backend.*Up"; then
    print_warning "Backend контейнер не запущен. Запускаем..."
    docker-compose up -d

    # Ждем, пока контейнер полностью запустится
    print_status "Ожидание запуска контейнера..."
    sleep 10
fi

# Определяем тип тестов для запуска
TEST_TYPE=${1:-"all"}

case $TEST_TYPE in
    "unit"|"services")
        print_status "Запуск unit тестов сервисного слоя..."
        docker-compose exec backend pytest apps/tasks/tests/test_services.py -v
        ;;
    "e2e"|"endpoints")
        print_status "Запуск E2E тестов API endpoints..."
        docker-compose exec backend pytest apps/tasks/tests/test_endpoints.py -v
        ;;
    "adapters")
        print_status "Запуск тестов адаптеров..."
        docker-compose exec backend pytest apps/tasks/tests/test_adapters.py -v
        ;;
    "repositories"|"repo")
        print_status "Запуск тестов репозиториев..."
        docker-compose exec backend pytest apps/tasks/tests/test_repositories.py -v
        ;;
    "coverage"|"cov")
        print_status "Запуск тестов с покрытием кода..."
        docker-compose exec backend pytest --cov=apps.tasks --cov-report=html --cov-report=term-missing
        print_status "Отчет о покрытии сохранен в htmlcov/"
        ;;
    "fast")
        print_status "Запуск быстрых тестов (только unit)..."
        docker-compose exec backend pytest apps/tasks/tests/test_services.py apps/tasks/tests/test_adapters.py -v
        ;;
    "all"|*)
        print_status "Запуск всех тестов..."
        docker-compose exec backend pytest apps/tasks/tests/ -v
        ;;
esac

# Проверяем код выхода
if [ $? -eq 0 ]; then
    print_status "✅ Все тесты прошли успешно!"
else
    print_error "❌ Некоторые тесты провалились!"
    exit 1
fi

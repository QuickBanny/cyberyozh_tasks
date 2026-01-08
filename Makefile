# Makefile для управления проектом CyberYozh

.PHONY: help build up down restart logs shell test test-unit test-e2e test-coverage clean

# Цвета для вывода
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

help: ## Показать справку по командам
	@echo "$(GREEN)Доступные команды:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

build: ## Собрать Docker образы
	@echo "$(GREEN)Сборка Docker образов...$(NC)"
	docker-compose build

up: ## Запустить все сервисы
	@echo "$(GREEN)Запуск сервисов...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✅ Сервисы запущены!$(NC)"
	@echo "Backend: http://localhost:8000"
	@echo "Admin: http://localhost:8000/admin (admin/admin123)"

down: ## Остановить все сервисы
	@echo "$(YELLOW)Остановка сервисов...$(NC)"
	docker-compose down

restart: down up ## Перезапустить все сервисы

logs: ## Показать логи всех сервисов
	docker-compose logs -f

logs-backend: ## Показать логи backend сервиса
	docker-compose logs -f backend

logs-db: ## Показать логи базы данных
	docker-compose logs -f db

shell: ## Открыть shell в backend контейнере
	docker-compose exec backend bash

django-shell: ## Открыть Django shell
	docker-compose exec backend python manage.py shell

migrate: ## Выполнить миграции
	@echo "$(GREEN)Выполнение миграций...$(NC)"
	docker-compose exec backend python manage.py migrate --settings=config.settings.docker

makemigrations: ## Создать миграции
	@echo "$(GREEN)Создание миграций...$(NC)"
	docker-compose exec backend python manage.py makemigrations --settings=config.settings.docker

superuser: ## Создать суперпользователя
	docker-compose exec backend python manage.py createsuperuser --settings=config.settings.docker

collectstatic: ## Собрать статические файлы
	docker-compose exec backend python manage.py collectstatic --noinput --settings=config.settings.docker

# Команды для pre-commit (локальные)
pre-commit-install: ## Установить pre-commit hooks локально
	@echo "$(GREEN)Установка pre-commit hooks...$(NC)"
	@echo "$(YELLOW)Убедитесь что pre-commit установлен: pip install pre-commit$(NC)"
	pre-commit install

pre-commit-run: ## Запустить pre-commit на всех файлах
	@echo "$(GREEN)Запуск pre-commit на всех файлах...$(NC)"
	pre-commit run --all-files

pre-commit-update: ## Обновить pre-commit hooks
	@echo "$(GREEN)Обновление pre-commit hooks...$(NC)"
	pre-commit autoupdate

# Команды для тестирования
test: ## Запустить все тесты
	@echo "$(GREEN)Запуск всех тестов...$(NC)"
	docker-compose exec backend python manage.py test apps.users.tests apps.tasks.tests --verbosity=2

test-unit: ## Запустить unit тесты сервисов
	@echo "$(GREEN)Запуск unit тестов...$(NC)"
	docker-compose exec backend pytest apps/tasks/tests/test_services.py apps/users/tests/test_services.py -v

test-e2e: ## Запустить E2E тесты API
	@echo "$(GREEN)Запуск E2E тестов...$(NC)"
	docker-compose exec backend pytest apps/tasks/tests/test_endpoints.py -v

test-repositories: ## Запустить тесты репозиториев
	@echo "$(GREEN)Запуск тестов репозиториев...$(NC)"
	docker-compose exec backend pytest apps/tasks/tests/test_repositories.py apps/users/tests/test_repositories.py -v

test-auth: ## Запустить тесты аутентификации
	@echo "$(GREEN)Запуск тестов аутентификации...$(NC)"
	docker-compose exec backend python manage.py test apps.users.tests.test_auth --verbosity=2

test-users: ## Запустить все тесты пользователей
	@echo "$(GREEN)Запуск тестов пользователей...$(NC)"
	docker-compose exec backend python manage.py test apps.users.tests --verbosity=2

test-tasks: ## Запустить все тесты задач
	@echo "$(GREEN)Запуск тестов задач...$(NC)"
	docker-compose exec backend python manage.py test apps.tasks.tests --verbosity=2

test-domain: ## Запустить тесты доменных сущностей
	@echo "$(GREEN)Запуск тестов доменных сущностей...$(NC)"
	docker-compose exec backend pytest apps/users/tests/test_domain_entities.py -v

test-coverage: ## Запустить тесты с покрытием кода
	@echo "$(GREEN)Запуск тестов с покрытием...$(NC)"
	docker-compose exec backend pytest --cov=apps.tasks --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)Отчет о покрытии сохранен в htmlcov/$(NC)"

test-fast: ## Запустить быстрые тесты (unit + adapters)
	@echo "$(GREEN)Запуск быстрых тестов...$(NC)"
	docker-compose exec backend pytest apps/tasks/tests/test_services.py apps/tasks/tests/test_adapters.py -v

test-watch: ## Запустить тесты в режиме наблюдения
	@echo "$(GREEN)Запуск тестов в режиме наблюдения...$(NC)"
	docker-compose exec backend pytest-watch apps/tasks/tests/

# Команды для разработки
install-dev: ## Установить зависимости для разработки
	docker-compose exec backend pip install pytest-cov pytest-django pytest-watch

lint: ## Проверить код линтером
	docker-compose exec backend flake8 apps/

format: ## Отформатировать код
	docker-compose exec backend black apps/

# Команды для очистки
clean: ## Очистить Docker ресурсы
	@echo "$(YELLOW)Очистка Docker ресурсов...$(NC)"
	docker-compose down -v
	docker system prune -f

clean-all: ## Полная очистка (включая образы)
	@echo "$(RED)Полная очистка Docker ресурсов...$(NC)"
	docker-compose down -v --rmi all
	docker system prune -af

# Команды для бэкапа
backup-db: ## Создать бэкап базы данных
	@echo "$(GREEN)Создание бэкапа базы данных...$(NC)"
	docker-compose exec db pg_dump -U postgres cyberyozh > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore-db: ## Восстановить базу данных из бэкапа (указать файл: make restore-db FILE=backup.sql)
	@echo "$(GREEN)Восстановление базы данных...$(NC)"
	docker-compose exec -T db psql -U postgres cyberyozh < $(FILE)

# Команды для мониторинга
status: ## Показать статус сервисов
	docker-compose ps

stats: ## Показать статистику использования ресурсов
	docker stats

# Команды для API
api-docs: ## Открыть документацию API
	@echo "$(GREEN)Документация API доступна по адресу:$(NC)"
	@echo "http://localhost:8000/api/v1/"

api-test: ## Протестировать API endpoints
	@echo "$(GREEN)Тестирование API...$(NC)"
	curl -X GET http://localhost:8000/api/v1/tasks/ -H "Content-Type: application/json"

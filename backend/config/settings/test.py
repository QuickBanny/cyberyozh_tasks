"""
Настройки Django для тестирования.
"""

from .base import *  # noqa: F403

# Используем SQLite в памяти для быстрых тестов
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}


# Отключаем миграции для ускорения тестов
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Отключаем логирование во время тестов
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "root": {
        "handlers": ["null"],
    },
}

# Отключаем кеширование
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Простой хешер паролей для ускорения тестов
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Отключаем CSRF для API тестов
REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = [  # noqa: F405
    "rest_framework.authentication.SessionAuthentication",
]

# Отключаем пагинацию для простоты тестирования
REST_FRAMEWORK["PAGE_SIZE"] = None  # noqa: F405

# Отключаем статические файлы
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Отключаем отправку email
EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"

# Секретный ключ для тестов
SECRET_KEY = "test-secret-key-not-for-production"

# Отключаем DEBUG для более реалистичных тестов
DEBUG = False

# Разрешаем все хосты для тестов
ALLOWED_HOSTS = ["*"]

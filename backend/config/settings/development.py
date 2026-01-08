"""
Настройки для разработки.
"""

from .base import *  # noqa: F403

DEBUG = True

# Дополнительные приложения для разработки
INSTALLED_APPS += [  # noqa: F405
    "django_extensions",
]

# Настройки для разработки
INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

# Логирование для разработки
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}

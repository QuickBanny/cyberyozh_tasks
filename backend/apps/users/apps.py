"""
Конфигурация приложения аутентификации.
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Конфигурация приложения аутентификации."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"
    verbose_name = "Пользователи"

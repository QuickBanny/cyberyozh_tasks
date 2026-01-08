"""
Административный интерфейс для приложения tasks.
Импорт админки из infrastructure слоя.
"""

from .infrastructure.admin import TaskAdmin, TaskCommentAdmin  # noqa: F401

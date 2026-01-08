"""
Модели приложения tasks.
Импорт Django моделей из infrastructure слоя для совместимости с Django.
"""

from .infrastructure.models import TaskCommentModel as TaskComment  # noqa: F401
from .infrastructure.models import TaskModel as Task  # noqa: F401

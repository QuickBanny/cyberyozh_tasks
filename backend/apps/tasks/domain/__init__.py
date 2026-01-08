"""
Domain слой для управления задачами.
Содержит бизнес-логику и интерфейсы, независимые от внешних фреймворков.
"""

from .entities import Task, TaskComment, TaskStatus
from .interfaces import CommentRepositoryInterface, TaskRepositoryInterface

__all__ = [
    "Task",
    "TaskComment",
    "TaskStatus",
    "TaskRepositoryInterface",
    "CommentRepositoryInterface",
]

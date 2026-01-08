"""
Интерфейсы репозиториев для domain слоя.
Определяют контракты для работы с данными без привязки к конкретной реализации.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from apps.users.domain.entities import UserId

from .entities import Task, TaskComment


class TaskRepositoryInterface(ABC):
    """Интерфейс репозитория для работы с задачами."""

    @abstractmethod
    def get_by_id(self, task_id: int) -> Optional[Task]:
        """Получить задачу по ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[Task]:
        """Получить все задачи."""
        pass

    @abstractmethod
    def get_by_user(self, user_id: int) -> List[Task]:
        """Получить задачи пользователя."""
        pass

    @abstractmethod
    def get_assigned_to_user(self, user_id: int) -> List[Task]:
        """Получить задачи, назначенные пользователю."""
        pass

    @abstractmethod
    def get_created_by_user(self, user_id: int) -> List[Task]:
        """Получить задачи, созданные пользователем."""
        pass

    @abstractmethod
    def save(self, task: Task) -> Task:
        """Сохранить задачу."""
        pass

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        """Удалить задачу."""
        pass


class UserRepositoryInterface(ABC):
    """Интерфейс репозитория для работы с пользователями."""

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[UserId]:
        """Получить пользователя по ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[UserId]:
        """Получить всех пользователей."""
        pass


class CommentRepositoryInterface(ABC):
    """Интерфейс репозитория для работы с комментариями."""

    @abstractmethod
    def get_by_task_id(self, task_id: int) -> List[TaskComment]:
        """Получить комментарии к задаче."""
        pass

    @abstractmethod
    def save(self, comment: TaskComment) -> TaskComment:
        """Сохранить комментарий."""
        pass

    @abstractmethod
    def delete(self, comment_id: int) -> bool:
        """Удалить комментарий."""
        pass

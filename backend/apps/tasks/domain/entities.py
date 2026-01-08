"""
Модели домена для управления задачами.
Независимые от фреймворка бизнес-сущности.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional

from apps.users.domain.entities import User
from django.utils import timezone


class TaskStatus(Enum):
    """Статусы задач."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class TaskComment:
    """Доменная модель комментария к задаче."""

    id: Optional[int]
    content: str
    author: User
    task_id: int
    created_at: datetime

    def __str__(self) -> str:
        return f"Комментарий к задаче {self.task_id} от {self.author.username}"


@dataclass
class Task:
    """Доменная модель задачи."""

    id: Optional[int]
    title: str
    description: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    assigned_to: Optional[User]
    created_by: User
    comments: List[TaskComment]

    def __post_init__(self):
        """Инициализация после создания объекта."""
        if self.comments is None:
            self.comments = []

    def __str__(self) -> str:
        return self.title

    def add_comment(self, comment: TaskComment) -> None:
        """Добавляет комментарий к задаче."""
        self.comments.append(comment)

    def update_status(self, new_status: TaskStatus) -> None:
        """Обновляет статус задачи."""
        self.status = new_status
        self.updated_at = timezone.now()

    def assign_to_user(self, user: Optional[User]) -> None:
        """Назначает задачу пользователю."""
        self.assigned_to = user
        self.updated_at = timezone.now()

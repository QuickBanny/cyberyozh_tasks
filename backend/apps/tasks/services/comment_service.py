"""
Сервисный слой для бизнес-логики.
Содержит сервисы для управления комментариями.
"""

from typing import List

from apps.tasks.domain.entities import TaskComment
from apps.tasks.domain.interfaces import (
    CommentRepositoryInterface,
    TaskRepositoryInterface,
    UserRepositoryInterface,
)
from django.utils import timezone


class CommentService:
    """Сервис для управления комментариями."""

    def __init__(
        self,
        comment_repo: CommentRepositoryInterface,
        task_repo: TaskRepositoryInterface,
        user_repo: UserRepositoryInterface,
    ):
        self.comment_repo = comment_repo
        self.task_repo = task_repo
        self.user_repo = user_repo

    def get_task_comments(self, task_id: int) -> List[TaskComment]:
        """Получить комментарии к задаче."""
        return self.comment_repo.get_by_task_id(task_id)

    def create_comment(self, task_id: int, content: str, author_id: int) -> TaskComment:
        """Создать комментарий к задаче."""
        # Проверяем существование задачи
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ValueError(f"Задача с ID {task_id} не найдена")

        # Проверяем существование автора
        author = self.user_repo.get_by_id(author_id)
        if not author:
            raise ValueError(f"Пользователь с ID {author_id} не найден")

        # Создаем комментарий
        comment = TaskComment(
            id=None,
            content=content,
            author=author,
            task_id=task_id,
            created_at=timezone.now(),
        )

        return self.comment_repo.save(comment)

    def delete_comment(self, comment_id: int) -> bool:
        """Удалить комментарий."""
        return self.comment_repo.delete(comment_id)

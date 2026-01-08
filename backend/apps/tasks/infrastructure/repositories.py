"""
Репозитории для работы с данными.
Реализация интерфейсов репозиториев из domain слоя.
"""

from typing import List, Optional

from apps.tasks.domain.entities import Task, TaskComment, TaskStatus
from apps.tasks.domain.interfaces import (
    CommentRepositoryInterface,
    TaskRepositoryInterface,
)
from apps.users.domain.entities import User
from django.db import models

from .models import TaskCommentModel, TaskModel


class DjangoTaskRepository(TaskRepositoryInterface):
    """Репозиторий для работы с задачами через Django ORM."""

    def _to_domain(self, task_model: TaskModel) -> Task:
        # Преобразуем комментарии с полными данными пользователей
        comments = []
        for comment in task_model.comments.all():
            author = User(
                id=comment.author.id,
                username=comment.author.username,
                first_name=comment.author.first_name,
                last_name=comment.author.last_name,
                email=comment.author.email,
            )
            comments.append(
                TaskComment(
                    id=comment.id,
                    content=comment.content,
                    author=author,
                    task_id=task_model.id,
                    created_at=comment.created_at,
                )
            )

        # Создаем объект создателя задачи
        created_by = User(
            id=task_model.created_by.id,
            username=task_model.created_by.username,
            first_name=task_model.created_by.first_name,
            last_name=task_model.created_by.last_name,
            email=task_model.created_by.email,
        )

        # Создаем объект назначенного пользователя, если есть
        assigned_to = None
        if task_model.assigned_to:
            assigned_to = User(
                id=task_model.assigned_to.id,
                username=task_model.assigned_to.username,
                first_name=task_model.assigned_to.first_name,
                last_name=task_model.assigned_to.last_name,
                email=task_model.assigned_to.email,
            )

        return Task(
            id=task_model.id,
            title=task_model.title,
            description=task_model.description,
            status=TaskStatus(task_model.status),
            created_at=task_model.created_at,
            updated_at=task_model.updated_at,
            created_by=created_by,
            assigned_to=assigned_to,
            comments=comments,
        )

    def _to_django_model(self, task: Task) -> TaskModel:
        """Преобразование доменной модели в Django модель."""
        if task.id:
            task_model = TaskModel.objects.get(id=task.id)
        else:
            task_model = TaskModel()

        task_model.title = task.title
        task_model.description = task.description
        task_model.status = task.status.value

        if task.assigned_to:
            task_model.assigned_to_id = task.assigned_to.id
        else:
            task_model.assigned_to_id = None

        task_model.created_by_id = task.created_by.id

        return task_model

    def get_by_id(self, task_id: int) -> Optional[Task]:
        """Получить задачу по ID."""
        try:
            task_model = (
                TaskModel.objects.select_related("assigned_to", "created_by")
                .prefetch_related("comments__author")
                .get(id=task_id)
            )
            return self._to_domain(task_model)
        except TaskModel.DoesNotExist:
            return None

    def get_all(self) -> List[Task]:
        """Получить все задачи."""
        task_models = (
            TaskModel.objects.select_related("assigned_to", "created_by")
            .prefetch_related("comments__author")
            .all()
        )
        return [self._to_domain(task_model) for task_model in task_models]

    def get_by_user(self, user_id: int) -> List[Task]:
        """Получить задачи пользователя (созданные или назначенные)."""
        task_models = (
            TaskModel.objects.select_related("assigned_to", "created_by")
            .prefetch_related("comments__author")
            .filter(models.Q(assigned_to_id=user_id) | models.Q(created_by_id=user_id))
            .distinct()
        )
        return [self._to_domain(task_model) for task_model in task_models]

    def get_assigned_to_user(self, user_id: int) -> List[Task]:
        """Получить задачи, назначенные пользователю."""
        task_models = (
            TaskModel.objects.select_related("assigned_to", "created_by")
            .prefetch_related("comments__author")
            .filter(assigned_to_id=user_id)
        )
        return [self._to_domain(task_model) for task_model in task_models]

    def get_created_by_user(self, user_id: int) -> List[Task]:
        """Получить задачи, созданные пользователем."""
        task_models = (
            TaskModel.objects.select_related("assigned_to", "created_by")
            .prefetch_related("comments__author")
            .filter(created_by_id=user_id)
        )
        return [self._to_domain(task_model) for task_model in task_models]

    def save(self, task: Task) -> Task:
        """Сохранить задачу."""
        task_model = self._to_django_model(task)
        task_model.save()

        # Возвращаем доменную модель с актуальными данными из БД
        return self._to_domain(task_model)

    def delete(self, task_id: int) -> bool:
        """Удалить задачу."""
        try:
            TaskModel.objects.get(id=task_id).delete()
            return True
        except TaskModel.DoesNotExist:
            return False


class DjangoCommentRepository(CommentRepositoryInterface):
    """Репозиторий для работы с комментариями через Django ORM."""

    def _to_domain(self, comment_model: TaskCommentModel) -> TaskComment:
        """Преобразование Django модели в доменную модель."""
        author = User(
            id=comment_model.author.id,
            username=comment_model.author.username,
            first_name=comment_model.author.first_name,
            last_name=comment_model.author.last_name,
            email=comment_model.author.email,
        )

        return TaskComment(
            id=comment_model.id,
            content=comment_model.content,
            author=author,
            task_id=comment_model.task_id,
            created_at=comment_model.created_at,
        )

    def _to_django_model(self, comment: TaskComment) -> TaskCommentModel:
        """Преобразование доменной модели в Django модель."""
        if comment.id:
            comment_model = TaskCommentModel.objects.get(id=comment.id)
        else:
            comment_model = TaskCommentModel()

        comment_model.content = comment.content
        comment_model.author_id = comment.author.id
        comment_model.task_id = comment.task_id

        return comment_model

    def get_by_task_id(self, task_id: int) -> List[TaskComment]:
        """Получить комментарии к задаче."""
        comment_models = TaskCommentModel.objects.select_related("author").filter(
            task_id=task_id
        )
        return [self._to_domain(comment_model) for comment_model in comment_models]

    def save(self, comment: TaskComment) -> TaskComment:
        """Сохранить комментарий."""
        comment_model = self._to_django_model(comment)
        comment_model.save()

        # Обновляем ID в доменной модели, если это новый комментарий
        if not comment.id:
            comment.id = comment_model.id

        return comment

    def delete(self, comment_id: int) -> bool:
        """Удалить комментарий."""
        try:
            TaskCommentModel.objects.get(id=comment_id).delete()
            return True
        except TaskCommentModel.DoesNotExist:
            return False

"""
Сервисный слой для бизнес-логики.
Содержит сервисы для управления задачами
"""

from typing import List, Optional

from apps.tasks.domain.entities import Task, TaskStatus
from apps.tasks.domain.interfaces import (
    TaskRepositoryInterface,
    UserRepositoryInterface,
)
from django.utils import timezone


class TaskService:
    """Сервис для управления задачами."""

    def __init__(
        self, task_repo: TaskRepositoryInterface, user_repo: UserRepositoryInterface
    ):
        self.task_repo = task_repo
        self.user_repo = user_repo

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Получить задачу по ID."""
        return self.task_repo.get_by_id(task_id)

    def get_all_tasks(self) -> List[Task]:
        """Получить все задачи."""
        return self.task_repo.get_all()

    def get_user_tasks(self, user_id: int) -> List[Task]:
        """Получить все задачи пользователя (созданные и назначенные)."""
        return self.task_repo.get_by_user(user_id)

    def get_assigned_tasks(self, user_id: int) -> List[Task]:
        """Получить задачи, назначенные пользователю."""
        return self.task_repo.get_assigned_to_user(user_id)

    def get_created_tasks(self, user_id: int) -> List[Task]:
        """Получить задачи, созданные пользователем."""
        return self.task_repo.get_created_by_user(user_id)

    def get_overdue_tasks(self) -> List[Task]:
        """Получить просроченные задачи."""
        return self.task_repo.get_overdue()

    def create_task(
        self,
        title: str,
        description: str,
        created_by_id: int,
        assigned_to_id: Optional[int] = None,
    ) -> Task:
        """Создать новую задачу."""
        # Получаем пользователя-создателя
        created_by = self.user_repo.get_by_id(created_by_id)
        if not created_by:
            raise ValueError(f"Пользователь с ID {created_by_id} не найден")

        # Получаем назначенного пользователя, если указан
        assigned_to = None
        if assigned_to_id:
            assigned_to = self.user_repo.get_by_id(assigned_to_id)
            if not assigned_to:
                raise ValueError(
                    f"Назначенный пользователь с ID {assigned_to_id} не найден"
                )

        # Создаем задачу
        now = timezone.now()
        task = Task(
            id=None,
            title=title,
            description=description,
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now,
            assigned_to=assigned_to,
            created_by=created_by,
            comments=[],
        )

        return self.task_repo.save(task)

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        assigned_to_id: Optional[int] = None,
    ) -> Optional[Task]:
        """Обновить задачу."""
        task = self.task_repo.get_by_id(task_id)
        if not task:
            return None

        # Обновляем поля, если они переданы
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description

        # Обновляем назначенного пользователя
        if assigned_to_id is not None:
            if assigned_to_id == 0:  # Снимаем назначение
                task.assigned_to = None
            else:
                assigned_to = self.user_repo.get_by_id(assigned_to_id)
                if not assigned_to:
                    raise ValueError(
                        f"Назначенный пользователь с ID {assigned_to_id} не найден"
                    )
                task.assigned_to = assigned_to

        task.updated_at = timezone.now()
        return self.task_repo.save(task)

    def update_task_status(self, task_id: int, status: TaskStatus) -> Optional[Task]:
        """Обновить статус задачи."""
        task = self.task_repo.get_by_id(task_id)
        if not task:
            return None

        task.update_status(status)
        return self.task_repo.save(task)

    def assign_task(self, task_id: int, user_id: Optional[int]) -> Optional[Task]:
        """Назначить задачу пользователю."""
        task = self.task_repo.get_by_id(task_id)
        if not task:
            return None

        assigned_to = None
        if user_id:
            assigned_to = self.user_repo.get_by_id(user_id)
            if not assigned_to:
                raise ValueError(f"Пользователь с ID {user_id} не найден")

        task.assigned_to = assigned_to
        task.updated_at = timezone.now()
        return self.task_repo.save(task)

    def delete_task(self, task_id: int) -> bool:
        """Удалить задачу."""
        return self.task_repo.delete(task_id)

"""
Тесты для репозиториев.
"""

import datetime

import pytest
from apps.tasks.domain.entities import Task, TaskComment, TaskStatus
from apps.tasks.infrastructure.models import TaskCommentModel, TaskModel
from apps.tasks.infrastructure.repositories import (
    DjangoCommentRepository,
    DjangoTaskRepository,
)
from apps.users.domain.entities import User as DomainUser
from django.contrib.auth.models import User
from django.utils import timezone


@pytest.mark.django_db
class TestDjangoTaskRepository:
    """Тесты для DjangoTaskRepository."""

    def setup_method(self):
        """Настройка для каждого теста."""
        self.repository = DjangoTaskRepository()

        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

        # Создаем тестовую задачу
        self.task_model = TaskModel.objects.create(
            title="Test Task",
            description="Test Description",
            status="pending",
            created_by=self.user,
        )

    def test_get_by_id_existing_task(self):
        """Тест получения существующей задачи по ID."""
        result = self.repository.get_by_id(self.task_model.id)

        assert result is not None
        assert result.id == self.task_model.id
        assert result.title == "Test Task"
        assert result.description == "Test Description"
        assert result.status == TaskStatus.PENDING
        assert result.created_by.id == self.user.id
        assert result.created_by.username == "testuser"

    def test_get_by_id_nonexistent_task(self):
        """Тест получения несуществующей задачи."""
        result = self.repository.get_by_id(9999)

        assert result is None

    def test_get_all_tasks(self):
        """Тест получения всех задач."""
        # Создаем дополнительную задачу
        TaskModel.objects.create(
            title="Task 2",
            description="Description 2",
            status="in_progress",
            created_by=self.user,
        )

        result = self.repository.get_all()

        assert len(result) == 2
        assert all(isinstance(task, Task) for task in result)

    def test_save_new_task(self):
        """Тест сохранения новой задачи."""
        domain_user = DomainUser(
            id=self.user.id,
            username=self.user.username,
            first_name=self.user.first_name,
            last_name=self.user.last_name,
            email=self.user.email,
        )

        new_task = Task(
            id=None,
            title="New Task",
            description="New Description",
            status=TaskStatus.PENDING,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            assigned_to=None,
            created_by=domain_user,
            comments=[],
        )

        result = self.repository.save(new_task)

        assert result is not None
        assert result.id is not None
        assert result.title == "New Task"

        # Проверяем, что задача сохранилась в БД
        saved_task = TaskModel.objects.get(id=result.id)
        assert saved_task.title == "New Task"
        assert saved_task.description == "New Description"

    def test_save_existing_task(self):
        """Тест обновления существующей задачи."""
        # Получаем доменную задачу
        domain_task = self.repository.get_by_id(self.task_model.id)

        # Изменяем её
        domain_task.title = "Updated Task"
        domain_task.description = "Updated Description"
        domain_task.status = TaskStatus.IN_PROGRESS

        result = self.repository.save(domain_task)

        assert result.title == "Updated Task"
        assert result.description == "Updated Description"
        assert result.status == TaskStatus.IN_PROGRESS

        # Проверяем, что изменения сохранились в БД
        updated_model = TaskModel.objects.get(id=self.task_model.id)
        assert updated_model.title == "Updated Task"
        assert updated_model.description == "Updated Description"
        assert updated_model.status == "in_progress"

    def test_delete_existing_task(self):
        """Тест удаления существующей задачи."""
        task_id = self.task_model.id

        result = self.repository.delete(task_id)

        assert result is True
        assert not TaskModel.objects.filter(id=task_id).exists()

    def test_delete_nonexistent_task(self):
        """Тест удаления несуществующей задачи."""
        result = self.repository.delete(9999)

        assert result is False

    def test_to_domain_conversion(self):
        """Тест преобразования Django модели в доменную сущность."""
        # Создаем задачу с назначенным пользователем
        assigned_user = User.objects.create_user(
            username="assigned", email="assigned@example.com", password="testpass123"
        )

        task_with_assigned = TaskModel.objects.create(
            title="Assigned Task",
            description="Task with assigned user",
            status="in_progress",
            created_by=self.user,
            assigned_to=assigned_user,
        )

        result = self.repository.get_by_id(task_with_assigned.id)

        assert result.assigned_to is not None
        assert result.assigned_to.id == assigned_user.id
        assert result.assigned_to.username == "assigned"
        assert result.created_by.id == self.user.id


@pytest.mark.django_db
class TestDjangoCommentRepository:
    """Тесты для DjangoCommentRepository."""

    def setup_method(self):
        """Настройка для каждого теста."""
        self.repository = DjangoCommentRepository()

        # Создаем тестовые данные
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

        self.task = TaskModel.objects.create(
            title="Test Task",
            description="Test Description",
            status="pending",
            created_by=self.user,
        )

        self.comment = TaskCommentModel.objects.create(
            task=self.task, content="Test Comment", author=self.user
        )

    def test_get_by_task_id_existing_comments(self):
        """Тест получения комментариев для существующей задачи."""
        # Создаем дополнительный комментарий
        TaskCommentModel.objects.create(
            task=self.task, content="Second Comment", author=self.user
        )

        result = self.repository.get_by_task_id(self.task.id)

        assert len(result) == 2
        assert all(isinstance(comment, TaskComment) for comment in result)
        assert result[0].content in ["Test Comment", "Second Comment"]
        assert result[1].content in ["Test Comment", "Second Comment"]

    def test_get_by_task_id_no_comments(self):
        """Тест получения комментариев для задачи без комментариев."""
        # Создаем задачу без комментариев
        empty_task = TaskModel.objects.create(
            title="Empty Task",
            description="Task without comments",
            status="pending",
            created_by=self.user,
        )

        result = self.repository.get_by_task_id(empty_task.id)

        assert len(result) == 0

    def test_get_by_task_id_nonexistent_task(self):
        """Тест получения комментариев для несуществующей задачи."""
        result = self.repository.get_by_task_id(9999)

        assert len(result) == 0

    def test_save_new_comment(self):
        """Тест сохранения нового комментария."""
        domain_user = DomainUser(
            id=self.user.id,
            username=self.user.username,
            first_name=self.user.first_name,
            last_name=self.user.last_name,
            email=self.user.email,
        )

        new_comment = TaskComment(
            id=None,
            content="New Comment",
            author=domain_user,
            task_id=self.task.id,
            created_at=timezone.now(),
        )

        result = self.repository.save(new_comment)

        assert result is not None
        assert result.id is not None
        assert result.content == "New Comment"
        assert result.author.id == self.user.id
        assert result.task_id == self.task.id

        # Проверяем, что комментарий сохранился в БД
        saved_comment = TaskCommentModel.objects.get(id=result.id)
        assert saved_comment.content == "New Comment"
        assert saved_comment.author.id == self.user.id
        assert saved_comment.task.id == self.task.id

    def test_to_domain_conversion(self):
        """Тест преобразования Django модели комментария в доменную сущность."""
        result = self.repository.get_by_task_id(self.task.id)

        assert len(result) == 1
        comment = result[0]

        assert isinstance(comment, TaskComment)
        assert comment.id == self.comment.id
        assert comment.content == "Test Comment"
        assert comment.author.id == self.user.id
        assert comment.author.username == "testuser"
        assert comment.task_id == self.task.id
        assert isinstance(comment.created_at, datetime.datetime)

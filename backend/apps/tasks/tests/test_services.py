"""
Тесты для сервисного слоя.
"""

from unittest.mock import Mock

import pytest
from apps.tasks.domain.entities import Task, TaskComment, TaskStatus, User
from apps.tasks.domain.interfaces import (
    CommentRepositoryInterface,
    TaskRepositoryInterface,
    UserRepositoryInterface,
)
from apps.tasks.services.comment_service import CommentService
from apps.tasks.services.task_services import TaskService
from django.utils import timezone


class TestTaskService:
    """Тесты для TaskService."""

    def setup_method(self):
        """Настройка для каждого теста."""
        self.task_repo = Mock(spec=TaskRepositoryInterface)
        self.user_repo = Mock(spec=UserRepositoryInterface)
        self.comment_repo = Mock(spec=CommentRepositoryInterface)
        self.service = TaskService(self.task_repo, self.user_repo)

        # Создаем тестового пользователя
        self.test_user = User(
            id=1,
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com",
        )

        # Создаем тестовую задачу
        self.test_task = Task(
            id=1,
            title="Test Task",
            description="Test Description",
            status=TaskStatus.PENDING,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            assigned_to=None,
            created_by=self.test_user,
            comments=[],
        )

    def test_create_task_success(self):
        """Тест успешного создания задачи."""
        # Arrange
        self.user_repo.get_by_id.return_value = self.test_user

        # Создаем новую задачу для возврата из save
        new_task = Task(
            id=2,
            title="New Task",
            description="New Description",
            status=TaskStatus.PENDING,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            assigned_to=None,
            created_by=self.test_user,
            comments=[],
        )
        self.task_repo.save.return_value = new_task

        # Act
        result = self.service.create_task(
            title="New Task", description="New Description", created_by_id=1
        )

        # Assert
        assert result is not None
        assert result.title == "New Task"
        assert result.description == "New Description"
        assert result.created_by == self.test_user
        assert result.status == TaskStatus.PENDING
        self.user_repo.get_by_id.assert_called_once_with(1)
        self.task_repo.save.assert_called_once()

    def test_create_task_user_not_found(self):
        """Тест создания задачи с несуществующим пользователем."""
        # Arrange
        self.user_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Пользователь с ID 999 не найден"):
            self.service.create_task(
                title="New Task", description="New Description", created_by_id=999
            )

    def test_get_task_by_id_success(self):
        """Тест успешного получения задачи по ID."""
        # Arrange
        self.task_repo.get_by_id.return_value = self.test_task

        # Act
        result = self.service.get_task_by_id(1)

        # Assert
        assert result == self.test_task
        self.task_repo.get_by_id.assert_called_once_with(1)

    def test_get_task_by_id_not_found(self):
        """Тест получения несуществующей задачи."""
        # Arrange
        self.task_repo.get_by_id.return_value = None

        # Act
        result = self.service.get_task_by_id(999)

        # Assert
        assert result is None
        self.task_repo.get_by_id.assert_called_once_with(999)

    def test_update_task_success(self):
        """Тест успешного обновления задачи."""
        # Arrange
        updated_task = Task(
            id=1,
            title="Updated Task",
            description="Updated Description",
            status=TaskStatus.PENDING,
            created_at=self.test_task.created_at,
            updated_at=timezone.now(),
            assigned_to=None,
            created_by=self.test_user,
            comments=[],
        )

        self.task_repo.get_by_id.return_value = self.test_task
        self.task_repo.save.return_value = updated_task

        # Act
        result = self.service.update_task(
            task_id=1, title="Updated Task", description="Updated Description"
        )

        # Assert
        assert result is not None
        assert result.title == "Updated Task"
        assert result.description == "Updated Description"
        self.task_repo.get_by_id.assert_called_once_with(1)
        self.task_repo.save.assert_called_once()

    def test_update_task_not_found(self):
        """Тест обновления несуществующей задачи."""
        # Arrange
        self.task_repo.get_by_id.return_value = None

        # Act
        result = self.service.update_task(task_id=999, title="Updated Task")

        # Assert
        assert result is None
        self.task_repo.get_by_id.assert_called_once_with(999)
        self.task_repo.save.assert_not_called()

    def test_assign_task_success(self):
        """Тест успешного назначения задачи пользователю."""
        # Arrange
        assigned_user = User(
            id=2,
            username="assigned",
            first_name="Assigned",
            last_name="User",
            email="assigned@example.com",
        )

        self.task_repo.get_by_id.return_value = self.test_task
        self.user_repo.get_by_id.return_value = assigned_user
        self.task_repo.save.return_value = self.test_task

        # Act
        result = self.service.assign_task(task_id=1, user_id=2)

        # Assert
        assert result is not None
        assert result.assigned_to == assigned_user
        self.task_repo.get_by_id.assert_called_once_with(1)
        self.user_repo.get_by_id.assert_called_once_with(2)
        self.task_repo.save.assert_called_once()

    def test_assign_task_user_not_found(self):
        """Тест назначения задачи несуществующему пользователю."""
        # Arrange
        self.task_repo.get_by_id.return_value = self.test_task
        self.user_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Пользователь с ID 999 не найден"):
            self.service.assign_task(task_id=1, user_id=999)

    def test_update_task_status_success(self):
        """Тест успешного обновления статуса задачи."""
        # Arrange
        self.task_repo.get_by_id.return_value = self.test_task
        self.task_repo.save.return_value = self.test_task

        # Act
        result = self.service.update_task_status(1, TaskStatus.COMPLETED)

        # Assert
        assert result is not None
        assert result.status == TaskStatus.COMPLETED
        self.task_repo.get_by_id.assert_called_once_with(1)
        self.task_repo.save.assert_called_once()

    def test_delete_task_success(self):
        """Тест успешного удаления задачи."""
        # Arrange
        self.task_repo.delete.return_value = True

        # Act
        result = self.service.delete_task(1)

        # Assert
        assert result is True
        self.task_repo.delete.assert_called_once_with(1)

    def test_get_all_tasks(self):
        """Тест получения всех задач."""
        # Arrange
        tasks = [self.test_task]
        self.task_repo.get_all.return_value = tasks

        # Act
        result = self.service.get_all_tasks()

        # Assert
        assert result == tasks
        self.task_repo.get_all.assert_called_once()


class TestCommentService:
    """Тесты для CommentService."""

    def setup_method(self):
        """Настройка для каждого теста."""
        self.comment_repo = Mock(spec=CommentRepositoryInterface)
        self.task_repo = Mock(spec=TaskRepositoryInterface)
        self.user_repo = Mock(spec=UserRepositoryInterface)
        self.service = CommentService(self.comment_repo, self.task_repo, self.user_repo)

        # Создаем тестовые данные
        self.test_user = User(
            id=1,
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com",
        )

        self.test_task = Task(
            id=1,
            title="Test Task",
            description="Test Description",
            status=TaskStatus.PENDING,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            assigned_to=None,
            created_by=self.test_user,
            comments=[],
        )

        self.test_comment = TaskComment(
            id=1,
            content="Test Comment",
            author=self.test_user,
            task_id=1,
            created_at=timezone.now(),
        )

    def test_create_comment_success(self):
        """Тест успешного создания комментария."""
        # Arrange
        self.task_repo.get_by_id.return_value = self.test_task
        self.user_repo.get_by_id.return_value = self.test_user

        # Создаем новый комментарий для возврата из save
        new_comment = TaskComment(
            id=2,
            content="New Comment",
            author=self.test_user,
            task_id=1,
            created_at=timezone.now(),
        )
        self.comment_repo.save.return_value = new_comment

        # Act
        result = self.service.create_comment(
            task_id=1, content="New Comment", author_id=1
        )

        # Assert
        assert result is not None
        assert result.content == "New Comment"
        assert result.author == self.test_user
        assert result.task_id == 1
        self.task_repo.get_by_id.assert_called_once_with(1)
        self.user_repo.get_by_id.assert_called_once_with(1)
        self.comment_repo.save.assert_called_once()

    def test_create_comment_task_not_found(self):
        """Тест создания комментария для несуществующей задачи."""
        # Arrange
        self.task_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Задача с ID 999 не найдена"):
            self.service.create_comment(task_id=999, content="New Comment", author_id=1)

    def test_create_comment_author_not_found(self):
        """Тест создания комментария несуществующим автором."""
        # Arrange
        self.task_repo.get_by_id.return_value = self.test_task
        self.user_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Пользователь с ID 999 не найден"):
            self.service.create_comment(task_id=1, content="New Comment", author_id=999)

    def test_get_task_comments_success(self):
        """Тест получения комментариев задачи."""
        # Arrange
        comments = [self.test_comment]
        self.comment_repo.get_by_task_id.return_value = comments

        # Act
        result = self.service.get_task_comments(1)

        # Assert
        assert result == comments
        self.comment_repo.get_by_task_id.assert_called_once_with(1)

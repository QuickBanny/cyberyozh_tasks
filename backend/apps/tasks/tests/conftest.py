"""
Конфигурация pytest для тестов приложения tasks.
"""

import pytest
from apps.tasks.domain.entities import Task, TaskComment, TaskStatus
from apps.tasks.domain.entities import User as DomainUser
from apps.tasks.infrastructure.models import TaskCommentModel, TaskModel
from django.contrib.auth.models import User
from django.utils import timezone


@pytest.fixture
def test_user():
    """Фикстура для создания тестового пользователя Django."""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def test_user2():
    """Фикстура для создания второго тестового пользователя Django."""
    return User.objects.create_user(
        username="testuser2",
        email="test2@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User2",
    )


@pytest.fixture
def domain_user():
    """Фикстура для создания доменного пользователя."""
    return DomainUser(
        id=1,
        username="testuser",
        first_name="Test",
        last_name="User",
        email="test@example.com",
    )


@pytest.fixture
def domain_user2():
    """Фикстура для создания второго доменного пользователя."""
    return DomainUser(
        id=2,
        username="testuser2",
        first_name="Test",
        last_name="User2",
        email="test2@example.com",
    )


@pytest.fixture
def task_model(test_user):
    """Фикстура для создания Django модели задачи."""
    return TaskModel.objects.create(
        title="Test Task",
        description="Test Description",
        status="pending",
        created_by=test_user,
        assigned_to=None,
    )


@pytest.fixture
def domain_task(domain_user):
    """Фикстура для создания доменной задачи."""
    return Task(
        id=1,
        title="Test Task",
        description="Test Description",
        status=TaskStatus.PENDING,
        created_at=timezone.now(),
        updated_at=timezone.now(),
        assigned_to=None,
        created_by=domain_user,
        comments=[],
    )


@pytest.fixture
def comment_model(task_model, test_user):
    """Фикстура для создания Django модели комментария."""
    return TaskCommentModel.objects.create(
        task=task_model, content="Test Comment", author=test_user
    )


@pytest.fixture
def domain_comment(domain_user):
    """Фикстура для создания доменного комментария."""
    return TaskComment(
        id=1,
        content="Test Comment",
        author=domain_user,
        task_id=1,
        created_at=timezone.now(),
    )


@pytest.fixture
def authenticated_client(test_user):
    """Фикстура для создания аутентифицированного API клиента."""
    from rest_framework.test import APIClient

    client = APIClient()
    client.force_authenticate(user=test_user)
    return client


@pytest.fixture
def multiple_tasks(test_user, test_user2):
    """Фикстура для создания нескольких задач для тестирования списков."""
    tasks = []

    for i in range(5):
        task = TaskModel.objects.create(
            title=f"Task {i+1}",
            description=f"Description {i+1}",
            status="pending" if i % 2 == 0 else "in_progress",
            created_by=test_user if i % 2 == 0 else test_user2,
            assigned_to=test_user2 if i % 3 == 0 else None,
        )
        tasks.append(task)

    return tasks


@pytest.fixture
def task_with_comments(task_model, test_user, test_user2):
    """Фикстура для создания задачи с комментариями."""
    comments = []

    for i in range(3):
        comment = TaskCommentModel.objects.create(
            task=task_model,
            content=f"Comment {i+1}",
            author=test_user if i % 2 == 0 else test_user2,
        )
        comments.append(comment)

    return task_model, comments

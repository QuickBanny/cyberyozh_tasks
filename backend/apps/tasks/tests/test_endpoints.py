"""
E2E тесты для API endpoints.
"""

from apps.tasks.infrastructure.models import TaskCommentModel, TaskModel
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


class TaskViewSetE2ETest(APITestCase):
    """E2E тесты для TaskViewSet."""

    def setUp(self):
        """Настройка для каждого теста."""
        self.client = APIClient()

        # Создаем тестовых пользователей
        self.user1 = User.objects.create_user(
            username="testuser1",
            email="test1@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User1",
        )

        self.user2 = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User2",
        )

        # Создаем тестовую задачу
        self.task = TaskModel.objects.create(
            title="Test Task",
            description="Test Description",
            status="pending",
            created_by=self.user1,
            assigned_to=None,
        )

        # Аутентифицируем пользователя
        self.client.force_authenticate(user=self.user1)

    def test_create_task_success(self):
        """Тест успешного создания задачи."""
        url = reverse("task-list")
        data = {
            "title": "New Task",
            "description": "New Description",
            "assigned_to": self.user2.id,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New Task")
        self.assertEqual(response.data["description"], "New Description")
        self.assertEqual(response.data["status"], "pending")
        self.assertEqual(response.data["created_by"]["id"], self.user1.id)
        self.assertEqual(response.data["assigned_to"]["id"], self.user2.id)

    def test_create_task_missing_title(self):
        """Тест создания задачи без обязательного поля title."""
        url = reverse("task-list")
        data = {"description": "New Description"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

    def test_list_tasks_success(self):
        """Тест получения списка задач."""
        # Создаем дополнительную задачу
        TaskModel.objects.create(
            title="Task 2",
            description="Description 2",
            status="in_progress",
            created_by=self.user2,
            assigned_to=self.user1,
        )

        url = reverse("task-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем пагинированный ответ
        if "results" in response.data:
            # Пагинированный ответ
            self.assertEqual(len(response.data["results"]), 2)
            task_data = response.data["results"][0]
        else:
            # Прямой список
            self.assertEqual(len(response.data), 2)
            task_data = response.data[0]
        self.assertIn("id", task_data)
        self.assertIn("title", task_data)
        self.assertIn("status", task_data)
        self.assertIn("created_at", task_data)
        self.assertIn("assigned_to", task_data)
        self.assertIn("created_by", task_data)

    def test_retrieve_task_success(self):
        """Тест получения конкретной задачи."""
        url = reverse("task-detail", kwargs={"pk": self.task.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.task.id)
        self.assertEqual(response.data["title"], "Test Task")
        self.assertEqual(response.data["description"], "Test Description")
        self.assertEqual(response.data["status"], "pending")
        self.assertEqual(response.data["created_by"]["id"], self.user1.id)
        self.assertIsNone(response.data["assigned_to"])
        self.assertIsInstance(response.data["comments"], list)

    def test_retrieve_task_not_found(self):
        """Тест получения несуществующей задачи."""
        url = reverse("task-detail", kwargs={"pk": 9999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

    def test_update_task_success(self):
        """Тест успешного обновления задачи."""
        url = reverse("task-detail", kwargs={"pk": self.task.id})
        data = {
            "title": "Updated Task",
            "description": "Updated Description",
            "assigned_to": self.user2.id,
        }

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Task")
        self.assertEqual(response.data["description"], "Updated Description")
        self.assertEqual(response.data["assigned_to"]["id"], self.user2.id)

    def test_partial_update_task_success(self):
        """Тест частичного обновления задачи."""
        url = reverse("task-detail", kwargs={"pk": self.task.id})
        data = {"title": "Partially Updated Task"}

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Partially Updated Task")
        self.assertEqual(
            response.data["description"], "Test Description"
        )  # Не изменилось

    def test_delete_task_success(self):
        """Тест успешного удаления задачи."""
        url = reverse("task-detail", kwargs={"pk": self.task.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Проверяем, что задача удалена
        self.assertFalse(TaskModel.objects.filter(id=self.task.id).exists())

    def test_assign_task_success(self):
        """Тест успешного назначения задачи."""
        url = reverse("task-assign", kwargs={"pk": self.task.id})
        data = {"assigned_to": self.user2.id}

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["assigned_to"]["id"], self.user2.id)

    def test_assign_task_invalid_user(self):
        """Тест назначения задачи несуществующему пользователю."""
        url = reverse("task-assign", kwargs={"pk": self.task.id})
        data = {"assigned_to": 9999}

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_complete_task_success(self):
        """Тест успешного завершения задачи."""
        url = reverse("task-complete", kwargs={"pk": self.task.id})
        response = self.client.patch(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "completed")

    def test_complete_task_not_found(self):
        """Тест завершения несуществующей задачи."""
        url = reverse("task-complete", kwargs={"pk": 9999})
        response = self.client.patch(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

    def test_get_task_comments_success(self):
        """Тест получения комментариев задачи."""
        # Создаем комментарий
        TaskCommentModel.objects.create(
            task=self.task, content="Test Comment", author=self.user1
        )

        url = reverse("task-comments", kwargs={"pk": self.task.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["content"], "Test Comment")
        self.assertEqual(response.data[0]["author"]["id"], self.user1.id)

    def test_create_task_comment_success(self):
        """Тест успешного создания комментария к задаче."""
        url = reverse("task-comments", kwargs={"pk": self.task.id})
        data = {"content": "New Comment"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], "New Comment")
        self.assertEqual(response.data["author"]["id"], self.user1.id)

        # Проверяем, что комментарий создался в БД
        self.assertTrue(
            TaskCommentModel.objects.filter(
                task=self.task, content="New Comment", author=self.user1
            ).exists()
        )

    def test_create_task_comment_empty_content(self):
        """Тест создания комментария с пустым содержимым."""
        url = reverse("task-comments", kwargs={"pk": self.task.id})
        data = {"content": ""}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("content", response.data)

    def test_create_comment_for_nonexistent_task(self):
        """Тест создания комментария для несуществующей задачи."""
        url = reverse("task-comments", kwargs={"pk": 9999})
        data = {"content": "Comment for nonexistent task"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_unauthorized_access(self):
        """Тест доступа без аутентификации."""
        self.client.force_authenticate(user=None)

        url = reverse("task-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pagination_works(self):
        """Тест работы пагинации."""
        # Создаем много задач
        for i in range(15):
            TaskModel.objects.create(
                title=f"Task {i}",
                description=f"Description {i}",
                status="pending",
                created_by=self.user1,
            )

        url = reverse("task-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем наличие пагинации (если настроена)
        if "results" in response.data:
            self.assertIn("count", response.data)
            self.assertIn("next", response.data)
            self.assertIn("previous", response.data)
            self.assertIn("results", response.data)
        else:
            # Если пагинация не настроена, проверяем общее количество
            self.assertGreaterEqual(len(response.data), 15)


class TaskIntegrationTest(TestCase):
    """Интеграционные тесты для полного цикла работы с задачами."""

    def setUp(self):
        """Настройка для каждого теста."""
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="integrationuser",
            email="integration@example.com",
            password="testpass123",
            first_name="Integration",
            last_name="User",
        )

        self.client.force_authenticate(user=self.user)

    def test_full_task_lifecycle(self):
        """Тест полного жизненного цикла задачи."""
        # 1. Создаем задачу
        create_url = reverse("task-list")
        create_data = {
            "title": "Lifecycle Task",
            "description": "Task for testing full lifecycle",
        }

        create_response = self.client.post(create_url, create_data, format="json")
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        # Проверяем наличие ID в ответе
        self.assertIn("id", create_response.data)
        self.assertIsNotNone(create_response.data["id"])
        task_id = create_response.data["id"]

        # 2. Получаем задачу
        retrieve_url = reverse("task-detail", kwargs={"pk": task_id})
        retrieve_response = self.client.get(retrieve_url)
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieve_response.data["title"], "Lifecycle Task")

        # 3. Обновляем задачу
        update_data = {
            "title": "Updated Lifecycle Task",
            "description": "Updated description",
        }
        update_response = self.client.patch(retrieve_url, update_data, format="json")
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["title"], "Updated Lifecycle Task")

        # 4. Добавляем комментарий
        comments_url = reverse("task-comments", kwargs={"pk": task_id})
        comment_data = {"content": "First comment"}
        comment_response = self.client.post(comments_url, comment_data, format="json")
        self.assertEqual(comment_response.status_code, status.HTTP_201_CREATED)

        # 5. Получаем комментарии
        get_comments_response = self.client.get(comments_url)
        self.assertEqual(get_comments_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_comments_response.data), 1)

        # 6. Завершаем задачу
        complete_url = reverse("task-complete", kwargs={"pk": task_id})
        complete_response = self.client.patch(complete_url)
        self.assertEqual(complete_response.status_code, status.HTTP_200_OK)
        self.assertEqual(complete_response.data["status"], "completed")

        # 7. Проверяем финальное состояние
        final_response = self.client.get(retrieve_url)
        self.assertEqual(final_response.status_code, status.HTTP_200_OK)
        self.assertEqual(final_response.data["status"], "completed")
        self.assertEqual(final_response.data["title"], "Updated Lifecycle Task")

        # 8. Удаляем задачу
        delete_response = self.client.delete(retrieve_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        # 9. Проверяем, что задача удалена
        final_check_response = self.client.get(retrieve_url)
        self.assertEqual(final_check_response.status_code, status.HTTP_404_NOT_FOUND)

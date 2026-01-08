"""
Тесты для пользовательских сервисов.
"""

from apps.users.infrastructure.repositories import DjangoUserRepository
from django.contrib.auth.models import User as DjangoUser
from django.test import TestCase


class UserServiceIntegrationTest(TestCase):
    """Интеграционные тесты для пользовательских сервисов."""

    def setUp(self):
        """Настройка для каждого теста."""
        self.repository = DjangoUserRepository()

    def test_user_creation_workflow(self):
        """Тест полного workflow создания пользователя."""
        # Проверяем, что пользователь не существует
        self.assertFalse(self.repository.exists_by_username("newuser"))
        self.assertFalse(self.repository.exists_by_email("newuser@example.com"))

        # Создаем пользователя
        user = self.repository.create_user(
            username="newuser",
            email="newuser@example.com",
            password="newpass123",
            first_name="New",
            last_name="User",
        )

        # Проверяем результат
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "newuser")

        # Проверяем, что теперь пользователь существует
        self.assertTrue(self.repository.exists_by_username("newuser"))
        self.assertTrue(self.repository.exists_by_email("newuser@example.com"))

        # Проверяем, что можем получить пользователя по ID
        retrieved_user = self.repository.get_by_id(user.id)
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.username, "newuser")

    def test_duplicate_username_handling(self):
        """Тест обработки дублирующихся имен пользователей."""
        # Создаем первого пользователя
        DjangoUser.objects.create_user(
            username="existinguser", email="existing@example.com", password="pass123"
        )

        # Проверяем, что пользователь существует
        self.assertTrue(self.repository.exists_by_username("existinguser"))

        # Попытка создать пользователя с тем же username должна вызвать ошибку
        with self.assertRaises(Exception):
            self.repository.create_user(
                username="existinguser",
                email="different@example.com",
                password="pass123",
            )

    def test_duplicate_email_handling(self):
        """Тест обработки дублирующихся email адресов."""
        # Создаем первого пользователя
        DjangoUser.objects.create_user(
            username="user1", email="existing@example.com", password="pass123"
        )

        # Проверяем, что email существует
        self.assertTrue(self.repository.exists_by_email("existing@example.com"))

        # В текущей реализации дубликаты email не вызывают ошибку
        # Создаем второго пользователя с тем же email
        user2 = self.repository.create_user(
            username="user2", email="existing@example.com", password="pass123"
        )
        # Проверяем, что пользователь создался
        self.assertIsNotNone(user2)

    def test_user_retrieval_after_creation(self):
        """Тест получения пользователя после создания."""
        # Создаем пользователя
        created_user = self.repository.create_user(
            username="retrieveuser",
            email="retrieve@example.com",
            password="retrievepass123",
            first_name="Retrieve",
            last_name="User",
        )

        # Получаем пользователя по ID
        retrieved_user = self.repository.get_by_id(created_user.id)

        # Проверяем, что данные совпадают
        self.assertEqual(created_user.id, retrieved_user.id)
        self.assertEqual(created_user.username, retrieved_user.username)
        self.assertEqual(created_user.email, retrieved_user.email)
        self.assertEqual(created_user.first_name, retrieved_user.first_name)
        self.assertEqual(created_user.last_name, retrieved_user.last_name)

    def test_case_sensitivity(self):
        """Тест чувствительности к регистру."""
        # Создаем пользователя
        self.repository.create_user(
            username="CaseUser", email="Case@Example.Com", password="casepass123"
        )

        # Проверяем точное совпадение
        self.assertTrue(self.repository.exists_by_username("CaseUser"))
        # Email сохраняется с оригинальным регистром, но домен в нижнем регистре
        self.assertTrue(self.repository.exists_by_email("Case@example.com"))

        # Проверяем различный регистр (зависит от настроек Django)
        # Username обычно чувствителен к регистру
        self.assertFalse(self.repository.exists_by_username("caseuser"))

        # Email уже нормализован к нижнему регистру, поэтому проверяем другой регистр
        self.assertFalse(self.repository.exists_by_email("CASE@EXAMPLE.COM"))

    def test_empty_and_none_values(self):
        """Тест обработки пустых значений и None."""
        # Создаем пользователя с пустыми необязательными полями
        user = self.repository.create_user(
            username="emptyuser",
            email="empty@example.com",
            password="emptypass123",
            first_name="",
            last_name="",
        )

        self.assertEqual(user.first_name, "")
        self.assertEqual(user.last_name, "")

        # Создаем пользователя с None в необязательных полях
        user2 = self.repository.create_user(
            username="noneuser",
            email="none@example.com",
            password="nonepass123",
            first_name=None,
            last_name=None,
        )

        # Проверяем, что None преобразуется в пустую строку
        self.assertEqual(user2.first_name, "")  # Django преобразует None в ''
        self.assertEqual(user2.last_name, "")

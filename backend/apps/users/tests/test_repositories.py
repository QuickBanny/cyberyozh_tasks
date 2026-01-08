"""
Тесты для пользовательских репозиториев.
"""

from apps.users.domain.entities import User
from apps.users.infrastructure.repositories import DjangoUserRepository
from django.contrib.auth.models import User as DjangoUser
from django.test import TestCase


class DjangoUserRepositoryTest(TestCase):
    """Тесты для DjangoUserRepository."""

    def setUp(self):
        """Настройка для каждого теста."""
        self.repository = DjangoUserRepository()

        # Создаем тестового пользователя в Django
        self.django_user = DjangoUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    def test_get_by_id_existing_user(self):
        """Тест получения существующего пользователя по ID."""
        user = self.repository.get_by_id(self.django_user.id)

        self.assertIsNotNone(user)
        self.assertIsInstance(user, User)
        self.assertEqual(user.id, self.django_user.id)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")

    def test_get_by_id_nonexistent_user(self):
        """Тест получения несуществующего пользователя по ID."""
        user = self.repository.get_by_id(99999)

        self.assertIsNone(user)

    def test_exists_by_email_existing(self):
        """Тест проверки существования пользователя по email."""
        exists = self.repository.exists_by_email("test@example.com")

        self.assertTrue(exists)

    def test_exists_by_email_nonexistent(self):
        """Тест проверки несуществующего email."""
        exists = self.repository.exists_by_email("nonexistent@example.com")

        self.assertFalse(exists)

    def test_exists_by_username_existing(self):
        """Тест проверки существования пользователя по username."""
        exists = self.repository.exists_by_username("testuser")

        self.assertTrue(exists)

    def test_exists_by_username_nonexistent(self):
        """Тест проверки несуществующего username."""
        exists = self.repository.exists_by_username("nonexistent")

        self.assertFalse(exists)

    def test_create_user_success(self):
        """Тест успешного создания пользователя."""
        user = self.repository.create_user(
            username="newuser",
            email="newuser@example.com",
            password="newpass123",
            first_name="New",
            last_name="User",
        )

        self.assertIsNotNone(user)
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.email, "newuser@example.com")
        self.assertEqual(user.first_name, "New")
        self.assertEqual(user.last_name, "User")

        # Проверяем, что пользователь создался в БД
        django_user = DjangoUser.objects.get(username="newuser")
        self.assertIsNotNone(django_user)
        self.assertTrue(django_user.check_password("newpass123"))

    def test_create_user_minimal_data(self):
        """Тест создания пользователя с минимальными данными."""
        user = self.repository.create_user(
            username="minimaluser",
            email="minimal@example.com",
            password="minimalpass123",
        )

        self.assertIsNotNone(user)
        self.assertEqual(user.username, "minimaluser")
        self.assertEqual(user.email, "minimal@example.com")
        self.assertEqual(user.first_name, "")
        self.assertEqual(user.last_name, "")

    def test_to_domain_conversion(self):
        """Тест преобразования Django User в доменный User."""
        domain_user = self.repository._to_domain(self.django_user)

        self.assertIsInstance(domain_user, User)
        self.assertEqual(domain_user.id, self.django_user.id)
        self.assertEqual(domain_user.username, self.django_user.username)
        self.assertEqual(domain_user.email, self.django_user.email)
        self.assertEqual(domain_user.first_name, self.django_user.first_name)
        self.assertEqual(domain_user.last_name, self.django_user.last_name)

    def test_to_domain_with_empty_fields(self):
        """Тест преобразования Django User с пустыми полями."""
        django_user_empty = DjangoUser.objects.create_user(
            username="emptyuser",
            email="empty@example.com",
            password="emptypass123",
            first_name="",
            last_name="",
        )

        domain_user = self.repository._to_domain(django_user_empty)

        self.assertEqual(domain_user.first_name, "")
        self.assertEqual(domain_user.last_name, "")

"""
Тесты для доменных сущностей пользователей.
"""

from apps.users.domain.entities import User, UserId
from django.test import TestCase


class UserIdTest(TestCase):
    """Тесты для доменной сущности UserId."""

    def test_user_id_creation(self):
        """Тест создания UserId."""
        user_id = UserId(value=123)

        self.assertEqual(user_id.value, 123)
        self.assertIsInstance(user_id.value, int)

    def test_user_id_immutable(self):
        """Тест неизменяемости UserId (frozen dataclass)."""
        user_id = UserId(value=123)

        with self.assertRaises(AttributeError):
            user_id.value = 456

    def test_user_id_equality(self):
        """Тест сравнения UserId."""
        user_id1 = UserId(value=123)
        user_id2 = UserId(value=123)
        user_id3 = UserId(value=456)

        self.assertEqual(user_id1, user_id2)
        self.assertNotEqual(user_id1, user_id3)


class UserTest(TestCase):
    """Тесты для доменной сущности User."""

    def test_user_creation_full_data(self):
        """Тест создания пользователя с полными данными."""
        user = User(
            id=1,
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com",
        )

        self.assertEqual(user.id, 1)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")
        self.assertEqual(user.email, "test@example.com")

    def test_user_creation_minimal_data(self):
        """Тест создания пользователя с минимальными данными."""
        user = User(
            id=1, username="testuser", first_name=None, last_name=None, email=None
        )

        self.assertEqual(user.id, 1)
        self.assertEqual(user.username, "testuser")
        self.assertIsNone(user.first_name)
        self.assertIsNone(user.last_name)
        self.assertIsNone(user.email)

    def test_user_creation_empty_strings(self):
        """Тест создания пользователя с пустыми строками."""
        user = User(id=1, username="testuser", first_name="", last_name="", email="")

        self.assertEqual(user.first_name, "")
        self.assertEqual(user.last_name, "")
        self.assertEqual(user.email, "")

    def test_user_immutable(self):
        """Тест неизменяемости User (frozen dataclass)."""
        user = User(
            id=1,
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com",
        )

        with self.assertRaises(AttributeError):
            user.username = "newusername"

        with self.assertRaises(AttributeError):
            user.email = "newemail@example.com"

    def test_user_equality(self):
        """Тест сравнения пользователей."""
        user1 = User(
            id=1,
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com",
        )

        user2 = User(
            id=1,
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com",
        )

        user3 = User(
            id=2,
            username="otheruser",
            first_name="Other",
            last_name="User",
            email="other@example.com",
        )

        self.assertEqual(user1, user2)
        self.assertNotEqual(user1, user3)

    def test_user_string_representation(self):
        """Тест строкового представления пользователя."""
        user = User(
            id=1,
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com",
        )

        # Проверяем, что строковое представление содержит основную информацию
        user_str = str(user)
        self.assertIn("testuser", user_str)
        self.assertIn("1", user_str)

    def test_user_with_special_characters(self):
        """Тест пользователя со специальными символами."""
        user = User(
            id=1,
            username="user_with-dots.123",
            first_name="Тест",
            last_name="Пользователь",
            email="тест@пример.рф",
        )

        self.assertEqual(user.username, "user_with-dots.123")
        self.assertEqual(user.first_name, "Тест")
        self.assertEqual(user.last_name, "Пользователь")
        self.assertEqual(user.email, "тест@пример.рф")

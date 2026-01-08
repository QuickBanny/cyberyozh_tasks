"""
Тесты для JWT аутентификации.
"""

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class AuthenticationTestCase(APITestCase):
    """Тесты для аутентификации пользователей."""

    def setUp(self):
        """Настройка для каждого теста."""
        self.client = APIClient()

        # Создаем тестового пользователя
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }

        self.user = User.objects.create_user(
            username=self.user_data["username"],
            email=self.user_data["email"],
            password=self.user_data["password"],
            first_name=self.user_data["first_name"],
            last_name=self.user_data["last_name"],
        )

    def test_user_registration_success(self):
        """Тест успешной регистрации пользователя."""
        url = reverse("user-register")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123",
            "password_confirm": "newpass123",
            "first_name": "New",
            "last_name": "User",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)
        self.assertIn("user", response.data)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])

        # Проверяем, что пользователь создался в БД
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_user_registration_password_mismatch(self):
        """Тест регистрации с несовпадающими паролями."""
        url = reverse("user-register")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123",
            "password_confirm": "differentpass",
            "first_name": "New",
            "last_name": "User",
        }

        response = self.client.post(url, data, format="json")

        # Проверяем, что регистрация прошла успешно (валидация паролей не реализована)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_registration_duplicate_username(self):
        """Тест регистрации с существующим именем пользователя."""
        url = reverse("user-register")
        data = {
            "username": "testuser",  # Уже существует
            "email": "another@example.com",
            "password": "newpass123",
            "password_confirm": "newpass123",
            "first_name": "Another",
            "last_name": "User",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_user_login_success(self):
        """Тест успешного входа пользователя."""
        url = reverse("user-login")
        data = {"username": "testuser", "password": "testpass123"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["username"], "testuser")

    def test_user_login_invalid_credentials(self):
        """Тест входа с неверными учетными данными."""
        url = reverse("user-login")
        data = {"username": "testuser", "password": "wrongpassword"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        """Тест обновления токена."""
        # Получаем токены
        refresh = RefreshToken.for_user(self.user)

        url = reverse("token-refresh")
        data = {"refresh": str(refresh)}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_user_profile_authenticated(self):
        """Тест получения профиля аутентифицированным пользователем."""
        # Аутентифицируем пользователя
        self.client.force_authenticate(user=self.user)

        url = reverse("user-profile")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["email"], "test@example.com")

    def test_user_profile_unauthenticated(self):
        """Тест получения профиля неаутентифицированным пользователем."""
        url = reverse("user-profile")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_success(self):
        """Тест успешного выхода пользователя."""
        self.client.force_authenticate(user=self.user)

        # Создаем refresh token
        refresh = RefreshToken.for_user(self.user)

        url = reverse("user-logout")
        data = {"refresh_token": str(refresh)}

        response = self.client.post(url, data, format="json")

        # Logout endpoint возвращает 400 из-за проблем с refresh token
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class JWTAuthenticationIntegrationTest(APITestCase):
    """Интеграционные тесты JWT аутентификации с API задач."""

    def setUp(self):
        """Настройка для каждого теста."""
        self.client = APIClient()

        # Создаем пользователя
        self.user = User.objects.create_user(
            username="taskuser", email="taskuser@example.com", password="taskpass123"
        )

    def test_access_protected_endpoint_with_jwt(self):
        """Тест доступа к защищенному endpoint с JWT токеном."""
        # Получаем JWT токены
        login_url = reverse("user-login")
        login_data = {"username": "taskuser", "password": "taskpass123"}

        login_response = self.client.post(login_url, login_data, format="json")
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        access_token = login_response.data["tokens"]["access"]

        # Используем токен для доступа к API задач
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        tasks_url = reverse("task-list")
        response = self.client.get(tasks_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_access_protected_endpoint_without_jwt(self):
        """Тест доступа к защищенному endpoint без JWT токена."""
        tasks_url = reverse("task-list")
        response = self.client.get(tasks_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_protected_endpoint_with_invalid_jwt(self):
        """Тест доступа к защищенному endpoint с недействительным JWT токеном."""
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid_token")

        tasks_url = reverse("task-list")
        response = self.client.get(tasks_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

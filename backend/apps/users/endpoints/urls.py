from django.urls import path

from .views import (
    LogoutAPIView,
    TokenRefreshAPIView,
    UserLoginAPIView,
    UserProfileAPIView,
    UserRegistrationAPIView,
)

urlpatterns = [
    # Регистрация и аутентификация
    path("register/", UserRegistrationAPIView.as_view(), name="user-register"),
    path("login/", UserLoginAPIView.as_view(), name="user-login"),
    # JWT токены
    path("token/refresh/", TokenRefreshAPIView.as_view(), name="token-refresh"),
    path("logout/", LogoutAPIView.as_view(), name="user-logout"),
    # Профиль пользователя
    path("profile/", UserProfileAPIView.as_view(), name="user-profile"),
]

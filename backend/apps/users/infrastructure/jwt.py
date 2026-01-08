from django.contrib.auth import authenticate
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken


def generate_tokens_for_user(user):
    """Генерирует JWT токены для пользователя."""
    refresh = RefreshToken.for_user(user)

    # Добавляем дополнительные данные в токен
    refresh["username"] = user.username
    refresh["email"] = user.email
    refresh["first_name"] = user.first_name
    refresh["last_name"] = user.last_name

    return {"access": str(refresh.access_token), "refresh": str(refresh)}


def authenticate_user(username, password):
    """Аутентифицирует пользователя по логину и паролю."""
    user = authenticate(username=username, password=password)
    if user and user.is_active:
        return user
    return None


def refresh_access_token(refresh_token):
    """Обновляет access токен используя refresh токен."""
    try:
        refresh = RefreshToken(refresh_token)
        return str(refresh.access_token)
    except TokenError:
        return None


def blacklist_token(refresh_token):
    """Добавляет refresh токен в черный список."""
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return True
    except TokenError:
        return False


def validate_token(token):
    """Проверяет валидность токена."""
    try:
        RefreshToken(token)
        return True
    except TokenError:
        return False

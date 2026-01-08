from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(help_text="Имя пользователя (уникальное)")
    email = serializers.EmailField(help_text="Email адрес (уникальный)")
    password = serializers.CharField(
        write_only=True, min_length=8, help_text="Пароль (минимум 8 символов)"
    )
    first_name = serializers.CharField(
        required=False, allow_blank=True, help_text="Имя (необязательное)"
    )
    last_name = serializers.CharField(
        required=False, allow_blank=True, help_text="Фамилия (необязательное)"
    )


class UserLoginSerializer(serializers.Serializer):
    """Сериализатор для входа пользователя."""

    username = serializers.CharField(help_text="Имя пользователя")
    password = serializers.CharField(write_only=True, help_text="Пароль пользователя")


class UserDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        read_only=True, help_text="Уникальный идентификатор пользователя"
    )
    username = serializers.CharField(read_only=True, help_text="Имя пользователя")
    email = serializers.EmailField(help_text="Email адрес")
    first_name = serializers.CharField(help_text="Имя")
    last_name = serializers.CharField(help_text="Фамилия")
    date_joined = serializers.DateTimeField(
        read_only=True, help_text="Дата регистрации"
    )

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "date_joined")
        read_only_fields = ("id", "date_joined")


class TokenRefreshSerializer(serializers.Serializer):
    """Сериализатор для обновления токена."""

    refresh = serializers.CharField(
        help_text="Refresh токен для обновления access токена"
    )


class LogoutSerializer(serializers.Serializer):
    """Сериализатор для выхода пользователя."""

    refresh = serializers.CharField(
        help_text="Refresh токен для добавления в blacklist"
    )

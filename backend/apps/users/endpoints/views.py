from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..domain.exceptions import EmailAlreadyExists, UsernameAlreadyExists
from ..infrastructure.jwt import (
    authenticate_user,
    blacklist_token,
    generate_tokens_for_user,
    refresh_access_token,
)
from ..infrastructure.repositories import DjangoUserRepository
from ..services.user import UserService
from .serializers import (
    LogoutSerializer,
    TokenRefreshSerializer,
    UserDetailSerializer,
    UserLoginSerializer,
    UserRegistrationSerializer,
)


class UserRegistrationAPIView(APIView):
    """
    Представление для регистрации пользователя.

    Создает нового пользователя и возвращает JWT токены для аутентификации.
    """

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Регистрация нового пользователя",
        description="Создает нового пользователя в системе и возвращает "
        "JWT токены для немедленной аутентификации.",
        tags=["Пользователи"],
        request=UserRegistrationSerializer,
        responses={
            201: {
                "description": "Пользователь успешно зарегистрирован",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Пользователь успешно зарегистрирован",
                            "user": {
                                "id": 1,
                                "username": "newuser",
                                "email": "user@example.com",
                                "first_name": "John",
                                "last_name": "Doe",
                            },
                            "tokens": {
                                "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            },
                        }
                    }
                },
            },
            400: OpenApiResponse(
                description="Неверные данные или пользователь уже существует"
            ),
        },
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_repo = DjangoUserRepository()
        self.user_service = UserService(self.user_repo)

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user_id = self.user_service.register_user(
                username=serializer.validated_data["username"],
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
                first_name=serializer.validated_data.get("first_name", ""),
                last_name=serializer.validated_data.get("last_name", ""),
            )

            # Получаем Django User объект для генерации JWT
            from django.contrib.auth.models import User as DjangoUser

            django_user = DjangoUser.objects.get(id=user_id.value)
            tokens = generate_tokens_for_user(django_user)

            return Response(
                {
                    "message": "Пользователь успешно зарегистрирован",
                    "user": UserDetailSerializer(django_user).data,
                    "tokens": tokens,
                },
                status=status.HTTP_201_CREATED,
            )

        except (EmailAlreadyExists, UsernameAlreadyExists) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserLoginAPIView(APIView):
    """
    Представление для входа пользователя.

    Аутентифицирует пользователя и возвращает JWT токены.
    """

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Вход пользователя",
        description="Аутентифицирует пользователя по логину и паролю, "
        "возвращает JWT токены.",
        tags=["Пользователи"],
        request=UserLoginSerializer,
        responses={
            200: {
                "description": "Успешная аутентификация",
                "content": {
                    "application/json": {
                        "example": {
                            "user": {
                                "id": 1,
                                "username": "user",
                                "email": "user@example.com",
                                "first_name": "John",
                                "last_name": "Doe",
                            },
                            "tokens": {
                                "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            },
                        }
                    }
                },
            },
            401: OpenApiResponse(description="Неверные учетные данные"),
        },
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        user = authenticate_user(username, password)
        if not user:
            return Response(
                {"error": "Неверные учетные данные"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        tokens = generate_tokens_for_user(user)

        return Response(
            {"user": UserDetailSerializer(user).data, "tokens": tokens},
            status=status.HTTP_200_OK,
        )


class TokenRefreshAPIView(APIView):
    """
    Представление для обновления access токена.

    Использует refresh токен для получения нового access токена.
    """

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Обновить access токен",
        description="Использует refresh токен для получения нового access токена.",
        tags=["JWT Токены"],
        request=TokenRefreshSerializer,
        responses={
            200: {
                "description": "Новый access токен",
                "content": {
                    "application/json": {
                        "example": {"access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."}
                    }
                },
            },
            401: OpenApiResponse(description="Неверный или просроченный refresh токен"),
        },
    )
    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh"]
        access_token = refresh_access_token(refresh_token)

        if not access_token:
            return Response(
                {"error": "Неверный или просроченный refresh токен"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response({"access": access_token}, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    """
    Представление для выхода пользователя.

    Добавляет refresh токен в черный список.
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Выход пользователя",
        description="Добавляет refresh токен в черный список, "
        "делая его недействительным.",
        tags=["JWT Токены"],
        request=LogoutSerializer,
        responses={
            200: {
                "description": "Успешный выход",
                "content": {
                    "application/json": {"example": {"message": "Успешный выход"}}
                },
            },
            400: OpenApiResponse(description="Неверный refresh токен"),
            401: OpenApiResponse(description="Не авторизован"),
        },
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh"]
        success = blacklist_token(refresh_token)

        if success:
            return Response({"message": "Успешный выход"}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Неверный refresh токен"}, status=status.HTTP_400_BAD_REQUEST
            )


class UserProfileAPIView(APIView):
    """
    Представление для просмотра профиля пользователя.

    Возвращает информацию о текущем аутентифицированном пользователе.
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Получить профиль пользователя",
        description="Возвращает информацию о текущем аутентифицированном пользователе.",
        tags=["Пользователи"],
        responses={
            200: UserDetailSerializer,
            401: OpenApiResponse(description="Не авторизован"),
        },
    )
    def get(self, request):
        user = request.user
        return Response(UserDetailSerializer(user).data, status=status.HTTP_200_OK)

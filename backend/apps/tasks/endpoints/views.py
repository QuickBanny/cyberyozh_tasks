"""
API представления для управления задачами.
"""

from apps.tasks.domain.entities import TaskStatus
from apps.tasks.endpoints.serializers import (
    DomainCommentSerializer,
    DomainTaskSerializer,
    TaskAssignSerializer,
    TaskCommentCreateSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
)
from apps.tasks.infrastructure.models import TaskModel
from apps.tasks.infrastructure.repositories import (
    DjangoCommentRepository,
    DjangoTaskRepository,
)
from apps.tasks.services.comment_service import CommentService
from apps.tasks.services.task_services import TaskService
from apps.users.infrastructure.repositories import DjangoUserRepository
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@extend_schema_view(
    list=extend_schema(
        summary="Получить список задач",
        description="Возвращает пагинированный список всех задач в системе.",
        tags=["Задачи"],
        responses={
            200: DomainTaskSerializer(many=True),
            401: OpenApiResponse(description="Не авторизован"),
        },
    ),
    create=extend_schema(
        summary="Создать новую задачу",
        description="Создает новую задачу в системе. "
        "Автор задачи устанавливается автоматически.",
        tags=["Задачи"],
        request=TaskCreateSerializer,
        responses={
            201: DomainTaskSerializer,
            400: OpenApiResponse(description="Неверные данные"),
            401: OpenApiResponse(description="Не авторизован"),
        },
    ),
    retrieve=extend_schema(
        summary="Получить задачу по ID",
        description="Возвращает детальную информацию о задаче, включая комментарии.",
        tags=["Задачи"],
        responses={
            200: DomainTaskSerializer,
            404: OpenApiResponse(description="Задача не найдена"),
            401: OpenApiResponse(description="Не авторизован"),
        },
    ),
    update=extend_schema(
        summary="Обновить задачу",
        description="Обновляет все поля задачи.",
        tags=["Задачи"],
        request=TaskUpdateSerializer,
        responses={
            200: DomainTaskSerializer,
            400: OpenApiResponse(description="Неверные данные"),
            404: OpenApiResponse(description="Задача не найдена"),
            401: OpenApiResponse(description="Не авторизован"),
        },
    ),
    partial_update=extend_schema(
        summary="Частично обновить задачу",
        description="Обновляет отдельные поля задачи.",
        tags=["Задачи"],
        request=TaskUpdateSerializer,
        responses={
            200: DomainTaskSerializer,
            400: OpenApiResponse(description="Неверные данные"),
            404: OpenApiResponse(description="Задача не найдена"),
            401: OpenApiResponse(description="Не авторизован"),
        },
    ),
    destroy=extend_schema(
        summary="Удалить задачу",
        description="Полностью удаляет задачу из системы.",
        tags=["Задачи"],
        responses={
            204: OpenApiResponse(description="Задача успешно удалена"),
            404: OpenApiResponse(description="Задача не найдена"),
            401: OpenApiResponse(description="Не авторизован"),
        },
    ),
)
class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления задачами.

    Предоставляет CRUD операции для работы с задачами,
    а также дополнительные действия для назначения,
    завершения и работы с комментариями.
    """

    queryset = TaskModel.objects.all()
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Инициализация сервисов
        task_repo = DjangoTaskRepository()
        user_repo = DjangoUserRepository()
        comment_repo = DjangoCommentRepository()
        self.task_service = TaskService(task_repo, user_repo)
        self.comment_service = CommentService(comment_repo, task_repo, user_repo)

    def get_queryset(self):
        """Оптимизированный queryset с предзагрузкой связанных объектов."""
        return TaskModel.objects.select_related(
            "assigned_to", "created_by"
        ).prefetch_related("comments__author")

    def list(self, request, *args, **kwargs):
        """Получение списка задач через сервисный слой."""
        # Используем сервис для получения всех задач
        tasks = self.task_service.get_all_tasks()

        # Используем стандартную пагинацию Django REST Framework
        page = self.paginate_queryset(tasks)
        if page is not None:
            serializer = DomainTaskSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = DomainTaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Получение задачи через сервисный слой."""
        task_id = int(kwargs["pk"])
        task = self.task_service.get_task_by_id(task_id)

        if not task:
            return Response(
                {"error": "Задача не найдена"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = DomainTaskSerializer(task)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """Обновление задачи через сервисный слой."""
        partial = kwargs.pop("partial", False)
        task_id = int(kwargs["pk"])

        serializer = TaskUpdateSerializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        try:
            # Преобразуем assigned_to в int, если это не None
            assigned_to_value = serializer.validated_data.get("assigned_to")
            assigned_to_id = None
            if assigned_to_value is not None:
                if hasattr(assigned_to_value, "id"):  # Если это объект User
                    assigned_to_id = assigned_to_value.id
                else:
                    assigned_to_id = assigned_to_value
            # Используем сервис для обновления задачи
            updated_task = self.task_service.update_task(
                task_id=task_id,
                title=serializer.validated_data.get("title"),
                description=serializer.validated_data.get("description"),
                assigned_to_id=assigned_to_id,
            )
            if updated_task:
                serializer = DomainTaskSerializer(updated_task)
                return Response(serializer.data)
            else:
                return Response(
                    {"error": "Задача не найдена"}, status=status.HTTP_404_NOT_FOUND
                )

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """Удаление задачи через сервисный слой."""
        task_id = int(kwargs["pk"])

        if self.task_service.delete_task(task_id):
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"error": "Задача не найдена"}, status=status.HTTP_404_NOT_FOUND
            )

    def create(self, request, *args, **kwargs):
        """Создание задачи через сервисный слой."""
        serializer = TaskCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Используем сервис для создания задачи
            task = self.task_service.create_task(
                title=serializer.validated_data["title"],
                description=serializer.validated_data.get("description", ""),
                created_by_id=request.user.id,
                assigned_to_id=serializer.validated_data.get("assigned_to"),
            )

            serializer = DomainTaskSerializer(task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Назначить задачу пользователю",
        description="Назначает задачу конкретному пользователю по его ID.",
        tags=["Задачи"],
        request=TaskAssignSerializer,
        responses={
            200: DomainTaskSerializer,
            400: OpenApiResponse(description="Неверные данные"),
            404: OpenApiResponse(description="Задача не найдена"),
            401: OpenApiResponse(description="Не авторизован"),
        },
        parameters=[
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID задачи",
            )
        ],
    )
    @action(detail=True, methods=["patch"])
    def assign(self, request, pk=None):
        """Назначение задачи пользователю."""
        user_id = request.data.get("assigned_to")

        if user_id is None:
            return Response(
                {"error": "Необходимо указать ID пользователя"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Преобразуем user_id в int, если это не None
            user_id_int = None
            if user_id is not None:
                if hasattr(user_id, "id"):  # Если это объект User
                    user_id_int = user_id.id
                else:
                    user_id_int = int(user_id)

            # Используем сервис для назначения задачи
            updated_task = self.task_service.assign_task(int(pk), user_id_int)

            if updated_task:
                serializer = DomainTaskSerializer(updated_task)
                return Response(serializer.data)
            else:
                return Response(
                    {"error": "Задача не найдена"}, status=status.HTTP_404_NOT_FOUND
                )

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Отметить задачу как выполненную",
        description="Изменяет статус задачи на 'completed'.",
        tags=["Задачи"],
        responses={
            200: DomainTaskSerializer,
            404: OpenApiResponse(description="Задача не найдена"),
            400: OpenApiResponse(description="Ошибка обновления"),
            401: OpenApiResponse(description="Не авторизован"),
        },
        parameters=[
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID задачи",
            )
        ],
    )
    @action(detail=True, methods=["patch"])
    def complete(self, request, pk=None):
        """Отметка задачи как выполненной."""
        try:
            # Используем сервис для обновления статуса
            updated_task = self.task_service.update_task_status(
                int(pk), TaskStatus.COMPLETED
            )

            if updated_task:
                serializer = DomainTaskSerializer(updated_task)
                return Response(serializer.data)
            else:
                return Response(
                    {"error": "Задача не найдена"}, status=status.HTTP_404_NOT_FOUND
                )

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Работа с комментариями к задаче",
        description="GET: Получает все комментарии к задаче. "
        "POST: Создает новый комментарий.",
        tags=["Комментарии"],
        request={"application/json": TaskCommentCreateSerializer},
        responses={
            200: DomainCommentSerializer(many=True),
            201: DomainCommentSerializer,
            400: OpenApiResponse(description="Неверные данные"),
            404: OpenApiResponse(description="Задача не найдена"),
            401: OpenApiResponse(description="Не авторизован"),
        },
        parameters=[
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID задачи",
            )
        ],
    )
    @action(detail=True, methods=["get", "post"])
    def comments(self, request, pk=None):
        """Получение и создание комментариев к задаче."""
        if request.method == "GET":
            # Используем сервис для получения комментариев
            domain_comments = self.comment_service.get_task_comments(int(pk))

            serializer = DomainCommentSerializer(domain_comments, many=True)
            return Response(serializer.data)

        elif request.method == "POST":
            serializer = TaskCommentCreateSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    # Используем сервис для создания комментария
                    domain_comment = self.comment_service.create_comment(
                        task_id=int(pk),
                        content=serializer.validated_data["content"],
                        author_id=request.user.id,
                    )

                    serializer = DomainCommentSerializer(domain_comment)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)

                except ValueError as e:
                    return Response(
                        {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
                    )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import serializers


class TaskCreateSerializer(serializers.Serializer):
    """Сериализатор для создания задач."""

    title = serializers.CharField(
        max_length=200, required=True, help_text="Название задачи (обязательное поле)"
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Подробное описание задачи (необязательное)",
    )
    status = serializers.CharField(
        max_length=15, required=False, help_text="Статус задачи (по умолчанию: pending)"
    )
    assigned_to = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="ID пользователя, которому назначается задача (необязательное)",
    )

    def validate_title(self, value):
        """Валидация заголовка."""
        if not value.strip():
            raise serializers.ValidationError("Заголовок не может быть пустым.")
        return value.strip()


class TaskUpdateSerializer(serializers.Serializer):
    """Сериализатор для обновления задач."""

    title = serializers.CharField(
        max_length=200, required=False, help_text="Новое название задачи"
    )
    description = serializers.CharField(
        required=False, allow_blank=True, help_text="Новое описание задачи"
    )
    status = serializers.CharField(
        max_length=15,
        required=False,
        help_text="Новый статус задачи (pending, in_progress, completed, cancelled)",
    )
    assigned_to = serializers.IntegerField(
        required=False, allow_null=True, help_text="ID нового исполнителя задачи"
    )

    def validate_title(self, value):
        """Валидация заголовка."""
        if value is not None and not value.strip():
            raise serializers.ValidationError("Заголовок не может быть пустым.")
        return value.strip() if value else value


class TaskStatusUpdateSerializer(serializers.Serializer):
    """Сериализатор для обновления статуса задачи."""

    status = serializers.CharField(
        max_length=15,
        required=True,
        help_text="Новый статус задачи (pending, in_progress, completed, cancelled)",
    )

    def validate_status(self, value):
        """Валидация статуса."""
        valid_statuses = ["pending", "in_progress", "completed"]
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Недопустимый статус. Доступные: {', '.join(valid_statuses)}"
            )
        return value


class TaskAssignSerializer(serializers.Serializer):
    """Сериализатор для назначения задачи."""

    assigned_to = serializers.IntegerField(
        required=True, help_text="ID пользователя, которому назначается задача"
    )


class TaskCommentCreateSerializer(serializers.Serializer):
    """Сериализатор для создания комментариев."""

    content = serializers.CharField(required=True, help_text="Текст комментария")

    def validate_content(self, value):
        """Валидация содержимого комментария."""
        if not value.strip():
            raise serializers.ValidationError("Комментарий не может быть пустым.")
        return value.strip()


class DomainUserSerializer(serializers.Serializer):
    """Сериализатор для доменных объектов User."""

    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    first_name = serializers.CharField(
        read_only=True, allow_null=True, allow_blank=True
    )
    last_name = serializers.CharField(read_only=True, allow_null=True, allow_blank=True)
    email = serializers.CharField(read_only=True, allow_null=True, allow_blank=True)


class DomainTaskSerializer(serializers.Serializer):
    """Сериализатор для доменных объектов Task."""

    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    status = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    assigned_to = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    def get_status(self, obj):
        """Получить статус задачи."""
        if hasattr(obj.status, "value"):
            return obj.status.value
        return str(obj.status)

    def get_assigned_to(self, obj):
        """Получить назначенного пользователя."""
        if not obj.assigned_to:
            return None
        return DomainUserSerializer(obj.assigned_to).data

    def get_created_by(self, obj):
        """Получить создателя задачи."""
        if not obj.created_by:
            return None
        return DomainUserSerializer(obj.created_by).data

    def get_comments(self, obj):
        """Получить комментарии к задаче."""
        if not obj.comments:
            return []

        return DomainCommentSerializer(obj.comments, many=True).data


class DomainCommentSerializer(serializers.Serializer):
    """Сериализатор для доменных объектов TaskComment."""

    id = serializers.IntegerField(read_only=True)
    content = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    author = DomainUserSerializer(read_only=True)

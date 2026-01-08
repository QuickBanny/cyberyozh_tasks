"""
Административный интерфейс для управления задачами.
"""

from django.contrib import admin

from .models import TaskCommentModel, TaskModel


@admin.register(TaskModel)
class TaskAdmin(admin.ModelAdmin):
    """Административный интерфейс для задач."""

    list_display = ["title", "status", "assigned_to", "created_by", "created_at"]

    list_filter = ["status", "created_at", "assigned_to", "created_by"]

    search_fields = ["title", "description"]

    list_editable = ["status", "assigned_to"]

    date_hierarchy = "created_at"

    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Основная информация", {"fields": ("title", "description", "status")}),
        ("Назначение", {"fields": ("assigned_to", "created_by")}),
        ("Временные рамки", {"fields": ("created_at", "updated_at")}),
    )

    def get_queryset(self, request):
        """Оптимизация запросов."""
        return super().get_queryset(request).select_related("assigned_to", "created_by")


@admin.register(TaskCommentModel)
class TaskCommentAdmin(admin.ModelAdmin):
    """Административный интерфейс для комментариев."""

    list_display = ["task", "author", "content_preview", "created_at"]

    list_filter = ["created_at", "author"]

    search_fields = ["content", "task__title"]

    readonly_fields = ["created_at"]

    def content_preview(self, obj):
        """Предварительный просмотр содержания комментария."""
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "Содержание"

    def get_queryset(self, request):
        """Оптимизация запросов."""
        return super().get_queryset(request).select_related("task", "author")

"""
Django модели для инфраструктурного слоя.
Адаптеры для работы с базой данных.
"""

from django.contrib.auth.models import User
from django.db import models


class TaskModel(models.Model):
    """Django модель задачи."""

    STATUS_CHOICES = [
        ("pending", "Ожидает"),
        ("in_progress", "В работе"),
        ("completed", "Завершена"),
        ("cancelled", "Отменена"),
    ]

    title = models.CharField(
        "Название", max_length=200, help_text="Краткое название задачи"
    )

    description = models.TextField(
        "Описание", blank=True, help_text="Подробное описание задачи"
    )

    status = models.CharField(
        "Статус",
        max_length=15,
        choices=STATUS_CHOICES,
        default="pending",
        help_text="Текущий статус задачи",
    )

    created_at = models.DateTimeField(
        "Дата создания", auto_now_add=True, help_text="Дата и время создания задачи"
    )

    updated_at = models.DateTimeField(
        "Дата обновления", auto_now=True, help_text="Дата и время последнего обновления"
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Исполнитель",
        related_name="assigned_tasks",
        help_text="Пользователь, назначенный для выполнения задачи",
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Создатель",
        related_name="created_tasks",
        help_text="Пользователь, создавший задачу",
    )

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class TaskCommentModel(models.Model):
    """Django модель комментария к задаче."""

    task = models.ForeignKey(
        TaskModel,
        on_delete=models.CASCADE,
        verbose_name="Задача",
        related_name="comments",
        help_text="Задача, к которой относится комментарий",
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор",
        help_text="Автор комментария",
    )

    content = models.TextField("Содержание", help_text="Текст комментария")

    created_at = models.DateTimeField(
        "Дата создания",
        auto_now_add=True,
        help_text="Дата и время создания комментария",
    )

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["-created_at"]

    def __str__(self):
        return f'Комментарий к "{self.task.title}" от {self.author.username}'

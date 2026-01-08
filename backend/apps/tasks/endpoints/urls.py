"""
URL маршруты для API управления задачами.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TaskViewSet

# Создание роутера для автоматической генерации URL
router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("", include(router.urls)),
]

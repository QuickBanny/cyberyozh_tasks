"""
Docker-specific settings for the Django project.
"""

import os

import dj_database_url

from .base import *  # noqa: F403,F401

# Database configuration for Docker
DATABASES = {
    "default": dj_database_url.parse(
        os.environ.get(
            "DATABASE_URL", "postgresql://postgres:postgres@db:5432/cyberyozh"
        )
    )
}

# Security settings
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "backend"]

# Static files configuration for Docker
STATIC_ROOT = "/app/staticfiles"
MEDIA_ROOT = "/app/media"

# CORS settings for Docker
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://frontend:3000",
]

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

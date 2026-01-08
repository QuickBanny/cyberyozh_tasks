"""
Инфраструктурный слой аутентификации.
"""

from .repositories import DjangoUserRepository

__all__ = [
    "DjangoUserRepository",
]

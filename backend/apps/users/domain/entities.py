from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class UserId:
    value: int


@dataclass(frozen=True)
class User:
    """Доменная модель пользователя."""

    id: int
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]

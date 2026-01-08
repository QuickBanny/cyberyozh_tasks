from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from apps.tasks.domain.entities import Task, TaskComment


@dataclass(frozen=True)
class UserDTO:
    """DTO для пользователя."""

    id: int
    username: str
    first_name: str
    last_name: str
    email: str


@dataclass(frozen=True)
class CommentDTO:
    """DTO для комментария."""

    id: int
    content: str
    author: UserDTO
    created_at: datetime


@dataclass(frozen=True)
class TaskDTO:
    """DTO для задачи."""

    id: int
    title: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime
    created_by: UserDTO
    assigned_to: Optional[UserDTO]
    comments: List[CommentDTO]


class TaskMapper:
    """Маппер для преобразования доменных сущностей в DTO."""

    @staticmethod
    def user_to_dto(user) -> UserDTO:
        """Преобразует пользователя в DTO."""
        return UserDTO(
            id=user.id,
            username=user.username,
            first_name=user.first_name or "",
            last_name=user.last_name or "",
            email=user.email or "",
        )

    @staticmethod
    def comment_to_dto(comment: TaskComment, author_user) -> CommentDTO:
        """Преобразует комментарий в DTO."""
        return CommentDTO(
            id=comment.id,
            content=comment.content,
            author=TaskMapper.user_to_dto(author_user),
            created_at=comment.created_at,
        )

    @staticmethod
    def to_dto(
        task: Task, created_by_user, assigned_to_user=None, comment_users=None
    ) -> TaskDTO:
        """Преобразует задачу в DTO."""
        comments_dto = []
        if task.comments and comment_users:
            for comment in task.comments:
                author_user = comment_users.get(comment.author.value)
                if author_user:
                    comments_dto.append(TaskMapper.comment_to_dto(comment, author_user))

        return TaskDTO(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status.value,
            created_at=task.created_at,
            updated_at=task.updated_at,
            created_by=TaskMapper.user_to_dto(created_by_user),
            assigned_to=TaskMapper.user_to_dto(assigned_to_user)
            if assigned_to_user
            else None,
            comments=comments_dto,
        )

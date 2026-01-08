from apps.users.domain.entities import UserId
from apps.users.domain.exceptions import (
    EmailAlreadyExists,
    UsernameAlreadyExists,
    UserNotFound,
)


class UserService:
    def __init__(self, user_repo):
        self.user_repo = user_repo

    def register_user(
        self, username: str, email: str, password: str, first_name=None, last_name=None
    ):
        if self.user_repo.exists_by_email(email):
            raise EmailAlreadyExists(f"Пользователь с email {email} уже существует")

        if self.user_repo.exists_by_username(username):
            raise UsernameAlreadyExists(
                f"Пользователь с username {username} уже существует"
            )

        user = self.user_repo.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        return UserId(user.id)

    def get_user_by_id(self, user_id: int):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFound()
        return user

from apps.users.domain.entities import User as DomainUser
from django.contrib.auth import get_user_model

DjangoUser = get_user_model()


class DjangoUserRepository:
    def _to_domain(self, django_user: DjangoUser) -> DomainUser:
        """Преобразование Django User в доменный User."""
        return DomainUser(
            id=django_user.id,
            username=django_user.username,
            first_name=django_user.first_name,
            last_name=django_user.last_name,
            email=django_user.email,
        )

    def exists_by_email(self, email: str) -> bool:
        return DjangoUser.objects.filter(email=email).exists()

    def exists_by_username(self, username: str) -> bool:
        return DjangoUser.objects.filter(username=username).exists()

    def create_user(
        self, username: str, email: str, password: str, first_name=None, last_name=None
    ):
        # Обеспечиваем, что first_name и last_name не None для избежания NULL constraint
        django_user = DjangoUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name or "",
            last_name=last_name or "",
        )
        return self._to_domain(django_user)

    def get_by_id(self, user_id: int):
        try:
            django_user = DjangoUser.objects.get(id=user_id)
            return self._to_domain(django_user)
        except DjangoUser.DoesNotExist:
            return None

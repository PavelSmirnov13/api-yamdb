from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models


ME = 'me'


class Role(models.TextChoices):
    """Роли у пользователей."""

    USER = 'user', 'Пользователь'
    MODERATOR = 'moderator', 'Модератор'
    ADMIN = 'admin', 'Администратор'


def validate_username(value):
    """Проверка запрещенного имени пользователя."""
    if value.lower() == ME:
        raise ValidationError(f'Имя {ME} использовать запрещено!')


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        "Имя пользователя", max_length=150,
        unique=True, validators=[UnicodeUsernameValidator(), validate_username]
    )
    email = models.EmailField('Почта', max_length=254, unique=True)
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Роль', max_length=32, choices=Role.choices, default=Role.USER,
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def is_admin(self):
        """Проверка пользователя на роль Администратор."""
        return self.role == Role.ADMIN or self.is_superuser or self.is_staff

    def is_moderator(self):
        """Проверка пользователя на роль Модератора."""
        return self.role == Role.MODERATOR

import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, IntegrityError
from django.utils.text import slugify

from .constants import (
    MAX_LENGTH_EMAIL,
    MAX_LENGTH_NAME,
    MAX_LENGTH_ROLE,
    MAX_LENGTH_SLUG,
    MAX_LENGTH_USERNAME,
)


ME = 'me'


class Role(models.TextChoices):
    """Роли у пользователей."""

    USER = 'user', 'Пользователь'
    MODERATOR = 'moderator', 'Модератор'
    ADMIN = 'admin', 'Администратор'


def validate_username(username):
    """Проверка запрещенного имени пользователя."""
    if username.lower() == ME:
        raise ValidationError(f'Имя {ME} использовать запрещено!')


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        'Имя пользователя',
        max_length=MAX_LENGTH_USERNAME,
        unique=True,
        validators=[UnicodeUsernameValidator(), validate_username],
    )
    email = models.EmailField(
        'Почта',
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
    )
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Роль',
        max_length=MAX_LENGTH_ROLE,
        choices=Role.choices,
        default=Role.USER,
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        """Проверка пользователя на роль Администратор."""
        return self.role == Role.ADMIN or self.is_superuser or self.is_staff

    @property
    def is_moderator(self):
        """Проверка пользователя на роль Модератора."""
        return (
            self.role == Role.MODERATOR
            or self.is_superuser
            or self.is_staff
        )


class Category(models.Model):
    """Модель категории произведения.

    Категории определяют тип произведения.
    """

    name = models.CharField(
        'Название',
        max_length=MAX_LENGTH_NAME,
        help_text='Название категории',
    )
    slug = models.SlugField(
        'Слаг',
        unique=True,
        max_length=MAX_LENGTH_SLUG,
        help_text='Уникальный идентификатор для URL',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель жанра произведения.

    Жанры определяют стиль произведения.
    """

    name = models.CharField(
        'Название',
        max_length=MAX_LENGTH_NAME,
        help_text='Название жанра',
    )
    slug = models.SlugField(
        'Слаг',
        unique=True,
        max_length=MAX_LENGTH_SLUG,
        help_text='Уникальный идентификатор для URL',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель произведения (книга, фильм, музыка)."""

    name = models.CharField(
        'Название',
        max_length=MAX_LENGTH_NAME,
        help_text='Название произведения',
    )
    slug = models.SlugField(
        'Слаг',
        unique=True,
        blank=True,
        max_length=MAX_LENGTH_SLUG,
        help_text='Уникальный идентификатор для URL',
    )
    year = models.SmallIntegerField(
        'Год',
        validators=[
            MinValueValidator(0),
            MaxValueValidator(9999),
        ],
        help_text='Год выпуска произведения',
    )
    description = models.TextField(
        'Описание',
        blank=True,
        help_text='Описание произведения (необязательно)',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категория',
        help_text='Категория произведения',
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанры',
        help_text='Жанры произведения',
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('-year',)

    def _slug_exists(self, slug):
        """Проверяет, существует ли slug в базе."""
        qs = Title.objects.filter(slug=slug)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        return qs.exists()

    def _generate_base_slug(self):
        """Генерирует базовый слаг из названия или UUID."""
        return slugify(self.name) or f'title-{uuid.uuid4().hex[:8]}'

    def _generate_candidate_slug(self, base_slug):
        """Генерирует уникальный слаг с проверкой."""
        if self.year:
            candidate = f'{base_slug}-{self.year}'
            if not self._slug_exists(candidate):
                return candidate
        return f'{base_slug}-{uuid.uuid4().hex[:4]}'

    def save(self, *args, **kwargs):
        """Сохраняет объект с гарантированно уникальным слагом."""
        if not self.slug:
            base_slug = self._generate_base_slug()
            candidate = self._generate_candidate_slug(base_slug)
            attempt = 0
            while self._slug_exists(candidate) and attempt < 10:
                attempt += 1
                candidate = f'{base_slug}-{uuid.uuid4().hex[:4]}'
            self.slug = candidate

        try:
            super().save(*args, **kwargs)
        except IntegrityError:
            self.slug = f'{self.slug}-{uuid.uuid4().hex[:4]}'
            super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель для хранения отзывов и оценок на произведения."""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор',
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
    )
    text = models.TextField('Текст')
    score = models.PositiveSmallIntegerField(
        'Оценка',
        validators=[
            MinValueValidator(1, 'Оценка не может быть меньше 1'),
            MaxValueValidator(10, 'Оценка не может быть больше 10'),
        ],
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_review',
            )
        ]

    def __str__(self):
        return f'{self.author} - {self.title}'


class Comment(models.Model):
    """Модель для хранения комментариев к отзывам."""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв',
    )
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.author} - {self.review}'

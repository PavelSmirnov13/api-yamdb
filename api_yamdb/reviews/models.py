from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models, IntegrityError
from django.utils.text import slugify
import uuid

ME = 'me'


class Role(models.TextChoices):
    """Роли пользователей в системе."""
    USER = 'user', 'Пользователь'
    MODERATOR = 'moderator', 'Модератор'
    ADMIN = 'admin', 'Администратор'


def validate_username(value):
    """Запрещает использование имени 'me' в качестве username."""
    if value.lower() == ME:
        raise ValidationError(f'Имя {ME} использовать запрещено!')


class User(AbstractUser):
    """
    Кастомная модель пользователя.

    Расширяет стандартную модель Django:
    - Добавляет поле role (роль в системе)
    - Добавляет поле bio (биография)
    - Использует email как уникальное поле
    - Запрещает username = 'me'
    """
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[UnicodeUsernameValidator(), validate_username]
    )
    email = models.EmailField(max_length=254, unique=True)
    bio = models.TextField(blank=True)
    role = models.CharField(
        max_length=32, choices=Role.choices, default=Role.USER
    )

    class Meta:
        ordering = ('username',)

    def __str__(self):
        return self.username

    def is_admin(self):
        """Проверяет, является ли пользователь администратором."""
        return self.role == Role.ADMIN or self.is_superuser or self.is_staff

    def is_moderator(self):
        """Проверяет, является ли пользователь модератором."""
        return self.role == Role.MODERATOR


class Category(models.Model):
    """
    Модель категории произведения.

    Категории определяют тип произведения
    (например, 'Фильмы', 'Книги', 'Музыка').
    Одно произведение может быть привязано только к одной категории.
    """
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    """
    Модель жанра произведения.

    Жанры определяют стиль произведения (например, 'Рок', 'Сказка', 'Артхаус').
    Одно произведение может иметь несколько жанров.
    """
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    """
    Модель произведения (книга, фильм, музыка).

    Произведение — это основной объект, к которому пользователи пишут отзывы.
    Содержит информацию о названии, годе выпуска, описании,
    а также связь с категорией и жанрами.
    """
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, blank=True, max_length=256)
    year = models.IntegerField()
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles'
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles'
    )
    rating = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def _slug_exists(self, slug):
        """Проверяет, существует ли slug в базе (исключая текущий объект)."""
        qs = Title.objects.filter(slug=slug)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        return qs.exists()

    def _generate_base_slug(self):
        """Генерирует базовый слаг из названия или UUID."""
        base_slug = slugify(self.name)
        return base_slug or f"title-{uuid.uuid4().hex[:8]}"

    def _generate_candidate_slug(self, base_slug):
        """Генерирует уникальный слаг с проверкой."""
        if self.year:
            candidate = f"{base_slug}-{self.year}"
            if not self._slug_exists(candidate):
                return candidate
        # Если год не указан или занят — добавляем случайный суффикс
        return f"{base_slug}-{uuid.uuid4().hex[:4]}"

    def save(self, *args, **kwargs):
        """Сохраняет объект с гарантированно уникальным слагом."""
        if not self.slug:
            base_slug = self._generate_base_slug()
            candidate = self._generate_candidate_slug(base_slug)

            # Гарантируем уникальность с защитой от бесконечного цикла
            attempt = 0
            while self._slug_exists(candidate) and attempt < 10:
                attempt += 1
                if self.year and attempt == 1:
                    # Сначала пробуем с годом
                    candidate = f"{base_slug}-{self.year}"
                else:
                    # Добавляем случайный суффикс
                    candidate = f"{base_slug}-{uuid.uuid4().hex[:4]}"
            self.slug = candidate

        try:
            super().save(*args, **kwargs)
        except IntegrityError:
            # Финальный запасной вариант
            self.slug = f"{self.slug}-{uuid.uuid4().hex[:4]}"
            super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель для хранения отзывов и оценок на произведения."""
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField()
    score = models.IntegerField()
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author} - {self.title}'


class Comment(models.Model):
    """Модель для хранения комментариев к отзывам."""
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author} - {self.review}'

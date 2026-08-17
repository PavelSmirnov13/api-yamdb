from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
import uuid
from django.db import IntegrityError


ME = 'me'


class Role(models.TextChoices):
    USER = 'user', 'Пользователь'
    MODERATOR = 'moderator', 'Модератор'
    ADMIN = 'admin', 'Администратор'


def validate_username(value):
    if value.lower() == ME:
        raise ValidationError(f'Имя {ME} использовать запрещено!')


class User(AbstractUser):
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
        return self.role == Role.ADMIN or self.is_superuser or self.is_staff

    def is_moderator(self):
        return self.role == Role.MODERATOR


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
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
        qs = Title.objects.filter(slug=slug)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        return qs.exists()

    def _generate_base_slug(self):
        base_slug = slugify(self.name)
        return base_slug or f"title-{uuid.uuid4().hex[:8]}"

    def _generate_candidate_slug(self, base_slug):
        if self.year:
            candidate = f"{base_slug}-{self.year}"
            if not self._slug_exists(candidate):
                return candidate
        return f"{base_slug}-{uuid.uuid4().hex[:4]}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = self._generate_base_slug()
            self.slug = self._generate_candidate_slug(base_slug)
        try:
            super().save(*args, **kwargs)
        except IntegrityError:
            self.slug = f"{self.slug}-{uuid.uuid4().hex[:4]}"
            super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Review(models.Model):
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

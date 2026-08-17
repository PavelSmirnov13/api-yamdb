from django.db import models


class Category(models.Model):
    """
    Модель категории произведения.

    Категории определяют тип произведения
    (например, 'Фильмы', 'Книги', 'Музыка').
    Одно произведение может быть привязано только к одной категории.
    """
    name = models.CharField(
        max_length=256,
        help_text='Название категории'
    )
    slug = models.SlugField(
        unique=True,
        help_text='Уникальный идентификатор для URL (например, "films")'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        """Возвращает название категории."""
        return self.name

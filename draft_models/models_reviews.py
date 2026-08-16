from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    """Модель для хранения отзывов и оценок на произведения."""

    title = models.IntegerField(
        help_text="Заглушка под Title ForeignKey"
    )
    text = models.TextField()
    author = models.IntegerField(
        help_text="Заглушка под User ForeignKey"
    )
    score = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )
    pub_date = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    """Модель для хранения комментариев к отзывам."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    author = models.IntegerField(
        help_text="Заглушка под User ForeignKey"
    )
    pub_date = models.DateTimeField(auto_now_add=True)

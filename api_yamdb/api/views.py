from rest_framework import viewsets, filters, mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

from reviews.models import Category, Genre, Title, Review, Comment
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    ReviewSerializer,
    CommentSerializer
)
from .permissions import IsAdminOrReadOnly, IsAuthorOrModeratorOrAdminOrReadOnly


class CategoryViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Вьюсет для модели Category.
    Поддерживает создание, удаление и список категорий.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"
    pagination_class = PageNumberPagination


class GenreViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Genre.
    Полный CRUD для жанров.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Title.
    Поддерживает фильтрацию по категории, жанру и году.
    Оптимизирован с помощью select_related и prefetch_related.
    """
    queryset = (
        Title.objects.all()
        .select_related("category")
        .prefetch_related("genre")
    )
    serializer_class = TitleSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["category", "genre", "year"]
    ordering_fields = ["name", "year"]


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Review.
    Работает с отзывами на конкретное произведение.
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrModeratorOrAdminOrReadOnly]

    def get_title(self):
        """Возвращает объект Title по id из URL."""
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, pk=title_id)

    def get_queryset(self):
        """Возвращает все отзывы на конкретное произведение."""
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        """Сохраняет отзыв с автором и произведением."""
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Comment.
    Работает с комментариями к конкретному отзыву.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrModeratorOrAdminOrReadOnly]

    def get_review(self):
        """Возвращает объект Review по id из URL."""
        return get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
        )

    def get_queryset(self):
        """Возвращает все комментарии к конкретному отзыву."""
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        """Сохраняет комментарий с автором и отзывом."""
        serializer.save(author=self.request.user, review=self.get_review())

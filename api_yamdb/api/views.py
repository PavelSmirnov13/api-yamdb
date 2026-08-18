from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from api_yamdb.models import Category, Genre, Title
from .serializers import CategorySerializer, GenreSerializer, TitleSerializer
from .permissions import IsAdminOrReadOnly


class CategoryViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Category."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class GenreViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Genre."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Title с фильтрацией и оптимизацией запросов."""
    queryset = (
        Title.objects
        .all()
        .select_related('category')
        .prefetch_related('genre')
    )
    serializer_class = TitleSerializer
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['category', 'genre', 'year']
    ordering_fields = ['name', 'year']

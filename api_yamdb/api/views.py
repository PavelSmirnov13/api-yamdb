from django.db import IntegrityError
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, filters, mixins, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Title, Review, User
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    ReviewSerializer,
    CommentSerializer,
    SignUpSerializer,
    TokenSerializer,
    UserSerializer,
    MeSerializer,
)
from .permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
    IsAuthorOrModeratorOrAdminOrReadOnly
)


User = get_user_model()


class CategoryViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Вьюсет для модели Category."""
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    pagination_class = PageNumberPagination


class TitleViewSet(viewsets.ModelViewSet):
    queryset = (
        Title.objects.all()
        .annotate(rating=Avg('reviews__score'))
        .order_by('name')
        .select_related('category')
        .prefetch_related('genre')
    )
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = ['category__slug', 'year', 'name']
    search_fields = ['name']
    ordering_fields = ['name', 'year']
    http_method_names = ['get', 'post', 'patch', 'delete']
    pagination_class = PageNumberPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        genre_slug = self.request.query_params.get('genre')
        category_slug = self.request.query_params.get('category')

        if genre_slug:
            queryset = queryset.filter(genre__slug=genre_slug)
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        return queryset

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class GenreViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с отзывами."""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrModeratorOrAdminOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, pk=title_id)

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с комментариями."""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrModeratorOrAdminOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_review(self):
        return get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
        )

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """Регистрация пользователей."""

    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    email = serializer.validated_data['email']
    try:
        user, _ = User.objects.get_or_create(username=username, email=email)
    except IntegrityError:
        return Response(
            {'error': 'Такой username или email уже заняты'},
            status=status.HTTP_400_BAD_REQUEST
        )
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        'Код подтверждения',
        f'Ваш код {confirmation_code}',
        settings.DEFAULT_FROM_EMAIL,
        [email]
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def token_generate(request):
    """Выдаёт JWT-токен в обмен на код подверждения."""

    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    user = get_object_or_404(User, username=username)
    confirmation_code = serializer.validated_data['confirmation_code']
    if not default_token_generator.check_token(user, confirmation_code):
        return Response(
            {'confirmation_code': 'Неверный код подтверждения'},
            status=status.HTTP_400_BAD_REQUEST
        )
    new_token = AccessToken.for_user(user)
    return Response({'token': str(new_token)}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'username'
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']
    http_method_names = ['get', 'post', 'patch', 'delete', 'options', 'head']

    @action(detail=False,
            methods=('get', 'patch'),
            permission_classes=[IsAuthenticated]
            )
    def me(self, request):
        if request.method == 'PATCH':
            serializer = MeSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        serializer = MeSerializer(request.user)
        return Response(serializer.data)

from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers
from reviews.models import (
    Category,
    Genre,
    Title,
    Review,
    Comment,
    User,
    validate_username,
)
from reviews.constants import MAX_LENGTH_EMAIL, MAX_LENGTH_USERNAME
from rest_framework.exceptions import NotFound


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class BaseTitleSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для Title."""

    rating = serializers.IntegerField(read_only=True, default=None)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating',
            'description', 'category', 'genre'
        )


class TitleWriteSerializer(BaseTitleSerializer):
    """Сериализатор для создания и обновления Title."""

    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all(),
        allow_empty=False,
    )


class TitleReadSerializer(BaseTitleSerializer):
    """Сериализатор для чтения Title."""

    category = CategorySerializer()
    genre = GenreSerializer(many=True)


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""

    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, attrs):
        request = self.context.get('request')
        if request.method != 'POST':
            return attrs
        title_id = self.context['view'].kwargs.get('title_id')
        if request.user.reviews.filter(title_id=title_id).exists():
            raise serializers.ValidationError(
                'Вы уже оставили отзыв на это произведение.'
            )
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""

    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class SignUpSerializer(serializers.Serializer):
    """Сериализатор для регистрации нового пользователя."""

    username = serializers.CharField(
        max_length=MAX_LENGTH_USERNAME,
        validators=[UnicodeUsernameValidator(), validate_username],
    )
    email = serializers.EmailField(max_length=MAX_LENGTH_EMAIL)

    def validate(self, attrs):
        """Валидация логина и почты."""
        username = attrs['username']
        email = attrs['email']
        conflicts = {}
        if User.objects.filter(
            username=username
        ).exclude(email=email).exists():
            conflicts['username'] = ['Имя занято другим пользователем']
        if User.objects.filter(
            email=email
        ).exclude(username=username).exists():
            conflicts['email'] = ['Почта занята другим пользователем']
        if conflicts:
            raise serializers.ValidationError(conflicts)
        return attrs

    def save(self):
        """Создает пользователя."""
        return User.objects.get_or_create(
            username=self.validated_data['username'],
            email=self.validated_data['email'],
        )[0]


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""

    username = serializers.CharField(max_length=MAX_LENGTH_USERNAME)
    confirmation_code = serializers.CharField()

    def validate(self, attrs):
        """Валидация токена."""
        username = attrs['username']
        user = User.objects.filter(username=username).first()
        if not user:
            raise NotFound('Пользователь не найден')
        confirmation_code = attrs['confirmation_code']
        if not default_token_generator.check_token(user, confirmation_code):
            raise serializers.ValidationError({
                'confirmation_code': 'Неверный код подтверждения!'
            })
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для CRUD Администратора."""

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


class MeSerializer(UserSerializer):
    """Сериализатор для профиля пользователя."""

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)

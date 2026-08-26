from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers
from reviews.models import (
<<<<<<< HEAD
    Category, Genre, Title, Review, Comment, User, validate_username
=======
    Category,
    Genre,
    Title,
    Review,
    Comment,
    User,
    validate_username,
>>>>>>> develop
)


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


<<<<<<< HEAD
class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления Title."""

    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
=======
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
>>>>>>> develop
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
<<<<<<< HEAD
        queryset=Genre.objects.all()
    )
    rating = serializers.IntegerField(read_only=True, default=None)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating',
            'description', 'category', 'genre'
        )


class TitleReadSerializer(serializers.ModelSerializer):
=======
        queryset=Genre.objects.all(),
        allow_empty=False,
    )


class TitleReadSerializer(BaseTitleSerializer):
>>>>>>> develop
    """Сериализатор для чтения Title."""

    category = CategorySerializer()
    genre = GenreSerializer(many=True)
<<<<<<< HEAD
    rating = serializers.IntegerField(read_only=True, default=None)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating',
            'description', 'category', 'genre'
        )
=======
>>>>>>> develop


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""

    author = serializers.SlugRelatedField(
<<<<<<< HEAD
        slug_field='username',
        read_only=True
=======
        slug_field='username', read_only=True
>>>>>>> develop
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

<<<<<<< HEAD
    def validate(self, data):
        request = self.context.get('request')
        if request.method != 'POST':
            return data
        title_id = self.context['view'].kwargs.get('title_id')
        if Review.objects.filter(
            author=request.user, title_id=title_id
        ).exists():
            raise serializers.ValidationError(
                'Вы уже оставили отзыв на это произведение.'
            )
        return data
=======
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
>>>>>>> develop


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""

    author = serializers.SlugRelatedField(
<<<<<<< HEAD
        slug_field='username',
        read_only=True
=======
        slug_field='username', read_only=True
>>>>>>> develop
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class SignUpSerializer(serializers.Serializer):
    """Сериализатор для регистрации нового пользователя."""

    username = serializers.CharField(
        max_length=150,
<<<<<<< HEAD
        validators=[UnicodeUsernameValidator(), validate_username]
=======
        validators=[UnicodeUsernameValidator(), validate_username],
>>>>>>> develop
    )
    email = serializers.EmailField(max_length=254)


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""

    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для CRUD Администратора."""

    class Meta:
        model = User
        fields = (
<<<<<<< HEAD
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
=======
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
>>>>>>> develop
        )


class MeSerializer(UserSerializer):
    """Сериализатор для профиля пользователя."""

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)

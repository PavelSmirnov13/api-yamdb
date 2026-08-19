from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """Права доступа для Администратора."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin()


class IsAdminOrReadOnly(BasePermission):
    """Для Администратора.

    Чтение доступно всем пользователям, включая анонимных.
    Создание, изменение и удаление только Администраторам.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_admin()


class IsAuthorOrStaffOrReadOnly(BasePermission):
    """Для авторизованных пользователей, Администратора, Модератора.

    Разрешает авторизованным пользователям создавать отзыв или комментарий,
    изменять или удалять объект может Автор, Модератор, Администратор.
    """

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin()
            or request.user.is_moderator()
        )

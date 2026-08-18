from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Разрешает создание, изменение и удаление только администраторам."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'admin'


class IsAuthorOrModeratorOrAdminOrReadOnly(permissions.BasePermission):
    """Разрешает редактирование автору, модератору или админу."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
            or request.user.is_superuser
        )

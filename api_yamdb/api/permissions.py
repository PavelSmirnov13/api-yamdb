from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение на редактирование только для администраторов и модераторов.
    Для остальных методов (GET, HEAD, OPTIONS) доступ открыт всем.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_authenticated and (
            request.user.is_admin() or request.user.is_moderator()
        )


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
        return request.user.is_authenticated and (
            obj.author == request.user
            or getattr(request.user, "is_moderator", False)
            or getattr(request.user, "is_admin", False)
            or request.user.is_superuser
        )

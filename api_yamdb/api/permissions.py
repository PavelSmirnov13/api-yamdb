<<<<<<< HEAD
from rest_framework.permissions import BasePermission, SAFE_METHODS
=======
from rest_framework.permissions import (
    BasePermission,
    IsAuthenticatedOrReadOnly,
    SAFE_METHODS,
)
>>>>>>> develop


class IsAdmin(BasePermission):
    """Права доступа для Администратора."""

    def has_permission(self, request, view):
<<<<<<< HEAD
        return request.user.is_authenticated and request.user.is_admin()


class IsAdminOrReadOnly(BasePermission):
    """
    Разрешение на редактирование только для администраторов и модераторов.
=======
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnly(BasePermission):
    """Разрешение на редактирование только для администраторов.

>>>>>>> develop
    Для остальных методов (GET, HEAD, OPTIONS) доступ открыт всем.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
<<<<<<< HEAD
        return request.user.is_authenticated and request.user.is_admin()


class IsAuthorOrModeratorOrAdminOrReadOnly(BasePermission):
    """Разрешает редактирование автору, модератору или админу."""

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
=======
        return request.user.is_authenticated and request.user.is_admin


class IsAuthorOrModeratorOrAdminOrReadOnly(IsAuthenticatedOrReadOnly):
    """Разрешает редактирование автору, модератору или админу."""

    def has_object_permission(self, request, view, review):
        return (
            request.method in SAFE_METHODS
            or review.author == request.user
            or request.user.is_admin
            or request.user.is_moderator
>>>>>>> develop
        )

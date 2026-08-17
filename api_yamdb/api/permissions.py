from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Разрешает создание, изменение и удаление только администраторам."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'admin'

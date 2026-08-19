from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение на редактирование только для администраторов и модераторов.
    Для остальных методов (GET, HEAD, OPTIONS) доступ открыт всем.
    """
    def has_permission(self, request, view):
        # 1. Разрешаем чтение (GET, HEAD, OPTIONS) всем: и гостям, и пользователям, и админам
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 2. Для методов изменения (POST, PUT, PATCH, DELETE) проверяем, что пользователь авторизован
        # И что он является либо админом, либо модератором
        return (
            request.user.is_authenticated 
            and (request.user.is_admin() or request.user.is_moderator())
        ) 

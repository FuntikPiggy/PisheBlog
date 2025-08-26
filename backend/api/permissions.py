from rest_framework import permissions

from recipes.models import Recipe


class AuthorOrReadOnly(permissions.BasePermission):
    """Позволяет только самому пользователю редактировать свои данные."""

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj == request.user
                or isinstance(obj, Recipe) and obj.author == request.user)

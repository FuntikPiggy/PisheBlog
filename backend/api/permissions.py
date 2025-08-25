from rest_framework import permissions


class AuthorOrReadOnly(permissions.BasePermission):
    """Позволяет только самому пользователю редактировать свои данные."""

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj == request.user)

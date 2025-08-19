from rest_framework import permissions


class IsAuthorOrStaff(permissions.BasePermission):
    """Позволяет делать запросы только аутентифицированному пользователю,
    редакитировать объект - владельцу, админу и суперпользователю."""

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or request.user.is_staff


class SelfOrStaffOrReadOnly(permissions.BasePermission):
    """Позволяет делать запросы только аутентифицированному пользователю,
    редакитировать объект - владельцу, админу и суперпользователю."""

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj == request.user or request.user.is_staff)

from rest_framework import permissions


# class IsAuthorOrStaffOrReadOnly(permissions.BasePermission):
#     """Позволяет редактировать объект только
#     его автору, модератору или админу."""
#
#     def has_permission(self, request, view):
#         return request.method in permissions.SAFE_METHODS
#
#     def has_object_permission(self, request, view, obj):
#         return (request.method in permissions.SAFE_METHODS
#                 or obj.author == request.user
#                 or obj == request.user)


class IsAuthorOrStaff(permissions.BasePermission):
    """Позволяет делать запросы только аутентифицированному пользователю,
    редакитировать объект - владельцу, админу и суперпользователю."""

    # def has_permission(self, request, view):
    #     return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or request.user.is_staff


class SelfOrStaffOrReadOnly(permissions.BasePermission):
    """Позволяет делать запросы только аутентифицированному пользователю,
    редакитировать объект - владельцу, админу и суперпользователю."""

    # def has_permission(self, request, view):
    #     return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj == request.user or request.user.is_staff)


# class IsAdmin(permissions.BasePermission):
#     """Позволяет делать запросы только админу и суперпользователю."""
#
#     def has_permission(self, request, view):
#         return request.user.is_authenticated and request.user.is_admin
#
#
# class IsAdminOrReadOnly(IsAdmin):
#     """Позволяет редактировать объект только админу и суперпользователю."""
#
#     def has_permission(self, request, view):
#         return (request.method in permissions.SAFE_METHODS
#                 or super().has_permission(request, view))

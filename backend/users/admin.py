from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import FgUser


@admin.register(FgUser)
class FgUserAdmin(UserAdmin):
    """Настройки раздела пользователей админ-панели."""

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets[1][1]['fields'] = fieldsets[1][1]['fields'] + ('bio',)
        fieldsets[2][1]['fields'] = ('role',) + fieldsets[2][1]['fields']
        return fieldsets

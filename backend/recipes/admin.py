from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Tag, Ingredient, Recipe, FgUser


@admin.register(FgUser)
class FgUserAdmin(UserAdmin):
    """Настройки раздела пользователей админ-панели."""

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets[1][1]['fields'] = fieldsets[1][1]['fields'] + ('bio',)
        fieldsets[2][1]['fields'] = ('role',) + fieldsets[2][1]['fields']
        return fieldsets


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройки раздела Тэги админ-панели."""

    list_display = ('name', 'slug',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройки раздела Ингредиенты админ-панели."""

    list_display = ('name', 'measurement_unit',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройки раздела Рецепты админ-панели."""

    list_display = ('name', 'text', 'cooking_time', 'author', 'image',)
    # filter_horizontal = ('ingredients', 'tags',)

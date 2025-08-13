from django.contrib import admin

from .models import Tag, Ingredient, Recipe


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

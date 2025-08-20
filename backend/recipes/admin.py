from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Tag, Ingredient, Recipe


User = get_user_model()

admin.site.empty_value_display = 'Не задано'


@admin.register(User)
class FgUserAdmin(UserAdmin):
    """Настройки раздела пользователей админ-панели."""

    list_editable = ('first_name', 'last_name')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройки раздела Тэги админ-панели."""

    list_display = ('name', 'slug',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройки раздела Ингредиенты админ-панели."""

    list_display = ('name', 'measurement_unit',)
    list_per_page = 15
    search_fields = ('name',)


class TagsInline(admin.TabularInline):
    model = Recipe.tags.through


class IngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройки раздела Рецепты админ-панели."""

    fields = ('author_name', 'followers', 'self_name',
              'image', 'text', 'cooking_time',)
    readonly_fields = ('author_name', 'followers', 'self_name',)
    list_display = ('self_name', 'author_name', 'followers', 'text', )
    search_fields = ('name', 'author__first_name', 'author__last_name',)
    list_filter = ('tags__name',)
    inlines = [
        TagsInline,
        IngredientInline,
    ]

    @admin.display(description="Добавили в избранное",)
    def followers(self, obj):
        return obj.userfavorites.count()

    @admin.display(description="Автор",)
    def author_name(self, obj):
        return f'{obj.author.first_name} {obj.author.last_name}'

    @admin.display(description="Название",)
    def self_name(self, obj):
        return obj.name

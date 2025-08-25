from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .filters import (HasRecipes, HasSubscriptions, HasFollowers,
                      IsInRecipe, IsInFavorites, CookTimeFilter)
from ..models import Tag, Ingredient, Recipe


User = get_user_model()

admin.site.empty_value_display = 'Не задано'


class RecipesCountMixin(admin.ModelAdmin):
    """Миксин для добавления поля с количеством рецептов
    и ограничения выдачи."""

    list_per_page = 15

    @admin.display(description='Рецептов',)
    def recipes_count(self, obj):
        return f'{obj.recipes.count()}'


@admin.register(User)
class FoodgramUserAdmin(RecipesCountMixin, UserAdmin):
    """Настройки раздела пользователей админ-панели."""

    list_display = ('id', 'username', 'full_name',
              'avatar_small', 'email', 'recipes_count',
              'subscriptions_count', 'followers_count',)
    list_display_links = ('id', 'username', 'full_name',)
    ordering = ('last_name',)
    readonly_fields = ('full_name', 'recipes_count', 'subscriptions_count', 'followers_count',)
    list_filter = (HasRecipes, HasSubscriptions, HasFollowers, )
    list_per_page = 8

    @admin.display(description='ФИО',)
    def full_name(self, user):
        return f'{user.last_name} {user.first_name}'

    @admin.display(description='Подписок',)
    def subscriptions_count(self, user):
        return f'{user.subscriptions.count()}'

    @admin.display(description='Подписчиков',)
    def followers_count(self, user):
        return f'{user.followers.count()}'


@admin.register(Tag)
class TagAdmin(RecipesCountMixin, admin.ModelAdmin):
    """Настройки раздела Тэги админ-панели."""

    list_display = ('name', 'slug', 'recipes_count',)
    search_fields = ('name', 'slug',)

@admin.register(Ingredient)
class IngredientAdmin(RecipesCountMixin, admin.ModelAdmin):
    """Настройки раздела Ингредиенты админ-панели."""

    list_display = ('name', 'measurement_unit', 'recipes_count',)
    list_filter = (IsInRecipe, 'measurement_unit',)
    search_fields = ('name', 'measurement_unit',)


class TagsInline(admin.TabularInline):
    model = Recipe.tags.through


class IngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройки раздела Рецепты админ-панели."""

    list_display = ('id', 'name', 'tags_ul', 'image_small', 'author_name',
                    'followers', 'ingredients_ul', 'cooking_time',)
    list_display_links = ('id', 'name', 'image_small',)
    readonly_fields = ('author_name', 'followers', 'name',)
    search_fields = ('name', 'author__first_name', 'author__last_name',)
    list_filter = (IsInFavorites, CookTimeFilter, 'tags__name',)
    inlines = [
        TagsInline,
        IngredientInline,
    ]
    filter_horizontal = ('tags', 'ingredients',)
    list_per_page = 7

    @admin.display(description='В избранном',)
    def followers(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='Полное имя втора',)
    def author_name(self, recipe):
        return f'{recipe.author.first_name} {recipe.author.last_name}'

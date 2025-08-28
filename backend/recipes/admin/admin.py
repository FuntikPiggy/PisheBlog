from admin_decorators import short_description
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.db.models import F
from django.utils.safestring import mark_safe

from .filters import (HasRecipes, HasSubscriptions, HasFollowers,
                      IsInRecipe, IsInFavorites, CookTimeFilter)
from ..models import Tag, Ingredient, Recipe, Subscription, Favorite, Purchase

User = get_user_model()

admin.site.empty_value_display = 'Не задано'


class RecipesCountMixin:
    """Миксин для добавления поля с количеством рецептов
    и ограничения выдачи."""

    list_display = ('recipes_count',)
    list_per_page = 15

    @admin.display(description='Рецептов',)
    def recipes_count(self, obj):
        return obj.recipes.count()


@admin.register(User)
class FoodgramUserAdmin(RecipesCountMixin, UserAdmin):
    """Настройки раздела пользователей админ-панели."""

    list_display = ('id', 'username', 'full_name', 'avatar_small', 'email',
                    *RecipesCountMixin.list_display, 'subscriptions_count',
                    'followers_count',)
    list_display_links = ('id', 'username', 'full_name',)
    ordering = ('last_name',)
    readonly_fields = ('full_name', 'recipes_count',
                       'subscriptions_count', 'followers_count',)
    list_filter = (HasRecipes, HasSubscriptions, HasFollowers, )
    list_per_page = 8

    @admin.display(description='ФИО',)
    def full_name(self, user):
        return f'{user.last_name} {user.first_name}'

    @admin.display(description='Подписок',)
    def subscriptions_count(self, user):
        return user.subscriptions_added.count()

    @admin.display(description='Подписчиков',)
    def followers_count(self, user):
        return user.subscriptions_recieved.count()

    def get_avatar(self, user):
        if not user.avatar:
            return '/static/recipes/admin/ava_default.jpg'
        return user.avatar.url

    @short_description('Аватар')
    @mark_safe
    def avatar_small(self, user):
        return f'<img src="{self.get_avatar(user)}" width="35" height="35" />'


@admin.register(Tag)
class TagAdmin(RecipesCountMixin, admin.ModelAdmin):
    """Настройки раздела Теги админ-панели."""

    list_display = ('name', 'slug', *RecipesCountMixin.list_display,)
    search_fields = ('name', 'slug',)


@admin.register(Ingredient)
class IngredientAdmin(RecipesCountMixin, admin.ModelAdmin):
    """Настройки раздела Продукты админ-панели."""

    list_display = ('name', 'measurement_unit',
                    *RecipesCountMixin.list_display,)
    list_filter = (IsInRecipe, 'measurement_unit',)
    search_fields = ('name', 'measurement_unit',)


class TagsInline(admin.TabularInline):
    model = Recipe.tags.through


class IngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through


class IngrediensListMixin:
    """Миксин для добавления поля с перечнем продуктов."""

    @short_description('Продукты')
    @mark_safe
    def ingredients_list(self, obj):
        recipe = obj if isinstance(obj, Recipe) else obj.recipe
        ingredients = list(
            recipe.ingredients.all().prefetch_related(
                'recipeingredients',
            ).values(
                'name',
                unit=F('measurement_unit'),
                amount=F('recipeingredients__amount'),
            )
        )
        return "".join(
            [f"{i['name']} - {i['amount']}{i['unit']}<br>"
             for i in ingredients]
        )


@admin.register(Recipe)
class RecipeAdmin(IngrediensListMixin, admin.ModelAdmin):
    """Настройки раздела Рецепты админ-панели."""

    list_display = ('id', 'name', 'tags_list', 'image_small', 'author_name',
                    'followers', 'ingredients_list', 'cooking_time',)
    list_display_links = ('id', 'name', 'image_small',)
    readonly_fields = ('author_name', 'followers', 'name',)
    search_fields = ('name', 'author__first_name', 'author__last_name',)
    list_filter = (IsInFavorites, CookTimeFilter, 'tags__name',)
    inlines = [
        TagsInline,
        IngredientInline,
    ]
    filter_horizontal = ('tags', )
    list_per_page = 8

    @admin.display(description='В избранном',)
    def followers(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='ФИО автора',)
    def author_name(self, recipe):
        return f'{recipe.author.first_name} {recipe.author.last_name}'

    def get_image(self, recipe):
        if not recipe.image:
            return '/static/recipes/admin/not-found.png'
        return recipe.image.url

    @short_description('Изображение')
    @mark_safe
    def image_small(self, recipe):
        return f'<img src="{self.get_image(recipe)}" width="70" height="70" />'

    @short_description('Теги')
    @mark_safe
    def tags_list(self, recipe):
        return "".join([f"{i.name}<br>" for i in recipe.tags.all()])


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Настройки раздела Подписки админ-панели."""

    list_display = ('id', 'subsription_name', 'user_name_id', 'author_name_id',)
    list_display_links = ('id', 'subsription_name',)
    search_fields = ('user__last_name', 'user__first_name', )
    ordering = ('user__last_name',)
    list_per_page = 15

    @staticmethod
    def get_user_info(user):
        return f'{user.last_name} {user.first_name} ({user.id})'

    @admin.display(description='Подписка',)
    def subsription_name(self, subscription):
        return (f'{subscription.user.username} '
                f'на {subscription.author.username}')

    @admin.display(description='ФИО (id) подписчика',)
    def user_name_id(self, subscription):
        return self.get_user_info(subscription.user)

    @admin.display(description='ФИО (id) автора',)
    def author_name_id(self, subscription):
        return self.get_user_info(subscription.author)


class UserFavoriteBaseAdmin(IngrediensListMixin, admin.ModelAdmin):
    """Базовый класс для Избранного и Корзины покупок."""

    list_display = ('id', 'user_name', 'recipe__name', 'ingredients_list')
    list_display_links = ('id', 'user_name',)
    search_fields = ('user__last_name', 'user__first_name',
                     'recipe__name', 'recipe__ingredients__name')
    ordering = ('user__last_name',)
    list_per_page = 8

    @admin.display(description='ФИО пользователя',)
    def user_name(self, favorite):
        return f'{favorite.user.first_name} {favorite.user.last_name}'


@admin.register(Favorite)
class FavoriteAdmin(UserFavoriteBaseAdmin):
    """Настройки раздела Избранное админ-панели."""


@admin.register(Purchase)
class PurchaseAdmin(UserFavoriteBaseAdmin):
    """Настройки раздела Корзина покупок админ-панели."""
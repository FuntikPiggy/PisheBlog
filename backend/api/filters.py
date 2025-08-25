from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters

from recipes.models import Recipe

User = get_user_model()


class RecipeFilter(filters.FilterSet):
    """Фильтр для рецептов"""

    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug', lookup_expr='contains',)

    # tags = filters.AllValuesMultipleFilter(
    #     field_name='tags__slug', lookup_expr='contains',)
    # is_favorited = filters.ModelChoiceFilter(
    #     queryset=User.objects.all(), field_name='fans',)
    # is_in_shopping_cart = filters.ModelChoiceFilter(
    #     queryset=User.objects.all(), field_name='buyers',)

    is_favorited = filters.ModelChoiceFilter(
        queryset=User.objects.all(), field_name='favorites__user_id',)
    is_in_shopping_cart = filters.ModelChoiceFilter(
        queryset=User.objects.all(), field_name='purchases__user_id',)

    # is_favorited = filters.ModelChoiceFilter(
    #     queryset=User.objects.all(), field_name='favorites__recipe',)
    # is_in_shopping_cart = filters.ModelChoiceFilter(
    #     queryset=User.objects.all(), field_name='purchases__recipe',)
    # is_favorited = filters.ModelMultipleChoiceFilter(
    #     queryset=User.objects.all(), field_name='favorites__recipe_id', to_field_name='id',)
    # is_in_shopping_cart = filters.ModelMultipleChoiceFilter(
    #     queryset=User.objects.all(), field_name='purchases__recipe_id', to_field_name='id',)

    class Meta:
        model = Recipe
        fields = ('author', 'is_favorited', 'is_in_shopping_cart',)


class IngredientFilter(filters.FilterSet):
    """Фильтр для ингредиентов"""

    name = filters.CharFilter(field_name='name', lookup_expr='istartswith',)

from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters, BooleanFilter, NumberFilter

from recipes.models import Recipe


User = get_user_model()


class RecipeFilter(filters.FilterSet):
    """Фильтр для рецептов"""

    is_in_shopping_cart = NumberFilter(method='filter_is_in_shopping_cart')
    is_favorited = NumberFilter(method='filter_is_favorited')

    class Meta:
        model = Recipe
        fields = ('author', 'is_favorited', 'is_in_shopping_cart',)

    def filter_is_in_shopping_cart(self, queryset,):
        return queryset.filter(purchases__user_id=self.request.user.id)

    def filter_is_favorited(self, queryset,):
        return queryset.filter(favorites__user_id=self.request.user.id)


class IngredientFilter(filters.FilterSet):
    """Фильтр для ингредиентов"""

    name = filters.CharFilter(field_name='name', lookup_expr='istartswith',)

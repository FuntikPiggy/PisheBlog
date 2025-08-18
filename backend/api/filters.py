from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters, ModelChoiceFilter

from recipes.models import Recipe

User = get_user_model()


class RecipeFilter(filters.FilterSet):
    """Фильтр для рецептов"""

    tags = filters.AllValuesMultipleFilter(field_name='tags__slug', lookup_expr='contains',)
    is_favorited = ModelChoiceFilter(queryset=User.objects.all(), field_name='fans',)
    is_in_shopping_cart = ModelChoiceFilter(queryset=User.objects.all(), field_name='buyers',)

    class Meta:
        model = Recipe
        fields = ('author',)

class IngredientFilter(filters.FilterSet):
    """Фильтр для ингредиентов"""

    name = filters.CharFilter(field_name='name', lookup_expr='startswith',)

from django_filters import rest_framework as filters
# from django_filters.widgets import CSVWidget

from recipes.models import Recipe, Tag


class RecipeFilter(filters.FilterSet):
    # tags__contains =
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug', lookup_expr='contains')
    # is_favorited = filters.CharFilter(field_name="is_favorited", lookup_expr='contains')
    # max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')
    # is_favorited = filters.BooleanFilter(field_name="price",)
    # is_in_shopping_cart = filters.BooleanFilter(field_name="price",)

    class Meta:
        model = Recipe
        fields = ['author', 'is_favorited', 'is_in_shopping_cart',]

        # fields = {
        #     'tags__slug': ('in',),
        #     'author': ('exact',),
        #     'is_favorited': ('exact',),
        #     'is_in_shopping_cart': ('exact',),
        # }

#     @staticmethod
#     def filter_tags(queryset, field_name, value):
#         return queryset.filter(tags__name__in=value)
#
#
# from django_filters.rest_framework import FilterSet, filters
#
# from .models import Contact
#
#
# class ContactFilter(FilterSet):
#
#     class Meta:
#         model = Contact
#
#     @staticmethod
#     def filter_tags(queryset, field_name, value):
#         return queryset.filter(tags__name__in=value)
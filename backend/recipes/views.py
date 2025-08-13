from rest_framework.viewsets import ReadOnlyModelViewSet

from recipes.models import Tag, Ingredient


class CategoryGenreViewSet(ReadOnlyModelViewSet):
    """Представление моделей тэга и ингредиента."""

    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('name',)
    # permission_classes = (IsAdminOrReadOnly,)

    def get_queryset(self):
        if self.basename == 'tag':
            return Tag.objects.all()
        return Ingredient.objects.all()

    # def get_serializer_class(self):
    #     if self.basename == 'genre':
    #         return TagSerializer
    #     return IngredientSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from recipes.models import Tag, Ingredient, Recipe


class TagViewSet(ReadOnlyModelViewSet):
    """Представление модели тэга."""
    queryset = Tag.objects.all()


class IngredientViewSet(ReadOnlyModelViewSet):
    """Представление модели ингредиента."""
    queryset = Ingredient.objects.all()


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']
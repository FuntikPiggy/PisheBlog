from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from recipes.models import Tag, Ingredient, Recipe
from recipes.serializers import TagSerializer, IngredientSerializer, RecipeSerializer


class TagViewSet(ReadOnlyModelViewSet):
    """Представление модели тэга."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class IngredientViewSet(ReadOnlyModelViewSet):
    """Представление модели ингредиента."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
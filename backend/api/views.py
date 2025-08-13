from django.contrib.auth import get_user_model
from djoser.views import UserViewSet

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from recipes.models import Tag, Ingredient, Recipe
from recipes.serializers import TagSerializer, IngredientSerializer, RecipeSerializer
from .serializers import SubscriptionsSerializer


User = get_user_model()


class FgUserViewSet(UserViewSet):
    http_method_names = ['get', 'post', 'put', 'delete']
    pagination_class = LimitOffsetPagination


    @action(['get',], url_path='subscriptions', detail=False)
    def get_subscriptions(self, request):
        return Response(
            SubscriptionsSerializer(
                request.user.subscriptions.all(),
                many=True,
                context={'request': request}
            ).data,
            status=status.HTTP_200_OK
        )

    @action(['put', 'delete'], url_path='me/avatar', detail=False)
    def avatar(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == 'PUT':
            return self.partial_update(request, *args, **kwargs)
        elif request.method == 'DELETE':
            request.user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


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
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet

from rest_framework import status, permissions, filters
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from recipes.models import Tag, Ingredient, Recipe
from .filters import IsInFavoritesFilterBackend
from .permissions import IsAuthorOrStaffOrReadOnly
from .serializers import TagSerializer, IngredientSerializer, RecipeInSerializer, SubscriptionsSerializer, \
    RecipeOutSerializer


User = get_user_model()


class FgUserViewSet(UserViewSet):
    http_method_names = ['get', 'post', 'put', 'delete']
    pagination_class = LimitOffsetPagination

    @action(
        ['get',], url_path='subscriptions',
        detail=False, permission_classes=(IsAuthorOrStaffOrReadOnly,)
    )
    def get_subscriptions(self, request):
        return Response(
            SubscriptionsSerializer(
                request.user.subscriptions.all(),
                many=True,
                context={'request': request}
            ).data,
            status=status.HTTP_200_OK
        )

    @action(
        ['put', 'delete'], url_path='me/avatar',
        detail=False, permission_classes=(IsAuthorOrStaffOrReadOnly,)
    )
    def avatar(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == 'PUT':
            return self.partial_update(request, *args, **kwargs)
        elif request.method == 'DELETE':
            request.user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ModelViewSet):
    """Представление модели тэга."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Представление модели ингредиента."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.SearchFilter, )
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    """Представление модели рецепта."""

    # queryset = Recipe.objects.prefetch_related(Prefetch('ingredients_amount', queryset=RecipeIngredient.objects.all()))
    queryset = Recipe.objects.all().prefetch_related('ingredients', 'recipeingredients')
    serializer_class = RecipeInSerializer
    filter_backends = (DjangoFilterBackend, IsInFavoritesFilterBackend,)
    filterset_fields = ('author', 'tags',)
    pagination_class = LimitOffsetPagination
    permission_classes = (AllowAny,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action == 'create':
            return context
        context.update({'queryset': self.queryset})
        return context

    # def get_queryset(self):
    #     # queryset = list(RecipeIngredient.objects.all().select_related('recipe', 'ingredient'))
    #     queryset = list(Recipe.objects.prefetch_related(Prefetch('ingredients_amount', queryset=RecipeIngredient.objects.all())))
    #     return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return self.serializer_class
        return RecipeOutSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # def get_serializer_context(self):
    #     return {
    #         'request': self.request,
    #         'format': self.format_kwarg,
    #         'view': self,
    #         'tags': Tag.objects.all(),
    #     }

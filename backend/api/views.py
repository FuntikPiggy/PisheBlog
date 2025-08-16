from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet

from rest_framework import status, permissions, filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from recipes.models import Tag, Ingredient, Recipe
from .filters import RecipeFilter
from .permissions import IsAuthorOrStaffOrReadOnly
from .serializers import TagSerializer, IngredientSerializer, RecipeInSerializer, SubscriptionsSerializer, \
    RecipeOutSerializer, CustomUserSerializer

User = get_user_model()


class FgUserViewSet(UserViewSet):
    """Представление модели пользователя."""

    http_method_names = ('get', 'post', 'put', 'delete',)
    # permission_classes = (IsAuthorOrStaffOrReadOnly,)
    serializer_class = CustomUserSerializer

    @action(
        ('get',), url_path='subscriptions',
        detail=False#, permission_classes=(IsAuthorOrStaffOrReadOnly,)
    )
    def get_subscriptions(self, request):
        return Response(
            SubscriptionsSerializer(
                request.user.subscriptions.all(),
                many=True,
                # context={'request': request}
            ).data,
            status=status.HTTP_200_OK
        )

    @action(
        ('put', 'delete'), url_path='me/avatar',
        detail=False#, permission_classes=(IsAuthorOrStaffOrReadOnly,)
    )
    def avatar(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == 'PUT':
            return self.partial_update(request, *args, **kwargs)
        elif request.method == 'DELETE':
            request.user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ('post', 'delete',), url_path=r'(?P<follow_id>\d*)/subscribe',
        detail=False#, permission_classes=(IsAuthorOrStaffOrReadOnly,)
    )
    def subscribe(self, request, follow_id, *args, **kwargs):
        if request.method == 'POST':
            self.request.user.subscriptions.add(follow_id)
            return Response(status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            self.request.user.subscriptions.remove(follow_id)
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ModelViewSet):
    """Представление модели тэга."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Представление модели ингредиента."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """Представление модели рецепта."""

    http_method_names = ('get', 'post', 'patch', 'delete',)
    permission_classes = (permissions.AllowAny,)
    # queryset = Recipe.objects.prefetch_related(Prefetch('ingredients_amount', queryset=RecipeIngredient.objects.all()))
    queryset = Recipe.objects.all()#.prefetch_related('ingredients', 'recipeingredients')
    serializer_class = RecipeInSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    # filterset_fields = ('author__contains', 'tags__contains', 'is_favorited', 'is_in_shopping_cart',)
    # pagination_class = LimitOffsetPagination

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
